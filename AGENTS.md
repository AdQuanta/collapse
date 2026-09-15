# AGENTS.md

Repository-wide instructions for coding and research agents. Read this file
before every task.

**Working code only. Finish the job. Plausibility is not correctness.**

## 0. Non-negotiables

1. Do not fabricate file paths, results, parameters, citations, API names,
   validation, or command output. Read the file, run the command, or say that
   the information is unknown.
2. Prioritize physical and mathematical correctness, falsifiability,
   reproducibility, numerical reliability, maintainability, then performance.
3. Distinguish projective-root geometry/statistics from operational measurement
   probabilities. Never silently identify them.
4. Disagree plainly with a false premise and stop when an ambiguity would
   materially change the result.
5. Touch only what the request requires. Preserve unrelated user changes.

Use the evidence labels `PROVED`, `VERIFIED_NUMERICALLY`,
`PRELIMINARY_NUMERIC`, `CONJECTURE`, `FALSIFIED`, and `OPEN` accurately.

## 1. Before writing code

Understand the problem and the repository before producing a diff.

- State a short plan and success criterion before editing.
- Read the files being changed and the relevant callers, tests, configs, and
  reports.
- For substantive research, read in order: this file, `goal.md` if present,
  `RESEARCH_STATE.md`, `wiki/index.md`, then only the relevant wiki and
  implementation files.
- Treat `RESEARCH_STATE.md` as a concise handoff, not an archive. If it may be
  stale, inspect the linked code and reports before relying on it.
- Match existing repository patterns. Surface material assumptions explicitly.

## 2. Writing code: simplicity and SOLID

Implement the smallest complete change that solves the request. Do not add
speculative features, abstractions, configurability, or unrelated cleanup.

All code must adhere to the SOLID principles:

- **Single Responsibility:** each module, class, or function has one cohesive
  reason to change.
- **Open/Closed:** extend behavior through composition or focused interfaces
  rather than repeatedly modifying stable code.
- **Liskov Substitution:** implementations honor the contracts and invariants
  of the abstractions they replace.
- **Interface Segregation:** keep interfaces narrow; clients should not depend
  on unused methods or parameters.
- **Dependency Inversion:** high-level logic depends on abstractions, with
  concrete numerical and I/O details supplied at the edges.

Use Python 3.11, type hints for nontrivial interfaces, `pathlib.Path`, explicit
tolerances, deterministic tests, explicit `numpy.random.Generator` instances,
and domain-aware docstrings.

## 3. Surgical changes

Every changed line must trace to the request or to correctness of the change.
Do not reformat, refactor working adjacent code, or delete pre-existing dead
code merely because you noticed it. Clean up only orphans created by your own
edit, and preserve failed-experiment records and curated production data.

## 4. Goal-driven research loop

For an active scientific goal:

1. identify the highest-value unresolved question;
2. state one falsifiable hypothesis and its strongest alternative;
3. predict the discriminating outcome before running anything;
4. change one primary variable or mechanism where possible;
5. run the fixed verifier and compare with baseline and controls;
6. classify the result as `KEEP`, `REJECT`, `INCONCLUSIVE`, or `PROMOTE`;
7. record configuration, commit, seed, sizes/times, metrics, status, and
   artifact paths;
8. update `RESEARCH_STATE.md` and the relevant wiki page only when the
   scientific state changes.

A failed experiment can be a successful research step if it eliminates a
hypothesis. Do not replace an analytical derivation with numerical fitting.

## 5. Scientific and numerical integrity

- Use the production observable, homogeneous QZ/projective calculation, root
  conventions, acceptance gate, binning, and held-out set for comparable
  experiments. A verifier change is a separately versioned research-method
  change.
- State basis/tensor ordering, signs, normalization, boundary conditions,
  branches, degeneracies, zero/infinite roots, approximation regime, and
  neglected terms when relevant.
- Check conditioning, residuals/backward error, degeneracy handling, symmetry
  sectors, cancellation/precision, coverage, and size/time/tolerance
  dependence. Do not claim convergence from one resolution.
- Never mix independent exact symmetry sectors before a valid level-spacing
  analysis. Preserve negative evidence and failed coverage/root-validity cases.
- Record provenance for scientific outputs: config/schema, source commit,
  Python/dependency versions, seed, solver/tolerance, protocol, conventions,
  timestamp, and validation summary.

## 6. Tool use and verification

Prefer running code to guessing. Read complete errors and inspect exit status.
Use the narrowest relevant check first, then broaden only for an unresolved
concern. For local Python work, resolve the interpreter in this order: active
virtual environment, `.venv/bin/python` or `venv/bin/python`, the project
Python 3.11 virtual environment, then verified `python3.11` on `PATH`.

Do not claim success from a plausible diff. If a verifier fails, fix the cause
or report the limitation; do not weaken the test or tune the definition after
seeing the result.

## 7. Session hygiene and communication

Be direct and concise. Do not use flattery, filler, ceremonial openings, or
unsupported certainty. Keep context focused on the current question. After two
failed corrections on the same issue, summarize the evidence and ask for a
sharper direction instead of looping.

Ask before proceeding when the interpretation materially changes the output,
when credentials or production resources are required, or when the request
conflicts with a load-bearing/versioned rule. Proceed when the ambiguity can be
resolved from the repository or the action is local and reversible.

## 8. Project context

### Stack

- Language: Python 3.11.
- Scientific runtime: NumPy, SciPy, QuSpin, Matplotlib; development tools also
  include pytest, SymPy, Pillow, pypdf, and ReportLab.
- Package installation: `requirements.txt` and `requirements-dev.txt`.
- Runtime targets: local Python 3.11 and production PBS jobs on Technion Zeus.

### Commands

- Install: `python3.11 -m pip install -r requirements-dev.txt`
- Compile check: `python3.11 -m py_compile path/to/file.py`
- Test all: `python3.11 -m pytest -q`
- Test one file: `python3.11 -m pytest -q tests/test_<feature>.py`
- Run a study: `python3.11 scripts/<runner>.py --help`, then use its checked-in
  config and documented arguments.
- Zeus production: use the applicable `hpc/` runbook and `submit_*.sh` wrapper;
  never invent an ad hoc submission command.
- Lint/typecheck: no repository-wide linter or type checker is configured;
  use focused syntax, tests, and scientific validation instead.

### Layout

- `core/`: reusable physics and numerical logic.
- `scripts/`: thin study, analysis, aggregation, and figure orchestration.
- `configs/`: versioned research parameters and campaign manifests.
- `hpc/`: PBS jobs, submission wrappers, and Zeus runbooks.
- `tests/`: unit, regression, invariant, and campaign-contract tests.
- `wiki/`: durable scientific knowledge; `raw/`, when present, is immutable
  source material for the wiki.
- `research_reports/`, `reports/`, `figures/`, `manuscript/`: research outputs.
- `work/`, `output/`, `tmp/`: generated data; never active imports.
- `archive/`: legacy material; never active imports.

Do not overwrite prior curated or production outputs. Put derived outputs in a
new descriptive location.

### Conventions specific to this repository

- The central qubit is first in tensor-product ordering. Production projective
  roots use homogeneous generalized eigenvalues of `C v = lambda A v`, with
  finite, infinite, and indeterminate roots handled explicitly.
- Keep equations and observable definitions independent of implementation, and
  do not silently change the thermodynamic/time-limit order in `goal.md`.
- Use focused pytest tests for invariants and reproducibility. Record seeds and
  campaign parameters for stochastic graph or parameter-space studies.
- Keep raw experiment logs append-only; put durable derivations and synthesis in
  `wiki/`, and concise frontier status in `RESEARCH_STATE.md`.

### Forbidden

- Do not use convenient surrogate solvers or observables for production claims
  without labeling a separate experiment.
- Do not tune thresholds, bins, held-out sets, or acceptance gates to rescue a
  candidate.
- Do not mix symmetry sectors, omit failed cases, infer asymptotic identities
  from finite-size agreement, or invent citations/results.
- Do not use destructive reset, force-push, broad deletion, or `rsync --delete`
  on project or campaign data.

## 9. Project skills

Use these project skills when their scope applies:

- **Zeus HPC** — `.agents/skills/zeus-hpc/SKILL.md` governs preparation,
  synchronization, authorized PBS submission, monitoring, collection, and
  post-processing of production campaigns.
- **High-impact academic scientific writing** —
  `.agents/skills/high-impact-academic-scientific-writing/SKILL.md` governs
  manuscript structure, claim strength, figures, references, and reviewer
  responses.
- **Karpathy LLM wiki** — `.agents/skills/karpathy-llm-wiki/SKILL.md` governs
  the `raw/` and `wiki/` knowledge-base architecture, grounding, indexing,
  append-only logging, querying, and linting.

Read the applicable skill file before acting. Skill instructions supplement
this file; they do not expand user authorization.

## 10. Git delivery

At task start, inspect branch, upstream, remotes, and `git status --short`.
Preserve pre-existing changes. For substantive changes, use an agent-owned
`codex/<topic>` branch unless the user requests a direct update. Stage explicit
paths, inspect the staged diff, and exclude secrets, generated bulk data, and
unrelated edits. Commit only after validation; push and integrate into the
default branch when authorized by the repository policy. Create or merge a PR
only when requested. Never rewrite history or force-push.

## 11. Project Learnings

Append a concrete one-line rule here when the user corrects an agent mistake;
prune rules that no longer prevent real errors.

- (empty)
