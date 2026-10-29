"""Label mapping and validation for the LIAR four-class task."""
from __future__ import annotations

import pandas as pd

from .config import CLASS_NAMES, LABEL_MAPPING


class LabelValidationError(ValueError):
    """Raised when the dataset contains labels outside the documented mapping."""


def map_raw_label(raw_label: str) -> str:
    """Map one PolitiFact rating to a project category.

    Raises:
        LabelValidationError: if the rating is not part of the documented scale.
    """
    key = str(raw_label).strip().lower()
    if key not in LABEL_MAPPING:
        raise LabelValidationError(
            f"Unknown raw label {raw_label!r}. Expected one of {sorted(LABEL_MAPPING)}."
        )
    return LABEL_MAPPING[key]


def add_mapped_label(df: pd.DataFrame, raw_column: str = "raw_label") -> pd.DataFrame:
    """Return a copy of ``df`` with an ``expected_label`` column derived from the raw rating.

    This is used as a consistency check against the supplied ``label`` column so a
    wrong mapping can never silently pass through training.
    """
    out = df.copy()
    out["expected_label"] = out[raw_column].map(lambda v: map_raw_label(v))
    return out


def validate_label_column(df: pd.DataFrame) -> dict:
    """Validate that ``label`` matches the documented mapping and return a summary."""
    checked = add_mapped_label(df)
    mismatches = checked[checked["label"] != checked["expected_label"]]
    if len(mismatches):
        preview = mismatches[["text", "raw_label", "label", "expected_label"]].head(5)
        raise LabelValidationError(
            f"{len(mismatches)} rows have a label that disagrees with the documented "
            f"mapping:\n{preview.to_string(index=False)}"
        )
    counts = checked["label"].value_counts().reindex(CLASS_NAMES, fill_value=0)
    return {name: int(counts[name]) for name in CLASS_NAMES}
