#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run on Zeus." >&2; exit 2; }

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_hamiltonian_classification_$(date +%Y%m%d_%H%M%S)}"
case "$RUN_ROOT" in /*) ;; *) RUN_ROOT="$REPO_ROOT/$RUN_ROOT" ;; esac
mkdir -p "$RUN_ROOT/logs"
MANIFEST="$RUN_ROOT/scan_manifest.csv"
python3.11 scripts/generate_hamiltonian_classification_manifest.py \
  --config configs/hamiltonian_classification_zeus_campaign.json \
  --output "$MANIFEST"
JOB_ID="$(qsub -v "RUN_ROOT=$RUN_ROOT,MANIFEST=$MANIFEST" "$REPO_ROOT/hpc/zeus_hamiltonian_classification_array.pbs")"
printf '%s job_id=%s array=0-19 run_root=%s manifest=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$RUN_ROOT" "$MANIFEST" \
  | tee "$RUN_ROOT/submitted_jobs.txt"

