# Production Pipeline & Validation

## Overview
The production pipeline is the sequence of tools used to turn a Hamiltonian configuration into a validated set of projective roots and Born diagnostics.

## Workflow
1. **Configuration**: Parameters are defined in `configs/*.json`.
2. **Generation**: `core/hamiltonians` generates the matrices.
3. **Solver**: `core/relative_evolution_pencil.py` uses the **Homogeneous-QZ** algorithm to find roots.
4. **Diagnostics**: `core/hamiltonian_classification.py` computes $S_{\text{born}}$, RMSE, and harmonic leakage.
5. **Validation**: The pipeline checks `qz_valid` (residuals and isometry) before accepting a result.

## Validation Gates
A result is only "Production-Grade" if it passes:
- **Coverage Gate**: Full reflected polar coverage (all bins filled).
- **Residual Gate**: Homogeneous backward residuals below a strict tolerance (e.g., $10^{-12}$).
- **Isometry Gate**: Column isometry residual $\approx 0$.

See also: [[homogeneous-qz]], [[symmetry-resolution]].
