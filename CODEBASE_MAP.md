# Codebase map for the Hamiltonian-classification program

Date of audit: 2026-08-15  
Python target: 3.11  
Scope: active source, tests, configurations, Zeus orchestration, and the stored
evidence relevant to qubit--detector root geometry. Generated data were read
only; no prior result was modified.

## 1. Physical and computational flow

The active calculation has the following dependency chain:

```text
Hamiltonian specification
  -> NumPy or QuSpin operator construction
  -> full or symmetry-sector eigendecomposition
  -> U(t) block column (U00, U10) for a fixed input qubit pole
  -> projective pencil U10 v = lambda U00 v
  -> labelled antipodal Bloch roots
  -> polar/azimuthal or full-sphere density diagnostics
  -> parameter-family tables, figures, and Zeus checkpoints
```

This is the **Hamiltonian-dynamics chain**. It yields special product-boundary
root geometry. It does not, by itself, provide a preparation or root-selection
measure. Gleason-type probability assignments are a separate logical chain and
must not be used to classify a Hamiltonian without an additional physical
measure/postulate.

## 2. Mathematical convention used by production code

For the central qubit first in the tensor-product basis,

```math
U(t)=\begin{pmatrix}A&B\\C&D\end{pmatrix},
\qquad A=U_{00},\quad C=U_{10}.
```

The production fixed-input-pole problem solves

```math
C v=\lambda A v.
```

When `A` is invertible, this is the spectrum of `A^{-1}C`. A finite root maps
to the branch-0 qubit state

```math
|\phi_0(\lambda)\rangle
=\frac{|0\rangle+\lambda|1\rangle}{\sqrt{1+|\lambda|^2}},
\quad
\theta=2\arctan|\lambda|,\quad\phi=\arg\lambda.
```

The stored companion convention is `D1 = -conj(D0)` in the opposite affine
chart, producing the exact antipodal state

```math
|\phi_1\rangle
=\frac{-\lambda^*|0\rangle+|1\rangle}{\sqrt{1+|\lambda|^2}}.
```

The same-unitary **forward preimage** pencils are instead
`(alpha C + beta D) eta = 0` and `(alpha A + beta B) eta = 0`. Production at
`t` is the forward-pole construction for `U(t)^dagger = U(-t)`. These related
problems must not be silently identified at the same time. For a real
symmetric Hamiltonian, their polar radii agree and the azimuth is reflected.

## 3. Active reusable package (`collapse/`)

### Hamiltonian definitions

- `collapse/hamiltonians/base.py`: minimal generator contract; full-basis
  diagonalization fallback and sector-result schema.
- `collapse/hamiltonians/numpy_hamiltonians.py`: dense reference
  implementations. These are the small-system correctness baseline.
- `collapse/hamiltonians/quspin_hamiltonians.py`: sparse/sector-aware QuSpin
  implementations used for larger local and Zeus runs.
- `collapse/detector_graphs.py`: deterministic graph realization from an
  explicit `DetectorGraphSpec`; records seed, edge list, degree sequence, and
  Laplacian connectivity.
- `collapse/disorder.py`: uniform, Gaussian, and Lorentzian parameter disorder.

Implemented model families are:

1. Mixed-field periodic Ising chain,
   `-J sum Zi Zi+1 - hx sum Xi - hz sum Zi`.
2. Single-pixel detector: central qubit 0 plus a detector graph. Detector edges
   support ZZ (`J`), exchange (`Jpm`), independent XX/YY (`Jxx`, `Jyy`), and
   ring second-neighbour ZZ/exchange (`J2`, `Jpm2`). Central--detector edges
   support XX, YY, ZZ, ZX, and exchange (`Jx`, `Jy`, `Jz`, `Jzx`, `Jcpm`).
   Central and detector fields are independently selectable (`hx0`, `hz0`,
   `hx`, `hz`).
3. Dimerized single-pixel detector with non-overlapping detector dimers.
4. Two-pixel detector with opposite-sign central coupling to the two pixels.
5. Central-spin/star model with XX and ZZ central--satellite coupling.

Single-pixel detector connectivity includes chain, ring, all-to-all,
Erdos--Renyi, Watts--Strogatz, Barabasi--Albert, and random regular. `expander`
is only an alias for a random-regular candidate; expansion is not assumed
without checking the recorded spectral gap.

### Evolution and roots

- `collapse/analysis.py`: legacy/production block construction and direct
  `solve`/eigenvalue path; `DisentanglementAnalyzer` maps roots to qubit states.
  Its pseudoinverse fallback is useful descriptively but is not acceptable for
  theorem-level claims near a singular pencil.
- `collapse/relative_evolution_pencil.py`: current homogeneous generalized
  eigenvalue implementation. It preserves finite, infinite, and indeterminate
  projective pairs and reports block rank/conditioning and normalized right
  residuals. This is the correct base for the requested robust QZ diagnostics.
- `collapse/relative_evolution_sector.py`: aggregates the homogeneous pencil
  across symmetry sectors and validates column isometry. It fails closed if a
  proposed sector does not preserve the relative-evolution block problem.
- `collapse/relative_unitary_theory.py`: exact conditional-unitary/Cayley
  identities for `H = HD + g X_Q tensor V`, plus perturbative finite-time
  kernels.
- `collapse/relative_evolution_study.py`: reproducible studies of the relative
  evolution matrix and its spectral approximations.

The homogeneous module already handles infinity and residuals, but it does
not yet provide the full requested audit: left-eigenvector conditioning,
representative root nullities, regular/singular-pencil certification, and
duplicate/defective-root diagnostics remain to be added.

### Symmetry handling

QuSpin models expose reduced bases through `diagonalize_sectors()`.

- Clean rings can use detector cyclic-shift momentum sectors when central
  coupling is translation invariant. Those sectors are local to the
  relative-evolution pencil.
- Magnetization sectors are used when total `Nup` is conserved.
- Magnetization-parity sectors are used when single-spin flips are absent but
  pair flips are present.
- Dimerized and two-pixel models add spatial symmetries when their couplings
  preserve them.
- Generic random graphs have no assumed circular symmetry. Their largest valid
  internal sector is selected from conserved magnetization or parity when
  available.

Some Hamiltonian sectors mix the central-qubit slices needed by `(U00,U10)`.
They are valid for Hamiltonian diagonalization but not local pencil solves; the
code marks these `relative_evolution_local=False` and reconstructs exact
full-basis blocks. Level-spacing statistics must always be computed separately
inside irreducible sectors, never on a concatenated spectrum.

### Existing diagnostics

- `collapse/born.py`: polar reflected-density score `S_born`, radius-tail and
  reciprocal-envelope diagnostics, and azimuthal histogram statistics. These
  are screening diagnostics, not full-sphere probability laws.
- `collapse/spherical_harmonics.py`: accurate complex spherical-harmonic
  quadrature/projector. It is generic and tested, but currently lacks the
  domain-specific labelled-density/asymmetry interface.
- `collapse/level_spacing.py`, `collapse/graph_spectral_sectors.py`, and
  `collapse/graph_symmetry.py`: symmetry-resolved spectral statistics and graph
  automorphism support.
- `collapse/detector_gap_matrix.py`, `collapse/detector_resonance.py`,
  `collapse/degenerate_activation.py`: detector gaps, matrix elements, and
  near-degenerate activation diagnostics.
- `collapse/distribution_fit.py` and `collapse/wrapped_cauchy.py`: radial and
  folded phase-distribution models.

The requested full-sphere fields
`rho_0`, `rho_1`, `a=(rho_0-rho_1)/(rho_0+rho_1)`, the direct division-free
Born density-ratio residual, dipole vector/sharpness,
higher-odd leakage, axis fidelity, antipodal residual, and composition
consistency are not yet a reusable tested package. A manuscript-local
prototype exists in `prl_draft/scripts/build_figures.py`.

### Campaign and analysis services

- `collapse/single_pixel_atlas.py`, `collapse/anisotropic_sweep.py`, and
  `collapse/scaling_campaign.py`: clean-ring and anisotropic atlas services.
- `collapse/sobol_coupling_scan.py` and `collapse/zeus_sobol_array.py`:
  deterministic Sobol parameter points, resumable configuration directories,
  and PBS-array sharding.
- `collapse/ranked_born_campaign.py`, `collapse/network_ranked_followup.py`,
  and `collapse/network_resampled_scaling_campaign.py`: ranked follow-ups,
  graph resampling, and size scaling.
- `collapse/degeneracy_heavy_tail_campaign.py` and
  `collapse/relative_scale_campaign.py`: mechanism-specific campaigns.

## 4. Entry points, configuration, and Zeus

- `examples/` contains thin runners and post-processors. Current production
  entry points are the `run_*` scripts; `build_*`, `analyze_*`, and `plot_*`
  should remain post-processing only.
- `configs/` stores JSON campaign definitions. New scientifically meaningful
  scans should add a complete, versioned configuration here rather than hide
  parameter grids in a PBS file.
- `hpc/` contains PBS scripts, submission wrappers, restart/runbook utilities,
  and post-processing gates. Recent Zeus jobs use explicit array indices,
  per-configuration completion files, and unique `RUN_ROOT` values.
- `tests/` has focused coverage for NumPy/QuSpin agreement, connectivity,
  symmetry sectors, homogeneous QZ, atlas services, Sobol partitioning,
  restart behavior, and plotting data. Production-size jobs are not tests.

## 5. Stored evidence most relevant to this program

### Strongest current positive candidate

The strongest audited clean candidate is the matched-field ring

```math
h_{z0}=h_z=0.1,\quad J=1,\quad J_{pm}=J_y=0,
\quad J_x^{source}=0.01,
\quad J_x^{edge}=J_x^{source}/\sqrt N.
```

Trusted post-cutoff raw roots are under
`work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/`. For `N=11,...,16`
and `t=10^3,10^4,10^5,10^6`, the audited four-time median polar score rises
from approximately 0.192 to 0.807. This is finite-size numerical evidence,
not a convergence proof.

At `N=16`, `t=10^4`, the stored file contains 65,536 finite production roots.
The manuscript-local equal-area `36 x 18` analysis reports fixed-`+z` Born RMS
about 0.089 and dipole fraction about 0.982 of resolved odd power through
`ell=7`. These values are **derived numerical claims requiring independent
reproduction in the new reusable pipeline**, because the production run did
not store homogeneous QZ pairs, backward errors, or nullity diagnostics.

Primary provenance is recorded in `prl_draft/NUMERICAL_PROVENANCE.md` and
`prl_draft/figures/figure_manifest.json`; the raw N16, `t=10^4` SHA-256 is
`e467b5efa6a5b8b7e3e7333a06555007b629a26bbeac2b21cd3da27d88313d59`.

### Important negative controls and broader surveys

- `work/single_pixel_quspin_fresh_2026-07-12/` and the associated resonance
  reports: resonance broadens polar support but the clean model can remain
  azimuthally localized and non-Born.
- `work/expanded_hamiltonian_sweep_2026-07-16/` and
  `work/conjecture_candidate_campaign_2026-07-16/`: matched/detuned,
  multiaxis, disorder, dimerized, chain-end, and exchange screens at small N.
- `work/zeus_single_pixel_anisotropic_20260718_130606/`: large parameter grid
  over detector fields and ZZ/exchange strengths with multiple completed N.
- August 2026 Sobol ring, second-neighbour, and four random-network-family
  directories: broad parameter studies and ranked/resampled follow-ups.
  Rankings use legacy polar `S_born`. The 1,366 completed random-network
  configurations have now been passed through the common strict full-sphere
  coverage gate by `examples/aggregate_network_hamiltonian_classification.py`;
  none covers the full `16 x 8` grid, so harmonic metrics are withheld. Their
  saved affine roots do not contain the homogeneous pairs needed for a
  retrospective QZ audit.
- `proofs/`: a separate Lean/numerical heavy-tail core. It addresses a
  Cayley/tail mechanism, not the full Hamiltonian classification theorem.

Pre-July artifacts and files with only copied modification timestamps are
background, not empirical evidence, unless independently reproduced.

## 6. Manuscript/theory material

- `prl_draft/` and `reports/prl_unitary_collapse_2026-08-14/`: manuscript,
  supplement, evidence registry, numerical provenance, and hostile audits.
- `prl_draft/audits/THEORY_AUDIT.md`: exact complementary-minor antipodal
  theorem, regular-root count, forward/production distinction, Haar spherical
  ensemble, and foundations limitations.
- `prl_draft/audits/NUMERICAL_AUDIT.md`: eligible post-cutoff evidence and
  missing numerical checks.
- `reports/` contains campaign-specific derived tables/figures. These are
  evidence summaries; raw files and manifests remain authoritative.
- `figures/hamiltonian_classification_20260815/` contains the reproducible
  composition-consistency figure, direct-sum refinement counterexample,
  conditional saved-data detuning figure, and random-network great-circle
  no-go, with machine-readable source data. Figures requiring the unrun Zeus
  manifest are intentionally absent.

## 7. Gaps that define the next implementation stages

1. Run the prepared 149-point Zeus manifest to apply homogeneous QZ and common
   full-sphere gates to transverse mixing, detuning, multiaxis coupling,
   scrambling, physical architectures, random networks, and Haar controls.
2. Establish size/time and five-seed network uncertainty from that complete
   campaign without pooling roots as independent stochastic samples.
3. Evaluate symmetry-resolved detector spectral mechanisms against the root
   diagnostics using the prepared postprocessor.
4. Test density-estimator and detector-size convergence of the direct
   stereographic density-ratio residual.
5. Derive or falsify a physical preparation/selection measure over roots and
   null vectors; geometry and equal algebraic multiplicity do not supply it.
6. Investigate context refinements beyond the proved tensor spectator,
   basis-permutation invariance, and nonuniform direct-sum counterexample.

## 8. Scientific status at the audit boundary

- **PROVED ANALYTICALLY:** regular projective root count; exact antipodal
  relation between the two labelled forward root multisets; inversion-odd
  asymmetry; exact Haar one-point isotropy.
- **VERIFIED NUMERICALLY in existing focused tests:** NumPy/QuSpin operator
  agreement for covered families, symmetry reconstruction, homogeneous finite
  and infinite roots, residual formulas, and campaign partitioning.
- **SUPPORTED NUMERICALLY but requiring common-pipeline reproduction:** the
  matched clean ring develops a strongly dipolar, Born-like finite-size root
  geometry at the best stored points.
- **NOT SUPPORTED:** Hamiltonian dynamics alone derives a probability measure;
  generic chaos, exact degeneracy, or heavy tails are sufficient; the observed
  finite-size trend is thermodynamically converged.
