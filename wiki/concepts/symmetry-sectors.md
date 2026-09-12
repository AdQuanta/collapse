# Symmetry Sectors

The `unitary-collapse` project relies on the exact resolution of detector symmetries to correctly diagnose the spectral properties of the system and avoid misleading results in level-statistics analysis.

## The Golden Rule of Level Statistics
**Never mix eigenvalues from independent exact irreducible sectors before forming level-spacings.**

If eigenvalues from different sectors (e.g., different magnetization $N_\uparrow$) are concatenated into a single list, the resulting level-spacing distribution will appear Poissonian, regardless of whether the individual sectors are chaotic (Wigner-Dyson). This is because independent spectra are uncorrelated and thus "pass through" each other without repulsion.

## Primary Symmetries in the Project
The detector Hamiltonians typically employ the following symmetries:
1. **Magnetization ($N_\uparrow$)**: The total spin in the $Z$-direction.
2. **Translation Momentum ($k$)**: For ring topologies, the eigenvalues of the translation operator.

A complete resolution involves decomposing the detector Hilbert space into sectors $(k, N_\uparrow)$.

## Dynamical Coupling Between Sectors
While the detector Hamiltonian $H_D$ is block-diagonal in these sectors, the coupling operator $V$ (e.g., $X_0 \sum X_i$) may connect them.
For a uniform collective coupling, the selection rule is:
$$ (k, N_\uparrow) \longrightarrow (k, N_\uparrow \pm 1) $$
This means the qubit's evolution involves transitions between adjacent magnetization sectors while preserving momentum.

## Sector-Resolved Root Evaluation
To compute projective roots without constructing the full dense $U(t)$ matrix, the project evaluates the pencil $(C, A)$ sector-by-sector. This ensures:
- **Computational Efficiency**: Only small block-matrices are handled.
- **Correct Weighting**: Each sector's contribution to the total root multiset is weighted by its dimension.

See also: [[spectral-statistics]], [[symmetry-resolution]], [[production-pipeline]].
