# N=14 Vab atlas at unscaled Jx=1e-3

This campaign repeats all 880 ordered configurations from
`reports/vab_coupling_group_atlas_2026-07-28` at `N=14`, `t=1e6`, and
`hz0=0`. The only physics change is the collective coupling
`Jx=1e-3` before the established scaling, so every detector edge uses
`Jx_edge=1e-3/sqrt(14)`. Periodic-ring boundary conditions and `Jy=0` are
unchanged.

From the repository root on Zeus:

```bash
bash hpc/submit_zeus_vab_atlas_jx_1em3_N14.sh
```

The submission creates nine array jobs: eight jobs contain 100 cases and the
last contains 80. Each job requests 8 CPUs and 128 GB and runs two independent
fixed-`(hz,J)` row workers. Each row checkpoints all ten `Jpm` values.

Sampling grid:

- `hz = -2.01,-2,-1,-0.1,-0.01,0,0.01,0.1,1,2,2.01`;
- `J = 0,0.1,0.25,0.5,0.75,1,1.5,2`;
- `Jpm = 0,0.01,0.05,0.1,0.25,0.5,0.75,1,1.5,2`.

No virtual environment is activated. Outputs include raw spectra, metrics,
standard diagnostics, row checkpoints, logs with timestamps, and the final
per-`N` aggregate manifest. To select a new output directory:

```bash
RUN_ROOT="$PWD/work/my_jx_1em3_atlas" \
  bash hpc/submit_zeus_vab_atlas_jx_1em3_N14.sh
```

Sampling-only validation of one shard:

```bash
python3.11 examples/run_zeus_vab_atlas_jx_1em3_N14.py \
  --batch-index 0 --output-root work/jx_1em3_dry_run --dry-run
```

