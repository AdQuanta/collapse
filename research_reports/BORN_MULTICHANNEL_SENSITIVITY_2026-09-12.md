# Reduced multichannel sensitivity: coherent fields versus polar coverage

**VERIFIED_NUMERICALLY, reduced systems only.** All 162 preregistered full
Hamiltonian/QZ conditions completed with valid homogeneous roots. None has full
64-bin reflected coverage; none passes the frozen structural gate. None of the
16 signed perturbation/seed combinations meets the preregistered worst-time
improvement rule. **INCONCLUSIVE for a thermodynamic Born basin:** these small
systems do not reproduce the large-N positive regime even at the baseline.
The exact open-phase objective remains **OPEN**.

## Question, prediction and conventions

Starting from archived multichannel configs 079 and 047, test whether a small
central field or longitudinal coupling improves direct projective balance
without losing coverage. The alternative is a time-dependent tradeoff rather
than a uniformly improved candidate. The config and worker were committed as
`eb48c0a` before the run. This is one-variable-at-a-time local sensitivity,
not an optimization sweep or a held-out validation claim.

The model is exactly `RingChainSpec` with the repository's positive Pauli
coefficients, central qubit first, periodic detector bonds, hbar=1, and ring
couplings divided by sqrt(N), sqrt(N), N once. Parameters are checked against
the original source metadata, including the native-to-positive sign change.
No ZX coupling, altered root definition, or Magnus approximation is used.

- Seeds: 079 and 047, including both nonzero gx and gy.
- Detector sizes: N=5,6,7; times: 10³,10⁵,10⁶, evaluated separately.
- Baseline plus independent positive/negative h0x, h0y, h0z and gz increments.
- Each increment has magnitude .05 max(|gx|,|gy|): .000626368058626856
  for 079 and .0107690604821116 for 047, in energy units. gz receives the
  additional native 1/N edge scaling; the central fields do not.
- 54 Hamiltonians and 162 conditions. All roots retain algebraic multiplicity.
- Discovery data only. No averaging over times, optimized readout, resampling,
  smoothing, or replacement of empty bins.

The frozen `born-phase-verifier-v1` is unchanged. For every size separately,
a direction can be retained only if its worst-time normalized balance and
moment errors do not increase and its minimum coverage does not decrease,
with at least one strict balance improvement. This rule describes the reduced
screen and does not certify finite parameter width. All 16 comparisons are
**REJECT** under that rule, with no root-validation failure causing rejection.

## Main evidence

At N=7, extrema across all three times are:

| Seed / perturbation | Minimum coverage | Worst moment error | Worst relative balance |
|---|---:|---:|---:|
| 079 baseline | .25000 | .053256 | 1.000000 |
| 079 +h0x | .15625 | 1.355015 | 1.000000 |
| 079 +h0y | .53125 | 1.251666 | .840455 |
| 079 +h0z | .25000 | .049266 | 1.000000 |
| 079 +gz | .25000 | .051082 | 1.000000 |
| 047 baseline | .18750 | .015807 | 1.000000 |
| 047 +h0x | .37500 | 3.392479 | 1.000000 |
| 047 +h0y | .31250 | 3.266677 | 1.000000 |
| 047 +h0z | .15625 | .012898 | 1.000000 |
| 047 +gz | .18750 | .017196 | 1.000000 |

All signs, sizes and times are retained in the records and figures; this table
does not replace the complete comparison. Negative transverse signs give the
same polar law by the exact symmetry below. Longitudinal negative signs are
not redundant and remain in the experiment.

Across all 162 conditions, coverage ranges from .09375 to .9375. The baseline
tilted mass ranges from .001119 to .023276. Thus the baseline's small absolute
moment residuals coexist with near-north-pole concentration and poor coverage.
The normalized direct balance is often saturated at one because the tilted
and reflected tilted histograms have disjoint support at this resolution.
Differences of order machine epsilon around one are roundoff and provide no
ranking evidence. The recorded values are not clipped to improve a result.

The h0y perturbation of 079 expands the angular support but substantially
worsens moment balance. h0x and h0y have large worst-time effects for both
seeds. h0z and gz show mixed size-dependent changes. This is evidence against
uniform improvement by these particular reduced perturbations, not a no-go
for any of those channels in the thermodynamic limit.

## Exact sign equivalence for the tested transverse directions

**PROVED in this seed family.** Let P=product_i Zi on the detector and
G=Z0 tensor P. With only detector z fields and diagonal XYZ bonds/couplings,
conjugation by G leaves all two-spin terms invariant and sends
(h0x,h0y) to (-h0x,-h0y), leaving h0z and gz unchanged. For propagator blocks,

\[
A'=PAP,\qquad C'=-PCP.
\]

Hence each homogeneous root (alpha,beta) maps to (-alpha,beta), preserving
its polar angle and algebraic multiplicity, including zero/infinite roots.
Along an isolated h0x or h0y axis from h0x=h0y=0, opposite perturbation signs
therefore have identical polar statistics at every N and time. This does not
allow independent sign removal when both transverse fields are nonzero or
when the detector has transverse fields. It is a useful exact control and
removes redundant signed conditions from a future campaign in this scope.

**VERIFIED_NUMERICALLY:** all 36 opposite-transverse-sign pairs agree in
sorted polar angles to at worst 1.50345e-7. The nonzero discrepancy at long
times is consistent with the independently observed numerical sensitivity
below; no exact equality is inferred from finite precision.

## Numerical reliability and artifacts

Hermitian eigensystems use SciPy eigh (evr). Independent evd comparisons
cover both seeds at N7, baseline and +h0x, at every time: 12 comparisons.
The predeclared tolerances were 1e-6 for the homogeneous radial potential
and 1e-4 for sorted polar angles. All comparisons passed.

| Check | Observed maximum |
|---|---:|
| Relative Hamiltonian eigen-residual | 3.642e-15 |
| Normalized unitarity residual | 2.061e-13 |
| Right homogeneous QZ residual | 4.341e-15 |
| Left homogeneous QZ residual | 4.318e-15 |
| evr/evd radial-potential discrepancy | 4.025e-9 |
| evr/evd sorted-polar discrepancy | 7.275e-8 |
| evr/evd normalized propagator discrepancy | 3.264e-8 |

All QZ pole classifications and local coordinate condition diagnostics are
retained. The maximum reported local coordinate condition is 2438.75. Small
backward residuals alone are not forward-error guarantees, especially at
t=1e6; the cross-driver checks address a finite subset, not every condition
or an arbitrary-precision guarantee.

The run took 4.619 seconds with one BLAS thread, Python 3.11, NumPy 2.4.6 and
SciPy 1.17.1. Every one of 165 output files listed in the run manifest was
checksummed and revalidated. Raw alpha, beta, theta and both residual arrays
are saved for each condition. No large local production simulation was run.

- `reports/born_multichannel_sensitivity_v1_2026-09-12/`: preregistration,
  append-only condition records, per-condition NPZs, decisions and manifest.
- `reports/born_multichannel_sensitivity_v1_figures_2026-09-12/`: worst-time
  heatmap and 18 PDF profile pages showing **all 162** P/reflected-P and
  R/Born pairs. Empty ratio bins remain undefined. The overview PNG and
  an N7 profile PNG were visually inspected.
- `tests/test_born_multichannel_sensitivity.py`: normalization and tests
  preventing favorable-time selection, ignored validation failures, or a
  balance improvement hiding lost coverage. Nineteen focused tests passed
  with the ring/chain convention and frozen-verifier suites.

## Decision and next useful action

**KEEP** the full-QZ runner and exact sign control. **REJECT** the tested
directions as uniformly improving reduced candidates. **INCONCLUSIVE** for
the requested open Born phase. All high-N archived leads remain candidates;
the small-N failure does not overturn their reproduced large-N observations.

Do not continue optimizing a reduced baseline with saturated balance error
and inadequate coverage. Next, prepare an exact detector-translation-sector
implementation for the full admissible ring parameters, cross-check it against
this dense reference, and use it for a properly authorized larger-N
time/field experiment. Translation survives uniform central and detector
fields and XYZ bonds; sector-local root multisets must be combined with full
algebraic multiplicity, without mixing sectors for level-spacing analysis.
Existence of the thermodynamic-first late-time law and a microscopic proof
of its exact tilt remain unresolved.
