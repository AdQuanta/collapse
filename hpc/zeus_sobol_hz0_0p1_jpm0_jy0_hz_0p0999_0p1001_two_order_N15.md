# Very-narrow-hz N=15 Sobol scan with a two-order weak-Jx constraint

This campaign contains 100 deterministic scrambled-Sobol configurations with
`N=15`, `t=1e6`, `hz0=0.1` exactly, and `Jpm=Jy=0` exactly. The detector field
`hz` is sampled logarithmically over `[0.0999,0.1001]`, while `J` is sampled
logarithmically over `[1e-3,10]`.

The unscaled coupling is sampled logarithmically between `1e-5` and
`0.01*min(J,hz,abs(hz0))`. Therefore every configuration obeys
`Jx <= 0.01 J`, `Jx <= 0.01 hz`, and `Jx <= 0.01 |hz0|` before the backend
applies `Jx_edge=Jx/sqrt(15)` exactly once.

Submit from the repository root on Zeus:

```bash
bash hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_two_order_N15.sh
```

The array indices are `0-3`; each job owns 25 non-overlapping configurations,
requests 8 CPUs and 128 GB, and runs two configuration workers. Results are
checkpointed after every configuration. Failures remain recorded but are
excluded from success-only aggregation. No virtual environment is activated.
