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

*Note on convention:* Later project phases adopt the complementary-minor / fixed-input-pole convention $Cv = \lambda Av$ (see [[projective-roots]] and [[homogeneous-qz]]), related by unitary dualities.

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
  - **App B:** Homogeneous coordinates $(\alpha, \beta)$ and Bloch vector $r = \frac{1}{|\alpha|^2+|\beta|^2}(2\text{Re}(\alpha^*\beta), 2\text{Im}(\alpha^*\beta), |\alpha|^2-|\beta|^2)^T$.
  - **App C:** Random unitary isotropy and the complex spherical Ginibre ensemble $\det(G_1 - zG_2)$.
  - **App D:** Martingales, optional stopping theorem, Gleason, and Busch.
  - **App E:** Energy-level statistics primer: consecutive-gap ratio $\langle \tilde{r} \rangle$, ETH, and MBL distinctions.
  - **App F:** Computational scaling: $O(4^n)$ memory, $O(8^n)$ operations for dense diagonalization.

---

## Relation to Subsequent Research (August 13 – September 12, 2026)

The August 12 draft provided the broad conceptual canvas. Subsequent work in the repository has significantly sharpened the physics:
1. **Symmetry Sectors & RMT Auditing (Late August):** Mandated sector-by-sector analysis (`scripts/analyze_zeus_spectral_relations.py`), avoiding artificial Poissonian artifacts.
2. **$N=17$ Symmetry-Resolved Spacings (August 29):** Falsified the naive WD-only conjecture; demonstrated that level statistics alone do not control Born quality ([[spectral-statistics]]).
3. **Central-X Great-Circle No-Go (August 27):** Showed that $X$-conserving models are restricted to a 1D great circle, requiring non-$X$ channels ($J_z, J_{zx}$) for full-sphere coverage ([[coverage-gates]]).
4. **Exact Asymptotic Obstructions (September 11):** Proved Theorems A (recurrence), B (commuting conditional limits are $\delta_0$ or uniform), C (measure-zero field restriction), D (folded Gaussian for collective $X$), E (detuned light-tailed coupling no-go). See [[asymptotic-obstructions]].
5. **Scalar Potential & Nonnormal Limits (September 12):** Derived $J_{C,A}(x)$ potential (Theorem F) and proved that Gaussian operator-moment substitution fails for nonnormal root problems (Theorem G). See [[nonnormal-limits]].
6. **Detuning Interval No-Go (September 12):** Proved Theorem H, ruling out open detuning intervals for phase-mixed commuting vector fields ([[detuning-intervals]]).
7. **Constructive Commuting Family (September 11):** Certified a discrete combinatorial family meeting the 64-bin acceptance gate ([[constructive-families]]).
8. **Resonant Return & Multichannel Ring Leads (September 12):** Formulated exact Schur return representation and audited positive $N=14\text{--}17$ XYZ ring candidates ([[resonant-return-dynamics]], [[weak-coupling-search]]).

See also: [[big-picture]], [[projective-roots]], [[haar-baseline]], [[theorem-targets]], [[falsifiability-and-experiments]].
