---
name: deutsch-1991
description: Foundational work on quantum statistical mechanics in closed systems; precursor to ETH.
metadata:
  type: reference
---

# Deutsch 1991 — Quantum statistical mechanics in a closed system

**Reference**: D. Deutsch, *Phys. Rev. A* **43**, 2046 (1991).

## Core Thesis
Isolated quantum many-body systems can be described by equilibrium statistical mechanics not because they "sample" Hilbert space, but because for chaotic systems, the individual energy eigenstates themselves are "thermal."

## Key Contributions
- **Justification of Statistical Mechanics**: Proved that in the limit of large degrees of freedom ($N \to \infty$), the expectation values of observables in the eigenstates of a chaotic Hamiltonian converge to the predictions of the microcanonical ensemble.
- **RMT Application**: Used Random Matrix Theory to show that a small, chaotic perturbation to an integrable system is sufficient to induce thermalization.
- **Foundation of ETH**: Established the central philosophy that thermalization is a property of the eigenstates themselves, rather than a property of the time-evolution of a state.

## Relevance to `unitary-collapse`
The `unitary-collapse` project uses ETH as a conceptual anchor for "unitary irreversibility." 

In the project's "Pitch," thermalization is cited as an example of a process that *looks* irreversible but is purely unitary. The `unitary-collapse` program seeks to find a similar "eigenstate-like" property for measurement: specifically, that "collapsible states" are the analogue of "thermal eigenstates" for the measurement process. 

While ETH describes the **averaging** of information across an ensemble, the `unitary-collapse` project identifies **precise points** (roots) that recover disentanglement. Both, however, represent the emergence of a stable, effectively classical property (thermal equilibrium / definite outcome) from a purely unitary, high-dimensional quantum evolution.
