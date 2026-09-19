# Exact collapse formalism: proposed verifier v1

**Status: ACTIVATED — explicitly approved by the user on 2026-09-19.** This
frozen verifier produces `PASS` / `FAIL` for the exact-collapse-formalism gate.
It changes no SPEC definition and cannot certify any other readiness gate.

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
including failures. Its activated manifest binds the approved verifier sources
and controlling SPEC hash. Full input matrices and vectors are saved in states.npz;
JSON records, figure data, source copies, Git patch and environment metadata allow
reconstruction of an uncommitted code state. The source snapshot supplements the
Git patch for new untracked files. Source copies have a `.snapshot` suffix so
test discovery cannot execute evidence copies. The checker validates their
hashes and requires the packet and working SPEC to match the review manifest.

The known matched-ring repeated-root failure and the zero-field independent-spin
angle regression both reproduce with the unchanged HEAD root module. They prevent
claims of complete numerical root validation; it does not contradict the
state-level block identity. Independent review must assess this separation.
The user explicitly approved this concrete contract on 2026-09-19. Promotion
still requires a fresh certification run and independent scientific referee
review. Until both pass, the exact-formalism gate remains INCOMPLETE; all other
gates are unchanged and paper_ready=false.
