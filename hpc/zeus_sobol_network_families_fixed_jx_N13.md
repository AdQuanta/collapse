# Fixed-Jx N=13 network-family campaign

For each of the four detector graph families, this campaign simulates 100
matched Sobol configurations at detector size `N=13` and evolution time
`t=1e6`. The detector Hamiltonian is

```text
H_D = -hz sum_i Z_i
      -J sum_(i,j in E) Z_i Z_j
      -Jpm sum_(i,j in E) (sigma_i^+ sigma_j^- + sigma_i^- sigma_j^+),
```

and the central-qubit interaction is

```text
V = -(0.01/sqrt(13)) X_0 sum_i X_i.
```

Thus the stored unscaled `Jx` is exactly 0.01 and the Hamiltonian receives
`Jx_effective=0.01/sqrt(13)`. Here `hz0=0` and `Jy=0`. The Sobol coordinates are
`(J,Jpm,hz)`, each log-mapped to `[1,100]`, so
`Jx/min(J,Jpm,hz) <= 1e-2` for every configuration. The same 100 Hamiltonian
parameter triples are used for every family.

The graph is regenerated deterministically for every configuration. Fixed
family hyperparameters are `p=0.3` for Erdos-Renyi, `k=4,p=0.3` for
Watts-Strogatz, `m=2` for Barabasi-Albert, and `d=4` for random regular.

Submit with:

```bash
bash hpc/submit_zeus_sobol_network_families_fixed_jx_N13.sh
```

The default 16-element PBS array has four batches of 25 configurations for
each of the four families. Every configuration is checkpointed independently,
and rerunning against the same `RUN_ROOT` resumes completed configurations.
Each array element uses one in-process simulation worker with eight numerical
library threads. This avoids the POSIX semaphore required by Python process
pools, which is not consistently available on Zeus compute nodes. Matplotlib
font-manager warnings are suppressed in the runner.
