# Zeus runbook: conjecture-driven candidate campaign, N=11..18

This array runs the 12 conjecture-motivated Hamiltonian cases in
`configs/conjecture_candidate_campaign_2026-07-16.json`. Each array element
owns one total qubit count `N=11,...,18`; each Hamiltonian is checkpointed as
soon as it finishes. No jobs were submitted during preparation.

## Upload and submit

Upload the current repository to Zeus, then log in and run the following from
the repository root (normally `$HOME/research/collapse`):

```bash
cd "$HOME/research/collapse"
mkdir -p logs
qsub hpc/zeus_conjecture_candidate_campaign_N11_N18.pbs
```

That is the complete command after `qsub`: 
`hpc/zeus_conjecture_candidate_campaign_N11_N18.pbs`.

The PBS script contains the requested settings:

- queue `zeus_new_q`;
- one node, 8 CPUs, 128 GB RAM;
- mail events `abe` to `matanhaller@campus.technion.ac.il`;
- Python 3.11, verified before simulation;
- array indices 11 through 18.

The script resolves the project through `PBS_O_WORKDIR` and invokes the runner
with an absolute path. This avoids the earlier `hpc/...: No such file or
directory` failure. If you submit from elsewhere, supply the project root:

```bash
qsub -v PROJECT_ROOT="$HOME/research/collapse" \
  "$HOME/research/collapse/hpc/zeus_conjecture_candidate_campaign_N11_N18.pbs"
```

## Outputs and restart behavior

For each N, results are saved after every Hamiltonian under:

```text
work/conjecture_candidate_campaign_<RUN_TAG>/N<N>/<case-id>/
```

Each case directory contains `results.csv`, `results.json`,
`top_candidates.md`, `run.log`, and its diagnostic figure. The N-level folder
also receives `aggregate_results.csv`, `case_summary.csv`,
`candidate_list_and_local_results.md`, and `campaign_manifest.json`.
Synthesis figures are stored under
`figures/conjecture_candidate_campaign_<RUN_TAG>/N<N>/`, while scheduler-side
logs are under `logs/conjecture_candidate_campaign_<RUN_TAG>/`.

If a job stops, resubmit with the same roots and tag. Completed case
checkpoints are reused:

```bash
qsub -v RUN_TAG=my_fixed_tag \
  hpc/zeus_conjecture_candidate_campaign_N11_N18.pbs
```

Use the same `RUN_TAG` on the retry. To force recomputation, run the Python
runner manually with `--force`.

## Monitor

```bash
qstat -u "$USER"
find logs -path '*conjecture_candidate_campaign*' -type f | sort | tail
tail -n 80 logs/conjecture_candidate_campaign_<RUN_TAG>/N11.*.log
find work/conjecture_candidate_campaign_<RUN_TAG> -name results.csv | sort
```

## Resource warning

The Hilbert-space dimension grows as `2^N`. Dense complex matrices alone scale
as `16 * 4^N` bytes before eigensolver workspaces: approximately 64 GB at
`N=16`, 256 GB at `N=17`, and 1 TB at `N=18`. The search engine therefore uses
`--backend auto` so QuSpin symmetry blocks are attempted. Even with 128 GB,
some `N=17,18` cases may still be infeasible when a symmetry is broken by
disorder or anisotropy. Treat N=11 first as a pilot, inspect memory and logs,
then allow the higher array elements to proceed. The scripts cover every
requested N, but they do not pretend that an unblocked dense N=18
diagonalization fits in 128 GB.

To pilot only N=11 before the full array, PBS Pro installations usually allow:

```bash
qsub -J 11 hpc/zeus_conjecture_candidate_campaign_N11_N18.pbs
```

If Zeus does not accept command-line array overrides, copy the PBS file and
temporarily change `#PBS -J 11-18` to `#PBS -J 11`.
