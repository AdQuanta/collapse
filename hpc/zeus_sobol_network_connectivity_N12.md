# Non-circular single-pixel Sobol campaigns

The four campaigns sample `(J, hz, Jpm, Jx)` with the established conditional
weak-coupling constraint, `hz0=Jy=0`, a central qubit coupled to every detector
qubit, and one deterministic graph realization per Sobol configuration.

Defaults are 400 configurations, four shards of 100, and detector size `N=12`.
The Python runners expose `--detector-n`, `--count`, and `--batch-size`; the
submission wrappers expose the matching `DETECTOR_N`, `COUNT`, and `BATCH_SIZE`
environment variables and override the PBS array range accordingly.

## Why N=12 rather than N=14

Non-circular graphs do not generally admit the ring's pixel-shift sectors. They
do retain exact total-magnetization parity because every enabled off-diagonal
term flips an even number of spins. The implementation diagonalizes the two
parity blocks and reconstructs the exact full relative-evolution blocks. On the
local four-thread BLAS path, measured diagonalization plus relative-evolution
times were:

| detector N | total Hilbert dimension | elapsed time |
|---:|---:|---:|
| 10 | 2,048 | 33.95 s |
| 11 | 4,096 | 100.65 s |

Conservative cubic extrapolation projects approximately 13.4 minutes per N=12
configuration, about 11.2 hours for 100 configurations on two concurrent
workers before fitting and plotting overhead. N=13 projects to roughly 89
worker-pair hours per shard, beyond the 72-hour allocation, and N=14 is plainly
unsuitable without another symmetry or iterative reformulation. N=12 is
therefore the largest reasonable default; a pilot should still precede all four
production arrays.

Planning estimates for N=12 are below 12 GB peak memory per worker (dense parity
blocks, projected eigenvectors, and the full relative-evolution work arrays),
so two workers retain a wide margin inside the requested 128 GB node. Output is
expected to remain below roughly 2 GB per 400-case campaign: the small-system
smoke result was 0.55 MB/configuration, while the compressed spectral arrays
grow to 4,096 detector eigenvalues at N=12. These are estimates, not Zeus
measurements; the pilot should confirm peak RSS, wall time, and output volume.

## Submission

```bash
bash hpc/submit_zeus_sobol_erdos_renyi_hz0_0.sh
bash hpc/submit_zeus_sobol_watts_strogatz_hz0_0.sh
bash hpc/submit_zeus_sobol_barabasi_albert_hz0_0.sh
bash hpc/submit_zeus_sobol_expander_hz0_0.sh
```

Example small pilot with a fixed graph realization:

```bash
DETECTOR_N=9 COUNT=8 BATCH_SIZE=4 RUN_ROOT=work/network_pilot \
  bash hpc/submit_zeus_sobol_expander_hz0_0.sh
```

For a fixed graph across all configurations, invoke the Python runner directly
with `--no-graph-per-configuration` (or change the corresponding PBS common
argument). Graph family parameters are `ERDOS_RENYI_P`, `WATTS_STROGATZ_K`,
`WATTS_STROGATZ_P`, `BARABASI_ALBERT_M`, and `REGULAR_DEGREE`.
