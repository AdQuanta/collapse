# AGENTS.md — Collapse research repository

This file contains **stable repository-wide operating rules**. Keep it short and
rarely change it. Scientific goals belong in the active goal file; detailed
knowledge belongs in `wiki/`; current frontier status belongs in
`RESEARCH_STATE.md`; raw experiment evidence belongs in append-only logs and
report/output artifacts.

## 1. Mission

Prioritize, in order:

1. physical and mathematical correctness;
2. falsifiability and reproducibility;
3. numerical reliability;
4. maintainable code;
5. performance.

Never invent results, parameters, citations, validation, or command output.
Label claims explicitly as `PROVED`, `VERIFIED_NUMERICALLY`,
`PRELIMINARY_NUMERIC`, `CONJECTURE`, `FALSIFIED`, or `OPEN`.

Root geometry/statistics and operational measurement probabilities are distinct
questions. Never silently identify them.

## 2. Start of substantive work

Read, in this order:

1. this file;
2. the active goal file (normally `goal.md`, if present);
3. `RESEARCH_STATE.md`;
4. `wiki/index.md` and only the wiki pages relevant to the current question;
5. the implementation, tests, configs, and reports needed for the next
   experiment.

If `RESEARCH_STATE.md` is older than relevant repository changes, inspect those
changes before trusting it.

Do not reload the entire project history by default. Pull detailed background
from `wiki/` or `research_reports/` only when needed.

## 3. Research memory architecture

Use each layer for one purpose:

- `goal.md`: human-owned research objective, constraints, verifier, completion
  condition.
- `AGENTS.md`: stable repository policy.
- `CLAUDE.md`: thin tool-specific overlay only.
- `RESEARCH_STATE.md`: concise current frontier/champion/next questions.
- `wiki/`: durable scientific knowledge, derivations, failed mechanisms, and
  conceptual synthesis.
- experiment log: append-only machine-readable record of every experiment,
  including failures.
- `research_reports/`, `reports/`, `output/`: detailed evidence and derived
  artifacts.

Do not turn `RESEARCH_STATE.md` into a chronological archive. Move durable
details to the wiki/report layer and leave a short pointer.

## 4. Karpathy-style research loop

For an active research goal, use this loop:

1. **Read state.** Identify the single highest-value unresolved question.
2. **Hypothesize.** State one falsifiable hypothesis and its strongest
   alternative.
3. **Predict.** Write the expected discriminating outcome before running.
4. **Intervene minimally.** Change one primary scientific variable or mechanism
   per experiment whenever possible.
5. **Run the fixed verifier.** Do not change evaluation definitions mid-run.
6. **Compare.** Use the current baseline/champion and appropriate positive and
   negative controls.
7. **Decide.** Classify the result: `KEEP`, `REJECT`, `INCONCLUSIVE`, or
   `PROMOTE`.
8. **Log.** Record configuration, commit, seed, sizes/times, metrics, status,
   and artifact paths.
9. **Learn.** Update `RESEARCH_STATE.md` and the relevant wiki page only when
   the scientific state changed.
10. **Repeat.** Choose the next experiment for information gain, not compute
    volume.

A failed experiment is still a successful research step if it eliminates a
hypothesis. Revert failed candidate code/config when appropriate, but preserve
the experiment record and scientific lesson.

## 5. Verifier boundary

The evaluator is the scientific equivalent of Karpathy's fixed `prepare.py`.

During a comparable experiment series:

- do not modify the production observable definition, root solver, acceptance
  gate, binning convention, or held-out set to rescue a candidate;
- do not tune thresholds after seeing the result;
- do not omit failed coverage/root-validity cases;
- do not replace the production QZ/projective calculation with a convenient
  surrogate without labeling it as a separate experiment.

A verifier change is a **research-method change**. Make it separately, justify
it scientifically, regression-test it, version it, and restart comparisons
under the new verifier version.

For theory, the verifier cannot prove a theorem. Numerical verification may
falsify or support a claim; exact statements require analytical proof.

## 6. Scientific contract

For substantive theory or numerical work, make explicit as needed:

- physical question and observable;
- basis/tensor ordering, signs, normalization, boundary conditions, branches,
  degeneracies, and zero/infinite-root conventions;
- equations independent of implementation;
- approximation regime and neglected terms;
- exact limits, symmetries, and conservation laws;
- material numerical error sources;
- independent validation or solvable controls.

Never infer a continuum/asymptotic identity from finite-size agreement alone.
Never tune conventions to obtain a preferred conclusion. Preserve evidence
against the current hypothesis.

Evidence strength, highest first:

1. exact theorem/identity;
2. exact solvable limit;
3. independent formulation;
4. trusted benchmark;
5. convergence/sensitivity study;
6. qualitative agreement.

## 7. Numerical reliability

Use the production implementation for claims about production observables.

Check the errors material to the method: size/time/tolerance dependence,
conditioning, residuals/backward error, degeneracy handling, symmetry sectors,
precision/cancellation, stochastic uncertainty, and coverage.

Do not claim convergence from one resolution. Prefer at least three systematic
sizes/refinements when making scaling claims.

Use explicit `numpy.random.Generator` objects and record seeds. Do not mix
independent exact symmetry sectors before level-spacing analysis.

Large production simulations belong on Zeus. Read
`.agents/skills/zeus-hpc/SKILL.md` before remote mutation. Production
submission/resubmission/cancellation/resource changes require the authorization
defined there.

## 8. Implementation discipline

Repository map:

- `core/`: reusable scientific logic;
- `scripts/`: thin orchestration/CLI;
- `configs/`: validated scientific parameters;
- `hpc/`: production wrappers/runbooks;
- `tests/`: unit/regression/integration tests;
- `wiki/`: durable knowledge;
- `research_reports/`, `reports/`, `figures/`, `manuscript/`: research outputs;
- `work/`, `output/`, `tmp/`: generated data, never active imports;
- `archive/`: legacy, never active imports.

Prefer small complete changes, pure functions, explicit dependencies, validated
dataclasses/configs, and narrow interfaces. Keep models, solvers, I/O, plotting,
and orchestration separate. Avoid speculative abstraction and unrelated
refactoring.

Use Python 3.11, type hints for nontrivial interfaces, `pathlib.Path`, explicit
tolerances, deterministic tests, and domain-aware docstrings.

Typical checks, narrowest first:

```bash
python -m py_compile path/to/file.py
python scripts/<script>.py --help
python -m pytest -q tests/test_<feature>.py
python -m pytest -q
```

Inspect exit status and output before reporting success.

## 9. Provenance

Scientific outputs should record, as applicable:

- effective config/schema version;
- Git commit/source hashes;
- Python/dependency versions;
- seed;
- solver and tolerance;
- system size/time protocol;
- basis/symmetry convention;
- units/normalization;
- timestamp;
- validation summary.

Treat prior curated/production data as immutable unless replacement is
explicitly requested. Put derived outputs in new descriptive locations.

## 10. Git

Preserve unrelated work and pre-existing changes.

For substantive implementation work, use a task branch unless the user
requests otherwise. Keep commits cohesive and stage explicit paths.

Do not force-push, rewrite unrelated history, delete others' branches, or
resolve unexpected remote conflicts silently.

### Git delivery policy

For every completed task that changes tracked repository files, after applicable
validation:

1. commit the completed changes in a cohesive commit;
2. push the commit/task branch to the configured remote;
3. when integration into the default branch is authorized, merge the task branch
   using a **non-fast-forward merge** (`git merge --no-ff ...`), even when a
   fast-forward merge would be possible;
4. push the updated default branch to the configured remote;
5. verify the expected remote ancestry/state before declaring delivery complete;
6. remove only redundant agent-owned branches, and only after successful remote
   delivery is verified.

If the task is performed directly on an authorized target branch rather than a
task branch, commit the completed changes there and push that branch to the
configured remote after validation.

Instruction-only analysis/review does not require an empty commit or push.

## 11. Completion

"Done" means the active goal's completion condition is met, applicable
validation is complete, evidence and limitations are recorded, and authorized
delivery is verified.

If the active scientific goal is not solved, do not manufacture closure.
Record the strongest verified partial result, update the state/wiki, and
continue the research loop when the task calls for persistent research.
