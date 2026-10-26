# Homework 1 — first appearances, counts, and rate-sensitive variability

Completed Tasks 1–9 in `01_counting_process.ipynb`, retaining the task specifications and standard setup. All code cells execute in order and seven figures are embedded. `metrics.json` contains the numerical results, random seed, catalog checksum, package versions, and measured execution time.

## What the analysis means

A sunspot group is a collection of dark-looking, cooler surface regions associated with strong magnetic fields. Latitude measures distance north or south of the Sun's equator. One group is recorded on many days; counting every daily row would count it repeatedly. We therefore count each group's **first recorded appearance**, which can occur days after its actual formation.

The analysis selects groups whose largest recorded area exceeds 30 millionths of a solar hemisphere (MSH), in solar cycles 12–23. A cycle's north and south wings are separate **hemicycles**. Each wing's clock `s` is measured in years relative to its modeled 15-degree latitude crossing: years are shifted, never stretched.

## Tasks and findings

1. **Score the existing latitude model.** Negative log-likelihood (NLL) penalizes observed latitudes that the model considers unlikely. Of 22,089 groups represented at their largest area, 110 (0.50%) receive zero density under the legacy model's hard gate. Its honest overall NLL is therefore **infinite**. The **finite-only subset** averages 3.2024 nats/event and excludes those 110 failures; it must not be presented as the full model score.
2. **Compare latitude distributions.** Earth Mover's Distance (EMD) measures the displacement between sampled and observed latitude distributions in degrees. The specified workflow samples the model's Gaussian latitude shape without its time gate. It therefore answers a different question from the full gated NLL. Twenty independent seeded repetitions quantify the additional Monte Carlo variation; they are not confidence intervals for solar behavior.
3. **Build an event table.** Use the earliest timestamp per group, its first non-null cycle label, and its lifetime maximum area for selection. This retrospective area selection uses future observations; it is not an online detection method.
4. **Apply the selection and shifted clocks.** The resulting table has **22,122 distinct groups across 24 hemicycles**, spanning 253.56 summed first-to-last-event hemicycle-years. The descriptive average is **87.24 first appearances per hemicycle-year**. This first-observation table differs from the 22,089-event peak-area table used for the legacy recap.
5. **Plot accumulated counts.** The staircase `N(s)` is the number of first appearances recorded by time `s`. A steep portion means frequent appearances. Groups per wing range from 522 to 1,590.
6. **Measure within-wing gaps.** There are 22,098 successive gaps: median 2.01 days and mean 4.19 days. **3,631 gaps (16.43%) are exactly zero**, reflecting shared recorded timestamps. Gaps are never computed across different wings.
7. **Measure count variability.** The Fano factor is sample variance divided by mean count in equal-width windows. The implementation includes empty windows, excludes trailing partial windows, uses unbiased sample variance (`ddof=1`), and keeps window boundaries half-open.
8. **Check with artificial constant-rate data.** Twenty realizations, each with 24 simulated wings, yield mean Fano values from 0.978 to 1.005 across the specified widths. One lies inside every empirical simulation band. This is a successful sanity check in this configuration, not a universal proof of estimator correctness.
9. **Compare with artificial changing-rate data.** Smooth each observed wing's daily counts over either 365 or 91 days, generate fresh independent Poisson counts, and scatter their times within their day. The last partial day's actual exposure is respected. These are simulations from estimated rates, not new observations and not a procedure for uniquely identifying the real rate.

## What the Fano curves establish

At one day, observed Fano factors are **1.174 north** and **1.157 south**. At 730 days they reach **76.63 north** and **67.72 south**. Large values can arise because a changing average rate makes some equal-length windows much busier than others, even with independent events.

At one day, observed Fano is about 5.8%/5.0% above the north/south 365-day-null means and 4.3%/3.7% above the 91-day-null means. At 27 days, north/south ratios are approximately 1.021/1.001 for the 365-day null but 0.918/0.909 for the 91-day null. Thus the sign of a departure depends on what variability the smoothing procedure incorporates into its rate estimate. Shorter smoothing retains some noisy fluctuations and then adds fresh Poisson variation, which can make that null more variable than the observations.

These results do **not** establish that groups physically trigger their successors, nor do they prove that the Sun's emergence is Poisson. The daily excess concerns recorded first appearances, with simultaneous records and visibility effects. A Fano factor near one is also insufficient to prove independence. A changing-rate Poisson process has independent increments conditional on its rate; its waiting times in ordinary calendar time need not be exponentially distributed or memoryless.

## Validation and limitations

Passed assertions check the expected catalog count, selected event count, unique event IDs, earliest event timestamps, nonnegative within-wing gaps, 24 hemicycles, and exact shift relation `s + t0 = t`. Hand-calculated count examples verify the Fano estimator's empty-bin, boundary, short-interval, and sample-variance behavior. Random seeds and numerical outputs are retained.

The raw file contains 314,648 rows, 249,752 rows with a group identifier, and 46,110 distinct groups. Neither raw data nor `legacy/` was modified. The derived emergence table is rebuilt in ignored `data/derived/`; the given cache-writing cell leaves an existing CSV unchanged, so this notebook's in-memory table is the authoritative analysis input.

Exposure is assumed complete based on the course's reported mean coverage of about 0.99; short missing-observation intervals can still matter. Intervals run from the first to last observed event, rather than independently established observing boundaries. Reference times come from the existing legacy fit; this is a descriptive exercise, not a held-out performance result. Null bands are empirical percentiles of only 20 simulations and omit uncertainty in rate estimation and observing selection. Longitude is deferred, limiting what these latitude/time analyses can say about clustering mechanisms.

Executed using sequential IPython cells with captured stdout and PNG figures because the sandbox prevented Jupyter kernel socket binding. The standard notebook setup cell is unchanged. No claim of student vocabulary mastery or unobserved learning-session dialogue is made here.

Suggested commit: `feat: complete homework 1 counting-process analysis`
