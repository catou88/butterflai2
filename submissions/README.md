# Catherine Zheng — Homework 1–3

These submissions complete the **released** course tasks, rather than inventing exercises from the syllabus:

- [Homework 1: Tasks 1–9](weeks/week_01/01_counting_process.ipynb), [results](weeks/week_01/REPORT.md), and [conversation handoff](weeks/week_01/vocal_handoff.md).
- [Homework 2: Tasks 10–19](weeks/week_02/02_rate_1d.ipynb), [results](weeks/week_02/REPORT.md), and [conversation handoff](weeks/week_02/vocal_handoff.md).
- [Homework 3: Tasks 20–31](weeks/week_03/03_latent_belt.ipynb), [results](weeks/week_03/REPORT.md), [independent review](weeks/week_03/REVIEW.md), [resume evidence](weeks/week_03/RESUME.md), and [conversation handoff](weeks/week_03/vocal_handoff.md).
- [Extended nine-model comparison](weeks/week_03/MODEL_COMPARISON_REPORT.md), [feature analysis](weeks/week_03/FEATURE_REVIEW.md), and [supplemental model review](weeks/week_03/COMPARISON_REVIEW.md).
- [Independent review](HOMEWORK_1_2_REVIEW.md) and [combined report / resume evidence](HOMEWORK_1_2_REPORT.md).

## Submission instructions followed

The last section of each released notebook, **Before you push: save the conversation**, requires a completed notebook and a `vocal_handoff.md` in the corresponding weekly submission folder, pushed together. The root course README says weekly pushes are progress reports. No additional upload portal or pull-request requirement is specified in the checked-in instructions. The destination is the student's fork, `catou88/butterflai2`, not the upstream class repository.

This checkout originally stopped at `a469fc9`. It was fast-forwarded to course release `84d50ec` before implementation. Instructor templates remain unchanged; completed work lives under `submissions/`. The Homework 1–2 reports describe those earlier experiments; Homework 3 has its own reports and conditional held-out evaluation.

## Reproduce

Open a notebook from this clone and run every cell in order. The first code cell is the unmodified course setup. Local Phase A analysis uses NumPy, pandas, SciPy, and Matplotlib; a GPU is not required. Each notebook is self-contained and reads the original catalog and frozen legacy model. Derived tables are regenerated under the ignored `data/derived/` directory. Each notebook documents its seeds and diagnostic settings. The recorded runs used Python 3.13.11; the course environment file specifies Python 3.12. Exact optimizer results can differ across package versions, so the measured package versions are retained alongside the results.

To execute with Jupyter tooling, from the repository root:

```sh
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 submissions/weeks/week_01/01_counting_process.ipynb
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 submissions/weeks/week_02/02_rate_1d.ipynb
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 submissions/weeks/week_03/03_latent_belt.ipynb
```

Run each command separately or in separate terminals. No notebook imports another week's code. Their derived inputs are reproducible from the raw catalog, not a hidden dependency. Homework 3 caches repeated fold computations under ignored `data/derived/` with input, code, and configuration provenance; incompatible caches must be rejected and regenerated. A cache hit is a replay of an earlier experiment, not a new optimization run or a measured speedup by itself.

Homework 3 also includes a fast, independent [numerical audit](weeks/week_03/verify_numerics.py) and its [measured results](weeks/week_03/numerical_verification.json). From the repository root, run `python submissions/weeks/week_03/verify_numerics.py`. It reads the submitted notebook's actual function definitions and checks their gradients and likelihood against independent calculations on artificial inputs; it does not refit the solar data or mutate fold caches.

The optional tree/boosting extension additionally needs scikit-learn and threadpoolctl; their tested versions are in [requirements_comparison.txt](weeks/week_03/requirements_comparison.txt). Run `python submissions/weeks/week_03/model_comparison.py --workers 2`, then `python submissions/weeks/week_03/plot_comparison.py`. To regenerate the two fitted finalists under ignored `data/derived/`, run `python submissions/weeks/week_03/fit_selected_models.py`; their training-only provenance is recorded in [selected_models.json](weeks/week_03/selected_models.json). These full-development refits do not add a new test score.

## Authorship and interpretation

Code, explanations, and reports were prepared with AI assistance at the student's explicit request. Independent agent roles checked science, implementation, metrics, and beginner comprehension. The handoffs are retrospective records of the actual conversation, not claims that the course's structured tutor dialogue was completed verbatim. They distinguish demonstrated understanding from concepts still open; no student predictions, quotations, or measurements are invented.

Resume claims must be tied to the recorded experiments. In particular, in-sample improvement is not held-out performance, count conservation at a freely fitted scale is not independent predictive accuracy, and this classical work is not neural-network training or production deployment.
