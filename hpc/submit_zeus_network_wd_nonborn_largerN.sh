#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_network_wd_nonborn_largerN_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/zeus_network_wd_nonborn_largerN.json}"
ARRAY_LAST="${ARRAY_LAST:-11}"
mkdir -p "$RUN_ROOT/logs"
sha256sum \
  "$CONFIG" \
  core/ranked_born_campaign.py \
  core/network_ranked_followup.py \
  core/network_spacing_summary.py \
  scripts/run_zeus_network_wd_nonborn_largerN.py \
  hpc/zeus_network_wd_nonborn_largerN_array.pbs \
  hpc/submit_zeus_network_wd_nonborn_largerN.sh \
  > "$RUN_ROOT/defining_files.sha256"
JOB_ID="$(qsub -J "0-$ARRAY_LAST" -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG" "$REPO_ROOT/hpc/zeus_network_wd_nonborn_largerN_array.pbs")"
printf '%s job_id=%s array=0-%s cases=4 N=13,14,15 total=12 storage=summary run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_LAST" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"
