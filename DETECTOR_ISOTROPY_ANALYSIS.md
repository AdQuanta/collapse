# Detector terms that cancel from the Born-root diagnostic

11 September 2026. This note extends [the structural analysis](BORN_STRUCTURE_ANALYSIS.md).
It concerns normalized algebraic root counting for
U10 v=lambda U00 v, theta=2 atan(|lambda|), and
R=P(theta)/(P(theta)+P(pi-theta)). Pauli eigenvalues are +/-1, hbar=1.
It does not derive preparation-dependent measurement probabilities.

## Exact cancellation criterion

Suppose H=I_q tensor K + H_rest with K Hermitian and
[I_q tensor K,H_rest]=0. Then

\[
U_{ab}=e^{-itK}(U_{\rm rest})_{ab}.
\]

Both blocks of the generalized pencil have the same invertible left factor,
so the entire root spectrum, P and R are unchanged by K. This statement
also covers regular pencils with infinite roots; it does not require U00
to be invertible. Indeterminate pencils still need to be rejected.
Changing detector levels through a cancelling term cannot tune visibility
or higher harmonics of R.

For a detector graph with arbitrary real edge weights, take

\[
K=-\sum_{(ij)}J_{ij}(X_iX_j+Y_iY_j+Z_iZ_j).
\]

Each edge is invariant under collective spin rotations. Thus K commutes
with S_a=sum_i sigma_i^a for a=x,y,z. With a uniform detector field and
uniform central coupling to these collective components, K commutes with
the rest of the Hamiltonian, including any qubit-only Hq. Graph connectivity
and the isotropic edge strengths therefore cancel from the root diagnostic.
This includes simultaneous isotropic first- and second-neighbor couplings.

In the native XXZ convention,

\[
H_D=-\sum_{(ij)}\left[J_{ij}Z_iZ_j+
\frac{J_{\pm,ij}}2(X_iX_j+Y_iY_j)\right]-h_zS_z,
\]

the isotropic line is **Jpm=2J on every edge**, and Jpm2=2J2 for second
neighbors. The factor of two follows from the production Pauli convention
in `SinglePixelHamiltonianQuSpin._build_static`, not a fitted convention.

Uniformity of the coupling is material. For V=-sum_i g_i X_i, direct Pauli
algebra gives

\[
[K,V]=2i\sum_{(ij)}J_{ij}(g_i-g_j)(Y_iZ_j-Z_iY_j).
\]

Thus unequal g_i across a nonzero edge generally breaks cancellation.
For a connected graph, equality across every nonzero edge forces uniform
g_i. Nonuniform detector fields, edge anisotropy and other noncommuting
detector terms can also make the interaction dynamically visible. None of
these changes by itself enforces the Born reflection balance.

The general criterion involves commutation with the *whole* H_rest. On an
anisotropic ring it is not valid to subtract an arbitrary isotropic part of
Hd: that part generally fails to commute with the remaining anisotropic
interaction. Accordingly R is not generally a function of J-Jpm/2 alone.

## Explicit full-space root measure when Hq=0

Now restrict to Hq=0, Hqd=-g X0 Sx, g=Jx/sqrt(N), with a uniform hz.
After cancellation of K, conditional detector evolution factorizes over
sites. The single-site relative unitary has eigenphases +/-phi, where

\[
\Omega=\sqrt{h_z^2+g^2},\qquad
\phi=2\arcsin\left|\frac{g}{\Omega}\sin(\Omega t)\right|.
\]

The zero-frequency value is defined continuously. Tensor multiplication
then gives the exact normalized counting measure

\[
P_N=2^{-N}\sum_{m=0}^{N}\binom Nm
\delta\!\left(\theta-
\left|\operatorname{wrap}[(N-2m)\phi]\right|\right).
\]

This uses the full 2^N detector space. Restricting to the maximal-total-spin
sector and assigning equal weights to its N+1 states would be incorrect.
The pair m and N-m folds to the same polar angle, so P has at most
floor(N/2)+1 distinct atoms. At B bins the reflection coverage is at most

\[
C\le\min\left(1,\frac{2(\lfloor N/2\rfloor+1)}{B}\right).
\]

For B=64 and N=11,12,13,14 the respective bounds are
0.1875, 0.21875, 0.21875 and 0.25. A globally covered Born-like profile at
these sizes therefore requires leaving at least one assumption of this
collective isotropic class. This is a finite-size/support obstruction, not
a theorem that anisotropy is necessary for every large-N approximate law.

## Numerical checks and controlled parameter grid

The source is the existing `zeus_single_pixel_anisotropic_20260718_130606`
campaign. Only the four sizes with DONE markers and complete 880-cell
inventories are included: N=11,12,13,14. At each size the full Cartesian
grid has 11 hz values, 8 J values and 10 Jpm values. Jx=0.01, hz0=0,
t=1e6, seed=44, nearest-neighbor ring and uniform central coupling are fixed.
The configuration records every value. No production jobs were submitted.

The audit verifies marker/configuration consistency, every required raw,
metadata, metric and figure path, all 2^N finite roots per case, reconstruction
of theta from lambda, and reproduction of the original 48-bin RMSE/coverage
and 100-bin S_born. The structural metrics and figures use 64 bins, with
raw-angle moments through order 16. These bin counts are not interchangeable.

All **220 isotropic spectra** agree with the exact binomial measure within
angular Wasserstein distance **2.024e-9 radians** at t=1e6, without fitting.
Every size attains but never exceeds its predicted coverage bound somewhere
in its isotropic grid. Independent native N=5,6 tests include both neighbor
ranges, zero/nonzero detector field and times 0.9,7.1,1e6. Further native
checks establish cancellation with nonzero qubit fields and uniform YY
coupling; the binomial formula itself is not applied to those cases.

As an additional exact check, global detector X rotation maps hz to -hz
while preserving XXZ exchange and the X coupling when Hq=0. All **1,600
matched positive/negative-field pairs** agree in moments through order 16
to **1.742e-9**. They are symmetry duplicates, not independent realizations.

For a descriptive comparison fixed before aggregation, call a case near
Born when all 64 reflection bins are occupied, R RMSE<=0.05, and the largest
of the first eight Born moment residuals is <=0.05. These are reporting
thresholds, not physical constants or a sufficiency theorem.

| N | full coverage, isotropic (55) | full coverage, pure ZZ anisotropic (77) | full coverage, exchange anisotropic (748) | near-Born exchange cases |
|---|---:|---:|---:|---:|
| 11 | 0 | 25 | 204 | 0 |
| 12 | 0 | 20 | 254 | 0 |
| 13 | 0 | 27 | 338 | 10 |
| 14 | 0 | 25 | 412 | 35 |

No pure-ZZ or isotropic grid point passes this joint near-Born definition.
The nonzero counts include both hz signs. Exchange and anisotropy jointly
support the successful cases in this grid, but 377 of 412 fully covered
anisotropic-exchange N=14 cases still fail the gate. Broadness is much less
restrictive than Born agreement, and neither exchange nor its anisotropy
sets the required reflection balance.

At fixed N=14,J=0.5,hz=0.1, changing Jpm from 0 to 0.1 opens full coverage
(0.21875 -> 1); setting Jpm=1 restores the isotropic obstruction (C=0.25).
The Jpm=0.1 and 2 profiles have full coverage but RMSE 0.08443 and 0.08156,
with higher-odd-harmonic norms 0.1103 and 0.1044. This is a matched example
of nonmonotonic exchange dependence, not a search for the best case.

There are successful neighboring samples too: at N=14,hz=0.01,J=0.5,
Jpm=0.1 and 0.25 have full coverage and R RMSE 0.03246 and 0.03167.
At J=1,Jpm=0.05, hz=2 and 2.01 give 0.03694 and 0.03610. Such endpoints
show success is not confined to one recorded coupling; they do not prove
agreement throughout the intervening interval or a multidimensional robust
phase. The changing N counts are size sensitivity, not a converged limit.

## Integrability versus detector chaos

The uniform nearest-neighbor detector is the standard integrable XXZ chain
in a longitudinal field; see the algebraic Bethe-ansatz treatment by
[Kitanine, Maillet and Terras](https://arxiv.org/abs/math-ph/9907019).
The overall energy sign and Pauli-to-spin normalization do not remove its
commuting integrals of motion. This statement concerns Hd alone, not the
coupled detector-qubit Hamiltonian or Hd +/- V, whose transverse fields can
change integrability.

The previously checksum-verified N=17 nearest-ring case has J=0.0275078909,
Jpm=0.0120491844, hz=0.0469773779, J2=Jpm2=0, and S_born=0.93163 with
full coverage and R RMSE=0.01592. Thus **nonintegrability/chaos of Hd is not
necessary for the observed approximate Born profile**. A finite-size spacing
histogram should not override this Hamiltonian identification. These data
neither establish a chaotic full-H mechanism nor derive the successful
relative-phase measure from Bethe integrability.

## Reliability and remaining mechanism

This legacy campaign lacks historical SHA-256 records and saved full-matrix
residuals. The new manifest hashes 10,572 loaded input files and inventories
to establish reproducible current provenance; it cannot retroactively
certify the original collection. The isotropic formula and field-sign
identities provide independent checks, but do not validate every anisotropic
eigensolve. The maximum scaled real part of lambda, whose exact value should
vanish in this X0-conserving model, is 1.412e-5. This is a spectral-geometry
consistency diagnostic, not a forward-error bound. Legacy generic-grid
claims remain qualified accordingly.

The new structural information is which Hd terms can influence R at all,
and an exact collective obstruction. Once those obstructions are removed,
the condition P=(1+cos(theta))A with reflection-even A still has to emerge
from the conditional dynamics. The grid does not establish a universal
sufficient bare-coupling criterion for that remaining balance.

## Reproduction and figures

```bash
python scripts/analyze_born_detector_grid.py --output reports/<fresh-grid-audit>
python -m pytest -q tests/test_isotropic_detector_identity.py
```

Use the project Python 3.11 environment and single-thread BLAS. This is
postprocessing plus reduced validation, not a new production simulation.
Nine isotropy tests pass, and 43 tests pass when combined with the existing
Born reciprocity, finite-field and table-export checks. All four new Python
files compile and the analysis CLI help check passes. The three rendered
figures were inspected; all 26 output hashes and named-column DAT exports
were checked after generation.

- [Parameter planes with coverage and Born-moment errors](reports/born_detector_isotropy_audit_2026-09-11/detector_parameter_plane.pdf)
- [Matched Jpm slices at four detector sizes](reports/born_detector_isotropy_audit_2026-09-11/matched_exchange_slices.pdf)
- [P, R, residuals and harmonics for four fixed-slice regimes](reports/born_detector_isotropy_audit_2026-09-11/representative_diagnostics.pdf)
- [All grid metrics](reports/born_detector_isotropy_audit_2026-09-11/case_metrics.csv)
- [Exact isotropic comparisons](reports/born_detector_isotropy_audit_2026-09-11/isotropic_identity_checks.csv)

Each `representative_Jpm_*` directory contains `profile.dat`,
`histogram_steps.dat`, `moments.dat`, and `R_harmonics.dat` for PGFPlots.
Figures use categorical parameter positions, no interpolation or smoothing,
and omit R harmonics whenever reflection support is incomplete.
