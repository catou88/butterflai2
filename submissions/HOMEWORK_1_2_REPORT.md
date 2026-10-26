# Homework 1–2 final report and resume evidence

## Outcome and scope

Completed the released Tasks 1–9 and 10–19 in separate, self-contained submission notebooks, with embedded outputs and beginner explanations. Two implementation agents worked in parallel. An independent metrics reviewer and a separate beginner-comprehension review challenged the work; implementations and explanations were revised before final verification. See [submission instructions and reproduction](README.md), [Homework 1 report](weeks/week_01/REPORT.md), [Homework 2 report](weeks/week_02/REPORT.md), and [independent review](HOMEWORK_1_2_REVIEW.md).

The course checkout was first updated from `a469fc9` to release `84d50ec`, revealing the actual assignments and tutor handoff requirements. Each week includes its notebook, results report, machine-readable `metrics.json`, and a retrospective `vocal_handoff.md`. The original course notebooks, raw catalog, and frozen legacy model are unchanged. The Week 3 release is present after synchronization, but Homework 3 is outside this completed work.

## Explanation without heliophysics prerequisites

**Homework 1 asks what the observations contain.** A sunspot group can be observed on many days, so a daily catalog row is not a new group. We reduce those repeated observations to one first-recorded appearance per group, then count appearances over equal-length intervals. Latitude means distance north or south of the Sun's equator. A hemispheric cycle is one hemisphere's activity during one solar cycle. The clock `s` shifts each cycle's time origin to a characteristic latitude crossing; it never stretches time.

The Fano factor is count variance divided by average count. A value above one means extra spread relative to a constant-rate Poisson reference. It does not establish that groups cause one another to appear: changing average rates can create that spread. We compare the real curves against artificial independent-event datasets with estimated changing rates. The conclusion depends on how those rates are estimated, which is a finding rather than something to hide.

**Homework 2 asks what changing rate explains the event times.** A rate is an expected average number of groups per year, not a guarantee. We fit a gamma-shaped rate curve by maximizing a probability-based score, the point-process likelihood. It rewards rates at observed event times and subtracts the expected total activity over the whole stated observation window. Without that second term, the fitted model can predict arbitrarily high rates everywhere.

**Thinning is a simulator, not a fitter.** We supply a rate curve, generate candidate artificial events at a constant upper-bound rate, and randomly retain each with probability `desired rate / upper-bound rate`. We do not remove actual observations. A fresh simulation from the same rate can have a different total count. Known-rate simulation followed by refitting checks the fitting procedure under controlled conditions; it does not prove that the Sun follows that model or that only one rate curve could explain the observations.

A fitted free scale makes its expected count essentially equal to the observed count. That equality checks implementation and observation-window consistency; it is not independent evidence of predictive accuracy. Timing patterns and residual diagnostics provide additional information. Here, whole-cycle held-out evaluation is explicitly deferred rather than improvised using the sealed cycles.

## Measured results

### Data and Homework 1

- Raw catalog: **314,648 rows**, 249,752 identified observations, 46,110 distinct groups.
- Selected first-observation analysis: **22,122 distinct events / 24 hemispheric cycles**, cycles 12–23, lifetime maximum corrected area above 30 MSH.
- Exactly tied successive timestamps: **3,631/22,098 (16.43%)**. This observation process matters at day-scale resolution.
- Fano at one day: **1.174 north / 1.157 south**; at 730 days: **76.63 / 67.72**.
- Homogeneous Poisson sanity check: mean Fano across the 17 specified widths ranges **0.978–1.005** over 20 realizations of 24 wings; each empirical simulation band contains one.
- Legacy latitude model: **110 observed groups receive zero density**, making full NLL infinite. Its finite-subset diagnostic of **3.2024 nats/event** explicitly excludes those failures and is not the full score.

### Rate fitting and Homework 2

- Development data: **16,611 events / 18 hemispheric cycles**. Cycles 16, 20, and 22 remain excluded from Week 2 fitting and diagnostics.
- Every score uses **`s` in [-6, +11] years**, a 17-year observation window per hemicycle, and the fixed **4,001-node** quadrature mesh. Its spacing is approximately 1.55 days, not finer than daily sampling.
- In-sample NLL: constant-rate baseline **-164.57**, changing-rate gamma **-203.87**, an absolute improvement of **39.30 nats/hemicycle-year**. Lower is better. These continuous-time density scores can be negative and must only be compared on the same window and time units.
- **20 independently seeded simulate-and-refit trials**, using one chosen development fit as the generating truth: peak-time RMSE **0.0609 years (22.23 days)**; derived-width RMSE **0.0491 years (17.93 days)**. These are synthetic recovery errors, not real-Sun forecast errors. The generating onset is at the imposed lower boundary; the experiment does not establish unbiased recovery across all model shapes.
- Median descriptive time-rescaling KS distance: **0.2788 constant-rate versus 0.0249 gamma-rate**, using the same seeded within-day jitter policy. Retaining ties gives gamma median **0.1555**. Fitted-data ordinary KS p-values are not calibrated hypothesis-test evidence; these distances and QQ plots remain descriptive diagnostics.
- **11/18 onsets hit the lower boundary**. Profiles show that some shape parameters trade off strongly. The data can constrain a peak or width more reliably than a unique onset and all individual parameters.
- Failure injection: omitting the integral drives the model's expected count to numerical overflow. Integrating from -3 rather than -6 produces about **2,062 expected events instead of 1,590** in the true window, despite a plausible-looking curve.

Full numerical records and run provenance are in the two `metrics.json` files. Runtime is reported with its actual measurement scope; no speedup claim is made without a controlled implementation baseline.

## Engineering and review evidence

The implementation preserves the given standard setup and reference workflows. Validation includes event uniqueness and earliest timestamps, half-open full-window counting, unbiased sample variance, thinning upper-bound rejection, independent KS implementation agreement with SciPy, multiple optimization starts, scale consistency, numerical integration/refinement checks, and deliberately broken objectives/windows. Final verification confirmed **91 sequentially executed code cells, 15 embedded figures, and zero stored errors** across the two notebooks. Notebook schemas, Python syntax, unchanged setup cells, completed task implementations, Colab submission links, required files, and catalog checksums passed the artifact audit. Homework 2’s final full execution took 76.97 seconds in the recorded environment. Package versions, random seeds, and the original catalog SHA-256 are retained.

The implement–execute–critique–fix loop corrected the template's mesh-spacing claim, unsupported fitted-KS conclusions, parameter-recovery SD/SE wording, profile-likelihood terminology, and the implication that changing a score's denominator alone introduces count information. Beginner review explicitly separated simulation, fitting, and model checking. See the independent review for final status and limitations.

Independent data-quality review also found **51 selected groups with multiple records at the earliest timestamp**, of which 50 have conflicting latitude values and 18 span both hemispheres. The development subset contains 38, 37, and 13 respectively. Sorting ties by original catalog row order gives both notebooks the same deterministic first-record convention; it does not determine which conflicting latitude is physically correct. The ignored derived CSV was independently checked against this rule and matched all 22,122 selected groups. This fixed a sort-algorithm-dependent discrepancy before submission.

The catalog checksum used by both notebooks is `be5b107506ab82fcf9658b961f798dbca338854924af22d04b0756d277061dcf`.

## Resume bullets supported by this work

**Data science / statistical ML:** Built a reproducible Python pipeline over **314,648 sunspot observations**, deriving **22,122 emergence events** and fitting **18 time-varying Poisson models**; improved in-sample likelihood by **39.3 nats per hemispheric-cycle year** versus a constant-rate baseline.

**Validation / modeling:** Validated a point-process fitter with **20 seeded simulation-recovery experiments**, achieving **22.2-day synthetic peak-timing RMSE** in the selected generating scenario; diagnosed weak parameter identifiability and injected likelihood/window failures to test numerical reliability.

**Software engineering:** Implemented **19 analysis tasks** in reproducible, self-contained Python notebooks with deterministic random seeds, data provenance hashes, executable consistency checks, and independently reviewed scientific explanations.

Choose one or two bullets appropriate to the role and be ready to explain the likelihood, thinning, model limitations, and what was personally understood. This work is classical statistical modeling; it does not support claims of deep-learning training, deployed production services, real-time prediction, or held-out accuracy. There is no meaningful generic “FAANG accuracy” metric for this project.

## Commit grouping

1. `feat: complete homework 1 counting-process analysis` — Week 1 notebook, handoff, measured metrics, and report.
2. `feat: complete homework 2 point-process rate fitting` — Week 2 notebook, handoff, measured metrics, and report.
3. `docs: report homework validation and resume evidence` — submission/reproduction guide, this report, and independent review.

Submission is by pushing these files to the student's fork as required by the checked-in course instructions. The final chat message records the actual pushed commit; this report does not claim a push before it happens.
