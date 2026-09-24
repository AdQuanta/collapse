#!/bin/bash
# Submit the resonant Ising ring sector campaign as one PBS array (kp = 0..N/2).
# Usage: N_PIXEL=18 J_BOND=0.37 G_COUP=0.1 TAUS=10,30,100 [WALLTIME=36:00:00] [RUN_ROOT=<dir>] \
#          hpc/submit_zeus_ring_h0z_eq_hz_sectors.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
: "${N_PIXEL:?}"; : "${J_BOND:?}"; : "${G_COUP:?}"; : "${TAUS:?}"
WALLTIME="${WALLTIME:-36:00:00}"
RUN_ROOT="${RUN_ROOT:?Set RUN_ROOT to a fresh directory}"
mkdir -p "$RUN_ROOT/logs" "$RUN_ROOT/sectors"
JOB_ID="$(qsub -N "ring_h0zhz_N${N_PIXEL}" -J "0-$((N_PIXEL / 2))" -l "walltime=$WALLTIME" \
  -v "RUN_ROOT=$RUN_ROOT,N_PIXEL=$N_PIXEL,J_BOND=$J_BOND,G_COUP=$G_COUP,TAUS=$TAUS" \
  "$REPO_ROOT/hpc/zeus_ring_h0z_eq_hz_sectors.pbs")"
printf '%s job_id=%s N=%s J=%s g=%s taus=%s walltime=%s run_root=%s\n' "$(date --iso-8601=seconds)" \
  "$JOB_ID" "$N_PIXEL" "$J_BOND" "$G_COUP" "$TAUS" "$WALLTIME" "$RUN_ROOT" | tee -a "$RUN_ROOT/submitted_jobs.txt"
