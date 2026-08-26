#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_top400_hz0_variants_N14_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/zeus_top400_hz0_variants_N14.json}"
ARRAY_LAST="${ARRAY_LAST:-3}"
WORKERS="${WORKERS:-2}"
mkdir -p "$RUN_ROOT/logs"
JOB_ID="$(qsub -J "0-$ARRAY_LAST" -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG,WORKERS=$WORKERS" "$REPO_ROOT/hpc/zeus_top400_hz0_variants_N14_array.pbs")"
printf '%s job_id=%s array=0-%s top=400 N=14 shard_size=100 workers=%s run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_LAST" "$WORKERS" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"
