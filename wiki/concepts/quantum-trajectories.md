# Quantum Trajectories, Continuous Measurement & Quantum Jumps

## Overview

Textbook quantum mechanics portrays measurement as an instantaneous, discontinuous, and unanalyzable "jump" (von Neumann's projection postulate). Over the past three decades, the development of cavity quantum electrodynamics, superconducting circuit QED, and quantum optics has revolutionized this picture. Quantum measurement can be conducted **continuously in time**, revealing that wave-function collapse is a continuous, smooth, and physically steerable dynamical trajectory governed by competition between Hamiltonian rotation and measurement back-action.

The modern theory of quantum trajectories (Wiseman & Milburn 2010, Carmichael 1993) establishes the physical basis of continuous observation, while groundbreaking experiments (Murch et al. 2013, Weber et al. 2014, Minev et al. 2019) have directly observed, tracked, and even caught and reversed individual quantum state collapses mid-flight.

---

## 1. Formalism of Continuous Quantum Measurement

### From POVMs to the Stochastic Master Equation (SME)
Consider a quantum system weakly coupled to a measurement probe over an infinitesimal time interval $dt$. The output measurement signal $J(t)$ contains the instantaneous expectation value of the measured observable $\hat{A}$ corrupted by fundamental quantum shot noise:
$$J(t) dt = \langle \hat{A} \rangle_t dt + \frac{dW(t)}{\sqrt{8k}},$$
where $dW(t)$ is a standard Wiener increment satisfying $\mathbb{E}[dW] = 0, dW^2 = dt$, and $k$ is the measurement measurement strength.

Conditioned on the continuous measurement record $J(t)$, the quantum state $\rho(t)$ evolves according to the **Belavkin Stochastic Master Equation (SME)**:
$$d\rho = -\frac{i}{\hbar}[\hat{H}, \rho] dt + \mathcal{D}[\hat{c}]\rho \, dt + \sqrt{\eta} \mathcal{H}[\hat{c}]\rho \, dW(t),$$
where:
- $\mathcal{D}[\hat{c}]\rho = \hat{c}\rho\hat{c}^\dagger - \frac{1}{2}\{\hat{c}^\dagger\hat{c}, \rho\}$ is the deterministic Lindblad dissipator representing ensemble dephasing.
- $\mathcal{H}[\hat{c}]\rho = \hat{c}\rho + \rho\hat{c}^\dagger - \operatorname{Tr}[(\hat{c} + \hat{c}^\dagger)\rho]\rho$ is the non-linear measurement innovation superoperator representing conditioning on the acquired measurement record.
- $\eta \in [0, 1]$ is the quantum measurement efficiency ($\eta = 1$ preserves state purity: $d\rho = |\psi\rangle\langle\psi|$).

---

## 2. Weak Measurements and Weak Values (AAV 1988)

When the coupling between a system and a measurement apparatus is tuned so weak that the pointer's quantum uncertainty exceeds the separation between the eigenvalues of the observable $\hat{A}$, an individual measurement extracts very little information and causes negligible back-action.

Yakir Aharonov, David Z. Albert, and Lev Vaidman (AAV, 1988) proved that conditioning weak measurements on a pre-selected initial state $|\psi_i\rangle$ and a post-selected final state $|\psi_f\rangle$ yields the **weak value**:
$$A_w \equiv \frac{\langle\psi_f | \hat{A} | \psi_i\rangle}{\langle\psi_f | \psi_i\rangle}.$$

### Properties of Weak Values
- **Weak Value Amplification:** When initial and final states are nearly orthogonal ($\langle\psi_f | \psi_i\rangle \to 0$), $A_w$ can lie far outside the eigenvalue spectrum of $\hat{A}$ (e.g., spin-$1/2$ yielding a measured component of 100).
- **Complex Quantity:**
  - $\operatorname{Re}(A_w)$ shifts the pointer's position coordinate (effective eigenvalue).
  - $\operatorname{Im}(A_w)$ shifts the pointer's conjugate momentum coordinate, measuring the rate of phase back-action.
- Weak measurements allow non-destructive interrogation of quantum trajectories along their entire paths.

---

## 3. Mapping the Optimal Paths of Collapse (Weber et al. 2014)

In 2014, S. J. Weber, K. W. Murch, I. Siddiqi, A. N. Jordan, and colleagues at Berkeley and Rochester tracked the continuous diffusion of a superconducting transmon qubit on the Bloch sphere during weak homodyne microwave monitoring.

### The Action Principle for Quantum Trajectories
By conditioning on both an initial preparation and a final post-selected measurement outcome, the team mapped the statistical distribution of thousands of individual collapse trajectories:
- Individual trajectories are stochastic and erratic due to Wiener noise $dW(t)$.
- However, the most probable paths—the **optimal paths**—obey an exact **Euler-Lagrange action principle** (the Chantasri–Dressel–Jordan path integral).
- Quantum collapse follows classical-like Hamiltonian equations of motion in phase space:
  $$\dot{z} = \frac{\partial \mathcal{H}_{\text{opt}}}{\partial p_z}, \quad \dot{p}_z = -\frac{\partial \mathcal{H}_{\text{opt}}}{\partial z}.$$
This proved experimentally that wave-function collapse is not an arbitrary discontinuous jump, but follows an extremal dynamical trajectory across the state space.

---

## 4. Catching and Reversing a Quantum Jump Mid-Flight (Minev et al. 2019)

In 2019, Zlatko Minev, Michel Devoret, and the Yale quantum team performed a landmark experiment answering Erwin Schrödinger's 1952 challenge: *"Are there quantum jumps?"*

### The Experimental Breakthrough
Using a three-level superconducting artificial atom with states:
- Ground state $|G\rangle$,
- Bright state $|B\rangle$ (interrogated by a readout resonator, generating a continuous fluorescence photodiode signal),
- Dark state $|D\rangle$ (metastable state).

```
          |B> (Bright)
           ^  \
           |   \ Fluorescence
     Drive |    v
           |   Photon Record
          |G> <=====================> |D> (Dark)
                 Jump of Interest
```

1. **The Quiescent Warning Signal:** Minev et al. discovered that while jumps from $|G\rangle$ to $|D\rangle$ occur stochastically in the long term, **every individual jump is preceded by an advance warning signal**: a brief quiescent latency period ($\sim \text{few }\mu\text{s}$) where fluorescence photon emissions cease.
2. **Deterministic Continuous Mid-Flight Flight:** The transition from $|G\rangle$ to $|D\rangle$ is not instantaneous: it is a continuous, smooth, coherent rotation on the Bloch sphere taking flight time $\tau_{\text{flight}} \approx 4\,\mu\text{s}$.
3. **Mid-Flight Reversal:** Detecting the onset of the quiescent period in real time via an FPGA controller, the team injected a microwave feedback pulse catching the state in mid-superposition and coherently rotating it back to $|G\rangle$, completely aborting the jump with zero loss of quantum information.

**Conclusion:** Nature does not make discontinuous jumps; quantum state reduction is a continuous physical transit that can be intercepted and controlled.

---

## 5. Relevance to `unitary-collapse`

The experimental realities of quantum trajectories provide direct empirical foundation for the `unitary-collapse` program:

1. **Validation of Continuous Unitary Dynamics:** Minev et al. and Weber et al. experimentally disprove the idea that collapse is an instantaneous, non-unitary axiom. If collapse is a physical, continuous transit lasting microseconds, then modeling collapse as an internal dynamical process governed by the Schrödinger equation is physically sound.
2. **Internal Stochasticity vs. External Noise:** In standard trajectory theory, the noise $dW(t)$ comes from an external classical environment/detector. In `unitary-collapse`, the detector is modeled microscopically as an $N$-spin quantum system: the effective noise arises internally from many-body dephasing and information dispersal among detector modes.
3. **Projective Roots as Exact Collapsible States:** In SPEC v1.0, exact collapsible states are defined as solutions of the dual homogeneous pencils $(U_{10} + \lambda U_{11})|D\rangle = 0$ (outcome 0) and $(U_{00} + \lambda U_{01})|D\rangle = 0$ (outcome 1). These initial product microstates evolve deterministically under $U(T)$ into unentangled pointer outcomes.

---

## Key References

- [[Minev-2019]] — Catching and reversing a quantum jump mid-flight.
- [[Li-Chen-Fisher-2019]] — Measurement-induced phase transitions in monitored circuits.
- [[Guttel-2026]] — Monitored superconducting qubits.
- [[falsifiability-and-experiments]] — Experimental routes for testing unitary collapse.
- [[big-picture]] — The conceptual trajectory of unitary collapse.
