# Network top-`S_born` central-field scan

This campaign selects the ten highest stored canonical `S_born`
configurations independently from each of the Erdos-Renyi, Watts-Strogatz,
Barabasi-Albert, and random-regular/expander source campaigns. Exact ties are
broken by source path.

Here, "closest to Born" means the largest **stored one-dimensional polar**
`S_born` used in the source studies. It is not a full-sphere Born certificate:
all source runs have `hz0=0` and central-X-only coupling, so their roots obey
the proven great-circle restriction. This scan tests whether turning on the
central longitudinal field changes that behavior while holding the detector
and its graph fixed.

For every selected configuration it preserves:

- `N=12`;
- `J`, `Jpm`, `hz`, and collective source `Jx`;
- evolution time and model seed;
- graph-family parameters and graph seed;
- the exact detector edge set, verified against the saved source metadata.

Only the central field changes. The default variants are

```text
hz0 = 0
hz0 = hz - 1e-3
hz0 = hz - 1e-4
hz0 = hz
hz0 = hz + 1e-4
hz0 = hz + 1e-3
```

The offsets are additive, in the same Hamiltonian units as `hz`. Numerical
duplicates are collapsed per source case. Defaults are versioned in
`configs/zeus_network_top_hz0_variants_N12.json`; change `top_count_per_family`,
the offsets, or `cases_per_array_task` there. The submission wrapper derives
the PBS array length from the validated selection.

The default campaign contains 40 source configurations and 240 simulations.
Each of 20 PBS tasks owns two source configurations and runs their six field
variants sequentially, avoiding nested multiprocessing/semaphore failures.
Every `(configuration,hz0)` directory writes its own atomic `COMPLETE.json`, so
resubmitting with the same `RUN_ROOT` safely resumes missing variants.

From the repository root on Zeus:

```bash
export RUN_ROOT="$PWD/work/zeus_network_top_hz0_variants_N12_$(date +%Y%m%d_%H%M%S)"
bash hpc/submit_zeus_network_top_hz0_variants_N12.sh
```

Inspect progress with

```bash
qstat -u "$USER"
tail -f "$RUN_ROOT"/logs/task_*.log
```

`selection_manifest.json` records the complete ranked source cases and graph
provenance. `tasks/task_*/RUNNING.json`, `COMPLETE.json`, and `FAILURE.json`
provide task-level status in addition to the fine-grained case checkpoints.
