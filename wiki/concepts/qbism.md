# QBism (Quantum Bayesianism)

## Overview

QBism (originally Quantum Bayesianism, now simply QBism) is an interpretation of quantum foundations developed by Christopher A. Fuchs, Carlton M. Caves, and Rüdiger Schack, with later contributions from N. David Mermin and Blake Stacey. QBism synthesizes quantum information theory with personalist (subjective) Bayesian probability theory in the tradition of Frank Ramsey, Bruno de Finetti, and Leonard Savage.

In QBism:
- The quantum state $|\psi\rangle$ or $\rho$ is **not an objective property of the physical world**, but an agent's personal degree of belief (credence) about the consequences of their future actions.
- A measurement is an active intervention performed by an agent on external reality, and the "outcome" is the unique personal experience elicited in that specific agent.
- Wave-function collapse is **not a physical event in spacetime**, but a standard Bayesian probability update: an agent updates their beliefs upon having a new experience.
- The Born rule is **not a descriptive law of nature**, but an empirical **normative constraint**—an addition to classical Dutch-book rationality that guides agents living in a quantum world to make coherent bets.

---

## Core Principles

1. **All Probabilities are Personal:** Following de Finetti's dictum (*"Probability does not exist"* as an objective feature of nature), all probabilities—including quantum probabilities and unit probabilities ($P=1$)—are personal judgments held by a situated decision-making agent.
2. **Measurement as Personal Experience:** A quantum measurement is an action an agent takes upon the physical world, and the outcome is the agent's subjective experience. Different agents observing the "same" experiment have their own private experiences and update their own personal states.
3. **Participatory Realism:** QBism is not solipsism or instrumentalism; it posits a genuine, objective external world that exists independently of observers. However, the world is radically unfinished and open: whenever an agent interacts with a system, reality itself is created anew.
4. **No Action-at-a-Distance:** Since quantum states are private beliefs, measurement on an entangled particle by Alice in lab A updates only *Alice's* expectations about what she will experience if she subsequently interacts with Bob. Her measurement has zero physical effect on Bob's system. Nonlocality evaporates.

---

## Key Mathematical Formalism

### 1. The Quantum de Finetti Theorem (Caves, Fuchs & Schack 2002)
In quantum tomography, an experimentalist claims to determine an "unknown quantum state" by measuring an ensemble of identically prepared systems. QBism refutes the existence of "unknown states" via the Quantum de Finetti Theorem:

Let $\rho^{(N)}$ be a state assigned to $N$ systems that is **exchangeable** (invariant under arbitrary permutations of subsystems $\pi \in S_N$):
$$P_\pi \rho^{(N)} P_\pi^\dagger = \rho^{(N)} \quad (\forall \pi \in S_N).$$
If $\rho^{(N)}$ is exchangeable for all $N$ (infinitely extendible), it can be uniquely represented as:
$$\rho^{(N)} = \int_{\mathcal{S}} d\mu(\phi) \, P(\phi) \, (|\phi\rangle\langle\phi|)^{\otimes N},$$
where $\mathcal{S}$ is the manifold of pure states, $P(\phi) \ge 0$, and $\int P(\phi) d\mu(\phi) = 1$.

**Significance:** Tomography does not reveal an objective "true state"; it is simply an agent updating their personal probability distribution $P(\phi)$ over possible pure states as measurement data arrives via Bayes' rule.

### 2. SIC-POVMs and the Fundamental Basis
QBism seeks to express quantum mechanics purely in terms of probabilities, eliminating complex vectors and operators. The ideal mathematical tool is a **Symmetric Informationally Complete Positive Operator-Valued Measure (SIC-POVM)**:

In a Hilbert space of dimension $d$, a SIC-POVM consists of $d^2$ rank-1 operators:
$$E_i = \frac{1}{d} \Pi_i = \frac{1}{d} |\psi_i\rangle\langle \psi_i| \quad (i = 1, 2, \dots, d^2),$$
satisfying:
1. **Completeness:** $\sum_{i=1}^{d^2} E_i = \mathbb{I}_d$.
2. **Equiangularity:** For all $i \neq j$:
   $$\operatorname{Tr}(\Pi_i \Pi_j) = |\langle \psi_i | \psi_j \rangle|^2 = \frac{1}{d+1}.$$

*Zauner's Conjecture (1999):* SIC-POVMs exist in every finite Hilbert space dimension $d \ge 2$. (Verified numerically up to $d > 100$ and analytically in dozens of dimensions).

### 3. The Urgleichung (The Primal Equation)
Any quantum state $\rho$ is completely and uniquely specified by the vector of probabilities $p(i) = \operatorname{Tr}(\rho E_i)$ of obtaining outcome $i$ in a reference SIC-POVM measurement.

When rewritten in terms of these reference probabilities, the Born rule for obtaining outcome $j$ on an arbitrary subsequent measurement $\{F_j\}$ takes the striking form:
$$Q(j) = (d+1) \sum_{i=1}^{d^2} p(i) r(j \mid i) - \frac{1}{d} \sum_{i=1}^{d^2} r(j \mid i),$$
where $r(j \mid i) = d \operatorname{Tr}(E_i F_j)$ is the conditional probability of outcome $j$ given SIC outcome $i$.

**Comparison with Classical Probability:**
In classical probability theory, the Law of Total Probability states:
$$Q_{\text{classical}}(j) = \sum_{i} p(i) r(j \mid i).$$
The **Urgleichung** reveals that quantum mechanics is simply classical probability theory augmented by the geometric scale factor $(d+1)$ and the baseline offset $-1/d$. In QBism, these modifications reflect the fundamental physical constraint that any measurement intervention inevitably disturbs the system.

---

## The Born Rule as a Normative Rule

In classical Bayesian decision theory, Dutch-book arguments prove that an agent whose subjective degrees of belief violate Kolmogorov's probability axioms can be subjected to a set of bets that guarantees a net financial loss regardless of the outcome. Kolmogorov's axioms are thus **normative rules for internal betting coherence**.

QBism argues that **the Born rule is an empirical normative addition to Dutch-book rationality**:
- The Born rule does not describe how microscopic particles behave in the absence of agents.
- Instead, an agent living in a quantum universe of dimension $d$ who desires betting coherence between direct measurements and reference SIC-POVM measurements **must** adjust their subjective odds to satisfy the Urgleichung.
- Violating the Born rule does not violate logic; it violates Dutch-book coherence in an empirical reality governed by quantum physics.

---

## Major Criticisms

- **The Solipsism Dilemma (Timpson 2008):** If states are private beliefs and outcomes are private experiences, how does science achieve objective consensus? QBists reply that agents communicate by treating other agents as physical systems and updating their own beliefs upon receiving reports. Critics argue this reduces intersubjectivity to an epistemic illusion.
- **The Explanatory Deficit:** QBism asserts that the Born rule is a normative constraint on rational betting. But *why* does this specific constraint work so extraordinarily well in our universe? Without positing an underlying objective ontic structure, the empirical success of the Born rule remains an unexplained coincidence.
- **Unclear Ontology:** What is the physical world made of when no agents are measuring it? QBism rejects wave functions, hidden variables, and classical particles as ontic entities, leaving reality's objective substrate thinly characterized.

---

## Comparison: QBism vs. Unitary Collapse

QBism and the `unitary-collapse` program represent radically opposing philosophies of quantum foundations:

| Philosophical Axis | QBism | Unitary Collapse (`collapse` program) |
|---|---|---|
| **Quantum State Ontology** | **$\psi$-epistemic:** personal subjective credence held by an agent | **$\psi$-ontic:** objective physical state of the closed many-body system |
| **Status of Collapse** | Epistemic Bayesian conditionalization upon personal experience | Autonomous, deterministic physical evolution via projective roots |
| **The Measurement Problem** | **Dissolved:** no objective collapse exists to explain | **Under investigation:** definite outcomes hypothesized from exact dual pencils (`paper_ready = false`) |
| **Role of the Observer** | Primary and indispensable (participatory agent) | Completely absent; purely Hamiltonian many-body dynamics |
| **Status of Born Rule** | Normative constraint on betting coherence (Urgleichung) | Hypothesized objective statistical measure from dual-pencil root geometry (unverified under SPEC v1.0) |
| **Locality** | Trivially local (beliefs update locally) | Strictly local (unitary evolution with local Hamiltonians) |
| **Statistical Independence** | Maintained (agents choose measurement settings freely) | Not determined by the root construction; a future selection law could raise measurement-independence questions |

---

## Key References

- [[Fuchs-Mermin-Schack-2014]] — Canonical pedagogical introduction to QBism and the measurement problem.
- [[Born-1926]] — The original descriptive statistical interpretation.
- [[Gleason-1957]] — Geometric derivation of the Born probability measure.
- [[Busch-2003]] — POVM extension of Gleason's theorem to qubits.
- [[big-picture]] — The linearity obstruction and the restricted-state loophole.
- [[projective-roots]] — Matrix pencil construction of collapsible states.
