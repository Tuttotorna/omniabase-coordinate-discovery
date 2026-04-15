Nome file

RESULTS.md

Contenuto completo

# OMNIABASE V1 - Results

This file records the current benchmark-supported results for **Omniabase V1**.

Omniabase V1 is a multibase structural analysis framework.

It does not interpret semantic meaning.
It does not claim universal prediction.
It measures structural behavior across multiple numerical representations.

The entries below record what has actually been tested.

---

## Experiment 1 - Logistic map multibase signatures v0

### Purpose

First proof of concept on a canonical 1D discrete dynamical system.

The goal was to test whether simple multibase signatures track periodic structure rather than producing arbitrary noise.

### System

Logistic map:

```text
x_(n+1) = r x_n (1 - x_n)

Initial settings

initial state: x0 = 0.123456

total iterations: 300

burn-in: 100

bases: 2 to 16

decimal precision: 12


Main result

At r = 3.5, the system falls into a clear period-4 cycle, and the extracted multibase signatures repeat with the same cycle.

Conclusion

Periodic structure is visible in the multibase signatures.


---

Experiment 2 - Logistic regime summary across coarse r values

Purpose

Test whether regime-level multibase summaries separate dynamical regimes beyond raw trajectory inspection.

Main result

From r = 3.6 onward, simple state counting saturates, but multibase summaries continue to move across chaotic regimes.

Conclusion

Omniabase does not only track obvious periodicity. It also distinguishes different already-chaotic regimes.


---

Experiment 3 - Fine-grained logistic transition scan

Purpose

Densify the scan around the bifurcation region to test whether multibase signatures amplify transition boundaries more clearly than simple scalar statistics.

Main result

Near the first period-doubling and later onset of strong complexity, multibase signatures change much more sharply than x_std.

Conclusion

Transition structure is amplified by the multibase lens.


---

Experiment 4 - Logistic delta sensitivity analysis

Purpose

Test whether the signal is merely noisier or whether it actually reacts earlier and more strongly near transitions.

Main result

Relative changes in multibase span metrics are much larger than relative changes in scalar variance near critical steps.

Conclusion

There is initial evidence of both:

transition amplification

pre-transition sensitivity



---

Experiment 5 - Synthetic transition score on logistic map

Purpose

Collapse several raw indicators into a single transition score.

Main result

The score peaks clearly around transition regions and falls in more stable zones.

Conclusion

A first practical transition detector exists.


---

Experiment 6 - Period-3 window test on logistic map

Purpose

Check whether the score can detect an ordered island embedded inside a chaotic region.

Main result

Inside the period-3 window around r ~ 3.83, the score collapses sharply relative to surrounding chaotic regions.

Conclusion

The score is not just reacting to noise. It is sensitive to embedded order.


---

Experiment 7 - Order/Event separation on logistic map

Purpose

Separate state-like order from event-like transition tension.

Main result

A first coordinate pair emerged:

order_score

event_score


order_score stays high in periodic regions and low in chaos. event_score peaks at regime breaks.

Conclusion

Order and transition can be represented as distinct structural coordinates.


---

Experiment 8 - Order/Event behavior inside the period-3 window

Purpose

Check whether the coordinate pair remains meaningful inside an ordered island embedded in chaos.

Main result

The ordered window shows high order and low event near its stable core, with event rising again near its exit.

Conclusion

The coordinate family remains usable inside local windows, not only at the global bifurcation strip.


---

Experiment 9 - Logistic noise robustness

Purpose

Test whether the order/event family survives mild stochastic perturbation.

Main result

Noise raises baseline turbulence but the qualitative order separation remains visible.

Conclusion

Initial qualitative noise robustness was observed on the logistic map.


---

Experiment 10 - Logistic weight sensitivity

Purpose

Test whether the order/event geometry depends critically on one manual weighting choice.

Main result

Reasonable perturbations of the weights preserve the same qualitative geometry:

ordered islands remain high-order

transition regions remain event-rich

chaotic regions remain low-order


Conclusion

The geometry is not a single-weight artifact.


---

Experiment 11 - Initial multibase scan on the 2D Hénon map

Purpose

Test whether multibase signatures remain meaningful when moving from 1D to a 2D discrete strange attractor.

Main result

Both coordinates produce active multibase signal. The method does not collapse in 2D.

Conclusion

Omniabase scales from 1D to 2D discrete systems.


---

Experiment 12 - Joint-state signature test on the 2D Hénon map

Purpose

Compare:

component-wise signatures

joint-derived signatures


using:

radius = sqrt(x^2 + y^2)

xy_product = x * y


Main result

The product-derived signature shows the strongest event-sensitive behavior. The radius behaves as a more stable global observable.

Conclusion

A hierarchical architecture is justified in 2D:

component layer

joint-derived layer



---

Experiment 13 - Hénon parameter scan with hierarchical component/joint scores

Purpose

Test whether the hierarchical architecture can detect:

fixed-point stability

low-period cycles

chaotic onset

periodic islands


under parameter variation.

Main result

The scan detects:

high order at fixed points

high order at periodic islands

strong event peaks near transition regions


Conclusion

The order/event family generalizes meaningfully to a 2D discrete parameter scan.


---

Experiment 14 - Initial multibase scan on a 10-site Coupled Map Lattice

Purpose

Test scaling from low-dimensional systems to a higher-dimensional discrete lattice with coupled local chaos.

Main result

Local component signatures remain relatively stable, but the strongest signal appears in multibase signatures of global moments, especially lattice variance.

Conclusion

In higher-dimensional discrete systems, global statistical moments can carry stronger multibase signal than local site averages.


---

Experiment 15 - Initial multibase scan on the continuous 3D Lorenz system

Purpose

Test whether Omniabase remains readable on a continuous-time system integrated numerically.

Main result

Multibase signatures remain active under RK4 integration. The radius remains the strongest global observable.

Conclusion

The multibase framework is not limited to discrete maps.


---

Experiment 16 - Lorenz rho scan

Purpose

Test whether the order/event family remains meaningful under parameter variation in a continuous 3D flow.

Main result

Low-rho stable regimes show maximal order. The first major loss of stability produces a strong event peak. Higher-rho complex regimes remain low-order.

Conclusion

Order/event structure remains operational in a continuous 3D parameter scan.


---

Experiment 17 - Lorenz real-time regime-shift alert

Purpose

Test whether rolling order/event scores can act as a real-time structural sentinel after a control-parameter switch.

Main result

A switch from rho = 13 to rho = 25 is detected with:

first alert after 20 steps

alert delay time 0.2


Conclusion

Omniabase can function as a fast benchmark regime-shift sentinel.


---

Experiment 18 - Lorenz real-time alert under sensor noise

Purpose

Test whether the real-time sentinel distinguishes regime shift from observational noise.

Main result

Noise raises the event baseline but does not produce false alerts, and the observed alert delay remains unchanged in the tested setup.

Conclusion

Initial noise robustness was observed for the real-time sentinel.


---

Experiment 19 - Blind regime classification on Lorenz

Purpose

Test whether a blind trajectory can be matched to a known reference library of regimes using multibase structural similarity.

Main result

Blind test cases are matched to nearby known regimes with distance acting as a confidence-like measure.

Conclusion

Omniabase shows initial evidence of blind regime classification by structural matching.


---

Experiment 20 - Synchronization measurement on coupled Lorenz systems

Purpose

Test whether Omniabase can measure the relational state between two coupled chaotic systems by analyzing the multibase structure of the synchronization error.

Main result

As coupling increases:

tail synchronization error decreases

synchronization score increases monotonically in the benchmark

divergence score decreases correspondingly


Conclusion

Synchronization appears as loss of multibase turbulence in the error dynamics.


---

Experiment 21 - Synchronization measurement under noisy observation

Purpose

Test whether the synchronization score survives sensor noise on the observed response system.

Main result

Noise prevents perfect saturation but does not generate false synchronization. Intermediate and strong synchronization remain clearly measurable.

Conclusion

Omniabase shows initial evidence of robust synchronization measurement under noisy observation.


---

Experiment 22 - Initial multibase scan on a 4D hyper-Lorenz-style system

Purpose

Test scaling from 3D continuous flow to a 4D continuous benchmark.

Main result

All four coordinates remain readable under the multibase lens. The added fourth dimension shows the strongest turbulence in this setup. The 4D radius remains a useful global observable.

Conclusion

Omniabase scales from 3D to a controlled 4D continuous benchmark without structural collapse.


---

Experiment 23 - Shadow projection test for hidden-dimension sensitivity

Purpose

Compare:

the true (x, y) projection of the 4D system

a naive 2D shadow model that ignores hidden dimensions


Main result

The projected 4D system shows much stronger visible-plane multibase turbulence than the naive 2D model.

Conclusion

In this controlled benchmark, Omniabase shows initial sensitivity to latent-variable influence in observable projections.


---

Experiment 24 - PRNG and chaos structure benchmark

Purpose

Test whether Omniabase can distinguish different generator classes by structural footprint.

Generators tested

Python Mersenne Twister

simple 32-bit LCG

logistic-map deterministic chaos


Main result

The benchmark yields a clear ranking:

deterministic chaos highest structure

simple LCG intermediate

Mersenne Twister flattest


Conclusion

Omniabase shows initial evidence of generator-type discrimination by multibase structure.


---

Experiment 25 - Synthetic market regime benchmark

Purpose

Test whether Omniabase can bridge from canonical dynamical systems toward market-like signals while still distinguishing different generating structures.

Synthetic regimes tested

pure noise

trend plus noise

mean reverting

latent chaotic driver


Main result

The benchmark yields a clear ranking:

latent chaotic driver highest structure

mean reversion intermediate

trend plus noise lower

pure noise flattest


Conclusion

Omniabase shows initial evidence of regime-type discrimination on synthetic market-like signals.


---

V1 Summary

Across the current benchmark suite, Omniabase V1 shows initial evidence of the following capabilities:

1. regime sensitivity


2. transition amplification


3. order/event separation


4. real-time structural alerting


5. noise robustness in tested settings


6. synchronization measurement


7. latent-dimension sensitivity in controlled projection tests


8. generator-type discrimination


9. structured synthetic signal discrimination




---

Strongest current description

The strongest accurate description of Omniabase V1 is:

a multibase structural diagnostic framework for regime, transition, synchronization, and latent-structure suspicion


---

Boundary reminder

For claim limits and allowed interpretations, see:

V1_SCOPE.md


