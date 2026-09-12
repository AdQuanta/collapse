# Weak Coupling Search (Rings & Chains)

## Objective
Construct robust, stable Born families using perturbative qubit-detector coupling, specifically focusing on interacting XYZ rings and endpoint-chains.

## Hamiltonian Conventions
The search uses a specific scaling to maintain stability as $N$ grows:
- **Ring Interaction**: $V_N = \frac{g_x}{\sqrt{N}} X_0 \sum X_i + \frac{g_y}{\sqrt{N}} Y_0 \sum Y_i + \frac{g_z}{N} Z_0 \sum Z_i$.
- **Chain Interaction**: $V_N = g_x X_0 X_1 + g_y Y_0 Y_1 + g_z Z_0 Z_1$ (endpoint attachment).

## Positive Numerical Leads
Interacting detectors (with non-zero $J_{r\alpha}$ bonds) show a promising trend: the ratio RMSE decreases as $N$ increases.
- **Nearest-neighbor ring**: RMSE $0.051 \to 0.016$ for $N=14 \to 17$.
- **Second-neighbor ring**: RMSE $0.058 \to 0.018$ for $N=14 \to 17$.
Both families exhibit full reflected polar coverage at $N=17$, though they remain $X$-conserving (roots lie on a great circle).

## Weak-Coupling Reduction
To analyze the dynamics without full diagonalization, a first-order Magnus approximation is used in the interaction picture:
$$ U^{(1)}(t) = e^{-iH_0t} e^{-i K_1(t)} $$
where $K_1(t) = \int_0^t V_I(s) ds$. This reduction retains resonances through a $\text{sinc}$ filter:
$$ (K_1)_{ab} = V_{ab} t e^{i\Delta t/2} \text{sinc}(\Delta t/2) $$
This provides a size-uniform estimate of the propagator in trace norm, useful for constructing effective propagators.

## Current Strategy
1. **Expand Coupling**: Move beyond $X$-only slices by admitting independent $g_x, g_y, g_z$ and central fields $h_0$.
2. **Resum Resonances**: Develop an effective dynamics that resums resonant subspaces and their second-order shifts.
3. **Certify Stability**: Establish a finite-width parameter neighborhood where reciprocal balance is maintained.

See also: [[born-like-points]], [[production-pipeline]].
