#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_network_resampled_jx_div10_timeavg_N12_15_$(date +%Y%m%d_%H%M%S)}"
CONFIG="${CONFIG:-configs/zeus_network_resampled_jx_div10_N12_15.json}"
SOURCE_ROOT="${SOURCE_ROOT:-$REPO_ROOT/work/zeus_network_extremes_resampled_N12_20260813_232636}"
ARRAY_RANGE="${ARRAY_RANGE:-0-19}"
[[ "$ARRAY_RANGE" =~ ^([0-9]+)-([0-9]+)$ ]] || { echo "ARRAY_RANGE must have the form START-END" >&2; exit 2; }
ARRAY_START="${BASH_REMATCH[1]}"
ARRAY_LAST="${BASH_REMATCH[2]}"
(( ARRAY_START >= 0 && ARRAY_LAST <= 19 && ARRAY_START <= ARRAY_LAST )) || { echo "ARRAY_RANGE must lie within 0-19" >&2; exit 2; }
[[ -d "$SOURCE_ROOT" ]] || { echo "Missing source campaign: $SOURCE_ROOT" >&2; exit 2; }
mkdir -p "$RUN_ROOT/logs"
JOB_ID="$(qsub -J "$ARRAY_RANGE" -v "RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG,SOURCE_ROOT=$SOURCE_ROOT" "$REPO_ROOT/hpc/zeus_network_resampled_jx_div10_N12_15_array.pbs")"
printf '%s job_id=%s array=%s samples_per_task=20 N=12,13,14,15 pooled_samples_per_case_N=32768 time_counts=8,4,2,1 Jx_factor=0.1 full_campaign_samples=400 Hamiltonian_N_cases=1600 time_evaluations=6000 checkpoint=each_sample_and_N run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_RANGE" "$RUN_ROOT" | tee -a "$RUN_ROOT/submitted_jobs.txt"
