# Relational Quantum Mechanics (RQM)

## Overview

Relational Quantum Mechanics (RQM), proposed by Carlo Rovelli in 1996 and formalized in subsequent works with Federico Laudisa and Andrea Di Biagio, is an interpretation inspired by the conceptual foundations of Einstein's special relativity. In special relativity, properties such as velocity, simultaneity, and time dilation have no absolute meaning: they exist only relative to a chosen reference frame. RQM extends this principle to all quantum observables:

> **Core Postulate:** *In quantum mechanics, physical variables do not take values absolutely ("in themselves"). A physical variable acquires a definite numerical value only relative to another physical system during an interaction.*

In RQM:
- Any physical system—from an electron or photon to a macroscopic apparatus—can play the role of an "observer" for another system.
- The quantum state $|\psi\rangle$ is not an ontic physical field residing in spacetime, but a book-keeping device representing the information that system $O$ possesses about system $S$.
- There is no absolute, observer-independent universal wave function.
- Wave-function collapse is not a physical process in spacetime; it is merely an update of the relational description relative to the interacting system.

---

## Core Mathematical Formulation

### The Wigner's Friend Scenario in RQM
Let a microscopic system $S$ have an initial state on $\mathcal{H}_S$:
$$|\psi\rangle_S = \alpha |1\rangle_S + \beta |2\rangle_S \quad (|\alpha|^2 + |\beta|^2 = 1).$$
Let $O$ (the Friend) be an observer with ready state $|o_0\rangle \in \mathcal{H}_O$, and $W$ (Wigner) be a super-observer outside the isolated laboratory.

1. **Relative to $O$ (The Interacting Observer):**
   $O$ interacts with $S$ via a physical coupling that measures observable $A = |1\rangle\langle 1| - |2\rangle\langle 2|$. During this physical interaction, a **relative fact** is realized: variable $A$ takes a definite eigenvalue $a \in \{+1, -1\}$. Relative to $O$, the state of $S$ collapses to $|1\rangle_S$ (with probability $|\alpha|^2$) or $|2\rangle_S$ (with probability $|\beta|^2$).

2. **Relative to $W$ (The Non-Interacting Observer):**
   $W$ has not interacted with either $S$ or $O$. Relative to $W$, the joint system $S \otimes O$ evolves strictly unitarily under the joint Hamiltonian:
   $$|\Psi_{SO}(t)\rangle = \hat{U}_{SO} \left( |\psi\rangle_S \otimes |o_0\rangle_O \right) = \alpha |1\rangle_S |o_1\rangle_O + \beta |2\rangle_S |o_2\rangle_O.$$
   Relative to $W$, **no collapse has occurred**. The observable $A$ has no definite value relative to $W$.

**The RQM Resolution:** There is no contradiction between $O$'s report and $W$'s description because both descriptions are true relative to their respective reference systems. The question *"what is the absolute, true state of S?"* is physically meaningless in RQM.

---

## Cross-Perspective Consistency

A major challenge to RQM is whether it collapses into solipsism: if $O$ saw a definite outcome $+1$, but to $W$ the outcome is indeterminate, can different observers ever agree on facts?

Rovelli proves that consistency between observers is established **operationally through physical interaction**:
- If $W$ measures $O$ (asking *"what did you observe?"*) and subsequently measures $S$ in the same basis, standard quantum mechanics guarantees that $W$ will never detect an inconsistency between $O$'s record and $S$'s state.
- The probability of $W$ finding a discrepancy vanishes identically:
  $$\langle \Psi_{SO} | \left( \hat{P}_{S, 1} \otimes \hat{P}_{O, 2} \right) | \Psi_{SO} \rangle = 0.$$
- Observers agree on facts not because an absolute third-person reality exists, but because their relative records become correlated whenever they physically communicate.

---

## Sparse Facts vs. Stable Facts (Di Biagio & Rovelli 2022)

To explain why the macroscopic world appears shared, robust, and classical to all observers, Di Biagio and Rovelli distinguished two tiers of ontology:

1. **Sparse (Relative) Facts:** Elementary quantum events occurring at the microscopic scale whenever any two systems interact. Between interactions, physical variables have no values.
2. **Stable Facts:** When system $O$ is macroscopic or coupled to an environmental bath $E$, the relative fact between $S$ and $O$ is redundantly recorded by trillions of environmental degrees of freedom:
   $$|\Psi_{SOE}\rangle = \alpha |1\rangle |o_1\rangle |e_1\rangle + \beta |2\rangle |o_2\rangle |e_2\rangle, \quad \langle e_1 \mid e_2 \rangle \sim e^{-N} \approx 0 \quad (N \sim 10^{23}).$$
   For any third observer $W$, the quantum interference between the two branches is suppressed by $e^{-N}$, rendering the relative fact between $S$ and $O$ a **stable fact for $W$ for all practical purposes (FAPP)**. Classical objectivity emerges from environmental decoherence without requiring absolute collapse.

---

## Extended Wigner's Friend & No-Go Theorems

Recent no-go theorems provide strong mathematical support for RQM's rejection of observer-independent facts:

### 1. Brukner's No-Go Theorem (2018)
Časlav Brukner analyzed an extended Wigner's friend thought experiment with two entangled particles distributed to two isolated labs with observers $F_A, F_B$, measured externally by $W_A, W_B$. Brukner proved that the conjunction of three assumptions:
1. **Universal Validity of Quantum Mechanics;**
2. **Locality (Parameter Independence);**
3. **Observer-Independent Facts** (each measurement yields a single real value that is true for all observers);
leads directly to a Bell-type inequality $S \le 2$, which quantum mechanics violates ($S = 2\sqrt{2}$). Brukner concluded that assumption 3 (**Observer-Independent Facts**) must be rejected, exactly as posited by RQM.

### 2. Frauchiger–Renner Theorem (2018)
Daniela Frauchiger and Renato Renner proved that no physical theory can simultaneously satisfy:
- **(Q):** Quantum mechanics holds universally;
- **(C):** Consistency (agents can use conclusions reached by other agents);
- **(S):** Single-world / single-outcome.
RQM evades the paradox by rejecting **(C)**: an agent outside an isolated lab cannot treat another agent's measurement outcome as an absolute fact without physically interacting with that lab.

---

## Informational Axiomatics

Rovelli's original 1996 derivation based RQM on two informational postulates:
1. **Postulate 1 (Limited Relevant Information):** There is a maximum amount of relevant information that can be extracted from any finite quantum system (e.g., exactly 1 bit for a spin-$1/2$ particle).
2. **Postulate 2 (Unlimited Acquisition of New Information):** It is always possible to acquire new information about a system through new physical interactions.

Because acquiring new information cannot exceed the fixed maximum capacity $N$, learning new information must necessarily render previously acquired information irrelevant. This fundamental informational trade-off directly forces non-commuting observables ($[\hat{A}, \hat{B}] \neq 0$), the Heisenberg uncertainty relation, and the probabilistic structure of state transitions.

---

## Comparison: RQM vs. Unitary Collapse

| Conceptual Dimension | Relational QM (Rovelli) | Unitary Collapse (`collapse` program) |
|---|---|---|
| **Ontology of State** | **$\psi$-relational / epistemic:** state is relative to an observer | **$\psi$-ontic:** objective physical state of the closed system |
| **Status of Facts** | Observer-dependent / relative; no view from nowhere | Absolute, single-world objective reality |
| **Dynamical Law** | Unitary relative to non-interacting systems; collapse relative to interacting system | **Globally unitary at all times**; no relativization |
| **Mechanism of Definiteness**| Relational interaction event | Candidate exact product-to-pole boundary condition; physical selection remains open |
| **Brukner / FR Resolution** | Rejects Observer-Independent Facts | No established resolution under the current SPEC |
| **Role of Detector** | Generic physical system acting as relational reference | Specific many-body Hamiltonian with structured dual pencils |
| **Origin of Born Rule** | Informational capacity postulates | Hypothesized algebraic density of projective roots (unverified under SPEC v1.0, `paper_ready = false`) |

---

## Key References

- [[Rovelli-1996]] — Foundational paper introducing Relational Quantum Mechanics.
- [[Frauchiger-Renner-2018]] — Extended Wigner's friend no-go theorem on self-referential quantum theory.
- [[Zurek-2003]] — Decoherence and einselection.
- [[big-picture]] — The linearity obstruction and the restricted-state loophole.
- [[superdeterminism]] — Unitary superdeterminism as an alternative escape from Wigner's friend paradoxes.
