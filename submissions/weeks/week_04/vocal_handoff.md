# Week 04 conversation handoff

No tutor session was held for Week 4, so this is **not** a `wrap up` HANDOFF block from the released
`vocal_prompt_week04.md`. It is a short record of the Week 4 decisions taken in the project conversation, so
that next week's session does not start cold. Replace it with a real HANDOFF if a tutor session is run later.

Decisions made by the learner:

- **Own knob (Task 36):** a heavy-tailed (Student-t) belt profile across latitude, chosen from three
  options. The question: are there more groups far from the belt centre than a Gaussian allows? This
  continues a question the learner raised earlier in Week 1: whether a "peak that is not high enough" is a
  width or a kurtosis effect.
- **Experiment menu:** "use different knobs as needed to see which one is best". So every one-knob ablation
  was run, followed by combinations.
- **Report name:** catou88. **Push:** commit only, no push.

Results the learner should be able to explain (see REPORT.md):

- The amplitude-dependent width is the largest single gain.
- Their own knob is the most consistent single gain (3.1 SE), and about ten times larger than predicted.
- The combination falls 0.15 short of the sum of its parts. A likely but untested reason: the width varies
  between wings, and that can mimic heavy tails.
- The threshold is a tie, and cannot be tested on this catalog.
- Cycle 19 shows the time profile and drift are not amplitude-dependent: that is the next knob.

Concepts discussed in this conversation before Week 4 (Week 1 material): the EMD versus NLL distinction
(distance versus surprise), why NLL punishes low density at real events, how EMD pairs up sorted samples,
variance versus kurtosis, the inter-arrival histograms, and the Fano factor with rate-matched nulls (they
reject independence only one way and cannot prove it). No vocabulary probes or prediction exercises from the
Week 4 tutor prompt were run.

```text
HANDOFF
turns: n/a (no Week 4 tutor session)
domain: point processes | level: 2 | milestone: 2 reached provisionally | anchor: Fano factor
domain: statistical inference | level: 2 | milestone: 2 reached provisionally | anchor: held-out log-likelihood
leaderboard | claim: no | prior: none | end: introduced | "use different knobs as needed to see which one is best"
ablation | claim: no | prior: none | end: introduced | "no quote"
model selection | claim: no | prior: none | end: introduced | "no quote"
metric gaming | claim: no | prior: none | end: introduced | "no quote"
domain: solar cycle physics | level: 1 | milestone: 2 not yet | anchor: belt width
belt width | claim: no | prior: none | end: introduced | "no quote"
hemispheric asymmetry | claim: no | prior: none | end: introduced | "no quote"
```
