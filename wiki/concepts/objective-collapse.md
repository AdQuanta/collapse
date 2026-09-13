# Objective Collapse Theories (Spontaneous Localization Models)

## Overview

Objective collapse models (or spontaneous wave-function reduction theories) modify the linear Schrödinger equation by introducing non-linear and stochastic terms that describe spontaneous, physical localization of quantum states in space. Unlike standard Copenhagen quantum mechanics, objective collapse theories eliminate the observer, measurement apparatus, and arbitrary "classical/quantum cuts." Unlike Many-Worlds or Bohmian mechanics, they are **empirically distinct from standard quantum mechanics**, making distinct, experimentally testable predictions.

The major objective collapse paradigms include:
1. **GRW Model (Ghirardi, Rimini & Weber 1986):** Discrete spontaneous Poissonian hits.
2. **CSL Model (Continuous Spontaneous Localization - Pearle 1989, Ghirardi et al. 1990):** Continuous stochastic diffusion in Hilbert space.
3. **Diósi–Penrose Model (Diósi 1987, Penrose 1996):** Gravitationally induced collapse driven by gravitational self-energy differences.
4. **Relativistic Flash Models (Tumulka 2006):** Lorentz-invariant collapse with flash ontology in spacetime.

---

## 1. The GRW Model (Discrete Hits)

In the Ghirardi–Rimini–Weber (GRW) model (1986), each particle in an $N$-particle system evolves unitarily according to the Schrödinger equation, but is subject to spontaneous, Poissonian "localization hits" at a constant mean rate $\lambda_{\text{GRW}} \approx 10^{-16}\text{ s}^{-1}$ (one hit every $\sim 10^8$ years for a single nucleon).

When a hit occurs on particle $i$ at position $\mathbf{x}$, the global wave function undergoes an instantaneous jump:
$$|\psi\rangle \longrightarrow \frac{\hat{L}_i(\mathbf{x}) |\psi\rangle}{\| \hat{L}_i(\mathbf{x}) |\psi\rangle \|},$$
where $\hat{L}_i(\mathbf{x})$ is a Gaussian localization operator:
$$\hat{L}_i(\mathbf{x}) = \left( \frac{1}{\pi r_C^2} \right)^{3/4} \exp\left( -\frac{(\hat{\mathbf{r}}_i - \mathbf{x})^2}{2 r_C^2} \right),$$
with localization length $r_C \approx 10^{-7}\text{ m} = 100\text{ nm}$. The probability density for the hit to occur at position $\mathbf{x}$ is governed by the Born-like measure:
$$P(\mathbf{x}) = \| \hat{L}_i(\mathbf{x}) |\psi\rangle \|^2.$$

---

## 2. Continuous Spontaneous Localization (CSL)

The CSL model (Pearle 1989; Ghirardi, Pearle & Rimini 1990) replaces discontinuous jumps with continuous stochastic diffusion governed by a non-linear **Stochastic Schrödinger Equation (SSE)**:

$$d|\psi_t\rangle = \left[ -\frac{i}{\hbar}\hat{H} dt + \sqrt{\gamma} \int d^3x \left( \hat{M}(\mathbf{x}) - \langle \hat{M}(\mathbf{x}) \rangle_t \right) dW_t(\mathbf{x}) - \frac{\gamma}{2} \int d^3x \left( \hat{M}(\mathbf{x}) - \langle \hat{M}(\mathbf{x}) \rangle_t \right)^2 dt \right] |\psi_t\rangle,$$

where:
- **Smeared Mass-Density Operator $\hat{M}(\mathbf{x})$:**
  $$\hat{M}(\mathbf{x}) = \frac{1}{m_0} \int d^3y \, g(\mathbf{y} - \mathbf{x}) \sum_j m_j \hat{a}_j^\dagger(\mathbf{y}) \hat{a}_j(\mathbf{y}),$$
  with $m_0$ the nucleon mass and Gaussian kernel $g(\mathbf{x}) = (2\pi r_C^2)^{-3/2} e^{-|\mathbf{x}|^2 / 2r_C^2}$.
- **Wiener Noise Field $W_t(\mathbf{x})$:** Continuous white noise with $\mathbb{E}[dW_t(\mathbf{x}) dW_t(\mathbf{y})] = \delta(\mathbf{x} - \mathbf{y}) dt$.
- **Non-Linear Drift:** $\langle \hat{M}(\mathbf{x}) \rangle_t = \langle \psi_t | \hat{M}(\mathbf{x}) | \psi_t \rangle$ preserves state normalization and derives Born probabilities as a martingale property.

### Master Equation for the Ensemble
Averaging over the noise field $\rho_t = \mathbb{E}[|\psi_t\rangle\langle\psi_t|]$, the non-linear terms cancel, yielding a linear Lindblad master equation:
$$\frac{d\rho_t}{dt} = -\frac{i}{\hbar}[\hat{H}, \rho_t] - \frac{\gamma}{2} \int d^3x \left[ \hat{M}(\mathbf{x}), \left[ \hat{M}(\mathbf{x}), \rho_t \right] \right].$$
Because this master equation is linear and completely positive, **faster-than-light signaling is strictly prohibited**.

---

## 3. The Amplification Mechanism

The decisive feature of objective collapse models is the **macro-amplification mechanism**, which explains why microscopic systems remain quantum while macroscopic systems are classical:

For an object of $N$ nucleons separated by distance $\Delta x$:
1. **Microscopic System ($N = 1$):**
   $$\Gamma_{\text{collapse}} \approx \lambda \approx 10^{-16}\text{ s}^{-1} \implies \tau \approx 10^8\text{ years}.$$
   The particle evolves unitarily and displays pristine quantum interference.
2. **Macroscopic Object ($N \sim 10^{23}$):**
   - For small spatial superpositions ($\Delta x \ll r_C$):
     $$\Gamma_{\text{collapse}} \propto N^2 \lambda \quad (\text{coherent scaling}).$$
   - For large spatial superpositions ($\Delta x \gg r_C$):
     $$\Gamma_{\text{collapse}} \approx N \lambda \approx 10^{23} \times 10^{-16}\text{ s}^{-1} = 10^7\text{ s}^{-1} \implies \tau_{\text{collapse}} \approx 100\text{ ns}!$$

A macroscopic pointer or cat superposition is destroyed in a fraction of a microsecond.

---

## 4. Diósi–Penrose Gravitational Collapse

Lajos Diósi (1987) and Roger Penrose (1996) proposed that collapse is not caused by ad-hoc noise, but by a fundamental conflict between general relativity and quantum superposition. 

In general relativity, a mass distribution determines the spacetime metric $g_{\mu\nu}$. A spatial superposition of two mass distributions $|\psi\rangle = \frac{1}{\sqrt{2}}(|M_1\rangle + |M_2\rangle)$ corresponds to a superposition of two distinct spacetime geometries, leading to an ill-defined time-translation generator $\partial/\partial t$.

Penrose quantified the ill-definedness as the **gravitational self-energy difference** $\Delta E_G$:
$$\Delta E_G = -G \iint d^3x \, d^3y \frac{[\rho_1(\mathbf{x}) - \rho_2(\mathbf{x})][\rho_1(\mathbf{y}) - \rho_2(\mathbf{y})]}{|\mathbf{x} - \mathbf{y}|}.$$
The superposition spontaneously reduces on the characteristic gravitational decoherence timescale:
$$\tau_{\text{DP}} \approx \frac{\hbar}{\Delta E_G}.$$
For a nucleon ($\Delta E_G \sim 10^{-35}\text{ J}$), $\tau_{\text{DP}} \sim 10^6\text{ years}$. For a $1\,\mu\text{m}$ dust speck ($\Delta E_G \sim 10^{-18}\text{ J}$), $\tau_{\text{DP}} \sim 1\text{ ms}$.

---

## 5. Experimental Status and Parameter Exclusion (Carlesso et al. 2022)

Unlike philosophical interpretations, objective collapse models are **falsifiable**:

### Signatures of Collapse Models
1. **Loss of Matter-Wave Interference:** Spatial coherences are damped exponentially with mass $M$ and separation $\Delta x$.
2. **Spontaneous Kinetic Heating:** Localization kicks momentum randomly by $\Delta p \sim \hbar/r_C$, causing a steady energy drift:
   $$\frac{d\langle E \rangle}{dt} = \frac{3}{4} \frac{\hbar^2 \lambda}{m_0 r_C^2} N.$$
3. **Spontaneous Bremsstrahlung Radiation:** Charged particles (electrons, protons) jiggled by the stochastic field spontaneously emit unprompted X-rays and $\gamma$-rays.

```
Parameter Space (lambda vs. r_C at r_C = 10^-7 m):
  10^-8  s^-1  [Adler Enhanced Rate]  <-- FALSIFIED by Germanium X-ray searches
  10^-11 s^-1  [Majorana / VIP-2]     <-- CURRENT EXPERIMENTAL CEILING
  10^-13 s^-1  [LISA Pathfinder]     <-- Strict mechanical bounds
  10^-16 s^-1  [Original GRW Rate]   <-- Still experimentally open!
```

- **Adler's Enhanced Rate ($\lambda \sim 10^{-8}\text{ s}^{-1}$):** Definitively **FALSIFIED** by underground radiation searches at Gran Sasso (VIP-2) and the Majorana Demonstrator, as well as test mass acceleration noise in LISA Pathfinder.
- **Original GRW Rate ($\lambda \sim 10^{-16}\text{ s}^{-1}$):** Still experimentally viable, but macromolecular matter-wave interferometry (Arndt group, Vienna, $M > 2.5 \times 10^4\text{ Da}$) and levitated nanoparticle optomechanics (Ulbricht group) are rapidly closing the viable parameter window.

---

## Detailed Comparison: Objective Collapse vs. Unitary Collapse

| Feature | Objective Collapse (GRW / CSL / DP) | Unitary Collapse (`collapse` program) |
|---|---|---|
| **Dynamical Equation** | **Non-linear, stochastic** modification of Schrödinger equation | **Strictly linear, deterministic** Schrödinger equation |
| **Unitarity** | Fundamentally violated | Strictly preserved globally |
| **Energy Conservation** | Violated (spontaneous heating / energy drift) | Strictly conserved ($\langle \hat{H} \rangle = \text{const}$) |
| **Origin of Single Outcomes** | Real, spontaneous stochastic noise field in nature | Autonomous dynamical latching onto projective roots $(A_N, C_N)$ |
| **Role of Initial Conditions** | Irrelevant (noise drives any state to collapse) | **Crucial:** only projective root microstates yield definite outcomes |
| **Status of Born's Rule** | Derived dynamically from martingale property of SSE | Derived from geometric distribution of projective roots |
| **Experimental Deviations** | Spontaneous heating, force noise, anomalous X-rays | Short-time readout latency $t_m$, covering-radius scaling $\delta_n$ |

---

## Key References

- [[GRW-1986]] — Foundational paper on spontaneous localization.
- [[Pearle-1989-CSL]] — Continuous Spontaneous Localization (CSL).
- [[Bassi-et-al-2013]] — Comprehensive review of objective collapse models and bounds.
- [[Diosi-Penrose-Model]] — Gravity-induced collapse mechanism.
- [[falsifiability-and-experiments]] — Experimental routes distinguishing unitary collapse from objective collapse.
- [[big-picture]] — The linearity obstruction and the restricted-state loophole.
