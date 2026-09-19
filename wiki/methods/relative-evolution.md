# Relative-Unitary Evolution

## The Construction
The starting point is the qubit-first block decomposition at the externally specified time \(T\):
\[
U(T)=\begin{pmatrix}U_{00}&U_{01}\\U_{10}&U_{11}\end{pmatrix},
\]
where each block acts on the detector Hilbert space and the basis is the candidate outcome basis.

## The Relative Propagator
For \(|\psi_q(\lambda)\rangle=(|0\rangle+\lambda|1\rangle)/\sqrt{1+|\lambda|^2}\), exact collapse is defined by the dual equations
\[
(U_{10}+\lambda U_{11})|D\rangle=0\quad(b=0),
\]
\[
(U_{00}+\lambda U_{01})|D\rangle=0\quad(b=1).
\]
A relative operator formed by inverting one block is only a regular-chart reduction of one pencil. It is never the definition and cannot represent singular, infinite, or indeterminate roots. Special reductions such as conditional detector evolutions in symmetry-constrained classes are mechanism-specific diagnostics and must be checked against the full time-domain dual pencils.

## Mapping to the Bloch Sphere
Finite roots map by
\[
\lambda=e^{i\phi}\tan(\theta/2),
\]
with \(\lambda=\infty\) mapped explicitly to the opposite pole. Every point is weighted by its kernel multiplicity. The two outcome measures are normalized separately before computing the strong conditional ratio and weak azimuthal marginals; a polar histogram alone is insufficient.

See also: [[projective-roots]], [[born-like-points]].
