---
name: palmer-2026
description: Rational Quantum Mechanics (RaQM) - a discrete, rational restriction of Hilbert Space.
metadata:
  type: reference
---

# Palmer 2026 — Rational Quantum Mechanics (RaQM)

**Reference**: T. Palmer, "Rational quantum mechanics: a new theory of quantum physics" (University of Oxford / arXiv:2510.02877).

## Core Thesis
The continuous complex Hilbert space of standard Quantum Mechanics is an unphysical approximation. Nature is fundamentally discrete, and quantum states are only defined in bases where the squared amplitudes and phases are **rational numbers** ($\mathbb{Q}$). This discretization, potentially driven by gravity, resolves the paradoxes of QM (non-locality, etc.) by replacing them with a framework of "holism" and finite information capacity.

## Key Concepts
- **Finite Arithmetic State-Space Restriction**: A quantum state $|\psi\rangle$ is only defined if $\cos^2(\theta/2) \in \mathbb{Q}$ and $\phi/2\pi \in \mathbb{Q}$. 
- **Bit-String Representation**: States are represented as length-$L$ bit strings, where $L$ is a fundamental granularity constant.
- **The "Impossible Triangle"**: Uses Niven's Theorem to show that if two bases are rational, their linear combination is almost certainly irrational (and thus undefined), providing a geometric explanation for interference and the non-commutativity of observables.
- **Qubit Information Capacity (QIC)**: Predicts a fundamental limit ($N_{\text{max}}$) to quantum computing. Once $N > N_{\text{max}}$, the linear information growth of RaQM cannot support the exponential dimensions of standard Hilbert space, leading to the failure of algorithms like Shor's.

## Relevance to `unitary-collapse`
The `unitary-collapse` project deals with a **discrete set of "collapsible states"** on the Bloch sphere. 

Palmer's RaQM provides a radical theoretical justification for why such a discrete set should exist: **because the continuum itself is a mathematical fiction.**

While the `unitary-collapse` project identifies the collapsible states as the projective roots of a relative propagator (a dynamical origin), RaQM suggests that any "physical" state must be rational (an arithmetic origin). If the projective roots of the relative propagator for a physical Hamiltonian happen to coincide with (or be approximated by) the rational points of RaQM, it would provide a deep link between the *dynamics* of measurement and the *fundamental arithmetic* of the universe.
