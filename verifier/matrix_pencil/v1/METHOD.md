# METHOD — matrix-pencil-v1 (CANDIDATE, not activated)

Derivation and validation method for the `SPEC.md` §3 gate,
**Complete matrix-pencil characterization**. This document is hashed by
`check.py`.

## 1. The object the specification asks for

`SPEC.md` §3 fixes the outcome pencils

$$
M_0(\lambda)=U_{10}+\lambda U_{11},
\qquad
M_1(\lambda)=U_{00}+\lambda U_{01},
$$

and states that for every admissible root $\lambda_j^{(b)}$ the Bloch point
receives weight

$$
k_j^{(b)}=\dim\ker M_b\!\left(\lambda_j^{(b)}\right),
$$

that the generic case is $k_j=1$, that **degenerate or singular pencils must be
handled correctly rather than discarded**, and that the $\lambda=\infty$ sector
must be included.

The required object is therefore a set of **distinct** projective roots with
kernel-dimension weights. A QZ spectrum is not that object: it returns one
entry per *algebraic* multiplicity, each with one arbitrary eigenvector.

## 2. Solver slots, and the infinite sector

`characterize_pencil_roots(u00, u10)` evaluates the homogeneous pencil

$$
P(\alpha,\beta)=\beta\,\texttt{u10}-\alpha\,\texttt{u00},
$$

where the two arguments are **positional solver slots, not** $U_{00}$ and
$U_{10}$ of §1. The `SPEC.md` §3 outcome pencils enter through

$$
\texttt{outcome }b:\qquad
\texttt{u00}:=U_{b1},\qquad \texttt{u10}:=-\,U_{b0},
$$

that is `(U11, -U10)` for outcome 0 and `(U01, -U00)` for outcome 1, which is
exactly the mapping `forward_pole_root_spectrum` already applies. Stating this
matters precisely here, because the infinite sector is read off the slots: at
$(\alpha,\beta)=(1,0)$ we get $P=-\texttt{u00}$, so the weight at
$\lambda=\infty$ is $\dim\ker U_{b1}$ — $\dim\ker U_{11}$ for outcome 0, not
$\dim\ker U_{00}$.

$P$ is homogeneous of degree one, so $\lambda=\infty$ needs no separate branch
and no division is performed anywhere.

## 3. Why algebraic multiplicity is the wrong weight

Let $J$ be a $2\times2$ Jordan block at $\lambda=1$. Then
$\det(\lambda I-J)=(\lambda-1)^2$ but $\dim\ker(I-J)=1$. Counting the two QZ
entries assigns weight two to a point that carries one collapsible direction.
`check.py` verifies both statements exactly in SymPy, and realizes the same
pencil physically: with

$$
D=\left(I+MM^{\dagger}\right)^{-1/2},\qquad C=-DM,
$$

the rows of $[\,C\;D\,]$ are orthonormal, so the completion

$$
U=\begin{pmatrix}N^{\dagger}\\ C\quad D\end{pmatrix},
\qquad
\operatorname{cols}(N)=\text{orthonormal basis of }\ker[\,C\;D\,],
$$

is unitary and its outcome-0 pencil is $D(\lambda I-M)$.

## 4. The reduction

1. **Solve** the homogeneous pencil once (QZ, DFT-preconditioned; see
   `wiki/methods/homogeneous-qz.md` for why the preconditioner is required).
2. **Cluster** projectively coincident roots by chordal distance at
   `CLUSTER_TOLERANCE`. This groups a *semisimple* degeneracy; a defective
   scatter is caught in step 6 instead, not here.
3. **Locate** each cluster at its phase-aligned mean on $\mathbb{CP}^1$. For a
   defective root of multiplicity $m$ the computed roots scatter around the
   true location at order $\epsilon^{1/m}$, so the mean is a strictly better
   estimator than any single member; for a semisimple cluster the members
   already agree and the mean changes nothing.
4. **Take one SVD per distinct root.** The numerical rank at the formation-scale
   tolerance of §6 gives $k_j=n-\operatorname{rank}$, and
   the trailing right singular vectors give an orthonormal kernel basis. That
   basis — not one arbitrary QZ eigenvector — supplies the collapsible detector
   states.
5. **Retain algebraic multiplicity as a diagnostic only.**
6. **Check that the distinct roots really are distinct**, by the kernel
   conditioning test of §5. Steps 2-5 cannot do this on their own.

## 5. Fail-closed conditions

The characterization refuses to report a usable measure in four situations.

- **`singular_measure_undefined`.** If $\det P\equiv0$ then every projective
  point has a nonzero kernel, the collapsible set is a continuum, and the
  finite weighted sum of §3 does not define a measure on it. SWAP is the exact
  example: for outcome 0,
  $P_0(\alpha,\beta)=(\beta|0\rangle+\alpha|1\rangle)\langle1|$ has kernel
  $\operatorname{span}\{|0\rangle\}$ at *every* $[\alpha:\beta]$, matching
  $\mathrm{SWAP}(|q\rangle\otimes|0\rangle)=|0\rangle\otimes|q\rangle$ for every
  input ray. No root set is emitted. A specification decision is required
  before any measure can be defined here; until then this branch is a refusal,
  not a result.
- **`defective_roots_present`.** $k_j<$ algebraic multiplicity, detected when
  the cluster is recognized as one root. The location then carries
  $\epsilon^{1/m}$ sensitivity and is not determined in double precision.
  *Correction:* an earlier version of this document claimed such a root's
  weights "cannot sum to $n$". That is true only when the cluster is grouped.
  When the scatter exceeds the cluster tolerance the weights **do** sum to $n$,
  which is exactly how a Jordan block of size $\ge3$ previously escaped as
  `regular`; the conditioning test below is what closes that hole.
- **`roots_not_separated`.** The certification question is not "is this pencil
  defective" but **"are its roots determined at all"**, answered by the root
  condition number $\kappa_j=\lVert y\rVert\lVert v\rVert/|y^{\dagger}Av|$. A
  defective root has $\kappa=\infty$; a regular pencil whose roots are not
  resolvable has a large one and is equally uncertifiable. A root of condition
  $\kappa$ is located to about $\kappa\epsilon$, so requiring it to be
  determined better than $\sqrt{\epsilon}$ gives the bound $1/\sqrt{\epsilon}$.

  *Two earlier guards are withdrawn.* A bare rank test on the stacked kernels
  fails because the theorem it rests on has a false converse. Its replacement,
  the conditioning of the stacked kernel basis, fails for a deeper reason:
  **defectiveness is invariant under $(A,C)\to(LAR,LCR)$ and that conditioning
  is not**, so a change of basis defeats it. The witness is an exactly
  representable integer pencil,
  $u_{00}=\begin{psmallmatrix}-22&28\\-49&63\end{psmallmatrix}$,
  $u_{10}=\begin{psmallmatrix}-30&28\\-67&63\end{psmallmatrix}$, with exact
  determinant $-14(\alpha-\beta)^2$ and exact kernel dimension one, which was
  reported `regular` with two spurious simple roots. Both witnesses are now
  fixtures.
- **`rank_gap_unresolved`.** The cluster mean is not a root of the pencil at
  all, so the rank statement does not yield a weight.

## 6. Numerical constants, and their provenance

`ROOT_CONDITION_BOUND` $=1/\sqrt{\epsilon}\approx6.7\times10^{7}$, derived in §5
from the requirement that a root be located to better than $\sqrt{\epsilon}$.
The *test* was introduced reactively, after a Jordan block of size three was
found being reported `regular`, and its first form — a bound on the conditioning
of the stacked kernel basis — was then refuted by an independent referee. The
current form is stated on the invariant quantity.

**Measured margins, stated as measured.** Over the fixture set, certified
pencils reach $\kappa=82$ and refused ones start at $4.2\times10^{8}$: five
orders of clearance below the bound and a factor of $6.3$ above it. An earlier
version of this document claimed a nine-order separation with "roughly six
orders clear of either population"; that claim was about the withdrawn kernel
conditioning, it was **false**, and it is retracted. The upper margin is the
tighter one and the suite pins it — multiplying the bound by two fails, as does
multiplying by $10^3$ or dividing by $10^4$. Dividing by two does **not** fail,
and should not: tightening a conservative bound cannot create a false
certification.

`CLUSTER_TOLERANCE` $=10^{-7}$ groups QZ images of one semisimple root. It is
not relied on to group a defective scatter — the root-condition test does that —
so no value of it needs to be tuned against Jordan blocks. Distinct roots closer
than this are refused rather than merged.

`SINGULARITY_SAMPLE_FLOOR` $=8$, with the actual count $\max(8,n+1)$. The
determinant is homogeneous of degree $n$, so it vanishes identically only if it
vanishes at $n+1$ distinct points; a count independent of $n$ has no guarantee.
An earlier version used a fixed 8 and is superseded.

`RANK_GAP_FACTOR` **was removed** after being declared frozen, because no case
could be constructed in which it changed a verdict.

The rank tolerance is $n\epsilon\left(|\beta|\,\lVert U_{10}\rVert+
|\alpha|\,\lVert U_{00}\rVert\right)$, the backward-error scale of the
*formed* matrix. The code takes the maximum of that and $\sigma_{\max}$ of the
difference; since $\sigma_{\max}\le|\beta|\lVert C\rVert+|\alpha|\lVert
A\rVert$ always, that maximum is **inert**, and is retained only as a guard
against a future change of scaling. Reverting to $\sigma_{\max}$ alone is
pinned hard; loosening by $10^{6}$ is **not** pinned, which is a stated gap.

Regularity is decided at **generic** points from a fixed seed, never the
cardinal points $\lambda\in\{0,\infty,1,-1,i\}$.

## 6b. Known limitations

- On $10^{4}$ random regular pencils under two-sided equivalences of condition
  up to $10^{4}$, **61 (0.61%) were refused rather than certified**; 58 of those
  had condition above $10^{3}$, where refusal is correct, but **3 (0.03%) were
  well conditioned** and were refused as `rank_gap_unresolved` because the
  cluster mean's smallest singular value fell just above the rank tolerance.
  This is conservative, not a false certification, and it is not fixed.
- Loosening the rank tolerance by $10^{6}$ is not caught by any test.
- No claim is made that the method is complete for arbitrary Kronecker
  structure. A staircase/GUPTRI computation is the tool that would settle that;
  this is a certification-by-refusal, and its guarantee is one-sided.

## 7. Coverage

The checker refuses to pass unless all five fixture families are present:
`finite`, `infinite`, `degenerate`, `defective`, `singular`. Positive fixtures
carry expectations known by construction (generic Haar blocks: every $k_j=1$
and $\sum k_j=n$; rank-deficient $U_{00}$: one infinite root of weight equal to
that nullity; matched ring: nine distinct roots with a sixfold kernel).
Negative controls must be *refused*, not merely survived: the Jordan pencil must
report algebraic 2 with weight 1, the nilpotent exchange sectors must never
report usable roots, and both SWAP pencils must emit no roots at all.

## 7b. Contract fixtures: which are present, and which are not

The 2026-09-19 contract lists F0-F8 as mandatory for the first verifier candidate.
Present: **F0** (identity, pole-only geometry, weight three at each pole), **F1**
(strict QND with detector phases, outcome 1 exercising the infinite root), **F2**
(generic QR unitary), **F3** (direct sum of rotations with a repeated angle,
weights two and one at $-\tan(\theta/2)$), **F4** (Jordan colligation, extended
here to sizes 2-5 in both outcome mappings), **F5** (SWAP, singular), and **F6**
(uncoupled spectator doubling every weight, in the test suite).

**F7 and F8 are absent, and cannot be supplied by this verifier.** Both require
both forward outcome measures to agree between the full basis and a
symmetry-sector path, and the 2026-09-19 audit records that the sector evaluator
"constructs only the fixed-input $A,C$ pencil. It does not reconstruct $B,D$ or
solve the two SPEC forward pencils." Until that path exists there is nothing to
compare against, so claiming F7/F8 coverage would be fabrication. This is a real
gap in the evidence for any gate that depends on the sector path.

## 8. Dependency hashing

`check.py` hashes `SPEC.md`, its own two files, **and** the `core/` modules it
imports. Hash-binding only the specification and the verifier's own source is
insufficient for any verifier that imports `core/`: a change there can alter
verifier output while every recorded hash still matches. `exact-formalism-v1`
is unaffected in practice because it imports no `core/` module, but
`verifier/analytic_p_theta/generic_verifier.py` does import
`core/relative_evolution_pencil.py` and hashes no `core/` file, which is an open
governance gap recorded in `wiki/governance/paper-readiness-ledger.md`.

## 9. Activation status

**CANDIDATE.** `SPEC.md` §0.1 permits proposing a verifier and forbids
activating one without explicit user approval. `check.py` therefore reports
`certification: false` unless the manifest `status` is `activated`, which only
the user may set, accompanied by an approval record under
`raw/project-governance/`.
