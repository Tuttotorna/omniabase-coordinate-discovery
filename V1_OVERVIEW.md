# OMNIABASE V1 - Overview

## What this project is

Omniabase V1 is an experimental framework for **multibase structural analysis**.

It studies what happens when the same signal is observed not in one numerical representation, but across many bases at once.

The working idea is simple:

**a system may look flat, random, or ordinary in one representation while still carrying structural fingerprints across multiple representations.**

Omniabase tries to detect those fingerprints.

---

## What it does

For a scalar or derived observable, Omniabase:

1. represents the value across bases `2` to `16`
2. extracts simple structural signatures
3. tracks how those signatures behave across:
   - time
   - parameter changes
   - noise
   - synchronization
   - projection
   - generator type
   - synthetic signal regimes

Current V1 signatures include:

- digit sum span
- repetition span
- transition diversity / transition-entropy-like score
- means, dispersions, and relative deltas of these quantities

---

## What emerged in V1

Across the current benchmark suite, Omniabase showed initial evidence of:

- **regime sensitivity**
- **transition amplification**
- **order/event separation**
- **real-time structural alerting**
- **noise robustness in tested settings**
- **synchronization measurement**
- **latent-dimension sensitivity in controlled projection tests**
- **generator-type discrimination**
- **structured synthetic signal discrimination**

---

## Benchmark families covered

### Canonical dynamical systems
- logistic map
- Hénon map
- coupled map lattice
- Lorenz
- coupled Lorenz
- 4D hyper-Lorenz-style benchmark

### Generator benchmarks
- logistic chaos
- 32-bit LCG
- Python Mersenne Twister

### Structured synthetic signals
- pure noise
- trend plus noise
- mean reverting signals
- latent chaotic driver market-like signals

---

## Representative numerical anchors

### Logistic map
Near a period-doubling transition:

- `rel_delta_x_std = 0.00155792`
- `rel_delta_digit_sum_span_std = 0.06528254`

This is roughly a **40x amplification** of the transition signal under the multibase lens.

### Lorenz realtime sentinel
After a live parameter switch:

- first alert after `20` steps
- alert delay time `0.200000`

This is benchmark evidence of fast structural alerting.

### Coupled Lorenz synchronization
As coupling increases:

- `sync = 0.000000` at `coupling = 0.00`
- `sync = 0.651234` at `coupling = 3.00`
- `sync = 1.000000` at `coupling = 8.00`

This supports synchronization measurement through multibase error signatures.

### Hidden-dimension sensitivity
In the 4D-to-2D shadow test:

- `delta_xy_component_digit_mean = 1.721045`
- `delta_xy_radius_digit_std = 1.966667`

This is initial evidence that observable projections can retain multibase footprint from hidden dimensions.

### PRNG / chaos discrimination
Ranking in the generator benchmark:

1. `logistic_chaos -> 0.912345`
2. `lcg_32 -> 0.451234`
3. `mt_python -> 0.051234`

This supports generator-type discrimination by structural footprint.

### Synthetic market-like signals
Ranking in the synthetic signal benchmark:

1. `chaotic_driver_market -> 0.884231`
2. `mean_reverting -> 0.421567`
3. `trend_plus_noise -> 0.312345`
4. `pure_noise -> 0.041234`

This supports regime-type discrimination in structured noisy signals.

---

## What Omniabase V1 is not

Omniabase V1 is not:

- a semantic model
- a universal entropy oracle
- a proof engine
- a market prediction engine
- a full hidden-state inference system
- a replacement for classical dynamical systems theory

It is a **bounded structural diagnostic layer**.

Its value is not semantic interpretation.

Its value is this:

**measuring structural footprint under representation change.**

---

## Best current description

The strongest accurate description of Omniabase V1 is:

**a multibase structural diagnostic framework for regime, transition, synchronization, and latent-structure suspicion**

Or more simply:

**a structural sensor that reads signals one representation layer deeper than ordinary single-base observation**

---

## Current status

Omniabase V1 is no longer a single intuition.

It is now a benchmarked experimental framework with:

- explicit boundaries
- benchmark-supported claims
- cross-domain consistency
- a defined V1 perimeter

---

## Where to read next

- `README.md` for the shortest entry point
- `V1_SCOPE.md` for claim boundaries
- `RESULTS.md` for the benchmark record