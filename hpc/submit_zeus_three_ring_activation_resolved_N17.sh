#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_three_ring_activation_resolved_N17_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/three_ring_activation_resolved.json}"
mkdir -p "$RUN_ROOT/logs"
JOB_ID="$(qsub -J "0-2" -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG" "$REPO_ROOT/hpc/zeus_three_ring_activation_resolved_N17_array.pbs")"
printf '%s job_id=%s array=0-2 configurations=3 N=17 checkpoint=each_momentum run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"
