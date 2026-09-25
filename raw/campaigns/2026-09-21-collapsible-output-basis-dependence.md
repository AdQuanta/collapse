# Output-Basis Dependence of Collapsible States: Derivation and Repository Audit

> Source: In-session analytical derivation plus direct audit of the repository at commit-time 2026-09-21 (files read: core/projective_roots.py, core/outcome_measures.py, scripts/eval_preferred_basis.py, wiki/campaigns/preferred-basis-campaign.md, wiki/concepts/outcome-antipodality.md, wiki/campaigns/commuting-qnd-sector.md, SPEC.md).
> Collected: 2026-09-21
> Published: 2026-09-21

## 1. Conventions, verified against code

`core/projective_roots.py::split_qubit_first_blocks` returns, for a square even-dimensional
operator of size 2d:

    A = matrix[:half, :half]
    B = matrix[:half, half:]
    C = matrix[half:, :half]
    D = matrix[half:, half:]

with half = d. Qubit-first tensor ordering, so A = U_00, B = U_01, C = U_10, D = U_11.

`core/projective_roots.py::bloch_vectors_from_homogeneous` docstring:

    "The associated normalized qubit ket is proportional to ``(beta, alpha)``."

and the projective root is z = alpha/beta. So the input qubit state for ray [alpha:beta] is
beta|0> + alpha|1>.

`core/projective_roots.py::forward_pole_root_spectrum` docstring:

    "For outcome 0 this solves ``-C eta = z D eta``, equivalent to
    ``(C + z D) eta = 0``.  For outcome 1 it solves
    ``-A eta = z B eta``, equivalent to ``(A + z B) eta = 0``."

Its signature is `forward_pole_root_spectrum(unitary, outcome, **solver_options)`. There is no
basis argument.

This matches `wiki/concepts/outcome-antipodality.md`, which writes the forbidden branch of
outcome b as M_0(alpha,beta) = beta U_10 + alpha U_11 and M_1(alpha,beta) = beta U_00 + alpha U_01.

## 2. Derivation

Write the branch operators

    N_0(alpha,beta) = beta A + alpha B        (amplitude landing in output |0>)
    N_1(alpha,beta) = beta C + alpha D        (amplitude landing in output |1>)

so that

    U |Psi_in> = |0> tensor N_0|D> + |1> tensor N_1|D>

and the input is collapsible to outcome b exactly when N_{1-b}|D> = 0. For outcome 0 this is
(beta C + alpha D)|D> = 0, i.e. (C + zD)eta = 0, which is what the code solves.

Change the qubit OUTPUT basis to |b_n> = V|b>, V in SU(2). Collapsibility to outcome b in the new
basis means (<b'_n| tensor I) U |Psi_in> = 0 for the other branch b'. Since <b'_n| = <b'|V^dagger,

    (<b'_n| tensor I) U = (<b'| tensor I) (V^dagger tensor I) U

Therefore: changing the output basis by V is exactly replacing U by

    U^(n) = (V^dagger tensor I) U

Physically this is appending a qubit-only gate at readout; the detector is untouched.

Writing V^dagger = [[w00, w01],[w10, w11]], the blocks of U^(n) are

    A^(n) = w00 A + w01 C
    B^(n) = w00 B + w01 D
    C^(n) = w10 A + w11 C
    D^(n) = w10 B + w11 D

and hence the branch operators transform as a two-component spinor with operator-valued entries:

    N_b^(n)(alpha,beta) = w_{b0} N_0(alpha,beta) + w_{b1} N_1(alpha,beta)

The new outcome-0 pencil is

    N_1^(n) = beta (w10 A + w11 C) + alpha (w10 B + w11 D)

This is a pencil on a different pair of matrices: independent linear combinations of all four
blocks of U. Consequences:

(a) There is no Bloch rotation R with z_j^(n) = R . z_j. The root set is not a rigid rotation of
    the old one.
(b) ker N_1^(n)(z_j^(n)) is the kernel of a different operator, so the collapsible DETECTOR states
    change too.

So the collapsible set -- both the input rays and the detector null vectors -- is genuinely
output-basis dependent.

## 3. The input basis is inert

SPEC.md section 2 defines collapsibility as U(T)|Psi_in> = |b> tensor |D_b'>. The condition names
no input basis; |psi> is a vector in C^2. A change of input basis U -> U(W tensor I) relabels the
coordinates z of the same rays, rotating the Bloch root cloud rigidly, and leaves the collapsible
SET invariant.

Structural asymmetry: the input side is a continuum (CP^1) needing only coordinates; the output
side is a discrete two-outcome alternative needing a choice, and the choice changes the set. The
SPEC section 12 preferred axis is an output-side object.

## 4. Bidegree (d,d) counting

Fix the input ray [alpha:beta]. The output directions making it collapsible satisfy

    det( w10 N_0(alpha,beta) + w11 N_1(alpha,beta) ) = 0

a homogeneous binary form of degree d in (w10 : w11), hence generically d roots in CP^1, i.e. d
output directions. Dually, for a fixed output axis the pencil has d roots, i.e. d input rays. The
collapsible locus is therefore a curve of bidegree (d,d) in CP^1_in x CP^1_out.

Check d = 1 (no detector, U in U(2)): N_0, N_1 are scalars; w10 N_0 + w11 N_1 = 0 has the single
solution (w10 : w11) = (N_1 : -N_0), the unique axis through the output state U|psi>. Correct: a
single-qubit state is a basis state in exactly one basis.

Check U = I: A = D = I, B = C = 0, so N_0 = beta I and N_1 = alpha I. Outcome-0 pencil alpha I has
root z = 0 with kernel dimension d, i.e. |0> tensor |D> is collapsible to 0 for every |D>. For a
fixed ray, det(w10 beta + w11 alpha)^d = 0 gives the unique axis containing |psi> with multiplicity
d. Both correct.

Interpretation: existence of collapsible states is generic and carries no physics. The content of
SPEC section 12 is that ONE output axis serves a whole cloud of input rays WITH Born statistics.

## 5. What survives a change of output basis

(a) Antipodality is basis-covariant. The theorem in wiki/concepts/outcome-antipodality.md is proved
    for every unitary U with no family restriction. U^(n) = (V^dagger tensor I) U is unitary
    whenever U is, so outcome 0_n and 1_n remain antipodally paired with equal kernel dimensions in
    every output basis.

(b) B1 is invariant under INPUT rotation. With S = sum_j k_j u_j u_j^T and m = sum_j k_j u_j, an
    input rotation R sends u_j -> R u_j, hence S -> R S R^T and m -> R m, so

        n_hat_raw' = (R S R^T)^{-1} R m = R S^{-1} R^T R m = R S^{-1} m = R n_hat_raw

    using R^{-T} = R and R^{-1} = R^T. Therefore n_hat rotates with the cloud and
    B1 = ||n_hat_raw|| is invariant.

(c) B1 is NOT invariant under OUTPUT-basis change, because the cloud is a different point set. B1
    is a function of the output basis: B1 = B1(n).

## 6. The fixed-point condition

Born's rule for a qubit measures the angle from the outcome direction itself:

    P(outcome 0_n | psi) = |<0_n|psi>|^2 = cos^2(theta_n / 2)

with theta_n the Bloch angle between psi and n. SPEC section 5.1's target p_0(Omega) =
cos^2(theta/2) is therefore a Born statement only if theta is measured from the same axis n that
defines outcome 0.

Define Phi : S^2 -> S^2 by Phi(n) = n_hat_fit( C_0(n) ), the axis fitted from the outcome-0 cloud
of the pencil built in output basis n. The preferred basis must satisfy

    Phi(n_*) = n_*

SPEC section 12's uniqueness up to n <-> -n is uniqueness of this fixed point up to outcome
relabelling; its stability requirement is that the fixed point be attracting.

This supplies an algorithm: fixed-point iteration n_{k+1} = Phi(n_k), one pencil solve plus one
3x3 solve per step, rather than a search over S^2.

## 7. Audit of the current implementation

Verified by reading the repository:

- `core/projective_roots.py::forward_pole_root_spectrum(unitary, outcome, **solver_options)` has no
  basis argument and uses (D, -C) for outcome 0 and (B, -A) for outcome 1. That is the lab-frame
  z output basis, hardcoded.
- No caller rotates U first. `scripts/eval_preferred_basis.py` line 161 calls
  `outcome_bloch_cloud(unitary, outcome=0, **PENCIL_SOLVER_OPTIONS)` on the propagator returned by
  `unitary_at_time`, with no basis transformation.
- `core/outcome_measures.py::preferred_axis_from_cloud` then fits n_hat freely from that cloud.
- `wiki/campaigns/preferred-basis-campaign.md` records that ratios are "measured from the *fitted*
  preferred axis, not a lab-frame pole".

So the scoring axis rotates but the pencil's output basis does not. Phi is evaluated once, at
n = z_hat, and its output is not fed back. The fixed-point condition is not imposed. The diagnostic
that would expose this, n_hat . z_hat, is not reported anywhere; the campaign reports
n_hat . h_0_hat.

Note that the estimator cannot detect the mismatch on its own: if a cloud happens to be Born about
some axis other than the pencil's output axis, the l=1 solve returns B1 = 1 at that other axis,
which is not Born's rule for the measurement actually being described.

`wiki/campaigns/commuting-qnd-sector.md` already records the scoped form of this issue for the
QND no-go: "The no-go assumes the $Z$ outcome basis. `SPEC.md` requires the preferred axis to be
identified rather than assumed. For a rotated output basis, even the $h_\perp=0$ dynamics can
sweep a latitude, so the pole conclusions change."

## 8. Campaign numbers quoted for the WP5 reading

All values below are quoted verbatim from `wiki/campaigns/preferred-basis-campaign.md` (WP5 table,
"`h_0` rotated at fixed `|h_0| = 2.9527`, everything else held at `screen_00`") and from the same
file's screen_00 parameter listing. They are that document's numbers, reproduced here for
grounding; no new computation produced them.

WP5 table:

| direction | B1 (N=8) | B1 (N=10) | n_hat . h_0_hat, N=10 (signed) | axis error, N=10 (deg) |
|---|---|---|---|---|
| h_0 || x | 0.0417 | 0.0102 | -0.063 | 86.41 |
| h_0 || y | 0.4485 | 0.4337 | 0.001 | 89.93 |
| h_0 || z | 1.0108 | 1.0233 | 1.0000 | 0.46 |
| screen_00 direction | 1.3018 | 1.1496 | 0.9997 | 1.51 |
| generic 3 | 1.4530 | 1.2078 | -0.994 | 6.30 |

screen_00 qubit self-field, from the same file:

    h_0x = -1.35  h_0y = -1.69  h_0z = +2.01

Derived from those three components: |h_0| = sqrt(1.35^2 + 1.69^2 + 2.01^2) = sqrt(1.8225 + 2.8561
+ 4.0401) = sqrt(8.7187) = 2.9527, consistent with the WP5 header's stated |h_0| = 2.9527; and
h_0_hat . z_hat = 2.01 / 2.9527 = 0.6807, i.e. h_0_hat lies about 47 degrees from z_hat
(arccos 0.6807 = 47.07 deg).

Consequences for the two rows where n_hat . z_hat is recoverable from published numbers:

- h_0 || z: n_hat . h_0_hat = 1.0000 and h_0_hat = z_hat, so n_hat is aligned with the pencil's
  hardcoded output axis (misalignment about 0 deg). B1 = 1.0108 at N=8, 1.0233 at N=10.
- screen_00: n_hat . h_0_hat = 0.9997 and h_0_hat is about 47 deg from z_hat, so the fitted axis is
  about 47 deg from the pencil's output axis. B1 = 1.3018 at N=8, 1.1496 at N=10.

For h_0 || x and h_0 || y only n_hat . h_0_hat is published (-0.063 and 0.001), which confines
n_hat to a plane but does not determine n_hat . z_hat. For "generic 3" the h_0 direction is not
published, so n_hat . z_hat is likewise not recoverable.

## 9. Alternative reading of WP5, and what defeats it

RESEARCH_STATE.md reads the three-point pattern as "pointing at the detector's own distinguished
axis rather than an accident of one cell, though three points is not enough to call this
established."

An alternative reading consistent with the same rows: B1 tracks the misalignment between the fitted
axis and the pencil's hardcoded output axis, so the h_0 || x and h_0 || y "nulls" would be a
mismatched-basis artifact rather than a mechanism. Of the two rows where the misalignment is
computable, the aligned one has B1 = 1.0108 (N=8) and the 47-degree-misaligned one has B1 = 1.3018
(N=8).

This alternative is NOT established and is partly contradicted by the N-trend. At screen_00 the
misalignment is the same 47 degrees at both sizes (h_0 is fixed and n_hat . h_0_hat is 0.9997),
yet B1 falls from 1.3018 at N=8 to 1.1496 at N=10. Misalignment alone therefore cannot explain the
N dependence, so at most it is a confound on the fixed-N ordering, not a complete alternative
explanation.

The two readings separate cheaply: rebuild the pencil with U -> (V^dagger tensor I) U for V
carrying z_hat to the fitted axis, then re-fit. If B1 for h_0 || x falls toward 1, the null was a
basis artifact. If it does not, the detector-axis reading survives a real test.

## 10. Scope

Sections 2 through 6 are derivations and are unconditional: no assumption on the Hamiltonian
family, the dimension, regularity, degeneracy or defectiveness. Section 7 is an audit of code as
read on 2026-09-21. Sections 8 and 9 quote existing campaign numbers and propose a reading; the
reading is a hypothesis, not a result. Nothing here promotes a gate or changes paper_ready.

## 11. Addendum: N=12 centre point (read after sections 8-9 were drafted)

`wiki/campaigns/preferred-basis-campaign.md` carries an N=12 centre measurement newer than the
RESEARCH_STATE.md paragraph quoted above. Its centre table reads:

| N | B1 | axis error (deg) | cond(S) | odd(l=3,5,7)/total | E_2 | E_inf | E_harm | E_marg | quartet coverage |
|---|---|---|---|---|---|---|---|---|---|
| 8 | 1.3018 | 1.548 | 1.83 | 0.2422 | 0.1812 | 0.6831 | 0.3756 | 0.8807 | 1.00 (8x16) |
| 10 | 1.1496 | 1.506 | 1.89 | 0.0909 | 0.1455 | 0.6081 | 0.0419 | 0.3470 | 1.00 (18x36) |
| 12 | 0.8795 | 3.009 | 2.21 | 0.0596 | 0.0500 | 0.1481 | 0.0083 | 0.2217 | 1.00 (18x36) |

with the accompanying text: "`B1` does **not** plateau in `1.05`-`1.15`: it crosses below 1
between `N=10` and `N=12`", and the axis leg violated at N=12
(`n_hat . h_0_hat = 0.99862 < 0.999`).

This bears directly on section 9. At screen_00 the misalignment between the fitted axis and the
hardcoded z output axis is fixed at about 47 degrees across all three sizes, because h_0 does not
move and n_hat . h_0_hat stays near 1. Yet B1 runs 1.3018 -> 1.1496 -> 0.8795, crossing through 1.
B1 is therefore not a function of the misalignment, and the section 9 alternative reading is
demoted: it cannot account for the WP5 pattern on its own, and survives only as a confound on
fixed-N comparisons between cells whose fitted axes sit at different angles to z_hat.

The fixed-point condition of section 6 is unaffected, being definitional rather than explanatory:
a cloud scored about an axis other than the one defining the outcome is not being scored against
Born's rule, whatever sets the value of B1, and that applies to the N=12 point as much as to N=8.

## 12. Correction to section 7: the rotation helper already exists

Section 7's phrase "no caller rotates U first" was too broad and is corrected here.
`scripts/h0_basis_outcome_clouds.py` implements the output-basis rotation directly:

    def rotate_qubit0_output_basis(unitary, direction):
        rotation_dagger = qubit0_pole_rotation(direction).conj().T
        r00, r01 = rotation_dagger[0, 0], rotation_dagger[0, 1]
        r10, r11 = rotation_dagger[1, 0], rotation_dagger[1, 1]
        rotated[:half] = r00 * top + r01 * bottom
        rotated[half:] = r10 * top + r11 * bottom

This is exactly the block law derived in section 2, with w = R^dagger, and is therefore an
independent confirmation of the spinor transformation. Its docstring states the construction in
the same terms: "Left-multiplying the qubit-0 (most significant, per the house tensor-ordering
convention) block of the propagator by ``R^dagger`` therefore redefines the outcome-0/outcome-1
split without touching the initial-state parameterization at all", and it independently notes the
basis-covariance of antipodality: "``R^dagger tensor I`` composed with a unitary ``U`` is itself
unitary, with the same qubit-first block structure, so ... the antipodal-pairing theorem ...
applies to the rotated propagator exactly as it does to the original".

The audit conclusion of section 7 is nevertheless unchanged, and is confirmed by that same
docstring, which states the helper is "Shared by the ad hoc h0-rotation summary figures
(``plot_h0_rotation_summary_figure.py``, ``plot_h0_rotation_summary_figure_ring.py``) only -- not
part of the frozen ``goal_preferred_basis.md`` campaign machinery (``core/outcome_measures.py``,
``scripts/eval_preferred_basis.py``), which is left untouched."

So the correct statement is: the rotation capability exists at script level and is deliberately
excluded from the measurement path, not that it is absent. Closing the fixed-point loop is
therefore a wiring task against existing, already-written code rather than new numerics.

## 13. Quoted strings in plain form

Reproduced without markup so the exact literals used in the compiled article are greppable here.

From scripts/h0_basis_outcome_clouds.py:

not part of the frozen goal_preferred_basis.md campaign machinery, which is left untouched

From wiki/campaigns/commuting-qnd-sector.md:

The no-go assumes the Z outcome basis. SPEC.md requires the preferred axis to be identified rather than assumed.
