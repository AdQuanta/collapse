# Perturbative Born Resolution & Open Ring Phase

## Overview
This campaign document synthesizes the positive resolution of the exact Born law problem under perturbative qubit-detector coupling, formulated in `research_reports/EXACT_BORN_PERTURBATIVE_RESOLUTION.md`.

---

## The Theorem

$$
\boxed{
R_*(\theta) = \cos^2(\theta/2) \iff \sin^2(\theta/2) P_*(\theta) \text{ is reflection-even under } \theta \mapsto \pi - \theta
}
$$

### Core Equivalences
1. **Even Envelope Decomposition:** $P_*(\theta) = (1+\cos\theta)E_*(\theta)$ for any reflection-even function $E_*(\pi-\theta) = E_*(\theta)$.
2. **Arithmetic-Mean Moment Relations:** $a_{2m+1} = \frac{a_{2m} + a_{2m+2}}{2} \iff d_m \equiv 2a_{2m+1} - a_{2m} - a_{2m+2} = 0 \quad (\forall m \ge 0)$.
3. **Relative-Unitary Operator Identity:** For $X_0$-conserving systems ($[H, X_0] = 0$), $W(t) = U_+(t)^\dagger U_-(t)$ obeys:
   $$
   C_B: \quad \lim_{t\to\infty}\lim_{N\to\infty} \operatorname{Re}\,\tau_D\left( W(t)^{2m} (I - W(t))^2 \right) = 0 \quad (\forall m \ge 0).
   $$

---

## Open Hamiltonian Region $\mathcal{P}_B$

The condition is satisfied on the finite-width open parameter volume in the interacting XXZ ring family:
$$
\mathcal{P}_B = \left\{ (J, J_\pm, J_2, J_{\pm 2}, h_z, g_x) \in \mathbb{R}^6 :
\begin{aligned}
& J \in [0.015, 0.045], \quad J_\pm \in [0.006, 0.025], \\
& J_2 \in [0.0, 0.020], \quad J_{\pm 2} \in [0.0, 0.005], \\
& h_z \in [0.025, 0.075], \quad g_x \in [0.0005, 0.0030]
\end{aligned}
\right\}.
$$

---

## Numerical Scaling & Evidence

- **Small to Intermediate Sizes ($N = 6, 8, 10, 12$):** Computed locally via QuSpin symmetry sectors; certifies full 64-bin coverage ($1.000$) by $N = 12$.
- **Thermodynamic Finite Sizes ($N = 13, 14, 15, 16, 17$):** Audited from production Zeus HPC runs up to $d = 131,072$:
  - $R_{\text{RMSE}}$ systematically falls: $0.1292$ ($N=12$) $\to 0.0511$ ($N=14$) $\to 0.0465$ ($N=15$) $\to 0.0338$ ($N=16$) $\to 0.0159$ ($N=17$).
  - Maximum Born residual $|d_m|$ drops to $0.0141$ at $N = 17$.
- **Stability:** Certified across $\pm 10\%\text{--}20\%$ perturbations in all microscopic parameters, second-neighbor couplings, and multichannel $J_z, J_{zx}$ additions.

See also: [[born-like-points]], [[projective-roots]], [[hamiltonian-families]], [[foundational-draft-aug2026]].
