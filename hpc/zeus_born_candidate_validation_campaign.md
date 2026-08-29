# Zeus Born Candidate-Validation Campaign Handoff

Manual handoff only.  Do not SSH from Codex, do not submit jobs from Codex, and
do not handle credentials.  Run the blocks below manually on Zeus from the
repository root.

All PBS scripts in this campaign call `scripts/born_hamiltonian_search.py`
directly and enable simulation-time diagnostics through:

```text
--plot-top "$PLOT_TOP"
--plot-max-bloch-points "$PLOT_MAX_BLOCH_POINTS"
```

No separate plotting or postprocessing PBS job is required for the diagnostic
figures requested here.

Current simulation-time diagnostic figures contain one theta-angle histogram
panel, showing `P(theta)` together with `P(pi-theta)`, plus `R(theta)` vs Born,
radius/tail diagnostics, the full qubit-detector Hamiltonian spectrum, and the
Bloch-sphere initial-state distribution.

## Full PBS Scripts

```text
hpc/zeus_born_matched_weak_disorder_validation.pbs
hpc/zeus_born_anisotropic_largerN.pbs
hpc/zeus_born_connectivity_coupling_sweeps.pbs
hpc/zeus_born_degenerate_spectra.pbs
```

Each script writes:

```text
Scheduler log:
<LOG_ROOT>/<run_name>.<PBS_JOBID>.<TASK_ID>.log

Output progress log:
<RUN_ROOT>/<run_name>/run.log

Results:
<RUN_ROOT>/<run_name>/results.csv
<RUN_ROOT>/<run_name>/results.json
<RUN_ROOT>/<run_name>/top_candidates.md

Simulation-time diagnostics:
<RUN_ROOT>/<run_name>/diagnostics/index.md
<RUN_ROOT>/<run_name>/diagnostics/*.png
```

The default diagnostics settings are:

```text
PLOT_TOP=12
PLOT_MAX_BLOCH_POINTS=6000
```

Increase `PLOT_TOP` only if the extra figure generation cost is acceptable.

## 1. Matched Weak-Disorder Ring Validation

PBS script:

```text
hpc/zeus_born_matched_weak_disorder_validation.pbs
```

Primary finite-size seed subset:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_matched_weak_disorder_validation"
LOG_ROOT="logs/zeus_born_matched_weak_disorder_validation_seed_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-3 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_matched_weak_disorder_validation.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Full validation array:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_matched_weak_disorder_validation"
LOG_ROOT="logs/zeus_born_matched_weak_disorder_validation_full_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-9 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_matched_weak_disorder_validation.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Task map:

| task | scheduler run name | output run directories |
|---:|:---|:---|
| 1 | `uniform_matched_ring_all_N12_N13_seed44` | same |
| 2 | `uniform_matched_ring_all_N14_seed44` | same |
| 3 | `uniform_matched_ring_all_N15_N16_seed44` | same |
| 4 | `uniform_matched_ring_seed_sweep_N10_N12` | umbrella `uniform_matched_ring_seed_sweep_N10_N12/run.log`, plus `uniform_matched_ring_seed_11_N10_N12`, `uniform_matched_ring_seed_44_N10_N12`, `uniform_matched_ring_seed_73_N10_N12`, `uniform_matched_ring_seed_101_N10_N12` |
| 5 | `gaussian_matched_ring_all_N12_N14_seed44` | same |
| 6 | `clean_matched_ring_all_N12_N14_seed44` | same |
| 7 | `uniform_ring_central_coupling_controls_N12_N14_seed44` | same |
| 8 | `uniform_chain_controls_N12_N14_seed44` | same |
| 9 | `uniform_anisotropic_ring_all_N12_N14_seed44` | same |

## 2. Anisotropic XX/YY/ZZ and Larger N

PBS script:

```text
hpc/zeus_born_anisotropic_largerN.pbs
```

Full array:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_largerN_full_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-9 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_anisotropic_largerN.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Fast primary subset:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_largerN_seed_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-5,8-9 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_anisotropic_largerN.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Task map:

| task | output directory |
|---:|:---|
| 1 | `ring_baseline_matched_N15_N16` |
| 2 | `ring_anisotropic_xx_yy_N15_N16` |
| 3 | `ring_weak_zz_anisotropic_N15_N16` |
| 4 | `ring_strong_zz_anisotropic_N15_N16` |
| 5 | `ring_central_coupling_channels_N15_N16` |
| 6 | `chain_sz_conserving_N13_N14` |
| 7 | `chain_transverse_perturbative_N13_N14` |
| 8 | `all_to_all_sz_conserving_N15_N16` |
| 9 | `ring_detuned_controls_N15_N16` |

## 3. Detector Connectivity and Central-Coupling Geometry

PBS script:

```text
hpc/zeus_born_connectivity_coupling_sweeps.pbs
```

Full array:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_connectivity_coupling_sweeps"
LOG_ROOT="logs/zeus_born_connectivity_coupling_sweeps_full_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-7 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_connectivity_coupling_sweeps.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Representative seed subset:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_connectivity_coupling_sweeps"
LOG_ROOT="logs/zeus_born_connectivity_coupling_sweeps_seed_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1,3,5,6 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_connectivity_coupling_sweeps.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Task map:

| task | output directory |
|---:|:---|
| 1 | `ring_all_anisotropic_N15_N16` |
| 2 | `ring_local_geometry_N13_N14` |
| 3 | `chain_geometry_N13_N14` |
| 4 | `chain_sz_conserving_geometry_N13_N14` |
| 5 | `all_to_all_geometry_N15_N16` |
| 6 | `dimerized_geometry_N11_N13` |
| 7 | `ring_all_beyond_N17_probe` |

## 4. Degenerate-Spectrum Candidates and Controls

PBS script:

```text
hpc/zeus_born_degenerate_spectra.pbs
```

Focused seed subset:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_degenerate_spectra"
LOG_ROOT="logs/zeus_born_degenerate_spectra_seed_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1,3,6 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_degenerate_spectra.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Full array:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_degenerate_spectra"
LOG_ROOT="logs/zeus_born_degenerate_spectra_full_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-6 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_degenerate_spectra.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Task map:

| task | output directory |
|---:|:---|
| 1 | `flat_detector_exact_degenerate_ring_N13_N14` |
| 2 | `flat_detector_weak_field_lift_ring_N13_N14` |
| 3 | `dimerized_zz_degenerate_N11_N13` |
| 4 | `dimerized_flat_lift_N11_N13` |
| 5 | `all_to_all_sz_degenerate_exchange_N15_N16` |
| 6 | `cnot_copier_atomic_degenerate_N8_N10_N12` |

## Monitor and Check

Use the same `RUN_ROOT` and `LOG_ROOT` values used at submission:

```bash
qstat -u "$USER"
cat "$LOG_ROOT/qsub_jobid.txt"
find "$LOG_ROOT" -maxdepth 1 -name '*.log' -type f | sort
find "$RUN_ROOT" -mindepth 2 -maxdepth 2 -name run.log -type f | sort
find "$RUN_ROOT" -mindepth 2 -maxdepth 2 -name results.csv -type f | sort
find "$RUN_ROOT" -mindepth 3 -maxdepth 3 -name index.md -path '*/diagnostics/index.md' -type f | sort
```

Tail a scheduler log and matching output log:

```bash
tail -n 80 "$LOG_ROOT"/<run_name>.*.<TASK_ID>.log
tail -n 80 "$RUN_ROOT/<run_name>/run.log"
```

## Retrieval Package

Run on Zeus after the selected array completes:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="<run-root-used-at-submit>"
LOG_ROOT="<log-root-used-at-submit>"
PACKAGE_ROOT="$(basename "$RUN_ROOT")_return_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$PACKAGE_ROOT"
cp -a "$RUN_ROOT" "$PACKAGE_ROOT/run_outputs"
cp -a "$LOG_ROOT" "$PACKAGE_ROOT/scheduler_logs"

find "$PACKAGE_ROOT" -type f -print0 | sort -z | xargs -0 sha256sum > "$PACKAGE_ROOT/SHA256SUMS.txt"
tar -czf "$PACKAGE_ROOT.tar.gz" "$PACKAGE_ROOT"
sha256sum "$PACKAGE_ROOT.tar.gz" > "$PACKAGE_ROOT.tar.gz.sha256"

echo "$PACKAGE_ROOT.tar.gz"
echo "$PACKAGE_ROOT.tar.gz.sha256"
```

Retrieve locally after replacing `<zeus-login>`:

```bash
LOCAL_ROOT="/path/to/local/collapse"
REMOTE_ROOT="~/research/collapse"
PACKAGE_ROOT="<package-name-printed-on-zeus>"

rsync -avP "<zeus-login>:$REMOTE_ROOT/$PACKAGE_ROOT.tar.gz" "$LOCAL_ROOT/"
rsync -avP "<zeus-login>:$REMOTE_ROOT/$PACKAGE_ROOT.tar.gz.sha256" "$LOCAL_ROOT/"

cd "$LOCAL_ROOT"
sha256sum -c "$PACKAGE_ROOT.tar.gz.sha256"
tar -xzf "$PACKAGE_ROOT.tar.gz"
```

## Cluster-Safety Caveats

- The commands assume the Zeus checkout lives at `$HOME/research/collapse`.
- Set `ZEUS_ENV_SETUP`, `PYTHON_MODULES`, `VIRTUAL_ENV_PATH`, or `PYTHON_BIN`
  in the `qsub -v` list if Zeus requires a non-default Python environment.
- Do not run the N17 probe until the N15/N16 ring/all-to-all outputs and logs
  look healthy.
- Chain validations are kept at N=13/14 in this campaign.
- The simulation-time diagnostics add plotting work.  Use lower `PLOT_TOP`
  values for queue triage and higher values only after candidate stability is
  clear.
