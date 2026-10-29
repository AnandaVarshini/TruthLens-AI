# Evaluation — measured results (TruthLens AI)

These numbers were produced by `python scripts/train_models.py` on the supplied
`data/cleaned_dataset.csv`. They are reproduced verbatim from `results/metrics.json`; nothing is
hardcoded in the application.

**Environment used:** Python 3.11.2 · scikit-learn 1.9.1 · pandas 3.0.5 · NumPy 2.4.6 · SciPy 1.17.1
· Linux x86_64. Selected model: **Logistic Regression (A1)**.

## 1. Data used

| Split | Rows |
| --- | --- |
| Train | 10,252 |
| Validation | 1,279 |
| Test (untouched) | 1,279 |

26 exact duplicate statements removed across splits (leakage prevention). Label distribution:
Partially False 4,746 · Fake 3,561 · Misleading 2,466 · Real 2,063.

## 2. Test-split comparison

| Model | Accuracy | Precision (w) | Recall (w) | F1 (w) | F1 (macro) |
| --- | --- | --- | --- | --- | --- |
| **Logistic Regression (A1)** — deployed | **0.3784** | 0.3613 | 0.3784 | 0.3590 | 0.3231 |
| Multinomial Naive Bayes (A4) | 0.3581 | 0.3515 | 0.3581 | 0.3538 | **0.3278** |
| Random Forest (A3) | 0.3745 | 0.3502 | 0.3745 | 0.2982 | 0.2383 |
| Linear SVM (A2) | 0.3440 | 0.3342 | 0.3440 | 0.3374 | 0.3087 |

**Selection note.** The deployed model is chosen by validation macro-F1, not by test metrics. On the
validation split Logistic Regression scored the highest macro-F1 (≈0.338 vs ≈0.327 for Naive Bayes),
so it was selected before the test split was touched. On the test split Naive Bayes edges ahead on
macro-F1 by 0.005 while trailing on accuracy — a difference well within noise for 1,279 rows. This is
reported transparently rather than retro-fitting the selection to the test result (which would be
test-set leakage).

## 3. Per-class performance of the deployed model (test)

| Class | Precision | Recall | F1 | Support |
| --- | --- | --- | --- | --- |
| Real | 0.2705 | 0.1571 | 0.1988 | 210 |
| Misleading | 0.3221 | 0.1928 | 0.2412 | 249 |
| Partially False | 0.4137 | 0.5792 | 0.4826 | 480 |
| Fake | 0.3720 | 0.3676 | 0.3698 | 340 |

Confusion matrix (rows = actual, columns = predicted):

| Actual \ Predicted | Real | Misleading | Partially False | Fake |
| --- | --- | --- | --- | --- |
| Real | 33 | 27 | 97 | 53 |
| Misleading | 31 | 48 | 127 | 43 |
| Partially False | 34 | 53 | 278 | 115 |
| Fake | 24 | 21 | 170 | 125 |

Figures: `results/figures/confusion_logistic_regression.png`,
`results/figures/model_comparison.png`, `results/figures/class_distribution.png`.

## 4. Interpretation

1. **Accuracy ≈ 38 % is expected, not a bug.** A majority-class-only classifier gets ≈37.5 %.
   Four-class LIAR with TF-IDF + classical models is a hard benchmark; published work with classical
   models reports accuracy in the 20–30 % range for the six-class version, and higher figures usually
   add metadata, embeddings or external knowledge.
2. **The model is better than a majority baseline on macro-F1.** It finds minority classes at least
   sometimes (Real recall 15.7 %, Misleading 19.3 %) rather than collapsing entirely.
3. **Errors cluster between neighbouring categories.** Most misclassifications land in
   “Partially False”, which is both the majority class and semantically the “middle” of the scale.
   Distinguishing “half-true” from “barely-true” is inherently subjective even for humans.
4. **Random Forest has the lowest macro-F1** despite reasonable accuracy: it over-predicts the
   majority class, so minority F1 is poor (macro-F1 0.2383).
5. **Naive Bayes is competitive and extremely fast**, but its independence assumption and smoothing
   sensitivity make it less stable across hyper-parameters (see the notebook A4 grid).
6. **SVM** is the weakest on this split; its decision scores are not calibrated, which is why the UI
   labels them differently if it were ever deployed.
7. **No model is “best” by every metric.** The project states its criterion (validation macro-F1) and
   reports all metrics for all models, rather than cherry-picking.

## 5. Why the project does not report 100 % accuracy

* The dataset contains genuinely ambiguous labels; identical wording can appear in different
  categories depending on context that is not in the text.
* Any pipeline that reaches 100 % would require the answer (label) to be present in the features —
  i.e. leakage. This project fits vectorizers on training data only and de-duplicates across splits,
  specifically to prevent that.
* The application therefore presents predictions as **estimates** with visible class scores, and
  states that it cannot prove a claim true or false.

## 6. Verification of the shipped artifact

Notebook `A5_Model_Comparison_and_Final_Evaluation.ipynb` reloads
`models/truthlens_pipeline.joblib`, re-predicts the test split and asserts that the accuracy equals
the recorded value. That assertion executed successfully, which confirms:

* the shipped artifact is the evaluated pipeline,
* the vectorizer inside it matches the training configuration,
* loading it in a fresh process (as the API does) reproduces the reported results.
