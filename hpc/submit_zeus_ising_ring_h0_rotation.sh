#!/bin/bash
# Submit one N_pixel value of the Ising-ring h_0-rotation campaign
# (scripts/plot_ising_ring_h0_rotation_bloch_and_ratio.py --symmetry --basis h0).
#
# Usage: N_OFFSET=<0..5> WALLTIME=<hh:mm:ss> RUN_ROOT=<dir> \
#          hpc/submit_zeus_ising_ring_h0_rotation.sh
# N_OFFSET 0..5 maps to N_pixel = 13..18. Each call submits one independent
# (non-array) job so walltime can be tailored per N.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }

: "${N_OFFSET:?Set N_OFFSET=0..5 (N_pixel = 13 + N_OFFSET)}"
if [[ ! "$N_OFFSET" =~ ^[0-5]$ ]]; then
  echo "N_OFFSET must be 0..5; got '$N_OFFSET'" >&2
  exit 2
fi
WALLTIME="${WALLTIME:-6:00:00}"
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_ising_ring_h0_rotation_$(date +%Y%m%d_%H%M%S)}"
case "$RUN_ROOT" in
  /*) ;;
  *) RUN_ROOT="$REPO_ROOT/$RUN_ROOT" ;;
esac
mkdir -p "$RUN_ROOT/logs"

JOB_ID="$(qsub -N "ising_h0rot_N$((13 + N_OFFSET))" -l "walltime=$WALLTIME" \
  -v "RUN_ROOT=$RUN_ROOT,N_OFFSET=$N_OFFSET" \
  "$REPO_ROOT/hpc/zeus_ising_ring_h0_rotation_array.pbs")"
printf '%s job_id=%s n_pixel=%d walltime=%s run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$((13 + N_OFFSET))" "$WALLTIME" "$RUN_ROOT" \
  | tee -a "$RUN_ROOT/submitted_jobs.txt"
