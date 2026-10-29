# Testing & verification report — TruthLens AI

Everything below was **actually executed** while building this project. Commands are reproducible
from the project root. Anything not executed is listed explicitly in section 5.

## 1. Environment

| Item | Value |
| --- | --- |
| Python | 3.11.2 |
| scikit-learn | 1.9.1 |
| pandas | 3.0.5 |
| NumPy | 2.4.6 |
| SciPy | 1.17.1 |
| FastAPI | 0.162.0 |
| SQLAlchemy | 2.1.6 |
| Node.js | 24.21.0 |
| npm | 11.19.0 |
| Vite | 7.3.7 |

## 2. Backend API tests — `python -m pytest backend/tests -q`

**Result: 9 passed** (2.1 s). The suite uses a temporary SQLite database and the real trained model.

| # | Test | What it proves | Outcome |
| --- | --- | --- | --- |
| 1 | `test_health` | `/api/health` reports `model_ready: true` | PASS |
| 2 | `test_register_login_and_profile` | duplicate email → 409; wrong password → 401; correct login + `/me` | PASS |
| 3 | `test_register_rejects_mismatched_passwords` | confirmation mismatch → 422 | PASS |
| 4 | `test_protected_endpoints_require_token` | predict/history/stats → 401 without JWT | PASS |
| 5 | `test_prediction_returns_real_model_output` | label ∈ 4 classes, 4 scores summing to 1, model name present | PASS |
| 6 | `test_prediction_validation_and_errors` | blank text → 422; 10,000-char text → 422 | PASS |
| 7 | `test_history_is_user_scoped` | user B cannot see/delete user A's rows (404); owner can delete (204) | PASS |
| 8 | `test_dashboard_stats` | counts, 4 categories, model accuracy present | PASS |
| 9 | `test_insights_expose_computed_results` | confusion matrix, split counts, selected model present | PASS |

## 3. Machine-learning pipeline — `python scripts/train_models.py`

**Result: completed in ~84 s**, all artifacts regenerated.

| Check | Result |
| --- | --- |
| Dataset loads, 11 columns | PASS |
| Label mapping validation (row-by-row) | PASS — 0 mismatches |
| Duplicate removal across splits | PASS — 26 removed, 0 duplicates remain |
| Splits used | train 10,252 / valid 1,279 / test 1,279 |
| All four algorithms trained | PASS |
| Hyper-parameter selection on validation only | PASS |
| Test evaluation | accuracy 0.3784, macro-F1 0.3231 (Logistic Regression) |
| Artifacts written | `models/truthlens_pipeline.joblib` + 4 candidates + `model_metadata.json` |
| Metrics written | `results/metrics.json`, `metrics.csv`, `EVALUATION_RESULTS.md` |
| Figures written | 6 PNGs (4 confusion matrices, comparison, class distribution) |
| Artifact reload | PASS — identical predictions |

## 4. Notebooks — executed with `nbclient` (Restart & Run All)

| Notebook | Execution time | Outcome |
| --- | --- | --- |
| `A1_Logistic_Regression_Fake_News_Detection.ipynb` | 33.5 s | PASS, outputs stored |
| `A2_SVM_Fake_News_Detection.ipynb` | 11.6 s | PASS |
| `A3_Random_Forest_Fake_News_Detection.ipynb` | 46.4 s | PASS |
| `A4_Naive_Bayes_Fake_News_Detection.ipynb` | 7.5 s | PASS |
| `A5_Model_Comparison_and_Final_Evaluation.ipynb` | 3.0 s | PASS — artifact-vs-record assertion holds |

Notebook A5 contains the assertion:

```python
assert abs(live["accuracy"] - selected["test"]["accuracy"]) < 1e-6
```

It passed, proving the shipped artifact reproduces the recorded test accuracy.

## 5. Frontend

| Check | Command | Result |
| --- | --- | --- |
| Dependency install | `npm install` | PASS — 142 packages |
| Unit tests | `npx vitest run` | PASS — 5 tests |
| Production build | `npm run build` | PASS — 643 modules, 686 kB JS, 8.8 kB CSS |

Frontend unit tests cover the category definition (exact four labels), colour/description presence,
the six→four label-mapping table, and the date/percentage formatters.

## 6. End-to-end smoke test (real HTTP, real model)

Performed against `uvicorn app.main:app --port 8011` with a fresh SQLite file:

| Step | Request | Observed |
| --- | --- | --- |
| Health | `GET /api/health` | `200 {"status":"ok","model_ready":true,"model_name":"Logistic Regression (A1)"}` |
| Swagger | `GET /docs` | `200` |
| SPA root | `GET /` | `200` (built React app served by FastAPI) |
| SPA deep link | `GET /login` | `200` (SPA fallback) |
| Register | `POST /api/auth/register` | `201`, JWT returned |
| Predict | `POST /api/predict` | `201`, `label: "Partially False"`, 4 scores summing to 1.0 |
| Stats | `GET /api/predictions/stats` | `200`, totals updated from the saved row |

## 6b. Clean-environment dependency install

A **fresh virtual environment** was created and `pip install -r requirements.txt` was run in it,
resolving to Python 3.11.2 · scikit-learn 1.9.1 · pandas **3.1.0** · FastAPI 0.162.0. In that clean
environment:

| Check | Result |
| --- | --- |
| `pip install -r requirements.txt` | PASS (no version conflicts) |
| `pytest backend/tests -q` | PASS — 9 tests |
| Dataset load | PASS — 10,252 / 1,279 / 1,279 |
| Load shipped artifact + predict | PASS |

This confirms the version ranges in `requirements.txt` are not tied to the exact versions used to
train, as long as the scikit-learn **minor** version matches (retrain otherwise).

## 7. File and path checks

| Check | Result |
| --- | --- |
| All source files listed in the README exist | PASS |
| Dataset path relative, no absolute machine paths in code | PASS |
| Model artifact size sane (2.8 MB) and loadable with `joblib` | PASS |
| `models/`, `results/`, `data/` shipped with the project | PASS |
| `.env` and `*.db` excluded from the ZIP | PASS |
| `node_modules` and notebook scratch models excluded from the ZIP | PASS |

## 8. Not executed / unverified here

Be explicit with faculty about these:

1. **Windows execution.** Development and testing ran on Linux. The Windows instructions use standard
   `cmd`/PowerShell commands and `.bat` helpers, but were not physically run on Windows 11.
2. **Python 3.14.** Tested on 3.11. The requirements use version ranges to allow newer Pythons; if a
   wheel is unavailable for 3.14, use Python 3.12 in a separate venv (documented in the README).
3. **Browser-level UI automation.** No Playwright/Selenium run. The React app was built, unit-tested
   and its HTTP contract verified through the API and SPA-serving checks; manual UI clicks were not
   automated.
4. **Cross-version artifact loading.** The `.joblib` was produced by scikit-learn 1.9.1. If your
   installed version differs, retrain with `python scripts/train_models.py` (one command) — the code
   handles this case with a clear 503 error instead of crashing.

## 9. How to reproduce every check

```bat
python scripts/train_models.py
python -m pytest backend/tests -q
cd frontend && npm install && npx vitest run && npm run build
cd ..\backend && uvicorn app.main:app --reload --port 8000
:: open http://localhost:8000/docs and try the endpoints
```
