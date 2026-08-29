# Zeus runbook: relative \(h_z,J,J_\pm\) regimes

This campaign compares 30 explicit cases for
\(N=13,\ldots,18\), with

\[
h_{z0}=0,\qquad J_x=0.01,\qquad
g_{\rm edge}=\frac{0.01}{\sqrt N},\qquad t=10^6.
\]

Exact zeros are permitted as limiting controls. Every nonzero
\(|h_z|,J,J_\pm\) is at least \(10J_x\), enforced when the JSON configuration
is loaded. Every ordinary `>>` hierarchy step is also at least \(10{:}1\).
The exact relations \(h_z=2J\) and \(J_\pm=2J\) are separate
resonance/symmetry controls and are not interpreted as hierarchy steps.

The core is exhaustive in the relative magnitudes
\((|h_z|,J,J_\pm)\): all 13 positive weak orderings, all nine cases with
exactly one zero and two positive scales, the three single-nonzero limits, and
the all-zero limit. Four additional points check field sign, common absolute
scale, the Ising-resonance surface, and the SU(2) line. The exact list and
physical descriptions are in
`configs/zeus_relative_scale_regimes_N13_N18.json`.

## Inspect or smoke-test

Run from the repository root. The scripts use Zeus `python3.11` directly and
do not activate a virtual environment.

```bash
cd "$HOME/research/collapse"

python3.11 scripts/run_relative_scale_regime_campaign.py \
  --config configs/zeus_relative_scale_regimes_N13_N18.json \
  describe

qsub -J 13 \
  -v DRY_RUN=1 \
  hpc/zeus_relative_scale_regimes_N13_N18.pbs

qsub -J 13 \
  -v SMOKE=1,CONFIG_WORKERS=2 \
  hpc/zeus_relative_scale_regimes_N13_N18.pbs
```

The smoke run uses \(N=4,t=100\) and four distinct regimes under
`$RUN_ROOT/smoke/`.

## Production

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="work/zeus_relative_scale_regimes_${RUN_TAG}"
LOG_ROOT="logs/zeus_relative_scale_regimes_${RUN_TAG}"

qsub \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_relative_scale_regimes_N13_N18.pbs
```

The header supplies `#PBS -J 13-18`. Different regime configurations are
distributed among process workers. Defaults are four workers for \(N=13\),
two for \(N=14,15\), and one for \(N=16,17,18\).

## Checkpoint and aggregation behavior

After every Hamiltonian, the parent atomically saves:

- the raw spectrum and runtime metadata;
- the heavy-tail and Born metrics;
- the three-row blue/red figure containing histogram
  \(P(\theta),P(\pi-\theta)\), connected \(R(\theta)\) versus Born, and the
  corresponding Bloch-sphere points;
- the updated `RUNNING.json` checkpoint.

After each complete \(N\), the same job saves the per-\(N\) comparison plot,
CSV, and summary, refreshes the cross-\(N\) heatmaps under an atomic lock, and
only then writes `DONE.json`. No separate aggregation job is required.

```text
$RUN_ROOT/
  raw/Nxx/.../spectrum_t1000000.npz
  regime_metrics/Nxx/<case_id>/metrics.json
  figures/Nxx/<case_id>/blue_red.png
  status/Nxx/RUNNING.json
  status/Nxx/DONE.json
  aggregates/Nxx/relative_scale_metrics_Nxx.csv
  aggregates/Nxx/relative_scale_comparison_Nxx.png
  aggregates/Nxx/summary.json
  aggregates/all_N/all_relative_scale_metrics.csv
  aggregates/all_N/relative_scale_across_N.png
  aggregates/all_N/summary.json
```

Cross-\(N\) heatmaps contain no cell numbers. Logs contain a timestamp,
worker process number/name, PID, and Hamiltonian parameters for every
calculation:

```bash
tail -f "$LOG_ROOT"/N13_*.log
```

Completed cases are reused after interruption. Resubmit with the same
`RUN_ROOT` to continue; use `FORCE=1` only for deliberate recomputation.
