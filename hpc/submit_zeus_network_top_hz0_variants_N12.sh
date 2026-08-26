#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_network_top_hz0_variants_N12_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/zeus_network_top_hz0_variants_N12.json}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
mkdir -p "$RUN_ROOT/logs"
DESCRIPTION="$RUN_ROOT/campaign_description.json"
"$PYTHON_BIN" examples/run_zeus_network_top_hz0_variants_N12.py \
  --config "$CONFIG" --describe | tee "$DESCRIPTION"
ARRAY_TASKS="$("$PYTHON_BIN" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["array_tasks"])' "$DESCRIPTION")"
if [[ "$ARRAY_TASKS" -lt 1 ]]; then
  echo "Campaign description returned no array tasks." >&2
  exit 2
fi
ARRAY_LAST=$((ARRAY_TASKS - 1))
JOB_ID="$(qsub -J "0-$ARRAY_LAST" -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG,PYTHON_BIN=$PYTHON_BIN" "$REPO_ROOT/hpc/zeus_network_top_hz0_variants_N12_array.pbs")"
printf '%s job_id=%s array=0-%s families=4 top_per_family=10 N=12 total=240 run_root=%s config=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_LAST" "$RUN_ROOT" "$CONFIG" \
  | tee "$RUN_ROOT/submitted_jobs.txt"
