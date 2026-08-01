# Zeus Born Follow-up Runbook

This follow-up validates the current best numerical region and its controls
using the existing search script:

- Primary candidate: matched single-pixel ring, `N=12..14`, `Jx_unscaled`
  in the perturbative grid `{0.02, 0.03, 0.04, 0.05}`, `hz` near `0.1`,
  `Jpm` in `{0, 0.05, 0.1}`.
- Time validation: longer time sweep for the most promising matched-ring point.
- Controls: detuned ring rows that looked surprisingly good, chain controls,
  exact-Sz exchange controls, and the degenerate CNOT copier.

Codex should not handle SSH credentials for this workflow.  The HPC
handoff/retrieval lane should provide exact upload, `qsub`, retrieval, and
post-processing command blocks for the user to run manually.

## Files

- PBS script: `hpc/zeus_born_followup.pbs`
- Search entry point: `examples/born_hamiltonian_search.py`
- Existing Zeus results used to choose the grid:
  `figures/zeus_born_hamiltonian_search`

The PBS script writes one output directory per task:

```text
<RUN_ROOT>/
  primary_matched_ring_N12/
  primary_matched_ring_N13/
  primary_matched_ring_N14/
  primary_matched_ring_long_time_N12_N13/
  detuning_control_ring_N12_N13/
  chain_control_N12_N13/
  sz_exchange_control_N12_N13/
  cnot_copier_degenerate_N8_N10_N12/
```

Each directory should contain `results.json`, `results.csv`,
`top_candidates.md`, and `run.log`.  Scheduler-side stdout/stderr logs go under
`<LOG_ROOT>`.

The single-pixel follow-up grid is intentionally small-coupling:

- primary matched-ring tasks use `Jx_unscaled <= 0.05`;
- detuned and chain controls use `Jx_unscaled` in `{0.03, 0.05}`;
- exact-Sz exchange controls use `Jx_unscaled=0` and
  `Jcpm_unscaled` in `{0.02, 0.05}`.
- no follow-up task sets `hx`, so the search script default `hx=0` is used.

Larger central-coupling rows from earlier scans are comparison data only, not
primary Born-rule candidates.

## Task Map

| task | scan | purpose |
|---:|:---|:---|
| 1 | matched ring, `N=12` | Recheck the best region with finer `Jx`, `hz`, `Jpm`, and time grid. |
| 2 | matched ring, `N=13` | First finite-size validation beyond current `N=12` evidence. |
| 3 | matched ring, `N=14` | Higher-cost finite-size validation. Run after confirming quota and runtime tolerance. |
| 4 | matched ring long-time, `N=12,13` | Distinguish transient Born-like rows from stable time windows. |
| 5 | detuned ring, `N=12,13` | Test whether high-scoring `zero`/`minus` rows survive finite-size checks. |
| 6 | chain control, `N=12,13` | Confirm that the chain stays weaker than the ring. |
| 7 | exact-Sz exchange, `N=12,13` | Confirm tails without Born ratio under exact conserved-Sz dynamics. |
| 8 | CNOT copier, `N=8,10,12` | Degenerate/atomic copier control. |

## Confirmed PBS Defaults

These were copied from the previous Zeus submission that already ran:

```bash
ZEUS_QUEUE="zeus_new_q"
ZEUS_REMOTE='$HOME/research/collapse'
PYTHON_BIN="python3.11"
RUN_ROOT="figures/zeus_born_followup"
LOG_ROOT="logs/zeus_born_followup"
```

The PBS file also embeds:

```text
#PBS -q zeus_new_q
#PBS -l select=1:ncpus=8:mem=64gb
#PBS -J 1-8
#PBS -m abe
#PBS -M matanhaller@campus.technion.ac.il
```

## Log Files

Every follow-up task writes two progress logs:

```text
<LOG_ROOT>/<RUN_NAME>.<PBS_JOBID>.<TASK_ID>.log
<RUN_ROOT>/<RUN_NAME>/run.log
```

The first log is the PBS-side stream captured with `tee`; the second log is
written by `examples/born_hamiltonian_search.py` and travels with the result
directory.  Use the PBS-side log for live monitoring and the result-side
`run.log` for archived provenance.

## Manual Handoff Policy

- When a simulation is too slow locally, the HPC handoff lane should give the
  user a concrete command block to run on Zeus.
- Prefer commands that run from a Zeus login shell, because they do not require
  Codex to know SSH credentials.
- Codex should not submit jobs, handle credentials, or run SSH commands for this
  workflow. Retrieval and post-processing commands below are for the user to run
  manually.
- Every command block should preserve both scheduler-side logs under
  `<LOG_ROOT>` and output-side simulation logs under `<RUN_ROOT>/<RUN_NAME>/run.log`.

## Manual Variables

Set these manually. On Zeus, run the first block from the repository root,
usually `$HOME/research/collapse`.

```bash
RUN_TAG="followup_<DATE>_<SHORT_LABEL>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"
ZEUS_ENV_SETUP=""
```

If the cluster needs modules or conda activation, prefer putting the exact
commands in a remote setup file and pass `ZEUS_ENV_SETUP=/path/to/file.sh`.
The PBS script can also load simple whitespace-separated `PYTHON_MODULES` or
activate `VIRTUAL_ENV_PATH`, but those exact module names are currently unknown.

## Preflight

Run this locally before copying code to Zeus, or on Zeus after updating code:

```bash
python -m py_compile examples/born_hamiltonian_search.py collapse/born.py
```

The follow-up script deliberately uses `--backend quspin` for single-pixel
tasks. If QuSpin is absent on Zeus, the job should fail early instead of doing
large dense NumPy diagonalizations.

## Upload Code Manually

If the Zeus checkout is not already updated, run one of these yourself from the
local repository. This intentionally avoids `--delete` and excludes local
figures/logs so previous remote results are not removed by accident.

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"

rsync -avz \
  --exclude ".git/" \
  --exclude "__pycache__/" \
  --exclude "*.pyc" \
  --exclude ".ipynb_checkpoints/" \
  --exclude "figures/" \
  --exclude "logs/" \
  ./ "${ZEUS_TARGET}:${REMOTE_ROOT}/"
```

If `rsync` is unavailable, use `scp`:

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"

ssh "${ZEUS_TARGET}" "mkdir -p '${REMOTE_ROOT}'"
scp -r collapse examples hpc "${ZEUS_TARGET}:${REMOTE_ROOT}/"
```

If Zeus requires a nonstandard port, bastion, VPN, or SSH alias, encode that in
your own SSH config or replace `ZEUS_TARGET` accordingly.

## Submit From Zeus Login Shell

Full submission, using the embedded `#PBS -q zeus_new_q` and `#PBS -J 1-8`:

```bash
cd "$HOME/research/collapse"
RUN_TAG="followup_$(date +%Y%m%d_%H%M%S)_born"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_followup.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "Scheduler-side task logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "Per-output simulation logs: $RUN_ROOT/<run-name>/run.log"
```

If a setup file is needed for QuSpin/Python, pass it explicitly:

```bash
cd "$HOME/research/collapse"
RUN_TAG="followup_$(date +%Y%m%d_%H%M%S)_born"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"
ZEUS_ENV_SETUP="$HOME/research/collapse/hpc/zeus_env.sh"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",ZEUS_ENV_SETUP="$ZEUS_ENV_SETUP" \
  hpc/zeus_born_followup.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "Scheduler-side task logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "Per-output simulation logs: $RUN_ROOT/<run-name>/run.log"
```

Pilot task 1 only by making a temporary PBS copy on Zeus:

```bash
cd "$HOME/research/collapse"
RUN_TAG="pilot_$(date +%Y%m%d_%H%M%S)_born_task1"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

sed 's/^#PBS -J .*/#PBS -J 1/' \
  hpc/zeus_born_followup.pbs > hpc/zeus_born_followup_task1.pbs

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_followup_task1.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "Scheduler-side task log: $LOG_ROOT/primary_matched_ring_N12.<PBS_JOBID>.1.log"
echo "Per-output simulation log: $RUN_ROOT/primary_matched_ring_N12/run.log"
```

If task 3 (`N=14`) is too large for the queue, submit tasks 1, 2, and 4-8
first using two temporary PBS copies:

```bash
cd "$HOME/research/collapse"
RUN_TAG="followup_$(date +%Y%m%d_%H%M%S)_born_noN14"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

sed 's/^#PBS -J .*/#PBS -J 1-2/' \
  hpc/zeus_born_followup.pbs > hpc/zeus_born_followup_tasks1_2.pbs
sed 's/^#PBS -J .*/#PBS -J 4-8/' \
  hpc/zeus_born_followup.pbs > hpc/zeus_born_followup_tasks4_8.pbs

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_followup_tasks1_2.pbs | tee "$LOG_ROOT/qsub_jobid_tasks1_2.txt"
qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_followup_tasks4_8.pbs | tee "$LOG_ROOT/qsub_jobid_tasks4_8.txt"

echo "Scheduler-side task logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "Per-output simulation logs: $RUN_ROOT/<run-name>/run.log for tasks 1,2,4-8"
```

Then run task 3 separately with a larger memory request only if Zeus permits it:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup_<SAME_RUN_TAG_AS_ABOVE>"
LOG_ROOT="logs/zeus_born_followup_<SAME_RUN_TAG_AS_ABOVE>"

sed -e 's/^#PBS -J .*/#PBS -J 3/' \
    -e 's/^#PBS -l select=.*/#PBS -l select=1:ncpus=8:mem=128gb/' \
  hpc/zeus_born_followup.pbs > hpc/zeus_born_followup_task3_128gb.pbs

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_followup_task3_128gb.pbs | tee "$LOG_ROOT/qsub_jobid_task3.txt"

echo "Scheduler-side task log: $LOG_ROOT/primary_matched_ring_N14.<PBS_JOBID>.3.log"
echo "Per-output simulation log: $RUN_ROOT/primary_matched_ring_N14/run.log"
```

## Monitor On Zeus

```bash
cd "$HOME/research/collapse"
qstat -u "$USER"
qstat -f <JOB_ID>
find "$LOG_ROOT" -maxdepth 1 -type f | sort | tail
find "$RUN_ROOT" -path '*/run.log' -type f | sort
tail -n 80 "$LOG_ROOT/<RUN_LOG>.log"
tail -n 80 "$RUN_ROOT/<RUN_NAME>/run.log"
```

Cancel if needed:

```bash
qdel <JOB_ID>
```

## Retrieve

Option A: package results on Zeus, then download the tarball by your preferred
method.

```bash
cd "$HOME/research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"

tar -czf "zeus_born_followup_${RUN_TAG}.tar.gz" "$RUN_ROOT" "$LOG_ROOT"
ls -lh "zeus_born_followup_${RUN_TAG}.tar.gz"
```

Option B: retrieve from the local machine using your configured Zeus SSH alias.
This does not overwrite the existing first-pass Zeus directory.

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"

mkdir -p "./${RUN_ROOT}" "./${LOG_ROOT}"
rsync -avz \
  "${ZEUS_TARGET}:${REMOTE_ROOT}/${RUN_ROOT}/" \
  "./${RUN_ROOT}/"
rsync -avz \
  "${ZEUS_TARGET}:${REMOTE_ROOT}/${LOG_ROOT}/" \
  "./${LOG_ROOT}/"
```

With `scp`:

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"

scp -r "${ZEUS_TARGET}:${REMOTE_ROOT}/${RUN_ROOT}" "$(dirname "./${RUN_ROOT}")/"
scp -r "${ZEUS_TARGET}:${REMOTE_ROOT}/${LOG_ROOT}" "$(dirname "./${LOG_ROOT}")/"
```

## Post-Retrieval Analysis

Do not run follow-up analysis until the actual Zeus result directory has been
retrieved locally. First check that the expected result CSVs and provenance
logs are present:

```bash
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_followup_${RUN_TAG}"

python examples/check_zeus_followup_import.py \
  --root "$RUN_ROOT" \
  --logs-root "$LOG_ROOT" \
  --json-out "$RUN_ROOT/import_check.json"
```

The checker distinguishes CSV-readiness from full provenance. Aggregate
analysis can run once all `results.csv` files are present, but missing
`run.log` or scheduler logs should still be retrieved.

## Postprocess Already-Imported Root

Use this block when `figures/zeus_born_followup` has already been uploaded to
Zeus and contains `summary_rows.csv`, `shortlist_primary_n13_n14.csv`, and
`shortlist_off_resonance_controls.csv`.  This is postprocessing only: it does
not submit `hpc/zeus_born_followup.pbs` or start a new follow-up scan.

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_followup"
STABILITY_LOG_ROOT="logs/zeus_born_postprocess_stability_$(date +%Y%m%d_%H%M%S)"
DIAGNOSTICS_LOG_ROOT="logs/zeus_born_postprocess_diagnostics_$(date +%Y%m%d_%H%M%S)"

test -s "$RUN_ROOT/summary_rows.csv"
test -s "$RUN_ROOT/shortlist_primary_n13_n14.csv"
test -s "$RUN_ROOT/shortlist_off_resonance_controls.csv"

mkdir -p "$STABILITY_LOG_ROOT" "$DIAGNOSTICS_LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$STABILITY_LOG_ROOT",SUMMARY_CSV="$RUN_ROOT/summary_rows.csv",PRIMARY_QUEUE_CSV="$RUN_ROOT/shortlist_primary_n13_n14.csv",OFF_RESONANCE_CSV="$RUN_ROOT/shortlist_off_resonance_controls.csv" \
  hpc/zeus_born_postprocess_stability.pbs | tee "$STABILITY_LOG_ROOT/qsub_jobid.txt"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$DIAGNOSTICS_LOG_ROOT",SUMMARY_CSV="$RUN_ROOT/summary_rows.csv",PRIMARY_QUEUE_CSV="$RUN_ROOT/shortlist_primary_n13_n14.csv",OFF_RESONANCE_CSV="$RUN_ROOT/shortlist_off_resonance_controls.csv" \
  hpc/zeus_born_postprocess_diagnostics.pbs | tee "$DIAGNOSTICS_LOG_ROOT/qsub_jobid.txt"

echo "Stability scheduler logs: $STABILITY_LOG_ROOT/*.log"
echo "Diagnostics scheduler logs: $DIAGNOSTICS_LOG_ROOT/*.log"
echo "Stability output logs:"
echo "  $RUN_ROOT/metric_stability_primary_N13_N14/run.log"
echo "  $RUN_ROOT/metric_stability_off_resonance_controls_N12_N13/run.log"
echo "Diagnostic output logs:"
echo "  $RUN_ROOT/diagnostics_primary_N13_N14/run.log"
echo "  $RUN_ROOT/diagnostics_off_resonance_controls/run.log"
```

Monitor the postprocess jobs on Zeus:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup"
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>"
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>"

qstat -u "$USER"

find "$STABILITY_LOG_ROOT" -maxdepth 1 -type f | sort
find "$DIAGNOSTICS_LOG_ROOT" -maxdepth 1 -type f | sort
find "$RUN_ROOT" -path '*/run.log' -type f | sort

tail -n 80 "$STABILITY_LOG_ROOT"/*.log
tail -n 80 "$DIAGNOSTICS_LOG_ROOT"/*.log
tail -n 80 "$RUN_ROOT/metric_stability_primary_N13_N14/run.log"
tail -n 80 "$RUN_ROOT/metric_stability_off_resonance_controls_N12_N13/run.log"
tail -n 80 "$RUN_ROOT/diagnostics_primary_N13_N14/run.log"
tail -n 80 "$RUN_ROOT/diagnostics_off_resonance_controls/run.log"
```

Package the postprocess outputs and the missing original follow-up provenance
for retrieval:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup"
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>"
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>"
STAMP="$(date +%Y%m%d_%H%M%S)"

tar -czf "zeus_born_postprocess_${STAMP}.tar.gz" \
  "$RUN_ROOT/metric_stability_primary_N13_N14" \
  "$RUN_ROOT/metric_stability_off_resonance_controls_N12_N13" \
  "$RUN_ROOT/diagnostics_primary_N13_N14" \
  "$RUN_ROOT/diagnostics_off_resonance_controls" \
  "$STABILITY_LOG_ROOT" \
  "$DIAGNOSTICS_LOG_ROOT"

tar -czf "zeus_born_followup_missing_logs_${STAMP}.tar.gz" \
  "$RUN_ROOT"/*/run.log \
  logs/zeus_born_followup*

ls -lh "zeus_born_postprocess_${STAMP}.tar.gz" \
  "zeus_born_followup_missing_logs_${STAMP}.tar.gz"
```

Before marking provenance complete after retrieval, verify that both output-side
and scheduler-side logs are present:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup"
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>"
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>"

test -s "$RUN_ROOT/metric_stability_primary_N13_N14/run.log"
test -s "$RUN_ROOT/metric_stability_off_resonance_controls_N12_N13/run.log"
test -s "$RUN_ROOT/diagnostics_primary_N13_N14/run.log"
test -s "$RUN_ROOT/diagnostics_off_resonance_controls/run.log"

find "$RUN_ROOT" -mindepth 2 -maxdepth 2 -name run.log -type f | sort
find "$STABILITY_LOG_ROOT" -maxdepth 1 -name '*.log' -type f | sort
find "$DIAGNOSTICS_LOG_ROOT" -maxdepth 1 -name '*.log' -type f | sort
find logs -path 'logs/zeus_born_followup*/*.log' -type f | sort
```

After the data files are present, regenerate the aggregate ranking and
finite-size scaling summary for the follow-up root from the local repository:

```bash
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"

python examples/summarize_born_search_results.py \
  --root "$RUN_ROOT" \
  --top 40 \
  --out-md "$RUN_ROOT/summary.md" \
  --out-csv "$RUN_ROOT/summary_rows.csv"

python examples/compare_born_followup_scaling.py \
  --source-csv "$RUN_ROOT/summary_rows.csv" \
  --out-md "$RUN_ROOT/scaling_summary.md" \
  --top 40

python examples/shortlist_born_followup_candidates.py \
  --source-csv "$RUN_ROOT/summary_rows.csv" \
  --out-dir "$RUN_ROOT" \
  --top 20
```

Then run the multiscale metric-stability screen on the retrieved rows.  This
checks whether the best rows survive theta-bin and tail-fraction changes:

```bash
python examples/born_candidate_stability.py \
  --source-csv "$RUN_ROOT/summary_rows.csv" \
  --queue-csv "$RUN_ROOT/shortlist_primary_n13_n14.csv" \
  --mode primary \
  --min-n 13 \
  --max-n 14 \
  --family primary_matched_ring_N13 primary_matched_ring_N14 primary_matched_ring_long_time_N12_N13 \
  --top-groups 8 \
  --top-rows 16 \
  --bins 60 80 120 \
  --tail-fractions 0.05 0.10 0.20 \
  --log-bins 40 \
  --backend auto \
  --out-dir "$RUN_ROOT/metric_stability_primary_N13_N14"
```

If this is too slow locally, submit the stability rerun on Zeus instead:

```bash
cd "$HOME/research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_postprocess_stability_${RUN_TAG}"
mkdir -p "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",SUMMARY_CSV="$RUN_ROOT/summary_rows.csv",PRIMARY_QUEUE_CSV="$RUN_ROOT/shortlist_primary_n13_n14.csv",OFF_RESONANCE_CSV="$RUN_ROOT/shortlist_off_resonance_controls.csv" \
  hpc/zeus_born_postprocess_stability.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "Scheduler-side logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "Per-output logs: $RUN_ROOT/metric_stability_primary_N13_N14/run.log"
echo "Per-output logs: $RUN_ROOT/metric_stability_off_resonance_controls_N12_N13/run.log"
```

After the stability screen, generate visual diagnostic plots for the primary
N13/N14 rows and the off-resonance falsifier controls on Zeus:

```bash
cd "$HOME/research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_postprocess_diagnostics_${RUN_TAG}"
mkdir -p "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",SUMMARY_CSV="$RUN_ROOT/summary_rows.csv",PRIMARY_QUEUE_CSV="$RUN_ROOT/shortlist_primary_n13_n14.csv",OFF_RESONANCE_CSV="$RUN_ROOT/shortlist_off_resonance_controls.csv" \
  hpc/zeus_born_postprocess_diagnostics.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "Scheduler-side logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "Primary diagnostic log: $RUN_ROOT/diagnostics_primary_N13_N14/run.log"
echo "Off-resonance diagnostic log: $RUN_ROOT/diagnostics_off_resonance_controls/run.log"
```

Monitor the postprocess job on Zeus with both log streams:

```bash
cd "$HOME/research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_postprocess_stability_${RUN_TAG}"

qstat -u "$USER"
find "$LOG_ROOT" -maxdepth 1 -type f | sort
find "$RUN_ROOT" -path '*/run.log' -type f | sort
tail -n 80 "$LOG_ROOT/<RUN_LOG>.log"
tail -n 80 "$RUN_ROOT/metric_stability_primary_N13_N14/run.log"
tail -n 80 "$RUN_ROOT/metric_stability_off_resonance_controls_N12_N13/run.log"
```

Retrieve postprocess stability outputs and logs locally:

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_followup_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_postprocess_stability_${RUN_TAG}"

mkdir -p "./${RUN_ROOT}" "./${LOG_ROOT}"
rsync -avz \
  "${ZEUS_TARGET}:${REMOTE_ROOT}/${RUN_ROOT}/metric_stability_primary_N13_N14/" \
  "./${RUN_ROOT}/metric_stability_primary_N13_N14/"
rsync -avz \
  "${ZEUS_TARGET}:${REMOTE_ROOT}/${RUN_ROOT}/metric_stability_off_resonance_controls_N12_N13/" \
  "./${RUN_ROOT}/metric_stability_off_resonance_controls_N12_N13/"
rsync -avz \
  "${ZEUS_TARGET}:${REMOTE_ROOT}/${LOG_ROOT}/" \
  "./${LOG_ROOT}/"
```

If the detuned controls score well in the aggregate summary, run the same
stability screen with `--mode controls` into a separate output directory before
interpreting them as real candidates.

```bash
python examples/born_candidate_stability.py \
  --source-csv "$RUN_ROOT/summary_rows.csv" \
  --mode controls \
  --top-rows 12 \
  --bins 60 80 120 \
  --tail-fractions 0.05 0.10 0.20 \
  --log-bins 40 \
  --backend auto \
  --out-dir "$RUN_ROOT/metric_stability_controls"
```

## User Decisions Before Running

- Whether to use the default remote project directory `$HOME/research/collapse`
  or a scratch/project path for this larger follow-up.
- Whether task 3 (`N=14`) should stay at `select=1:ncpus=8:mem=64gb` or be
  submitted separately with a larger memory request.
- Python environment setup beyond `python3.11`, if QuSpin is not already
  available in the default environment.
- BLAS/OpenMP thread policy for the queue.
- Whether the existing email notification target should be changed from
  `matanhaller@campus.technion.ac.il`.
