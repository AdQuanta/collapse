#!/bin/bash
# Shared execution body for the four N=11..18 diagnostic-atlas PBS arrays.
# The caller must set STUDY before sourcing this file.

set -euo pipefail

: "${STUDY:?set STUDY before sourcing zeus_single_pixel_atlas_common.sh}"
REPO_ROOT="${REPO_ROOT:-${PBS_O_WORKDIR:?PBS_O_WORKDIR is unavailable}}"
cd "$REPO_ROOT"
if [[ ! -f "collapse/scaling_campaign.py" ]]; then
  echo "Missing collapse/scaling_campaign.py under REPO_ROOT=$REPO_ROOT; synchronize the new campaign files to Zeus." >&2
  exit 2
fi

if [[ -n "${ZEUS_ENV_SETUP:-}" ]]; then
  # shellcheck source=/dev/null
  source "$ZEUS_ENV_SETUP"
fi

if [[ -n "${PYTHON_MODULES:-}" ]]; then
  if ! command -v module >/dev/null 2>&1; then
    echo "PYTHON_MODULES is set, but the module command is unavailable." >&2
    exit 2
  fi
  for mod in $PYTHON_MODULES; do
    module load "$mod"
  done
fi

if [[ -n "${VIRTUAL_ENV_PATH:-}" ]]; then
  # shellcheck source=/dev/null
  source "$VIRTUAL_ENV_PATH/bin/activate"
fi

PYTHON_BIN="${PYTHON_BIN:-python3.11}"
TASK_N="${PBS_ARRAY_INDEX:-${PBS_ARRAYID:-${TASK_N:-}}}"
if [[ -z "$TASK_N" || ! "$TASK_N" =~ ^(11|12|13|14|15|16|17|18)$ ]]; then
  echo "PBS array index must select N=11,12,13,14,15,16,17,18; got '$TASK_N'." >&2
  exit 2
fi

case "$STUDY" in
  hz0)          LAUNCHER="examples/run_hz0_atlas_scaling.py" ;;
  hz_resonance) LAUNCHER="examples/run_hz_resonance_atlas_scaling.py" ;;
  jpm_hz)       LAUNCHER="examples/run_jpm_hz_atlas_scaling.py" ;;
  jpm_coupling) LAUNCHER="examples/run_jpm_coupling_atlas_scaling.py" ;;
  *) echo "Unknown STUDY=$STUDY" >&2; exit 2 ;;
esac
if [[ ! -f "$LAUNCHER" ]]; then
  echo "Missing $LAUNCHER under REPO_ROOT=$REPO_ROOT; synchronize the study launchers to Zeus." >&2
  exit 2
fi

RUN_ROOT="${RUN_ROOT:-work/zeus_single_pixel_atlas_scaling_2026-07-14}"
LOG_ROOT="${LOG_ROOT:-logs/zeus_single_pixel_atlas_scaling_2026-07-14/$STUDY}"
MPLCONFIGDIR="${MPLCONFIGDIR:-$RUN_ROOT/.mplconfig}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT" "$MPLCONFIGDIR"
export MPLBACKEND=Agg
export MPLCONFIGDIR
export PYTHONUNBUFFERED=1

# One N is assigned to each PBS array job.  Keep numerical-library threading
# bounded; array-level parallelism supplies the useful process parallelism.
NUMERIC_THREADS="${NUMERIC_THREADS:-4}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-$NUMERIC_THREADS}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-$NUMERIC_THREADS}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-$NUMERIC_THREADS}"
export BLIS_NUM_THREADS="${BLIS_NUM_THREADS:-$NUMERIC_THREADS}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-$NUMERIC_THREADS}"

JOB_TAG="${PBS_JOBID:-manual}"
PBS_LOG="$LOG_ROOT/N${TASK_N}_${JOB_TAG}.log"
exec >"$PBS_LOG" 2>&1

echo "[$(date --iso-8601=seconds)] Starting STUDY=$STUDY N=$TASK_N"
echo "PBS_JOBID=${PBS_JOBID:-}"
echo "PBS_ARRAY_INDEX=${PBS_ARRAY_INDEX:-}"
echo "PBS_O_WORKDIR=$PBS_O_WORKDIR"
echo "RUN_ROOT=$RUN_ROOT"
echo "LOG_ROOT=$LOG_ROOT"
echo "PYTHON_BIN=$PYTHON_BIN"
echo "COLLECTIVE_JX=0.01"
echo "EDGE_COUPLING_FORMULA=0.01/sqrt(N)"
echo "NUMERIC_THREADS=$NUMERIC_THREADS"

"$PYTHON_BIN" -c 'import sys; assert sys.version_info[:2] == (3, 11), sys.version; import importlib.metadata as m; expected={"quspin":"1.0.0","quspin-extensions":"0.1.6"}; actual={k:m.version(k) for k in expected}; assert actual == expected, actual; print(sys.version); print(actual)'

RUN_N="$TASK_N"
EXTRA_ARGS=()
if [[ "${SMOKE:-0}" == "1" ]]; then
  RUN_N=4
  EXTRA_ARGS+=(--allow-small-smoke)
  RUN_ROOT="$RUN_ROOT/smoke_task_N${TASK_N}"
  echo "SMOKE=1: running N=4 in $RUN_ROOT"
fi
if [[ "${DRY_RUN:-0}" == "1" ]]; then
  EXTRA_ARGS+=(--dry-run)
fi
if [[ "${FORCE:-0}" == "1" ]]; then
  EXTRA_ARGS+=(--force)
fi

TASK_ROOT="$RUN_ROOT/$STUDY/N$(printf '%02d' "$RUN_N")"
mkdir -p "$TASK_ROOT"
trap 'date --iso-8601=seconds > "$TASK_ROOT/INTERRUPTED"; exit 143' TERM INT

# One size per array task is safest for N>=16.  The Python launchers also
# support --workers >1 when several smaller N values share a sufficiently
# large allocation outside the PBS-array workflow.
"$PYTHON_BIN" "$LAUNCHER" \
  --N "$RUN_N" \
  --workers "${CAMPAIGN_WORKERS:-1}" \
  --campaign-root "$RUN_ROOT" \
  --python "$PYTHON_BIN" \
  "${EXTRA_ARGS[@]}"

if [[ "${DRY_RUN:-0}" != "1" ]]; then
  test -f "$TASK_ROOT/DONE.json"
fi
rm -f "$TASK_ROOT/INTERRUPTED"
echo "[$(date --iso-8601=seconds)] Finished STUDY=$STUDY N=$RUN_N"
echo "Per-N outputs: $TASK_ROOT"
echo "PBS log: $PBS_LOG"
