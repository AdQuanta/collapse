# Zeus: two-pixel conjecture comparison

This PBS array repeats the complete 59-point, four-time single/two-pixel
comparison at equal total detector sizes `N_D=10,12,14`. No job has been
submitted by Codex.

Submit from the repository root:

```bash
qsub hpc/zeus_two_pixel_conjecture_comparison.pbs
```

If the pinned Python 3.11 environment is not already active:

```bash
qsub -v VIRTUAL_ENV_PATH="$PWD/.venv-zeus-atlas" hpc/zeus_two_pixel_conjecture_comparison.pbs
```

The script verifies Python 3.11, `quspin==1.0.0`, and
`quspin-extensions==0.1.6` before simulation. It uses collective `Jx=0.01`,
so every central edge is `0.01/sqrt(N_D)`. Each array index has its own raw and
figure directories; all 472 spectra are checkpointed independently, and the
31 plots plus manifest are written before `DONE`.

Useful checks:

```bash
qsub -J 10 -v DRY_RUN=1 hpc/zeus_two_pixel_conjecture_comparison.pbs
qsub -J 10 -v SMOKE=1 hpc/zeus_two_pixel_conjecture_comparison.pbs
```

Use a unique output namespace for production:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
qsub -v RUN_ROOT="work/two_pixel_${RUN_TAG}",LOG_ROOT="logs/two_pixel_${RUN_TAG}" hpc/zeus_two_pixel_conjecture_comparison.pbs
```

`MODEL_WORKERS=1` is the safe default because dense relative-evolution matrices
make memory, not CPU count, the limiting resource. A single complex128 matrix
requires about 0.25 GiB at `N_D=12` and 4 GiB at `N_D=14`, before additional
propagator and eigensolver workspaces. The 128 GiB request is therefore a
planning allocation, not a measured Zeus peak. Inspect the `N_D=10` log before
scaling. The dense method is not advertised for `N_D>=16` under 128 GiB.

The job accepts `FORCE=1` to recompute checkpoints deliberately. Without it,
reruns resume from the existing per-spectrum NPZ files. PBS output is merged
and redirected to `$LOG_ROOT/ND<N>_<PBS_JOBID>.log`.
