#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_network_extremes_resampled_N12_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/zeus_network_extremes_resampled_N12.json}"
ARRAY_LAST="${ARRAY_LAST:-19}"
mkdir -p "$RUN_ROOT/logs"
JOB_ID="$(qsub -J "0-$ARRAY_LAST" -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG" "$REPO_ROOT/hpc/zeus_network_extremes_resampled_N12_array.pbs")"
printf '%s job_id=%s array=0-%s families=4 tails=10+10 realizations=5 N=12 total=400 run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_LAST" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"
