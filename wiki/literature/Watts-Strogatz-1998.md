---
name: watts-strogatz-1998
description: Landmark paper introducing the small-world network model interpolating between regular lattices and random graphs.
metadata:
  type: reference
---

# Watts & Strogatz 1998 — Collective Dynamics of 'Small-World' Networks

**Reference**: Duncan J. Watts and Steven H. Strogatz, "Collective dynamics of 'small-world' networks", *Nature* **393**(6684), 440–442 (1998). DOI: [10.1038/30918](https://doi.org/10.1038/30918).

## Core Thesis
Revealed that real-world complex networks (neural networks, power grids, collaboration graphs) are neither completely regular lattices nor completely random graphs, but lie in a distinct structural class: **small-world networks**. By introducing an edge-rewiring probability $p$, Watts and Strogatz demonstrated that adding a tiny fraction of random long-range shortcuts to a regular lattice drastically reduces average path length to logarithmic scaling while preserving high local clustering.

## Key Mathematical Formalism
- **The $WS(N, k, p)$ Construction:**
  Start with a 1D ring of $N$ vertices, each connected to $k$ nearest neighbors ($k$ even). With probability $p$, each edge $(i, j)$ is rewired to a randomly chosen vertex $k$, precluding self-loops and duplicate edges.
- **Two Structural Diagnostics:**
  1. **Characteristic Path Length $L(p)$:** The average shortest distance between all pairs of nodes:
     $$L(p) = \frac{1}{N(N-1)} \sum_{i \neq j} d(i, j).$$
  2. **Clustering Coefficient $C(p)$:** The fraction of a node's neighbors that are connected to each other:
     $$C_i = \frac{2 E_i}{k_i (k_i - 1)}, \quad C(p) = \frac{1}{N} \sum_{i=1}^N C_i.$$
- **The Small-World Regime ($0.001 < p < 0.1$):**
  - For $p = 0$: $L(0) \sim N / 2k$ (linear growth), $C(0) \approx \frac{3(k-2)}{4(k-1)} \approx \frac{3}{4}$.
  - As $p$ increases, $L(p)$ drops rapidly as $L(p) \sim \frac{\ln N}{k}$ due to shortcuts, while $C(p) \approx C(0)$ remains nearly constant.
  - A small-world network is formally defined by $L \sim \ln N$ and $C \gg C_{\text{random}} \sim k/N$.

## Relevance to `unitary-collapse`
In `core/detector_graphs.py`, the Watts–Strogatz topology is implemented as `kind="watts_strogatz"`. Watts–Strogatz networks provide an ideal control parameter ($p_{\text{rewire}}$) to test the stability of the Born dipole:
- At $p = 0$, the detector is a 1D ring, where audited calculations exhibit high Born scores ($S_{\text{born}} > 0.93$).
- Increasing $p_{\text{rewire}}$ introduces long-range shortcut couplings, transitioning the detector from local transport to rapid multi-spin scrambling. Measuring the Born score $S_{\text{born}}(p)$ as a function of $p$ locates the exact structural boundary where small-world shortcuts destroy the projective root balance condition.
