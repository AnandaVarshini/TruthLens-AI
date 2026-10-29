# Troubleshooting — TruthLens AI

## Python / environment

### `'python' is not recognized`
Install Python 3.10+ from python.org and enable **“Add python.exe to PATH”**. Reopen the terminal.

### PowerShell: “running scripts is disabled on this system”
Activation of the venv is blocked by execution policy. Either use **Command Prompt**, or in the same
PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### `pip install` fails building `numpy` / `scipy` / `scikit-learn` on Python 3.14
New Python releases sometimes lack pre-built wheels. Install Python 3.12 alongside your current
version (do not uninstall 3.14), then:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'src'`
The shared package is at the project root.

* Backend: start it from the `backend/` folder — `app/__init__.py` adds the project root to `sys.path`.
* Scripts: run from the project root — `python scripts/train_models.py`.
* Notebooks: the first cell resolves the root automatically; make sure the working directory is
  `notebooks/` or the project root.

## Model and predictions

### Backend log: “Model NOT ready”
`models/truthlens_pipeline.joblib` or `results/metrics.json` is missing. From the project root:

```bat
python scripts/train_models.py
```

Then stop and restart `uvicorn`.

### `503` on `/api/predict` with “created with a different scikit-learn version”
scikit-learn pickles are not guaranteed across versions. Retrain in the same environment:

```bat
pip install -r requirements.txt
python scripts/train_models.py
```

### Every prediction is “Partially False”
That is the majority class (37 %) and the model is genuinely weak — this is the measured behaviour
of the four-class task, not a broken install. Verify with:

```bat
python -m pytest backend/tests -q
```

and read `results/EVALUATION_RESULTS.md`. The class-score bars should still differ per input; if all
four are exactly 0.25 for every text, the model file is corrupt → retrain.

### `joblib` raises `ModuleNotFoundError` for a `src.truthlens` symbol
Start from the correct folder (see the `ModuleNotFoundError: src` section). The pipeline pickle
references functions from `src/truthlens/preprocessing.py`.

## Backend

### `'uvicorn' is not recognized`
The venv is not activated or uvicorn is not installed:

```bat
.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### `[Errno 10048] address already in use`
Port 8000 is busy. Run on 8001:

```bat
uvicorn app.main:app --reload --port 8001
```

If you use the Vite dev server, point it at the new port:

```bat
set VITE_PROXY_TARGET=http://127.0.0.1:8001
npm run dev
```

### `sqlite3.OperationalError: unable to open database file`
The `backend/` folder is not writable, or `TRUTHLENS_DB_PATH` points somewhere invalid. Set:

```bat
set TRUTHLENS_DB_PATH=%CD%\backend\truthlens.db
```

### Forgotten password / want a clean database
Accounts are stored in `backend/truthlens.db`. Stop the backend, delete that file, restart, and
register again. (There is no password-reset flow in this academic project.)

### CORS error in the browser
Add the exact origin you are using to `TRUTHLENS_CORS_ORIGINS` in `.env`
(e.g. `http://localhost:5173`) and restart the backend. Serve the UI from `localhost` or
`127.0.0.1` consistently — mixing them counts as different origins for CORS.

### `TRUTHLENS_SECRET_KEY is not set` warning
Set it in `.env` (see `.env.example`) and restart. Tokens signed with the development key are fine
locally but must never be used in a shared deployment.

## Frontend

### “Cannot reach the backend”
* Is uvicorn running? Open <http://localhost:8000/api/health>.
* Is the frontend on a different port? Ensure `vite.config.js` proxies `/api` to port 8000.
* If the backend is on another port, set `VITE_PROXY_TARGET`.

### `npm install` errors
* Use Node.js 20+ (`node --version`).
* Delete `frontend\node_modules` and `frontend\package-lock.json`, then retry.
* Corporate proxy/offline? Use a normal internet connection — no paid registry is needed.

### Blank page at `localhost:8000`
The SPA is only served if `frontend/dist` exists. Rebuild it:

```bat
cd frontend
npm install
npm run build
```

then restart the backend.

### Refreshing `/dashboard` returns 404
Deep-link fallback is served by the backend only when `frontend/dist` exists. With the Vite dev
server this is handled automatically.

## Notebooks

### `FileNotFoundError: results/metrics.json` in A5
Run once from the project root:

```bat
python scripts/train_models.py
```

### `ModuleNotFoundError: No module named 'sklearn'` inside Jupyter
The notebook is using a different kernel. Register the venv:

```bat
pip install ipykernel
python -m ipykernel install --user --name truthlens --display-name "Python (TruthLens)"
```

Then choose **Kernel → Change kernel → Python (TruthLens)**.

### Notebook runs very slowly on A3
The Random Forest trains 200 trees over ~120k sparse features (≈20–45 s each configuration). This is
expected; A1/A2/A4 finish in seconds.

## Data

### `ValueError: Dataset is missing required columns`
You replaced `data/cleaned_dataset.csv`. Restore the supplied file with columns
`text, label, raw_label, split` (see `data/README.md`).

### `LabelValidationError: rows have a label that disagrees with the documented mapping`
The CSV was edited. Either restore the original file or update
`LABEL_MAPPING` in `src/truthlens/config.py` — but keep the mapping consistent with your report.
