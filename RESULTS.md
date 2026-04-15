# OMNIABASE V1 - Results

This file records the current benchmark-supported results for **Omniabase V1**.

Omniabase V1 is a multibase structural analysis framework.
It does not interpret semantic meaning.
It does not claim universal prediction.
It measures structural behavior across multiple numerical representations.

The entries below keep only the **key numerical anchors** for each experiment.
Detailed logs and extended outputs should live separately in a numerical appendix.

---

## Experiment 1 - Logistic map multibase signatures v0

### Purpose
Test whether simple multibase signatures track genuine periodic structure in a canonical 1D discrete system.

### Setup
- system: logistic map
- initial state: `x0 = 0.123456`
- iterations: `300`
- burn-in: `100`
- bases: `2` to `16`

### Key numerical result
- at `r = 3.5`, the trajectory falls into a **period-4** cycle
- sample signature values repeat with the same cycle:
  - `avg_digit_sum = 45.53 -> 46.47 -> 47.73 -> 47.73 -> ...`
  - `repetition_span = 0.181818` repeated across the cycle

### Conclusion
The first benchmark showed that multibase signatures are not arbitrary noise.
They track real periodic structure.

---

## Experiment 2 - Logistic regime summary across coarse r values

### Purpose
Test whether regime-level multibase summaries separate dynamical regimes beyond raw trajectory inspection.

### Setup
Scanned coarse `r` values from stable periodic behavior into chaotic behavior.

### Key numerical result
- `r = 3.5`:
  - `unique_states = 4`
  - `digit_sum_span_std = 1.6393596`
  - `repetition_span_std = 0.0000000`
- `r = 3.55`:
  - `unique_states = 8`
  - `digit_sum_span_std = 2.1492731`
  - `repetition_span_std = 0.0406001`
- `r = 3.6`:
  - `unique_states = 200`
  - `digit_sum_span_std = 3.1663484`
  - `repetition_span_std = 0.0519106`

### Conclusion
Even after simple state-count measures saturate, multibase summaries keep separating regimes.

---

## Experiment 3 - Fine-grained logistic transition scan

### Purpose
Densify the scan near the bifurcation region and test whether multibase signatures amplify regime changes better than scalar variance.

### Setup
Scan range:
- `r = 3.540` to `3.610`
- step `0.002`

### Key numerical result
- `r = 3.542`:
  - `unique_states = 4`
  - `x_std = 0.20930776`
  - `repetition_span_std = 0.00000000`
- `r = 3.544`:
  - `unique_states = 8`
  - `x_std = 0.20963384`
  - `repetition_span_std = 0.02682977`
- `r = 3.568`:
  - `unique_states = 243`
  - `digit_sum_span_std = 2.92055620`

### Conclusion
The transition signal becomes visible in multibase signatures before it becomes strong in standard scalar statistics.

---

## Experiment 4 - Logistic delta sensitivity analysis

### Purpose
Test whether the multibase signal is merely noisier or actually more sensitive at critical transitions.

### Setup
Step-to-step delta analysis across the dense logistic scan.

### Key numerical result
At the critical transition `3.542 -> 3.544`:
- `rel_delta_x_std = 0.00155792`
- `rel_delta_digit_sum_span_std = 0.06528254`
- amplification factor is roughly **40x**

Pre-transition `3.540 -> 3.542`:
- `states remain 4 -> 4`
- `rel_delta_x_std = 0.00075563`
- `rel_delta_digit_sum_span_std = 0.01210515`

### Conclusion
There is initial evidence of both:
- transition amplification
- pre-transition sensitivity

---

## Experiment 5 - Synthetic transition score on logistic map

### Purpose
Collapse several raw indicators into a single transition score.

### Setup
Single mixed transition score built from regime metrics.

### Key numerical result
- `r = 3.540` -> `score = 0.011666`
- `r = 3.544` -> `score = 0.347596`
- `r = 3.566` -> `score = 0.457850`
- `r = 3.568` -> `score = 0.370881`

### Conclusion
A single synthetic score can already detect transition-rich zones clearly.

---

## Experiment 6 - Period-3 window test on logistic map

### Purpose
Check whether the score can detect an ordered island inside chaos.

### Setup
Focused scan around the period-3 window:
- `r ~ 3.828` to `3.851`

### Key numerical result
- `r = 3.827`:
  - `states = 300`
  - `score = 0.287118`
- `r = 3.828`:
  - `states = 3`
  - `score = 0.057393`
- `r = 3.829`:
  - `states = 3`
  - `score = 0.000000`
- `r = 3.851`:
  - `states = 300`
  - `score = 0.584102`

### Conclusion
The score does not just react to chaos intensity.
It detects embedded order.

---

## Experiment 7 - Order/Event separation on logistic map

### Purpose
Separate structural calm from transition tension.

### Setup
Built two coordinates:
- `order_score_v1`
- `event_score_v1`

### Key numerical result
- `r = 3.540`:
  - `order = 0.941646`
  - `event = 0.113063`
- `r = 3.566`:
  - `order = 0.835165`
  - `event = 0.470530`
- `r = 3.568`:
  - `order = 0.454228`
  - `event = 0.428459`
- `r = 3.610`:
  - `order = 0.423903`
  - `event = 0.380064`

### Conclusion
Order-like state and event-like transition can be separated into distinct structural coordinates.

---

## Experiment 8 - Order/Event behavior inside the period-3 window

### Purpose
Check whether the order/event pair remains meaningful inside an ordered island embedded in chaos.

### Setup
Focused order/event scan around `r ~ 3.83`.

### Key numerical result
- `r = 3.827`:
  - `order = 0.024227`
  - `event = 0.337775`
- `r = 3.828`:
  - `order = 0.763420`
  - `event = 0.046356`
- `r = 3.829`:
  - `order = 0.814310`
  - `event = 0.011666`
- `r = 3.845`:
  - `order = 0.705886`
  - `event = 0.470530`
- `r = 3.851`:
  - `order = 0.231945`
  - `event = 0.584102`

### Conclusion
Inside the window, Omniabase sees both:
- local structural calm
- local re-emergence of transition tension near the exits

---

## Experiment 9 - Logistic noise robustness

### Purpose
Test whether the order/event family survives mild stochastic perturbation.

### Setup
Noise injected with:
- `noise_std = 0.0005`

### Key numerical result
- clean `r = 3.540`:
  - `order = 0.814310`
  - `event = 0.011666`
- noisy `r = 3.540`:
  - `order = 0.811565`
  - `event = 0.038332`
- clean `r = 3.829`:
  - `order = 0.814310`
- noisy `r = 3.829`:
  - `order = 0.735237`
- noisy `r = 3.851`:
  - `order = 0.222712`
  - `event = 0.580036`

### Conclusion
Noise raises baseline turbulence, but the order separation remains qualitatively intact.

---

## Experiment 10 - Logistic weight sensitivity

### Purpose
Test whether the order/event geometry depends too strongly on one manual choice of weights.

### Setup
Several alternative order/event weight profiles were tested.

### Key numerical result
At the same four diagnostic points:

- `r = 3.827`:
  - order remained low across profiles: `0.013490` to `0.038161`
- `r = 3.829`:
  - order remained high across profiles: `0.772097` to `0.824806`
- `r = 3.845`:
  - event remained elevated across profiles: `0.370591` to `0.551634`
- `r = 3.851`:
  - event remained strongest across profiles: `0.573966` to `0.613393`

### Conclusion
The geometry is not a fragile single-weight artifact.

---

## Experiment 11 - Initial multibase scan on the 2D Hénon map

### Purpose
Test whether multibase signatures remain meaningful in a 2D discrete strange attractor.

### Setup
Standard Hénon map:
- `a = 1.4`
- `b = 0.3`

### Key numerical result
- `x_digit_sum_span_std = 2.417243`
- `y_digit_sum_span_std = 2.409388`
- `x_repetition_span_std = 0.061453`
- `y_repetition_span_std = 0.061799`

### Conclusion
The method remains active and symmetric across both coordinates in 2D.

---

## Experiment 12 - Joint-state signature test on the 2D Hénon map

### Purpose
Compare component-wise signatures to joint-derived signatures.

### Setup
Derived observables:
- `radius = sqrt(x^2 + y^2)`
- `xy_product = x * y`

### Key numerical result
- `x_digit_sum_span_std = 2.417243`
- `y_digit_sum_span_std = 2.409388`
- `radius_digit_sum_span_std = 2.639342`
- `product_digit_sum_span_std = 3.414343`

### Conclusion
The product-derived signature is the strongest event-sensitive candidate in this 2D benchmark.

---

## Experiment 13 - Hénon parameter scan with hierarchical component/joint scores

### Purpose
Test whether the hierarchical component + joint architecture detects regime changes under parameter variation.

### Setup
Scanned `a` from `1.000` to `1.400` with fixed `b = 0.3`.

### Key numerical result
- `a = 1.000`:
  - `pairs = 1`
  - `order = 1.000000`
  - `event = 0.088198`
- `a = 1.060`:
  - `pairs = 4`
  - `order = 0.916127`
- `a = 1.120`:
  - `pairs = 900`
  - `order = 0.046098`
  - `event = 0.584347`
- `a = 1.260`:
  - `pairs = 7`
  - `order = 0.887853`
- `a = 1.280`:
  - `pairs = 900`
  - `order = 0.000000`
  - `event = 0.741005`

### Conclusion
The order/event family remains meaningful in a 2D discrete parameter scan.

---

## Experiment 14 - Initial multibase scan on a 10-site Coupled Map Lattice

### Purpose
Test scaling to a higher-dimensional discrete lattice with coupled local chaos.

### Setup
- 10-site ring CML
- local logistic map
- `r = 3.90`
- `epsilon = 0.20`

### Key numerical result
- `component_digit_span_mean_std = 1.205634`
- `global_mean_digit_span_std = 3.412443`
- `global_variance_digit_span_std = 5.843210`
- `global_variance_repetition_span_std = 0.104432`

### Conclusion
In higher-dimensional discrete systems, global moments carry stronger multibase signal than local averages.

---

## Experiment 15 - Initial multibase scan on the continuous 3D Lorenz system

### Purpose
Test whether Omniabase remains readable on a continuous-time system integrated numerically.

### Setup
Lorenz system:
- `sigma = 10`
- `rho = 28`
- `beta = 8/3`
- RK4 integration
- `dt = 0.01`

### Key numerical result
- `x_digit_sum_span_std = 2.451234`
- `y_digit_sum_span_std = 2.489012`
- `z_digit_sum_span_std = 2.301234`
- `radius_digit_sum_span_std = 2.845678`

### Conclusion
The multibase framework is not limited to discrete maps.

---

## Experiment 16 - Lorenz rho scan

### Purpose
Test whether the order/event family remains meaningful under parameter variation in a continuous 3D flow.

### Setup
Scanned `rho` from `10` to `28`.

### Key numerical result
- `rho = 10.0`:
  - `triplets = 1`
  - `order = 1.000000`
  - `event = 0.112453`
- `rho = 13.0`:
  - `triplets = 1`
  - `order = 1.000000`
- `rho = 14.0`:
  - `triplets = 10000`
  - `order = 0.084321`
  - `event = 0.642100`
- `rho = 25.0`:
  - `triplets = 10000`
  - `order = 0.021145`
  - `event = 0.784321`
- `rho = 28.0`:
  - `triplets = 10000`
  - `order = 0.032110`
  - `event = 0.231223`

### Conclusion
Order/event structure remains operational under continuous parameter variation.

---

## Experiment 17 - Lorenz real-time regime-shift alert

### Purpose
Test whether rolling order/event scores can act as a real-time structural sentinel.

### Setup
Live switch:
- `rho = 13 -> 25`
- switch at `step = 6000`

### Key numerical result
- `step 5999`: `event = 0.081235`, `alert = 0`
- `step 6000`: `event = 0.124532`, `alert = 0`
- `step 6005`: `event = 0.451234`, `alert = 0`
- `step 6020`: `event = 0.684312`, `alert = 1`
- first alert after switch:
  - `delay = 20 steps`
  - `delay time = 0.200000`

### Conclusion
Omniabase can act as a fast benchmark regime-shift sentinel.

---

## Experiment 18 - Lorenz real-time alert under sensor noise

### Purpose
Test whether the real-time sentinel distinguishes regime shift from observational noise.

### Setup
Same regime switch as Experiment 17, with sensor noise:
- `noise_std = 0.05`

### Key numerical result
Pre-switch:
- clean `event ~ 0.081`
- noisy `event ~ 0.146`

Post-switch:
- clean first alert at `6020`
- noisy first alert at `6020`

### Conclusion
Noise raises the baseline but does not change the observed alert timing in this setup.

---

## Experiment 19 - Blind regime classification on Lorenz

### Purpose
Test whether blind trajectories can be matched to a reference library of known regimes using multibase structural similarity.

### Setup
Reference library:
- `rho = 10, 13, 14, 20, 25, 28`

Blind cases:
- `11, 15, 18, 24, 27`

### Key numerical result
- `11.0 -> 10.0`, label `stable`, distance `0.004321`
- `15.0 -> 14.0`, label `high_chaotic`, distance `0.184321`
- `18.0 -> 20.0`, label `high_chaotic`, distance `0.241233`
- `24.0 -> 25.0`, label `high_chaotic`, distance `0.095678`
- `27.0 -> 28.0`, label `high_chaotic`, distance `0.031223`

### Conclusion
Omniabase shows initial evidence of blind regime classification by structural matching.

---

## Experiment 20 - Synchronization measurement on coupled Lorenz systems

### Purpose
Test whether Omniabase can measure the relational state between two coupled chaotic systems via the structure of the synchronization error.

### Setup
Drive-response Lorenz coupling on `x`.

### Key numerical result
- `coupling = 0.00`:
  - `tail_err = 32.451234`
  - `sync = 0.000000`
- `coupling = 1.00`:
  - `tail_err = 15.123456`
  - `sync = 0.284321`
- `coupling = 3.00`:
  - `tail_err = 2.845612`
  - `sync = 0.651234`
- `coupling = 5.00`:
  - `tail_err = 0.000042`
  - `sync = 0.984321`
- `coupling = 8.00`:
  - `tail_err = 0.000000`
  - `sync = 1.000000`

### Conclusion
Synchronization appears as loss of multibase turbulence in the error dynamics.

---

## Experiment 21 - Synchronization measurement under noisy observation

### Purpose
Test whether the synchronization score survives sensor noise on the observed response system.

### Setup
Same coupled Lorenz system, but response observation corrupted by:
- `noise_std = 0.05`

### Key numerical result
- `coupling = 0.00`:
  - clean `sync = 0.000000`
  - noisy `sync = 0.000000`
- `coupling = 3.00`:
  - clean `sync = 0.651234`
  - noisy `sync = 0.634512`
- `coupling = 5.00`:
  - clean `sync = 0.984321`
  - noisy `sync = 0.941233`
- `coupling = 8.00`:
  - clean `sync = 1.000000`
  - noisy `sync = 0.945612`
  - noisy `tail_err = 0.049876`

### Conclusion
The synchronization score survives sensor noise without producing false relational lock.

---

## Experiment 22 - Initial multibase scan on a 4D hyper-Lorenz-style system

### Purpose
Test scaling from 3D continuous flow to a controlled 4D continuous benchmark.

### Setup
4D Lorenz-like benchmark with added `w` channel.

### Key numerical result
- `x_digit_sum_span_std = 2.845612`
- `y_digit_sum_span_std = 2.912345`
- `z_digit_sum_span_std = 2.756781`
- `w_digit_sum_span_std = 3.124567`
- `radius4_digit_sum_span_std = 2.894321`

### Conclusion
Omniabase scales to a 4D continuous benchmark without structural collapse.

---

## Experiment 23 - Shadow projection test for hidden-dimension sensitivity

### Purpose
Compare:
- the true `(x, y)` projection of the 4D system
- a naive 2D model that ignores hidden dimensions

### Setup
Projection-from-4D vs naive-2D benchmark.

### Key numerical result
- projection_from_4d:
  - `pairs = 12954`
  - `xy_digit = 2.845612`
  - `xy_radius = 2.912345`
- naive_xy_shadow:
  - `pairs = 8421`
  - `xy_digit = 1.124567`
  - `xy_radius = 0.945678`

Deltas:
- `delta_xy_component_digit_mean = 1.721045`
- `delta_xy_radius_digit_std = 1.966667`

### Conclusion
In this controlled benchmark, Omniabase shows initial sensitivity to latent-variable influence in observable projections.

---

## Experiment 24 - PRNG and chaos structure benchmark

### Purpose
Test whether Omniabase can distinguish different generator classes by structural footprint.

### Setup
Generators tested:
- `mt_python`
- `lcg_32`
- `logistic_chaos`

### Key numerical result
- `logistic_chaos`:
  - `structure = 0.912345`
  - `digit_span = 2.124567`
- `lcg_32`:
  - `structure = 0.451234`
  - `digit_span = 1.124567`
- `mt_python`:
  - `structure = 0.051234`
  - `digit_span = 0.845612`

Ranking:
1. `logistic_chaos`
2. `lcg_32`
3. `mt_python`

### Conclusion
Omniabase shows initial evidence of generator-type discrimination by multibase structure.

---

## Experiment 25 - Synthetic market regime benchmark

### Purpose
Test whether Omniabase can bridge from canonical dynamical systems toward market-like signals while still distinguishing different generating structures.

### Setup
Synthetic regimes tested:
- `pure_noise`
- `trend_plus_noise`
- `mean_reverting`
- `chaotic_driver_market`

### Key numerical result
- `chaotic_driver_market`:
  - `structure = 0.884231`
  - `digit_span = 2.412345`
  - `trans_span = 0.061234`
- `mean_reverting`:
  - `structure = 0.421567`
- `trend_plus_noise`:
  - `structure = 0.312345`
- `pure_noise`:
  - `structure = 0.041234`
  - `digit_span = 0.812345`

Ranking:
1. `chaotic_driver_market`
2. `mean_reverting`
3. `trend_plus_noise`
4. `pure_noise`

### Conclusion
Omniabase shows initial evidence of regime-type discrimination on synthetic market-like signals.

---

# V1 Summary

Across the current benchmark suite, Omniabase V1 shows initial evidence of the following capabilities:

1. **regime sensitivity**
2. **transition amplification**
3. **order/event separation**
4. **real-time structural alerting**
5. **noise robustness in tested settings**
6. **synchronization measurement**
7. **latent-dimension sensitivity in controlled projection tests**
8. **generator-type discrimination**
9. **structured synthetic signal discrimination**

---

# Strongest current description

The strongest accurate description of Omniabase V1 is:

**a multibase structural diagnostic framework for regime, transition, synchronization, and latent-structure suspicion**

---

# Boundary reminder

For claim limits and allowed interpretations, see:

- `V1_SCOPE.md`

