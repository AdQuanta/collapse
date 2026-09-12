# Projective Roots & Special States

## The Construction
The system consists of a central qubit coupled to a detector:
$$ H = H_Q + H_D + H_{QD} $$
The evolution operator is partitioned as:
$$ U(t) = \begin{pmatrix} A & B \\ C & D \end{pmatrix} $$

## Disentanglement Condition
Projective disentanglement roots are obtained from the generalized eigenvalue problem:
$$ Cv = \lambda Av $$
A finite root $\lambda$ defines an initial qubit state $|\phi_0(\lambda)\rangle$ that disentangles from the detector at time $t$.

## Bloch Sphere Mapping
The root $\lambda$ maps to a Bloch polar angle:
$$ \theta = 2\arctan |\lambda| $$

## Implementation
The production solver uses **homogeneous generalized eigenvalues (QZ)** to correctly handle finite, infinite, and indeterminate projective roots.

See also: [[born-like-points]], [[relative-propagator]].
