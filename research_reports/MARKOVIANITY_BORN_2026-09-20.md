# Is Markovianity necessary or sufficient for a Born-like profile?

**Date:** 2026-09-20
**Status:** Exploratory mechanism study. **No paper-readiness gate is claimed**, no
verifier is frozen, and `paper_ready` remains `false`.
**Code:** working tree at `core/markovianity.py`, `scripts/run_markovianity_born_comparison.py`,
`scripts/plot_markovianity_born.py`, `tests/test_markovianity.py`
**Data:** `reports/markovianity_born_2026-09-20/`

## Question and the repair it required

The conjecture asks whether one-way information flow from qubit into detector —
Markovianity in the informal sense — is necessary or sufficient for the
projective-root measure to approach `R(θ) = cos²(θ/2)`.

As posed it is not testable. At finite `N` nothing is strictly Markovian, because a
finite bath always recurs, so a binary criterion is satisfied vacuously by every
model in the approved family. "Born-like" is also an asymptotic statement, defined
as `N→∞` then `T→∞` (`SPEC.md` §7.1), whereas Markovianity is a property of the
whole trajectory `{Λ_t}` and additionally depends on the initial detector state,
which the root measure never sees.

The repair adopted here is to make both sides quantitative on a **fixed, stated
time window** and to study the `N`-scaling. That is well posed in SPEC's own limit
order: if the backflow per window vanishes as `N→∞` inside a family, that family is
asymptotically Markovian in a sense the Born question can be compared against.

"One-way information flow" is formalised as the Breuer–Laine–Piilo measure: the
trace distance between two evolving qubit states decreases monotonically when
information only leaves the qubit, and any increase is backflow.

## 1. Explicit Hamiltonians

The two geometries are exactly the two `SPEC.md`-approved families, so no
new-family approval was required (`SPEC.md:33`, hard-FAIL #9).

Ring, `connectivity="ring"`, `central_coupling="all"` (SPEC §9.1), with detector
spins `i = 1…N`, central qubit `0`, and `Z_{N+1} ≡ Z_1`:

    H_ring = −J Σ_{i=1..N} Z_i Z_{i+1} − J_z Z_0 Σ_{i=1..N} Z_i
             − Σ_{i=1..N} $h_x X_i + h_z Z_i$ − h_x0 X_0

Endpoint chain, `connectivity="chain"`, `central_coupling="first"` (SPEC §9.2):

    H_chain = −J Σ_{i=1..N−1} Z_i Z_{i+1} − J_z Z_0 Z_1
              − Σ_{i=1..N} $h_x X_i + h_z Z_i$ − h_x0 X_0

Two further cells, `ring`/`first` and `chain`/`all`, are run as
**mechanism-separating controls** and are never treated as production families.
They exist because comparing only the two SPEC cells confounds geometry with
coupling structure.

**Sign convention.** The builder carries an overall minus sign, so the code
coefficients are the negatives of the SPEC ones: `J_SPEC = −J_code` and
`g_SPEC = −Jz_code`. Every result packet records this in `metadata.json`.

## 2. Coupling and its N-scaling

Fixed `J = 1.0` as the energy unit. The central coupling is set by a **matched
effective strength** rather than a matched per-edge coefficient, because
`_central_targets` applies `J_z` to every target, so a collective ring has total
coupling `J_z·N` while an endpoint chain has `J_z`. Comparing at equal per-edge
`J_z` measures coupling strength, not geometry.

With `Λ = max(|J|, |h_x|, |h_z|)` and `n` the number of central targets:

- `norm` scaling: `J_z = ε Λ / n`, matching the total coupling operator norm
  across geometries. For the collective ring this is exactly SPEC §9's
  conservative `g_N ∝ 1/N` baseline.
- `fluctuation` scaling: `J_z = ε Λ / √n`, matching typical magnetization
  fluctuations instead — the `α = 1/2` case of the commuting/QND trichotomy in
  `wiki/campaigns/commuting-qnd-sector.md`.

Both arms are run at matched `ε = 0.10`.

## 3. Evolution times

Three windows, all fixed before the first production run:

| Window | Range | Sampling | Used for |
|---|---|---|---|
| early memory | `t ∈ [0, 60]` | `Δt = 0.1`, 601 points | `N_BLP`, volume, RHP |
| late memory | `t ∈ [100, 160]` | `Δt = 0.1`, 601 points | same, at late times |
| Born | `t ∈ [100, 1000]` | 6 log-spaced points | root statistics |

The two memory windows have equal length and sampling so their `N_BLP` values are
directly comparable. The Born grid is the repository's existing long-time
convention (`goal_born_search.md` §3).

`N_BLP` is an **unnormalized accumulation** over its window: it grows with window
length and with sampling density, so only same-window, same-`Δt` comparisons are
meaningful. It is also a **lower bound**, since the supremum over state pairs is
estimated on a 512-point Fibonacci direction grid.

## 4. Temporal averaging

The memory measures are **not** time-averaged: `N_BLP` is the summed positive
increments of `D(t)` across its window, a total variation.

The Born side **is** pooled across its 6 long times before histogramming, which is
the repository's existing time-average convention. The two sides therefore treat
time differently, and this is stated rather than papered over: the memory number
answers "how much information returned during this window", the Born number
answers "what does the pooled late-time root measure look like".

## 5. Builders

Production Hamiltonians are built with `SinglePixelHamiltonianQuSpin`. Every
configuration is independently rebuilt with `SinglePixelHamiltonianNumpy` and the
run aborts if the two disagree by more than `1e-12`; the observed maximum
difference is recorded per case in `metadata.json`.

Propagator blocks are never formed at every time step. Writing
`H = V diag(w) V†` and letting `c^(i)` be the qubit-`i` row block of `V`, the
channel tensor `T[i,j,k,l] = Tr(U_kl† U_ij ρ_D)` becomes a quadratic form in the
eigenphases, costing `O(D²)` per time instead of `O(D³)`
(`core.markovianity.bloch_series_from_spectrum`). This is what makes 288
configurations with 1202 time samples each tractable locally.

## 6. Parameters varied and held

| Parameter | Values |
|---|---|
| geometry cell | ring/all (SPEC §9.1), chain/first (SPEC §9.2), ring/first, chain/all |
| `h_x / J` | 0.5 (ordered), 1.0 (critical), 1.5 (disordered) |
| `h_x0` | 0.0, 0.5 |
| coupling scaling | `norm`, `fluctuation` |
| `N` | 4, 5, 6, 7, 8, 9 |
| `ε` | 0.10 |
| `h_z` | 0.3 |
| `J` | 1.0 |
| everything else | `J_pm = J_xx = J_yy = J_x = J_y = J_zx = J_cpm = J_2 = J_pm2 = h_z0 = 0` |

288 configurations.

**`h_x0 = 0` has a degenerate Born side by construction.** With only `J_z` coupling
and no transverse qubit field, `[H, Z_0] = 0`, so the off-diagonal propagator
blocks vanish and every projective root sits at the pole. That arm is therefore a
**memory reference only**; the Born correlation is evaluated on the `h_x0 = 0.5`
arm. This is the commuting/QND tier, which `wiki/campaigns/commuting-qnd-sector.md`
already shows cannot satisfy the weak Born criterion in the `Z` basis.

**Deviation from plan:** sizes run to `N = 9` rather than `N = 11`. The endpoint
chain has no symmetry-sector path (`core/ring_translation.py:41`), so a *matched*
comparison must be dense on both sides; `N ≤ 9` keeps the full 288-cell factorial
within a local run. Ring-only extension to larger `N` would confound size with
solver path.

## 7. Binning and empty bins

Plotted `P` and `R` use 64 bins; `S_Born` uses 100 bins. This follows the ring
catalog convention stated in that figure family's own footer
(`scripts/build_collected_ring_catalog_report.py:109`). Empty bins are never
imputed: the ratio is masked on `R_occupied` and the reported error is
`born_RMSE_occupied`. Coverage is reported beside every score.

---

# Results

288 configurations completed. Across all of them the QuSpin and NumPy builders
agreed to `0.0` exactly, hermiticity residuals were `0.0`, and **no roots were
excluded at infinity** $0 of 290,304$.

## 8. The geometry labelling in the conjecture is backwards

`N_BLP` on the early window, maximally mixed detector, `h_x0 = 0.5`:

| cell | `h_x/J` | N=4 | N=5 | N=6 | N=7 | N=8 | N=9 | trend |
|---|---|---|---|---|---|---|---|---|
| ring/all | 0.5 | 0.1118 | 0.0104 | 0.0303 | 0.0261 | 0.0178 | 0.0144 | decaying |
| ring/all | 1.0 | 0.0750 | 0.0283 | 0.0217 | 0.0084 | 0.0008 | 0.0011 | decaying |
| ring/all | 1.5 | 0.0818 | 0.0674 | 0.0281 | 0.0179 | 0.0099 | 0.0033 | decaying |
| chain/first | 0.5 | 0.3027 | 0.2096 | 0.1956 | 0.2434 | 0.2333 | 0.2307 | **saturating** |
| chain/first | 1.0 | 0.1579 | 0.0848 | 0.0105 | 0.0003 | 0.0003 | 0.0006 | decaying |
| chain/first | 1.5 | 0.2300 | 0.0323 | 0.0678 | 0.0782 | 0.0788 | 0.0728 | mixed |

(`norm` arm; `chain/first` is identical in the `fluctuation` arm because a
single-target cell has `n = 1`, so the two scalings coincide by construction.)

The collectively coupled ring — the model the conjecture expected to be the
non-Markovian one — has `N_BLP` **decaying monotonically with `N` in all six
rows**, reaching `1.1e-3` at `N = 9`. It is asymptotically Markovian, under both
the conservative and the fluctuation scaling.

The one family whose memory does **not** decay is the **gapped endpoint chain**
(`h_x/J = 0.5`), flat at ≈0.23 from `N = 6` onward. Physically, a gapped chain
traps the excitation beside the qubit instead of transporting it away, so the
information returns; at criticality the same chain transports it ballistically
and `N_BLP` collapses to `3e-4`, the most Markovian behaviour in the whole grid.

So the correct statement is not "chain Markovian, ring non-Markovian". It is
**detector phase, not geometry, decides**, and the collective ring is Markovian
in the thermodynamic limit either way.

## 9. Sufficiency: refuted

The least Markovian configurations are not Born-like. The five largest `N_BLP`
values in the grid carry `S_Born` between `−0.32` and `−0.63`, far below even the
uninformative baseline of 0. Combined with the existing `Z`-basis no-go for the
commuting/QND tier, non-Markovianity plainly does not suffice.

## 10. Necessity: not supported — the evidence runs the other way

Within each `N`, which holds root count and estimator noise fixed, the Spearman
correlation between `N_BLP` and `S_Born` is:

| `N` | all cells | SPEC production cells only |
|---|---|---|
| 4 | +0.037 $p=0.86$ | −0.428 $p=0.17$ |
| 5 | +0.061 $p=0.78$ | −0.046 $p=0.89$ |
| 6 | +0.101 $p=0.64$ | +0.654 $p=0.021$ |
| 7 | −0.303 $p=0.15$ | −0.322 $p=0.31$ |
| 8 | −0.552 $p=0.0052$ | −0.505 $p=0.094$ |
| 9 | **−0.587 $p=0.0026$** | **−0.845 $p=0.00055$** |

A negative relationship emerges and strengthens with size: **less memory goes with
more Born-like**. At `N = 9` restricted to the two SPEC production cells it reaches
`ρ = −0.845`. The small-`N` rows are noise, as section 12 shows.

The single most Born-like configuration in the grid is also among the most
Markovian: critical `chain/first` at `N = 9`, `S_Born = +0.325` with full
coverage and `N_BLP = 5.7e-4`.

## 11. But nothing in this grid is Born-like

The best `S_Born` reached is `+0.325`, against `1.0` for an exact Born profile and
`0` for the uninformative law. No configuration approaches Born. The honest
statement of sections 9 and 10 is therefore comparative: *among configurations
that all fail to be Born*, the more Markovian ones fail by less.

## 12. The apparent finite-size improvement is an estimator artifact

`S_Born` rises with `N` in almost every cell, which would naively read as
convergence toward Born. It is not. Root count grows as `2^N × 6 times`, so bin
occupancy and hence binomial noise on `R` change drastically across the range:

| `N` | finite roots | per plotted bin | noise on `R` |
|---|---|---|---|
| 4 | 96 | 1.5 | 0.408 |
| 6 | 384 | 6.0 | 0.204 |
| 9 | 3072 | 48.0 | 0.072 |

Thinning the `N = 9` root set back to the `N = 4` budget of 96 roots and
recomputing (200 draws) removes the entire effect:

| cell | `h_x/J` | `S(N=4)` | `S(N=9)` | `S(N=9, thinned to 96 roots)` |
|---|---|---|---|---|
| ring/all | 1.0 | −0.420 | +0.148 | −0.388 ± 0.125 |
| chain/first | 1.0 | −0.459 | +0.325 | −0.264 ± 0.113 |
| ring/first | 1.5 | −0.682 | +0.167 | −0.367 ± 0.140 |
| chain/all | 1.5 | −0.497 | +0.044 | −0.402 ± 0.149 |

Thinned `N = 9` values land on top of the measured `N = 4` values. **There is no
evidence of genuine finite-size convergence toward Born anywhere in this grid**;
the trend is bin occupancy. This is precisely `SPEC.md` hard-FAIL condition 6,
and it is recorded as a negative result rather than presented as convergence.

The within-`N` correlations of section 10 are unaffected, because at fixed `N`
every cell has identical root count and identical noise, and coverage is 1.00 for
every `h_x0 = 0.5` case at `N = 9`.

## 13. Late-window memory

Averaged over phases at `N = 9`, `h_x0 = 0.5`:

| cell | early `[0,60]` | late `[100,160]` |
|---|---|---|
| ring/all | 0.0314 | 0.1130 |
| chain/first | 0.1014 | 0.0807 |
| ring/first | 0.0406 | 0.0366 |
| chain/all | 0.0137 | 0.0611 |

The collective ring's memory is roughly 3.6× larger on the late window than the
early one: its backflow is not a transient but recurs. The endpoint chain instead
decays slightly. Any asymptotic claim about the ring must therefore be made at
fixed window with the window stated, which is why both are reported.

# Verdict

- **Sufficient? No.** Refuted; the least Markovian cells are the least Born-like.
- **Necessary? Not supported, and the sign is against it.** Within-`N`
  correlations are negative and strengthen with size (`ρ = −0.85` at `N = 9` on
  the SPEC cells). Suppressing memory is associated with *better* Born
  similarity, not worse.
- **Both subject to a hard caveat:** no configuration here is Born-like, and the
  finite-size trend that superficially suggested progress toward Born is an
  estimator artifact. The correct reading is a ranking among failures, not a
  demonstrated mechanism.

# Limitations

1. `N ≤ 9` and `ε = 0.10` only. A matched ring/chain comparison must be dense on
   both sides because the chain has no sector path, so this cannot yet reach the
   sizes at which the existing ring campaigns operate.
2. `N_BLP` is an unnormalized window accumulation and a lower bound on the BLP
   supremum (512-point direction grid). Values are comparable only at fixed
   window and fixed `Δt`.
3. The memory side is a total variation over a window; the Born side is pooled
   over 6 long times. The two treat time differently by construction.
4. `S_Born` is a diagnostic, not a `SPEC.md` metric. `E_2`, `E_∞`, `E_harm` and
   `E_marg` were not computed.
5. The correlation is an association across a parameter grid, not a demonstrated
   causal mechanism. No mechanism-breaking control was run.
6. Two unrelated repository tests fail on degenerate-root cluster matching at
   ~4e-9; they are untouched by this work and were verified unchanged.

# Next

The sharpest follow-up is the gapped endpoint chain, the only family here whose
memory saturates rather than decaying with `N`. If the negative association holds,
it should be the *worst* Born performer at large `N` — and it is the natural
subject for a mechanism-breaking control, since its memory can be suppressed
continuously by tuning `h_x/J` toward criticality without changing anything else.

