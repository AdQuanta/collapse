# Go/No-Go Theorem for Born-Profile Stable Regions in the Ring and Endpoint-Chain Families

Research report, 2026-09-24. **No paper-readiness gate is promoted; `paper_ready` remains `false`.**
Branch `born-gonogo-theorem`. Evidence: `raw/campaigns/2026-09-24-born-gonogo-*.md` (brief, work packages WP1-WP5,
WP3 referee) and `raw/campaigns/2026-09-24-ring-h0z-eq-hz-sqrtN-study.md` (focus-case numerics). Wiki:
`wiki/campaigns/born-gonogo-theorem.md`.

Status labels: **PROVED** (complete argument in the cited raw report), **PROVED-CONDITIONAL** (complete modulo a named
hypothesis), **HEURISTIC**, **NUMERICAL** (finite-N evidence), **CONJECTURE**. Only WP3 has had an independent
referee; the other work packages are single-author derivations with their own numerical checks.

---

## 0. Answer in one paragraph

In every weak-coupling regime of the approved ring and endpoint-chain families that could be controlled, the
projective-root law does **not** converge to an exact Born profile in the SPEC order (`N -> infinity`, then
`T -> infinity`). The obstruction is a single mechanism shared by both geometries: **energy conservation grades the
outcome pencil.** The on-shell (secular) part of the weak-coupling dynamics conserves `H_0 = H_q + H_D`, and any
conserved `c(a.sigma_0) + Q_D` forces every outcome-0 root onto the pole `+a` exactly. The processes that relax the
qubit are on-shell, so relaxation does not spread the collapse law; only off-shell (energy-counter-rotating)
processes move roots, by an amount set by `g/omega`. The self-consistent preferred axis is the qubit's own field
axis `h0_hat` (for `|h0| >> g`), selected kinematically, not the detector field. The one place where the weak Born
ratio comes close is the resonant ring studied at the user's request (`h0z = hz`, `g_x/sqrt(N)`, interacting Ising
detector): at late times the ratio sits within about 0.05 of Born with full polar coverage, but a systematic
residual is resolved at `N = 14`, and a 3% detuning of `h0z` destroys it. That is an **approximately Born-like plateau
confined to a resonance manifold of width of order `g`**, not an open Born phase. Exact Born is not forbidden by unitarity itself: explicit unitary ensembles achieve it, but only at a
single finely tuned cosine-sine law that no weak-coupling, graded or scrambling mechanism in these families selects.

## 1. Setting, definitions, and what counts as a "go"

`H = h0.sigma_0 + sum_i h.sigma_i + sum_bonds (J_xx XX + J_yy YY + J_zz ZZ) + H_qD`; ring
`H_qD = sum_a g_{a,N} sigma_0^a sum_i sigma_i^a` (scaling stated per result), chain `H_qD = sum_a g_a sigma_0^a sigma_1^a`.
Outcome pencils `(U10 + lambda U11) D = 0` and `(U00 + lambda U01) D = 0`; `lambda = e^{i phi} tan(theta/2)`.

**Nondegenerate Born profile** (WP1 §1; referee of WP3). A delta at a pole, a polar cap of radius `eps` and an
equatorial atom satisfy the Born ratio vacuously or to `O(eps^2)`. A "go" therefore requires the Born identity
**plus coverage**: the polar support of `rho0 + rho1` is `[0, pi]` (weak) or the support is `S^2` (strong), in an
open parameter region, at an attracting fixed point `Phi(n*) = n*` of the preferred-axis map
(`wiki/concepts/collapsible-basis-dependence.md`). Concentration alone does not exclude Born: the WP3 referee gave
an exactly Born, fully supported family that converges to a delta. Every no-go below is therefore stated through
symmetry, grading or a measured ratio defect, not through concentration.

## 2. Exact tools (PROVED)

1. **Antipodality** (repository, PROVED): `rho1` is the antipodal image of `rho0` in every output basis, so strong
   Born is `rho0(-Omega) = tan^2(theta/2) rho0(Omega)` and the weak ratio is `P(theta)/(P(theta)+P(pi-theta))`.
2. **Log-potential identity** (brief §2.1; checked to about 1e-6 per harmonic up to `l = 4`):
   `rho0 = (1/4pi)[1 + Lap_S L1]`, `L1 = (1/d) log det E1(Omega)`, with `E1` the detector-side outcome-1 effect.
   Strong Born with an inversion-uniform even part is equivalent to `L1 = c - (1/2) n.Omega` ("logit-linearity").
   A scalar `E1` gives the aberration law `(1 - m^2)/(4pi (1 - m cos theta)^2)`, never Born for `0 < |m| < 1`.
   Weak Born is the detailed fluctuation relation `P0(-x) = e^{2x} P0(x)` for `x = log tan(theta/2)`; its integral
   form is `E_{rho0}[tan^2(theta/2)] = 1`.
3. **Generalized charge grading, GCG** (WP4 P4.12a; WP3 P1): if `[H, c(a.sigma_0) + Q_D] = 0` for real `c != 0` and
   any Hermitian detector operator `Q_D`, then `det(U10^(a) + lambda U11^(a)) = lambda^d det U11^(a)` in basis `a`, so
   every outcome-0 root sits at `+a`, for every `N` and `T`. Special cases: pointer-QND (`Q_D = 0`), charge
   conservation, and energy grading (`Q_D = H_D`).
4. **Graded-RWA theorem** (WP3 P1): the secular part of the dynamics on any resonance, for any detector and any
   tilt of `h0`, conserves `H_0` and so has an exact delta law at the qubit-energy pole.
5. **Counter-rotating gauge identity** (WP3 P2; referee: confirmed at operator level to 1e-13): for detectors
   conserving `M = sum Z_i`, roots scale exactly as `sqrt(kappa)` in `kappa = (g_x - g_y)/(g_x + g_y)` at all orders
   in `g`, `N` and `T`. Grading breaking is amplified only as a square root, not as a Jordan-block `eps^{1/N}`.
6. **Covariance lemma** (WP1 P1): a product symmetry makes the root-measure family covariant; a unique fixed point
   must be symmetric; every continuous qubit-side symmetry is a GCG charge, so continuous symmetry and
   nondegenerate Born are incompatible.
7. **Light-cone limit for the chain** (WP4 P4.1-P4.5): at fixed `T` the finite-`N` chain equals a light-cone
   unitary times spectators up to an exponentially small error; the `N`-first law exists modulo a light-cone-local
   log-tail hypothesis (H1).

## 3. Theorem 1 — exact no-go classes (PROVED; WP1 master table)

No open Born region, in either geometry and at any coupling scaling, contains a point of:
- **QND/cone class** `[H, a.sigma_0] = 0` for `a in {x, y, z}`: roots on the cone `a.Omega = a.n` in every output
  basis `n`; strong Born fails everywhere; Theorem C and R10 exclude open sets in the perpendicular bases.
- **Charge-graded class** (`|g_b| = |g_c| != 0`, detector and fields symmetric about the third axis, the chain's
  staggered lines, the isotropic case): delta law at the forced axis.
- **Commuting-detector classes** B, D, E, H of the repository.
- **Ising chain** with `h_D` parallel to `z` (chain analogues of Tiers 1-3): four atoms per time, `N`-independent.
- **Matchgate (free-fermion XY) chain**: one radius per time.

Under SPEC's `1/N` ring scaling the `N`-first law is the decoupled delta: unconditionally in the QND, charge-graded
and commuting classes, and conditionally on log-tail control elsewhere (WP1 P8). The generic interior of the ring
tiers (open and dense) is not covered by Theorem 1; it is the subject of Theorem 2.

## 4. Theorem 2 — the weak-coupling interior (PROVED-CONDITIONAL / HEURISTIC / NUMERICAL)

1. **Preferred axis** (WP2 P2.1, P2.5, P2.6). For `|h0| >> g` the fixed point of `Phi` is `h0_hat + O(g^2)`
   (centroid) or `+ O(g)` (dipole fit), for kinematic reasons: in its own basis the free precession leaves
   `h0_hat` fixed. The detector field enters only at second order, through the cross-correlation of flip and
   longitudinal channels. Only at `h0 = 0` does the axis follow the coupling-weighted detector field `g o h_D`
   (not `h_D`). **The goal's premise that the axis aligns with the detector field is false** at `screen_00`, where
   the recorded 1.5-3 degree alignment with `h0_hat` is the free-precession cone (cone lemma, `B1_kin = 1.469`).
2. **Off resonance** (WP2 P2.4, PROVED-CONDITIONAL on first-order non-resonance): in the self-consistent basis the
   root cloud is an `O(g/delta)` cap uniform in `T` up to `T ~ delta/g^2` (longer under higher-order
   non-resonance): a degenerate pass that fails coverage.
3. **Ring on resonance** (WP3 P3, P6, P8; HEURISTIC after referee): the secular part is exactly graded; the
   counter-rotating part moves roots by `sqrt(g/omega)`; the bulk is a `sqrt(g/omega)` cap with a power-law south
   tail. The self-consistent basis is repelling on the resonance set. See §5 for the ratio measured in the focus
   case.
4. **Chain in the SPEC order** (WP4 P4.8-P4.15): the qubit depolarizes on the golden-rule time `T1` while the
   collapse law stays a cap well past `T1`, because the secular dynamics is energy-graded (GCG); gapped couplings
   give `O(g/Delta)` caps for all `T`. The campaign's `S_Born` plateau, deficit and `B1` trend at `screen_00` are
   reverse-order, lab-basis objects (finite-chain equilibration beyond the Heisenberg time).
5. **Classical-noise reduction fails for root laws** (WP3 P4, WP4 P4.12c): it reproduces trace quantities such as
   the qubit channel, but the root law depends on the geometric mean of forward and backward filters and on exact
   grading, which no two-point description captures.

## 5. Focus case — resonant Ising ring, `h0z = hz`, `g_x/sqrt(N)` (NUMERICAL, exact sectors)

`H = h0z s0^z + hz sum s_i^z + J sum s_i^z s_{i+1}^z + (gx/sqrt(N)) s0^x sum s_i^x`, `h0z = hz`. Parity
`Z0 prod Z_i` makes `z` an exact fixed point of `Phi`. `h0z = hz` is the `m = 0` member of the first-order
resonance set `|h0z| = |hz + m J|`, `m in {-2, 0, 2}`, so **it is neither necessary nor sufficient** for anything
Born-like: it is one codimension-one resonance among several, and on it the secular law is an exact delta.

Computation: detector-momentum sectors via `SinglePixelHamiltonianQuSpin` and the local relative-evolution path of
`DisentanglementAnalyzer.from_sectors` (`scripts/ring_h0z_eq_hz_sector_roots.py`, test
`tests/test_ring_h0z_eq_hz_sector_roots.py`); collective-spin sectors for `J = 0` up to `N = 400`. Single times,
no pooling, `z` output basis, unit root weights. Statistics count each momentum class and each parity pair once.

- **`J = 0` control**: pole-concentrated law, `N`-convergent at fixed `T`, oscillating in `T`; no Born region.
- **`h = 1`, `J = 0.37`, `g = 0.1`**: the late-time (`tau = gT = 10-100`) ratio error falls from about 0.15 at
  `N = 10` to about 0.06 at `N = 12` and then **stays at about 0.06 at `N = 14`**, with a resolved residual
  (north-half chi-square about 100-155 on 9 bins).
- **User parameters `hz = h0z = 0.1`, `J = 1`, `gx = 0.01`**: at `T = 1000` and `3000` the `N = 12` ratio is
  consistent with Born, but at `N = 14` the residual is resolved (chi-square `117.6` and `104.7` on 9 bins) while
  the error stays at about 0.05-0.07; the excess over Born sits at mid-northern latitudes in every case.
  At `N = 16` (Zeus, 9 sectors hash-validated) the late-time plateau persists (ratio error 0.065, 0.064 at
  `T = 1000, 3000`; chi-square about 910 on 9 bins), so the late-time law does not converge to Born. At the
  intermediate time `T = 300` (`tau = 3`) the error falls steadily with `N` (0.046, 0.045, 0.030, 0.020 for
  `N = 10`-`16`, calibration 1.07): a finite-time near-Born crossover, not the SPEC-order late-time limit.
  `N = 18` is queued on Zeus (job `4701702[]`).
- **Perturbation cloud at `N = 14`** about the user point: the plateau is insensitive to `J` (+-20%, ratio error
  0.050-0.073) and `gx` (+-30%, 0.039-0.080), but a 3% detuning of `h0z` (0.003, below the coupling scale) raises the
  error to 0.22 and removes the south mass, and a 10% detuning collapses the law to a polar cap (8-10 of 18 bins
  covered). The plateau therefore lives on a sliver of width of order `g` around the resonance manifold
  `h0z = hz`, which vanishes as `g -> 0`.

Reading: an approximately Born-like weak ratio with full coverage and a small, systematic residual at the largest
sizes computed; the strong criterion is favourable only in that the late-time azimuthal second harmonic is small
(about 0.03). By `SPEC.md` §7.3 and §24 this is at most an "approximately Born-like" regime, and the cloud shows it is
tied to the resonance manifold: it fails SPEC §13 (a fine-tuned lower-dimensional manifold, hard-FAIL condition 2)
independently of how the residual behaves at larger `N`.

## 6. Theorem 3 — what a go requires, and existence (WP5)

**Necessary conditions** (Theorem N, PROVED under the existence of the limit): no exact cone or grading symmetry;
a Jensen gap above the sharp floor `G_* = 0.08198` for the uniform-prior Born law (1/2 if the channel fully
depolarizes), which is necessary but not sufficient, because exactly graded delta laws have `G = 1.69-1.70`;
logit-linearity; a non-uniform law with the Born dipole; an attracting fixed point; coverage and calibration
(`E tan^2(theta/2) = 1`).

**Existence** (PROVED within the stated random-matrix classes): exact Born with full coverage is achieved by
classical-label ensembles and by a unitarily invariant R-diagonal ensemble whose cosine-sine law has mean pole flip
probability `1/phi^2`. The approved families cannot host the first (they supply only a one-parameter label), and
the second is a single point in the space of cosine-sine laws, while the three known universality mechanisms
(weak coupling, graded secular dynamics, full scrambling) flow to the delta, the delta, and the Haar law
respectively. **The martingale route does not apply**: exact zero drift is pointer-QND and gives a delta, and the
quantities a martingale controls cannot distinguish a Born root law from a single latitude.

## 7. Tier-by-tier answers

- **Tier 1** (Ising ring, `hz, h0z, gx`): off resonance, degenerate caps; on the resonance set, graded secular
  law plus `sqrt(g/omega)` spreading; `h0z = hz` neither necessary nor sufficient. Late-time near-Born plateau on
  `h0z = hz` with a resolved residual (§5).
- **Tier 2** (`+h0x`): the X field rotates the preferred basis to `h0_hat`, kinematically; resonance becomes
  `|h0| = |hz + mJ|`; no attracting fixed point on resonance; the `h0z = 0` slice is X0-conserving (Theorem 1).
- **Tier 3** (`+gy`): for `M`-conserving detectors multichannel coupling is single-channel up to the exact
  `sqrt(kappa)` gauge; `|gy| = |gx|` is charge-graded (delta). Multichannel coupling cannot seed a Born region.
- **Tier 4** (XXZ): collective coupling sees only the SU(2)-breaking anisotropy `|J_zz - J_perp|`; the isotropic
  point drops out; `M` conservation keeps the secular law graded for every anisotropy. No special anisotropy.
- **Tier 5** (XYZ): load-bearing parameters are `h0` (the axis), the coupling components transverse to it, the
  detector spectral weight at `2|h0|`, and exact conserved quantities (each a no-go or a degeneracy); decorative
  at leading order are `g_z/N`, `g_x` versus `g_y` beyond the gauge combination, and isotropic exchange. The axis is
  a static feature of `H_q` (for `|h0| >> g`), made a fixed point kinematically.
- **Tier 6** (chain): the same mechanism, with a light cone replacing collective fluctuations; exactly solvable
  Ising and matchgate classes are excluded outright; generic interacting chains give caps in the SPEC order.
- **Tier 7**: one mechanism for both geometries (energy grading of the pencil); the geometries differ in
  bookkeeping (coupling scaling, light cone).

## 8. Rigorous versus heuristic, and what remains open

Rigorous: Sections 2-3, the gauge identity, the fixed-`T` cap bounds (WP2 P2.3), the chain light-cone
factorization, the existence results. Conditional or heuristic: uniform-in-`T` off-resonance control beyond
`delta/g^2` (prethermal multi-flip resonances); tightness in `N` of the resonant ring law; secular suppression for
detectors without a conserved charge (Tier 5); the SPEC-order `T -> infinity` law of gapless interacting chains
beyond `T1`; log-tail control of the large-`N` limit for every family outside the exact classes. Numerically open:
whether the focus-case residual (§5) persists at `N = 16, 18` and across the perturbation cloud.

## 9. Implications for the paper

- The formalism admits exact Born (Theorem 3), so a negative result is about the dynamics of local weak-coupling
  detectors, not about unitarity. That is a clean and publishable dichotomy.
- The mechanism is new relative to decoherence accounts: relaxation and dephasing, which drive the qubit's reduced
  state, leave the exact collapse law pinned, because they are on-shell. Born-like root statistics require
  off-shell processes of order unity, which weak coupling forbids.
- The preferred basis is the qubit's energy basis, selected kinematically; claims of detector-selected axes should
  be withdrawn at `screen_00`.
- Earlier near-Born numerics are reverse-order, lab-basis or fine-tuned objects, and should be relabelled as such.
- Testable predictions: in the self-consistent basis the root law of a weakly coupled qubit stays a cap across the
  qubit's `T1`; grading-breaking strength enters as `sqrt(kappa)`; and the resonant-ring plateau carries a
  mid-latitude excess over Born of about 0.05.
