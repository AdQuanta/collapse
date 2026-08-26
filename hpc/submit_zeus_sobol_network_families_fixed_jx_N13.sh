#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }

DETECTOR_N=13
COUNT_PER_FAMILY="${COUNT_PER_FAMILY:-100}"
BATCH_SIZE="${BATCH_SIZE:-25}"
WORKERS="${WORKERS:-1}"
if (( COUNT_PER_FAMILY < 1 || BATCH_SIZE < 1 || COUNT_PER_FAMILY % BATCH_SIZE != 0 )); then
  echo "COUNT_PER_FAMILY must be positive and divisible by BATCH_SIZE." >&2
  exit 2
fi
if (( WORKERS < 1 || WORKERS > 8 )); then
  echo "WORKERS must be in 1..8 for the requested eight-core node." >&2
  exit 2
fi

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_sobol_network_families_fixed_jx0p01_N13_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$RUN_ROOT/logs"
BATCHES_PER_FAMILY=$((COUNT_PER_FAMILY / BATCH_SIZE))
ARRAY_LAST=$((4 * BATCHES_PER_FAMILY - 1))
JOB_ID="$(qsub -J "0-$ARRAY_LAST" -v "RUN_ROOT=$RUN_ROOT,DETECTOR_N=$DETECTOR_N,COUNT_PER_FAMILY=$COUNT_PER_FAMILY,BATCH_SIZE=$BATCH_SIZE,WORKERS=$WORKERS" "$REPO_ROOT/hpc/zeus_sobol_network_families_fixed_jx_N13_array.pbs")"
printf '%s job_id=%s array=0-%s families=4 N=%s configurations_per_family=%s total_configurations=%s shard_size=%s run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_LAST" "$DETECTOR_N" \
  "$COUNT_PER_FAMILY" "$((4 * COUNT_PER_FAMILY))" "$BATCH_SIZE" "$RUN_ROOT" \
  | tee "$RUN_ROOT/submitted_jobs.txt"
