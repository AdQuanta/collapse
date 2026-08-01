# Zeus Handoff: Single-Pixel ZZ + Jpm Detector, Jx x Jpm Heatmaps

Date: 2026-07-01

## Purpose

Run the requested heavy scan:

$$
H_D
=
J\sum_{\langle i,j\rangle}Z_iZ_j
+
J_{\pm}\sum_{\langle i,j\rangle}(S_i^+S_j^-+S_i^-S_j^+)
+
h_z\sum_i Z_i,
$$

with

$$
J=1,
\qquad
H_{\rm int}=J_x X_0\sum_i X_i,
$$

for `single_pixel`, ring nearest-neighbor detector connectivity, central qubit
coupled to all detector qubits, \(h_{z0}=0\) and \(h_{z0}=h_z\), and
\(N=11,\ldots,17\).

Each PBS array task runs one checkpoint:

```text
(N, hz0_mode) in {11..17} x {zero, matched}
```

so completed \(N\) values leave usable results even if later larger-\(N\)
tasks fail or time out.

## Files

- PBS script: `hpc/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17.pbs`
- Result root default:
  `figures/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_<timestamp>/`
- Log root default:
  `logs/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_<timestamp>/`

Each task writes:

- `N##_hz0-zero/index.md` or `N##_hz0-matched/index.md`
- `pairwise_summary.csv`
- `results.json`
- `run.log`
- `heatmap_t*_Jx_unscaled_vs_Jpm.png`
- `diagnostics/*_born_diagnostics.png`
- `CHECKPOINT_DONE.txt`

The diagnostic figures include:

- \(P(\theta)\) and \(P(\pi-\theta)\) histograms in one panel.
- \(R(\theta)\) compared with \(\cos^2(\theta/2)\).
- Radius/tail diagnostics.
- \(\phi\)-angle distribution.
- Bloch-sphere qubit-state distribution.
- Full qubit-detector spectrum.
- Detector-only spectrum.
- Full/detector unfolded level-spacing histograms when resolvable.

## Symmetry Used

The relevant older `sp_ring_*` scripts use
`SinglePixelHamiltonianQuSpin(..., connectivity="ring", use_symmetry=True)`
followed by `ham.diagonalize_sectors()` and
`DisentanglementAnalyzer.from_sectors()`.

For this requested scan, the central interaction is

$$
H_{\rm int}
=
J_x X_0\sum_i X_i,
\qquad
J_x \ne 0
$$

on every grid row.  This XX term does **not** conserve total magnetization
(`Nup`, or total \(S_z\)).  The usable symmetry is therefore the cyclic
detector-site shift symmetry of the clean ring:

$$
i \mapsto i+1 \pmod {N_{\rm pixel}},
$$

with the central qubit fixed.  In the QuSpin implementation this is the
`kblock=(T_pixel, k)`/`pixel_shift` sector path.

Practical consequences:

- `CONNECTIVITY=ring` and `CENTRAL_COUPLING=all` are intentional and now
  enforced by the PBS script.
- `BACKEND=quspin` is enforced so the run uses the sector-aware
  `analysis.py` infrastructure.
- Magnetization sectors are available only in the special \(J_x=0\) or
  otherwise \(S_z\)-conserving limits.  The current sweep starts at nonzero
  perturbative `Jx`, so it should be treated as pixel-shift-only.
- Changing to `CONNECTIVITY=chain`, local central coupling, or disorder would
  remove this ring momentum symmetry and should be done only as a much smaller
  control run.

## Default Sweep

The PBS defaults are:

```bash
J=1.0
HZ=0.1
CONNECTIVITY=ring
CENTRAL_COUPLING=all
BACKEND=quspin
EXPECTED_SYMMETRY=pixel_shift

JX_VALUES="0.0025 0.005 0.0075 0.01 0.015 0.02 0.03 0.04 0.05 0.07 0.1"
JPM_VALUES="0 0.01 0.02 0.03 0.04 0.05 0.06 0.08 0.1 0.15 0.2"
TIMES="100 316.227766 1000 3162.27766 10000 100000 1000000"
```

These are unscaled \(J_x\) values.  The Python code uses the existing project
convention and scales the physical coupling as \(J_x/\sqrt{N_{\rm pixel}}\).

The heatmap colormap is `RdYlGn` with fixed \(S_{\rm born}=0\) red and
\(S_{\rm born}=1\) green.

## Multiprocessing And Memory

The PBS script parallelizes independent grid points inside each array task via
`--workers`.

Defaults:

```bash
BORN_WORKERS_LOW=4     # N=11,12,13
BORN_WORKERS_MID=2     # N=14,15
BORN_WORKERS_HIGH=1    # N=16,17
```

It also sets:

```bash
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
```

This avoids BLAS oversubscription.  For N16/N17, raising workers can be faster
but may overcommit memory because every worker performs independent
diagonalizations.

## Pilot Submission

Run one small pilot first, e.g. \(N=11,h_{z0}=0\):

```bash
cd "$HOME/research/collapse"
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_pilot_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_pilot_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",BORN_WORKERS=4 \
  hpc/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17.pbs \
  | tee "$LOG_ROOT/qsub_jobid.txt"
```

Check:

```bash
tail -f "$LOG_ROOT/N11_hz0-zero/run.log"
```

Expected successful checkpoint:

```text
$RUN_ROOT/N11_hz0-zero/CHECKPOINT_DONE.txt
```

## Full Submission

After the pilot is clean:

```bash
cd "$HOME/research/collapse"
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-14 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17.pbs \
  | tee "$LOG_ROOT/qsub_jobid.txt"
```

If the cluster is busy or memory pressure is expected, throttle the array:

```bash
qsub -J 1-14%2 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17.pbs \
  | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Optional Smaller Pilot Grid

For a faster functional check, override the grids:

```bash
cd "$HOME/research/collapse"
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="figures/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_smallpilot_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_smallpilot_${RUN_TAG}"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",JX_VALUES="0.005 0.02 0.05",JPM_VALUES="0 0.05 0.1",TIMES="100 1000",PLOT_TOP=3,BORN_WORKERS=2 \
  hpc/zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17.pbs \
  | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Retrieval Checklist

After completion, retrieve both roots:

```bash
tar -czf zeus_single_pixel_zz_jpm_jx_heatmaps_N11_N17_results.tgz \
  "$RUN_ROOT" "$LOG_ROOT"
```

Then import the archive into the workspace under `figures/` and `logs/`, or
copy the directories directly.

Minimum files to check before analysis:

```bash
find "$RUN_ROOT" -name CHECKPOINT_DONE.txt -print
find "$RUN_ROOT" -name pairwise_summary.csv -print
find "$RUN_ROOT" -name 'heatmap_t*_Jx_unscaled_vs_Jpm.png' -print
find "$LOG_ROOT" -name run.log -print
```

## Notes

- The requested N17 jobs are heavy even with translation symmetry.  The ring
  all-coupled geometry is intentional because it preserves pixel-shift symmetry
  in the current QuSpin infrastructure.
- Changing `CONNECTIVITY=chain` will likely remove that symmetry and is not
  recommended for N15/N16/N17 unless the grid is reduced.
- The PBS script exits if `CONNECTIVITY`, `CENTRAL_COUPLING`, or `BACKEND` are
  overridden in a way that would bypass the intended sector calculation.  Use
  `ALLOW_NO_SHIFT_SYMMETRY=1` only for deliberately smaller controls.
- No SSH, upload, or qsub action was performed by Codex.
