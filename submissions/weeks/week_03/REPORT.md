# Homework 3 — model intensity, inferred belt, and conditional cycle comparisons

Tasks 20–31 are implemented and executed in [03_latent_belt.ipynb](03_latent_belt.ipynb). The run completed **64 code cells with no recorded execution errors**, taking **639.07 seconds**. Numerical outputs and optimizer histories are retained in [metrics.json](metrics.json). The returned amplitude-dependent width model has the best average held-out score among the three tested belt models, but incomplete optimization and limited cycle replication qualify that ranking.

## What the model actually learns

A sunspot group's first recorded appearance supplies an observed time and latitude. It does not supply a measurement of the magnetic field below the Sun's surface. We posit a drifting magnetic band `B(latitude, s)` and an emission rule that converts it into intensity `Lambda(latitude, s)`.

These are different objects:

- `B` is inferred model strength, expressed relative to an imposed critical scale. It is not a measurement in gauss or tesla.
- `Lambda` is expected groups per degree of latitude per year.
- Integrating `Lambda` over latitude gives a time-dependent expected rate, in groups per year.
- Integrating over latitude and time gives an expected count. The observed count is one random realization.

Fitting chooses model parameters using the observed event times and latitudes, including the likelihood's required integral penalty. It does not match the inferred belt to an independently measured field history. Several parameter combinations can explain similar intensities.

The analysis uses **16,611 events across nine development cycles, or 18 hemispheric wings**. Cycles **16, 20 and 22 remain sealed**: three whole cycles, equivalent to six wings. Six whole cycles were not withheld.

## Tasks 20–24: clocks, field, emission, and likelihood

**Task 20** estimates an initial time origin from each wing's downward 15-degree latitude crossing. **Task 21** refines the origins with a shared exponential latitude drift and a separate shift per wing. Time `s` is years relative to the fitted origin: dates are shifted, never stretched. The pooled alignment timescale is **8.0276 years**, with conditional Jacobian standard error **0.1091 years**. The average conditional standard error of a wing's shift is **0.1114 years**. These errors assume the selected curve and independent, equal-variance residuals; they omit several observational and model uncertainties.

**Tasks 22–23** implement the Gaussian belt and smooth emission `c * softplus(B − 1)`, fixing the exponent to one. The response has no hard cutoff. At zero field, `softplus(−1)` is about 0.313 before multiplication by `c`. In the fitted constant-width model, this floor corresponds to **0.1731 expected groups per wing** over the specified domain.

**Task 24** implements the full two-dimensional event-pattern likelihood. Its scoring domain is fixed at **s = −6 to +11 years** and **absolute latitude 0 to 60 degrees**, with a **201 × 241** trapezoid mesh. Constant-intensity cases agree with their analytic likelihood to approximately **4.55 × 10⁻¹³ nats** in the independent numerical check. A two-dimensional latitude/time likelihood cannot be ranked directly against Homework 2's time-only likelihood: they score different observed quantities and reference units.

## Tasks 25–26: pooling and parameter limits

Task 25 fits each wing's amplitude conditional on a shared shape; Task 26 alternates shared-shape and amplitude updates and solves the global emission scale analytically. The constant-width emission model has six shared parameters and 18 wing amplitudes, conditional on previously estimated clocks.

Its full-development fit gives time-shape parameters `k = 7.7669`, `theta = 0.8112 years`, drift parameters `mu_a = 14.5832 degrees`, `mu_b = 7.2261 years`, width **6.4546 degrees**, and emission scale **0.0005416**. This intensity drift need not equal the least-squares alignment drift; the two fitted curves answer different questions.

Peak belt amplitudes range from approximately **11,450 to 34,884 times the chosen critical scale**. Their large values put much of the response in an approximately linear high-field regime, where field amplitude and emission scale can trade off. These numerical strengths should not be interpreted as measured solar magnetic fields. Fixing a threshold convention does not solve every identifiability problem.

The fitted total expected count equals 16,611 by the analytic scale identity. This is a property of maximum likelihood with a freely fitted global multiplier, not independent predictive validation. The in-sample negative log-likelihood is **−26.5899 nats per hemicycle-year**. Negative values are valid with these fixed intensity units; lower NLL is better.

## Task 27: generation and controlled recovery

Thinning generates new artificial events from a fully specified intensity. It does not estimate the intensity or remove actual observations. One independently simulated pooled dataset contained **16,750 events**, compared with **16,611 expected events**. The subsequent fit used fixed initial constants, without being supplied the generating parameters.

The mean relative integrated absolute error between recovered and generating intensities was **0.03309**, approximately 3.31%. This is an intensity-error measure, not “96.69% accuracy.” It is one simulation trial, not a repeated-simulation confidence interval. Raw field-strength ratios remain weakly identified, so recovery of an intensity surface is more informative here than forcing every parameter to agree to an arbitrary percentage. Passing this controlled check does not establish that the Sun possesses this exact belt or follows this emission law.

The synthetic butterfly diagram is compared with the observed training wings in sample. Visual resemblance is a plausibility check, not held-out evidence or a magnetic measurement.

## Task 28: nine leave-one-cycle-out folds

Each fold trains on eight complete development cycles and reserves both wings of the ninth. Shared alignment, pooled shape, area-to-amplitude mapping and variant initialization exclude the reserved cycle. The held-out wing still supplies its own time shift and a full-cycle area summary. This is therefore a **retrospective conditional shape evaluation**, not a forecast of a future cycle's dates, size, or field strength.

The constant-width model's mean held-out NLL is **−25.3786 nats per hemicycle-year**. Its between-wing score standard deviation is **17.9941**; that spread is not an error bar on a model difference. Using the area summary for amplitude rather than fitting amplitude from the reserved events costs **0.2767 nats per hemicycle-year** on average, with descriptive nine-cycle SE **0.0847**. The own-event amplitude score is an optimistic fitted diagnostic.

The constant-width model's held-out mean absolute percentage count error is **8.77%**, reaching **30.68%** for the worst wing. Latitude-centroid RMSE is approximately **1.263 degrees** and spread RMSE **0.842 degrees**. These are computed from fold-specific predictions, rather than the full-development model.

For timing alone, the median descriptive time-rescaling KS distance is **0.03030** for the pooled belt and **0.02452** for independently fitted direct gamma rates on the development wings. This is an in-sample timing diagnostic under a stated jitter policy; fitted-data KS probabilities are not calibrated process-validity tests.

## Task 29: changing the scoring ruler

Keeping the fitted model and observed events unchanged, coarsening the mesh raises its log-likelihood score by **0.03933 nats per hemicycle-year**. Extending latitude to 90 degrees changes the score by **−0.00509**, while extending time to +15 years changes it by **−5.07411**, including a different per-year denominator. These are changes in the scoring definition, not improvements to the predictions.

In the separate mesh-refinement experiment, the frozen-mesh fitted model differs from fine-reference scoring by approximately **0.000542 nats per hemicycle-year**. Numerical accuracy depends on the integrand, and every comparison must state its mesh, window, latitude domain and units.

## Tasks 30–31: what “spread” means and which width rule scores better

The observed spread can mean raw latitude standard deviation or residual standard deviation after subtracting the fitted drift at each event. Raw spread includes the latitude range traversed over time. Residual spread also reflects emission, truncation, observation effects and drift-model mismatch; it is not a direct measurement of a hidden magnetic belt width.

Across the 18 development wings, the slope of log spread against log event count is **0.3389** for raw latitude and **0.3888** for drift residuals. These are descriptive associations, not causal scaling laws.

All three belt rules score the same physical held-out events, using the same fold-specific clocks and domain:

- **Constant width:** mean held-out NLL **−25.3786** nats per hemicycle-year.
- **Amplitude-dependent width:** mean held-out NLL **−26.0987**. Relative to constant width, mean gain is **0.7201**, median gain **0.2827**, with descriptive SE **0.3331** over nine cycle averages. It improves **15 of 18 wings** and **7 of 9 cycle averages**. The strongest individual gain is **5.6716**, so the mean alone overstates the typical improvement. The full-development fitted exponent is **0.7461**.
- **Latitude-dependent width:** mean held-out NLL **−25.5177**. Mean gain is **0.1392**, median gain **0.0835**, with descriptive nine-cycle SE **0.0651**. It improves **14 of 18 wings** and **8 of 9 cycle averages**. Its fitted descriptive rule is approximately `w = 4.8018 + 0.10551 * mu`, in degrees.

Here a positive gain means lower NLL than constant width. Standard errors over 18 wings are also recorded in the metrics, but north and south of a cycle are related. Training sets overlap between folds, so even the cycle-level SE is descriptive rather than an exact significance test. Selecting variants on these development folds does not supply a new independent test.

## Optimization and review qualifications

Every inner shared-shape optimizer returned a success status, but alternating optimization has a separate stopping criterion and a cap of 16 rounds. Across 34 recorded pooled fitting calls, **9 meet that criterion and 25 do not**. Among the 27 validation fits, **5 of 9 constant-width folds meet it; none of the 9 amplitude-width or 9 latitude-width folds do**. Both full-development width variants are also flagged. A successful notebook run does not mean a globally optimal fit was established.

Independent continuation of selected constant-width folds changed individual held-out NLL scores by less than **0.0005 nats per hemicycle-year**. Continuing the amplitude-width cycle-12 fit changed its largest held-out score by **0.00931** and still did not meet the alternating criterion. These selected checks are useful sensitivity evidence, not an upper bound on unresolved optimization error across all variants. The returned width ranking is therefore a measured result for these approximate fits, not a certified globally best astrophysical model.

Independent direct recalculation of all 27 returned belt folds reproduced 108 held-out scores and their counts, maps and references at stored precision. This checks the returned parameters and bookkeeping, not independent reoptimization. [review_evidence.json](review_evidence.json) retains those checks. [REVIEW.md](REVIEW.md) separates completed independent checks from implementation assertions. [verify_numerics.py](verify_numerics.py) and [numerical_verification.json](numerical_verification.json) provide the retained numerical verification. [FEATURE_REVIEW.md](FEATURE_REVIEW.md) and [feature_analysis.json](feature_analysis.json) examine the supplemental feature design. The separate [MODEL_COMPARISON_REPORT.md](MODEL_COMPARISON_REPORT.md) reports supplementary statistical models once their benchmark is finalized; this core report makes no unmeasured tree or boosting claim.

First-observation delays, uncertain observing exposure, same-time catalog ambiguities, retrospective area selection, unpropagated clock uncertainty, the deterministic latent assumption, and deferred longitude limit physical conclusions. These constraints should accompany any presentation or resume claim based on the results.

Suggested core commit message: `feat: complete homework 3 latent-belt analysis and cycle validation`
