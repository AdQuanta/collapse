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

## Validation & Diagnostics
The revalidated pipeline must report, for both outcomes:

- homogeneous backward residuals in the original pencil;
- root classification and kernel multiplicity;
- reconstructed normalized input $|\psi_q(\lambda)\rangle\otimes|D\rangle$;
- the forbidden-output amplitude after applying $U(T)$, which is the exact-collapse residual;
- propagator unitarity and block-isometry identities;
- sensitivity to numerical precision and rank thresholds near singular roots.

Condition numbers are warnings, not permission to discard roots. No result is current until the frozen verifier independently reproduces these checks.

See also: [[projective-roots]], [[production-pipeline]].

