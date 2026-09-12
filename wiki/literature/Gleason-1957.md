---
name: gleason-1957
description: Mathematical proof that the Born rule is the only consistent probability measure for Hilbert spaces of dim >= 3.
metadata:
  type: reference
---

# Gleason 1957 — Measures of Projection Operators

**Reference**: A. M. Gleason, *J. Math. Phys.* **1**, 484 (1957).

## Core Thesis
For any Hilbert space with dimension $\ge 3$, any non-contextual probability measure assigned to projection operators must take the form of the Born rule: $p = \operatorname{Tr}(\rho P)$. This proves that the Born rule is the unique mathematically consistent way to assign probabilities to quantum measurements, provided the probabilities are independent of the measurement context.

## Key Contributions
- **Derivation of the Born Rule**: Transforms the Born rule from a postulate into a mathematical necessity of Hilbert space geometry.
- **Justification of the Density Matrix**: Proves that the set of all possible probability measures on $\mathcal{H}$ corresponds exactly to the set of positive-semidefinite operators with unit trace.
- **Constraint on Hidden Variables**: Established that non-contextual hidden variable theories are impossible in dimensions $\ge 3$.

## Relevance to `unitary-collapse`
Gleason's theorem is a **downstream constraint**. It tells us that if we want to assign a probability to a measurement outcome, the Born rule is the only consistent choice for the *entire* Hilbert space.

However, the `unitary-collapse` project focuses on a **restricted subset** of states (the collapsible states). This is a critical distinction:
1. **Gleason's Scope**: Applies to the *global* structure of the Hilbert space (all projections).
2. **`unitary-collapse` Scope**: Investigates the *local* structural properties of a specific unitary operator.

The project doesn't seek to replace Gleason's theorem, but rather to find the **dynamical mechanism** that implements the Born rule's predictions. By showing that the distribution of collapsible states follows $\cos^2(\theta/2)$, the project provides a physical, structural "reason" for why the Born rule emerges from the dynamics of a detector, rather than just accepting it as a geometric necessity of the state space.
