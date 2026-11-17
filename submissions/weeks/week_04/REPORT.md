# Homework 4 — Scoreboard 1: which classical model predicts a cycle it has never seen?

Tasks 32–43 are implemented in [04_scoreboard1.ipynb](04_scoreboard1.ipynb). The notebook runs top to bottom
with **no errors and no `raise NotImplementedError` left** (63 code cells; about 60 s with the variant cache
warm). **20 variants** were fitted and scored by leave-one-cycle-out (LOCO) on the nine development cycles. All
of them share the protocol fingerprint **`5e55384fbc54`**: mesh 201 × 241, |lat| 0–60°, s −6 to +11 yr,
folds 12, 13, 14, 15, 17, 18, 19, 21, 23, and amplitude from the area record. Cycles **16, 20 and 22 were
never fitted or scored.** They are loaded with the catalog and filtered out before anything is fitted. One
indirect channel remains in the given code: the 365-day centred area smoothing can let a withheld cycle's
area enter a neighbouring development cycle's amplitude near the boundary. Every number below is in [metrics.json](metrics.json), which
[collect_metrics.py](collect_metrics.py) rebuilds from the cache and the executed notebook.

The submission is [scoreboard1_report_catou88.json](scoreboard1_report_catou88.json).

## The answer

**My model** is `profile-student_t__shape-two_sided__width-amplitude`, with 27 fitted parameters. It
combines:

- a belt width that grows with cycle amplitude,
- a time profile whose early side and late side can have different widths, and
- my own knob, a heavy-tailed (Student-t) belt across latitude.

The buoyancy threshold is kept.

| | held-out NLL (nats / hemicycle-year) | paired gain vs baseline | median gain | wings better | KS median (not rejected at 5%) |
|---|---|---|---|---|---|
| Week 3 baseline | −25.4193 | — | — | — | 0.0459 (8/18) |
| **my model** | **−26.3977** | **+0.978 ± 0.407** | +0.595 | **16/18** | **0.0416** (8/18) |

Lower NLL is better, and a positive "gain" means my model is better. The ± is the standard error of the
paired, wing-by-wing difference. The baseline reproduces Week 3: −26.5997 in sample (Week 3: −26.598) and
−25.4193 held out (Week 3: −25.422; the small difference is `a_ref`, now recomputed inside each fold).

## The one-knob leaderboard (ablations)

Each row changes exactly one knob from the Week 3 model, so the difference in score belongs to that knob.

| knob | paired vs baseline (neg = better) | SE | median | better | KS median | reading |
|---|---|---|---|---|---|---|
| width = amplitude | −0.688 | 0.293 | −0.286 | 15/18 | 0.0453 | win (2.3 SE) |
| width = combo | −0.650 | 0.290 | −0.256 | 14/18 | 0.0451 | win; its latitude slope fits to −0.007 |
| width = piecewise | −0.494 | 0.163 | −0.394 | 15/18 | 0.0471 | win (3.0 SE) |
| **profile = student_t (mine)** | **−0.256** | **0.082** | −0.156 | 15/18 | 0.0461 | **win (3.1 SE, the most consistent)** |
| shape = two_sided | −0.185 | 0.125 | −0.118 | 13/18 | **0.0423** | win (1.5 SE); best KS |
| width = latitude | −0.137 | 0.061 | −0.083 | 14/18 | 0.0452 | win (2.2 SE) |
| emission = direct | −0.003 | 0.013 | −0.001 | 10/18 | 0.0459 | **tie** |
| pooling = hemi | +0.299 | 0.276 | +0.002 | 9/18 | 0.0481 | worse on the mean (1.1 SE), a tie on the median |
| shape = weibull | +0.337 | 0.376 | +0.309 | 7/18 | 0.0565 | a tie by the SE rule (0.9 SE), worse on median and KS |
| shape = symmetric (control) | +0.766 | 0.340 | +0.554 | 5/18 | 0.0606 | loses, as a control should |
| shape = lognormal | +1.149 | 0.336 | +0.904 | 2/18 | 0.0498 | loses |
| *pooling = wing_rise* | *−3.054* | *1.108* | | *17/18* | *0.0410* | *bound: not ranked* |
| *pooling = wing_all* | *−3.685* | *1.170* | | *18/18* | *0.0346* | *bound: not ranked* |

Read the mean and the median together. The amplitude width has the largest mean gain, but its median is
only −0.29, so a few strong wings carry most of it. The piecewise width has a smaller mean but a better
median and half the SE.

## Combining the winners (Task 40)

The greedy rule adopts every stage whose best value won its ablation: two_sided, amplitude, student_t and
direct. The tie rule then reverts `direct` (gain 0.003 against an SE of 0.013). I tried four further
candidates and adopted one only if it beat the current model by more than the standard error of *their*
paired difference, or tied it with fewer parameters. None did:

| candidate vs my model | difference (pos = worse) | SE |
|---|---|---|
| drop two_sided (student_t + amplitude) | +0.188 | 0.125 |
| drop my knob (two_sided + amplitude) | +0.104 | 0.042 |
| piecewise width instead of amplitude | +0.178 | 0.244 |
| piecewise + student_t only | +0.333 | 0.317 |

**My knob is still worth 0.104 ± 0.042 inside the combined model (2.5 SE).** That is less than the 0.256 it
gains on its own.

**The combination is 0.150 short of the sum of its parts** (sum 1.128, together 0.978). A likely reason,
which I have not tested: alone, the Student-t belt fits ν = 12.3, but inside the combination it relaxes to
ν = 21, closer to Gaussian. A width that changes from wing to wing makes a pooled set of wings *look*
heavy-tailed. So some of the tail my knob fitted on its own may have been wings of different widths, which
would mean part of the two knobs' work overlaps. A test would be to compare the Student-t gain in narrow and
in wide wings.

## What the winning knobs say about the Sun

These are statements about the *emerging* band, inferred from where and when first observations land.
They are not measurements of a subsurface field.

- **The belt is wider in stronger cycles, roughly as the square root of the amplitude.** The fitted rule is
  w = 6.05° · (a/a_ref)^0.48. Week 3 found the same exponent (0.49), now confirmed as the largest single gain.
  Physically: a stronger cycle spreads its emergence over a broader band of latitudes at the same time, not
  only producing more groups at the same latitudes.
- **Latitude dependence of the width is mostly a stand-in for amplitude.** The latitude rule wins on its own,
  but when amplitude and latitude terms are fitted together (`combo`) the latitude slope goes to −0.007°/°. The
  piecewise rule finds a belt about 3° wide near 5° and about 7° wide at 15°. This is real structure, but it
  did not beat the amplitude rule in combination (+0.178 ± 0.244 worse, a tie).
- **More groups emerge far from the belt centre than a Gaussian allows** (my knob, 3.1 SE). The belt has
  heavy tails in latitude.
- **The time profile is lopsided.** In my model it peaks at s ≈ −0.87 yr, with a width of 1.45 yr on the
  early side and 2.89 yr on the late side: emergence falls off twice as slowly as it builds up. The
  symmetric control loses by 0.77, so the data clearly reject a mirror-image profile.
- **The hemispheres share a shape.** Separate north and south time profiles fit almost identical values (k
  7.80 vs 7.73), and held out they are worse on the mean (1.1 SE) and tied on the median. Within this model, hemispheric asymmetry lives in amplitude and timing (the
  clock), not in the shape of a wing.
- **The buoyancy threshold is untested, not rejected.** Fitted belt amplitudes are 1.5 × 10⁴ to 3.3 × 10⁴
  times critical, where softplus(B − 1) ≈ B. The two emissions only differ for a cycle near critical, and
  cycles 12–23 contain none.

### My knob: prediction against outcome

I wrote the prediction down in Task 36 before scoring. I predicted a small gain ("a few hundredths of a nat"),
no change in KS, and a width that shrinks as ν falls. The outcome:

- **The gain was 0.256 ± 0.082, about ten times what I predicted.** I underestimated how much of the
  likelihood sits in groups several degrees from the track.
- **KS was unchanged (0.0461 vs 0.0459), as predicted.** The knob only reshapes latitude, and KS sees only
  times.
- **The width parameter fell from 6.45° to 6.05°, but my prediction misread what that means.** For a
  Student-t, w is a scale, not a standard deviation. At ν = 12.3 the effective spread is
  6.05° × √(12.3/10.3) ≈ 6.6°, slightly *wider* than the Gaussian's 6.45°. The belt has a narrower core and
  heavier tails, not a narrower spread.

## Two metrics

The likelihood and KS disagree in a readable way. The knobs that act on latitude (width rules, my knob)
improve the NLL with little change in KS. The knob that acts on time (two_sided) gives the best KS of any
honest ablation (0.0423). Still, every honest model passes KS at 5% in only 7 to 9 of the 18 wings. The time profile is
the weak part, and the plausibility check below shows where.

## Protocol violations (Task 41)

Violations 1 and 2 were scored on the identical fitted baseline. Violation 3 is the separately fitted
`wing_rise` model, scored on its own fold parameters. Half a nat per fitted parameter over 17 years is 0.029
nats per hemicycle-year.

| violation | buys (nats / hemicycle-year) | SE | wings improved |
|---|---|---|---|
| 1 · amplitude fitted on the held-out events | 0.279 | 0.089 | 18/18 |
| 2 · clock from the all-data alignment | 0.040 | 0.038 | 9/18 |
| 3 · per-wing rise fitted on the scored wing (`wing_rise`) | 3.054 | 1.108 | 17/18 |

I wrote the order (3 ≫ 1 ≫ 2) before running these, but it was not a blind prediction: the notebook's own
text already quotes rough sizes for all three. Violation 3 buys **three times the best honest
model's gain** (0.978), and violation 1 buys ten times the half-nat rule. They are leaks, not optimism, which
is why bounds are reported unranked. Violation 2 buys about one SE: every wing's origin is already fitted
from its own events, so the all-data fit differs only in μ_b. *The notebook's text quotes 1.94 for violation
3, and I measured 3.05. I have not established why. One untested possibility is that my `wing_rise` frees
the gamma `k` (my choice of rise index). The conclusion, that this violation buys more than any honest
model, holds either way.*

## Physical plausibility (Task 42): held-out cycle 19

Cycle 19 is the strongest development cycle. The comparison uses the fold that never saw it.

| | count (pred / obs) | centroid (model / obs) | spread (model / obs) |
|---|---|---|---|
| my model, 19N | 1441 / 1590 | 15.2° / 17.2° | 7.7° / 8.5° |
| my model, 19S | 1253 / 1121 | 15.1° / 16.4° | 7.5° / 7.6° |
| baseline (both wings) | count error 10.6% | 14.8° / 16.8° | 7.0° / 8.1° |

- **My model fixes about half the spread error.** The baseline predicts the same 7.0° for every wing; my
  model predicts 7.6° for cycle 19.
- **It does not fix the centroid.** Cycle 19 emerges about 1.6° further from the equator than either model
  predicts.
- **Figure 9 shows the bigger failure.** The real cycle 19 has finished emerging by s ≈ +5.5 yr, but both
  synthetic cycles keep producing groups out to s ≈ +8–9 yr.
- **Both failures have a likely common cause.** The time profile and the drift track are the **same for
  every cycle strength**. Stronger cycles are known to start at higher latitude and evolve faster, and
  nothing in this model's knob catalog lets it say so.
- **That gives the next knob to try:** an amplitude-dependent time scale or drift track.
- **The count errors are −9% north and +12% south.** The area-record amplitude map is the obvious suspect,
  but I did not test it. The predicted count also depends on the shape integral and on w(a). Comparing
  against the own-events amplitude row would separate the two.

## Caveats

- **Model selection.** My model was chosen among 20 variants on the same nine folds that score it, so its
  margin is optimistic. Judged on their own paired differences, it beats the next candidates by 0.104 ±
  0.042 (2.5 SE) and 0.188 ± 0.125 (1.5 SE), and it ties the piecewise-width alternatives. Those are
  selection-inflated margins on nine cycles. Only the sealed cycles can test the ordering.
- **Conditional, not a forecast.** The held-out wing supplies two things to its own score: its own clock
  (time shift from its own events) and its own area-record amplitude. The area record is an independent
  observable, but it is built from the same groups' areas, and only the map's coefficients come from the
  training wings. The score says the model predicts a wing's *shape* on a standardized clock, given its
  area-record amplitude. It does not predict when a cycle happens or how big it will be.
- **Soft warm-start channel.** As the runner's reference workflow prescribes, every fold starts its
  optimizer from the in-sample fit over all 18 wings (including the held-out one) and runs 2 sweeps. No
  held-out parameter is fitted, but a fold that has not converged keeps some memory of that starting point.
  I did not measure how much.
- **Identifiability.**
  - ν and w trade off, as noted above.
  - With the `direct` emission, and effectively with the threshold at about 10⁴ × critical, c and the
    amplitudes are degenerate as a group: c·a is a flat direction. The closed-form c does not remove it; the
    alternating fit stays wherever the starting amplitudes put it. Only amplitude *ratios* between wings are
    identified, and those are all the amplitude map uses.
  - Amplitudes far above critical make the threshold unidentifiable on this catalog.
  - The clock is fitted first, from latitudes alone, and then frozen, so the time profile's peak position
    is measured relative to the 15° crossing, not fitted against it.
- **Data.**
  - Event times are first observations, not emergence; they lag by up to several days. This is irrelevant
    at the yearly scale of g(s), but it matters for any day-scale claim.
  - Exposure is treated as complete (about 99% coverage). Every rate is about 1% low, and this does not
    transfer to other catalogs.
  - Longitude is deferred.
- **Cost estimate.** In the executed notebook it predicts about 25–58 s per one-knob variant from a single
  timed sweep; the single-sweep timing varies from run to run. Actual runs took 44–438 s, mainly because I
  ran up to 13 variants at once on one machine. Figure 5 shows the gap.

## How this was produced

The implementation was written with an AI coding assistant (Claude Code) at my direction. I chose the knob
(heavy-tailed profile), asked for every knob to be tried, and set the report name. The variants were fitted
by parallel processes running the notebook's own code into the shared cache; the notebook then reads the
cache. The upstream `*.solution.ipynb` files were not opened.

The knob and its question are mine. The assistant drafted the written expectation in Task 36 from that
question, before the knob's variant was fitted. No tutor session was held for this week, so the Section 3
knob dialogue the week asks for did not take place; see [vocal_handoff.md](vocal_handoff.md).
