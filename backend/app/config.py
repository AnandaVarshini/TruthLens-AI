"""Backend configuration.

Every path is derived from the project root so the API works from any folder.
Secrets are read from environment variables (see ``.env.example``); the fallback
development key is clearly marked and only intended for local use.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

# Optional .env files (project root first, then backend/ overrides).
load_dotenv(PROJECT_ROOT / ".env", override=False)
load_dotenv(BACKEND_DIR / ".env", override=False)

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
SELECTED_MODEL_PATH = MODELS_DIR / "truthlens_pipeline.joblib"
METRICS_JSON_PATH = RESULTS_DIR / "metrics.json"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

DB_PATH = Path(os.getenv("TRUTHLENS_DB_PATH", BACKEND_DIR / "truthlens.db"))
if not DB_PATH.is_absolute():
    DB_PATH = (PROJECT_ROOT / DB_PATH).resolve()

FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "TRUTHLENS_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173",
    ).split(",")
    if origin.strip()
]

SECRET_KEY = os.getenv("TRUTHLENS_SECRET_KEY", "dev-only-change-me-truthlens-local-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TRUTHLENS_TOKEN_MINUTES", "720"))
DEV_SECRET_IN_USE = "TRUTHLENS_SECRET_KEY" not in os.environ
MAX_TEXT_LENGTH = 5000
