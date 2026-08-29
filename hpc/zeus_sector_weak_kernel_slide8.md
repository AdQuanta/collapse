# Zeus handoff: sector weak-kernel diagnostic for the slide-8 `hz0=0` family

Date: 2026-06-20

This handoff tests the current analytic explanation of the slide-8 N16 row:
`hz0=0`, detector ZZ plus \(J_{\pm}\), weak all-site central \(J_x\), and a
Born-like ratio.  The script diagonalizes the first-order weak kernel

$$
K_t(A,D,B)_{\nu\mu}
=
\langle \nu,D|B|\mu,A\rangle F_t(d_\nu-a_\mu)
$$

in detector magnetization and ring-momentum sectors.  This avoids the dense
\(2^{16}\)-dimensional block construction and is appropriate for the clean,
ring, all-site, \(S_z\)-conserving detector family.

## Supported Hamiltonian family

The script covers:

```text
model = single_pixel
connectivity = ring
central_coupling = all
disorder = none
Jz = Jzx = Jxx = Jyy = Jy = Jcpm = hx = 0
detector terms = ZZ J + exchange Jpm + detector hz
central flip = weak Jx / sqrt(N-1)
```

The detector Hamiltonian is

$$
H_B
=
-J\sum_{\langle i,j\rangle}Z_iZ_j
-J_{\pm}\sum_{\langle i,j\rangle}
\left(\sigma_i^+\sigma_j^-+\sigma_i^-\sigma_j^+\right)
-h_z\sum_iZ_i.
$$

For `hz0=0`, \(A=D=H_B\), and the selected frequency is

$$
\Delta=E_\nu-E_\mu.
$$

The test is whether the weak-kernel radius density satisfies

$$
q(1/x)\simeq x^4q(x),
$$

which is the condition behind the Born-like ratio

$$
R(\theta)\simeq\cos^2(\theta/2).
$$

## Script

PBS script:

```bash
hpc/zeus_sector_weak_kernel_slide8.pbs
```

Python script:

```bash
scripts/sector_weak_kernel_diagnostics.py
```

Each task writes:

- scheduler-side log: `${LOG_ROOT}/${RUN_NAME}.${PBS_JOBID}.${TASK_ID}.log`
- diagnostic log: `${RUN_ROOT}/${RUN_NAME}/run.log`
- summary table: `${RUN_ROOT}/${RUN_NAME}/sector_weak_kernel_summary.csv`
- momentum-block table: `${RUN_ROOT}/${RUN_NAME}/sector_weak_kernel_blocks.csv`
- summary page: `${RUN_ROOT}/${RUN_NAME}/summary.md`
- figures: `${RUN_ROOT}/${RUN_NAME}/*_sector_weak_kernel_t*.png`

Every run logs progress with timestamps.

## Task map

| Task | Run name | Purpose |
| ---: | --- | --- |
| 1 | `N14_reference_all_controls` | medium-size reference; all `hz0={zero,matched}` and `Jpm={0,0.05}` controls |
| 2 | `N15_slide8_all_controls` | N15 precursor to the slide-8 family |
| 3 | `N16_slide8_all_controls` | direct N16 control set matching the slide-8 parameters |
| 4 | `N16_slide8_zero_Jpm_time_sweep` | `hz0=zero`, `Jpm=0.05`, \(t=316,1000,3162,10000\) |
| 5 | `N16_zero_Jpm_Jx_sweep` | `hz0=zero`, `Jpm=0.05`, \(J_x^{\rm unscaled}=0.03,0.04,0.05\) |
| 6 | `N16_zero_Jpm_hz_sweep` | `hz0=zero`, `Jpm=0.05`, \(h_z=0.08,0.10,0.12\) |

## Recommended manual submission

Local validation after the momentum-block projection optimization gives the
following scale:

| N | max momentum block | local wall time for one `hz0=zero,Jpm=0.05,t=1000` row | \(S_{\mathrm{born}}\) |
| ---: | ---: | ---: | ---: |
| 12 | 188 | 18.5 s | 0.292 |
| 14 | 632 | 103 s | 0.719 |

The N15/N16 runs should still go to Zeus because the largest momentum blocks
grow rapidly, but the N14 trend is encouraging: the first-order weak kernel is
already moving toward the Born-like slide-8 behavior.

Run the direct control set first:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_sector_weak_kernel_slide8"
LOG_ROOT="logs/zeus_sector_weak_kernel_slide8_$(date +%Y%m%d_%H%M%S)"
BORN_WORKERS=2
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-3 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_sector_weak_kernel_slide8.pbs \
  | tee "$LOG_ROOT/qsub_direct_controls_jobid.txt"
```

Then run the N16 parameter sweeps:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_sector_weak_kernel_slide8"
LOG_ROOT="logs/zeus_sector_weak_kernel_slide8_$(date +%Y%m%d_%H%M%S)"
BORN_WORKERS=2
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 4-6 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_sector_weak_kernel_slide8.pbs \
  | tee "$LOG_ROOT/qsub_N16_sweeps_jobid.txt"
```

If queue pressure is low, still avoid launching the full array with too many
worker processes per task.  Use:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_sector_weak_kernel_slide8"
LOG_ROOT="logs/zeus_sector_weak_kernel_slide8_$(date +%Y%m%d_%H%M%S)"
BORN_WORKERS=2
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",BORN_WORKERS="$BORN_WORKERS" \
  hpc/zeus_sector_weak_kernel_slide8.pbs \
  | tee "$LOG_ROOT/qsub_all_jobid.txt"
```

For a scheduler/memory pilot before the full N16 rows:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_sector_weak_kernel_slide8_pilot"
LOG_ROOT="logs/zeus_sector_weak_kernel_slide8_pilot_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",BORN_WORKERS=1 \
  hpc/zeus_sector_weak_kernel_slide8.pbs \
  | tee "$LOG_ROOT/qsub_pilot_jobid.txt"
```

## Monitoring

Replace `<JOBID>` with the identifier written by `qsub`.

```bash
qstat -t <JOBID>
tail -f "$LOG_ROOT"/*.log
```

Inspect a completed task:

```bash
RUN_ROOT="figures/zeus_sector_weak_kernel_slide8"
RUN_NAME="N16_slide8_all_controls"

ls "$RUN_ROOT/$RUN_NAME"
tail -n 80 "$RUN_ROOT/$RUN_NAME/run.log"
head -n 20 "$RUN_ROOT/$RUN_NAME/sector_weak_kernel_summary.csv"
```

## Post-processing after results are available

After Zeus tasks finish and the result folders are available in the workspace,
combine the sector summaries and generate overview plots with:

```bash
cd "$HOME/research/collapse"
mkdir -p figures/zeus_sector_weak_kernel_slide8_summary
python scripts/summarize_sector_weak_kernel_results.py \
  figures/zeus_sector_weak_kernel_slide8 \
  --out-dir figures/zeus_sector_weak_kernel_slide8_summary \
  | tee figures/zeus_sector_weak_kernel_slide8_summary/postprocess.log
```

If you also want to compare the Zeus rows against the local N10/N12/N14 probes:

```bash
cd "$HOME/research/collapse"
mkdir -p figures/sector_weak_kernel_summary_with_zeus_2026-06-20
python scripts/summarize_sector_weak_kernel_results.py \
  figures/sector_weak_kernel_compare_N10_2026-06-20 \
  figures/sector_weak_kernel_scaling_probe_N12_2026-06-20 \
  figures/sector_weak_kernel_scaling_probe_N14_2026-06-20 \
  figures/zeus_sector_weak_kernel_slide8 \
  --out-dir figures/sector_weak_kernel_summary_with_zeus_2026-06-20 \
  | tee figures/sector_weak_kernel_summary_with_zeus_2026-06-20/postprocess.log
```

The summarizer writes:

- `sector_weak_kernel_combined.csv`
- `summary.md`
- `born_similarity_vs_N.png`
- `reciprocity_error_vs_N.png`
- `radius_q99_over_q50_vs_N.png`
- `max_momentum_block_dimension_vs_N.png`
- `born_similarity_vs_tail_spread.png`

## Interpretation

If the N16 `hz0=zero, Jpm=0.05` weak-kernel row is Born-like and has a good
reciprocal-core score, the slide-8 behavior is explained already at first
order in the perturbative central coupling.

If exact \(M(t)\) remains Born-like but this weak-kernel diagnostic does not,
the next analytic target is a resummed or finite-coupling treatment of
\(M(t)=U_{00}^{-1}U_{10}\), because first order is not enough at the simulated
times.
