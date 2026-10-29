# TruthLens AI — Fake News Detection System Using Machine Learning

A complete, locally runnable full-stack application that classifies a news claim into one of four
reliability levels — **Real**, **Misleading**, **Partially False**, **Fake** — using TF-IDF features
and four classical machine-learning algorithms trained on the **LIAR** benchmark dataset.

* **Frontend:** React 19 + Vite + custom dark navy / purple design system, Recharts
* **Backend:** Python FastAPI, SQLAlchemy, SQLite, JWT authentication, bcrypt password hashing
* **ML:** scikit-learn Pipelines (word + character TF-IDF), Logistic Regression, Linear SVM,
  Random Forest, Multinomial Naive Bayes
* **Notebooks:** five runnable notebooks (A1–A5) with executed outputs
* **No cloud, no paid API, no Docker required.** Predictions are computed locally by the trained
  model; no third-party AI service is called.

---

## ⚠️ Read this first: about "100 % accuracy"

The supplied dataset is the four-class LIAR task. On this benchmark, honest TF-IDF + classical-model
accuracy is around **35–40 %** (a random guess is 25 %). That is expected: the classes overlap
(“half-true” vs “barely-true”), statements are short, and the dataset is imbalanced.

**No legitimate model reaches 100 % accuracy on this data.** Any project claiming 100 % here is
either leaking the test set, evaluating on training rows, or inventing numbers. This project reports
only measured results and never hardcodes a prediction. What *is* 100 % verified here is that the
project **works end to end** — training, model loading, registration, login, prediction, history,
dashboard, model insights and the API tests all run and were executed (see
[`docs/TESTING.md`](docs/TESTING.md)).

Measured test-split results from this build:

| Model | Accuracy | Precision (w) | Recall (w) | F1 (w) | F1 (macro) |
| --- | --- | --- | --- | --- | --- |
| **Logistic Regression (deployed)** | **0.3784** | 0.3613 | 0.3784 | 0.3590 | 0.3231 |
| Multinomial Naive Bayes | 0.3581 | 0.3515 | 0.3581 | 0.3538 | 0.3278 |
| Random Forest | 0.3745 | 0.3502 | 0.3745 | 0.2982 | 0.2383 |
| Linear SVM | 0.3440 | 0.3342 | 0.3440 | 0.3374 | 0.3087 |

The deployed model is chosen by **highest macro-F1 on the validation split** and evaluated once on
the untouched test split. Full detail: [`results/EVALUATION_RESULTS.md`](results/EVALUATION_RESULTS.md)
and [`docs/EVALUATION.md`](docs/EVALUATION.md).

---

## 1. What is included

```
TruthLens-AI/
├─ README.md                     ← this file
├─ QUICKSTART.md                 ← one-page start guide
├─ requirements.txt              ← all Python dependencies (training + API + notebooks)
├─ .env.example                  ← environment template (no secrets)
├─ start_backend.bat             ← Windows one-click backend
├─ start_frontend.bat            ← Windows one-click frontend
├─ start.sh                      ← macOS/Linux helper
│
├─ data/
│  ├─ cleaned_dataset.csv        ← your LIAR dataset (12,836 statements, unchanged)
│  └─ README.md                  ← provenance, columns, label mapping, counts
│
├─ src/truthlens/                ← shared ML code used by scripts, notebooks and the API
│  ├─ config.py                  ← paths, classes, label mapping, TF-IDF settings
│  ├─ preprocessing.py           ← text cleaning (identical in training and inference)
│  ├─ labels.py                  ← label mapping + validation
│  ├─ data.py                    ← dataset loading, auditing, leakage-safe splits
│  └─ pipeline.py                ← feature union, model factories, metrics
│
├─ scripts/
│  └─ train_models.py            ← train → tune → evaluate → export everything
│
├─ notebooks/
│  ├─ A1_Logistic_Regression_Fake_News_Detection.ipynb
│  ├─ A2_SVM_Fake_News_Detection.ipynb
│  ├─ A3_Random_Forest_Fake_News_Detection.ipynb
│  ├─ A4_Naive_Bayes_Fake_News_Detection.ipynb
│  ├─ A5_Model_Comparison_and_Final_Evaluation.ipynb
│  └─ reference_originals/       ← the submitted notebooks, kept for history only
│
├─ models/
│  ├─ truthlens_pipeline.joblib  ← deployed pipeline (TF-IDF + Logistic Regression)
│  ├─ candidates/*.joblib        ← all four fitted candidate pipelines
│  └─ model_metadata.json
│
├─ results/
│  ├─ metrics.json               ← every metric shown in the UI (computed, not typed)
│  ├─ metrics.csv
│  ├─ EVALUATION_RESULTS.md
│  └─ figures/*.png              ← confusion matrices, comparison chart, class distribution
│
├─ backend/
│  ├─ requirements.txt
│  ├─ app/
│  │  ├─ main.py                 ← FastAPI app, CORS, static frontend, error handling
│  │  ├─ config.py               ← env vars and paths
│  │  ├─ database.py             ← SQLite + SQLAlchemy session
│  │  ├─ models.py               ← users, predictions
│  │  ├─ schemas.py              ← Pydantic request/response models
│  │  ├─ security.py             ← bcrypt hashing + JWT
│  │  ├─ deps.py                 ← authenticated-user dependency
│  │  ├─ ml_service.py           ← loads the pipeline once, runs predictions
│  │  └─ routers/                ← auth.py, predictions.py, insights.py
│  └─ tests/                     ← 9 pytest API tests
│
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.js             ← /api proxy to the backend
│  ├─ index.html
│  ├─ public/favicon.svg
│  ├─ dist/                      ← pre-built production UI (optional, already built)
│  └─ src/
│     ├─ main.jsx, App.jsx, styles.css
│     ├─ components/             ← Layout, ProtectedRoute, UI helpers
│     ├─ lib/                    ← api client, auth context, constants
│     └─ pages/                  ← Home, Register, Login, Dashboard, Detect, History,
│                                  Insights, Profile
│
└─ docs/
   ├─ ARCHITECTURE.md
   ├─ METHODOLOGY.md
   ├─ EVALUATION.md
   ├─ API.md
   ├─ TESTING.md
   ├─ TROUBLESHOOTING.md
   ├─ VIVA_GUIDE.md
   └─ reference/ML_DOCUMENT_FINAL_project_report.docx
```

### Feature checklist

| Requirement | Status |
| --- | --- |
| Home / landing page | ✅ |
| Registration with validation + duplicate prevention | ✅ |
| Login with hashed passwords + JWT | ✅ |
| User dashboard with real saved data | ✅ |
| Fake-news detection page calling the real model | ✅ |
| Prediction history with pagination + delete | ✅ |
| Model insights with real metrics, confusion matrix, comparison | ✅ |
| Profile + secure logout | ✅ |
| Protected backend endpoints and user-scoped data | ✅ |
| SQLite database, auto-created | ✅ |
| Swagger/OpenAPI docs | ✅ `/docs` |
| Four trained algorithms + saved artifacts | ✅ |
| Five runnable notebooks | ✅ |
| API tests | ✅ 9 passing |
| Frontend production build | ✅ |

---

## 2. Quick start on Windows 11 (VS Code)

> Every command below is exact and matches this folder structure. Use **Command Prompt** or
> **PowerShell** — both work.

### Step 0 — Check your tools

Open a terminal in VS Code (``Ctrl + ` ``) and run:

```bat
python --version
pip --version
node --version
npm --version
git --version
```

You need Python 3.10+ and Node.js 18+ (Node 20+ recommended).

### Step 1 — Extract the ZIP and open the folder

1. Right-click the ZIP → **Extract All…** (avoid running inside the ZIP preview).
2. In VS Code: **File → Open Folder…** → select the `TruthLens-AI` folder (the one that contains
   `README.md`, `backend`, `frontend`).
3. Open a terminal with ``Ctrl + ` ``. The prompt should end in `\TruthLens-AI`.

### Step 2 — Create and activate a virtual environment

**Command Prompt:**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation with an execution-policy error, either use Command Prompt, or run
once in the same window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Your prompt should now start with `(.venv)`.

### Step 3 — Install Python dependencies

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs the API, ML and notebook dependencies. It takes a few minutes the first time.

> **Python 3.14 note:** the project code is compatible with 3.14, but some third-party wheels may
> lag behind a brand-new Python release. If `pip install` fails on `scikit-learn`, `numpy`, `scipy`
> or `pandas`, install **Python 3.12 alongside your existing Python** (python.org installer, tick
> “Add to PATH” but keep your 3.14), then create the venv explicitly with it:
> `py -3.12 -m venv .venv`. Your existing Python installation is not modified. Do **not** uninstall
> Python 3.14.
>
> This project was trained and tested here with Python 3.11.2, scikit-learn 1.9.1, pandas 3.0.5,
> NumPy 2.4.6, SciPy 1.17.1.

### Step 4 — Configure environment variables (optional but recommended)

```bat
copy .env.example .env
```

Open `.env` and replace `TRUTHLENS_SECRET_KEY` with a long random string (32+ characters). If you
skip this step the app still runs with a clearly-marked development key.

### Step 5 — Prepare the data

Nothing to do — `data/cleaned_dataset.csv` is already in place and the app/training scripts use
relative paths. To confirm it is readable:

```bat
python -c "import pandas as pd; d=pd.read_csv('data/cleaned_dataset.csv'); print(d.shape, d['label'].value_counts().to_dict())"
```

Expected: `(12836, 11)` and four labels.

### Step 6 — Train and evaluate the models (optional — artifacts are already included)

The trained pipelines in `models/` are included so you can run the app immediately. To regenerate
them from scratch (about 1–2 minutes):

```bat
python scripts/train_models.py
```

This will:

1. audit the dataset (labels, missing text, 26 cross-split duplicates),
2. train all four algorithms on the training split,
3. tune on the validation split,
4. select the deployed model by validation macro-F1,
5. evaluate once on the test split,
6. rewrite `models/` and `results/` (metrics JSON/CSV, charts, `EVALUATION_RESULTS.md`).

### Step 7 — Initialise the database

The database is created automatically on backend startup. To create it explicitly:

```bat
python -c "import sys; sys.path.insert(0,'backend'); from app.database import init_db; init_db(); print('Database ready')"
```

### Step 8 — Start the backend

```bat
cd backend
uvicorn app.main:app --reload --port 8000
```

Expected log lines:

```
INFO | truthlens | Model ready: Logistic Regression (A1)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal running.

### Step 9 — Open the application

**Fastest option (no frontend install needed):** the ZIP already contains the built frontend, and
FastAPI serves it automatically.

* App: **<http://localhost:8000>**
* API docs (Swagger): **<http://localhost:8000/docs>**
* Health check: **<http://localhost:8000/api/health>**

**Developer option (React dev server with hot reload):** open a **second** terminal in the project
root:

```bat
cd frontend
npm install
npm run dev
```

Then open **<http://localhost:5173>**. Vite proxies `/api` to `http://127.0.0.1:8000`.

> Use one option at a time for the UI, but keep the backend running in both cases.

### Step 10 — Create an account and make a prediction

1. Click **Get started** → fill in name, email and a password (min. 8 characters, confirmed).
2. You are logged in and redirected to the dashboard (empty at first — by design).
3. Open **Detect**, paste a claim, click **Predict category**.
4. The result shows the category, all four class scores, model name and timestamp.
5. Check **Dashboard** and **History** — they now show your real saved records.
6. Open **Model Insights** for the measured evaluation of all four algorithms.
7. **Profile → Log out** ends the session.

### Step 11 — Run the notebooks (optional)

```bat
pip install jupyter
jupyter notebook
```

In the browser, open the `notebooks/` folder and run any `A1`–`A5` notebook from top to bottom
(**Kernel → Restart & Run All**). They expect to be started from the `notebooks/` folder and resolve
the project root automatically.

### Step 12 — Run the tests (optional)

```bat
python -m pytest backend/tests -q
```

Expected: `9 passed`.

### Step 13 — Stop everything

Press `Ctrl + C` in the backend terminal and, if used, in the frontend terminal. Deactivate the venv
with `deactivate`.

---

## 3. First-run verification checklist

| Check | Expected |
| --- | --- |
| `http://localhost:8000/api/health` | `{"status":"ok","model_ready":true,...}` |
| `http://localhost:8000/docs` | Swagger UI lists Auth, Predictions, Model insights |
| Register with the same email twice | Second attempt returns “An account with this email already exists.” |
| Wrong password | “Incorrect email or password.” |
| Detect with empty input | Inline validation, no request sent |
| Detect with a real claim | A category + four scores + timestamp |
| Open History in a private window as another user | Empty — histories are isolated |
| Stop the backend and click Predict | Clear “Cannot reach the backend…” message |

---

## 4. How a prediction flows through the system

```
Browser (Detect page)
   │  POST /api/predict  { text }  + Bearer JWT
   ▼
FastAPI (backend/app/routers/predictions.py)
   │  validates token, validates text (10–5000 chars)
   ▼
ModelService (backend/app/ml_service.py)  ← loads models/truthlens_pipeline.joblib ONCE
   │  preprocess_text(text) → TF-IDF (word 1–2 + char 3–5) → Logistic Regression
   ▼
Prediction saved in SQLite (predictions table) → JSON response
   ▼
React renders category, class probabilities, model name, timestamp
```

The same `preprocess_text` and the same pipeline object are used in training, notebooks and the API,
so preprocessing cannot drift between them.

---

## 5. API summary

| Method | Endpoint | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/health` | No | Service + model status |
| POST | `/api/auth/register` | No | Create account, returns JWT |
| POST | `/api/auth/login` | No | Log in, returns JWT |
| GET | `/api/auth/me` | Yes | Current profile |
| POST | `/api/predict` | Yes | Classify a claim |
| GET | `/api/predictions` | Yes | Paginated history (own only) |
| GET | `/api/predictions/stats` | Yes | Dashboard counters + recent |
| DELETE | `/api/predictions/{id}` | Yes | Delete one own prediction |
| DELETE | `/api/predictions` | Yes | Clear own history |
| GET | `/api/insights` | No | Full computed evaluation record |
| GET | `/api/model-info` | No | Compact model metadata |

Examples and schemas: [`docs/API.md`](docs/API.md).

---

## 6. Machine-learning design (short version)

* **Input:** the statement text only (`text`), cleaned by `preprocess_text`.
* **Features:** word TF-IDF (1–2 grams, `min_df=2`, 60k) **+** character `char_wb` TF-IDF
  (3–5 grams, `min_df=3`, 60k), concatenated in a `FeatureUnion` inside the pipeline.
* **Split:** the dataset’s predefined train (10,252) / validation (1,279) / test (1,279) partitions.
  26 exact duplicate statements were removed across splits to prevent leakage.
* **Tuning:** small grids per algorithm, scored on the validation split only.
* **Selection:** highest validation macro-F1 → Logistic Regression (`C=1.0`, no class weighting).
* **Final report:** one evaluation on the untouched test split (accuracy 0.3784, macro-F1 0.3231).
* **Artifacts:** every candidate saved under `models/candidates/`; the deployed pipeline at
  `models/truthlens_pipeline.joblib`.

Full reasoning and metric definitions: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

---

## 7. Changes made to the original files (and why)

The four original notebooks referenced `fake_or_real_news.csv` (a **binary** REAL/FAKE dataset) and
one used KNN, while the project report and the supplied dataset describe a **four-class LIAR** task.
That mismatch would have made the results inconsistent with the report and the web application.

What was corrected:

1. **Dataset alignment** — all corrected notebooks and the application use your supplied
   `cleaned_dataset.csv` and its four-class labels.
2. **Label mapping validation** — `true → Real`, `mostly-true → Misleading`,
   `half-true`/`barely-true → Partially False`, `false`/`pants-fire → Fake`, verified row by row.
3. **Leakage fixes** — vectorizers are fitted inside pipelines on training data only; 26 cross-split
   duplicate statements were removed; test data is never used for tuning.
4. **Algorithm correction** — the fourth algorithm is Multinomial Naive Bayes (A4), as in the report,
   not KNN.
5. **Honest metrics** — recomputed from the real data; no number is hardcoded or copied.
6. **Missing-value / blank-text handling and reproducible seeds** — added and documented.
7. **Full-stack application added** — the report only proposed a UI; this project implements it.

The original notebooks are preserved unchanged in `notebooks/reference_originals/` for transparency.

---

## 8. Troubleshooting (most common issues)

| Symptom | Fix |
| --- | --- |
| `'uvicorn' is not recognized` | Activate the venv, then `python -m uvicorn app.main:app --reload --port 8000` from `backend/` |
| `Model NOT ready` in the backend log | Run `python scripts/train_models.py` from the project root, then restart the API |
| `ModuleNotFoundError: No module named 'src'` | Start the backend from `backend/` (the app adds the project root), or run scripts from the project root |
| Predictions fail with 503 | The artifact is missing or was saved by a different scikit-learn version → retrain |
| Frontend shows “Cannot reach the backend” | Start the backend on port 8000; check `http://localhost:8000/api/health` |
| `npm install` fails | Use Node.js 20+; delete `frontend/node_modules` and retry |
| Port 8000 already in use | `uvicorn app.main:app --reload --port 8001` and set `VITE_PROXY_TARGET` accordingly |
| PowerShell blocks venv activation | Use Command Prompt, or `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| Password rejected at login after re-creating the DB | Accounts live in `backend/truthlens.db`; delete the file to reset, then register again |
| `sqlite3.OperationalError: unable to open database file` | Ensure the `backend/` folder is writable, or set `TRUTHLENS_DB_PATH` to a writable absolute path |

More: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

---

## 9. Limitations and responsible use

* Predictions are **statistical estimates**, not fact-checks. The app never claims a statement is
  proven true or false.
* The model was trained on short political statements from LIAR; long news articles, sarcasm, new
  vocabulary and breaking-news events are outside its training distribution.
* Accuracy is ~38 % on four classes; it is a screening aid, not an authority.
* Speaker metadata (party, state, job title) is deliberately **not** used as a feature, to avoid
  learning political bias instead of linguistic patterns.
* The system does not browse the web and does not use any external AI API.

---

## 10. Documentation index

| Document | Contents |
| --- | --- |
| [`QUICKSTART.md`](QUICKSTART.md) | One-page command sheet |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layers, data flow, database schema, security |
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | Dataset, preprocessing, features, protocol, metric definitions |
| [`docs/EVALUATION.md`](docs/EVALUATION.md) | Measured results, confusion matrices, interpretation |
| [`docs/API.md`](docs/API.md) | Endpoint reference with curl examples |
| [`docs/TESTING.md`](docs/TESTING.md) | Tests executed, exact outcomes, unverified items |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Detailed error resolution |
| [`docs/VIVA_GUIDE.md`](docs/VIVA_GUIDE.md) | Presentation script and likely questions |

---

**Academic project:** Fake News Detection System Using Machine Learning — Aditya University,
Department of Information Technology (Academic Year 2026–2027).
Refer to `docs/reference/ML_DOCUMENT_FINAL_project_report.docx` for the submitted report.
