# API Reference — TruthLens AI

Base URL in development: `http://localhost:8000`
Interactive documentation: `/docs` (Swagger UI) · `/redoc`

All request and response bodies are JSON. Authenticated endpoints require:

```
Authorization: Bearer <access_token>
```

Errors always use the shape `{"detail": "human-readable message"}`.

## System

### `GET /api/health`

```json
{
  "status": "ok",
  "model_ready": true,
  "model_name": "Logistic Regression (A1)",
  "detail": null
}
```

Returns `status: "degraded"` and `model_ready: false` when artifacts are missing.

## Authentication

### `POST /api/auth/register`

```json
{
  "name": "Durga Prasad",
  "email": "durga@example.com",
  "password": "StrongPass123",
  "confirm_password": "StrongPass123"
}
```

* `201` → `{ "access_token": "...", "token_type": "bearer", "user": {...} }`
* `409` → email already registered
* `422` → validation failure (short password, mismatched confirmation, invalid email)

### `POST /api/auth/login`

```json
{ "email": "durga@example.com", "password": "StrongPass123" }
```

* `200` → token + user
* `401` → “Incorrect email or password.”

### `GET /api/auth/me` 🔒

Returns the authenticated profile: `id`, `name`, `email`, `created_at`.

## Predictions

### `POST /api/predict` 🔒

```json
{ "text": "The unemployment rate has fallen to its lowest level in fifty years." }
```

`201` response:

```json
{
  "id": 1,
  "text": "The unemployment rate has fallen to its lowest level in fifty years.",
  "label": "Partially False",
  "confidence": 0.367361,
  "score_type": "probability",
  "scores": [
    { "label": "Partially False", "score": 0.367361 },
    { "label": "Fake", "score": 0.266059 },
    { "label": "Misleading", "score": 0.262541 },
    { "label": "Real", "score": 0.104039 }
  ],
  "model_name": "Logistic Regression (A1)",
  "created_at": "2026-10-29T07:23:59.415229"
}
```

* `score_type` is `"probability"` for probabilistic estimators and `"decision_score"` for
  decision-function-only models (LinearSVC). Decision scores are **not** calibrated probabilities.
* `422` → blank, under 10 characters, over 5,000 characters, or no usable text.
* `401` → missing/expired token.
* `503` → model artifacts missing or incompatible.

### `GET /api/predictions?limit=20&offset=0` 🔒

```json
{
  "total": 12,
  "limit": 20,
  "offset": 0,
  "items": [ { "...prediction..." } ]
}
```

Only the caller's rows are returned, newest first. `limit` 1–100, `offset` ≥ 0.

### `GET /api/predictions/stats` 🔒

```json
{
  "total_predictions": 8,
  "counts_by_label": [
    { "label": "Real", "count": 1 },
    { "label": "Misleading", "count": 2 },
    { "label": "Partially False", "count": 4 },
    { "label": "Fake", "count": 1 }
  ],
  "recent": [ { "...prediction..." } ],
  "model_name": "Logistic Regression (A1)",
  "model_accuracy_test": 0.3784206411258796
}
```

Powers the dashboard. All values are computed from saved rows; a new user sees zeros and an empty
“recent” list.

### `DELETE /api/predictions/{id}` 🔒

* `204` on success, `404` if the row does not exist or belongs to another user.

### `DELETE /api/predictions` 🔒

Deletes all of the caller's predictions and returns `{"deleted": n}`.

## Model insights

### `GET /api/insights`

Public. Returns the complete evaluation record from `results/metrics.json`:

* `selected_model`, `selected_model_display_name`, `selection_criterion`
* `classes`, `label_mapping`, `class_descriptions`
* `selected_model_metrics` (accuracy, weighted/macro precision/recall/F1, per-class metrics,
  confusion matrix)
* `candidates` — all four models with best params, validation and test metrics
* `dataset` — split counts, class distribution, audit details
* `features`, `preprocessing`, `environment`, `generated_at`

### `GET /api/model-info`

Compact subset of the above for lightweight clients.

## curl examples

```bash
# health
curl http://localhost:8000/api/health

# register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo User","email":"demo@example.com","password":"StrongPass123","confirm_password":"StrongPass123"}'

# login and capture the token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"StrongPass123"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# predict
curl -X POST http://localhost:8000/api/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"The city council approved the budget by a narrow margin last Tuesday."}'

# history
curl "http://localhost:8000/api/predictions?limit=5" -H "Authorization: Bearer $TOKEN"
```

## Status codes used

| Code | Meaning |
| --- | --- |
| 200 | OK |
| 201 | Created (registration, prediction) |
| 204 | No content (deletion) |
| 401 | Missing/invalid credentials |
| 404 | Not found / not owned |
| 409 | Email already registered |
| 422 | Validation error |
| 500 | Handled server error (generic message) |
| 503 | Model not ready |
