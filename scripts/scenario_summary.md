# Full Hamiltonian Scenario Scan — Scenario Summary

This document describes every scenario evaluated by
[full_hamiltonian_scan.py](full_hamiltonian_scan.py).
All scenarios use `seed=44` and are evaluated at times
**t = 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100**.
No symmetries are exploited (NumPy Hamiltonians, full dense diagonalization).

---

## 1. Central Spin (CS) — 40 scenarios

### Hamiltonian

$$
H = -\sum_{i=1}^{N^*}\bigl(J_x\, X_0 X_i + J_z\, Z_0 Z_i\bigr)
    -\sum_{i=0}^{N}\bigl(h_x\, X_i + h_z\, Z_i\bigr)
$$

Qubit 0 is the central qubit; qubits 1…N* are satellite qubits ($N^* = N - 1$).

### Clean Coupling Regimes (8)

| # | Label | $J_x$ | $J_z$ | Physical meaning |
|---|-------|--------|--------|------------------|
| 1 | Clean Ising | 0 | 1 | Pure ZZ star — diagonal in computational basis |
| 2 | Heisenberg | 1 | 1 | Isotropic XX+ZZ; maximally scrambling |
| 3 | XX-only | 1 | 0 | Pure XX; conserves total $S_z$ |
| 4 | Weak | 0.1 | 0.1 | Near-free / perturbative regime |
| 5 | Strong | 3 | 3 | Fast scrambling |
| 6 | Extremely weak | 0.01 | 0.01 | Ultra-perturbative; near-perfect disentanglement |
| 7 | Extremely strong | 10 | 10 | Ultra-strong; very rapid scrambling |
| 8 | Asymmetric | 0.3 | 0.8 | Tests anisotropy effects |

### Clean Field Regimes (5)

| # | Label | $h_x$ | $h_z$ | Physical meaning |
|---|-------|--------|--------|------------------|
| 9 | Transverse field | 1 | 0 | Competes with ZZ coupling |
| 10 | Longitudinal field | 0 | 1 | Adds $z$-spectrum inhomogeneity |
| 11 | Weak fields | 0.1 | 0.1 | Fields as small perturbation |
| 12 | Strong fields | 3 | 3 | Field-dominated regime |
| 13 | Mixed fields | 0.5 | 0.5 | All terms active (with $J_x{=}J_z{=}1$) |

### Disorder Regimes (27)

3 disorder components × 3 strengths × 3 distributions = 27:

| Component | Disordered param | Base | $A_\text{base}$ |
|-----------|-----------------|------|-----------------|
| Coupling (XX) | $J_x$ | $J_x{=}1, J_z{=}1$ | 2.0 |
| Coupling (ZZ) | $J_z$ | $J_x{=}0, J_z{=}1$ | 2.0 |
| Field | $h_z$ | $J_z{=}1, h_z{=}0.5$ | 2.0 |

---

## 2. Mixed-Field Ising (MFI) — 37 scenarios

### Hamiltonian

$$
H = -\sum_{i} J\, Z_i Z_{i+1} - \sum_{i} h_x\, X_i - \sum_{i} h_z\, Z_i
$$

Periodic boundary conditions. All scenarios fix **$J = 1$**.

### Clean Field Regimes (10)

| # | Label | $h_x$ | $h_z$ | Physical meaning |
|---|-------|--------|--------|------------------|
| 1 | Integrable | 1 | 0 | Transverse-field Ising at quantum critical point |
| 2 | Chaotic | 0.9045 | 0.809 | Known chaotic point; Wigner–Dyson statistics |
| 3 | Deep paramagnetic | 5 | 0 | Field-dominated; nearly free quasiparticles |
| 4 | Longitudinal only | 0 | 1 | Classical — diagonal in computational basis |
| 5 | Weak fields | 0.1 | 0.1 | Deep ferromagnetic regime |
| 6 | Strong transverse | 3 | 0 | Far into paramagnetic phase |
| 7 | Mixed fields | 0.5 | 0.5 | Non-integrable, generic dynamics |
| 8 | Extremely weak | 0.01 | 0 | Near-pure Ising chain |
| 9 | Extremely strong | 10 | 0 | Ultra-paramagnetic |
| 10 | Strong longitudinal | 0 | 3 | Classical with strong $z$-field |

### Disorder Regimes (27)

3 disorder components × 3 strengths × 3 distributions = 27:

| Component | Disordered param | Base | $A_\text{base}$ |
|-----------|-----------------|------|-----------------|
| Coupling | $J$ | $J{=}1, h_x{=}1$ | 2.0 |
| Field (long.) | $h_z$ | $h_x{=}0.5$ | 8.0 |
| Field (trans.) | $h_x$ | $h_x{=}1$ | 8.0 |

---

## 3. Single Pixel (SP) — 84 scenarios

### Hamiltonian

$$
H = -J\sum_{\langle i,j\rangle_\text{pixel}} Z_i Z_j
    -\sum_{i \in \text{targets}} \bigl(J_x\, X_0 X_i + J_z\, Z_0 Z_i\bigr)
    -\sum_{i} \bigl(h_x\, X_i + h_z\, Z_i\bigr)
$$

Qubit 0 is central; $N_\text{pixel} = N - 1$ pixel qubits. All use **$J = 1$**.

### Clean Coupling Regimes (8 per connectivity × 3 = 24)

| # | Label | $J_x$ | $J_z$ | Physical meaning |
|---|-------|--------|--------|------------------|
| 1 | Balanced | 0.5 | 0.5 | Baseline; intra-pixel dominates |
| 2 | Weak central | 0.1 | 0.1 | Central qubit nearly decoupled |
| 3 | Strong central | 1 | 1 | Matches intra-pixel coupling |
| 4 | XX-dominant | 1 | 0 | Only spin-flip coupling |
| 5 | ZZ-dominant | 0 | 1 | Only $z$-$z$ coupling |
| 6 | Asymmetric | 0.3 | 0.8 | Anisotropic central coupling |
| 7 | Extremely weak | 0.01 | 0.01 | Ultra-perturbative |
| 8 | Extremely strong | 10 | 10 | Central coupling overwhelms pixel |

### Clean Field Regimes (5 per connectivity × 3 = 15)

| # | Label | $h_x$ | $h_z$ | Physical meaning |
|---|-------|--------|--------|------------------|
| 9 | Transverse field | 1 | 0 | $h_x$ competes with ZZ pixel coupling |
| 10 | Longitudinal field | 0 | 1 | $h_z$ adds $z$-inhomogeneity |
| 11 | Weak fields | 0.1 | 0.1 | Fields as perturbation |
| 12 | Strong fields | 3 | 3 | Field-dominated dynamics |
| 13 | Mixed fields | 0.5 | 0.5 | Balanced coupling + balanced fields |

All field regimes use $J_x{=}0.5, J_z{=}0.5$ as the central coupling baseline.

### Disorder Regimes (45, ring connectivity only)

5 disorder components × 3 strengths × 3 distributions = 45:

| Component | Disordered param | Base | $A_\text{base}$ |
|-----------|-----------------|------|-----------------|
| Central coupling (XX) | $J_x$ | $J_x{=}0.5$ | 0.8 |
| Central coupling (ZZ) | $J_z$ | $J_z{=}0.5$ | 0.8 |
| Intra-pixel coupling | $J$ | $J{=}1$ | 0.8 |
| Field (long.) | $h_z$ | $h_z{=}0.3$ | 0.8 |
| Field (trans.) | $h_x$ | $h_x{=}0.3$ | 0.8 |

---

## 4. Two Pixel (TP) — 84 scenarios

### Hamiltonian

$$
H = -J\sum_{\langle i,j\rangle_{P_1}} Z_i Z_j
    -J\sum_{\langle i,j\rangle_{P_2}} Z_i Z_j
    -\sum_{i \in P_1} \bigl(J_x X_0 X_i + J_z Z_0 Z_i\bigr)
    +\sum_{i \in P_2} \bigl(J_x X_0 X_i + J_z Z_0 Z_i\bigr)
    -\sum_{i} \bigl(h_x X_i + h_z Z_i\bigr)
$$

Central qubit 0 between two pixels of $N_\text{pixel} = (N-1)/2$.
Opposite-sign coupling to the two pixels. All use **$J = 1$**.

### Clean Coupling Regimes (8 per connectivity × 3 = 24)

Same 8 coupling regimes as SP: balanced, weak, strong, XX-only, ZZ-only, asymmetric, extremely weak, extremely strong.

### Clean Field Regimes (5 per connectivity × 3 = 15)

Same 5 field regimes as SP: transverse, longitudinal, weak, strong, mixed — all with $J_x{=}0.5, J_z{=}0.5$.

### Disorder Regimes (45, ring connectivity only)

5 disorder components × 3 strengths × 3 distributions = 45:

| Component | Disordered param | Base | $A_\text{base}$ |
|-----------|-----------------|------|-----------------|
| Intra-pixel coupling | $J$ | $J{=}1$ | 0.8 |
| Central coupling (XX) | $J_x$ | $J_x{=}0.5$ | 0.8 |
| Central coupling (ZZ) | $J_z$ | $J_z{=}0.5$ | 0.8 |
| Field (trans.) | $h_x$ | $h_x{=}0.3$ | 0.5 |
| Field (long.) | $h_z$ | $h_z{=}0.3$ | 0.5 |

---

## Disorder Scaling Convention

| Distribution | Scaling | Formula |
|-------------|---------|---------|
| **Uniform** | $1/\sqrt{N}$ | $\sigma = A / \sqrt{N}$, then $\delta \sim U(-\sigma, +\sigma)$ |
| **Gaussian** | $1/\sqrt{N}$ | $\sigma = A / \sqrt{N}$, then $\delta \sim \mathcal{N}(0, \sigma)$ |
| **Lorentzian** | $1/N$ | $\gamma = A / N$, then $\delta \sim \gamma \cdot \text{Cauchy}$ |

Strength multipliers: **weak** (×0.3), **medium** (×1.0), **strong** (×3.0).

## Grand Total

| Model | Coupling | Field | Disorder | Total |
|-------|----------|-------|----------|-------|
| Central Spin | 8 | 5 | 27 | **40** |
| Mixed-Field Ising | – | 10 | 27 | **37** |
| Single Pixel | 24 | 15 | 45 | **84** |
| Two Pixel | 24 | 15 | 45 | **84** |
| **Grand Total** | **56** | **45** | **144** | **245** |

Each scenario is evaluated at 10 time points → **2450 total (scenario, time) pairs**.

---

## Complete Parameter Table (N=7)

See [scenario_table.md](scenario_table.md) for the full 245-row table with exact parameter values.
