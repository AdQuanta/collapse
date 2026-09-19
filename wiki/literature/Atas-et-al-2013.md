---
name: atas-et-al-2013
description: Introduction of the level-spacing ratio as a tool for spectral analysis without unfolding.
metadata:
  type: reference
---

# Atas et al. 2013 — Distribution of the Ratio of Consecutive Level Spacings in Random Matrix Ensembles

**Reference**: Atas et al., *Phys. Rev. Lett.* **110**, 084101 (2013).

## Core Thesis
The ratio of consecutive level spacings $r_n = (e_{n+1} - e_n) / (e_n - e_{n-1})$ is a universal diagnostic of a quantum system's symmetry and chaoticity. Unlike the standard nearest-neighbor spacing distribution, the ratio is independent of the local density of states and therefore does not require the computationally expensive process of "unfolding."

## Key Contributions
- **Ratio Fingerprints**: Derived the probability distributions $P(r)$ for the three classical Gaussian ensembles (GOE, GUE, GSE) and the Poisson distribution.
- **Mean Ratio $\langle r \rangle$**: Established the mean ratio values as a "fingerprint" for symmetry classes:
    - **Poisson ($\sim 0.386$ for $\tilde{r}$)**: Indicates integrable/regular dynamics.
    - **GOE ($\sim 0.536$ for $\tilde{r}$)**: Indicates chaotic dynamics with time-reversal symmetry.
    - **GUE ($\sim 0.603$ for $\tilde{r}$)**: Indicates chaotic dynamics without time-reversal symmetry.
- **Universality**: Demonstrated that the ratio distribution accurately identifies the spectral properties of diverse systems, from quantum Ising chains to the zeros of the Riemann zeta function.

## Relevance to `unitary-collapse`
The `unitary-collapse` project uses level-spacing statistics as a diagnostic tool to classify the spectral properties of candidate detector Hamiltonians.

Specifically, the project:
1. **Uses the Ratio $\langle r \rangle$** within strictly separated symmetry sectors to determine if a candidate Hamiltonian is in the chaotic (GOE/GUE) or regular/integrable (Poisson) regime.
2. **Distinguishes Structure from Chaos**: Comparing the root geometry of Haar-random (isotropic) unitaries against candidate structured unitaries indicates that Born-like geometry is not a generic consequence of chaos alone.

Under SPEC v1.0, spectral statistics serve as diagnostics inside a derived physical mechanism chain rather than as a substitute for root, Born, control, and asymptotic gates; all paper-readiness gates remain `INCOMPLETE`.
