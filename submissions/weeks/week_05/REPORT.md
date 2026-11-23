# Homework 5 — Neural fields: does a more flexible belt predict emergence better?

Tasks 44–55 are implemented in [05_neural_fields.ipynb](05_neural_fields.ipynb). The notebook runs top to bottom
with **no errors and no live `raise NotImplementedError`**. The full run from an empty cache takes about 10 minutes
on a laptop CPU. Every number below is in [metrics.json](metrics.json), which
[collect_metrics.py](collect_metrics.py) rebuilds from the caches and the executed notebook.

> **Read this first: these are `taste`-profile numbers, two scored wings deep.** This machine has no GPU, so the
> notebook chose its CPU profile automatically. That profile uses 4 northern wings (13N, 14N, 18N, 19N), a
> width-16 network, 300 epochs, and two scored folds (cycles 18 and 19).
> - The protocol fingerprint `e65670626346` encodes the profile, so these rows cannot be mixed with `full` rows.
> - The `full` profile was measured at ~0.8 s per epoch on this CPU, roughly 6 h for the notebook, against about
>   8 min on a GPU.
> - The notebook's own closing text (Section 7: "a tie", "the champion's 1.3") describes the **GPU** profile.
>   It does not describe the numbers below.

Cycles 16, 20 and 22 were never fitted or scored. Longitude is deferred, and the latent field is deterministic.

## The answer, in one table

The quantity is held-out negative log-likelihood (NLL), in nats per hemicycle-year. **Lower is better.**
"vs champion" is the paired, wing-by-wing difference against the course's Week 4 champion; negative means the
model is better. Every neural row carries its seed and its epoch budget.

| model | fitted numbers | held-out NLL | 18N | 19N | vs champion (mean ± SE) | KS median |
|---|---|---|---|---|---|---|
| **champion** (course Week 4) | 15 | **−65.999** | −54.77 | −77.23 | — | 0.060 |
| neural **concat** (seed 42, 12 epochs) | 642 | −53.333 | −48.93 | −57.74 | +12.67 ± 6.83 | 0.070 |
| my Week 4 model (catou88) ‡ | 13 | −48.243 | −52.02 | −44.46 | +17.76 | 0.113 |
| Week 3 baseline | 10 | −41.768 | −50.76 | −32.78 | +24.23 ± 20.22 | 0.113 |
| neural **FiLM** (seed 42, 8 epochs) | 898 | −26.725 | −47.46 | −5.99 | +39.27 ± 31.97 | 0.140 |
| neural **none** (seed 42, 4 epochs) | 610 | −7.508 | −48.16 | +33.14 | +58.49 ± 51.88 | 0.280 |

‡ Extension, not a course task: my Week 4 submission (two-sided time profile, amplitude-dependent width,
Student-t belt), refitted by the same `run_variant` on these folds.

No model beats the champion on either wing. The KS test rejects every model on both wings at 5%, apart from two
`none` runs on 18N, so on the KS side every model fails.

**Robustness across seeds.** The notebook's own seed check re-runs concat on cycle 18 at seeds 42, 43 and 44:
−48.93, −36.93 and −45.04, a spread of **6.12**. That number comes from the *easy* fold only. The extension
re-ran all three variants at all three seeds on both folds:

| variant (3 seeds × 2 wings) | held-out NLL, mean ± seed sd | vs champion, mean | wing-seed pairs better than champion |
|---|---|---|---|
| concat | −41.54 ± 17.68 | +24.46 | 0/6 |
| FiLM | −27.39 ± 18.32 | +38.61 | 0/6 |
| none | −19.73 ± 15.69 | +46.27 | 0/6 |

**Conclusions, in decreasing order of confidence:**

1. **On this profile the parametric champion is better than every neural variant.** It wins on all 6 wing-seed
   pairs, by 12.7 nats at seed 42.
2. **Conditioning on amplitude helps:** concat is the best neural variant at every seed. FiLM vs none is *not*
   stable: none beats FiLM at seed 44.
3. **Averaged over seeds, the best network only ties the 10-parameter Week 3 belt** (−41.5 vs −41.8).
   - At seed 42 it beats the belt; at seed 44 it scores −21.2.
   - My Week 4 model (−48.2) beats both.

## Why: an extrapolation on 19N, and a fit that never leaves its warm start

**19N is an extrapolation.** Holding out cycle 19 leaves 13N, 14N and 18N to train on, so the conditioning scaler
comes from amplitudes 0.097–0.193. On that scale 19N (A = 0.315) sits at **+3.0 standard deviations** of log A,
outside anything the network saw. The 19N column shows it:

- the networks scatter from −63.9 to +33.1 across variants and seeds;
- concat alone gives −57.7, −63.2 and +2.6 at seeds 42–44;
- the champion carries amplitude through fitted physical stages (an amplitude-driven time shift, an instantaneous
  width, a late gate), which extrapolate gracefully.

**18N is inside the range, and the network still does not beat the belt there.** On 18N:

| model | 18N score |
|---|---|
| champion | −54.8 |
| my Week 4 model | −52.0 |
| Week 3 belt | −50.8 |
| concat, seeds 42 / 43 / 44 | −48.9 / −36.9 / −45.0 |

**The budgets are tiny, and they sit in Adam's start-up transient.** The given learning rate is 3 × 10⁻³, and the
validation curves (Figure 5) oscillate for the first ~30 epochs. The honest budgets come out as **none 4, concat
12, FiLM 8** epochs. The neural rows are therefore "a warm-start copy of the Week 3 belt, plus a handful of Adam
steps". Two consequences follow:

- A budget picked as the minimum of an oscillating curve is itself noisy.
- The network never gets the long, stable training that would let it move far from the belt.

A learning-rate warm-up or a smaller rate would be the natural fix, and it is the next experiment. On three
training wings, longer training mostly overfits: 13N's score climbs from −9.6 to +7.1 by epoch 300.

**This is a statement about three training wings and this protocol, not about neural fields.** The `full`
profile trains on 16 wings, and 19N sits inside its amplitude range.

## Section by section

**Task 44: the likelihood in torch.**
- The torch loss agrees with the numpy loss to **1.4 × 10⁻¹⁴** nats per hemicycle-year in float64, and to
  **1.5 × 10⁻⁵** in float32.
- The check uses the champion's own latent field, recovered exactly through `B = softplus⁻¹(Λ/c) + 1`. That is
  possible only because the emission is fixed by the gauge (B_crit = 1, α = 1, one global c).
- So the plan stands: train in float32, score in float64 with the Phase A numpy likelihood.

**Task 45: the network.**
- A 3 × 16 tanh perceptron with 609 weights.
- Its output is log B on a fixed scale, `log B = 1.151 + 8.059 × output`, built from two round constants
  (B_start = 10⁴, B_floor = 10⁻³) and **not from any fitted field**, so normalisation cannot carry a held-out wing
  into a fold.
- It starts as a flat field at B = 10⁴, far above critical, so the likelihood has a gradient everywhere.

**Task 46: the warm start.** In log B the regression error falls from 97.45 to **0.218**. One field for four
belts cannot do better than 0.112, so the copy is within a factor of two of that limit. Most of the remaining error
sits in the floored corners where B < B_floor, not on the ridge.

**Tasks 47–48: training.**
- The unconditioned field reaches −30.45 in sample. That is worse than the Week 3 belt (−33.09) and the champion
  (−41.38): **609 weights, but no way to tell the wings apart.**
- The given rate of 3 × 10⁻³ makes Adam overshoot at first: the loss goes from −27.9 to −19.9 over the first two
  steps, then oscillates down. I checked that this is the optimizer, not a bug:
  - a directional finite difference matches autograd (−4.70 × 10⁻³ actual vs −4.74 × 10⁻³ predicted);
  - ∂loss/∂log c = 0 at the count-matched c, as the theory requires;
  - at 3 × 10⁻⁴ the loss falls monotonically.

**Task 49: the epoch budget and the stopping leak.** Watched runs are scored before the first step and after every
epoch. The task suggests every epochs // 60, which is 5 here, but that grid would have quantized these short
budgets.
- **Honest budget.** The unconditioned field, watched on cycle 13, is best after **4 epochs**. Training on stronger
  wings then over-predicts the weak 13N.
- **Forbidden version.** It is run like a fold: trained without cycle 18 and warm-started from that fold's own
  Week 3 belt. It shares the honest run's standard clock, as the task prescribes.
  - Stopping where cycle 18 itself likes best (epoch 300, the cap) would have reported **−1.87 nats** better.
  - That is a lower bound, because the best sits at the cap.
- **For comparison:** Week 4's amplitude leak was +0.279 and its fitted-shape bound +1.94. The stopping leak is the
  easiest of the three to commit by accident: an `EarlyStopping` callback pointed at the wrong set does it silently.

**Tasks 50–51: conditioning, learning rate, budgets.**
- **Inputs:** the wing's own standardized log A and hemisphere. On this profile the hemisphere is the constant +1,
  since all wings are northern. No event times and no opposite hemisphere enter.
- **FiLM check:** the notebook asserts that FiLM, with its modulation zero-initialised, reproduces the unconditional
  network exactly.
- **Tie rule:** fixed before any run. Lowest cycle-13 score wins; anything within 0.05 nats counts as tied; among
  tied rates the cheapest wins.

| learning rate | best cycle-13 score | at epoch | |
|---|---|---|---|
| 3 × 10⁻⁴ | −7.64 | 97 | |
| **3 × 10⁻³** | **−9.56** | **12** | **chosen, no tie** |
| 3 × 10⁻² | −6.24 | 0 (the warm start itself) | diverged afterwards (training NLL +130) |

The concat network's predicted count rises smoothly with A through the observed range (Figure 6a).

**Task 52: the fold runner.** Inside each fold, these all come from the training wings alone:
- the clock;
- the conditioning scaler;
- the warm-start target (that fold's own Week 3 belt);
- the network.

The cache key is generated from the configuration: variant, seed, folds, budget, rate, size, and a hash of every
warm-start setting. Rows use Week 4's column names and jitter seeds. `a (area record)` is left empty, because a
network has no fitted belt amplitude; the input amplitude is stored in its own column. Each fold's weights are saved
beside its JSON. Two checks on the runner:
- **Determinism:** a second run from an empty cache reproduced every score.
- **Fold independence:** the one-fold seed run and the two-fold run give identical 18N scores.

**Task 54: generating held-out cycle 18.**

| cycle 18 | count | latitude centroid | latitude spread |
|---|---|---|---|
| observed | 1138 | 15.18° | 6.70° |
| network | predicted 1195, simulated 1212 | 16.20° | 7.85° |
| champion | predicted 1058, simulated 1129 | 15.37° | 7.19° |

The network's synthetic wing sits about 1° too high and is slightly too wide. Its time marginal overlaps the
champion's (Figure 9d). The thinning bound was the mesh maximum × 1.05, because a network has no analytic supremum.
`simulate_wing` would have raised an error if any proposal exceeded it; none did.

**Task 55, plus the warm-start control from the extension.**

| on 19N / over 4 wings | belt centre at s = 0 | last s with a ridge | envelope-peak slope (yr per unit log A) |
|---|---|---|---|
| Week 3 belt (the warm-start target) | 14.50° | 11.0 | 0.000 (by construction) |
| network, warm-start copy, **0 likelihood steps** | 16.50° | 6.3 | −0.076 |
| network, **after 12 likelihood steps** | 16.25° | 6.0 | **−0.976** |
| champion | 12.8° | — | −1.706 |

- **The timing slope is learned.**
  - The copy has essentially none (−0.08). Twelve likelihood steps, told only log A, produce −0.98 yr per unit
    log A: stronger wings peak earlier after their 15° crossing.
  - That is the sign of the **Waldmeier effect**. Hathaway (2015, *Living Rev. Sol. Phys.* 12, 4) gives rise time
    ≈ 35 + 1800/R months, about −0.75 to −1.5 yr per e-fold. Cameron & Schüssler (2016, *A&A*) align cycles on the
    15° crossing and find that weak cycles run about 2 yr longer.
  - **Caveats:**
    - this is an in-sample regression on 4 wings, two of them close together in A;
    - its size depends on the budget (an earlier run with a 20-epoch budget gave −1.42);
    - the effect is reported to be weak in area-based amplitudes (Dikpati et al. 2008).
  - **The sign agrees with the literature; the size should not be trusted at this depth.**
- **The belt centre at s = 0 is not evidence.**
  - The network's 16.25° on 19N was already 16.5° in the warm-start copy, an artifact of the regression rather than
    something the events taught it. I withdraw my earlier reading of it as an "independent witness" against the
    champion's 12.8°.
  - With 12 steps from a copy, the network cannot settle the open question. The champion's 12.8° is still more
    plausibly a consequence of its drift and width shapes than of the Sun, but that is a hypothesis, not a result.
- **The ridge** now leaves out times where B is below critical everywhere, or where the maximum sits on the λ = 0
  boundary. Beyond s ≈ 6 the network's field peaks on the equator boundary, a region with almost no events. The
  copy already does this, so it is inherited, not learned.

## Leakage and identifiability

**Checked:**
- withheld cycles never fitted or scored;
- inside every fold: no held-out events, scaler, clock or warm-start target;
- budgets and learning rate chosen on cycle 13 only;
- conditioning limited to the wing's own area record and hemisphere;
- output normalisation built from constants;
- the leak run warm-started from its fold's own belt.

**Second-order dependencies, by design of the task:**
- The learning rate and budgets are chosen by models trained on 14N, 18N and 19N, which include both scored wings.
  They run on the standard clock and warm-start from a belt fitted on all four wings. So the *choice of setting* has
  seen scored events, though no score was ever watched.
- Section 4's conditioning scaler includes 13N's area record. No scored information enters, but 13N is
  standardized to −1.11 rather than the ≈ −1.65 a training-only scaler would give.
- The given parametric folds warm-start from the all-wing fit.
- The given 365-day centred area smoothing can leak a withheld cycle's area into a neighbour's amplitude.

**Identifiability:**
- B means something only because the emission is fixed. The log-B output scale is a reparameterisation of the head,
  not a fitted number.
- The amplitude A is built from the *same catalog's* group areas, so a rising count with A is partly mechanical.
- Whether strong cycles sit higher at a fixed s, or only shift activity to earlier s, cannot be separated on four
  wings.

**Assumptions:**
- Exposure is treated as complete (mean coverage ~0.99 for cycles 12–23).
- First observation is treated as emergence: groups are first seen at a median ~65° from the central meridian. That
  matters at day scales, not at the year scales measured here.
- The 1976 RGO-to-SOON area calibration affects cycles 21–23, none of which is in this profile.

**Not comparable:** the board's in-sample column means different things for different rows.
- *Neural rows:* the mean over folds of the training-wing NLL (3 wings, fold clock).
- *Parametric rows:* the all-wing fit.

## Predictions, checked

The course asks the student to write four predictions in a tutor session before running anything. **No tutor
session was held.** I wrote the predictions below before any neural fit ran, and they are mine, not the student's.

| # | prediction (written before running) | measured | verdict |
|---|---|---|---|
| 1 | In sample, the unconditioned network is worse than the champion | −30.45 vs −41.38 | right |
| 2 | Held out, the conditioned network is worse than the champion (3 training wings) | +12.67 (concat), 0/6 wing-seeds better | right |
| 3 | The best neural variant held out is concat (FiLM has more ways to fit noise) | concat at every seed | right; FiLM vs none is unstable |
| 4 | Stopping leak: a few hundredths to ~0.3 nats | **−1.87 nats** (a lower bound) | **wrong by ~6×**: with three training wings, the scored wing's own curve and the validation cycle's disagree completely |

## What I would run next

1. **The same notebook with a learning-rate warm-up, or at 3 × 10⁻⁴.**
   - Prediction: budgets move out of the transient, the seed spread on 18N shrinks below ~3 nats, and the
     Waldmeier slope stabilizes.
2. **The `full` profile on a GPU (16 training wings, 19N inside the amplitude range).**
   - Prediction: concat lands within the seed spread of the champion, as the course's GPU run reports.
   - The timing slope stays negative.

## Files

- [05_neural_fields.ipynb](05_neural_fields.ipynb): the executed notebook. Task code sits in the cell under each
  spec, with each `raise` line left visible as a comment. The extension is clearly marked after Section 7.
- [metrics.json](metrics.json) and [collect_metrics.py](collect_metrics.py): every cached result and the printed
  outputs.
- [vocal_handoff.md](vocal_handoff.md): an honest record of the conversation. It is not a tutor HANDOFF.

Code and this report were prepared with AI assistance at the student's request. Research agents checked the
heliophysics and the ML methods. An independent review agent checked leakage, signs, numbers and comment clarity;
its findings changed the monitoring grid, the leak run's warm start, the ridge masking, the cache key and this
report's interpretation of the belt centre.
