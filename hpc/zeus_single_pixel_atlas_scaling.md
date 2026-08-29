# Zeus runbook: 2026-07-14 single-pixel atlas scaling

Four independent campaigns reproduce the corrected simulations at detector
sizes `N=11,12,13,14,15,16,17,18`. No Zeus job was submitted by Codex.

| Campaign | Fixed model | Single-N launcher | PBS array |
|---|---|---|---|
| central field | `J=1, hz=0.1`, seven `hz0` values | `scripts/run_hz0_atlas_scaling.py` | `hpc/zeus_hz0_atlas_N11_N18.pbs` |
| Ising field neighborhoods | `J=1, hz0=0`, near `hz=-2,0,+2` | `scripts/run_hz_resonance_atlas_scaling.py` | `hpc/zeus_hz_resonance_atlas_N11_N18.pbs` |
| plus-minus field neighborhoods | `J=0, Jpm=1, hz0=0`, near `hz=-2,-1,0,+1,+2` | `scripts/run_jpm_hz_atlas_scaling.py` | `hpc/zeus_jpm_hz_atlas_N11_N18.pbs` |
| plus-minus coupling | `J=1, hz=0.1, hz0=0`, twelve `Jpm` values including `Jpm=J` | `scripts/run_jpm_coupling_atlas_scaling.py` | `hpc/zeus_jpm_coupling_atlas_N11_N18.pbs` |

Every command explicitly passes collective `Jx=0.01`. The Hamiltonian edge
coefficient is verified after every completed size to be `0.01/sqrt(N)`.

## Environment

Zeus uses Python 3.11 for these jobs. Prepare a Python 3.11 environment with
the pinned numerical packages, then supply its path when needed:

```bash
python3.11 -m venv .venv-zeus-atlas
source .venv-zeus-atlas/bin/activate
python -m pip install -r requirements-local-study.txt
```

All four PBS headers target `zeus_new_q`, request `8` CPUs and `128gb`, and
send `abe` notifications to `matanhaller@campus.technion.ac.il`, as specified.
The PBS helper defaults to `python3.11`. Before doing any work it requires
Python 3.11, `quspin==1.0.0`, and `quspin-extensions==0.1.6`. Use
`VIRTUAL_ENV_PATH`, `ZEUS_ENV_SETUP`, or `PYTHON_MODULES` only when your Zeus
environment needs them. No account or module name is assumed.

## Dry run and smoke test

Submit from the repository root or directly from its `hpc/` directory. The
PBS bootstrap now detects either layout. Use a single array index for smoke
tests so several jobs do not write the same `N=4` namespace:

```bash
qsub -J 11 -v DRY_RUN=1 hpc/zeus_hz0_atlas_N11_N18.pbs
qsub -J 11 -v SMOKE=1 hpc/zeus_hz0_atlas_N11_N18.pbs
qsub -J 11 -v SMOKE=1 hpc/zeus_hz_resonance_atlas_N11_N18.pbs
qsub -J 11 -v SMOKE=1 hpc/zeus_jpm_hz_atlas_N11_N18.pbs
qsub -J 11 -v SMOKE=1 hpc/zeus_jpm_coupling_atlas_N11_N18.pbs
```

## Final production submission

Because the array range, queue, resources, and mail settings are already in
each PBS header, the shortest final commands from the repository root are:

```bash
qsub hpc/zeus_hz0_atlas_N11_N18.pbs
qsub hpc/zeus_hz_resonance_atlas_N11_N18.pbs
qsub hpc/zeus_jpm_hz_atlas_N11_N18.pbs
qsub hpc/zeus_jpm_coupling_atlas_N11_N18.pbs
```

If the packages live in a virtual environment that is not already active,
add it to each command, for example:

```bash
qsub -v VIRTUAL_ENV_PATH="$PWD/.venv-zeus-atlas" hpc/zeus_hz0_atlas_N11_N18.pbs
```

The other three commands use the same `-v VIRTUAL_ENV_PATH=...` prefix.

Before submission, verify that the complete new implementation was copied to
Zeus—not only the four small PBS files:

```bash
test -f hpc/zeus_single_pixel_atlas_common.sh
test -f core/scaling_campaign.py
test -f scripts/run_hz0_atlas_scaling.py
```

If submitting while inside `hpc/`, use `qsub zeus_hz0_atlas_N11_N18.pbs`.
The job will resolve the repository as the parent directory.

Use a unique campaign root for production:

```bash
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="work/zeus_single_pixel_atlas_${RUN_TAG}"
LOG_ROOT="logs/zeus_single_pixel_atlas_${RUN_TAG}"

qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT/hz0" hpc/zeus_hz0_atlas_N11_N18.pbs
qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT/hz_resonance" hpc/zeus_hz_resonance_atlas_N11_N18.pbs
qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT/jpm_hz" hpc/zeus_jpm_hz_atlas_N11_N18.pbs
qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT/jpm_coupling" hpc/zeus_jpm_coupling_atlas_N11_N18.pbs
```

Each PBS array index owns exactly one size. This is the useful and
memory-safe multiprocessing layer on Zeus: independent `N` values run on
different nodes. The Python launchers also accept `--workers`, which launches
independent sizes with `ProcessPoolExecutor`; use more than one only for small
sizes and only when the allocation can hold their combined peak memory.

## Checkpointing and logs

For a campaign named `STUDY`, each size is isolated under

```text
$RUN_ROOT/STUDY/Nxx/
  raw/                 raw NPZ spectra and per-case metadata
  figures/             every atlas, summary, metrics CSV, and manifest
  logs/stdout.log      simulation and plotting standard output
  logs/stderr.log      warnings and tracebacks
  RUNNING.json         command and environment while active
  DONE.json            written only after all outputs validate
  FAILED.json          subprocess or output-validation failure
```

The campaign-level `campaign_summary.json` is rewritten atomically after each
size finishes. Thus completed sizes retain both results and plots if a later
size reaches wall time. Rerunning the same command reuses `DONE.json` sizes and
the underlying raw-spectrum checkpoints. Set `FORCE=1` only for deliberate
recomputation. PBS-level logs are written under `$LOG_ROOT`.

## Memory scaling and N=17,18 caution

The final relative matrix has dimension `2^N`. The storage for only one dense
complex128 matrix is:

| N | matrix dimension | one complex matrix |
|---:|---:|---:|
| 11 | 2,048 | 0.06 GiB |
| 12 | 4,096 | 0.25 GiB |
| 13 | 8,192 | 1 GiB |
| 14 | 16,384 | 4 GiB |
| 15 | 32,768 | 16 GiB |
| 16 | 65,536 | 64 GiB |
| 17 | 131,072 | 256 GiB |
| 18 | 262,144 | 1,024 GiB |

The calculation holds additional matrices and eigensolver workspaces, so
actual peak memory is larger. The requested 128 GiB PBS allocation is a
starting point for the smaller sizes, not evidence that `N=16..18` fits.
Submit one `N=11` task,
inspect its logs and peak memory, then scale one size at a time. Override the
resource request from `qsub` or copy the PBS header for high-memory nodes. For
example, only if Zeus exposes a suitable allocation:

```bash
qsub -J 17 -l select=1:ncpus=8:mem=512gb hpc/zeus_hz0_atlas_N11_N18.pbs
qsub -J 18 -l select=1:ncpus=8:mem=1500gb hpc/zeus_hz0_atlas_N11_N18.pbs
```

Those values are lower-bound planning estimates, not validated Zeus resource
claims. The scripts cover `N=17,18`, but the dense algorithm may require an
algorithmic change or hardware unavailable on Zeus.

## Manual non-PBS use

Each launcher defaults to all eight requested sizes and saves after every N:

```bash
python3.11 scripts/run_hz0_atlas_scaling.py --workers 1
python3.11 scripts/run_hz_resonance_atlas_scaling.py --workers 1
python3.11 scripts/run_jpm_hz_atlas_scaling.py --workers 1
python3.11 scripts/run_jpm_coupling_atlas_scaling.py --workers 1
```

For a small parallel pilot, use a restricted grid such as
`--N 11 12 --workers 2`. Do not launch large N values concurrently merely
because CPUs are available; memory, not CPU count, is the governing limit.
