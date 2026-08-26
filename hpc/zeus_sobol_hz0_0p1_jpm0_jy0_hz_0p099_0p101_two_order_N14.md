# N=14 narrow-hz Sobol scan with two-order weak Jx

This is the `N=14` counterpart of the corresponding `N=15` campaign. It uses
the same Sobol seed, so the 100 unscaled parameter configurations match
configuration-by-configuration across the two sizes.

Fixed settings:

- `hz0=0.1`, `Jpm=0`, `Jy=0`, and `t=1e6`;
- `J` sampled logarithmically over `[1e-3,10]`;
- `hz` sampled logarithmically over `[0.099,0.101]`;
- unscaled `Jx` sampled logarithmically from `1e-5` to
  `0.01*min(J,hz,abs(hz0))`;
- effective coupling `Jx_edge=Jx/sqrt(14)`, applied exactly once.

Submit on Zeus from the repository root:

```bash
bash hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14.sh
```

The PBS array has indices `0-3`, with 25 configurations per job. Each job
requests 8 CPUs and 128 GB and runs two configuration workers. Results are
checkpointed after each configuration and each array shard. No virtual
environment is activated.

Sampling-only validation:

```bash
python3.11 examples/run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N14.py \
  --batch-index 0 --output-root work/two_order_N14_dry_run --dry-run
```

