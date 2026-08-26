# Independent mathematical and foundations audit

Date: 2026-08-14  
Scope: `C:\Users\matan\Downloads\main.pdf`, the repository theory and production-analysis code, tests, and the existing report collection.  
Mandate: audit only; no manuscript source was edited.

## Executive verdict

The matrix-pencil idea is mathematically sound, but the strongest exact theory differs in two important ways from the narrative in `main.pdf`.

1. **The two forward outcome pencils are not independent.** For every unitary block matrix, their projective root multisets are exact Bloch antipodes, with algebraic multiplicity. A regular problem therefore has `d` independent projective coordinates and their deterministically labelled antipodes, not two unrelated `d`-point clouds.
2. **The repository's production calculation is a different pencil.** The numerical campaigns solve `C v = lambda A v` (equivalently `A^{-1} C` when `A` is nonsingular), which fixes an input pole and enumerates separable output qubits. The source PDF instead derives the forward preimage pencils `(alpha C + beta D) eta = 0` and `(alpha A + beta B) eta = 0`. Production at time `t` is exactly a forward-pole construction for `U(t)^dagger = U(-t)`, not generally for `U(t)`.

These corrections do not destroy the paper. They sharpen it. The referee-resistant exact backbone is:

- a projective generalized-eigenvalue characterization of pole-factorizing boundary states;
- exact antipodal pairing of the two outcome root multisets;
- exactly `d` projective roots counted with algebraic multiplicity for a regular detector-dimension-`d` pencil;
- an exact complex-spherical-ensemble law for the Haar root process, hence uniform one-point intensity at every `d`;
- generic non-additivity of the **product-state intersection**, carefully separated from a physical restricted-state postulate.

The construction does **not** derive definite outcomes, a root-selection probability, a common apparatus-ready state, stable records, or an arrow of time. The single most damaging foundations objection is that equal algebraic root counting is not a physical probability measure and generic roots require different detector microstates correlated with the qubit input.

## 1. Conventions and exact block algebra

Let

```math
U=\begin{pmatrix}A&B\\ C&D\end{pmatrix},\qquad
A,B,C,D\in\mathbb C^{d\times d},
```

where the qubit index is first, the detector basis is fixed, and the input qubit ray is represented homogeneously by

```math
q=[\alpha:\beta]\in\mathbb{CP}^1,
\qquad |q\rangle=\alpha|0\rangle+\beta|1\rangle .
```

For a detector vector `eta`,

```math
U(|q\rangle\otimes|\eta\rangle)
=|0\rangle\otimes(\alpha A+\beta B)\eta
+|1\rangle\otimes(\alpha C+\beta D)\eta .
```

Therefore the two same-propagator forward pole conditions are exactly

```math
L_0(\alpha,\beta)\eta
=(\alpha C+\beta D)\eta=0,
```

for output pole `|0>`, and

```math
L_1(\alpha,\beta)\eta
=(\alpha A+\beta B)\eta=0,
```

for output pole `|1>`. These assignments and signs in `main.pdf`, Eqs. (15) and (17), are correct.

If `q` and `eta` are nonzero and the undesired component vanishes, unitarity guarantees that the surviving component is nonzero: a nonzero normalized input cannot be mapped to the zero vector.

In the affine chart `alpha != 0`,

```math
z=\beta/\alpha=e^{i\phi}\tan(\theta/2),
```

and the pencils become `C+zD` and `A+zB`. The south pole is the homogeneous point `[0:1]`, i.e. `z=infinity`; it must not be dropped by converting prematurely to an affine eigenvalue.

## 2. Exact theorem: the outcome pencils are antipodally paired

### Theorem 1 (unitary complementary-minor duality)

Let `U` be unitary and let the normalized qubit coordinate be `q=(alpha,beta)^T`. Define its orthogonal/antipodal coordinate

```math
q^\perp=(-\bar\beta,\bar\alpha)^T.
```

Then

```math
\det L_0(\alpha,\beta)
=(-1)^d\det(U)\,
\overline{\det L_1(-\bar\beta,\bar\alpha)} .
```

Consequently,

```math
\det L_0(q)=0
\quad\Longleftrightarrow\quad
\det L_1(q^\perp)=0.
```

The projective roots of the two outcome pencils are therefore exact antipodal multisets, including algebraic multiplicity. In stereographic coordinates,

```math
z\longmapsto z_\perp=-1/\bar z,
```

with `0 <-> infinity`.

### Proof

Form the qubit rotation

```math
R_q=\begin{pmatrix}
\alpha&-\bar\beta\\
\beta&\bar\alpha
\end{pmatrix}\in SU(2)
```

and the unitary `V=U(R_q tensor I_d)`. Its lower-left block is `L_0(q)` and its upper-right block is `L_1(q^perp)`. Jacobi's complementary-minor identity for a unitary matrix gives

```math
\det V_{\mathrm{lower},\mathrm{left}}
=(-1)^d\det(V)\,
\overline{\det V_{\mathrm{upper},\mathrm{right}}}.
```

Since `det(R_q tensor I_d)=1`, `det V=det U`, proving the identity.

### Corollaries that should be elevated

1. If one forward pencil is regular, so is the other. If one is singular (`det L identically 0`), so is the other.
2. For regular pencils, there are `d` independent projective roots, not `2d` independent roots. There are `d` roots for each label, but the second labelled multiset is the deterministic antipode of the first.
3. For empirical measures,

   ```math
   \rho_1(\Omega)=\rho_0(-\Omega)
   ```

   exactly, realization by realization, provided multiplicity and smoothing are treated identically.
4. Hence

   ```math
   f_0(\Omega)
   =\frac{\rho_0(\Omega)}{\rho_0(\Omega)+\rho_0(-\Omega)},
   \qquad
   a(-\Omega)=-a(\Omega).
   ```

   The asymmetry field is inversion-odd. Its spherical-harmonic expansion contains only odd `ell`; an ideal Born measurement is the `ell=1` component, while the first permitted non-Born multipoles are `ell=3,5,...`. Even-`ell` power in an exactly paired analysis is a diagnostic of inconsistent labeling, binning, smoothing, or numerical error.
5. The repository's reflected-polar statistic `P(theta)/[P(theta)+P(pi-theta)]` is not merely an assumed branch construction; the antipodal **root locations** have an exact unitary basis. The associated companion detector vectors still must be solved if they are needed physically.

For a target axis `n`, the exact full-sphere Born condition can now be written using only one root intensity:

```math
\frac{\rho_0(\Omega)}{\rho_0(\Omega)+\rho_0(-\Omega)}
=\frac{1+\hat n\cdot r(\Omega)}2.
```

Equivalently, there must exist a nonnegative inversion-even envelope `s(Omega)=s(-Omega)` such that

```math
\rho_0(\Omega)=\frac{s(\Omega)}2\,
[1+\hat n\cdot r(\Omega)].
```

Thus Born behavior does not require a uniform total point density; it requires the odd part of a single outcome intensity to be exactly dipolar relative to its even envelope. For the `z` axis this gives

```math
\frac{\rho_0(-\Omega)}{\rho_0(\Omega)}
=\tan^2(\theta/2).
```

This is the full-sphere form of the repository's reflected-density criterion.

This exact antipodal theorem is absent from `main.pdf` and is stronger than its appeal to outcome-interchange symmetry only in the Haar ensemble.

## 3. Homogeneous coordinates, infinity, regularity, and root counts

### Theorem 2 (regular-pencil count)

For

```math
p_0(\alpha,\beta)=\det(\alpha C+\beta D),
```

regularity means `p_0` is not the zero polynomial. It is a homogeneous degree-`d` polynomial, so it has exactly `d` zeros in `CP^1` counted with algebraic multiplicity. The same statement holds for `p_1`, and Theorem 1 pairs the two multisets antipodally.

The theorem does **not** imply:

- `d` distinct Bloch points;
- `d` independent detector rays;
- simple roots;
- a probability weight of one per algebraic copy;
- density on the sphere as `d` grows.

At a projective root `q_j`, define

```math
g_j=\dim\ker L_k(q_j).
```

Then the compatible detector rays form `CP^{g_j-1}`. Algebraic multiplicity `m_j` and nullity/geometric multiplicity `g_j` need not agree. A defective multiple root can have `m_j>g_j=1`.

### Infinite roots

For the affine outcome-0 pencil `C+zD`, `z=infinity` is `[alpha:beta]=[0:1]` and is a root precisely when `D` is singular. For outcome 1, infinity is controlled by `B`. The antipodal theorem pairs a zero root of one label with an infinite root of the other.

If QZ solves

```math
C v=\lambda Dv,
```

with homogeneous pair `(a,b)` satisfying `b C v=a D v`, then the physical affine coordinate in `C+zD` is `z=-a/b`; the physical qubit homogeneous coordinate can be stored as `[alpha:beta]=[b:-a]`. A `b=0` QZ eigenvalue is therefore a physical `z=infinity`, not a failure.

The normalized homogeneous residual should be of the form

```math
r=\frac{\|bCv-aDv\|}
{(|b|\|C\|+|a|\|D\|)\|v\|}.
```

### Singular pencils

If `det L(alpha,beta)` vanishes identically, every qubit coordinate has at least one compatible detector null vector and the finite-root theorem is inapplicable. The correct object is the Kronecker structure/minimal indices of the singular pencil, not a list of `d` generalized eigenvalues.

The clean counterexample is qubit-qubit SWAP:

```math
U_{\rm SWAP}(|q\rangle_Q|0\rangle_D)
=|0\rangle_Q|q\rangle_D .
```

Thus every input qubit reaches pole 0 with detector input `|0>`, and the outcome-0 pencil is singular. The outcome-1 pencil is singular as well, as Theorem 1 requires.

The opposite caution is `U=I`: the pencils are regular but maximally degenerate. Outcome 0 has only the north-pole Bloch point with algebraic multiplicity `d` and a `d`-dimensional detector nullspace; outcome 1 has the antipodal south pole.

### Numerical implementation assessment

`collapse/relative_evolution_pencil.py` correctly preserves homogeneous QZ pairs, classifies infinite and indeterminate `(0,0)` pairs, and reports normalized residuals and block conditioning. The focused tests in `tests/test_relative_evolution_pencil.py` cover finite roots, exact infinity, a common-nullspace indeterminate pair, scaling invariance, and residuals.

By contrast, the older `solver="auto"` path in `collapse/analysis.py` can replace a singular solve by a Moore-Penrose pseudoinverse. That is not a projectively valid continuation of a singular pencil and must not support theorem-level root claims. Manuscript numerics should use the homogeneous-QZ path and explicitly report:

- regular versus singular/indeterminate classification;
- finite and infinite counts;
- algebraic multiplicities or root clustering tolerance;
- nullities at repeated roots where relevant;
- maximum homogeneous residual;
- block condition number and rank threshold.

## 4. Critical theory-to-code mismatch

The source PDF and production repository study related but different boundary problems.

### Source-PDF forward preimage problem

`main.pdf`, pp. 8-10 and Appendix B, solves

```math
(\alpha C+\beta D)\eta=0
```

and

```math
(\alpha A+\beta B)\eta=0.
```

These enumerate product **inputs** that reach a specified output pole under the same `U`.

### Production fixed-input-pole problem

`collapse/analysis.py` and `collapse/relative_evolution_pencil.py` use `U00=A` and `U10=C` and solve

```math
C v=\lambda A v.
```

For a finite root,

```math
U(|0\rangle\otimes v)
=(|0\rangle+\lambda|1\rangle)\otimes Av.
```

This enumerates separable **outputs** produced from a fixed input pole. The companion root locations used by production are encoded as

```math
q_0(\lambda)\propto(1,\lambda),
\qquad
q_1(\lambda)\propto(-\lambda^*,1),
```

which are exact antipodes. In code, `D1=-conj(D0)` is the first/second amplitude ratio for the second chart, not the standard stereographic coordinate; the latter is `-1/conj(lambda)`.

### Exact time-direction bridge

The production output cloud for `U^dagger` is exactly the forward outcome-0 preimage cloud for `U`. Therefore production at `+t` supports a forward-preimage statement for `U(-t)`, not automatically for `U(+t)`.

For a real symmetric Hamiltonian in the chosen tensor-product basis, `U(t)` is complex symmetric and `U(-t)=U(t)^*`. Then the `+t` and `-t` production roots are complex conjugate multisets, so polar radii agree while azimuths reverse. This rescues polar histograms for the real Hamiltonian families, but it does not license a same-time full-sphere identification without checking the reality convention.

An independent Haar `d=3` spot check found:

- forward outcome-0 versus forward outcome-1 antipodal matching error: `1.2e-15` maximum Bloch distance;
- production first-pole versus production companion antipodal matching error: `2.0e-15` maximum Bloch distance;
- same-`U` forward outcome-0 versus production first-pole mismatch: `1.25` RMS Bloch distance.

Thus the mismatch is material, not a sign or chart convention.

Relevant source locations:

- `collapse/analysis.py:29-104`, `262-427`;
- `collapse/born.py:83-145`, `195ff`;
- `collapse/relative_evolution_pencil.py:1-183`;
- `tests/test_relative_evolution_pencil.py`;
- `examples/haar_random_unitary.py`;
- `reports/prl_unitary_collapse_2026-08-14/AUDIT.md` and its associated manuscript skeleton, which already recognized the forward/production mismatch but did not state the exact forward-outcome antipodal theorem.

## 5. Precise non-superposition statement

The draft's generic conclusion is directionally correct but its proof and interpretation need tightening.

Define the linear pole-preimage subspace

```math
\mathcal L_k=U^\dagger(|k\rangle\otimes\mathcal H_D),
\qquad \dim\mathcal L_k=d,
```

and the product cone (Segre cone) `Sigma`. The exact special product states are

```math
\mathcal S_k=\mathcal L_k\cap\Sigma.
```

### Theorem 3 (generic non-additivity of the product intersection)

Assume the outcome-`k` pencil is regular and has at least two distinct projective roots `q_1 != q_2`. Pick nonzero `eta_j in ker L_k(q_j)`. Then

```math
q_1\otimes\eta_1+q_2\otimes\eta_2
```

has Schmidt rank two and is not in `Sigma`, hence not in `S_k`.

Reason: for two distinct qubit factors, their sum is product only if the detector factors are proportional. If `eta_1` and `eta_2` were proportional, the same nonzero `eta` would satisfy `L_k(q_1)eta=L_k(q_2)eta=0`; invertibility of the two-coordinate coefficient matrix would imply both detector blocks annihilate `eta`, making the pencil singular. That contradicts regularity.

Within a repeated-root fiber, however,

```math
q\otimes\ker L_k(q)
```

is a linear cone and is closed under addition. If all `d` algebraic roots coincide, as for `U=I`, the fixed-outcome special cone can itself be linear. Therefore the manuscript should not describe all degeneracy exceptions vaguely as an "invariant subspace"; it should state the distinct-root condition and distinguish algebraic multiplicity from nullity.

### Foundations qualification

`L_k` itself is a linear subspace and is exactly closed under superposition. Nonclosure enters only after intersecting it with the demand that the **initial state be product**. Therefore the sentence in `main.pdf` that non-superposition closure "arises directly from the generalized-eigenvalue construction" is too strong. The accurate claim is:

> For a regular pencil with at least two distinct roots, the product boundary-compatible subset is not additive, although its full pole-preimage subspace is linear. Identifying this product subset with the physically realizable global state set is an additional hypothesis.

Also avoid proving nonclosure using normalized states; normalized states are trivially not closed under arbitrary addition or scaling. State the result for nonzero cones/rays.

## 6. Haar/SU(2) covariance and exact isotropy

### The covariance proof is valid, with one direction correction

For `R in SU(2)` let `U_R=U(R tensor I)`. If `Xi_0(U)` is the outcome-0 projective root multiset, then

```math
L_{0,U_R}(q)=L_{0,U}(Rq),
\qquad
\Xi_0(U_R)=R^{-1}\Xi_0(U).
```

Right Haar invariance therefore implies

```math
\Xi_0(U)\overset{d}=R^{-1}\Xi_0(U),
```

which is rotational invariance on the Bloch sphere. `main.pdf`, Eqs. (25)-(26), has the correct block transformation and Möbius map, but should say explicitly that the root set transforms by the inverse map.

### Theorem 4 (the Haar root process is exactly spherical)

The source draft says the Haar block pencil is "not literally" a pair of independent Ginibre matrices. The blocks are correlated, but their **generalized roots are exactly** the complex spherical ensemble.

For the forward outcome-0 pencil, the adjoint block row

```math
Q=\begin{pmatrix}C^\dagger\\D^\dagger\end{pmatrix}
```

is a Haar Stiefel frame. Hence in distribution

```math
Q=\begin{pmatrix}G_0\\G_1\end{pmatrix}
(G^\dagger G)^{-1/2},
```

with independent complex Ginibre `G_0,G_1`. Taking adjoints gives

```math
C+zD=(G^\dagger G)^{-1/2}
(G_0^\dagger+zG_1^\dagger).
```

The common invertible left factor does not change generalized roots. Thus the affine joint density is the complex spherical-ensemble density

```math
p(z_1,\ldots,z_d)\propto
\prod_{i<j}|z_i-z_j|^2
\prod_{j=1}^d(1+|z_j|^2)^{-(d+1)}.
```

Its one-point plane intensity is

```math
\rho^{(1)}(z)=\frac d\pi(1+|z|^2)^{-2},
```

equivalently `d/(4 pi)` per unit solid angle on `S^2`. This is exact for every `d`, not merely asymptotic.

The same exact reduction applies to the production pencil `(C,A)` because the first block column `(A^T,C^T)^T` is Haar Stiefel and its common invertible right factor cancels.

### What isotropy does and does not imply

Defensible:

- the ensemble root process has no preferred Bloch axis;
- the ensemble one-point intensity is exactly uniform at every `d`;
- the second outcome is the exact antipodal image of the first, so its one-point intensity is also uniform;
- the ratio of the two ensemble intensities is `1/2`.

Not established by symmetry alone:

- a single finite-`d` realization is uniform;
- a quantitative concentration rate or covering-radius law;
- independence of the two outcome clouds (they are deterministically antipodal);
- equivalence of Haar dynamics with finite-time local chaotic Hamiltonians or finite-depth random circuits;
- that "complexity" in every reasonable sense is insufficient.

The sharp conceptual statement is:

> Haar-distributed global propagators cannot select a projective measurement axis at the ensemble one-point level; their exact special-state root process is rotationally invariant. Therefore Haar genericity is not, by itself, a mechanism for a fixed-axis Born dipole.

## 7. Hostile foundations assessment

### 7.1 No definite-outcome theorem

The calculation shows that selected product boundary states exist. It does not show that a generic prepared state dynamically becomes one record. The final factorization is enforced by a two-time compatibility condition. Calling this "collapse" must remain operational and qualified.

### 7.2 No physical root-selection measure

Algebraic roots and their multiplicities are not probabilities. A probability law requires a measure over:

- qubit coordinates;
- detector null rays, including `CP^{g-1}` fibers at degenerate roots;
- apparatus microstates within a macroscopic ready sector;
- times or stopping rules if `t` is scanned;
- disorder/Hamiltonian realizations if those are averaged.

Equal algebraic counting is a convention until a preparation/selection mechanism derives it. Consequently a root-count ratio that resembles `cos^2(theta/2)` is a **Born-like geometric statistic**, not a derivation of Born probabilities.

### 7.3 Generic roots correlate the input qubit with detector microstate

For a regular pencil, the same detector vector cannot support two distinct qubit roots for the same outcome; otherwise both blocks share a kernel and the pencil is singular. Thus different qubit roots generically require different detector microstates.

An ordinary measurement is expected to accept an arbitrary qubit state with one macroscopically fixed apparatus-ready condition. The present construction instead supplies special global pairs `(q_j,eta_j)`. Without a large ready macro-subspace and a dynamics/measure that samples the required `eta_j` independently of deliberate qubit preparation, the proposal risks assuming a preparation correlation of the kind it is meant to explain.

### 7.4 Pole factorization is not a detector record

The condition only puts the qubit at `|0>` or `|1>` and leaves an arbitrary detector factor. It does not establish that outcome detector states are:

- macroscopically distinguishable;
- stable for a time interval;
- redundant across fragments;
- robust to perturbations;
- orthogonal or even well separated between labels.

Instantaneous zero entanglement is therefore not yet measurement-like record formation.

### 7.5 No quantum arrow of time is derived

The unitary algebra and its product-boundary solutions are time-reversal symmetric. The arrow enters through the imposed ready/final boundary conditions and any future coarse-graining or record stability. The arrow-of-time frame is excellent motivation, but the paper must say it formulates a candidate boundary-state loophole rather than deriving an emergent arrow.

### 7.6 The readout axis is inserted, not derived

The block decomposition chooses `|0>,|1>`. Haar covariance shows why a Haar ensemble cannot prefer it. A structured Hamiltonian can break rotational symmetry, but the paper must identify the physical coupling/readout algebra that selects the axis rather than treating a post hoc coordinate choice as measurement-axis emergence.

### 7.7 The standard linearity obstruction is not evaded by algebra alone

The standard measurement argument uses superposed qubit inputs with the same apparatus-ready state. The mathematical special set is non-additive because of a product constraint and input-detector correlations. The physical evasion requires a law saying why only that non-additive set is realizable. That law is explicitly absent.

## 8. Claim-strength matrix

| Candidate claim | Audit status | Referee-safe formulation |
|---|---|---|
| Forward pole compatibility reduces to two detector-size pencils | **Established** | State exact block convention and homogeneous equations. |
| `d` roots per outcome | **Established only for regular pencils, algebraic multiplicity** | Add antipodal pairing: `d` projective coordinates plus labelled antipodes. |
| Up to `2d` independent special states | **False/misleading** | The two outcome root multisets are deterministically antipodal. Detector rays may still differ. |
| Special set is not superposition closed | **Established generically for the product intersection** | Require a regular pencil with at least two distinct roots; distinguish from the linear pole-preimage subspace. |
| Nonclosure follows from unitary dynamics alone | **False** | It follows from intersecting a linear preimage subspace with the product-state cone; physical restriction is postulated. |
| Haar point process is isotropic | **Established exactly** | In fact the root law is exactly the complex spherical ensemble. |
| Haar outcome fraction is `1/2` | **Established at ensemble-intensity level** | Do not conflate ratio of intensities with a finite-realization local ratio or physical probability. |
| Haar finite clouds become uniform | **Unproved here** | Requires discrepancy/concentration/covering-radius analysis. |
| Generic randomness/complexity cannot measure | **Overbroad** | Haar global propagators cannot select a fixed axis at ensemble one-point level. |
| Production numerics compute the source PDF's forward pencils at the same `t` | **False** | They compute fixed-input-pole separable outputs; bridge to forward preimages uses `U^dagger`. |
| Root density yields Born probability | **Not established** | Call it a Born-like multiplicity-weighted root-count statistic. |
| Construction produces definite records | **Not established** | It produces exact pole-factorizing boundary states. |
| Construction explains the arrow of time | **Not established** | Arrow of time is motivation and a target for record/coarse-graining dynamics. |

## 9. Manuscript corrections required before theorem-level submission

1. Replace the two-independent-cloud narrative by the exact antipodal theorem and its complementary-minor proof.
2. Count `d` projective roots plus antipodal label images; continue to say each outcome pencil has `d` roots counted with algebraic multiplicity. Do not call the coordinates statistically independent.
3. Reduce the full-sphere Born diagnostic to one root density and its antipode. Enforce/check odd parity of `a(Omega)` and report `ell=1` versus odd `ell>=3` power.
4. Separate the source forward pencils from the production `(C,A)` pencil in the main text, not only the Supplement.
5. State the `U^dagger`/negative-time bridge and the additional real-Hamiltonian condition used to transfer polar data between `+t` and `-t`.
6. Use homogeneous QZ data throughout. Remove pseudoinverse-derived roots from theorem-supported datasets.
7. Replace "the dynamics generates a non-superposition-closed physical set" with the precise Segre-intersection statement and label the physical-state restriction as a hypothesis.
8. Call every Born comparison a geometric root-count statistic unless a preparation measure is supplied.
9. Add a fixed-ready-state/ready-subspace criterion and detector-record criterion to `RESULTS_NEEDED.md`.
10. Keep the arrow-of-time language as the motivating question; do not present a time-asymmetry theorem.

## 10. Strongest defensible analytical claims

The following claims should survive a hostile mathematical referee:

1. **Constructive reduction.** For any finite qubit-detector unitary, exact product inputs reaching a specified qubit pole are precisely the projective nulls of one detector-size homogeneous matrix pencil.
2. **Antipodal duality.** Unitarity pairs the two outcome root multisets exactly by Bloch antipodes, including algebraic multiplicity. A regular detector-dimension-`d` problem has `d` projective coordinates and their outcome-labelled antipodes; no statistical independence is implied.
3. **Regular/singular dichotomy.** A regular pencil has exactly `d` roots on `CP^1` counted algebraically; repeated roots, nontrivial nullity fibers, infinity, and singular-pencil continua are distinct cases that the homogeneous formulation resolves.
4. **Haar null model.** For Haar `U(2d)`, the root process is exactly the complex spherical ensemble, with uniform one-point intensity `d/(4 pi)` on the Bloch sphere at every `d`. The paired outcome cloud is its deterministic antipode.
5. **Geometric non-additivity.** For a regular pencil with at least two distinct roots, the product boundary-compatible set is not additive, although the full pole-preimage subspace is linear. Treating this set as physically realizable is an extra foundations hypothesis.
6. **Production bridge.** The repository's `(C,A)` roots enumerate separable outputs from a fixed pole input; the same roots for `U^dagger` enumerate forward preimages of a pole. This is an exact time-direction bridge, not an identity of the two same-time problems.

## 11. Source/evidence map

- Source research map: `C:\Users\matan\Downloads\main.pdf`, especially pp. 8-12 and 29-30.
- Production relative-evolution definition and antipodal construction: `collapse/analysis.py`.
- Born/reflection and azimuthal diagnostics: `collapse/born.py`.
- Homogeneous QZ implementation: `collapse/relative_evolution_pencil.py`.
- Projective unit tests: `tests/test_relative_evolution_pencil.py`.
- Haar numerical driver: `examples/haar_random_unitary.py`.
- Relative-unitary/weak-coupling analytical bridge: `collapse/relative_unitary_theory.py` and `tests/test_relative_unitary_theory.py`.
- Existing project self-audit recognizing the forward/production mismatch: `reports/prl_unitary_collapse_2026-08-14/AUDIT.md`.
- Existing project skeleton with the exact Stiefel-to-spherical reduction for the production pencil: `reports/prl_unitary_collapse_2026-08-14/main.tex` and `supplement.tex`.

## Bottom line for the Letter

The best theory paper is not "unitarity derives collapse and Born's rule." It is:

> Pole-factorizing boundary states of a finite qubit-detector unitary form an exactly enumerable projective root process. Unitarity imposes an unrecognized antipodal outcome duality, while Haar dynamics yields the exact spherical ensemble and therefore cannot select a fixed measurement axis. Structured many-body dynamics can then be tested against the sharply defined requirement that the odd root-asymmetry field be dominated by an `ell=1` Born dipole.

This is a publishable mathematical-many-body program if the manuscript is explicit that root counting is not yet probability and that the physical selection/ready-state/record mechanism remains open.

## 12. Integration and compiled-PDF audit (August 14, 2026)

The current `prl_draft/main.tex` and `prl_draft/supplement.tex` were checked against the theorems above and compiled with MiKTeX. Both compile with resolved citations and cross-references to a four-page Letter and a nine-page, single-column Supplement. The following theory-facing corrections were integrated:

- the repository Hamiltonian's overall minus-sign convention is now used in both documents;
- the production factorization is explicitly restricted to finite roots;
- the forward/production time-direction bridge is stated in the Letter and proved in the Supplement;
- the Haar statement now uses the normalized ensemble intensity fraction rather than an ambiguous finite-cloud ``outcome fraction'';
- a direct `SU(2)` covariance argument supplements the exact spherical-ensemble reduction;
- the complementary-minor proof explicitly chooses a normalized homogeneous representative;
- the generalized-eigenpair sign convention and homogeneous residual are explicit;
- statistically misleading uses of ``independent roots'' were replaced by ``projective roots'';
- the Hamiltonian and polar-score equations were reflowed to remove two-column overfull boxes, and the construction diagram was separated to eliminate overlap.

The unresolved scientific blockers remain unchanged: no physical preparation/selection measure, no common apparatus-ready sector, no stable/redundant record demonstration, and no production-scale homogeneous-QZ conditioning audit. These are not typesetting caveats; they delimit the actual theorem.
