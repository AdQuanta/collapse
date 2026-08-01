# Zeus handoff: matched weak-disorder validation

Date: 2026-06-20

This handoff validates the current strongest perturbative candidate family:
small qubit-detector coupling on a matched single-pixel ring with weak detector
bond disorder. It also runs decisive controls for clean rings, local/ends
coupling, chains, and anisotropic XX/YY/ZZ variants.

## Hamiltonian being validated

For the central qubit `0` and detector/pixel spins `i=1,...,N-1`, the base
single-pixel family is

$$
H =
H_{\mathrm{det}}
+ h_{z0}\sigma_0^z
+ \sum_i J_x^{(i)}\sigma_0^x\sigma_i^x
+ \sum_i J_y^{(i)}\sigma_0^y\sigma_i^y
+ \sum_i J_{zx}^{(i)}\sigma_0^z\sigma_i^x
+ \sum_i J_{cpm}^{(i)}(\sigma_0^+\sigma_i^-+\sigma_0^-\sigma_i^+),
$$

with detector terms

$$
H_{\mathrm{det}} =
\sum_{\langle i,j\rangle}
\left[
J_{ij}\sigma_i^z\sigma_j^z
+J_{\pm,ij}(\sigma_i^+\sigma_j^-+\sigma_i^-\sigma_j^+)
+J_{xx,ij}\sigma_i^x\sigma_j^x
+J_{yy,ij}\sigma_i^y\sigma_j^y
+J_{z,ij}\sigma_i^z\sigma_j^z
\right]
+ h_z\sum_i\sigma_i^z .
$$

The perturbative normalization used by the search is

$$
J_x^{(i)} = \frac{J_{x,\mathrm{unscaled}}}{\sqrt{N-1}},
\qquad
J_y^{(i)} = \frac{J_{y,\mathrm{unscaled}}}{\sqrt{N-1}},
\qquad
J_{cpm}^{(i)} = \frac{J_{cpm,\mathrm{unscaled}}}{\sqrt{N-1}} .
$$

Candidate rows are evaluated by diagonalizing

$$
M(t)=U_{00}(t)^{-1}U_{10}(t),
$$

then computing eigenvalue radii `r`, angles

$$
\theta = 2\tan^{-1} r,
\qquad
R(\theta)=\frac{P(\theta)}{P(\theta)+P(\pi-\theta)} ,
$$

and comparing `R(theta)` with

$$
R_{\mathrm{Born}}(\theta)=\cos^2(\theta/2).
$$

The current `S_born` metric is retained for consistency with previous reports.

## Script

PBS script:

```bash
hpc/zeus_born_matched_weak_disorder_validation.pbs
```

It is a PBS array with tasks `1-9`. Each task writes:

- scheduler-side log: `${LOG_ROOT}/${RUN_NAME}.${PBS_JOBID}.${TASK_ID}.log`
- simulation log: `${RUN_ROOT}/${run_name}/run.log`
- numerical tables: `${RUN_ROOT}/${run_name}/results.csv`, `results.json`,
  `top_candidates.md`
- simulation-time diagnostic plots:
  `${RUN_ROOT}/${run_name}/diagnostics/*.png`
- diagnostic index:
  `${RUN_ROOT}/${run_name}/diagnostics/index.md`

The simulator now generates the requested plots directly during the run:
`P(theta)` with `P(pi-theta)`, `R(theta)` against the Born profile, radius/tail
diagnostics, the full qubit-detector Hamiltonian spectrum, and initial-state
distribution on the Bloch sphere.  The theta-angle distribution is shown only
once, in the `P(theta)`/`P(pi-theta)` panel.

## Task map

| Task | Run name | Purpose |
| ---: | --- | --- |
| 1 | `uniform_matched_ring_all_N12_N13_seed44` | scale weak-disordered matched ring beyond local N=10 |
| 2 | `uniform_matched_ring_all_N14_seed44` | intermediate-size validation |
| 3 | `uniform_matched_ring_all_N15_N16_seed44` | larger-N validation target |
| 4 | `uniform_matched_ring_seed_sweep_N10_N12` | seed robustness |
| 5 | `gaussian_matched_ring_all_N12_N14_seed44` | disorder-law robustness |
| 6 | `clean_matched_ring_all_N12_N14_seed44` | no-disorder control |
| 7 | `uniform_ring_central_coupling_controls_N12_N14_seed44` | local/ends coupling controls |
| 8 | `uniform_chain_controls_N12_N14_seed44` | chain geometry controls |
| 9 | `uniform_anisotropic_ring_all_N12_N14_seed44` | anisotropic XX/YY/ZZ follow-up |

## Recommended manual submission

Run this first: it covers the main candidate, scaling, seed stability, and
Gaussian-disorder robustness.

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_matched_weak_disorder_validation"
LOG_ROOT="logs/zeus_born_matched_weak_disorder_validation_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-5 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP=12,PLOT_MAX_BLOCH_POINTS=6000 \
  hpc/zeus_born_matched_weak_disorder_validation.pbs \
  | tee "$LOG_ROOT/qsub_primary_jobid.txt"
```

Then run the controls:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_matched_weak_disorder_validation"
LOG_ROOT="logs/zeus_born_matched_weak_disorder_validation_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 6-9 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP=12,PLOT_MAX_BLOCH_POINTS=6000 \
  hpc/zeus_born_matched_weak_disorder_validation.pbs \
  | tee "$LOG_ROOT/qsub_controls_jobid.txt"
```

If Zeus queue pressure is low and you want the whole campaign at once:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_matched_weak_disorder_validation"
LOG_ROOT="logs/zeus_born_matched_weak_disorder_validation_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP=12,PLOT_MAX_BLOCH_POINTS=6000 \
  hpc/zeus_born_matched_weak_disorder_validation.pbs \
  | tee "$LOG_ROOT/qsub_all_jobid.txt"
```

## Monitoring

Replace `<JOBID>` with the identifier written by `qsub`.

```bash
qstat -t <JOBID>
tail -f "$LOG_ROOT"/*.log
tail -f "$RUN_ROOT"/*/run.log
```

After completion, a quick result inventory should show which tasks produced
tables and diagnostics:

```bash
find "$RUN_ROOT" -maxdepth 2 -name results.csv -print
find "$RUN_ROOT" -maxdepth 3 -path '*/diagnostics/*.png' -print | head -50
find "$RUN_ROOT" -maxdepth 3 -name index.md -path '*/diagnostics/*' -print
```

## Retrieval hint

After Zeus finishes, copy back the whole result root and the corresponding log
root. The useful directories are:

```bash
figures/zeus_born_matched_weak_disorder_validation
logs/zeus_born_matched_weak_disorder_validation_*
```

No SSH credentials or cluster submission are handled by Codex in this workflow;
these commands are intended for manual submission by the user.
