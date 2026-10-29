# TruthLens AI — Quick Start (Windows)

```bat
:: 1. Open the extracted TruthLens-AI folder in VS Code, then:
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt

:: 2. Optional configuration
copy .env.example .env
::    edit .env and set a long TRUTHLENS_SECRET_KEY

:: 3. Start the backend (keep this window open)
cd backend
uvicorn app.main:app --reload --port 8000

:: 4. Open the app
::    http://localhost:8000          <- application (pre-built UI is included)
::    http://localhost:8000/docs     <- Swagger API documentation
```

Create an account → **Detect** → paste a claim → **Predict category**.

## Optional commands

```bat
:: Retrain all four models and regenerate results (~1–2 min)
python scripts/train_models.py

:: Run the API tests (from the project root)
python -m pytest backend/tests -q

:: Run the React dev server instead of the pre-built UI (second terminal)
cd frontend
npm install
npm run dev        :: http://localhost:5173
```

## If something fails

* `'uvicorn' is not recognized` → activate `.venv` first, then use `python -m uvicorn ...`
* Backend log says **Model NOT ready** → run `python scripts/train_models.py`, restart the API
* `pip` cannot build `scikit-learn` on Python 3.14 → create the venv with Python 3.12:
  `py -3.12 -m venv .venv`
* Port already in use → change `--port 8000` to `--port 8001` (and set
  `VITE_PROXY_TARGET=http://127.0.0.1:8001` before `npm run dev`)

Full instructions: [`README.md`](README.md) · Detailed errors: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)
