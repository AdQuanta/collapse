# Zeus Sobol scan with fixed hz0=0.1 and N=15

Run from the repository root on a Zeus login node. Python 3.11 is invoked
directly; no virtual environment is activated.

```bash
cd /path/to/collapse
bash hpc/submit_zeus_sobol_hz0_0p1_N15.sh
```

This submits one PBS array with indices `0-7`:

- indices `0-3`: `Jy=0`, four disjoint 100-configuration batches;
- indices `4-7`: `Jy>0`, four disjoint 100-configuration batches.

Thus each Jy family contains exactly 400 points from one reproducible scrambled
Sobol sequence. Configuration IDs are global within the family:
`config_000` through `config_399`. Every subjob runs exactly 100 of them.

The production invariants are hard-coded:

- `N=15` detector spins;
- `hz0=0.1` exactly, with no command-line override;
- `t=1e6`;
- `J,Jpm,hz` sampled logarithmically over `[1e-3,10]`;
- `Jx` and nonzero `Jy` sampled conditionally so
  `max(Jx,Jy) <= 0.1 min(J,Jpm,hz,abs(hz0))`;
- effective central couplings are divided by `sqrt(N)` exactly once.

Each array subjob requests 8 CPUs and 128 GB, matching the established N=15
relative-scale schedule. It runs two configuration workers, with four numerical
library threads available to each worker. Different `(J,Jpm,hz,Jx[,Jy])`
configurations therefore run concurrently.

Each successful configuration immediately saves reusable numerical data,
metrics, WG/WC fits, validation, the standard blue-red diagnostic figure, the
fit diagnostic figure, execution log, and checksummed `COMPLETE.json` marker.
Failures are non-fatal and retained as `FAILURE.json`; final aggregation uses
only validated successful configurations.

Logs are written to:

```text
$RUN_ROOT/logs/<family>_N15_batch<batch>_<job-id>.log
```

To choose the output directory explicitly:

```bash
export RUN_ROOT="$PWD/work/my_hz0_0p1_scan"
bash hpc/submit_zeus_sobol_hz0_0p1_N15.sh
```

For a local sampling-only check, run any batch with `--dry-run`, for example:

```bash
python3.11 examples/run_zeus_sobol_hz0_0p1_N15.py \
  --family jy_zero --batch-index 0 --output-root work/hz0_0p1_dry_run --dry-run
```
