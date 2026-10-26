# Independent review of Homework 1 and 2

This review covers scientific interpretation, implementation integrity, reproducibility, and the limits of resume claims. The homework implementations were written by separate agents. The review used their source code and executed artifacts, independently reconstructed cohorts from the raw catalog, checked notebook structure, and inspected embedded figures. It does not claim an independent full rerun of every optimization experiment.

**Final decision: ready for submission, with the documented scientific limitations.** All 19 released tasks are implemented. No unresolved implementation blocker remains. The final artifacts contain 91 executed code cells and 15 embedded figures, with no stored execution errors. This is a code-and-artifact review decision, not a claim that the real Sun has been proved to follow the fitted model.

## A consequential input-quality finding

Both homeworks need the same definition of a group's first observation. Sorting only on time with an unstable sorting algorithm can choose different rows when a group has several records at exactly its earliest timestamp. Those rows can disagree on latitude, even on hemisphere.

The independent audit found:

- Across the 22,122 selected groups, **51** have multiple rows at their earliest timestamp; **50** have conflicting earliest latitudes; **18** have earliest rows on both sides of the equator.
- Across the 16,611 development groups, the corresponding counts are **38**, **37**, and **13**.
- In this environment, changing the sorting algorithm changed the selected hemisphere of four development groups: `GPR_410`, `GPR_1145`, `GPR_5887`, and `DPD_8762`. The first two exchanged hemispheres within cycle 12, so their aggregate count changes canceled. The other two changed the per-hemisphere counts in cycles 14 and 23.

Homework 1 already used stable sorting. The review requested that Homework 2 use the same **original-source-order tie policy** and rerun its results. This is a deterministic, reproducible convention; it does not establish which conflicting record is physically correct. No ambiguous groups were silently deleted or reassigned by a new scientific rule.

The ignored `data/derived/emergences.csv` was independently compared with the stable construction. It already had the same 22,122 IDs and zero discrepancies in time, latitude, longitude, cycle, lifetime maximum area, and hemisphere (numeric tolerance `1e-10`). The cache did not require replacement, and both notebooks rebuild their actual analysis inputs from raw observations.

The audit can be reproduced from the repository root:

```python
import pandas as pd

raw = pd.read_csv("data/composite_sunspot_groups_daily_measurements_10_23.csv")
obs = raw.loc[raw["uniqueID"].notna()].copy()
obs["stamp"] = pd.to_datetime(dict(
    year=obs.year, month=obs.month, day=obs.day,
    hour=obs.hour.fillna(12).astype(int),
    minute=obs.minute.fillna(0).astype(int),
    second=obs.second.fillna(0).astype(int),
))
obs = obs.sort_values("stamp", kind="stable")
earliest = obs.loc[obs.stamp.eq(obs.groupby("uniqueID").stamp.transform("min"))]
audit = earliest.groupby("uniqueID").agg(
    rows=("latitude", "size"), latitudes=("latitude", "nunique"),
    lo=("latitude", "min"), hi=("latitude", "max"),
)
audit["cycle"] = obs.groupby("uniqueID").CYCLE.first()
audit["peak_area"] = obs.groupby("uniqueID").correctedArea.max()
audit = audit.loc[audit.cycle.between(12, 23) & (audit.peak_area > 30)]
for label, subset in (
    ("analysis", audit),
    ("development", audit.loc[~audit.cycle.isin([16, 20, 22])]),
):
    print(label, len(subset), dict(
        multiple_first_rows=int((subset.rows > 1).sum()),
        conflicting_first_latitude=int((subset.latitudes > 1).sum()),
        ambiguous_first_hemisphere=int(((subset.lo < 0) & (subset.hi >= 0)).sum()),
    ))
```

## Homework 1 findings

The reviewer independently reproduced 314,648 catalog rows, 249,752 identified observations, 46,110 distinct group IDs, and the 22,122-group analysis cohort. The catalog checksum in `metrics.json` matches the raw file.

Code review confirmed the separation between the earliest event row and the lifetime maximum-area selection; first non-null cycle labels; unique events; within-hemicycle differences; half-open, complete counting windows; empty-window inclusion; and sample variance with `ddof=1`. The changing-rate null respects exposure in the last partial daily bin.

The final artifact has 38 executed code cells, seven embedded figures, and no stored execution errors. Notebook schema validation passed. The standard first setup cell matches the course template, reference workflows and tutor directives remain present, and no active `NotImplementedError` remains. The reviewer visually inspected the legacy score comparison, homogeneous-Poisson sanity plot, and two-bandwidth Fano comparison; their axes, units, legends, and interpretation are readable.

Measured evidence:

- The full legacy latitude NLL is **infinite** because 110 observations receive zero density. The finite-only score of **3.2024 nats/event** must retain its exclusion disclosure.
- One-day Fano factors are **1.174 north** and **1.157 south**; at 730 days they are **76.63** and **67.72**. These values do not establish direct triggering.
- Constant-rate simulation mean Fano factors range from **0.978 to 1.005** over the specified window widths. The simulation bands are empirical percentiles from 20 realizations, not formal confidence intervals for solar physics.
- The EMD comparison samples an ungated Gaussian shape and has additional Monte Carlo variability. The notebook repeats that sampling 20 times and reports its spread instead of presenting a single draw as exact.

The report clearly explains first observation versus formation, retrospective area selection, data-defined observing spans, exposure assumptions, and the inability to infer longitude-based mechanisms from these analyses.

## Homework 2 numerical and control checks

After the stable-tie correction, the reviewer independently reconstructed all 16,611 development events from the raw file and confirmed every fitted hemicycle's count. Recomputing each of the 18 log-likelihoods directly from the reported parameters, using the analytic gamma log-rate expression, reproduced the stored values to a maximum discrepancy of **1.82e-12 nats**. The constant-rate baseline was separately recomputed from `n log(n/17) - n`. The resulting score comparison is:

- Gamma NLL: **−203.8683099424 nats/hemicycle-year**.
- Constant-rate NLL: **−164.5682851344 nats/hemicycle-year**.
- Absolute in-sample improvement: **39.3000248080 nats/hemicycle-year**.

As a separate numerical check, the reviewer evaluated the gamma integral with the incomplete-gamma function. Its largest difference from the fixed 4,001-node trapezoidal expected count was approximately **1.00e-6 events** across the 18 fitted wings. This supports numerical integration accuracy for these fitted curves; it is not a statement about all possible rate functions.

The executed notebook also provides substantive positive and negative controls:

- Constant-rate quadrature agrees with its analytic likelihood to floating-point precision.
- An invalid thinning upper bound is rejected, rather than silently biasing the simulation.
- The custom two-sided KS distance agrees with SciPy for independently generated exponential samples to floating-point precision.
- All **108 development optimization starts** report successful termination; their largest final within-fit NLL spread is **2.73e-12 nats**. Agreement among starts supports numerical stability without proving a global maximum.
- Omitting the integral term makes the expected count overflow. Using the wrong integration start produces approximately **2,061.6 expected events** over the true window instead of 1,590. These controls reveal different failure modes.
- A diagnostic reevaluation on 8,001 nodes changes NLL by at most **7.50e-7 nats** and KS distance by **3.54e-5**; fits and headline scores retain 4,001 nodes.

The 20 seeded recovery experiments give peak-time RMSE **0.060862 years (22.23 days)** and width RMSE **0.049100 years (17.93 days)**. The reviewer checked their definition against the recorded errors and confirmed that these are synthetic recovery errors for the selected 19N-derived rate, whose onset lies on the imposed lower boundary. They are not forecasts of unseen solar events or evidence that all raw parameters are unbiasedly recoverable.

Median KS distance is **0.02495** for the gamma model with within-day jitter, **0.15549** with ties retained, and **0.27877** for the constant baseline with the same jitter draws. The final pooled gamma distance is **0.01517**. The report correctly treats these as fitted-data descriptive diagnostics. The ordinary p-values are uncalibrated. An outdated reference to the naive p-value count was corrected to the final **16/18** after the deterministic tie correction.

Notebook schema validation passed for all 53 executed code cells and eight figures. The standard setup matches the original, no active task placeholder raises remain, and the catalog checksum matches. Visual review of the thinning/recovery illustration, QQ/KS comparison, and onset/physical-plausibility plots found readable axes, legends, and units. The three sealed cycles are excluded from fitting and diagnostic evaluation. The full execution time of approximately **76.97 seconds** is reported with its environment and is not described as a speedup.

## Corrections requested during review

The review identified these issues in the released teaching text or early submission drafts; the submissions distinguish corrected explanations from preserved task specifications:

- **Quadrature spacing:** 4,001 nodes over 17 years imply approximately **1.55 days** between nodes, not finer than the one-day catalog sampling. The mandated mesh is preserved; refinement is a numerical sensitivity check, not a knob selected to improve scores.
- **Count conservation:** with a freely fitted multiplicative scale, integrated expected count equaling observed count is a likelihood identity. Homework 2 explicitly applies a conditional scale update. Agreement is therefore a consistency check, not independent predictive accuracy or proof of a global optimum.
- **Recovery uncertainty:** replicate standard deviation and the standard error of a replicate mean are different. Recovery is reported with bias and RMSE, and boundary-sensitive raw parameters are not called exactly or unbiasedly recovered.
- **KS inference:** ordinary fitted-data KS p-values are uncalibrated after parameter estimation and the assumed day-jitter policy. QQ plots and KS distances are descriptive diagnostics; a nominal non-rejection is not proof of Poisson behavior.
- **Profile likelihood:** a four-nat sensitivity subset is descriptive, not an automatically calibrated confidence interval. An onset at the window boundary is not a measured physical start date.
- **Shared source:** event counts and smoothed area are complementary summaries of the same catalog. Their correlation is not independent validation, causation, or a demonstrated forecasting model.
- **Language:** a changing-rate Poisson process has independent increments conditional on its rate; ordinary calendar-time waiting times need not have the constant-rate memoryless property. A high Fano factor is not equivalent to positive skew or proof of event dependence.
- **Conversation records:** the handoffs disclose their retrospective origin and do not invent student predictions or mastery. An inaccurate quoted excerpt and a word-count statement were corrected.

## Resume interpretation

The defensible accomplishments are a reproducible data pipeline, classical point-process modeling, numerical validation, repeated simulation recovery, deliberate failure injection, and diagnosis of input ambiguity and parameter identifiability. These are relevant data-science and scientific-software skills.

Likelihood gains on the 18 fitted development hemicycles must be called **in sample**, not held-out accuracy. Synthetic peak/width recovery errors describe the specified simulation scenario, not real solar forecasting errors. Runtime measurements describe this environment and are not speedups without a controlled benchmark. This work does not establish neural-network training, production deployment, or a unique magnetic mechanism.

The exact final measurements and scope are recorded in each week's `metrics.json` and `REPORT.md`, with a consolidated interpretation in `HOMEWORK_1_2_REPORT.md`.

**Final review status: PASS.** Requested implementation and explanatory corrections are resolved, the combined report agrees with the final stable-tie metrics, and no additional experiments are needed for the stated homework scope. Remaining limitations above constrain interpretation and resume wording; they are not hidden execution failures. Review artifacts are frozen for the requested commit and push.
