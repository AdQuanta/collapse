---
name: pearle-1989-csl
description: Foundational paper introducing Continuous Spontaneous Localization (CSL) via stochastic non-linear dynamics.
metadata:
  type: reference
---

# Pearle 1989 — Continuous Spontaneous Localization (CSL)

**Reference**: Philip Pearle, "Combining stochastic dynamical state-vector reduction with spontaneous localization", *Physical Review A* **39**(5), 2277–2289 (1989). DOI: [10.1103/PhysRevA.39.2277](https://doi.org/10.1103/PhysRevA.39.2277).

*Companion formalization*: G. C. Ghirardi, P. Pearle, and A. Rimini, "Markov processes in Hilbert space and continuous spontaneous localization of systems of identical particles", *Physical Review A* **42**(1), 78–89 (1990). DOI: [10.1103/PhysRevA.42.78](https://doi.org/10.1103/PhysRevA.42.78).

## Core Thesis
Replaces the discrete Poissonian jump hits of the original GRW (1986) model with a continuous, stochastic diffusion process in Hilbert space. The wave function evolves under a non-linear, stochastic extension of the Schrödinger equation that continuously drives spatial superpositions toward localized pointer states, providing an objective, observer-free, and mathematically rigorous solution to the quantum measurement problem.

## Key Mathematical Formalism
- **Stochastic Schrödinger Equation (SSE):**
  $$d|\psi_t\rangle = \left[ -\frac{i}{\hbar}\hat{H} dt + \sqrt{\gamma} \int d^3x \left( \hat{M}(\mathbf{x}) - \langle \hat{M}(\mathbf{x}) \rangle_t \right) dW_t(\mathbf{x}) - \frac{\gamma}{2} \int d^3x \left( \hat{M}(\mathbf{x}) - \langle \hat{M}(\mathbf{x}) \rangle_t \right)^2 dt \right] |\psi_t\rangle,$$
  where $\hat{M}(\mathbf{x})$ is the smeared mass-density operator with localization length $r_C \approx 100\text{ nm}$, and $W_t(\mathbf{x})$ is a spatial white-noise Wiener field.
- **Amplification Mechanism:** For a macroscopic object of $N$ nucleons, the collapse rate scales coherently as $\Gamma_{\text{macro}} \propto N^2 \lambda$, suppressing macroscopic superpositions in $\tau_{\text{collapse}} \lesssim 100\text{ ns}$ while leaving single atoms unaffected ($\tau_{\text{micro}} \sim 10^8\text{ years}$).
- **Ensemble Lindblad Equation:** Averaging over the stochastic noise yields a completely positive, linear master equation that strictly forbids superluminal signaling.

## Experimental Signatures & Bounds
Because CSL modifies fundamental dynamics, it produces testable physical effects:
1. **Spontaneous Heating:** Momentum diffusion continuously transfers energy to particles: $\frac{d\langle E \rangle}{dt} = \frac{3}{4}\frac{\hbar^2 \lambda}{m_0 r_C^2} N$.
2. **Spontaneous Bremsstrahlung Radiation:** Continuous kicks to atomic electrons cause anomalous spontaneous X-ray emission. Underground searches (Majorana Demonstrator, VIP-2) have completely ruled out Adler's enhanced rate ($\lambda \sim 10^{-8}\text{ s}^{-1}$), placing upper bounds near $\lambda \lesssim 10^{-11}\text{ s}^{-1}$ at $r_C = 100\text{ nm}$.

## Relevance to `unitary-collapse`
CSL is the definitive benchmark for non-unitary collapse models. The `unitary-collapse` program seeks to reproduce the same physical outcome—definite macroscopic records—**without modifying the linear Schrödinger equation, without non-unitary stochastic noise, and without energy non-conservation**, deriving collapse solely from the algebraic geometry of projective roots in structured detector Hamiltonians.
