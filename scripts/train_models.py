"""Train, tune, evaluate and export the TruthLens AI models.

Usage (from the project root):

    python scripts/train_models.py

What it does
------------
1. Loads ``data/cleaned_dataset.csv`` and audits it (labels, duplicates, splits).
2. Trains the four algorithms on the *training* split only.
3. Selects hyper-parameters using the *validation* split (no test leakage).
4. Picks the final model by macro-F1 on validation.
5. Reports the untouched *test* metrics and writes every artifact:

   models/truthlens_pipeline.joblib   <- loaded by the FastAPI backend
   models/candidates/<name>.joblib    <- all four fitted candidates
   models/model_metadata.json
   results/metrics.json  /  results/metrics.csv
   results/figures/*.png
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import sklearn  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sklearn.metrics import ConfusionMatrixDisplay  # noqa: E402

from src.truthlens.config import (  # noqa: E402
    CANDIDATES_DIR,
    CLASS_NAMES,
    CLASS_DESCRIPTIONS,
    LABEL_MAPPING,
    METRICS_CSV_PATH,
    METRICS_JSON_PATH,
    MODEL_METADATA_PATH,
    SELECTED_MODEL_PATH,
    ensure_directories,
)
from src.truthlens.data import load_dataset  # noqa: E402
from src.truthlens.pipeline import (  # noqa: E402
    default_candidates,
    evaluate_predictions,
)

FIGURES = PROJECT_ROOT / "results" / "figures"


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def train() -> dict:
    ensure_directories()
    FIGURES.mkdir(parents=True, exist_ok=True)
    started = time.time()

    print("=" * 72)
    print("TruthLens AI - training pipeline")
    print("=" * 72)

    bundle = load_dataset()
    train_df, valid_df, test_df = bundle.train, bundle.valid, bundle.test
    print(f"Rows -> train={len(train_df)} valid={len(valid_df)} test={len(test_df)}")
    print(f"Class distribution: {bundle.report['class_distribution']}")

    X_train, y_train = train_df["model_text"].tolist(), train_df["label"].tolist()
    X_valid, y_valid = valid_df["model_text"].tolist(), valid_df["label"].tolist()
    X_test, y_test = test_df["model_text"].tolist(), test_df["label"].tolist()

    candidates = default_candidates()
    results: dict[str, dict] = {}
    fitted: dict[str, object] = {}

    for key, meta in candidates.items():
        print(f"\n--- {meta['display_name']} ---")
        best = None
        best_params: dict = {}
        for params in meta["grid"]:
            print(f"  fitting {params} ...", end=" ", flush=True)
            t0 = time.time()
            pipe = meta["factory"](**params)
            pipe.fit(X_train, y_train)
            valid_pred = pipe.predict(X_valid)
            valid_metrics = evaluate_predictions(y_valid, valid_pred)
            elapsed = time.time() - t0
            print(
                f"val_acc={_fmt(valid_metrics['accuracy'])} "
                f"val_macro_f1={_fmt(valid_metrics['f1_macro'])} ({elapsed:.1f}s)"
            )
            if best is None or valid_metrics["f1_macro"] > best[0]["f1_macro"]:
                best = (valid_metrics, pipe)
                best_params = params

        assert best is not None
        valid_metrics, pipe = best
        test_pred = pipe.predict(X_test)
        test_metrics = evaluate_predictions(y_test, test_pred)

        results[key] = {
            "display_name": meta["display_name"],
            "short_name": meta["short_name"],
            "description": meta["description"],
            "best_params": best_params,
            "validation": valid_metrics,
            "test": test_metrics,
            "training_seconds": None,
            "artifact": f"models/candidates/{key}.joblib",
        }
        fitted[key] = pipe

        joblib.dump(pipe, CANDIDATES_DIR / f"{key}.joblib", compress=3)
        print(
            f"  selected {best_params}: test_acc={_fmt(test_metrics['accuracy'])} "
            f"test_macro_f1={_fmt(test_metrics['f1_macro'])}"
        )

    # ---- final model selection: macro-F1 on the validation split -------------
    selected_key = max(results, key=lambda k: results[k]["validation"]["f1_macro"])
    selected_pipe = fitted[selected_key]
    selected_test = results[selected_key]["test"]
    print(f"\nSelected model (validation macro-F1): {results[selected_key]['display_name']}")

    joblib.dump(selected_pipe, SELECTED_MODEL_PATH, compress=3)

    metadata = {
        "project": "TruthLens AI",
        "task": "Four-class fake-news / claim reliability classification",
        "classes": CLASS_NAMES,
        "class_descriptions": CLASS_DESCRIPTIONS,
        "label_mapping": LABEL_MAPPING,
        "selected_model": selected_key,
        "selected_model_display_name": results[selected_key]["display_name"],
        "selection_criterion": "highest macro-F1 on the validation split",
        "selected_model_metrics": selected_test,
        "candidates": {
            key: {
                "display_name": value["display_name"],
                "best_params": value["best_params"],
                "validation": value["validation"],
                "test": value["test"],
            }
            for key, value in results.items()
        },
        "dataset": bundle.report,
        "preprocessing": {
            "steps": [
                "HTML unescape",
                "lowercase",
                "remove URLs",
                "remove HTML tags",
                "remove punctuation and digits",
                "collapse whitespace",
            ],
            "stop_words": "scikit-learn English stop-word list inside TF-IDF",
        },
        "features": {
            "word_tfidf": "TF-IDF, 1-2 grams, min_df=2, max_features=60000, sublinear_tf",
            "char_tfidf": "char_wb TF-IDF, 3-5 grams, min_df=3, max_features=60000",
        },
        "environment": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "training_seconds": round(time.time() - started, 1),
        "disclaimer": (
            "Predictions are statistical estimates learned from the LIAR dataset, "
            "not proof that a statement is true or false."
        ),
    }

    METRICS_JSON_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    MODEL_METADATA_PATH.write_text(
        json.dumps(
            {
                "selected_model": selected_key,
                "selected_model_display_name": results[selected_key]["display_name"],
                "classes": CLASS_NAMES,
                "label_mapping": LABEL_MAPPING,
                "selection_criterion": metadata["selection_criterion"],
                "test_metrics": selected_test,
                "generated_at": metadata["generated_at"],
                "environment": metadata["environment"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # ---- flat CSV for the report -------------------------------------------
    rows = []
    for key, value in results.items():
        for split in ("validation", "test"):
            m = value[split]
            rows.append(
                {
                    "model": value["display_name"],
                    "model_key": key,
                    "split": split,
                    "accuracy": round(m["accuracy"], 4),
                    "precision_weighted": round(m["precision_weighted"], 4),
                    "recall_weighted": round(m["recall_weighted"], 4),
                    "f1_weighted": round(m["f1_weighted"], 4),
                    "f1_macro": round(m["f1_macro"], 4),
                }
            )
    pd.DataFrame(rows).to_csv(METRICS_CSV_PATH, index=False)

    _write_figures(results, selected_key)
    _write_report_tables(metadata)

    print("\nArtifacts written:")
    print(f"  {SELECTED_MODEL_PATH}")
    print(f"  {METRICS_JSON_PATH}")
    print(f"  {METRICS_CSV_PATH}")
    print(f"  {FIGURES}")
    print(f"Training finished in {metadata['training_seconds']}s")
    return metadata


def _write_figures(results: dict, selected_key: str) -> None:
    plt.style.use("dark_background")
    accent = "#8b5cf6"

    # Model comparison (test split)
    names = [results[k]["short_name"] for k in results]
    accuracy = [results[k]["test"]["accuracy"] for k in results]
    macro_f1 = [results[k]["test"]["f1_macro"] for k in results]
    weighted_f1 = [results[k]["test"]["f1_weighted"] for k in results]

    x = np.arange(len(names))
    width = 0.26
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width, accuracy, width, label="Accuracy", color="#8b5cf6")
    ax.bar(x, macro_f1, width, label="Macro F1", color="#22d3ee")
    ax.bar(x + width, weighted_f1, width, label="Weighted F1", color="#f59e0b")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("TruthLens AI - model comparison (test split)")
    ax.legend()
    for i, value in enumerate(accuracy):
        ax.text(i - width, value + 0.02, f"{value:.2f}", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "model_comparison.png", dpi=160)
    plt.close(fig)

    # Confusion matrices for every candidate
    for key, value in results.items():
        cm = np.array(value["test"]["confusion_matrix"])
        fig, ax = plt.subplots(figsize=(6, 5))
        disp = ConfusionMatrixDisplay(cm, display_labels=CLASS_NAMES)
        disp.plot(ax=ax, cmap="Purples", colorbar=False, values_format="d")
        ax.set_title(f"{value['display_name']} - test confusion matrix")
        plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
        fig.tight_layout()
        fig.savefig(FIGURES / f"confusion_{key}.png", dpi=160)
        plt.close(fig)

    # Class distribution
    dist = None
    for key in results:
        pass
    metadata = json.loads(METRICS_JSON_PATH.read_text(encoding="utf-8"))
    dist = metadata["dataset"]["class_distribution"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(list(dist.keys()), list(dist.values()), color=accent)
    ax.set_title("Dataset label distribution (all splits)")
    ax.set_ylabel("Statements")
    for bar, value in zip(bars, dist.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 40, str(value), ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "class_distribution.png", dpi=160)
    plt.close(fig)


def _write_report_tables(metadata: dict) -> None:
    """Human-readable metric tables for the report and viva."""
    lines = ["# TruthLens AI - evaluation results", ""]
    lines.append(f"Generated: {metadata['generated_at']}")
    lines.append(f"Selected model: **{metadata['selected_model_display_name']}** "
                 f"(criterion: {metadata['selection_criterion']})")
    lines.append("")
    lines.append("## Test-split comparison")
    lines.append("")
    lines.append("| Model | Accuracy | Precision (w) | Recall (w) | F1 (w) | F1 (macro) |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for value in metadata["candidates"].values():
        m = value["test"]
        lines.append(
            f"| {value['display_name']} | {m['accuracy']:.4f} | {m['precision_weighted']:.4f} | "
            f"{m['recall_weighted']:.4f} | {m['f1_weighted']:.4f} | {m['f1_macro']:.4f} |"
        )
    lines.append("")
    lines.append("## Per-class metrics of the selected model (test split)")
    lines.append("")
    lines.append("| Class | Precision | Recall | F1 | Support |")
    lines.append("| --- | --- | --- | --- | --- |")
    for cls, m in metadata["selected_model_metrics"]["per_class"].items():
        lines.append(
            f"| {cls} | {m['precision']:.4f} | {m['recall']:.4f} | "
            f"{m['f1']:.4f} | {m['support']} |"
        )
    lines.append("")
    lines.append("Confusion matrix (rows = actual, columns = predicted):")
    lines.append("")
    lines.append("| Actual \\ Predicted | " + " | ".join(CLASS_NAMES) + " |")
    lines.append("| --- |" + " --- |" * len(CLASS_NAMES))
    for cls, row in zip(CLASS_NAMES, metadata["selected_model_metrics"]["confusion_matrix"]):
        lines.append(f"| {cls} | " + " | ".join(str(v) for v in row) + " |")
    lines.append("")
    (PROJECT_ROOT / "results" / "EVALUATION_RESULTS.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


if __name__ == "__main__":
    train()
