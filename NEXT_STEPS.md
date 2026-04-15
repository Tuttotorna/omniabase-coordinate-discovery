# Next Steps

## Current position

The repository now has five stable findings on the logistic map:

1. raw multi-base signatures track periodic regimes correctly
2. cross-base signatures amplify transition regions more strongly than simple scalar variance
3. step-to-step delta analysis shows stronger transition sensitivity than standard scalar summaries
4. there is initial evidence of pre-transition tension before visible regime jumps
5. a first synthetic score (`transition_score_v1`) behaves as a strong event detector

---

## What is now known

### Confirmed

- periodic tracking works
- transition amplification works
- pre-transition sensitivity has initial evidence
- the synthetic score is effective at highlighting regime breaks

### Not yet confirmed

- whether the score is a good state estimator
- whether the score cleanly detects windows of order inside chaos
- whether the anticipation effect is robust across systems

---

## Immediate next experiment

The next correct test is a local scan around the periodic window near:

- `r ~ 3.83`

This test matters because it separates two possibilities.

### Possibility A

The current score is only reacting to violent transitions and local discontinuities.

### Possibility B

The current score is detecting deeper latent structure, and should therefore drop inside a stable periodic window embedded in chaos.

If possibility B holds, the method becomes significantly stronger.

---

## Hypothesis for the next test

Inside a known periodic window within the chaotic region:

- `transition_score_v1` should decrease
- the score should rise again near the window boundaries
- this drop should be sharper or more interpretable than what `x_std` alone provides

---

## Next file to build

`experiments/window_scan_383_v1.py`

---

## Operational rule

Do not change the dynamical system yet.

Do not add complexity yet.

First test whether the current coordinate family can detect:

- periodic regimes
- transitions
- ordered islands inside chaos

Only after that decide whether the signature family is robust enough to generalize.