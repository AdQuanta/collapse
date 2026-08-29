# Zeus Pairwise Born-Stability Heatmaps

This runbook submits `hpc/zeus_born_pairwise_heatmaps.pbs`, which runs
`scripts/born_pairwise_heatmap.py` for two-parameter stability checks around
current successful points and degeneracy controls.

The script writes:

- scheduler logs: `${LOG_ROOT}/${RUN_NAME}.${PBS_JOBID}.${TASK_ID}.log`
- per-output logs: `${RUN_ROOT}/${RUN_NAME}/run.log`
- heatmaps: `${RUN_ROOT}/${RUN_NAME}/heatmap_*.png`
- flat metric table: `${RUN_ROOT}/${RUN_NAME}/pairwise_summary.csv`
- top-row diagnostics with full Hamiltonian spectra:
  `${RUN_ROOT}/${RUN_NAME}/diagnostics/*.png`

`BORN_WORKERS` defaults to `2` because the N15/N16 heatmap tasks can hold
multiple large diagonalizations in memory.  Increase it only after checking
memory usage in logs.

## Tasks

| task | run name | purpose |
|---:|:---|:---|
| 1 | `matched_ring_N15_Jx_hz` | local stability around matched-ring success |
| 2 | `zero_ring_slide8_Jpm_Jx_N15` | zero-field `Jpm`/central-coupling stability |
| 3 | `anisotropic_ring_Jxx_Jyy_N15` | anisotropic `XX/YY` stability around current success |
| 4 | `weak_disorder_ring_dJ_dhz_N15` | weak-disorder stability and degeneracy lifting |
| 5 | `degenerate_flat_lift_Jx_hz_N13` | exact-degeneracy control with weak lift |

## Manual Submit Block

Run on Zeus from the repository root:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_born_pairwise_heatmaps"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_${RUN_TAG}"
PLOT_TOP=8
PLOT_MAX_BLOCH_POINTS=6000
BORN_WORKERS=2

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-5 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_born_pairwise_heatmaps.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "Scheduler logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "Output logs: $RUN_ROOT/<run-name>/run.log"
echo "Heatmaps: $RUN_ROOT/<run-name>/heatmap_*.png"
```

## Conservative Pilot

To test scheduler syntax and memory before launching the full array:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_born_pairwise_heatmaps_pilot"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_pilot_${RUN_TAG}"

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP=4,PLOT_MAX_BLOCH_POINTS=4000,BORN_WORKERS=1 \
  hpc/zeus_born_pairwise_heatmaps.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```
