# Next Steps

## Current position

The repository now has eight stable findings on the logistic map:

1. raw multi-base signatures track periodic regimes correctly
2. cross-base signatures amplify transition regions more strongly than simple scalar variance
3. step-to-step delta analysis shows stronger transition sensitivity than standard scalar summaries
4. there is initial evidence of pre-transition tension before visible regime jumps
5. a first synthetic score (`transition_score_v1`) behaves as a strong event detector
6. the score shows initial evidence of detecting ordered windows embedded inside chaos
7. a first separation between state-like order and event-like transition tension exists on the main transition region
8. the same order/event separation also remains meaningful inside the period-3 window around `r ~ 3.83`

---

## What is now known

### Confirmed

- periodic tracking works
- transition amplification works
- pre-transition sensitivity has initial evidence
- the synthetic mixed score is effective at highlighting regime breaks
- the score can collapse inside at least one ordered window within chaos
- `order_score_v1` and `event_score_v1` are not the same signal
- the coordinate pair remains usable both on the main bifurcation strip and inside an ordered island embedded in chaos

### Not yet confirmed

- whether the current weights are robust or ad hoc
- whether the internal event activity inside ordered windows is meaningful structure or weighting artifact
- whether the separation remains stable under noise
- whether the coordinate family generalizes beyond the logistic map

---

## Immediate next goal

The next correct step is not to move to a new dynamical system yet.

The next correct step is to stress-test the current coordinate family on the logistic map itself.

Why:

At this point the core question is no longer:

**"does Omniabase detect something?"**

That is already established.

The real question is now:

**"are these coordinates structurally robust, or are they fragile to weighting and clean conditions?"**

---

## Priority 1 - Noise robustness

The first real stress test should be:

**add controlled stochastic noise to the logistic map and see whether the coordinate family still distinguishes:**

- periodic state
- transition edge
- ordered island inside chaos
- chaotic regime

This matters because clean deterministic success is not enough.
If the coordinates collapse under mild noise, they are still too brittle.

### Goal

Check whether:

- `order_score_v1` stays relatively high in ordered zones under noise
- `event_score_v1` still peaks at edges under noise
- the pair degrades gradually rather than catastrophically

---

## Priority 2 - Weight sensitivity

The second test should be:

**perturb the score weights and see whether the qualitative geometry survives.**

This matters because a useful coordinate family should not depend entirely on one arbitrary weighting choice.

### Goal

Check whether the same broad structure survives under small changes to:

- order weights
- event weights

If the geometry remains similar, the coordinates are more likely to be structural rather than tuned.

---

## Priority 3 - Cleaner separation of state vs event

The current pair is already useful, but not yet fully clean.

The next refinement target is:

- make `order_score` flatter inside genuinely stable windows
- make `event_score` more concentrated at transition edges
- reduce mixed behavior in interior periodic zones

This is a refinement problem, not a restart problem.

---

## Recommended next experiment

The single best next experiment is:

`experiments/logistic_map_noise_robustness_v1.py`

This experiment should:

1. add small controlled noise to the logistic map trajectory
2. recompute the same multibase signatures
3. rebuild `order_score_v1` and `event_score_v1`
4. compare clean vs noisy behavior on:
   - periodic regime
   - bifurcation zone
   - period-3 window
   - chaotic zone

---

## Operational rule

Do not move to Hénon or Lorenz yet.

First verify that the current coordinate family survives:

- mild noise
- mild weighting perturbation

Only after that should a second dynamical system be introduced.

---

## Decision criterion

Move to a second system only if the logistic-map coordinate family shows:

- qualitative stability under noise
- qualitative stability under weight perturbation
- preserved distinction between order and event

If these conditions fail, refine the coordinate family before generalization.