---
name: kottos-smilansky-1997
description: Foundational paper introducing quantum chaos on graphs and establishing Wigner-Dyson spectral statistics on networks.
metadata:
  type: reference
---

# Kottos & Smilansky 1997 — Quantum Chaos on Graphs

**Reference**: Tsampikos Kottos and Uzy Smilansky, "Quantum Chaos on Graphs", *Physical Review Letters* **79**(24), 4794–4797 (1997). DOI: [10.1103/PhysRevLett.79.4794](https://doi.org/10.1103/PhysRevLett.79.4794).

*Comprehensive review*: S. Gnutzmann and U. Smilansky, "Quantum graphs: Applications to quantum chaos and universal spectral statistics", *Advances in Physics* **55**(5–6), 527–625 (2006). DOI: [10.1080/00018730600908042](https://doi.org/10.1080/00018730600908042).

## Core Thesis
Introduced **quantum graphs** (metric networks of 1D wires connected at vertices) as the ideal, analytically tractable paradigm for quantum chaos. Kottos and Smilansky proved that the Bohigas–Giannoni–Schmit (BGS) conjecture holds on graphs: when the classical motion on a graph is chaotic (mixing of paths across incommensurate bond lengths), the quantum energy spectrum exhibits universal Random Matrix Theory (RMT) level-spacing statistics (Gaussian Orthogonal or Unitary Ensembles).

## Key Mathematical Formalism
- **The Quantum Graph Model:** A network of $V$ vertices and $B$ bonds. On each bond $b = (i, j)$ of length $L_b$, the wave function satisfies the 1D Helmholtz equation:
  $$\left( -\frac{d^2}{dx^2} \right) \psi_b(x) = k^2 \psi_b(x), \quad E = k^2.$$
- **Vertex Boundary Conditions:** Wave functions are continuous at vertices, and current is conserved via Neumann/Kirchhoff boundary conditions:
  $$\sum_{b \in \mathcal{N}(v)} \frac{d\psi_b}{dx}\Bigg|_{v} = 0.$$
- **The Quantum Scattering Matrix $\Sigma(k)$:**
  Wave propagation is described by a $2B \times 2B$ unitary bond scattering matrix:
  $$U(k) = S \, e^{i k L},$$
  where $S$ encodes vertex scattering and $L = \operatorname{diag}(L_1, L_1, \dots, L_B, L_B)$ contains bond lengths.
  The quantum eigenvalues $k_n$ are the exact roots of the secular determinant:
  $$\det[\mathbb{I} - U(k_n)] = 0.$$
- **Exact Gutzwiller-like Trace Formula:**
  The oscillating density of states is given as an exact sum over all periodic orbits $p$ on the graph:
  $$d_{\text{osc}}(k) = \frac{1}{\pi} \operatorname{Im} \sum_p \sum_{r=1}^\infty L_p (\mathcal{A}_p)^r e^{i r k L_p}.$$
- **Emergence of Wigner–Dyson Statistics:** For incommensurate bond lengths, the level-spacing distribution $P(s)$ conforms precisely to the GOE Wigner surmise: $P(s) \approx \frac{\pi}{2} s e^{-\pi s^2 / 4}$.

## Relevance to `unitary-collapse`
In the `unitary-collapse` program, the spectral statistics of the detector Hamiltonian are diagnosed using the consecutive spacing ratio $\langle r \rangle$ (evaluated in `core/graph_spectral_sectors.py`). Kottos and Smilansky's work explains why random detector interaction graphs naturally produce Wigner–Dyson level repulsion: the multi-path connectivity of the graph acts as an internal chaotic quantum billiard.
