"""Dataset loading, validation and leakage-safe split handling."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .config import CLASS_NAMES, DATASET_PATH, RANDOM_STATE, TEST_SIZE
from .labels import validate_label_column
from .preprocessing import preprocess_text

REQUIRED_COLUMNS = {"text", "label", "raw_label", "split"}


@dataclass
class DatasetBundle:
    """Container for the three splits plus an auditable loading report."""

    train: pd.DataFrame
    valid: pd.DataFrame
    test: pd.DataFrame
    report: dict = field(default_factory=dict)

    @property
    def all_rows(self) -> int:
        return len(self.train) + len(self.valid) + len(self.test)


def _normalise_key(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower()


def load_dataset(path: str | None = None) -> DatasetBundle:
    """Load and validate ``data/cleaned_dataset.csv``.

    Steps
    -----
    1. Read the CSV and check the required columns exist.
    2. Drop rows with missing/blank text or an unknown label (reported, not hidden).
    3. Verify the supplied four-class label agrees with the documented mapping.
    4. Remove exact duplicate statements *across* splits so the test set can never
       contain a statement the model has already memorised from training.
    5. Use the dataset's own train/valid/test partitions (no re-splitting).
    """
    csv_path = path or str(DATASET_PATH)
    df = pd.read_csv(csv_path)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing_columns)}. "
            f"Found: {list(df.columns)}"
        )

    initial_rows = len(df)
    df = df.dropna(subset=["text", "label", "raw_label", "split"])
    df = df[df["text"].astype(str).str.strip() != ""]
    df = df[df["raw_label"].astype(str).str.strip().str.lower() != ""]
    df["label"] = df["label"].astype(str).str.strip()
    df["raw_label"] = df["raw_label"].astype(str).str.strip().str.lower()
    df = df[df["label"].isin(CLASS_NAMES)]
    cleaned_rows = len(df)

    class_counts = validate_label_column(df)

    df["split"] = df["split"].astype(str).str.strip().str.lower()
    df["text_key"] = _normalise_key(df["text"])

    # Cross-split duplicate removal: keep the copy from the earliest split.
    split_priority = {"train": 0, "valid": 1, "test": 2}
    df["_priority"] = df["split"].map(split_priority).fillna(9).astype(int)
    df = df.sort_values("_priority", kind="stable")
    duplicates_before = int(df.duplicated(subset=["text_key"]).sum())
    df = df.drop_duplicates(subset=["text_key"], keep="first")

    train = df[df["split"] == "train"].copy()
    valid = df[df["split"] == "valid"].copy()
    test = df[df["split"] == "test"].copy()

    if len(train) < 100 or len(valid) < 30 or len(test) < 30:
        # The pre-defined split is unusable: fall back to a reproducible split.
        df = df.sample(frac=1.0, random_state=RANDOM_STATE)
        train = df.sample(frac=0.80, random_state=RANDOM_STATE)
        remaining = df.drop(train.index)
        valid = remaining.sample(frac=0.50, random_state=RANDOM_STATE)
        test = remaining.drop(valid.index)
        fallback = True
    else:
        fallback = False

    for part in (train, valid, test):
        part["model_text"] = part["text"].map(preprocess_text)
        part.drop(columns=[c for c in ("_priority", "text_key") if c in part], inplace=True)

    report = {
        "source_file": csv_path,
        "initial_rows": initial_rows,
        "rows_after_basic_cleaning": cleaned_rows,
        "duplicate_rows_removed": duplicates_before,
        "duplicates_inside_train": int(train["text"].duplicated().sum()),
        "split_fallback_used": fallback,
        "split_counts": {
            "train": int(len(train)),
            "valid": int(len(valid)),
            "test": int(len(test)),
        },
        "class_distribution": class_counts,
        "class_distribution_by_split": {
            name: {cls: int((part["label"] == cls).sum()) for cls in CLASS_NAMES}
            for name, part in (("train", train), ("valid", valid), ("test", test))
        },
    }
    return DatasetBundle(train=train, valid=valid, test=test, report=report)


def rebuild_test_set_from_file(path: str | None = None) -> DatasetBundle:
    """Convenience wrapper used by notebooks/tests."""
    return load_dataset(path)


__all__ = ["DatasetBundle", "load_dataset", "TEST_SIZE", "RANDOM_STATE"]
