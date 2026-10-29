"""Central project configuration (paths, labels, model constants).

All paths are derived from the project root so the project works on any
machine (Windows, macOS, Linux) without editing absolute paths.
"""
from __future__ import annotations

from pathlib import Path

# src/truthlens/config.py -> parents[2] == project root (TruthLens-AI/)
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

DATA_DIR: Path = PROJECT_ROOT / "data"
DATASET_PATH: Path = DATA_DIR / "cleaned_dataset.csv"

MODELS_DIR: Path = PROJECT_ROOT / "models"
CANDIDATES_DIR: Path = MODELS_DIR / "candidates"
SELECTED_MODEL_PATH: Path = MODELS_DIR / "truthlens_pipeline.joblib"
MODEL_METADATA_PATH: Path = MODELS_DIR / "model_metadata.json"

RESULTS_DIR: Path = PROJECT_ROOT / "results"
FIGURES_DIR: Path = RESULTS_DIR / "figures"
METRICS_JSON_PATH: Path = RESULTS_DIR / "metrics.json"
METRICS_CSV_PATH: Path = RESULTS_DIR / "metrics.csv"

RANDOM_STATE: int = 42
TEST_SIZE: float = 0.20  # only used if a predefined split is unusable

# Display order of the four reliability categories.
CLASS_NAMES: list[str] = ["Real", "Misleading", "Partially False", "Fake"]

# Original PolitiFact (LIAR) six-point scale -> four project categories.
LABEL_MAPPING: dict[str, str] = {
    "true": "Real",
    "mostly-true": "Misleading",
    "half-true": "Partially False",
    "barely-true": "Partially False",
    "false": "Fake",
    "pants-fire": "Fake",
}

# Short, human-readable meaning of each category (used in docs / frontend).
CLASS_DESCRIPTIONS: dict[str, str] = {
    "Real": "The statement is rated accurate; the available evidence supports the claim.",
    "Misleading": "The statement is mostly accurate but omits context or overstates the case.",
    "Partially False": "Part of the claim is accurate and part is false or unsupported.",
    "Fake": "The statement is false or fabricated; the evidence contradicts the claim.",
}

TFIDF_WORD_PARAMS: dict = dict(
    analyzer="word",
    ngram_range=(1, 2),
    min_df=2,
    max_features=60_000,
    sublinear_tf=True,
    strip_accents="unicode",
    stop_words="english",
    lowercase=True,
)

TFIDF_CHAR_PARAMS: dict = dict(
    analyzer="char_wb",
    ngram_range=(3, 5),
    min_df=3,
    max_features=60_000,
    sublinear_tf=True,
    strip_accents="unicode",
    lowercase=True,
)


def ensure_directories() -> None:
    """Create every directory the pipeline writes to."""
    for path in (MODELS_DIR, CANDIDATES_DIR, RESULTS_DIR, FIGURES_DIR):
        path.mkdir(parents=True, exist_ok=True)
