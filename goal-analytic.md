# goal_analytic_distribution.md — Analytic \(P(\theta)\) and \(R(\theta)\) across the perturbative ring/chain ladder

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

for **every case in the coefficient/scaling ledger below**.

Proceed gradually. Do not attack the fully general Hamiltonian first.

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

throughout the entire ledger below.

Do **not** introduce NNN interactions until every NN case below has been analytically classified for both ring and chain.

The goal is first to understand exhaustively how:

* detector field hierarchy;
* NN interaction hierarchy;
* anisotropy;
* integrability;
* criticality;
* one-axis versus multi-axis qubit coupling

affect \(P\) and \(R\).

Only after the full NN ledger is complete may a separate NNN ladder begin.

---

# 5. NN coefficient/scaling ledger

Take \(\mathbf h_0\) as general unless restricting it is mathematically necessary. If it must be restricted, derive the restricted case first and then determine exactly which additional \(\mathbf h_0\) components can be restored.

The coefficients listed in each row are the detector/coupling coefficients that are nonzero.

Use axis permutations when genuinely equivalent, but prove the equivalence rather than duplicating calculations.

## A. Baseline and one-axis/QND cases

| Case | Nonzero coefficients | Scaling regime              |             |          |
| ---- | -------------------- | --------------------------- | ----------- | -------- |
| 0    | none                 | decoupled detector baseline |             |          |
| 1    | \(g_z\)              | perturbative \(g_z\)        |             |          |
| 2    | \(h_z,g_z\)          | \(g_z\ll h_z\)              |             |          |
| 3    | \(h_z,g_z\)          | (g_z\ll h_z\ll              | \mathbf h_0 | )        |
| 4    | \(h_z,g_z\)          | (g_z\ll                     | \mathbf h_0 | \ll h_z) |
| 5    | \(J_z,g_z\)          | \(g_z\ll J_z\)              |             |          |
| 6    | \(h_z,J_z,g_z\)      | \(g_z\ll h_z\ll J_z\)       |             |          |
| 7    | \(h_z,J_z,g_z\)      | \(g_z\ll J_z\ll h_z\)       |             |          |
| 8    | \(h_z,J_z,g_z\)      | \(g_z\ll h_z\sim J_z\)      |             |          |

These cases should be exhausted completely before moving to noncommuting detector terms.

---

## B. Ising / transverse-field Ising ladder

| Case | Nonzero coefficients | Scaling regime               |
| ---- | -------------------- | ---------------------------- |
| 9    | \(h_x,J_z,g_z\)      | \(g_z\ll h_x\ll J_z\)        |
| 10   | \(h_x,J_z,g_z\)      | \(g_z\ll J_z\ll h_x\)        |
| 11   | \(h_x,J_z,g_z\)      | \(g_z\ll h_x\sim J_z\)       |
| 12   | \(h_x,h_z,J_z,g_z\)  | \(g_z\ll h_z\ll h_x\ll J_z\) |
| 13   | \(h_x,h_z,J_z,g_z\)  | \(g_z\ll h_x\ll h_z\ll J_z\) |
| 14   | \(h_x,h_z,J_z,g_z\)  | \(g_z\ll J_z\ll h_x,h_z\)    |

Treat the critical/crossover regime separately from the gapped ordered and polarized regimes.

---

## C. XX ladder

Let

$$
J_x=J_y\equiv J_\perp.
$$

| Case | Nonzero coefficients | Scaling regime             |
| ---- | -------------------- | -------------------------- |
| 15   | \(h_z,J_x=J_y,g_z\)  | \(g_z\ll h_z\ll J_\perp\)  |
| 16   | \(h_z,J_x=J_y,g_z\)  | \(g_z\ll J_\perp\ll h_z\)  |
| 17   | \(h_z,J_x=J_y,g_z\)  | \(g_z\ll h_z\sim J_\perp\) |

---

## D. XY ladder

| Case | Nonzero coefficients | Scaling regime  |     |   |     |          |
| ---- | -------------------- | --------------- | --- | - | --- | -------- |
| 18   | \(h_z,J_x,J_y,g_z\)  | (g_z\ll h_z\ll  | J_x | , | J_y | )        |
| 19   | \(h_z,J_x,J_y,g_z\)  | (g_z\ll         | J_x | , | J_y | \ll h_z) |
| 20   | \(h_z,J_x,J_y,g_z\)  | (g_z\ll h_z\sim | J_x | , | J_y | )        |

Track separately the isotropic limit

$$
J_x=J_y
$$

and anisotropic limit

$$
J_x\neq J_y.
$$

---

## E. XXZ ladder

Let

$$
J_x=J_y\equiv J_\perp.
$$

| Case | Nonzero coefficients    | Scaling regime                    |
| ---- | ----------------------- | --------------------------------- |
| 21   | \(h_z,J_\perp,J_z,g_z\) | \(g_z\ll h_z\ll J_\perp,J_z\)     |
| 22   | \(h_z,J_\perp,J_z,g_z\) | \(g_z\ll h_z\ll J_\perp\ll J_z\)  |
| 23   | \(h_z,J_\perp,J_z,g_z\) | \(g_z\ll h_z\ll J_z\ll J_\perp\)  |
| 24   | \(h_z,J_\perp,J_z,g_z\) | \(g_z\ll h_z\ll J_z\sim J_\perp\) |
| 25   | \(h_z,J_\perp,J_z,g_z\) | \(g_z\ll J_\perp,J_z\ll h_z\)     |
| 26   | \(h_z,J_\perp,J_z,g_z\) | \(g_z\ll h_z\sim J_\perp,J_z\)    |

Explicitly distinguish:

$$
\Delta=\frac{J_z}{J_\perp},
$$

including:

* easy-plane;
* Heisenberg vicinity;
* easy-axis;
* field-polarized;
* critical/gapless regimes.

---

## F. XYZ ladder with longitudinal qubit coupling

| Case | Nonzero coefficients          | Scaling regime  |           |          |
| ---- | ----------------------------- | --------------- | --------- | -------- |
| 27   | \(h_z,J_x,J_y,J_z,g_z\)       | (g_z\ll h_z\ll  | J_\alpha  | )        |
| 28   | \(h_z,J_x,J_y,J_z,g_z\)       | (g_z\ll         | J_\alpha  | \ll h_z) |
| 29   | \(h_z,J_x,J_y,J_z,g_z\)       | (g_z\ll h_z\sim | J_\alpha  | )        |
| 30   | \(\mathbf h,J_x,J_y,J_z,g_z\) | (g_z\ll         | \mathbf h | \ll J)   |
| 31   | \(\mathbf h,J_x,J_y,J_z,g_z\) | (g_z\ll J\ll    | \mathbf h | )        |
| 32   | \(\mathbf h,J_x,J_y,J_z,g_z\) | (g_z\ll         | \mathbf h | \sim J)  |

Here \(J\) denotes the characteristic nonzero NN interaction scale.

---

## G. Perturbative transverse qubit–detector coupling

| Case | Nonzero coefficients        | Scaling regime                |
| ---- | --------------------------- | ----------------------------- |
| 33   | \(h_z,J_x=J_y,g_x=g_y\)     | \(g_\perp\ll h_z\ll J_\perp\) |
| 34   | \(h_z,J_x=J_y,g_x=g_y\)     | \(g_\perp\ll J_\perp\ll h_z\) |
| 35   | \(h_z,J_x=J_y,J_z,g_x=g_y\) | \(g_\perp\ll h_z\ll J\)       |
| 36   | \(h_z,J_x=J_y,J_z,g_x=g_y\) | \(g_\perp\ll J\ll h_z\)       |

For the endpoint chain, prioritize Jordan–Wigner/BdG representations whenever the qubit plus endpoint detector can be treated as an extended quadratic chain.

For the ring, prioritize collective-spin, momentum-sector, symmetry, and form-factor representations.

---

## H. Multi-axis perturbative qubit coupling

| Case | Nonzero coefficients                  | Scaling regime              |
| ---- | ------------------------------------- | --------------------------- |
| 37   | \(h_z,J_x=J_y,J_z,g_x=g_y,g_z\)       | \(g_\perp,g_z\ll h_z\ll J\) |
| 38   | \(h_z,J_x=J_y,J_z,g_x=g_y,g_z\)       | \(g_\perp,g_z\ll J\ll h_z\) |
| 39   | \(\mathbf h,J_x,J_y,J_z,g_x,g_y\)     | \(g_x,g_y\ll h,J\)          |
| 40   | \(\mathbf h,J_x,J_y,J_z,g_x,g_y,g_z\) | \(g_x,g_y,g_z\ll h,J\)      |

Case 40 is the **full NN production family in the perturbative qubit–detector regime**.

Do not begin NNN work until Case 40 has been reached for both ring and chain and all earlier cases have been entered in the analytical ledger.

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

`verifier/analytic_p_theta/`

The verifier is a separate scientific component.

Boundary rules:

* derivation code must not import verifier code;
* verifier code must not import candidate derivation code;
* verifier never repairs a candidate;
* verifier definitions remain fixed during a comparison series;
* changes to the verifier require justification, regression tests, versioning, and restart of affected comparisons.

Use exact arithmetic whenever possible.

## Required SymPy checks

For tractable small \(N\):

* construct ring and chain Hamiltonians independently;
* compute \(U_N(t)\);
* extract \(A_N,C_N\);
* compute generalized projective roots;
* verify analytic root formulas;
* verify perturbative coefficients in \(g\);
* compare Taylor expansions in \(t\);
* verify normalization;
* verify reflection relations;
* verify zero-coefficient reductions;
* verify special rational/algebraic parameter cases;
* verify determinant/Pfaffian/transfer-matrix identities where proposed;
* verify moments or characteristic functions if direct measure comparison is impractical.

Use high-precision independent numerical substitutions only as a secondary test.

Numerics can falsify or support.

They do not prove an analytic theorem.

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
   Run the fixed verifier.

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

13. **Advance**
    Move to the next scaling regime only after the current one is analytically classified.

Use repository evidence labels exactly:

`PROVED`
`VERIFIED_NUMERICALLY`
`PRELIMINARY_NUMERIC`
`CONJECTURE`
`FALSIFIED`
`OPEN`

---

# 11. Required analytical ledger

Maintain:

`research_reports/analytic_p_theta/`

`wiki/`

`RESEARCH_STATE.md`

and an append-only verifier log.

Maintain one compact master table with columns:

`family | case | nonzero coefficients | scale hierarchy | perturbative type | perturbative parameter | P_N | P_inf | Pbar_N | Pbar_inf | R_N | R_inf | Rbar_N | Rbar_inf | Born deviation | status`

Each cell should contain either:

* a formula reference;
* `PROVED`;
* `OPEN`;
* or a precise obstruction.

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
15. independent small-\(N\) verifier checks;
16. explicit perturbative validity domain.

If one of these cannot presently be derived, mark that item `OPEN` and state the precise mathematical obstruction.

Do not hide an unresolved item behind a formal spectral decomposition.

---

# 13. NN milestone

Write

`NN_LEDGER_COMPLETE`

only when Cases 0–40 have been processed for both ring and chain and every case has either:

* the requested analytical expressions; or
* a precisely established obstruction explaining why the current analytic machinery cannot produce them.

The full NN family must at minimum have a controlled perturbative-in-\(g\) representation.

Do not introduce \(J_2\) before this milestone.

---

# 14. NNN phase

Only after `NN_LEDGER_COMPLETE`, create a separate NNN ladder.

Start from the simplest extensions:

1. one \(J_{2\alpha}\);
2. NNN interactions that preserve quadratic/free-fermion structure;
3. NNN XX/XY;
4. NNN XXZ-like regimes;
5. anisotropic NNN XYZ;
6. full \(\mathbf J_2\).

At each NNN rung repeat the same eight-observable program.

Do not jump directly to arbitrary \(\mathbf J_2\).

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

1. all NN ledger cases;
2. the full perturbative NN family;
3. the subsequent NNN ladder;
4. the full implemented production family within its explicitly stated perturbative domain.

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
