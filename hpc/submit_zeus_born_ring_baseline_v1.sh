#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${RUN_ROOT:?Set a fresh absolute output root}"
: "${PYTHON_BIN:?Set the verified Python 3.11 executable}"
test ! -e "$RUN_ROOT" || { echo "Output root already exists" >&2; exit 2; }
"$PYTHON_BIN" scripts/run_born_ring_campaign.py --output-root "$RUN_ROOT" --dry-run
command -v qsub >/dev/null
mkdir -p "$RUN_ROOT/logs"
sha256sum configs/born_ring_baseline_campaign_v1.json configs/born_multichannel_sensitivity_v1.json \
  core/ring_translation.py core/born_phase_verifier.py scripts/run_born_ring_campaign.py \
  hpc/zeus_born_ring_baseline_v1.pbs hpc/submit_zeus_born_ring_baseline_v1.sh > "$RUN_ROOT/defining_files.sha256"
JOB_ID="$(qsub -o "$RUN_ROOT/logs/" -v "RUN_ROOT=$RUN_ROOT,PYTHON_BIN=$PYTHON_BIN" hpc/zeus_born_ring_baseline_v1.pbs)"
printf '%s\n' "$JOB_ID" | tee "$RUN_ROOT/job_id.txt"
