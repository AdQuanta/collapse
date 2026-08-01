# Zeus 11x11 Pairwise Born Heatmaps

Manual handoff only. Do not SSH from Codex and do not submit jobs from Codex.
Run these blocks yourself on Zeus from the repository root, usually
`$HOME/research/collapse`.

PBS script:

```text
hpc/zeus_born_pairwise_heatmaps_11x11.pbs
```

This handoff runs dense `11x11` pairwise heatmaps around current successful
Born-like candidates. The long-time grid is:

```text
t = 1000, 10000, 100000, 1000000
```

The PBS defaults are intentionally conservative:

```text
#PBS -l select=1:ncpus=8:mem=192gb
BORN_WORKERS=1
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
BLIS_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1
NUMEXPR_NUM_THREADS=1
```

Increase `BORN_WORKERS` only after a pilot confirms memory headroom. Keep each
BLAS backend at one thread so multiprocessing does not oversubscribe the node.

## Outputs

Each array task writes:

```text
Scheduler log:
<LOG_ROOT>/<run_name>.<PBS_JOBID>.<TASK_ID>.log

Output progress log:
<RUN_ROOT>/<run_name>/run.log

Flat heatmap table:
<RUN_ROOT>/<run_name>/pairwise_summary.csv

Heatmaps:
<RUN_ROOT>/<run_name>/heatmap_*.png

Diagnostic index and figures:
<RUN_ROOT>/<run_name>/index.md
<RUN_ROOT>/<run_name>/diagnostics/*.png
```

## Task Map

| task | run name | purpose |
|---:|:---|:---|
| 1 | `matched_ring_Jx_hz_N15_11x11_t1e6` | N15 local stability around the matched-ring `Jx,hz` success |
| 2 | `matched_ring_Jx_hz_N16_11x11_t1e6` | N16 feasibility/finite-size copy of task 1 |
| 3 | `matched_ring_Jpm_Jx_N15_11x11_t1e6` | N15 exchange/central transverse stability |
| 4 | `matched_ring_Jpm_Jx_N16_11x11_t1e6` | N16 feasibility/finite-size copy of task 3 |
| 5 | `anisotropic_ring_Jxx_Jyy_N15_11x11_t1e6` | N15 anisotropic `XX/YY` stability |
| 6 | `anisotropic_ring_Jxx_Jyy_N16_11x11_t1e6` | N16 feasibility/finite-size copy of task 5 |
| 7 | `weak_disorder_ring_dJ_dhz_N15_11x11_t1e6` | N15 weak-disorder degeneracy-lifting stability |
| 8 | `all_to_all_sz_Jpm_Jcpm_N15_11x11_t1e6` | N15 all-to-all Sz-conserving comparison |

N16 is included for the ring candidate families that are most feasible and most
important for finite-size validation. The weak-disorder and all-to-all controls
are N15 in this handoff; only promote them to N16 after the pilot logs show
comfortable memory and wall-time margins.

## Conservative Pilot

Run one N15 task first:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_born_pairwise_heatmaps_11x11_pilot"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_11x11_pilot_${RUN_TAG}"
PLOT_TOP=4
PLOT_MAX_BLOCH_POINTS=4000
MAX_DETECTOR_SPECTRUM_QUBITS=12
BORN_WORKERS=1

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS",MAX_DETECTOR_SPECTRUM_QUBITS="$MAX_DETECTOR_SPECTRUM_QUBITS",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_born_pairwise_heatmaps_11x11.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "qsub job id: $LOG_ROOT/qsub_jobid.txt"
echo "scheduler log: $LOG_ROOT/matched_ring_Jx_hz_N15_11x11_t1e6.<PBS_JOBID>.1.log"
echo "output log: $RUN_ROOT/matched_ring_Jx_hz_N15_11x11_t1e6/run.log"
```

Pilot an N16 task separately before launching the full N16 subset:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_born_pairwise_heatmaps_11x11_pilot_N16"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_11x11_pilot_N16_${RUN_TAG}"
PLOT_TOP=4
PLOT_MAX_BLOCH_POINTS=4000
MAX_DETECTOR_SPECTRUM_QUBITS=12
BORN_WORKERS=1

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 2 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS",MAX_DETECTOR_SPECTRUM_QUBITS="$MAX_DETECTOR_SPECTRUM_QUBITS",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_born_pairwise_heatmaps_11x11.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "qsub job id: $LOG_ROOT/qsub_jobid.txt"
echo "scheduler log: $LOG_ROOT/matched_ring_Jx_hz_N16_11x11_t1e6.<PBS_JOBID>.2.log"
echo "output log: $RUN_ROOT/matched_ring_Jx_hz_N16_11x11_t1e6/run.log"
```

## Full Manual Submit

Launch the full array only after the pilots look healthy:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_born_pairwise_heatmaps_11x11"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_11x11_${RUN_TAG}"
PLOT_TOP=12
PLOT_MAX_BLOCH_POINTS=6000
MAX_DETECTOR_SPECTRUM_QUBITS=12
BORN_WORKERS=1

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-8 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS",MAX_DETECTOR_SPECTRUM_QUBITS="$MAX_DETECTOR_SPECTRUM_QUBITS",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_born_pairwise_heatmaps_11x11.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "qsub job id: $LOG_ROOT/qsub_jobid.txt"
echo "scheduler logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "output logs: $RUN_ROOT/<run-name>/run.log"
echo "heatmaps: $RUN_ROOT/<run-name>/heatmap_*.png"
echo "summary CSVs: $RUN_ROOT/<run-name>/pairwise_summary.csv"
echo "diagnostics: $RUN_ROOT/<run-name>/diagnostics/*.png"
```

## Staged Submit Blocks

Primary N15 tasks:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_born_pairwise_heatmaps_11x11"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_11x11_N15_${RUN_TAG}"
PLOT_TOP=12
PLOT_MAX_BLOCH_POINTS=6000
MAX_DETECTOR_SPECTRUM_QUBITS=12
BORN_WORKERS=1

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1,3,5,7,8 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS",MAX_DETECTOR_SPECTRUM_QUBITS="$MAX_DETECTOR_SPECTRUM_QUBITS",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_born_pairwise_heatmaps_11x11.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

N16 ring finite-size tasks:

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_born_pairwise_heatmaps_11x11"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_11x11_N16_${RUN_TAG}"
PLOT_TOP=8
PLOT_MAX_BLOCH_POINTS=5000
MAX_DETECTOR_SPECTRUM_QUBITS=12
BORN_WORKERS=1

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 2,4,6 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS",MAX_DETECTOR_SPECTRUM_QUBITS="$MAX_DETECTOR_SPECTRUM_QUBITS",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_born_pairwise_heatmaps_11x11.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Monitor

```bash
qstat -u "$USER"
cat "$LOG_ROOT/qsub_jobid.txt"
tail -n 80 "$LOG_ROOT"/*.log
tail -n 80 "$RUN_ROOT"/matched_ring_Jx_hz_N15_11x11_t1e6/run.log
```

## Diagnostic Completion Checklist

Before treating a run as complete, verify that the diagnostic figures for the
top rows include all of the following:

- `P(theta)` together with `P(pi-theta)`, or an equivalent panel where the two
  mirror-angle distributions can be compared.
- `P(theta)+P(pi-theta)` normalization/envelope information, not just the ratio.
- `R(theta) = P(theta)/(P(theta)+P(pi-theta))` plotted against the Born curve.
- Phi histograms for detector-state phases.
- Bloch-state plots or Bloch-coordinate distributions.
- Full qubit-detector Hamiltonian spectra and detector/relative spectra.
- Unfolded spacing histograms, with the resolved-degeneracy tolerance recorded.

If any item is missing from the generated diagnostics, do not silently mark the
campaign complete. Record the missing panel in the run log or handoff notes and
send the result to the diagnostics/code-change lane.

## Retrieval Package

Create checksums and an archive on Zeus after jobs finish:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_pairwise_heatmaps_11x11"
LOG_ROOT="logs/zeus_born_pairwise_heatmaps_11x11_<timestamp-used-at-submit>"
PACKAGE_ROOT="zeus_born_pairwise_heatmaps_11x11_package_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$PACKAGE_ROOT"
cp -a "$RUN_ROOT" "$PACKAGE_ROOT/results"
cp -a "$LOG_ROOT" "$PACKAGE_ROOT/scheduler_logs"

find "$PACKAGE_ROOT" -type f -print0 | sort -z | xargs -0 sha256sum > "$PACKAGE_ROOT/SHA256SUMS.txt"
tar -czf "$PACKAGE_ROOT.tar.gz" "$PACKAGE_ROOT"
sha256sum "$PACKAGE_ROOT.tar.gz" > "$PACKAGE_ROOT.tar.gz.sha256"

echo "$PACKAGE_ROOT.tar.gz"
echo "$PACKAGE_ROOT.tar.gz.sha256"
```
