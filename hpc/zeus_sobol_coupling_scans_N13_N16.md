# Zeus Sobol weak-coupling campaigns

Run from the repository root (the directory containing `scripts/`, `core/`,
and `hpc/`). Python 3.11 is invoked directly; no virtual environment is
activated.

## Recommended: independently sized per-N jobs

The recommended launcher submits eight independent jobs with the same shared
output root. Run:

```bash
cd /path/to/collapse
bash hpc/submit_zeus_sobol_coupling_scans_tuned.sh
```

The resource and parallelism schedule exactly follows the relative-scale
simulation. Every job requests 8 CPUs and 128 GB:

- N=13: 4 configuration workers, 2 numerical-library threads per worker;
- N=14: 2 configuration workers, 4 numerical-library threads per worker;
- N=15: 2 configuration workers, 4 numerical-library threads per worker;
- N=16: 1 configuration worker, 8 numerical-library threads.

Workers process different Sobol configurations concurrently. BLAS/OpenMP
threads accelerate the dense calculation within each worker. To choose the
output root yourself:

```bash
export RUN_ROOT="$PWD/work/my_sobol_campaign"
bash hpc/submit_zeus_sobol_coupling_scans_tuned.sh
```

The launcher calls `zeus_sobol_jy_zero_worker.pbs` and
`zeus_sobol_jy_nonzero_worker.pbs`, passing `N`, `CONFIG_WORKERS`, and
`NUMERIC_THREADS`, together with the exact per-job `select` request through
`qsub`.

## Uniform-resource PBS-array alternative

To use the earlier uniform-resource array launchers instead, choose one new
shared, absolute output directory and submit both jobs with that same value:

```bash
cd /path/to/collapse
export RUN_ROOT="$PWD/work/zeus_sobol_coupling_scans_$(date +%Y%m%d_%H%M%S)"
qsub -v RUN_ROOT="$RUN_ROOT" hpc/zeus_sobol_jy_zero_N13_N16.pbs
qsub -v RUN_ROOT="$RUN_ROOT" hpc/zeus_sobol_jy_nonzero_N13_N16.pbs
```

Each array submission is a four-element PBS array: N=13,14,15,16 run as independent
subjobs in parallel. Configurations are also parallelized within each N subjob;
the Python driver caps the requested eight workers to four for N=13, two for
N=14 and N=15, and one for N=16. Each completed
configuration has a checksummed `COMPLETE.json`; `--resume` skips only
validated, complete outputs.

Failures are non-fatal. Every failure is preserved in that configuration's
`FAILURE.json` and execution log, checkpoint summaries analyze only cases with
a validated `COMPLETE.json`, and the PBS subjob exits normally after processing
all remaining configurations.

Each successful-case aggregation also writes CSV, JSON, and heatmap summaries
of descriptive Spearman correlations between the log-unscaled parameters,
every nonredundant pairwise parameter ratio, the enforced weak-coupling ratio,
`S_born`, and all common wrapped-Gaussian/wrapped-Cauchy discrepancy measures.
The cross-N version uses one averaged record per configuration.

All nonzero sampled parameters use the logarithmic interval
`[1e-3, 10]`. The weak-coupling constraint is applied after sampling the
detector scales.

To inspect the exact samples before submitting:

```bash
python3.11 scripts/run_zeus_sobol_jy_zero_scan.py --output-root "$RUN_ROOT" --dry-run
python3.11 scripts/run_zeus_sobol_jy_nonzero_scan.py --output-root "$RUN_ROOT" --dry-run
```

The expensive production jobs may safely reuse that prepared root because the
PBS launchers pass `--resume`.
