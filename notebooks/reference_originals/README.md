# Reference originals (not part of the runnable pipeline)

These four notebooks are the files originally submitted with the project. They are kept only as a
historical reference and are **not** used by the application or by the corrected notebooks.

| File | What it actually does | Why it is not used |
| --- | --- | --- |
| `A1_original_binary_notebook.ipynb` | Binary REAL/FAKE Logistic Regression on `fake_or_real_news.csv` | Different dataset and binary task; the project report and the supplied cleaned dataset describe a four-class LIAR task. |
| `A2_original_binary_notebook.ipynb` | Binary SVM on `fake_or_real_news.csv` | Same dataset mismatch. |
| `A4_original_binary_notebook.ipynb` | Binary Naive Bayes on `fake_or_real_news.csv` | Same dataset mismatch. |
| `L3_original_random_forest_notebook.ipynb` | Random Forest referenced against the LIAR data | Uses the older pipeline layout and does not share the leakage-safe protocol. |

The corrected, runnable notebooks live one folder up:

* `A1_Logistic_Regression_Fake_News_Detection.ipynb`
* `A2_SVM_Fake_News_Detection.ipynb`
* `A3_Random_Forest_Fake_News_Detection.ipynb`
* `A4_Naive_Bayes_Fake_News_Detection.ipynb`
* `A5_Model_Comparison_and_Final_Evaluation.ipynb`

They run on `data/cleaned_dataset.csv`, use the documented four-class label mapping, and share one
preprocessing/feature/evaluation protocol.
