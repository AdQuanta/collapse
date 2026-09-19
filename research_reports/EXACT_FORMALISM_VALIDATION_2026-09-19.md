# Exact collapse formalism: validation candidate

**Date:** 2026-09-19  
**Status:** DRAFT_PASS; activation and independent certification review pending  
**Gate:** Exact collapse-like formalism remains INCOMPLETE; paper_ready=false  
**Code:** 2626a878de11dd96c09ef3274b5a5f10606766af plus the saved working-tree patch and source snapshots

## Result and scope

The new `reconstruct_collapse_state(U, outcome, alpha, beta, detector_state)` API
normalizes valid inputs and reports direct state reconstruction without assigning
any readiness verdict. Its retained detector branch is not renormalized.
The [dimension-independent proof and proposed contract](../verifier/exact_formalism/v1/METHOD.md)
show that the forbidden-branch kernel equation is necessary and sufficient for
exact factorization, including infinity, degenerate kernels and singular pencils.
The same proof explains antipodal pairing with equal kernel dimensions.

The independent draft checker passes all 122 fixture records: 88 valid states
and 34 expected rejections. Maximum positive-state forbidden-branch norm is
5.291901841267055e-16; maximum retained-norm error is 2.220446049250313e-16; maximum
unitarity error is 1.0420220379717926e-15. All proposed absolute tolerances are 1e-12.
Six symbolic identity checks pass. None of these results certifies root
completeness, general multiplicity detection, a singular-continuum measure,
Born statistics, or a physical Hamiltonian candidate.

| Fixture | States | Expected result | Maximum forbidden-branch norm |
|---|---:|---|---:|
| identity | 8 | Accepted state | 0.000000e+00 |
| qnd | 8 | Accepted state | 0.000000e+00 |
| generic | 8 | Accepted state | 4.986840e-16 |
| semisimple | 8 | Accepted state | 4.019672e-17 |
| kernel_superposition | 2 | Accepted state | 4.019672e-17 |
| defective | 2 | Accepted state | 2.684341e-17 |
| swap | 12 | Accepted state | 0.000000e+00 |
| homogeneous_rescaling | 8 | Accepted state | 5.291902e-16 |
| detector_basis_change | 8 | Accepted state | 5.023874e-16 |
| spectator | 24 | Accepted state | 4.989019e-16 |
| wrong_outcome | 8 | Expected rejection | 1.000000e+00 |
| wrong_coordinate_order | 8 | Expected rejection | 9.162975e-01 |
| perturbed_detector | 8 | Expected rejection | 8.380670e-02 |
| nonunitary | 8 | Expected rejection | 5.040140e-16 |
| near_collapse | 2 | Expected rejection | 1.000000e-06 |

## Tests and negative evidence

The final focused suite passes 26 tests. The full suite gives **641 passed,
2 failed**, with one existing NumPy matrix deprecation warning. Both failures
reproduce when the unchanged Git HEAD version of `core/projective_roots.py`
is loaded in memory instead of the working version:

- Matched-ring forward bridge: 3.907827153052709e-09 against 2e-11.
- Zero-field independent-spin angle comparison: 5.025573734940281e-09 against 1e-12.

The baseline comparison ran those exact two tests with every threshold unchanged.
It establishes that these are not regressions introduced by this reconstruction
API. It does not certify the surrounding numerical pipeline. Independent review
must decide whether both failures are separable from the single formalism gate.

An initial full-suite attempt stopped with two collection errors because copied
Python tests in the first evidence packet were discovered as duplicate modules.
That log is retained in `reports/exact_formalism/2026-09-19-candidate-v1/pytest-collection-failure.txt`.
Source snapshots now use non-executable `.snapshot` suffixes; no scientific
criterion or numerical tolerance changed. The initial packet remains superseded
by the review packet. Byte-for-byte state-data hashes agree between the packets.

Compilation passes. The scoped diff has no whitespace errors; global
`git diff --check` reports a pre-existing trailing blank line in the user's
modified `wiki/methods/homogeneous-qz.md`, left untouched by this task.

## Figures

The [wiki figure gallery](../wiki/campaigns/exact-collapse-formalism.md) embeds all
15 PNG panels. Corresponding vector PDFs and numerical histogram data are in
the packet. The figures show both separately normalized polar histograms and
their supported-bin ratio against cos(theta/2)^2, using 18 fixed bins and no
pseudocounts. Empty bins are marked undefined. Both generic outcome pencils are
solved independently; the antipodal relationship is a cross-check.

Analytically known fixtures use the correct supplied kernel weights. SWAP uses
six representative rays for each outcome and is explicitly labeled as a sample:
its continuum probability measure is undefined. Selected kernel-superposition
plots are incomplete samples. Negative-control plots contain rejected input
rays, not outcome measures. Invalid input dimensions and zero rays cannot have
theta distributions and are covered by rejection tests instead. No plotted
agreement is a Born or estimator-robustness result.

## Reproduce

In the pinned Python 3.11 environment:

```sh
python3.11 -m pytest -q tests/test_collapse_state_reconstruction.py tests/test_exact_formalism_verifier.py
python3.11 scripts/build_exact_formalism_packet.py --output reports/exact_formalism/NEW_REVIEW_DIRECTORY
python3.11 verifier/exact_formalism/v1/check.py --packet reports/exact_formalism/NEW_REVIEW_DIRECTORY --log reports/exact_formalism/verifier_log.jsonl
```

This session used `PYTHONPATH=/private/tmp/collapse_py311_deps`,
`NUMBA_CACHE_DIR=/private/tmp/collapse_numba_cache`, and
`MPLCONFIGDIR=/private/tmp/collapse_matplotlib_cache`. The builder refuses to
overwrite any packet directory. Reconstruct the saved code state from the
recorded commit, binary working-tree patch, then source copies with the
`.snapshot` suffix removed. Verify hashes against provenance.json.

[Review packet](../reports/exact_formalism/2026-09-19-candidate-v1-review/)
contains states.npz, cases.json, reconstruction.json, plot_data.json,
provenance.json, working-tree.patch, source snapshots, review_manifest.json,
review_result.json, and focused/full/baseline test logs.
The append-only experiment and verifier logs retain failed and successful runs.
A separate delivery manifest hashes all packet artifacts, including plots and logs.

## Approval boundary

The proposed verifier is `exact-formalism-v1-candidate`; its
[manifest](../verifier/exact_formalism/v1/manifest.json) is explicitly
`draft-awaiting-approval`. The checker only emits DRAFT_PASS or DRAFT_FAIL and
`certification=false`. No readiness gate has changed.

SPEC section 0.1 requires explicit approval before activation. After approval:
freeze an activated version, rerun certification from fresh fixtures, obtain an
independent fresh-context referee review of the proof, evidence, limitations and
both baseline failures, then promote only the exact-formalism row if both layers
pass. All other rows and paper_ready remain unchanged.
