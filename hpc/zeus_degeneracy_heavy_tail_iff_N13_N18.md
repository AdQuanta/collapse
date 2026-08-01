# Zeus runbook: degenerate \(V_{ab}\) activation iff wrapped-heavy \(P(\theta)\)

Submit from the repository root on Zeus. Submission from `hpc/` is also
supported. The main PBS array is a unified simulation-and-aggregation job:
every Hamiltonian is checkpointed, every completed \(N\) gets its own
plots/tables, and that same array element refreshes the cross-\(N\) summary.
It uses Python 3.11, `zeus_new_q`, 8 CPUs, 128 GB, email notifications, and
timestamped worker logs.

## What is tested

The suite uses the periodic detector

\[
H_D=h_z\sum_i Z_i+J\sum_i Z_iZ_{i+1}
 +J_\pm\sum_i(\sigma_i^+\sigma_{i+1}^-+\mathrm{h.c.}),\qquad
V=\sum_iX_i,
\]

with

\[
H=I_0\otimes H_D+\frac{0.01}{\sqrt N}X_0\otimes V,\qquad
h_{z0}=0,\quad t=10^6,
\]

For the pure-Ising cases \(J_\pm=0\), a nonzero element of \(V\) flips one
detector spin. Its energy gap is one of

\[
2|h_z-2J|,\qquad 2|h_z|,\qquad 2|h_z+2J|.
\]

Therefore, for every \(N\ge3\),

\[
P_EVP_E\ne0\ \text{for some degenerate energy }E
\quad\Longleftrightarrow\quad h_z\in\{-2J,0,+2J\}.
\]

For the non-pure-Ising SU(2) cases, \(J_\pm=2J\), so the exchange part is
proportional to \(\sum_i(X_iX_{i+1}+Y_iY_{i+1}+Z_iZ_{i+1})\) and commutes
with \(V\). Every nonzero \(V\) transition then has gap \(2|h_z|\); exact
activation occurs iff \(h_z=0\). These statements hold at every simulated
\(N\), not merely at a small reference size.

The script records the appropriate exact activation certificate without
constructing a dense detector matrix. The expensive simulation independently determines
whether \(P(\theta)\) passes:

1. the historical project power-law gate; and
2. a stricter robustness gate that rejects atomic, poorly resolved, and
   nearly uniform impostors.

The eleven cases include clean-Ising resonances/detunings and four
non-pure-Ising SU(2)-exchange configurations spanning
\((J,J_\pm)=(0.25,0.5),(0.5,1),(1,2)\), plus the zero-field SU(2) symmetry
limit. `active_flat_atomic` and `nonising_su2_active_hz0` challenge
sufficiency; the \(\pm2.01\) Ising detunings challenge necessity.

Zero parameters are permitted as exact symmetry limits. Every nonzero
\(|h_z|,|J|,|J_\pm|\) is at least \(10J_x\); this constraint is checked while
loading the configuration. The physical coefficient on each central-detector
edge is smaller still: \(J_x/\sqrt N\).

## Environment

The PBS scripts use Zeus's `python3.11` directly and do not create or activate
a virtual environment. Verify once that the required packages are available:

```bash
cd "$HOME/research/collapse"
python3.11 -c 'import importlib.metadata as m; print({p:m.version(p) for p in ("quspin","quspin-extensions")})'
```

The job itself aborts before simulation unless these versions are exactly
`quspin==1.0.0` and `quspin-extensions==0.1.6`.

## Inspect and dry-run

```bash
cd "$HOME/research/collapse"

python3.11 examples/run_degeneracy_heavy_tail_campaign.py \
  --config configs/zeus_degeneracy_heavy_tail_iff_N13_N18.json \
  describe

qsub -J 13 \
  -v DRY_RUN=1 \
  hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.pbs

qsub -J 13 \
  -v SMOKE=1,CONFIG_WORKERS=2 \
  hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.pbs
```

The smoke job writes only under `$RUN_ROOT/smoke/`, uses `N=4`, four cases, and
`t=100`; it cannot be mistaken for production.

## Recommended staged production

Start with \(N=13\) and \(N=14\):

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="work/zeus_degeneracy_heavy_tail_iff_${RUN_TAG}"
LOG_ROOT="logs/zeus_degeneracy_heavy_tail_iff_${RUN_TAG}"

SIM_JOB_ID="$(
  qsub -J 13-14 \
    -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
    hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.pbs
)"
echo "$SIM_JOB_ID"
```

After inspecting runtime and memory, submit \(N=15,\ldots,18\) into the same
`RUN_ROOT`:

```bash
qsub -J 15-18 \
  -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
  hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.pbs
```

Completed cases are reused automatically after wall-time interruption. Use
`FORCE=1` only when a deliberate recomputation is required.

## Full production in one submission

```bash
cd "$HOME/research/collapse"

RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="work/zeus_degeneracy_heavy_tail_iff_${RUN_TAG}"
LOG_ROOT="logs/zeus_degeneracy_heavy_tail_iff_${RUN_TAG}"

SIM_JOB_ID="$(
  qsub \
    -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT" \
    hpc/zeus_degeneracy_heavy_tail_iff_N13_N18.pbs
)"
echo "$SIM_JOB_ID"
```

Because the PBS header contains `#PBS -J 13-18`, the command above runs all six
sizes. The defaults use 4 process workers for \(N=13\), 2 for \(N=14,15\), and
1 for \(N=16,17,18\). Workers always process different Hamiltonian cases.
BLAS/OpenMP threads use the remaining CPUs.

## Unified aggregation

No second `qsub` is required. Each `simulate-N` array element performs:

1. atomic raw-data, metadata, metric, and figure writes after every case;
2. the completed-\(N\) CSV, truth table, and aggregate plot;
3. a concurrency-locked refresh of `aggregates/all_N/`;
4. the final `status/Nxx/DONE.json` manifest.

The lock prevents simultaneous array completions from racing on the shared
cross-\(N\) files. The last successful array element therefore leaves the
complete six-size synthesis. The standalone aggregation PBS is retained only
as a manual rebuild/recovery tool.

## Logs

Every backend calculation prints timezone-aware `START` and `FINISH` records
with worker name/number, PID, \(N,h_z,J,J_\pm\), and elapsed time. The parent
prints a timestamped `CHECKPOINT` after saving each raw spectrum, metadata,
metrics, and figure. `DONE.json` is written only after the per-\(N\) products
and latest cross-\(N\) synthesis are safely stored.

```bash
qstat -u "$USER"
tail -f "$LOG_ROOT"/N13_*.log
tail -f "$LOG_ROOT"/N18_*.log
```

## Outputs

Each \(N\) is complete and independently interpretable before another size
finishes:

```text
$RUN_ROOT/
  raw/Nxx/.../spectrum_t1000000.npz
  campaign_metrics/Nxx/<case_id>/metrics.json
  figures/Nxx/<case_id>/blue_red.png
  status/Nxx/RUNNING.json
  status/Nxx/DONE.json
  aggregates/Nxx/case_metrics_Nxx.csv
  aggregates/Nxx/activation_vs_heavy_Nxx.png
  aggregates/Nxx/truth_table.json
  aggregates/all_N/all_case_metrics.csv
  aggregates/all_N/case_persistence.csv
  aggregates/all_N/heavy_tail_persistence.png
  aggregates/all_N/summary.json
```

Every `blue_red.png` has the established three-part diagnostic: blue
\(P(\theta)\) and red \(P(\pi-\theta)\) **histograms**, connected
\(R(\theta)\) points against \(\cos^2(\theta/2)\), and the corresponding
blue/red Bloch-sphere point distributions.

The final `summary.json` says `falsified_both_directions` only if the delivered
large-\(N\) rows contain both an activated/non-heavy case and a
non-activated/heavy case under the pre-registered primary gate. The robust
classification is retained separately, so a verdict cannot be manufactured by
changing the gate after seeing the data.

## Resource warning

The campaign has only eleven configurations per \(N\), rather than the earlier
880-point grid, but \(N=17,18\) remain expensive because the exact dynamics
requires complete symmetry-sector spectra. The scripts cover and checkpoint
those sizes; they do not guarantee that every \(N=18\) case will finish inside
one 120-hour allocation. Resubmit with the same `RUN_ROOT` to resume.
