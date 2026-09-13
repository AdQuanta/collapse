---
name: tikhonov-mirlin-2016
description: Detailed analysis of wave function multifractality and non-ergodic extended states on random regular graphs.
metadata:
  type: reference
---

# Tikhonov & Mirlin 2016 — Fractality of Wave Functions on Random Regular Graphs

**Reference**: K. S. Tikhonov, A. D. Mirlin, and M. A. Skvortsov, "Anderson localization on the Bethe lattice: Nonergodicity of extended states, correlations, and scaling", *Physical Review B* **94**(22), 224203 (2016). DOI: [10.1103/PhysRevB.94.224203](https://doi.org/10.1103/PhysRevB.94.224203). arXiv: [1604.05353](https://arxiv.org/abs/1604.05353).

*Companion*: K. S. Tikhonov and A. D. Mirlin, "Fractality of wave functions on a Cayley tree: Difference between tree and locally treelike graphs", *Physical Review B* **94**(18), 184203 (2016). DOI: [10.1103/PhysRevB.94.184203](https://doi.org/10.1103/PhysRevB.94.184203).

## Core Thesis
Demonstrated that quantum wave functions on **Random Regular Graphs (RRG)**—which possess finite volume, loop structure, and no boundary, unlike open Cayley trees—exhibit a distinct **non-ergodic extended (NEE)** regime with non-trivial **multifractality**. The authors resolved the long-standing debate on whether true MBL and Bethe-lattice localization transitions feature intermediate non-ergodic phases, proving that finite-size scaling on RRGs displays anomalous multifractal exponents $0 < D_q < 1$.

## Key Mathematical Formalism
- **The RRG Tight-Binding Model:**
  $$H = \sum_{i=1}^N \epsilon_i |i\rangle\langle i| + \sum_{\langle i, j \rangle} (|i\rangle\langle j| + |j\rangle\langle i|),$$
  where each node has fixed degree $d = m + 1$, and on-site energies $\epsilon_i$ are independent random variables uniformly distributed in $[-W/2, W/2]$.
- **Inverse Participation Ratios (IPR) & Multifractality:**
  The spatial distribution of eigenstate $|\psi\rangle$ is quantified by the generalized moments:
  $$P_q = \sum_{i=1}^N |\psi_i|^{2q} \sim N^{-\tau(q)}, \quad \tau(q) \equiv D_q(q - 1),$$
  where $D_q$ is the fractal dimension.
  - *Ergodic Phase:* $D_q = 1$ for all $q$ (uniform spreading over the entire volume $N$).
  - *Localized Phase:* $D_q = 0$ for $q > 0$ (confinement to $\mathcal{O}(1)$ sites).
  - *Multifractal / Non-Ergodic Phase:* $0 < D_q < 1$ continuously varies with $q$, indicating that the wave function occupies an extensive but sparse, self-similar fractal subset of vertices.
- **Population Dynamics & Finite-Size Scaling:**
  Using population dynamics simulations on graphs of up to $N \sim 10^7$ nodes, Tikhonov and Mirlin showed that the apparent non-ergodic phase on RRGs undergoes very slow logarithmic scaling, establishing the benchmark for numerical scaling studies of MBL.

## Relevance to `unitary-collapse`
In `core/detector_graphs.py`, `random_regular` expanders represent the highest algebraic connectivity available for a fixed degree. Tikhonov and Mirlin's work provides the mathematical foundation for analyzing how the eigenstates of the detector Hamiltonian distribute across the graph nodes: if the detector exhibits multifractal or non-ergodic eigenstate structure, it can resist complete thermalization and sustain the coherent phase relationships necessary for the projective-root Born balance condition $C_B$.
