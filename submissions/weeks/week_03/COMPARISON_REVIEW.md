# Independent review of the supplementary model comparison

Independent recalculation reproduces all **216 saved wing scores from 72 fitted-model artifacts**. The raw-coordinate, 15-leaf boosting configuration has the lowest average leave-one-cycle-out NLL, but its advantage over the drift-residual configuration is smaller than the descriptive cycle-level standard error. The comparison supports a competitive set of statistical intensity models, not a unique physical or universally best algorithm.

This review checks returned predictions, cohorts, numerical scoring and interpretation. It does **not** constitute a second independent training run, independent optimization of every candidate, or external academic peer review. The benchmark's executable implementation is [model_comparison.py](model_comparison.py), with settings in [comparison_config.json](comparison_config.json), results in [comparison_metrics.json](comparison_metrics.json), and per-wing scores in [comparison_scores.csv](comparison_scores.csv).

## What was independently checked

The audit rebuilt the first-observation event catalog from the raw daily measurements, preserving the stable source-row convention for equal-time records. It did not import the benchmark's catalog, feature or scoring functions. It reconstructed cell assignment by comparing event coordinates with cell midpoints, and integrated the saved intensities using independently constructed cell areas.

All **72 saved prediction files** were inspected: six fixed candidate configurations across nine leave-one-cycle-out folds and three grouped folds. Their **216 wing predictions** were independently rescored. These are 72 fitted artifacts, not 72 independent solar datasets. The nine-fold analysis trains on eight development cycles and reserves one; each secondary fold trains on six cycles and reserves three.

The audit confirmed:

- Held-out cycles were excluded from training groups in all 12 partitions; the sealed cycles 16, 20 and 22 were excluded throughout.
- All primary held-out physical event pairs and time origins matched the corresponding core belt-fold cohorts exactly. Different source ordering among equal-time events was handled by setwise cohort verification, with core ordering retained for the common jitter calculation.
- Every training wing contributed the entire 201 × 241 count grid, including zero-count cells. Grid counts summed to the training event total, and every cell had positive integration exposure. Each wing covered 1,020 degree-years.
- All saved intensity surfaces were finite, had the required 241 × 201 layout, and respected the declared positive intensity floor.
- Recomputed expected counts and event-pattern NLLs matched the saved results with **zero discrepancy at stored precision**.
- Exact uniform-within-cell latitude centroids differed by at most **1.42 × 10⁻¹⁴ degrees**, and spreads by at most **2.49 × 10⁻¹⁴ degrees**.
- An independently constructed compensator, integrating cell overlaps directly, and a direct empirical-versus-exponential CDF calculation reproduced the descriptive KS distances within **2.54 × 10⁻¹³**. The same fixed jitter seed convention is now used for the primary belt and supplemental comparisons.
- A separate simultaneous least-squares alignment fit reproduced the secondary grouped-fold clocks: shared timescale differences were at most **1.43 × 10⁻⁷ years**, and held-out origin differences at most **3.18 × 10⁻⁸ years**. Returned-score recalculation used the stored benchmark origins; the separately fitted origins were a distinct consistency check.

The current script checksum and all six candidate definitions matched the saved configuration and result manifests. Poisson boosting loss and disabled automatic early stopping were verified. This confirms configuration consistency; it is not an externally attested preregistration history.

## Why the likelihood comparison is valid

Each supplemental model predicts an intensity that is constant within the fixed node-centered cells. An observed event receives its cell's predicted intensity, and the expected-count term sums intensity times each cell's latitude–time area. This is a complete event-pattern score, including unoccupied cells.

For a cell with count `n`, exposure `E`, target `n/E` and weight `E`, the Poisson data-loss term is equivalent to `E * intensity − n * log(intensity)`, apart from data-only constants and conventional scaling. This matches the negative event-pattern likelihood for that piecewise-constant intensity. Boosting's additional L2 regularization is a training restriction; the reported likelihood is scored without that training penalty. The match concerns the Poisson data term rather than every term of the regularized optimization objective.

The statistical models and belt models use the same reserved physical events, units, time window, latitude domain and frozen integration convention in the primary comparison. Their functions differ: the belt is smooth, while the supplemental model is explicitly cellwise constant. The declarations and independent recalculation avoid silently changing the scoring definition when changing algorithms.

## The top average is not a uniquely resolved winner

Lower NLL is better. In primary leave-one-cycle-out evaluation:

- Raw-coordinate boosting with 15 leaves/120 iterations averages **−26.9856 nats per hemicycle-year**.
- Drift-residual boosting with 15 leaves/120 iterations averages **−26.8704**.
- The amplitude-dependent belt averages **−26.0987** for its returned approximate fits.

For **raw boosting minus residual boosting**, the mean NLL difference is **−0.11513**, but the descriptive SE over nine cycle averages is **0.17958**. The median difference is **+0.17129**, and raw boosting is better in only **8 of 18 wings** and **4 of 9 cycle averages**. Thus the raw model's small mean advantage does not meet the assignment's own mean-versus-SE rule for separating these candidates. The median and sign count favor the residual model on a typical reserved unit.

For **raw boosting minus the amplitude-dependent belt**, the mean difference is **−0.88690**, median **−0.71855**, and cycle-level SE **0.49295**. Raw boosting improves **12 of 18 wings** and **7 of 9 cycle averages**. This is a meaningful observed advantage for the returned configurations, approximately 1.8 descriptive SEs, rather than a decisive significance result or an optimization-independent bound. The belt fits retain the convergence qualifications in [REVIEW.md](REVIEW.md).

In the secondary six-cycle-training analysis, residual boosting has the lowest mean among the six supplemental configurations: **−26.9619**, compared with **−26.7671** for raw 15-leaf boosting. This changes both training-set size and partition structure. It is a robustness comparison, not an additional independent test of the primary winner; belt models were not refitted under these secondary partitions.

## Scientific interpretation

The statistical models predict recorded first appearances, conditional on data-derived clocks and retrospective area summaries. They do not measure the interior magnetic field, isolate buoyancy physics, or forecast a cycle before its full area record exists. The residual-coordinate transform incorporates a training-derived drift curve; it reorganizes the same latitude/time information rather than adding a new magnetic observation.

The many grid rows represent integration and count structure. They do not enlarge the independent cross-cycle sample beyond nine development cycles. North and south remain paired, and validation training sets overlap. Correlated features, implicit extrapolation limits of trees, area-feature selection, observing delays and missing exposure remain relevant; see [FEATURE_REVIEW.md](FEATURE_REVIEW.md).

The observed rankings are informative about conditional intensity modeling under these specific choices. They support reporting both leading boosting variants, paired uncertainty and diagnostics, alongside the interpretable belt benchmark. They do not support claiming that a single algorithm has established the Sun's underlying emergence mechanism.
