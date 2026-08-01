# Zeus runbook: expanded perturbative Hamiltonian sweep

This PBS array scales the designed multi-factor campaign in
`configs/expanded_hamiltonian_sweep_2026-07-16.json` to total qubit counts
`N=11,...,18`. It varies `Jpm`, detector anisotropy, independent central X/Y
couplings, weak transverse and longitudinal channels, field/bond disorder,
matching, and geometry. Every unscaled central coupling is at most 0.01 and is
divided by `sqrt(N_pixel)` by the simulation engine.

No jobs were submitted during preparation.

## Submit from the Zeus repository root

```bash
cd "$HOME/research/collapse"
mkdir -p logs
qsub hpc/zeus_expanded_hamiltonian_sweep_N11_N18.pbs
```

The script requests `zeus_new_q`, 8 CPUs, 128 GB, Python 3.11, and mail events
`abe` to `matanhaller@campus.technion.ac.il`.

If submitting outside the repository root:

```bash
qsub -v PROJECT_ROOT="$HOME/research/collapse" \
  "$HOME/research/collapse/hpc/zeus_expanded_hamiltonian_sweep_N11_N18.pbs"
```

## Checkpoints and logs

Each N is independent. Each Hamiltonian writes `results.csv`, `results.json`,
`top_candidates.md`, `run.log`, and a diagnostic figure before the next case
begins. N-level aggregation then writes `aggregate_results.csv`,
`expanded_case_summary.csv`, `ranked_results.csv`,
`expanded_sweep_findings.md`, and the tradeoff figure. The final serial
post-processing stage caches every relative-unitary spectrum under each
case's `atlas_raw/` directory and renders the report-style blue/red 3xL pages
under `<FIGURE_ROOT>/atlases/`. The atlas cache is resumable and avoids
parallel dense diagonalizations within the 128 GB allocation.

Default locations:

```text
work/expanded_hamiltonian_sweep_<RUN_TAG>/N<N>/
figures/expanded_hamiltonian_sweep_<RUN_TAG>/N<N>/
logs/expanded_hamiltonian_sweep_<RUN_TAG>/
```

For a restart, resubmit with the same `RUN_TAG`; completed case checkpoints are
reused:

```bash
qsub -v RUN_TAG=expanded_fixed_tag \
  hpc/zeus_expanded_hamiltonian_sweep_N11_N18.pbs
```

## Pilot and memory warning

Run `N=11` first. Dense complex storage scales as `16*4^N` bytes before
eigensolver workspaces: roughly 64 GB at N=16, 256 GB at N=17, and 1 TB at
N=18. `--backend auto` attempts QuSpin symmetry blocks, but disorder,
anisotropy, and all-to-all cases can break those symmetries. The array covers
every requested size; it does not imply that every N=17 or N=18 Hamiltonian
fits in 128 GB.

On PBS Pro, a typical N=11 pilot is:

```bash
qsub -J 11 hpc/zeus_expanded_hamiltonian_sweep_N11_N18.pbs
```

Monitor with:

```bash
qstat -u "$USER"
find logs -path '*expanded_hamiltonian_sweep*' -type f | sort | tail
find work -path '*expanded_hamiltonian_sweep*' -name results.csv | sort
```
