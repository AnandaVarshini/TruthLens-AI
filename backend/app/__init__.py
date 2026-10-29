"""TruthLens AI backend package."""

import sys
from pathlib import Path

# Make the shared ``src`` package importable when uvicorn is started from
# backend/ (uvicorn app.main:app) or from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
