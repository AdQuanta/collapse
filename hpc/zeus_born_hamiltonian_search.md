# Zeus Born Hamiltonian Search Handoff

This is the first-pass Zeus runbook for `scripts/born_hamiltonian_search.py`.
The search entry point writes `results.json`, `results.csv`,
`top_candidates.md`, and `run.log` under `--out-dir`.

Coordination policy: Codex does not handle SSH credentials and does not submit
jobs directly. Use this file as a manual runbook: run PBS/qsub blocks yourself
on Zeus, then run retrieval and post-processing blocks locally.

## Confirmed Zeus Defaults

These defaults came from the previous successful Zeus run:

- Queue: `zeus_new_q`.
- Resource request style in the template: `#PBS -l select=1:ncpus=8:mem=64gb`.
- Notification email: `matanhaller@campus.technion.ac.il`.
- Remote workdir convention: `$HOME/research/collapse`.
- Python command convention: `python3.11`.
- Submission command: `qsub <script.pbs>`.

If any of these are wrong, update `hpc/zeus_born_hamiltonian_search.pbs`
before submitting.

## Local Outputs Inspected

- `figures/born_hamiltonian_search_N11_crosscheck_b50_tail20`: current strongest
  local crosscheck; top row is N=11 ring, matched, `Jpm=0.1`, `Jx_unscaled=0.1`,
  `hz=0.1`, `t=100`, score about 0.671.
- `figures/born_hamiltonian_search_ring_N9_small`: ring control has plausible
  tails; top row score about 0.423.
- `figures/born_hamiltonian_search_chain_N9_small`: chain control scores poorly;
  top row score about 0.021.
- `figures/born_hamiltonian_search_sz_conserving_control_N9`: fresh control run
  observed during this handoff; it is atomic and scores about 0.002.

## PBS Template

Use `hpc/zeus_born_hamiltonian_search.pbs` after confirming:

- `#PBS -J 1-5` is accepted on Zeus. If not, replace it with `#PBS -t 1-5` or
  submit five separate jobs with `TASK_ID=1`, ..., `TASK_ID=5`.
- `select=1:ncpus=8:mem=64gb` is appropriate for this script. The search
  itself is a single Python process per array task, so CPU use depends on
  BLAS/QuSpin threading and Zeus policy. If memory is tight for larger N,
  request more memory or split the grid into smaller array tasks.
- `python3.11` has the required packages, especially NumPy and QuSpin.

The template uses a PBS array:

- Task 1: broad matched ring scan, N=11 and N=12.
- Task 2: detuning scan, N=11 ring with `zero`, `half`, and `minus` hz0 modes.
- Task 3: broader Jpm scan, N=11 ring.
- Task 4: chain control, N=11.
- Task 5: Sz-conserving exchange/control, N=11 with `Jx_unscaled=0` and
  `Jcpm_unscaled` including zero and nonzero central flip-flop exchange.

Outputs go to `figures/zeus_born_hamiltonian_search/<run_name>`. Each output
directory has its own `run.log`. Scheduler-side stdout/stderr logs go to
`logs/zeus_born_hamiltonian_search/<run_name>.<jobid>.<task>.log`.

## Upload Code Manually

If the Zeus checkout is not already updated, run one of these yourself from the
local repository. This avoids deleting remote result directories.

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"

rsync -avz \
  --exclude ".git/" \
  --exclude "__pycache__/" \
  --exclude "*.pyc" \
  --exclude ".ipynb_checkpoints/" \
  --exclude "figures/" \
  --exclude "logs/" \
  ./ "${ZEUS_TARGET}:${REMOTE_ROOT}/"
```

If `rsync` is unavailable, use `scp`:

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"

ssh "${ZEUS_TARGET}" "mkdir -p '${REMOTE_ROOT}'"
scp -r core scripts hpc "${ZEUS_TARGET}:${REMOTE_ROOT}/"
```

## Submit From Zeus Login Shell

Run this on Zeus from the repository root. The PBS file embeds
`#PBS -q zeus_new_q` and `#PBS -J 1-5`.

```bash
cd "$HOME/research/collapse"
RUN_TAG="firstpass_$(date +%Y%m%d_%H%M%S)_born"
RUN_ROOT="figures/zeus_born_hamiltonian_search_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_hamiltonian_search_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_hamiltonian_search.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "Scheduler-side task logs: $LOG_ROOT/<run-name>.<PBS_JOBID>.<TASK_ID>.log"
echo "Per-output simulation logs: $RUN_ROOT/<run-name>/run.log"
```

## Monitor On Zeus

```bash
cd "$HOME/research/collapse"
qstat -u "$USER"
qstat -f <JOB_ID>
find "$LOG_ROOT" -maxdepth 1 -type f | sort | tail
find "$RUN_ROOT" -path '*/run.log' -type f | sort
tail -n 80 "$LOG_ROOT/<RUN_LOG>.log"
tail -n 80 "$RUN_ROOT/<RUN_NAME>/run.log"
```

Cancel if needed:

```bash
qdel <JOB_ID>
```

## Retrieve Results

Run this locally after the Zeus job completes. It retrieves both the
scheduler-side logs and the per-output `run.log` files.

```bash
ZEUS_TARGET="<YOUR_ZEUS_SSH_ALIAS_OR_USER_AT_HOST>"
REMOTE_ROOT="research/collapse"
RUN_TAG="<RUN_TAG_USED_FOR_THE_JOB>"
RUN_ROOT="figures/zeus_born_hamiltonian_search_${RUN_TAG}"
LOG_ROOT="logs/zeus_born_hamiltonian_search_${RUN_TAG}"

mkdir -p "./${RUN_ROOT}" "./${LOG_ROOT}"
rsync -avz \
  "${ZEUS_TARGET}:${REMOTE_ROOT}/${RUN_ROOT}/" \
  "./${RUN_ROOT}/"
rsync -avz \
  "${ZEUS_TARGET}:${REMOTE_ROOT}/${LOG_ROOT}/" \
  "./${LOG_ROOT}/"
```

## Coordination With Numerical Work

- Do not overwrite local numerical output directories. Use a unique Zeus run
  root such as `figures/zeus_born_hamiltonian_search_YYYYMMDD_<tag>` when the
  final grid is approved.
- Keep the numerical subagent's commands as the source of truth. The PBS
  template should either mirror those exact arguments or use `RUN_ROOT` and
  `PYTHON_BIN` environment overrides around them.
- Keep one result directory per scan slice. The search script always writes
  `results.json`, `results.csv`, `top_candidates.md`, and `run.log`, so
  retrieval and comparison scripts can glob for those names.
- Capture stdout/stderr with `tee` logs and keep the in-output `run.log`.
  The script prints candidate progress, selected backend, and final top
  candidates, which is enough for remote triage.
- Prefer `--backend auto` on Zeus so QuSpin is used when available and NumPy is
  used only as fallback. If QuSpin is absent and N=12 NumPy runs are too large,
  rerun only after the user approves dependency installation or a smaller grid.
