#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run this on Zeus." >&2; exit 2; }

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_ring_born_like_hz0_scan_N17_$(date +%Y%m%d_%H%M%S)}"
SOURCE_CONFIG="${CONFIG:-configs/ring_born_like_hz0_scan_N17.json}"
ARRAY_RANGE="${ARRAY_RANGE:-0-19}"
mkdir -p "$RUN_ROOT/logs"
CONFIG="$RUN_ROOT/effective_scan_config.json"
cp "$SOURCE_CONFIG" "$CONFIG"

JOB_ID="$(qsub -J "$ARRAY_RANGE" -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG" "$REPO_ROOT/hpc/zeus_ring_born_like_hz0_scan_N17_array.pbs")"
printf '%s job_id=%s array=%s configurations=20 N=17 checkpoint=each_momentum run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_RANGE" "$RUN_ROOT" | tee -a "$RUN_ROOT/submitted_jobs.txt"
printf 'After the array completes, run:\n%s\n' \
  "python3.11 scripts/summarize_ring_hz0_activation_scan.py --run-root \"$RUN_ROOT\""
