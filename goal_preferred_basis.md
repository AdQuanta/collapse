# goal_preferred_basis.md — Campaign: the preferred basis and the strong Born criterion

> **Objective:** Decide whether the asymmetry field of the two `SPEC.md` §3 outcome measures
> converges to the exact Born form $\hat n\cdot\mathbf r$ with $\hat n$ equal to the qubit
> self-field direction $\hat h_0$, over a finite open region rather than at a point.

Status of every result below: `PRELIMINARY_NUMERIC`, single seed, **no gate credit**.
`paper_ready` remains `false`. Nothing here promotes a ledger row; promotion needs a fresh
result packet and an independent referee under the rule in
[paper-readiness-ledger.md](wiki/governance/paper-readiness-ledger.md).

---

## 1. The hypothesis, in one sentence

For the endpoint-chain family in the self-Hamiltonian-dominated regime
($|h_0|\gg\max|g|$), the asymmetry field
$a(\Omega)=(\rho_0-\rho_1)/(\rho_0+\rho_1)$ converges as $N\to\infty$ to $\hat n\cdot\mathbf r$
with $\hat n=\hat h_0$ — so that $\hat n\cdot\hat h_0\to1$, the dipole magnitude $\to1$ and the
non-dipole odd-harmonic leakage $\to0$ — throughout a finite open neighbourhood of `screen_00`.

**Pre-registered prediction (agent, 2026-09-21, before any campaign run):** the axis leg holds,
$\hat n\cdot\hat h_0>0.999$; the exactness leg fails, with the dipole statistic plateauing in
$1.05$–$1.15$ rather than at 1. Reason: the strong criterion implies the weak one, and the
budget-controlled weak score for this very region already runs
$0.557, 0.670, 0.716, 0.728, 0.707$ at $N=8\ldots12$ — turning over at $N=12$
([chain-born-regions.md](wiki/campaigns/chain-born-regions.md)). Record this prediction and
report against it; do not tune anything toward it.

---

## 2. The observable: use $B_1$, not a histogram

### 2.1 Derivation

By [outcome antipodality](wiki/concepts/outcome-antipodality.md), $\rho_1=\mathcal A_*\rho_0$, so the
strong criterion is a statement about $\rho_0$ alone:
$\rho_0(-\Omega)=\tan^2(\theta'/2)\,\rho_0(\Omega)$, with $\theta'$ the polar angle from $\hat n$.
Multiplying by $\cos^2(\theta'/2)\,g(\Omega)$ and substituting $\Omega\to-\Omega$ gives

$$\mathbb E_{\rho_0}\big[\sin^2(\theta'/2)\big(g(-\Omega)-g(\Omega)\big)\big]=0\quad\text{for all }g,$$

i.e. **the reweighted measure $\nu=\sin^2(\theta'/2)\rho_0$ is inversion-symmetric**, i.e. every
odd-$\ell$ spherical-harmonic moment of $\nu$ vanishes. This is exactly equivalent to the strong
criterion — no binning, no density ratio, no coverage requirement.

### 2.2 The closed form

Take $g=Y_{1m}$. With Bloch unit vectors $u_j$, kernel weights $k_j$ and
$w_j=(1-\hat n\cdot u_j)/2$, the $\ell=1$ block reads $\sum_j k_j(1-\hat n\cdot u_j)u_j=0$, i.e.

$$S\,\hat n = m,\qquad S=\sum_j k_j\,u_ju_j^{\mathsf T},\qquad m=\sum_j k_j\,u_j .$$

Therefore

$$\boxed{\;\hat n_{\rm raw}=S^{-1}m,\qquad \hat n=\hat n_{\rm raw}/B_1,\qquad B_1\equiv\lVert S^{-1}m\rVert\;}$$

a $3\times3$ linear solve on the root cloud. **Born forces $B_1=1$ exactly.** $B_1$ is the
binning-free replacement for the histogram dipole magnitude, and $\hat n$ is the preferred axis.

Residual Born content lives in $\ell\ge3$: with the weights recomputed at the normalized $\hat n$,
report the normalized odd-$\ell$ power for $\ell=3,5,7$, which Born sends to zero.

### 2.3 Why this replaces the histogram estimator

$B_1$ is a sample moment, so it carries bootstrap error bars and is evaluated at a fixed root
count by construction. The bin-occupancy artifact that has already corrupted two results in this
project — the markovianity finite-size trend, and roughly half of the exploratory
$\varepsilon_{\rm Born}$ trend of 2026-09-21 — cannot arise. This also discharges the
estimator-robustness requirement of `SPEC.md` §6.5 on its own terms.

### 2.4 Mandatory fail-closed branch

$S$ is singular exactly when the roots collapse onto a great circle or a point. That is the
degenerate case `RESEARCH_STATE.md` §3 warns satisfies moment relations **vacuously**, and it is
reachable in the approved families (central-X great-circle confinement, nilpotent collapsed laws).
Gate on $\operatorname{cond}(S)$ and **refuse** rather than report. Report coverage alongside every
$B_1$ regardless.

### 2.5 Acceptance tests for the estimator (closed-form answers)

Build $\rho_0=\cos^{2p}(\theta'/2)\,T(\Omega)$ on a quadrature grid, with $T$ a non-trivial
inversion-even envelope (include a quadrupole and a $\cos2\phi$ azimuthal term, so the test does not
pass merely because $T$ is isotropic). The estimator must reproduce:

| $p$ | 0.6 | 0.8 | **1.0 (Born)** | 1.3 | 2.0 | 3.0 |
|---|---|---|---|---|---|---|
| $B_1$ | 0.7457 | 0.8929 | **1.0000000000** | 1.1060 | 1.2123 | 1.2375 |

with axis error below $10^{-3}$ degrees at every $p$ and $\ell\ge3$ odd power below $10^{-30}$ at
$p=1$. The axis must be recovered far from Born as well as at it — the preferred-basis measurement
must not presuppose the hypothesis it tests.

---

## 3. Model, conventions and required disclosure

Every reported number must state all of the following, without being asked.

- **Builder:** `SinglePixelHamiltonianQuSpin` with `use_symmetry=False`. The QuSpin twin is
  required for anything intended to connect to production.
- **Hamiltonian and sign convention.** The builder carries an overall minus sign:
  $H=-J_{zz}\sum ZZ-J_{xx}\sum XX-J_{yy}\sum YY-g_xX_0X_1-g_yY_0Y_1-g_zZ_0Z_1-\sum_i(h_xX_i+h_yY_i+h_zZ_i)-(h_{0x}X_0+h_{0y}Y_0+h_{0z}Z_0)$,
  so code parameters are the **negatives** of the `SPEC.md` §9 coefficients.
- **Region center `screen_00`,** endpoint chain, `central_coupling="first"`:
  $J_{xx}=1.32$, $J_{yy}=2.53$, $J_{zz}=1.10$; $h_x=-1.34$, $h_y=0$, $h_z=1.00$;
  $h_{0x}=-1.35$, $h_{0y}=-1.69$, $h_{0z}=2.01$; $g_x=0.10$, $g_y=0.05$, $g_z=0.06$.
  Held at zero: `Jpm`, `Jcpm`, `Jzx`, `J2`, `Jpm2`.
- **Coupling scaling:** per edge; the endpoint chain has total coupling $g$, with no $N$-scaling.
- **Times:** the frozen window, six log-spaced $t\in[100,1000]$, pooled across times.
  **No time average** is taken; if one ever is, it must be labelled as the `SPEC.md` §7.2
  fallback and never conflated with instantaneous convergence.
- **Reference axis:** $\hat h_0=(-0.4572,-0.5723,0.6807)$, $|h_0|=2.9527$, which is
  $47.10°$ from $z$ and $|h_0|/\max|g|=29.5$.

---

## 4. Work packages

### WP1 — `core/outcome_measures.py`

Both `SPEC.md` §3 outcome pencils via `forward_pole_root_spectrum`, kernel-dimension weights,
separate normalization; then $(\hat n, B_1, \text{odd-}\ell\text{ power})$ and the `SPEC.md` §6
quartet $E_2, E_\infty, E_{\rm harm}, E_{\rm marg}$ through the existing
[gleason_diagnostics.py](core/gleason_diagnostics.py), which no Born script currently calls.
Tested against §2.5.

**Cost constraint on weights.** Exact kernel dimensions cost one SVD per distinct root, $O(n^4)$,
which is impossible at $n=4096$. Use $k_j=1$ with a duplicate-detection guard for the campaign and
run the full `characterize_pencil_roots` only at $N\le6$ to certify genericity. Record that this is
what was done.

**Free cross-check.** Where $h_{0y}=0$ the fixed-input and outcome pencils are conjugate
([fixed-input-outcome-equivalence.md](wiki/concepts/fixed-input-outcome-equivalence.md)), so the two
routes must agree to machine precision. At `screen_00` itself $h_{0y}=-1.69$, so the genuine
outcome pencils are **required** — the conjugation shortcut is not valid there.

### WP2 — Size trend

$N=8,10,12$ at the region center, bootstrap CIs, fixed root budget across sizes. $N=12$ means an
`eigh` of dimension 8192 and twelve non-Hermitian eigensolves of dimension 4096: **probe the cost
at a single time before launching the sweep.** Apple Accelerate's `zheevd` is broken at dimension
4096 for complex Hermitian matrices; use `scipy.linalg.eigh(driver="evr")`.

$N=14$ is out of reach locally and goes to Zeus via the `zeus-hpc` skill **only if** the local three
points are inconclusive.

Existing exploratory values, for continuity (histogram dipole $|d|$, not $B_1$):
$1.3361, 1.2224, 1.1760$ at $N=6,8,10$, budget-controlled $N=10$ mean $1.1613$; angle to $\hat h_0$
$9.01°, 5.49°, 2.85°$.

### WP3 — Region, not point

Eight generic perturbation directions from **two** independent seeds at 20% relative radius, at
$N=8$ and $N=10$; then 35% and 50% for the degradation profile. Report level, spread and worst case
of $B_1$ and $\hat n\cdot\hat h_0$ over each cloud, and **rank on the conservative statistic**. A
center scoring well with a tight cloud beats a better point that collapses. Spreads from fewer than
eight directions are not reportable — that trap was hit three times in the 2026-09-20 campaign.

### WP4 — Weak coupling (`SPEC.md` §8)

Sweep $\varepsilon=\max|g|/\min|\text{nonzero non-}g|\in\{0.025,0.05,0.1\}$, taking $N$ to its
largest value **first**, and report the $\varepsilon$-trend of $B_1$. This is the only dial that can
overturn the pre-registered prediction: if the $0.72$ weak ceiling is set by the perturbative
constraint rather than by the family, $B_1$ should fall toward 1 as $\varepsilon$ rises.
$\varepsilon=0.1$ is the approved ceiling and must not be exceeded.

### WP5 — Mechanism and its control

Rotate $\hat h_0$ over ~8 directions at fixed $|h_0|$ and fixed everything else, at $N=8$ and
$N=10$; report $\hat n\cdot\hat h_0$ and $B_1$ per direction. Exploratory values at $N=8$:
the axis tracked the field to $5.49°$, $10.67°$ and $16.76°$ in three directions, while
$\hat h_0\parallel x$ gave $|d|=0.079$ — the asymmetry collapses entirely there, which is a
**free `SPEC.md` §15.2 mechanism-breaking control**. Establish whether that null is a symmetry of
the model or an accident of that cell.

---

## 5. Falsifiers, frozen before any run

The hypothesis is **falsified** by any one of:

1. $B_1$ plateauing away from 1, or its budget-controlled increments decelerating geometrically to
   a limit that excludes 1;
2. normalized $\ell\ge3$ odd power not vanishing with $N$;
3. $\hat n$ separating from $\hat h_0$ as $N$ grows;
4. any of the above holding at the center but not across the 20% cloud.

No threshold, bin count, budget or acceptance gate may be adjusted after results are seen
(`CLAUDE.md` §10 Forbidden). Extrapolations must be reported under at least two reasonable ansätze:
on the existing $|d|$ data, geometric-in-$N$ gives a limit of $1.09$ while least-squares linear in
$1/N$ gives $0.896$ — they straddle 1, which is why three points decide nothing and why WP2 exists.

---

## 6. Out of scope

Do not run further $S_{\rm Born}$ maximization; do not chase a higher score; do not add Hamiltonian
families beyond the approved ones; do not promote any ledger gate; do not activate any verifier
(`SPEC.md` §0.1 reserves activation to the user); do not overwrite prior curated campaign data.

---

## 7. Deliverables

A standardized result packet under `reports/`, an append-only ledger entry, a wiki campaign page,
and a compact `RESEARCH_STATE.md` frontier update. Figures follow the established ring-catalog
diagnostic style — reuse `_plot_angular` and `_plot_ratio` rather than designing new charts —
in Helvetica Neue, with bin coverage reported next to every score. State the negative result as
plainly as a positive one.
