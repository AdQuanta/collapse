# Zeus Anisotropic Larger-N Born Search

This handoff covers the perturbative larger-N scan requested for anisotropic
`XX`, `YY`, and `ZZ` weights, central coupling channels, and detector
connectivity controls.

Born-ratio target:

$$
R(\theta)=\frac{P(\theta)}{P(\theta)+P(\pi-\theta)}
\approx \cos^2(\theta/2).
$$

Heavy-tail target:

$$
q(x)\sim x^{-p},\qquad x=|\lambda|=\tan(\theta/2),\qquad p\simeq 2.
$$

## 1. Submit the scan

PBS script:

```bash
hpc/zeus_born_anisotropic_largerN.pbs
```

Submit command with simulation-time diagnostic figures:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_largerN_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_anisotropic_largerN.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

For a faster primary subset, skip only the transverse-chain branch.  Use this
command instead of the full `#PBS -J 1-9` array; do not edit the PBS file:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_largerN_$(date +%Y%m%d_%H%M%S)_skip_task7"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-6,8-9 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_anisotropic_largerN.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Outputs:

```text
figures/zeus_born_anisotropic_largerN/<run_name>/results.csv
figures/zeus_born_anisotropic_largerN/<run_name>/results.json
figures/zeus_born_anisotropic_largerN/<run_name>/top_candidates.md
figures/zeus_born_anisotropic_largerN/<run_name>/run.log
```

Scheduler-side logs:

```text
<LOG_ROOT>/<run_name>.<PBS_JOBID>.<TASK_ID>.log
```

Task map:

| task | run | purpose |
|---:|:---|:---|
| 1 | `ring_baseline_matched_N15_N16` | matched ring baseline with perturbative `Jx` |
| 2 | `ring_anisotropic_xx_yy_N15_N16` | independent bath `Jxx`/`Jyy` weights |
| 3 | `ring_weak_zz_anisotropic_N15_N16` | weaker ZZ scale, `J=0.75` |
| 4 | `ring_strong_zz_anisotropic_N15_N16` | stronger ZZ scale, `J=1.25` |
| 5 | `ring_central_coupling_channels_N15_N16` | perturbative `Jy`, `Jz`, `Jzx`, and `Jcpm` |
| 6 | `chain_sz_conserving_N13_N14` | reduced-N chain control that preserves magnetization sectors |
| 7 | `chain_transverse_perturbative_N13_N14` | reduced-N transverse-chain control |
| 8 | `all_to_all_sz_conserving_N15_N16` | all-to-all Sz-conserving connectivity control |
| 9 | `ring_detuned_controls_N15_N16` | detuned `hz0` falsifier controls |

The transverse-chain control intentionally remains at `N=13,14`. Without
translation or magnetization sectors, an `N=15` transverse-chain run requires
the full dense/QZ path and does not fit the validated 96 GB workflow with left
eigenvector diagnostics enabled. This makes the chain comparison a
reduced-size control; do not present it as a same-size comparison with the
primary `N=15,16` ring families. Legacy `chain_transverse_perturbative_N15`
rows remain readable by the summary tooling but are not scheduled here.

### 1a. Rerun task 6 at reduced chain size

Current priority: replace the incomplete `chain_sz_conserving_N15_N16` branch
with the less demanding `chain_sz_conserving_N13_N14` task 6, while preserving
the partial `N15/N16` log already imported under
`figures/zeus_born_anisotropic_largerN`.

Run this from a Zeus login shell after the repository code is up to date:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_anisotropic_largerN"
OLD_TASK6_DIR="$RUN_ROOT/chain_sz_conserving_N15_N16"
TASK6_DIR="$RUN_ROOT/chain_sz_conserving_N13_N14"
LOG_ROOT="logs/zeus_born_anisotropic_largerN_chain_task6_$(date +%Y%m%d_%H%M%S)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OLD_LOG_BACKUP="$OLD_TASK6_DIR/_manual_backup_before_N13_N14_task6_$STAMP"

mkdir -p "$RUN_ROOT" "$TASK6_DIR" "$LOG_ROOT"

if [ -f "$OLD_TASK6_DIR/run.log" ]; then
  mkdir -p "$OLD_LOG_BACKUP"
  cp -p "$OLD_TASK6_DIR/run.log" "$OLD_LOG_BACKUP/run.log.partial_N15_N16"
  sha256sum "$OLD_LOG_BACKUP/run.log.partial_N15_N16" | tee "$OLD_LOG_BACKUP/SHA256SUMS.txt"
fi

PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

qsub -J 6 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",BACKUP_EXISTING_OUTPUTS=1,PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_anisotropic_largerN.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "qsub job id: $LOG_ROOT/qsub_jobid.txt"
echo "scheduler log: $LOG_ROOT/chain_sz_conserving_N13_N14.<PBS_JOBID>.6.log"
echo "new run log: $TASK6_DIR/run.log"
echo "old N15/N16 log backup: $OLD_LOG_BACKUP"
echo "job-start backup, if old files existed: $TASK6_DIR/_rerun_backup_<YYYYMMDD_HHMMSS>/"
```

Expected task-6 outputs after completion:

```text
figures/zeus_born_anisotropic_largerN/chain_sz_conserving_N13_N14/results.csv
figures/zeus_born_anisotropic_largerN/chain_sz_conserving_N13_N14/results.json
figures/zeus_born_anisotropic_largerN/chain_sz_conserving_N13_N14/top_candidates.md
figures/zeus_born_anisotropic_largerN/chain_sz_conserving_N13_N14/run.log
```

## 2. Submit the postprocess

Run this only after the scan outputs are present.

PBS script:

```bash
hpc/zeus_born_anisotropic_postprocess.pbs
```

Submit command:

```bash
cd "$HOME/research/collapse"
RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_postprocess_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_anisotropic_postprocess.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Outputs:

```text
figures/zeus_born_anisotropic_largerN/summary.md
figures/zeus_born_anisotropic_largerN/summary_rows.csv
figures/zeus_born_anisotropic_largerN/shortlist.md
figures/zeus_born_anisotropic_largerN/shortlist_primary_n15_n16.csv
figures/zeus_born_anisotropic_largerN/shortlist_primary_n15_n16_rows.csv
figures/zeus_born_anisotropic_largerN/resonance_audit.md
figures/zeus_born_anisotropic_largerN/metric_stability_primary_N15_N16/
figures/zeus_born_anisotropic_largerN/metric_stability_controls_N13_N16/
figures/zeus_born_anisotropic_largerN/diagnostics_primary_N15_N16/
figures/zeus_born_anisotropic_largerN/diagnostics_controls_N13_N16/
```

Scheduler-side logs:

```text
<LOG_ROOT>/<run_name>.<PBS_JOBID>.<TASK_ID>.log
```

Postprocess task map:

| task | run | purpose |
|---:|:---|:---|
| 1 | `summary_shortlist_audit` | combine CSVs, shortlist N15/N16 candidates, audit resonance labels |
| 2 | `metric_stability_primary_N15_N16` | recompute primary metrics across bins/tail fractions |
| 3 | `metric_stability_controls_N13_N16` | recompute control metrics across bins/tail fractions |
| 4 | `diagnostics_primary_N15_N16` | compact and six-panel distribution plots for primary rows |
| 5 | `diagnostics_controls_N13_N16` | compact and six-panel distribution plots for controls |

## Notes

- All central detector couplings in this handoff are kept perturbative:
  `Jx_unscaled`, `Jy_unscaled`, `Jcpm_unscaled`, and `hx` are at or below
  `0.05` in the search and postprocess filters.
- N16 transverse chain is intentionally not included, because without
  translation or magnetization sectors it becomes a full dense diagonalization.
- The postprocess diagnostics use `--extra-distribution-plots`, so every plotted
  row gets both the compact diagnostic figure and a six-panel distribution pack.

## 3. Monitor, checksum, and retrieve

After submitting task 6, monitor it from Zeus:

```bash
RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_largerN_chain_task6_<timestamp-used-at-submit>"

qstat -u "$USER"
cat "$LOG_ROOT/qsub_jobid.txt"
tail -n 80 "$LOG_ROOT"/chain_sz_conserving_N13_N14.*.6.log
tail -n 80 "$RUN_ROOT/chain_sz_conserving_N13_N14/run.log"
```

Before retrieving, create checksums and a compact archive on Zeus:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_largerN_chain_task6_<timestamp-used-at-submit>"
TASK6_DIR="$RUN_ROOT/chain_sz_conserving_N13_N14"
PACKAGE_ROOT="zeus_born_anisotropic_largerN_task6_package_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$PACKAGE_ROOT"
cp -a "$TASK6_DIR" "$PACKAGE_ROOT/"
cp -a "$LOG_ROOT" "$PACKAGE_ROOT/scheduler_logs_task6"

find "$PACKAGE_ROOT" -type f -print0 | sort -z | xargs -0 sha256sum > "$PACKAGE_ROOT/SHA256SUMS.txt"
tar -czf "$PACKAGE_ROOT.tar.gz" "$PACKAGE_ROOT"
sha256sum "$PACKAGE_ROOT.tar.gz" > "$PACKAGE_ROOT.tar.gz.sha256"

echo "$PACKAGE_ROOT.tar.gz"
echo "$PACKAGE_ROOT.tar.gz.sha256"
```

Retrieve from the local machine after replacing `<zeus-login>` with the Zeus
login target:

```bash
LOCAL_ROOT="/path/to/local/collapse"
REMOTE_ROOT="~/research/collapse"
PACKAGE_ROOT="<package-name-printed-on-zeus>"

rsync -avP "<zeus-login>:$REMOTE_ROOT/$PACKAGE_ROOT.tar.gz" "$LOCAL_ROOT/"
rsync -avP "<zeus-login>:$REMOTE_ROOT/$PACKAGE_ROOT.tar.gz.sha256" "$LOCAL_ROOT/"

cd "$LOCAL_ROOT"
sha256sum -c "$PACKAGE_ROOT.tar.gz.sha256"
tar -xzf "$PACKAGE_ROOT.tar.gz"
rsync -av "$PACKAGE_ROOT/chain_sz_conserving_N13_N14/" \
  "figures/zeus_born_anisotropic_largerN/chain_sz_conserving_N13_N14/"
rsync -av "$PACKAGE_ROOT/scheduler_logs_task6/" \
  "logs/zeus_born_anisotropic_largerN_chain_task6_imported/"
```

After retrieval and only after
`figures/zeus_born_anisotropic_largerN/chain_sz_conserving_N13_N14/results.csv`
exists, submit the postprocess job from Zeus:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_anisotropic_postprocess_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_anisotropic_postprocess.pbs | tee "$LOG_ROOT/qsub_jobid.txt"

echo "qsub job id: $LOG_ROOT/qsub_jobid.txt"
echo "scheduler logs: $LOG_ROOT/<run_name>.<PBS_JOBID>.<TASK_ID>.log"
echo "postprocess run logs: $RUN_ROOT/<postprocess_run>/run.log"
```
