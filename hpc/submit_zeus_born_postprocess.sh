#!/usr/bin/env bash
# Submit the postprocess-only Born-rule gate on Zeus.
#
# Run this from a Zeus login shell after the current repository code and the
# imported figures/zeus_born_followup inputs have been uploaded.

set -euo pipefail

WORKDIR="${ZEUS_BORN_WORKDIR:-$HOME/research/collapse}"
cd "$WORKDIR"

RUN_ROOT="${RUN_ROOT:-figures/zeus_born_followup}"
SUMMARY_CSV="${SUMMARY_CSV:-$RUN_ROOT/summary_rows.csv}"
PRIMARY_QUEUE_CSV="${PRIMARY_QUEUE_CSV:-$RUN_ROOT/shortlist_primary_n13_n14.csv}"
OFF_RESONANCE_CSV="${OFF_RESONANCE_CSV:-$RUN_ROOT/shortlist_off_resonance_controls.csv}"

STAMP="${RUN_STAMP:-$(date +%Y%m%d_%H%M%S)}"
STABILITY_LOG_ROOT="${STABILITY_LOG_ROOT:-logs/zeus_born_postprocess_stability_${STAMP}}"
DIAGNOSTICS_LOG_ROOT="${DIAGNOSTICS_LOG_ROOT:-logs/zeus_born_postprocess_diagnostics_${STAMP}}"

mkdir -p "$STABILITY_LOG_ROOT" "$DIAGNOSTICS_LOG_ROOT"

SUBMIT_LOG="${SUBMIT_LOG:-$STABILITY_LOG_ROOT/submit.log}"
DIAGNOSTICS_SUBMIT_LOG="${DIAGNOSTICS_SUBMIT_LOG:-$DIAGNOSTICS_LOG_ROOT/submit.log}"
exec > >(tee -a "$SUBMIT_LOG" "$DIAGNOSTICS_SUBMIT_LOG") 2>&1

echo "Submit timestamp: $(date -Is)"
echo "Submit logs:"
echo "  $SUBMIT_LOG"
echo "  $DIAGNOSTICS_SUBMIT_LOG"

for path in "$SUMMARY_CSV" "$PRIMARY_QUEUE_CSV" "$OFF_RESONANCE_CSV"; do
  if [ ! -s "$path" ]; then
    echo "Missing required input: $path" >&2
    exit 2
  fi
done

for path in hpc/zeus_born_postprocess_stability.pbs hpc/zeus_born_postprocess_diagnostics.pbs; do
  if [ ! -s "$path" ]; then
    echo "Missing PBS script: $path" >&2
    exit 2
  fi
done

if ! command -v qsub >/dev/null 2>&1; then
  echo "qsub was not found on PATH. Run this from a Zeus login shell." >&2
  exit 2
fi

mkdir -p "$RUN_ROOT" "$STABILITY_LOG_ROOT" "$DIAGNOSTICS_LOG_ROOT"

optional_vars=""
if [ -n "${ZEUS_ENV_SETUP:-}" ]; then
  optional_vars="${optional_vars},ZEUS_ENV_SETUP=${ZEUS_ENV_SETUP}"
fi
if [ -n "${PYTHON_MODULES:-}" ]; then
  optional_vars="${optional_vars},PYTHON_MODULES=${PYTHON_MODULES}"
fi
if [ -n "${VIRTUAL_ENV_PATH:-}" ]; then
  optional_vars="${optional_vars},VIRTUAL_ENV_PATH=${VIRTUAL_ENV_PATH}"
fi
if [ -n "${PYTHON_BIN:-}" ]; then
  optional_vars="${optional_vars},PYTHON_BIN=${PYTHON_BIN}"
fi

stability_vars="RUN_ROOT=${RUN_ROOT},LOG_ROOT=${STABILITY_LOG_ROOT},SUMMARY_CSV=${SUMMARY_CSV},PRIMARY_QUEUE_CSV=${PRIMARY_QUEUE_CSV},OFF_RESONANCE_CSV=${OFF_RESONANCE_CSV}${optional_vars}"
diagnostics_vars="RUN_ROOT=${RUN_ROOT},LOG_ROOT=${DIAGNOSTICS_LOG_ROOT},SUMMARY_CSV=${SUMMARY_CSV},PRIMARY_QUEUE_CSV=${PRIMARY_QUEUE_CSV},OFF_RESONANCE_CSV=${OFF_RESONANCE_CSV}${optional_vars}"

echo "Submitting Born postprocess stability job"
echo "  RUN_ROOT=$RUN_ROOT"
echo "  LOG_ROOT=$STABILITY_LOG_ROOT"
qsub -v "$stability_vars" hpc/zeus_born_postprocess_stability.pbs | tee "$STABILITY_LOG_ROOT/qsub_jobid.txt"

echo "Submitting Born postprocess diagnostics job"
echo "  RUN_ROOT=$RUN_ROOT"
echo "  LOG_ROOT=$DIAGNOSTICS_LOG_ROOT"
qsub -v "$diagnostics_vars" hpc/zeus_born_postprocess_diagnostics.pbs | tee "$DIAGNOSTICS_LOG_ROOT/qsub_jobid.txt"

cat <<EOF

Submitted postprocess jobs.

Monitor:
  qstat -u "\$USER"
  find "$STABILITY_LOG_ROOT" -maxdepth 1 -type f | sort
  find "$DIAGNOSTICS_LOG_ROOT" -maxdepth 1 -type f | sort
  find "$RUN_ROOT" -path '*/run.log' -type f | sort

Verify after completion:
  STABILITY_LOG_ROOT="$STABILITY_LOG_ROOT" DIAGNOSTICS_LOG_ROOT="$DIAGNOSTICS_LOG_ROOT" \\
    bash hpc/verify_zeus_born_postprocess.sh
EOF
