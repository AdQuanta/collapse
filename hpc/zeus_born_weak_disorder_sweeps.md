# Zeus Weak-Disorder Sweep Handoff

This handoff packages weakly disordered detector-family sweeps.  It preserves
`central_coupling`, disorder fields, and the canonical `born_similarity`
(`S_born`) metric in CSV outputs.

PBS script:

```text
hpc/zeus_born_weak_disorder_sweeps.pbs
```

## Submit

Run on Zeus from the repository root:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_weak_disorder_sweeps"
LOG_ROOT="logs/zeus_born_weak_disorder_sweeps_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_weak_disorder_sweeps.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Matched-ring seed subset if the full array is too expensive:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_weak_disorder_sweeps"
LOG_ROOT="logs/zeus_born_weak_disorder_sweeps_matched_ring_seed_$(date +%Y%m%d_%H%M%S)"
PLOT_TOP=16
PLOT_MAX_BLOCH_POINTS=6000

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-3 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",PLOT_TOP="$PLOT_TOP",PLOT_MAX_BLOCH_POINTS="$PLOT_MAX_BLOCH_POINTS" \
  hpc/zeus_born_weak_disorder_sweeps.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

Task map:

| task | output directory |
|---:|:---|
| 1 | `uniform_ring_all_N15_N16` |
| 2 | `gaussian_ring_all_N15_N16` |
| 3 | `uniform_ring_local_N13_N14` |
| 4 | `uniform_chain_geometry_N13_N14` |
| 5 | `uniform_all_to_all_sz_N15_N16` |
| 6 | `uniform_dimerized_N11_N13` |

## Logs

Scheduler logs and output-side `run.log` files include line timestamps in the
form `[YYYY-MM-DDTHH:MM:SS+ZZZZ]`.

Scheduler-side logs:

```text
<LOG_ROOT>/<run_name>.<PBS_JOBID>.<TASK_ID>.log
```

Output-side run logs:

```text
figures/zeus_born_weak_disorder_sweeps/<run_name>/run.log
```

Monitor:

```bash
RUN_ROOT="figures/zeus_born_weak_disorder_sweeps"
LOG_ROOT="logs/zeus_born_weak_disorder_sweeps_<timestamp-used-at-submit>"

qstat -u "$USER"
cat "$LOG_ROOT/qsub_jobid.txt"
find "$LOG_ROOT" -maxdepth 1 -name '*.log' -type f | sort
find "$RUN_ROOT" -mindepth 2 -maxdepth 2 -name run.log -type f | sort
tail -n 80 "$LOG_ROOT"/uniform_ring_all_N15_N16.*.1.log
tail -n 80 "$RUN_ROOT/uniform_ring_all_N15_N16/run.log"
```

## Retrieve

Package on Zeus:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_weak_disorder_sweeps"
LOG_ROOT="logs/zeus_born_weak_disorder_sweeps_<timestamp-used-at-submit>"
PACKAGE_ROOT="zeus_born_weak_disorder_sweeps_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$PACKAGE_ROOT"
cp -a "$RUN_ROOT" "$PACKAGE_ROOT/"
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

rsync -av "$PACKAGE_ROOT/zeus_born_weak_disorder_sweeps/" \
  "figures/zeus_born_weak_disorder_sweeps/"
rsync -av "$PACKAGE_ROOT/scheduler_logs/" \
  "logs/zeus_born_weak_disorder_sweeps_imported/"
```

## Post-Return Commands

```bash
python examples/summarize_born_search_results.py \
  --root figures/zeus_born_weak_disorder_sweeps \
  --out-md figures/zeus_born_weak_disorder_sweeps/summary.local.md \
  --out-csv figures/zeus_born_weak_disorder_sweeps/summary_rows.local.csv \
  --top 40
```
