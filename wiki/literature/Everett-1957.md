---
name: everett-1957
description: Foundational Relative State Formulation of Quantum Mechanics establishing universal unitary dynamics and branching.
metadata:
  type: reference
---

# Everett 1957 — "Relative State" Formulation of Quantum Mechanics

**Reference**: Hugh Everett III, "'Relative State' Formulation of Quantum Mechanics", *Reviews of Modern Physics* **29**(3), 454–462 (1957). DOI: [10.1103/RevModPhys.29.454](https://doi.org/10.1103/RevModPhys.29.454).

*Unabridged dissertation*: H. Everett III, "The Theory of the Universal Wave Function", Ph.D. thesis, Princeton University (directed by John A. Wheeler, 1956). Published in DeWitt & Graham (1973), pp. 3–140.

## Core Thesis
Standard quantum mechanics contains an internal inconsistency between two contradictory dynamical laws: Process 1 (discontinuous, non-unitary wave-function collapse upon measurement) and Process 2 (continuous, deterministic unitary Schrödinger evolution). Everett resolves this by discarding Process 1 entirely. The universe is a closed quantum system governed solely by Process 2. Subsystems do not possess absolute states; a subsystem exists only in a **relative state** conditioned on a definite state of the rest of the universe.

## Key Mathematical Formalism
- **Universal State Vector:** The global state $|\Psi(t)\rangle$ satisfies $i\hbar \partial_t |\Psi\rangle = \hat{H}|\Psi\rangle$ universally.
- **Relative State Representation:** For composite state $|\Psi\rangle = \sum_{i,j} c_{ij} |s_i\rangle |a_j\rangle$, the relative state of subsystem $S$ given state $|\eta\rangle$ of $A$ is:
  $$|\psi_{\text{rel}}^S(\eta)\rangle = \mathcal{N} \sum_i \left( \sum_j c_{ij} \langle \eta | a_j \rangle \right) |s_i\rangle.$$
- **Memory Entanglement & Branching:** Apparatus memory registers accumulate correlated records:
  $$\left(\sum_i c_i |s_i\rangle\right) |a_0\rangle \xrightarrow{U} \sum_i c_i |s_i\rangle |a_i\rangle.$$
  Each branch $|a_i\rangle$ describes an internally coherent classical history for embedded observers.
- **Conserved Measure of Existence:** Everett proved that any positive measure $m(c_i)$ assigned to branches that is additive under sub-branching must take the Born form $m(c_i) = k |c_i|^2$.

## Relevance to `unitary-collapse`
Both Everett's formulation and `unitary-collapse` reject non-unitary collapse and take exact linear Schrödinger evolution as fundamental. However, their physical mechanisms for definiteness are diametrically opposed:
- **Everett:** All outcomes physically occur; the universe branches into an unobserved multiverse.
- **`unitary-collapse`:** A single outcome occurs; the physically realized microstates are restricted to projective roots of the detector matrix pencil $(A_N, C_N)$, providing a single-world unitary resolution.
