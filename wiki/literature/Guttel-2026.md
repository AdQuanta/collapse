---
name: guttel-2026
description: Experimental study of sharp dynamical transitions in continuously measured superconducting qubits.
metadata:
  type: reference
---

# Guttel 2026 — Gradually opening Schrödinger’s box reveals a cascade of sharp dynamical transitions

**Reference**: Guttel et al., *arXiv:2602.02672*.

## Core Thesis
The transition from coherent quantum evolution to classical-like measurement outcomes is not a smooth crossover but a **cascade of three sharp dynamical transitions** occurring at critical measurement strengths $\lambda$. These transitions mark the emergence of quantum jumps, state-freezing, and the Quantum Zeno effect.

## Key Dynamical Transitions
1. **Quantum-Jump Transition ($\lambda \approx 1$):** Coherent Rabi oscillations cease; the system evolves toward stable fixed points of a non-Hermitian Hamiltonian, punctuated by detector-click resets.
2. **State-Freezing Transition ($\lambda \approx 1.15$):** The "dwell time" in the vicinity of the stable fixed point diverges, effectively trapping the qubit state.
3. **Quantum Zeno Transition ($\lambda \approx 2$):** Dynamics shift to overdamped decay, where increased measurement strength paradoxesly slows down the relaxation toward the steady state.

## Key Finding: The Role of Decoherence
The study reveals that **decoherence fundamentally reorganizes the phase diagram**. In real superconducting qubits, decoherence inverts the order of the transitions (e.g., state-freezing occurs before the cessation of oscillations), decoupling signatures that appear simultaneous in idealized models.

## Relevance to `unitary-collapse`
The `unitary-collapse` project investigates the **static root geometry** of the relative propagator. Guttel et al. investigate the **dynamic trajectory** of a qubit under continuous monitoring.

The link is found in the **non-Hermitian evolution**:
1. Guttel's "quantum jumps" are driven by the eigenvalues of a non-Hermitian Hamiltonian.
2. The `unitary-collapse` projective roots are the "zero-energy" solutions of a non-Hermitian operator pencil.

Both works highlight that the "classical" limit (jumps, freezing, definite outcomes) is not a gradual limit of $N \to \infty$, but can be reached via **sharp transitions** driven by the competition between coherent drive ($\Omega_S$) and measurement rate ($\alpha$). This suggests that the "Born-like" profile found in the `unitary-collapse` project might itself be associated with a dynamical transition in the detector's parameter space.
