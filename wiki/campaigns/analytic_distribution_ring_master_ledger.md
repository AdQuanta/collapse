# Analytic \(P(\theta)\) / \(R(\theta)\) Master Ledger — ring

This is the **master progress index for the ring geometry** in the analytic-distribution program.

Use the repository's production ring coupling scalings (including the appropriate \(N\)-dependence) in every row.

> [!TIP]
> **TOKEN-EFFICIENCY & NAVIGATION DIRECTIVE:**
> To prevent context saturation, the ~1,700 atomic rows are partitioned into family-level ledgers located in [`wiki/campaigns/ledgers/ring/`](ledgers/ring/).
> When working on a given Case $k$, open **only** the corresponding family ledger file (e.g., [`family_A.md`](ledgers/ring/family_A.md)) or use `grep_search` on the specific case code (e.g. `0.H0`). **Do not load or edit all families simultaneously.**

---

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

---

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

---

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

---

## Master Family Index

The atomic rows are partitioned across 14 dedicated family ledgers in [`wiki/campaigns/ledgers/ring/`](ledgers/ring/):

| Family | Case Range | Physical Model Description | Rows | Family Ledger Link | Status | Born Profile Target |
|---|---|---|---|---|---|---|
| **Family A** | Cases 0–8 | Decoupled baseline and one-axis / QND cases ($g_z$) | 70 | [`ledgers/ring/family_A.md`](ledgers/ring/family_A.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family B** | Cases 9–14 | Transverse-field Ising model (TFIM / Ising ladder) | 60 | [`ledgers/ring/family_B.md`](ledgers/ring/family_B.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family C** | Cases 15–17 | XX ladder ($J_x = J_y \equiv J_\perp$) | 30 | [`ledgers/ring/family_C.md`](ledgers/ring/family_C.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family D** | Cases 18–20 | XY ladder (isotropic & anisotropic branches) | 60 | [`ledgers/ring/family_D.md`](ledgers/ring/family_D.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family E** | Cases 21–26 | XXZ ladder (easy-plane, Heisenberg, easy-axis, critical) | 300 | [`ledgers/ring/family_E.md`](ledgers/ring/family_E.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family F** | Cases 27–32 | Anisotropic XYZ ladder with longitudinal qubit coupling ($g_z$) | 60 | [`ledgers/ring/family_F.md`](ledgers/ring/family_F.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family G** | Cases 33–36 | Perturbative transverse qubit–detector coupling ($g_\perp$) | 40 | [`ledgers/ring/family_G.md`](ledgers/ring/family_G.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family H** | Cases 37–40 | Multi-axis perturbative qubit coupling ($g_\perp, g_z$) — Full NN Family | 40 | [`ledgers/ring/family_H.md`](ledgers/ring/family_H.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family I** | Cases 41–48 | Single-axis NNN couplings ($J_{2z}$) | 100 | [`ledgers/ring/family_I.md`](ledgers/ring/family_I.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family J** | Cases 49–54 | Frustrated Ising models with competing NN/NNN interactions | 120 | [`ledgers/ring/family_J.md`](ledgers/ring/family_J.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family K** | Cases 55–60 | NNN XX and XY models | 180 | [`ledgers/ring/family_K.md`](ledgers/ring/family_K.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family L** | Cases 61–69 | NNN XXZ models | 450 | [`ledgers/ring/family_L.md`](ledgers/ring/family_L.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family M** | Cases 70–77 | Anisotropic NNN XYZ models | 80 | [`ledgers/ring/family_M.md`](ledgers/ring/family_M.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Family N** | Cases 78–86 | Full production Hamiltonian with arbitrary NN/NNN XYZ and multi-axis coupling | 90 | [`ledgers/ring/family_N.md`](ledgers/ring/family_N.md) | `OPEN` | $R = \cos^2(\theta/2)$ |
| **Total** | **Cases 0–86** | **Full Ring Program** | **1,680** | — | `OPEN` | — |
