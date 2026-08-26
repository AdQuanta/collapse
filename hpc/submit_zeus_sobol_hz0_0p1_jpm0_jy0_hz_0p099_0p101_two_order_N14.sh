#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v qsub >/dev/null 2>&1; then
  echo "qsub is not available; run this script on a Zeus login node." >&2
  exit 2
fi

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_sobol_hz0_0p1_hz_0p099_0p101_two_order_N14_$(date +%Y%m%d_%H%M%S)}"
case "$RUN_ROOT" in
  /*) ;;
  *) RUN_ROOT="$REPO_ROOT/$RUN_ROOT" ;;
esac
mkdir -p "$RUN_ROOT/logs"

PBS_SCRIPT="$REPO_ROOT/hpc/zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14_array.pbs"
JOB_ID="$(qsub -v "RUN_ROOT=$RUN_ROOT" "$PBS_SCRIPT")"
printf '%s job_id=%s array=0-3 N=14 hz0=0.1 hz=[0.099,0.101] Jpm=0 Jy=0 kappa=0.01 total=100 shard_size=25 run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"

printf '\nSubmitted four disjoint 25-configuration N=14 jobs.\n'
printf 'Constraint: Jx <= 0.01 min(J,hz,abs(hz0)) before 1/sqrt(14).\n'
printf 'Shared output root: %s\n' "$RUN_ROOT"

