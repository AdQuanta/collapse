# Full-parameter ring translation method and baseline campaign preparation

**PROVED, algebraic reduction.** The uniform ring Hamiltonian commutes with
detector translation for every independent component of h0, h, J1, J2 and g.
Writing detector space as the direct sum of momentum sectors gives

\[
H=\bigoplus_k H_k,\qquad A=\bigoplus_k A_k,\quad C=\bigoplus_k C_k,
\qquad \det(\beta C-\alpha A)=\prod_k\det(\beta C_k-\alpha A_k).
\]

Consequently the complete homogeneous projective root multiset is the union
of the sector root multisets, including zero and infinite roots, with each
root retaining algebraic multiplicity. It is not an average of sector ratios.
No magnetization or parity constraint is imposed; nonzero independent Y
fields and anisotropic first/second-neighbor XYZ bonds remain admissible.
This exact reduction changes neither the family nor the frozen verifier.

`core/ring_translation.py` implements one block at a time, reusing the
repository's exact cyclic multiplicities and production homogeneous QZ.
QuSpin's central bit 1 represents physical |0>; sector central slices are
explicitly ordered and checked for matching detector representatives. The
open chain is rejected by this method because its endpoint breaks translation.

**VERIFIED_NUMERICALLY.** Tests independently project the dense NumPy
Hamiltonian for all 15 individual coefficients, then check every momentum
sector for generic XYZ rings at N=5,6,7. The projectors are complete and
orthonormal. Full complex Bloch rays are matched, so an unnoticed complex
conjugation is not accepted merely because polar angles agree.

The preregistered validation uses both positive multichannel seeds and a
generic 15-component example, N=5,6,7 and t=.31,1e3,1e6: all 27 conditions
passed. Dense calculations use eigh/evd and sectors use eigh/evr, with the
same QZ solver. Maxima were:

| Quantity | Maximum |
|---|---:|
| Dense Hamiltonian/block intertwining residual | 5.0212e-16 |
| Eigensystem/orthogonality/Hermiticity residual | 1.4751e-14 |
| Matched Bloch-ray Euclidean error | 2.4559e-8 |
| Bounded radial-potential error | 7.5652e-9 |

Predeclared tolerances: matrix/eigensystem/isometry 1e-12, Bloch matching
2e-5 and radial potential 1e-6. Neither the core verifier's thresholds nor
its binning was changed. Evidence is in
`reports/born_ring_translation_validation_v1_2026-09-12/` (the directory
retains the date when the validation began).

**KEEP** the exact sector method for full-family ring work. This validates a
computational reduction, not an exact Born law or a root-limit interchange.
The full scientific objective remains **OPEN**.

## Prepared next experiment

`configs/born_ring_baseline_campaign_v1.json` defines six independently owned
seed/N tasks for configs 079/047 at N13–15 and four instantaneous times.
The campaign tests baseline time stability before a costly neighborhood scan.
It includes t=1e6 for comparison to immutable archives and disjoint discovery
and held-out time sets. Long-time phase error at t=1e7 remains a material
numerical concern requiring assessment before a phase claim.

The worker checkpoints each momentum with hashes, verifies complete sector
coverage and full root counts, records conditioning and both QZ residuals,
and refuses changed source/config/runtime on resume. Local tests exercise an
actual reduced campaign run, resume, and corruption detection. The combined
focused suite passed 38 tests; the earlier sector-only suite passed 37.

The [runbook](../hpc/zeus_born_ring_baseline_v1.md) records resources, exact
task counts, source/output locations, completion gates and required
authorization. Zeus initially responded with a valid Python scientific stack
and an empty own-user queue; subsequent SSH source preparation timed out.
No production job has been submitted. Remote source state must be inspected
and preflight completed before requesting the concrete submission approval.

## Long-time endpoint check

An additional preregistered nine-condition check at t=1e7 passed with the same
method-validation thresholds. Maximum matched Bloch-ray error was 2.73449e-7,
and radial-potential discrepancy was 3.82823e-8. This supports reduced
implementation consistency at the planned endpoint, not a size-uniform
precision bound for N13–15. Evidence is in
`reports/born_ring_translation_long_time_v1_2026-09-13/`.

The final connection audit records three SSH timeouts after the initial
success. Snapshot transfer and remote tests are **unverified**. There is no
PBS job ID and no submission. Local preflight evidence and defining hashes
are in `reports/born_ring_campaign_preflight_2026-09-13/preflight.json`.
