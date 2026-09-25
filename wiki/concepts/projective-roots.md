# Projective Roots and Exact Collapsible States

> Sources: `SPEC.md` v1.0, 2026-09-15
> Raw: [Research specification snapshot](../../raw/project-governance/research-spec-v1.md)
> Updated: 2026-09-21

This page records the controlling algebraic definition. It replaces the legacy single-pencil and inverse-relative-propagator conventions.

## Exact condition

Write the qubit-block decomposition of the propagator as

$$
U(T)=\begin{pmatrix}U_{00}&U_{01}\\U_{10}&U_{11}\end{pmatrix}_q,
\qquad
|\psi_q(\lambda)\rangle=\frac{|0\rangle+\lambda|1\rangle}{\sqrt{1+|\lambda|^2}}.
$$

For an unrestricted detector state $|D\rangle$, exact collapse at the externally specified time $T$ means

$$
U(T)|\psi_q(\lambda),D\rangle=|b\rangle|D_b'\rangle.
$$

The two outcome pencils are therefore

$$
M_0(\lambda)=U_{10}+\lambda U_{11},
\qquad
M_1(\lambda)=U_{00}+\lambda U_{01},
$$

with $M_b(\lambda)|D\rangle=0$. Both pencils are required. A pencil such as $Cv=\lambda Av$ may arise in a special chart or derived symmetry reduction, but it is not the project-wide definition and cannot replace either outcome pencil.

## Homogeneous roots

Use projective coordinates $[\alpha:\beta]$ with $\lambda=\alpha/\beta$. The homogeneous pencils are

$$
\widehat M_0(\alpha,\beta)=\beta U_{10}+\alpha U_{11},
\qquad
\widehat M_1(\alpha,\beta)=\beta U_{00}+\alpha U_{01}.
$$

This convention gives the qubit state and Bloch vector

$$
|\psi_q\rangle=\frac{\beta|0\rangle+\alpha|1\rangle}{\sqrt{|\alpha|^2+|\beta|^2}},
$$

$$
\mathbf r=\frac{(2\operatorname{Re}\beta^*\alpha,\ 2\operatorname{Im}\beta^*\alpha,\ |\beta|^2-|\alpha|^2)}{|\alpha|^2+|\beta|^2},
\qquad
\theta=2\operatorname{atan2}(|\alpha|,|\beta|).
$$

Thus $[0:1]$ is the north pole ($\lambda=0$) and $[1:0]$ is the south pole ($\lambda=\infty$). A numerical implementation must retain finite, infinite, multiple, singular, and indeterminate cases rather than filtering them through matrix inversion.

## Multiplicity and finite-$N$ measure

For every admissible root, the physical weight is the kernel dimension

$$
k_j^{(b)}=\dim\ker M_b(\lambda_j^{(b)}).
$$

The separately normalized empirical outcome measure is

$$
\rho_b^{(N)}(\Omega;T)=\frac{1}{K_b}\sum_j k_j^{(b)}\delta(\Omega-\Omega_j),
\qquad K_b=\sum_j k_j^{(b)}.
$$

For a regular $d\times d$ pencil, the determinant has total algebraic degree $d$ on the Riemann sphere, but kernel dimension and algebraic multiplicity are not interchangeable in singular or defective cases. The verifier must report both when relevant.

The two outcome measures are not independent: unitarity makes each the antipodal pushforward of the other, with identical kernel weights, so $K_0=K_1$ and one solved pencil determines both sets. See [[outcome-antipodality]] for the theorem and its consequences for the two Born criteria.

## Numerical tolerance is not the definition

Residuals and singular values locate and verify roots. They do not turn a near-null vector into an exactly collapsible state. Every accepted root needs a homogeneous backward residual, a kernel/nullity determination, and an explicit classification of singular or indeterminate cases. Approximate-collapse basins may be studied as a separate experiment only when clearly labelled.

## Status

The derivation above follows directly from block multiplication and is the current contract. The production solver and all historical root sets still require fresh dual-pencil validation before they satisfy any paper-readiness gate.

See also: [[collapsible-basis-dependence]], [[born-like-points]], [[outcome-antipodality]], [[homogeneous-qz]], [[relative-propagator]], [[research-specification-v1]].
