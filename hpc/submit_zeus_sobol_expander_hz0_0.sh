#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"; cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
DETECTOR_N="${DETECTOR_N:-12}"; COUNT="${COUNT:-400}"; BATCH_SIZE="${BATCH_SIZE:-100}"
(( COUNT % BATCH_SIZE == 0 )) || { echo "COUNT must be divisible by BATCH_SIZE" >&2; exit 2; }
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_sobol_expander_hz0_0_N${DETECTOR_N}_$(date +%Y%m%d_%H%M%S)}"; mkdir -p "$RUN_ROOT/logs"; LAST=$((COUNT / BATCH_SIZE - 1))
JOB_ID="$(qsub -J "0-$LAST" -v "RUN_ROOT=$RUN_ROOT,DETECTOR_N=$DETECTOR_N,COUNT=$COUNT,BATCH_SIZE=$BATCH_SIZE,WORKERS=${WORKERS:-2},GRAPH_SEED=${GRAPH_SEED:-2026081401},LOWER=${LOWER:-1e-3},UPPER=${UPPER:-10},KAPPA=${KAPPA:-0.1},EVOLUTION_TIME=${EVOLUTION_TIME:-1e6},REGULAR_DEGREE=${REGULAR_DEGREE:-4}" "$REPO_ROOT/hpc/zeus_sobol_expander_hz0_0_array.pbs")"
printf '%s job_id=%s array=0-%s N=%s total=%s shard_size=%s run_root=%s\n' "$(date --iso-8601=seconds)" "$JOB_ID" "$LAST" "$DETECTOR_N" "$COUNT" "$BATCH_SIZE" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"
