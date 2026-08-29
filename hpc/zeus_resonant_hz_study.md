# Zeus/PBS runbook: resonant h_z study

This repository uses PBS on Zeus. No account, queue, module, or filesystem value is assumed. Set `PYTHON_MODULE` only if the site requires one; otherwise arrange for `python3.11` to be on `PATH`.

Create the exact environment once:

```bash
VENV=.venv-resonant PYTHON_BIN=python3.11 bash hpc/create_resonant_env.sh
```

Dry-run one array task, then smoke-test it:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="work/zeus_resonant_${RUN_TAG}"
LOG_ROOT="logs/zeus_resonant_${RUN_TAG}"
qsub -J 0 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",DRY_RUN=1 hpc/zeus_resonant_hz_study_template.pbs
qsub -J 0 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",SMOKE=1 hpc/zeus_resonant_hz_study_template.pbs
```

Default production grid (`N=10..14`, `h_z=-3,-2,-1,0,1,2,3`, all five required times):

```bash
qsub -J 0-34 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT",VENV=.venv-resonant hpc/zeus_resonant_hz_study_template.pbs
```

Override resources by copying the PBS template and changing only the `#PBS -l` lines. Local dense scaling gives about 16 minutes for the complete N=10 seven-field/five-time sweep at full dimension 2048. Dense memory scales approximately as the square of the full dimension and eigensolution time approximately cubically, so the default 32 GB and 12 hours are estimates that must be checked from the first N=11 log before scaling further.

Each task has an isolated output root and can be safely resumed. After every task has `metadata.json` and no `INCOMPLETE` marker, aggregate without recomputation:

```bash
python scripts/aggregate_resonant_hz_runs.py --input-root "$RUN_ROOT/tasks" --out "$RUN_ROOT/aggregated"
python scripts/complete_resonant_hz_analysis.py --mandatory "$RUN_ROOT/aggregated" --near-resonance work/single_pixel_quspin_fresh_2026-07-12/near_resonance_N8 --long-average work/single_pixel_quspin_fresh_2026-07-12/long_average_N8_v2 --out "$RUN_ROOT/figures"
```

Logs are deterministic under `$LOG_ROOT`. A nonzero PBS exit, missing `metadata.json`, or an `INCOMPLETE` marker is a failed task. This runbook has been syntax-reviewed locally but no Zeus job was submitted by Codex.
