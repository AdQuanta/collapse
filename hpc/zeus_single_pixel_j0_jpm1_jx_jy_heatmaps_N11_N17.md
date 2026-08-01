# Zeus Runbook: Single-Pixel `J=0`, `Jpm=1`, `Jx`-`Jy` Heatmaps

This submits `hpc/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N11_N17.pbs`.

Hamiltonian scanned:

```text
H = hz0 sigma_0^z
  + hz sum_i sigma_i^z
  + J sum_i sigma_i^z sigma_{i+1}^z
  + Jpm sum_i (sigma_i^+ sigma_{i+1}^- + sigma_i^- sigma_{i+1}^+)
  + (Jx_unscaled/sqrt(N)) sigma_0^x sum_i sigma_i^x
  + (Jy_unscaled/sqrt(N)) sigma_0^y sum_i sigma_i^y
```

with `J=0`, `Jpm=1`, ring detector connectivity, all-site central coupling,
`hz=0.1`, and `hz0 in {0, hz}`. The sweep grid is `Jx_unscaled x
Jy_unscaled`, defaulting to 11 perturbative values in each direction.

The script enforces `BACKEND=quspin`, `CONNECTIVITY=ring`, and
`CENTRAL_COUPLING=all`, which uses the cyclic detector-site shift symmetry in
the existing single-pixel ring infrastructure.

Diagnostic spectrum and level-spacing panels are disabled by default in this
run (`PLOT_SPECTRA=0`) because they add extra spectral work during diagnostic
plotting. Heatmaps still include the main Born metrics and the energy
degeneracy metrics produced during the primary diagonalization. For a narrow
rerun of selected tasks, set `PLOT_SPECTRA=1`.

## Full Submission

Run from the repository root on Zeus after uploading the updated code:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N11_N17_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N11_N17_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-14 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_SPECTRA=0 \
  hpc/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N11_N17.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Pilot Submission

Use this for the two `N=11` tasks before launching the full array. Zeus rejected
`-J 1` previously; for a single task use `-J 1-1`.

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_pilot_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_pilot_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-2 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP=4,PLOT_MAX_BLOCH_POINTS=2500,BORN_WORKERS=1,PLOT_SPECTRA=0 \
  hpc/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N11_N17.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Narrow Spectral Rerun

After identifying leading rows from `pairwise_summary.csv`, rerun a small task
with spectrum/level-spacing diagnostics enabled:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_spectra_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_spectra_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",JX_VALUES="0.01 0.02 0.03",JY_VALUES="0.01 0.02 0.03",TIMES="1000 10000",PLOT_TOP=4,BORN_WORKERS=1,PLOT_SPECTRA=1 \
  hpc/zeus_single_pixel_j0_jpm1_jx_jy_heatmaps_N11_N17.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Outputs

Each array task writes a checkpoint after completing one `(N, hz0)` branch.
Task directories are named like `N11_hz0-zero` or `N16_hz0-matched`.

- Results: `$RUN_ROOT/N11_hz0-zero/`
- CSV table: `$RUN_ROOT/N11_hz0-zero/pairwise_summary.csv`
- Heatmaps: `$RUN_ROOT/N11_hz0-zero/heatmap_*.png`
- Diagnostics: `$RUN_ROOT/N11_hz0-zero/diagnostics/`
- Run log: `$LOG_ROOT/N11_hz0-zero/run.log`
- Scheduler context: `$LOG_ROOT/N11_hz0-zero/scheduler_context.log`
- Completion marker: `$RUN_ROOT/N11_hz0-zero/CHECKPOINT_DONE.txt`
