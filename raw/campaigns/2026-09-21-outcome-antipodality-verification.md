# Outcome-pencil antipodality: derivation review and numerical certification

Source: repository execution (`tests/test_outcome_antipodality.py`) and `verifier/exact_formalism/v1/METHOD.md`
Collected: 2026-09-21
Published: 2026-09-21

**Date:** 2026-09-21
**Status:** Certified numerically; the theorem itself is exact and was already argued in the frozen `exact-formalism-v1` METHOD note
**Gate:** No gate promoted; `paper_ready = false`
**Branch:** `fix/homogeneous-root-newton-refinement`

## Why this was checked

Every Born score in the repository is formed as
`born_ratio_from_theta(theta, np.pi - theta)` (`core/born.py:83`,
`scripts/eval_chain_born.py:298`, `scripts/born_hamiltonian_search.py:492`, and
others): the outcome-1 root set is obtained by reflecting the outcome-0 set
rather than by solving the second `SPEC.md` §3 pencil. `SPEC.md` §4 and §5
define the criteria on two separately solved, separately normalized outcome
measures, and `wiki/concepts/born-like-points.md` records that the reflected
ratio equals the SPEC weak ratio only if the outcome measures are antipodal.
This session tested that condition directly instead of assuming it.

## Statement

For a unitary `U` on `C^2 (x) H_D` written qubit-first, and for a homogeneous
qubit ray `[alpha:beta]` with forbidden branches
`M_0 = beta U_10 + alpha U_11` and `M_1 = beta U_00 + alpha U_01`,

    dim ker M_0(alpha, beta) = dim ker M_1(conj(beta), -conj(alpha))

for every ray. The right-hand ray is the Bloch antipode of the left-hand one.
No assumption on dimension, Hamiltonian family, regularity, degeneracy or
defectiveness is used.

## Numerical certification

`python3.11 -m pytest -q tests/test_outcome_antipodality.py` gives 13 passed.
Mutation check on the antipodal map: replacing it by the identity is killed by
3 of 3 kernel-dimension tests; a conjugate swap without the sign is killed by 2
of 3, surviving only at the poles where the two maps coincide.

Measured quantities, where the Gram identity residual is
`max |M_0(c)* M_0(c') + M_1(c)* M_1(c') - <c,c'> I|` over 20 random ray pairs,
and the chordal gaps compare each outcome-1 Bloch root to the nearest antipode
of an outcome-0 root, and to the nearest non-antipodal one:

| case | Gram identity residual | worst antipodal chordal gap | worst non-antipodal gap |
|---|---:|---:|---:|
| Haar unitary 2x2 | 1.790e-15 | 2.719e-16 | 1.756e+00 |
| Haar unitary 2x4 | 2.809e-15 | 9.289e-16 | 1.285e+00 |
| Haar unitary 2x8 | 5.024e-15 | 2.212e-15 | 8.207e-01 |
| ring/all N=3 t=3.7 | 1.013e-14 | 1.569e-16 | 1.999e+00 |
| ring/all N=4 t=211.0 | 1.210e-12 | 1.307e-14 | 1.998e+00 |
| chain/first N=3 t=3.7 | 2.275e-14 | 1.553e-16 | 2.000e+00 |
| chain/first N=4 t=211.0 | 8.820e-13 | 7.841e-16 | 2.000e+00 |

The two `t = 211.0` residuals are not a property of the theorem: the
propagators themselves carry `||U* U - I||_max` of 3.428e-13 (ring) and
2.562e-13 (chain) at that time, so the Gram residual tracks the unitarity error
of `expm` and inherits the `|c|^2` scale of the random test rays. At
`t = 3.7` the same propagators are unitary to 2.442e-15 and 3.664e-15.

Degenerate and defective cases, where kernel dimension and algebraic
multiplicity differ:

- `I_2 (x) I_3`: outcome 0 at the north pole has kernel dimension 3; outcome 1
  at its antipode, the south pole, also has kernel dimension 3.
- The unitary completion whose outcome-0 pencil is `D (lambda I - M)` for a
  single 2x2 Jordan block `M` — algebraic multiplicity two at `lambda = 1`,
  kernel dimension one — gives kernel dimension 1 on both sides of the map.

Ray-local complementarity, a by-product of the same identity: at a single ray
the squared singular values of the two branches satisfy
`sigma^2(M_0) + sigma^2(M_1) = |c|^2` pairwise, verified at
`[alpha:beta] = [0.4+0.9i : -1.3+0.2i]` on a Haar unitary of dimension 8 to
1.776e-15.

## Scope and what is not established

The theorem pairs rays and kernel *dimensions*. It does not pair the detector
kernel vectors themselves, it supplies no measure for a singular pencil's
continuum of rays, and it makes neither Born criterion true. Its consequence
for the repository is narrower and specific: the reflected polar scoring in use
is exact rather than a surrogate, and the strong criterion is a statement about
a single measure and its antipodal image.
