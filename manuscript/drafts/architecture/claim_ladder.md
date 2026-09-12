# The Claim Ladder

This ladder orders the major scientific claims of the paper. Each claim must be earned by the previous one.

## Claim 1: The Theory of Collapsible States
**Statement**: Unitary evolution of a qubit-detector system possesses a finite set of initial qubit states—"collapsible states"—that evolve into perfect product states at a given time $t$. While sparse relative to the full Hilbert space, this set can be dense on the Bloch sphere as the detector size grows.
- **Evidence**: `PROVED` (Projective root construction / QZ solver).
- **Comparator**: Contrast with standard decoherence/dephasing where a state is only "approximately" mixed.
- **Wording Ceiling**: "Establishes the existence of a discrete set of collapsible states that recover perfect disentanglement."

## Claim 2: Emergence of Born-like Statistics
**Statement**: For certain complex detector Hamiltonians, the distribution of these special states on the Bloch sphere approximates the Born rule $\cos^2(\theta/2)$.
- **Evidence**: `VERIFIED_NUMERICALLY` (Interacting ring/chain size scaling).
- **Comparator**: Contrasted with Haar-random unitaries (isotropic) and QND (pole-only).
- **Wording Ceiling**: "Demonstrates a strong numerical preference for Born-like polar statistics."

## Claim 3: Analytical Sufficiency of Commuting-X Families
**Statement**: There exists a non-empty family of Hamiltonians (the Commuting-X class) that analytically satisfy the Born-like finite-resolution gate $C_B$.
- **Evidence**: `PROVED` (Constructive commuting family derivation).
- **Caveat**: Requires specific coupling values $g_i$.
- **Wording Ceiling**: "Proves the existence of a native Hamiltonian family that satisfies the Born-like criteria."

## Claim 4: Obstructions to Simple Commuting Fields
**Statement**: Simple commuting vector fields (e.g., $H = K - X_q V - Z_q W$ with $[K,V]=0$) cannot yield exact Born balance across open detuning intervals.
- **Evidence**: `PROVED` (Theorem H / Detuning Interval obstruction).
- **Comparator**: Shows that the "Constructive Family" is a specific point, not a generic property of commuting fields.
- **Wording Ceiling**: "Establishes a rigorous no-go for commuting vector fields."

## Claim 5: The Non-Normal Thermodynamic Limit
**Statement**: Convergence of operator moments and singular-value statistics is insufficient to determine the thermodynamic root law of non-normal projective pencils.
- **Evidence**: `PROVED` (Scalar potential $J(x)$ + Exchange channel counterexample).
- **Caveat**: Requires control over logarithmic tails of the singular-value measure.
- **Wording Ceiling**: "Falsifies the Gaussian-substitution shortcut for non-normal root limits."

## Claim 6: Structural Requirements for Born Geometry
**Statement**: Born-like root geometry is a product of specific structural properties of the relative propagator (e.g., reciprocal branch balance) rather than generic chaos or simple randomization.
- **Evidence**: `VERIFIED_NUMERICALLY` (WD vs. Haar comparison).
- **Comparator**: Haar-random is "too random" to be Born.
- **Wording Ceiling**: "Suggests that Born-like geometry requires a balance between structure and complexity."
