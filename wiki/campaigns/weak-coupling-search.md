# Weak Coupling Search (Rings & Chains)

## Objective
Construct robust, stable Born families using perturbative qubit-detector coupling, specifically focusing on interacting XYZ rings and endpoint-chains.

## Hamiltonian Conventions
The user specifies the following normalization; it does not by itself prove a stable Born phase:
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
Here sinc(x)=sin(x)/x, continued at zero. The proved bound is a fixed-time estimate in normalized Hilbert–Schmidt norm, uniform in N for the stated ring normalization. It is not a trace-norm, kinetic-time, or root-convergence theorem.

## Current Strategy
1. **Expand Coupling**: Move beyond $X$-only slices by admitting independent $g_x, g_y, g_z$ and central fields $h_0$.
2. **Resum Resonances**: Develop an effective dynamics that resums resonant subspaces and their second-order shifts.
3. **Certify Stability**: Establish a finite-width parameter neighborhood where reciprocal balance is maintained.

See also: [[born-like-points]], [[production-pipeline]].

## Multichannel leads and required diagnostics (2026-09-12)
**REPRODUCED_NUMERIC.** Archived ring config_079 and config_047 have both
gx and gy nonzero. Their 64-bin ratio RMSE improves from 0.09770 to
0.05498 (N=13–15), and 0.12358 to 0.06279 (N=13–16). All have full
reflected polar coverage, at one time t=1e6. The eight-moment maximum does
not systematically improve, and no open neighborhood is established.
See [the audit and exact parameters](../../research_reports/BORN_POSITIVE_MULTICHANNEL.md).

The user requests P(theta), reflected P, and R(theta) versus cos²(theta/2)
wherever numerical candidate assessment needs them. Eight PNG/PDF figures
now cover these seven saved positive snapshots and all 48 reduced
return-study snapshots in `reports/born_positive_diagnostics_2026-09-12/`.
No smoothing or empty-bin replacement is used. Born constrains the ratio;
it does not select a unique P density.

The positive construction now uses [[resonant-return-dynamics]] to retain
conditional detector shifts and repeated qubit flips. The proposed g²/E_D
scale remains dimensional until matrix spectral-measure control is proved.

## Reduced sensitivity follow-up (2026-09-12)

**VERIFIED_NUMERICALLY:** 162 full-QZ conditions for seeds 079/047 at N=5,6,7
and t=10³,10⁵,10⁶ passed numerical validation. Independent ±h0x, ±h0y, ±h0z
and ±gz increments of .05 max(|gx|,|gy|) produced no uniformly improving
candidate under the preregistered size/worst-time rule. Every condition has
incomplete 64-bin coverage. Reduced baselines are nearly north-polar; their
small moment residuals are insufficient. Transverse fields cause large
worst-time moment errors, while longitudinal perturbations give mixed effects.
This is **INCONCLUSIVE** for the larger-N Born regime, not a full-family no-go.

**PROVED in this seed slice:** global Z rotation maps each isolated positive
transverse central field to its negative and sends lambda to -lambda, leaving
polar statistics unchanged. All 36 signed numerical pairs support the identity.

Next: verify an exact translation-sector implementation of the full ring
parameter family before larger-N time/perturbation work. Do not tune small-N
scores in the regime where balance saturates and coverage fails.
See [complete experiment](../../research_reports/BORN_MULTICHANNEL_SENSITIVITY_2026-09-12.md).
