#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v qsub >/dev/null 2>&1; then
  echo "qsub is not available; run this script on a Zeus login node." >&2
  exit 2
fi

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_vab_atlas_jx_1em3_N14_$(date +%Y%m%d_%H%M%S)}"
case "$RUN_ROOT" in
  /*) ;;
  *) RUN_ROOT="$REPO_ROOT/$RUN_ROOT" ;;
esac
mkdir -p "$RUN_ROOT/logs"

JOB_ID="$(qsub -v "RUN_ROOT=$RUN_ROOT" "$REPO_ROOT/hpc/zeus_vab_atlas_jx_1em3_N14_array.pbs")"
printf '%s job_id=%s array=0-8 N=14 hz0=0 Jx_unscaled=1e-3 total=880 shard_sizes=100x8+80 run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"

printf '\nSubmitted the nine-element weak-Jx atlas array.\n'
printf '  0-7: 100 configurations per job\n'
printf '  8:   final 80 configurations\n'
printf 'Shared output root: %s\n' "$RUN_ROOT"

