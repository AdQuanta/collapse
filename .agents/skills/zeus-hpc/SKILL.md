---
name: zeus-hpc
description: Run, monitor, recover, collect, or post-process production-scale collapse simulations on the Technion Zeus PBS cluster through the `zeus` SSH alias. Use for large HPC campaigns; do not use for ordinary local tests or small smoke calculations.
---

# Zeus HPC workflow

Use this skill for production computation whose cost, runtime, or memory makes
local execution inappropriate. Follow the repository's `AGENTS.md`; this skill
adds the operational Zeus procedure.

## Fixed context

- SSH alias: `zeus`
- Remote project: `/home/matanhaller/research/collapse`
- Scheduler: PBS (`qsub`, `qstat`, job arrays)
- Campaign definitions, wrappers, and runbooks: `hpc/`
- Production data: remote `work/`; collected data: a new timestamped local
  directory under `work/`

Treat the SSH alias and remote path as configuration, not proof that the host
is reachable or that the remote directory is a Git checkout. Inspect before
acting. Never expose credentials or private keys in commands, logs, metadata,
or commits.

## Authorization boundary

Read-only connection checks, queue inspection, log inspection, and validation
are allowed when relevant. Obtain explicit user authorization before the first
production `qsub`. Do not cancel, resubmit, alter, or delete jobs or campaign
outputs without authorization for that action. A request to monitor or collect
does not authorize a new submission.

## 1. Prepare locally

1. Read the applicable `hpc/` runbook, PBS file, submission wrapper, config,
   worker, and focused tests.
2. Confirm scientific parameters, units, symmetry sectors, random seeds,
   solver tolerances, expected array cardinality, and expected artifacts.
3. Run the narrow local checks: configuration validation, `--help` or dry run,
   a reduced smoke case, syntax checks, and focused pytest tests.
4. Estimate runtime, memory, output volume, walltime, and array size. Ensure
   every array index owns a unique shard and long work checkpoints at a natural
   restart boundary.
5. Use a fresh descriptive `RUN_ROOT`. Completion markers must be written only
   after all artifacts for their scope exist and are checksummed.

Do not describe a smoke test as production evidence. Do not start a large
local fallback if Zeus is unavailable.

## 2. Connect and synchronize safely

Start with a bounded connection and read-only inspection, for example:

```bash
ssh -o ConnectTimeout=20 zeus 'hostname; pwd; test -d /home/matanhaller/research/collapse'
```

Inspect the remote repository state and active jobs before synchronization.

- If the remote project is a clean Git checkout on the intended branch, use a
  normal fetch and fast-forward-only update. Never discard remote changes.
- If it is not a Git checkout, make a timestamped source backup, then use a
  non-deleting synchronization limited to active source, configs, tests, and
  `hpc/` files. Exclude `.git`, virtual environments, credentials, `work/`,
  `output/`, `reports/`, `figures/`, logs, and caches.
- Never use `rsync --delete`, overwrite remote campaign outputs, or assume the
  local and remote Python environments have the same absolute path.

After synchronization, compare hashes for the config, worker, PBS file, and
submission wrapper that define the campaign. On Zeus, run the dry run or import
smoke check again with Python 3.11 before submission.

## 3. Submit through the repository wrapper

Use the documented `hpc/submit_*.sh` wrapper rather than an ad hoc `qsub`.
Record exactly:

- job and array IDs;
- remote repository and `RUN_ROOT`;
- Git commit or synchronized source hashes;
- config path and SHA-256;
- Python and dependency versions;
- queue resources, array range, seeds, and expected artifact counts.

Inspect the wrapper output and initial `qstat -t` state. A returned job ID is
evidence of submission, not evidence that the calculation started or passed.

## 4. Monitor without disturbing the run

Use `qstat -t <job-id>` plus campaign markers and logs. Report concise progress:
queued/running/finished/failed indices, completed checkpoints versus expected,
completion-marker count, and detected tracebacks, memory failures, or walltime
failures.

Do not collect partial results or treat `qstat: Unknown Job Id` alone as
success. If access fails, distinguish DNS, VPN, timeout, authentication, and
remote-command errors. Preserve existing checkpoints. If a task fails, list
its index and last valid checkpoint; wait for user authorization before
resubmission or resource changes.

For a user request to wait, use an existing-thread heartbeat when available.
The PBS job continues if the laptop sleeps after successful submission, but
local monitoring and collection pause until the laptop and network return.

## 5. Require a completion gate

Treat a campaign as complete only when all applicable checks pass:

1. no tasks remain queued or running;
2. the exact expected number of terminal completion markers exists;
3. the exact expected checkpoint/artifact count exists;
4. no failure markers or relevant log errors exist;
5. every completion marker is valid JSON with the expected status and scope;
6. every file listed by a marker exists and matches its recorded SHA-256;
7. numerical validation fields such as residuals, orthogonality, convergence,
   and sample counts meet the campaign's documented thresholds.

An expired queue record is normal after completion; artifact validation is the
authoritative gate.

## 6. Collect and post-process reproducibly

Copy a completed campaign into a new timestamped local `work/` directory. Do
not overwrite or merge it with an earlier collection. Re-run the manifest and
hash validation locally before analysis.

Use or add a reproducible script for aggregation and plotting. Keep symmetry
sectors separate unless the analysis explicitly defines a valid aggregation;
never mix raw levels across independent sectors. Save provenance containing
the remote source, collection time, defining hashes or commit, aggregation
rule, numerical method, validation summary, and output hashes. Write derived
reports or figures to a new descriptive directory.

Report the exact local paths, validation commands and results, scientific
limitations, and any missing convergence evidence. Stop any completion
heartbeat after successful collection and delivery.
