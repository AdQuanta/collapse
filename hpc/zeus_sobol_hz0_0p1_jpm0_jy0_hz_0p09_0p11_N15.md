# Zeus Sobol scan: hz in [0.09,0.11], hz0=0.1, Jpm=0, Jy=0, N=15

From the repository root on a Zeus login node, run:

```bash
bash hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p09_0p11_N15.sh
```

This submits one PBS array with indices `0-3`. The campaign contains exactly
100 configurations from one reproducible scrambled Sobol sequence, partitioned
as follows:

- index 0: `config_000`--`config_024`;
- index 1: `config_025`--`config_049`;
- index 2: `config_050`--`config_074`;
- index 3: `config_075`--`config_099`.

The production runner hard-codes all fixed quantities and exposes no override
for them:

- `hz0=0.1` exactly;
- `Jpm=0` exactly;
- `Jy=0` exactly;
- `hz` is sampled logarithmically in `[0.09,0.11]`;
- `N=15` and `t=1e6`.

Only `J`, `hz`, and `Jx` are sampled. `J` uses the logarithmic interval
`[1e-3,10]`, while `hz` uses `[0.09,0.11]`. `Jx` is sampled conditionally so that

```text
Jx <= 0.1 min(J,hz,abs(hz0)).
```

The effective Hamiltonian coefficient is `Jx/sqrt(N)`, applied exactly once.
Each subjob requests 8 CPUs and 128 GB and runs two configuration workers with
four numerical-library threads per worker.

Every successful configuration immediately saves numerical results, metrics,
WG/WC fits, validation, the standard blue-red/Bloch diagnostic, fit diagnostics,
an execution log, and a checksummed `COMPLETE.json`. Failures remain non-fatal
and are excluded from the final success-only aggregation.

To choose the output directory:

```bash
export RUN_ROOT="$PWD/work/my_jpm0_jy0_hz_near_hz0_scan"
bash hpc/submit_zeus_sobol_hz0_0p1_jpm0_jy0_hz_0p09_0p11_N15.sh
```
