# Analytic \(P(\theta)\) / \(R(\theta)\) Master Ledger — ring

This is the **single atomic progress ledger for the ring geometry** in the analytic-distribution program.

Use the repository's production ring coupling scalings (including the appropriate \(N\)-dependence) in every row.

Every physical case/subcase occupies its **own row** so an agent can progress mechanically through the program without implicitly collapsing distinct regimes.

## Completion rule

A row may be marked `PROVED` only after the requested analytical program has been addressed for the **ring** geometry, including:

- specialized Hamiltonian;
- actual perturbative control parameter and Type I–V classification;
- symmetry / sector / integrability structure;
- analytical projective-root representation;
- \(P_N(\theta,t)\);
- \(P_\infty(\theta,t)\);
- \(\overline P_N(\theta)\);
- \(\overline P_\infty(\theta)\);
- \(R_N(\theta,t)\);
- \(R_\infty(\theta,t)\);
- \(\overline R_N(\theta)\);
- \(\overline R_\infty(\theta)\);
- support, atoms, zero roots, infinite roots, and indeterminate pencils;
- reductions to all nested earlier cases;
- independent verification where applicable;
- explicit perturbative validity domain;
- analytical comparison to \(R_{\rm Born}(\theta)=\cos^2(\theta/2)\).

Allowed status labels:

`PROVED` · `VERIFIED_NUMERICALLY` · `PRELIMINARY_NUMERIC` · `CONJECTURE` · `FALSIFIED` · `OPEN`

## \(h_0\)-regime notation

Let \(\Lambda\) be the characteristic nonzero intrinsic detector scale relevant to that row. When no intrinsic detector scale exists, use the nonzero qubit–detector coupling as the comparison scale.

| Code | Meaning |
|---|---|
| H0 | \(\mathbf h_0=0\) |
| HzS | \(\mathbf h_0=h_{0z}\hat z,\ 0<|h_{0z}|\ll\Lambda\) |
| HzC | \(\mathbf h_0=h_{0z}\hat z,\ |h_{0z}|\sim\Lambda\) |
| HzL | \(\mathbf h_0=h_{0z}\hat z,\ \Lambda\ll|h_{0z}|\) |
| HpS | \(h_{0z}=0,\ 0<h_{0\perp}\ll\Lambda\) |
| HpC | \(h_{0z}=0,\ h_{0\perp}\sim\Lambda\) |
| HpL | \(h_{0z}=0,\ \Lambda\ll h_{0\perp}\) |
| HgS | \(h_{0z}h_{0\perp}\neq0,\ 0<|\mathbf h_0|\ll\Lambda\) |
| HgC | \(h_{0z}h_{0\perp}\neq0,\ |\mathbf h_0|\sim\Lambda\) |
| HgL | \(h_{0z}h_{0\perp}\neq0,\ \Lambda\ll|\mathbf h_0|\) |

with \(h_{0\perp}=\sqrt{h_{0x}^2+h_{0y}^2}\).

## Additional branch codes

| Code | Meaning |
|---|---|
| ISO | isotropic XY branch, \(J_x=J_y\) |
| ANI | anisotropic XY branch, \(J_x\neq J_y\) |
| EP | easy-plane / Luttinger-like |
| HV | Heisenberg vicinity |
| EA | easy-axis |
| FP | field-polarized |
| CR | critical / gapless boundary or manifold |

## Master ledger

| family | case | parent case | nonzero coefficients | scale hierarchy | h0 regime | perturbative type | perturbative parameter | P_N | P_inf | Pbar_N | Pbar_inf | R_N | R_inf | Rbar_N | Rbar_inf | Born deviation | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A baseline | 0.H0 | 0 | none | decoupled detector baseline | $\mathbf h_0=0$ | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A baseline | 0.Hz | 0 | none | decoupled detector baseline | $\mathbf h_0=h_{0z}\hat z\neq0$ | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A baseline | 0.Hp | 0 | none | decoupled detector baseline | $h_{0z}=0,\ h_{0\perp}>0$ | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A baseline | 0.Hg | 0 | none | decoupled detector baseline | $h_{0z}h_{0\perp}\neq0$ | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.H0 | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HzS | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HzC | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HzL | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HpS | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HpC | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HpL | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HgS | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HgC | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 1.HgL | 1 | $g_z$ | perturbative $g_z$; $\Lambda=\|g_z\|$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.H0 | 2 | $h_z,g_z$ | $g_z\ll h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HzS | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HzC | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HzL | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HpS | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HpC | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HpL | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HgS | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HgC | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 2.HgL | 2 | $h_z,g_z$ | $g_z\ll h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 3.HzL | 3 | $h_z,g_z$ | $g_z\ll h_z\ll\|\mathbf h_0\|$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 3.HpL | 3 | $h_z,g_z$ | $g_z\ll h_z\ll\|\mathbf h_0\|$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 3.HgL | 3 | $h_z,g_z$ | $g_z\ll h_z\ll\|\mathbf h_0\|$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 4.HzS | 4 | $h_z,g_z$ | $g_z\ll\|\mathbf h_0\|\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 4.HpS | 4 | $h_z,g_z$ | $g_z\ll\|\mathbf h_0\|\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 4.HgS | 4 | $h_z,g_z$ | $g_z\ll\|\mathbf h_0\|\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.H0 | 5 | $J_z,g_z$ | $g_z\ll J_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HzS | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HzC | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HzL | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HpS | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HpC | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HpL | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HgS | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HgC | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 5.HgL | 5 | $J_z,g_z$ | $g_z\ll J_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.H0 | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HzS | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HzC | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HzL | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HpS | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HpC | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HpL | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HgS | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HgC | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 6.HgL | 6 | $h_z,J_z,g_z$ | $g_z\ll h_z\ll J_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.H0 | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HzS | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HzC | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HzL | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HpS | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HpC | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HpL | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HgS | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HgC | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 7.HgL | 7 | $h_z,J_z,g_z$ | $g_z\ll J_z\ll h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.H0 | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HzS | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HzC | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HzL | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HpS | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HpC | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HpL | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HgS | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HgC | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| A QND | 8.HgL | 8 | $h_z,J_z,g_z$ | $g_z\ll h_z\sim J_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.H0 | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HzS | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HzC | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HzL | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HpS | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HpC | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HpL | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HgS | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HgC | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 9.HgL | 9 | $h_x,J_z,g_z$ | $g_z\ll h_x\ll J_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.H0 | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HzS | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HzC | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HzL | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HpS | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HpC | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HpL | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HgS | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HgC | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 10.HgL | 10 | $h_x,J_z,g_z$ | $g_z\ll J_z\ll h_x$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.H0 | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HzS | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HzC | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HzL | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HpS | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HpC | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HpL | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HgS | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HgC | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 11.HgL | 11 | $h_x,J_z,g_z$ | $g_z\ll h_x\sim J_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.H0 | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HzS | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HzC | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HzL | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HpS | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HpC | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HpL | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HgS | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HgC | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 12.HgL | 12 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_z\ll h_x\ll J_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.H0 | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HzS | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HzC | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HzL | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HpS | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HpC | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HpL | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HgS | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HgC | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 13.HgL | 13 | $h_x,h_z,J_z,g_z$ | $g_z\ll h_x\ll h_z\ll J_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.H0 | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HzS | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HzC | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HzL | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HpS | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HpC | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HpL | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HgS | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HgC | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| B TFIM/Ising | 14.HgL | 14 | $h_x,h_z,J_z,g_z$ | $g_z\ll J_z\ll h_x,h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.H0 | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HzS | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HzC | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HzL | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HpS | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HpC | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HpL | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HgS | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HgC | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 15.HgL | 15 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\ll J_\perp$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.H0 | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HzS | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HzC | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HzL | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HpS | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HpC | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HpL | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HgS | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HgC | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 16.HgL | 16 | $h_z,J_\perp,g_z$ | $g_z\ll J_\perp\ll h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.H0 | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HzS | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HzC | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HzL | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HpS | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HpC | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HpL | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HgS | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HgC | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| C XX | 17.HgL | 17 | $h_z,J_\perp,g_z$ | $g_z\ll h_z\sim J_\perp$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.H0 | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HzS | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HzC | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HzL | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HpS | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HpC | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HpL | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HgS | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HgC | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ISO.HgL | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x=J_y$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.H0 | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HzS | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HzC | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HzL | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HpS | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HpC | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HpL | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HgS | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HgC | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 18.ANI.HgL | 18 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\ll\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.H0 | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HzS | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HzC | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HzL | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HpS | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HpC | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HpL | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HgS | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HgC | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ISO.HgL | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x=J_y$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.H0 | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HzS | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HzC | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HzL | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HpS | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HpC | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HpL | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HgS | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HgC | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 19.ANI.HgL | 19 | $h_z,J_x,J_y,g_z$ | $g_z\ll\|J_x\|,\|J_y\|\ll h_z$; $J_x\neq J_y$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.H0 | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HzS | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HzC | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HzL | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HpS | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HpC | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HpL | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HgS | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HgC | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ISO.HgL | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x=J_y$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.H0 | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HzS | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HzC | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HzL | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HpS | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HpC | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HpL | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HgS | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HgC | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| D XY | 20.ANI.HgL | 20 | $h_z,J_x,J_y,g_z$ | $g_z\ll h_z\sim\|J_x\|,\|J_y\|$; $J_x\neq J_y$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.H0 | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HzS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HzC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HzL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HpS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HpC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HpL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HgS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HgC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EP.HgL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.H0 | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HzS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HzC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HzL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HpS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HpC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HpL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HgS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HgC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.HV.HgL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.H0 | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HzS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HzC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HzL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HpS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HpC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HpL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HgS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HgC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.EA.HgL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.H0 | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HzS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HzC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HzL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HpS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HpC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HpL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HgS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HgC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.FP.HgL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.H0 | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HzS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HzC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HzL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HpS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HpC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HpL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HgS | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HgC | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 21.CR.HgL | 21 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp,J_z$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.H0 | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HzS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HzC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HzL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HpS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HpC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HpL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HgS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HgC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EP.HgL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.H0 | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HzS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HzC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HzL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HpS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HpC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HpL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HgS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HgC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.HV.HgL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.H0 | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HzS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HzC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HzL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HpS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HpC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HpL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HgS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HgC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.EA.HgL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.H0 | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HzS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HzC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HzL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HpS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HpC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HpL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HgS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HgC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.FP.HgL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.H0 | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HzS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HzC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HzL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HpS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HpC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HpL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HgS | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HgC | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 22.CR.HgL | 22 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_\perp\ll J_z$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.H0 | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HzS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HzC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HzL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HpS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HpC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HpL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HgS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HgC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EP.HgL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.H0 | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HzS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HzC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HzL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HpS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HpC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HpL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HgS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HgC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.HV.HgL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.H0 | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HzS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HzC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HzL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HpS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HpC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HpL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HgS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HgC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.EA.HgL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.H0 | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HzS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HzC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HzL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HpS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HpC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HpL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HgS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HgC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.FP.HgL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.H0 | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HzS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HzC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HzL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HpS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HpC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HpL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HgS | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HgC | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 23.CR.HgL | 23 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\ll J_\perp$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.H0 | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HzS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HzC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HzL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HpS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HpC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HpL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HgS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HgC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EP.HgL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.H0 | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HzS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HzC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HzL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HpS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HpC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HpL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HgS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HgC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.HV.HgL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.H0 | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HzS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HzC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HzL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HpS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HpC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HpL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HgS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HgC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.EA.HgL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.H0 | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HzS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HzC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HzL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HpS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HpC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HpL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HgS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HgC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.FP.HgL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.H0 | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HzS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HzC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HzL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HpS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HpC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HpL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HgS | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HgC | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 24.CR.HgL | 24 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\ll J_z\sim J_\perp$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.H0 | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HzS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HzC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HzL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HpS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HpC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HpL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HgS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HgC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EP.HgL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.H0 | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HzS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HzC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HzL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HpS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HpC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HpL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HgS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HgC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.HV.HgL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.H0 | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HzS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HzC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HzL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HpS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HpC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HpL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HgS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HgC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.EA.HgL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.H0 | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HzS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HzC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HzL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HpS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HpC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HpL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HgS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HgC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.FP.HgL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.H0 | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HzS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HzC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HzL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HpS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HpC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HpL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HgS | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HgC | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 25.CR.HgL | 25 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll J_\perp,J_z\ll h_z$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.H0 | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HzS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HzC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HzL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HpS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HpC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HpL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HgS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HgC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EP.HgL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.H0 | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HzS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HzC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HzL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HpS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HpC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HpL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HgS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HgC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.HV.HgL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.H0 | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HzS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HzC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HzL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HpS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HpC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HpL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HgS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HgC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.EA.HgL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.H0 | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HzS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HzC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HzL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HpS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HpC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HpL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HgS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HgC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.FP.HgL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.H0 | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HzS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HzC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HzL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HpS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HpC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HpL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HgS | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HgC | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| E XXZ | 26.CR.HgL | 26 | $h_z,J_\perp,J_z,g_z$ | $g_z\ll h_z\sim J_\perp,J_z$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.H0 | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HzS | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HzC | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HzL | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HpS | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HpC | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HpL | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HgS | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HgC | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 27.HgL | 27 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\ll J_\alpha$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.H0 | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HzS | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HzC | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HzL | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HpS | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HpC | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HpL | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HgS | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HgC | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 28.HgL | 28 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll J_\alpha\ll h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.H0 | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HzS | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HzC | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HzL | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HpS | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HpC | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HpL | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HgS | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HgC | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 29.HgL | 29 | $h_z,J_x,J_y,J_z,g_z$ | $g_z\ll h_z\sim J_\alpha$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.H0 | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HzS | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HzC | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HzL | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HpS | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HpC | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HpL | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HgS | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HgC | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 30.HgL | 30 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\ll J$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.H0 | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HzS | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HzC | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HzL | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HpS | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HpC | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HpL | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HgS | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HgC | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 31.HgL | 31 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll J\ll\|\mathbf h\|$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.H0 | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HzS | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HzC | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HzL | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HpS | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HpC | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HpL | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HgS | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HgC | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| F XYZ + longitudinal coupling | 32.HgL | 32 | $\mathbf h,J_x,J_y,J_z,g_z$ | $g_z\ll\|\mathbf h\|\sim J$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.H0 | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HzS | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HzC | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HzL | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HpS | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HpC | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HpL | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HgS | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HgC | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 33.HgL | 33 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll h_z\ll J_\perp$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.H0 | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HzS | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HzC | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HzL | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HpS | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HpC | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HpL | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HgS | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HgC | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 34.HgL | 34 | $h_z,J_x=J_y,g_x=g_y$ | $g_\perp\ll J_\perp\ll h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.H0 | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HzS | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HzC | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HzL | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HpS | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HpC | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HpL | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HgS | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HgC | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 35.HgL | 35 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll h_z\ll J$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.H0 | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HzS | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HzC | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HzL | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HpS | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HpC | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HpL | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HgS | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HgC | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| G transverse coupling | 36.HgL | 36 | $h_z,J_x=J_y,J_z,g_x=g_y$ | $g_\perp\ll J\ll h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.H0 | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HzS | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HzC | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HzL | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HpS | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HpC | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HpL | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HgS | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HgC | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 37.HgL | 37 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll h_z\ll J$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.H0 | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HzS | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HzC | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HzL | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HpS | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HpC | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HpL | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HgS | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HgC | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 38.HgL | 38 | $h_z,J_x=J_y,J_z,g_x=g_y,g_z$ | $g_\perp,g_z\ll J\ll h_z$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.H0 | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HzS | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HzC | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HzL | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HpS | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HpC | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HpL | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HgS | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HgC | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 39.HgL | 39 | $\mathbf h,J_x,J_y,J_z,g_x,g_y$ | $g_x,g_y\ll h,J$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.H0 | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HzS | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HzC | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HzL | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HpS | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HpC | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HpL | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HgS | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HgC | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| H multi-axis coupling | 40.HgL | 40 | $\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z$ | $g_x,g_y,g_z\ll h,J$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.H0 | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HzS | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HzC | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HzL | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HpS | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HpC | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HpL | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HgS | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HgC | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 41.HgL | 41 | one $J_{2z}$ + parent NN family | $J_2\ll J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.H0 | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HzS | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HzC | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HzL | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HpS | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HpC | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HpL | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HgS | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HgC | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 42.HgL | 42 | one $J_{2z}$ + parent NN family | $J_2\sim J_1,\ J_2\ll h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.H0 | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HzS | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HzC | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HzL | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HpS | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HpC | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HpL | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HgS | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HgC | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 43.HgL | 43 | one $J_{2z}$ + parent NN family | $J_2\sim h,\ J_2\lesssim J_1$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.H0 | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HzS | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HzC | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HzL | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HpS | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HpC | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HpL | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HgS | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HgC | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 44.HgL | 44 | one $J_{2z}$ + parent NN family | $J_1,h\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.H0 | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HzS | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HzC | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HzL | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HpS | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HpC | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HpL | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HgS | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HgC | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 45.HgL | 45 | one $J_{2x}$ + parent NN family | $J_2\ll J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.H0 | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HzS | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HzC | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HzL | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HpS | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HpC | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HpL | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HgS | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HgC | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 46.HgL | 46 | one $J_{2x}$ + parent NN family | $J_2\sim J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.H0 | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HzS | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HzC | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HzL | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HpS | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HpC | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HpL | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HgS | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HgC | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 47.HgL | 47 | one $J_{2x}$ + parent NN family | $J_1,h\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.H0 | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HzS | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HzC | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HzL | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HpS | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HpC | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HpL | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HgS | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HgC | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.W.HgL | 48 | one $J_{2y}$ + parent NN family | $J_2\ll J_1,h$; weak NNN | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.H0 | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HzS | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HzC | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HzL | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HpS | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HpC | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HpL | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HgS | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HgC | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.C.HgL | 48 | one $J_{2y}$ + parent NN family | $J_2\sim J_1,h$; comparable NNN | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.H0 | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HzS | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HzC | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HzL | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HpS | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HpC | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HpL | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HgS | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HgC | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| I single-axis NNN | 48.D.HgL | 48 | one $J_{2y}$ + parent NN family | $J_1,h\ll J_2$; NNN-dominated | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.H0 | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HzS | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HzC | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HzL | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HpS | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HpC | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HpL | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HgS | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HgC | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 49.HgL | 49 | $h_z,J_{1z},J_{2z}$ | $J_2\ll J_1$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.H0 | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HzS | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HzC | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HzL | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HpS | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HpC | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HpL | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HgS | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HgC | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 50.HgL | 50 | $h_z,J_{1z},J_{2z}$ | $J_2\sim J_1$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.H0 | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HzS | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HzC | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HzL | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HpS | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HpC | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HpL | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HgS | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HgC | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 51.HgL | 51 | $h_z,J_{1z},J_{2z}$ | $J_1\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.H0 | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HzS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HzC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HzL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HpS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HpC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HpL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HgS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HgC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KW.HgL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\ll J_1$; weak frustration | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.H0 | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HzS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HzC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HzL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HpS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HpC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HpL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HgS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HgC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KC.HgL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_2\sim J_1$; frustration crossover | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.H0 | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HzS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HzC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HzL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HpS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HpC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HpL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HgS | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HgC | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 52.KD.HgL | 52 | $h_x,J_{1z},J_{2z}$ | $h_x\ll J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.H0 | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HzS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HzC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HzL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HpS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HpC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HpL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HgS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HgC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KW.HgL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\ll J_1$; weak frustration | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.H0 | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HzS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HzC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HzL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HpS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HpC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HpL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HgS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HgC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KC.HgL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_2\sim J_1$; frustration crossover | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.H0 | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HzS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HzC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HzL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HpS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HpC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HpL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HgS | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HgC | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 53.KD.HgL | 53 | $h_x,J_{1z},J_{2z}$ | $h_x\sim J_1,J_2$; $J_1\ll J_2$; NNN-dominated | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.H0 | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HzS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HzC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HzL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HpS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HpC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HpL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HgS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HgC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KW.HgL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\ll J_1$; weak frustration | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.H0 | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HzS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HzC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HzL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HpS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HpC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HpL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HgS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HgC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KC.HgL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_2\sim J_1$; frustration crossover | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.H0 | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HzS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HzC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HzL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HpS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HpC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HpL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HgS | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HgC | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| J frustrated Ising | 54.KD.HgL | 54 | $h_x,J_{1z},J_{2z}$ | $J_1,J_2\ll h_x$; $J_1\ll J_2$; NNN-dominated | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.H0 | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HzS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HzC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HzL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HpS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HpC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HpL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HgS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HgC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hS.HgL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\ll J_1,J_2$; weak field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.H0 | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HzS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HzC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HzL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HpS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HpC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HpL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HgS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HgC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hC.HgL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.H0 | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HzS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HzC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HzL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HpS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HpC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HpL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HgS | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HgC | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 55.hL.HgL | 55 | NN XX + NNN XX | $J_{2\perp}\ll J_{1\perp}$; $J_1,J_2\ll h$; strong field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.H0 | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HzS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HzC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HzL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HpS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HpC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HpL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HgS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HgC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hS.HgL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\ll J_1,J_2$; weak field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.H0 | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HzS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HzC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HzL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HpS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HpC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HpL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HgS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HgC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hC.HgL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $h\sim J_1,J_2$; comparable field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.H0 | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HzS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HzC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HzL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HpS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HpC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HpL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HgS | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HgC | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 56.hL.HgL | 56 | NN XX + NNN XX | $J_{2\perp}\sim J_{1\perp}$; $J_1,J_2\ll h$; strong field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.H0 | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HzS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HzC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HzL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HpS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HpC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HpL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HgS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HgC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hS.HgL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\ll J_1,J_2$; weak field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.H0 | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HzS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HzC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HzL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HpS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HpC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HpL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HgS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HgC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hC.HgL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $h\sim J_1,J_2$; comparable field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.H0 | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HzS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HzC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HzL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HpS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HpC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HpL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HgS | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HgC | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 57.hL.HgL | 57 | NN XX + NNN XX | $J_{1\perp}\ll J_{2\perp}$; $J_1,J_2\ll h$; strong field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.H0 | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HzS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HzC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HzL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HpS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HpC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HpL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HgS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HgC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hS.HgL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\ll J_1,J_2$; weak field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.H0 | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HzS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HzC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HzL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HpS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HpC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HpL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HgS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HgC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hC.HgL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $h\sim J_1,J_2$; comparable field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.H0 | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HzS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HzC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HzL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HpS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HpC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HpL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HgS | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HgC | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 58.hL.HgL | 58 | anisotropic NN+NNN XY | $J_2\ll J_1$; $J_1,J_2\ll h$; strong field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.H0 | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HzS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HzC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HzL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HpS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HpC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HpL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HgS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HgC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hS.HgL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\ll J_1,J_2$; weak field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.H0 | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HzS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HzC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HzL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HpS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HpC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HpL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HgS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HgC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hC.HgL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $h\sim J_1,J_2$; comparable field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.H0 | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HzS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HzC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HzL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HpS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HpC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HpL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HgS | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HgC | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 59.hL.HgL | 59 | anisotropic NN+NNN XY | $J_2\sim J_1$; $J_1,J_2\ll h$; strong field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.H0 | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HzS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HzC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HzL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HpS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HpC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HpL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HgS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HgC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hS.HgL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\ll J_1,J_2$; weak field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.H0 | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HzS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HzC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HzL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HpS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HpC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HpL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HgS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HgC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hC.HgL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $h\sim J_1,J_2$; comparable field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.H0 | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HzS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HzC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HzL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HpS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HpC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HpL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HgS | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HgC | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| K NNN XX/XY | 60.hL.HgL | 60 | anisotropic NN+NNN XY | $J_1\ll J_2$; $J_1,J_2\ll h$; strong field | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.H0 | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HzS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HzC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HzL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HpS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HpC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HpL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HgS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HgC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EP.HgL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.H0 | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HzS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HzC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HzL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HpS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HpC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HpL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HgS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HgC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.HV.HgL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.H0 | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HzS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HzC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HzL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HpS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HpC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HpL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HgS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HgC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.EA.HgL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.H0 | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HzS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HzC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HzL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HpS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HpC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HpL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HgS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HgC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.FP.HgL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.H0 | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HzS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HzC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HzL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HpS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HpC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HpL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HgS | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HgC | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 61.CR.HgL | 61 | NN+NNN XXZ | $J_2\ll J_1,\ h\ll J_1$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.H0 | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HzS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HzC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HzL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HpS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HpC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HpL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HgS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HgC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EP.HgL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.H0 | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HzS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HzC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HzL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HpS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HpC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HpL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HgS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HgC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.HV.HgL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.H0 | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HzS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HzC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HzL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HpS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HpC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HpL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HgS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HgC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.EA.HgL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.H0 | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HzS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HzC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HzL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HpS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HpC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HpL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HgS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HgC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.FP.HgL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.H0 | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HzS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HzC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HzL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HpS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HpC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HpL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HgS | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HgC | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 62.CR.HgL | 62 | NN+NNN XXZ | $J_2\ll J_1,\ h\sim J_1$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.H0 | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HzS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HzC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HzL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HpS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HpC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HpL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HgS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HgC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EP.HgL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.H0 | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HzS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HzC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HzL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HpS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HpC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HpL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HgS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HgC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.HV.HgL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.H0 | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HzS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HzC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HzL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HpS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HpC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HpL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HgS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HgC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.EA.HgL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.H0 | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HzS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HzC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HzL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HpS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HpC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HpL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HgS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HgC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.FP.HgL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.H0 | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HzS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HzC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HzL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HpS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HpC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HpL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HgS | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HgC | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 63.CR.HgL | 63 | NN+NNN XXZ | $J_2\ll J_1\ll h$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.H0 | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HzS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HzC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HzL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HpS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HpC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HpL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HgS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HgC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EP.HgL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.H0 | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HzS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HzC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HzL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HpS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HpC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HpL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HgS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HgC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.HV.HgL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.H0 | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HzS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HzC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HzL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HpS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HpC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HpL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HgS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HgC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.EA.HgL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.H0 | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HzS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HzC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HzL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HpS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HpC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HpL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HgS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HgC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.FP.HgL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.H0 | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HzS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HzC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HzL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HpS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HpC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HpL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HgS | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HgC | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 64.CR.HgL | 64 | NN+NNN XXZ | $J_2\sim J_1,\ h\ll J_1,J_2$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.H0 | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HzS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HzC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HzL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HpS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HpC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HpL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HgS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HgC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EP.HgL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.H0 | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HzS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HzC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HzL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HpS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HpC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HpL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HgS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HgC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.HV.HgL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.H0 | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HzS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HzC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HzL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HpS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HpC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HpL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HgS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HgC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.EA.HgL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.H0 | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HzS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HzC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HzL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HpS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HpC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HpL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HgS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HgC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.FP.HgL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.H0 | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HzS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HzC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HzL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HpS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HpC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HpL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HgS | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HgC | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 65.CR.HgL | 65 | NN+NNN XXZ | $J_2\sim J_1\sim h$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.H0 | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HzS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HzC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HzL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HpS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HpC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HpL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HgS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HgC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EP.HgL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.H0 | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HzS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HzC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HzL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HpS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HpC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HpL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HgS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HgC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.HV.HgL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.H0 | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HzS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HzC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HzL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HpS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HpC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HpL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HgS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HgC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.EA.HgL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.H0 | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HzS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HzC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HzL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HpS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HpC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HpL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HgS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HgC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.FP.HgL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.H0 | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HzS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HzC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HzL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HpS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HpC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HpL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HgS | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HgC | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 66.CR.HgL | 66 | NN+NNN XXZ | $J_2\sim J_1\ll h$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.H0 | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HzS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HzC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HzL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HpS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HpC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HpL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HgS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HgC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EP.HgL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.H0 | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HzS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HzC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HzL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HpS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HpC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HpL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HgS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HgC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.HV.HgL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.H0 | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HzS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HzC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HzL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HpS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HpC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HpL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HgS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HgC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.EA.HgL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.H0 | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HzS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HzC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HzL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HpS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HpC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HpL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HgS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HgC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.FP.HgL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.H0 | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HzS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HzC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HzL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HpS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HpC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HpL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HgS | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HgC | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 67.CR.HgL | 67 | NN+NNN XXZ | $J_1\ll J_2,\ h\ll J_2$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.H0 | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HzS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HzC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HzL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HpS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HpC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HpL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HgS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HgC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EP.HgL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.H0 | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HzS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HzC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HzL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HpS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HpC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HpL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HgS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HgC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.HV.HgL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.H0 | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HzS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HzC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HzL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HpS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HpC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HpL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HgS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HgC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.EA.HgL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.H0 | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HzS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HzC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HzL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HpS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HpC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HpL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HgS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HgC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.FP.HgL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.H0 | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HzS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HzC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HzL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HpS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HpC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HpL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HgS | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HgC | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 68.CR.HgL | 68 | NN+NNN XXZ | $J_1\ll J_2\sim h$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.H0 | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HzS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HzC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HzL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HpS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HpC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HpL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HgS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HgC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EP.HgL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-plane / Luttinger-like | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.H0 | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HzS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HzC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HzL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HpS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HpC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HpL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HgS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HgC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.HV.HgL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; Heisenberg vicinity | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.H0 | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HzS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HzC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HzL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HpS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HpC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HpL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HgS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HgC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.EA.HgL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; easy-axis | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.H0 | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HzS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HzC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HzL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HpS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HpC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HpL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HgS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HgC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.FP.HgL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; field-polarized | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.H0 | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HzS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HzC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HzL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HpS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HpC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HpL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HgS | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HgC | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| L NNN XXZ | 69.CR.HgL | 69 | NN+NNN XXZ | $J_1\ll J_2\ll h$; critical/gapless boundary or manifold | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.H0 | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HzS | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HzC | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HzL | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HpS | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HpC | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HpL | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HgS | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HgC | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 70.HgL | 70 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\ll J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.H0 | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HzS | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HzC | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HzL | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HpS | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HpC | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HpL | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HgS | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HgC | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 71.HgL | 71 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1,\ h\ll J$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.H0 | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HzS | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HzC | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HzL | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HpS | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HpC | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HpL | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HgS | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HgC | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 72.HgL | 72 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\sim h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.H0 | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HzS | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HzC | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HzL | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HpS | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HpC | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HpL | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HgS | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HgC | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 73.HgL | 73 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_2\sim J_1\ll h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.H0 | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HzS | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HzC | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HzL | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HpS | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HpC | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HpL | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HgS | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HgC | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 74.HgL | 74 | $\mathbf J_1,\mathbf J_2,h_z$ | $J_1,h\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.H0 | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HzS | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HzC | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HzL | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HpS | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HpC | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HpL | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HgS | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HgC | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 75.HgL | 75 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\ll J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.H0 | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HzS | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HzC | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HzL | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HpS | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HpC | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HpL | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HgS | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HgC | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 76.HgL | 76 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_2\sim J_1\sim h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.H0 | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HzS | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HzC | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HzL | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HpS | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HpC | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HpL | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HgS | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HgC | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| M NNN XYZ | 77.HgL | 77 | $\mathbf h,\mathbf J_1,\mathbf J_2$ | $J_1,h\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.H0 | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HzS | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HzC | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HzL | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HpS | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HpC | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HpL | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HgS | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HgC | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 78.HgL | 78 | full detector + $g_z$ | $g_z\ll J_2\ll J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.H0 | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HzS | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HzC | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HzL | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HpS | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HpC | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HpL | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HgS | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HgC | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 79.HgL | 79 | full detector + $g_z$ | $g_z\ll J_1\sim J_2\sim h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.H0 | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HzS | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HzC | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HzL | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HpS | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HpC | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HpL | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HgS | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HgC | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 80.HgL | 80 | full detector + $g_z$ | $g_z\ll J_1,h\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.H0 | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HzS | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HzC | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HzL | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HpS | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HpC | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HpL | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HgS | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HgC | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 81.HgL | 81 | full detector + $g_x,g_y$ | $g_\perp\ll J_2\ll J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.H0 | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HzS | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HzC | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HzL | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HpS | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HpC | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HpL | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HgS | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HgC | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 82.HgL | 82 | full detector + $g_x,g_y$ | $g_\perp\ll J_1\sim J_2\sim h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.H0 | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HzS | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HzC | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HzL | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HpS | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HpC | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HpL | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HgS | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HgC | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 83.HgL | 83 | full detector + $g_x,g_y$ | $g_\perp\ll J_1,h\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.H0 | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HzS | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HzC | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HzL | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HpS | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HpC | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HpL | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HgS | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HgC | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 84.HgL | 84 | full detector + $g_x,g_y,g_z$ | $g\ll J_2\ll J_1,h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.H0 | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HzS | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HzC | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HzL | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HpS | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HpC | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HpL | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HgS | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HgC | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 85.HgL | 85 | full detector + $g_x,g_y,g_z$ | $g\ll J_1\sim J_2\sim h$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.H0 | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | H0 | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HzS | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HzS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HzC | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HzC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HzL | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HzL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HpS | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HpS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HpC | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HpC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HpL | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HpL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HgS | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HgS | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HgC | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HgC | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
| N full NNN production | 86.HgL | 86 | full detector + $g_x,g_y,g_z$ | $g\ll J_1,h\ll J_2$ | HgL | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN | OPEN |
