# Claude Code instructions: unitary-collapse research program

You are working inside the `AdQuanta/collapse` research repository. Treat the repository's code,
raw data, tests, evidence registries, and current handoff reports as the executable source of truth.
This overlay is scientific memory and research guidance, not permission to override the code.

**Mission Priority:** Prioritize physical correctness, reproducibility, numerical reliability,
maintainable Python, then performance. Never invent results, parameters, citations, validation, 
or command output. Label exact, approximate, fitted, numerical, heuristic, and conjectural claims distinctly.

## Start here, every session

Read `RESEARCH_STATE.md`. Use the `wiki/` directory for deep-dive conceptual synthesis and navigation.

`RESEARCH_STATE.md` is the **canonical shared research memory** for this project: it carries the
project-wide scientific context, current hypotheses, evidence status, and priorities across Ido,
Claude Code, ChatGPT/Codex, and future agents. Work to the priorities it declares.

It is canonical, not infallible. Also weigh what you know from the current conversation and from the
repository itself, and **argue the point whenever they conflict** — with the user, and in writing here.
Inspect the linked repository files before making claims; validated repository
documents remain authoritative for implementation details and derivations.

Update `RESEARCH_STATE.md` whenever a discussion, calculation, or decision changes the scientific
state, the priorities, or the evidence — before ending the session. Tag every entry with an evidence
label and never silently promote a conjecture to a result.

## Mandatory reading order before substantive work

1. `RESEARCH_STATE.md`
2. `wiki/index.md`
3. `README.md`
4. `manuscript/EVIDENCE_REGISTRY.md`
5. `manuscript/NUMERICAL_PROVENANCE.md`
6. `manuscript/RESULTS_NEEDED.md`
7. `manuscript/audits/NUMERICAL_AUDIT.md`
8. `manuscript/audits/THEORY_AUDIT.md`

If HEAD is newer than the last update recorded in `RESEARCH_STATE.md`, inspect
the intervening commits and recent validated results before assuming the memory
file is current.

## Project Architecture

### Directory Map
- `core/`: reusable models, equations, solvers, analysis, serialization, plots.
- `scripts/`: thin configuration, orchestration, persistence, provenance CLIs.
- `configs/`: versioned and validated scientific parameters.
- `hpc/`: Zeus PBS files, submission wrappers, campaign runbooks.
- `tests/`: unit, regression, integration, and smoke tests.
- `manuscript/`, `reports/`, `figures/`, `presentations/`: research outputs.
- `work/`, `output/`, `tmp/`: generated data; never import active code from them.
- `archive/`: legacy material; never import it as active code.

### Primary Skills
- `zeus-hpc`: prepare, synchronize, submit, monitor, recover, collect, or post-process a production Zeus campaign.
- `high-impact-academic-scientific-writing`: draft, revise, restructure, or critique scientific manuscripts, sections, captions, and reviewer responses.

## Scientific Standards

### The Scientific Contract
Before substantive theory or numerical work, establish these in the relevant code, tests, or research artifact:
1. **Physical context**: Question, observable, units, and validity regime.
2. **Conventions**: Basis/tensor ordering, signs, phases, normalization, boundaries, gauge, branches, degeneracies, and zero modes.
3. **Governing equations**: Defined independently of implementation; separate analytical definitions from discretizations.
4. **Validation logic**: Applicable exact limits, symmetries, conservation laws, and scaling checks before implementation; identify material error sources.

### Numerical Reliability
- **Error Analysis**: Check material errors for the method: basis/grid/cutoff/size/timestep/tail and tolerance dependence; finite volume/boundaries; precision, cancellation, conditioning; residuals, backward error, orthogonality, spectral matching and symmetry sectors; quadrature/regularization; optimization branches/initialization; Monte Carlo uncertainty, autocorrelation, burn-in, and seeds.
- **Convergence**: Do not claim convergence from one resolution. Prefer at least three systematic refinements for orders or extrapolation; label results provisional if cost prevents adequate evidence. Name unchecked error sources.
- **Linear Algebra**: Preserve matrix structure (e.g., Hermitian routines for Hermitian problems). Prefer factorizations or `solve` over matrix inversion. Handle near-degeneracy and eigenvector phase ambiguity explicitly.
- **Stochastics**: Pass `numpy.random.Generator` explicitly. Save actual seeds and quantify stochastic uncertainty. Use multiple seeds when conclusions depend on a realization.

### Core Constraints
- Never turn a numerical trend into a theorem.
- Never call a result "Born" merely because one scalar score is favorable. Distinguish polar
  screening scores, full-sphere asymmetry/harmonics, direct density-ratio residuals, and any
  operational probability statement.
- Endpoint pole projection is built into the special-state construction. It is **not** a discriminator
  between Born-producing and non-Born Hamiltonians.
- Gleason/Busch is downstream. It constrains probability assignments and does not classify
  Hamiltonians.
- "Chaos" is not the working explanation. Current data explicitly show that indiscriminate scrambling
  can coexist with uniform/non-Born root geometry, and that several useful candidate structures are
  more specific than chaos.
- Poisson statistics do not imply MBL. Resolve exact symmetries before level-statistics analysis and
  pair spectral diagnostics with eigenvector/dynamical diagnostics.
- The physically realized special set is generically not closed under superposition. Do not silently
  restore universal physical superposition as an assumption.
- Keep ontology separate from mathematics. Superselection, superdeterminism, primordial selection,
  or an unknown attracting dynamics are possible interpretations, not established mechanisms.

## Coding Standards

### Implementation (SOLID)
Apply all five SOLID principles to all new/modified code:
- **Single responsibility**: Separate models, solvers, config, I/O, plotting, CLI, and HPC submission.
- **Open/closed**: Extend behavior through composition/strategies; avoid spreading algorithm-selection conditionals.
- **Liskov substitution**: Honor documented contracts (domains, units, normalization, shapes, error behavior).
- **Interface segregation**: Expose only the capabilities each caller needs; prefer focused protocols.
- **Dependency inversion**: Keep scientific policy independent of concrete solver/RNG/storage implementations.

### Python & Validation
- **Conventions**: Python 3.11, type hints for nontrivial interfaces, `pathlib.Path`, explicit tolerance keywords, and domain-aware docstrings.
- **Anti-patterns**: Avoid mutable defaults, wildcard imports, global mutable state, import-time computation, and hidden caches.
- **Testing**: First reproduce existing anchor calculations. Use `tests/test_<feature>.py`, deterministic seeds, and method-justified tolerances. Add failing regressions for bugs. Production-size runs are not unit tests.
- **Verification**: Use `py_compile`, `pytest` (narrow scope first), and inspect exit status/output before reporting success.

## Research Operations

### Provenance & Outputs
- **Parameters**: Keep in validated, human-readable `configs/` files.
- **Metadata**: Record effective config/schema version, Git commit/source hashes, Python/dependency versions, seed, solver, tolerance, discretization, basis, cutoff, size, units, and timestamp.
- **Data Integrity**: Downloaded Zeus data and curated results are immutable. Use new descriptive/timestamped directories for derived outputs.
- **Figures**: Trace figures to code and data. Label axes, units, parameters, normalization; record smoothing, filtering, or cropping.

### Execution & Communication
- **HPC**: Large simulations belong on Zeus. Local runs are for validation/smoke cases. Production submission requires explicit authorization, a documented `hpc/` wrapper, and a fresh output root.
- **Communication**: Lead with the result and evidence. Use concise connected paragraphs, precise verbs, and technical detail. Avoid promotional adjectives or decorative contrast.
- **Completion (Done)**: The requested outcome is implemented, all scientific/validation requirements are met, prior data is preserved, and authorized Git delivery is verified.

## Git Delivery

Standing authorization covers committing and pushing completed in-scope work.
1. Create `codex/<topic>` branches for substantive work from the default branch.
2. Keep commits cohesive; separate scientific implementation from instruction maintenance.
3. Validate thoroughly before committing.
4. Integrate into the default branch (fast-forward preferred) and delete the task branch.
5. Follow the detailed flow in the repository for remote conflicts and push failures.

## Research loop

For each question:
1. State the hypothesis and its strongest plausible alternative.
2. Identify the cheapest decisive calculation.
3. Define the observable before running it.
4. Reproduce a positive and negative control.
5. Run size/time/seed scaling when feasible.
6. Analyze failure modes and confounds.
7. Update evidence status: PROVED / REPRODUCED_NUMERIC / PRELIMINARY_NUMERIC / FALSIFIED /
   CONJECTURE / SPECULATIVE.
8. Record the activity in `wiki/log.md` and integrate synthesis into relevant `wiki/concepts/` pages.
9. Only then propose manuscript wording.

## Highest-priority scientific objective

Find structural conditions on the Hamiltonian/relative propagator that distinguish a Born-like
special-state point process from the Haar/uniform and strict-QND/no-cloud controls. The most promising
current language combines relative-unitary eigenphases, finite-time detector kernels, resonance/activation,
reciprocal branch balance, symmetry-resolved spectral structure, and information propagation/backflow.
