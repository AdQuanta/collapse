#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_ranked_ring_extremes_N17_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/zeus_ranked_ring_extremes_N17.json}"
ARRAY_RANGE="${ARRAY_RANGE:-0-19}"
REUSE_EXISTING_N17="${REUSE_EXISTING_N17:-1}"

mkdir -p "$RUN_ROOT/logs"
cp "$CONFIG" "$RUN_ROOT/effective_campaign_config.json"

JOB_ID="$(qsub -J "$ARRAY_RANGE" \
  -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG,REUSE_EXISTING_N17=$REUSE_EXISTING_N17" \
  "$REPO_ROOT/hpc/zeus_ranked_ring_extremes_N17_array.pbs")"

printf '%s job_id=%s array=%s configurations=40 cases_per_task=2 N=17 reuse_existing_N17=%s checkpoint=each_configuration run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_RANGE" "$REUSE_EXISTING_N17" "$RUN_ROOT" \
  | tee "$RUN_ROOT/submitted_jobs.txt"
