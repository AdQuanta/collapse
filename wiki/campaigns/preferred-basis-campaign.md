# Preferred-basis campaign: the strong Born criterion

> Status: **exploratory, no gate credit claimed.** Every number below is `PRELIMINARY_NUMERIC`,
> single seed per Hamiltonian evaluation, no bootstrap on `B1` itself. `paper_ready` remains
> `false`. Nothing here promotes a ledger row; promotion needs a fresh result packet and an
> independent referee under the rule in
> [paper-readiness-ledger.md](../governance/paper-readiness-ledger.md).
> Campaign version: `preferred-basis-v1`
> Started: 2026-09-21, per [goal_preferred_basis.md](../../goal_preferred_basis.md)

## Pre-registered prediction

Recorded 2026-09-21, before any campaign run (see the goal file for the full text): the axis leg
holds, `n_hat . h_0_hat > 0.999`; the exactness leg fails, with `B1` plateauing in `1.05`-`1.15`
rather than at 1.

**Verdict with `N=12` in hand: neither half of the prediction is confirmed as stated.** The axis
leg's threshold is violated at `N=12` (`n_hat . h_0_hat = 0.99862 < 0.999`), after holding at
`N=8`/`N=10`. The exactness leg's specific mechanism was right (`B1` does not reach 1) but its
predicted plateau band was not: `B1` crossed *through* 1 rather than plateauing above it
(`1.302 -> 1.150 -> 0.880`). See WP2 and the falsifier reassessment below for the full picture --
this is a genuine, reported miss on the specifics of a pre-registered prediction, not something to
retrofit as "basically right."

## What is being tested, and how

`goal_preferred_basis.md` asks whether the asymmetry field of the two `SPEC.md` §3 outcome
measures converges to the exact Born form `n_hat . r` with `n_hat = h_0_hat`, over a finite open
region rather than at a point, for the endpoint-chain family in the self-Hamiltonian-dominated
regime (`|h_0| >> max|g|`).

The estimator (`core/outcome_measures.py`) is the closed-form, binning-free preferred axis derived
in the goal file: build the outcome-0 Bloch root cloud (`forward_pole_root_spectrum`, weight
`k_j = 1` per raw root, no kernel-dimension SVD -- infeasible at this size, see below), solve the
`l = 1` vanishing-moment system `S n_hat_raw = m` for the axis, and read `B1 = ||S^-1 m||` as the
dipole-sharpness diagnostic that Born forces to exactly 1. The `SPEC.md` §6 quartet
(`E_2, E_inf, E_harm, E_marg`) is read off `core.gleason_diagnostics` at the fitted axis as a
histogram-based cross-check; the exact mapping used is documented in `spec_quartet`'s docstring
and disclosed again in every result packet.

**Outcome 1 is not independently solved.** Unitarity forces `rho_1 = A_* rho_0` (the antipodal
pushforward) for *every* unitary -- proved in
[outcome-antipodality.md](../concepts/outcome-antipodality.md) and certified on the exact
approved endpoint-chain family by `tests/test_outcome_antipodality.py` and again by
`tests/test_outcome_measures.py::test_antipodal_cloud_matches_independent_outcome_one_solve`.
Deriving outcome 1's cloud this way rather than with a second QZ solve is therefore exact, not an
approximation, and it halves the pencil-solving cost of every measurement -- the difference
between an infeasible and a feasible `N = 12` probe (see WP2). This is unrelated to, and does not
reuse, the separate (and at `screen_00`, invalid: `h_0y != 0`)
[fixed-input/outcome-0 shortcut](../concepts/fixed-input-outcome-equivalence.md); the genuine
outcome-0 forward pencil is always solved.

**Cost-limited kernel weights (goal §4, WP1).** Exact kernel-dimension weights need one SVD per
distinct root (`core/pencil_characterization.py`), `O(n^4)`, infeasible at `n = 4096` (`N = 12`).
Every raw non-indeterminate root from `forward_pole_root_spectrum` is weighted `k_j = 1`; the
pencil's own QZ duplicate-cluster diagnostics (`largest_cluster_multiplicity`,
`distinct_root_count`) are recorded in every packet as the substitute guard, per goal §4. This is
recorded, not silently assumed.

**Fail-closed branch (goal §2.4).** `S` is singular exactly when the roots collapse onto a great
circle or a point -- the degenerate case `RESEARCH_STATE.md` §3 warns satisfies moment relations
vacuously. `preferred_axis_from_cloud` gates on `cond(S) > 1e6` (matching the house
`ILL_CONDITIONED_THRESHOLD` convention) and refuses rather than reports; certified by
`tests/test_outcome_measures.py::test_great_circle_confinement_refuses_rather_than_reports` and
`test_point_confinement_refuses`.

## Model and sign convention

Unchanged from [chain-born-regions.md](chain-born-regions.md): the `SPEC.md` §9.2 endpoint chain,
`connectivity="chain"`, `central_coupling="first"`. The builder carries an overall minus sign, so
code parameters are the negatives of the `SPEC.md` §9 coefficients. `screen_00` region center:

    J_xx = +1.32  J_yy = +2.53  J_zz = +1.10
    h_x  = -1.34  h_y  =  0     h_z  = +1.00
    h_0x = -1.35  h_0y = -1.69  h_0z = +2.01
    g_x  = +0.10  g_y  = +0.05  g_z  = +0.06

Reference axis `h_0_hat = (-0.4572, -0.5723, 0.6807)`, `|h_0| = 2.9527`. Times: the same frozen
six log-spaced points in `[100, 1000]`, pooled across times, never averaged (goal §3).

## Acceptance tests for the estimator (`tests/test_outcome_measures.py`)

`goal_preferred_basis.md` §2.5 specifies an acceptance table of exact `B1` values for
`rho_0 = cos^(2p)(theta'/2) T(Omega)` against an unspecified non-trivial inversion-even envelope
`T`. **That exact table could not be reproduced**: a hand derivation (recorded in the test
module's docstring) shows `B1` at `p != 1` depends on `T`'s quadrupole amplitude, which the goal
text does not give, so no independently chosen `T` regenerates those six numbers. What *is*
provable independent of `T`, and what the tests instead certify:

- at `p = 1` (exact Born), `B1 = 1` and the `l >= 3` odd leakage vanish exactly for *any*
  inversion-even `T`, because `T` cancels from the ratio `rho_0(-Omega)/rho_0(Omega)`;
- for the specific `T` used in the tests (a quadrupole plus a `cos(2 phi)` term, azimuthal content
  restricted to `m in {0, +-2}`), the fitted axis is exact at *every* `p` tested, not only at Born;
- `B1` moves monotonically away from 1 as `p` moves away from 1, in the same direction as the
  goal's own (`T`-specific) table.

All eight tests pass. This substitution is a documented, math-justified limitation, not a silent
deviation.

## WP2 -- size trend at the center

| N | B1 | axis error (deg) | cond(S) | odd(l=3,5,7)/total | E_2 | E_inf | E_harm | E_marg | quartet coverage |
|---|---|---|---|---|---|---|---|---|---|
| 8 | 1.3018 | 1.548 | 1.83 | 0.2422 | 0.1812 | 0.6831 | 0.3756 | 0.8807 | 1.00 (8x16) |
| 10 | 1.1496 | 1.506 | 1.89 | 0.0909 | 0.1455 | 0.6081 | 0.0419 | 0.3470 | 1.00 (18x36) |
| 12 | 0.8795 | 3.009 | 2.21 | 0.0596 | 0.0500 | 0.1481 | 0.0083 | 0.2217 | 1.00 (18x36) |

**`N=12` completed (elapsed 12,593 s, ~3.5 h; `hermiticity_residual=0`, `max_unitary_residual=7.2e-11`,
`cond(S)=2.21` -- well-conditioned, not a fail-closed refusal). The result is decisive, and it is
not the plateau the pre-registration predicted.**

`B1` does **not** plateau in `1.05`-`1.15`: it crosses below 1 between `N=10` and `N=12`
(`1.302 -> 1.150 -> 0.880`), and the decrements *grow* rather than shrink (`-0.152` then `-0.270`)
-- the opposite of the deceleration a genuine plateau would show. Every other diagnostic keeps
improving monotonically and often sharply toward its Born target: odd-`l>=3` leakage
`0.242 -> 0.091 -> 0.060`, `E_2` `0.181 -> 0.145 -> 0.050`, `E_inf` `0.683 -> 0.608 -> 0.148`,
`E_harm` `0.376 -> 0.042 -> 0.008` (a further order of magnitude), `E_marg`
`0.881 -> 0.347 -> 0.222`. **The one diagnostic that got worse is the axis itself**: axis error
`1.548 -> 1.506 -> 3.009` degrees, and `n_hat . h_0_hat` fell to `0.99862`, which is **below** the
pre-registered `> 0.999` threshold for the first time. The axis leg's "already holds strongly"
read from N=8/N=10 alone does not survive N=12: it is still a small angle in absolute terms, but it
moved in the wrong direction, and three points cannot yet say whether that is a genuine trend
(goal §5 falsifier 3, "`n_hat` separating from `h_0_hat` as `N` grows") or a single-point
fluctuation. Reported exactly as found, not smoothed into the earlier framing.

Read together, this is neither the pre-registered plateau (falsifier 1's literal form) nor clean
monotonic convergence to Born: `B1` overshoots past 1 while the harmonic-content and marginal
diagnostics keep improving and the axis wobbles. Two readings are both consistent with three
points and cannot be distinguished here: (a) `B1` is oscillating toward 1 (an overshoot that would
correct at larger `N`, the way an underdamped approach can cross its target before settling), or
(b) `B1` is on a trajectory that will keep moving away from 1 in the other direction, i.e. a
different, non-Born asymptote approached from below. `SPEC.md` §7.3 requires the limit to be
stable against reasonable extrapolation ansätze; three points, one of which already reverses sign
relative to 1, cannot support any extrapolation, so none is attempted here (`chain-born-regions.md`
hit exactly this problem with five points on the weak criterion and still called it undecided).

**`N=12` numerical disclosure.** The known LAPACK issue reoccurred: `On entry to ZHEEVD, parameter
number 10 had an illegal value` printed once during the run (matching
`chain-born-regions.md`'s documented Apple Accelerate `zheevd` defect at dimension >= 4096). The
returned `hermiticity_residual=0.0` and `max_unitary_residual=7.2e-11` and the well-conditioned
`cond(S)=2.21` are consistent with a clean result, and `core/outcome_measures.py`'s own eigensolve
path already falls back to `scipy.linalg.eigh(driver="evr")` on a `LinAlgError` -- but the warning
was not raised as an exception here, so it is disclosed rather than silently treated as harmless;
it should be tracked down (which internal call emits it) before this specific number is used for
anything beyond the preliminary read given here.

**Estimator-robustness disclosure (`SPEC.md` §6.5):** the two independent odd-leakage estimates --
`core.outcome_measures.odd_harmonic_power`'s direct point-measure moment and
`core.gleason_diagnostics`'s histogram-based `E_harm` -- agree in direction and order of magnitude
at every size (both fall sharply with `N`) but not in absolute value (`0.242` vs `0.376` at N=8;
`0.060` vs `0.008` at N=12, now differing by a full order of magnitude). Neither should be read as
more than one significant figure.

**`N=12` cost.** A single time step (detector dimension 4096, full 8192-dimensional propagator):
`eigh` 155.8 s, propagator construction 15.9 s, the outcome-0 QZ pencil solve 1697.8 s in the
initial probe. The full six-time pooled run for this one candidate took 12,593 s (~3.5 h) --
longer than the ~2.9 h probe-based estimate, consistent with running alongside this session's other
(lower-priority) CPU-bound work for part of that window. Against
`wiki/campaigns/chain-born-regions.md`'s `~9 minutes` for the *weak*-only evaluator at the same
`N`, the difference is the generalized (QZ) eigenvalue solve this campaign's genuine outcome
pencil requires, which the weak evaluator's single relative-evolution-operator route
(`solve` + `eigvals`) avoids entirely. This cost is why `N=12` was run only once, at the center,
and why WP3-WP5 do not extend to it.

## WP3 -- region, not point (N=8 and N=10)

**Sampling note, itself a finding.** A first attempt at "eight generic perturbation directions at
20% relative radius" used a single globally-normalized 12-dimensional Gaussian direction. This
rejected *every* candidate: `screen_00` already sits with `h_y = 0` (a currently-inactive
coordinate) and with `max|g| = 0.10` exactly at the perturbative ceiling, so (a) any direction with
an `h_y` component collapses the rule's denominator (the documented failure mode in
`chain-born-regions.md`: "introducing a small term in a currently-inactive direction... collapses
the coupling ceiling"), and (b) a global-norm perturbation applies a wildly disproportionate
*relative* shift to the already-thirty-times-smaller couplings. Both are fixed the same way:
directions are confined to the eleven already-active parameters, each displaced by the stated
radius **times its own magnitude** (not the vector's global norm) -- the only reading of "relative"
under which every parameter is perturbed by the same fraction of itself. This is not a gate change
(the `0.1` ceiling is untouched); it is a sampling-space restriction, disclosed here per CLAUDE.md's
prohibition on adjusting gates after seeing results. Even so, `screen_00` sitting exactly at the
coupling ceiling means roughly half of otherwise-generic active-subspace directions are rejected by
the (unmodified) perturbative rule on sign alone -- itself part of the region's characterization,
not a sampling artifact: **1536** candidates were not needed; 20/48, 17/48, 15/48 pass at 20%/35%/50%
radius over 6 seeds x 8 directions, comfortably above the "at least eight directions" reportability
floor at every radius.

| radius | n passed | B1 mean | B1 sd | B1 min/max | axis err mean (deg) | axis err max (deg) |
|---|---|---|---|---|---|---|
| 20% | 20 | 1.324 | 0.039 | 1.247 / 1.398 | 2.65 | 4.39 |
| 35% | 17 | 1.328 | 0.039 | 1.258 / 1.391 | 3.87 | 7.66 |
| 50% | 15 | 1.349 | 0.070 | 1.227 / 1.447 | 5.29 | 10.41 |

**A genuine finite region at N=8.** `B1` stays in a tight band (`1.32-1.35`) out to 50% radius --
it does not collapse or diverge -- while the axis error degrades gently and monotonically
(`2.65 -> 3.87 -> 5.29` degrees mean). Ranked on the conservative (worst-case) statistic per goal
§4, WP3: the worst `B1` anywhere in the 20% cloud is `1.247`, still well above the pre-registered
plateau ceiling of `1.15`.

**`N=10` region-cloud results, all 20 of 20 directions, 20% radius.** Cost rose sharply at N=10
(each candidate ~550-665s against ~3.4s at N=8 -- both the full-propagator construction and the
outcome-0 QZ pencil solve at detector dimension 1024 dominate).

| n | B1 mean | B1 sd | B1 min/max | axis err mean (deg) | axis err max (deg) |
|---|---|---|---|---|---|
| 20 of 20 | 1.173 | 0.030 | 1.120 / 1.221 | 2.55 | 6.10 |

**The region survives to N=10, tighter in both absolute and relative terms than at N=8.** All
twenty directions land in `1.12-1.22` (sd `0.030` vs `0.039` at N=8), consistent with the center's
own N=8->N=10 trend (`1.302 -> 1.150`). The worst-case (conservative) statistic per goal §4, WP3
is `B1 = 1.221` -- still above the pre-registered plateau ceiling of `1.15`, but the region-mean
(`1.173`) has moved into it. Axis error is essentially unchanged from N=8 (mean `2.65 -> 2.55`
degrees). Two sizes are not enough to read a limit (goal §5 falsifier 1 requires this
distinguished from a genuine asymptote), but nothing here has collapsed, diverged, or separated
from `h_0_hat` as `N` grew -- falsifiers 3 and 4 are not triggered at either size measured.

## WP4 -- weak coupling sweep (N=8 and N=10)

Coupling direction `(g_x, g_y, g_z)/max|g|` held fixed; only the overall magnitude `epsilon` swept.
`screen_00` itself sits at `epsilon = 0.10`, the approved ceiling.

| epsilon | B1 (N=8) | B1 (N=10) | axis err, N=10 (deg) | odd(l>=3), N=10 | E_marg, N=10 |
|---|---|---|---|---|---|
| 0.025 | 1.4255 | 1.4101 | 2.657 | 0.3030 | 1.0557 |
| 0.050 | 1.3778 | 1.3439 | 2.646 | 0.2225 | 0.7574 |
| 0.100 | 1.3018 | 1.1496 | 1.506 | 0.0909 | 0.3470 |

**This is the one dial that can overturn the pre-registered prediction, and at both sizes it
points away from a pure perturbative-regime artifact -- more clearly at N=10 than at N=8.**
`B1`, the odd-`l>=3` leakage, and `E_marg` all move *toward* Born (down) as `epsilon` *increases*
toward the ceiling, monotonically at both sizes -- the opposite of "weaken the coupling and the
family becomes more Born-like." **The N=8->N=10 improvement itself grows with `epsilon`**:
`B1` barely moves at `epsilon=0.025` (`1.4255 -> 1.4101`, `Delta=-0.015`) or `epsilon=0.05`
(`1.3778 -> 1.3439`, `Delta=-0.034`), but drops sharply at the ceiling, `epsilon=0.10`
(`1.3018 -> 1.1496`, `Delta=-0.152`, ten times the weakest-coupling point's improvement). If this
holds at larger `N`, it says the family's approach to Born is *itself* coupling-strength
dependent, not a fixed `N`-only trend independent of `epsilon` -- which argues against reading the
weak-criterion ceiling in `chain-born-regions.md` as a small-`epsilon` perturbative-window
artifact, and suggests instead that the ceiling and the exactness gap here share a coupling-driven
mechanism.

## WP5 -- mechanism and its control (N=8 and N=10)

`h_0` rotated at fixed `|h_0| = 2.9527`, everything else held at `screen_00`.

| direction | B1 (N=8) | B1 (N=10) | n_hat . h_0_hat, N=10 (signed) | axis error, N=10 (deg) |
|---|---|---|---|---|
| `h_0 \|\| x` | 0.0417 | 0.0102 | -0.063 | 86.41 |
| `h_0 \|\| y` | 0.4485 | 0.4337 | 0.001 | 89.93 |
| `h_0 \|\| z` | 1.0108 | 1.0233 | 1.0000 | 0.46 |
| `screen_00` direction | 1.3018 | 1.1496 | 0.9997 | 1.51 |
| generic 1 | -- | -- | -- | REJECTED at both sizes: ratio 0.291 > 0.1 |
| generic 2 | -- | -- | -- | REJECTED at both sizes: ratio 0.181 > 0.1 |
| generic 3 | 1.4530 | 1.2078 | -0.994 | 6.30 |
| generic 4 | -- | -- | -- | REJECTED at both sizes: ratio 0.137 > 0.1 |

Three of the eight rotations are rejected outright: rotating `h_0` away from `screen_00`'s
direction can drive one Cartesian component of `h_0` toward zero, which -- like WP3's sampling
issue -- tightens the perturbative-ratio denominator. This is a genuine physical consequence of
the rotation at fixed magnitude, not a sampling bug, and is left as-is; it does not depend on `N`.

**The `h_0 \|\| x` null (`chain-born-regions.md` item 8: weak-criterion `|d| = 0.079`) is confirmed
not unique to x, and sharpens with N rather than being an accident of one cell.** `h_0 \|\| y` is
equally suppressed at both sizes (`B1 ~ 0.43-0.45`, `n_hat . h_0_hat ~ 0`); `h_0 \|\| x`'s own
suppression strengthens from `B1=0.042` at N=8 to `B1=0.010` at N=10, moving *toward* exactly zero
rather than toward 1. `h_0 \|\| z`, by contrast, sits close to Born at both sizes
(`B1 = 1.011, 1.023`, axis error `0.11, 0.46` degrees) and, notably, does **not** improve with `N`
the way `screen_00`'s own direction and the couplings-strengthened WP4 points do -- it is already
near its own plateau. This points at a mechanism tied to the detector's own distinguished axis
(`h_z = 1.00` is the only nonzero single-site detector field; `J_zz`, unlike `J_xx`/`J_yy`, sits
nearest 1) rather than to an
accident of one cell -- the `N=8 -> N=10` behaviour (the null sharpens, `h_0 \|\| z` does not move)
is itself evidence for a structural rather than accidental effect -- but three suppressed/one
enhanced/one baseline direction is still not enough to call this established as a `SPEC.md` §15.2
mechanism-breaking control; more directions at fixed `N` are needed next.

## Falsifiers (frozen before any run, goal §5)

1. `B1` plateauing away from 1, or decelerating geometrically to a limit excluding 1;
2. normalized `l>=3` odd power not vanishing with `N`;
3. `n_hat` separating from `h_0_hat` as `N` grows;
4. any of the above holding at the center but not across the 20% cloud.

**Decided at the center, undecided across the cloud.** With `N=12` in hand:

1. **`B1` does not plateau away from 1 -- it crosses it.** Falsifier 1's literal form ("plateauing
   away from 1") is not what happened; `B1` moved *through* 1 between `N=10` and `N=12`
   (`1.302 -> 1.150 -> 0.880`) with growing, not shrinking, decrements. This is not the
   pre-registered outcome, and it is not yet distinguishable from "still falsifier 1 but on the
   other side" (a limit below 1) versus a genuine (if unusually large) overshoot toward exact
   convergence. Three points, one of which already reversed sign relative to the target, cannot
   support any extrapolation ansatz (`SPEC.md` §7.3), so none is claimed.
2. **Falsifier 2 (odd `l>=3` power) is not triggered and keeps improving**: `0.242 -> 0.091 ->
   0.060` at the center, monotonically toward zero at every size measured.
3. **Falsifier 3 (`n_hat` separating from `h_0_hat`) has a warning sign, not a clean trigger.**
   Axis error at the center went `1.548 -> 1.506 -> 3.009` degrees; `n_hat . h_0_hat` fell to
   `0.99862`, below the pre-registered `0.999` threshold for the first time. It is a small angle in
   absolute terms and could be a single-point fluctuation rather than a trend, but it moved the
   wrong way, and the earlier "axis leg already holds strongly" framing from `N=8`/`N=10` alone did
   not survive the third point.
4. **Falsifier 4 (center vs. cloud) is untested at `N=12` and cannot be tested locally.** The
   20-direction region cloud (WP3) was only run at `N=8` and `N=10`; a single `N=12` candidate
   already took ~3.5 hours, so the cloud at `N=12` would cost on the order of **70 hours** locally.
   Whether the center's overshoot is shared by the region or is a property of `screen_00` alone is
   an open question this session could not close.

## Scope limit: the fitted axis and the pencil's output basis are not the same object

Every cloud in this campaign is solved in the **lab-frame $\hat z$ output basis**.
`core/projective_roots.py::forward_pole_root_spectrum` takes no basis argument — it uses $(D,-C)$
for outcome 0 and $(B,-A)$ for outcome 1 — and this campaign's path does not rotate the propagator first. (`scripts/h0_basis_outcome_clouds.py::rotate_qubit0_output_basis` does implement the rotation, but its docstring records that it serves two ad hoc figure scripts and leaves this campaign's machinery untouched — so closing the loop is a wiring job, not new numerics.) The fitted
axis `n_hat` is then free, and the §6 quartet is evaluated at it.

Born's rule measures the angle *from the outcome direction itself*, so `SPEC.md` §5.1's
$p_0=\cos^2(\theta/2)$ is a Born statement only when the scoring axis coincides with the axis
defining outcome 0. The preferred basis must therefore be a **fixed point** of
$\Phi(\mathbf n)=\hat{\mathbf n}_{\rm fit}(\mathcal C_0(\mathbf n))$, and this campaign evaluates
$\Phi$ once, at $\mathbf n=\hat z$, without feeding the result back. Changing the output basis is
not a rotation of the cloud: it replaces $U$ by $(V^\dagger\otimes I)U$ and yields a pencil on
independent linear combinations of all four blocks, so both the roots and the detector kernels
change. See [[collapsible-basis-dependence]] for the derivation.

Two practical consequences. First, `n_hat . z_hat` is the alignment the Born reading requires and
is not reported anywhere here; `n_hat . h_0_hat` is reported instead. At `screen_00`
($h_{0x}=-1.35$, $h_{0y}=-1.69$, $h_{0z}=+2.01$, so $\hat{\mathbf h}_0\cdot\hat z=2.01/2.9527=0.6807$)
the fitted axis sits about $47^\circ$ from the pencil's output axis at every size measured.
Second, the estimator cannot detect the mismatch unaided: a cloud that is Born about some *other*
axis returns `B1 = 1` at that axis, which is not Born's rule for the measurement being described.

This does **not** explain the WP5 ordering or the centre trend — `B1` runs
$1.3018\to1.1496\to0.8795$ at $N=8,10,12$ while the misalignment stays fixed at about $47^\circ$,
so `B1` is not a function of it. The point is definitional rather than explanatory, and it applies
to the $N=12$ point below as much as to $N=8$. Closing the loop costs one extra pencil solve per
iteration.

## Honest summary (N=8, N=10 complete; N=12 at the center only)

The picture is more complicated than the `N=8`/`N=10` interim read suggested, and the complication
is itself the most important result of this run. Every histogram/harmonic-content diagnostic
(`E_2`, `E_inf`, `E_harm`, `E_marg`, odd-`l>=3` leakage) improved monotonically and often sharply
across all three sizes, consistent with a genuine approach to the strong Born criterion. But the
two diagnostics the hypothesis is actually framed around behaved differently from that clean
story: `B1` overshot past 1 rather than approaching it from above, and the axis alignment --
called "already holding strongly" after two sizes -- got measurably worse at the third, dropping
just below the pre-registered threshold. Neither of these is a clean falsification (`B1` moving
through 1 is not the same as plateauing away from it; a `3` degree axis error is still small), and
neither is a clean confirmation. **The honest statement is that three sizes, with a reversal in the
trend's sign relative to the target, are not enough to call this converging, plateauing, or
diverging**, and the goal's own extrapolation-stability requirement (`SPEC.md` §7.3) is explicitly
not satisfiable on three points where one already crosses the target. The weak-coupling sweep
(`N=8`, `N=10` only) still argues against reading any of this as a purely perturbative-coupling
artifact: the size-improvement in `B1` scaled with coupling strength, not against it. The
mechanism-rotation control (`N=8`, `N=10` only) still shows the `h_0 \|\| x`/`y` null sharpening
with `N` while `h_0 \|\| z` does not move. **Next**, in priority order: (1) understand the
recurring `ZHEEVD` warning at `N=12` well enough to rule it out as the source of the axis-error
increase before treating that increase as physical; (2) a fourth size point (`N=14`, per the
goal's own contingency, likely on Zeus given the `N=12` cost) to see which side of `B1=1` the trend
settles on, if either; (3) if resources allow, at least one off-center `N=12` point to speak to
falsifier 4.

## Reused machinery, not redesigned

Figures reuse `_plot_angular` (`scripts/build_network_wd_nonborn_size_spacing_figures.py`) and
`_plot_ratio` (`scripts/plot_hz0_0_ring_spacing_born_catalog.py`) exactly as
`chain-born-regions.md`'s own diagnostics do, in Helvetica Neue. The angle plotted is `theta'`
measured from the *fitted* preferred axis, not a lab-frame pole; `_plot_ratio`'s legacy
`S_Born`/`RMSE` text-box fields hold `B1` and the occupied-bin RMSE against `cos^2(theta'/2)`
here, disclosed at the call site and in every packet's `metadata.json`
(`scripts/plot_preferred_basis_diagnostics.py`, `scripts/export_preferred_basis_profile.py`).

## Artifacts

- Estimator: `core/outcome_measures.py`; acceptance tests `tests/test_outcome_measures.py`
- Campaign evaluator: `scripts/eval_preferred_basis.py` (contract tests
  `tests/test_eval_preferred_basis.py`); batch runner
  `scripts/run_preferred_basis_campaign.py`; candidate generator
  `scripts/generate_preferred_basis_candidates.py`
  (`batches/preferred_basis_wp3.json`, `_wp4.json`, `_wp5.json`)
- Append-only log: `reports/preferred_basis/experiment_log.jsonl`
- Profile export/plot: `scripts/export_preferred_basis_profile.py`,
  `scripts/plot_preferred_basis_diagnostics.py`
- Bloch-sphere point-cloud figures (pooled and per-evolution-time, sphere drawn as a light
  three-great-circle contour, no wireframe grid or filled surface): `scripts/
  plot_preferred_basis_bloch_sphere.py --profile <dir> [--per-time]`, reading the raw
  `points_0`/`points_1`/`n_hat` arrays a current `export_preferred_basis_profile.py` run writes
  into `results.npz`. `screen_00` figures are under `reports/preferred_basis/screen_00_N{8,10}/`.
  A separate ad hoc script, `scripts/plot_h0_directions_bloch_sphere.py --family {xxz,xyz}`,
  sweeps `h_0`'s direction (x/y/z/(1,1,1) at fixed `|h_0|`, no perturbative-ratio gate applied) on
  either the XXZ tier-3 cell or the general XYZ `screen_00` cell and plots each direction's
  per-time clouds; output under `reports/preferred_basis/{xxz,xyz}_h0_directions/`. Notably,
  `h_0 || z` on the **XXZ** cell (`J_xx = J_yy`) collapses every root to a single point per label
  -- exact total-`Z` conservation, the same degenerate limit `chain-born-regions.md` item 1
  documents -- while the same direction on the general **XYZ** cell (`J_xx != J_yy`, no residual
  `U(1)`) does not collapse and instead gives the sweep's best axis alignment (`B1 = 1.011`),
  confirming the collapse is a symmetry of the anisotropy, not an artifact of the direction itself.
- **One-figure summary of the `h_0`-rotation phenomenon**:
  `scripts/plot_h0_rotation_summary_figure.py`
  (`reports/preferred_basis/h0_rotation_summary_figure.pdf`). A 19-point sweep of `h_0`'s polar
  angle `theta` away from `z` on the XXZ cell (representative of the full rotation because
  `J_xx = J_yy` gives a residual axial symmetry -- `h_0 || x` and `h_0 || y` give identical `B1`)
  shows the trend is **not monotonic**: `B1` rises smoothly from the `theta=0` collapse through
  exact Born near `theta=5 deg` to a peak of `1.54` at `theta=65-70 deg`, overshooting Born by
  more before falling sharply to the suppressed null (`B1=0.44`) at `theta=90 deg`. This refines
  the coarser four-direction (x/y/z/(1,1,1)) picture above: the richest alignment is not at the
  space-diagonal direction but at a specific off-axis angle closer to the plane.

## Out of scope (goal §6)

No further `S_Born`-style maximization was run; no Hamiltonian family beyond the approved endpoint
chain was added; no ledger gate is promoted; no verifier was activated; no prior curated campaign
data was overwritten.
