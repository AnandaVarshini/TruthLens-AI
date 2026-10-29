# Dataset notes — `data/cleaned_dataset.csv`

## Provenance

* **Benchmark:** LIAR — *"Liar, Liar Pants on Fire": A New Benchmark Dataset for Fake News Detection*,
  William Yang Wang, ACL 2017 (UC Santa Barbara).
* **Content:** 12,836 short political statements fact-checked by PolitiFact editors, with speaker
  metadata and the original six-point truth rating.
* **Mirror used by the project report:** <https://github.com/ekagra-ranjan/fake-news-detection-LIAR-pytorch>
* The file in this folder is the cleaned dataset supplied with the project. It has **not** been
  replaced, regenerated or re-labelled.

## Columns

| Column | Type | Description | Used as a feature? |
| --- | --- | --- | --- |
| `text` | text | Original statement | **Yes** (cleaned at train/inference time) |
| `clean_text` | text | Pre-cleaned statement supplied with the dataset | No — the project recomputes cleaning so the same code path is used in training and inference |
| `label` | categorical | Four-class target: `Real`, `Misleading`, `Partially False`, `Fake` | **Target** |
| `raw_label` | categorical | Original PolitiFact rating (`true`, `mostly-true`, `half-true`, `barely-true`, `false`, `pants-fire`) | Only for mapping validation |
| `speaker`, `party_affiliation`, `speaker_job_title`, `state_info` | categorical | Speaker metadata | No |
| `subjects`, `context` | text | Topic and venue of the statement | No |
| `split` | categorical | Predefined `train` / `valid` / `test` partition | Drives the split |

Only the statement text is used as a model feature, matching the methodology in the project report.
Speaker metadata is retained in the file for transparency and future work.

## Label mapping (validated row-by-row in `src/truthlens/labels.py`)

| PolitiFact rating | Project label |
| --- | --- |
| `true` | Real |
| `mostly-true` | Misleading |
| `half-true` | Partially False |
| `barely-true` | Partially False |
| `false` | Fake |
| `pants-fire` | Fake |

`Partially False` is the category called **Partially Misleading** in some descriptions; the project
keeps the dataset/report name so the UI and the data always agree.

## Counts (after cleaning)

| Split | Rows |
| --- | --- |
| train | 10,252 |
| valid | 1,279 |
| test | 1,279 |

| Class | Rows (all splits) |
| --- | --- |
| Real | 2,063 |
| Misleading | 2,466 |
| Partially False | 4,746 |
| Fake | 3,561 |

26 exact duplicate statements were removed across splits so a test statement can never appear in the
training set (see `results/metrics.json → dataset`).

## Licensing / use

The dataset is distributed for research and educational use. Cite Wang (2017) if you reuse it.
