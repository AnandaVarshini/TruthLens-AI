# Architecture — TruthLens AI

## 1. Layers

```
┌────────────────────────────────────────────────────────────────────────┐
│  Presentation (React 19 + Vite)                                        │
│  Home · Register · Login · Dashboard · Detect · History · Insights ·   │
│  Profile — routed with react-router, protected routes, auth context    │
└───────────────────────────────┬────────────────────────────────────────┘
                                │ JSON over HTTP (JWT Bearer)
┌───────────────────────────────▼────────────────────────────────────────┐
│  API (FastAPI)                                                         │
│  /api/auth/*   /api/predict   /api/predictions*   /api/insights        │
│  Pydantic validation · CORS · error handlers · static SPA fallback     │
└──────────────┬─────────────────────────────────┬───────────────────────┘
               │                                 │
┌──────────────▼──────────────┐   ┌──────────────▼───────────────────────┐
│  Persistence (SQLAlchemy)   │   │  Inference (scikit-learn Pipeline)   │
│  SQLite: users, predictions │   │  preprocess → TF-IDF → classifier    │
└─────────────────────────────┘   └──────────────┬───────────────────────┘
                                                 │
                                  ┌──────────────▼───────────────────────┐
                                  │  Artifacts on disk                   │
                                  │  models/truthlens_pipeline.joblib    │
                                  │  results/metrics.json                │
                                  └──────────────────────────────────────┘
```

Training/production share `src/truthlens/` (preprocessing, label mapping, pipeline builders), which is
what guarantees that inference sees exactly the data distribution the model was fitted on.

## 2. Backend request lifecycle (prediction)

1. `POST /api/predict` arrives with `Authorization: Bearer <jwt>`.
2. `deps.get_current_user` decodes the JWT, loads the user row, rejects invalid/expired tokens (401).
3. Pydantic validates the body (`text`: 1–5000 characters).
4. `validate_input_text` rejects blank/too-short/too-long/unusable text (422).
5. `model_service.predict` cleans the text and calls the **already-loaded** pipeline.
6. Scores are produced from `predict_proba` (Logistic Regression, Random Forest, Naive Bayes) or
   from `decision_function` normalised and labelled `decision_score` (LinearSVC). Raw decision
   values are never presented as probabilities.
7. The prediction row is written with `user_id` from the token — never from the request body.
8. The response contains the label, all four scores, model name and UTC timestamp.

## 3. Model reload policy

* The pipeline is loaded **lazily on first use**, guarded by a `threading.Lock`, and reused.
* It is never retrained inside a request.
* If the artifact is missing or incompatible with the installed scikit-learn, the service raises a
  clear `ModelNotReadyError`; `/api/health` reports `model_ready: false` and prediction endpoints
  return **503** with the exact command to fix it.
* After retraining, restart the API (or `--reload`) to load the new artifact.

## 4. Database schema

```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    name          VARCHAR(120) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME NOT NULL
);

CREATE TABLE predictions (
    id           INTEGER PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text         TEXT NOT NULL,
    label        VARCHAR(40) NOT NULL,
    confidence   FLOAT,
    score_type   VARCHAR(24) NOT NULL,
    scores_json  TEXT,
    model_name   VARCHAR(80) NOT NULL,
    created_at   DATETIME NOT NULL
);
CREATE INDEX ix_predictions_user_id ON predictions(user_id);
CREATE INDEX ix_predictions_created_at ON predictions(created_at);
```

* `users.email` is unique (case-insensitive check in the API plus the DB constraint).
* Every history query filters by `user_id` from the verified token.
* Deleting a prediction checks ownership; a foreign id returns **404**, not another user's data.
* Tables are created automatically at startup (`Base.metadata.create_all`).

## 5. Security model

| Concern | Implementation |
| --- | --- |
| Password storage | bcrypt, cost 12, over a SHA-256 pre-hash (handles bcrypt's 72-byte limit) |
| Session | HS256 JWT with `sub = user id`, `exp` (default 12 h) |
| Secret management | `TRUTHLENS_SECRET_KEY` env var / `.env`; development fallback logged as a warning |
| Route protection | `OAuth2PasswordBearer` dependency on all private endpoints |
| Data isolation | All queries scoped by authenticated user id |
| Input validation | Pydantic schemas + explicit text validation + SQLAlchemy parameterisation |
| CORS | Explicit localhost origins only |
| Error leakage | Generic 500 handler; no stack traces or password hashes in responses |
| Secrets in ZIP | None — `.env` is git-ignored; only `.env.example` ships |

**Why bcrypt directly instead of passlib?** Recent bcrypt releases (5.x) broke passlib's version
detection, producing runtime errors. Using `bcrypt` directly is simpler and version-safe.

## 6. Frontend architecture

* `lib/AuthContext.jsx` — token in `localStorage`, profile fetch on load, login/register/logout.
* `lib/api.js` — single fetch wrapper; maps backend errors to readable messages; handles network
  failures.
* `components/ProtectedRoute.jsx` — redirects unauthenticated users, preserving the intended path.
* `components/Layout.jsx` — responsive navigation and footer.
* Pages consume only real API data; empty states are shown instead of fake statistics.
* Charts use Recharts; the confusion matrix is a CSS grid coloured by cell value (no extra library).
* Design tokens (colours, radii, spacing) live in `src/styles.css` as CSS custom properties.

## 7. Why this structure

* **Shared `src/truthlens/`** prevents the classic train/serve skew of duplicating preprocessing.
* **Pipelines, not loose vectorizers** make artifacts self-contained (vectorizer + model in one file).
* **Generated metrics in `results/`** are the single source of truth for the Insights page, so the UI
  can never display a hand-typed number.
* **SQLite** keeps setup to zero external services while still using a real relational schema and ORM.
