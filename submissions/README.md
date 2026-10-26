# Catherine Zheng — Homework 1 and 2

These submissions complete the **released** course tasks, rather than inventing exercises from the syllabus:

- [Homework 1: Tasks 1–9](weeks/week_01/01_counting_process.ipynb), [results](weeks/week_01/REPORT.md), and [conversation handoff](weeks/week_01/vocal_handoff.md).
- [Homework 2: Tasks 10–19](weeks/week_02/02_rate_1d.ipynb), [results](weeks/week_02/REPORT.md), and [conversation handoff](weeks/week_02/vocal_handoff.md).
- [Independent review](HOMEWORK_1_2_REVIEW.md) and [combined report / resume evidence](HOMEWORK_1_2_REPORT.md).

## Submission instructions followed

The last section of each released notebook, **Before you push: save the conversation**, requires a completed notebook and a `vocal_handoff.md` in the corresponding weekly submission folder, pushed together. The root course README says weekly pushes are progress reports. No additional upload portal or pull-request requirement is specified in the checked-in instructions. The destination is the student's fork, `catou88/butterflai2`, not the upstream class repository.

This checkout originally stopped at `a469fc9`. It was fast-forwarded to course release `84d50ec` before implementation. Instructor templates remain unchanged; completed work lives under `submissions/`. Homework 3 is not completed by this submission.

## Reproduce

Open a notebook from this clone and run every cell in order. The first code cell is the unmodified course setup. Local Phase A analysis uses NumPy, pandas, SciPy, and Matplotlib; a GPU is not required. Each notebook is self-contained and reads the original catalog and frozen legacy model. Derived tables are regenerated under the ignored `data/derived/` directory. Each notebook documents its seeds and diagnostic settings. The recorded runs used Python 3.13.11; the course environment file specifies Python 3.12. Exact optimizer results can differ across package versions, so the measured package versions are retained alongside the results.

To execute with Jupyter tooling, from the repository root:

```sh
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 submissions/weeks/week_01/01_counting_process.ipynb
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 submissions/weeks/week_02/02_rate_1d.ipynb
```

Run the two commands separately or in separate terminals. Neither notebook imports the other. Their shared derived emergence table is reproducible from the raw catalog, not a hidden dependency.

## Authorship and interpretation

Code, explanations, and reports were prepared with AI assistance at the student's explicit request. Independent agent roles checked science, implementation, metrics, and beginner comprehension. The handoffs are retrospective records of the actual conversation, not claims that the course's structured tutor dialogue was completed verbatim. They distinguish demonstrated understanding from concepts still open; no student predictions, quotations, or measurements are invented.

Resume claims must be tied to the recorded experiments. In particular, in-sample improvement is not held-out performance, count conservation at a freely fitted scale is not independent predictive accuracy, and this classical work is not neural-network training or production deployment.
