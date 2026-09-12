---
name: srednicki-1994
description: Definitive formulation of the Eigenstate Thermalization Hypothesis (ETH).
metadata:
  type: reference
---

# Srednicki 1994 — Chaos and Quantum Thermalization

**Reference**: M. Srednicki, *Phys. Rev. E* **50**, 888 (1994).

## Core Thesis
Thermalization in isolated quantum many-body systems is not a result of ergodicity (sampling phase space) but is an intrinsic property of individual energy eigenstates. In chaotic systems, any single energy eigenstate is "thermal," meaning its local observables are consistent with the microcanonical ensemble.

## Key Contributions
- **Eigenstate Thermalization Hypothesis (ETH)**: Postulated that for chaotic systems, the expectation values of local observables in an energy eigenstate $|\alpha\rangle$ equal the thermal average at that energy, with fluctuations that vanish in the thermodynamic limit.
- **Berry's Conjecture**: Used the idea that eigenfunctions of chaotic systems behave like Gaussian random variables to prove that the momentum distribution of a single particle in an eigenstate follows the Maxwell-Boltzmann distribution.
- **Dynamical Decoherence**: Explained the approach to equilibrium as the rapid decoherence of the relative phases between energy eigenstates in a superposition, causing non-thermal features to vanish over time.

## Relevance to `unitary-collapse`
The `unitary-collapse` project leverages the logic of ETH to frame the "measurement problem" as a dynamical process of state selection. 

ETH shows that "thermal" properties emerge from the statistical structure of eigenstates. The `unitary-collapse` program asks a parallel question: *Can "measurement" properties emerge from the statistical structure of the relative propagator's roots?*

If ETH tells us that most eigenstates of a chaotic system are thermal, the `unitary-collapse` program seeks to prove that most "special states" of a measurement-capable Hamiltonian are Born-like. Both programs replace an axiomatic "collapse" (of the wave function or of the thermal ensemble) with a structural property of the unitary operator's spectrum.
