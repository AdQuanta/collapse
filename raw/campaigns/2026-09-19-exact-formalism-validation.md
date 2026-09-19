# Exact formalism implementation and review packet

Source: repository execution and verifier/exact_formalism/v1/METHOD.md
Collected: 2026-09-19
Published: 2026-09-19

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

---

# Exact collapse formalism: proposed verifier v1

**Status: DRAFT — awaiting explicit activation approval.** This candidate can
produce only `DRAFT_PASS` / `DRAFT_FAIL`; neither certifies a readiness gate.
No previous verifier or SPEC definition is changed.

## Claim and proof

Let U be any unitary on C² tensor Cᵈ, with the qubit first and d finite.
The outcome basis is fixed and orthonormal. A different fixed basis follows by
unitary change of coordinates on the input/output qubit; no preferred-axis
selection is asserted. Write U = [[A,B],[C,D]]. For any nonzero pair (α,β), set
s = sqrt(|α|²+|β|²), q = (β,α)/s and let d₀ be any normalized detector vector.
Direct block multiplication gives

    U(q ⊗ d₀) = |0> ⊗ r₀ + |1> ⊗ r₁,
    r₀ = (βA + αB)d₀/s,    r₁ = (βC + αD)d₀/s.

For either b, projection onto the orthogonal outcome shows necessity:
U(q ⊗ d₀) = |b> ⊗ d′ implies r₁₋ᵦ = 0. Conversely r₁₋ᵦ = 0
leaves exactly |b> ⊗ rᵦ. Orthogonality and unitarity imply

    1 = ||U(q ⊗ d₀)||² = ||r₀||² + ||r₁||²,

so ||rᵦ|| = 1; no normalization or nonzero-output assumption is missing.
Thus the forbidden-branch kernel equation is necessary and sufficient.

This proof never divides by β, takes a matrix inverse, counts roots, or assumes
pencil regularity. It covers α=0, β=0, any vector or superposition in a degenerate
kernel, and kernels present for every projective ray in singular pencils.
For SWAP, SWAP(q ⊗ |b>) = |b> ⊗ q for arbitrary q. The definition remains
valid although it supplies no probability measure on this continuum.
The exact component and SWAP identities are additionally checked with SymPy;
finite symbolic fixtures supplement, rather than replace, the dimension-free proof.

The factorization residual uses the actual, unnormalized retained branch. It
equals the forbidden-branch norm. These are consistency diagnostics, not two
independent mathematical constraints. Retained-branch norm and unitarity are
checked separately. A small numerical residual supports a computed solution;
it does not redefine exact collapse as a high-fidelity event.

## Antipodal relation and plot meaning

Let S = U(q ⊗ Cᵈ) and T = |b> ⊗ Cᵈ. The kernel dimension equals dim(S∩T).
Both subspaces have dimension d in dimension 2d, so

    dim(S∩T) = dim(S-perp ∩ T-perp).

Unitarity identifies their complements as U(q-perp ⊗ Cᵈ) and
|1-b> ⊗ Cᵈ. Hence the opposite-outcome ray is antipodal with equal kernel
dimension. In homogeneous coordinates it is (conj(β), -conj(α)); its polar
angle is π-θ. This relates outcome sets and weights, not their detector vectors.
Both generic forward pencils are nevertheless independently solved in this
packet, and their antipodal pairing is tested. Singular sets still require a
measure decision; antipodal pairing alone does not select one.

Plots use 18 fixed equal-width theta bins on [0,π]. Each outcome histogram is
normalized separately. Ratios use those normalized densities after azimuthal
integration, with no pseudocounts; empty bins remain undefined. The Born curve
is only a reference. Finite-bin ratios at bin centers are not exact pointwise
claims. No histogram is an acceptance gate, estimator study, or Born result.
Identity/QND, semisimple and defective fixtures use analytically supplied distinct
roots and kernel weights. Generic fixtures use their simple QZ roots. Spectator
weights follow tensor-product kernels. Selected kernel superpositions and SWAP
are explicitly incomplete/illustrative samples. Negative-control plots show
rejected input rays, never valid outcome sets. Invalid dimensions or zero rays
have no theta histogram; their rejection is covered by API tests.

## Fixed checks and fixture definitions

All norm checks use absolute tolerance 1e-12 with no relative tolerance. Matrices
are at most dimension 24. Positive records must pass unitarity (spectral norm),
input/output normalization, forbidden-branch norm, retained norm and exact
factorization residual. Saved production outputs must agree with independent
full-matrix propagation. Negative controls must fail their named physical check
and still agree with the independent reconstruction; accidental unrelated
failures cannot satisfy their intended check.

The required case IDs and counts are fixed in check.py. Numerical fixtures:
- Identity and phase-diagonal QND with three detector states plus a complex
  kernel superposition, for each outcome.
- Eight-dimensional complex-normal QR unitary, RNG seed 20260919; every solver
  vector from each forward outcome pencil is propagated.
- Direct-sum rotations at angles (0.2,0.2,1.0); supplied kernel basis and a
  complex superposition for both outcomes.
- Defective Jordan M=[[1,1],[0,1]], D=(I+MM†)^(-1/2), E=(I+M†M)^(-1/2),
  U=[[E,EM†],[-DM,D]]. Outcome-zero root α=β=1 uses detector e₀;
  outcome-one root α=-β=-1 uses e₁. Each kernel has dimension one.
- SWAP with six Bloch-axis rays and both detector pole inputs.
- Generic-fixture homogeneous rescaling by 2-3i, detector permutation (2,0,3,1),
  and three-dimensional uncoupled QR spectator with RNG seed 20260819.
- Wrong outcomes, swapped homogeneous coordinates, detector perturbation 0.1e₀,
  nonunitary scaling by 1.001, and identity near-collapse inputs with amplitude
  1e-6 in the forbidden branch.

No nullity classifier, singular measure, root completeness, production scaling,
Hamiltonian family, physical time, or preferred-basis result is certified here.

## Reproduction, approval, and limitations

Use the pinned requirements-dev.txt environment, Python 3.11. The builder accepts
`--output NEW_DIRECTORY` and refuses to overwrite an existing packet. The checker
accepts `--packet DIRECTORY --log FILE.jsonl`; each invocation appends its result,
including failures. Its draft manifest binds source hashes for review, not an
approved frozen verifier. Full input matrices and vectors are saved in states.npz;
JSON records, figure data, source copies, Git patch and environment metadata allow
reconstruction of an uncommitted code state. The source snapshot supplements the
Git patch for new untracked files. Source copies have a `.snapshot` suffix so
test discovery cannot execute evidence copies. The checker validates their
hashes and requires the packet and working SPEC to match the review manifest.

The known matched-ring repeated-root failure and the zero-field independent-spin
angle regression both reproduce with the unchanged HEAD root module. They prevent
claims of complete numerical root validation; it does not contradict the
state-level block identity. Independent review must assess this separation.
The required promotion sequence is explicit user approval of this concrete
contract, activation and source freeze, fresh certification run, then independent
scientific referee review. Until then the exact-formalism gate is INCOMPLETE,
all other gates are unchanged, and paper_ready=false.
