# Zeus N=13 detector-spectrum atlas

This job repeats the validated N=11 full detector-spectrum analysis at
\(N=13\), dimension \(2^{13}=8192\), for all 30 regimes in
`configs/zeus_relative_scale_regimes_N13_N18.json`.

For every regime it fully diagonalizes

\[
H_D=h_z\sum_i Z_i+J\sum_iZ_iZ_{i+1}
+J_\pm\sum_i(\sigma_i^+\sigma_{i+1}^-+\mathrm{h.c.}),
\qquad V=\sum_iX_i,
\]

and saves the sorted eigenvalues, full \(V_{ab}\), energy-gap matrix,
degeneracy mask, degeneracy-masked \(V_{ab}\), invariant block summaries,
validation metadata, and the common-style six-panel heatmap.

## Submit

Synchronize the repository to Zeus, then run from the repository root:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="work/zeus_detector_spectra_N13_${RUN_TAG}"
LOG_ROOT="logs/zeus_detector_spectra_N13_${RUN_TAG}"

qsub \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_detector_spectra_N13.pbs
```

The PBS job uses `python3.11` directly, without virtual-environment
activation. It requests `zeus_new_q`, eight CPUs, 128 GB RAM, and email
notifications.

## Dry run

This validates paths, dependencies, all 30 configurations, and the N=13
resource estimate without diagonalizing:

```bash
qsub \
  -v DRY_RUN=1,RUN_ROOT="work/zeus_detector_spectra_N13_dryrun",LOG_ROOT="logs/zeus_detector_spectra_N13_dryrun" \
  hpc/zeus_detector_spectra_N13.pbs
```

## Checkpoints and restart

The job processes one dense regime at a time and gives its BLAS/LAPACK solve
all eight CPUs. This avoids multiplying the approximately 5.95 GiB
conservative per-regime dense-memory estimate.

After every regime, the following files are complete and reusable:

```text
$RUN_ROOT/regimes/<case_id>/
  spectral_data.npz
  degenerate_blocks.csv
  metadata.json
```

When all regimes are complete, the job creates each
`spectral_heatmaps.png`, the global CSV summaries, `REPORT.md`, and
`run_manifest.json`.

If the job is interrupted, resubmit with exactly the same `RUN_ROOT`.
Regimes whose metadata exists, reports `status=complete`, passes validation,
and records `N=13` are reused rather than recomputed.

## Monitor

```bash
qstat -u "$USER"
tail -f "$LOG_ROOT"/N13_*.log
find "$RUN_ROOT/regimes" -name metadata.json | wc -l
```

Every scheduler-log line contains a timestamp and `worker=1`. The worker is
the single memory-safe regime worker; its eight numerical threads execute the
dense LAPACK calculation.

## Main outputs

```text
$RUN_ROOT/
  REPORT.md
  run_manifest.json
  computational_summary.csv
  spectral_summary.csv
  coupling_summary.csv
  all_degenerate_blocks.csv
  regimes/<case_id>/spectral_heatmaps.png
  regimes/<case_id>/spectral_data.npz
  regimes/<case_id>/degenerate_blocks.csv
  regimes/<case_id>/metadata.json
```
