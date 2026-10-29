"""Model loading and inference for the API.

The selected scikit-learn pipeline is loaded exactly once (lazily, guarded by a
lock) and reused for every request. It is never retrained during a request.
"""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

import joblib
import numpy as np

from src.truthlens.preprocessing import preprocess_text, validate_input_text

from .config import METRICS_JSON_PATH, SELECTED_MODEL_PATH

logger = logging.getLogger("truthlens.ml")


class ModelNotReadyError(RuntimeError):
    """Raised when the trained artifacts are missing or unreadable."""


class ModelService:
    def __init__(self) -> None:
        self._pipeline = None
        self._metadata: dict | None = None
        self._lock = threading.Lock()
        self._load_error: str | None = None

    # ------------------------------------------------------------------ load
    def _read_metadata(self) -> dict:
        if self._metadata is None:
            if not METRICS_JSON_PATH.exists():
                raise ModelNotReadyError(
                    f"Evaluation metadata not found at {METRICS_JSON_PATH}. "
                    "Run: python scripts/train_models.py"
                )
            self._metadata = json.loads(METRICS_JSON_PATH.read_text(encoding="utf-8"))
        return self._metadata

    def load(self) -> None:
        """Load the artifact once. Safe to call repeatedly."""
        if self._pipeline is not None:
            return
        with self._lock:
            if self._pipeline is not None:
                return
            if not SELECTED_MODEL_PATH.exists():
                self._load_error = (
                    f"Trained model not found at {SELECTED_MODEL_PATH}. "
                    "Run: python scripts/train_models.py"
                )
                raise ModelNotReadyError(self._load_error)
            try:
                pipeline = joblib.load(SELECTED_MODEL_PATH)
            except Exception as exc:  # version mismatch / corrupt file
                self._load_error = (
                    "The saved model could not be loaded. It was created with a different "
                    "scikit-learn version. Re-run: python scripts/train_models.py "
                    f"(details: {exc})"
                )
                raise ModelNotReadyError(self._load_error) from exc

            if not hasattr(pipeline, "predict"):
                raise ModelNotReadyError("The model artifact is not a valid scikit-learn pipeline.")
            self._pipeline = pipeline
            self._load_error = None
            logger.info("Loaded model artifact from %s", SELECTED_MODEL_PATH)

    def is_ready(self) -> bool:
        try:
            self.load()
            return True
        except ModelNotReadyError:
            return False

    # ------------------------------------------------------------------ info
    @property
    def metadata(self) -> dict:
        return self._read_metadata()

    def model_name(self) -> str:
        try:
            return self.metadata.get("selected_model_display_name", "TruthLens model")
        except ModelNotReadyError:
            return "unavailable"

    def insights(self) -> dict:
        return self.metadata

    # -------------------------------------------------------------- predict
    def predict(self, text: str) -> dict:
        ok, message = validate_input_text(text)
        if not ok:
            raise ValueError(message)

        self.load()
        assert self._pipeline is not None
        cleaned = preprocess_text(text)
        pipeline = self._pipeline
        classes = [str(c) for c in getattr(pipeline, "classes_", [])]
        if not classes:
            classifier = pipeline.named_steps.get("classifier")
            classes = [str(c) for c in getattr(classifier, "classes_", [])]

        prediction = pipeline.predict([cleaned])[0]
        score_type = "probability"
        scores: list[dict] = []
        confidence: float | None = None

        classifier = pipeline.named_steps.get("classifier") if hasattr(pipeline, "named_steps") else None
        if hasattr(classifier, "predict_proba"):
            raw = np.asarray(pipeline.predict_proba([cleaned])[0], dtype=float)
            pairs = list(zip(classes, raw))
            confidence = float(max(raw))
        elif hasattr(classifier, "decision_function"):
            raw = np.asarray(pipeline.decision_function([cleaned]))
            raw = raw.reshape(1, -1)[0].astype(float)
            exp = np.exp(raw - raw.max())
            norm = exp / exp.sum()
            pairs = list(zip(classes, norm))
            score_type = "decision_score"
            confidence = float(norm.max())
        else:
            pairs = [(c, 1.0 if c == str(prediction) else 0.0) for c in classes]
            score_type = "none"
            confidence = None

        scores = [{"label": label, "score": round(float(score), 6)} for label, score in pairs]
        scores.sort(key=lambda item: item["score"], reverse=True)
        return {
            "label": str(prediction),
            "confidence": round(confidence, 6) if confidence is not None else None,
            "score_type": score_type,
            "scores": scores,
            "model_name": self.model_name(),
            "cleaned_text": cleaned,
        }


model_service = ModelService()
