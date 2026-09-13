---
name: rovelli-1996
description: Foundational paper introducing Relational Quantum Mechanics (RQM).
metadata:
  type: reference
---

# Rovelli 1996 — Relational Quantum Mechanics

**Reference**: Carlo Rovelli, "Relational Quantum Mechanics", *International Journal of Theoretical Physics* **35**(8), 1637–1678 (1996). DOI: [10.1007/BF02302261](https://doi.org/10.1007/BF02302261). arXiv: [quant-ph/9609002](https://arxiv.org/abs/quant-ph/9609002).

## Core Thesis
Inspired by the relational foundations of Einstein's special relativity, Rovelli proposes that in quantum mechanics, physical variables do not have absolute, observer-independent values. A physical variable acquires a definite numerical value only **relative to another physical system** during an interaction. Any physical system can act as an observer. The quantum state $|\psi\rangle$ is not an ontic field, but a representation of the relational information one system possesses about another.

## Key Mathematical Formalism
- **Relational Description of Wigner's Friend:**
  - Relative to Friend $O$, an interaction with system $S$ realizes a relative fact: observable $A$ collapses to eigenvalue $a_1$ or $a_2$ with probabilities $|\alpha|^2$ and $|\beta|^2$.
  - Relative to Wigner $W$ outside, the joint system evolves strictly unitarily: $|\Psi_{SO}\rangle = \alpha |1\rangle|o_1\rangle + \beta |2\rangle|o_2\rangle$. No collapse has occurred.
- **Cross-Perspective Consistency:** If $W$ physically interacts with $O$ and $S$, quantum mechanics guarantees that $W$ will never detect an inconsistency between $O$'s record and $S$'s state:
  $$\langle \Psi_{SO} | \left( \hat{P}_{S, 1} \otimes \hat{P}_{O, 2} \right) | \Psi_{SO} \rangle = 0.$$
- **Informational Postulates:** RQM derives quantum mechanics from two informational axioms: (1) there is a maximum amount of relevant information that can be extracted from a finite system; (2) it is always possible to acquire new information about a system. This forces non-commuting observables and the Heisenberg uncertainty relation.

## Relevance to `unitary-collapse`
RQM resolves the measurement problem by relativizing reality to observers, preserving unitarity globally for non-interacting observers while allowing effective collapse relative to interacting observers. `unitary-collapse` preserves an absolute, single-world reality: collapse is an objective, autonomous physical mechanism executed by structured detector Hamiltonians acting on projective roots.
