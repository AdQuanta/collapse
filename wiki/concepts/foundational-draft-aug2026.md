# Foundational Manuscript Draft (August 12, 2026)

**Title:** *A Unitary Route to Measurement-Like Collapse and Born Probabilities in Many-Body Detectors*  
**Date:** August 12, 2026  
**Document Type:** Comprehensive foundation paper draft (36 pages)  
**Location:** Derived from `main.pdf`

---

## Executive Summary & Conceptual Arc

This draft serves as the foundational architecture for the `unitary-collapse` program. It addresses the central tension of quantum measurement: if unitary evolution is universal and every mathematical superposition in Hilbert space is physically realizable, then linear dynamics unavoidably correlates superpositions of system states with superpositions of macroscopic apparatus records (the **linearity obstruction**).

The draft explores the constructive **restricted-state loophole**:
1. Retain exact microscopic unitarity ($U(t) = e^{-iHt}$).
2. Relax the assumption that all vectors in Hilbert space are physically realizable.
3. Show that the set of product states evolving at time $t$ into separable product states aligned with a measurement basis is a **finite, discrete, non-vector-space subset** of Hilbert space ($d = 2^n$ states per outcome).
4. Investigate which many-body Hamiltonian structures generate an outcome distribution of these special states on the Bloch sphere that matches the **Born rule** ($\cos^2(\theta/2)$) rather than Haar-random uniformity.

```
Spontaneous emission       Thermalization             Measurement
reduced irreversibility    local relaxation           definite outcome
global unitarity       --> global unitarity       --> unitary route?
[Lindblad/Open Systems]    [ETH/Dephasing/Scrambling] [Restricted State Loophole]
```

---

## Core Technical Structure

### 1. The Block Propagator & Dual Pencils (§3, App. B)
In the readout basis $\{|0\rangle, |1\rangle\}$ for the measured qubit:
$$
U(t) = \begin{pmatrix} A(t) & B(t) \\ C(t) & D(t) \end{pmatrix}, \quad A, B, C, D \in \mathbb{C}^{d \times d}.
$$
Using stereographic qubit coordinates $|\psi(z)\rangle = \frac{|0\rangle + z|1\rangle}{\sqrt{1+|z|^2}}$ with $z = e^{i\phi}\tan(\theta/2)$:
- **Outcome 0:** $(C + zD)|\eta\rangle = 0 \iff C|\eta\rangle = \lambda D|\eta\rangle, \quad z = -\lambda$.
- **Outcome 1:** $(A + zB)|\eta\rangle = 0 \iff A|\eta\rangle = \lambda B|\eta\rangle, \quad z = -\lambda$.

*Current convention:* `SPEC.md` v1.0 retains the two physical pencils $(C+zD)$ and $(A+zB)$ in homogeneous form. A complementary or inverse-based pencil is only a derived chart and cannot replace either outcome equation.

### 2. Foundational Mathematical Propositions
- **Proposition 1 (Finite special-state set):** For regular degree-$d$ pencils, counting algebraic multiplicity on the Riemann sphere yields exactly $d = 2^n$ roots per outcome. For finite $n$, this set is of measure zero on the continuous Bloch sphere.
- **Proposition 2 (Generic non-closure under superposition):** Distinct roots have distinct detector eigenvectors; their linear combination is not a product state and fails the pencil condition. The physical set is non-linearly closed by dynamical construction.
- **Proposition 3 (Haar-random rotational invariance):** For $U \sim \text{Haar}(U(2d))$, right-multiplication by $R \in SU(2)$ induces a Möbius transformation $z \mapsto \frac{r_{10}+zr_{11}}{r_{00}+zr_{01}}$ that preserves the pencil's distribution. Thus, Haar unitaries produce an **isotropic, uniform** special-state distribution ($a(\Omega) = 0$), never Born! (See [[haar-baseline]]).

### 3. Asymmetry & Born Profile (§4)
For local counts $N_k(R)$, the outcome fraction is $f_0(R) = \frac{N_0(R)}{N_0(R)+N_1(R)}$. The outcome asymmetry:
$$
a(\Omega) = \frac{\rho_0(\Omega) - \rho_1(\Omega)}{\rho_0(\Omega) + \rho_1(\Omega)} = \hat{n} \cdot \vec{r}(\Omega)
$$
is a pure dipolar ($\ell = 1$) spherical harmonic for an ideal projective measurement along $\hat{n}$.

> [!IMPORTANT]
> **Key Geometric Note on $P(\theta)$ vs. $R(\theta)$:**
> The reflected ratio $R(\theta) = \frac{P(\theta)}{P(\theta)+P(\pi-\theta)} = \cos^2(\theta/2)$ does **not** require $P(\theta)$ itself to have a pure cosine shape! Exact Born balance holds if and only if $P(\theta) = (1+\cos\theta)E(\theta)$ for **any** reflection-even function $E(\pi-\theta) = E(\theta)$. $P(\theta)$ may possess non-trivial structure, ripples, or background, provided the reflection-even balance is satisfied (see [[born-like-points]]).

---

## Evidence Ledger from the Draft (Table 2)

| Statement | Status in Draft | Subsequent Research Status (Post-August 12) |
|---|---|---|
| Block-unitary construction reduces pole collapse to generalized eigenvalues | Established | Preserved across all analytical and production pipelines. |
| Special-state set is generically not closed under superposition | Established generically | Proved mathematically; core premise of the loophole. |
| Special qubit set has measure zero at finite detector size | Established | Finite algebraic count $d=2^n$; density as $d\to\infty$ remains an active question. |
| Haar-random global unitary produces rotationally invariant (uniform) special states | Established | Proved analytically via $SU(2)$ covariance; connected to spherical Ginibre ensemble. |
| Structured Ising and XY detectors can approach Born-like statistics | Numerical observation | Confirmed in high-$N$ ring studies ($N=14\text{--}17$), though constrained by great-circle support. |
| Adding transverse field $h_x$ drives Ising model toward uniform | Preliminary observation | **Contextualized & Refined:** Found on August 27 to be confounded by the central-X great-circle no-go ($h_{z0}=0$ forces 1D circle). |
| Born-like behavior is caused by Poisson rather than Wigner-Dyson level statistics | Conjecture | **Falsified as a single discriminator (August 29, $N=17$ study):** Both Poisson and GOE span $S_{\text{born}} = 0.015\text{--}0.932$. |
| Martingale / zero-drift dynamics gives Born hitting probabilities | Established math implication | Recognized as a viable stochastic route; microscopic derivation remains open. |
| Gleason / Busch theorems explain which Hamiltonians give Born | False / Not claimed | These theorems constrain probability assignments, not Hamiltonian dynamics. |
| Harmonic-oscillator detector makes special set a vector subspace | Open hypothesis | Remains an open solvable-model target. |

---

## Strategic Roadmap & Appendices

- **Section 12 & Appendix G (Falsifiability & Experimental Roadmap):** Four-stage experimental program: (1) numerical classification, (2) programmable mesoscopic quantum simulators, (3) short-time and finite-size deviations, (4) circuit complexity and metric entropy ($K_N(\varepsilon) = \log_2 \mathcal{N}_\varepsilon(\mathcal{R}_N)$). See [[falsifiability-and-experiments]].
- **Section 15 (Five Theorem Targets):**
  1. *Pointer-algebra route* (Doucet-Deffner commutant classification).
  2. *Spectral route* (Integrable vs. chaotic block pencils).
  3. *Entanglement-geometry route* (Product variety intersections with unitary image).
  4. *Stochastic route* (Martingale / zero-drift branch coordinate).
  5. *Locality / record route* (Quantum Markov blankets, coarse record degeneracy).
  See [[theorem-targets]].
- **Appendices:**
  - **App A:** Primer on decoherence, einselection, and why reduced density matrix diagonality is not dynamical collapse.
  - **App B:** With $z=\alpha/\beta$ and state proportional to $\beta|0\rangle+\alpha|1\rangle$, the current Bloch convention is $r = \frac{1}{|\alpha|^2+|\beta|^2}(2\text{Re}(\beta^*\alpha), 2\text{Im}(\beta^*\alpha), |\beta|^2-|\alpha|^2)^T$.
  - **App C:** Random unitary isotropy and the complex spherical Ginibre ensemble $\det(G_1 - zG_2)$.
  - **App D:** Martingales, optional stopping theorem, Gleason, and Busch.
  - **App E:** Energy-level statistics primer: consecutive-gap ratio $\langle \tilde{r} \rangle$, ETH, and MBL distinctions.
  - **App F:** Computational scaling: $O(4^n)$ memory, $O(8^n)$ operations for dense diagonalization.

---

## Relation to the SPEC v1.0 Reset

The August 12 draft is historical architecture, not the current research contract. Its single-pencil convention, manuscript claims, parameter families, and acceptance gates are superseded by `SPEC.md` v1.0. Earlier symmetry, spectral, asymptotic, constructive, and multichannel campaign reports remain evidence to inspect, but none receives v1.0 credit without fresh verification through the dual pencils and complete metric suite.

The only newly audited analytic result is the scoped [[commuting-qnd-sector]] calculation: its exact sector reduction is valid and its critical Gaussian limit fails exact Born in the natural $Z$ output basis, but it does not yet rule out every preferred axis. Historical positive scores and theorem labels must not be quoted as current results.

See also: [[big-picture]], [[projective-roots]], [[haar-baseline]], [[theorem-targets]], [[falsifiability-and-experiments]].
