# Exact-Born claim audit and frozen verifier v1

**OPEN:** no full-family positive or negative theorem has been established.
**REJECT:** the claimed completion in `EXACT_BORN_PERTURBATIVE_RESOLUTION.md`.
**KEEP:** its valid conditional measure identities and independently reproduced
finite-size evidence. This audit changes no Hamiltonian or production QZ rule.

## 1. Mathematical audit

The conditional identity

\[
S_*[\sin^2(\theta/2)\mu]=\sin^2(\theta/2)\mu
\]

is **PROVED** and equivalent to the full sequence of cosine-moment constraints.
It does not establish existence of a limiting measure, nondegenerate coverage,
or a Hamiltonian mechanism. An atom at the north pole is invisible to the tilt.
Consequently, even all moment equalities alone do not meet the goal.

The report's scalar-potential equivalence is **FALSIFIED as written**.
For a finite nonzero root with log-radius y, the normalized kernel is

\[
k_y(x)=\max(y,x)-\max(y,0),\qquad
k_y'(x)=1_{x>y},\qquad k_y''=\delta_y.
\]

Thus J' is the cumulative distribution (with the appropriate one-sided
derivative at atoms), and J'' is the interior log-radius measure. Where a
density exists, the correct relation is

\[
e^x J''(x)=e^{-x}J''(-x).
\]

The original relation with J' fails even for exact Born densities. For example,
P(theta)=(1+cos(theta))/pi has log-radius CDF
F(x)=(theta(x)+sin(theta(x)))/pi. Its derivative is the density; F itself
cannot obey the claimed exponentially tilted reflection identity. Zero roots
contribute a linear x term to J; infinite roots contribute zero. The two
endpoint masses must be recovered from limiting slopes, not J'' on R.
This distinction was already implemented and tested in
`core/projective_potential.py` and `tests/test_projective_potential.py`.

The open-phase assertion is **OPEN**, not proved by the valid equivalences:

- The six-dimensional displayed box fixes gy=gz=0 and central fields to zero,
  with additional detector restrictions. It has empty interior in the full
  15-component parameter space of `RingChainSpec` at fixed topology and N.
  Its use of closed intervals is a secondary issue; taking their interiors
  still does not give full-parameter interior.
- Existing Theorem C in `BORN_ASYMPTOTIC_OBSTRUCTIONS.md`, section 9, already
  excludes a Born interval in the central-X field at every X-conserving seed,
  allowing arbitrary interacting detector dynamics. In particular, an open
  exact-Born region in the full parameter space cannot contain such a seed:
  its intersection with that central-field line would be an excluded interval.
  This does **not** exclude a disjoint open region with broken X conservation.
- At full central-field interval width w and time t, the same existing proof
  gives |mean_h d0 + 1| <= 5/(2w|t|). Requiring |d0|<=epsilon at every field
  implies w<=5/[2|t|(1-epsilon)]. At t=1e6 and epsilon=.05, this is
  2.631579e-6 in energy units, independently of N. This is a necessary bound,
  not a measured basin width or a new theorem from this audit.
- Declaring N-first limits is not proving they exist. Finite-N recurrence
  does not produce an ordinary delta_0 late-time limit; it prevents the
  generic nontrivial ordinary limit. A fixed-time perturbative error estimate
  cannot be extended to arbitrary late times without a uniform bound.
- Broadening/wrapping resonant phases does not derive the required Born tilt.
  The claimed mechanism has no proof of the all-order trace constraints.
- The reported N10 perturbations use 32 bins and errors .136--.312, and some
  have incomplete coverage. They do not pass the declared 64-bin .05 gate.
  The ZX central-detector term is outside the goal's diagonal XYZ family.
  Those historical numbers were not independently reproduced in this audit.

## 2. Frozen numerical verifier

`core/born_phase_verifier.py` defines **born-phase-verifier-v1**. It wraps the
unchanged `born_ratio_from_theta`, `cosine_moments`, and homogeneous QZ spectrum.
Constants: 64 production bins, eight moment pairs, ratio and moment tolerances
.05, and a separately declared homogeneous residual tolerance 1e-10. The
numerical gate requires both left and right diagnostics and no indeterminate
or missing roots. It records pole fractions and conditioning; small backward
residuals do not guarantee accurate ill-conditioned roots.

For the empirical measure mu, the added direct diagnostic uses

\[
\nu=\sin^2(\theta/2)\mu,\quad
D_{64}=\sum_{B\in\mathcal B_{64}}|\nu(B)-(S_*\nu)(B)|,
\quad D_{64}^{rel}=D_{64}/[2\nu([0,\pi])].
\]

The reflected weighted histogram is computed from the same roots with their
original weights. This directly tests the detailed-balance measure, without
affine division or a bin-center approximation to the tilt. At finite resolution
it is weaker than equality of measures. No acceptance threshold is assigned to
this new diagnostic after inspecting candidates. The absolute residual and
tilted mass accompany the normalized value. If tilted mass is zero, the
normalized residual is undefined and coverage fails. No IID errors, smoothing,
empty-bin replacement, or time average is used for a global pass.

Campaign summaries retain size/time/perturbation identities, failures, missing
values, and separate discovery/held-out groups. All-condition worst errors
are undefined if a condition failed; global ratio errors are undefined when
coverage is incomplete. Missing QZ evidence remains unavailable. Changing the
metric definitions or constants requires a new schema and restarted comparison.

## 3. Preregistered archive reproduction

Hypothesis, alternative and prediction are recorded before calculation in
`configs/born_phase_archive_audit_v1.json`. **VERIFIED_NUMERICALLY:** all 15
source snapshots passed the selected COMPLETE hash checks, parameter scaling,
size/time, root-count and archived validation checks; production ratio RMSE
reproduced within 1e-12. These are source/reanalysis checks, not new QZ solves.

Largest available size for each seed, all at t=1e6 with full reflected coverage:

| Seed | N | Ratio RMSE | Eight-moment max | Tilted mass | D64 relative |
|---|---:|---:|---:|---:|---:|
| Nearest-neighbor ring | 17 | .015923 | .014054 | .117527 | .058081 |
| Second-neighbor ring | 17 | .017574 | .015164 | .130123 | .056752 |
| Config 079 | 15 | .054979 | .052994 | .071055 | .271075 |
| Config 047 | 16 | .062789 | .045441 | .042248 | .367316 |

**KEEP as finite-size leads; no PROMOTE.** The multichannel balance residuals
improve with N, but remain substantial. Their small absolute moment errors
coexist with relatively small tilted masses. The X-only seeds have better
balance diagnostics, but the known field obstruction excludes an open phase
containing them. All four groups contain just one time and no perturbation or
held-out validation condition. Historical finite-eigenvalue checks cannot
certify the requested homogeneous QZ residuals or numerical pole fractions.

Outputs: `reports/born_phase_archive_audit_v1_2026-09-12/`, including
`results.json`, input/code/output hashes in `manifest.json`, and four PNG/PDF
figures showing P, reflected P and R against Born. These are derived files;
all source archives are unchanged.

## 4. Validation and next experiment

Solvable positive controls are the independently inverted exact Born density
and a weighted two-angle detailed-balance measure. Negative controls include
the Haar polar law, vacuous north-pole moments, indeterminate pencils, missing
left diagnostics, missing roots and failed held-out conditions. The initial
8192-quantile Born control exceeded its test-only discretization bound
(.0046225 versus .004); increasing quadrature resolution to 32768 quantiles
resolved it without changing any verifier metric or candidate threshold.

Validation: **67 tests passed** across the verifier, potential, reciprocity,
Born histogram and projective-root convention suites. Python compilation and
CLI help passed; all defining-code and output hashes were rechecked. The
config-079 PNG was visually inspected, with separate P/reflected-P and R/Born
panels and readable labels. Reproduction uses Python 3.11:

```bash
python -m pytest -q tests/test_born_phase_verifier.py tests/test_projective_potential.py tests/test_born_reciprocity.py tests/test_born.py tests/test_projective_root_conventions.py
python scripts/audit_born_phase_archives.py --output reports/born_phase_archive_audit_fresh
```

The next useful question is whether genuinely multichannel seeds retain their
direct balance under independent central fields and gz, at multiple times.
Fresh reduced production-QZ checks should establish the runner and controls
before a production campaign. Do not spend a new large campaign measuring an
open-phase width around an exactly X-conserving seed already excluded by C.
The full positive-or-negative goal remains **OPEN**.
