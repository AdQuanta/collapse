# Many-Worlds Interpretation (Everettian Quantum Mechanics)

## Overview

The Many-Worlds Interpretation (MWI), originating in Hugh Everett III's 1957 Princeton doctoral dissertation under John Archibald Wheeler, resolves the quantum measurement problem by taking the linear, unitary Schrödinger evolution as universally and strictly valid for all physical systems at all times. MWI rejects the postulate of wave-function collapse (von Neumann's Process 1). Instead, when an interaction correlates a microscopic quantum system with a macroscopic apparatus and environment, the universal quantum state splits into a coherent superposition of mutually non-interfering branches, each corresponding to an objectively real, parallel macroscopic world.

---

## Historical Development

### 1. Everett's Original "Relative State" Formulation (1956–1957)
Everett formulated the theory to eliminate the dual-law inconsistency of textbook quantum mechanics (Process 1 vs. Process 2). In Everett's terminology, the universal state vector evolves deterministically; subsystems do not possess absolute states in isolation, but only **relative states** conditioned on definite states of other subsystems.

### 2. DeWitt & Graham's Popularization (1970–1973)
Bryce DeWitt and Neill Graham reified Everett's mathematical formalism into a literal multiverse of physically splitting parallel universes. Graham proposed an infinite-tensor-product frequency operator attempting to deduce the Born rule without decision theory.

### 3. Modern Emergent Multiverse (1990s–Present)
Modern Everettian theory (David Deutsch, Simon Saunders, David Wallace, Sean Carroll) discards literal, discontinuous splitting in physical space. Instead, "worlds" are recognized as **emergent quasi-classical patterns** in the universal wave function, defined and isolated dynamically by environmental decoherence.

---

## Core Mathematical Structure

### Universal Unitary Evolution
The universal state vector $|\Psi(t)\rangle \in \mathcal{H}_{\text{universe}}$ satisfies the time-dependent Schrödinger equation:
$$i\hbar \frac{\partial}{\partial t} |\Psi(t)\rangle = \hat{H} |\Psi(t)\rangle$$
with no non-linear or stochastic modifications.

### Relative States
For a bipartite system $\mathcal{H} = \mathcal{H}_S \otimes \mathcal{H}_A$ in an arbitrary state:
$$|\Psi\rangle = \sum_{i,j} c_{ij} |s_i\rangle \otimes |a_j\rangle,$$
and for any chosen state vector $|\eta\rangle \in \mathcal{H}_A$, the relative state of subsystem $S$ is uniquely defined by:
$$|\psi_{\text{rel}}^S(\eta)\rangle = \mathcal{N} \sum_i \left( \sum_j c_{ij} \langle \eta | a_j \rangle \right) |s_i\rangle,$$
where $\mathcal{N}$ is a normalization constant.

### Apparatus Memory and Branching Dynamics
Let an apparatus $A$ with ready memory state $|a_0\rangle$ interact with system $S = \sum_i c_i |s_i\rangle$ via a unitary measurement propagator $U(t)$:
$$U(t) \left[ \left( \sum_i c_i |s_i\rangle \right) \otimes |a_0\rangle \right] = \sum_i c_i |s_i\rangle \otimes |a_i\rangle.$$
Subsequent measurements on $S$ or another system $B$ correlate further registers:
$$\sum_{i,j} c_i d_{j|i} |s_i\rangle |b_j\rangle \otimes |a_{i,j}\rangle.$$
Because each component $|a_{i,j}\rangle$ records a fully consistent sequence of classical measurement records, embedded observers within each branch experience an unbroken, determinate classical history.

---

## The Preferred Basis Problem & Decoherence

A long-standing objection to early MWI was basis ambiguity: since a vector can be decomposed in infinitely many orthonormal bases, why does the universe branch in the position/pointer basis rather than an arbitrary macroscopic superposition?

Modern MWI resolves this via **environment-induced superselection (einselection)** (Zurek 1982, 2003; Zeh 1970):
1. The apparatus couples unavoidably to an environment $E$ consisting of $10^{20}-10^{26}$ uncontrolled degrees of freedom (photons, air molecules, phonons):
   $$H_{\text{int}} = \sum_k P_k^A \otimes B_k^E.$$
2. The pointer basis $\{|a_k\rangle\}$ comprises the eigenstates of operators that commute with the interaction Hamiltonian:
   $$[H_{\text{int}} + H_A, P_k^A] \approx 0.$$
3. The reduced density matrix of the system-apparatus rapidly diagonalizes in the pointer basis:
   $$\rho_{SA}(t) = \mathrm{Tr}_E |\Psi\rangle\langle\Psi| = \sum_k |c_k|^2 (|s_k\rangle\langle s_k| \otimes |a_k\rangle\langle a_k|) + \mathcal{O}(e^{-t/\tau_{\text{dec}}}),$$
   with decoherence timescale $\tau_{\text{dec}} \sim 10^{-20}\text{ s}$. Decoherence dynamically suppresses inter-branch interference, preventing macroscopic superpositions from recombining and establishing stable, non-interfering branches.

---

## Derivations of the Born Rule in MWI

Since all branches are actualized in MWI, explaining why observers observe statistical frequencies matching Born's rule $p_k = |c_k|^2$ is the central theoretical challenge:

### 1. Decision-Theoretic Derivation (Deutsch 1999, Wallace 2007/2012)
David Wallace proved the **Deutsch-Wallace Theorem**: Any rational agent who knows they are facing a branching event and whose preferences satisfy standard Savage/decision-theoretic axioms (richness, state supervenience, solution independence, and branching indifference) **must** order their preferences as if outcome $k$ had objective subjective probability equal to its branch weight:
$$\mathcal{U}(\text{act}) = \sum_k |c_k|^2 u(x_k).$$
Probability is thus grounded in operational rationality: an agent who bets against Born weights acts irrationally.

### 2. Environment-Assisted Invariance / Envariance (Zurek 2003, 2005)
Wojciech Zurek derived the Born rule from symmetry properties of entangled states. If an entangled state $|\psi_{SE}\rangle = \frac{1}{\sqrt{2}}(|0_S\rangle|0_E\rangle + |1_S\rangle|1_E\rangle)$ is symmetric under a local swap $u_S = |0\rangle\langle 1| + |1\rangle\langle 0|$ that can be completely undone by an operation on the isolated environment $u_E$, the local probabilities on $S$ must be identical ($p_0 = p_1 = 1/2$). Extending this to unequal amplitudes via fine-graining yields $p_k = |c_k|^2$ without assuming probability or decision theory.

### 3. Self-Locating Uncertainty (Vaidman 1998, Carroll & Sebens 2014)
Between the physical branching of the wave function and an observer reading the outcome record, there exists an interval where the observer exists on a specific branch but does not know *which* branch they occupy. In this state of self-locating uncertainty, the unique rational credence assignment satisfying epistemic separability is the branch weight $|c_k|^2$.

---

## Major Criticisms

- **The Incoherence Problem (Maudlin, Albert, Kent):** If all possible measurement outcomes physically occur with 100% certainty in different branches, what does it mean to say that one outcome had a 70% "probability" of occurring? Critics argue that decision theory presupposes uncertainty about what *will* happen, whereas in MWI the agent knows with certainty that *all* outcomes will happen.
- **The Maverick Branch Problem (Kent 2010):** In an infinite branching tree, there exist branches where the Born rule is wildly violated (e.g., a radioactive source never decaying over billions of years). Observers on those branches will deduce incorrect laws of physics. Why should we believe our branch is typical?
- **Ontological Extravagance:** Postulates an unobservable, continuously multiplying continuum of macroscopic universes.
- **Measure Problem:** Because decoherence is an approximate, continuous process, there is no discrete, well-defined integer count of "worlds."

---

## Detailed Comparison: MWI vs. Unitary Collapse

The `unitary-collapse` program and Many-Worlds share the fundamental premise that **Schrödinger evolution is exact and universal** (no non-unitary collapse modifications). However, they resolve the measurement problem through completely opposite mechanisms:

| Architectural Axis | Many-Worlds Interpretation (Everett) | Unitary Collapse (`collapse` program) |
|---|---|---|
| **Dynamical Law** | Exact linear unitary evolution ($U(t) = e^{-iHt/\hbar}$) | Exact linear unitary evolution ($U(t) = e^{-iHt/\hbar}$) |
| **Number of Outcomes** | **All outcomes occur** (branching multiverse) | **Single outcome occurs** (single classical reality) |
| **Physical State Space** | **Unrestricted Hilbert space**: all $|\psi\rangle \in \mathcal{H}$ physically realizable | **Restricted state variety**: only projective roots $\mathcal{R} \subset \mathcal{H}$ are physically realized |
| **Bell's Trilemma** | Violates Single World (keeps Locality + Stat. Indep.) | Violates Statistical Independence (keeps Realism + Locality + Single World) |
| **Mechanism of Definiteness**| Dynamic isolation by infinite environmental decoherence | Autonomous finite-time latching via detector matrix pencil $(A_N, C_N)$ |
| **Origin of Born Rule** | Decision theory (Wallace) or envariance (Zurek) | Algebraic geometry / density of projective roots on the Bloch sphere |
| **Detector Requirement** | Open macroscopic environment with infinite bath modes | Closed, finite mesoscopic detector ($N$ spins) with structured pencil |
| **Ontological Cost** | Infinite parallel universes continuously branching | Restriction of initial microstates (unitary superdeterminism) |

---

## Key References

- [[Everett-1957]] — Foundational relative-state formulation.
- [[Wallace-2012]] — The comprehensive modern defense of the emergent multiverse.
- [[Zurek-2003]] — Decoherence, pointer states, and einselection.
- [[Zurek-2009]] — Quantum Darwinism: redundant broadcast of pointer observables.
- [[big-picture]] — The linearity obstruction and the restricted-state loophole.
- [[projective-roots]] — Matrix pencil construction of collapsible states.
- [[superdeterminism]] — Unitary superdeterminism as the single-world alternative to MWI.
