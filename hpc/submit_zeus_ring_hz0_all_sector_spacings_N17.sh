#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
command -v qsub >/dev/null 2>&1 || { echo "qsub is unavailable; run this on Zeus." >&2; exit 2; }

RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_ring_hz0_all_sector_spacings_N17_$(date +%Y%m%d_%H%M%S)}"
SOURCE_CONFIG="${CONFIG:-configs/ring_second_neighbor_wd_hz0_all_sector_spacings_N17.json}"
ARRAY_RANGE="${ARRAY_RANGE:-0-19}"
mkdir -p "$RUN_ROOT/logs"
CONFIG="$RUN_ROOT/effective_scan_config.json"
cp "$SOURCE_CONFIG" "$CONFIG"
python3.11 -m json.tool "$CONFIG" >/dev/null

QSUB_VARIABLES="RUN_ROOT=$RUN_ROOT,CONFIG=$CONFIG"
if [[ "${SMOKE:-0}" == "1" ]]; then QSUB_VARIABLES="$QSUB_VARIABLES,SMOKE=1"; fi
if [[ "${DRY_RUN:-0}" == "1" ]]; then QSUB_VARIABLES="$QSUB_VARIABLES,DRY_RUN=1"; fi
if [[ -n "${VIRTUAL_ENV_PATH:-}" ]]; then QSUB_VARIABLES="$QSUB_VARIABLES,VIRTUAL_ENV_PATH=$VIRTUAL_ENV_PATH"; fi
if [[ -n "${ZEUS_ENV_SETUP:-}" ]]; then QSUB_VARIABLES="$QSUB_VARIABLES,ZEUS_ENV_SETUP=$ZEUS_ENV_SETUP"; fi
if [[ -n "${PYTHON_BIN:-}" ]]; then QSUB_VARIABLES="$QSUB_VARIABLES,PYTHON_BIN=$PYTHON_BIN"; fi

JOB_ID="$(qsub -J "$ARRAY_RANGE" -v "$QSUB_VARIABLES" "$REPO_ROOT/hpc/zeus_ring_hz0_all_sector_spacings_N17_array.pbs")"
printf '%s job_id=%s array=%s unique_sectors=20 hz0_values=20 eigenvalues=512 checkpoint=each_hz0 run_root=%s\n' \
  "$(date --iso-8601=seconds)" "$JOB_ID" "$ARRAY_RANGE" "$RUN_ROOT" | tee -a "$RUN_ROOT/submitted_jobs.txt"
printf 'Expected production outputs: 20 sector COMPLETE.json files and 400 checkpoint archives.\n'
