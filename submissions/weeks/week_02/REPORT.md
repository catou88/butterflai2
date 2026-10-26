# Homework 2 completion report

Completed Tasks 10–19 in [02_rate_1d.ipynb](02_rate_1d.ipynb), with beginner explanations, executable implementations, outputs, and 8 embedded figures. The notebook is self-contained and uses the released setup cell unchanged. [metrics.json](metrics.json) contains exact measurements, fitted values, recovery errors, profile samples, package versions, catalog checksum, and execution timing.

## What was built

- **Task 10:** the complete event-pattern log-likelihood: reward rate at observed events and subtract the integrated expected activity over the observed window. The constant-rate analytic identity and impossible-event behavior are checked.
- **Tasks 11–12:** positive gamma-rate parameters, an onset restricted to the released range, and six-start Nelder–Mead fitting with a second optimization pass. The free rate scale is then normalized to its exact conditional maximum-likelihood value.
- **Tasks 13–14:** thinning from a certified analytic gamma-rate maximum and 20 independent simulate-and-refit trials. An invalid supplied bound raises. Thinning generates separate artificial datasets; it does not remove real observations or select a rate model.
- **Task 15:** two intentional failures: omit the integral term, or integrate over the wrong window. Both expose why the complete likelihood and observation window matter.
- **Tasks 16–17:** cumulative-rate time rescaling, reproducible uniform within-day jitter, QQ plots, and a two-sided empirical-CDF KS statistic checked against SciPy.
- **Tasks 18–19:** onset profiles that refit the other parameters, comparisons of raw and derived shape quantities, and descriptive comparisons with the catalog’s smoothed-area record.

## Scope and measured results

The emergence table uses stable time sorting and retains the first original catalog row among equal earliest timestamps, matching Homework 1. This is a reproducible convention, not a resolution of conflicting latitude or hemisphere information in duplicate records; no ambiguous groups were selectively removed.

All fits use the **18 development hemispheric cycles**, comprising **16,611 first-observation events**. Cycles **16, 20, and 22 remain sealed**. Time is years since the 15° latitude crossing, using the same **s ∈ [−6,+11]** observation window and **4001 quadrature nodes**. No cycle-length normalization, cross-week imports, LOCO scoring, or withheld-cycle evaluation was added.

The gamma rate achieves **-203.8683 nats per hemicycle-year**, versus **-164.5683** for the best constant-rate baseline: an improvement of **39.3000**. These are **in-sample fits**, not held-out prediction results. Negative continuous-time NLL values are legitimate; the time unit and observation window must match for comparison.

In 20 independent trials generated from the fitted 19N rate, peak-time RMSE is **0.060862 years (22.23 days)**, and width RMSE is **0.049100 years (17.93 days)**. Mean peak bias is -0.03470 years; mean width bias is +0.01280 years. The truth’s onset lies at the lower model boundary, and fitted onset has bias +0.14497 years. Thus this checks one controlled scenario and demonstrates finite-sample/boundary effects; it does not establish unbiased recovery, uniqueness, or physical truth. Metrics include both replicate SD and standard error of the mean rather than conflating them. The assignment’s broad bias-versus-SD assertion is a sanity screen, not a test that the estimator is unbiased.

Median per-wing KS distance is **0.02495** for gamma plus day jitter, **0.15549** when ties are retained, and **0.27877** for the constant baseline with identical jitter draws. The pooled jittered gamma KS is **0.01517**. These diagnostics show the importance of the observation-time policy. The ordinary KS p-values are **uncalibrated after fitting**, jitter and finite-window stopping; “16/18 p-values above .05” is not a formal model-validation claim or proof of independent events.

**11 of 18** fitted onsets sit within 0.001 years of −6. The two onset profiles show substantial raw-parameter tradeoffs while derived peak and width change less. The four-nat profile band and between-wing/within-wing ratios are descriptive sensitivity summaries, not calibrated confidence intervals or significance tests. An onset before the window is mathematically allowed in a general point-process model; the restriction here is inherited from the released assignment and its boundary effects are disclosed.

Event-count versus area-amplitude correlation is **+0.9413**; fitted versus area peak timing correlation is **+0.6836**, with peak-difference SD **0.7168 years**. Width–amplitude correlation is **-0.3013**. These are complementary summaries of the **same catalog**, not statistically independent measurements, causal effects, or validated predictors of a new cycle.

## Checks and limitations

All **53 code cells** executed from top to bottom in a fresh Python process using sequential IPython with rich-output capture. The full execution took **76.97 seconds**; modeling-stage timing from Task 11 was **70.96 seconds**. No error outputs remain.

The development fits’ maximum final NLL spread across six starts is **2.73e-12 nats**; successful-start counts are recorded per fit. The maximum expected-count discrepancy is **6.82e-13 events**. Because conditional scale normalization explicitly enforces that identity, it checks implementation consistency rather than independently establishing shape accuracy or a global optimum.

Mesh-halving convergence behaves as expected for trapezoidal quadrature. As an additional diagnostic, evaluating the already-fitted rates on 8001 nodes changes a wing’s NLL by at most **7.5e-07 nats** and its KS distance by at most **3.54e-05**. Fits and headline scores retain the mandated 4001 nodes. The fixed mesh spacing is 1.55 days, **coarser than** one-day timestamps; the template’s contrary assertion was corrected.

The missing-integral demonstration drives expected count to overflow. Moving the integration start to s=−3 gives an implied true-window count around 2062 rather than 1590 and shifts the fitted peak by about 1.36 years. Such a calculation deliberately scores events against an inconsistent observation window; it is a failure demonstration, not another valid model comparison.

Exposure is assumed complete for this composite’s recommended span. First observations can lag actual emergence by days, uniform day jitter adds an explicit within-day observation assumption, and a marginal exponential-gap check cannot establish independence. No longitude information or stochastic magnetic-field interpretation is inferred. Week 3 must evaluate pooling on development-cycle folds before any predictive claim.

Catalog SHA256: `be5b107506ab82fcf9658b961f798dbca338854924af22d04b0756d277061dcf`.

Suggested commit message: `Complete Week 2 rate fitting, recovery tests, and diagnostics`.
