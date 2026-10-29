"""Text cleaning used by training *and* inference.

The same function must be applied on both sides; otherwise the vectorizer sees
different token distributions at prediction time. It is intentionally simple,
deterministic and dependency-free.
"""
from __future__ import annotations

import html
import re

URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
NON_ALPHA_RE = re.compile(r"[^a-z\s]")
WHITESPACE_RE = re.compile(r"\s+")

MAX_INPUT_CHARS = 5000


def preprocess_text(text: str) -> str:
    """Lowercase, strip URLs/HTML/punctuation/digits and collapse whitespace.

    Stop-word removal is deliberately left to the TF-IDF vectorizer so the exact
    same stop-word list is stored inside the saved pipeline.
    """
    if text is None:
        return ""
    text = html.unescape(str(text)).lower()
    text = URL_RE.sub(" ", text)
    text = HTML_TAG_RE.sub(" ", text)
    text = NON_ALPHA_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def validate_input_text(text: str) -> tuple[bool, str]:
    """Return ``(ok, message)`` for a user-supplied statement before prediction."""
    if text is None or not str(text).strip():
        return False, "Please enter a news claim before requesting a prediction."
    text = str(text).strip()
    if len(text) < 10:
        return False, "The statement is too short to analyse (minimum 10 characters)."
    if len(text) > MAX_INPUT_CHARS:
        return False, f"The statement is too long (maximum {MAX_INPUT_CHARS} characters)."
    if not preprocess_text(text).strip():
        return False, "The statement contains no usable words after text cleaning."
    return True, ""
