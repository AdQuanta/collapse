# Scientific Contract & Reliability

This page defines the rigor required for any claim made within the `unitary-collapse` research program.

## The Scientific Contract
For any substantive theory or numerical work, the following must be established:
1. **Physical Definition**: Clear statement of the question, observable, units, and validity regime.
2. **Conventions**: Explicit documentation of basis, tensor ordering, signs, phases, and normalization.
3. **Governing Equations**: Equations stated independently of implementation; approximations and neglected terms must be explicit.
4. **Limits & Symmetries**: Identification of exact limits, conservation laws, and scaling checks *before* implementation.
5. **Validation**: Smallest testable implementation, provenance, and unresolved limitations.

## Numerical Reliability Standards
To prevent "false positives" and numerical artifacts, the following rules apply:
- **Material Error Checks**: Analysis of basis/grid/cutoff/timestep dependence.
- **Symmetry-Sectoring**: Mandatory use of sector-by-sector analysis for RMT diagnostics.
- **Matrix Structure**: Use Hermitian routines for Hermitian problems; prefer factorizations over inversions.
- **Stochastic Rigor**: Explicit use of `numpy.random.Generator`, saved seeds, and quantification of uncertainty.
- **Convergence**: No claim of convergence from a single resolution; a minimum of three systematic refinements is required.

See also: [[production-pipeline]], [[symmetry-resolution]].
