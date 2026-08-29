# AGENTS.md — Theoretical and Numerical Physics Research

## Purpose and Priority

This repository contains Python research code for theoretical and numerical physics. Work in this repository must prioritize, in order:

1. physical and mathematical correctness;
2. reproducibility and traceability;
3. numerical reliability and explicit validation;
4. clear, maintainable Python that follows pragmatic SOLID design;
5. computational efficiency after correctness is established.

Repository-specific instructions in this file take precedence over generic preferences. A more deeply nested `AGENTS.md` may refine these rules for its subtree, but should not silently weaken scientific-integrity, safety, or reproducibility requirements.

Do not invent results, references, parameter values, conventions, validation outcomes, or successful command output. Distinguish clearly between exact statements, approximations, numerical evidence, conjectures, and implementation choices.

## Repository Structure

Use the existing layout consistently:

- `core/`: reusable physics models, analytical helpers, numerical algorithms, analysis utilities, serialization, and plotting code;
- `scripts/`: executable studies, parameter sweeps, report-building entry points, and thin orchestration scripts;
- `configs/`: versioned parameter sets and run configurations;
- `hpc/`: PBS job scripts, submission wrappers, and Zeus campaign utilities;
- `tests/`: pytest unit, regression, integration, and smoke tests;
- `manuscript/`: PRL-style manuscript, supplement, figures, provenance, and audits;
- `reports/`: research reports and manuscript-related sources;
- `figures/`: curated figures intended for reports or presentations;
- `presentations/`: presentation sources and assets;
- `work/`, `output/`, `tmp/`: generated, intermediate, or scratch data;
- `archive/`: legacy material, not active source code.

Place reusable logic in `core/`, not in notebooks or large entry-point scripts. Keep `scripts/` scripts thin: parse configuration, call library functions, save outputs, and report provenance. Do not import active code from `archive/`, `work/`, `output/`, or `tmp/`.

Before adding a new module, inspect nearby modules and tests. Extend an established abstraction when it fits; do not create a parallel framework for the same concept.

## Environment and Standard Commands

Use Python 3.11, matching the Zeus environment.

Typical macOS setup:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install numpy scipy matplotlib pytest
python -m pytest -q
```

Useful focused checks:

```bash
.venv/bin/python -m pytest -q tests/test_detector_resonance.py
.venv/bin/python -m pytest -q tests/test_<feature>.py
.venv/bin/python -m py_compile path/to/script.py
.venv/bin/python scripts/<script>.py --help
```

Use documented scripts in `hpc/` for Zeus campaigns. Do not bypass established submission wrappers unless the task explicitly requires changing them.

Run the narrowest relevant checks first, then broaden validation. Never claim a command passed unless it was actually run and its exit status and output were inspected.

## Scientific Workflow

For substantive physics changes, follow this sequence:

1. State the physical question and observable.
2. Record assumptions, approximations, conventions, and validity regime.
3. Derive or identify the governing equations independently of implementation details.
4. Identify exact checks, limiting cases, symmetries, conservation laws, and expected scaling.
5. Choose a numerical representation and explain its error sources.
6. Implement the smallest testable change.
7. Validate against analytical results, independent formulations, or trusted benchmarks.
8. Perform convergence, stability, or sensitivity checks appropriate to the method.
9. Save enough metadata to reproduce the result.
10. Report unresolved limitations honestly.

Do not tune code merely to reproduce a desired plot or conclusion. When evidence contradicts an expectation, preserve and report the contradiction.

## Theoretical Physics Standards

### Conventions and assumptions

Every derivation or theory-facing implementation must make relevant conventions explicit, including as applicable:

- units and whether quantities are dimensional or nondimensionalized;
- metric, Fourier-transform, phase, and sign conventions;
- basis ordering, tensor-index ordering, and matrix layout;
- boundary and initial conditions;
- normalization of states, distributions, transforms, and observables;
- gauge choice and residual gauge freedom;
- operator domains, Hermiticity assumptions, and inner products;
- branch choices for logarithms, roots, phases, and inverse functions;
- treatment of degeneracies, resonances, zero modes, and singular limits.

Do not silently change conventions to make an equation or test pass. If existing code uses inconsistent conventions, isolate the inconsistency, document it, and fix it with regression tests.

### Exact versus approximate statements

Label expressions as exact, asymptotic, perturbative, heuristic, fitted, or numerical. For approximations, state:

- the small or large parameter;
- the retained order;
- the neglected terms or expected remainder;
- the regime in which the approximation is controlled;
- known failure modes, especially near resonances or singular points.

Do not use perturbation theory across a vanishing denominator without an explicit degenerate, resonant, resummed, or regularized treatment. Do not infer a continuum identity solely from finite-size agreement.

### Derivation checks

Whenever applicable, verify:

- dimensional consistency;
- symmetry transformations and selection rules;
- conservation laws and Ward-like identities;
- Hermiticity, positivity, unitarity, or normalization;
- limiting cases and exactly solvable regimes;
- equivalence under relabeling of dummy indices;
- consistency between component, matrix, operator, and spectral forms;
- asymptotic scaling and expected parameter dependence.

Use symbolic algebra as a verification aid, not as a substitute for reasoning. Record assumptions supplied to symbolic simplifiers. Numerically spot-check symbolic identities at nonsingular parameter points when practical.

### Theory-to-code correspondence

A numerical object must be traceable to the mathematical object it represents. Use names and docstrings that connect code variables to equations, operators, basis states, parameters, and observables. When implementing a published or report-specific formula, cite the local equation, section, or source in the docstring or nearby comment where useful.

Keep analytical definitions separate from numerical discretizations. For example, distinguish a continuum operator from its finite-dimensional matrix representation and distinguish the physical model from a particular solver.

## Numerical Physics Standards

### Numerical validity

Numerical output is evidence only after relevant error sources have been assessed. Depending on the calculation, examine:

- grid, basis, truncation, cutoff, or system-size convergence;
- timestep or solver-tolerance convergence;
- finite-volume and boundary effects;
- quadrature error and tail truncation;
- residual norms and backward error;
- condition numbers or sensitivity to perturbations;
- Monte Carlo sampling error, autocorrelation, burn-in, and seed dependence;
- optimizer initialization and local-minimum sensitivity;
- floating-point precision and cancellation;
- regularization and extrapolation dependence.

Do not claim convergence from a single resolution. Prefer at least three systematically refined values when establishing an order or extrapolating a limit. If cost prevents a full study, state that the result is provisional.

### Stable linear algebra

- Prefer `numpy.linalg.solve` or an appropriate factorization over explicit matrix inversion.
- Use Hermitian/symmetric routines such as `eigh` when their assumptions hold.
- Check residuals, not only returned status flags.
- Preserve structure such as sparsity, Hermiticity, block form, or positive definiteness.
- Avoid forming dense matrices when a matrix-free operator is sufficient.
- Treat near-degeneracy and eigenvector phase/sign ambiguity explicitly.
- Sort or match spectra by a physically justified rule, not by fragile raw indices.

### Method-specific expectations

For ODEs and time evolution, document solver, tolerances, conserved quantities, stiffness considerations, and timestep sensitivity. For PDEs, document discretization, boundary conditions, stability restrictions, resolution, and continuum checks. For eigenproblems, validate residuals, orthogonality, symmetry sectors, degeneracies, and spectral ordering. For quadrature, inspect convergence, singular points, oscillatory tails, and domain truncation. For root finding and optimization, inspect residuals, constraints, initialization sensitivity, and alternative branches. For Monte Carlo or stochastic methods, pass explicit generators, save seeds, quantify uncertainty, and use more than one seed when conclusions depend on stochastic variation.

### Validation hierarchy

Prefer several independent checks rather than one elaborate check:

1. exact identities and invariants;
2. analytically solvable limits;
3. independent formulations or algorithms;
4. published or previously validated benchmarks;
5. convergence and sensitivity studies;
6. qualitative physical behavior.

A visually plausible figure is not sufficient validation.

## Python Design and SOLID Principles

Use pragmatic SOLID design to improve scientific clarity and testability. SOLID does not mean turning every function into a class or introducing factories without a concrete need. Prefer the simplest design that separates responsibilities and supports verification.

### Single Responsibility Principle

A module, class, or function should have one coherent reason to change. Separate, where practical:

- physical model definitions;
- analytical formulae and derived quantities;
- numerical solvers and discretizations;
- configuration parsing and validation;
- data loading and serialization;
- plotting and presentation;
- command-line orchestration;
- HPC submission logic.

A function that constructs a Hamiltonian should not also submit a PBS job, write figures, and mutate global configuration. Break long research scripts into importable functions before adding more behavior.

### Open/Closed Principle

Design stable core behavior so new models, observables, solvers, boundary conditions, or output formats can often be added through composition, callables, configuration, or small interfaces rather than repeated edits to a central conditional block.

Do not force extensibility prematurely. Introduce an abstraction after at least one real variation exists or when a second implementation is part of the current task.

### Liskov Substitution Principle

Subtypes and implementations must preserve the documented contract of the abstraction they implement. They must not silently narrow accepted domains, change units, alter normalization, weaken numerical guarantees, or return incompatible shapes and types.

If two solvers have materially different assumptions or guarantees, express those differences in separate interfaces or explicit capabilities rather than hiding them behind a misleading common base class.

### Interface Segregation Principle

Prefer small, role-specific interfaces. Use `typing.Protocol`, callables, or narrow abstract base classes only when multiple implementations benefit from a shared contract. Do not require a physics model to implement plotting, persistence, optimization, and time evolution merely to supply an operator or right-hand side.

### Dependency Inversion Principle

Keep high-level scientific workflows independent of concrete I/O, random-number sources, optimizers, solvers, and storage backends. Inject these dependencies as arguments or configuration where substitution improves testing or scientific comparison.

Pass `numpy.random.Generator` objects explicitly. Allow core calculations to receive callables or protocol-typed dependencies rather than constructing global singletons internally.

### Composition and functional core

Prefer composition over deep inheritance. Use:

- pure functions for equations, kernels, transformations, and observables;
- frozen dataclasses for validated immutable parameter sets;
- small stateful objects only when genuine lifecycle or cached state exists;
- explicit orchestration at the repository boundary.

Avoid global mutable state, import-time computation, hidden caches, and implicit environment-dependent behavior. Any cache that affects scientific output must include all relevant parameters in its key and have a clear invalidation rule.

## Python Style and API Conventions

Follow PEP 8 with four-space indentation. Match surrounding code because no formatter is currently enforced, and avoid unrelated reformatting.

Use:

- `snake_case` for modules, functions, variables, and filenames;
- `PascalCase` for classes and dataclasses;
- `UPPER_SNAKE_CASE` for constants;
- type hints for public APIs and nontrivial internal interfaces;
- `pathlib.Path` for filesystem paths;
- NumPy-style array shape and dtype documentation where ambiguity is possible;
- explicit keyword arguments for tolerances, conventions, units, and algorithm choices.

Public functions should document physical meaning, parameter units or nondimensionalization, accepted shapes, return values, conventions, and important failure modes. Prefer domain-specific exceptions or clear `ValueError` messages over silent clipping or fallback behavior.

Do not use mutable default arguments. Avoid wildcard imports. Avoid boolean flags that produce substantially different algorithms; use separate functions, enums, or strategy objects when clearer.

Vectorize only when it improves clarity or measured performance. Do not replace a transparent correct implementation with an opaque optimization without benchmarks and regression tests.

## Configuration and Reproducibility

Version research parameters in `configs/`. Configuration files should be human-readable, validated, and sufficient to identify the calculation. Do not bury scientifically relevant constants inside scripts.

Every saved result should include, as applicable:

- configuration or a complete copy of effective parameters;
- code version or Git commit when available;
- Python and relevant dependency versions;
- random seeds;
- solver and tolerance settings;
- discretization, basis, cutoff, and system size;
- units and normalization conventions;
- timestamp and output schema version.

A default seed is not a substitute for recording the seed actually used. Do not rely on iteration order, unspecified parallel scheduling, or ambient environment variables for reproducibility.

Changing a default that can alter scientific results is an API and research-method change. Document it and add regression coverage.

## Testing Requirements

Tests use pytest. Follow `tests/test_<feature>.py`, with test names describing expected behavior.

For scientific changes, add the most relevant combination of:

- unit tests for formulas, transformations, and edge cases;
- regression tests for corrected equations or previous failures;
- invariant/property tests for symmetry, normalization, conservation, Hermiticity, positivity, or reversibility;
- comparison tests against exact limits or independent implementations;
- serialization round-trip tests;
- deterministic plotting-data tests when visual output changes;
- job-array partitioning tests for HPC changes;
- small-system integration or smoke tests.

Use deterministic seeds and explicit floating-point tolerances. Choose tolerances from numerical error analysis or method behavior, not merely large enough to pass. Prefer `numpy.testing` helpers and state whether comparisons are absolute, relative, or norm-based.

Tests must not require production-scale Zeus jobs. Validate expensive campaigns with dry runs or small systems locally, but do not present those as production-scale scientific evidence.

When fixing a bug, first add a test that fails for the bug when practical. Do not weaken or delete a valid test to accommodate a code change.

## HPC and Performance Safety

Production computation is expensive and potentially destructive. Unless explicitly requested:

- do not submit PBS jobs;
- do not cancel or alter existing jobs;
- do not launch large local simulations or parameter sweeps;
- do not overwrite campaign outputs;
- do not change queue, walltime, memory, array size, or resource requests speculatively.

Before a new Zeus campaign:

1. validate configuration parsing;
2. run `--help`, dry-run, or equivalent inspection;
3. run a small-system smoke test;
4. estimate memory, runtime, output volume, and array size;
5. verify output paths and checkpoint behavior;
6. verify each array index maps to a unique parameter shard;
7. use the documented `hpc/` wrapper.

Checkpoint long runs after each requested system size or other natural unit of work. Make restart behavior idempotent and ensure partial results are not mistaken for completed results.

Optimize only after profiling representative workloads. Preserve a clear reference implementation when introducing complex acceleration. Benchmark with fixed inputs and report accuracy changes as well as speed changes.

## Results, Figures, and Data Safety

Preserve downloaded Zeus data, previous reports, and curated results. Treat existing outputs as immutable unless the task explicitly authorizes replacement.

Write derived outputs to a new descriptive or timestamped directory. Never silently reuse an output directory whose contents could be confused with a different configuration. Avoid embedding local absolute paths in source, configuration, reports, or metadata intended for sharing.

Do not commit caches, virtual environments, logs, temporary files, or bulk generated data excluded by `.gitignore`. Never commit credentials, tokens, private keys, or secrets.

Figures must be generated from traceable data and scripts. Label axes, units, parameters, and normalization. Do not smooth, crop, filter, or select data in a way that changes interpretation without recording the operation. Keep presentation-only styling separate from the numerical computation where practical.

## Reports, Mathematics, and Citations

Maintain notation consistently across code, reports, figures, and presentations. When changing an equation in code, inspect related tests, reports, captions, and configuration documentation.

Do not fabricate citations or claim that a paper supports a statement without checking it. Mark unpublished reasoning, conjectures, and heuristic arguments as such. Preserve distinctions between results derived in this repository and results taken from external sources.

Generated tables and figures should be reproducible from committed code and recorded configurations, even when the large raw data remain outside Git.

## Change Discipline

Make the smallest coherent change that solves the task. Do not refactor unrelated code, rename broad APIs, rewrite configurations, or reformat entire files without a clear need.

Before editing:

- inspect relevant modules, tests, configurations, and call sites;
- identify the scientific contract and existing conventions;
- check whether outputs or serialized formats are relied upon elsewhere.

After editing:

- inspect the diff for accidental changes;
- run focused tests and syntax checks;
- run broader tests when feasible;
- state exactly what was and was not validated;
- record any remaining numerical or scientific uncertainty.

Do not preserve backward compatibility blindly if it would preserve a scientific error. When a correction breaks compatibility, make the change explicit, document the reason, and provide a migration path when practical.

## Git and Pull Requests

This repository has no established commit-history convention. Use concise imperative commit subjects, for example:

```text
Add hz0 resonance atlas
Fix eigenvalue matching near degeneracy
Validate detector response convergence
```

Keep commits scoped. Do not commit generated bulk data or unrelated edits.

Pull requests should state:

- the scientific objective;
- equations, assumptions, parameters, or conventions changed;
- implementation and design choices;
- validation commands and observed results;
- convergence or sensitivity evidence;
- generated-output paths;
- Zeus resource implications;
- limitations and unresolved questions.

Include representative figures when visual behavior changes, but accompany them with quantitative validation.

## Definition of Done

A task is complete only when the applicable items below are satisfied:

- the requested behavior is implemented in the correct repository location;
- the implementation matches stated equations, conventions, and validity assumptions;
- code follows pragmatic SOLID principles without unnecessary abstraction;
- public interfaces are typed and documented appropriately;
- relevant regression, invariant, and edge-case tests exist;
- focused tests and syntax checks pass;
- numerical claims include appropriate residual, convergence, stability, or sensitivity evidence;
- stochastic results record seeds and uncertainty;
- expensive computation was not launched without authorization;
- prior data and reports were preserved;
- outputs are written to unique, traceable paths with sufficient provenance;
- the diff contains no credentials, local paths, generated clutter, or unrelated changes;
- exact, approximate, numerical, and conjectural conclusions are clearly distinguished;
- any unperformed validation or unresolved limitation is stated explicitly.

When these conditions cannot all be met, provide the best verified partial result and explain precisely what remains unverified.
