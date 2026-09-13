# Consistent Histories (Decoherent Histories)

## Overview

The Consistent Histories (or Decoherent Histories) interpretation, pioneered by Robert B. Griffiths (1984) and extended by Roland Omnès (1988–1994) and Murray Gell-Mann & James B. Hartle (1990–1993), formulates quantum mechanics without invoking wave-function collapse, observers, or external measurement apparatuses. It interprets quantum theory as a generalized stochastic theory of closed systems—such as the universe as a whole—that assigns objective probabilities to sequences of quantum events (histories) provided that quantum interference between alternative histories vanishes according to a rigorous **decoherence functional** criterion.

---

## Core Mathematical Structure

### Quantum Histories
A history $\alpha$ is a time-ordered sequence of quantum properties represented by projection operators $P_{\alpha_k}(t_k)$ at discrete times $t_1 < t_2 < \dots < t_n$:
$$\alpha = \left( P_{\alpha_1}(t_1), P_{\alpha_2}(t_2), \dots, P_{\alpha_n}(t_n) \right),$$
where each $P_{\alpha_k}(t_k)$ is a Heisenberg-picture projection operator:
$$P_{\alpha_k}(t_k) = e^{i\hat{H}t_k/\hbar} P_{\alpha_k} e^{-i\hat{H}t_k/\hbar}, \quad P_{\alpha_k}^\dagger = P_{\alpha_k} = P_{\alpha_k}^2, \quad \sum_{\alpha_k} P_{\alpha_k} = \mathbb{I}.$$

### Class Operators
The entire sequence of events defining history $\alpha$ is represented by a single **class operator** $C_\alpha$, given by the time-ordered product:
$$C_\alpha \equiv P_{\alpha_n}(t_n) P_{\alpha_{n-1}}(t_{n-1}) \cdots P_{\alpha_1}(t_1).$$
Note that while the individual $P_{\alpha_k}$ are projection operators, the product $C_\alpha$ is generally neither Hermitian nor a projector ($C_\alpha^\dagger \neq C_\alpha$, $C_\alpha^2 \neq C_\alpha$).

### The Decoherence Functional
For a closed quantum system with initial density matrix $\rho_0$, the interference between two alternative histories $\alpha$ and $\alpha'$ is quantified by the **decoherence functional**:
$$D(\alpha, \alpha') \equiv \operatorname{Tr}\left[ C_\alpha \rho_0 C_{\alpha'}^\dagger \right].$$

The decoherence functional satisfies three fundamental mathematical properties:
1. **Hermiticity:** $D(\alpha, \alpha') = D^*(\alpha', \alpha)$.
2. **Positivity:** $D(\alpha, \alpha) \ge 0$ for all $\alpha$.
3. **Normalization:** $\sum_{\alpha, \alpha'} D(\alpha, \alpha') = \operatorname{Tr}[\rho_0] = 1$.

---

## Consistency Conditions

In general, quantum mechanics exhibits interference between histories: the probability of a disjunction of histories $P(\alpha \vee \alpha')$ is not the sum of their individual probabilities because:
$$\operatorname{Tr}\left[ (C_\alpha + C_{\alpha'}) \rho_0 (C_\alpha + C_{\alpha'})^\dagger \right] = D(\alpha, \alpha) + D(\alpha', \alpha') + 2\operatorname{Re} D(\alpha, \alpha').$$

Probabilities can only be assigned meaningfully to a family of histories if the interference term vanishes identically, restoring the classical Kolmogorov additivity axiom:

### 1. Weak Consistency (Griffiths 1984)
$$\operatorname{Re} D(\alpha, \alpha') = 0 \quad (\forall \alpha \neq \alpha').$$
This is the minimal, necessary and sufficient condition for Kolmogorov probability additivity:
$$P(\alpha \vee \alpha') = P(\alpha) + P(\alpha').$$

### 2. Medium / Strong Consistency (Gell-Mann & Hartle 1990)
$$D(\alpha, \alpha') = 0 \quad (\forall \alpha \neq \alpha') \iff D(\alpha, \alpha') = P(\alpha) \delta_{\alpha \alpha'}.$$
Both the real and imaginary parts of the off-diagonal elements vanish. Strong consistency guarantees that the probability structure is robust under arbitrary fine-graining, coarse-graining, and unitary phase rotations.

When consistency holds, the probability of history $\alpha$ is given by:
$$P(\alpha) = D(\alpha, \alpha) = \operatorname{Tr}\left[ C_\alpha \rho_0 C_\alpha^\dagger \right].$$

---

## Key Principles & Logical Structure

### The Single-Framework Rule
A central tenet of Griffiths' formulation is the **Single-Framework Rule** (or "Liberty, not Equality"):
- An investigator is free to choose any consistent family (framework) to describe a physical system.
- Within that chosen framework, standard classical Boolean logic and probability theory apply without exception.
- However, combining propositions from two mutually incompatible (non-commuting) consistent frameworks $\mathcal{F}_1$ and $\mathcal{F}_2$ is strictly forbidden. The conjunction $A \wedge B$ of a property $A \in \mathcal{F}_1$ and $B \in \mathcal{F}_2$ has no meaning in quantum theory unless there exists a common refinement that is itself a consistent framework.
- Griffiths uses this rule to dissolve standard paradoxes (EPR, Bell, Wheeler's delayed-choice, Schrödinger's cat) without non-locality or collapse.

### Quasiclassical Realms in Quantum Cosmology
Gell-Mann and Hartle showed that in quantum cosmology, where no external observers exist, the universe naturally exhibits **quasiclassical realms**—maximally refined sets of coarse-grained alternative histories that decohere and exhibit classical deterministic predictability punctuated only by isolated quantum branchings. The hydrodynamic variables (densities of energy, momentum, and particle number) decohere rapidly due to environmental particle scattering, preserving classical conservation equations across cosmological history.

---

## The Dowker–Kent Critique: Anarchy of Frameworks

Fay Dowker and Adrian Kent (1995, 1996) proved a series of theorems demonstrating that the consistent histories program suffers from severe underdetermination:

1. **Proliferation Theorem:** For any given system and initial state $\rho_0$, there exist an uncountably infinite number of mutually incompatible consistent sets of histories.
2. **Counter-Quasiclassical Histories:** Almost all mathematically consistent sets do *not* describe a classical world. Dowker and Kent explicitly constructed consistent sets that match classical reality in the past, but whose future projectors predict bizarre, macroscopic quantum superpositions at the next instant.
3. **Non-Extendibility Theorem:** Given a consistent set of histories defined up to time $t_n$, it is generically impossible to extend the set to time $t_{n+1}$ without destroying consistency at earlier times.

**Conclusion:** The consistency condition alone is too weak to explain why the world appears classical. Some external selection principle is needed to pick out the "physically realized" framework—which risks re-introducing the measurement problem under a new guise.

---

## Comparison: Consistent Histories vs. Unitary Collapse

| Feature | Consistent / Decoherent Histories | Unitary Collapse (`collapse` program) |
|---|---|---|
| **Dynamical Law** | Exact unitary Schrödinger evolution | Exact unitary Schrödinger evolution |
| **Collapse Postulate** | Rejected: replaced by history probabilities | Rejected: replaced by projective root geometry |
| **Framework Status** | **Infinite incompatible frameworks** coexist; observer picks framework | **Unique physical framework** determined by the detector's matrix pencil $(A_N, C_N)$ |
| **Ontology** | Intersubjective / logical propositions | Objective ontic state restricted to algebraic root varieties |
| **Measurement Description**| Coarse-graining + consistency functional | Autonomous dynamic latching onto projective roots |
| **Dowker–Kent Anarchy** | **Vulnerable**: no dynamical rule selects the classical framework | **Immune**: root solutions are mathematically fixed by the detector Hamiltonian spectrum |
| **Born Rule Status** | Diagonal elements of decoherence functional $D(\alpha, \alpha)$ | Distribution of projective roots on the Bloch sphere |

---

## Key References

- [[Griffiths-1984]] — Foundational paper introducing consistent histories.
- [[Gell-Mann-Hartle-1990]] — Decoherent histories in quantum cosmology.
- [[Zurek-2003]] — Decoherence and einselection.
- [[stochastic-quantum-correspondence]] — Barandes' SQC as an indivisible stochastic framework.
- [[big-picture]] — The linearity obstruction and the restricted-state loophole.
- [[projective-roots]] — Matrix pencil construction of collapsible states.
