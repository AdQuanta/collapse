# Claude Code instructions: unitary-collapse research program

You are working inside the `AdQuanta/collapse` research repository. Treat the repository's code,
raw data, tests, evidence registries, and current handoff reports as the executable source of truth.
This overlay is scientific memory and research guidance, not permission to override the code.

## Start here, every session

Read `AGENTS.md`, then read `RESEARCH_STATE.md`. Use the `wiki/` directory for deep-dive conceptual synthesis and navigation.

`RESEARCH_STATE.md` is the **canonical shared research memory** for this project: it carries the
project-wide scientific context, current hypotheses, evidence status, and priorities across Ido,
Claude Code, ChatGPT/Codex, and future agents. Work to the priorities it declares.

It is canonical, not infallible. Also weigh what you know from the current conversation and from the
repository itself, and **argue the point whenever they conflict** — with the user, and in writing here.
Inspect the linked repository files before making claims; `AGENTS.md` and the validated repository
documents remain authoritative for implementation details and derivations.

Update `RESEARCH_STATE.md` whenever a discussion, calculation, or decision changes the scientific
state, the priorities, or the evidence — before ending the session. Tag every entry with an evidence
label and never silently promote a conjecture to a result.

## Mandatory reading order before substantive work

1. `AGENTS.md`
2. `RESEARCH_STATE.md`
3. `wiki/index.md`
4. `README.md`
5. `manuscript/EVIDENCE_REGISTRY.md`
6. `manuscript/NUMERICAL_PROVENANCE.md`
7. `manuscript/RESULTS_NEEDED.md`
8. `manuscript/audits/NUMERICAL_AUDIT.md`
9. `manuscript/audits/THEORY_AUDIT.md`

If HEAD is newer than the last update recorded in `RESEARCH_STATE.md`, inspect
the intervening commits and recent validated results before assuming the memory
file is current.

## Scientific rules

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

## Coding rules

- First reproduce existing anchor calculations and tests. Do not refactor first.
- Prefer existing service modules and versioned JSON configs over ad-hoc scripts.
- Every new scientifically meaningful campaign must record parameters, git SHA, random seeds,
  software versions, sizes, times, runtime, completion status, raw-data paths, and analysis version.
- Do not form inverse matrices when a generalized eigenvalue/QZ formulation exists.
- Preserve projective roots at infinity and singular/indeterminate-pencil diagnostics.
- Never concatenate symmetry sectors for level-spacing statistics.
- Production-size runs are not unit tests.
- Record new claims and campaigns in the existing evidence/provenance
  registries and follow the metadata contract in `AGENTS.md`.

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
