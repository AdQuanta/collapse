# WP1: exact no-go classes, covariance lemma, master table

> Source: Agent work-package report, go/no-go derivation workflow (scratchpad `gonogo/wp/WP1/REPORT.md`), 2026-09-24. Derivations and bornkit numerics (N <= 10); not refereed unless stated. The report was interrupted by a usage limit in places; content preserved verbatim.
> Collected: 2026-09-24
> Published: 2026-09-24

# WP1 — Theorem 1: exact no-go classes and definitions

Status: COMPLETE (resumed run, narrowed scope; see section 0).
Conventions: SPEC positive convention (BRIEF 1.1), qubit first, U = exp(-iHT), blocks A,B,C,D = U00,U01,U10,U11.
Outcome-0 pencil in output basis n: M0^(n)(Omega) (BRIEF 2.1). Builder for all numerics: bornkit.build_H.

## 0. Summary of results
Status: COMPLETE for the narrowed scope (b), (c), (d), (h), (i); (e)-(g) restated with scope, citing WP4 for the chain classes.
- **P1 (covariance, PROVED).** A product symmetry V (x) W of H makes the root-measure family covariant, rho_0^(R_V n) = (R_V)_* rho_0^(n),
  at every N, T and in every limit; antiunitary chiral symmetries give improper covariance, equivalent (by antipodality) to a proper
  pi-rotation; time reversal only relates forward and fixed-input laws. A unique fixed point must be symmetric: continuous symmetry
  about a gives n* = +-a, a pi-rotation gives n* in {+-a} cup a-perp. **P1.4: every continuous qubit-side symmetry is a GCG charge, so
  the law at the forced axis is delta**: continuous symmetry and nondegenerate Born are incompatible.
- **P2-P3 (QND in every basis, PROVED).** For [H, a.sigma_0] = 0 the roots in basis n are exactly {R_a(chi_k) n}, chi_k the eigenphases
  of W_-^dag W_+. Coverage is possible only for n perp a; strong fails everywhere; Phi(n) = sign(a.n) a with a delta at a. Theorem C and
  R10 transfer verbatim to a in {x,y,z} and every n perp a (signed-permutation rotation of the whole model). No open region contains
  a QND point.
- **P4 (complete charge-graded list, PROVED).** GCG with ANY Hermitian Q_D occurs in the approved families iff h0 || a and QND_f, or
  CG_f (|g_b| = |g_c| != 0, h || f, J_bb = J_cc; chain also J_bb = -J_cc), or CG_iso (isotropic |g|, tilted a). New: the x and y
  versions, the staggered chain lines, and the necessity of every condition.
- **P5 (discrete symmetries; commuting classes).** Pi_a iff h0, h || a; plus single-coupling Pauli strings. Constraint only.
  Commuting classes are solvable in every basis; the late-time law is not weak-Born about any n with n_x != 0 or n = +-y (new).
- **P6-P7** cite WP4 (Ising chain: 4 atoms in every basis; matchgate: one radius in the z basis only).
- **P8 (1/N ring).** Operator-norm cap for T < 1/|g|_1 (PROVED); HS decoupling at every T (PROVED); N-first law = decoupled delta iff the
  Jensen gap G_N(T) -> 0, equivalently LT (PROVED-CONDITIONAL); unconditional in QND, CG, COM. Numerics: G_N falls with N when
  T|g|_2/sqrtN < 1 and roughly collapses on that variable; at T = 20 N <= 10 is pre-asymptotic (crossover N* ~ (T|g|_2)^2 ~ 80).
- **P9 master table** (section 9): every Tier 1-6 sub-pattern assigned to an exact class or to the generic interior. The chain
  Tiers 1-3 as posed are excluded outright (Ising chain); the ring tiers are excluded only on closed positive-codimension sets, so
  the generic interior (open, dense) is the whole residual, and it is excluded under SPEC 1/N only conditionally on LT.

## 1. Definitions (a)

Notation. For output axis n, V_n is any qubit unitary with V_n|0> = |+n>; outcome 0 in basis n means collapse to |+n>.
The outcome-0 root set is R_0^(n) = {Omega in S^2 : ker (<-n| (x) I) U (|Omega> (x) .) != 0}, with kernel weights k_j (SPEC)
or algebraic multiplicities m_j (log-potential identity, BRIEF 2.1). It is canonical: it does not depend on the choice of
V_n or on spinor phases. rho_b^(n)(N,T) is the normalized weighted root measure; rho_1^(n) = A_* rho_0^(n) with A the
antipodal map (antipodality, BRIEF 1.6). P_b^(n) denotes the polar marginal about n (pushforward under Omega -> angle(Omega,n)).

### D1 Nondegenerate weak Born profile (about n)
Let rho_0^(n)(T) := w-lim_{N->inf} rho_0^(n)(N,T) (limit along the full N-sequence, at fixed T) and
rho_0^(n)(inf) := w-lim_{T->inf} rho_0^(n)(T) (instantaneous; the Cesaro fallback replaces it by
lim (1/T) int_0^T rho_0^(n)(t) dt and must be labelled). The limiting law is a **weak Born profile about n** if
(W1) [coverage] supp(P_0 + P_1) = [0, pi], and
(W2) [ratio] dP_0 / d(P_0 + P_1) = cos^2(theta/2), (P_0+P_1)-almost everywhere (Radon-Nikodym form).
Justification. (W2) is SPEC section 5.2 (SPEC.md:273-307) written without assuming densities; it is equivalent to SPEC's
form whenever densities exist, and by antipodality to P_0 = (1 + cos theta) E with E reflection-even (BRIEF 2.2-2.3).
(W1) is the coverage clause BRIEF 2.1(vii) requires: without it delta_N, polar caps, finitely many atoms satisfying
tan^2(theta/2) = m(pi-theta)/m(theta) and the equatorial atom all pass (W2) vacuously.
Absolute continuity. (W1)+(W2) do not require it: P_0 = (1+cos theta)E with E a singular, reflection-even measure of full
support satisfies both. I propose a two-level convention: **no-go statements are proved against (W1)+(W2) only** (the
weakest reading, so the no-go is strongest); **any "go" claim must in addition show P_0 << d theta with a density positive
a.e.** (SPEC's own formulation uses densities rho_b^(theta)(theta), SPEC.md:283-290, and SPEC section 6.4's E_marg needs one).

### D2 Nondegenerate strong Born profile (about n)
(S1) supp(rho_0 + rho_1) = S^2 and (S2) d rho_0 / d(rho_0 + rho_1)(Omega) = cos^2(angle(Omega,n)/2), (rho_0+rho_1)-a.e.
Strong about n implies weak about n (integrate (S2) over the azimuth; (S1) implies (W1)). Strong implies the dipole fit
is exactly n with B1 = 1 [OWN-proof: with nu = rho_0 + rho_1 antipodally even, m = int u d rho_0 = (1/2) S_nu n and
S_rho0 = (1/2) S_nu, so n_raw = n]. The same absolute-continuity convention as D1 applies.

### D3 Open stable region at a fixed ring-scaling hypothesis
Fix: geometry G in {ring, chain}; for the ring a per-axis scaling hypothesis g_{a,N} = g_a N^{-kappa_a} (SPEC 1/N:
kappa = 1; pre-SPEC mixed: kappa = (1/2, 1/2, 1); chain: kappa = 0), stated explicitly; the time object tau in
{instantaneous (primary), Cesaro (labelled fallback)}; a criterion in {weak, strong}; and a parameter space P, which must be
named: either the full approved space P_full = R^12 (h0, h, J, g) or a tier subspace (the other coordinates held at 0, and
every such zero flagged if it creates a conservation law, section 9). Let P_eps = {p in P : |g|_inf <= eps * Delta(p)}
be the perturbative domain, with Delta(p) a stated non-g energy scale (the code gate eps = 0.1 with Delta = min nonzero
non-g coefficient, scripts/eval_chain_born.py:107-117, is a code convention, not SPEC section 8).
An **open stable region** is a nonempty set O subset P_eps, open in the relative topology of P, such that for every p in O:
(i) the N-first limit exists at every T and the tau-limit exists; (ii) there is an axis n*(p), unique up to sign (SPEC
section 12, SPEC.md:711-745), that is an attracting fixed point of Phi_p (D4); (iii) the tau-limit law in basis n*(p) is a
nondegenerate weak (resp. strong) Born profile (D1/D2); (iv) p -> n*(p) is continuous on O (SPEC section 13,
SPEC.md:751-770). The openness space matters: a result "open in a tier subspace" is not "open in P_full", and conversely
an exclusion proved only in P_full (e.g. via a free h_0x direction) need not apply inside a tier that fixes h_0x = 0.

### D4 Preferred axis as an attracting fixed point of Phi
For a probability measure mu on S^2 put m_mu = int u d mu, S_mu = int u u^T d mu, and n_fit(mu) = S_mu^{-1} m_mu / |S_mu^{-1} m_mu|
when S_mu is invertible and S_mu^{-1} m_mu != 0 (this is core/outcome_measures.py:33-65's estimator applied to the limit
law); extend by n_fit(delta_v) := v for a point mass (continuous extension along the resultant; flagged, since the estimator
itself refuses). Phi(n) := n_fit(rho_0^(n)) with rho_0^(n) the tau-limit law. By antipodality Phi(-n) = -Phi(n), so Phi
descends to RP^2. For orthogonal R (proper or improper), n_fit(R_* mu) = R n_fit(mu) (S -> R S R^T, m -> R m).
A **preferred axis** is n* with Phi(n*) = +n* (the sign is forced: Born about n gives n_fit = +n, D2), unique in RP^2,
and attracting: there is a neighbourhood V of n* on which Phi is defined and Phi^k(n) -> n* for n in V (equivalently,
where Phi is C^1, the tangent map D Phi(n*) has spectral radius < 1). Phi need not be continuous: in the QND class it is
sign(a.n) a, undefined on the great circle a-perp (section 3).

## 2. Covariance lemma and fixed-point constraints (b)  [P1]

Notation. For V in U(2), R_V in SO(3) is its adjoint rotation, V (r.sigma) V^dag = (R_V r).sigma. M_y = diag(1,-1,1),
A = -I. K is complex conjugation in the product computational basis. The standard spinor |Omega> = (cos th/2, e^{i ph} sin th/2)
satisfies V|Omega> = e^{i alpha}|R_V Omega> and K|Omega> = |M_y Omega>.

### P1.1 Covariance lemma (unitary product symmetry)
**Statement.** If [V (x) W, H] = 0 with V in U(2), W in U(d), then for every N, T and output axis n,
R_0^(R_V n)(T) = R_V R_0^(n)(T), with kernel dimensions and algebraic multiplicities preserved. Hence
rho_0^(R_V n) = (R_V)_* rho_0^(n) at every finite (N,T), with either weight convention, and for every weak limit built from them
(N-first at fixed T, then instantaneous T -> inf, or Cesaro).
**Status.** PROVED.
**Proof.** Let M0^(n)(Omega) be the d x d map D -> (<-n| (x) I) U (|Omega> (x) D). Since (V^dag (x) I) U (V (x) I) = (I (x) W) U (I (x) W^dag)
and <-R_V n| is proportional to <-n| V^dag, M0^(R_V n)(R_V Omega) = e^{i gamma(n,Omega)} W M0^(n)(Omega) W^dag with |e^{i gamma}| = 1.
So D is in the kernel at (n,Omega) iff W D is in the kernel at (R_V n, R_V Omega) (kernel weights), and
|det M0^(R_V n)(R_V Omega)| = |det M0^(n)(Omega)|, i.e. L1^(R_V n)(R_V .) = L1^(n)(.), which by the log-potential identity (BRIEF 2.1)
gives the algebraic-weight statement; a singular pencil stays singular. Pushforward by a fixed continuous map commutes with weak
limits and with time averages. QED.
**Numerical check** (`n1_core.py`, `n1_core.json` key B; N = 5, T = 6.1, single time, no pooling; builder bornkit.build_H; ring
scaling {x: 1/sqrtN, y: 1/sqrtN, z: 1/N}; two random axes n per case; matched chordal distance between R_0^(R n) and R R_0^(n)):
continuous, charge-graded ring `{h0z .9, hz .7, Jxx=Jyy=.8, Jzz 1, gx=gy=.3, gz .1}` (R_z(phi), phi = 2.67, 2.68): 2.4e-14, 1.4e-14;
continuous, staggered charge-graded chain `{h0z .9, hz .7, Jxx .8, Jyy -.8, Jzz 1, gx .3, gy -.3, gz .1}`: 8.6e-15, 3.4e-14;
discrete Pi_z ring (Tier-5 z-field slice `{h0z .9, hz .7, Jxx .5, Jyy 1.1, Jzz .9, gx .3, gy .12, gz .2}`, R_z(pi)): 7.0e-15, 4.6e-15;
discrete Pi_x chain (`{h0x .9, hx .7, same J, g}`, R_x(pi)): 5.1e-14, 4.4e-14; non-Pi Pauli string Z_0 prod Y_i
(`{h0z .9, hy .7, Jxx .5, Jyy 1.1, Jzz .9, gx .3}`, R_z(pi), `wp1_checks2.py` (3)): ring 1.6e-14, chain 2.2e-14.
Controls without the symmetry: generic ring with h0x = .4 added, R_z(pi): 1.93, 1.47; Tier-2 tilted ring `{h0x .5, h0z .8, hz .7,
Jzz .9, gx .3}`: R_z(pi) 1.7, R_{h0hat}(pi) 0.73. All other parameters are zero; the zeros are the symmetry being tested.

### P1.2 Antiunitary symmetries, time reversal, complex conjugation
**Statement.** (a) If Theta = (V (x) W)K satisfies Theta H Theta^{-1} = -H, then Theta U(T) Theta^{-1} = U(T) and
rho_0^(S n) = S_* rho_0^(n) with S = R_V M_y (improper). Because rho_0^(-n) = rho_1^(n) = A_* rho_0^(n) (antipodality, BRIEF 1.6),
this is equivalent to covariance under the proper rotation -S = R_V R_y(pi). Qubit parts K, XK, ZK give R_y(pi), R_z(pi), R_x(pi);
YK (spin time reversal) gives S = -I, i.e. nothing beyond antipodality.
(b) If Theta H Theta^{-1} = +H (a time-reversal symmetry), or a unitary satisfies (V (x) W) H (V (x) W)^dag = -H, the symmetry maps
U(T) to U(T)^dag. It does not constrain a single forward law; it relates the forward law to the fixed-input law (the outcome-0 law of
U^dag, BRIEF 1.8): rho_fi^(S n) = S_* rho_fwd^(n). For real H (h0y = hy = 0; note g_y Y0 Y_i and J_yy are real) this is
rho_fi^(M_y n) = (M_y)_* rho_fwd^(n), which is the repository's duality. So **for real H the fixed-input preferred axis is the
y-mirror of the forward one**; they coincide as lines only for n* in the xz-plane or along y.
(c) Parameter-space form (no symmetry assumed). With p~ := -conj(p) (flip every SPEC coefficient except h0y and hy),
U(p~, T) = conj U(p, T), so rho_fwd^(M_y n)[p~] = (M_y)_* rho_fwd^(n)[p] and Phi_{p~}(M_y n) = M_y Phi_p(n). The set of D3 points is
invariant under p -> p~ with n* -> M_y n*. For real H, p~ = -p: the global sign flip (code <-> SPEC convention) mirrors the preferred
axis in y. For complex H, -p gives U^dag, i.e. the fixed-input law (BRIEF 1.1).
**Status.** PROVED.
**Proof.** Theta U Theta^{-1} = exp(+i Theta H Theta^{-1} T) = U when Theta H Theta^{-1} = -H. Then U = (V (x) W) conj(U) (V (x) W)^dag.
Complex-conjugating the root equation of conj(U) in basis m gives R_0^(m)[conj U] = M_y R_0^(M_y m)[U], and P1.1's computation for
the unitary part gives R_0^(n)[(V (x) W) X (V (x) W)^dag] = R_V R_0^(R_V^{-1} n)[X]. Composing, R_0^(S m) = S R_0^(m). With
R_X = diag(1,-1,-1), R_Y = diag(-1,1,-1), R_Z = diag(-1,-1,1): -M_y = R_y(pi); -R_X M_y = diag(-1,-1,1) = R_z(pi);
-R_Y M_y = I (so S = -I); -R_Z M_y = diag(1,-1,-1) = R_x(pi). (b) and (c) are the same computation applied to U^dag. QED.
**Numerical check** (`n1_core.json` key C; complex H `{h0x .4, h0y -.5, h0z .9, hx .3, hy .6, hz .7, Jxx .5, Jyy 1.1, Jzz .9,
gx .3, gy .12, gz .2}`, T = 7.3, single time, ring {1/sqrtN,1/sqrtN,1/N} and chain): matched distance between
R_0^(M_y n)[p~] and M_y R_0^(n)[p] is 4.0e-14, 3.2e-14 (ring N=4,5), 4.5e-14, 6.3e-14 (chain N=4,5); the naive comparison with -H in
the same basis gives 0.91-1.96.
**Failure modes.** In the approved families an antiunitary Theta with Theta H Theta^{-1} = -H and a non-YK qubit part requires
every retained term to be odd, which forces bond or coupling zeros. With all three J_aa nonzero no site-local Theta exists: a local
antiunitary acts on each site's Pauli vector by an improper orthogonal S_i, and a bond flips only if S_i^T diag(J) S_{i+1} = -diag(J);
taking determinants, det diag(J) = -det diag(J), so some J_aa = 0.
Such points are exotic and add no constraint beyond P1.3 applied to the resulting pi-rotation.

### P1.3 Fixed-point constraint
**Statement.** Let G_p = {S in O(3) : rho_0^(S n) = S_* rho_0^(n) for all n} for the tau-limit law (a closed subgroup containing -I),
and G_p^+ = G_p cap SO(3). Wherever Phi is defined, Phi(S n) = S Phi(n) for S in G_p. Consequently every fixed point's G_p-orbit
consists of fixed points, and a fixed point n* that is unique in RP^2 satisfies S n* = +-n* for all S in G_p. In particular:
(i) SO(2)_a subset G_p^+ => n* = +-a; (ii) R_a(pi) in G_p^+ => n* in {+-a} cup a-perp, and Phi(a) in {+a, -a} whenever defined;
(iii) R_a(2 pi/k) in G_p^+ with k >= 3 => n* = +-a; (iv) {R_x(pi), R_y(pi), R_z(pi)} subset G_p^+ => n* in {+-x, +-y, +-z};
(v) if G_p^+ has no invariant line (e.g. SO(3), or the tetrahedral/octahedral groups) there is no unique fixed point, so D4 fails.
**Status.** PROVED.
**Proof.** n_fit(S_* mu) = S n_fit(mu) for S in O(3) (S_mu -> S S_mu S^T, m_mu -> S m_mu; D4's point-mass extension is also
equivariant). Hence Phi(S n) = n_fit(rho_0^(S n)) = n_fit(S_* rho_0^(n)) = S Phi(n). If Phi(n*) = n*, then Phi(S n*) = S n*.
Uniqueness in RP^2 gives S n* = +-n*, i.e. n* spans a line invariant under every element of G_p^+. The invariant lines of SO(2)_a and
of R_a(2pi/k), k >= 3, are the a-line only; those of R_a(pi) are the a-line and every line in a-perp; the common invariant lines of
D_2 are the coordinate axes. For (ii): an R_a(pi)-invariant measure has m parallel to a and S block-diagonal in (a, a-perp), so
S^{-1} m is parallel to a. QED.
**Intuition.** Symmetry cannot choose between the images of an axis, so a unique axis must be symmetric. Covariance is an equivariance
statement: it constrains where n* can be, never whether Born holds there.
**Failure modes.** (ii) leaves the whole plane a-perp open. Nothing here gives attractivity. Detector-only symmetries (translation,
reflection, prod X_i at h_z = 0, ...) have R_V = I and give no qubit-side constraint; they only block-decompose the pencil.

### P1.4 Theorem (continuous qubit-side symmetry => degenerate)
**Statement.** Suppose H has a one-parameter group of product symmetries V(phi) (x) W(phi) whose qubit part is nontrivial. Then its
generator is c a.sigma_0 + Q_D with c != 0 and Q_D Hermitian, and at every N and every regular time T: rho_0^(a)(N,T) = delta_{+a}
(algebraic weights; the kernel-weight measure is also delta_{+a}). Every fixed point of Phi is either +-a, where the law is delta_{+a},
or lies on a whole circle of fixed points. Hence no such parameter point satisfies D3 (weak or strong, instantaneous or Cesaro, any
scaling, ring or chain), and no open stable region contains one.
**Status.** PROVED.
**Proof.** The Lie algebra of the group {V (x) W} is {X (x) I + I (x) Y}; write X = c a.sigma + const. If c = 0 the qubit part is a phase.
So [H, c a.sigma_0 + Q_D] = 0 with c != 0, which is WP4's generalized charge grading (GCG, `wp/WP4/REPORT.md` P4.12, "all d outcome-0
roots sit at +a", PROVED). All roots at +a gives delta_{+a} in either weight convention at regular times; singular times are isolated
(e.g. t = pi/(4g) in the charge-graded classes, BRIEF 3 "CG") and do not affect the instantaneous limit along regular times or the
Cesaro average. SO(2)_a is in G_p^+ by P1.1, so P1.3(i) and the orbit remark give the dichotomy. At n* = +-a, D4's point-mass extension
gives Phi(a) = a, and the law is a point mass, which fails (W1) and (S1). QED.
**Intuition.** A conserved quantity with a qubit component along a makes the a-basis measurement "already done": the detector
records a without back-action on it, so every collapsible input collapses to +a.

## 3. QND-cone lemma in every output basis; generalized Theorem C (c)  [P2, P3]

### P2 Orbit form of the QND-cone lemma, coverage, and Phi
**Statement.** Let [H, a.sigma_0] = 0, so U = P_+^a (x) W_+ + P_-^a (x) W_- with W_+- unitary. Let e^{i chi_k}, k = 1..d, be the
eigenvalues of the unitary W_-^dag W_+ (independent of the output basis). Then for every output axis n the outcome-0 roots are exactly
R_0^(n) = {R_a(chi_k) n}, with multiplicities those of the eigenvalues (the pencil is diagonalizable in the eigenbasis of W_-^dag W_+,
so kernel weights equal algebraic weights). Consequences, with beta = angle(a, n):
(a) every root lies on the cone a.Omega = a.n (BRIEF 2.4) and cos angle(Omega_k, n) = cos^2 beta + sin^2 beta cos chi_k;
(b) the polar support about n lies in [0, 2 min(beta, pi - beta)], so **weak coverage (W1) fails in every basis with 0 < beta < pi/2**
and at beta = 0 (delta_{+a}); only bases n perp a (a great circle) can have polar support [0, pi], and there the polar law about n is
the law of |wrap chi|, the same for every n in a-perp;
(c) the support is a circle for every N, T, so the strong criterion (S1) fails in every basis;
(d) whenever the eigenphase law nu_chi has at least three support points, Phi(n) = sign(a.n) a with B1 = 1/|cos beta| for a.n != 0
(cone lemma), and Phi is undefined on a-perp (S_aa = 0). If nu_chi is a point mass, Phi(n) = R_a(chi) n (D4 extension). In both cases
the unique fixed line is a, it is superattracting in the first case, and the law there is delta_{+a}.
**Status.** PROVED.
**Proof.** Let D_k be an orthonormal eigenbasis of W_-^dag W_+, so W_+ D_k = e^{i chi_k} W_- D_k. Then
M0^(n)(Omega) D_k = f_k(Omega) W_- D_k with the scalar f_k(Omega) = e^{i chi_k} <-n|+a><+a|Omega> + <-n|-a><-a|Omega>, so
M0^(n)(Omega) = W_- diag(f_k(Omega)) in that basis and det M0 = det W_- prod_k f_k(Omega). Each f_k is a nonzero linear functional of
the spinor (its two coefficients cannot both vanish), so it has exactly one projective zero; the pencil is diagonal, hence kernel and
algebraic multiplicities coincide. In a frame with a = z, n = (beta, phi_n), Omega = (theta, phi):
<-n|+a>/<-n|-a> = -e^{i phi_n} tan(beta/2) and <-a|Omega>/<+a|Omega> = e^{i phi} tan(theta/2), so f_k = 0 iff
e^{i phi} tan(theta/2) = e^{i(chi_k + phi_n)} tan(beta/2), i.e. theta = beta and phi = phi_n + chi_k: Omega = R_a(chi_k) n (the
homogeneous form covers the poles). (a) is the spherical law of cosines, (b) follows from cos chi >= -1, (c) is immediate, and (d) is
the cone lemma (`bornkit.dipole`; BRIEF 1.4) plus P1.3. QED.
**Numerical check** (`n1_core.py` key A; random detector with all fields and XYZ bonds nonzero, coupling g_a = 0.3 and qubit field
h0a = 0.7 only, a in {x,y,z}, ring {1/sqrtN,1/sqrtN,1/N} and chain, N = 4, 6, T = 20 single time, two random n each, 24 cases):
cone residual max|a.Omega - a.n| <= 2.4e-14; eigenphase formula residual <= 1.5e-14; fit axis angle to a = 0.0 deg with
sign(fit.a) = sign(a.n) in 24/24; B1 equals 1/|cos beta| to <= 4e-13 relative (e.g. beta = 91.8 deg: B1 = 32.5964 vs 32.5964).
The zeros (h0 perp a, g perp a) are the hypothesis [H, a.sigma_0] = 0.

### P3 Generalized Theorem C and R10 for [H, a.sigma_0] = 0, a in {x, y, z}
**Statement.** In the approved families, [H, a.sigma_0] = 0 holds exactly on the pattern QND_a: h0 parallel to a and g_b = g_c = 0
for the two axes b, c != a (detector arbitrary; ring or chain; any scaling). Fix all parameters except h0a, and fix n perp a.
(i) (Theorem C transferred.) If E is a measurable set of h0a values on which the first Born residual d_0^(n) (BRIEF 2.2) has an
N-first limit at each T > 0 and that limit tends to 0 as T -> inf, then |E| = 0; over an interval of width w,
|mean d_0 + 1| <= 5/(2 w |T|), uniformly in N and detector.
(ii) (R10 transferred.) Within report 10's scope (all detector fields, NN/NNN XYZ, fixed coupling), for Lebesgue-a.e. h0a the
N-first Cesaro polar law about n is d theta/pi, i.e. R = 1/2.
(iii) (Rigid shift.) Changing h0a by dh rotates every root set rigidly about a by 2 dh T (sign fixed by the convention), in every
output basis, at every N.
Consequently, together with P2 and P1.4, no open stable region (D3, in P_full or in any tier subspace that contains an h0a-interval
through the point) contains a QND_a point, even if the fixed-point requirement D4 is dropped and bases n perp a are allowed.
**Status.** PROVED (i, iii); PROVED within report 10's stated scope (ii).
**Proof.** For coordinate a and coordinate n perp a, pick the signed permutation R in SO(3) with R a = x, R n = z. Apply the same
rotation to the qubit and to every detector site. This maps H to an approved-family Hamiltonian with h0 -> R h0, h -> R h, the
exchange tensor diag(J) -> R diag(J) R^T and the coupling tensor diag(g) -> R diag(g) R^T (both still diagonal: J_aa and g_a are
permuted, field components permuted with signs), and maps the output basis n to z. Roots transform by R (P1.1's computation with
the rotated H), and polar angles about n become polar angles about z. The image is exactly the X0 class I (x) K - X_q (x) (V + h I)
of Theorem C (`research_reports/BORN_ASYMPTOTIC_OBSTRUCTIONS.md:52-64`, "any sequence of detector Hermitian pairs") with
h = -h0a (sign immaterial) and V = the rotated coupling, and it is in the scope of report 10
(`research_reports/analytic_p_theta/10_almost_every_central_field.md:1-17`). For non-coordinate n perp a, P2(b) says the polar law about
n does not depend on n in a-perp. (iii): h0a (a.sigma_0) commutes with H and enters W_+- as e^{-+ i h0a T}, so
W_-^dag W_+ -> e^{-2 i h0a T} W_-^dag W_+, i.e. chi_k -> chi_k - 2 h0a T; apply P2. For the corollary: an open set containing a QND_a
point p contains an h0a-interval of QND_a points (varying h0a preserves the pattern); by P2(d) every such point has n* = a with
law delta (violating D3), and without D4 the only covering bases are n perp a, where (i) makes the Born set of h0a null. QED.
**Numerical check** (`wp1_checks2.py` (1); random detector with all fields and bonds, h0a = 0.55, g_a = 0.25 only, N = 5, T = 7.3,
dh = 0.013, one random n perp a; ring {1/sqrtN,1/sqrtN,1/N} and chain): great-circle residual max|a.Omega| <= 7.3e-15; matched
distance between the shifted root set and R_a(2 dh T) applied to the unshifted one <= 1.2e-13 for all six (a, geometry) cases,
against 0.83-2.0 for the opposite rotation sense and 0.51-1.7 with no rotation.
**Which tier patterns realize each a.** QND_x (h0y = h0z = 0, g_y = g_z = 0): Tier 1 at h0z = 0; Tier 2 at h0z = 0; Tier 3 at
h0z = 0 only if also g_y = 0 (then it is Tier 2); the central-X slices of Tiers 4-5; the chain analogues (Tier 6). QND_y
(h0x = h0z = 0, g_x = g_z = 0): not reachable in Tiers 1-4 as posed (they carry g_x); a Tier-5 slice. QND_z (h0x = h0y = 0,
g_x = g_y = 0, "pointer QND"): a Tier-5 slice (g_z only) and SPEC's first tier; not reachable in GOAL Tiers 1-4 (they carry g_x).
**Intuition.** A conserved qubit component a turns the detector into a phase clock: the only thing the detector can do is rotate the
collapsible input about a by its eigenphases. That is a one-dimensional family, so strong Born is impossible; weak coverage needs the
great circle, and there a field shift slides the whole law rigidly, which is incompatible with a Born law holding on a field interval.

## 4. Charge-graded theorem, all patterns and all output bases (d)  [P4]

### P4 Complete list of generalized-charge-graded (GCG) points in the approved families
**Statement.** Approved family: uniform fields h0, h; uniform NN XYZ exchange diag(J); diagonal coupling diag(g) (ring: collective,
any N-scaling absorbed into g; chain: to site 1 only). A point admits [H, c a.sigma_0 + Q_D] = 0 with c != 0, a unit vector a and
SOME Hermitian Q_D on the detector (not necessarily local) if and only if g != 0 is excluded as trivial and h0 is parallel to a (or
h0 = 0), and one of the following holds (f a coordinate axis, b and c the other two):
- **QND_f**: a = f and g_b = g_c = 0 (detector arbitrary), Q_D = 0.
- **CG_f**: a = f, g_c = +-g_b != 0, g_f arbitrary, h parallel to f, and J_bb = J_cc (ring or chain; this includes the Ising case
  J_bb = J_cc = 0); in the **chain only**, also J_bb = -J_cc != 0. The charge is sigma_0^f + sum_i s_i sigma_i^f with
  s_1 = sgn(g_b g_c) (co-rotating vs counter-rotating), and s_{i+1} = s_i sgn(J_bb J_cc) along the chain (all four sign combinations
  of (g_c/g_b, J_cc/J_bb) occur in the chain; in the ring s_i = s_1 and J_bb = -J_cc is excluded).
- **CG_iso** (non-coordinate a): |g_x| = |g_y| = |g_z| != 0, and the detector commutes with the collective rotation about
  k = (s_x a_x, s_y a_y, s_z a_z) (signs fixed by the g-sign pattern). In the ring this forces isotropic exchange
  J_xx = J_yy = J_zz and h parallel to k. (Chain: the same necessary condition on g; the detector condition is not worked out
  further, since the set is exotic.)
Consequence (with P1.4). Every GCG point has rho_0^(a)(N,T) = delta_{+a} at every N and regular T, continuous covariance about a,
and no D3 point: excluded in every output basis, weak and strong, instantaneous and Cesaro, any scaling, ring and chain.
In particular this includes, besides the repository's CG theorem, the analogous patterns about x (h0 || x, h || x, J_yy = J_zz,
g_z = +-g_y) and about y (h0 || y, h || y, J_xx = J_zz, g_x = +-g_z), the staggered chain patterns, and exact energy grading
(Q_D = H_D, WP4 P4.12): every exactly energy-graded approved point is one of the points listed.
**Status.** PROVED (ring: all three cases; chain: QND_f and CG_f complete, CG_iso necessary condition only).
**Proof.** Write H_qD = sum_b sigma_0^b (x) B_b (ring B_b = g_b S_b with S_b = sum_i sigma_i^b; chain B_b = g_b sigma_1^b). Expanding
[H, c a.sigma_0 + Q_D] in the qubit Pauli basis, the identity component is [H_D, Q_D] = 0 and the sigma^e component is
2ic (h0 x a)_e I + 2ic sum_b (e_b x a)_e B_b + [B_e, Q_D] = 0.
(1) Taking the normalized trace of the sigma^e component kills the last two terms, so h0 x a = 0.
(2) Form of Q_D. Ring: decompose operator space into isotypic components of the collective SU(2) adjoint action; S = (S_x,S_y,S_z)
spans one spin-1 copy, and its HS-orthogonal complement is invariant. Write Q_D = k.S + Q_perp. The equation requires
[Q_D, B_e] in span{S}; since [Q_perp, S_e] lies in the complement, [Q_perp, S_e] = 0 for every e with g_e != 0. If two g_e are
nonzero, Q_perp commutes with collective su(2): Q_D = k.S + Q', Q' in the commutant. (With a single nonzero g_e the sigma^{e'}
components, e' != e, give epsilon_{e'ef} a_f = 0, i.e. a = e_e and QND_e.) Chain: write Q_D = sum_mu sigma_1^mu (x) R_mu; for
[Q_D, sigma_1^e] to lie in span{sigma_1^nu (x) I}, every R_mu with epsilon_{mu e nu} != 0 must be scalar; with two nonzero g_e,
Q_D = k.sigma_1 + I (x) R_0.
(3) Coupling equations. Comparing coefficients of S_b (or sigma_1^b) gives, for each ordered pair (e,b) of distinct axes with f the
third, g_e k_f = c g_b a_f. For each f: if a_f != 0 then either g_e = g_b = 0 or g_e^2 = g_b^2 != 0 with k_f = c (g_b/g_e) a_f
(a mixed case g_e != 0 = g_b gives k_f = 0 and then c g_e a_f = 0, a contradiction); if a_f = 0 then k_f = 0 unless g_e = g_b = 0.
For a = e_f this gives QND_f or |g_b| = |g_c| != 0 with k = +-c e_f. For a with two or more nonzero components it forces
|g_x| = |g_y| = |g_z| != 0 (or g = 0).
(4) Detector condition, ring. [H_D, k.S + Q'] = 0. Split H_D into collective rank 1 (h.S) and rank 2 (anisotropic exchange, one copy,
since it is the image of one bond tensor) and into weights m under ad(k.S). For m != 0 the weight-m part H^(m) must satisfy
[Q', H^(m)] = -mu_m H^(m) with mu_m != 0 and mu_{-m} = -mu_m. On one copy of an irrep ad(Q') acts as a scalar (Schur), and a
Hermitian H_D has both H^(m) and H^(-m) nonzero if either is, which gives -mu_m = -mu_{-m}, a contradiction. So H_D commutes with k.S:
h || k, and diag(J) is invariant under rotations about k, which for a coordinate k means J_bb = J_cc and for a non-coordinate k means
J isotropic. Chain, a = z, k = +-c e_z: the site-1 Pauli components of [H_D, +-c Z_1 + R_0] = 0 give h_x = h_y = 0 (traces) and
J_xx [X_2, R_0] = -+2ic J_yy Y_2, J_yy [Y_2, R_0] = +-2ic J_xx X_2, J_zz [Z_2, R_0] = 0. Either J_xx = J_yy = 0 (Ising, R_0 = 0), or
steps (2)-(3) applied to site 2 give |J_xx| = |J_yy| and R_0 = +-c (J_yy/J_xx) Z_2 + R_0'; induct along the chain. Sufficiency in every
case is a direct check that the stated charge commutes term by term. QED.
**Numerical check** (`wp1_checks2.py` (2); ptp over a 400-point Fibonacci grid of L1(Omega) - log((1 - a.Omega)/2) in output
basis a, which is 0 iff all roots sit at +a; single time T = 6.1; ring scaling 1/sqrtN on all axes; N = 4, 5; all unlisted
parameters zero):
| pattern (SPEC, nonzero parameters) | predicted | ptp N=4 | ptp N=5 |
|---|---|---|---|
| CG_x ring: h0x .9, hx .7, Jxx .6, Jyy = Jzz = .8, gy = gz = .3, gx .15 | delta | 7.2e-10 | 9.6e-9 |
| CG_y chain: h0y .9, hy .7, Jxx = Jzz = .8, Jyy .5, gz = -gx = -.3, gy .1 | delta | 2.2e-13 | 4.8e-11 |
| CG_z staggered chain: h0z .9, hz .7, Jxx .8 = -Jyy, Jzz 1, gy = -gx = -.3, gz .1 | delta | 1.6e-13 | 1.9e-10 |
| CG_z staggered chain with gy = +gx (s_1 = +1, s_2 = -1) | delta | 5.4e-11 | 1.7e-11 |
| CG_z Ising chain: h0z .9, hz .7, Jzz 1, gx = gy = .3, gz .1 | delta | 3.6e-15 | 6.7e-15 |
| CG_iso ring, a = (.6,0,.8): h0 = .9a, h = .7a, J = .9 isotropic, g = .3 isotropic | delta | 1.0e-11 | 3.8e-11 |
| ring Jxx .8 = -Jyy, gy = +gx | not delta | 1.6 | 3.5 |
| ring Jxx .8 = -Jyy, gy = -gx | not delta | 1.8 | 2.4 |
| ring CG_z plus hx = 0.05 | not delta | 1.2 | 0.74 |
| ring tilted a, g = (.3,.3,.2) (anisotropic) | not delta | 1.6 | 1.4 |
The 1e-10 to 1e-8 values reflect the conditioning of the defective pencil (BRIEF 7 caveat), not a spread. The fourth row was
labelled a "control" in the script by mistake; the classification predicts delta (both sign choices are graded in the chain) and the
numerics agree. Covariance for CG_z (ring) and staggered CG_z (chain): P1.1 check, 2.4e-14 and 3.4e-14.
**Where these patterns sit in the tiers.** CG_z: Tier 3 at h0x = 0 with |g_y| = |g_x| (Ising detector, h || z), ring and chain; Tier 4
with h0 || z and g_y = +-g_x (any g_z); the chain additionally at J_xx = -J_yy (a Tier-5 chain point). CG_x, CG_y, CG_iso: Tier-5
slices only (Tiers 1-4 carry h_z and g_x, which forbid them).
**Intuition.** The coupling must transport exactly one quantum of a conserved detector charge per qubit flip. That is possible only
when the two transverse couplings have equal modulus (a pure raising or lowering operator) and the detector conserves the matching
charge, which forces the field along the axis and U(1)-invariant exchange.

## 5. Pi-parity and the commuting-detector classes B, D, E, H (e)  [P5]

### P5.1 Discrete qubit-side symmetries in the approved families; Pi-parity
**Statement.** (a) Pi_a := sigma_0^a prod_i sigma_i^a commutes with H iff h0 || a and h || a (all J and g free; ring and chain).
Then R_a(pi) is in G_p, so n* in {+-a} cup a-perp, Phi(a) in {+-a}, and in basis a the root set is invariant under
lambda -> -lambda (R_a(pi)). WP3 P0 adds finite-size north atoms of weight D(N)/2^N (0.375, 0.188, 0.102, 0.055 at N = 4..10) in
translation-invariant Pi_z rings; they vanish like 2^{-N/2} and do not survive the N-first limit.
(b) For product symmetries V (x) w^{(x)N} (ring) or V (x) (x)_i w_i (chain) with single-site w, commutation holds iff
R_V h0 = h0, R_{w_i} h = h, R_{w_i} diag(J) R_{w_{i+1}}^T = diag(J) on every bond, and R_V diag(g) R_{w_i}^T = diag(g) on every coupled
site. With R_V = R_b(pi) (b a coordinate axis): if two or more g are nonzero, R_w = R_V, i.e. Pi_b; if only g_c != 0 with c != b,
also w = pi-rotation about the third axis e (pattern h0 || b, h || e, coupling g_c only; e.g. Z_0 prod Y_i with h0 || z, h || y,
g_x only), and, when J_bb = J_ee, about any axis of the (b,e)-plane containing h. Tilted-axis discrete symmetries occur only on the
U(1)-degenerate sets |g_b| = |g_c|, J_bb = J_cc, where a global rotation about the third axis maps them to the coordinate case.
Symmetries of order k >= 3 with R_V != I occur only inside the continuous (GCG) classes.
**Status.** PROVED (a); PROVED for single-site detector parts (b); detector parts that are not products of single-site unitaries are
covered only when continuous (P4).
**Proof.** (a) Conjugation by Pi_a flips every one-site Pauli other than sigma^a and leaves every two-site term sigma^b sigma^b
invariant. (b) Conjugation by a product of single-site unitaries maps sigma_j^b to sum_c (R_{w_j})_{cb} sigma_j^c; one-site and two-site
Pauli strings are linearly independent, which gives the four conditions. For R_V = R_b(pi), column-wise R_{w} e_c = (R_V)_cc e_c for
every c with g_c != 0; two such columns fix a rotation, so R_w = R_V. With one nonzero g_c the only constraint is R_w e_c = -e_c
(c != b), i.e. a pi-rotation about an axis m perp e_c, and R_w must fix h and diag(J), which gives the listed cases. QED.
**Numerical check.** P1.1 (Pi_z ring, Pi_x chain, Z_0 prod Y_i ring and chain: <= 5.1e-14; controls O(1)); n1_core B.
**Consequence for the tiers.** Pi_z holds on all of Tier 1, on the h0 || z slices of Tiers 3-4 (fields along z), and on the chain
analogues. There it leaves two candidate families for n*: the z-line and the equatorial plane. Tier 2 with h0x h0z != 0 has no
qubit-side product symmetry at all (checked: R_z(pi) and R_{h0hat}(pi) fail at O(1)).

### P5.2 Commuting-detector classes: restatement with scope, and extension to other output bases
**Restatement** (repository, pre-reset, PROVED in the stated scope; `research_reports/BORN_ASYMPTOTIC_OBSTRUCTIONS.md:31-82`,
`research_reports/BORN_DETUNING_INTERVAL.md:9-52`; digest [PT] section 3.1, 3.5). All are Z-basis statements.
- B: H = I (x) K - X_q (x) (V + hI), [K,V] = 0, any scaling: the late-time law (if the limits exist) is L delta_0 + (1-L) d theta/pi,
  Born only at L = 1 (delta). This class is inside QND_x, so P2-P3 already exclude it in every basis.
- D: V = (g/sqrtN) sum X_i, h = 0: folded wrapped Gaussian at each T, uniform (R = 1/2) as T -> inf; under 1/N the law is delta_0.
- E: B plus a detuning -b Z_q, b != 0, light-tailed spectral law of V: the ordinary late-time limit exists and is not Born.
- H, H1: no open detuning interval (H); pointwise failure for V = h + g S_N, S_N = N^{-1/2} sum X_i, any K commuting with S_N (H1;
  the c != 0 central ZX term is outside the approved family, c = 0 is Theorem E's family).
In approved terms the commuting condition [H_D, S_x] = 0 means h || x and J_yy = J_zz (ring), or the zero detector
(h_z = J_zz = 0 in Tiers 1-2); for the chain [H_D, X_1] = 0 forces the X-Ising chain with h || x (report 01; a rotated P4.6 case).
**Extension** [OWN-proof]. Let H = K + h0.sigma_0 + g X_0 V with [K, V] = 0 (ring, any h0 including h0y). In the joint eigenbasis,
H = direct sum over eigenvalues u of V of [K_u + h_eff(u).sigma_0], h_eff(u) = h0 + g u e_x, so U(T) is a direct sum of products and the
outcome-0 roots in ANY basis n are the kinematic points chi_n(u,T) = R(h_eff(u), -2|h_eff(u)|T) n, with multiplicity dim(block).
Hence rho_0^(n)(N,T) is the push-forward of the spectral law nu_N of V under u -> chi_n(u,T) (exact, every N, T, basis). If
nu_N -> nu (for V = S_N at 1/sqrtN, nu is the standard Gaussian), the N-first law at each T is the push-forward of nu. If nu is
absolutely continuous, the ordinary late-time limit exists and equals the nu-mixture of uniform measures on the circles through n
about h_eff(u)-hat (Riemann-Lebesgue in the frequency |h_eff(u)|). In every basis with n_x != 0, some u* has h_eff(u*) perp n; if
nu has positive density at u* and d beta/du != 0 there (beta(u) = angle(n, h_eff(u))), the south-cap mass about n is
S(eps) = [nu(u*)/|beta'(u*)|] eps (1 + o(1)), whereas a weak Born law without a north atom has S(eps) = o(eps)
(P0 = (1 + cos theta) E, E reflection-even: S(eps) <= 2 eps E([0, r]) -> 0 as eps -> 0, eps = sin^2(r/2)); the mixture has no atom
at n because nu has none. So the late-time law is not weak-Born about any n with n_x != 0. For n = +-y every circle is a great
circle through n and the polar law is exactly d theta/pi (R = 1/2). The bases with n_x = 0, n != +-y are covered only for n = +-z
(Theorem E/H1); the rest of that meridian is OPEN.
**Status.** PROVED (block formula in every basis; late-time mixture for a.c. nu; non-Born for n_x != 0 and for n = +-y);
OPEN for n in the (y,z)-meridian other than +-y, +-z.
**Consequence.** With Pi_z (zero detector, h0 || z: Tier 1 at h_z = J_zz = 0), the candidate axes are z (Theorem E) and z-perp
(covered here), so that slice is excluded at 1/sqrtN in the fixed-point basis. With a tilted h0 in the xz-plane (Tier 2 zero-detector
slice), the weak-coupling fixed point is near h0hat, which has n_x != 0, so it is covered; an exact exclusion would need the
fixed point off the (y,z)-meridian, which is not proved. Under 1/N, nu_N -> delta_0 and the law is delta at the kinematic point in
every basis, unconditionally.

## 6. Ising chain with h_D parallel to z (f)  [P6]
Cited, not re-derived: WP4 P4.6 (`wp/WP4/REPORT.md`, "Ising chain with h_D || z", PROVED). For the chain with h_x = h_y = 0 and
J_xx = J_yy = 0, arbitrary h0 and g, [H, Z_i] = 0 for i >= 2, and for every N >= 2 and T the outcome-0 law is four atoms of
weight 1/4, exactly N-independent (the N-first limit is the N = 2 law, both orders coincide). Two remarks from this WP:
(1) the reduction is detector-side, so it holds in **every** output basis n (the qubit rotation does not touch Z_{i>=2}); hence
coverage and strong Born fail in every basis at every T, which excludes the class from D3 with or without the fixed-point condition;
(2) by relabeling the axes, the same holds for the X-Ising chain (h || x, only J_xx) and the Y-Ising chain; the commuting chain of
report 01 is the X case. The Cesaro (torus) law being non-Born is NUMERICAL in WP4; with g_y = +-g_x and h0 || z all four atoms
sit at +z (CG, P4).

## 7. Matchgate / free-fermion chain (g)  [P7]
Cited, not re-derived: WP4 P4.7 (PROVED formula; lab-z roots are two points +-lambda* of equal polar angle, each of kernel dimension
2^{N-1}, tan^2(theta*/2) = |r + is|/|p + iq|; unconditional N-first limit; late-time regimes (ii-a) zero mode: theta* -> pi/2,
(ii-b) bound states: cap, (ii-c) a.c.: no limit, stationary non-Born distribution [HEURISTIC + NUMERICAL]). Remarks from this WP:
(1) the one-radius statement is a z-basis statement; a qubit rotation about x or y is not Gaussian, so other bases are not covered;
(2) the matchgate chain is Pi_z-symmetric (h0 || z, h || z), so n* in {+-z} cup z-perp (P1.3); if n* = +-z the class is excluded
(atomic at every T); an equatorial n* is not excluded by any exact result; (3) it also has the antiunitary chiral symmetry with qubit
part YK (alternating XK, YK on the detector), which by P1.2 gives nothing beyond antipodality.

## 8. 1/N ring decoupling (h)  [P8]

Notation. u_q(T) = exp(-i T h0.sigma); U_0 = u_q (x) e^{-i H_D T} is the decoupled propagator. Its outcome-0 roots in basis n are
all at the kinematic point chi_n(T) = R(h0hat, -2|h0|T) n (multiplicity d), and M0^0(Omega) = c(Omega) e^{-iH_D T} with
|c(Omega)| = sin(angle(Omega, chi_n)/2). p1(Omega) = (1/d) Tr E1(Omega) = (1 + w.Omega)/2 (BRIEF 2.1) and the Jensen gap is
G_N(T) = <log p1 - L1> over S^2 (normalized area), G_N >= 0.

### P8.1 Operator-norm cap (any geometry, any scaling, any N)
**Statement.** If T ||H_qD|| < 1, every outcome-0 root in every basis n lies in the cap angle(Omega, chi_n(T)) <= 2 arcsin(T ||H_qD||).
Under SPEC 1/N (ring) and for the chain, ||H_qD|| <= sum_a |g_a| = |g|_1 independently of N, so for T < 1/|g|_1 the law at every N
(hence any N-first limit) is confined to a cap and fails coverage. Under 1/sqrtN, ||H_qD|| ~ |g|_1 sqrtN and the bound is empty.
**Status.** PROVED.
**Proof.** Duhamel: ||U - U_0|| <= T ||H_qD||. M0(Omega) - M0^0(Omega) is a compression of U - U_0, so by Weyl's inequality every
singular value of M0(Omega) is >= |c(Omega)| - T||H_qD||, which is > 0 outside the cap. QED.
**Numerical check** (`wp1_checks2.py` (4cap); ring, SPEC 1/N on all axes, H = 0.5 X0 - 0.3 Y0 + 0.9 Z0 + sum_i (0.4 X_i + 0.25 Y_i
+ 0.8 Z_i) + sum_bonds (0.7 XX + 1.1 YY + 0.9 ZZ) + (1/N)(0.3 X0 sum X_i + 0.2 Y0 sum Y_i + 0.25 Z0 sum Z_i); T = 0.9/|g|_1 = 1.2;
z basis; single time): max angle to chi = 22.0, 21.5, 21.3 deg at N = 4, 6, 8, below the bound 128.3 deg (valid but loose).

### P8.2 Normalized-HS decoupling at every fixed T (SPEC 1/N ring)
**Statement.** For g_{a,N} = g_a/N, ||H_qD||_2 = |g|_2/sqrtN exactly (normalized HS norm), so ||U - U_0||_2 <= T|g|_2/sqrtN, and
uniformly in Omega: (1/d) sum_k (s_k(M0(Omega)) - |c(Omega)|)^2 <= 2 T^2 |g|_2^2/N, and w_N -> -chi_n(T), i.e.
p1 -> sin^2(angle(Omega, chi_n)/2) uniformly.
**Status.** PROVED.
**Proof.** tau(H_qD^2) = sum_{a,b} (g_a g_b/N^2) tau(sigma^a sigma^b) tau(S_a S_b) = sum_a g_a^2 N/N^2. Duhamel in ||.||_2 (unitarily
invariant). The block is a compression, so ||M0 - M0^0||_{2,d}^2 <= 2 ||U - U_0||_{2,2d}^2, and Mirsky's inequality bounds the
singular-value deviation. p1 = (1/d)||M0||_F^2 converges with it. QED.

### P8.3 The N-first law is the decoupled one, given the log-tail hypothesis
**Hypothesis LT(T).** lim_{eps->0} limsup_{N->inf} integral over S^2 of (1/d) sum_{k: e_k(Omega) < eps} |log e_k(Omega)| dOmega = 0,
where e_k(Omega) are the eigenvalues of E1(Omega) in basis n at time T (BRIEF 2.1 "named obstruction", Theorem F eq. 7 form).
Given P8.2, LT(T) is equivalent to **G_N(T) -> 0**.
**Statement.** Under SPEC 1/N, if G_N(T) -> 0 (equivalently LT(T)) then rho_0^(n)(N,T) => delta_{chi_n(T)} as N -> inf.
**Status.** PROVED-CONDITIONAL (hypothesis G_N(T) -> 0 at the given T and basis).
**Proof.** Equivalence: by P8.2 the e_k concentrate at |c|^2 in W2 uniformly, so log p1 - L1 = -(1/d) sum_k log(e_k/p1) tends to 0
off the small-eigenvalue tail, and the tail contribution is exactly the LT integrand up to o(1). Convergence: log p1_N =
log((1 + w_N.Omega)/2) -> log((1 - chi.Omega)/2) =: L^0 in L^1 (w_N -> -chi, and log(1 + w.Omega) is uniformly integrable for |w| <= 1).
Since log p1_N - L1_N >= 0 (Jensen) and its mean G_N -> 0, L1_N -> L^0 in L^1. Weak convergence of rho_0 is equivalent to L^1
convergence of L1 - <L1> (BRIEF 2.1), and (1/4 pi)(1 + Lap L^0) = delta_chi (Lap log(1 - cos gamma) = 4 pi delta - 1). QED.
The converse fails in general: rho => delta_chi only forces limsup of the constant kappa_N = <L1_N> + 1 to be <= 0, so a law can
converge to delta with a non-vanishing Jensen gap.
**Numerical check** (`wp1_oneN.py`, `wp1_checks2.py` (4); the Hamiltonian of P8.1; ring, SPEC 1/N on all axes; single
instantaneous times, no pooling; 600-point Fibonacci grid; builder bornkit.build_H; all 12 parameters nonzero, so no conservation law
beyond detector translation):
| T | N | T/t_H | T|g|_2/sqrtN | ||U-U_0||_2 | G_N (h0hat basis) | G_N (z basis) |
|---|---|---|---|---|---|---|
| 2 | 4 | 0.17 | 0.44 | 0.383 | 0.243 | 0.234 |
| 2 | 6 | 0.059 | 0.36 | 0.314 | 0.185 | 0.178 |
| 2 | 8 | 0.019 | 0.31 | 0.272 | 0.150 | 0.146 |
| 2 | 10 | 0.006 | 0.28 | 0.244 | 0.128 | 0.124 |
| 5 | 4 | 0.42 | 1.10 | 0.855 | 0.776 | 0.772 |
| 5 | 6 | 0.15 | 0.90 | 0.701 | 0.577 | 0.567 |
| 5 | 8 | 0.047 | 0.78 | 0.600 | 0.459 | 0.451 |
| 5 | 10 | 0.015 | 0.69 | PENDING5 | 0.395 | 0.389 |
| 20 | 4 | 1.69 | 4.39 | - | 0.422 | 0.438 |
| 20 | 6 | 0.59 | 3.58 | - | 0.480 | 0.486 |
| 20 | 8 | 0.19 | 3.10 | - | 0.624 | 0.595 |
| 20 | 10 | 0.058 | 2.78 | - | 0.794 | 0.706 |
Reading. At T = 2 and T = 5 (T|g|_2/sqrtN < 1.1) the gap falls monotonically over the N-ladder, roughly like N^{-0.7}, consistent with
P8.3's hypothesis; the HS distance falls like N^{-1/2} as P8.2 requires. At T = 20 the gap rises with N: here T|g|_2/sqrtN = 2.8-4.4,
so N <= 10 is far below the crossover N* ~ (T|g|_2)^2 (about 80 at T = 20) where P8.2's bound becomes small, and the N = 4 point is
beyond the Heisenberg time. These data neither support nor refute LT at T = 20; they show that N <= 10 cannot probe the 1/N ring's
N-first law at gT = O(10). Cloud diagnostics at T = 20 in the h0hat basis (N = 4, 6, 8): resultant 0.962, 0.963, 0.943, median
angle to chi 12.5, 11.2, 14.7 deg: a cap about the kinematic point, not a spread law. PENDING_S05
**Intuition.** Under 1/N a typical detector state feels a field of size g/sqrtN on the qubit; only an exponentially small fraction of
highly polarized states feels O(g). The roots follow the typical states unless that small fraction carries a logarithmically large
weight, which is exactly what LT forbids.
**Failure modes.** Theorem G shows HS convergence does not control roots of non-normal pencils in general; LT is the precise extra
input. The crossover N* ~ (gT)^2 means that the order of limits matters: at T ~ 1/g^2 (van Hove) one needs N >> g^{-2}.

### P8.4 Consequences for D3 under SPEC 1/N (conditional)
**Statement.** If G_N(T) -> 0 for every T (and every basis n), the N-first law is delta_{chi_n(T)} at every T. Then: (instantaneous)
the T -> inf limit exists only for n = +-h0hat (law delta_{+-h0hat}) or h0 = 0 (law delta_n for every n, so Phi = id and no unique
fixed point); (Cesaro) the law is the uniform measure on the circle through n about h0hat, so Phi_C(n) = sign(h0hat.n) h0hat
(cone lemma) with n* = h0hat and law delta. Either way no D3 point: **the SPEC-1/N ring is a no-go in every tier, conditionally on
LT.** **Status.** PROVED-CONDITIONAL.

### P8.5 Unconditional 1/N statements
**Statement.** Under SPEC 1/N, the N-first law at every T is delta_{chi_n(T)} in every basis, without LT, in: (i) QND_a (the roots are
R_a(chi_k) n with W_-^dag W_+ unitary and ||W_-^dag W_+ - e^{-2i h0a T}||_2 <= 2T|g_a|/sqrtN, so Hoffman-Wielandt for normal
matrices sends the eigenphase law to a point); (ii) COM (the block formula of P5.2 with nu_N = law of g S_x/N -> delta_0);
(iii) CG (delta_{+a} at every N already, in the forced basis). **Status.** PROVED.

## 9. Master table, Tiers 1-6 (i)  [P9]

**Class key** (all PROVED unless marked; "excluded" = no point of the class satisfies D3, so no open stable region contains one):
- **QND_a** (P2, P3): [H, a.sigma_0] = 0. Excluded in every basis (fixed point a with law delta; bases n perp a: Theorem C null
  set, R10 Cesaro R = 1/2 a.e.; other bases: no coverage); strong fails everywhere. Any scaling.
- **CG** (P1.4, P4): GCG points. Excluded in every basis (delta at the forced axis). Any scaling.
- **Pi_a** (P1.3, P5.1): constraint only, n* in {+-a} cup a-perp. Not an exclusion.
- **COM** (P5.2; B, D, E, H1): commuting detector [H_D, S_x] = 0 with g_x only. Z basis: excluded (B/D if h0z = 0, E/H1 if not;
  1/sqrtN); bases with n_x != 0 and n = +-y: late-time law not Born; (y,z)-meridian otherwise OPEN. Under 1/N: delta, unconditional.
- **ISI** (P6 = WP4 P4.6): chain with J and h along one axis. Four atoms per T, N-independent, every basis: excluded.
- **MG** (P7 = WP4 P4.7): chain {h_z, J_xx, J_yy, g_x, g_y, h0z}. One radius per T in the z basis: excluded if n* = +-z; z-perp open.
- **ISO**: ring with J_xx = J_yy = J_zz (BRIEF 3 "ISO"). Proof: the Heisenberg term commutes with the collective S, and every other
  ring term is built from sigma_0 and S, so U = e^{-i H_Heis T} U_{J=0} with a detector-only first factor; M0 is multiplied on the left
  by a unitary and the roots are those of the J = 0 ring with the same fields and couplings. Not an exclusion.
- **1/N** (P8): SPEC ring scaling. Law delta at the kinematic point at every fixed T: PROVED-CONDITIONAL on G_N(T) -> 0 (LT);
  unconditional inside QND, CG, COM. Excludes every ring tier under SPEC scaling, conditionally.
- **DEC**: g = 0, delta at the kinematic point (trivial).
- **GI** (generic interior): no exact class applies; this is the named residual (BRIEF G1, G2).

Parameters are SPEC; "only" lists the nonzero ones. Ring statements hold for every scaling hypothesis unless the class says
otherwise; under SPEC 1/N every ring row is additionally covered by the conditional 1/N row. "Conserved" names the conservation law
that the zero pattern creates.

### Ring, Tier 1 {J_zz, h_z, h0z, g_x} (Pi_z on the whole tier)
| sub-pattern | conserved / symmetry | exact class and consequence | residual |
|---|---|---|---|
| all four nonzero | Pi_z | Pi_z: n* in {+-z} cup z-perp; WP3 P1-P3 resonance and gauge laws (conditional) | **GI** |
| h0z = 0 | X_0 | QND_x (R05 explicit law; resonant h_z in {0, +-2J_zz} gives R = 1/2) | excluded |
| J_zz = 0 | total collective spin (detector-only), Pi_z | none beyond Pi_z (WP3 P3b leading order) | **GI** |
| h_z = 0 | prod X_i (detector-only), Pi_z; resonant Ising point | none beyond Pi_z | **GI** |
| h_z = J_zz = 0 | S_x (detector), Pi_z | COM (E/H1 in z; P5.2 in z-perp): all Pi_z-allowed axes covered at 1/sqrtN; delta under 1/N (P8.5) | excluded (1/sqrtN and 1/N) |
| h_z = J_zz = h0z = 0 | X_0, S_x | QND_x and COM (B, D) | excluded |
| J_zz = h0z = 0 | X_0 | QND_x (R03) | excluded |
| g_x = 0 | decoupled | DEC | excluded |

### Ring, Tier 2 {J_zz, h_z, h0x, (h0z), g_x}
| sub-pattern | conserved / symmetry | exact class and consequence | residual |
|---|---|---|---|
| h0x, h0z both nonzero (tilted) | none on the qubit side (P5.1; checked) | none | **GI** |
| h0z = 0 | X_0 | QND_x (Theorem C, R10, GC, QAI) | excluded |
| h0x = 0 | Pi_z | = Tier 1 | see Tier 1 |
| h_z = J_zz = 0 (tilted h0) | S_x (detector) | COM: z basis E/H1; P5.2 for n_x != 0 (covers the weak-coupling n* ~ h0hat) | excluded in z and for n_x != 0 (1/sqrtN); meridian open |
| h_z = 0 or J_zz = 0 alone (tilted h0) | detector-only | none | **GI** |

### Ring, Tier 3 {J_zz, h_z, h0x, h0z, g_x, g_y} (or g_x with a transverse detector field h_x)
| sub-pattern | conserved / symmetry | exact class and consequence | residual |
|---|---|---|---|
| generic | none on the qubit side | none | **GI** |
| h0x = 0, g_y = +-g_x | Z_0 +- sum Z_i | CG_z (delta for every N, T) | excluded |
| h0x = 0, g_y != +-g_x | Pi_z, [H_D, M_z] = 0 | Pi_z; Theorem I and WP3 P2 (radii ~ sqrt(kappa), kappa = (g_x-g_y)/(g_x+g_y)) | **GI** |
| h0 = 0, g_y = +-g_x | charge | CG_z | excluded |
| h0 = 0, g_y != +-g_x | Pi_z | Pi_z | **GI** |
| g_x = 0 and h0 = 0 | Y_0 | QND_y | excluded |
| g_x = 0, h0 || z | Pi_z | Pi_z | **GI** |
| h0z = 0, g_y != 0 | none (g_y breaks X_0; h_z breaks Pi_x) | none | **GI** |
| variant h_x != 0, g_y = 0: h0z = 0 | X_0 | QND_x (R05: detector h_x gives R = 1/2) | excluded |
| variant h_x != 0, g_y = 0: h0z != 0 | none | none | **GI** |

### Ring, Tier 4 XXZ {J_perp = J_xx = J_yy, J_zz, h_z, h0x, h0z, g_x, g_y, (g_z)}
| sub-pattern | conserved / symmetry | exact class and consequence | residual |
|---|---|---|---|
| generic (tilted h0, g_y != +-g_x) | none on the qubit side | none (WP3 P7 golden-rule band, heuristic) | **GI** |
| h0 || z, g_y = +-g_x (any g_z) | Z_0 +- M_z | CG_z | excluded |
| h0 || z, g_y != +-g_x | Pi_z, M_z | Pi_z; Theorem I, WP3 P2 | **GI** |
| h0 || x, g_y = g_z = 0 | X_0 | QND_x (historical leads 4a-4d live here) | excluded |
| J_perp = J_zz (isotropic) | exchange decouples | ISO: reduces to the J = 0 ring; with h0 || h || z and g_x = g_y: CG_z | GI unless CG/QND |
| J_perp = 0 | | = Tiers 1-3 | see those |
| J_zz = 0 (XX ring) | M_z if fields || z | Pi_z if h0 || z (no free-fermion structure: the collective coupling is non-local after Jordan-Wigner) | **GI** |

### Ring, Tier 5 XYZ (all 12)
| sub-pattern | exact class | residual |
|---|---|---|
| h0 || a, g perp a vanish (a = x, y, z) | QND_a | excluded |
| h0 || f, h || f, J_bb = J_cc, g_c = +-g_b != 0 (f = x, y, z) | CG_f (x and y versions new here) | excluded |
| |g_x| = |g_y| = |g_z|, J isotropic, h0 || a, h || k (tilted) | CG_iso | excluded |
| h0 || a, h || a (other terms free) | Pi_a | constraint only; **GI** |
| h0 || b, h || e, only g_c (b, c, e distinct) | sigma_0^b prod sigma_i^e, R_b(pi) | constraint only; **GI** |
| h || x, J_yy = J_zz, only g_x (any h0) | COM | n_x != 0 and n = +-y excluded at 1/sqrtN (P5.2); z basis by E/H1 when h0y = 0; rest of the (y,z)-meridian open |
| J_xx = J_yy = J_zz | ISO (reduces to J = 0) | GI unless another class |
| everything else | none | **GI** |

### Chain, Tier 6 (coupling O(1); no 1/N, no ISO)
| sub-pattern | exact class | residual |
|---|---|---|
| Tier-1 chain {J_zz, h_z, h0z, g_x} | ISI (4 atoms, every basis) | excluded |
| Tier-2 chain (+ h0x) | ISI | excluded |
| Tier-3 chain (+ g_y, any g_z) | ISI; with h0 || z and g_y = +-g_x also CG_z (atoms at +z) | excluded |
| Tier-3 variant, TFIM detector (h_x, h_z, J_zz), h0z = 0, g_x only | QND_x (Theorem C, R07, R10) | excluded |
| Tier-3 variant, TFIM, otherwise | none | **GI** |
| XXZ chain, h0 || z, g_y = +-g_x | CG_z | excluded |
| XX chain (J_zz = 0), h || z, h0 || z, g_z = 0 | MG (z basis) + Pi_z | excluded if n* = +-z; equatorial n* open |
| XXZ chain, h0 || x, g || x | QND_x | excluded |
| XXZ chain otherwise (interacting) | Pi_z if fields || z | **GI** (N-first limit at fixed T exists: WP4 P4.1-P4.5) |
| XYZ chain: J_xx = -J_yy, h || z, h0 || z, g_y = +-g_x | CG_z staggered (new) | excluded |
| XYZ chain: J and h along one axis a | ISI rotated | excluded |
| XYZ chain: XY-type in the plane perp a, h || a, h0 || a, coupling perp a | MG rotated (basis a) | excluded if n* = +-a |
| XYZ chain otherwise | none | **GI** |

**What remains in the generic interior.** Tier 1 with h0z, J_zz, h_z all nonzero (and its J_zz = 0 and h_z = 0 faces); Tier 2 with
a tilted qubit field and a nonzero Ising detector; Tier 3 away from h0x = 0, g_y = +-g_x; Tier 4 away from h0 || z with
g_y = +-g_x and away from the central-X slice; the XYZ ring off the exact submanifolds; the interacting chains (XXZ with J_zz != 0,
XYZ, TFIM) off their QND/CG/ISI/MG submanifolds; the matchgate chain in equatorial bases. Every exact class is a closed set of
positive codimension in its tier (except that ISI covers the whole Tier-1-3 chain as posed), so in the ring tiers the exact classes
exclude only their own points: the generic interior is open and dense, and an open stable region, if one exists, must lie inside it.
Under SPEC 1/N the ring's generic interior is also excluded, conditionally on LT (P8).

## 10. Numerical verification log
All runs: bornkit (BRIEF 7) with the mandated command; SPEC positive convention; builder bornkit.build_H; single instantaneous times,
no pooling or averaging; N <= 10 (roots N <= 8, log-potential up to N = 10). Every zero parameter in a lemma check is the hypothesis
being tested (it creates the conservation law); controls add the breaking term.
- `n1_core.py` -> `n1_core.json` (from the interrupted attempt; re-read and sanity-checked against the theory here, not re-run):
  QND_a cone and orbit formula (P2), covariance (P1.1), mirror identity (P1.2). N = 4-6, T = 3.7-20.
- `lemma_checks.py`: written by the interrupted attempt, never produced output; superseded by `wp1_checks2.py`.
- `wp1_checks2.py` -> `wp1_checks2.log`, `wp1_checks2.json` (263 s): (1) rigid shift / generalized Theorem C (P3); (2) GCG
  completeness (P4); (3) Pauli-string covariance (P1.1, P5.1); (4) 1/N and 1/sqrtN ring clouds and Jensen gaps at T = 5, 20 (P8.3);
  (4cap) the operator-norm cap (P8.1).
- `wp1_oneN.py` -> `wp1_oneN.log`, `wp1_oneN.json`: 1/N crossover at T = 2, 5, N = 4-10, coupling multipliers s = 1, 0.5 (P8.3).
- 1/sqrtN comparison (`wp1_checks2.log` (4), same Hamiltonian but g_x, g_y scaled by 1/sqrtN and g_z by 1/N, T = 20, h0hat basis):
  G_N = 0.49, 0.77, 0.89 and resultant 0.88, 0.79, 0.77 at N = 4, 6, 8 (T/t_H = 1.7, 0.60, 0.19): no decoupling trend, as expected
  (the HS coupling does not vanish at 1/sqrtN). Not a trend claim beyond N <= 8.

## 11. Answers to GOAL questions, open items, surprises

### Answers (WP1 scope: Theorem 1, exact no-go classes)
1. **Theorem 1 (exact no-go classes).** Fix the geometry, the scaling hypothesis, and D1-D4. No open stable region (D3) contains a
   point of: QND_a for a in {x,y,z} (P2, P3; every basis); any GCG point, i.e. QND_f, CG_f (f = x, y, z; ring J_bb = J_cc; chain also
   J_bb = -J_cc) and CG_iso (P1.4, P4; every basis); the Ising chains ISI (P6; every basis); the zero-detector Tier-1 ring slice at
   1/sqrtN (COM, P5.2 with Pi_z). The matchgate chain (P7) and the tilted-field commuting ring slice (P5.2) are excluded except for
   preferred axes in an explicitly named leftover set (equatorial for MG; the (y,z)-meridian for COM). Under SPEC 1/N every ring
   point is excluded conditionally on LT (P8.4), and QND, CG, COM ring points unconditionally (P8.5). Status: PROVED except where
   marked.
2. **Does symmetry fix the preferred axis?** Only partly. A continuous qubit-side symmetry fixes n* = +-a but then forces the law to be
   delta (P1.4): symmetry protection and nondegenerate Born are incompatible. A discrete pi-rotation (Pi_a and the single-coupling Pauli
   strings) leaves n* in {+-a} cup a-perp (P1.3, P5.1); it constrains, it does not exclude. Real H relates the forward and
   fixed-input axes by the y-mirror (P1.2) and constrains neither alone. Generic tilted-field points (Tier 2 as posed, Tier 5 interior)
   have no qubit-side symmetry, so n* is a dynamical object there.
3. **Zero-parameter patterns.** Section 9 lists every sub-pattern. The zeros that matter are those that create a conserved quantity with a
   qubit component: h0z = 0 in Tiers 1-2 (X_0), h0 || z with g_y = +-g_x and U(1) detector (charge), a single coupling axis parallel to
   h0 (QND), and in the chain J_xx = J_yy = 0 with h || z (Z_{i>=2}). Zeros that create only detector-side or discrete symmetries
   (J_zz = 0, h_z = 0, Pi) leave the point in the generic interior.
4. **h0 parallel to a coupling axis.** With the other two couplings zero it is QND (excluded); with other couplings present it gives
   Pi or nothing, unless the charge-graded conditions hold.
5. **g_y = +-g_x.** Excluded (CG) exactly when h0 || z, h || z and J_xx = J_yy (ring) or J_xx = +-J_yy (chain); otherwise (tilted h0,
   transverse detector field, or ring J_xx != J_yy) it is not graded (numerical controls in P4) and falls in the generic interior.
6. **Isotropic exchange.** In the ring it drops out (ISO); in the chain it does not. It is excluded only together with CG conditions.
7. **Ring vs chain (exact classes).** The chain has two whole-tier exclusions the ring lacks (ISI covers Tiers 1-3 as posed; MG covers
   the XY chain in the z basis) and extra staggered CG patterns; the ring has ISO and the 1/N decoupling. Generic-interior residuals
   remain in both.
8. **Weak vs strong.** Every exact class fails the strong criterion (1D or atomic support, or delta). For the weak criterion the only
   classes that reach coverage are QND bases n perp a (then Theorem C/R10) and COM (then P5.2); all others fail coverage.

### Open items
- LT / G_N(T) -> 0 for the SPEC-1/N ring at fixed T: numerically consistent at T|g|_2/sqrtN < 1 (N <= 10), untestable at T = 20 with
  N <= 10 (crossover N* ~ (T|g|_2)^2 ~ 80). This is BRIEF G1 in its cleanest form.
- COM class with tilted h0: preferred axes on the (y,z)-meridian other than +-y, +-z are not covered by P5.2 or E/H1.
- MG chain and every Pi_a-symmetric generic-interior point: equatorial preferred axes are not excluded by any exact result.
- CG_iso in the chain: detector condition not derived (necessary condition |g_x| = |g_y| = |g_z| only). Exotic.
- Discrete qubit-side symmetries with non-product detector parts are not classified (continuous ones are, by P4).
- Attractivity (D4) of the Pi-fixed axis is unstudied: at g -> 0 Phi is a rotation about h0hat (neutral), so attractivity is an
  O(g) property. The instantaneous T -> inf law in Tier 1 need not exist (pure-point Ising spectrum), in which case D4 is posed on
  the Cesaro law.

### Surprises
- The QND root set is an orbit, {R_a(chi_k) n}, of the eigenphases of one basis-independent unitary W_-^dag W_+: a single circle
  measure determines the law in every basis (P2).
- Every continuous qubit-side symmetry is a GCG charge, so continuous symmetry always forces a point mass (P1.4). Only discrete
  symmetries survive as axis selectors compatible with a spread law.
- The endpoint chain has charge-graded lines absent from the ring (J_bb = -J_cc, pairing exchange with a staggered charge), and all
  four sign combinations of (g_c/g_b, J_cc/J_bb) are graded. My own script mislabelled one of them as a control; the numerics
  (ptp 5e-11) agreed with the classification, not with the label.
- Under 1/N, ||H_qD|| stays |g|_1 in operator norm; only the normalized HS norm vanishes. The Jensen gap at T = 20 grows with N over
  N = 4-10 at a generic Tier-5 point (0.44 -> 0.71, z basis), while the cloud stays a 12-15 deg cap about the kinematic point: the
  BRIEF's decreasing Tier-4 gap at T = 20 is not universal at accessible N.
- For real H, flipping every sign (code vs SPEC) mirrors the preferred axis in y (P1.2); the campaign's screen_00 has h0y != 0, so
  there the sign flip instead exchanges forward and fixed-input laws.

### Corrections to BRIEF
- BRIEF 3 "CG" row lists only the z-pattern with "no transverse detector field". P4 proves the complete list: also g_z arbitrary,
  the x and y versions (Tier-5 slices), the chain's staggered J_xx = -J_yy lines with either g sign, and the isotropic-modulus tilted
  set. The listed hypotheses are also necessary (P4, including J_xx = J_yy in the ring).
- BRIEF 1.5 "Pi parity ... Phi(z) = +-z": correct, but Pi_z only restricts n* to {+-z} cup z-perp; z is an invariant line of Phi,
  not necessarily the preferred axis. Non-Pi Pauli strings (sigma_0^b prod sigma_i^e with a single coupling g_c) give the same
  R_b(pi) constraint (P5.1).
- BRIEF 3 lists E and H/H1 as covering the "T1/T2 zero-detector slices" without saying they are Z-basis statements. P5.2 extends
  them to bases with n_x != 0 and n = +-y; the rest of the (y,z)-meridian is open.
- BRIEF 2.7 "Matchgate: a Gaussian chain has <= 2 roots +-lambda* per time": z basis only (P7 remark 1).
- BRIEF 1.2 "1/N trivializes the ring ... elsewhere, given log-tail control": confirmed, with the hypothesis stated as
  G_N(T) -> 0 (equivalently LT, P8.3), plus two additions: the operator norm of H_qD does not vanish under 1/N (only a T < 1/|g|_1 cap
  follows, P8.1), and exact numerics reach the decoupled regime only for N >> (T|g|_2)^2.
