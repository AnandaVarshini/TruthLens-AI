"""Model factories and evaluation helpers shared by scripts, notebooks and the API."""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from .config import (
    CLASS_NAMES,
    RANDOM_STATE,
    TFIDF_CHAR_PARAMS,
    TFIDF_WORD_PARAMS,
)


def build_feature_union() -> FeatureUnion:
    """Word (1-2)-gram + character (3-5)-gram TF-IDF features.

    Word n-grams capture vocabulary and short phrases; character n-grams make the
    model more robust to misspellings and inflection, which matters for the short,
    informal statements in LIAR.
    """
    return FeatureUnion(
        [
            ("word_tfidf", TfidfVectorizer(**TFIDF_WORD_PARAMS)),
            ("char_tfidf", TfidfVectorizer(**TFIDF_CHAR_PARAMS)),
        ]
    )


def build_pipeline(estimator: Any) -> Pipeline:
    """Attach the shared feature extraction step to a classifier."""
    return Pipeline([("features", build_feature_union()), ("classifier", estimator)])


def default_candidates() -> dict[str, dict[str, Any]]:
    """The four project algorithms with the hyper-parameter grids tuned on validation.

    Every entry is a single scikit-learn Pipeline, so the exact preprocessing seen
    in training is reused at prediction time when the artifact is loaded.
    """
    return {
        "logistic_regression": {
            "display_name": "Logistic Regression (A1)",
            "short_name": "A1·LogReg",
            "description": (
                "Linear model that estimates one coefficient per TF-IDF feature for each "
                "class. Fast, interpretable and a strong baseline for sparse text."
            ),
            "grid": [
                {"C": 1.0, "class_weight": None},
                {"C": 2.0, "class_weight": None},
                {"C": 2.0, "class_weight": "balanced"},
                {"C": 4.0, "class_weight": "balanced"},
            ],
            "factory": lambda **kw: build_pipeline(
                LogisticRegression(max_iter=3000, random_state=RANDOM_STATE, **kw)
            ),
        },
        "svm": {
            "display_name": "Support Vector Machine (A2)",
            "short_name": "A2·SVM",
            "description": (
                "Linear support-vector classifier with a squared-hinge loss. Effective on "
                "high-dimensional sparse text. LinearSVC does not produce calibrated "
                "probabilities, so the API reports normalised decision scores for this "
                "model and labels them as such."
            ),
            "grid": [{"C": 0.1}, {"C": 0.25}, {"C": 0.5}, {"C": 1.0}],
            "factory": lambda **kw: build_pipeline(
                LinearSVC(random_state=RANDOM_STATE, **kw)
            ),
        },
        "random_forest": {
            "display_name": "Random Forest (A3)",
            "short_name": "A3·Forest",
            "description": (
                "An ensemble of decision trees trained on bootstrap samples. Captures "
                "non-linear interactions but is slower and less precise on very sparse "
                "TF-IDF features."
            ),
            "grid": [
                {"n_estimators": 200, "min_samples_leaf": 1},
                {"n_estimators": 200, "min_samples_leaf": 3},
            ],
            "factory": lambda **kw: build_pipeline(
                RandomForestClassifier(
                    random_state=RANDOM_STATE, n_jobs=-1, max_features="sqrt", **kw
                )
            ),
        },
        "naive_bayes": {
            "display_name": "Multinomial Naive Bayes (A4)",
            "short_name": "A4·NB",
            "description": (
                "Probabilistic classifier that assumes conditional independence between "
                "terms. Extremely fast and a classic text-classification baseline."
            ),
            "grid": [{"alpha": 0.1}, {"alpha": 0.3}, {"alpha": 1.0}],
            "factory": lambda **kw: build_pipeline(MultinomialNB(**kw)),
        },
    }


def has_probabilities(pipeline: Pipeline) -> bool:
    return hasattr(pipeline, "predict_proba") and hasattr(pipeline.named_steps["classifier"], "predict_proba")


def predict_scores(pipeline: Pipeline, texts: list[str]) -> tuple[list[str], np.ndarray, str]:
    """Predict labels plus per-class scores.

    Returns ``(labels, scores, score_type)``. ``score_type`` is ``"probability"``
    when the estimator is probabilistic; for a decision-function-only estimator the
    scores are normalised decision values and must be labelled as such in the UI.
    """
    labels = list(pipeline.predict(texts))
    if has_probabilities(pipeline):
        scores = pipeline.predict_proba(texts)
        return labels, np.asarray(scores), "probability"
    if hasattr(pipeline, "decision_function"):
        raw = np.asarray(pipeline.decision_function(texts), dtype=float)
        exp = np.exp(raw - raw.max(axis=1, keepdims=True))
        scores = exp / exp.sum(axis=1, keepdims=True)
        return labels, scores, "decision_score"
    onehot = np.zeros((len(texts), len(CLASS_NAMES)))
    return labels, onehot, "none"


def _safe_metric(fn, y_true, y_pred, **kwargs) -> float:
    try:
        return float(fn(y_true, y_pred, **kwargs))
    except Exception:  # pragma: no cover - defensive for degenerate predictions
        return 0.0


def evaluate_predictions(y_true, y_pred, labels: list[str] | None = None) -> dict:
    """Compute the full metric set used across the project."""
    labels = labels or CLASS_NAMES
    report = classification_report(
        y_true, y_pred, labels=labels, output_dict=True, zero_division=0
    )
    per_class = {
        cls: {
            "precision": float(report[cls]["precision"]),
            "recall": float(report[cls]["recall"]),
            "f1": float(report[cls]["f1-score"]),
            "support": int(report[cls]["support"]),
        }
        for cls in labels
    }
    return {
        "accuracy": _safe_metric(accuracy_score, y_true, y_pred),
        "precision_weighted": _safe_metric(
            precision_score, y_true, y_pred, average="weighted", zero_division=0
        ),
        "recall_weighted": _safe_metric(
            recall_score, y_true, y_pred, average="weighted", zero_division=0
        ),
        "f1_weighted": _safe_metric(
            f1_score, y_true, y_pred, average="weighted", zero_division=0
        ),
        "f1_macro": _safe_metric(
            f1_score, y_true, y_pred, average="macro", zero_division=0
        ),
        "precision_macro": _safe_metric(
            precision_score, y_true, y_pred, average="macro", zero_division=0
        ),
        "recall_macro": _safe_metric(
            recall_score, y_true, y_pred, average="macro", zero_division=0
        ),
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "labels": labels,
    }
