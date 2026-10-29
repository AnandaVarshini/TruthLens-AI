# TruthLens AI - evaluation results

Generated: 2026-10-29T07:20:47.803772+00:00
Selected model: **Logistic Regression (A1)** (criterion: highest macro-F1 on the validation split)

## Test-split comparison

| Model | Accuracy | Precision (w) | Recall (w) | F1 (w) | F1 (macro) |
| --- | --- | --- | --- | --- | --- |
| Logistic Regression (A1) | 0.3784 | 0.3613 | 0.3784 | 0.3590 | 0.3231 |
| Support Vector Machine (A2) | 0.3440 | 0.3342 | 0.3440 | 0.3374 | 0.3087 |
| Random Forest (A3) | 0.3745 | 0.3502 | 0.3745 | 0.2982 | 0.2383 |
| Multinomial Naive Bayes (A4) | 0.3581 | 0.3515 | 0.3581 | 0.3538 | 0.3278 |

## Per-class metrics of the selected model (test split)

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
