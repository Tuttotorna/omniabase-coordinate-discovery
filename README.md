# Omniabase Coordinate Discovery

A minimal research prototype for using multi-base observation as a coordinate-discovery method in dynamical systems.

This repository does not start from language.  
It starts from dynamics.

Its core question is:

**Can a phenomenon reveal useful latent structure when the same trajectory is observed simultaneously through multiple numerical bases?**

The working hypothesis is simple:

A single representation may hide structure.  
A coordinated family of representations may expose it.

The goal is not only to measure stability.  
The goal is to discover signatures, transitions, and possible latent coordinates that are less obvious in standard human-default representations.

---

## Why this exists

Most systems are modeled through a small number of conventional representations:

- decimal values
- standard coordinates
- fixed feature sets
- human-intuitive summaries

These are useful.  
They are not guaranteed to be structurally optimal.

Omniabase Coordinate Discovery explores a different possibility:

**some regime changes, regularities, or latent signatures may become more visible when the same state sequence is observed across multiple bases at once.**

---

## Core idea

The repository treats Omniabase not as a truth gate, but as a multi-representation engine.

The primary task here is not:

**"is this output stable?"**

but:

**"what becomes visible when representation stops being singular?"**

This shifts Omniabase away from post-hoc judgment and toward coordinate discovery.

---

## Initial testbed

The first testbed is the logistic map:

\[
x_{n+1} = r x_n (1 - x_n)
\]

This system is simple enough to compute, but rich enough to exhibit:

- fixed points
- periodic behavior
- bifurcations
- chaotic regimes

That makes it a good first target for testing whether multi-base signatures reveal useful structure.

---

## Initial objective

The first prototype asks:

- do multi-base representations produce signatures that differ across regimes?
- do those signatures change before standard visible regime shifts?
- can we extract candidate coordinates or pre-features that help distinguish dynamical behavior?

---

## v0 setup

Initial experiment settings:

- system: logistic map
- r values: 3.50, 3.55, 3.60, 3.70, 3.80, 3.90, 4.00
- initial state: x0 = 0.123456
- total iterations: 300
- burn-in: 100
- bases: 2 to 16
- decimal precision per state: 12 digits

---

## First experiment

The first experiment will:

1. generate trajectories from the logistic map
2. convert each state into multiple bases
3. extract simple cross-base signatures
4. test whether those signatures separate dynamical regimes

This is a minimal starting point, not a final method.

---

## Expected output

The first output of the repository is not a grand theory.

It is a simple question:

**Do multi-base signatures contain usable signal about hidden regime structure?**

If yes, the next step is to refine the signatures.  
If no, the method must be changed early.

---

## Research direction

The intended trajectory is:

1. minimal proof on a simple dynamical system
2. improved multi-base signatures
3. regime-separation tests
4. early-shift detection tests
5. extension to more realistic signals

Possible later applications include:

- anomaly detection
- forecasting pre-features
- regime shift sensing
- system diagnostics
- representation discovery before modeling

---

## Status

Early prototype.

The current phase is focused on:

- defining the first experimental setup
- generating trajectories
- extracting minimal signatures
- checking whether anything nontrivial emerges

---

## Author

**Massimiliano Brighindi**
