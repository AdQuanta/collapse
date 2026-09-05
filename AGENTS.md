# AGENTS.md — Theoretical and Numerical Physics Research

## Mission and authority

Prioritize, in order: physical correctness, reproducibility, numerical
reliability, maintainable Python, then performance. Never invent results,
parameters, citations, validation, or command output. Label exact,
approximate, fitted, numerical, heuristic, and conjectural claims distinctly.

Interpret requests by outcome:

- For explanation, review, diagnosis, or status, inspect and report; do not
  change files or external state unless asked.
- For change, build, or fix requests, make the smallest complete in-scope
  change, validate it, then commit and push it under **Git delivery**.
- For production computation, follow **Zeus and expensive computation**.
- Stop for user input only when a missing choice materially changes the
  scientific result, cost, destructive effect, or scope. State assumptions
  that permit safe progress.

Deeper `AGENTS.md` files may specialize a subtree but must not weaken these
scientific-integrity, data-safety, or reproducibility requirements.

## Repository map

- `core/`: reusable models, equations, solvers, analysis, serialization, plots
- `scripts/`: thin study, sweep, report, and orchestration entry points
- `configs/`: versioned, validated scientific parameters
- `hpc/`: Zeus PBS files, submission wrappers, and campaign runbooks
- `tests/`: pytest unit, regression, integration, and smoke tests
- `manuscript/`, `reports/`, `figures/`, `presentations/`: research outputs
- `work/`, `output/`, `tmp/`: generated or intermediate data
- `archive/`: legacy material; never import it as active code

Put reusable logic in `core/`. Keep `scripts/` responsible for configuration,
calls into reusable code, persistence, and provenance. Do not import active
code from generated-output directories. Inspect nearby modules, tests, and
call sites before introducing a new abstraction.

## Environment and routine checks

Use Python 3.11, matching Zeus. On the primary macOS workstation, prefer
`~/.venvs/collapse-py311/bin/python` when present; otherwise use an activated
Python 3.11 environment documented in `README.md`.

Run the narrowest relevant checks first, then broaden in proportion to risk:

```bash
python -m py_compile path/to/script.py
python scripts/<script>.py --help
python -m pytest -q tests/test_<feature>.py
python -m pytest -q
```

Inspect exit status and output before claiming a check passed. Do not install
or change dependencies merely to satisfy optional development tooling without
a project need.

## Scientific contract

For substantive theory or numerical work:

1. State the physical question, observable, units, and validity regime.
2. Record relevant conventions: basis and tensor ordering, signs and phases,
   normalization, boundaries, gauge, branches, degeneracies, and zero modes.
3. Identify the governing equations independently of implementation and mark
   the approximation order and neglected terms.
4. Identify exact limits, symmetries, conservation laws, scaling, and other
   checks before implementation.
5. Choose a numerical representation and name its error sources.
6. Implement the smallest testable change.
7. Validate against exact limits, invariants, an independent formulation, or a
   trusted benchmark; add convergence or sensitivity evidence when relevant.
8. Save sufficient provenance and report unresolved limitations.

Do not change conventions or tune code to obtain a preferred conclusion.
Preserve and report evidence that contradicts the hypothesis. Do not apply
non-degenerate perturbation theory across a vanishing denominator or infer a
continuum identity from finite-size agreement alone.

Maintain traceability between equations, operators, basis states, parameters,
arrays, and figures. Separate analytical definitions from discretizations.
Use symbolic algebra to verify reasoning, recording its assumptions; spot-check
identities numerically at nonsingular points when practical.

## Numerical reliability

Numerical output is evidence only after the material error sources have been
checked. Choose checks relevant to the method:

- basis, grid, cutoff, size, timestep, tolerance, and tail convergence;
- finite-volume, boundary, precision, cancellation, and conditioning effects;
- residuals, backward error, orthogonality, symmetry sectors, degeneracies,
  and spectral matching;
- quadrature, regularization, optimization branch, and initialization
  sensitivity;
- Monte Carlo uncertainty, autocorrelation, burn-in, and seed dependence.

Do not claim convergence from one resolution. When establishing an order or
extrapolation, prefer at least three systematic refinements; if cost prevents
this, label the result provisional.

Preserve matrix structure. Prefer Hermitian routines for Hermitian problems,
factorizations or `solve` over explicit inversion, sparse or matrix-free
operators over unnecessary dense matrices, and residual checks over solver
status alone. Treat near-degeneracy and eigenvector phase ambiguity explicitly.

Pass `numpy.random.Generator` objects explicitly. Save the actual seeds and
quantify stochastic uncertainty; use multiple seeds when conclusions depend
on a realization.

Validation evidence is strongest in this order: exact identities and
invariants; solvable limits; independent methods; trusted benchmarks;
convergence and sensitivity; qualitative behavior. A plausible plot is not a
validation by itself.

## Python design and interfaces

Use pragmatic SOLID design without ceremonial abstractions:

- Give functions and modules one coherent responsibility. Separate models,
  solvers, configuration, I/O, plotting, CLI orchestration, and HPC submission.
- Prefer composition, pure functions, and frozen validated dataclasses. Add an
  interface only when real alternative implementations need it.
- Preserve subtype contracts, including accepted domains, units,
  normalization, shapes, and numerical guarantees.
- Inject solvers, RNGs, optimizers, and storage dependencies when doing so
  enables scientific comparison or testing.
- Avoid global mutable state, import-time computation, and hidden caches. A
  scientific cache key must include every output-affecting parameter.

Follow PEP 8 and surrounding style; no formatter is enforced. Use type hints
for public and nontrivial interfaces, `pathlib.Path`, explicit keyword
arguments for tolerances and conventions, clear exceptions, and domain-aware
docstrings. Never use mutable defaults or wildcard imports. Prefer separate
functions or strategies to boolean flags that select substantially different
algorithms. Optimize only after profiling, with accuracy-preserving regression
tests and a clear reference implementation where useful.

## Configuration, provenance, and outputs

Keep scientifically relevant parameters in validated, human-readable files
under `configs/`; changing an output-affecting default is a research-method and
API change requiring documentation and regression coverage.

Saved results should include, as applicable:

- effective configuration and schema version;
- Git commit or defining source hashes;
- Python and dependency versions;
- seed, solver, tolerance, discretization, basis, cutoff, and size;
- units and normalization conventions;
- timestamp and validation summary.

Do not rely on unspecified iteration or parallel scheduling order. Avoid local
absolute paths in shareable source, configs, reports, and metadata.

Treat downloaded Zeus data, prior reports, and curated results as immutable
unless replacement is explicitly requested. Write new derived outputs to a
descriptive or timestamped directory. Do not commit ignored bulk data, caches,
logs, virtual environments, temporary files, or secrets.

Figures must be traceable to code and data, with axes, units, parameters, and
normalization labeled. Record any smoothing, filtering, cropping, aggregation,
or selection that could affect interpretation. Keep presentation styling
separate from numerical computation where practical.

Use consistent notation across code, reports, and manuscripts. Verify sources
before citing them, and distinguish repository results from published results.

## Tests and change discipline

Use pytest files named `tests/test_<feature>.py`, deterministic seeds, and
tolerances justified by the numerical method. Select applicable tests:

- formula, edge-case, and regression tests;
- symmetry, conservation, Hermiticity, normalization, or positivity checks;
- exact-limit or independent-implementation comparisons;
- serialization round trips and deterministic plotting-data tests;
- HPC array-partitioning tests and reduced integration smoke tests.

For a bug, add a failing regression test first when practical. Never weaken a
valid test to fit a change. Tests must not require a production Zeus run.

Before editing, inspect the scientific contract, relevant call sites, existing
outputs, and serialized formats. Avoid unrelated refactoring or formatting.
After editing, inspect the diff, run focused checks, broaden when feasible, and
state unperformed validation and remaining uncertainty.

Backward compatibility does not justify preserving a scientific error. Make a
necessary break explicit and provide a migration path when practical.

## Zeus and expensive computation

For any request to prepare, synchronize, submit, monitor, recover, collect, or
post-process a production Zeus campaign, invoke and follow `$zeus-hpc` from
`.agents/skills/zeus-hpc/SKILL.md` before remote mutation. Large simulations
belong on Zeus; local execution is limited to validation and reduced smoke
cases.

Production submission requires explicit user authorization. Use the documented
`hpc/` wrapper and a fresh output root. Never cancel, resubmit, change resources,
or overwrite a campaign without authorization for that action. Production code
and configuration should be committed and pushed before submission so results
can name a commit; when the remote tree is not Git-backed, record verified
source hashes instead.

## Git delivery

This section is standing authorization to commit and push successfully
completed, in-scope change/build/fix work and to integrate its task branch into
the default branch with a non-fast-forward merge. It also authorizes deleting
that agent-owned task branch locally and from its configured remote after the
merge is pushed and verified. It does not authorize deleting other branches,
creating or merging a pull request, rewriting shared history, force-pushing,
publishing a release, or including unrelated user changes.

1. At task start, inspect branch, upstream, remotes, and `git status --short`.
   Identify pre-existing changes and preserve their ownership.
2. On the default branch, create a focused `codex/<topic>` branch for
   substantive work unless the user explicitly requests a direct default-branch
   update. Reuse an existing task branch when it clearly owns the work.
3. Keep commits cohesive and reviewable. Separate unrelated prior work from the
   current task, and separate scientific implementation from instruction-only
   maintenance when that improves review.
4. Stage explicit paths, inspect `git diff --cached`, and check for secrets,
   local paths, generated bulk data, and accidental edits. Do not use a broad
   staging command when the worktree contains unrelated changes.
5. Commit only after applicable validation passes. Use a concise imperative
   subject such as `Add hz0 resonance atlas` or `Validate detector response`.
6. Push the current task branch with its upstream (`git push -u origin HEAD`).
   Never force-push. If the push is rejected or the remote advanced, fetch and
   inspect; do not silently rebase or discard work.
7. For a completed task branch, update the local default branch with
   fast-forward-only pull, merge the task branch using `git merge --no-ff`, and
   push the default branch. Preserve the merge commit even when a fast-forward
   would be possible. Stop before resolving unexpected conflicts or overwriting
   remote work; report the conflicting paths and request direction.
8. After the default-branch push succeeds, verify that the task commit is an
   ancestor of both the local and remote-tracking default branches. Then delete
   only the now-redundant agent-owned task branch from its remote and locally,
   using ordinary non-force deletion. Never delete the default branch, a
   protected branch, a branch checked out in another worktree, an unmerged
   branch, or a branch whose ownership or purpose is ambiguous. If either
   deletion is rejected, preserve the branch and report why; do not force it.
9. Report the task and default branches, commit and merge hashes, pushed
   remote, deleted branch names, validations, generated but uncommitted
   outputs, and limitations.

Do not create an empty commit. Do not commit incomplete or failing work merely
to satisfy this policy; explain the blocker instead. Read-only tasks do not
produce a commit. Create or merge a pull request only when the user asks; the
default delivery path is the explicit local `--no-ff` integration above.

Pull-request descriptions should include the scientific objective, changed
equations or conventions, implementation choices, exact validation commands
and results, convergence or sensitivity evidence, generated-output paths,
Zeus resource implications, and unresolved limitations. Pair representative
figures with quantitative evidence.

## Definition of done

A task is done when the applicable conditions hold:

- requested behavior is implemented in the correct location;
- equations, conventions, approximations, and validity regime are explicit;
- focused tests and numerical checks pass;
- provenance and stochastic seeds are recorded;
- expensive computation stayed within its authorization boundary;
- prior data are preserved and new outputs are uniquely identified;
- the diff excludes secrets, machine-specific clutter, and unrelated changes;
- exact, approximate, numerical, and conjectural conclusions remain distinct;
- completed changes are organized into scoped commits, pushed, and integrated
  with a non-fast-forward merge;
- the redundant agent-owned task branch is deleted locally and remotely after
  its integration is verified, unless a documented safety check prevents it;
- the final report names what was and was not validated.

If a condition is inapplicable, do not create work merely to satisfy the list.
If completion is blocked, deliver the best verified partial result and name the
precise blocker.
