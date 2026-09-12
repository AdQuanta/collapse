# Homogeneous-QZ Pipeline

## The Problem
Finding the projective roots of the pencil $(C, A)$ requires solving $Cv = \lambda Av$. Standard eigenvalue solvers (like `eig(C @ inv(A))`) fail when $A$ is singular or ill-conditioned, which is common in the `unitary-collapse` model.

## The Solution: QZ Decomposition
The production pipeline uses the **QZ algorithm** (Generalized Schur Decomposition), which decomposes $A$ and $C$ into upper triangular matrices $S$ and $T$ using unitary matrices $Q$ and $Z$:
$$ A = Q S Z^H, \quad C = Q T Z^H $$
The generalized eigenvalues are then simply the ratios of the diagonal elements:
$$ \lambda_j = \frac{T_{jj}}{S_{jj}} $$

## Validation & Diagnostics
To ensure the numerical integrity of the roots, the pipeline reports several diagnostics:
- **Homogeneous Residual**: $\max \|T_{jj} v_j - S_{jj} \lambda_j v_j\|$.
- **Column Isometry**: Checks if $U_{00}^\dagger U_{00} + U_{10}^\dagger U_{10} = I$.
- **Condition Number**: $\kappa(U_{00})$ is tracked to identify pencils where $A$ is nearly singular.
- **Root Classification**: Roots are explicitly tagged as **finite**, **infinite** ($S_{jj} = 0$), or **indeterminate** ($S_{jj} = T_{jj} = 0$).

See also: [[projective-roots]], [[production-pipeline]].
