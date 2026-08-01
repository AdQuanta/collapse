# Zeus Weak-Disorder Collective Born Search

This handoff tests weakly symmetry-broken detector Hamiltonians while preserving the existing canonical `S_born` metric. It does not submit jobs automatically.

## Submit

Run on Zeus from the repository root:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_weak_disorder_collective"
LOG_ROOT="logs/zeus_born_weak_disorder_collective_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_weak_disorder_collective.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

If the queue is tight, start with the all-to-all tasks:

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_weak_disorder_collective"
LOG_ROOT="logs/zeus_born_weak_disorder_collective_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$RUN_ROOT" "$LOG_ROOT"

qsub -J 1-2 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_born_weak_disorder_collective.pbs | tee "$LOG_ROOT/qsub_jobid.txt"
```

## Tasks

- Task 1: all-to-all near degree-normalized detector, `N=9,10`, weak detector-bond disorder.
- Task 2: focused all-to-all near degree-normalized detector, `N=11,12`.
- Task 3: ring detector with weak detector-bond disorder, `N=11,12`.
- Task 4: chain detector control with weak detector-bond disorder, `N=11,12`.
- Task 5: dimerized detector degeneracy control with weak detector-bond disorder, `N=11,13`.

All tasks keep central couplings perturbative: `Jx_unscaled <= 0.05`, `Jy_unscaled=0`, `Jcpm_unscaled=0`, and `hx=0`.

## Logs

- Scheduler-side logs: `$LOG_ROOT/*.log`
- Per-output logs: `$RUN_ROOT/<run_name>/run.log`
- Job id record: `$LOG_ROOT/qsub_jobid.txt`

## Postprocess After Completion

```bash
cd "$HOME/research/collapse"

RUN_ROOT="figures/zeus_born_weak_disorder_collective"

python3.11 examples/summarize_born_search_results.py \
  --root "$RUN_ROOT" \
  --out-md "$RUN_ROOT/summary.md" \
  --out-csv "$RUN_ROOT/summary_rows.csv" \
  --top 40

python3.11 examples/born_candidate_stability.py \
  --source-csv "$RUN_ROOT/summary_rows.csv" \
  --out-dir "$RUN_ROOT/stability_top24" \
  --mode all \
  --top-rows 24 \
  --min-n 0 \
  --max-n 13 \
  --min-born-similarity -1 \
  --max-atomic-fraction 1 \
  --max-jx-unscaled 0.05 \
  --max-jy-unscaled 0.05 \
  --max-jcpm-unscaled 0.05 \
  --max-hx 0.05 \
  --bins 60 80 120 \
  --tail-fractions 0.05 0.10 0.20 \
  --log-bins 50 \
  --backend auto \
  --top 24 \
  --log-file "$RUN_ROOT/stability_top24/run.log"

python3.11 examples/plot_born_candidate_diagnostics.py \
  --source-csv "$RUN_ROOT/summary_rows.csv" \
  --out-dir "$RUN_ROOT/diagnostics_top24" \
  --mode all \
  --top-rows 24 \
  --min-n 0 \
  --max-n 13 \
  --min-born-similarity -1 \
  --max-atomic-fraction 1 \
  --max-jx-unscaled 0.05 \
  --max-jy-unscaled 0.05 \
  --max-jcpm-unscaled 0.05 \
  --max-hx 0.05 \
  --bins 120 \
  --tail-fraction 0.10 \
  --log-bins 60 \
  --backend auto \
  --pseudocount 0.5 \
  --extra-distribution-plots \
  --log-file "$RUN_ROOT/diagnostics_top24/run.log"
```

## Why N<=12 Here

Weak disorder plus perturbative central XX coupling generally breaks the sector decompositions used for larger clean/symmetry-preserving scans. Use the existing larger-N anisotropic and degenerate-spectrum PBS scripts for `N=15,16` families where symmetry remains exploitable.
