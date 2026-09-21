# Fixed-input pencil versus SPEC outcome pencils: proof and numerical certification

Source: repository execution and user correction, 2026-09-21
Collected: 2026-09-21
Published: 2026-09-21

**Date:** 2026-09-21
**Status:** Proved; certified numerically over both approved families
**Gate:** No gate promoted; `paper_ready = false`
**Branch:** `wiki-fixed-input-outcome-equivalence`

## Why this was checked

An agent-side session reported as a finding that the production Born pipeline
"scores the wrong pencil": `scripts/eval_born.py:143`,
`scripts/eval_chain_born.py:433` and `core/analysis.DisentanglementAnalyzer`
all solve the block-column pencil `C v = z A v` built from `(U_00, U_10)` —
the fixed-input problem, in which the qubit starts in `|0>` — whereas
`SPEC.md` §3 defines collapsibility through the block-row pencils
`U_10 + lambda U_11` and `U_00 + lambda U_01`. On a Haar unitary the two root
sets are plainly different: at detector dimension 4, seed 7, the fixed-input
radii are `{1.032, 1.048, 1.676, 1.784}` while the outcome-0 radii are
`{0.570, 1.392, 1.798, 2.264}`.

The user rejected the finding: *"The two pencil characterizations are provably
the same."* This record contains the proof and its certification. The user was
correct; the surrogate-observable claim is withdrawn.

## Statement

Write `U` qubit-first with blocks `U_ba`. Let the *fixed-input* roots be the
projective solutions of `U_10 v = z U_00 v`, and let the outcome-`b` roots be
the `SPEC.md` §3 solutions of `(U_10 + lambda U_11)|D> = 0` and
`(U_00 + lambda U_01)|D> = 0`.

**(A) Time-reversal duality, unconditional.** The fixed-input characterization
of `U` equals the outcome-0 characterization of `U^dagger`: same projective
roots, same kernel dimensions.

**(B) Equality under time-reversal symmetry.** If `U^T = U` — equivalently
`H` is real in the computational basis — then

    fixed-input roots of U = conj(outcome-0 roots of U)

with equal kernel dimensions. Radii are therefore identical and azimuths are
mirrored.

## Proof

**(A)** If `U_10 v = z U_00 v` then

    U (|0> tensor v) = |0> tensor U_00 v + |1> tensor U_10 v
                     = (|0> + z|1>) tensor U_00 v,

so with `|D'> = U_00 v`, applying `U^dagger` gives
`U^dagger (|psi_q(z)> tensor |D'>) ∝ |0> tensor v`, which is `SPEC.md` §2's
definition of exact collapsibility to outcome 0 for the unitary `U^dagger` at
the projective point `z`. Conversely, if
`U^dagger (|psi_q(lambda)> tensor |D>) = |0> tensor |D''>` then
`U (|0> tensor |D''>) = |psi_q(lambda)> tensor |D>`, which forces
`U_10 |D''> = lambda U_00 |D''>` and `|D> ∝ U_00 |D''>`. The map
`v -> U_00 v` is injective on the fixed-input kernel, because `U_00 v = 0`
together with `U_10 v = z U_00 v` gives `U (|0> tensor v) = 0`, impossible for
`v != 0` under a unitary. It is surjective by the converse. Hence the kernel
dimensions agree ray by ray.

**(B)** `U = exp(-iHT)` satisfies `U^T = U` iff `H^T = H`, and a Hermitian `H`
has `H^T = conj(H)`, so this holds iff `H` is real. Then `U_01^T = U_10`, and
since `det M = det M^T` and `dim ker M = dim ker M^T`, the outcome-1 pencil may
be transposed:

    (U_00 + lambda U_01)^T = U_00 + lambda U_10
                           = -lambda (U_10 - (-1/lambda) U_00),

so the outcome-1 roots and weights are the fixed-input roots and weights under
`z = -1/lambda_1`. Composing with the antipodal pairing already proved in
`wiki/concepts/outcome-antipodality.md`, `lambda_1 = -1/conj(lambda_0)`, gives
`z = conj(lambda_0)`.

## Numerical certification

All runs use `SinglePixelHamiltonianQuSpin` with `use_symmetry=False`, dense
`numpy.linalg.eigh`, and the propagator formed as `V exp(-iEt) V^dagger`.

**(A), Haar unitaries of matrix dimension 8** (`generate_random_unitary`,
seeds 7, 11, 23), comparing sorted projective roots:

| seed | \|fixed(U) - outcome0(U^dagger)\| | \|fixed(U) - outcome0(U)\| |
|---|---:|---:|
| 7 | 0.000e+00 | 3.043e+00 |
| 11 | 0.000e+00 | 2.789e+00 |
| 23 | 0.000e+00 | 1.799e+00 |

**(B), 36-cell sweep of both approved families.** `connectivity` in
{ring, chain} x `central_coupling` in {all, first} x `N` in {3, 4, 5} x `t` in
{1, 37, 211}, at `J = 1.10`, `Jxx = 1.32`, `Jyy = 2.53`, `Jx = 0.10`,
`Jy = 0.05`, `Jz = 0.06`, `hx = -1.34`, `hz = 1.00`, `hx0 = -1.35`,
`hz0 = 2.01`, with `Jpm = Jcpm = Jzx = J2 = Jpm2 = 0`:

| Y self-fields | worst max\|U - U^T\| | worst \|fixed - conj(outcome0)\| | worst radii gap |
|---|---:|---:|---:|
| off (`hy = hy0 = 0`) | 1.665e-16 | 8.265e-14 | 5.662e-14 |
| on (`hy = 0.7`, `hy0 = -1.69`) | 1.026e+00 | 2.670e+00 | 1.541e-01 |

**Single-cell detail**, `screen_00` chain parameters at `N = 5`, `t = 211`:
with `h0y = 0` the Hamiltonian has `max|Im H| = 0.000e+00`,
`max|U - U^T| = 8.442e-17`, `|fixed - conj(outcome0)| = 0.000e+00`,
`|fixed - (-1/outcome1)| = 7.130e-10`, and sorted-radii agreement to
`0.000e+00`; `characterize_pencil_roots` returns `regular` with 32 distinct
roots and total kernel weight 32 on both pencils. With the published
`h0y = -1.69` the same cell gives `max|Im H| = 1.690e+00`,
`max|U - U^T| = 5.625e-01` and a sorted-radii gap of `2.706e-02`.

**Mutation check.** On a Haar unitary of matrix dimension 8 the same
conjugation map gives `1.442e+00`, so the agreement above is produced by the
symmetry and not by the map being vacuous.

## Consequence for the repository

Because the radii coincide exactly, the polar marginals coincide, and the
reflected scoring `born_ratio_from_theta(theta, pi - theta)` applied to
fixed-input radii computes the `SPEC.md` §5.2 weak ratio itself. Every
`S_Born` in the repository is the SPEC quantity, not an approximation to it,
for every Hamiltonian in the approved families with no single-site `Y` term.

## Scope and what is not established

The conjugation mirrors azimuths, so a full-sphere (strong-criterion) measure
built from the fixed-input pencil is the true measure reflected through the
`xz` plane; the transverse components of an estimated preferred axis come out
sign-flipped unless the roots are conjugated first. The polar marginal, and
therefore the weak criterion, is untouched by this.

`U^T = U` fails exactly when a single-site `Y` operator is present. Every other
term in the approved families — `Z_i Z_j`, `X_i X_j`, `Y_i Y_j`, `Z_0 Z_i`,
`X_0 X_i`, `Y_0 Y_i`, `X_i`, `Z_i` — is real in the computational basis, so the
`h_y` and `h_0y` self-fields added on 2026-09-20 under
`raw/project-governance/2026-09-20-y-self-field-family-extension-approval.md`
are the sole exception. The `screen_00` endpoint-chain region carries
`h_0y = -1.69` as its only imaginary term; there the two measures differ
genuinely, and the measured `S_Born` gap between them is 0.0224, 0.0097 and
0.0030 at `N = 6, 8, 10` on the frozen six-time window
`t` log-spaced in `[100, 1000]`. That sequence is a measurement, not a proof of
asymptotic equality.

Nothing here makes either Born criterion true and no gate is promoted.
