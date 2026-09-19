# Relative Propagators as Derived Charts

> Sources: `SPEC.md` v1.0, 2026-09-15
> Raw: [Research specification snapshot](../../raw/project-governance/research-spec-v1.md)
> Updated: 2026-09-19

A relative propagator can simplify a regular matrix pencil in a chart where one coefficient block is invertible. It is not the definition of an exact collapsible state.

For a pencil $C+\lambda D$, if $D$ is invertible then its finite roots are eigenvalues of $-D^{-1}C$. Equivalent left/right conventions can be used after their signs and projective coordinate have been stated. The inverse chart fails or becomes ill-conditioned at singular $D$, can hide roots at infinity, and does not classify singular or indeterminate pencils.

The controlling construction is therefore the pair

$$
U_{10}+\lambda U_{11},
\qquad
U_{00}+\lambda U_{01},
$$

solved in homogeneous coordinates. A derived relative operator is acceptable only when its roots are cross-checked against the corresponding homogeneous pencil, including multiplicities, kernel dimensions, infinite roots, and residuals. A single operator such as $A^{-1}C$ or a complementary pencil does not automatically represent both outcomes.

Conditional relative unitaries remain useful in symmetry-reduced QND or conserved-qubit sectors, where they may expose eigenphases or exact antipodal relations. Those are model-specific reductions and must be derived before use.

See also: [[projective-roots]], [[homogeneous-qz]], [[relative-evolution]].
