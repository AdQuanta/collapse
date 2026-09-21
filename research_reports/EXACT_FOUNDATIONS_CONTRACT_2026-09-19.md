# Exact Foundations Contract for `SPEC.md` v1.0

**Date:** 2026-09-19  
**Code state inspected:** `2626a878de11dd96c09ef3274b5a5f10606766af` plus the uncommitted weak-Born correction of 2026-09-19  
**Scope:** `SPEC.md` §§2–4 and the implementation needed to certify the first three paper-readiness gates  
**Status:** contract and fresh audit complete; paper-readiness gates remain `INCOMPLETE`

## Finding

The repository already contains most of the Hamiltonian construction and homogeneous generalized-eigenvalue machinery needed for the first milestone. In particular, the full-basis path can solve both exact forward outcome pencils without matrix inversion, retain finite and infinite projective roots, and report backward residuals. The QuSpin implementation already covers the approved ring and endpoint-chain geometries and several higher Hamiltonian tiers.

That machinery is not yet a SPEC-complete outcome-measure pipeline. It does not reconstruct and verify all collapse states, reduce repeated algebraic roots to distinct roots weighted by kernel dimension, or define the measure for singular pencils. The symmetry-sector production path constructs only the historical fixed-input pencil from two propagator blocks, not both forward outcome pencils from all four blocks. One existing focused numerical test also fails under the pinned environment. These gaps prevent promotion of the exact-formalism, complete-pencil, and outcome-measure gates.

## Exact forward characterization

Write the qubit-first propagator as

$$
U=\begin{pmatrix}A&B\\C&D\end{pmatrix}
=\begin{pmatrix}U_{00}&U_{01}\\U_{10}&U_{11}\end{pmatrix}.
$$

Use homogeneous qubit coordinates $[\alpha:\beta]\in\mathbb{CP}^1$, with normalized input ray

$$
|q(\alpha,\beta)\rangle
=\frac{\beta|0\rangle+\alpha|1\rangle}
{\sqrt{|\alpha|^2+|\beta|^2}}.
$$

For a normalized detector vector $|d\rangle$, block multiplication gives

$$
U|q,d\rangle
=\frac{|0\rangle\otimes(\beta A+\alpha B)|d\rangle
+|1\rangle\otimes(\beta C+\alpha D)|d\rangle}
{\sqrt{|\alpha|^2+|\beta|^2}}.
$$

The exact homogeneous pencils are therefore

$$
P_0(\alpha,\beta)=\beta C+\alpha D,
\qquad
P_1(\alpha,\beta)=\beta A+\alpha B.
$$

Outcome 0 requires $P_0|d\rangle=0$; outcome 1 requires $P_1|d\rangle=0$. This includes the affine chart $\lambda=\alpha/\beta$, the north pole $[0:1]$, and the south pole $[1:0]$. Because $U$ is unitary, a normalized input satisfying one forbidden-branch equation has a nonzero retained branch of unit norm. The normalized output detector state is the retained branch itself:

$$
|d'_0\rangle
=\frac{(\beta A+\alpha B)|d\rangle}
{\sqrt{|\alpha|^2+|\beta|^2}},
\qquad
|d'_1\rangle
=\frac{(\beta C+\alpha D)|d\rangle}
{\sqrt{|\alpha|^2+|\beta|^2}}.
$$

Numerically, the collapse residual is the norm of the forbidden branch. A tolerance certifies a computed solution; it does not replace the exact kernel equation with a fidelity definition.

## Multiplicity and the regular-pencil measure

A square pencil is **regular** when its homogeneous determinant is not identically zero. Its distinct projective roots form a finite set, including any root at infinity. At a distinct root $[\alpha_j:\beta_j]$, the SPEC weight is the geometric multiplicity

$$
k_j^{(b)}=\dim\ker P_b(\alpha_j,\beta_j),
$$

and the finite outcome measure is

$$
\rho_b^{(N)}
=\frac{1}{K_b}\sum_j k_j^{(b)}\delta_{\Omega_j},
\qquad
K_b=\sum_j k_j^{(b)}.
$$

The algebraic multiplicity returned by QZ is not this weight. A fresh unitary fixture constructed from the defective Jordan matrix

$$
M=\begin{pmatrix}1&1\\0&1\end{pmatrix}
$$

is obtained explicitly by setting

$$
D=(I+MM^\dagger)^{-1/2},
\qquad C=-DM,
$$

choosing the columns of $N$ as an orthonormal basis of $\ker[C\;D]$, and forming

$$
U=\begin{pmatrix}N^\dagger\\C&D\end{pmatrix}.
$$

The rows of $[C\;D]$ are orthonormal, so this completion is unitary, and its outcome-0 pencil is $D(\lambda I-M)$. It has one distinct root at $\lambda=1$, algebraic multiplicity two, and kernel dimension one. The current solver reports two coincident QZ roots and correctly finds nullity one when both representatives are explicitly audited. Counting the two QZ entries would assign the wrong physical weight.

The production contract must consequently cluster projectively coincident roots, preserve their algebraic multiplicity as a diagnostic, compute an SVD nullspace once per distinct root, and use only its dimension as the measure weight. The nullspace basis, not one arbitrary QZ eigenvector, supplies the detector states.

## Singular pencils expose an unresolved measure definition

A pencil is **singular** when

$$
\det P_b(\alpha,\beta)\equiv0.
$$

Then every projective coordinate has a nonzero kernel; the collapsible qubit set is generally a continuum, and its kernel dimension may change at exceptional points. Homogeneous QZ output for a singular pencil is not a finite root multiset. A $(0,0)$ pair records indeterminate Kronecker structure, while any accompanying determined pair does not convert the continuum into isolated physical roots.

SWAP on a qubit and a one-qubit detector gives the exact example

$$
A=|0\rangle\langle0|,\quad
B=|1\rangle\langle0|,\quad
C=|0\rangle\langle1|,\quad
D=|1\rangle\langle1|.
$$

For outcome 0,

$$
P_0(\alpha,\beta)
=(\beta|0\rangle+\alpha|1\rangle)\langle1|,
$$

whose kernel is $\operatorname{span}\{|0\rangle\}$ for every $[\alpha:\beta]$. Indeed,

$$
\operatorname{SWAP}(|q\rangle\otimes|0\rangle)
=|0\rangle\otimes|q\rangle
$$

for every input qubit ray. Outcome 1 has the analogous continuum with detector input $|1\rangle$. Fresh checks found rank one and nullity one at every sampled projective coordinate for both pencils, while QZ returned one indeterminate and one apparently determined pair per pencil.

The finite weighted sum in `SPEC.md` does not select a probability measure on this continuum. Until the user approves an additional rule, a singular outcome pencil must be reported as `measure_undefined_singular_pencil`; its QZ pairs must not enter a histogram. A successful candidate can avoid this unresolved branch by proving both outcome pencils regular throughout the claimed parameter region, but the complete singular-case gate itself cannot be certified from the current specification.

## Existing implementation map

| SPEC responsibility | Existing implementation | Fresh assessment |
|---|---|---|
| Approved local Hamiltonians | `SinglePixelHamiltonianQuSpin` and its NumPy counterpart implement central site 0, detector rings and chains, collective ring targets, endpoint-chain targets, longitudinal and transverse fields, and axis-aligned detector and qubit-detector interactions. | Substantial implementation exists. The constructors use a minus-sign parameter convention, so every result packet must record the mapping from SPEC coefficients. |
| Collective scaling | QuSpin applies the supplied coupling to each selected edge. `RingChainSpec` supplies $N^{-1/2}$ for ring $x,y$ couplings and $N^{-1}$ for $z$. | Scaling is campaign-side. The `RingChainSpec` transverse default is not the SPEC conservative baseline and needs the permitted fluctuation-scaling derivation before production use. |
| Scope enforcement | The Hamiltonian classes also implement disorder, next-nearest-neighbor, cross-axis, and nonlocal graph terms. | Availability does not grant SPEC approval. Initial validation fixtures must set excluded channels exactly to zero. |
| Four qubit blocks | `split_qubit_first_blocks` extracts $A,B,C,D$ from a full operator. | Implemented and directly usable at small size. |
| Both outcome pencils | `forward_pole_root_spectrum(U, outcome=0|1)` maps $(D,-C)$ and $(B,-A)$ into the homogeneous solver. | Algebraically matches $P_0$ and $P_1$ for full-basis unitaries. |
| Homogeneous QZ | `generalized_relative_evolution_spectrum` retains finite, infinite, and indeterminate pairs and reports left/right residuals, conditioning, duplicate clusters, optional nullity audits, and sampled regularity. | Strong reusable core. Sampled regularity cannot prove singularity; root audits are optional and do not return a nullspace basis. |
| Symmetry sectors | `SinglePixelHamiltonianQuSpin.diagonalize_sectors` marks translation sectors as locally safe and magnetization/parity sectors for full-basis projection. | The active sector evaluator constructs only historical $A,C$ fixed-input pencils. It does not reconstruct $B,D$ or solve the two SPEC forward pencils. |
| Collapse-state reconstruction | Homogeneous coordinates map to Bloch vectors; QZ right vectors are available. | No canonical result object normalizes every kernel basis vector, propagates it, stores the retained detector output, and checks exact factorization. |
| Kernel weights | Duplicate clusters and selected SVD nullities are diagnostics. | No complete distinct-root reduction or kernel-dimension-weighted outcome measure exists. Equal QZ-root counting is invalid for defective roots. |
| Singular pencils | Indeterminate pairs and a five-point numerical rank audit are retained. | Correctly avoids pseudoinverse continuation, but does not characterize Kronecker structure or the continuum and cannot construct the SPEC measure. |

The historical `production_root_spectrum` and `relative_evolution_sector` paths solve $Cv=\lambda Av$. They remain useful derived diagnostics but cannot substitute for either forward outcome pencil.

## Fresh validation evidence

The pinned dependencies from `requirements-dev.txt` were installed under `/private/tmp/collapse_py311_deps`; no repository environment or tracked output was created.

### Existing focused suites

Command:

```sh
PYTHONPATH=/private/tmp/collapse_py311_deps \
NUMBA_CACHE_DIR=/private/tmp/collapse_numba_cache \
MPLCONFIGDIR=/private/tmp/collapse_matplotlib_cache \
python3.11 -m pytest -q \
  tests/test_relative_evolution_pencil.py \
  tests/test_projective_root_conventions.py \
  tests/test_relative_evolution_sector.py
```

Result: **23 passed, 1 failed**. The failure is `test_small_matched_ring_obeys_real_hamiltonian_forward_bridge`: maximum matched Bloch distance $3.907827153052709\times10^{-9}$ versus the frozen test threshold $2\times10^{-11}$.

The failed case has well-conditioned denominator blocks (condition number $1.074$) but a sixfold projective cluster. Its maximum homogeneous residuals are $7.94\times10^{-9}$ for the production pencil and $3.97\times10^{-9}$ for the forward pencil. With the default SVD threshold, most representative root audits report nullity zero. This points to unresolved repeated-root and numerical-rank handling; it does not justify loosening the threshold after observing the result.

> **Correction, 2026-09-20.** The repeated-root attribution in the paragraph above is wrong, and so is the "Next action" that followed from it. The failure is not a multiplicity effect. Every eigenvalue of that pencil is semisimple — geometric multiplicity equals algebraic multiplicity at all nine distinct roots, verified by SVD nullity of $C-\lambda A$ — so there is no Jordan block and no $\epsilon^{1/m}$ conditioning. Every eigenvalue condition number is order one — between $1.2$ and $21$ under the textbook $1/|y^{\dagger}Av|$ definition with unit left and right eigenvectors. The largest error, $2.96\times10^{-9}$, sits on a **simple, well-separated** root, not on the sixfold cluster, whose internal spread is only $1.7\times10^{-10}$; cluster-averaging therefore cannot fix it.
>
> The cause is LAPACK `zggev` as shipped in Apple Accelerate, against which this repository's `scipy` is linked. It loses six to nine digits on exactly structured blocks. `np.linalg.eigvals(solve(A, C))` returns the same roots at $5.9\times10^{-17}$; generic random and random-unitary-block pencils at dimension 8 to 64 return $2\times10^{-16}$ from `zggev` itself; and adding $10^{-13}$ noise to the failing blocks, or applying any random similarity, restores $10^{-17}$. The trigger is the exact zeros and exact symmetries of the blocks. This is a second Accelerate defect alongside the `zheevd` failure at dimension 4096 already recorded in `RESEARCH_STATE.md`.
>
> The error grows with size and is worse on chains than rings: at $t=37$ with the same structured parameters, the maximum scale-invariant pencil residual runs $1.9\times10^{-9}$, $7.9\times10^{-9}$, $8.8\times10^{-9}$, $2.1\times10^{-8}$ for rings at $N=3,4,5,6$ and $1.3\times10^{-8}$, $3.9\times10^{-8}$, $3.8\times10^{-8}$, $3.4\times10^{-7}$ for endpoint chains at the same sizes.
>
> The resolution is a unitary DFT right factor applied to both blocks before the solver call, with the right eigenvectors mapped back. It is exact in exact arithmetic, and it restores both the roots and the eigenvectors to $10^{-15}$ or better. See [homogeneous QZ](../wiki/methods/homogeneous-qz.md).
>
> The scope of the defect is set by the **detector** transverse field alone. Over a 192-cell sweep (rings and endpoint chains, $N=3\ldots6$, $h_z\in\{0,0.7\}$, $t\in\{1,37,211\}$), the plain path exceeds a $10^{-12}$ backward-error tolerance in 48/48 cells at $h_x=h_{0x}=0$ and in 24/48 cells at $h_x=0,\;h_{0x}=0.3$, with the worst residual of the whole sweep, $3.55\times10^{-7}$, occurring at $h_{0x}\neq0$; it exceeds it in 0/96 cells whenever $h_x\neq0$. With the preconditioner the worst residual over the same sweep is $2.36\times10^{-15}$. It never moved a binned Born score: on ring and chain configurations at $N=6,8$, $S_{\mathrm{Born}}$ is identical to every digit printed with and without the correction, because a $10^{-8}$ shift in a root radius cannot change 100-bin occupancy — though the Born pipeline also largely bypasses this solver by construction, so that invariance is mostly structural rather than an independent empirical escape. What the defect corrupted was every exactness claim at frozen tolerances of $10^{-11}$ and below, which is exactly what the two open test failures were reporting.
>
> **Referee correction, 2026-09-20.** An earlier version of this block asserted that "with either $h_x$ or $h_{0x}$ nonzero the plain path is already at $10^{-15}$." An independent fresh-context referee falsified that with 64 counterexamples and it is reproduced above: a nonzero central-qubit field does not rescue the plain path. The same review recorded that the condition-number interval quoted below uses the textbook $1/|y^{\dagger}Av|$ definition with unit vectors, whereas the pipeline's own `local_coordinate_condition_numbers` estimator gives $0.433$ to $7.49$ on the same pencil; both are order one, but the two normalizations must not be conflated. It also measured the generic-pencil `zggev` backward errors quoted below as $6.5\times10^{-16}$ to $1.5\times10^{-15}$ rather than $2\times10^{-16}$.

Command:

```sh
PYTHONPATH=/private/tmp/collapse_py311_deps \
NUMBA_CACHE_DIR=/private/tmp/collapse_numba_cache \
MPLCONFIGDIR=/private/tmp/collapse_matplotlib_cache \
python3.11 -m pytest -q tests/test_connectivity.py tests/test_symmetry_diag.py
```

Result: **49 passed**. These tests freshly support NumPy–QuSpin Hamiltonian agreement, central-target geometry, symmetry-aware eigenspectra, and the existing historical relative-spectrum reconstruction. They do not validate the missing dual forward sector pipeline.

### Independent algebraic fixtures

- A seeded generic $8\times8$ unitary was solved for both outcomes. Direct propagation of every normalized QZ input gave maximum forbidden-branch norm $5.35\times10^{-16}$ and maximum retained-branch norm error $2.22\times10^{-16}$.
- The defective physical unitary described above had unitarity residual $6.59\times10^{-16}$, two QZ entries at $\lambda=1$, and audited kernel dimension one.
- Both SWAP outcome pencils had rank one and nullity one at the four sampled coordinates $[0:1],[1:0],[1:1],[i:1]$, while the regularity audit classified them as numerically singular at all samples.

These checks validate the block derivation and expose the exact multiplicity and singular-measure gaps. They do not certify a paper-readiness gate.

## Required validation fixtures for implementation

The first verifier candidate must include the following deterministic cases.

| ID and construction | Required result |
|---|---|
| F0: $I_2\otimes I_3$ | Outcome 0 only at the north pole and outcome 1 only at the south pole, each with kernel weight three; exact output factorization. |
| F1: strict QND with detector phases $(0.2,-0.7,1.1)$ and $(-0.1,0.8,1.7)$ | The same pole-only geometry with nontrivial detector evolution; outcome 1 exercises the infinite root. |
| F2: QR unitary of dimension eight from `numpy.random.default_rng(20260919)` complex-normal input | Two independently solved regular outcome sets, projective residuals, reconstructed detector inputs and outputs, and direct forbidden-branch checks. |
| F3: direct sum of real qubit rotations with angles $(0.2,0.2,1.0)$ | Two distinct roots; the repeated coordinate has algebraic and kernel multiplicity two and weight two. |
| F4: the Jordan colligation $M,D,C,N,U$ defined above | One root at $\lambda=1$, algebraic multiplicity two, kernel weight one; no double counting. |
| F5: exact two-qubit SWAP | Singular status for both outcomes, continuum recognized, and no finite measure emitted. |
| F6: detector permutation $(2,0,3,1)$ applied to F2 and an uncoupled spectator unitary from seed `20260819` | Root coordinates and weights invariant under the basis change; spectator dimension multiplies every kernel dimension while normalized measures remain unchanged. |
| F7: four-spin detector ring with `J=1`, `Jpm=0.2`, `Jx=0.005`, `hz=0.3`, `hx0=0`, `hz0=0.1`, collective coupling, and $T=3.7$ | NumPy–QuSpin agreement for the Hamiltonian and all four propagator blocks; both forward outcome measures agree between full basis and translation sectors. |
| F8: four-spin detector chain with the F7 coefficients, endpoint coupling, and $T=3.7$ | NumPy–QuSpin agreement and both forward outcome measures agree between the full basis and the required projected-sector path. |

## Proposed executable contract

The future implementation should return one record per outcome with:

- `status`: `regular`, `singular`, or `numerically_unresolved`;
- normalized homogeneous root coordinates for each distinct regular root;
- algebraic multiplicity and kernel dimension as separate fields;
- an orthonormal detector-kernel basis at every root;
- scale-invariant pencil residuals and singular-value gaps;
- normalized input qubit and detector states, normalized retained detector outputs, and direct forbidden-branch/factorization residuals;
- separately normalized kernel-weighted measure data;
- regularity evidence and all tolerances used.

The verifier must fail closed when singular-value gaps do not separate numerical rank, when a pencil cannot be certified regular, or when a singular pencil reaches measure construction. Repeated-root validation should operate on the clustered root and its SVD nullspace rather than on individual QZ eigenvectors. Numerical thresholds must remain frozen during a run. The matched-ring failure that motivated this sentence has since been understood and resolved without moving any tolerance; see the correction above.

## Next action

**Superseded in part, 2026-09-20.** The matched-ring failure was not a repeated-root problem and is resolved; see the correction above. The remaining actions stand: implement the regular-pencil outcome record and both full-basis forward measures, followed by the four-block symmetry-sector path. Separately, obtain an explicit specification decision for how singular-pencil continua should enter—or be excluded from—the outcome measure before claiming complete singular-case coverage or freezing the first verifier.

