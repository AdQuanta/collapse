# Gleason/Born Hamiltonian classification

Current evidence report, 2026-08-15. This is a living research report. It
records completed analytical/numerical results and labels every unperformed
decisive calculation explicitly. It does not identify algebraic root counting
with an operational probability measure.

## 1. Question and logical separation

The dynamical chain studied here is

```math
H\longrightarrow U(t)\longrightarrow
\text{projective matrix-pencil roots}\longrightarrow a(\Omega)
\longrightarrow\{P_\ell\}.
```

It is separate from the probability-assignment chain

```math
\text{positive, normalized, additive, noncontextual assignment}
\longrightarrow\text{trace rule}.
```

Gleason-type results constrain the second chain; they do not classify
Hamiltonians. The present program asks whether dynamics generates geometric
and composition/context properties compatible with that second chain. No
physical preparation or root-selection measure has yet been derived.

## 2. Block and root conventions

With the central qubit first,

```math
U=\begin{pmatrix}A&B\\C&D\end{pmatrix}.
```

Production data solve the fixed-input-pole problem

```math
C v=\lambda A v,
```

and map a finite root to

```math
q(\lambda)\propto(1,\lambda),\qquad
\mathbf r(\lambda)=
\frac{(2\Re\lambda,2\Im\lambda,1-|\lambda|^2)}{1+|\lambda|^2}.
```

The same-unitary forward pole-preimage pencils are

```math
(C+zD)\eta=0,\qquad(A+zB)\eta=0.
```

The production cloud of `U(t)` is the forward outcome-0 cloud of
`U(t)^dagger=U(-t)`. For a real symmetric Hamiltonian, the same-time forward
cloud is obtained from production by azimuthal reflection
`lambda -> conj(lambda)`. This bridge and the two-forward-label antipodal
pairing are covered by executable tests, including a small matched ring.

Homogeneous generalized eigenvalues `(alpha,beta)` obey

```math
\beta C v=\alpha A v,
```

and represent the qubit ket `(beta,alpha)`. Thus `beta=0` is a legitimate
south-pole/infinite affine root, while `(alpha,beta)=(0,0)` is indeterminate
and warns of singular-pencil structure.

## 3. Full-sphere definitions

The exact label relation is

```math
\rho_1(\Omega)=\rho_0(-\Omega).
```

Define

```math
a(\Omega)=\frac{\rho_0(\Omega)-\rho_1(\Omega)}
{\rho_0(\Omega)+\rho_1(\Omega)}.
```

Then `a(-Omega)=-a(Omega)`, so only odd spherical harmonics are physical in an
exactly paired analysis. For target axis `n`, the Born field is

```math
a_B(\Omega)=\hat{\mathbf n}\cdot\mathbf r(\Omega).
```

The primary diagnostics are

```math
\mathcal L_{\ge3}=
\frac{\sum_{\ell=3,5,\ldots}\sum_m|a_{\ell m}|^2}
{\sum_{\ell=1,3,5,\ldots}\sum_m|a_{\ell m}|^2},
```

```math
\mathbf d=\frac{3}{4\pi}\int a(\mathbf r)\mathbf r\,d\Omega,
\qquad \eta=|\mathbf d|,
\qquad F_{\rm axis}=\hat{\mathbf d}\cdot\hat{\mathbf n},
```

and

```math
\epsilon_{\rm anti}=
\left[\frac{\int|a(\Omega)+a(-\Omega)|^2d\Omega}
{\int|a(\Omega)|^2d\Omega}\right]^{1/2}.
```

The reported `epsilon_B` in the common CSV is the total-root-density-weighted
RMS of `a-n.r`. Area-normalized and relative-L2 variants are retained in the
per-run manifests.

The common table also records a direct, division-free stereographic density
ratio residual.  For the target axis `n`, Born compatibility requires

```math
\rho_0(-\mathbf r)(1+\mathbf n\cdot\mathbf r)
=\rho_0(\mathbf r)(1-\mathbf n\cdot\mathbf r).
```

For `n=z` and `lambda=q_1/q_0`, this is equivalent away from the poles to
`rho_0(-Omega)/rho_0(Omega)=|lambda|^2`.  The implementation normalizes the
weighted L2 norm of the difference by that of the sum, avoiding division by
zero at poles or empty single-label cells.  An analytic cell-center density
control gives residual below `1e-15`.

### Estimator contract

Root densities are currently estimated by an unsmoothed equal-area histogram
uniform in `(mu=cos(theta),phi)`. No full-sphere harmonic result is emitted if
any cell is empty, unless an explicitly recorded regularization is requested.
The modern harmonic estimator is a weighted least-squares fit on cell centers.
It exactly recovers a retained band-limited field on a full-rank grid.

The older manuscript used midpoint quadrature. An analytic control showed
that midpoint quadrature on a `16 x 8` grid falsely assigns approximately
0.170 higher-odd leakage to an exact dipole. It is therefore retained only as
a labeled legacy reproduction, not used for the modern low-resolution size
comparison.

An estimate `eta>1` is possible for a bounded but non-Born asymmetry field and
also through finite-bin noise. It is reported as oversharp/non-ideal, not
silently clipped to one.

The direct density-ratio residual is deliberately stricter than the
asymmetry/harmonic fit and is sensitive to finite empirical occupancy. In the 20
fully covered legacy matched-ring rows it ranges from `0.561` to `0.723`
(median `0.658`), despite substantially smaller asymmetry residuals.  This is
not a contradiction: the asymmetry constrains a ratio after combining both
labels with total-density weighting, whereas the cross residual tests the
unsmoothed single-label density and effectively emphasizes squared total
density. For the strongest `N=16`, `t=10^4` cloud it decreases from `0.602` to
`0.538` to `0.526` on the `24 x 12`, `36 x 18`, and `48 x 24` grids. The
resolution dependence is real, but the persistent order-one value is direct
evidence that the finite cloud does not satisfy the stronger cellwise density
criterion, especially in high-density regions. Density-estimator and size
convergence are still required before assigning an asymptotic interpretation.

## 4. Generalized-eigenvalue validation

The reusable QZ path now records:

- homogeneous `(alpha,beta)` pairs;
- finite, infinite, and indeterminate classifications;
- right and left normalized homogeneous backward residuals;
- denominator rank, smallest singular value, and condition number;
- finite-`lambda` or inverse-coordinate local condition estimates;
- optional SVD rank/nullity audits at selected roots;
- sampled numerical regularity warnings;
- projective duplicate clusters for manageable root counts.

Pairwise duplicate work is skipped above a declared size threshold. A sampled
full-rank pencil value numerically certifies regularity; failure at the sampled
values is a warning, not an exact Kronecker-form proof of singularity.

Focused projective/QZ tests currently pass for finite roots, exact infinity,
common-nullspace indeterminacy, scaling invariance, repeated roots,
representative nullity, left/right residuals, sector reconstruction, the
production/forward bridge, and strict QND.

## 5. Reproduction of the strongest matched-field ring

The exact audited Hamiltonian is the single-pixel ring with repository-wide
minus signs and

```math
h_{z0}=h_z=0.1,\quad J=1,\quad J_{pm}=J_y=0,
\quad J_x^{source}=0.01,
\quad J_x^{edge}=0.01/\sqrt N,
```

with the central qubit coupled by XX to every detector spin. The trusted
`N=16`, `t=10^4` affine-root file has SHA-256
`e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59`
and contains 65,536 finite roots.

**VERIFIED NUMERICALLY:** the modern post-processor reproduces the stored
polar score `S_born=0.7856819129539223` exactly at its original settings. At
the legacy `36 x 18` resolution it also reproduces the prior midpoint
`P1/Podd=0.9818030721` and total-density-weighted Born RMS `0.0890867410`.

The modern harmonic estimates are:

| grid `(phi x mu)` | coverage | `L>=3` | `P1/Podd` | `eta` | `F_axis` | weighted Born RMS | density-ratio residual |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `24 x 12` | 1 | 0.01104 | 0.98896 | 1.14594 | 1 within `2e-14` | 0.09039 | 0.60169 |
| `36 x 18` | 1 | 0.01160 | 0.98840 | 1.14506 | 1 within `2e-14` | 0.08909 | 0.53782 |
| `48 x 24` | 1 | 0.01324 | 0.98676 | 1.14149 | 1 within `6e-13` | 0.11539 | 0.52632 |

The first two grids agree closely; the finer grid has larger sampling noise.
This supports a strongly axis-aligned, dipole-dominated field with resolved
nonzero higher odd content and an oversharp dipole estimator. The direct
density-ratio test is much less favorable and remains order one as the grid is
refined. It is not an exact Born field and does not establish an operational
probability law.

The stored affine roots do not contain homogeneous QZ pairs or propagator
blocks. Therefore their publication-level QZ status remains
**HPC CALCULATION REQUIRED** for large N. The QZ implementation and a small
matched-ring direct validation are complete locally.

## 6. Matched-ring finite-size and time behavior

All 24 trusted size/time files (`N=11,...,16`, four times from `10^3` through
`10^6`) reproduce their stored polar scores to below `1e-12`. On the common
modern `16 x 8`, `l_max=7` estimator, all four `N=12,...,16` rows per size have
full coverage; the four N=11 rows cover only 0.906--0.938 and are not assigned
harmonic metrics.

| N | median polar `S_born` | median `L>=3` | median `P1/Podd` | median `eta` | median weighted Born RMS |
|---:|---:|---:|---:|---:|---:|
| 11 | 0.192 | unavailable | unavailable | unavailable | unavailable |
| 12 | 0.411 | 0.496 | 0.504 | 1.119 | 0.167 |
| 13 | 0.571 | 0.380 | 0.620 | 1.155 | 0.130 |
| 14 | 0.715 | 0.033 | 0.967 | 1.145 | 0.119 |
| 15 | 0.788 | 0.114 | 0.886 | 1.149 | 0.114 |
| 16 | 0.807 | 0.029 | 0.971 | 1.155 | 0.111 |

**SUPPORTED NUMERICALLY:** the polar and weighted-residual trends improve over
this range and N=14/N=16 are strongly dipole dominated. The odd-harmonic trend
is nonmonotonic at N=15 and only four deterministic times are available.
No asymptotic scaling law is currently justified.

## 7. Strict-QND no-go

Consider

```math
H=H_Q+H_D+Z_Q\otimes V_D,\qquad[H,Z_Q]=0.
```

In the pointer basis,

```math
U(t)=\begin{pmatrix}A&0\\0&D\end{pmatrix}.
```

For the production pencil, `C=0`, so

```math
0=\lambda A v.
```

Since `A` is unitary, all `d` algebraic roots are `lambda=0`: the north pole.
The forward outcome-0 pencil has the same north-pole roots, while the
outcome-1 pencil has `d` infinite roots: the south pole.

**PROVED ANALYTICALLY:** strict pointer-QND evolution can preserve/amplify a
readout basis but cannot generate a nontrivial dense Born root cloud in this
matrix-pencil mechanism.

**VERIFIED NUMERICALLY:** an interacting ring with detector ZZ/exchange,
detector transverse and longitudinal fields, and central ZZ/ZX coupling was
tested for detector `N=2,...,6`. In every case:

- the relative commutator norm and off-diagonal propagator blocks were exactly
  zero in the constructed representation;
- all production roots were exactly at the north pole and all second-label
  roots at the south pole;
- QZ left/right residuals were zero;
- the repeated production root had nullity `2^N`;
- only 2 of 128 equal-area cells were physically occupied after pole azimuth
  canonicalization.

The detector in this control is not noninteracting; the no-go follows from
central-pointer conservation, not from the absence of detector mixing.

## 8. Uncoupled-spectator composition consistency

Let

```math
U'=U_{QD}\otimes U_A
```

in ordering `Q tensor D tensor A`. Every qubit-first block tensors by the same
invertible `U_A`, so

```math
\det[(C-\lambda A)\otimes U_A]
=\det(C-\lambda A)^{\dim A}\det(U_A)^{\dim D}.
```

**PROVED ANALYTICALLY:** every projective root is repeated by `dim(A)`, but the
normalized empirical root measure, normalized labelled densities, asymmetry,
dipole, and harmonic fractions are invariant. Thus normalized algebraic root
geometry passes the narrowly defined uncoupled tensor-factor composition test.

**VERIFIED NUMERICALLY:** on the hashed `N=16`, `t=10^4` matched roots,
spectator dimensions 1, 2, 3, 4, and 8 scaled the raw count from 65,536 to
524,288. The largest composition error was `8.8e-17`; density, dipole, and
harmonic discrepancies were at roundoff.

This does not establish general noncontextuality. Splitting detector levels,
adding inactive basis states without a tensor-product unitary, changing a
ready macrosector, or coupling the added system can alter the pencil and
remain untested.

Two further context statements are now exact:

1. **PROVED ANALYTICALLY and VERIFIED NUMERICALLY:** a detector-basis
   permutation conjugates every pencil block by the same permutation and
   leaves the projective root multiset invariant.
2. **PROVED ANALYTICALLY and VERIFIED NUMERICALLY:** equal algebraic root
   counting is not invariant under a nonuniform direct-sum refinement. If
   `U_1` and `U_2` act on two detector microsectors, the direct-sum detector has
   the union of their root multisets. Replacing `U_1 direct_sum U_2` by
   `U_1 direct_sum U_1 direct_sum U_2` changes normalized equal-root weights
   from `1/2,1/2` to `2/3,1/3`, even though the duplicated microsector has
   identical dynamics.

The second result is a counterexample to interpreting unweighted algebraic
root multiplicity itself as a generally refinement-noncontextual probability
measure. Declaring the two refinements physically equivalent still requires a
preparation/coarse-graining rule, but root counting alone does not supply one.
The exact source data and publication figure are
`figures/hamiltonian_classification_20260815/source_data/context_refinement_counterexample.csv`
and `context_refinement_counterexample.{png,pdf}` in the parent directory.

## 9. Transverse mixing

The QND endpoint establishes that some central-qubit noncommutation is
necessary for nontrivial coverage within the tested mechanism. It does not yet
establish that one transverse channel is sufficient or that an intermediate
optimum exists.

Older scans contain transverse-coupling variations, but they were ranked by
polar diagnostics and were not generated with the modern full-sphere/QZ
pipeline. A controlled `g_x` scan from the exact QND endpoint, with fixed
detector structure and explicit time separation, is **HPC CALCULATION
REQUIRED** after a small local manifest smoke test.

## 10. Matched-field detuning

Existing resonance studies show that matching/band resonance can broaden
polar support without guaranteeing Born-like azimuthal geometry. The positive
matched-ring sequence is therefore not explained by resonance alone.

The saved `N=14`, `t=10^6`, `hz0=0.1`,
`hz in [0.0999,0.1001]` Sobol campaign now provides a strict common-sphere
test over 400 configurations. Only 52 cover every cell of the `16 x 8`
equal-area grid. Within those resolved cases:

- `L_{>=3}` ranges from `0.0255` to `0.99997` (median `0.366`);
- `eta` ranges from `1.098` to `1.414` (median `1.253`);
- fixed-`+z` axis fidelity is at least `0.99999999999`;
- density-weighted `epsilon_B` ranges from `0.1300` to `0.1582`;
- the unsmoothed direct density-ratio residual ranges from `0.834` to `0.998`
  (median `0.944`).

Thus a matched field band and complete angular coverage preserve the intended
axis but are not sufficient for a pure or sharp Born dipole. Across the 52
resolved configurations, absolute source detuning correlates with the legacy
polar score (`rho=-0.457`, descriptive FDR `q=0.0066`) but not significantly
with higher-harmonic leakage. No scanned Hamiltonian feature has a resolved
association with `L_{>=3}` after within-outcome FDR correction (all descriptive
`q>=0.493`). The apparent resonance effect is therefore polar, not yet a
demonstrated higher-harmonic-suppression mechanism.

Coverage over all 400 points is most strongly associated with smaller
`Jpm/J` (`rho=-0.858`), while within the resolved subset larger source `Jx`
correlates with worse `epsilon_B` (`rho=0.664`, `q=8.0e-7`) and larger
oversharpness (`rho=0.625`, `q=7.4e-6`). These are conditional associations in
a deterministic Sobol design, not disorder-ensemble uncertainty or causal
effects.

The direct ratio residual is most strongly associated with absolute source
detuning (`rho=0.610`, descriptive FDR `q=1.6e-5`). Because this residual is
also strongly affected by sparse single-label bin occupancy, the relation is
a useful density-level falsification signal but is not yet evidence for a
continuum resonance law.

A controlled scan of

```math
\delta=(h_{z0}-h_z)/J_x
```

with homogeneous QZ diagnostics across N and time has not yet been completed.
The `N=14` saved-root result above rules out matching as a sufficient condition,
but the causal and scaling status remains **HPC CALCULATION REQUIRED**.

## 11. Second transverse channel and multiaxis coupling

The code supports independent central XX and YY channels (`Jx`, `Jy`) plus
ZZ, ZX, and exchange channels. Small-N legacy screens are not sufficient to
classify the effect of `Jy/Jx`. Whether a second noncommuting channel rotates,
weakens, or destroys the selected dipole remains **HPC CALCULATION REQUIRED**.

## 12. Detector scrambling and spectral mechanisms

The repository supports transverse detector fields, exchange, anisotropic
XX/YY terms, second-neighbour rings, disorder, and random graph families. It
also contains symmetry-resolved adjacent-gap and matrix-element/gap tools.

Current evidence does not show that chaos, exact degeneracy, or heavy tails
are sufficient for Born geometry. Prior resonance and degeneracy controls
contain counterexamples. A correlation analysis is meaningful only after all
root metrics are recomputed with a common estimator and spectra are kept in
irreducible symmetry sectors. Causal scrambling claims are currently **NOT
SUPPORTED**.

## 13. Cross-Hamiltonian comparison

The common CSV presently contains 2,468 rows in ten named classes:

1. matched-field collective-XX ring (24 size/time rows);
2. strict-QND interacting ring (five sizes);
3. Erdos-Renyi detector graphs (346 completed realizations);
4. Watts-Strogatz detector graphs (334 completed realizations);
5. Barabasi-Albert detector graphs (347 completed realizations);
6. random-regular/expander detector graphs (339 completed realizations).
7. nearest-neighbour `hz0=0` Sobol rings (329 completed configurations);
8. second-neighbour `hz0=0` Sobol rings (343 completed configurations);
9. narrow matched-band `hz0=0.1` Sobol rings (400 configurations).
10. one locally smoke-tested `N=8` Haar-unitary null (the manifest contains
    five additional Haar points for Zeus).

Both `hz0=0` Sobol ring families obey the same central-X theorem as the random
networks. Neither adding second-neighbour ZZ/exchange couplings nor varying
`J,hz,Jpm,Jx,J2,Jpm2` over the saved design creates full-sphere support:
median/common maximum coverage is `0.4375`, and all roots remain on the `y-z`
great circle to numerical precision (`max |r_x| < 3.04e-7`).

The 1,366 network rows were recomputed from independently stored blue/red
Bloch coordinates, not from plotted images. Their median legacy polar
`S_born` values are respectively `0.174`, `0.183`, `0.165`, and `0.172`; each
family nevertheless contains isolated polar scores near `0.8`. On the common
`16 x 8` equal-area sphere, however, median coverage is only `0.25` for every
family (ranges: Erdos-Renyi `0.0625--0.3125`, Watts-Strogatz
`0.0625--0.25`, Barabasi-Albert `0.0625--0.34375`, expander
`0.0625--0.4375`). Therefore none admits an unregularized full-sphere harmonic
classification at this resolution. This is an important negative control:
a high one-dimensional polar score does not establish Born-compatible
full-sphere geometry.

The restriction is structural, not merely sparse sampling. All 1,366 clouds
obey `max |r_x| < 1.27e-7` (median maximum `1.93e-9`): they lie on the `y-z`
great circle. **PROVED ANALYTICALLY:** for these `hz0=hx0=0`, central-X-only
models,

```math
H=I_Q\otimes H_D+X_Q\otimes V_D,
\qquad [H,X_Q]=0,
```

so in the central-Z basis `U=[[A,C],[C,A]]`. Unitarity gives
`A^dagger C+C^dagger A=0`. For every regular finite production root
`Cv=lambda Av`, multiplication by `v^dagger A^dagger` implies
`Re(lambda)=0`; zero and infinite roots also lie on the same great circle.
Thus changing only detector graph connectivity cannot create two-dimensional
full-sphere support in this symmetry class. This theorem is independently
verified by a random-matrix unit test.

These saved network files contain affine roots and legacy validation but not
homogeneous QZ pairs. Their common-table rows are explicitly marked not QZ
audited. A decisive comparison requires rerunning selected realizations with
homogeneous QZ and adding an azimuth-generating/non-real coupling if the
physical hypothesis calls for genuinely two-dimensional sphere support.

The star/disordered, Ising-like, XY/local-edge, random-network, strong
scrambling, and Haar controls have relevant legacy data or implementations,
but not yet a common full-sphere/QZ classification. Cross-family sufficiency
is **HPC CALCULATION REQUIRED** where raw roots cannot be post-processed.

The Haar ensemble remains an analytical null: its one-point root intensity is
rotationally invariant and therefore selects no fixed measurement axis at the
ensemble level. This does not supply a finite-realization concentration result
or a probability-selection mechanism.

The first explicit Haar smoke realization is fully covered and homogeneous-QZ
valid (maximum right/left residuals `3.26e-15`/`2.99e-15`, isometry residual
`6.76e-17`). It has `L_{>=3}=0.896`, `eta=0.0267`, axis fidelity `-0.694`, and
`epsilon_B=0.657`. This is **VERIFIED NUMERICALLY** for one finite realization
and behaves as the intended no-selected-axis, non-Born null; ensemble
concentration awaits the remaining seeds.

A 24-point local `N=6` screen was also completed for transverse strength,
matched-field detuning, `Jy/Jx`, and detector transverse field. Nearly every
point left empty equal-area cells, so the strict estimator correctly withheld
harmonic metrics instead of filling unobserved directions. The sole
full-coverage point (`Jx=0.3` before the documented `1/sqrt(N)` scaling) was
strongly non-Born (`epsilon_B approximately 0.661`, `L_{>=3} approximately
0.091`, `eta approximately 0.680`). This small-system screen is useful for
workflow validation and campaign design, not for a positive causal claim.

A restartable 149-point Zeus manifest now covers matched-QZ reproduction,
transverse scans, detuning scans, multiaxis scans, and detector-transverse-field
scans at `N=10,12,14`, plus 40 matched-field random-network controls at
`N=8,10` over five recorded graph seeds, identically parameterized ring
controls, eight explicit noninteracting-star/Ising-ring/XY-ring/XY-edge
architecture controls, and six Haar-unitary nulls. It is partitioned over a 20-element
PBS array. A local
`N=10` sector-resolved smoke point completed with maximum right/left pencil
residuals `3.35e-15`/`1.61e-15` and propagator isometry error `2.87e-15`;
coverage was only `0.75`, so harmonic metrics were again withheld. The Zeus
campaign has been prepared but not submitted.

The symmetry-broken network path was independently smoked at `N=8` for one
Erdos-Renyi realization: all 256 roots were determined, the maximum right/left
QZ backward residuals were `2.00e-15`/`1.78e-15`, and the pencil was regular at
the audited root. Coverage was `0.28125`, so no harmonic metrics were emitted.
This validates execution and provenance only; it is not evidence for or
against the `N=10` network comparison.

A separate restartable Zeus follow-up now selects the ten largest stored polar
`S_born` cases independently in each of the four network families and reuses
each exact saved `N=12` graph while scanning `hz0=0`, `hz0=hz`, and additive
offsets `+/-1e-4` and `+/-1e-3` around `hz`. This is a 240-run controlled
central-field intervention, not a claim that the selected `hz0=0` cases are
full-sphere Born-compatible. The campaign has been prepared and validated but
not submitted; production results remain **HPC CALCULATION REQUIRED**.

## 14. Disorder and uncertainty

No disorder-ensemble claim is made from roots within one pencil. Future
disordered comparisons must use independent recorded seeds and report
between-realization mean, median, spread, quantiles, and confidence intervals.
The clean matched sequence has deterministic time variation, not stochastic
error bars.

## 15. Current Hamiltonian classification

The strongest statement currently justified is:

- **PROVED ANALYTICALLY:** central pointer-QND conservation forces pole-only
  geometry, regardless of internal detector interaction/mixing.
- **SUPPORTED NUMERICALLY:** a preferred Z axis plus weak collective transverse
  XX coupling, exact qubit/detector field matching, and an interacting ring can
  produce a highly aligned, dipole-dominated finite-size root asymmetry.
- **NOT SUPPORTED:** unitarity, QND structure, interaction, resonance,
  degeneracy, heavy tails, or generic scrambling alone is sufficient.
- **INFERRED:** at least one central-qubit noncommuting channel is necessary to
  leave the QND poles in this model class. Necessity across every possible
  Hamiltonian representation is not proved.
- **CONJECTURAL:** controlled intermediate transverse mixing plus structured
  spreading is the distinguishing motif.
- **PROVED ANALYTICALLY:** normalized algebraic root geometry is invariant
  under a dynamically uncoupled tensor-factor spectator.
- **NOT SUPPORTED:** this narrow invariance is enough for Gleason
  noncontextuality. Equal algebraic root multiplicity is explicitly
  context-sensitive under nonuniform direct-sum microsector duplication.

## 16. Reproducible artifacts

- Repository map: `CODEBASE_MAP.md`.
- Common table: `hamiltonian_classification_results.csv`.
- Root conventions: `collapse/projective_roots.py`.
- Homogeneous audit: `collapse/relative_evolution_pencil.py`.
- Full-sphere diagnostics: `collapse/gleason_diagnostics.py`.
- Matched reproduction:
  `work/hamiltonian_classification_20260815/matched_ring_reproduction/`.
- QND validation:
  `work/hamiltonian_classification_20260815/qnd_no_go_validation/`.
- Composition validation:
  `work/hamiltonian_classification_20260815/composition_consistency/`.
- Network full-sphere adapter and table:
  `examples/aggregate_network_hamiltonian_classification.py` and
  `work/hamiltonian_classification_20260815/network_full_sphere/`.
- Sobol ring/second-neighbour/matched-band full-sphere tables and descriptive
  parameter relations:
  `work/hamiltonian_classification_20260815/sobol_ring_full_sphere/`.
- Local hypothesis screen:
  `work/hamiltonian_classification_20260815/local_hypothesis_screen_N6/`.
- Zeus dry run and smoke point:
  `work/hamiltonian_classification_20260815/zeus_campaign_dry_run/` and
  `work/hamiltonian_classification_20260815/zeus_campaign_smoke_haar_149point/`.
- Current publication figures and source data:
  `figures/hamiltonian_classification_20260815/`. Figure E is complete for the
  uncoupled tensor-factor theorem; the network great-circle no-go is an
  additional negative-control figure. Figure B now has a conditional `N=14`
  resolved-subset panel with explicit source data. Multi-N Figure B and the
  requested Figures A, C, and D remain **HPC CALCULATION REQUIRED** and must not
  be populated by regularizing incomplete angular support.
- Reproduction and aggregation entry points are under `examples/` and have
  focused tests under `tests/`.
- `examples/plot_zeus_hamiltonian_classification.py` is the completeness-gated
  Figure A--D builder for the 149-point manifest; it refuses partial or corrupt
  collections and saves the selected numerical source rows with each figure.
- `examples/analyze_zeus_spectral_relations.py` is the matching completeness-
  gated mechanism analysis. It computes detector gap ratios only inside exact
  graph-automorphism/Hamming-weight/spin-reversal sectors and keeps five-seed
  network uncertainty distinct from pooled descriptive correlations. It also
  processes the four physical-architecture controls; for the exactly
  noninteracting detector it reports within-sector spacing statistics as
  undefined rather than inventing spacings between degenerate symmetry blocks.

## 17. Highest-value unresolved calculations

1. Recompute selected matched points from propagator blocks with full
   homogeneous QZ provenance.
2. Controlled QND-to-transverse scan at fixed detector structure.
3. Matched-field detuning scan in `delta` across several N and independent
   saved times.
4. `Jy/Jx` multiaxis scan.
5. Symmetry-resolved scrambling comparison with common root estimators.
6. Cross-family replication and disorder realizations.
7. Context refinements more general than tensor-factor spectators.
8. A physical preparation/selection measure over root coordinates and
   detector null vectors.

No martingale diagnostic is currently defined because the repository has no
validated stochastic trajectory variable. Forcing one from deterministic root
sets would not answer the stated physical question.

## 18. Current answer to the final research question

**SUPPORTED NUMERICALLY, with exact no-go boundaries:** the strongest current
distinction is not “interacting,” “chaotic,” “decohering,” or “scrambling.” A
candidate Born-producing detector must first escape both strict pointer-QND
pole degeneracy and any conserved-central-axis constraint that confines roots
to a great circle. In the successful finite matched-ring examples it also
retains a preferred `z` axis while weak collective transverse coupling spreads
the roots over the sphere. Those ingredients generate coverage and alignment,
but the 400-point matched-band counterexamples show that they do not by
themselves suppress higher odd harmonics or drive `eta` to one.

Therefore the only presently reliable discriminator is the resulting
conditional-unitary/root geometry itself: low `L_{>=3}`, `eta` near one, stable
axis fidelity, small `epsilon_B`, and estimator-converged density relations.
No simpler microscopic Hamiltonian criterion has yet been established.
Moreover, unweighted algebraic root counting fails a direct refinement-
noncontextuality test, so even ideal geometry would not by itself provide the
missing physical outcome-selection measure. The causal cross-family and
finite-size discrimination is **HPC CALCULATION REQUIRED**; the complete
149-point Zeus campaign prepared here is the next controlled test.
