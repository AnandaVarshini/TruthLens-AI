"""TruthLens AI shared machine-learning package."""

from .config import CLASS_NAMES, CLASS_DESCRIPTIONS, LABEL_MAPPING
from .preprocessing import MAX_INPUT_CHARS, preprocess_text, validate_input_text

__all__ = [
    "CLASS_NAMES",
    "CLASS_DESCRIPTIONS",
    "LABEL_MAPPING",
    "MAX_INPUT_CHARS",
    "preprocess_text",
    "validate_input_text",
]
__version__ = "1.0.0"
