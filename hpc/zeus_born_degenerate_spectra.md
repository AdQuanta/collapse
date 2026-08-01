# Zeus Degenerate-Spectrum Hamiltonian Handoff

This handoff adds Hamiltonian candidates whose detector eigenenergies are
exactly or nearly degenerate.  The purpose is to test whether degeneracies can
produce both:

$$
P(\theta)\ \mathrm{heavy\ tailed}
$$

and

$$
R(\theta)=\frac{P(\theta)}{P(\theta)+P(\pi-\theta)}
\approx \cos^2(\theta/2),
$$

without merely creating atomic histogram artifacts.

## Submit

Run on Zeus from the repository root:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_degenerate_spectra"
LOG_ROOT="logs/zeus_born_degenerate_spectra_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_degenerate_spectra.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Task map:

| task | output directory | degeneracy mechanism |
|---:|:---|:---|
| 1 | `flat_detector_exact_degenerate_ring_N13_N14` | `J=0`, `hz=0` flat detector spectrum with weak central coupling |
| 2 | `flat_detector_weak_field_lift_ring_N13_N14` | weak local-field lift of the flat detector spectrum |
| 3 | `dimerized_zz_degenerate_N11_N13` | independent ZZ dimers with combinatorial multiplets |
| 4 | `dimerized_flat_lift_N11_N13` | dimerized model at `J=0` plus weak perturbative lifts |
| 5 | `all_to_all_sz_degenerate_exchange_N15_N16` | all-to-all conserved-`S_z` detector with large permutation multiplets |
| 6 | `cnot_copier_atomic_degenerate_N8_N10_N12` | exact atomic/gate copier baseline |

Tasks 1 through 4 sweep:

```text
central_coupling = all, first, ends
```

Task 5 sweeps:

```text
central_coupling = all, first
```

Perturbative central detector couplings:

```text
abs(Jx_unscaled) <= 0.04
abs(Jcpm_unscaled) <= 0.05
hx = 0
```

The search script records these additional columns in `results.csv`:

```text
energy_degenerate_fraction
energy_degenerate_cluster_fraction
energy_max_multiplicity
energy_resolved_level_count
energy_mean_spacing_ratio
energy_min_spacing
```

The result CSV also includes:

```text
radius_atomic_fraction
radius_unique_count
reciprocity_error
tail_density_exponent
born_similarity
```

## Logs

Scheduler logs and output-side `run.log` files include line timestamps in the
form `[YYYY-MM-DDTHH:MM:SS+ZZZZ]`.

Scheduler-side logs:

```text
<LOG_ROOT>/<run_name>.<PBS_JOBID>.<TASK_ID>.log
```

Per-output progress logs:

```text
figures/zeus_born_degenerate_spectra/<run_name>/run.log
```

Monitor:

```bash
qstat -u "$USER"
cat "$LOG_ROOT/qsub_jobid.txt"
tail -n 80 "$LOG_ROOT"/flat_detector_exact_degenerate_ring_N13_N14.*.1.log
tail -n 80 "$RUN_ROOT/flat_detector_exact_degenerate_ring_N13_N14/run.log"
tail -n 80 "$LOG_ROOT"/dimerized_zz_degenerate_N11_N13.*.3.log
tail -n 80 "$RUN_ROOT/dimerized_zz_degenerate_N11_N13/run.log"
```

If the full array is too expensive, start with tasks 1, 3, and 6:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_degenerate_spectra"
LOG_ROOT="logs/zeus_born_degenerate_spectra_seed_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1,3,6 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_degenerate_spectra.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Optional Postprocess on Zeus

The scan PBS script already writes simulation-time diagnostic figures under
`<RUN_ROOT>/<run_name>/diagnostics/`.  The postprocess blocks below are optional
summary/stability follow-ups, not a dependency for the campaign diagnostics.

After the scan array finishes and at least one task directory contains
`results.csv`, submit postprocess task 1 to build `summary_rows.csv`:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_degenerate_spectra"
LOG_ROOT="logs/zeus_born_degenerate_spectra_postprocess_$(date +%Y%m%d_%H%M%S)"
SUMMARY_CSV="$RUN_ROOT/summary_rows.csv"

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",SUMMARY_CSV="$SUMMARY_CSV" \
  hpc/zeus_born_degenerate_spectra_postprocess.pbs | tee "$LOG_ROOT/qsub_summary_jobid.txt"
```

After task 1 finishes and `summary_rows.csv` exists, submit tasks 2-3:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_degenerate_spectra"
LOG_ROOT="logs/zeus_born_degenerate_spectra_postprocess_<timestamp-used-for-summary>"
SUMMARY_CSV="$RUN_ROOT/summary_rows.csv"

test -s "$SUMMARY_CSV"

qsub -J 2-3 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",SUMMARY_CSV="$SUMMARY_CSV" \
  hpc/zeus_born_degenerate_spectra_postprocess.pbs | tee "$LOG_ROOT/qsub_metric_diagnostics_jobid.txt"
```

Postprocess task map:

| task | output directory | purpose |
|---:|:---|:---|
| 1 | `summary_degenerate` | write `summary.md` and `summary_rows.csv` |
| 2 | `metric_stability_degenerate` | recompute metrics across bin/tail settings |
| 3 | `diagnostics_degenerate` | create compact and six-panel distribution plots |

Postprocess scheduler-side logs:

```text
<LOG_ROOT>/summary_degenerate.<PBS_JOBID>.1.log
<LOG_ROOT>/metric_stability_degenerate.<PBS_JOBID>.2.log
<LOG_ROOT>/diagnostics_degenerate.<PBS_JOBID>.3.log
```

Postprocess output-side logs:

```text
figures/zeus_born_degenerate_spectra/summary_degenerate/run.log
figures/zeus_born_degenerate_spectra/metric_stability_degenerate/run.log
figures/zeus_born_degenerate_spectra/diagnostics_degenerate/run.log
```

## Retrieve

Package on Zeus after the scan and postprocess jobs finish:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_degenerate_spectra"
LOG_ROOT="logs/zeus_born_degenerate_spectra_<timestamp-used-at-submit>"
POSTPROCESS_LOG_ROOT="logs/zeus_born_degenerate_spectra_postprocess_<timestamp-used-at-submit>"
PACKAGE_ROOT="zeus_born_degenerate_spectra_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$PACKAGE_ROOT"
cp -a "$RUN_ROOT" "$PACKAGE_ROOT/"
cp -a "$LOG_ROOT" "$PACKAGE_ROOT/scheduler_logs"
cp -a "$POSTPROCESS_LOG_ROOT" "$PACKAGE_ROOT/postprocess_scheduler_logs"

find "$PACKAGE_ROOT" -type f -print0 | sort -z | xargs -0 sha256sum > "$PACKAGE_ROOT/SHA256SUMS.txt"
tar -czf "$PACKAGE_ROOT.tar.gz" "$PACKAGE_ROOT"
sha256sum "$PACKAGE_ROOT.tar.gz" > "$PACKAGE_ROOT.tar.gz.sha256"

echo "$PACKAGE_ROOT.tar.gz"
echo "$PACKAGE_ROOT.tar.gz.sha256"
```

Retrieve from the local machine after replacing `<zeus-login>`:

```bash
LOCAL_ROOT="/path/to/local/collapse"
REMOTE_ROOT="~/research/collapse"
PACKAGE_ROOT="<package-name-printed-on-zeus>"

rsync -avP "<zeus-login>:$REMOTE_ROOT/$PACKAGE_ROOT.tar.gz" "$LOCAL_ROOT/"
rsync -avP "<zeus-login>:$REMOTE_ROOT/$PACKAGE_ROOT.tar.gz.sha256" "$LOCAL_ROOT/"

cd "$LOCAL_ROOT"
sha256sum -c "$PACKAGE_ROOT.tar.gz.sha256"
tar -xzf "$PACKAGE_ROOT.tar.gz"

rsync -av "$PACKAGE_ROOT/zeus_born_degenerate_spectra/" \
  "figures/zeus_born_degenerate_spectra/"
rsync -av "$PACKAGE_ROOT/scheduler_logs/" \
  "logs/zeus_born_degenerate_spectra_imported/"
rsync -av "$PACKAGE_ROOT/postprocess_scheduler_logs/" \
  "logs/zeus_born_degenerate_spectra_postprocess_imported/"
```

## Post-Return Commands

After import, regenerate the local summary index if desired:

```bash
python examples/summarize_born_search_results.py \
  --root figures/zeus_born_degenerate_spectra \
  --out-md figures/zeus_born_degenerate_spectra/summary.local.md \
  --out-csv figures/zeus_born_degenerate_spectra/summary_rows.local.csv \
  --top 30
```
