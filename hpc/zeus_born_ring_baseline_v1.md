# Six-task multichannel baseline replication

Prepared and submitted 2026-09-13 after explicit user authorization.
Preparation and local validation do not constitute submission. Follow
`.agents/skills/zeus-hpc/SKILL.md` and inspect current remote state first.

## Scientific scope

Config: `configs/born_ring_baseline_campaign_v1.json`.
Method: `ring-translation-qz-v1`; unchanged `born-phase-verifier-v1`.
The two saved multichannel seeds are replicated at N=13,14,15 with full
homogeneous QZ at t=1e4,1e5,1e6,1e7. Discovery times are 1e4 and 1e6;
the other two times are held out from candidate selection. No parameter
perturbation or fitting is performed in this first campaign.

The matrix is block diagonalized only by detector translation. All momenta,
all detector states and every projective root retain their algebraic weights.
The worker saves full pole, validity, residual, conditioning and coverage
diagnostics. Root statistics are not operational measurement probabilities.

## Task map and resources

| Index | Seed | N | Momentum blocks | Roots per time |
|---|---|---:|---:|---:|
| 0 | 079 | 13 | 13 | 8192 |
| 1 | 079 | 14 | 14 | 16384 |
| 2 | 079 | 15 | 15 | 32768 |
| 3 | 047 | 13 | 13 | 8192 |
| 4 | 047 | 14 | 14 | 16384 |
| 5 | 047 | 15 | 15 | 32768 |

Six array tasks, each requesting 8 CPUs, 16 GiB RAM and 24 hours; at most
two run concurrently. These are allocation limits, not measured runtimes.
Total expected outputs: 84 momentum checkpoints, 336 sector/time root NPZs,
six task completion markers and 24 pooled instantaneous profiles.

The largest N15 detector-sector dimension is 2192, with a full Hamiltonian
block dimension 4384. Sixteen complex128 arrays of that full block size use
4.583 GiB; the 16 GiB allocation allows additional basis, LAPACK and QZ
workspace. This is a conservative working estimate, not a profiled peak-RSS
bound. Only one block is diagonalized at a time. Root arrays and JSON metadata
are retained; eigenvector matrices are not saved. Expected stored roots are
458752 homogeneous pairs across all cases/times, plus residuals and metadata;
raw numeric root storage is about 24.5 MiB before compression (JSON additional).
Actual larger-N runtime and peak memory are unmeasured for this method.

## Isolated source and preflight

Intended source snapshot:
`/home/matanhaller/research/collapse/source_snapshots/born_ring_89b7c36`.
Defining commit: `89b7c36` (expanded hash via git). The main Zeus source tree
is not Git-backed, so prepare a fresh non-overwriting snapshot from tracked
files and compare hashes before using it. Existing campaign/source files
must remain untouched.

Fresh intended output root:
`/home/matanhaller/research/collapse/work/born_ring_baseline_v1_89b7c36`.
Verified remote Python entry point: `/usr/bin/python3.11`.
Verified runtime: Python 3.11.11, NumPy 2.2.6, SciPy 1.17.1 and QuSpin 0.3.7.
After the user restored connectivity, the isolated snapshot was transferred
and its archive plus all worker-defining source/config/PBS/wrapper hashes
matched locally. The intended output root remains absent. The initial SSH
failures are preserved in the earlier preflight record.

Before submission, verify the complete source/config/PBS/wrapper hashes,
run the focused test suite and dry run, confirm a fresh output root, check
the current queue, and record all outputs. These remote checks passed on
2026-09-13: 38 focused tests, the six-task dry run and shell syntax checks;
qsub is present and the user's queue is empty. System Python lacks pytest,
so tests used `/tmp/born_ring_preflight_89b7c36`, an isolated venv containing
pytest 9.1.1. Both Python entry points resolve the exact same installed
NumPy/SciPy/QuSpin modules and versions. Production still uses
`/usr/bin/python3.11`. Evidence:
`reports/born_ring_campaign_remote_preflight_2026-09-13/`.
Submitted as `4682629[].zeus-master` with the approved resources. Initial task 0
failed the unchanged eigensystem orthogonality gate at momentum zero
(1.2284321012392794e-12 > 1e-12); tasks 1 and 2 were running, 3–5 queued.
Evidence: `reports/born_ring_campaign_submission_2026-09-13/`.
No recovery or production source modification has been performed.

Local validation passed 38 tests,
including an actual reduced worker run, successful resume and deliberate
checkpoint corruption rejection. The separate dense/sector validation passed
27 conditions through t=1e6, followed by nine more at t=1e7; all passed
the predeclared method thresholds. These are reduced N5–7 checks, not a
large-N precision certificate.

## Submission command, after authorization and remote preflight

```bash
cd /home/matanhaller/research/collapse/source_snapshots/born_ring_89b7c36
RUN_ROOT=/home/matanhaller/research/collapse/work/born_ring_baseline_v1_89b7c36 \
PYTHON_BIN=/usr/bin/python3.11 \
bash hpc/submit_zeus_born_ring_baseline_v1.sh
```

The wrapper checks for a new output root and executes a dry run before qsub.
Record the returned job ID and inspect `qstat -t`. Never rerun the wrapper
after an uncertain submission without inspecting queue and job-ID artifacts.

## Recovery and completion

Each task owns a unique seed/N directory. Completed momentum checkpoints
contain checksummed diagnostics and all four time NPZs. A resumed task verifies
source/config/runtime identity, checks every completed checkpoint, and
recomputes only an incomplete momentum block. Recovery needs the authorization
defined in the skill. Failure markers are preserved in timestamped history
on authorized resume. No thresholds are changed to make a failed job pass.

Require all six task markers, all 84 checkpoint markers, all 336 NPZ files,
matching recursive hashes, no active failure marker, and passed scientific
validity diagnostics. A missing PBS record alone is insufficient. Collect
only a completed campaign into a fresh local directory and verify hashes
again. Preserve discovery/held-out separation and show every P/reflected-P
and R/Born profile, including failed coverage cases. No candidate is promoted
to an exact phase from this finite sample.

The local `scripts/audit_born_ring_campaign.py` validates all task, momentum
and time coverage, recursive hashes, source/config identity and saved numerical
diagnostics, then recomputes pooled frozen metrics from homogeneous root files.
Run it against a completed collection with a fresh derived output directory.
It retains failed angular coverage as a scientific result; it does not rerun
QZ or establish an asymptotic limit.
