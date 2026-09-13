---
name: thooft-2016
description: Cellular Automaton Interpretation — quantum mechanics as emergent linear algebra for deterministic Planck-scale dynamics.
metadata:
  type: reference
---

# 't Hooft 2016 — The Cellular Automaton Interpretation of Quantum Mechanics

**Reference**: G. 't Hooft, *The Cellular Automaton Interpretation of Quantum Mechanics*, Fundamental Theories of Physics Vol. 185, Springer (2016). DOI: [10.1007/978-3-319-41285-6](https://doi.org/10.1007/978-3-319-41285-6). arXiv: [1405.1548](https://arxiv.org/abs/1405.1548).

## Core Thesis
The universe at the Planck scale is a **deterministic cellular automaton** with discrete ontological states $\{|e_i\rangle\}$ evolving by permutations $\hat{U}(\tau)|e_k\rangle = |e_{k+1 \bmod N}\rangle$. Quantum mechanics—complex amplitudes, Hilbert space, superposition, unitary operators—emerges as the natural linear-algebraic language for describing this discrete, deterministic dynamics.

## Key Concepts
- **Ontological basis:** The computational basis $\{|e_i\rangle\}$ represents physical reality. Superpositions $\sum c_i |e_i\rangle$ are statistical "templates" reflecting incomplete knowledge, not physical states.
- **Operator classification:**
  - *Beables:* Diagonal in the ontological basis — genuine physical facts.
  - *Changeables:* Map ontological states to ontological states.
  - *Superimposables:* Generic operators (e.g., $\sigma_x$ when the ontological basis is $\sigma_z$) — mathematical fictions.
- **Permutation → Hamiltonian:** Diagonalizing $\hat{U}(\tau)$ via DFT gives energy eigenstates with equally spaced spectrum $E_n = 2\pi n / (N\tau)$, formally identical to a truncated quantum harmonic oscillator.
- **Bell resolution:** Detector settings are beables; changing a setting means changing the entire automaton state. Counterfactual superpositions of settings do not exist ontologically, invalidating Bell's algebraic steps.

## Relevance to `unitary-collapse`
Both 't Hooft's CAI and `unitary-collapse` share the philosophical commitment that:
1. Definite outcomes are not produced by collapse but by deterministic evolution from constrained initial conditions.
2. Superposition of measurement outcomes is a mathematical artifact, not a physical reality.
3. Born's rule emerges from the structure of the underlying dynamics.

The key difference: CAI proposes a sub-Planckian deterministic ontology *beneath* quantum mechanics, while `unitary-collapse` works *within* standard QM, restricting initial states via the projective root variety.
