# Symmetry-Resolved Sectoring

## The Core Principle
**Mandatory Rule:** Never mix eigenvalues from independent exact irreducible sectors before forming level-spacings.

## Why it Matters
Mixing independent spectra can make a chaotic (Wigner-Dyson) Hamiltonian look artificially Poissonian. To correctly diagnose the spectral class, one must resolve the Hamiltonian into its irreducible sectors (e.g., by magnetization $N_\uparrow$ and momentum $k$).

## Implementation in `collapse`
The pipeline uses `QuSpin` and custom sector-decomposition logic:
1. **Symmetry Resolution**: Identify the irreducible sectors of the detector Hamiltonian.
2. **Sector-by-Sector Analysis**: Compute the adjacent-gap ratio $\langle r \rangle$ within each sector independently.
3. **Aggregation**: Report the mean $\langle r \rangle$ for each sector or pool them only after the spacing has been calculated.

## Sector-Safe Root Evaluation
In `core/relative_evolution_sector.py`, projective roots are evaluated per sector. This avoids the need for a dense projection of the full Hilbert space and ensures that each sector's contribution to the total root multiset is correctly weighted by its dimension.

This implementation claim remains to be revalidated. Sectorwise root solving is legitimate only when the full propagator blocks preserve the sector decomposition relevant to each of the two outcome pencils. The recombined empirical measure must include every sector and every kernel multiplicity exactly once. Symmetry-sector dimensions are not substitutes for nullity weights, and roots may not be dropped merely because a block is singular.

For preferred-axis searches, the basis rotation itself can change which symmetries are manifest in the blocks. The verifier must therefore confirm equivalence with the unsplit full-space construction at tractable sizes before sector decomposition is used for production claims.

See also: [[spectral-statistics]], [[production-pipeline]].
