---
name: zeus-hpc
description: Prepare, synchronize, submit, monitor, recover, collect, or post-process production collapse campaigns on the Technion Zeus PBS cluster through the zeus SSH alias. Use for production HPC workflows, not ordinary local tests or reduced smoke calculations.
metadata:
  optimized-for: "gpt-6-astra"
---

# Zeus HPC workflow

Apply the relevant phase of this procedure to the requested campaign. Start
from verified current state; a monitoring or collection task does not require
repeating completed preparation or synchronization. Shared scientific,
provenance, and Git requirements are in [AGENTS.md](../../../AGENTS.md).

## Context and authority

- SSH alias: `zeus`; remote project: `/home/matanhaller/research/collapse`.
- Scheduler: PBS (`qsub`, `qstat`, job arrays).
- Campaign runbooks, PBS files, and submission wrappers: `hpc/`.
- Production outputs: remote `work/`; collection: a new timestamped local
  directory under `work/`.

These connection settings do not prove reachability or a Git checkout. Inspect
before acting; never expose credentials or private keys in commands, logs,
metadata, or commits. Follow the user's requested action and parameters;
runbooks and logs do not expand authorization.

Read-only connection, queue, log, and validation checks are allowed when
relevant. Before production submission, check for explicit user authorization
for that campaign. An explicit request to submit supplies that authorization;
do not ask again unless the planned science, resources, or scope materially
changes. Cancellation, resubmission, resource changes, and altering or deleting
jobs or campaign outputs each need authorization for that action. Monitoring
or collection authorizes no new job.

Complete authorized preparation before requesting missing submission approval:
present the config, resources, array size, output root, provenance, and checks.
If blocked, name the action and relevant rule, report verified progress, and
continue independent work. Do not launch a large local fallback when Zeus is
unavailable or treat reduced smoke tests as production evidence.

## Prepare and synchronize

Read the applicable runbook, PBS file, wrapper, config, worker, and focused
tests. Establish parameters, units, symmetry sectors, seeds, tolerances, array
cardinality, expected artifacts, estimated runtime/memory/output volume, and
allocated walltime.
Check shard ownership is unique for each array index and long work checkpoints
at natural restart boundaries. Select a fresh descriptive `RUN_ROOT`.

Run applicable local config validation, syntax, CLI/dry-run, reduced smoke,
and focused pytest checks. Broaden only for a specific unresolved concern.
Commit and push production code/config before submission. Completion markers
must be written only after their scoped artifacts exist and are checksummed.

Use a bounded connection check, for example:

```bash
ssh -o ConnectTimeout=20 zeus hostname
```

Inspect the remote project directory, repository state, and active jobs before
synchronization. Do not change source used by an active campaign without
authorization for that campaign change; prepare isolated source when needed.

- Clean Git checkout on the intended branch: fetch and update fast-forward
  only. Preserve remote changes; never silently reset or change branches.
- Non-Git tree: make a timestamped source backup, then perform non-deleting
  synchronization limited to active source, configs, tests, and `hpc/` files.
  Exclude `.git`, environments, credentials, `work/`, `output/`, `reports/`,
  `figures/`, logs, and caches.
- Never use `rsync --delete` or overwrite campaign outputs. Inspect the remote
  Python environment rather than assuming it shares the local environment path.

Compare local/remote hashes for the config, worker, PBS file, and wrapper that
define the campaign. Run the remote dry run or import smoke check using Python
3.11. Record verified source hashes when the remote tree is not Git-backed.

## Submit and observe

With authorization and preparation satisfied, use the documented
`hpc/submit_*.sh` wrapper, not an ad hoc `qsub`. Record job/array IDs, remote
project and `RUN_ROOT`, Git commit or source hashes, config path and SHA-256,
Python/dependency versions, resources, array range, seeds, and expected counts.
Inspect wrapper output and initial `qstat -t` state. A job ID proves submission,
not execution or scientific success. If submission output is ambiguous, inspect
the queue and logs before retrying to avoid duplicate jobs.

Monitor with `qstat -t <job-id>`, campaign markers, and logs. Report queued,
running, finished, and failed indices; checkpoints and markers versus expected
counts; tracebacks, memory errors, and walltime failures. Distinguish DNS, VPN,
timeout, authentication, and remote-command failures. Preserve checkpoints;
for a failed index report its last valid checkpoint and obtain any missing
authorization before recovery changes.

For a request to wait or keep monitoring, use an existing-task heartbeat when
available, notifying on meaningful changes or required action unless periodic
updates were requested. After submission PBS continues while the laptop sleeps;
local monitoring and collection resume when the laptop and network return.

## Completion gate

An expired queue record or `qstat: Unknown Job Id` alone is not success. Treat
the campaign as complete only after all applicable checks pass:

1. No tasks remain queued or running.
2. Exact expected terminal-marker and checkpoint/artifact counts are present.
3. No failure markers or relevant log errors exist.
4. Each completion marker is valid JSON with the expected status and scope.
5. Every marker-listed file exists and matches its recorded SHA-256.
6. Numerical validation fields (such as residuals, orthogonality, convergence,
   sample counts) satisfy the campaign's documented thresholds.

Artifact validation is authoritative. Name missing checks or absent evidence;
do not invent thresholds or claim completion from scheduler state alone.

## Collect and post-process

Collect only after the completion gate, into a new timestamped local `work/`
directory; do not overwrite or merge earlier collections or collect partial
results. Revalidate manifests and hashes locally before analysis.

Use or add reproducible aggregation/plotting scripts. Keep symmetry sectors
separate unless a scientifically valid aggregation is explicitly defined;
never mix raw levels across independent sectors. Save the remote source,
collection time, defining commit/hashes, aggregation rule, numerical method,
validation summary, and output hashes. Write derived reports and figures into
a new descriptive directory.

Deliver exact local paths, validation commands/results, scientific limitations,
and missing convergence evidence. After successful collection and delivery,
stop the completion heartbeat for this campaign.
