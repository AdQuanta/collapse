#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v qsub >/dev/null 2>&1; then
  echo "qsub is not available; run this script on a Zeus login node." >&2
  exit 2
fi

# The caller may provide RUN_ROOT. Otherwise create one shared timestamped root.
RUN_ROOT="${RUN_ROOT:-$REPO_ROOT/work/zeus_sobol_coupling_scans_$(date +%Y%m%d_%H%M%S)}"
case "$RUN_ROOT" in
  /*) ;;
  *) RUN_ROOT="$REPO_ROOT/$RUN_ROOT" ;;
esac
mkdir -p "$RUN_ROOT/logs"
SUBMISSION_LOG="$RUN_ROOT/submitted_jobs.txt"

submit_one() {
  local script="$1"
  local prefix="$2"
  local n="$3"
  local workers="$4"
  local numeric_threads="$5"
  local ncpus=8
  local memory=128gb
  local job_id

  job_id="$(
    qsub \
      -N "${prefix}_N${n}" \
      -l "select=1:ncpus=${ncpus}:mem=${memory}" \
      -v "RUN_ROOT=${RUN_ROOT},N=${n},CONFIG_WORKERS=${workers},NUMERIC_THREADS=${numeric_threads}" \
      "$script"
  )"
  printf '%s simulation=%s N=%s ncpus=%s mem=%s workers=%s numeric_threads=%s job_id=%s\n' \
    "$(date --iso-8601=seconds)" "$prefix" "$n" "$ncpus" "$memory" \
    "$workers" "$numeric_threads" "$job_id" \
    | tee -a "$SUBMISSION_LOG"
}

# Match the validated relative-scale campaign: every job requests 8 CPUs and
# 128 GB; process workers decrease as dense-sector memory grows, while BLAS
# threads increase so all eight allocated CPUs remain available.
# Format: N:configuration_workers:numeric_threads.
for specification in "13:4:2" "14:2:4" "15:2:4" "16:1:8"; do
  IFS=: read -r n workers numeric_threads <<<"$specification"
  submit_one "$REPO_ROOT/hpc/zeus_sobol_jy_zero_worker.pbs" \
    "jy0" "$n" "$workers" "$numeric_threads"
done

for specification in "13:4:2" "14:2:4" "15:2:4" "16:1:8"; do
  IFS=: read -r n workers numeric_threads <<<"$specification"
  submit_one "$REPO_ROOT/hpc/zeus_sobol_jy_nonzero_worker.pbs" \
    "jynz" "$n" "$workers" "$numeric_threads"
done

printf '\nSubmitted eight independent jobs.\nShared output root: %s\nSubmission log: %s\n' \
  "$RUN_ROOT" "$SUBMISSION_LOG"
