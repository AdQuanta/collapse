#!/usr/bin/env bash
# Verify retrieved or on-Zeus Born postprocess outputs and run the gate evaluator.

set -euo pipefail

WORKDIR="${ZEUS_BORN_WORKDIR:-$HOME/research/collapse}"
cd "$WORKDIR"

RUN_ROOT="${RUN_ROOT:-figures/zeus_born_followup}"

latest_dir() {
  pattern="$1"
  set +e
  newest=$(ls -td $pattern 2>/dev/null | head -n 1)
  status=$?
  set -e
  if [ "$status" -ne 0 ]; then
    newest=""
  fi
  printf '%s' "$newest"
}

STABILITY_LOG_ROOT="${STABILITY_LOG_ROOT:-$(latest_dir 'logs/zeus_born_postprocess_stability_*')}"
DIAGNOSTICS_LOG_ROOT="${DIAGNOSTICS_LOG_ROOT:-$(latest_dir 'logs/zeus_born_postprocess_diagnostics_*')}"

VERIFY_LOG="${VERIFY_LOG:-logs/zeus_born_postprocess_verify_$(date +%Y%m%d_%H%M%S).log}"
mkdir -p "$(dirname "$VERIFY_LOG")"
exec > >(tee -a "$VERIFY_LOG") 2>&1

echo "Verify timestamp: $(date -Is)"
echo "Verify log: $VERIFY_LOG"

missing=0
check_file() {
  path="$1"
  if [ -s "$path" ]; then
    echo "OK  $path"
  else
    echo "MISS $path" >&2
    missing=1
  fi
}

check_dir() {
  path="$1"
  if [ -d "$path" ]; then
    echo "OK  $path"
  else
    echo "MISS $path" >&2
    missing=1
  fi
}

check_scheduler_log_prefixes() {
  path="$1"
  label="$2"
  shift 2
  for prefix in "$@"; do
    if [ -d "$path" ] && find "$path" -maxdepth 1 -name "${prefix}.*.log" -type f -size +0c | grep -q .; then
      echo "OK  $label scheduler log for $prefix in $path"
    else
      echo "MISS $label scheduler log for $prefix in $path" >&2
      missing=1
    fi
  done
}

check_file "$RUN_ROOT/summary_rows.csv"
check_file "$RUN_ROOT/shortlist_primary_n13_n14.csv"
check_file "$RUN_ROOT/shortlist_off_resonance_controls.csv"

check_file "$RUN_ROOT/metric_stability_primary_N13_N14/stability_summary.csv"
check_file "$RUN_ROOT/metric_stability_primary_N13_N14/run.log"
check_file "$RUN_ROOT/metric_stability_off_resonance_controls_N12_N13/stability_summary.csv"
check_file "$RUN_ROOT/metric_stability_off_resonance_controls_N12_N13/run.log"
check_file "$RUN_ROOT/diagnostics_primary_N13_N14/index.md"
check_file "$RUN_ROOT/diagnostics_primary_N13_N14/run.log"
check_file "$RUN_ROOT/diagnostics_off_resonance_controls/index.md"
check_file "$RUN_ROOT/diagnostics_off_resonance_controls/run.log"

if [ -n "$STABILITY_LOG_ROOT" ]; then
  check_dir "$STABILITY_LOG_ROOT"
  check_scheduler_log_prefixes \
    "$STABILITY_LOG_ROOT" \
    "stability" \
    metric_stability_primary_N13_N14 \
    metric_stability_off_resonance_controls_N12_N13
else
  echo "MISS stability scheduler log root" >&2
  missing=1
fi

if [ -n "$DIAGNOSTICS_LOG_ROOT" ]; then
  check_dir "$DIAGNOSTICS_LOG_ROOT"
  check_scheduler_log_prefixes \
    "$DIAGNOSTICS_LOG_ROOT" \
    "diagnostics" \
    diagnostics_primary_N13_N14 \
    diagnostics_off_resonance_controls
else
  echo "MISS diagnostics scheduler log root" >&2
  missing=1
fi

if [ "${REQUIRE_FOLLOWUP_PROVENANCE:-0}" != "0" ]; then
  echo
  echo "Original follow-up provenance:"
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
    check_file "$RUN_ROOT/$run_name/run.log"
    if [ -d logs ] && find logs -path "logs/zeus_born_followup*/${run_name}.*.log" -type f -size +0c | grep -q .; then
      echo "OK  original follow-up scheduler log for $run_name"
    else
      echo "MISS original follow-up scheduler log for $run_name" >&2
      missing=1
    fi
  done
fi

echo
echo "Output-side run logs:"
find "$RUN_ROOT" -mindepth 2 -maxdepth 2 -name run.log -type f | sort || true

echo
echo "Scheduler logs:"
if [ -n "$STABILITY_LOG_ROOT" ]; then
  find "$STABILITY_LOG_ROOT" -maxdepth 1 -name '*.log' -type f | sort || true
fi
if [ -n "$DIAGNOSTICS_LOG_ROOT" ]; then
  find "$DIAGNOSTICS_LOG_ROOT" -maxdepth 1 -name '*.log' -type f | sort || true
fi

if [ "$missing" -ne 0 ]; then
  echo "One or more required outputs or logs are missing." >&2
  exit 1
fi

if command -v python3.11 >/dev/null 2>&1; then
  PYTHON_CMD="${PYTHON_CMD:-python3.11}"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="${PYTHON_CMD:-python3}"
else
  PYTHON_CMD="${PYTHON_CMD:-python}"
fi

eval_args=(--root "$RUN_ROOT")
if [ -n "$STABILITY_LOG_ROOT" ]; then
  eval_args+=(--scheduler-log-root "$STABILITY_LOG_ROOT")
fi
if [ -n "$DIAGNOSTICS_LOG_ROOT" ]; then
  eval_args+=(--scheduler-log-root "$DIAGNOSTICS_LOG_ROOT")
fi

"$PYTHON_CMD" examples/evaluate_born_postprocess_gate.py "${eval_args[@]}"

echo "All required postprocess files are present."
