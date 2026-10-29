#!/usr/bin/env bash
# TruthLens AI - helper for macOS / Linux users (Windows users: use the .bat files).
set -euo pipefail
cd "$(dirname "$0")"

case "${1:-}" in
  backend)
    cd backend
    exec python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    ;;
  frontend)
    cd frontend
    [ -d node_modules ] || npm install
    exec npm run dev
    ;;
  train)
    exec python3 scripts/train_models.py
    ;;
  test)
    exec python3 -m pytest backend/tests -q
    ;;
  *)
    echo "Usage: ./start.sh {backend|frontend|train|test}"
    exit 1
    ;;
esac
