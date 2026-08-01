# Zeus Matched-Counterpart Falsifier Handoff

This handoff resolves the current `off_resonance_falsifier_challenge` in
`figures/zeus_born_anisotropic_largerN` by running exact `hz0=matched`
counterparts for the high-scoring detuned-control rows.

The source queue is:

```text
figures/zeus_born_anisotropic_largerN/matched_counterpart_requests.csv
```

It currently contains the missing same-parameter matched rows identified by:

```bash
python examples/compare_born_falsifier_challenges.py \
  --root figures/zeus_born_anisotropic_largerN
```

## Submit

Run on Zeus from the repository root:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_anisotropic_largerN"
REQUEST_CSV="$RUN_ROOT/matched_counterpart_requests.csv"
LOG_ROOT="logs/zeus_born_matched_counterparts_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$RUN_ROOT" "$LOG_ROOT"
test -s "$REQUEST_CSV"

qsub -v RUN_ROOT="$RUN_ROOT",REQUEST_CSV="$REQUEST_CSV",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_matched_counterparts.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Task map:

| task | output directory | purpose |
|---:|:---|:---|
| 1 | `metric_stability_matched_counterparts_N15_N16` | recompute matched-counterpart metrics across bin/tail settings |
| 2 | `diagnostics_matched_counterparts_N15_N16` | create compact and six-panel distribution plots |

The request rows are not already scored, so the PBS script intentionally passes:

```text
--min-born-similarity -1
--max-atomic-fraction 1
```

This prevents the normal postprocess filters from discarding the queue before
the matched counterparts are evaluated.

## Logs

Scheduler logs and output-side `run.log` files include line timestamps in the
form `[YYYY-MM-DDTHH:MM:SS+ZZZZ]`.

Scheduler-side logs:

```text
<LOG_ROOT>/metric_stability_matched_counterparts_N15_N16.<PBS_JOBID>.1.log
<LOG_ROOT>/diagnostics_matched_counterparts_N15_N16.<PBS_JOBID>.2.log
```

Per-output progress logs:

```text
figures/zeus_born_anisotropic_largerN/metric_stability_matched_counterparts_N15_N16/run.log
figures/zeus_born_anisotropic_largerN/diagnostics_matched_counterparts_N15_N16/run.log
```

Monitor:

```bash
qstat -u "$USER"
cat "$LOG_ROOT/qsub_jobid.txt"
tail -n 80 "$LOG_ROOT"/metric_stability_matched_counterparts_N15_N16.*.1.log
tail -n 80 "$RUN_ROOT/metric_stability_matched_counterparts_N15_N16/run.log"
tail -n 80 "$LOG_ROOT"/diagnostics_matched_counterparts_N15_N16.*.2.log
tail -n 80 "$RUN_ROOT/diagnostics_matched_counterparts_N15_N16/run.log"
```

## Retrieve

After completion, package the outputs on Zeus:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_anisotropic_largerN"
LOG_ROOT="logs/zeus_born_matched_counterparts_<timestamp-used-at-submit>"
PACKAGE_ROOT="zeus_born_matched_counterparts_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$PACKAGE_ROOT"
cp -a "$RUN_ROOT/matched_counterpart_requests.csv" "$PACKAGE_ROOT/"
cp -a "$RUN_ROOT/metric_stability_matched_counterparts_N15_N16" "$PACKAGE_ROOT/"
cp -a "$RUN_ROOT/diagnostics_matched_counterparts_N15_N16" "$PACKAGE_ROOT/"
cp -a "$LOG_ROOT" "$PACKAGE_ROOT/scheduler_logs"

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

rsync -av "$PACKAGE_ROOT/matched_counterpart_requests.csv" \
  "figures/zeus_born_anisotropic_largerN/matched_counterpart_requests.csv"
rsync -av "$PACKAGE_ROOT/metric_stability_matched_counterparts_N15_N16/" \
  "figures/zeus_born_anisotropic_largerN/metric_stability_matched_counterparts_N15_N16/"
rsync -av "$PACKAGE_ROOT/diagnostics_matched_counterparts_N15_N16/" \
  "figures/zeus_born_anisotropic_largerN/diagnostics_matched_counterparts_N15_N16/"
rsync -av "$PACKAGE_ROOT/scheduler_logs/" \
  "logs/zeus_born_matched_counterparts_imported/"
```

## Post-Return Audit

After importing the package under `figures/zeus_born_anisotropic_largerN`, run
the audit command with the returned matched-counterpart stability table:

```bash
python examples/compare_born_falsifier_challenges.py \
  --root figures/zeus_born_anisotropic_largerN \
  --extra-primary-csv figures/zeus_born_anisotropic_largerN/metric_stability_matched_counterparts_N15_N16/stability_summary.csv \
  > figures/zeus_born_anisotropic_largerN/falsifier_challenge_after_matched_counterparts.md
```

Post-return output:

```text
figures/zeus_born_anisotropic_largerN/falsifier_challenge_after_matched_counterparts.md
```
