# Memory versus Born statistics across the ring and endpoint-chain families

Source: repository execution, local run
Collected: 2026-09-20
Published: 2026-09-20

**Status:** Exploratory mechanism study. No paper-readiness gate is claimed, no
verifier is frozen, `paper_ready` remains `false`.
**Question:** Is one-way information flow (Markovianity) necessary or sufficient
for a Born-like projective-root profile?

## Why the conjecture had to be restated

A binary Markovian/non-Markovian criterion is vacuous here: at finite `N` a finite
bath always recurs, so every model in the approved family is non-Markovian on a
long enough window. "Born-like" is also asymptotic (`N→∞` then `T→∞`,
`SPEC.md` §7.1), while Markovianity is a property of the whole trajectory
`{Λ_t}` and depends on the initial detector state that the root measure never
sees. The study therefore measures information backflow on a fixed, stated window
and asks how it scales with `N`.

## What was run

288 configurations, all local, no HPC. The two production cells are exactly
`SPEC.md` §9.1 (ring, collective coupling) and §9.2 (endpoint chain, local
coupling); `ring`/`first` and `chain`/`all` are mechanism-separating controls.

| Axis | Values |
|---|---|
| cell | ring/all, chain/first, ring/first, chain/all |
| `h_x/J` | 0.5, 1.0, 1.5 |
| `h_x0` | 0.0, 0.5 |
| coupling scaling | `norm` (`J_z = εΛ/n`), `fluctuation` (`J_z = εΛ/√n`) |
| `N` | 4…9 |
| fixed | `J = 1.0`, `h_z = 0.3`, `ε = 0.10`, `h_z0 = 0`, all other couplings zero |

Coupling is matched by **effective strength**, not per-edge coefficient, because
`_central_targets` applies `J_z` to every target: a collective ring has total
coupling `J_z·N` against the chain's `J_z`. For a single-target cell the two
scaling arms coincide by construction, which is why `chain/first` and
`ring/first` show identical numbers across arms.

Windows, all frozen before the run: early memory `t ∈ [0,60]`, late memory
`t ∈ [100,160]`, both at `Δt = 0.1`; Born roots pooled over 6 log-spaced times in
`t ∈ [100,1000]`. Plotted `P`/`R` use 64 bins, `S_Born` uses 100.

## Method notes

The qubit Choi matrix is the Gram matrix of the four propagator-block images of
the detector state, verified against an explicit partial trace to `1.11e-16`. The
Bloch series is computed spectrally in `O(D²)` per time rather than by building
`U(t)`, which is what makes the grid tractable at `D = 2^(N+1)` up to 1024.

Hamiltonians are built with `SinglePixelHamiltonianQuSpin` and independently
rebuilt with the NumPy twin; the run aborts on any disagreement above `1e-12`.

Sign convention: the builder is
`H = −J ΣZZ − J_z Z_0 ΣZ − Σ(h_x X + h_z Z) − h_x0 X_0`, so `J_SPEC = −J_code`
and `g_SPEC = −Jz_code`.

## Known limitations recorded before results

- `h_x0 = 0` conserves `Z_0`, so the off-diagonal blocks vanish and every root
  sits at the pole. That arm is a memory reference only and carries no Born
  information; it is the commuting/QND tier with an existing `Z`-basis no-go.
- `N ≤ 9`, not 11 as originally planned. The endpoint chain has no symmetry-sector
  path (`core/ring_translation.py:41`), so a matched comparison must be dense on
  both sides.
- `N_BLP` is an unnormalized window accumulation and a lower bound on the true
  BLP supremum (512-point Fibonacci direction grid).
- The house convention drops roots at infinity; the excluded count is recorded.
- `S_Born` at small `N` is depressed by sparse bin occupancy, so cross-`N`
  comparison needs the thinning control rather than the raw trend.

## Artifacts

- `reports/markovianity_born_2026-09-20/` — per-case `results.npz`,
  `metrics.json`, `metadata.json`, plus `summary.json` and `figures/`
- `reports/markovianity_born_2026-09-20/pilot_sources/` — the exploratory scripts
  that preceded the module, stored with `.txt` suffixes
- `research_reports/MARKOVIANITY_BORN_2026-09-20.md` — the full report
- `core/markovianity.py`, `tests/test_markovianity.py`,
  `scripts/run_markovianity_born_comparison.py`,
  `scripts/plot_markovianity_born.py`

## Outcome

All 288 configurations completed. QuSpin/NumPy builder agreement `0.0` exactly,
hermiticity residual `0.0`, and 0 of 290,304 roots excluded at infinity.

- **Sufficiency refuted.** The five least-Markovian configurations have
  `S_Born` between −0.32 and −0.63.
- **Necessity not supported; sign runs the other way.** Within-`N` Spearman
  between `N_BLP` and `S_Born`: −0.587 (p=0.0026) at N=9 over all cells,
  −0.845 (p=0.00055) restricted to the two SPEC production cells.
- **Geometry labelling backwards.** `ring`/`all` memory decays monotonically with
  `N` in all six rows (1.1e-3 at N=9) under both scalings; the **gapped**
  `chain`/`first` is the only saturating family (≈0.23, flat from N=6). The same
  chain at criticality is the most Markovian cell in the grid (3e-4).
- **Nothing is Born-like.** Best `S_Born` = +0.325 (critical `chain`/`first`,
  N=9, coverage 1.00).
- **The finite-size trend is an estimator artifact.** Thinning the N=9 root set
  to the N=4 budget of 96 roots returns `S_Born` to its N=4 value in every cell
  (200 draws). `SPEC.md` hard-FAIL condition 6. Within-`N` comparisons are
  unaffected, since root count and noise are identical across cells at fixed `N`.
- **Late-window memory** for `ring`/`all` is ≈3.6× the early-window value, so its
  backflow recurs rather than being a transient.

Numeric outputs: `reports/markovianity_born_2026-09-20/analysis.txt` and
`resolution_control.txt`; figures in `figures/`.
