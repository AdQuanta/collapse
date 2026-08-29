# Narrow-hz Sobol scan with a two-order weak-Jx constraint

This campaign contains 100 deterministic scrambled-Sobol configurations at

- `N=15`, `t=1e6`, and `hz0=0.1` exactly;
- `Jpm=0` and `Jy=0` exactly;
- `J` sampled logarithmically over `[1e-3,10]`;
- `hz` sampled logarithmically over `[0.099,0.101]`;
- unscaled `Jx` sampled logarithmically between `1e-5` and
  `0.01*min(J,hz,abs(hz0))`.

Thus every accepted configuration obeys

```text
Jx <= 0.01 J,  Jx <= 0.01 hz,  Jx <= 0.01 |hz0|,
```

before the backend applies `Jx_edge=Jx/sqrt(15)` exactly once. Zero `Jpm` and
`Jy` are excluded from the ratio constraint, as required.

Submit from the repository root on Zeus:

```bash
bash hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N15.sh
```

The array has indices `0-3`; each job owns 25 non-overlapping configurations,
requests 8 CPUs and 128 GB, and runs two configuration workers. Results are
saved after every configuration and summarized after every shard. Failures are
recorded and excluded from success-only aggregation. No virtual environment is
activated.

To choose a new destination:

```bash
RUN_ROOT="$PWD/work/my_two_order_scan" \
  bash hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_two_order_N15.sh
```

Sampling-only check of the first shard:

```bash
python3.11 scripts/run_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p099_0p101_N15.py \
  --batch-index 0 --output-root work/two_order_dry_run \
  --kappa 0.01 --coupling-lower 1e-5 --dry-run
```

