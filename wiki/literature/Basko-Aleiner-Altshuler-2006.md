---
name: basko-aleiner-altshuler-2006
description: Landmark foundational paper establishing Many-Body Localization (MBL) as an Anderson localization transition in Fock space.
metadata:
  type: reference
---

# Basko, Aleiner & Altshuler 2006 — Many-Body Localization (BAA)

**Reference**: D. M. Basko, I. L. Aleiner, and B. L. Altshuler, "Metal-insulator transition in a weakly interacting many-electron system with localized single-particle states", *Annals of Physics* **321**(5), 1126–1205 (2006). DOI: [10.1016/j.aop.2005.11.014](https://doi.org/10.1016/j.aop.2005.11.014). arXiv: [cond-mat/0506617](https://arxiv.org/abs/cond-mat/0506617).

## Core Thesis
The foundational paper proving the existence of **Many-Body Localization (MBL)** at finite temperature and non-zero interaction strength in isolated quantum systems. Basko, Aleiner, and Altshuler (BAA) demonstrated that Anderson localization can survive electron-electron interactions, completely preventing an isolated many-body system from acting as its own heat bath. MBL systems fail to thermalize, violate the Eigenstate Thermalization Hypothesis (ETH), and maintain zero DC electrical and thermal conductivity.

## Key Mathematical Formalism
- **The Interacting Disordered Model:**
  $$H = \sum_\alpha \xi_\alpha c_\alpha^\dagger c_\alpha + \frac{1}{2} \sum_{\alpha\beta\gamma\delta} V_{\alpha\beta\gamma\delta} c_\alpha^\dagger c_\beta^\dagger c_\delta c_\gamma,$$
  where $\xi_\alpha$ are single-particle localized states with localization length $\xi$, and $V$ represents short-range interactions with typical matrix element $\lambda$.
- **Mapping to the Fock-Space Cayley Tree:**
  BAA mapped the many-body perturbation expansion onto a self-consistent localization problem on a high-dimensional Bethe-like graph. Each vertex represents a Slater determinant of occupied single-particle orbitals, and edges represent two-body scattering events.
- **The Self-Consistent Probability Distribution:**
  By analyzing the convergence of the locator expansion across all orders of perturbation theory:
  $$\Sigma_\alpha(E) = \sum_{\beta\gamma\delta} \frac{|V_{\alpha\beta\gamma\delta}|^2}{E + \xi_\beta - \xi_\gamma - \xi_\delta - \Sigma_{\beta\gamma\delta}(E)},$$
  BAA proved that below a critical temperature $T_c$:
  $$T_c \approx \frac{\delta_\xi}{\lambda \ln(1/\lambda)},$$
  where $\delta_\xi$ is the level spacing in the localization volume, the probability of finding an escape resonance vanishes. The imaginary part of the self-energy $\operatorname{Im}\Sigma$ is zero with probability 1, proving that the system remains an ideal quantum insulator.

## Relevance to `unitary-collapse`
BAA's Many-Body Localization proves that many-body quantum systems do not generically thermalize: interactions do not automatically destroy localization. In the `unitary-collapse` framework, this provides rigorous theoretical foundation for how a finite-dimensional detector can maintain non-thermal, structured pointer states without dissolving into an ergodic, maximally mixed thermal state.
