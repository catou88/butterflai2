# Homework 3 — independent checks and remaining uncertainty

The completed notebook runs through Tasks 20–31, and independent recalculation supports the reported likelihood values and fold isolation. This review does **not** certify global optimization, a unique hidden magnetic field, or prospective solar-cycle forecasting. Independent agent review is distinct from external academic peer review.

The retained evidence is [review_evidence.json](review_evidence.json), [numerical_verification.json](numerical_verification.json), [metrics.json](metrics.json), and the executable [verify_numerics.py](verify_numerics.py). Their source fingerprints associate checks with the submitted implementation. The core notebook contains 64 executed code cells, no recorded errors, and a measured runtime of 639.07 seconds.

## Review roles and attribution

The implementation role assembled the self-contained notebook, fitted the models, generated simulations, captured outputs, and recorded optimizer histories. A separate scientific/numerical reviewer checked gradient formulas, the constant-width validation folds and selected optimization continuations. The root integration role packaged the reproducible numerical verifier, retained the review evidence, checked notebook execution, and independently recalculated all returned belt-fold scores using direct intensity formulas. A beginner-comprehension review identified and corrected inherited template claims that confused model strength with observation, smooth emission with a hard cutoff, or conditional assessment with forecasting.

These roles provide complementary checks. Multiple reviewers agreeing is not itself evidence that every model assumption or optimization result is correct.

## Completed independent numerical checks

**Five gradient cases.** A separate reviewer compared the analytic shared-shape gradient with central finite differences at constant width, positive/negative amplitude-dependent exponents, and positive/negative latitude-dependent slopes. The largest scaled discrepancy was **1.76 × 10⁻⁸**, below the specified tolerance of **10⁻⁵**. The direct objective values differed by at most approximately **9.10 × 10⁻¹³ nats**. The gradient after profiling the analytic global scale was checked as well. These tests exercise selected interior parameter cases; they do not prove correctness across the entire parameter domain or at invalid-width boundaries.

The packaged verifier reproduces these selected tests on artificial events, without running the notebook's full data preparation, fits, plots or checkpoint writes:

```sh
python submissions/weeks/week_03/verify_numerics.py --output /tmp/week03_numerical_check.json
```

Constant-intensity likelihood checks also agree with the analytic answer to approximately **4.55 × 10⁻¹³ nats**. The verifier loads the submitted function definitions rather than maintaining a second copied model implementation; the finite-difference and analytic constant-intensity comparisons provide the independent reference quantities.

**All nine constant-width folds.** The original independent reviewer reconstructed raw event pairs, training membership, alignment, origins, amplitude references and area mappings for all nine folds. Maximum differences were approximately **9.28 × 10⁻⁸ years** in shared alignment timescale and **4.79 × 10⁻⁸ years** in origins. Raw event-pair discrepancies were zero. Training-likelihood discrepancies were at most **9.10 × 10⁻¹³ nats**; held-out score, predicted-count and map discrepancies were zero. The reviewer also recalculated fold-specific latitude moments, guarding against accidentally using the full-development shape for a held-out prediction.

**All 27 returned belt folds.** Root integration independently evaluated direct intensity surfaces and recomputed **108 held-out scores**: three width models × nine folds × two hemispheres × two amplitude sources. The maximum discrepancies in NLL, expected counts, area-map coefficients and amplitude references were zero at stored precision. Membership checks confirmed 16 training wings and two held-out wings per fold, excluded the three sealed cycles, and confirmed that models compared the same held-out clocks and events. This validates score bookkeeping for the returned models; it is **not** an independent refit or a convergence certificate for all 27 optimizations.

## Optimization sensitivity remains material

Inner shared-shape calls reported success, but alternating optimization has a separate convergence test and a cap of 16 rounds. Of 34 pooled calls recorded in the core metrics, 25 do not meet that alternating criterion. Among the 27 validation fits, four constant-width folds and all amplitude- and latitude-width folds are flagged. The full-development width variants are flagged as well. A clean execution status must not be substituted for this optimizer audit.

The independent reviewer continued three selected constant-width folds—cycles 14, 19 and 21. Their largest individual held-out score changes were approximately **0.0000494**, **0.000480** and **0.0000555 nats per hemicycle-year**, respectively. These are small sensitivity changes for those selected fits.

The reviewer also continued the amplitude-dependent cycle-12 fit for 16 additional rounds. Its training NLL improved by **0.04604 nats**, its largest held-out score changed by **0.00931 nats per hemicycle-year**, and it still did not meet the alternating criterion. This evidence cannot be extrapolated into a bound on every unchecked variant. Independent reoptimization of all 27 returned folds, a systematic alternative-start study, and a global-optimality proof were not completed.

The reported amplitude-width mean advantage of 0.7201 and latitude-width advantage of 0.1392 are measurements of the returned fits. Their cycle-level SEs, medians and sign counts describe sampling variation in those paired differences; they do not include all unresolved optimization or model-selection uncertainty. The ranking is therefore provisional within the tested belt parameterizations.

## Scientific and educational interpretation

The review distinguishes the fitted belt field, expected intensity, integrated expected counts, and actual recorded events. The field is latent; the catalog does not directly measure it. A smooth softplus response remains positive at zero field. Large fitted amplitudes and a compensating emission scale expose weak identification of physical strength even when the intensity fits well. The single cold-start synthetic recovery checks controlled intensity recovery, not the literal existence of the magnetic belt or a universal percentage recovery guarantee.

The validation design reserves whole cycles, both hemispheres together, and relearns shared quantities from training cycles. Yet each reserved wing supplies its own alignment and full-cycle area summary. The results support retrospective conditional shape comparisons, not an unconditional forecast. Three sealed cycles correspond to six hemispheric wings; no six-cycle holdout was used for the core nine-fold analysis.

The two hemispheres may be correlated, and fold training sets overlap. Consequently, the nine-cycle paired SE is a useful descriptive summary rather than an exact hypothesis test. Same-catalog area/count associations, residual-width slopes, KS diagnostics and feature importances cannot establish causal solar mechanisms. Exposure assumptions, first-observation delays, stable resolution of ambiguous equal-time rows, retrospective selection, unpropagated clock uncertainty and deferred longitude remain limitations.

[FEATURE_REVIEW.md](FEATURE_REVIEW.md) documents supplemental feature redundancy and leakage checks. The separate [MODEL_COMPARISON_REPORT.md](MODEL_COMPARISON_REPORT.md) records the finalized statistical-model benchmark. This review makes no supplementary tree or boosting performance claim before those results are finalized, and the core score audit should not be represented as a completed audit of that separate benchmark.
