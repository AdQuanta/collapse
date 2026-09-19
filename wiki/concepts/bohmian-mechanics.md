# Bohmian Mechanics (de Broglie–Bohm Pilot-Wave Theory)

## Overview

Bohmian mechanics is a deterministic, nonlocal hidden-variable completion of quantum mechanics in which point particles possess definite positions at all times and are guided by the wave function through a first-order velocity field on configuration space. It reproduces all predictions of standard QM without invoking wave-function collapse.

---

## Core Mathematical Structure

### Guiding Equation

For $N$ particles with positions $\mathbf{Q} = (\mathbf{Q}_1, \dots, \mathbf{Q}_N)$, the wave function $\Psi$ evolves via the standard Schrödinger equation while particle velocities obey the **guiding equation**:

$$\frac{d\mathbf{Q}_k}{dt} = \frac{\hbar}{m_k} \operatorname{Im} \frac{\nabla_k \Psi(\mathbf{Q}, t)}{\Psi(\mathbf{Q}, t)} = \frac{\nabla_k S(\mathbf{Q}, t)}{m_k}$$

where $\Psi = R e^{iS/\hbar}$. The velocity of particle $k$ depends on the instantaneous positions of **all** other particles through $S(\mathbf{Q}_1, \dots, \mathbf{Q}_N, t)$—this is manifest nonlocality.

### Quantum Potential (Bohm's Formulation)

Substituting $\Psi = R e^{iS/\hbar}$ into Schrödinger's equation yields a modified Hamilton–Jacobi equation:

$$\frac{\partial S}{\partial t} + \sum_k \frac{(\nabla_k S)^2}{2m_k} + V + Q = 0, \qquad Q = -\sum_k \frac{\hbar^2}{2m_k} \frac{\nabla_k^2 R}{R}.$$

The modern DGZ formulation treats $Q$ as an artifact of forcing first-order dynamics into second-order form; the guiding equation is the fundamental law.

### Quantum Equilibrium and Equivariance

**Quantum Equilibrium Hypothesis (QEH):** $\rho(\mathbf{q}, t_0) = |\Psi(\mathbf{q}, t_0)|^2$.

**Equivariance (DGZ 1992):** If this holds at $t_0$, it holds for all $t$, because the continuity equation for $\rho$ under the guiding equation is identical to that for $|\Psi|^2$ under Schrödinger evolution. Born's rule is the unique equivariant distribution.

### Emergence of Born's Rule

Two schools:

1. **Typicality (DGZ 1992):** For almost all initial universal configurations $Q_0$ (measured by $|\Psi|^2 dQ_0$), the empirical distribution of subsystem outcomes converges to Born.
2. **Dynamical relaxation (Valentini 1991, 2005):** Chaotic mixing in configuration space drives arbitrary initial $\rho \to |\Psi|^2$ via a subquantum $H$-theorem: $\bar{H}(t) = \int \bar{\rho} \ln(\bar{\rho}/\overline{|\Psi|^2}) \, dq \le 0$.

### Measurement: Effective Collapse

A measurement entangles system ($x$) with apparatus ($y$):

$$\Psi = \sum_k c_k \phi_k(x) \Phi_k(y)$$

The actual apparatus coordinate $Y(t)$ enters the support of exactly one $\Phi_k$; all other branches evaluate to zero at the particle's location. The **conditional wave function** $\psi_{\text{cond}}(x) \propto \phi_k(x)$—mimicking collapse without any non-unitary process.

### Spin and Relativistic Extensions

Spin is **not** an internal property: the particle has only position. The guiding equation generalizes to spinors via $\dot{\mathbf{Q}}_k = (\hbar/m_k) \operatorname{Im}(\Psi^\dagger \nabla_k \Psi / \Psi^\dagger \Psi)$.

Multi-particle relativistic Bohmian dynamics requires a preferred foliation of spacetime into spacelike hypersurfaces (Dürr et al. 2014).

---

## Key Conceptual Features

| Feature | Status |
|---|---|
| **Determinism** | Complete: given $\Psi, Q(0)$, the future is determined |
| **Nonlocality** | Explicit and instantaneous (but no-signaling in equilibrium) |
| **Contextuality** | Measurements are contextual; only position is fundamental |
| **Wave function status** | Ontic field (Bohm, Holland, Valentini) or nomological/law-like (DGZ) |
| **Empty waves** | Non-occupied branches persist unitarily; resolved by the nomological view |
| **Decoherence role** | Essential for permanent effective collapse via branch decoupling |

---

## Criticisms

- **Preferred foliation / relativity tension:** Nonlocal dynamics requires absolute simultaneity; Lorentz invariance of predictions holds but the ontology breaks Lorentz covariance.
- **Contextuality:** All observables except position are contextual—determined by apparatus, not intrinsic to particles.
- **Computational cost:** Computing Bohmian trajectories requires first solving the full $N$-body Schrödinger equation; no computational advantage over standard QM.
- **"Empty wave" / many-worlds-in-denial:** Non-occupied branches persist in the universal wave function (Deutsch 1996 critique).
- **Surreal trajectories:** ESSW (1992) interferometer objection; resolved by DGZ (1993)—contextual which-way detection. Confirmed experimentally by Mahler et al. (2016).

---

## Position in Bell's Trilemma

Bohmian mechanics maintains **Statistical Independence** ($P(\lambda | a, b) = P(\lambda)$) and **violates Bell Locality** (the guiding equation is explicitly nonlocal). This is orthogonal to superdeterminism, which preserves locality but violates Statistical Independence.

| | Bohmian Mechanics | Superdeterminism | Unitary Collapse |
|---|---|---|---|
| **Stat. Independence** | Preserved | Violated | Violated |
| **Bell Locality** | Violated | Preserved | Preserved |
| **Determinism** | Yes | Yes | Yes (unitary) |
| **State restriction** | None ($\forall \|\psi\rangle$) | Fractal/rational | Projective roots |
| **Born rule** | Equilibrium distribution | Emergent from $I_U$ measure | Hypothesized root distribution (unverified, `paper_ready = false`) |

---

## Relevance to `unitary-collapse`

The `unitary-collapse` program takes the **orthogonal** approach to Bohmian mechanics for resolving the measurement problem:

- **Bohm:** Keeps all $|\psi\rangle$ physically accessible; adds a hidden primitive ontology (particle positions $Q$) with nonlocal guidance.
- **Unitary-collapse project:** Adds no extra variables in the tested dynamics and defines projective-root initial states. It has not established that only those states are physically realizable or that their selection is superdeterministic.

Bell-type assumptions would have to be analyzed only after the project supplies an ontology and a preparation/selection law. Local Hamiltonian dynamics and a mathematical root subset alone do not prove violation of Statistical Independence.

Both theories share the commitment that **Born's rule is not a fundamental axiom** but an emergent statistical property (equivariant equilibrium in Bohm; hypothesized root distribution geometry in unitary collapse).

---

## Key References

- [[Bohm-1952]] — Foundational hidden-variable papers (Parts I & II).
- [[DGZ-1992]] — Equivariance, quantum equilibrium, and typicality.
- [[Hossenfelder-Palmer-2020]] — Superdeterminism as the contrasting approach.
- [[Schulman-Theory]] — Special states: the conceptual precursor to unitary collapse.
- [[big-picture]] — The restricted-state loophole and the linearity obstruction.

See also: [[superdeterminism]], [[stochastic-quantum-correspondence]], [[projective-roots]].
