---
name: abou-chacra-thouless-anderson-1973
description: Exact analytical theory of Anderson localization on the Bethe lattice via self-consistent recursive equations.
metadata:
  type: reference
---

# Abou-Chacra, Thouless & Anderson 1973 — Localization on the Bethe Lattice

**Reference**: R. Abou-Chacra, D. J. Thouless, and P. W. Anderson, "A selfconsistent theory of localization", *Journal of Physics C: Solid State Physics* **6**(10), 1734–1752 (1973). DOI: [10.1088/0022-3719/6/10/009](https://doi.org/10.1088/0022-3719/6/10/009).

## Core Thesis
Formulated the first exact, non-perturbative analytical theory of Anderson localization on a tree-like network: the **Bethe lattice** (infinite regular Cayley tree with coordination number $Z = K + 1$). By exploiting the tree's loop-free geometry, the authors derived a self-consistent recursive distributional equation for the local self-energy, proving the existence of a sharp, well-defined mobility edge separating an extended metallic phase from an exponentially localized insulating phase.

## Key Mathematical Formalism
- **Tight-Binding Hamiltonian on the Bethe Lattice:**
  $$\hat{H} = \sum_{i} \epsilon_i |i\rangle\langle i| + V \sum_{\langle i, j \rangle} (|i\rangle\langle j| + |j\rangle\langle i|),$$
  where $\epsilon_i$ are independent random site energies uniformly distributed in $[-W/2, W/2]$.
- **Cavity Green's Function & Self-Energy:**
  Due to the absence of closed loops, removing node $i$ disconnects the $K$ branches descending from it. The diagonal Green's function element at node $i$ satisfies:
  $$G_{ii}(E) = \frac{1}{E - \epsilon_i - \Sigma_i(E)}, \quad \Sigma_i(E) = V^2 \sum_{j=1}^K G_{jj}^{(i)}(E),$$
  where $G_{jj}^{(i)}$ is the Green's function on the cavity tree where node $i$ is removed.
- **The Self-Consistent Distributional Equation:**
  Let $P(\operatorname{Im}\Sigma)$ be the probability distribution of the imaginary part $\Delta_i \equiv \operatorname{Im}\Sigma_i(E - i0^+)$. In the localized phase, $\Delta_i \to 0$ almost surely:
  $$\Delta_i = V^2 \sum_{j=1}^K \frac{\Delta_j}{(E - \epsilon_j - \operatorname{Re}\Sigma_j)^2 + \Delta_j^2} \xrightarrow{\text{localized}} \pi V^2 \sum_{j=1}^K \delta(E - \epsilon_j - \operatorname{Re}\Sigma_j).$$
  Linearizing the integral equation determines the critical disorder threshold $W_c$ for the mobility edge.

## Relevance to `unitary-collapse`
The Bethe lattice is the foundational theoretical model for high-dimensional and expander graphs. In `unitary-collapse`, the Altshuler–Basko–Aleiner mapping represents the detector's many-body Fock space as a Bethe-like tree. The Abou-Chacra–Thouless–Anderson criterion defines the exact boundary where disorder in detector on-site magnetic fields ($h_i^z$) or couplings ($J_{ij}$) freezes many-body quantum dynamics into an localized state, shutting down the detector's measurement function.
