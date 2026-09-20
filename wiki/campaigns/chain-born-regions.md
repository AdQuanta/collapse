# Endpoint-chain Born region campaign

> Status: **exploratory, no gate credit claimed.** `paper_ready` remains `false`, no verifier is
> frozen for promotion, and nothing here has passed the full robustness gauntlet.
> Campaign version: `chain-born-v1`
> Started: 2026-09-20

## What is being searched, and for what

The objective is a **stable region** of the open endpoint-chain parameter space whose projective-root
statistics approach the Born profile `R(theta) = cos^2(theta/2)` — not the configuration with the
highest score. `SPEC.md` §13 requires the behaviour to occupy a finite open region and to vary
smoothly within it; hard-FAIL conditions 2 and 4 exclude success at isolated or fine-tuned points
and regions destroyed by small generic perturbations. A batch is therefore organised around
**centers and clouds**: each candidate center is displaced in several generic random directions at a
stated relative radius, and centers are judged on the level *and* the spread over the neighbourhood.

## Model

`SPEC.md` §9.2 endpoint chain, `connectivity="chain"` with `central_coupling="first"`. Central qubit
indexed 0, detector spins `i = 1..N`. The builder carries an overall minus sign, so it constructs

    H = -[ J_zz sum_{i=1}^{N-1} Z_i Z_{i+1} + J_xx sum X_i X_{i+1} + J_yy sum Y_i Y_{i+1} ]
        -[ g_z Z_0 Z_1 + g_x X_0 X_1 + g_y Y_0 Y_1 ]
        -[ h_0x X_0 + h_0y Y_0 + h_0z Z_0 ]
        - sum_{i=1}^{N} ( h_x X_i + h_y Y_i + h_z Z_i )

**The code coefficients are the negatives of the `SPEC.md` §9 ones.** Because the qubit couples to a
single edge, the total qubit–detector coupling is independent of `N`; no size scaling of `g` is
applied or needed, unlike the ring's collective coupling where it would be `N g`.

`h_y` and `h_0y` did not exist in the repository and were added to both Hamiltonian twins for this
campaign under explicit user approval; see
`raw/project-governance/2026-09-20-y-self-field-family-extension-approval.md`.

## Frozen contract

Fixed in `scripts/eval_chain_born.py` before the first batch and unchanged since. Thresholds are
never retuned after seeing results; a genuine change means a new campaign version.

| Item | Value |
|---|---|
| Size ladder | `N = 8, 9, 10` (extended to 11 for selected region points) |
| Times | six log-spaced points in `[100, 1000]`, fixed and independent of `N` |
| Score | `S_born`, 100 bins; plotted profiles 64 bins |
| Root budget | 1536 = `6 x 2^8`, with 200 bootstrap draws |
| Perturbative rule | `max|g| <= 0.1 x min|nonzero non-g|` |
| Scale convention | smallest nonzero non-coupling parameter normalised to 1 |
| Coverage gate | at least 20 of 100 bins occupied |

**Roots are pooled, not averaged over times.** All `2^N` roots from each of the six times are
concatenated into one array of `6 x 2^N` angles and histogrammed once. Since every time contributes
equally many roots this equals averaging the six densities and then scoring, which is the protocol of
`goal_born_search.md` §1; it is *not* the mean of six separate scores, because `S_born` is nonlinear
in `P`. Per-time scores, their spread, and `pooling_gain = S_pooled - max_k S_k` are recorded so that
time-averaged agreement stays distinguishable from actual convergence (`SPEC.md` §7.2).

**Scores are compared across `N` only at fixed root budget.** The finite root count grows as
`6 x 2^N`, so bin occupancy and hence `S_born` rise with `N` for reasons unrelated to Born. This is
the artifact documented in `research_reports/MARKOVIANITY_BORN_2026-09-20.md` §12 and `SPEC.md`
hard-FAIL 6.

## Artifacts

- Frozen evaluator: `scripts/eval_chain_born.py`, tests in `tests/test_eval_chain_born.py`
- Runner: `scripts/run_chain_born_campaign.py` (`--summarize` for a ranked view)
- Batches, one file per iteration: `batches/iteration_NN.json`
- Append-only log: `reports/chain_born_regions/experiment_log.jsonl` (gitignored, like all
  generated campaign data; the batch files plus the frozen evaluator reproduce it)
- Console stream: `reports/chain_born_regions/live.log`
- Profile export: `scripts/export_chain_born_region_profile.py`, writing `results.npz` in the
  ring-catalog array schema plus a `metadata.json` carrying the sign convention, the time grid, the
  bin counts and the coverage
- Figure: `scripts/plot_chain_born_region_diagnostics.py`, which reuses `_plot_angular` from
  `build_network_wd_nonborn_size_spacing_figures.py` and `_plot_ratio` from
  `plot_hz0_0_ring_spacing_born_catalog.py` rather than defining a new chart. Output for the best
  region is `reports/chain_born_regions/screen_00/diagnostics.pdf`.

The candidate list is deliberately **data, not code**. Each batch is written after reading the
previous one's results; committing hypotheses to a Python module would freeze them before any result
is seen.

## Established so far

1. **Rung 0 is identically degenerate, not merely unfavourable.** With `h_0x = h_0y = g_x = g_y = 0`
   the qubit's `Z` is conserved, the off-diagonal propagator block vanishes, every root sits at
   `theta = 0`, and coverage is 2 of 100 bins. Adding the detector's transverse field `h_x` changes
   nothing, because `h_x` never touches the qubit. Breaking `Z_0` is a precondition for any signal.
2. **Criticality is eliminated; integrability breaking is supported.** An integrable
   transverse-field Ising detector (`h_z = 0`) scored between `-0.152` and `+0.060` with coverage
   pinned at 12–24 bins across `h_x/J_zz` from 0.25 to 4.0, with no peak at the critical point.
   Turning on `h_z` raised coverage to 100 and the score to `+0.535`.
3. **The intra-detector interaction is load-bearing** (`SPEC.md` §15.1). Removing it gives `-0.050`
   at coverage 20 against `+0.521` with it. The mechanism-breaking control (`h_z = 0` at the peak
   `h_x`) degrades to `-0.152`, as the ergodicity reading predicts.
4. **The coupling dependence is partly, not wholly, a time-window artifact.** On the frozen window
   `S_born` rose monotonically with `epsilon`; rerunning with the window scaled by `(0.1/eps)^2`, so
   every candidate spans the same number of induced decoherence times, recovered roughly half the
   trend but not all of it. The score still falls toward zero as `g -> 0`, and at the perturbative
   ceiling `eps = 0.1` it caps near `+0.7`.
5. **All three qubit-field components are required.** Removing `h_0z` collapses the neighbourhood to
   `-0.735`; the symmetric `(1,1,1)` orientation outperforms every plane-confined alternative.
6. **The best region found is `screen_00`**, at

       J_xx = +1.32  J_yy = +2.53  J_zz = +1.10
       h_x  = -1.34  h_y  =  0     h_z  = +1.00
       h_0x = -1.35  h_0y = -1.69  h_0z = +2.01
       g_x  = +0.10  g_y  = +0.05  g_z  = +0.06

   Measured against the locally-refined incumbent on the same radius grid, with generic random
   displacement directions:

   | radius | `screen_00` mean | sd | min | incumbent mean | sd | min |
   |---|---|---|---|---|---|---|
   | 20% | +0.717 | 0.033 | +0.626 | +0.628 | 0.084 | +0.494 |
   | 35% | +0.656 | 0.081 | +0.542 | +0.587 | 0.087 | +0.478 |
   | 50% | +0.604 | 0.143 | +0.406 | +0.559 | 0.185 | +0.253 |

   The 20% row pools **two independent RNG seeds**, eight directions each. Seed A alone gave
   `+0.719 +/- 0.021` and seed B `+0.716 +/- 0.043`: the level replicates almost exactly while the
   spread does not, so the pooled sixteen-direction figure is the one quoted. Even at the looser
   pooled spread, `screen_00` is 2.5 times tighter than the incumbent.

   `screen_00` is higher, tighter, and better in the worst case at every radius. It is a genuine
   finite region: at 20% displacement the budget-controlled score varies by only `+/-0.02`, and it
   degrades smoothly rather than collapsing out to 50%.
7. **The budget-controlled `N`-trend is positive but decelerating.** On the incumbent region it is
   `+0.111` on average across `N = 8..11` over seven points, with the raw trend roughly 40% larger,
   so the budget control removes real estimator inflation while a genuine improvement survives. On
   `screen_00` the trend is stronger, `+0.171` to `+0.250`, but the increments shrink sharply:
   the center runs `0.557, 0.670, 0.716, 0.728, 0.707` for `N = 8 ... 12`, i.e. increments
   `+0.113, +0.046, +0.012, -0.021`. **The trend turns over at `N = 12`.** The last three sizes,
   `0.716, 0.728, 0.707` with a bootstrap spread of about `+/-0.030` on each, are consistent with a
   plateau near `0.72` and give no evidence of an approach to 1.

   **The large-`N` limit cannot be inferred from four sizes.** Fitting twelve such series under
   four reasonable ansätze gives, for the extrapolated limit:

   | ansatz | range over twelve series |
   |---|---|
   | `S_inf - A/N` | 0.69 – 1.50 (several above 1, which is unphysical) |
   | `S_inf - A/N^2` | 0.65 – 1.06 |
   | `S_inf - A exp(-bN)` | 0.54 – 0.89, with two fit failures |
   | `S_inf - A/2^N` | 0.56 – 0.77, the most stable |

   `SPEC.md` §7.3 requires the inferred limit to be stable against reasonable extrapolation
   ansätze. It is not: the spread is 0.54 to 1.50, and the one form that projects high (`1/N`)
   cannot saturate and returns unphysical values above 1. The decelerating increments are
   suggestive of a limit well below 1, but **four sizes do not establish one**, and it would be
   wrong to report convergence to Born. The `N = 12` point, which the fits above did not include,
   lands *below* `N = 11` and so favours the saturating forms over `1/N`. Taken with the
   extrapolation spread, the defensible statement is: **the budget-controlled score plateaus near
   `0.72` over `N = 10 ... 12`, with no evidence of approach to 1, and five sizes are still too few
   to pin the residual.** If the plateau is real, the result is *approximately* Born-like with a
   nonzero asymptotic residual, which is `SPEC.md` hard-FAIL condition 1 against a claim of exact
   asymptotic Born behaviour. Going further is expensive: `N = 12` took roughly 9 minutes for this
   single complex-Hamiltonian candidate.

   **The same ceiling appears in a structurally different region.** The best XXZ cell
   (`Delta = 0.5`, tier 3) runs `0.575, 0.629, 0.674, 0.695` over `N = 8 ... 11`, increments
   `+0.054, +0.046, +0.021` — the same decelerating approach to roughly the same value as the XYZ
   region's `0.72`. Two regions at different rungs of the hierarchy, found by different means,
   converging on `0.70–0.73` suggests the ceiling is a property of the endpoint-chain family under
   the perturbative constraint rather than of either region. That is a conjecture on two series,
   not a result.
8. **The azimuthal distribution is strongly non-uniform, so only the weak criterion has been
   tested.** The root azimuths at the best region carry a first circular moment
   `|<e^{i phi}>| = 0.505` against a finite-sampling noise floor of `0.018`, with a third moment of
   `0.129`. The exact Born profile contains only the `(0,0)` and `(1,0)` spherical-harmonic sectors
   and is azimuthally symmetric, so a moment this size signals large `m != 0` structure in the
   full-sphere root measure. This is physically unsurprising — `h_0x` and `h_0y` break the `U(1)`
   about `z` — and it is not specific to one region: the incumbent shows the same first moment,
   `0.474` against the same `0.013` floor, so the anisotropy is a property of the family. It means
   **every score in this campaign is a weak-Born (polar marginal) score**,
   exactly the gap `SPEC.md` §5.2 warns about: passing the weak criterion does not imply passing the
   strong one, because azimuthal anisotropy is hidden by marginalising over `phi`. Converting this
   into `E_2` and `E_harm` requires the outcome-resolved full-sphere densities and has not been
   done.

## Negative results and corrections, recorded so they are not rediscovered

- **Small-direction clouds cannot estimate flatness, and this trap was hit three times.** In each
  case a striking spread evaporated on replication: `0.029 -> 0.225` (three directions, twelve on
  resampling), `0.021 -> 0.033` (eight directions, one seed versus two), and `0.009 -> 0.033` at
  `Delta = 0.5` (four directions versus twelve). The level replicates reliably; **the spread does
  not**. Any flatness claim needs at least eight directions from at least two seeds, and the pooled
  figure is the one to quote.
- **A three-direction cloud cannot estimate flatness.** One center appeared to be five times flatter
  than any other (spread 0.029 at 20%); resampling with twelve independent directions gave spread
  0.225. The original draw had landed in a benign subspace. **Every ranking of nine centers made on
  three directions each is unreliable and was discarded.** Use at least eight directions.
- **A mislabelled control.** A candidate described as a free-fermion XY detector was not one: with
  `h_x != 0` an XY chain is not quadratic under Jordan–Wigner, because `X_i` carries a string. Only
  `ZZ + h_x` is free-fermionic. Its high score was therefore consistent with, not contrary to, the
  ergodicity reading.
- **Local adaptive refinement lost to uniform random screening.** A quasi-random screen of 24
  centers across all twelve parameters found three matching or beating the incumbent. Clouding the
  best three with eight directions each at 20% displacement gave:

  | region | n | mean | sd | min | spread |
  |---|---|---|---|---|---|
  | `screen_00` | 8 | +0.719 | 0.021 | +0.688 | 0.061 |
  | `screen_18` | 8 | +0.619 | 0.031 | +0.573 | 0.084 |
  | `screen_21` | 8 | +0.612 | 0.069 | +0.526 | 0.173 |
  | incumbent, after five adaptive iterations | 12 | +0.628 | 0.084 | +0.494 | 0.225 |

  A single random draw produced a region that is higher, four times flatter, and far better in the
  worst case than the one five iterations of local refinement converged on. Its parameters sit at
  the top of the `SPEC.md` §10 hierarchy — a full XYZ detector with `J_xx = 1.32, J_yy = 2.53,
  J_zz = 1.10`, all three qubit-field components, and all three coupling channels. **The practical
  lesson is that adaptive local refinement anchors, and a region search needs a broad uniform screen
  before and alongside the local work, not only after it.**
- **The perturbative rule blocks generic perturbation testing.** Because the denominator is the
  *minimum* nonzero parameter, introducing a small term in a currently-inactive direction makes it
  the minimum and collapses the coupling ceiling. Perturbations are therefore confined to the
  already-active subspace, which is weaker than `SPEC.md` §13 requires. **This needs a rule
  decision**: either a floor below which a parameter is treated as zero for the purposes of the
  minimum, or a denominator based on a physically meaningful detector scale.
- **Apple Accelerate's `zheevd` is broken at dimension 4096.** Complex Hermitian eigensolves fail
  with "illegal value in argument 10" — an `LRWORK` workspace bug — reached at `N >= 11` once a `Y`
  self-field makes the Hamiltonian complex. Both `numpy.linalg.eigh` and SciPy's `evd` driver fail;
  `scipy.linalg.eigh(driver="evr")` handles the same matrix and is about four times faster than the
  `ev` driver. The evaluator now falls back to it.

## XXZ intra-detector anisotropy (SPEC §10.1 tier 3)

This tier was skipped when the random screen jumped from Ising straight to XYZ, and was scanned on
request. With `J_xx = J_yy = J_perp` and anisotropy `Delta = J_zz / J_perp`, holding the qubit and
coupling fixed at `h_x = 1.4, h_z = 1.0, h_0x = h_0y = h_0z = 1, g_z = 0.1`, and varying `Delta`
without letting any parameter fall below 1:

| `Delta` | regime | directions | cloud mean | sd | min |
|---|---|---|---|---|---|
| 0.33 | easy-plane | 12 | +0.611 | 0.041 | +0.512 |
| **0.50** | easy-plane | 12 | **+0.650** | **0.033** | **+0.579** |
| 0.75 | easy-plane | 12 | +0.537 | 0.024 | +0.494 |
| 1.00 | isotropic (XXX) | 12 | +0.593 | 0.057 | +0.506 |
| 1.50 | easy-axis | 12 | +0.647 | 0.078 | +0.477 |
| 2.00 | easy-axis | 12 | +0.618 | 0.072 | +0.459 |
| 3.00 | easy-axis | 12 | +0.578 | 0.049 | +0.484 |

Every row pools twelve directions across two independent seeds. **The first four-direction draw
badly overstated the structure** — it gave `Delta = 0.5` a spread of `0.009` and the easy-axis
points spreads of `0.10–0.11`, suggesting a sharp stability boundary at the isotropic point. With
adequate sampling there is no such boundary, and the easy-plane/easy-axis framing is too coarse:
`Delta = 0.75` is a local *minimum* in level (`+0.537`), lower than the isotropic point, so the
easy-plane side is not uniformly better.

What survives is narrower and about one anisotropy rather than a regime: **`Delta = 0.5` is the best
XXZ cell on mean (`+0.650`), spread (`0.033`) and worst case (`+0.579`) simultaneously**, and the
three easy-axis cells have the three worst worst-cases in the scan (`+0.459` to `+0.484`). Ordering
by worst case over the cloud gives `0.5 > 0.33 > 1.0 > 0.75 > 3.0 > 1.5 > 2.0`.

Measured on the same radius grid as the XYZ region, the best XXZ cell is below it at every radius
where both are well sampled:

| radius | XYZ `screen_00` (n, mean, sd, min) | XXZ `Delta = 0.5` (n, mean, sd, min) |
|---|---|---|
| 20% | 16, +0.717, 0.033, +0.626 | 12, +0.650, 0.033, +0.579 |
| 35% | 8, +0.656, 0.081, +0.542 | 6, +0.565, 0.111, +0.416 |
| 50% | 8, +0.604, 0.143, +0.406 | 6, +0.577, 0.075, +0.477 |

So tier 3 does not supersede the XYZ region: `Delta = 0.5` is the best cell *within* XXZ, not the
best region found. The two are comparable only at 50% displacement, where both have degraded and the
samples are small.

## What the random screens say about the level distribution

Two quasi-random screens over all twelve parameters, drawing each non-coupling parameter as either
zero or a signed magnitude in `[1, 4]` and setting `g` at the ceiling the perturbative rule allows:

| screen | evaluated | mean | median | max | min | fraction at or above +0.60 |
|---|---|---|---|---|---|---|
| first | 24 / 24 | +0.275 | +0.266 | +0.712 | −0.455 | 17% |
| second | 12 / 40 | −0.006 | +0.055 | +0.446 | −0.722 | 0% |

The second screen was **stopped at 12 of 40** to reallocate the remaining compute to measuring the
best region's extent and `N`-trend; its 12 points are retained and are a valid but small sample. The
two screens are not in tension once the sample sizes are read: roughly one draw in six reaches
`+0.60`, so a 12-point screen finding none is unremarkable. Taken together they say the attainable
level in this family is broadly distributed with a mean near zero and a tail reaching `+0.7`, and
that `+0.7` is the top of the observed range rather than a typical value.

## The best region's profile

At `N = 10`, 6144 roots pooled over the six frozen times, `screen_00` gives `S_born = +0.776` on 100
bins with full 100/100 coverage, and an occupied-bin RMSE against `cos^2(theta/2)` of `0.059` on the
64 plotting bins with full 64/64 coverage. The folded fit prefers a wrapped Gaussian
(`sigma = 1.285`) over a wrapped Cauchy (`gamma = 1.327`). `R(theta)` tracks the Born target across
the whole range with visible but small oscillation; the residual is a systematic overshoot just
below `pi/2` and a slight undershoot in the far tail, not a failure of shape.

## Honest summary

Nothing here is Born-like. The best budget-controlled score anywhere is about `+0.72` against `1.0`
for an exact Born profile, the neighbourhood around it varies by `+/-0.08` under a 20% displacement,
and the level is capped by the perturbative constraint rather than approaching Born as the coupling
weakens. What has been established is a mechanism direction — a non-integrable interacting detector
with all three qubit-field components and `Z_0` broken — and a set of controls that behave as that
mechanism predicts.

## Best regions, as they stand

| | XYZ `screen_00` | XXZ `Delta = 0.5` |
|---|---|---|
| detector | `J_xx=1.32, J_yy=2.53, J_zz=1.10` | `J_xx=J_yy=2.0, J_zz=1.0` |
| detector fields | `h_x=-1.34, h_z=1.00` | `h_x=1.4, h_z=1.0` |
| qubit fields | `h_0x=-1.35, h_0y=-1.69, h_0z=2.01` | `h_0x=h_0y=h_0z=1.0` |
| coupling | `g_x=0.10, g_y=0.05, g_z=0.06` | `g_z=0.1` |
| 20% cloud | +0.717 +/- 0.033, min +0.626 (16 dirs) | +0.650 +/- 0.033, min +0.579 (12 dirs) |
| `N = 10` profile | `S_born` +0.776, RMSE 0.059, coverage 100/100 | — |
| `N`-trend | `0.557, 0.670, 0.716, 0.728, 0.707` (N=8..12) | `0.575, 0.629, 0.674, 0.695` (N=8..11) |
| how found | one draw of a 24-point random screen | requested XXZ anisotropy scan |

## Next

1. Resolve the perturbative-rule conflict so that generic perturbations can include currently
   inactive directions; until then the §13 robustness test is incomplete.
2. Cloud the screening centers with at least eight directions each to see whether any randomly-found
   high point is flatter than the incumbent.
3. Extend the size ladder further only for centers that survive, since `N = 12` costs roughly
   280 s per candidate against 10.3 s for the `N = 8..10` ladder.
4. Compute the remaining `SPEC.md` §6 diagnostics — `E_2`, `E_inf`, `E_harm` — which this campaign
   does not yet report, and produce the house-style angular figures for any surviving region.
