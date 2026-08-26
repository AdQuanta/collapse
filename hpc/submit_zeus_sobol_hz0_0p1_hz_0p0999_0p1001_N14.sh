#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14_$(date +%Y%m%d_%H%M%S)}"
case "$RUN_ROOT" in /*) ;; *) RUN_ROOT="$REPO_ROOT/$RUN_ROOT" ;; esac
mkdir -p "$RUN_ROOT/logs"
JOB_ID="$(qsub -v "RUN_ROOT=$RUN_ROOT" "$REPO_ROOT/hpc/zeus_sobol_hz0_0p1_hz_0p0999_0p1001_N14_array.pbs")"
printf '%s job_id=%s array=0-3 N=14 hz0=0.1 hz=[0.0999,0.1001] total=400 shard_size=100 run_root=%s\n' "$(date --iso-8601=seconds)" "$JOB_ID" "$RUN_ROOT" | tee "$RUN_ROOT/submitted_jobs.txt"
