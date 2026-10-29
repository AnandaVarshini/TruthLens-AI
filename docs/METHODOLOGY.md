# Methodology — TruthLens AI

## 1. Problem definition

Given a short news claim, predict one of four reliability levels:

| Label | Meaning |
| --- | --- |
| Real | The statement is accurate. |
| Misleading | Mostly accurate but missing context or overstated. |
| Partially False | Partly accurate and partly false/unsupported. |
| Fake | False or fabricated. |

This is a **four-class, single-label text classification** problem, not a fact-checking system.

## 2. Dataset

* LIAR benchmark (Wang, ACL 2017): 12,836 short political statements fact-checked by PolitiFact.
* Supplied file: `data/cleaned_dataset.csv` (11 columns, unchanged).
* Only the statement `text` is used as a feature. Speaker metadata is retained but not modelled, to
  avoid learning political affiliation instead of linguistic patterns.
* Predefined partitions are used: **train 10,269 / valid 1,284 / test 1,283** before duplicate
  handling.

### 2.1 Label mapping

| PolitiFact | Project label |
| --- | --- |
| true | Real |
| mostly-true | Misleading |
| half-true | Partially False |
| barely-true | Partially False |
| false | Fake |
| pants-fire | Fake |

`validate_label_column()` recomputes the mapping and raises if any row disagrees, so a silent
re-mapping is impossible.

### 2.2 Data audit (executed)

| Check | Result |
| --- | --- |
| Rows in file | 12,836 |
| Missing/blank text or label | 0 |
| Rows with an invalid label | 0 |
| Exact duplicate statements overall | 26 |
| Duplicates inside train | 11 |
| Duplicate statements shared between splits | 9 (5 train↔valid, 4 train↔test) |
| Action | Global de-duplication keeping the earliest split |
| Final sizes | train 10,252 · valid 1,279 · test 1,279 |

**Why this order matters:** keeping a statement in both train and test would inflate test accuracy.
Removing duplicates *before* evaluation makes the reported number slightly lower but honest.

### 2.3 Class imbalance

| Class | Rows | Share |
| --- | --- | --- |
| Partially False | 4,746 | 37.0 % |
| Fake | 3,561 | 27.8 % |
| Misleading | 2,466 | 19.2 % |
| Real | 2,063 | 16.1 % |

Because the majority class is 37 %, a model that always predicts “Partially False” already reaches
~37 % accuracy. That is why **macro-F1** is used for model selection — it weights every class equally
and exposes models that ignore minority classes.

## 3. Preprocessing

Implemented once in `src/truthlens/preprocessing.py` and used by training, notebooks and the API:

1. HTML unescape
2. lowercase
3. remove URLs (`http://…`, `www.…`)
4. remove HTML tags
5. remove punctuation and digits (`[^a-z\s] → space`)
6. collapse whitespace and trim

Stop-word removal is **not** done in this function; the TF-IDF vectorizer (stored inside the saved
pipeline) performs it, so the exact stop-word list travels with the model.

Validation for user input: 10–5,000 characters and at least one usable token after cleaning.

## 4. Features

A `FeatureUnion` of two TF-IDF blocks:

| Block | Configuration | Why |
| --- | --- | --- |
| Word | 1–2 grams, `min_df=2`, `max_features=60,000`, `sublinear_tf=True`, English stop words | Captures vocabulary and short phrases; sublinear scaling dampens repeated terms |
| Character | `char_wb`, 3–5 grams, `min_df=3`, `max_features=60,000`, `sublinear_tf=True` | Robust to spelling variants, suffixes and informal writing common in short statements |

Both live inside the pipeline, so `fit` sees only training rows. Total feature space ≈ 120,000
columns (sparse).

**Why not metadata?** Party affiliation and speaker identity could dominate the model and produce
politically biased predictions. The report specifies text-only classification.

## 5. Splits and tuning protocol

```
train (10,252)  → fit vectorizer + classifier, tune hyper-parameters by validation score
valid (1,279)   → select hyper-parameters and choose the deployed algorithm
test  (1,279)   → used once, after selection, for the final report
```

* The dataset's own partitions are used instead of a new random split (documented and reproducible).
* Every candidate is a full `Pipeline`; nothing is fitted on validation or test data.
* Selection criterion: **highest macro-F1 on validation** (stated in advance, not chosen after
  seeing test results).
* Hyper-parameter grids (small and interpretable, to avoid overfitting the validation split):

| Algorithm | Grid | Selected |
| --- | --- | --- |
| Logistic Regression | `C ∈ {1, 2}`, `class_weight ∈ {None, balanced}` | `C=1.0`, `class_weight=None` |
| Linear SVM | `C ∈ {0.1, 0.25, 0.5, 1}` | `C=0.5` |
| Random Forest | `n_estimators=200`, `min_samples_leaf ∈ {1, 3}` | `min_samples_leaf=1` |
| Multinomial NB | `alpha ∈ {0.1, 0.3, 1.0}` | `alpha=0.1` |

## 6. Algorithms

### A1 — Multinomial Logistic Regression
Linear model with one weight per (feature, class); softmax output gives probabilities. Fast,
interpretable (`coef_` maps directly to words), and provides well-behaved `predict_proba`.

### A2 — Linear Support Vector Machine
Maximum-margin linear classifier with squared-hinge loss. Strong on high-dimensional sparse text.
It has **no calibrated probabilities**; the API reports normalised decision values and labels them
`decision_score` in both the payload and the UI.

### A3 — Random Forest
Bagged decision trees with `max_features="sqrt"`. Captures non-linear interactions and is robust to
outliers, but each split examines a tiny fraction of ~120k features, making it slower and weaker on
this representation.

### A4 — Multinomial Naive Bayes
Bayes' rule with conditional independence and Laplace smoothing (`alpha`). Extremely fast baseline.
Strong smoothing (`alpha=1.0`) collapsed predictions toward the majority class in validation, so
`alpha=0.1` was selected.

## 7. Metrics — definitions used in the UI

| Metric | Definition | Why it is reported |
| --- | --- | --- |
| Accuracy | correct / total | Overall hit rate, but misleading under imbalance |
| Precision (weighted) | per-class precision weighted by support | How reliable positive predictions are |
| Recall (weighted) | per-class recall weighted by support | Coverage of actual class members |
| F1 (weighted) | harmonic mean, support-weighted | Balances precision/recall overall |
| F1 (macro) | unweighted mean of per-class F1 | Shows performance on minority classes; **selection criterion** |
| Per-class precision/recall/F1 | computed per label | Reveals which categories are confused |
| Confusion matrix | rows = actual, columns = predicted | Shows the direction of errors |

All values are computed by scikit-learn from real predictions on the test split and written to
`results/metrics.json`; the frontend only renders that file.

## 8. Reproducibility

* `RANDOM_STATE = 42` for every split/estimator that uses randomness.
* Fixed TF-IDF parameters and grids in `src/truthlens/config.py` and `pipeline.py`.
* One command regenerates every artifact: `python scripts/train_models.py`.
* `results/metrics.json` records the Python/scikit-learn/pandas/NumPy versions used.
* `models/truthlens_pipeline.joblib` is a standard pickle; retrain if the scikit-learn **minor**
  version differs (scikit-learn does not guarantee cross-version pickle compatibility).
* Notebook A5 re-loads the deployed artifact, re-scores the test split and asserts the accuracy
  matches the record — proving the shipped artifact is the evaluated one.

## 9. Known methodological limitations

1. **Domain shift** — short political statements ≠ full news articles; accuracy on real articles can
   differ from the test split.
2. **Label subjectivity** — PolitiFact ratings are editorial judgements; neighbouring classes are
   genuinely ambiguous, which caps achievable accuracy.
3. **No fact verification** — the model has no access to evidence, sources, dates or world knowledge.
4. **Imbalance** — minority classes (Real, Misleading) have lower recall; macro-F1 ~0.32 reflects this.
5. **Bag-of-features limits** — negation and long-range context are only partly captured by 1–2 grams.
6. **Single split** — results come from one predefined test split; a cross-validated estimate would
   have wider error bars. (Cross-validation was not used for the final number to keep the test set
   untouched.)
7. **Language** — English only.

## 10. Possible future work

* Transformer embeddings (BERT/RoBERTa) or sentence embeddings for context.
* Cross-validation and bootstrap confidence intervals.
* Metadata features with fairness analysis (party/state) reported separately.
* Retrieval-backed evidence and source credibility signals.
* Ordinal modelling that respects the Real → Fake ordering.
