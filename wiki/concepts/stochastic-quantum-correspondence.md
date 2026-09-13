# Stochastic-Quantum Correspondence (Barandes)

## Overview

Jacob Barandes (Harvard, 2023) establishes a mathematical equivalence between **indivisible stochastic processes** and quantum mechanics: quantum theory can be rigorously formulated as a real-valued stochastic process on a physical configuration space, with complex amplitudes emerging as linearizing potentials for intrinsically non-Markovian dynamics. The boundary separating quantum from classical is not non-commutative algebra or complex Hilbert space, but **indivisibility**—the failure of the Chapman–Kolmogorov composition law at unmeasured intermediate times.

---

## Core Mathematical Framework

### Unistochastic Transition Matrices

Given a unitary $U(t_f, t_i)$ and a configuration basis $\{|j\rangle\}$, define:

$$\Gamma_{ji}(t_f, t_i) = |U_{ji}(t_f, t_i)|^2 = |\langle j | U(t_f, t_i) | i \rangle|^2.$$

This matrix is:
- **Non-negative:** $\Gamma_{ji} \ge 0$.
- **Doubly stochastic:** Columns and rows sum to 1 (from $U^\dagger U = U U^\dagger = \mathbb{I}$).
- **Unistochastic:** Belongs to the non-convex subset of the Birkhoff polytope whose elements are squared moduli of a unitary matrix.

### Indivisibility and the Interference Tensor

For a classical Markov process, transition matrices compose via Chapman–Kolmogorov:

$$\Gamma^{\text{div}}_{ki}(t_2, t_0) = \sum_j \Gamma_{kj}(t_2, t_1) \Gamma_{ji}(t_1, t_0).$$

For quantum dynamics, using $U(t_2, t_0) = U(t_2, t_1) U(t_1, t_0)$ and squaring:

$$\Gamma_{ki}(t_2, t_0) = \sum_j \Gamma_{kj}(t_2, t_1) \Gamma_{ji}(t_1, t_0) + \mathcal{I}_{ki}(t_2, t_1, t_0),$$

where the **interference matrix** is:

$$\mathcal{I}_{ki} = 2 \sum_{j < l} \operatorname{Re}\!\left[ U_{kj}(t_2, t_1) U_{ji}(t_1, t_0) U_{kl}^*(t_2, t_1) U_{li}^*(t_1, t_0) \right].$$

Properties: $\sum_k \mathcal{I}_{ki} = 0$, $\sum_i \mathcal{I}_{ki} = 0$ (probability conserved globally), but generally $\mathcal{I} \neq 0$—the process is **indivisible**.

**Definition:** Quantum mechanics is an indivisible stochastic process: transition probabilities across an interval cannot be factored into independent sequential transitions over unmeasured intermediate states.

### Division Events

A **division event** is a time at which the system's state is "checked" or decohered, restoring divisibility:

$$P(k, t_2 \mid i, t_0)_{\text{divided}} = \sum_j P(k, t_2 \mid j, t_1) P(j, t_1 \mid i, t_0) = [\Gamma(t_2, t_1) \Gamma(t_1, t_0)]_{ki}.$$

Physically: environmental coupling or measurement interaction scrambles the interference phases, $\langle \mathcal{I}_{ki} \rangle_{\text{env}} = 0$, and the stochastic process becomes effectively Markovian at that point.

### Origin of Complex Amplitudes

Complex amplitudes are **not** ontological primitives but **linearizing gauge potentials**:

$$U_{ji}(t, t_0) = \sqrt{\Gamma_{ji}(t, t_0)} \, e^{i \phi_{ji}(t, t_0)}$$

maps the nonlinear, indivisible composition of $\Gamma$ matrices into a linear group representation ($U(t_2, t_0) = U(t_2, t_1) U(t_1, t_0)$). Analogous to how the electromagnetic four-potential $A_\mu$ linearizes gauge interactions.

### Born's Rule

In the SQC, Born's rule is not an independent postulate but the fundamental definition of the statistical state:

$$P(\text{outcome } j \mid \text{prepared in } k) = \Gamma_{jk}(t_f, t_i) = |U_{jk}|^2.$$

---

## Key Claims

| Concept | Barandes' Position |
|---|---|
| Is QM a stochastic process? | **Yes**—a genuine, real-valued, non-negative stochastic process. No negative probabilities needed. |
| Source of quantumness | **Indivisibility**: the failure of Chapman–Kolmogorov at unmeasured intermediate times. |
| Interference | The non-vanishing interference tensor $\mathcal{I}$: breakdown of the law of total probability when intermediate states are unmeasured. |
| Entanglement | Joint unistochastic matrix $\Gamma_{AB}$ does not factorize; indivisibility is global across space-like configurations. |
| Measurement / collapse | Division events followed by standard Bayesian conditioning. The quantum state is epistemic/auxiliary; configurations remain definite. |
| Complex amplitudes | Linearizing potentials for indivisible stochastic composition—not fundamental. |

---

## Comparison with Other Stochastic Approaches

### Nelson's Stochastic Mechanics (1966)

| Feature | Nelson (1966) | Barandes (2023) |
|---|---|---|
| Mathematical base | Continuous Brownian diffusion (Markov) | Configuration-space unistochastic matrices |
| Divisibility | Assumes underlying Markov paths | Explicitly **indivisible** between divisions |
| Wallstrom objection | **Fails**: must postulate quantized circulation $\oint v \cdot dr = 2\pi n \hbar/m$ ad hoc | **Immune**: phase quantization built into the unitary generator |
| Multi-time correlations | **Fail**: differ from standard QM | **Match QM exactly** via division events |
| Stochastic medium | Requires a physical "ether" | None required |

### Consistent Histories (Griffiths, Gell-Mann & Hartle)

Division events play a role analogous to "frameworks" in the consistent histories approach: histories are assigned probabilities only when consistency conditions (analogous to divisibility restoration) are met.

---

## Criticisms and Open Questions

1. **Formal equivalence, not new predictions:** The SQC reformulates QM without modifying predictions. Some argue it repackages the wave function as a generator of unistochastic transitions without truly eliminating it.
2. **Preferred basis problem:** Defining $\Gamma_{ji} = |U_{ji}|^2$ requires choosing a configuration basis $\{|j\rangle\}$. Without a dynamical mechanism (e.g., decoherence/einselection) selecting this basis, the choice remains arbitrary.
3. **Division event circularity:** If division events require macroscopic apparatus or environmental decoherence, the SQC may rename "collapse" rather than explaining it. Barandes argues that decoherence dynamically suppresses $\mathcal{I}$, providing the physical mechanism.

---

## Relevance to `unitary-collapse`

### Direct Connection: Divisibility and Projective Roots

The SQC provides a powerful conceptual lens for the `unitary-collapse` program:

1. **Projective roots as division-event-compatible states:** The projective roots of $C_N v = \lambda A_N v$ are initial qubit states that evolve unitarily into definite pointer states. In Barandes' language, these are the states for which an **autonomous division event** occurs—the many-body detector dynamics naturally restores divisibility without requiring external measurement.

2. **Indivisibility suppression as collapse mechanism:** The `unitary-collapse` mechanism corresponds to finding structural conditions under which many-body latching suppresses $\mathcal{I}_{ki}$ dynamically, producing an autonomous division event without environmental decoherence.

3. **Born rule from root geometry:** If only projective-root states can serve as legitimate division events (in the Barandes sense), then the Born-like distribution of these roots endows the Born rule with its physical content through the structure of the stochastic process itself.

### Repository Connection

The divisibility test was implemented in the repository's archive (`archive/sqc.ipynb`), monitoring:

$$D_{00}(t', t) = \Gamma_{00}(0 \to t) - \left[ \Gamma_{00}(t' \to t)\Gamma_{00}(0 \to t') + (1 - \Gamma_{00}(t' \to t))(1 - \Gamma_{11}(0 \to t')) \right],$$

which directly measures the amplitude of the indivisibility tensor $\mathcal{I}$.

### Contrast with Superdeterminism

- Barandes does **not** invoke superdeterminism: his framework modifies the stochastic composition rule rather than restricting initial conditions.
- However, if only certain states produce autonomous division events, this **implies** a state-space restriction—converging with the unitary-superdeterministic picture from a different direction.

---

## Key References

- [[Barandes-2023]] — The Stochastic-Quantum Correspondence (foundational paper).
- [[Barandes-Kagan-2020]] — Minimal Modal Interpretation (precursor).
- [[bohmian-mechanics]] — The contrasting deterministic hidden-variable approach.
- [[superdeterminism]] — State-space restriction as an alternative route.
- [[projective-roots]] — The constructive special states of unitary collapse.

See also: [[big-picture]], [[spectral-statistics]], [[haar-baseline]].
