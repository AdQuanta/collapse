#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_ring_catalog_missing_n17_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/zeus_ring_catalog_missing_n17.json}"
ARRAY_LAST="${ARRAY_LAST:-22}"

mkdir -p "$RUN_ROOT/logs"
sha256sum \
  "$CONFIG" \
  core/ranked_born_campaign.py \
  core/level_spacing.py \
  core/hamiltonians/quspin_hamiltonians.py \
  scripts/build_three_ring_momentum_spacing_figures.py \
  scripts/run_zeus_ring_catalog_missing_n17.py \
  hpc/zeus_ring_catalog_missing_n17_array.pbs \
  hpc/submit_zeus_ring_catalog_missing_n17.sh \
  > "$RUN_ROOT/defining_files.sha256"
git rev-parse HEAD > "$RUN_ROOT/git_commit.txt" 2>/dev/null || true

JOB_ID="$(qsub -J "0-$ARRAY_LAST" \
  -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG" \
  "$REPO_ROOT/hpc/zeus_ring_catalog_missing_n17_array.pbs")"

printf '%s job_id=%s array=0-%s configurations=23 N=17 hz0=0 storage=summary spacing_sectors=45 run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_LAST" "$RUN_ROOT" \
  | tee "$RUN_ROOT/submitted_jobs.txt"
