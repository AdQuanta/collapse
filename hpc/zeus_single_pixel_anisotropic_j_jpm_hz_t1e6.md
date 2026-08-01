# Zeus runbook: anisotropic single-pixel J--Jpm--hz sweep at t=1e6

Run commands from the repository root on Zeus (submission from `hpc/` is also
supported). Codex prepared and locally smoke-tested the files but did not
submit a Zeus job.

## Physics and parameter grid

\[
H=h_z\sum_{i=1}^{N}Z_i+J\sum_{i=1}^{N}Z_iZ_{i+1}
+J_{\pm}\sum_{i=1}^{N}(\sigma_i^+\sigma_{i+1}^-+\mathrm{h.c.})
+\frac{0.01}{\sqrt N}X_0\sum_{i=1}^{N}X_i,
\qquad h_{z0}=0,\quad t=10^6.
\]

The machine-readable grid is
`configs/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json`:

- `N=11,12,13,14,15,16,17,18`;
- `hz=-2.01,-2,-1,-0.1,-0.01,0,0.01,0.1,1,2,2.01`;
- `J=0,0.1,0.25,0.5,0.75,1,1.5,2`;
- `Jpm=0,0.01,0.05,0.1,0.25,0.5,0.75,1,1.5,2`.

There are 880 configurations per N and 7,040 in total.

## Multiprocessing and checkpointing

The PBS array has one task per `N`. Within that task, Python submits the full
Cartesian product of `(hz,J,Jpm)` to a `ProcessPoolExecutor`, so workers
genuinely evaluate different `J,Jpm` pairs concurrently. The memory-aware
defaults are:

| N | process workers | numerical-library threads per worker |
|---:|---:|---:|
| 11--13 | 4 | 2 |
| 14--15 | 2 | 2 |
| 16--18 | 1 | 2 |

Override the process count with `CONFIG_WORKERS`, and the inner BLAS/OpenMP
count with `NUMERIC_THREADS`, only after measuring memory. Each worker emits
timezone-aware START/FINISH log lines containing its process name/number, PID,
parameters, and elapsed times. The parent emits a timestamped CHECKPOINT line
after saving each result.

Every completed configuration is saved immediately as raw NPZ, metadata JSON,
metrics JSON, and a three-row blue/red PNG. The parent is the only writer, so
process completion order cannot corrupt shared state. When all 880 cases for
one N exist, the same job creates all 11 J--Jpm heatmaps, the per-N CSV, and
the per-N manifest before it exits. Thus results and plots are finalized after
each N independently.

## Environment

```bash
python3.11 -m venv .venv-zeus-anisotropic
source .venv-zeus-anisotropic/bin/activate
python -m pip install -r requirements-local-study.txt
```

The PBS scripts require Python 3.11, `quspin==1.0.0`, and
`quspin-extensions==0.1.6`. Their headers use `zeus_new_q`, 8 CPUs, 128 GB,
`#PBS -m abe`, and `matanhaller@campus.technion.ac.il`.

## Dry run and smoke test

```bash
python3.11 examples/run_single_pixel_anisotropic_sweep.py describe
qsub -J 11 -v DRY_RUN=1 hpc/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.pbs
qsub -J 11 -v SMOKE=1,CONFIG_WORKERS=2 hpc/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.pbs
```

The smoke run uses a separate `N=4`, four-configuration J--Jpm, `t=100` grid under
`$RUN_ROOT/smoke/`; it cannot be mistaken for production data. Different
`J,Jpm` configurations are processed concurrently when `CONFIG_WORKERS=2`.

## Recommended staged production

Start with N=11 and inspect the timestamped worker logs, elapsed times, and
peak memory:

```bash
RUN_TAG=$(date +%Y%m%d_%H%M%S)
RUN_ROOT="work/zeus_single_pixel_anisotropic_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_anisotropic_${RUN_TAG}"

qsub -J 11 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",CONFIG_WORKERS=4 \
  hpc/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.pbs
```

Rerun the same command and same `RUN_ROOT` after a wall-time interruption; all
completed configurations are reused. After N=11 succeeds, submit additional
sizes one at a time or as the complete array.

## Full production

```bash
RUN_TAG=$(date +%Y%m%d_%H%M%S)
RUN_ROOT="work/zeus_single_pixel_anisotropic_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_anisotropic_${RUN_TAG}"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.pbs
```

If the environment is not already active:

```bash
qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",VIRTUAL_ENV_PATH="$PWD/.venv-zeus-anisotropic" \
  hpc/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.pbs
```

The separate `..._aggregate.pbs` file remains available for cheap
post-processing reruns, but the production simulation job already aggregates
and plots each N automatically.

## Output layout

```text
$RUN_ROOT/
  raw/Nxx/hz_*/J_*/Jpm_*/spectrum_t1000000.npz
  raw/Nxx/hz_*/J_*/Jpm_*/metadata.json
  metrics/Nxx/hz_*/J_*/Jpm_*/diagnostics.json
  figures/Nxx/hz_*/J_*/Jpm_*/blue_red_t1000000.png
  status/Nxx/DONE.json
  aggregates/Nxx/S_born_hz_*_J_vs_Jpm.png
  aggregates/Nxx/anisotropic_metrics_Nxx.csv
  aggregates/Nxx/manifest.json
```

The per-configuration figure contains blue/red histogram stairs for
`P(theta)` and `P(pi-theta)`, connected occupied-bin `R(theta)` against
`cos^2(theta/2)`, and blue/red antipodal Bloch branches. Heatmaps use a fixed
`RdYlGn` scale from 0 (red) to 1 (green); negative values saturate red and
black circles mark `Jpm=J`. Heatmap cells contain no numeric annotations; exact
values remain available in the per-N CSV.

## Resource warning

The scripts cover every requested N but do not prove that 128 GB is enough.
A full dense `2^N` complex matrix alone would require about 64 GiB at N=16,
256 GiB at N=17, and 1 TiB at N=18. Pixel-shift sectors reduce individual
blocks, but all eigensystems and workspaces remain costly. Keep N=16--18 at
one process unless measured data justify otherwise, and do not infer
feasibility merely from the presence of the array indices.
