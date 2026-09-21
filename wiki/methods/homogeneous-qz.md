# Homogeneous-QZ Pipeline

## The Problem
Write the qubit-first propagator as
$$
U(T)=\begin{pmatrix}U_{00}&U_{01}\\U_{10}&U_{11}\end{pmatrix}.
$$
The exact projective coordinate $\lambda$ and detector vector $v\ne0$ obey one of two physical pencils:
$$
(U_{10}+\lambda U_{11})v=0\quad(b=0),\qquad
(U_{00}+\lambda U_{01})v=0\quad(b=1).
$$
An ordinary eigenproblem formed with an inverse is incomplete whenever a coefficient block is singular or ill-conditioned, and it omits the projective point $\lambda=\infty$.

## The Solution: QZ Decomposition
Solve each ordered coefficient pair in homogeneous coordinates. If a pencil is written as $M_0+\lambda M_1$, QZ returns a projective pair rather than requiring division; a finite coordinate can be formed only after applying the solver's sign and ordering convention. The implementation must test that convention directly by substituting the returned pair into the original physical pencil.

This keeps three cases distinct:

- finite roots;
- roots at $\lambda=\infty$, obtained from the appropriate kernel of the $\lambda$-coefficient;
- indeterminate/singular structure, where both homogeneous coefficients vanish and ordinary eigenvalue counting is insufficient.

For every admissible projective point, its physical weight is the geometric kernel multiplicity $k=\dim\ker(M_0+\lambda M_1)$, not merely the number of repeated floating-point eigenvalue entries.

## Unitary Preconditioning of the Solver Call

LAPACK `zggev`, as shipped in the Apple Accelerate framework this project's
`scipy` links against, loses six to nine digits on the exactly structured
blocks that symmetric ring and chain Hamiltonians produce. The loss is not a
conditioning effect: at the affected points every root is semisimple, every
eigenvalue condition number is order one, and $\operatorname{cond}(U_{00})$ is
close to one, yet the returned roots carry backward errors between
$10^{-9}$ and $10^{-7}$ while the same roots computed from the ordinary
eigenproblem reach $10^{-17}$. Adding $10^{-13}$ noise to the blocks, or
applying any random similarity, restores full precision, which identifies the
exact zeros and exact symmetries of the blocks as the trigger.

The pipeline therefore solves the unitarily equivalent pencil
$(U_{00}F,\;U_{10}F)$, where $F$ is the DFT matrix of the detector dimension,
and maps the right eigenvectors back with $F$. Because $v$ solves
$\beta U_{10}v=\alpha U_{00}v$ exactly when $w=F^{\dagger}v$ solves the
substituted pencil, no root, no left eigenvector and no condition number
changes in exact arithmetic; only the floating-point path does. The cost is two
FFTs on the blocks and one on the eigenvectors. The `preconditioner` field of
the spectrum record states whether it was applied.

The correction is scoped, and the scope is set by the **detector** transverse
field alone. Over a 192-cell sweep (rings and endpoint chains, $N=3\ldots6$,
$h_z\in\{0,0.7\}$, $t\in\{1,37,211\}$), the plain path violates a $10^{-12}$
backward-error tolerance in 48/48 cells at $h_x=h_{0x}=0$ and in 24/48 cells at
$h_x=0$, $h_{0x}=0.3$, with the single worst residual $3.55\times10^{-7}$
occurring at $h_{0x}\neq0$; it violates it in 0/96 cells whenever $h_x\neq0$.
A nonzero central-qubit field $h_{0x}$ therefore does **not** rescue the plain
path, and any claim scoped on $h_{0x}$ is false. With the preconditioner the
worst residual over the same sweep is $2.36\times10^{-15}$.

The correction never moves a binned Born score, because a $10^{-8}$ shift in a
root radius cannot change 100-bin occupancy. Note also that the Born pipeline
largely bypasses this solver by construction — `core/analysis.py` diagonalizes
$U_{00}^{-1}U_{10}$ directly and `scripts/eval_born.py` reaches the homogeneous
solver only when $\operatorname{cond}(U_{00})\ge10^{6}$ — so Born invariance is
mostly structural rather than an independent empirical escape. What the
correction does restore is every exactness check: convention bridges, root-set
comparisons, and collapsible-state reconstruction at frozen tolerances of
$10^{-11}$ and below.

The substitution is exact in exact arithmetic, but the FFT-based product is
itself an $O(\epsilon)$ backward perturbation (measured relative error
$3.3\times10^{-15}$ at $n=16$, $1.3\times10^{-14}$ at $n=64$). That is harmless
for a well-conditioned root and decisive for a defective one, which is the
subject of the next paragraph; exactness in exact arithmetic is therefore not
by itself a safety argument.

**Defective pencils are the exception, and the pipeline does not guard them.**
Where $U_{00}^{-1}U_{10}$ is nilpotent,
as in the collective-exchange sector, the root carries the $\epsilon^{1/m}$
sensitivity of a Jordan block and its location is not determined at double
precision at all: a $10^{-15}$ perturbation of the blocks spreads the angles to
$10^{-2}$. An unpreconditioned call returns exact zeros there only because
LAPACK deflates the exactly zero entries, which is an artifact of the basis.
Such a case must be certified through an exact, basis-independent property —
nilpotency of $U_{00}^{-1}U_{10}$, verified by matrix powers — and never
through a QZ angle gate.

**Open defect.** On such a pencil the preconditioned solver returns angles wrong
by up to $6.3\times10^{-3}$ while `maximum_homogeneous_residual` stays at
$10^{-16}$ and `near_singular_u00_warning` is `False`. The backward-error
diagnostics that every current test gates on therefore cannot see this failure,
which is exactly the expected behaviour for a defective root: tiny backward
error, large forward error. The only diagnostic that responds is
`local_coordinate_condition_numbers`, which reaches $10^{11}$ to $10^{15}$
there, and nothing in `core/` inspects it, warns, or falls back. A caller that
lands on a defective pencil gets silently wrong roots that pass every automated
check. `SPEC.md` §3 requires degenerate pencils to be handled rather than
discarded, so this must be closed before the matrix-pencil gate can be claimed.

## Validation & Diagnostics
The revalidated pipeline must report, for both outcomes:

- homogeneous backward residuals in the original pencil;
- root classification and kernel multiplicity;
- reconstructed normalized input $|\psi_q(\lambda)\rangle\otimes|D\rangle$;
- the forbidden-output amplitude after applying $U(T)$, which is the exact-collapse residual;
- propagator unitarity and block-isometry identities;
- sensitivity to numerical precision and rank thresholds near singular roots;
- whether the unitary preconditioner was applied, and the backward residual with and without it at any point where exactness is claimed.

Condition numbers are warnings, not permission to discard roots. No result is current until the frozen verifier independently reproduces these checks.

See also: [[projective-roots]], [[production-pipeline]].

