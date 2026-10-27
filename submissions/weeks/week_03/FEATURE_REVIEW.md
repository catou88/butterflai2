# Supplementary model and feature review

This is an independent agent review of the feature design and its numerical redundancy, alongside the supplementary model comparison. It is not external journal peer review. The measured feature diagnostics are in `feature_analysis.json`. No supplementary model accuracy is estimated in this feature analysis; model scores and fitted configurations belong to the separate benchmark artifacts.

## What is being predicted

The observed quantities are the first recorded times and latitudes of sunspot groups. The intensity is the expected number of such events per degree of latitude per year. Integrating intensity over latitude gives events per year; integrating over latitude and time gives an expected count. Actual counts vary between realizations. The magnetic belt is one inferred parameterization of that intensity, not a separate magnetic measurement against which the fitted field was verified.

The supplemental statistical models address the same conditional prediction problem as the belt models. Each reserved wing supplies its own data-derived time origin and a retrospective full-cycle area summary. Consequently, the comparison cannot be described as forecasting a future cycle's timing, strength, or sunspot count before the cycle has occurred.

## Validation design

There are 12 catalog cycles in scope. Three sealed cycles—16, 20 and 22—represent six hemispheric wings. The nine development cycles represent 18 wings. Primary leave-one-cycle-out validation has nine folds: train on eight cycles and reserve both wings of the ninth. Leaving out individual catalog rows would answer a different question and allow information about the same solar cycle into training.

The proposed secondary three-fold grouped analysis trains on six development cycles and reserves three development cycles per fold. This is a different training-set size and partition sensitivity check, not “six cycles held out.” It must refit alignment on its own training cycles. The sealed cycles remain excluded from both analyses.

Candidate algorithms and feature bases should be frozen before their supplementary scores are inspected. This is a fixed experimental configuration, not a claim of formal preregistration. If settings are subsequently selected from the nine evaluation folds, the reported winner is exploratory development selection. Estimating the performance of a tuning procedure requires an inner cycle-grouped selection loop confined to each outer training set. The bias from optimizing and evaluating on the same cross-validation results is explained in the [scikit-learn nested-validation example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).

Report per-wing scores plus paired differences, median, sign count and nine-cycle summaries. North and south are paired within a cycle. Cross-validation training sets overlap, so their standard errors remain descriptive rather than exact significance tests. Nine cycles are the available development replication count; this does not establish statistical independence of successive solar cycles.

## Candidate models and permissible information

The frozen comparison configuration contains six candidates: an area-conditioned uniform-intensity Poisson GLM; a time-only Poisson boosting ablation; a shallow Poisson decision tree on raw coordinates; two raw-coordinate Poisson histogram boosting configurations (15 leaves/120 iterations and 31 leaves/160 iterations); and physics-transformed Poisson histogram boosting (15 leaves/120 iterations). The other fixed settings are recorded in `comparison_config.json`. The uniform model checks whether latitude/time structure adds value beyond count scale. The time-only boosting ablation uses both time and area, and stays uniform over latitude; it isolates the value of adding latitude information.

The raw three-feature basis is `[s, |latitude|, log A_area]`. The physics-transformed basis is `[s, |latitude| − mu_train(s), log A_area]`, where `mu_train(s) = 15 exp(−s / mu_b_train)` and the drift timescale is learned only from the relevant training fold. The transformed model is given the same underlying observations through a scientifically motivated coordinate change; its tree partitions have a different geometry. It does not acquire a measurement of the hidden magnetic field.

`A_area` is the same wing's retrospective peak smoothed area summary. It is available under this conditional task, but it would be future information in a prospective forecast. Hemisphere indicators, recent-event history, cycle identifiers, observed total group count, and amplitudes optimized from the reserved wing's event likelihood are excluded from the planned predictive features. The hemisphere and count calculations below are descriptive checks, not additional inputs.

A valid count model retains empty cells and accounts for their exposure. For the frozen quadrature design, midpoint-bounded cells around the 201 × 241 nodes have areas equal to the tensor-product trapezoid weights, including half-width cells at boundaries. Counts divided by cell area can be fitted with that area as the sample weight, following the same exposure principle as the [official Poisson-regression example](https://scikit-learn.org/stable/auto_examples/linear_model/plot_poisson_regression_non_normal_loss.html). A declared piecewise-constant intensity should map physical event positions and integration nodes consistently into these cells; then its complete event-pattern likelihood and the cell-count training objective agree up to data-only terms. The benchmark must document its actual implementation and numerical checks.

Histogram boosting supports Poisson loss. Its automatic early stopping can reserve training rows once there are more than 10,000 rows; fixed `early_stopping=False` avoids a hidden random-row selection step in this grouped experiment. Any deliberate early-stopping validation should instead reserve complete training cycles. These behaviors are specified in the [estimator documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html).

## Measured feature redundancy

The analysis uses every frozen quadrature node for each of the 16 training wings in each primary fold: 775,056 representative rows per fold, weighted by domain exposure. These are numerical coordinates, not 775,056 independent observations of solar cycles. Each training fold covers 16,320 degree-years of integration exposure. No inference p-values are computed.

Three predictor bases were compared using weighted correlations, standardized matrix rank, condition number, and variance inflation factors (VIF). A VIF describes how well one predictor can be reconstructed by a linear combination of the others; it is not a model's predictive accuracy.

- **Raw three-feature basis:** rank 3 in every fold; all VIFs are 1.000 and the standardized condition number is approximately 1. The raw coordinates are orthogonal because this is a Cartesian integration design with the same latitude/time domain for each wing. This does **not** mean that event latitude and time are independent in the observed Sun.
- **Physics-transformed three-feature basis:** rank 3 in every fold. The VIFs of time and latitude residual range from 1.181 to 1.188; the area VIF remains 1.000. Standardized condition numbers range from 1.512 to 1.524. This avoids exact linear redundancy while representing displacement from the training drift curve.
- **All five candidate columns together:** `[s, |latitude|, log A_area, mu_train, residual]` has rank 4 rather than 5 in all nine folds. The identity `residual = |latitude| − mu_train` is exact by construction. Latitude, drift position and residual have infinite VIFs and the design condition number is infinite. The time VIF ranges from 14.524 to 15.141. Including all five gives redundant coordinates rather than five distinct measurements.

The deterministic nonlinear relationship between time and the exponential drift remains even when there is no exact linear dependence. Linear VIF alone cannot diagnose every nonlinear redundancy. Conversely, large VIF is principally a warning for separate linear coefficient interpretation; it does not automatically disqualify trees. For tree ensembles, correlated or interchangeable predictors can make individual feature-importance values misleading. Prefer the fixed whole-basis comparison and scientifically grouped ablations; ordinary one-feature permutation can create impossible combinations such as a residual inconsistent with latitude and drift. The [official correlated-feature importance example](https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance_multicollinear.html) illustrates this interpretation problem.

## Descriptive area and hemisphere checks

Across the 18 development wings, Pearson correlation between log area amplitude and log observed event count is 0.934; Spearman correlation between area and count is 0.913. This supports treating area as a potentially useful conditional count-scale covariate, but it is not independent validation: both summaries come from the same catalog, and count remains an outcome rather than an input.

Correlation between log area and the north-hemisphere indicator is −0.084. Mean area amplitudes are 0.1660 north and 0.1712 south in the course's normalized area units. North exceeds south in four of the nine cycles; the paired north-minus-south mean is −0.00518 and median is −0.00144. Across the nine cycle pairs, north and south area amplitudes correlate at 0.769. These small-sample descriptions do not establish hemispheric equivalence or an absence of physical asymmetry. They reinforce the choice to reserve both hemispheres together and offer no basis here for adding hemisphere as a predictive feature.

## Astrophysical interpretation and limits

The completed belt fits use very large field amplitudes relative to the imposed threshold, placing much of their fitted emission in an approximately linear high-field regime. Their zero-field floor is small in this fitted configuration, but not mathematically absent. Good predictions of event intensity can coexist with poor identification of internal field strength or buoyancy-threshold physics. A flexible statistical baseline is useful precisely because it asks whether the observed latitude/time/area relationships can be described without committing to a unique interior magnetic field.

A machine-learning gain would support that model's conditional intensity performance under this design. It would not refute magnetic buoyancy, establish causal triggering, or turn a statistical residual into a magnetic observation. A belt-model gain would support its chosen low-dimensional restrictions, rather than proving its literal hidden geometry. These are model comparisons for a limited first-observation catalog with assumed exposure, measurement delays, retrospective selection and deferred longitude.

For context, [Cloutier, Cameron and Gizon (2024)](https://arxiv.org/abs/2405.17185) analyze observed surface magnetic butterfly diagrams and their averaged relationship to surface field generation. Their magnetographic constraints differ from this project's group first-observation catalog. Our exercise must not be presented as making equivalent measurements of interior magnetic field strength.

Trees also have limited extrapolation beyond training feature support: an unusually strong reserved wing can receive a boundary-partition prediction, whereas the fitted belt amplitude map extrapolates as a power law. Which cycles drive a score difference matters. Minimum leaf size in the benchmark counts numerical quadrature rows rather than independent sunspot groups.

The feature analysis is reproducible from the completed core metrics and its recorded fold provenance. `feature_analysis.json` records the source metrics checksum, catalog checksum, feature definitions, weights, per-fold matrices and diagnostics, area summaries, package versions, and runtime. No sealed-cycle scores or unrun model results are included.
