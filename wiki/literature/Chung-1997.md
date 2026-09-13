---
name: chung-1997
description: Authoritative mathematical treatise on spectral graph theory, graph Laplacians, Cheeger inequalities, and expander graphs.
metadata:
  type: reference
---

# Chung 1997 — Spectral Graph Theory

**Reference**: Fan R. K. Chung, *Spectral Graph Theory*, CBMS Regional Conference Series in Mathematics, No. 92, American Mathematical Society, Providence, RI (1997). ISBN: 978-0-8218-0315-8. DOI: [10.1090/cbms/092](https://doi.org/10.1090/cbms/092).

## Core Thesis
The definitive mathematical monograph establishing the foundations of **spectral graph theory**. Fan Chung demonstrates that fundamental geometric, topological, and dynamical properties of a graph—including its expansion, diameter, mixing rate, bottleneck structure, and heat diffusion—are intimately governed by the eigenvalues and eigenvectors of its **normalized graph Laplacian** $\mathcal{L} = D^{-1/2} L D^{-1/2}$.

## Key Mathematical Formalism
- **The Normalized Laplacian $\mathcal{L}$:**
  $$\mathcal{L}(u, v) = \begin{cases} 1 & \text{if } u = v \text{ and } d_v \neq 0, \\ -\frac{1}{\sqrt{d_u d_v}} & \text{if } u \sim v, \\ 0 & \text{otherwise.} \end{cases}$$
  The spectrum satisfies $0 = \lambda_0 \le \lambda_1 \le \dots \le \lambda_{N-1} \le 2$.
- **Cheeger Inequality for Graphs:**
  Relates the spectral gap $\lambda_1$ to the isoperimetric / Cheeger constant $h_G$:
  $$2 h_G \ge \lambda_1 \ge \frac{h_G^2}{2}, \quad h_G \equiv \min_{S \subset V} \frac{|\partial S|}{\min(\operatorname{vol}(S), \operatorname{vol}(V \setminus S))}.$$
  A large spectral gap guarantees that the graph has no structural bottlenecks.
- **Expander Graphs & Mixing Lemma:**
  For any two subsets of vertices $S, T \subset V$, the number of edges between them satisfies the **Expander Mixing Lemma**:
  $$\left| e(S, T) - \frac{\operatorname{vol}(S) \operatorname{vol}(T)}{\operatorname{vol}(V)} \right| \le \lambda_{\max} \frac{\sqrt{\operatorname{vol}(S)\operatorname{vol}(T)\operatorname{vol}(V \setminus S)\operatorname{vol}(V \setminus T)}}{\operatorname{vol}(V)},$$
  where $\lambda_{\max} = \max(|\lambda_1 - 1|, |\lambda_{N-1} - 1|)$.
- **Diameter Bound:** $\operatorname{diam}(G) \le \left\lceil \frac{\ln(N - 1)}{\ln(1 + 2\lambda_1 / (2 - \lambda_1))} \right\rceil$.

## Relevance to `unitary-collapse`
In `core/detector_graphs.py`, the expander graph property (`kind="random_regular"` or `kind="expander"`) is explicitly verified by computing the Laplacian spectral gap $\lambda_2(L)$. Chung's spectral graph theory provides the analytical foundation for understanding why expander detectors rapidly scramble quantum information: a non-vanishing spectral gap enforces exponential spatial mixing, which drives the detector pencil toward Haar-like spectral isotropy and degrades the directional Born dipole.
