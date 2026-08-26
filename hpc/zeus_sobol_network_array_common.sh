#!/bin/bash
# Shared body for non-circular single-pixel Sobol PBS arrays.

set -euo pipefail

: "${RUNNER:?RUNNER must name the Python campaign entry point}"
: "${CAMPAIGN_SLUG:?CAMPAIGN_SLUG is required}"
: "${RUN_ROOT:?Submit with the documented wrapper or define RUN_ROOT}"

if [[ -f "$RUNNER" ]]; then
  REPO_ROOT="$PWD"
elif [[ -f "../$RUNNER" ]]; then
  REPO_ROOT="$(cd .. && pwd)"
else
  echo "Cannot locate $RUNNER" >&2
  exit 2
fi
cd "$REPO_ROOT"

DETECTOR_N="${DETECTOR_N:-12}"
COUNT="${COUNT:-400}"
BATCH_SIZE="${BATCH_SIZE:-100}"
WORKERS="${WORKERS:-2}"
if (( DETECTOR_N < 3 || COUNT < 1 || BATCH_SIZE < 1 || COUNT % BATCH_SIZE != 0 )); then
  echo "Require N>=3, positive COUNT/BATCH_SIZE, and COUNT divisible by BATCH_SIZE" >&2
  exit 2
fi
BATCH_COUNT=$((COUNT / BATCH_SIZE))
ARRAY_INDEX="${PBS_ARRAY_INDEX:-${PBS_ARRAYID:-}}"
if [[ ! "$ARRAY_INDEX" =~ ^[0-9]+$ ]] || (( ARRAY_INDEX >= BATCH_COUNT )); then
  echo "PBS array index must be in 0..$((BATCH_COUNT - 1)); got '$ARRAY_INDEX'" >&2
  exit 2
fi

mkdir -p "$RUN_ROOT/logs" "$RUN_ROOT/tmp/batch${ARRAY_INDEX}" "$RUN_ROOT/.mplconfig/batch${ARRAY_INDEX}"
export PYTHONUNBUFFERED=1 PYTHONHASHSEED=0 MPLBACKEND=Agg
export TMPDIR="$RUN_ROOT/tmp/batch${ARRAY_INDEX}" MPLCONFIGDIR="$RUN_ROOT/.mplconfig/batch${ARRAY_INDEX}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 BLIS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4

LOG="$RUN_ROOT/logs/${CAMPAIGN_SLUG}_N${DETECTOR_N}_batch${ARRAY_INDEX}_${PBS_JOBID:-manual}.log"
echo "[$(date --iso-8601=seconds)] campaign=$CAMPAIGN_SLUG batch=$ARRAY_INDEX N=$DETECTOR_N samples=$COUNT shard=$BATCH_SIZE parameters=J,hz,Jpm,Jx symmetry=magnetization_parity workers=$WORKERS" | tee -a "$LOG"
python3.11 "$RUNNER" \
  --batch-index "$ARRAY_INDEX" \
  --output-root "$RUN_ROOT" \
  --detector-n "$DETECTOR_N" \
  --count "$COUNT" \
  --batch-size "$BATCH_SIZE" \
  --lower "${LOWER:-1e-3}" \
  --upper "${UPPER:-10}" \
  --kappa "${KAPPA:-0.1}" \
  --evolution-time "${EVOLUTION_TIME:-1e6}" \
  --workers "$WORKERS" \
  --graph-seed "${GRAPH_SEED:-20260810}" \
  --graph-per-configuration \
  --graph-require-connected \
  "${GRAPH_ARGS[@]}" \
  --resume 2>&1 | tee -a "$LOG"
