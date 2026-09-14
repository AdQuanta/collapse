# goal.md — Analytic \(P(\theta)\) and \(R(\theta)\) across the perturbative ring/chain ladder

## Objective

For the repository's implemented **ring** and **endpoint-chain** qubit–detector Hamiltonian families, derive analytical expressions for the projective-root angular measures

$$
P_N(\theta,t),\qquad
P_\infty(\theta,t),\qquad
\overline P_N(\theta),\qquad
\overline P_\infty(\theta),
$$

and the corresponding canonical quantities

$$
R_N(\theta,t),\qquad
R_\infty(\theta,t),\qquad
\overline R_N(\theta),\qquad
\overline R_\infty(\theta),
$$

for **every case in the two authoritative master ledgers**:

- **Ring geometry:** [`wiki/campaigns/analytic_distribution_ring_master_ledger.md`](wiki/campaigns/analytic_distribution_ring_master_ledger.md)
- **Endpoint chain geometry:** [`wiki/campaigns/analytic_distribution_chain_master_ledger.md`](wiki/campaigns/analytic_distribution_chain_master_ledger.md)

### Strict Ordering Invariant
Derivations must proceed **strictly in order** (Case 0, Case 1, Case 2, etc.).
**Do not move to the next case before the current one is completely solved and verified.**
Proceed systematically across regimes; do not attack the general Hamiltonian first, and do not bypass intermediate cases.

The qubit–detector coupling is assumed throughout to be **perturbative** relative to the intrinsic detector scales. Exploit this assumption systematically.

The desired results should be:

* exact in \(N\), \(t\), detector fields, and detector interactions whenever tractable;
* exact in \(g\) when an exact reduction exists;
* otherwise a controlled perturbative expansion in \(g\), carried to the lowest order that fully determines the nontrivial projective-root distribution and \(R(\theta)\);
* supplemented by higher orders whenever the leading order is degenerate, symmetric, trivial, or insufficient to distinguish competing angular profiles.

Do not replace an analytical derivation by numerical fitting.

---

# 1. Production Hamiltonians

Use exactly the repository's implemented Hamiltonians and conventions.

## Ring

$$
\begin{aligned}
H_{\rm ring}^{(N)}
={}&
\mathbf h_0\cdot\boldsymbol\sigma_0
+\sum_{i=1}^{N}\mathbf h\cdot\boldsymbol\sigma_i\\
&+
\sum_{i=1}^{N}
\sum_{\alpha=x,y,z}
J_{1\alpha}\sigma_i^\alpha\sigma_{i+1}^\alpha\\
&+
\sum_{i=1}^{N}
\sum_{\alpha=x,y,z}
J_{2\alpha}\sigma_i^\alpha\sigma_{i+2}^\alpha\\
&+
g_{x,N}X_0\sum_iX_i+
g_{y,N}Y_0\sum_iY_i+
g_{z,N}Z_0\sum_iZ_i ,
\end{aligned}
$$

with periodic detector indices and the production \(N\)-scalings used by the repository.

Unless repository evidence says otherwise, use

$$
g_{x,N}=\frac{g_x}{\sqrt N},
\qquad
g_{y,N}=\frac{g_y}{\sqrt N},
\qquad
g_{z,N}=\frac{g_z}{N}.
$$

## Endpoint chain

$$
\begin{aligned}
H_{\rm chain}^{(N)}
={}&
\mathbf h_0\cdot\boldsymbol\sigma_0
+\sum_{i=1}^{N}\mathbf h\cdot\boldsymbol\sigma_i\\
&+
\sum_{i=1}^{N-1}
\sum_{\alpha=x,y,z}
J_{1\alpha}\sigma_i^\alpha\sigma_{i+1}^\alpha\\
&+
\sum_{i=1}^{N-2}
\sum_{\alpha=x,y,z}
J_{2\alpha}\sigma_i^\alpha\sigma_{i+2}^\alpha\\
&+
g_xX_0X_1+
g_yY_0Y_1+
g_zZ_0Z_1 .
\end{aligned}
$$

Before beginning new derivations, locate and record the canonical repository definitions for:

* tensor ordering;
* production \(N\)-scaling;
* block decomposition of \(U(t)\);
* projective roots;
* zero and infinite roots;
* \(\theta\);
* algebraic multiplicity and degeneracy;
* probability normalization;
* \(P\);
* reflection \(\theta\mapsto\pi-\theta\);
* canonical \(R\);
* singular/indeterminate pencils.

Do not silently redefine any production observable.

---

# 2. Canonical observables

Write

$$
U_N(t)=e^{-iH_Nt}
=
\begin{pmatrix}
A_N(t)&B_N(t)\\
C_N(t)&D_N(t)
\end{pmatrix}
$$

in the repository's central-qubit basis.

The projective roots are the homogeneous generalized eigenvalues of

$$
\beta C_N(t)v=\alpha A_N(t)v.
$$

For every regular root \((\alpha_j,\beta_j)\),

$$
\theta_j^{(N)}(t)
=
2\,\operatorname{atan2}
\!\left(
|\alpha_j|,
|\beta_j|
\right).
$$

The finite-\(N\) probability measure is

$$
P_N(d\theta,t)
=
\frac{1}{2^N}
\sum_{j=1}^{2^N}
\delta_{\theta_j^{(N)}(t)}(d\theta),
$$

counting algebraic multiplicity.

Retain atoms explicitly. Never assume a smooth density unless proved.

Define the fixed-time thermodynamic limit by weak convergence,

$$
P_\infty(d\theta,t)
=
\mathrm{w\!-\!lim}_{N\to\infty}
P_N(d\theta,t).
$$

At fixed finite \(N\), define

$$
\overline P_N
=
\mathrm{w\!-\!lim}_{T\to\infty}
\frac1T\int_0^T P_N(\cdot,t)\,dt.
$$

The project's primary asymptotic time-averaged object is thermodynamic-first:

$$
\boxed{
\overline P_\infty
=
\mathrm{w\!-\!lim}_{T\to\infty}
\frac1T
\int_0^T
P_\infty(\cdot,t)\,dt
}
$$

with

$$
P_\infty(\cdot,t)
=
\mathrm{w\!-\!lim}_{N\to\infty}
P_N(\cdot,t).
$$

Do not assume

$$
\overline P_\infty
=
\lim_{N\to\infty}\overline P_N
$$

unless independently proved.

For any probability measure \(\mu\), with reflection

$$
S(\theta)=\pi-\theta,
$$

define

$$
R_\mu(\theta)
=
\frac{d\mu}
{d(\mu+S_*\mu)}(\theta).
$$

Whenever a density exists,

$$
R(\theta)
=
\frac{P(\theta)}
{P(\theta)+P(\pi-\theta)}.
$$

Thus compute separately

$$
R_N,\qquad
R_\infty,\qquad
\overline R_N,\qquad
\overline R_\infty.
$$

Importantly,

$$
\overline R_N
\equiv
R_{\overline P_N},
\qquad
\overline R_\infty
\equiv
R_{\overline P_\infty},
$$

not a time average of instantaneous \(R\).

The Born target is

$$
R_{\rm Born}(\theta)
=
\cos^2\frac{\theta}{2}.
$$

---

# 3. Mandatory perturbative-coupling assumption

The qubit–detector coupling is always perturbative.

Schematically,

$$
g\ll \max(h,J),
$$

except for the deliberately minimal baseline cases where one of \(h,J\) is absent.

However, a symbolic inequality such as \(g\ll J\) is not by itself sufficient near degeneracies, closing gaps, critical points, or collectively enhanced matrix elements.

For every case, identify the **actual perturbative control parameter**.

For example, determine a quantity of the form

$$
\epsilon
\sim
\frac{
g_{\rm eff}
\left|
\langle m|V|n\rangle
\right|
}
{
|E_m-E_n|
},
$$

or its degenerate/resolvent analogue.

For the ring, explicitly account for:

* production \(N\)-scaling of \(g_{\alpha,N}\);
* collective matrix-element enhancement;
* possible \(N\)-dependence of gaps;
* whether perturbation theory is uniform in \(N\).

A regime is not considered analytically controlled merely because the bare coefficient satisfies \(g\ll J\).

When ordinary nondegenerate perturbation theory fails, use the appropriate exact or controlled method:

* degenerate perturbation theory;
* Schrieffer–Wolff transformation;
* resolvent/Feshbach reduction;
* interaction-picture/Dyson expansion;
* linked-cluster or cumulant expansion;
* Jordan–Wigner/Bogoliubov reduction;
* Bethe ansatz;
* transfer matrix;
* collective-spin decomposition;
* stationary phase;
* spectral measures;
* determinant/Pfaffian methods;
* another justified exact structure.

---

# 4. NN-first rule

Set

$$
J_{2x}=J_{2y}=J_{2z}=0
$$

throughout the initial NN phase (Cases 0–40, Families A–H).

Do **not** introduce NNN interactions until every NN case has been analytically classified and verified for both ring and chain.

The goal is first to understand exhaustively how:

* detector field hierarchy;
* NN interaction hierarchy;
* anisotropy;
* integrability;
* criticality;
* one-axis versus multi-axis qubit coupling

affect \(P\) and \(R\).

Only after the full NN phase (Cases 0–40) is complete and verified may the NNN phase (Cases 41–86, Families I–N) begin.

---

# 5. Master case ladder and ledgers

The complete, authoritative case specifications, scale hierarchies, and atomic subcase rows across all $\mathbf h_0$ regimes are maintained directly in the master ledgers, partitioned by Family into dedicated files to ensure token efficiency and prevent context saturation:

- **Ring geometry:** [`wiki/campaigns/analytic_distribution_ring_master_ledger.md`](wiki/campaigns/analytic_distribution_ring_master_ledger.md) (Family ledgers in [`wiki/campaigns/ledgers/ring/`](wiki/campaigns/ledgers/ring/))
- **Endpoint chain geometry:** [`wiki/campaigns/analytic_distribution_chain_master_ledger.md`](wiki/campaigns/analytic_distribution_chain_master_ledger.md) (Family ledgers in [`wiki/campaigns/ledgers/chain/`](wiki/campaigns/ledgers/chain/))

The program spans all 87 physical cases (Cases 0–86) and their detailed $h_0$ subcases, cataloged across 14 distinct families:

### Part I: Nearest-Neighbor (NN) Ladder (Cases 0–40)
- **Family A (Cases 0–8)**: Decoupled baseline and one-axis / QND cases ($g_z$ with field and interaction hierarchies).
- **Family B (Cases 9–14)**: Transverse-field Ising model (TFIM / Ising ladder with gapped, ordered, and critical regimes).
- **Family C (Cases 15–17)**: XX ladder ($J_x = J_y \equiv J_\perp$).
- **Family D (Cases 18–20)**: XY ladder (distinguishing isotropic $J_x = J_y$ and anisotropic $J_x \neq J_y$).
- **Family E (Cases 21–26)**: XXZ ladder (distinguishing easy-plane, Heisenberg vicinity, easy-axis, field-polarized, and critical regimes).
- **Family F (Cases 27–32)**: Anisotropic XYZ ladder with longitudinal qubit coupling ($g_z$).
- **Family G (Cases 33–36)**: Perturbative transverse qubit–detector coupling ($g_\perp$).
- **Family H (Cases 37–40)**: Multi-axis perturbative qubit coupling ($g_\perp, g_z$), culminating in Case 40 (full NN production family).

### Part II: Next-Nearest-Neighbor (NNN) & Full Production Ladder (Cases 41–86)
- **Family I (Cases 41–48)**: Single-axis NNN couplings ($J_{2z}$).
- **Family J (Cases 49–54)**: Frustrated Ising models with competing NN/NNN interactions.
- **Family K (Cases 55–60)**: NNN XX and XY models.
- **Family L (Cases 61–69)**: NNN XXZ models.
- **Family M (Cases 70–77)**: Anisotropic NNN XYZ models.
- **Family N (Cases 78–86)**: Full production Hamiltonian with arbitrary NN and NNN XYZ couplings and multi-axis qubit coupling ($g_x, g_y, g_z$).

### Sequential Derivation & Case-Level Batching Rule
Derivations must proceed strictly in order from Case 0 to Case 86.
Never move to Case $k+1$ before Case $k$ (including all its $\mathbf h_0$ subcases) has been completely solved and verified for both geometries.
**Case-Level Batching**: Because the intrinsic detector Hamiltonian $H_{\rm detector}$ and eigenbasis are identical across all $\mathbf h_0$ subcases of physical Case $k$, solve, verify, and record all $\mathbf h_0$ subcases of Case $k$ in a single consolidated pass rather than 10 separate turn cycles.

---

# 6. Required analytical output for every case

For **each case and for both ring and chain**, produce the following.

## A. Specialized Hamiltonian

Write the Hamiltonian explicitly after setting all coefficients not listed in that case to zero.

State the hierarchy of scales.

State the actual perturbative small parameter.

---

## B. Detector structure

Identify:

* conserved quantities;
* exact symmetries;
* sectors;
* integrability;
* useful transforms;
* spectral gaps or gapless modes;
* degeneracies relevant to perturbation theory;
* whether the ring and chain require fundamentally different treatments.

---

## C. Projective-root representation

Derive an analytical representation of the pencil

$$
C_N(t)-\lambda A_N(t)
$$

or equivalent homogeneous form.

A formal diagonalization of an arbitrary \(2^{N+1}\)-dimensional Hamiltonian does **not** count.

Acceptable forms include:

* explicit roots;
* finite sector sums;
* recurrences;
* generating functions;
* determinants;
* Pfaffians;
* transfer matrices;
* Bethe-root expressions;
* mode products;
* spectral-measure integrals;
* controlled perturbative root expansions;
* another comparably informative exact structure.

When perturbative, derive

$$
\lambda_j
=
\lambda_j^{(0)}
+
g\,\lambda_j^{(1)}
+
g^2\lambda_j^{(2)}
+\cdots
$$

or the correct degenerate/generalized-eigenvalue analogue.

Then derive

$$
\theta_j^{(N)}(t).
$$

---

## D. Finite-\(N\), finite-time distribution

Derive

$$
\boxed{
P_N(\theta,t)
}
$$

as an exact probability measure or controlled perturbative measure.

State explicitly:

* support;
* atoms;
* continuous pieces, if any;
* degeneracies;
* zero roots;
* infinite roots;
* indeterminate roots;
* normalization.

---

## E. Thermodynamic fixed-time limit

Take

$$
\boxed{
P_\infty(\theta,t)
=
\lim_{N\to\infty}P_N(\theta,t)
}
$$

at fixed \(t\).

Justify the limit.

Do not interchange:

* \(N\to\infty\);
* perturbative expansion;
* sector sums;
* mode integrals;
* derivatives;
* root limits

without justification.

Determine whether perturbation theory is uniform in \(N\).

If it is not uniform, derive the correct rescaled asymptotic theory.

---

## F. Finite-\(N\) limiting time average

Derive

$$
\boxed{
\overline P_N(\theta)
=
\lim_{T\to\infty}
\frac1T
\int_0^T
P_N(\theta,t)\,dt
}
$$

in the measure sense.

Handle exactly:

* commensurate frequencies;
* degeneracies;
* zero-frequency sectors;
* persistent atoms;
* quasiperiodic finite-size motion.

---

## G. Thermodynamic-first limiting time average

First derive \(P_\infty(\theta,t)\), then compute

$$
\boxed{
\overline P_\infty(\theta)
=
\lim_{T\to\infty}
\frac1T
\int_0^T
P_\infty(\theta,t)\,dt.
}
$$

This order is mandatory.

Separately compare against

$$
\lim_{N\to\infty}\overline P_N
$$

whenever both exist.

Record whether the two orders commute.

---

## H. The four canonical \(R\) quantities

From the corresponding measures derive:

$$
\boxed{
R_N(\theta,t)
}
$$

$$
\boxed{
R_\infty(\theta,t)
}
$$

$$
\boxed{
\overline R_N(\theta)
}
$$

$$
\boxed{
\overline R_\infty(\theta).
}
$$

Do not compute \(\overline R\) by averaging instantaneous \(R\).

For each case compare analytically against

$$
R_{\rm Born}(\theta)
=
\cos^2\frac{\theta}{2}.
$$

Where possible derive a quantitative deviation such as

$$
\Delta R(\theta)
=
R(\theta)-\cos^2\frac{\theta}{2},
$$

and an analytically tractable norm or harmonic decomposition.

---

# 7. Perturbative hierarchy requirements

For every case, explicitly determine which of the following applies:

### Type I — exactly solvable despite perturbative \(g\)

An all-orders result in \(g\) exists.

Use it.

Then expand in \(g\) only to expose the physical perturbative mechanism.

### Type II — regular perturbative roots

A controlled expansion in \(g\) exists with nonzero denominators.

Derive the lowest nontrivial order and estimate the remainder.

### Type III — degenerate perturbation theory

The \(g=0\) pencil or Hamiltonian has degeneracies relevant to the roots.

Diagonalize the perturbation within the degenerate subspace before forming \(P\).

### Type IV — resonant/critical perturbation theory

The detector gap closes or denominators scale to zero with \(N\).

Do not use naive nondegenerate perturbation theory.

Derive the appropriate scaling limit.

### Type V — perturbation theory nonuniform in \(N\)

If

$$
\lim_{N\to\infty}
\left[
P_N^{(0)}+gP_N^{(1)}+\cdots
\right]
$$

does not represent the fixed-\(g\) thermodynamic limit, identify the correct combined scaling variable and resum/reorganize the expansion.

This classification is mandatory for every ledger row.

---

# 8. Reduction and consistency ladder

Every later case must recover earlier cases by parameter reduction whenever the earlier case is contained in it.

Examples:

$$
J_z\to0,
\qquad
h_x\to0,
\qquad
J_x-J_y\to0,
\qquad
g_x\to0,
$$

etc.

For every derived formula, explicitly test all applicable nested reductions.

A later formula that fails an earlier exact limit must be rejected.

---

# 9. Independent fixed verifier

Create and freeze a versioned independent verifier before judging derivations:

`verifier/analytic_p_theta/generic_verifier.py`

The generic verifier is a separate scientific component. It receives candidate symbolic/analytical expressions (as formula strings, callables, or structured formula data), constructs the production Hamiltonians numerically using `SinglePixelHamiltonianQuSpin` (`quspin_hamiltonians`), verifies physical assumptions, and numerically checks the candidate projective roots against exact numerical eigensolvers up to \(N = 11\).

Boundary rules:

* derivation code must not import verifier code;
* verifier code must not import candidate derivation code (it receives candidate expressions as input data/strings/callables);
* verifier never repairs a candidate;
* verifier definitions remain fixed during a comparison series;
* changes to the verifier require justification, regression tests, versioning, and restart of affected comparisons.

Use high-precision numerical arithmetic and exact structural checks. Do not use SymPy for matrix algebra.

## Verification of Physical Assumptions

The verifier must explicitly check that all physical assumptions and validity conditions of the derivation are correct:

* verify Hamiltonian construction, coupling geometry, tensor ordering, and boundary conditions (periodic for ring, open for chain) via `quspin_hamiltonians`;
* verify scale hierarchies and explicit perturbative validity domains (checking that the actual control parameter \(\epsilon\), collective enhancement, and gap scalings satisfy the perturbative assumptions);
* verify exact symmetries, conserved quantities, and sector decompositions;
* verify hermiticity (\(\|H - H^\dagger\| / \max(\|H\|, 1) \le 10^{-12}\)), unitary time evolution / column isometry (\(\|A^\dagger A + C^\dagger C - I\| \le 10^{-10}\)), and regularity of the pencil (no indeterminate roots);
* verify exact measure normalization (\(\sum_j w_j = 1\)) and reflection relations (\(\theta \mapsto \pi - \theta\));
* verify all zero-coefficient reductions to earlier solved cases in the ladder.

## Numerical Verification up to \(N = 11\) using `quspin_hamiltonians`

Perform independent, high-precision numerical matrix exponentials, eigensolvers, and projective-root evaluations across system sizes up to \(N = 11\) (e.g., \(N = 1, 2, \dots, 11\)) to verify finite-\(N\) analytical expressions:

* independently construct production ring and chain Hamiltonians using `SinglePixelHamiltonianQuSpin` (`quspin_hamiltonians`) up to \(N = 11\);
* compute high-precision numerical propagators and block subblocks \((A_N(t), C_N(t))\) via exact diagonalization;
* solve the generalized eigenvalue pencil \(\beta C_N(t) v = \alpha A_N(t) v\) via generalized eigensolvers;
* evaluate candidate symbolic expressions at matching physical parameters, times, and sizes;
* numerically verify closed-form root formulas and angular values \(\theta_j^{(N)}(t)\) via Hungarian matched-angle assignment against numerical spectra;
* verify perturbative expansions against high-precision numerical results within their stated validity domains;
* evaluate error bounds, residuals, and numerical convergence across \(N \le 11\).

> [!WARNING]
> **RESTRICTION ON NUMERICAL VERIFICATION UP TO \(N = 11\):**
> **Numerical verification up to \(N = 11\) must NOT be used to determine if \(R(\theta)\) is Born-like (\(R_{\rm Born}(\theta) = \cos^2(\theta/2)\)).**
> Up to \(N = 11\), the root distribution is dominated by finite-size artifacts, discrete delta atoms, and boundary effects. Whether the system generates a Born profile is strictly an **asymptotic question** for the thermodynamic limit (\(N \to \infty\)) and infinite-time Cesàro limit (\(T \to \infty\)), embodied by \(\overline R_\infty(\theta)\). Numerics up to \(N = 11\) serve exclusively to verify the mathematical and numerical correctness of finite-\(N\) identities and solvers, never to judge asymptotic Born behavior.

Numerics can falsify or support finite-\(N\) identities up to \(N = 11\); they do not prove an asymptotic theorem, and finite-\(N\) numerics must never be used to judge whether \(R(\theta)\) is Born-like.

---

# 10. Research loop

LOOP UNTIL THE CURRENT LEDGER CASE IS RESOLVED:

1. **Read state**
   Read `RESEARCH_STATE.md` and only the relevant `wiki/` material.

2. **Choose one unresolved statement**
   Pick the smallest high-information analytic obstruction.

3. **Classify perturbative regime**
   Determine Type I–V from Section 7.

4. **Hypothesize**
   State one falsifiable analytic structure and its strongest alternative.

5. **Predict**
   Write an exact identity, asymptotic signature, or perturbative coefficient that distinguishes them.

6. **Derive**
   Perform the smallest decisive analytic calculation.

7. **Freeze candidate**
   Save the formula before verification.

8. **Verify independently**
   Run the fixed generic verifier (`verifier/analytic_p_theta/generic_verifier.py`): pass the symbolic expression, construct the Hamiltonian using `quspin_hamiltonians`, verify that all physical assumptions are correct, and numerically verify the result up to \(N = 11\). Do NOT use numerics up to \(N = 11\) to judge whether \(R(\theta)\) is Born-like.

9. **Decide**
   Label the result:

   `KEEP`, `REJECT`, `INCONCLUSIVE`, or `PROMOTE`.

10. **Complete the eight observables**
    Do not promote a ledger row merely because \(P_N\) is known. Attempt all of

    $$
    P_N,\;
    P_\infty,\;
    \overline P_N,\;
    \overline P_\infty,\;
    R_N,\;
    R_\infty,\;
    \overline R_N,\;
    \overline R_\infty.
    $$

11. **Log**
    Record formula, regime, assumptions, perturbative order, failed identities, artifacts, and verifier version.

12. **Learn**
    Update durable wiki/state only when scientific knowledge changed.

13. **Advance strictly in order**
    Move to the next case/subcase **only** after the current one is completely solved and verified across all 8 observables, or a definitive mathematical obstruction is proved. Never skip cases or work on subsequent cases while earlier cases remain unsolved.

Use repository evidence labels exactly:

`PROVED`
`VERIFIED_NUMERICALLY`
`PRELIMINARY_NUMERIC`
`CONJECTURE`
`FALSIFIED`
`OPEN`

---

# 11. Required analytical ledgers

All progress across the ladder is recorded atomically in the family-partitioned master ledgers:

- **Ring geometry:** [`wiki/campaigns/analytic_distribution_ring_master_ledger.md`](wiki/campaigns/analytic_distribution_ring_master_ledger.md) (Master Index) and [`wiki/campaigns/ledgers/ring/`](wiki/campaigns/ledgers/ring/)
- **Endpoint chain geometry:** [`wiki/campaigns/analytic_distribution_chain_master_ledger.md`](wiki/campaigns/analytic_distribution_chain_master_ledger.md) (Master Index) and [`wiki/campaigns/ledgers/chain/`](wiki/campaigns/ledgers/chain/)

> [!TIP]
> **TOKEN-EFFICIENCY DIRECTIVE FOR LEDGER UPDATES:**
> Never load or rewrite full monolithic master ledgers into context. When working on Case $k$ in Family $F$, inspect and update **only** the dedicated family ledger:
> `wiki/campaigns/ledgers/<ring|chain>/family_<F>.md`
> or use `grep_search` to target the specific case line directly.

Maintain:

- `wiki/campaigns/analytic_distribution_ring_master_ledger.md` (Index status summary)
- `wiki/campaigns/analytic_distribution_chain_master_ledger.md` (Index status summary)
- `wiki/campaigns/ledgers/ring/family_<A..N>.md` (Atomic case rows)
- `wiki/campaigns/ledgers/chain/family_<A..N>.md` (Atomic case rows)
- `research_reports/analytic_p_theta/`
- `wiki/`
- `RESEARCH_STATE.md`
- and an append-only verifier log (`reports/analytic_p_theta/verifier_log.jsonl`).

The family ledgers contain one dedicated row per physical case and $\mathbf h_0$ subcase, with columns:

`family | case | parent case | nonzero coefficients | scale hierarchy | h0 regime | perturbative type | perturbative parameter | P_N | P_inf | Pbar_N | Pbar_inf | R_N | R_inf | Rbar_N | Rbar_inf | Born deviation | status`

Each cell must contain either:

* a formula reference;
* `PROVED`;
* `OPEN`;
* or a precise, mathematically proved obstruction.

Never write “done” if only numerical evidence exists.

---

# 12. Case-completion criterion

A single ledger case is complete only when, for **both ring and chain**, the following have been addressed:

1. specialized Hamiltonian;
2. actual perturbative control parameter;
3. symmetry/sector structure;
4. analytical projective-root representation;
5. \(P_N(\theta,t)\);
6. \(P_\infty(\theta,t)\);
7. \(\overline P_N(\theta)\);
8. \(\overline P_\infty(\theta)\);
9. \(R_N(\theta,t)\);
10. \(R_\infty(\theta,t)\);
11. \(\overline R_N(\theta)\);
12. \(\overline R_\infty(\theta)\);
13. support/atoms/singular cases;
14. reduction to all nested earlier cases;
15. independent verification that all physical assumptions are correct and numerical verifier checks via `generic_verifier.py` / `quspin_hamiltonians` up to \(N = 11\) (with the strict rule that numerics up to \(N = 11\) are never used to judge Born-like behavior);
16. explicit perturbative validity domain.

If one of these cannot presently be derived, mark that item `OPEN` and state the precise mathematical obstruction.

Do not hide an unresolved item behind a formal spectral decomposition.

### Strict Sequential Progression Rule
**Cases must be derived in order.**
Do not move to the next case before the current case is completely solved and verified across all criteria above. Never skip unresolved intermediate cases.

---

# 13. NN milestone

Write

`NN_LEDGER_COMPLETE`

only when Cases 0–40 (Families A–H) have been completely solved and verified for both ring and chain, or have a precisely established mathematical obstruction.

Do not begin NNN work (Cases 41–86) before this milestone is met.

---

# 14. NNN & full production phase

Following `NN_LEDGER_COMPLETE`, proceed strictly in order through Cases 41–86 (Families I–N) as defined in the master ledgers:

1. Single-axis NNN interactions (Family I, Cases 41–48);
2. Frustrated Ising interactions (Family J, Cases 49–54);
3. NNN XX/XY interactions (Family K, Cases 55–60);
4. NNN XXZ interactions (Family L, Cases 61–69);
5. Anisotropic NNN XYZ interactions (Family M, Cases 70–77);
6. Full production Hamiltonian with arbitrary NN/NNN XYZ and multi-axis coupling (Family N, Cases 78–86).

At each case repeat the same eight-observable program and verification standards. Do not jump directly to arbitrary \(\mathbf J_2\).

---

# 15. Final completion

Write

`GOAL_COMPLETE`

only when both ring and chain have an analytical characterization, exact or systematically controlled in perturbative \(g\), of

$$
P_N,\;
P_\infty,\;
\overline P_N,\;
\overline P_\infty,\;
R_N,\;
R_\infty,\;
\overline R_N,\;
\overline R_\infty
$$

through:

1. all NN ledger cases (Cases 0–40);
2. the full perturbative NN family (Case 40);
3. the subsequent NNN ladder (Cases 41–86);
4. the full implemented production family (Case 86) within its explicitly stated perturbative domain.

Do not mark complete because:

* selected \(N\) values agree numerically;
* selected times agree;
* one integrable subfamily is solved;
* only \(P_N\) is known;
* a formal spectral sum exists;
* perturbation theory was used outside its validity domain;
* the thermodynamic and time limits were interchanged without proof.

The scientific goal is not merely to accumulate formulas.

The goal is to determine, systematically and analytically, **which detector structures and scaling regimes generate which projective-root measures, and which of them can produce**

$$
\boxed{
\overline R_\infty(\theta)
\approx
\cos^2\frac{\theta}{2}
}
$$

**in a controlled perturbative qubit–detector regime.**
