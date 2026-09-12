# The Claim Ladder

This ladder orders the major scientific claims of the manuscript according to the structural progression:
$$\text{Phenomenon / Platform} \longrightarrow \text{Decisive Observation} \longrightarrow \text{Mechanism} \longrightarrow \text{Robustness} \longrightarrow \text{Significance}$$

Each claim is earned by its predecessors and is strictly bound by its evidential state and wording ceiling.

---

## Claim 1: Exact Projective Pencil Construction & Antipodal Duality
*Phenomenon / Platform*

**Statement**: Under unitary evolution $U(t)$ of a qubit coupled to a $d$-dimensional detector, initial product states yielding definite measurement outcomes are precisely the projective roots of a detector-space matrix pencil $(C, A)$. Unitarity and Jacobi complementary-minor duality force the two outcome-root multisets to be exact Bloch antipodes.
- **Evidence**: `analytically derived`
- **Comparator**: Contrasts with standard open-system decoherence, which describes asymptotic density-matrix off-diagonal decay without identifying exact product-boundary preimages.
- **Caveat**: Algebraic root multiplicity on the Bloch sphere does not, by itself, define a physical probability measure or an outcome selection law.
- **Figure / Equation**: Figure 1 / Figure 2; Equations \eqref{eq:block}--\eqref{eq:asymmetry}.
- **Confidence**: Exact mathematical theorem.
- **Wording Ceiling**: *"Establishes an exact correspondence between definite-outcome product inputs and projective pencil roots, with antipodally paired outcome multisets."*

---

## Claim 2: Generic Haar Scrambling Precludes Axis Selection
*Decisive Observation / Null Model*

**Statement**: For Haar-distributed unitaries $U(2d)$, the projective pencil roots are distributed as the complex spherical ensemble with uniform one-point intensity $d/(4\pi)$ on the sphere. Generic unitary scrambling yields no preferred measurement axis at the ensemble level.
- **Evidence**: `analytically derived`
- **Comparator**: Directly rules out the hypothesis that generic chaotic or random unitary scrambling spontaneously produces a preferred Born measurement dipole.
- **Caveat**: Finite-size random realizations exhibit sample fluctuations; the theorem governs the ensemble one-point intensity ($S_{\mathrm{B}} = 0$).
- **Figure / Equation**: Figure 2(c) / Figure \ref{fig:scaling}(a) dashed baseline; Section "Haar null model".
- **Confidence**: Exact mathematical theorem based on Ginibre-Stiefel reduction.
- **Wording Ceiling**: *"Proves that generic Haar scrambling yields uniform spherical intensity and precludes an ensemble-selected measurement axis."*

---

## Claim 3: Emergence of Born-Like Dipolar Geometry in Many-Body Rings
*Decisive Observation / Numerical Geometry*

**Statement**: In a clean interacting many-body spin ring with collective transverse coupling, the full-sphere distribution of pencil roots develops a strongly dipolar root-count asymmetry matching the qubit Born rule $\cos^2(\theta/2)$, with a count-weighted residual of $0.089$ and $98.2\%$ of odd resolved power in the $\ell=1$ dipole mode.
- **Evidence**: `simulated`
- **Comparator**: Contrasted directly with the flat isotropic Haar null ($S_{\mathrm{B}} = 0$) and the extreme localized poles of strict-QND Hamiltonians.
- **Caveat**: Validated at finite resolution ($36\times18$ equal-area grid) at deterministic post-cutoff times ($t=10^4\,\hbar/J$); does not represent an infinite-time thermodynamic proof.
- **Figure / Equation**: Figure 2 / Figure \ref{fig:fullsphere}; Equation \eqref{eq:H}.
- **Confidence**: Verified on audited Zeus campaign datasets (`N16/hz0_+0.1000/raw_t10000.npz`).
- **Wording Ceiling**: *"Demonstrates that clean interacting spin rings generate a dipolar root-count geometry closely approximating the Born profile."*

---

## Claim 4: Finite-Size Convergence and Robustness Across System Scales
*Mechanism & Scaling*

**Statement**: The polar Born score $S_{\mathrm{B}}$ increases monotonically with system size from $0.192$ at $N=11$ ($2,048$ roots) to $0.807$ at $N=16$ ($65,536$ roots), maintaining unit full-sphere coverage and low azimuthal second-harmonic distortion ($|c_2| \le 0.25$) across all four audited time decades.
- **Evidence**: `simulated`
- **Comparator**: Distinguishes the matched spin ring from un-gated parameter sweeps that exhibit heavy radial tails, severe azimuthal warping, or zero coverage.
- **Caveat**: Evaluated across 24 deterministic parameter rows ($N=11\text{--}16$, $t=10^3\text{--}10^6$); thermodynamic scaling remains a numerical projection.
- **Figure / Equation**: Figure 3 / Figure \ref{fig:scaling}; Equation \eqref{eq:score}.
- **Confidence**: High empirical reproducibility across all 24 verified post-cutoff rows.
- **Wording Ceiling**: *"Shows monotonic finite-size convergence toward Born-like dipolar geometry while preserving unit full-sphere coverage."*

---

## Claim 5: Analytical Certification of Native Commuting-X Families
*Theoretical Certification / Constructive Family*

**Statement**: There exists an explicit, non-empty constructive class of Hamiltonians (the Commuting-X family) whose folded energy spectrum $\sum_i s_i g_i$ analytically satisfies the finite-resolution Born criterion $C_{\mathrm{B}}$.
- **Evidence**: `analytically derived`
- **Comparator**: Shows that Born-like root geometry does not require non-integrable chaos; it can be engineered constructively in structured integrable models.
- **Caveat**: Relies on finely tuned coupling ratios $g_i$ and specific phase choices rather than generic self-tuning.
- **Figure / Equation**: Figure 4(a); `campaigns/constructive-families.md`.
- **Confidence**: Exact analytical proof.
- **Wording Ceiling**: *"Proves the existence of a native Hamiltonian family whose spectrum analytically certifies the Born criterion."*

---

## Claim 6: Rigorous No-Go Boundaries and Non-Normal Breakdown
*Boundaries & Obstructions*

**Statement**: Simple commuting vector fields cannot produce exact Born balance across open detuning intervals (Theorem H). Furthermore, singular-value convergence is insufficient to predict the root distribution of non-normal pencils, falsifying naive Gaussian-substitution approximations.
- **Evidence**: `analytically derived`
- **Comparator**: Rules out simplistic commuting field models and heuristic random-matrix shortcuts.
- **Caveat**: The detuning obstruction applies to commuting fields; non-commuting Hamiltonians with non-trivial relative commutators bypass the no-go.
- **Figure / Equation**: Figure 4(b, c); `campaigns/detuning-intervals.md` and `campaigns/nonnormal-limits.md`.
- **Confidence**: Rigorous mathematical proofs.
- **Wording Ceiling**: *"Establishes rigorous no-go boundaries for commuting vector fields and proves the failure of Gaussian substitution in non-normal pencils."*

---

## Claim 7: Hamiltonian Classification of Unitary Measurement
*Scientific Capability & Significance*

**Statement**: Formulating measurement-compatible states via projective pencils converts the measurement problem into a concrete many-body classification program: characterizing the Hamiltonian algebras and spectral symmetries that produce Born root geometry and record stability.
- **Evidence**: `inferred`
- **Comparator**: Replaces unfalsifiable philosophical interpretations with mathematically defined spectral and geometric criteria.
- **Caveat**: Does not solve the operational preparation problem (why nature populates these boundary states) or prove macroscopic record amplification.
- **Figure / Equation**: Figure 1; Section "Interpretation".
- **Confidence**: Strong conceptual synthesis grounded directly in Claims 1–6.
- **Wording Ceiling**: *"Provides a structural framework for classifying which unitary many-body dynamics admit measurement-compatible root geometries."*
