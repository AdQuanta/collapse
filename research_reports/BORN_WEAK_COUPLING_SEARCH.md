# Positive search in perturbatively coupled XYZ rings and chains

12 September 2026. **Research checkpoint, not a resolution of the exact-Born
goal.** The search now prioritizes interacting ring and endpoint-chain families
with weak qubit–detector coupling. Two existing ring sequences provide useful
positive numerical leads. Neither is yet an established open Born phase.

## 1. Corrected Hamiltonians and conventions

The final user correction fixes the ring interaction to

\[
V_N=\frac{g_x}{\sqrt N}X_0\sum_{i=1}^N X_i
 +\frac{g_y}{\sqrt N}Y_0\sum_{i=1}^N Y_i
 +\frac{g_z}{N}Z_0\sum_{i=1}^N Z_i.
\tag{1}
\]

The chain interaction is
\(V_N=g_xX_0X_1+g_yY_0Y_1+g_zZ_0Z_1\), without size scaling.
For both families,

\[
H_0=\mathbf h_0\cdot\boldsymbol\sigma_0+
 \sum_i\mathbf h\cdot\boldsymbol\sigma_i+
 \sum_{r=1,2}\sum_{(i,i+r)}\sum_{\alpha=x,y,z}
 J_{r\alpha}\sigma_i^\alpha\sigma_{i+r}^\alpha,
\qquad H=H_0+V_N.
\tag{2}
\]

Ring indices are periodic; chain bonds stop at N-r. All signs in (1)–(2)
are positive coefficient conventions, spins are Pauli matrices, and hbar=1.
The dense reference uses rings N>=5 so the specified periodic bond sums
have no small-ring repeated-bond ambiguity. The central qubit is the first
tensor factor. Readout remains its fixed Z basis, including when h0 has
transverse components. All fields and couplings have energy units and t
has inverse-energy units. No detector state reweights the algebraic roots.

The reference implementation in `core/ring_chain_family.py` includes hy0,
hy and independent J2x,J2y,J2z for either topology. It is for reduced local
verification; it does not alter the production Hamiltonian generators or QZ.

## 2. Existing positive leads, with source integrity checked

The two source families have h0=0, hx=hy=0, gy=gz=0. Their coefficients
below use (1)–(2), translated from the repository's negative-sign convention.
For exchange, Jrx=Jry=-jpm_r/2; for Ising bonds, Jrz=-j_r.

| Parameter | Nearest-neighbor ring | Second-neighbor ring |
|---|---:|---:|
| hz | -0.04697737789563548 | -0.014352746605732818 |
| J1x=J1y | -0.006024592204038098 | -0.03048824849974197 |
| J1z | -0.027507890925136082 | -0.02418712918852393 |
| J2x=J2y | 0 | -0.13226687994843697 |
| J2z | 0 | -0.16899859316711222 |
| gx, before division by sqrt(N) | -0.0010470343101343842 | -0.001200423510786095 |

These parameters are identical across each saved N=14,15,16,17 sequence.
Every snapshot has t=10^6; this is a size comparison at one time.
The audit recomputes the unchanged 64-bin reflected ratio and all eight
raw cosine-moment residuals from all 2^N saved angles, without fitting,
pseudocounts, smoothing, or root selection.

| N | Nearest ratio RMSE | Nearest max moment residual | Second ratio RMSE | Second max moment residual |
|---:|---:|---:|---:|---:|
| 14 | 0.05108585 | 0.03308484 | 0.05775380 | 0.03102174 |
| 15 | 0.04651458 | 0.02539711 | 0.05072441 | 0.03880281 |
| 16 | 0.03376437 | 0.01892309 | 0.02458681 | 0.02338743 |
| 17 | 0.01592260 | 0.01405445 | 0.01757411 | 0.01516449 |

Every row has full reflected polar coverage in these 64 bins. At N=17,
the maximum bin-center errors are 0.04060667 and 0.03691154. The canonical
100-bin S_born values are 0.93163032 and 0.92955680. The saved azimuthal
second harmonic equals one: these X-conserving examples are on a great
circle. Full polar coverage does not mean uniform full-sphere coverage.

The decreasing ratio error motivates retaining these **interacting detector
Hamiltonians** as starting points. It does not justify extrapolation to an
exact limit. Existing central-field scans also show sensitivity:

| h0z/hz, N=17 | Nearest ratio RMSE | Second ratio RMSE |
|---:|---:|---:|
| 0 | 0.01592260 | 0.01757411 |
| 0.0001 | 0.04490367 | 0.08784918 |
| 0.001 | 0.07199483 | 0.04048429 |
| 0.01 | 0.15654396 | 0.09337715 |

Thus a positive construction must establish stability with additional
independent coupling directions and central fields. Restricting a search
to the best X-only slice would not establish the requested finite-width phase.
The nonmonotone second-family response also precludes estimating a stability
radius from these few points. These observations guide the next construction;
they are not another family no-go theorem.

Source roots are under
`work/zeus_top20_last5_largerN_20260810_001532/source_02/rank_001/`
and `source_03/rank_001/`. Their existing completion-manifest SHA256 values
were checked for arrays, metadata, metrics, and validation files at all four
sizes. Saved validation certifies finite counts and related diagnostics,
not a fresh homogeneous-QZ backward-error audit. Recomputed metrics reproduce
saved RMSE to 1e-12. Source and defining-code hashes are in the new provenance.

## 3. A finite-time weak-coupling reduction retaining resonances

**Exact definition.** In the interaction picture,

\[
V_I(s)=e^{iH_0s}Ve^{-iH_0s},\qquad
K_1(t)=\int_0^t V_I(s)\,ds.
\tag{3}
\]

For eigenvectors of H0 with energies Ea,

\[
(K_1)_{ab}=V_{ab}F_t(E_a-E_b),\quad
F_t(\Delta)=t e^{i\Delta t/2}
\operatorname{sinc}\!\left(\frac{\Delta t}{2\pi}\right),
\tag{4}
\]

where sinc(x)=sin(pi x)/(pi x). In particular F_t(0)=t. This formula is
entire in the energy difference and does not divide across a vanishing gap.
`core/weak_coupling_picture.py` implements (3)–(4), including complex phases,
and the first Magnus approximation

\[
U^{(1)}(t)=e^{-iH_0t}e^{-iK_1(t)}.
\tag{5}
\]

H0 includes the entire qubit field, so this construction does not assume
that h0 itself is small. Equation (5) is unitary and exact if the
interaction-picture operators commute at all times. Otherwise higher
Magnus terms are neglected. Near resonances are retained in (4); their
presence does not by itself control those omitted terms at late times.

**Proved finite-time error bound.** Let s=|t| ||V|| in operator norm.
Dyson expansion through first order, with the remaining exact propagator
left inside its double integral, gives remainder norm at most s²/2.
The exponential in (5) has the same first-order term and remainder at most
||K1||²/2 <= s²/2. Unitarity therefore gives

\[
\|U-U^{(1)}\|\le\min(2,t^2\|V\|^2).
\tag{6}
\]

This establishes second-order accuracy when V is scaled to epsilon V at
fixed N,t. It gives no error tending to zero at t~epsilon^-2.

There is also a useful size-uniform trace-norm estimate. Write
tau(M)=Tr(M)/2^(N+1) and ||M||_(p,tau)=tau(|M|^p)^(1/p). In the same two
remainders, Schatten Holder bounds each product V_I(s1)V_I(s2) in
normalized 2-norm by ||V||_(4,tau)^2. Minkowski gives
||K1||_(4,tau)<=|t| ||V||_(4,tau). Hence

\[
\|U-U^{(1)}\|_{2,\tau}\le t^2\|V\|_{4,\tau}^2.
\tag{7}
\]

For the corrected ring, independent Pauli trace identities give

\[
\tau(V_N^2)=g_x^2+g_y^2+g_z^2/N,
\quad
\|V_N\|_{4,\tau}\le(3-2/N)^{1/4}
(|g_x|+|g_y|+|g_z|/\sqrt N).
\tag{8}
\]

To verify the second inequality, each sum of N commuting Pauli operators
has fourth normalized moment 3N²-2N. Apply the triangle inequality to the
three central-Pauli terms with their respective divisors. No detector
eigenvector randomness or mixing assumption enters (7)–(8).
For the endpoint chain, tau(V²)=gx²+gy²+gz² and
||V||_(4,tau)<=|gx|+|gy|+|gz|.

Equation (7) is consequently uniform in N at fixed small |t| |g| for these
families, even though the ring operator-norm bound
||V_N||<=sqrt(N)(|gx|+|gy|)+|gz| grows. This is useful for constructing
effective propagators. **It does not imply convergence of projective roots.**
The normalized determinant/small-singular-value control required by
[the root-potential reduction](BORN_NONNORMAL_LIMIT.md) remains necessary
for that additional inference. The gz term must not be dropped from a
root calculation merely because its normalized second moment vanishes.

## 4. Positive construction to pursue

Keep the interacting detectors in section 2 and admit independent gx, gy,
gz and h0x,h0y,h0z, as well as the independent XYZ bonds in (2). Develop
the coupling-accessible resonant dynamics while retaining the full matrix
elements Vab. The relevant object is the resulting pencil (C,A), or its
normalized circle log determinant, rather than a scalar transition rate.
The endpoint chain is a second topology for this construction; previously
inspected chain examples attached at both ends with gx=gy do not test this
requested generic endpoint family.

A concrete next analytical step is to resum the resonant subspaces and
their second-order shifts before examining long times. The construction
must control near-degenerate clusters rather than invoke nondegenerate
perturbation theory with small denominators. Equations (3)–(8) supply a
benchmark for that effective dynamics at fixed time. The outstanding
positive proof must then establish a stable reciprocal balance of the
full root measure, including logarithmic tails, throughout a parameter
neighborhood. A Markov equation for qubit probabilities alone would not
establish that root law.

Phase removal requires an explicit equivalence. In (4) the prefactor is
separable: with D=exp(iH0 t/2), K1=D Kreal D†, where Kreal denotes the
kernel with the real sinc filter (V itself may be complex). Thus removing
this particular prefactor preserves the kernel eigenvalues. It also
conjugates (5) by D. Since H0=HQ+HD, D factors into central and detector
unitaries. If HQ is Z-diagonal, the central factor only changes the root
phase and the detector factor is a common similarity; polar roots are
preserved. With a general HQ direction, this central rotation changes the
fixed readout and must be retained or transformed explicitly. For kernels
between distinct conditional detector Hamiltonians, independent left and
right phases need not form a similarity at all. The unqualified phase
argument in `reports/weak_coupling_family_derivations_2026-06-20.md` therefore
needs this qualification; it is valid in the common-detector, Z-field case.
The historical report is preserved.

## 5. Verification and reproducibility

Six reduced tests cover the native sign/normalization mapping for a ring
and chain, independent tensor assembly with all Y fields and second XYZ
bonds, 64-node time quadrature at an exact degeneracy, three coupling
refinements with second-order propagator error, and an exactly commuting
resonant long-time limit. The focused suite passes. These tests certify
the reference and approximation order, not a Born phase.

Reproduce the saved-data audit with Python 3.11:

```bash
python -m pytest -q tests/test_ring_chain_weak_coupling.py
python scripts/audit_born_weak_coupling.py --output reports/born_weak_coupling_fresh
```

The output path must be new. Config:
`configs/born_weak_coupling_2026-09-12.json`.
Verified derived outputs are in `reports/born_weak_coupling_2026-09-12_final/`:
`evidence.json`, `provenance.json`, `ring_profiles.{png,pdf}` and
`ring_sensitivity.{png,pdf}`. No production calculation was submitted.

**Still open:** the exact non-tautological Born iff condition, its microscopic
realization, a finite-width phase, the N-first late-time root limit and its
stability. The present result is a corrected family definition, a controlled
weak-coupling reference and an audited positive starting point.
