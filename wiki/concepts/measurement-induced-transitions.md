# Measurement-Induced Phase Transitions (MIPT)

## Overview

Measurement-Induced Phase Transitions (MIPT) are non-equilibrium dynamical phase transitions in the entanglement structure of many-body quantum systems. When an interacting many-body system is subjected to the competing influences of:
1. **Unitary scrambling dynamics** (which generate multi-partite entanglement and spread information ballistically), and
2. **Local projective measurements** (which extract information and destroy quantum entanglement via the quantum Zeno effect),

the steady-state quantum trajectories undergo a sharp phase transition at a critical measurement rate $p_c$. Below $p_c$, the steady state exhibits extensive **volume-law entanglement**; above $p_c$, frequent measurements collapse the system into a localized **area-law entangled phase**.

MIPT demonstrates that measurement is not a passive external observation, but an active dynamical force capable of driving novel quantum critical phenomena.

---

## Core Physical Model: Hybrid Monitored Circuits

### Circuit Architecture
The standard theoretical platform is a 1D spatial array of $L$ qubits evolving under discrete time layers:
1. **Scrambling Unitary Layer:** Adjacent pairs of qubits undergo random two-qubit gates (Haar-random unitaries or random Clifford gates) arranged in a brickwork geometry. These gates generate entanglement and spread operators ballistically with butterfly velocity $v_B$.
2. **Measurement Layer:** Each qubit in the array is independently subjected to a projective measurement (e.g., measuring Pauli $\sigma_z$) with probability $p \in [0, 1]$.

```
Time ^
  t  |   ---[ U ]-------[ U ]-------[ U ]---   (Unitary brickwork)
     |      |    M(p)   |    M(p)   |
     |   -------[ U ]-------[ U ]-------    (Random measurements at rate p)
     |      M(p) |      M(p) |      M(p)
     +-------------------------------------> Space (x = 1 ... L)
```

---

## The Trajectory Nature of the Transition

A critical subtlety of MIPT is that the phase transition is **completely invisible at the ensemble-averaged level**:
$$\rho(t) = \mathbb{E}_{\mathbf{m}}\left[ |\psi_{\mathbf{m}}(t)\rangle\langle\psi_{\mathbf{m}}(t)| \right] = \sum_{\mathbf{m}} P(\mathbf{m}) |\psi_{\mathbf{m}}(t)\rangle\langle\psi_{\mathbf{m}}(t)|,$$
where $\mathbf{m} = (m_1, m_2, \dots, m_T)$ is the sequence of measurement outcomes. Averaging over all outcomes causes $\rho(t)$ to rapidly decohere into the completely mixed state $\rho \propto \mathbb{I}$, which has trivial thermal entanglement across all parameters.

**The transition exists solely at the level of individual pure-state quantum trajectories:**
$$\bar{S}_A = \mathbb{E}_{\mathbf{m}}\left[ -\operatorname{Tr}\left( \rho_A^{(\mathbf{m})} \ln \rho_A^{(\mathbf{m})} \right) \right],$$
where $\rho_A^{(\mathbf{m})} = \operatorname{Tr}_B |\psi_{\mathbf{m}}\rangle\langle\psi_{\mathbf{m}}|$ is the reduced density matrix of subsystem $A$ for a specific measurement trajectory.

---

## The Entanglement Phases

```
          Volume-Law Phase                Critical Point               Area-Law Phase
              (p < p_c)                     (p = p_c)                    (p > p_c)
    +---------------------------+   +-----------------------+   +-------------------------+
    |  Scrambling Dominates     |   |   Conformal Scaling   |   |   Zeno Pinning Dominates|
    |  S_A ~ s(p) * L_A         |   |   S_A ~ (c/3) * ln L_A|   |   S_A ~ const           |
    |  QEC Code Active          |   |   Logarithmic Scaling |   |   Entanglement Localized|
    +---------------------------+   +-----------------------+   +-------------------------+
    0 <--------------------------------------- p_c --------------------------------------> 1
                              Measurement Probability p
```

### 1. Volume-Law Entangled Phase ($p < p_c$)
Unitary scrambling dominates over local measurements. For a subsystem $A$ of length $L_A \le L/2$:
$$\bar{S}_A \sim s(p) L_A.$$
Information is encoded non-locally across multi-partite entangled degrees of freedom. Local measurements cannot collapse the global state because local observables contain virtually no extractable information about the scrambled subsystem.

### 2. Area-Law Entangled Phase ($p > p_c$)
Measurements dominate over unitary scrambling. By the **Many-Body Quantum Zeno Effect**, frequent measurements continuously project the state onto local product states faster than entanglement can build up:
$$\bar{S}_A \sim \text{const} \quad (\text{independent of } L_A).$$
Entanglement is confined to boundary pairs; long-range multi-partite entanglement is suppressed.

### 3. Critical Point ($p = p_c$)
At the transition threshold, the system displays universal scale invariance. The trajectory-averaged entanglement entropy scales logarithmically:
$$\bar{S}_A(L_A) = \frac{c_{\text{eff}}}{3} \ln\left[ \frac{L}{\pi} \sin\left(\frac{\pi L_A}{L}\right) \right] + s_0,$$
resembling the ground state of a 1D quantum critical system described by a 2D boundary Conformal Field Theory (CFT) with effective central charge $c_{\text{eff}}$.

---

## Statistical Mechanics Mapping via the Replica Trick

Skinner, Ruhman, Nahum (2019) and Fisher et al. (2023) mapped MIPT onto a classical statistical mechanics problem:
- Computing the $n$-th Rényi entropy across trajectories requires evaluating $\mathbb{E}_{\mathbf{m}} [(\operatorname{Tr} \rho_A^n) / (\operatorname{Tr} \rho)^n]$.
- In the replica limit $n \to 1$, this maps to the partition function of a 2D classical Potts/permutation spin model with symmetry group $(S_n \wr S_2)/\mathbb{Z}_2$.
- The **volume-law phase** corresponds to an ordered, symmetry-broken phase of the statistical mechanics model.
- Measurements act as symmetry-breaking boundary magnetic fields. As $p$ increases, these boundary fields induce a **domain-wall depinning transition** into the disordered phase (the area-law phase).

---

## Connection to Quantum Error Correction (QEC)

Choi, Bao, Qi, Altman (2020) and Gullans & Huse (2020) revealed the deep information-theoretic foundation of MIPT:
- The volume-law phase is literally a **dynamically generated quantum error-correcting code**.
- Unitary gates act as an encoding circuit that hides quantum information in non-local correlations.
- Local measurements act as quantum erasure/loss errors.
- As long as $p < p_c$, the code capacity is non-zero: an unknown qubit injected at time $t=0$ remains protected in the bulk code subspace for an exponentially long time $t \sim e^{\mathcal{O}(L)}$, with a code distance scaling as $d \sim L$.
- The critical measurement threshold $p_c$ is the **Shannon/quantum error-correction threshold** of the monitored circuit. Above $p_c$, the code capacity drops to zero, and measurements extract the quantum information faster than scrambling can conceal it.

---

## Experimental Observations on Quantum Processors

Observing MIPT experimentally is challenging due to the **post-selection problem**: repeatedly preparing the same pure-state trajectory requires obtaining an identical sequence of random measurement outcomes $\mathbf{m}$, an event whose probability decays exponentially as $2^{-p L T}$.

Two major breakthroughs bypassed the post-selection bottleneck:

1. **Google Quantum AI (2023 on Sycamore Processor):**
   - Implemented monitored Clifford circuits on up to 70 superconducting qubits.
   - Bypassed post-selection by coupling a single ancillary "reference qubit" to the system and measuring the **purification transition**: whether the reference qubit's entanglement with the system survives or purifies under measurements.
   - Verified the volume-law to area-law boundary and observed the QEC code threshold directly.

2. **IBM Quantum Processors (Hoke et al. 2023):**
   - Exploited **space-time duality** in 1D circuits (swapping spatial and temporal axes so that unitary gates map to non-unitary operations).
   - Used classical shadow tomography to measure non-linear entanglement measures with polynomial sample complexity.

---

## Relevance to `unitary-collapse`

MIPT has profound implications for the `unitary-collapse` program:

1. **Measurement as a Dynamical Many-Body Phase Transition:** MIPT proves that measurement is not an unmodeled, instantaneous collapse, but a genuine physical phase transition governed by competing microscopic timescales (scrambling time vs. measurement back-action time).
2. **The Scrambling-to-Born Hypothesis:** In the `unitary-collapse` program, it is hypothesized that an appropriately structured detector Hamiltonian can produce a Born-like root distribution, whereas an isotropic Haar-scrambling detector drives the system to a uniform baseline. The competition between local structured coupling and integrability-breaking scrambling in `unitary-collapse` is the Hamiltonian analog of the MIPT transition, subject to verification under the SPEC v1.0 frozen verifier.
3. **Experimental Validation Platforms:** The superconducting processors used to demonstrate MIPT (Google Sycamore, IBM Quantum) provide the exact experimental platforms proposed in the `unitary-collapse` experimental roadmap ([[falsifiability-and-experiments]]) to probe mesoscopic detector latching and covering-radius scaling.

---

## Key References

- [[Li-Chen-Fisher-2019]] — Discovery of measurement-induced entanglement transitions.
- [[Guttel-2026]] — Dynamical transitions in monitored superconducting qubits.
- [[falsifiability-and-experiments]] — Concrete mesoscopic tests of unitary collapse.
- [[spectral-statistics]] — Level statistics, chaos, and integrability breaking.
- [[big-picture]] — The restricted-state loophole and the linearity obstruction.
