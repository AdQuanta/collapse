# Superdeterminism

## Overview

Superdeterminism is an ontological framework that resolves Bell's theorem by rejecting **Statistical Independence** (measurement independence): the assumption that hidden variables $\lambda$ describing a quantum source are uncorrelated with the detector settings $(a, b)$ chosen by the experimenters. By allowing $P(\lambda \mid a, b) \neq P(\lambda)$, superdeterminism preserves strict locality and determinism while reproducing the observed violations of Bell inequalities.

The `unitary-collapse` program implements a form of **unitary superdeterminism**: restricting physically realizable states to projective roots of the evolution pencil, within standard linear Hilbert space, without requiring new physics.

---

## Historical Development

### Bell's Original Discussion (1976–1986)

Bell himself identified the superdeterministic loophole while formulating his theorem:

> *"There is a way to escape the inference of superluminal speeds... But it involves absolute determinism in the whole world... Suppose the world is super-deterministic... Then your choice of which measurement to make is predetermined, and it is correlated with the state of the particle you are measuring."* — J. S. Bell (1986, BBC interview)

Bell considered this escape "implausible" but never proved it inconsistent. Key discussions appear in *Speakable and Unspeakable in Quantum Mechanics* (1987), particularly "The Theory of Local Beables" (1976), "Free Variables and Local Causality" (1977), and "Bertlmann's Socks" (1981).

### Shimony–Clauser–Horne Critique (1976)

Formalized the **"conspiracy" objection**: if $P(\lambda \mid a, b) \neq P(\lambda)$, then macroscopic detector settings must be correlated with microscopic source states despite arbitrary physical interventions—an apparently unfalsifiable evasion.

### Modern Revival

Three independent programs have revitalized superdeterminism:

1. **Gerard 't Hooft (2014–2016):** Cellular Automaton Interpretation (CAI)—deterministic permutation dynamics at the Planck scale with quantum mechanics as an emergent linear description.
2. **Tim Palmer (2009–2026):** Invariant Set Theory (IST) and Rational Quantum Mechanics (RaQM)—physical state space as a fractal invariant set $I_U$ with $p$-adic metric geometry.
3. **Sabine Hossenfelder (2019–2024):** Systematic rebuttal of standard objections; local deterministic toy models and experimental proposals with Sandro Donadi.

---

## Core Concepts

### The Violation of Statistical Independence

Bell's theorem requires three assumptions:

1. **Realism:** Outcomes are determined by underlying variables $\lambda$.
2. **Local Causality (Bell Factorizability):** $P(A, B \mid a, b, \lambda) = P(A \mid a, \lambda) P(B \mid b, \lambda)$.
3. **Statistical Independence:** $P(\lambda \mid a, b) = P(\lambda)$.

Since quantum mechanics violates Bell inequalities, at least one assumption fails:
- Bohmian mechanics rejects (2).
- Superdeterminism rejects (3).

### Quantitative Bounds (Hall 2010)

Hall proved that only a **minimal** violation of Statistical Independence is needed to reproduce quantum correlations:

- **Total variation distance:** $M \ge \sqrt{2} - 1 \approx 0.414$ suffices to saturate the Tsirelson bound $S = 2\sqrt{2}$.
- **Mutual information:** $I(\lambda : a, b) \ge 0.144$ bits—less than 1/7 of a bit—reproduces full singlet state correlations locally and deterministically.

This demonstrates that superdeterminism requires far less "conspiracy" than commonly assumed.

### The Conspiracy Objection and Responses

| Objection | Response |
|---|---|
| Requires cosmological fine-tuning | "Fine-tuning" is metric-dependent; with $p$-adic or fractal metrics, the correlations are natural (Palmer) |
| Undermines the scientific method | Any randomized trial already assumes a conditional independence structure; superdeterminism modifies which conditionals hold |
| Unfalsifiable | Concrete experimental proposals exist (Donadi & Hossenfelder 2022, 2024) testing memory bounds in rapid repeated measurements |
| Same as retrocausality | Distinct: superdeterminism uses forward causation from shared past; retrocausality posits backward-in-time influence |

---

## Three Major Frameworks

### 't Hooft's Cellular Automaton Interpretation (CAI)

The universe at the Planck scale is a **deterministic cellular automaton** with $N$ ontological states $\{|e_i\rangle\}$ evolving by permutations. Quantum mechanics emerges as the natural linear algebra of this discrete system:

$$\hat{U}(\tau)|e_k\rangle = |e_{k+1 \bmod N}\rangle, \quad H = \sum_n E_n |n\rangle\langle n|, \quad E_n = 2\pi n/(N\tau).$$

Superpositions $\sum c_i |e_i\rangle$ are mathematical "templates"—statistical tools reflecting incomplete knowledge, not physical reality. Observables are classified as **beables** (diagonal in the ontological basis), **changeables**, or **superimposables** (mathematical fictions).

Bell inequality violations are explained because detector settings are themselves beables of the automaton: counterfactual settings would require a different automaton history, which is not a valid state.

### Palmer's Invariant Set Theory (IST) / Rational QM (RaQM)

Physical state space is a **fractal invariant set** $I_U \subset \Omega$ of the universe's nonlinear dynamics:

- States $\notin I_U$ are physically undefined.
- Under the **$p$-adic metric** natural to this fractal, counterfactual measurement settings (changing $a$ to $a'$ without changing $\lambda$) are infinitely far away—they lie off $I_U$.
- The $p$-adic ultrametric inequality $d_p(x, z) \le \max(d_p(x,y), d_p(y,z))$ means that states sharing macroscopic history but differing in a single detector setting are topologically separated.

**RaQM (2026):** Physical Bloch-sphere states are restricted to discrete points with rational squared amplitudes and rational phase fractions.

### Hossenfelder–Palmer Program (2019–2024)

Systematic defense and experimentalization of superdeterminism:

- **Donadi & Hossenfelder (2021):** Local deterministic toy model producing Born-rule statistics.
- **Donadi & Hossenfelder (2022, 2024):** Experimental proposals using rapidly repeated measurements on cold atoms / superconducting qubits before hidden variables re-equilibrate—testing whether superdeterministic correlations have a finite memory timescale.

---

## Mathematical Framework

### Relaxed CHSH Inequality

Under measurement dependence with total variation $M$:

$$|S| \le 2 + 2M.$$

Saturating the Tsirelson bound $S = 2\sqrt{2}$ requires only $M \ge \sqrt{2} - 1$.

### Hall's Information Deficit

For binary settings with $H(a,b) = 2$ bits, the mutual information needed is:

$$I(\lambda : a, b) \ge 1 - h\!\left(\frac{1 + 1/\sqrt{2}}{2}\right) \approx 0.144 \text{ bits},$$

where $h(p) = -p \log_2 p - (1-p) \log_2(1-p)$ is the binary entropy.

### Explicit Local Deterministic Models

Brans (1988) and Hall (2010) constructed explicit models with outcomes $A(a, \lambda) = \operatorname{sgn}(\cos(a - \lambda))$ and tailored $P(\lambda \mid a, b)$ that recover $E(a,b) = -\cos(a-b)$ exactly, with strict parameter independence and no superluminal signaling.

---

## Connection to `unitary-collapse`

### Unitary Superdeterminism

The `unitary-collapse` program is a **unitary, algebraic realization of superdeterminism** within standard linear Hilbert space:

| Superdeterminism concept | `unitary-collapse` analogue |
|---|---|
| Restricted state space ($I_U$, rational Bloch sphere) | Projective root variety of $(A_N, C_N)$ |
| Statistical independence violation | Only projective roots lead to definite outcomes |
| Born rule from attractor/fractal measure | Born profile $R_*(\theta) = \cos^2(\theta/2)$ from root distribution |
| Deterministic evolution | Standard unitary Schrödinger evolution |
| Macroscopic definiteness | Effective collapse via pencil-matched initial conditions |

### Key Distinction from IST / CAI

- **No new physics required:** No fractal attractors, $p$-adic metrics, or cellular automata; only standard QM with restricted initial conditions.
- **The restriction is dynamical:** The projective root set is determined by the system–detector Hamiltonian, not by cosmological boundary conditions.
- **Constructive mechanism:** Roots are computed explicitly from the generalized eigenvalue problem $C_N v = \lambda A_N v$.

### Schulman's Special States as the Bridge

Schulman's "special states" (1997) are the direct conceptual ancestor:
- Only certain microstates evolve unitarily into definite outcomes.
- The `unitary-collapse` program identifies these as projective roots.
- Superdeterminism provides the foundational justification for why only special states occur physically.

---

## Key References

- [[Hossenfelder-Palmer-2020]] — The benchmark modern review.
- [[Palmer-2026]] — Rational Quantum Mechanics.
- [[tHooft-2016]] — The Cellular Automaton Interpretation.
- [[Hall-2010]] — Quantitative relaxation bounds.
- [[Schulman-Theory]] — Special states as precursor.
- [[Bohm-1952]] / [[DGZ-1992]] — Bohmian mechanics as the contrasting (nonlocal) approach.
- [[Conway-Kochen-2006]] — Free Will Theorem as critical counterpoint.

See also: [[bohmian-mechanics]], [[stochastic-quantum-correspondence]], [[big-picture]], [[projective-roots]].
