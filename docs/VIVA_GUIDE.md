# Viva / project-review guide — TruthLens AI

A 6–8 minute demo script plus the questions examiners usually ask. Keep the measured numbers in
front of you; do not claim better accuracy than the tables.

## 1. One-sentence pitch

> “TruthLens AI is a full-stack web application that classifies a news claim into four reliability
> levels — Real, Misleading, Partially False, Fake — using TF-IDF features and four classical
> machine-learning algorithms trained on the LIAR benchmark, with a FastAPI backend, a SQLite
> database and a React frontend.”

## 2. Demo order (6–8 minutes)

1. **Landing page (30 s)** — project title, the four categories, the four algorithms, responsible-use
   note. Point out that the “selected model” and “test accuracy” chips are loaded from the backend,
   not typed into the page.
2. **Register (45 s)** — create a fresh account. Try a mismatched password first to show validation;
   try the same email twice to show duplicate prevention.
3. **Dashboard (30 s)** — it is empty for a new user. That is deliberate: no fabricated statistics.
4. **Detect (90 s)** — paste an example claim, predict, explain the four score bars, the model name,
   the timestamp, and the disclaimer. Clear and run a second, different claim.
5. **History (30 s)** — the two predictions appear; delete one; show pagination behaviour.
6. **Model Insights (90 s)** — comparison table, confusion matrix, per-class table, split counts.
   Explain why accuracy is ~38 % (imbalance, overlapping classes) and why that is honest.
7. **Profile / logout (20 s)** — protected routes redirect to login after logout; try opening
   `/dashboard` directly.
8. **Swagger (30 s)** — `http://localhost:8000/docs`, show the endpoints and a 401 without a token.
9. **Notebooks / training (60 s)** — show `python scripts/train_models.py` output and one executed
   notebook (A5 asserting the artifact reproduces the metrics).

## 3. Architecture explanation (draw this on the board)

```
React UI → FastAPI (/api/predict, JWT) → model_service (loads pipeline once)
        → preprocess_text → TF-IDF (word + char) → Logistic Regression
        → SQLite (prediction saved) → JSON → UI
```

Key sentence: **“The same preprocessing function and the same pipeline object are used in training
and inference, so there is no train/serve skew.”**

## 4. Likely questions and strong answers

**Q: Why only 38 % accuracy? Isn’t that bad?**
> It is the honest result for four-class LIAR with text-only TF-IDF. The majority class is 37 %, and
> neighbouring categories (half-true vs barely-true) overlap. The model beats a majority baseline on
> macro-F1 and finds minority classes. Reporting 100 % here would require leaking test data; we
> deliberately prevent that by fitting vectorizers on train only and removing 26 cross-split
> duplicates.

**Q: What exactly is the label mapping?**
> true → Real; mostly-true → Misleading; half-true and barely-true → Partially False; false and
> pants-fire → Fake. A validation function recomputes the mapping row by row and fails if the CSV
> disagrees.

**Q: Why TF-IDF and not BERT?**
> TF-IDF is fast, interpretable, CPU-friendly and appropriate for a classical-ML comparison. The
> project’s stated scope is comparing four classical algorithms. Transformers are listed as future
> work.

**Q: Why both word and character n-grams?**
> Word 1–2 grams capture vocabulary and short phrases; character 3–5 grams add robustness to
> spelling variation and suffixes, which matters for short informal statements. The union is still a
> single sparse matrix.

**Q: How did you prevent data leakage?**
> Vectorizers live inside the pipeline and are fitted on training rows only; hyper-parameters are
> chosen on validation; the test split is evaluated once; 26 duplicates shared between splits were
> removed; the final model was selected by validation macro-F1, not test accuracy.

**Q: Why is Logistic Regression deployed if Naive Bayes has a slightly higher test macro-F1?**
> The criterion was fixed in advance: validation macro-F1, where Logistic Regression scored higher.
> Choosing a model by test performance after the fact would be test-set leakage. Naive Bayes’
> 0.005 test-macro-F1 edge is within noise, and Logistic Regression additionally provides calibrated
> probabilities.

**Q: What do the scores mean?**
> For probabilistic models they are class probabilities from `predict_proba`. LinearSVC has no
> calibrated probabilities, so its normalised decision values are labelled `decision_score` in the
> API and the UI instead of being presented as probabilities.

**Q: Is the prediction stored? Where?**
> Yes — in the `predictions` table of `backend/truthlens.db` with the user id from the verified JWT,
> label, confidence, score type, JSON scores, model name and UTC timestamp.

**Q: How is authentication secured?**
> bcrypt hashing (cost 12, SHA-256 pre-hash for length), HS256 JWT with expiry, OAuth2 bearer
> dependency on all private routes, and every query scoped by the authenticated user id.

**Q: Why SQLite?**
> Zero configuration, file-based, perfect for local academic demos. The code uses SQLAlchemy, so
> switching to PostgreSQL only changes the connection URL.

**Q: What happens if the model file is missing?**
> The health endpoint reports `model_ready: false`, prediction endpoints return 503 with the exact
> retraining command, and the app does not silently return fake predictions.

**Q: How do you know the shipped model is the evaluated one?**
> Notebook A5 reloads `models/truthlens_pipeline.joblib`, re-predicts the test split and asserts the
> accuracy matches `results/metrics.json` to 1e-6. That assertion passed.

**Q: What are the limitations?**
> Short political statements vs full articles (domain shift), subjective labels, no factual
> evidence retrieval, English only, single test split, minority-class recall is low, and the model
> cannot detect breaking-news falsehoods phrased in ordinary language.

**Q: What would you do next?**
> Transformer embeddings, cross-validation with confidence intervals, ordinal modelling, external
> evidence retrieval, and a fairness analysis if metadata were used.

## 5. Numbers to memorise

| Quantity | Value |
| --- | --- |
| Dataset rows | 12,836 |
| Train / valid / test used | 10,252 / 1,279 / 1,279 |
| Duplicates removed | 26 |
| Deployed model | Logistic Regression, `C=1.0` |
| Test accuracy | 0.3784 |
| Test macro-F1 | 0.3231 |
| Test weighted F1 | 0.3590 |
| Features | ~120k sparse TF-IDF (word 1–2 + char 3–5) |
| API tests | 9 passed |
| Frontend build | 643 modules, 686 kB JS |

## 6. If the demo machine fails

Have these fallbacks ready:

1. `results/EVALUATION_RESULTS.md` and `results/figures/*.png` for the metrics discussion.
2. Executed notebooks (outputs are stored) — show them without running anything.
3. Swagger UI already running, or `curl http://localhost:8000/api/health` to prove the service.
4. Pre-built `frontend/dist` means the UI works from the backend alone, without npm.
