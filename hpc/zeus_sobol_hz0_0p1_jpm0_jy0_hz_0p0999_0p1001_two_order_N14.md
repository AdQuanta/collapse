# Very-narrow-hz N=14 Sobol scan with a two-order weak-Jx constraint

This is the `N=14` counterpart of the matching `N=15` campaign. It uses the
same 100 deterministic Sobol configurations, `t=1e6`, `hz0=0.1` exactly,
`Jpm=Jy=0` exactly, logarithmic `hz` sampling over `[0.0999,0.1001]`, and
logarithmic `J` sampling over `[1e-3,10]`.

The unscaled coupling obeys
`1e-5 <= Jx <= 0.01*min(J,hz,abs(hz0))`; the backend then applies
`Jx_edge=Jx/sqrt(14)` exactly once.

Submit from the repository root on Zeus:

```bash
bash hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p0999_0p1001_two_order_N14.sh
```

The array indices are `0-3`; each job owns 25 configurations, requests 8 CPUs
and 128 GB, and runs two workers. Results are checkpointed per configuration;
failures are recorded and excluded from success-only aggregation. No virtual
environment is activated.
