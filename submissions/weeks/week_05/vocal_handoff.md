# Week 05 conversation handoff

No tutor session was held for Week 5, so this is **not** a `wrap up` HANDOFF block from the released
`vocal_prompt_week05.md`. It is a short record of what happened in the project conversation, so that next
week's session does not start cold. Replace it with a real HANDOFF if a tutor session is run later.

What the learner asked for: complete Homeworks 4 and 5. Use research agents (heliophysics, ML methods), a written
plan, clean commented code, small commits, and no push until told. Homework 4 was already complete and committed
(Tasks 32–43). This week covered Tasks 44–55.

Decisions taken in the conversation:

- **Profile:** `taste`, chosen automatically because there is no GPU. The `full` profile was measured at about
  0.8 s per epoch on this CPU, roughly 6 h for the notebook. Recommended next: run `full` on Colab.
- **Integrity:** upstream `*.solution.ipynb` files were not opened. The Week 5 template was taken from the course
  repository unchanged, and only the empty task cells were filled.
- **Extension:** clearly marked after Section 7. It covers seed robustness of the board, my own Week 4 model
  refitted on the same folds, and a warm-start-only control for Section 6's measurements.
- **Independent review:** a review agent's findings were applied: every-epoch monitoring, a fold-proper leak run,
  ridge masking and a configuration-hashed cache key. Its finding that the belt centre is inherited from the warm
  start changed the interpretation.

Results the learner should be able to explain (see REPORT.md):

- **Conditioning matters more than flexibility.** The unconditioned network loses in sample to the
  10-parameter Week 3 belt.
- **On this profile the parametric champion wins held out.** Concat is +12.7 nats behind at seed 42, and 0/6
  wing-seed pairs are better. Averaged over three seeds, the best network only ties the Week 3 belt.
- **Two mechanisms explain the loss:**
  - held-out 19N is a +3 sd amplitude extrapolation for a network trained on three weaker wings;
  - the honest budgets (4–12 epochs) sit inside Adam's start-up oscillation, so the network barely leaves its
    warm start.
- **Concat is the best neural variant at every seed;** FiLM vs none is not stable.
- **Stopping on the scored wing** would have reported 1.87 nats of free improvement, and that is a lower bound.
- **The network learned a Waldmeier-signed timing slope:** −0.98 yr per unit log A after 12 steps, against −0.08
  in the warm-start copy. The champion's is −1.71.
- **The network's belt centre at s = 0 (16.25°) was inherited from the warm start (16.5°),** so it is not
  evidence about the gauge question.

In the block below, the levels for the three existing domains are carried over unchanged from the Week 4
handoff. `machine learning` is new this week and was not assessed, so it is set to level 1, the prompt's
default starting point. Every Week 5 target is listed as introduced, none as deployed, because no probe was run.

Predictions: no student predictions were recorded. The four predictions in REPORT.md were written by the AI
before the runs, and they are labelled as such. Three were right; the size of the stopping leak was wrong by
about six times.

```text
HANDOFF
turns: n/a (no Week 5 tutor session)
domain: point processes | level: 2 | milestone: 2 reached provisionally | anchor: held-out log-likelihood
domain: statistical inference | level: 2 | milestone: 2 reached provisionally | anchor: leaderboard
domain: solar cycle physics | level: 1 | milestone: 2 not yet | anchor: belt width
domain: machine learning | level: 1 | milestone: 1 not yet | anchor: none
neural field | claim: no | prior: none | end: introduced | "no quote"
tensor | claim: no | prior: none | end: introduced | "no quote"
automatic differentiation | claim: no | prior: none | end: introduced | "no quote"
activation function | claim: no | prior: none | end: introduced | "no quote"
initialization | claim: no | prior: none | end: introduced | "no quote"
gradient descent | claim: no | prior: none | end: introduced | "no quote"
Adam optimizer | claim: no | prior: none | end: introduced | "no quote"
learning rate | claim: no | prior: none | end: introduced | "no quote"
epoch | claim: no | prior: none | end: introduced | "no quote"
validation set | claim: no | prior: none | end: introduced | "no quote"
conditioning | claim: no | prior: none | end: introduced | "no quote"
FiLM | claim: no | prior: none | end: introduced | "no quote"
Waldmeier effect | claim: no | prior: none | end: introduced | "no quote"
```
