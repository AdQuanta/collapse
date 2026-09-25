# Go/No-Go Theorem for Born-Profile Stable Regions

> Sources: Go/no-go derivation workflow (work packages WP1-WP5 and referee), 2026-09-24
> Raw: [Ring h0z = hz study](../../raw/campaigns/2026-09-24-ring-h0z-eq-hz-sqrtN-study.md); [Brief](../../raw/campaigns/2026-09-24-born-gonogo-brief.md); [WP1 exact classes](../../raw/campaigns/2026-09-24-born-gonogo-wp1-exact-no-go-classes.md); [WP2 weak-coupling axis](../../raw/campaigns/2026-09-24-born-gonogo-wp2-weak-coupling-axis.md); [WP3 ring resonant regime](../../raw/campaigns/2026-09-24-born-gonogo-wp3-ring-resonant-regime.md); [WP3 referee](../../raw/campaigns/2026-09-24-born-gonogo-wp3-math-referee.md); [WP4 endpoint chain](../../raw/campaigns/2026-09-24-born-gonogo-wp4-endpoint-chain.md); [WP5 go requirements](../../raw/campaigns/2026-09-24-born-gonogo-wp5-go-requirements.md)
> Updated: 2026-09-24

**Status:** In progress. Derivations by work-package agents with bornkit numerics at `N <= 10`; only WP3 has been refereed (mathematics lens). **No gate is promoted and `paper_ready` remains `false`.** Every item below carries its own status label; `PROVED` here means a complete argument written in the linked raw report, not frozen-verifier credit.

## Overview

The programme asks when an open, stable region of the approved ring and endpoint-chain families gives Born statistics of projective roots, in the SPEC order `N -> infinity` then `T -> infinity`, at weak coupling. The answer so far is **no-go for exact Born in every controlled regime**, with one mechanism shared by both geometries: the on-shell (energy-conserving) part of the weak-coupling dynamics grades the outcome pencil and pins the collapse law to the pole of the qubit's own energy axis, so the very processes that relax the qubit do not spread it; only off-shell processes move roots. The closest approach is the resonant ring `h0z = hz` with `g_x/sqrt(N)` and an interacting detector, whose late-time weak ratio sits within about 0.05 of Born with full coverage but carries a residual resolved at `N = 14`: an approximately Born-like plateau on a resonance manifold, confined to a sliver of width of order `g` around `h0z = hz` (N = 14 perturbation cloud); `N = 16, 18` pending on Zeus. The consolidated statement is in `research_reports/BORN_GONOGO_THEOREM_2026-09-24.md`.

## Exact tools

- **Log-potential identity** [PROVED, VERIFIED_NUMERICALLY]: `rho0 = (1/4pi)[1 + Lap_S L1]`, `L1 = (1/d) log det E1(Omega)`, with `E1` the detector-side outcome-1 effect. Born with uniform prior is equivalent to `L1 = c - (1/2) n.Omega` ("logit-linearity"); a scalar `E1` gives the aberration law, never Born. See the brief §2.1.
- **Generalized charge grading (GCG)** [PROVED, WP4 P4.12a; WP3 P1]: if `[H, c(a.sigma_0) + Q_D] = 0` for real `c != 0` and any Hermitian `Q_D`, every outcome-0 root sits at `+a` in basis `a`, for every `N` and `T`. This covers pointer-QND (`Q_D = 0`), charge conservation, and energy grading (`Q_D = H_D`).
- **Graded-RWA theorem** [PROVED, WP3 P1]: the secular (rotating-wave) part of the dynamics on any resonance is exactly graded, so its law is a delta at the qubit-energy pole.
- **Counter-rotating gauge identity** [PROVED, WP3 P2; confirmed by referee]: for detectors conserving `M = sum Z_i`, roots scale exactly as `sqrt(kappa)` in the counter-rotating fraction `kappa = (g_x - g_y)/(g_x + g_y)` at every order, `N` and `T`. Grading breaking is amplified only as a square root, not as a Jordan-block `eps^(1/N)`.
- **Covariance lemma** [PROVED, WP1 P1]: a product symmetry makes the root-measure family covariant; a unique fixed point must be symmetric, and every continuous qubit-side symmetry is a GCG charge, so continuous symmetry and nondegenerate Born are incompatible.

## Exact no-go classes (WP1 master table)

No open Born region contains a point of: the QND/cone class `[H, a.sigma_0] = 0` (Theorem C and R10 transferred to every axis); the charge-graded patterns (`|g_b| = |g_c|` with an axially symmetric detector and field, the chain's staggered lines, the isotropic case); the commuting-detector classes; the Ising chain with `h_D` parallel to `z` (four atoms, `N`-independent); the matchgate chain (one radius per time). The ring tiers are excluded only on closed positive-codimension sets; their generic interior is the residual. Under SPEC's `1/N` ring scaling the law is the decoupled delta, unconditionally in the QND/charge/commuting classes and otherwise conditional on a log-tail hypothesis.

## The generic interior

- **Preferred axis** [WP2]: for `|h0| >> g` it is the qubit field `h0_hat` up to `O(g^2)` (centroid) or `O(g)` (dipole fit), for kinematic reasons; the detector field enters only at second order. Only at `h0 = 0` does the axis follow the coupling-weighted detector field `g o h_D`, not `h_D`. The goal's premise that the axis aligns with the detector field is false at `screen_00`.
- **Off resonance** [WP2 P2.4, PROVED-CONDITIONAL]: the root cloud in the self-consistent basis is an `O(g/delta)` cap uniform in `T` up to times of order `delta/g^2`; a degenerate pass.
- **Ring on resonance** [WP3 P3, P8]: the bulk is a `sqrt(g/omega)` polar cap with a power-law south tail, tending to the pole as `g -> 0`; the self-consistent basis is repelling there (WP3 P6).
- **Chain** [WP4]: golden-rule relaxation does not spread roots, because the secular dynamics is energy-graded. In SPEC-order numerics the qubit depolarizes while the collapse law stays a cap (P4.13). The campaign's `S_Born` plateau and `B1` trend are reverse-order, lab-basis objects (P4.15).
- **Classical-noise reduction** [REFUTED for root laws, WP3 P4 and WP4 P4.12c]: it reproduces trace quantities but not the root law, which sees the geometric mean of forward and backward filters.

> **Status: Disputed** (referee of WP3, 2026-09-24)
> WP3's verdict P8 argued "the law tends to a delta as `g -> 0`, hence not Born". The referee gave an explicit exactly-Born family with full support that also converges to a delta, so concentration alone does not exclude Born. The verdict is downgraded to HEURISTIC until a ratio-defect (fluctuation-relation) argument replaces it. The leading-order Dicke law is the rigorous template: it is never weak-Born.

## Focus case: ring with `h0z = hz` and `g_x/sqrt(N)` (user-specified, 2026-09-24)

Model: `H = h0z s0^z + hz sum s_i^z + J sum s_i^z s_{i+1}^z + (gx/sqrt(N)) s0^x sum s_i^x`, `h0z = hz = 1`, all other terms zero; Tier 1 on the `m = 0` resonance. Parity `Z0 prod Z_i` makes `z` an exact fixed point of the axis map. The secular (on-shell) dynamics conserves `H_0` and is therefore exactly graded (delta law); only off-shell terms move roots. `|J| = |hz|` is a double resonance (the pair-flip channel of `m = -+2` sites also becomes on-shell), still graded by `H_0` in the secular approximation. Exact sector methods: collective-spin sectors at `J = 0` up to `N = 400`; detector-momentum sectors for `J != 0` up to `N = 14`, cross-checked against dense roots to `6.583622536027178e-12`.

- **`J = 0` (non-interacting control)** [NUMERICAL, exact sectors]: the `N`-first law at fixed `T` converges in `N` and is pole-concentrated (median polar angle about 0.1-0.7 rad), oscillating in `T` with no late-time limit; the 18-bin ratio error is smallest near `tau = g T ~ 1` (e.g. `E=0.057` at `N = 320`, `g = 0.05`) and larger at `tau = 2, 5`. No Born region.
- **`J != 0` at late times** [PRELIMINARY_NUMERIC, `N <= 12`; `N = 14` running]: at `tau = 10-100` the law is still pole-concentrated but has full 18-bin polar coverage and is nearly azimuthally uniform, and its weak ratio **approaches the Born ratio as `N` grows**. With exactly degenerate roots counted once, the north-half binomial chi-square is `12.2`, `13.0`, `8.5` on 9 bins at `N = 10` (`tau = 10, 30, 100`) and `15.1`, `26.2`, `19.2` at `N = 12`, while the ratio error falls from about 0.15-0.17 to 0.05-0.09. This is the first observation in the programme pointing toward a **weak-Born limit with a concentrated law**, the scenario the WP3 referee showed is not excluded. It is not yet a trend claim. The same holds across the weak-coupling window at `N = 12`: for `g = 0.05` and `0.2` the deduplicated ratio error is `0.118`, `0.091`, `0.124` and `0.062`, `0.052`, `0.075` (`tau = 10, 30, 100`), with chi-square `32.9`, `19.6`, `23.5` and `18.0`, `17.0`, `24.2` on 9 bins: a small but resolved residual, concentrated where the ratio exceeds Born at mid-northern latitudes. Whether it keeps shrinking with `N` or saturates decides between a weak-Born limit and a near-Born crossover.

- **Resolution for `h = 1`, `J = 0.37`, `g = 0.1`** [NUMERICAL, exact sectors, `N = 14`]: the trend stops. The ratio error stays near 0.06 (`E=0.066`, `0.055`, `0.079` at `tau = 10, 30, 100`) and the deduplicated chi-square is `121.1`, `101.5`, `155.3` on 9 bins, a resolved residual from a systematic excess over Born at mid-northern latitudes. This parameter set is a **near-Born plateau, not a Born limit**.
- **User parameters `h0z = hz = 0.1`, `J = 1`, `gx = 0.01`** [PRELIMINARY_NUMERIC, `N = 10, 12`; `N = 14` local, `N = 16, 18` on Zeus]: at late times the `N = 12` ratio is statistically consistent with Born (chi-square `13.1` and `7.6` on 9 bins at `tau = 10, 30`, i.e. `T = 1000, 3000`) and the Born calibration `E tan^2(theta/2)` is `0.92` and `0.997`, against exactly 1 for Born; at `tau = 3` it is not (`98.2`). The previous parameter set looked equally good at `N = 12` and failed at `N = 14`, so no claim is made before the larger sizes.

- **User parameters at `N = 14`** [NUMERICAL]: the residual is resolved (chi-square `117.6` and `104.7` on 9 bins at `tau = 10, 30`) with ratio error `0.070` and `0.045`; same mid-northern excess over Born as the other set.
- **Perturbation cloud at `N = 14`** [NUMERICAL]: the near-Born plateau is insensitive to `J` (`J = 0.8`, `1.2`: `E=0.050`-`0.073`) and to `gx` (`gx = 0.007`, `0.013`: `E=0.039`-`0.080`), but detuning `h0z` to `0.103` or `0.097` (a shift of 0.003, below the coupling scale) raises the ratio error to `0.217`-`0.231` and removes the south mass, and at `h0z = 0.11` or `0.09` the law collapses to a polar cap covering 8-10 of 18 bins. **The plateau lives on a sliver of width of order `g` around the resonance manifold `h0z = hz`**, which shrinks as `g -> 0`: a fine-tuned codimension-one structure in the sense of SPEC §13, not an open region.

- **User parameters at `N = 16`** [NUMERICAL, Zeus, 9 sectors hash-validated]: at late times the plateau persists (`E=0.065`, `0.064` at `tau = 10, 30`) with the residual overwhelmingly resolved (chi-square `908.1`, `918.8` on 9 bins), so the late-time law does not converge to Born. At the intermediate time `tau = 3` (`T = 300`) the ratio error falls steadily with `N` (0.046, 0.045, 0.030, 0.020 at `N = 10`-`16`) and the calibration is `1.07`; this is a finite-time near-Born crossover on the resonance sliver, not the `T -> infinity` limit the SPEC order requires. `N = 18` queued on Zeus.

## What a go would require (WP5)

A strong go needs, among other things (Theorem N): no exact grading or cone symmetry; a Jensen gap above a sharp floor (`G_* = 0.08198` for the uniform-prior Born law, 1/2 if the channel fully depolarizes), which is necessary but not sufficient, since exactly graded delta laws have `G = 1.69-1.70`; logit-linearity; an attracting fixed point; and coverage. **Exact Born is achievable by unitary ensembles**: classical-label ensembles (`log(4/3)` Jensen gap) and a unitarily invariant R-diagonal ensemble whose cosine-sine law has mean pole flip probability `1/phi^2`. It is a single, finely tuned cosine-sine law, not an attractor of weak coupling, of graded secular dynamics or of full scrambling. The martingale route does not apply: exact zero drift is pointer-QND and gives a delta.

## Open items

- A ratio-defect replacement for the concentration argument (WP3 P8, and the analogous steps in WP2 and WP4).
- The SPEC-order `T -> infinity` law of gapless interacting chains beyond `T1`.
- Log-tail control of the large-`N` limit (all families).
- Refereeing of WP1, WP2, WP4 and WP5.

## See Also

- [Commuting/QND sector](commuting-qnd-sector.md)
- [Preferred-basis campaign](preferred-basis-campaign.md)
- [Endpoint-chain Born regions](chain-born-regions.md)
- [Basis dependence of collapsible states](../concepts/collapsible-basis-dependence.md)
- [Theorem targets](../concepts/theorem-targets.md)
