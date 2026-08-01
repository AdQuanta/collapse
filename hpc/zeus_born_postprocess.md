# Zeus Born Follow-up Postprocess Runbook

Date: 2026-06-15

This runbook is only for postprocessing the already-imported follow-up root:

```text
figures/zeus_born_followup
```

It does not launch a new broad follow-up scan.  It runs the N13/N14
metric-stability and visual-diagnostic gate on the current shortlist queues.
Codex should not handle SSH credentials; these commands are for the user to
run manually on Zeus.

## Inputs

The Zeus checkout should contain the current repository code and these files:

```text
figures/zeus_born_followup/summary_rows.csv
figures/zeus_born_followup/shortlist_primary_n13_n14.csv
figures/zeus_born_followup/shortlist_off_resonance_controls.csv
hpc/zeus_born_postprocess_stability.pbs
hpc/zeus_born_postprocess_diagnostics.pbs
```

The primary queue is perturbative matched-ring N13/N14.  The off-resonance
queue is the `hz0=zero`, `local_resonance_label=off`, `d_res=0.1` falsifier
set.

## Submit Postprocessing

The safest option is to run the helper script from a Zeus login shell:

```bash
cd "$HOME/research/collapse"
bash hpc/submit_zeus_born_postprocess.sh
```

The helper performs input checks, submits both PBS jobs, writes `qsub_jobid.txt`
files into the scheduler log roots, writes `submit.log` into both postprocess
log roots, and prints the monitor/verify commands.

The exact commands used by the helper are:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_followup"
STAMP="$(date +%Y%m%d_%H%M%S)"
STABILITY_LOG_ROOT="logs/zeus_born_postprocess_stability_${STAMP}"
DIAGNOSTICS_LOG_ROOT="logs/zeus_born_postprocess_diagnostics_${STAMP}"

test -s "$RUN_ROOT/summary_rows.csv"
test -s "$RUN_ROOT/shortlist_primary_n13_n14.csv"
test -s "$RUN_ROOT/shortlist_off_resonance_controls.csv"

mkdir -p "$RUN_ROOT" "$STABILITY_LOG_ROOT" "$DIAGNOSTICS_LOG_ROOT"
exec > >(tee -a "$STABILITY_LOG_ROOT/submit.log" "$DIAGNOSTICS_LOG_ROOT/submit.log") 2>&1

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$STABILITY_LOG_ROOT",SUMMARY_CSV="$RUN_ROOT/summary_rows.csv",PRIMARY_QUEUE_CSV="$RUN_ROOT/shortlist_primary_n13_n14.csv",OFF_RESONANCE_CSV="$RUN_ROOT/shortlist_off_resonance_controls.csv" \
  hpc/zeus_born_postprocess_stability.pbs | tee "$STABILITY_LOG_ROOT/qsub_jobid.txt"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$DIAGNOSTICS_LOG_ROOT",SUMMARY_CSV="$RUN_ROOT/summary_rows.csv",PRIMARY_QUEUE_CSV="$RUN_ROOT/shortlist_primary_n13_n14.csv",OFF_RESONANCE_CSV="$RUN_ROOT/shortlist_off_resonance_controls.csv" \
  hpc/zeus_born_postprocess_diagnostics.pbs | tee "$DIAGNOSTICS_LOG_ROOT/qsub_jobid.txt"
```

The PBS files currently use:

```text
#PBS -q zeus_new_q
#PBS -l select=1:ncpus=8:mem=64gb
#PBS -J 1-2
PYTHON_BIN=python3.11
```

Set `ZEUS_ENV_SETUP`, `PYTHON_MODULES`, or `VIRTUAL_ENV_PATH` in the `qsub -v`
environment only if Zeus needs explicit Python/QuSpin setup.

## Monitor

Run on Zeus:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup"
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>"
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>"
MONITOR_LOG="logs/zeus_born_postprocess_monitor_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs
exec > >(tee -a "$MONITOR_LOG") 2>&1

qstat -u "$USER"
find "$STABILITY_LOG_ROOT" -maxdepth 1 -type f | sort
find "$DIAGNOSTICS_LOG_ROOT" -maxdepth 1 -type f | sort
find "$RUN_ROOT" -path '*/run.log' -type f | sort

tail -n 80 "$STABILITY_LOG_ROOT"/*.log
tail -n 80 "$DIAGNOSTICS_LOG_ROOT"/*.log
```

Expected output-side logs:

```text
figures/zeus_born_followup/metric_stability_primary_N13_N14/run.log
figures/zeus_born_followup/metric_stability_off_resonance_controls_N12_N13/run.log
figures/zeus_born_followup/diagnostics_primary_N13_N14/run.log
figures/zeus_born_followup/diagnostics_off_resonance_controls/run.log
```

Expected scheduler-side logs:

```text
logs/zeus_born_postprocess_stability_*/metric_stability_primary_N13_N14.<PBS_JOBID>.1.log
logs/zeus_born_postprocess_stability_*/metric_stability_off_resonance_controls_N12_N13.<PBS_JOBID>.2.log
logs/zeus_born_postprocess_diagnostics_*/diagnostics_primary_N13_N14.<PBS_JOBID>.1.log
logs/zeus_born_postprocess_diagnostics_*/diagnostics_off_resonance_controls.<PBS_JOBID>.2.log
```

## Package For Retrieval

Run on Zeus after both jobs finish:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup"
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>"
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>"
STAMP="$(date +%Y%m%d_%H%M%S)"
RETRIEVAL_LOG="logs/zeus_born_postprocess_retrieval_${STAMP}.log"
mkdir -p logs
exec > >(tee -a "$RETRIEVAL_LOG") 2>&1

tar -czf "zeus_born_postprocess_retrieval_${STAMP}.tar.gz" \
  "$RUN_ROOT/metric_stability_primary_N13_N14" \
  "$RUN_ROOT/metric_stability_off_resonance_controls_N12_N13" \
  "$RUN_ROOT/diagnostics_primary_N13_N14" \
  "$RUN_ROOT/diagnostics_off_resonance_controls" \
  "$STABILITY_LOG_ROOT" \
  "$DIAGNOSTICS_LOG_ROOT"

ls -lh "zeus_born_postprocess_retrieval_${STAMP}.tar.gz"
```

If the original follow-up logs still exist on Zeus, package them too:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup"
STAMP="$(date +%Y%m%d_%H%M%S)"
RETRIEVAL_LOG="logs/zeus_born_followup_missing_logs_${STAMP}.log"
FILE_LIST="logs/zeus_born_followup_missing_logs_${STAMP}.files"
mkdir -p logs
exec > >(tee -a "$RETRIEVAL_LOG") 2>&1

for run_name in \
  primary_matched_ring_N12 \
  primary_matched_ring_N13 \
  primary_matched_ring_N14 \
  primary_matched_ring_long_time_N12_N13 \
  detuning_control_ring_N12_N13 \
  chain_control_N12_N13 \
  sz_exchange_control_N12_N13 \
  cnot_copier_degenerate_N8_N10_N12
do
  if [ -s "$RUN_ROOT/$run_name/run.log" ]; then
    printf '%s\n' "$RUN_ROOT/$run_name/run.log"
  fi
done > "$FILE_LIST"

if [ -d logs ]; then
  find logs -path 'logs/zeus_born_followup*/*.log' -type f | sort >> "$FILE_LIST"
fi

if [ -s "$FILE_LIST" ]; then
  tar -czf "zeus_born_followup_missing_logs_${STAMP}.tar.gz" -T "$FILE_LIST"
  ls -lh "zeus_born_followup_missing_logs_${STAMP}.tar.gz"
else
  echo "No original follow-up run.log or scheduler logs found to package."
fi
```

## Local Completion Check After Retrieval

Before treating provenance as complete, verify that these exist locally:

```text
figures/zeus_born_followup/*/run.log
logs/zeus_born_followup*/*.log
logs/zeus_born_postprocess_stability_*/metric_stability_primary_N13_N14.<PBS_JOBID>.1.log
logs/zeus_born_postprocess_stability_*/metric_stability_off_resonance_controls_N12_N13.<PBS_JOBID>.2.log
logs/zeus_born_postprocess_diagnostics_*/diagnostics_primary_N13_N14.<PBS_JOBID>.1.log
logs/zeus_born_postprocess_diagnostics_*/diagnostics_off_resonance_controls.<PBS_JOBID>.2.log
figures/zeus_born_followup/metric_stability_primary_N13_N14/run.log
figures/zeus_born_followup/metric_stability_off_resonance_controls_N12_N13/run.log
figures/zeus_born_followup/diagnostics_primary_N13_N14/run.log
figures/zeus_born_followup/diagnostics_off_resonance_controls/run.log
```

You can run the same verification via:

```bash
cd "$HOME/research/collapse"
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>" \
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>" \
  bash hpc/verify_zeus_born_postprocess.sh
```

To require the missing original follow-up provenance logs as part of the same
check, run:

```bash
cd "$HOME/research/collapse"
REQUIRE_FOLLOWUP_PROVENANCE=1 \
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>" \
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>" \
  bash hpc/verify_zeus_born_postprocess.sh
```

Then read:

```text
figures/zeus_born_followup/metric_stability_primary_N13_N14/stability_summary.md
figures/zeus_born_followup/metric_stability_off_resonance_controls_N12_N13/stability_summary.md
figures/zeus_born_followup/diagnostics_primary_N13_N14/index.md
figures/zeus_born_followup/diagnostics_off_resonance_controls/index.md
```

Generate the scalar gate report:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_followup"
STABILITY_LOG_ROOT="<STABILITY_LOG_ROOT_FROM_SUBMISSION>"
DIAGNOSTICS_LOG_ROOT="<DIAGNOSTICS_LOG_ROOT_FROM_SUBMISSION>"

python examples/evaluate_born_postprocess_gate.py \
  --root "$RUN_ROOT" \
  --scheduler-log-root "$STABILITY_LOG_ROOT" \
  --scheduler-log-root "$DIAGNOSTICS_LOG_ROOT" \
  --out-md "$RUN_ROOT/postprocess_gate_status.md" \
  --out-json "$RUN_ROOT/postprocess_gate_status.json"
```

Interpret results using:

```text
reports/n13_n14_gate_checklist_2026-06-15.md
reports/perturbative_resonance_derivation_2026-06-15.md
```
