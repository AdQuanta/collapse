# Zeus handoff: finite-time weak-kernel diagnostics

Date: 2026-06-20

This handoff tests the analytic explanation of the slide-8 `hz0=0` result:
the candidate may be a dressed zero-frequency response of the detector, but the
decisive object is the finite-time weak-coupling kernel

$$
K_t(A,D,B)_{\nu\mu}
=
\langle \nu,D|B|\mu,A\rangle F_t(d_\nu-a_\mu),
$$

and its radius density \(q(x)\), not only the scalar near-zero spectral weight
in \(\rho_B(\omega)\).

The run computes:

$$
x_j = |\lambda_j(K_t)|,
\qquad
\theta_j=2\tan^{-1}x_j,
\qquad
R(\theta)=\frac{P(\theta)}{P(\theta)+P(\pi-\theta)}.
$$

It compares \(R(\theta)\) with

$$
R_{\mathrm{Born}}(\theta)=\cos^2(\theta/2),
$$

using the same current `S_born` metric as the rest of the project.

## Script

PBS script:

```bash
hpc/zeus_detector_weak_kernel_diagnostics.pbs
```

The script is a PBS array with tasks `1-8`.  Each task writes:

- scheduler-side log: `${LOG_ROOT}/${RUN_NAME}.${PBS_JOBID}.${TASK_ID}.log`
- diagnostic log: `${RUN_ROOT}/${RUN_NAME}/run.log`
- spectral table: `${RUN_ROOT}/${RUN_NAME}/spectral_response_summary.csv`
- exact \(M(t)\) table: `${RUN_ROOT}/${RUN_NAME}/m_diagnostics_summary.csv`
- weak-kernel table: `${RUN_ROOT}/${RUN_NAME}/weak_kernel_diagnostics_summary.csv`
- summary page: `${RUN_ROOT}/${RUN_NAME}/summary.md`
- figures:
  `${RUN_ROOT}/${RUN_NAME}/*_spectral_response.png` and
  `${RUN_ROOT}/${RUN_NAME}/*_weak_kernel_t*.png`

Every run logs progress with timestamps.

## Task map

| Task | Run name | Purpose |
| ---: | --- | --- |
| 1 | `ring_all_N10_reference` | reproduce local N10 reference with weak \(K_t\) and exact \(M(t)\) |
| 2 | `ring_all_N11_scaling` | first scaling step |
| 3 | `ring_all_N12_scaling` | main dense diagnostic target |
| 4 | `ring_all_N13_dense_limit` | largest recommended dense run |
| 5 | `ring_all_N12_anisotropic_weak` | weak \(J_{xx}\ne J_{yy}\) dressing control |
| 6 | `ring_first_N12_coupling_control` | sparse central-coupling control |
| 7 | `ring_ends_N12_coupling_control` | boundary-like central-coupling control |
| 8 | `chain_all_N12_geometry_control` | chain geometry with all-site central coupling |

## Important limit

Do not use this dense script for the N16 slide-8 row.  It constructs dense
central-qubit blocks, so an N16 run would require dense matrices at full
dimension \(2^{16}\), which is not the right use of Zeus.

For the symmetric clean ring/all-site slide-8 family, use the sector-aware
handoff instead:

```bash
hpc/zeus_sector_weak_kernel_slide8.pbs
hpc/zeus_sector_weak_kernel_slide8.md
```

The exact N15/N16 \(M(t)\) simulations should continue using
`examples/born_hamiltonian_search.py` with QuSpin sectors.

## Recommended manual submission

Run the reference and N11/N12 scaling first:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_detector_weak_kernel_diagnostics"
LOG_ROOT="logs/zeus_detector_weak_kernel_diagnostics_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-3 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_detector_weak_kernel_diagnostics.pbs \
  | tee "$LOG_ROOT/qsub_reference_scaling_jobid.txt"
```

Then run the dense-limit and controls:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_detector_weak_kernel_diagnostics"
LOG_ROOT="logs/zeus_detector_weak_kernel_diagnostics_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 4-8 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_detector_weak_kernel_diagnostics.pbs \
  | tee "$LOG_ROOT/qsub_dense_controls_jobid.txt"
```

If the queue is quiet and you want all tasks at once:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_detector_weak_kernel_diagnostics"
LOG_ROOT="logs/zeus_detector_weak_kernel_diagnostics_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_detector_weak_kernel_diagnostics.pbs \
  | tee "$LOG_ROOT/qsub_all_jobid.txt"
```

## Monitoring

Replace `<JOBID>` with the identifier written by `qsub`.

```bash
qstat -t <JOBID>
tail -f "$LOG_ROOT"/*.log
```

Inspect a completed task with:

```bash
RUN_ROOT="figures/zeus_detector_weak_kernel_diagnostics"
RUN_NAME="ring_all_N12_scaling"

ls "$RUN_ROOT/$RUN_NAME"
tail -n 80 "$RUN_ROOT/$RUN_NAME/run.log"
head -n 20 "$RUN_ROOT/$RUN_NAME/weak_kernel_diagnostics_summary.csv"
```

## Expected decision rule

Promote the `hz0=0`, ZZ+\(J_{\pm}\) mechanism only if the weak-kernel density
develops the same reciprocal-core structure as the exact \(M(t)\) diagnostic:

$$
q(1/x)\simeq x^4q(x).
$$

If exact \(M(t)\) looks Born-like while \(K_t\) does not, the mechanism is not
captured by first order at those long times, and the next analytic target should
be a resummed or sector-aware finite-coupling treatment.
