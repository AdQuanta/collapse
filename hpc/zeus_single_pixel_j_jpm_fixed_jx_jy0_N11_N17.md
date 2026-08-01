# Zeus Handoff: Single-Pixel J-Jpm Scan With Fixed Weak XX Coupling And Jy=0

Date: 2026-07-03

## Purpose

This is the `Jy=0` companion to `zeus_single_pixel_j_jpm_fixed_jxjy_N11_N17.pbs`.

It runs the single-pixel ring Hamiltonian with weak central-qubit detector coupling

$$
J_x=10^{-2},
\qquad
J_y=0,
$$

and scans the detector \(J\)-\(J_{\pm}\) plane for \(N=11,\ldots,17\). The run uses QuSpin and enforces the existing cyclic detector-site shift sector path through clean `ring` connectivity and uniform `all` central coupling.

## Simulated Hamiltonian

For detector sites \(i=1,\ldots,N\) with periodic boundary conditions \(N+1\equiv1\),

$$
H_D
=
J\sum_i Z_iZ_{i+1}
+
J_{\pm}\sum_i\left(S_i^+S_{i+1}^-+S_i^-S_{i+1}^+\right)
+
h_z\sum_iZ_i.
$$

The central qubit has

$$
H_0=h_{z0}Z_0,
$$

with both branches

$$
h_{z0}=0
\qquad\text{and}\qquad
h_{z0}=h_z.
$$

The weak central coupling is

$$
H_{\rm int}
=
J_x^{\rm phys}X_0\sum_iX_i,
\qquad
J_y^{\rm phys}=0.
$$

The PBS defaults set

$$
J_x^{\rm unscaled}=10^{-2},
\qquad
J_y^{\rm unscaled}=0.
$$

The code convention is

$$
J_x^{\rm phys}=J_x^{\rm unscaled}/\sqrt{N}.
$$

## Default Grid

The PBS script defaults to the same 11x11 detector grid as the `Jx=Jy` companion:

```bash
J_VALUES="0 0.1 0.2 0.3 0.5 0.75 1.0 1.25 1.5 2.0 3.0"
JPM_VALUES="0 0.01 0.02 0.03 0.05 0.075 0.1 0.15 0.2 0.3 0.5"
TIMES="100 316.227766 1000 3162.27766 10000 100000 1000000"
```

Each task writes:

- heatmaps of \(S_{\rm born}\) in the \(J\)-\(J_{\pm}\) plane for every requested time;
- `pairwise_summary.csv`;
- `results.json`;
- `index.md`;
- top-row diagnostic plots under `diagnostics/`, including \(P(\theta)\), \(P(\pi-\theta)\), \(R(\theta)\) versus \(\cos^2(\theta/2)\), \(\phi\) histogram, Bloch-sphere distribution, spectra, and level-spacing diagnostics.

## PBS Script

Use:

```bash
hpc/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17.pbs
```

The array has 14 tasks:

| array id | \(N\) | \(h_{z0}\) |
| ---: | ---: | --- |
| 1 | 11 | 0 |
| 2 | 11 | \(h_z\) |
| 3 | 12 | 0 |
| 4 | 12 | \(h_z\) |
| 5 | 13 | 0 |
| 6 | 13 | \(h_z\) |
| 7 | 14 | 0 |
| 8 | 14 | \(h_z\) |
| 9 | 15 | 0 |
| 10 | 15 | \(h_z\) |
| 11 | 16 | 0 |
| 12 | 16 | \(h_z\) |
| 13 | 17 | 0 |
| 14 | 17 | \(h_z\) |

## Pilot Command

Paste this on Zeus from the repository root:

```bash
cd "$HOME/research/collapse"
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17_pilot_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17_pilot_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",EXPECTED_SYMMETRY=pixel_shift,BORN_WORKERS=4,PLOT_TOP=8 \
  hpc/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17.pbs \
  | tee "$LOG_ROOT/qsub_jobid.txt"
```

Inspect:

```bash
tail -f "$LOG_ROOT/N11_hz0-zero/run.log"
```

## Full Command

After the pilot completes and `index.md` plus diagnostic plots look healthy:

```bash
cd "$HOME/research/collapse"
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-14 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",EXPECTED_SYMMETRY=pixel_shift \
  hpc/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17.pbs \
  | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Optional Narrower Pilot

For a faster syntax/data-path test:

```bash
cd "$HOME/research/collapse"
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17_tiny_pilot_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17_tiny_pilot_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",EXPECTED_SYMMETRY=pixel_shift,BORN_WORKERS=2,PLOT_TOP=4,J_VALUES="0.5 1.0 1.5",JPM_VALUES="0 0.05 0.1",TIMES="100 1000" \
  hpc/zeus_single_pixel_j_jpm_fixed_jx_jy0_N11_N17.pbs \
  | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Logs And Checkpoints

For each task:

- scheduler context: `${LOG_ROOT}/N##_hz0-*/scheduler_context.log`
- live run log: `${LOG_ROOT}/N##_hz0-*/run.log`
- completion marker: `${RUN_ROOT}/N##_hz0-*/CHECKPOINT_DONE.txt`
- summary table: `${RUN_ROOT}/N##_hz0-*/pairwise_summary.csv`
- diagnostic plots: `${RUN_ROOT}/N##_hz0-*/diagnostics/`

The script sets `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, and `NUMEXPR_NUM_THREADS` to 1 by default. It uses multiprocessing across independent grid jobs through `BORN_WORKERS`. Defaults are:

- \(N=11,12,13\): 4 workers;
- \(N=14,15\): 2 workers;
- \(N=16,17\): 1 worker to reduce RAM pressure.
