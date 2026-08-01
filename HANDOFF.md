# Codex / LLM Project Handoff

Snapshot date: **2026-07-21** (Asia/Jerusalem)

## 2026-07-26: transferred Zeus results reassess exact activation iff broadness

- Ingested the transferred
  `work/zeus_degeneracy_heavy_tail_iff_N13_N18` and
  `work/zeus_relative_scale_regimes_20260724_144102` checkpoints.
- Primary inference uses only complete sizes \(N=13,14,15,16\): 44 targeted
  truth-table rows and 120 relative-scale rows at \(t=10^6\). At the analysis
  snapshot, targeted N=17 was 4/11, relative-scale N=17 was 5/30, and both
  N=18 tasks were 0; partial sizes were not pooled into the main counts.
- The conjecture remains falsified in both directions. Across complete
  targeted rows there are 11 active/non-broad and 8 inactive/broad outcomes.
  The fully degenerate and non-Ising SU(2) active families stay non-broad,
  while the exactly inactive \(h_z=\pm2.01J\) families stay broad at every
  complete size.
- The 30-regime sweep has 13 cases broad at all four complete sizes, 15
  non-broad at all four, one broad at three, and one broad at two. Only the
  seven analytically certifiable Ising/SU(2) regimes receive exact-activation
  labels; the other anisotropic cases remain explicitly uncertified.
- Added reusable analysis
  `collapse/degeneracy_zeus_assessment.py`, CLI
  `examples/analyze_degeneracy_heavy_tail_zeus_results.py`, and targeted test
  `tests/test_degeneracy_zeus_assessment.py`.
- The self-contained assessment, three figures, CSV tables, and JSON summary
  are under `reports/degeneracy_heavy_tail_zeus_2026-07-26/`; the earlier
  `reports/degeneracy_heavy_tail_iff_2026-07-24.md` now contains the Zeus
  update.
- Transfer limitation: all metric JSON files and diagnostic figures needed
  for the assessment are present and finite, but the referenced raw NPZ
  spectra are absent (48 targeted and 125 relative/partial paths). Therefore
  metrics were audited and cross-checked but could not be recomputed locally
  from eigenvalues. Eight duplicate parameter/size points agree exactly
  across the two independent pipelines.

## Anisotropic single-pixel J--Jpm--hz Zeus campaign (2026-07-18)

- Added a configuration-driven clean-ring campaign for
  `N=11,12,13,14,15,16,17,18`, collective `Jx=0.01` with physical edge
  coefficient `0.01/sqrt(N)`, `hz0=0`, and `t=1e6`. The grid contains 11
  `hz` values around `-2,0,+2` plus controls, 8 `J` values, and 10 `Jpm`
  values: 880 configurations per N and 7,040 total.
- The SOLID-style implementation is `collapse/anisotropic_sweep.py`; the CLI
  is `examples/run_single_pixel_anisotropic_sweep.py`; the exact grid is
  `configs/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json`.
- One PBS array task owns one N. A `ProcessPoolExecutor` evaluates different
  `(hz,J,Jpm)` configurations concurrently (4 workers for N=11--13, 2 for
  N=14--15, and 1 for N=16--18 by default). Diagonal J--Jpm scheduling gives
  simultaneously active workers different values of both couplings. The parent atomically saves raw
  spectra, metadata, metrics, and one blue/red three-row diagnostic PNG after
  every completion, then creates all per-hz J--Jpm `S_born` heatmaps and the
  per-N CSV/manifest before the N task exits.
- Calculation logs explicitly contain timezone-aware START/FINISH timestamps,
  process worker name/number, PID, parameters, and diagonalization/analysis
  durations. Parent CHECKPOINT lines include timestamps and worker identity.
  These fields are also persisted in every NPZ and metadata JSON.
- Production and optional postprocessing PBS files are
  `hpc/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.pbs` and
  `hpc/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6_aggregate.pbs`; exact
  smoke, staged, restart, and production commands are in the adjacent `.md`
  runbook. Headers use Python 3.11, `zeus_new_q`, 8 CPUs, 128 GB, and the
  requested mail settings. No Zeus job was submitted.
- A real local two-worker QuSpin smoke completed four distinct J--Jpm cases
  and automatically produced four diagnostic figures plus the N=4 heatmap at
  `work/anisotropic_sweep_multiprocess_smoke_v2_2026-07-18/smoke/`. Its DONE
  record names two different worker PIDs and timestamped calculations; its
  aggregate manifest is complete, and its inspected heatmap has no numeric
  cell annotations. Focused validation passes 6/6 new tests and
  20/20 existing Born/single-pixel service tests. Bash was unavailable on the
  Windows host, so PBS syntax received static contract validation rather than
  a local `bash -n` check.
- N=16--18 remain resource-risk requests, not validated feasibility claims.
  The runbook preserves the dense-memory warning and keeps their default
  process count at one.

### Periodic power-law reanalysis (2026-07-21)

- Replaced the report's wrapped-Cauchy composite heavy-tail criterion with a
  directly interpretable periodic power-law exponent.  For histogram bin
  centers `theta_b`, the fitted multinomial model is
  `p_b(alpha) proportional to Delta_theta_b * max(d_2pi(theta_b,0),
  Delta_theta/2)^(-alpha)`, where `d_2pi` is circular distance.  The bin-width
  floor regularizes the circle's pole without introducing an extra fitted
  parameter.
- `collapse/anisotropic_analysis.py` now exposes `fit_periodic_power_law`,
  stores `theta_power_law_alpha`, Jensen--Shannon fit divergence, likelihood
  per sample, and occupied-distance log-span, and provides alpha heatmap and
  Born-relationship plotters.  A fit is treated as resolved only when
  `JS <= 0.10`, angular coverage is at least `0.50`, and the occupied circular
  distance spans at least one decade.
- Reanalyzed all 3,722 delivered raw spectra.  Every spectrum has a finite
  fitted exponent and 49 unannotated J--Jpm alpha heatmaps were generated in
  `reports/anisotropic_parameter_study_2026-07-21/figures/theta_power_law_alpha_heatmaps/`.
  The complete N=11--14 grids contain 459, 536, 561, and 576 resolved fits,
  respectively.  At N=14, alpha and `S_born` have Spearman rho `-0.692`
  overall (`-0.605` within resolved fits).
- All 90 Born-like N=14 cases have `alpha` in `[0.519, 1.270]` with median
  `0.821`, but only 90 of 275 resolved cases with `alpha <= 1.27` are
  Born-like.  Shallow periodic decay is therefore an empirical necessary
  condition on this sampled grid, not a substitute for reciprocal-branch
  balance.  Tiny divergence on narrow angular support is explicitly rejected
  as an unresolved fit.
- The updated 8-page report and 19-slide Beamer deck are
  `output/pdf/anisotropic_spectrum_born_report_2026-07-21.pdf` and
  `output/pdf/anisotropic_spectrum_born_group_meeting_2026-07-21.pdf`.
  Both were rendered page-by-page/slide-by-slide and inspected without
  clipping; their LaTeX logs contain no warning, overfull, or underfull boxes.
  Focused validation is `12 passed` across
  `test_anisotropic_analysis.py`, `test_distribution_fit.py`, and
  `test_detector_resonance.py`.

## Two-pixel comparison across all conjecture Hamiltonians (2026-07-16)

- Repeated the four exact heavy-tail/Born evidence grids at equal total
  detector size: one 8-spin ring versus two independent 4-spin rings, with
  the historical opposite central-coupling signs.  Both use collective
  `Jx=0.01`, hence edge coefficient `0.01/sqrt(8)`, nine total qubits, and
  256 relative-evolution eigenvalues per spectrum.
- Coverage is 59 parameter pairs (7 `hz0`, 15 Ising `hz` neighborhoods, 12
  `Jpm` values including `Jpm=J`, and 25 `J=0,Jpm=1` field neighborhoods) at
  `t=1e3,1e4,1e5,1e6`: 118 Hamiltonians and 472 checkpointed spectra.
- Reusable definitions and paired metrics are in
  `collapse/conjecture_two_pixel_comparison.py`; the extended comparison core
  is `collapse/two_pixel_study.py`; the complete restartable driver is
  `examples/compare_two_pixel_conjecture_families.py`.
- Raw data are under `work/conjecture_two_pixel_comparison_2026-07-16/`.
  Metrics, paired distances, aggregates, manifest, 26 endpoint atlas pages,
  four topology heatmaps, and a synthesis plot are under
  `figures/conjecture_two_pixel_comparison_2026-07-16/` (31 PNG files total).
- Main measured result: splitting lowers the family-median Born score and
  polar coverage in all four sweeps.  It suppresses the plus-minus heavy-tail
  signatures: Cauchy-preferred fractions change `0.583 -> 0.229` in the
  fixed-field `Jpm` sweep and `0.840 -> 0.520` in the `J=0,Jpm=1` field sweep;
  the latter median density-tail exponent changes `2.07 -> 6.51`.
- At the matched point `hz0=hz=0.1`, the single detector passes the joint
  coverage/harmonic gate at all four times, while the split model passes only
  at `t=1e6` and has `S_born=-0.362` there.  No other spectrum passes both
  gates.  Pure-Ising splitting increases Cauchy-fit preference but retains a
  steep median exponent (`5.49`), low coverage (`0.292`), and harmonic
  localization (`0.938`), so the broadening is coherent/atomic rather than a
  Born-compatible continuous heavy tail.
- The self-contained LaTeX source is
  `reports/conjecture_two_pixel_comparison_2026-07-16.tex`; the visually
  verified 10-page report is
  `output/pdf/conjecture_two_pixel_comparison_2026-07-16.pdf`.  The rendered
  and overflow-tested 10-slide group-meeting deck is
  `output/two_pixel_conjecture_study_2026-07-16.pptx`.
- Larger even-size Zeus preparation is in
  `hpc/zeus_two_pixel_conjecture_comparison.pbs` and its adjacent Markdown
  runbook.  It targets `N_D=10,12,14`, Python 3.11, the pinned QuSpin versions,
  `zeus_new_q`, 8 CPUs, 128 GB, required mail settings, per-size logs,
  checkpoint/resume, dry-run, and smoke modes.  No Zeus job was submitted.
- Runtime manifest records Python 3.12.13, QuSpin 1.0.0,
  QuSpin Extensions 0.1.6, NumPy 2.4.6, SciPy 1.18.0, and Matplotlib 3.11.0.
  Focused tests pass; the full suite is `152 passed, 1 failed`, with the lone
  unrelated pre-existing failure in
  `test_anisotropic_larger_n_handoff_has_pbs_commands_and_logs` because
  `hpc/zeus_born_anisotropic_largerN.pbs` lacks the expected
  `chain_transverse_perturbative_N15` literal.

Reproduction command:

```powershell
$env:MPLCONFIGDIR='.mplconfig-conjecture-two-pixel'
$env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'
.\.venv\Scripts\python.exe examples\compare_two_pixel_conjecture_families.py --workers 4
```

## N=11..18 scaling launchers and Zeus arrays (2026-07-14)

- Added a shared checkpointed campaign service in
  `collapse/scaling_campaign.py` and four study-specific launchers:
  `run_hz0_atlas_scaling.py`, `run_hz_resonance_atlas_scaling.py`,
  `run_jpm_hz_atlas_scaling.py`, and `run_jpm_coupling_atlas_scaling.py`.
- Every launcher defaults to `N=11,12,13,14,15,16,17,18`, explicitly passes
  collective `Jx=0.01`, and validates `Jx_edge=0.01/sqrt(N)` before writing a
  per-size `DONE.json`.
- Each N owns isolated `raw/`, `figures/`, `logs/`, metrics, manifest, and
  status files. The campaign summary is atomically updated after each N, so
  completed results and plots survive later interruption.
- `ProcessPoolExecutor` supports independent-N multiprocessing for carefully
  selected smaller sizes. On Zeus the preferred parallel layer is one N per
  PBS array task, avoiding memory multiplication inside a node.
- Added four PBS arrays covering indices `11-18`:
  `hpc/zeus_hz0_atlas_N11_N18.pbs`,
  `hpc/zeus_hz_resonance_atlas_N11_N18.pbs`,
  `hpc/zeus_jpm_hz_atlas_N11_N18.pbs`, and
  `hpc/zeus_jpm_coupling_atlas_N11_N18.pbs`.
- User-specified scheduler settings are present in every header:
  `zeus_new_q`, `select=1:ncpus=8:mem=128gb`, `-m abe`, and notification
  address `matanhaller@campus.technion.ac.il`.
- After Zeus job `4444662[11]` exposed a relative-source failure, every PBS
  wrapper was made robust to submission from either the repository root or
  `hpc/`. It now resolves `REPO_ROOT` explicitly and reports a targeted error
  when the shared helper, campaign module, or study launcher was not copied to
  Zeus.
- The shared Zeus helper defaults to the user-confirmed `python3.11` and
  verifies `quspin==1.0.0` and `quspin-extensions==0.1.6`. It creates both PBS
  logs and per-N stdout/stderr logs.
- Full submission, dry-run, smoke, restart, output-layout, and resource notes
  are in `hpc/zeus_single_pixel_atlas_scaling.md`.
- Validation passed: all four launchers completed isolated N=4 end-to-end
  smoke campaigns (236 raw spectra and 40 atlases total), produced four
  validated `DONE.json` checkpoints plus stdout/stderr logs, all four PBS
  families passed Bash syntax checking, and the focused suite passed 53/53.
  See `reports/single_pixel_scaling_launchers_validation_2026-07-14.json`.
- Important feasibility limit: one dense complex relative matrix alone is
  about 64 GiB at N=16, 256 GiB at N=17, and 1 TiB at N=18. The scripts cover
  all requested sizes, but N=16..18 require staged pilots and may exceed Zeus
  hardware or require a future non-dense algorithm.

## Plus-minus `J=0, Jpm=1` field atlas (2026-07-14)

- The clean periodic detector Hamiltonian is
  `hz sum Zi + Jpm sum (sigma+_i sigma-_{i+1} + h.c.)`, with `hz0=0`,
  `J=0`, `Jpm=1`, collective `Jx=0.01`, and per-edge
  `Jx/sqrt(N)=0.0031622776601683794` at detector `N=10`.
- A 25-field sweep covers offsets `-0.05,-0.01,0,+0.01,+0.05` around
  `hz=-2,-1,0,+1,+2`, at `t=1e3,1e4,1e5,1e6`. It produced 100 raw spectra,
  twenty 3x5 atlases, a coupled summary, metrics, and a manifest under
  `figures/single_pixel_jpm_hz_atlas_2026-07-14`.
- The free-fermion active band is `|hz|<=Jpm`; `+-Jpm` are band edges and
  `+-2Jpm` are off-band controls. At the exact edges, coverage grows from
  70.8% to 91.7%, while `S_born` drops from -0.121 to -0.420. A 0.01 detuning
  restores a positive score, showing a sharp edge response.
- `hz=0` has positive `S_born=0.081--0.204` but only 45.8--54.2% polar
  coverage. `hz=+-2` stays narrow with near-zero score. The azimuthal second
  harmonic remains about 0.95--1.00 everywhere, so none of these cases yields
  isotropic Bloch support.
- `PlusMinusSpectralVarianceProvider` implements the exact finite-N spectral
  variance of Eq. (6.4) in the internal derivation as an injected theory
  strategy. The band-edge variance grows ballistically, but the no-fit wrapped
  Gaussian has large late-time L1 error against the atomic N=10 histograms.
- Validation passed for 100 spectra with 1024 finite eigenvalues each, 21
  high-resolution figures, coupling/model metadata, positive/negative-field
  symmetry, and rendering contracts. The focused suite passes 41/41.

## Corrected single-pixel coupling and `hz` resonance neighborhoods (2026-07-14)

- The coupling convention is now explicit and canonical: `Jx=0.01` is the
  collective coefficient before normalization; each `X0 Xi` interaction edge
  uses `Jx/sqrt(N)`. For the completed `N=10` sweeps this is
  `0.0031622776601683794` per edge.
- A fresh `hz0=0` sweep covers centers `hz=-2,0,+2` with detunings
  `-0.05,-0.01,0,+0.01,+0.05` at `t=1e3,1e4,1e5,1e6`. It produced 60 raw
  spectra, twelve 3x5 atlases, a coupled summary, metrics, and a manifest under
  `figures/single_pixel_hz_resonance_atlas_2026-07-14`.
- Exact resonances broaden polar support but all have negative `S_born`.
  `hz=+/-2` occupies 46/48 polar bins at every time with `S_born=-0.609` to
  `-0.787`; the `hz=0` exact point has `S_born=-0.211` to `-0.769`. The
  azimuthal second harmonic stays approximately `0.95--1.00`, demonstrating
  persistent meridional localization.
- The response is sharp: `0.01` detuning can retain broad support while
  changing `S_born` to small or positive values; `0.05` detuning strongly
  pole-localizes early-time distributions. Polar diagnostics are exactly
  symmetric under `hz -> -hz`.
- `collapse/single_pixel_atlas.py` implements a SOLID-style reusable core with
  separate immutable configuration, backend, spectrum computation, repository,
  sweep orchestration, and diagnostics services. Protocol-based fake-service
  tests exercise dependency inversion and resumability.
- Validation passed for all 60 spectra (1024 finite eigenvalues each), 13
  high-resolution figures, coupling metadata, symmetry, and rendering
  contracts. The focused test set passes 34/34.

## Central-field `hz0` atlas extension (corrected 2026-07-14)

- A fresh N=10 detector sweep was run for the clean single-pixel ring with
  `J=1`, fixed bath field `hz=0.1`, collective `Jx=0.01`, and per-edge
  coefficient `Jx/sqrt(N)=0.0031622776601683794`. The seven central fields are
  `hz0=0,0.05,0.09,0.10,0.11,0.15,0.20`; the four times are
  `1e3,1e4,1e5,1e6`. Raw spectra are isolated under
  `work/single_pixel_hz0_sweep_2026-07-14`.
- `examples/plot_single_pixel_hz0_diagnostic_atlas.py` creates four 3x7
  atlases. Both empirical `P(theta)` and `P(pi-theta)` distributions are
  histogram stairs. Occupied-bin `R(theta)` points are connected by lines,
  per the follow-up instruction. Row 3 retains the blue `v(lambda)` and red
  `-v(lambda)` Bloch branches.
- The corrected exact matched local resonance `hz0=hz=0.1` fills 44--46 of 48
  polar bins, while its second azimuthal harmonic is only 0.030--0.050. Its
  `S_born` values are 0.170, 0.033, 0.167, and 0.144, so broad polar and
  azimuthal support still does not guarantee the Born ratio.
- Canonical figures, metrics, manifest, and a concise interpretation are in
  `figures/single_pixel_hz0_diagnostic_atlas_2026-07-14`. Validation passed for
  all 28 raw 1024-eigenvalue spectra, five high-resolution figures, the
  histogram/connected-line rendering contract, and the exact matched
  resonance. The validator was rerun after forced regeneration with the
  corrected normalization.

## Diagnostic-atlas extension (2026-07-13)

The fresh study was extended using only the saved data under
`work/single_pixel_quspin_fresh_2026-07-12`; no result from the earlier study
was reused as evidence and no requested time was replaced by a nearby saved
time.

- `examples/plot_resonant_diagnostic_atlas.py` generates four matched 3x7
  N=10 atlases at `t=1e3,1e4,1e5,1e6`, with columns
  `hz=-3,-2,-1,0,1,2,3`. Row 1 contains blue `P(theta)` and red
  `P(pi-theta)` histograms plus the repository fixed, no-fit wrapped Gaussian
  and its reflection. Row 2 contains raw occupied-bin `R(theta)` points and the
  Born `cos^2(theta/2)` curve; empty bins are not connected. Row 3 contains
  blue `v(lambda)` and antipodal red `-v(lambda)` Bloch branches.
- The canonical figures, 28-row metric table, and manifest are in
  `figures/single_pixel_quspin_diagnostic_atlas_2026-07-13`. The coupled
  heatmap places `S_born`, Born RMSE, `cond(U00)`, second azimuthal harmonic,
  occupied-bin fraction, and wrapped-Gaussian L1 error on a common field/time
  grid.
- Measured result: at `hz=+/-2`, 46/48 polar bins are occupied at every
  requested time, while `S_born` remains negative (about -0.61 to -0.79 at
  N=10). The second azimuthal harmonic remains 0.953--1.000. Off resonance only
  2/48 bins are occupied, so the small raw Born RMSE there is a coverage
  artifact. Resonance broadens polar support but does not repair the reflected
  Born ratio or azimuthal support.
- Near-resonance N=8 evidence remains sharply localized: at `t=1e3`, changing
  `hz=2` to `2.01` changes `S_born` from about -0.406 to -0.059 and the theory
  variance from 100 to 0.296; changing `hz=0` to `0.01` changes `S_born` from
  about -0.215 to -0.008 and the variance from 200 to 0.592.
- The self-contained LaTeX source is
  `reports/single_pixel_diagnostic_atlas_2026-07-13.tex`; its visually checked
  13-page PDF is
  `output/pdf/single_pixel_diagnostic_atlas_2026-07-13.pdf`. The visually
  checked 16-slide group-meeting deck is
  `presentations/single_pixel_diagnostic_atlas_2026-07-13.pptx`, with companion
  speaker notes and rendered slide images in the same directory tree.
- Validation passed: 13 focused tests; the original fresh-data validator; the
  atlas validator (28 metrics rows, five high-resolution figures, 13 PDF pages,
  16 slides); and the presentation overflow checker. The machine-readable
  addendum validation record is
  `reports/single_pixel_diagnostic_atlas_validation_2026-07-13.json`.
- Reproduce with
  `python examples/plot_resonant_diagnostic_atlas.py` and validate with
  `python examples/validate_resonant_diagnostic_atlas.py`.

## Current canonical update: fresh resonant-hz study (2026-07-12)

The resonant single-pixel study requested on 2026-07-12 was performed **from
scratch** in a dedicated namespace. Earlier results were used only to locate
theory and conventions; they are not evidence for the results below. For this
study, this section supersedes the older continuation instruction retained
later in this document as historical context.

- Exact runtime: Python 3.12.13, `quspin==1.0.0`, and
  `quspin-extensions==0.1.6`; see `requirements-local-study.txt` and the run
  metadata. Distribution versions were verified with `pip show` (the modules'
  legacy `__version__` attributes report different internal values).
- Canonical parameters: `J=1`, `Jx=0.01`, `Jy=0`, `hz0=0`, periodic clean
  ring. The principal N=10 sweep completed at `hz=-3,-2,-1,0,1,2,3` and
  `t=100,1000,10000,100000,1000000` (35 raw time points; full dimension 2048).
- A fresh N=8 near-resonance sweep completed 27 fields around -2, 0, and +2,
  including offsets `0, +/-0.01, +/-0.05, +/-0.10, +/-0.25`, at all five
  required times (135 raw time points).
- A fresh N=8 long-time campaign completed 68 saved times for each of seven
  fields. Each reported average uses 66 distinct blocks strictly above 1000
  (476 raw time points). The first `long_average_N8` attempt is excluded because
  rounded filenames collided; the corrected canonical data are in
  `work/single_pixel_quspin_fresh_2026-07-12/long_average_N8_v2`.
- Fresh validation passed: 646 raw time points, maximum solve residual
  `7.51e-14`, maximum eigen residual `1.62e-13`, zero histogram-normalization
  error, and exact positive/negative-hz symmetry. See
  `reports/single_pixel_quspin_fresh_validation_2026-07-12.json`.
- Measured result: resonance broadens the polar distribution and increases
  `cond(U00)`, but does not recover the canonical Born statistic. At N=10 the
  resonant `S_born` values are generally negative, while off-resonant values
  are near zero; the azimuthal second harmonic remains about 0.95--1.00. The
  response is extremely sharp: at N=8 and t=1000, changing `hz=2` to `2.01`
  changes `S_born` from about -0.406 to -0.059. These are finite-size numerical
  observations, not thermodynamic conclusions.
- Canonical report: `reports/resonant_hz_study_2026-07-12.md` and `.pdf`.
  Figures and tables: `figures/single_pixel_quspin_fresh_2026-07-12`.
  Presentation: `presentations/single_pixel_quspin_fresh_2026-07-12.pptx` and
  its rendered slide-image directory and montage.
- Reproduce/validate with
  `python examples/validate_fresh_single_pixel_study.py`,
  `python examples/complete_resonant_hz_analysis.py --mandatory work/single_pixel_quspin_fresh_2026-07-12/mandatory_N10 --near-resonance work/single_pixel_quspin_fresh_2026-07-12/near_resonance_N8 --long-average work/single_pixel_quspin_fresh_2026-07-12/long_average_N8_v2 --out figures/single_pixel_quspin_fresh_2026-07-12`,
  and `python examples/build_resonant_hz_report_pdf.py`.
- The next scaling action is a dry run and one N=11 smoke task on Zeus using
  `hpc/zeus_resonant_hz_study_template.pbs` and
  `hpc/zeus_resonant_hz_study.md`. No Zeus job was submitted. Inspect memory
  and timing before increasing N.

This is the canonical restart document after the PC factory reset. A future
model or agent should read this file first, then read the current progress
report named below. All paths in this document are relative to the repository
root unless explicitly stated otherwise.

## Historical 2026-07-11 instruction (superseded by the fresh-study update above)

Resume this project; do not restart the investigation from scratch.

1. Confirm that the repository and large result files restored completely.
2. Read
   `reports/progress_2026-07-11/hamiltonian_born_progress_report_2026-07-11.md`.
3. Check `git status --short --branch`. At handoff creation Git was **not able
   to recognize this directory as a repository**, despite a `.git` directory
   being visible. Treat the current files as authoritative until Git metadata
   is restored or the remote history is recovered. Do not discard or overwrite
   files merely because they appear untracked in a newly cloned repository.
4. Recreate the Python environment and run the verification commands in this
   document.
5. The next research action is the bounded **N=11 detector resonant-coupling
   pilot on Zeus**, using `hpc/zeus_detector_eta_res_pilot_N11.md` and its PBS
   script. Do not scale the dense diagnostic beyond N=11 before evaluating its
   memory and scientific usefulness.
6. Import the pilot CSVs and correlate the new resonance metrics with the Born,
   coverage, tail, atom-fraction, and degeneracy diagnostics. Then update the
   dated progress report and this handoff.

## What this project is doing

The project investigates whether finite-dimensional unitary dynamics can
produce Born-rule-like statistics in a central-pixel/detector model. The active
numerical search varies detector Hamiltonians and weak central couplings, then
scores the eigenvalues of

$$
M(t)=U_{00}(t)^{-1}U_{10}(t)
$$

for radial Born behavior, Bloch-sphere angular coverage, heavy-tail behavior,
atomicity, and spectral degeneracy.

The current clean single-pixel ring family is

$$
H=h_{z0}\sigma_0^z+h_z\sum_{i=1}^{N}\sigma_i^z
+J\sum_{i=1}^{N}\sigma_i^z\sigma_{i+1}^z
+J_{\pm}\sum_{i=1}^{N}(\sigma_i^+\sigma_{i+1}^-+\sigma_i^-\sigma_{i+1}^+)
+\frac{J_x}{\sqrt N}\sigma_0^x\sum_i\sigma_i^x
+\frac{J_y}{\sqrt N}\sigma_0^y\sum_i\sigma_i^y.
$$

Here `N` is the detector size; the full system has `N+1` qubits. Broad scans
use a perturbative central-coupling convention and clean ring/all-site
coupling. In this geometry the QuSpin implementation can use cyclic
pixel-shift sectors. Do not assume magnetization conservation when XX/YY
central couplings or pairing terms break total $S^z$.

## Scientific state at the handoff

No new Zeus result directory had arrived after the 2026-07-08 import. The two
large scans remain incomplete. The unchanged all-criteria leader is:

| source | detector N | hz0 | t | J | Jpm | Jx | Jy | S_born | phi uniformity | tail alpha | radius atom fraction | full-H degenerate fraction |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| matched ring Jpm-Jx sweep | 16 | matched | 1000 | 1 | 0 | 0.055 | 0 | 0.884329 | 0.939872 | 3.07 | 0.000122 | 0.933 |

Its diagnostic PNG is:

```text
figures/zeus_born_pairwise_heatmaps_11x11_multiple_workers/matched_ring_Jpm_Jx_N16_11x11_t1e6/diagnostics/single_pixel_ring_N16_cc-all_Jx0.055_hz0.1_hz0-matched_Jpm0_Jxx0_Jyy0_Jy0_Jz0_Jzx0_Jcpm0_t1000_born_diagnostics.png
```

Imported scan status:

| scan | imported valid sizes | missing | best useful imported row |
|---|---|---|---|
| J-Jpm plane, Jy=0, Jx=0.01 | N=11..15 | N=16,17 | N=15, matched, t=316.228, J=0.1, Jpm=0.05: S=0.826400, phi=0.967606 |
| fixed J=0, Jpm=1, Jx-Jy plane | N=11..14 | N=15..17 | N=14, zero, t=10000, Jx=0.0025, Jy=0.075: S=0.798380, phi=0.766183 |
| older matched Jpm-Jx sweep | N=15,16 | none needed for leader comparison | N=16 leader above |

Important negative control: the raw J-Jpm maximum at `N=15`, `hz0=0`,
`t=1e6`, `J=0`, `Jpm=0.15`, `Jx=0.01` has `S_born=0.870276` but very poor
`phi_uniformity_score=0.096198`. A good radial score alone is not evidence of
adequate Bloch-sphere coverage.

## Analytical conclusion and newly implemented metric

For

$$
H=I_0\otimes H_D+\epsilon\sum_\alpha\sigma_0^\alpha\otimes B_\alpha,
$$

the detector-basis first-order kernel is

$$
K^{(1)}_{\alpha,ab}(t)=\epsilon(B_\alpha)_{ab}F_t(E_a-E_b),
\qquad
F_t(\Delta)=\begin{cases}
t,&\Delta=0,\\
(e^{i\Delta t}-1)/(i\Delta),&\Delta\ne0.
\end{cases}
$$

Exact degeneracy can create secular terms, while finite-time near-resonances
with $|E_a-E_b|\lesssim1/t$ can be equally relevant. The old literal claim
"heavy tails iff the interaction couples degenerate detector states" is
falsified: degeneracy is neither necessary nor sufficient. The refined target
is a broad, non-scalar finite-time resonant kernel that produces relative
eigenphases near the tangent pole.

`examples/detector_resonant_coupling_diagnostic.py` computes:

- `eta_res_exact` and `eta_res_window`, the fraction of interaction Frobenius
  weight in exact or finite-time resonant detector-basis elements;
- `eta_res_traceless_exact`, the exact-degenerate-block weight remaining after
  subtracting each block's scalar part; this vanishes if the interaction is
  scalar in every exactly degenerate block;
- `resonant_effective_elements`, an inverse-participation count distinguishing
  isolated resonances from a broad resonant kernel.

The code and its N=5 smoke CSV were completed on 2026-07-11. This is the main
new advance to carry forward.

## Files most relevant to the continuation

Files changed in the latest completed work session:

```text
examples/detector_resonant_coupling_diagnostic.py
hpc/zeus_detector_eta_res_pilot_N11.md
hpc/zeus_detector_eta_res_pilot_N11.pbs
figures/local_degenerate_coupling_conjecture_2026-07-11/local_j0_jpm1_eta_res_nonscalar_smoke.csv
reports/progress_2026-07-11/hamiltonian_born_progress_report_2026-07-11.md
```

Core search/postprocessing code to inspect before modifying behavior:

```text
examples/born_hamiltonian_search.py
examples/summarize_born_search_results.py
examples/born_candidate_diagnostics.py
examples/born_candidate_stability.py
examples/evaluate_born_postprocess_gate.py
collapse/hamiltonians/numpy_hamiltonians.py
collapse/hamiltonians/quspin_hamiltonians.py
```

Key scientific notes:

```text
reports/hamiltonian_born_search_status.md
reports/resonant_kernel_conjecture_2026-07-07.md
reports/four_model_finite_time_eigenvalue_derivation_2026-07-10.md
reports/weak_kernel_interacting_detector_note_2026-07-03.md
reports/perturbative_wrapped_gaussian_heavy_tail_proof_2026-07-05.md
```

## Environment recovery

At handoff creation:

- OS/shell: Windows / PowerShell locally; PBS/Linux on Zeus.
- Local interpreter: Python 3.12.10.
- No `pyproject.toml`, `setup.py`, or requirements file was found at the
  repository root. Dependency recovery is therefore manual unless packaging
  metadata is added later.
- Imports used by the code/tests include NumPy, SciPy, Matplotlib, QuSpin, and
  pytest. Jupyter is needed only for the notebooks.
- Run commands from the repository root so local imports and `examples` path
  assumptions resolve correctly.

Suggested clean-environment bootstrap (adjust QuSpin/Python versions if its
current compatibility requires it):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy scipy matplotlib pytest jupyter quspin
```

After the environment works, create and pin a requirements file; do not guess
exact old versions without checking any restored environment metadata or Zeus
modules first.

## Verification status and commands

The 2026-07-11 progress report records successful verification of:

```powershell
python -m py_compile examples/detector_resonant_coupling_diagnostic.py
# plus the N=5 diagnostic smoke that produced the CSV listed above
```

During creation of this handoff, `python -m pytest -q` was attempted but did
not complete within a 65.5-second command timeout and emitted no test summary.
Record this as **inconclusive**, not as a test failure. Re-run with more time
after restoring files locally (OneDrive hydration may have caused the delay):

```powershell
python -m py_compile examples/detector_resonant_coupling_diagnostic.py
python -m pytest -q
```

Then inspect the smoke data:

```powershell
Get-Content figures\local_degenerate_coupling_conjecture_2026-07-11\local_j0_jpm1_eta_res_nonscalar_smoke.csv
```

## Exact next HPC action: N=11 resonance pilot

Do not submit from a local Windows session. From the repository root on Zeus,
follow `hpc/zeus_detector_eta_res_pilot_N11.md`, currently:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_detector_eta_res_pilot_N11_${RUN_TAG}"
LOG_ROOT="logs/zeus_detector_eta_res_pilot_N11_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-2 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",MIN_N=11,MAX_N=11,TOP_ROWS=24,PHI_MIN=0.7,ENERGY_TOL=1e-9,WINDOW_FACTOR=1.0,REQUIRE_NONZERO_COUPLING=1 \
  hpc/zeus_detector_eta_res_pilot_N11.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Expected logs:

```text
logs/zeus_detector_eta_res_pilot_N11_<tag>/task_1_eta_res.log
logs/zeus_detector_eta_res_pilot_N11_<tag>/task_2_eta_res.log
```

Expected CSVs:

```text
figures/zeus_detector_eta_res_pilot_N11_<tag>/j_jpm_jy0_N11_eta_res.csv
figures/zeus_detector_eta_res_pilot_N11_<tag>/j0_jpm1_jx_jy_N11_eta_res.csv
```

The pilot intentionally does not use `BORN_WORKERS`: each task repeatedly
forms dense detector eigensystems, so process workers would compete for the
same memory. The PBS array provides two-way parallelism. Keep the dense pilot
at N=11 until resource use is measured.

After importing its outputs:

1. Validate row counts, NaNs/infinities, task logs, and parameter metadata.
2. Correlate `eta_res_window`, `eta_res_traceless_exact`, and
   `resonant_effective_elements` with `S_born`, `phi_uniformity_score`, tail
   alpha, radius atom fraction, and full-H degeneracy.
3. Compare successful candidates and the poor-phi controls; avoid interpreting
   correlation based only on the top radial score.
4. Decide whether the dense metric is useful enough to justify a
   sector-based/sampled estimator for larger N.
5. Update the dated report, `reports/hamiltonian_born_search_status.md`, and
   this handoff with exact output paths and results.

## Existing continuation jobs for incomplete broad scans

These are secondary to the N=11 pilot, but remain unfinished. Re-check the
latest imported directories and scheduler state before resubmitting, to avoid
duplicate work.

J-Jpm scan, missing N=16,17:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j_jpm_fixed_jx_jy0_N16_N17_continue_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j_jpm_fixed_jx_jy0_N16_N17_continue_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"
qsub -J 11-14 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_SPECTRA=0 \
  hpc/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Jx-Jy scan, missing N=15..17:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N15_N17_continue_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N15_N17_continue_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"
qsub -J 9-14 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_SPECTRA=0 \
  hpc/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N11_N17.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Research backlog, in priority order

1. Run and analyze the bounded N=11 resonant-coupling pilot.
2. Ingest missing high-N rows and apply all gates jointly: Born score, tail,
   phi coverage, and low atomicity. Never promote a point on radial score alone.
3. Relate the spectral measure of $P_{\delta_t}BP_{\delta_t}$ to continuity
   versus atomicity of the first-order eigenphase distribution.
4. If supported by the pilot, design a deliberately degenerate Hamiltonian
   family with a controllable non-scalar block splitting. Raw degeneracy is not
   itself the design target.
5. Only then consider implementing a scalable sector/sampled resonance metric.

## Repository and preservation warning

At this snapshot the working directory was:

```text
C:\Users\matan\OneDrive - Technion\Graduate\Research\1 Projects\Collapse and Chaos\Code\Python\collapse
```

Many files, including `.git`, showed OneDrive reparse-point attributes. `git
status` and `git log` both returned:

```text
fatal: not a git repository (or any of the parent directories): .git
```

Consequences:

- The handoff cannot reliably identify committed versus uncommitted files or a
  current commit hash.
- Before the factory reset, ensure this entire directory is fully synced or
  copied to independent storage. A green OneDrive icon should not be the only
  backup; verify by opening/copying critical files and, ideally, make a second
  archive or push a recovered Git repository to a remote.
- Preserve large `figures/`, `reports/`, `hpc/`, and `work/` outputs, not only
  Python source. Much of the research state lives in generated CSVs and notes.
- After restore, if `.git` remains invalid, recover/clone the remote into a new
  directory and copy this snapshot over it without deleting either copy. Then
  inspect diffs before committing.

## Definition of a successful restart

A future agent has successfully resumed when it can:

- import `collapse` and compile the diagnostic script;
- run the test suite (or document specific failures);
- locate the leader PNG and all latest-session files;
- account for the two incomplete scans without duplicate submission;
- run or ingest the N=11 pilot;
- report whether non-scalar resonant weight predicts the jointly gated
  Born-like candidates better than raw spectral degeneracy.

When progress is made, append a short dated update here or replace the snapshot
sections with a newer canonical state, while retaining important negative
results and exact artifact paths.
# 2026-07-14: fixed-J plus-minus-coupling atlas

- Added a fresh `N=10` single-pixel sweep at fixed `J=1`, `hz=0.1`, `hz0=0`,
  collective `Jx=0.01` (`Jx/sqrt(N)` per edge), varying
  `Jpm = 0, 0.001, 0.01, 0.03, 0.1, 0.3, 0.5, 0.75, 1, 1.5, 2, 3`.
- The exact requested `Jpm=J=1` point is included and marked in all figures.
- Production driver: `examples/plot_single_pixel_jpm_sweep_atlas.py`.
- Figures and self-contained findings:
  `figures/single_pixel_jpm_sweep_atlas_2026-07-14/README.md`.
- Raw outputs: `work/single_pixel_jpm_sweep_2026-07-14` (48 spectra, four
  requested late times).
- `collapse/single_pixel_atlas.py` now provides
  `DetectorSpectralVarianceProvider`, an exact finite-N spectral strategy for
  mixed ZZ plus plus-minus detector Hamiltonians. The previous
  `PlusMinusSpectralVarianceProvider` name remains compatible.
- Principal result: the coupling dependence is nonmonotonic. The full-grid
  maximum is `S_born=0.3028` at `Jpm=J=1,t=1e6`, but coverage is only 0.625,
  the second azimuthal harmonic is 0.986, and the spectral-WG L1 error is
  1.152; it is therefore not globally Born-like.
- Validator: `examples/validate_single_pixel_jpm_sweep_atlas.py`.

# 2026-07-24: exact-degeneracy iff wrapped-heavy falsification campaign

- Added a configuration-driven, restartable single-pixel campaign for
  `N=13,14,15,16,17,18`, `t=1e6`, `hz0=0`, collective `Jx=0.01`, and edge
  coefficient `Jx/sqrt(N)`.
- The universal conjecture “wrapped-heavy `P(theta)` iff `V` couples
  degenerate detector eigenstates” is analytically false in both directions.
  The concise proof and the existing 880-point contingency evidence are in
  `reports/degeneracy_heavy_tail_iff_2026-07-24.md`.
- Production configuration:
  `configs/zeus_degeneracy_heavy_tail_iff_N13_N18.json`. It contains 11 cases:
  clean-Ising exact resonances/detunings and four non-pure-Ising SU(2)
  exchange cases. Zero parameters are allowed as exact symmetry limits; every
  nonzero `|hz|`, `|J|`, and `|Jpm|` is at least `10*Jx`, enforced on load.
- `collapse/degeneracy_heavy_tail_campaign.py` provides analytic, all-N
  activation certificates for:
  1. `Jpm=0`, where coupled gaps are
     `2|hz-2J|, 2|hz|, 2|hz+2J|`; and
  2. `Jpm=2J`, where SU(2) invariance makes every nonzero `V` transition have
     gap `2|hz|`.
- The service parallelizes different Hamiltonian configurations with
  `ProcessPoolExecutor`, logs timestamp/worker/PID per calculation, and
  atomically saves raw data, metrics, and figures after every case. Each
  `blue_red.png` contains `P(theta)`/`P(pi-theta)` histograms, connected
  `R(theta)` versus Born, and blue/red Bloch-sphere points.
- Zeus files:
  `hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.pbs`,
  `hpc/zeus_degeneracy_heavy_tail_iff_aggregate.pbs`, and
  `hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.md`. The main array is unified:
  each completed N saves its own aggregate products and then refreshes the
  cross-N summary under an atomic lock. The aggregation-only PBS is retained
  for manual recovery, not normal operation. Both PBS scripts use Zeus
  `python3.11` directly; they do not create or activate a virtual environment,
  and they fail fast unless the required QuSpin package versions are present.
- Local validation used Python 3.12.13. Targeted campaign tests passed
  (`5 passed`); adjacent anisotropic sweep/analysis tests passed
  (`11 passed`); both PBS files passed `bash -n`. A real N=4 multiprocessing
  smoke run, including a non-Ising case and all three diagnostic rows,
  completed under `work/validation_degeneracy_heavy_tail_campaign/smoke`.
- No N=13..18 Zeus jobs were submitted locally. Run the exact single `qsub`
  command in the runbook from the repository root; aggregation is now part of
  each array element and needs no second submission.

# 2026-07-24: exhaustive relative-scale regime campaign

- Added `collapse/relative_scale_campaign.py`,
  `examples/run_relative_scale_regime_campaign.py`, and
  `configs/zeus_relative_scale_regimes_N13_N18.json`.
- The matrix is exhaustive in relative magnitudes `(abs(hz),J,Jpm)`: all 13
  positive weak orderings, all nine one-zero regimes, the three
  single-nonzero limits, and the all-zero limit. Four extra points test field
  sign, common absolute scale, the Ising-resonance surface, and the SU(2)
  line: 30 cases per N and 180 production simulations total.
- Conditions are `N=13..18`, `t=1e6`, `hz0=0`, collective `Jx=0.01`, and
  edge coefficient `Jx/sqrt(N)`. Every nonzero `abs(hz)`, `J`, and `Jpm` is
  at least `10*Jx`; exact zeros are admitted as limiting regimes. Every
  ordinary strict hierarchy step is also at least 10:1 (`>>`/`<<`), while
  `hz=2J` and `Jpm=2J` remain exact special-control relations.
- `hpc/zeus_relative_scale_regimes_N13_N18.pbs` uses Python 3.11 directly,
  `zeus_new_q`, 8 CPUs, 128 GB, the requested email directives, and
  multiprocessing across regime configurations. It checkpoints after every
  Hamiltonian and performs per-N plus locked cross-N aggregation in the same
  job. Run instructions are in
  `hpc/zeus_relative_scale_regimes_N13_N18.md`.
- Every case produces the established blue/red three-row diagnostic:
  histogram `P(theta)`/`P(pi-theta)`, connected `R(theta)` versus Born, and
  Bloch-sphere point distributions. Cross-N heatmaps have no cell numbers.
- Validation: 8 targeted campaign/conjecture tests passed, the PBS passed
  `bash -n`, and a real two-worker N=4 smoke run completed at
  `work/validation_relative_scale_campaign/smoke`, including all case,
  per-N, and cross-N checkpoint products.

# 2026-07-27: compact all-case detector energy-gap atlas

- Added `examples/build_vab_activation_all_cases_atlas.py`, a restartable
  generator covering all 880 complete `N=14`, `t=1e6` configurations in
  `work/zeus_single_pixel_anisotropic_20260718_130606`.
- Each case pairs the normalized detector gap heatmap
  `-log10(max(|Ea-Eb|/(Emax-Emin),1e-12))` at `N_D=8` with the existing
  dynamical diagnostic cropped to only the blue/red
  `P(theta)`/`P(pi-theta)` histograms and connected `R(theta)` versus Born.
  No dynamics were recomputed.
- The final atlas is compressed into 37 A4-landscape contact sheets (24 cases
  per sheet, 16 on the last) plus one reading-guide page:
  `output/pdf/vab_activation_all_cases_2026-07-27.pdf` (38 pages).
- Reusable per-case figures, contact sheets, manifest, and case index are under
  `reports/vab_activation_all_cases_2026-07-27/`.
- Validation: 880 heatmaps, 880 cropped diagnostics, and 37 contact sheets
  were produced with zero case errors; the generator passes `py_compile`;
  two clean LaTeX passes produced a 38-page A4 PDF; all 38 pages were rendered
  with Poppler and representative early, middle, and final pages were visually
  inspected for clipping and layout.

# 2026-07-28: three-group detector-degeneracy multiplicity atlas

- Added `examples/build_detector_degeneracy_group_atlas.py`, which applies the
  registered broadness and Born gates to all 880 complete `N=14`, `t=1e6`
  anisotropic cases and separates them into 90 broad/Born-like, 348
  broad/non-Born, and 442 non-broad cases.
- Reused every minus-log energy-gap heatmap and cropped `P(theta)`/`R(theta)`
  diagnostic from the 2026-07-27 atlas. Recomputed only the inexpensive
  `N_D=8` detector eigenspectra needed to recover each full multiplicity
  vector, using the established absolute degeneracy tolerance `1e-9`.
- For every case, generated a log-count histogram of energy-subspace
  multiplicities and recorded `f_deg`, `m_max`, the number of degenerate
  subspaces, the distinct-energy fraction, and the degenerate-pair probability
  `F_pair=sum_g m_g(m_g-1)/(D(D-1))`.
- Main result: raw degeneracy extent does not distinguish broad from non-broad
  cases (rank AUCs 0.482-0.531 across the five reported metrics). Within broad
  cases, Born-like outcomes favor milder degeneracy: median `m_max=4` versus
  `6`, median `F_pair=0.00358` versus `0.00420`, and the `F_pair` AUC is 0.279
  when larger values are scored as Born-like. The shift is highly significant
  but overlapping, so multiplicity is neither a broadness criterion nor the
  missing Born condition; coupling activation and branch reciprocity remain
  necessary dynamical information.
- Outputs are under
  `reports/detector_degeneracy_group_atlas_2026-07-28/`; the final 41-page
  A4-landscape report is
  `output/pdf/detector_degeneracy_group_atlas_2026-07-28.pdf`.
- Validation: 880 case-index rows, 880 multiplicity plots, 38 group-separated
  contact sheets, and zero multiplicity-invariant failures; all four scalar
  degeneracy summaries exactly reproduce the prior activation audit. The
  generator passes `py_compile`; two clean LaTeX passes produced exactly 41
  pages with no LaTeX/package/box warnings; all pages were rendered with
  Poppler and reviewed as an overview, with full-size checks of the analysis
  pages and representative first/final pages from every group.

# 2026-07-28: all-case detector spectrum and V_ab activation atlas

- Extended `examples/build_detector_degeneracy_group_atlas.py` to fully
  diagonalize every `N_D=8` detector Hamiltonian, transform
  `V=sum_i sigma_i^x` to the sorted detector-energy eigenbasis, and render
  `log10(|V_ab|^2/Tr(V^2))` with fixed `[-12,0]` limits for all 880 cases.
- Restored the original registered Born gate after user correction:
  `S_born>=0.75`, `born_rmse<=0.15`, and angular coverage `>=0.50`. Final
  groups are 90 broad/Born-like, 348 broad/non-Born, and 442 non-broad.
- Every atlas tile contains four explicitly equal framed plot boxes:
  minus-log energy gaps, `V_ab`, degenerate-subspace multiplicities, and the
  cropped `P(theta),P(pi-theta),R(theta)` diagnostics. There are 44
  group-separated contact sheets.
- Main result: exact degenerate-block activation has only modest broadness
  discrimination (AUC 0.595) and occurs in 10/90 broad/Born, 90/348
  broad/non-Born, and 16/442 non-broad cases. It is therefore favorable but
  neither necessary nor sufficient. The finite-time resonant kernel fraction
  is the decisive broadness correlate (AUC 0.937; Spearman rho with fitted
  alpha `-0.854`). Within broad cases it is nearly uncorrelated with
  `S_born` (rho `0.045`), so Born similarity remains a separate branch-balance
  condition.
- Outputs are under `reports/vab_coupling_group_atlas_2026-07-28/`; the final
  49-page A4-landscape PDF is
  `output/pdf/vab_coupling_group_atlas_2026-07-28.pdf`.
- Validation: all 880 cases have all four assets; 880 `V_ab` heatmaps and 44
  contact sheets exist; Hamiltonian/coupling Hermiticity errors are zero;
  maximum relative eigenpair residual is `3.17e-15`; maximum eigenvector
  orthonormality error is `1.86e-15`; coupling-transform norm error is below
  `4.72e-16`; targeted tests report `7 passed`; the final PDF has 49 pages and
  its five analysis pages plus representative first, middle, and final atlas
  pages were rendered and visually checked without clipping or unequal panel
  frames.
