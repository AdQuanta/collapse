---
name: erdos-renyi-1959
description: Foundational paper introducing the theory of random graphs and the emergence of the giant connected component.
metadata:
  type: reference
---

# Erdős & Rényi 1959 — On Random Graphs

**Reference**: P. Erdős and A. Rényi, "On Random Graphs. I", *Publicationes Mathematicae Debrecen* **6**, 290–297 (1959).

*Companion*: P. Erdős and A. Rényi, "On the Evolution of Random Graphs", *Publications of the Mathematical Institute of the Hungarian Academy of Sciences* **5**, 17–61 (1960).

## Core Thesis
Founded the mathematical theory of random graphs. The authors introduced the $G(N, M)$ and $G(N, p)$ random graph ensembles and discovered that macroscopic structural properties of graphs do not emerge gradually, but undergo sharp, threshold-like **percolation phase transitions** as the edge density increases past critical values.

## Key Mathematical Formalism
- **The $G(N, p)$ Model:** A graph on $N$ labeled vertices where each of the $\binom{N}{2}$ potential edges is included independently with probability $p$.
- **The Giant Component Phase Transition:**
  Let $p = c / N$ (constant mean degree $\langle k \rangle = c$):
  - **Subcritical Regime ($c < 1$):** All connected components are small trees or unicyclic components of size $|C| = \mathcal{O}(\ln N)$.
  - **Critical Point ($c = 1$):** The largest component scales as $|C_{\max}| \sim N^{2/3}$.
  - **Supercritical Regime ($c > 1$):** A unique **giant component** of extensive size $|C_{\text{giant}}| = S(c) N$ emerges, where the fraction $S(c)$ satisfies the transcendental equation $S = 1 - e^{-c S}$. All other components remain microscopic ($\mathcal{O}(\ln N)$).
- **Connectivity Threshold:** The graph is completely connected (no isolated vertices) almost surely if and only if $p > \frac{\ln N + \omega(N)}{N}$ with $\omega(N) \to \infty$.

## Relevance to `unitary-collapse`
In `core/detector_graphs.py`, the Erdős–Rényi topology is implemented as `kind="erdos_renyi"`. The requirement `require_connected=True` ensures that detector spins form a single connected quantum network above the connectivity threshold. Erdős–Rényi graphs serve as the baseline for homogeneous, uncorrelated randomness without geometric spatial locality, allowing the project to test whether Born-rule statistics persist in the absence of spatial boundaries.
