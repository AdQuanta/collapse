# WP4: endpoint chain in the SPEC order

> Source: Agent work-package report, go/no-go derivation workflow (scratchpad `gonogo/wp/WP4/REPORT.md`), 2026-09-24. Derivations and bornkit numerics (N <= 10); not refereed unless stated. The report was interrupted by a usage limit in places; content preserved verbatim.
> Collected: 2026-09-24
> Published: 2026-09-24

# WP4 — Endpoint chain in the SPEC order: impurity problem and late-time law

Status of this file: COMPLETE (2026-09-24); summary in summary.json. Scripts and data: this folder. Conventions: SPEC positive convention (BRIEF 1.1), chain
`H_qD = g_x X0X1 + g_y Y0Y1 + g_z Z0Z1`, O(1) in N. Builder `bornkit.build_H('chain', N, p)`. Orders: "N-first" = N -> inf
at fixed T; "late" = then T -> inf. `t_H = 2 pi 2^(N+1)/W` (W = spectral width of H).

## Skeleton (one heading per proposition)
- P4.1  Light-cone factorization of the effect operator (a)
- P4.2  Exact spectator invariance (a)
- P4.3  Root localization and non-normal displacement (a)
- P4.4  Potential representation and mean bound (a)
- P4.5  N-first limit at fixed T: weak convergence under H1 (a)
- P4.6  Ising chain with h_D || z: exact 4-atom law, late-time behaviour (b)
- P4.7  Matchgate chain: exact one-radius formula, SPEC-order late-time law (b)
- P4.8  First-order impurity law: kinematic point + 2g spec(F*) (c)
- P4.9  Schur bound: root spreading <= golden-rule depolarization (c)
- P4.10 Only spectral weight at 2|h0| moves roots in the fixed-point basis (c)
- P4.11 Gapped vs gapless boundary spectral function (c)
- P4.12 Late-time law predictions; failure of the classical-noise reduction for the chain (c)
- P4.13 Numerics in the SPEC order: light-cone saturation and T-flow (d)
- P4.14 SPEC order vs reverse order (d)
- P4.15 Reinterpretation of the 0.72 plateau / 0.12 deficit / screen_00 (e)
- P4.16 Ring vs chain comparison (f)

---
## Part (a): the N-first limit at fixed T via Lieb-Robinson

Notation. `P_1^{(N)}(T) = U_N(T)^dag (|1><1| (x) I) U_N(T)` (Heisenberg-evolved qubit projector; for output basis n use
`|-n><-n|`). `E1^{(N)}(Omega) = <psi_Omega| P_1^{(N)}(T) |psi_Omega>` (partial inner product on the qubit) `= M0^dag M0`, `M0 =
cos(theta/2)U10 + e^{i phi} sin(theta/2)U11`, `d_N = 2^N`, `L1^{(N)} = (1/d_N) log det E1^{(N)}`, `rho0 = (1/4pi)(1 + Delta_S L1)`
(BRIEF 2.1). The key observation used throughout: **E1 is the qubit compression of the Heisenberg evolution of a
LOCAL operator (the qubit projector)**, so it is controlled by Lieb-Robinson bounds, although U itself is not.

### P4.1 Light-cone factorization of the effect operator
**Statement.** For the endpoint chain on N sites, any L < N and any T,
`|| P_1^{(N)}(T) - P_1^{(L)}(T) (x) I_{L+1..N} || <= eps_L(T) := sum_a |J_aa| int_0^T ||[sigma_L^a, tau_L^u(P_1)]|| du`,
where `tau_L` is the Heisenberg evolution of the L-site chain (qubit + sites 1..L, open end). Hence
`sup_Omega || E1^{(N)}(Omega) - E1^{(L)}(Omega) (x) I || <= eps_L(T)` in every output basis. With the standard
nearest-neighbour Lieb-Robinson bound (Hastings' iteration, 3 bond choices per step; on-site fields removed by an
interaction picture), `eps_L(T) <= (1/3) (6 Jbar T)^{L+1}/(L+1)! e^{6 Jbar T}`, `Jbar = max(|g_x|+|g_y|+|g_z|, |J_xx|+|J_yy|+|J_zz|)`:
superexponentially small in L at fixed T.

**Status.** PROVED (the constant in the LR bound is the textbook one and is loose; the first, exact inequality is what
is used below).

**Proof.** Duhamel: `tau_N^T(O) - tau_L^T(O) (x) I = int_0^T tau_N^s( i[H_N - H_L, tau_L^{T-s}(O)] ) ds`. `tau_L^u(O)` is
supported on sites 0..L, and every term of `H_N - H_L` except the bond `h_{L,L+1} = sum_a J_aa sigma_L^a sigma_{L+1}^a`
commutes with it; `||[sigma_L^a sigma_{L+1}^a, X]|| = ||[sigma_L^a, X]||` for X on 0..L; `tau_N^s` is norm-preserving. The
compression by a unit qubit vector does not increase the norm. The LR bound: `C(u) = ||[sigma_L, tau_L^u(O)]|| <=
2 sum_{n>=L} (6 Jbar u)^n/n!` (paths of n overlapping bonds from bond (0,1) to bond (L-1,L)); integrate. QED.

**Numerical check** (`a_checks.py`, `a_checks.json`; builder `bk.build_H('chain', N, p)`; exact dense evolution).
`||P_1^{(9)}(T) - P_1^{(L)}(T) (x) I||_op`, L = 1..8:
- slow detector "R" (defined in P4.13: `h_x=0.6, h_z=0.8, J_xx=0.15, J_yy=0.10, J_zz=0.20, h0=1.0(sin20,0,cos20),
  g=(0.15,0.10,0.08)`): T=1: 5.8e-2 ... 3.2e-8, 1.7e-9; T=2: 2.0e-1 ... 7.6e-6, 8.1e-7; T=4: 5.7e-1 ... 1.5e-3, 3.3e-4.
- screen_00 (SPEC signs, BRIEF 1.1): T=1: 1.5e-1 ... 2.5e-2 at L=8; T=2: 0.17 at L=8; T=4: 0.33 at L=8.
  **The operator-norm light cone of screen_00 already exceeds 9 sites at T = 1-2** (its |J| ~ 1.1-2.5). BC-C's
  N-independence of the screen_00 dipole at N >= 6-9 (T <= 4) is therefore a statement about low moments of the law,
  not operator-norm light-cone saturation; the slow detector is light-cone controlled at N = 9-10 only for T <~ 5.

**Intuition.** The collapse law is built from where the qubit projector's Heisenberg image has support; beyond the
light cone the detector is a spectator.

**Failure modes.** None for the inequality; the LR constant is useless quantitatively (it predicts saturation at
L ~ 6e Jbar T ~ 20-100), so numerics must supply the actual saturation length.

### P4.2 Exact spectator invariance
**Statement.** If `E1 = E1_L (x) I_m` (in particular if `U = U_L (x) W` with W any unitary on uncoupled spectators,
`core/projective_roots.py:119-139`, `append_uncoupled_spectator`), then `L1 = (1/(d_L m)) log det(E1_L (x) I_m) =
L1_L` identically, so the normalized law is unchanged; every root's multiplicity is multiplied by m.
**Status.** PROVED (one line: `log det(A (x) I_m) = m log det A`; for `U_L (x) W`, `E1 = E1_L (x) W^dag W`).
**Consequence.** By P4.1 the N-chain effect operator is an `eps_L(T)`-perturbation of an m-fold spectator copy of the
L-chain one, with m = 2^{N-L}. The whole question of the N-first limit is how this perturbation acts on a
highly degenerate (m-fold) pencil: P4.3-P4.5.

### P4.3 Root localization and the non-normal displacement
**Statement.** (i) Every outcome-0 root of the N-chain at time T lies in the sublevel set
`S_L = {Omega : lambda_min(E1^{(L)}(Omega)) <= eps_L(T)} = {sigma_min(M0^{(L)}(Omega)) <= eps_L^{1/2}}` for every L < N.
(ii) Near a simple L-root Omega_j with homogeneous (chordal) condition number `kappa_j = |x||y|/sqrt(|y^H U10 x|^2 +
|y^H U11 x|^2)`, `sigma_min(M0^{(L)}(Omega)) = sin(gamma/2)/kappa_j (1 + o(1))` (gamma = angle to Omega_j), so the
component of S_L around Omega_j has angular radius `~ 2 kappa_j eps_L^{1/2}`; for a Jordan block of size s the radius is
`~ eps_L^{1/(2s)}`.
**Status.** PROVED ((i) is Weyl's inequality; (ii) is first-order perturbation of the smallest singular value: the
linear form `psi -> y^H(alpha U10 + beta U11)x` vanishes at psi_j and has norm `sqrt(|a|^2+|b|^2)`).
**What non-normality does (the question asked).** The individual roots are NOT controlled by eps_L: they may move by
`2 kappa_j eps_L^{1/2}` (square root, because only E1 = M0^dag M0 is controlled, not M0), and the m-fold spectator clusters
of the product pencil split in an uncontrolled pattern inside S_L. What IS controlled is the normalized mass in each
component of S_L (P4.5). Numerically (R detector, T=4, `a_checks.py` [3]): rms kappa = 20, 38, 173, 232, 642, 1811, 5177
at N = 3..9 (x2.5 per site); at T=2 it is 8, 13, 15, 20, 23, 28, 30. So at accessible sizes `eps_L kappa^2` is NOT small
for T >~ 4 (e.g. `3.3e-4 x 1.8e3^2 ~ 10^3` at L=8, T=4): superexponential decay of eps_L beats exponential growth of
kappa only at L ~ 6e Jbar T, beyond numerics. Part of the kappa growth is the cluster effect (near-multiple roots have
large individual condition numbers) and part is the near-scalar weak-coupling pencil (P4.8: roots are eigenvalues of
g * F*, so pencil perturbations are amplified by 1/g); neither is a pathology of the physical family.

### P4.4 Potential representation and the mean bound
**Statement.** For a regular outcome-0 pencil with roots Omega_j (algebraic multiplicity, d of them, rho = (1/d)
sum delta_{Omega_j}): `L1(Omega) = a + 1 + U_rho(Omega)`, with `U_rho(Omega) = int log((1 - Omega.Omega')/2) d rho(Omega') <= 0`,
`<U_rho> = -1`, `||U_rho||_{L1(S^2, dOmega/4pi)} = 1`, and `a = <L1> = (2/d) log|kappa_lead| - 1`, where kappa_lead is the
constant in the binary-form factorization `det(alpha U10 + beta U11) = kappa_lead prod_j (b_j alpha - a_j beta)` with unit
root vectors (a_j, b_j). Consequently **`a >= max_Omega L1(Omega) - 1`**, and weak convergence of laws is equivalent to
L1-convergence of `L1 - <L1>` (as BRIEF 2.1 states).
**Status.** PROVED. `|b_j alpha - a_j beta|^2 = 1 - |<psi_j|psi_Omega>|^2 = (1 - Omega.Omega_j)/2`; `int_{-1}^{1} log((1-u)/2) du/2 =
-1`; `U_rho <= 0` because `(1 - Omega.Omega')/2 <= 1`. The equivalence uses that the kernel is uniformly L1 and its
truncations are continuous.
**Numerical check.** Chain R, N=4, T=3, 40x80 Gauss-Legendre grid: `max|L1 - (a+1+U_rho)| = 1.3e-5` (quadrature),
a = -1.1996 >= max L1 - 1 = -1.2097.

### P4.5 Existence of the N-first law at fixed T (weak convergence)
**Statement.** Fix T and bounded chain parameters with regular pencils for all N. Let
`R_L(eps) = < (1/d_L) sum_k log(1 + eps/e_k^{(L)}(Omega)) >` (e_k = eigenvalues of E1^{(L)}(Omega); the regularized
small-eigenvalue log tail) and `delta_L = R_L(eps_L(T))`.
**Hypothesis H1:** `delta_L -> 0` as L -> infinity.
Then (i) `a_N = <L1^{(N)}>` converges to a finite `a_inf`; (ii) `L1^{(N)}` is Cauchy in L1(S^2):
`||L1^{(N)} - L1^{(N')}||_1 <= (a_{N'} - a_N) + 2 delta_{N'}` for N > N'; (iii) `rho0^{(N)}(T)` converges weakly to
`rho0^inf(T) = (1/4pi)(1 + Delta_S L1^inf)`. Without H1 one still has, unconditionally: `L1^{(N)} <= L1^{(L)}_{eps_L}
:= (1/d_L) sum_k log(e_k^{(L)} + eps_L)` pointwise, `a_N <= a_L + delta_L`, and `a_N >= log(max_Omega lambda_min^{(L)}(Omega)
- eps_L) - 1 > -inf` (P4.4), i.e. the means are bounded and subsequential weak limits exist.
**Sufficient condition for H1.** If the small-eigenvalue density is at most exponentially singular,
`< (1/d_L) #{k : e_k^{(L)}(Omega) < eta} > <= C (e^{cL} eta)^alpha` for some alpha, c, C independent of L, then
`delta_L = O(e^{cL} eps_L log(1/eps_L))^{alpha'} -> 0` because eps_L(T) is superexponentially small. For semisimple
roots with condition numbers kappa_j, `R_L(eps) ~ eps <kappa^2> (log(1/(eps <kappa^2>)) + 1)`, so H1 holds whenever
`<kappa^2>_L` grows at most exponentially (observed: x6 per site at T=4, x1.2 at T=2).
**Status.** PROVED-CONDITIONAL on H1 (H1 is the light-cone-local form of BRIEF's named obstruction G1; it is strictly
weaker, since it is needed only at the superexponentially small scale eps_L(T)).
**Proof.** Weyl with `||E1^{(N)} - E1^{(N')} (x) I|| <= eps := eps_{N'}` gives `e_k^{(N)} <= e~_k + eps` (e~ = eigenvalues
of `E1^{(N')} (x) I`), hence `L1^{(N)} <= L1^{(N')} + r` with `r = L1^{(N')}_eps - L1^{(N')} >= 0`, `<r> = delta_{N'}`.
Integrating, `a_N <= a_{N'} + delta_{N'}` for all N > N', so limsup a <= liminf a + 0: a_N converges in [-inf, 0]; the
lower bound of P4.4 (evaluate at the point where lambda_min^{(L)} is largest, using `e_k^{(N)} >= e~_k - eps`) makes the
limit finite. Then `f = L1^{(N')} + r - L1^{(N)} >= 0` with `<f> = a_{N'} + delta_{N'} - a_N -> 0`, and
`||L1^{(N)} - L1^{(N')}||_1 <= <f> + <r>`. L1-convergence of potentials gives distributional, hence (probability
measures on a compact space) weak, convergence of rho0 = (1/4pi)(1 + Delta L1). QED.
**Identification of the limit (remark, same hypothesis pointwise).** tau-moments `tau(E1^k)` of the Heisenberg-local
E1 converge superexponentially (P4.1), so the spectral measures of E1^{(N)}(Omega) under the normalized trace converge to
those of an operator E1^inf(Omega) in the infinite-temperature (tracial) half-chain algebra, and `L1^inf(Omega) = log
Delta_FK(E1^inf(Omega))` (Fuglede-Kadison determinant) whenever log is uniformly integrable near 0. The N-first chain law
is thus a Brown-measure-type object; convergence of finite-N eigenvalue laws to Brown measures is known to need exactly
this kind of small-singular-value control (the "single ring"/regularization literature: Guionnet-Krishnapur-Zeitouni,
Sniady). This is the precise sense in which non-normality enters the SPEC order.
**Numerical check.** P4.13 (N-ladder at fixed T: moments and `||L1^{(N)} - L1^{(N-2)}||_1`).
**Failure modes.** H1 could fail only if E1 had superexponentially small eigenvalues on a set of non-negligible
log-mass; nothing in the approved families suggests this (proportionate: stated, not pursued). Singular pencils
(`L1 = -inf`) are outside the statement (SPEC singular-continuum rule still owed, BRIEF 5.2.3).

---
## Part (b): exactly solvable chain subclasses in the SPEC order

### P4.6 Ising chain with h_D || z (Tier 1-3 analogues): exact 4-atom law; both orders coincide
**Statement.** Chain with `h_x = h_y = 0`, `J_xx = J_yy = 0`, arbitrary `h_0`, `g_x, g_y, g_z`. Then `[H, Z_i] = 0` for
all i >= 2, and for every N >= 2 and every T the outcome-0 law is `rho = (1/4) sum_{s=+-} sum_{j=1,2} delta_{Omega_j^s(T)}`,
where `Omega_{1,2}^s(T)` are the two roots of the 2x2 pencil of the qubit+site-1 problem
`H_s = H_q + (h_z + s J_zz) Z_1 + sum_a g_a sigma_0^a sigma_1^a` (4x4). The law is exactly N-independent, so the N-first
limit equals the N = 2 law and the SPEC and reverse orders coincide in this class. It is not Born in any
non-vacuous sense. Strong Born fails at every T (atomic law, BRIEF 3 "W/S/iff"). The support has at most 4 polar
angles, so coverage fails. The finite-support weak identity `tan^2(theta/2) = m(pi-theta)/m(theta)` could hold only
at isolated T (atom positions move with T, masses are multiples of 1/4), i.e. on a codimension >= 1 set of times. As
T -> inf the four atoms move quasi-periodically (frequencies = level differences of two 4x4 Hamiltonians): no
limit, and the Cesaro law is the push-forward of Haar measure on that torus. The first-order resonance manifold of
the chain is `|h_0| = |h_z +- J_zz|` (site 1 has ONE neighbour; the ring's is `{h_z, h_z +- 2J_zz}`, BRIEF C1.1).
**Status.** PROVED (structure, N-independence; strong fails and coverage fails at each T); NUMERICAL (the Cesaro law is not Born).
**Proof.** `Z_{i>=2}` commutes with Z fields, ZZ bonds and the qubit-site-1 couplings. So `H = (+)_{z} [H_{z_2} +
E(z)]`, where `E(z)` is a scalar per configuration of sites >= 2. Each block contributes `e^{-iE T}` times the
2x2 pencil of `H_{z_2}`, and each z_2 value carries 2^{N-2} copies. QED.
**Numerical check** (`ising.py`; `bk.build_H('chain', N, p)`, SPEC). The distinct roots at N = 2, 3, 5 are identical
(4 of them) at T = 3.3 and 57 in all 5 cases. Cesaro-type law: 20000 uniform random T in [0, 1e4], i.e. 80000 atoms,
whose exact-Born i.i.d. floor is S ~ 0.972. There is no order issue, since the law is N-independent.
| case (SPEC) | lab-z S / coverage | h0-basis S / coverage | <sin^2(theta/2)> (h0 basis) |
|---|---|---|---|
| J_zz=1, h_z=0.7, h_0z=0.9, g_x=0.1 (off resonance) | 0.061 / 16 | 0.061 / 16 | 0.0037 |
| same, h_0z = 1.7 = h_z+J_zz (resonant) | 0.557 / 100 | 0.501 / 100 | 0.024 |
| tilted h0=(0.3,0,0.9), g=(0.1,0.05,0.03), off res. | 0.448 / 54 | 0.035 / 12 | 0.0023 |
| tilted, |h0| = 1.7 (resonant) | **0.858** / 100 | 0.557 / 100 | 0.014 |
The lab-z 0.858 is kinematic: the free-precession cone about ĥ0, which is 19.5 deg from z, together with resonant
tails; in the ĥ0 basis the same law is a polar cap. f90 = 0.86-1.0. **Lesson:** a lab-basis S near 0.86 with full
coverage can come from a law that is a cap in its own fixed-point basis.
**Failure modes.** A Cesaro law on a torus of two 4x4 problems could be tuned to special values. Nothing selects
Born, and the per-time law is atomic.

### P4.7 Matchgate chain: exact one-radius formula, unconditional N-first limit, three late-time regimes
**Statement.** Take the chain with only `{h_z, J_xx, J_yy, g_x, g_y, h_0z}`, which is Gaussian. Write
`H = (i/4) gamma^T A gamma` (Jordan-Wigner with the qubit as site 0, `gamma_1 = X_0, gamma_2 = Y_0`) and
`B(T) = [e^{AT}]_{qubit block}` (2x2 real). Decompose `p = (B11+B22)/2`, `q = (B21-B12)/2` (rotation part) and
`r = (B11-B22)/2`, `s = (B12+B21)/2` (reflection part). Then, for every N >= 1 and T, the lab-z outcome-0 roots are
exactly two points `+-lambda*`. They have the same polar angle and antipodal azimuths, each has kernel dimension
2^{N-1}, and
`tan^2(theta*/2) = |r + i s| / |p + i q|`.
(i) The N-first limit exists **unconditionally**. B(T) is an entry of the single-particle propagator, which converges
superexponentially in N at fixed T. (ii) Late-time behaviour follows from the spectral decomposition of the qubit
Majorana block of iA on the half-line:
- (ii-a) **A single Majorana zero mode with weight u on the qubit Majoranas**, and no other qubit-weighted point
  spectrum, gives `B -> u u^T` (plus decaying terms), hence `|r+is| = p` and `theta* -> pi/2`. This is an equatorial pair, a vacuous weak pass, and strong fails.
- (ii-b) **Non-zero-energy bound states only** (qubit level outside the band) keep B quasi-periodic and non-decaying.
  theta* then stays in a small polar cap (degenerate).
- (ii-c) **Purely a.c. spectrum.** Both parts decay as T^{-3/2} (band edges), their ratio becomes a quasi-periodic
  function, and theta*(T) has no limit. It has a stationary O(1) distribution, and the pooled law is not Born.
**Status.** PROVED: the formula, the multiplicities, (i), (ii-a) and (ii-b). HEURISTIC plus NUMERICAL: (ii-c), whose
asymptotics are a stationary-phase statement.
**Proof of the formula.** Outcome 0 means `Z_0 U|psi,D> = U|psi,D>`, i.e. `Z_0(T)|psi,D> = |psi,D>` with
`Z_0(T) = -i gamma~_1 gamma~_2` and `gamma~_a = sum_b O_ab gamma_b` for `O = e^{AT}`. Set `f = (gamma~_1 + i gamma~_2)/2`.
Then `f^dag f = (1 - Z_0(T))/2`, so the condition is `f|psi,D> = 0` with `f = w_1 X_0 + w_2 Y_0 + Z_0 (x) F`,
`w_b = (O_1b + i O_2b)/2` and `F = sum_{b>=3} w_b gamma'_b`. The `|0>` and `|1>` components give
`F|D> = -(w_1 - i w_2)(beta/alpha)|D> = (w_1 + i w_2)(alpha/beta)|D>`. Hence `lambda^2 = (beta/alpha)^2 =
-(w_1+iw_2)/(w_1-iw_2)`, and D must be an eigenvector of F. Now `F^2 = sum_{b>=3} w_b^2`, a scalar, and
`sum_all w_b^2 = (|O_1|^2 - |O_2|^2 + 2i O_1.O_2)/4 = 0` by orthogonality. Consistency is therefore automatic. F is
traceless with `F^2 = -(w_1^2+w_2^2) != 0`, so it has two eigenspaces of dimension 2^{N-1}, one per sign of lambda.
The last step is the algebra `w_1 +- i w_2 = (r + is), (p + iq)`. When `w_1^2 + w_2^2 = 0`, F is nilpotent and the
pencil is defective; the charge-graded slice (`r = s = 0`, `lambda = 0`, BRIEF CG) is an instance. (ii-a): the
omega = 0 spectral projector restricted to the qubit block is `u u^T` with u real, and `p = |u|^2/2 = |(u_1+iu_2)^2|/2 =
|r+is|`. The a.c. part tends to 0 by Riemann-Lebesgue. QED.
**Numerical check** (`mg.py`, `mg_long.py`, `mg.json`). Formula vs `bk.roots` at N = 3, 5 and T = 0.7, 3.1: every root
sits at the formula angle to 1e-6 in 3 cases. SPEC order: single-particle N = 1500/2000/3000/4000, identical to
<= 1.7e-8, with light cone `2 v T < N` (v <= 0.8). Base SPEC parameters: `h_z=1, J_xx=0.3, J_yy=0.1, g_x=0.1,
g_y=0.05`; the band is 2|h_z +- (J_xx+J_yy)cos k|-type, roughly [1.2, 2.8].
- MG-res, `h_0z = 1.0` (qubit level in the band, no bound state): theta*/pi has mean 0.236 and 5-95% range
  [0.08, 0.54], identical over [200,400], ..., [1600,2000]. |rot| and |refl| decay with exponents -1.49 and -1.53.
  Pool over T in [1000,2000] (4001 times): S = 0.669 with coverage 100, against an exact-Born floor of 0.875 at the
  same n. Not Born.
- MG-gap, `h_0z = 2.0` (bound state): theta*/pi in [0, 0.023] for all T <= 600; S = 0.009, coverage 6.
- MG-topo, `h_z=0.2, J_xx=0.6, J_yy=0.2, h_0z=0.5` (ordered phase, edge Majorana): |rot| = |refl| = 0.0163 saturate,
  and theta*/pi has quartiles [0.499, 0.5006]. Equatorial, S = -0.475 (coverage 36).
**Correction to BRIEF (Tier 6 "Settled", `BRIEF.md:431-432`).** The claim "T -> inf law is delta_{pi/2} if the
boundary return decays" is **REFUTED**. A decaying return (ii-c) gives a non-degenerate, non-convergent, non-Born
oscillation. The equatorial delta comes instead from a Majorana zero mode (ii-a). Bound states at non-zero energy give
a cap (ii-b).
**Intuition.** theta* measures the ratio of the "anomalous" (pairing) to the "normal" part of the qubit Majorana
return amplitude. Nothing in a free-fermion chain calibrates that ratio to Born.

---
## Part (c): the generic interacting chain as an impurity problem

Setting. `H = H_q + H_D + V`, with `H_q = |h0| h0hat.sigma_0` and `V = sum_a g_a sigma_0^a sigma_1^a`. Take
`U = e^{-iH_0 T} U_I(T)` with `H_0 = H_q + H_D`, and output basis n. Define `chi = e^{i H_q T}|-n>`,
`K_a = <chi|U_I|chi_perp>` and `K_b = <chi|U_I|chi>` (detector operators). The kinematic point is
`Omega_kin(T) = Bloch(chi_perp) = u_q(T)^dag n`, and in the h0hat basis it is `Omega_kin = h0hat` for all T.

### P4.8 Exact transfer-operator form and the first-order impurity law
**Statement.** (i) The outcome-0 roots are exactly `psi_j ∝ chi_perp + x_j chi`, with `x_j` in spec(X), where
`X = -K_b^{-1} K_a` (when K_b is invertible), with geometric multiplicities as kernel dimensions. The polar angle
gamma from Omega_kin satisfies `tan(gamma/2) = |x|`, so the law is the push-forward of the eigenvalue distribution of X
under the stereographic chart centred at the kinematic point. (ii) `X = i F*(T) + O(g^2)` with
`F*(T) = sum_a g_a int_0^T <chi|sigma_{0,I}^a(s)|chi_perp> sigma_{1}^a(s) ds`. In the h0hat basis this is
`F*(T) = int_0^T e^{-2i|h0|s} e^{iH_D s} B_e e^{-iH_D s} ds`, `B_e = sum_a g_a (e_-)_a sigma_1^a`,
`e_- = <-h0hat|sigma|+h0hat>`. Equivalently `(F*)_mn = (B_e)_mn (e^{i Delta_mn T} - 1)/(i Delta_mn)`, with
`Delta_mn = E_m - E_n - 2|h0|` (H_D eigenbasis; this is the chain analogue of Theorem I's filter). (iii) N-first
(conditional): at first order the rescaled N-first law is the Brown measure of `i F*^inf(T)` in the tracial half-chain
algebra.
**Status.** (i) PROVED (linear algebra: `M(a chi_perp + b chi) = e^{-iH_D T}(a K_a + b K_b)`). (ii) PROVED at fixed N and
T as g -> 0 (Dyson expansion; eigenvalue continuity; for defective or non-normal F* the O(g^2) root error carries
eigenvalue condition numbers). (iii) PROVED-CONDITIONAL on H1-type small-singular-value control (P4.5 remark).
**Numerical check** (`fstar.py`; slow detector R/G, N = 6, g-scale 0.02, h0hat basis, T = 2, 4). The roots give
`sum tan^2(gamma/2)` = 7.496e-5, 2.541e-4, 2.043e-5, 2.198e-5, against `sum |f|^2` = 7.492e-5, 2.541e-4, 2.043e-5, 2.196e-5.
The sorted radii agree to 0.15-0.6% of max|f|.

### P4.9 Schur bound: at first order, root spreading <= qubit depolarization
**Statement.** At first order in g, `<tan^2(gamma/2)>_roots = <|f|^2> <= tau(F*^dag F*) = (1 - |w|)/2 + O(g^3)`. Here w is
the p1 vector (`p1(Omega) = (1 + w.Omega)/2`, the reduced-dynamics Bloch contraction for an infinite-temperature
detector). Equality holds iff F* is normal. The ratio `eta = <|f|^2>/tau(F*^dag F*)` in [0,1] measures non-normality.
**Status.** PROVED (Schur's inequality `sum|lambda_j|^2 <= ||F||_HS^2`). Also `p1(Omega_kin) = tau(K_a^dag K_a) =
tau(F^dag F) + O(g^3)`, and since p1 is exactly affine in Omega, `p1(Omega_kin) - min p1 = O(g^4)`.
**Meaning.** The golden-rule (T1) depolarization is only an UPPER bound on how far the roots move. Non-normality can
leave the roots at the kinematic point while the qubit relaxes.

### P4.10 In the fixed-point basis only the transverse spectral weight at 2|h0| moves roots; pure dephasing is inert
**Statement.** The longitudinal part of the coupling (`h0hat.sigma_0 (x) B_par`) drops out of F* because
`<-h0hat|h0hat.sigma|+h0hat> = 0`. `tau(F*^dag F*) = int (dw/2pi) S_e(w) 4 sin^2((w - 2|h0|)T/2)/(w - 2|h0|)^2`, which tends
to `T S_e(2|h0|)`, with `S_e` the infinite-temperature boundary spectral function of `B_e`. So at first order, in the
h0hat basis, **T2-type (pure dephasing) processes do not move roots at all**. Only T1-type spectral weight at the
qubit frequency does, and that weight is further suppressed by eta (P4.12). In a lab basis n != h0hat, dephasing
spreads the cloud along the cone about h0hat, which is kinematic: B1 = 1/|cos angle(h0hat, n)| (BRIEF cone lemma).
**Status.** PROVED (first order; exact for `[H, h0hat.sigma_0] = 0` by the QND-cone lemma).
**Time scales.**
- With `tau(F^dag F) = p1(Omega_kin) ≈ Gamma_down T`, `Gamma_down = S_e(2|h0|)` (normalization `int S dw/2pi = tau(B^dag B)`).
- At infinite temperature `Gamma_up = Gamma_down`, so `1/T1 = 2 S_e(2|h0|)`.
- `1/T2 = 1/(2 T1) + Gamma_phi`, with `Gamma_phi ∝ g_par^2 S_par(0)` from the longitudinal part.
- Only `T1` enters the fixed-point-basis law, and even it enters only through the non-normal part (P4.12).
- Check: for R at s = 1 the first-order slope of `tau(F^dag F)` is about 0.11, which gives `T1 ≈ 4.5`. The fit
  `(1-|w|)/2 = D_inf(1 - e^{-T/T1})` to the full numerics (P4.13) gives `T1 ≈ 3.4`.

### P4.11 Gapped vs gapless boundary spectral function
**Statement.** If `Delta = dist(2|h0|, supp S_e) > 0` (gapped), then `tau(F*^dag F*) <= 4 tau(B_e^dag B_e)/Delta^2` uniformly in
T. The first-order cap radius is then `O(g/Delta)` for all T: no relaxation, a dressed bound state, and a cap that
tends to delta as g -> 0 (degenerate pass). If `S_e(2|h0|) > 0` (gapless), `tau(F*^dag F*) ~ T S_e(2|h0|)` grows linearly
(golden rule).
**Status.** PROVED (the filter bound `|(e^{iDT}-1)/(iD)|^2 <= 4/D^2` in the 2-norm). "Gapped" is only approximate for an
interacting chain at infinite temperature, where spectral tails decay fast but are nonzero. The leakage rate is then
set by the tail, so relaxation is prethermal-slow (HEURISTIC).
**Numerical check** (`spectral.py`, N = 9, broadening 0.05; `fstar.py`). The slow detector's boundary spectral
functions have a transverse band 1.0 <~ w <~ 3.2 around `2|h_D| = 2`, a longitudinal peak at w ~ 0, and S < 5e-3 for
w > 3.4. Configuration R (`|h0| = 1`, 2|h0| = 2 in the band) gives tauFF = 0.029, 0.102, 0.335, 0.910, 2.08, 3.03, 3.81,
5.46 at T = 1, 2, 4, 8, 16, 24, 32, 48 (N = 10, 11), roughly linear with slope about 0.11. Configuration G
(`|h0| = 2.5`, 2|h0| = 5 outside) gives tauFF = 0.012, 0.003, 0.006, 0.007, 0.006 at T = 1-16: bounded.
**Connection to the Markovianity study.** The saturating memory of the gapped chain (`N_BLP` saturates at 0.23,
digest_numerics.md:293, citing `MARKOVIANITY_BORN_2026-09-20.md:169-230`) is this bound-state regime. It keeps the
law at the cap, which is consistent with "memory is not a sufficient driver of Born".

### P4.12 Generalized charge grading, and why weak-coupling relaxation does not spread the roots
**Lemma (GCG).** Suppose `[H, c (a.sigma_0) (x) I + I (x) Q_D] = 0` for some real c != 0, a unit a and ANY Hermitian
Q_D on a finite-dimensional detector. Then for every T, in output basis a, `det M0(psi) = kappa <-a|psi>^d`: all d
outcome-0 roots sit at +a (algebraically; they are generally defective).
**Status.** PROVED.
**Proof.** U preserves the eigenspaces of `K = c a.sigma (x) I + I (x) Q_D`. Hence `U_{-+} = <-a|U|+a>` maps the
`Q_D = q` eigenspace to `q + 2c`, and `U_{--}` preserves q. Order spec(Q_D) monotonically (the shift by 2c cannot
cycle on a finite set). Then `M0 = alpha U_{-+} + beta U_{--}` is block-triangular with diagonal blocks
`beta U_{--}^{(qq)}`. QED.
**Special cases.** QND (`Q_D = 0`, the BRIEF QND-cone lemma at n = a); the repository CG theorem (`a = z`,
`Q_D = +-Q`); and, new, **energy grading**: `Q_D = H_D`, `a = h0hat`, `c = |h0|`, i.e. any coupling that conserves the
unperturbed energy `H_q + H_D`.
**Numerical check** (`gcg_check.py`). Six random instances: d = 8, random Q_D containing 2|c|-ladders rotated by a
random unitary, and a random K-commuting H with off-diagonal norm 9-11. `|det M0(psi)|/|<-a|psi>|^d` is constant to
<= 6e-14. The QZ roots lie within 0.02 deg of +a (defective scatter).
**Consequence: secular suppression.** HEURISTIC, with exact first-order and numerical support. The golden-rule
(secular) part of the weak-coupling dynamics, which is what produces T1 relaxation, commutes with `H_q + H_D` and is
therefore energy-graded. By GCG it leaves every root at the kinematic point h0hat. Roots move only through
non-secular (off-shell) terms and the finite-time energy blur ~1/T. At first order, `F*(T) = T Pi_{2|h0|}(B_e) +
(bounded off-shell part)`, where the resonant part raises H_D-energy by exactly 2|h0| and is nilpotent at finite N.
The measured non-normality index is:
| T | 1 | 2 | 4 | 8 | 16 | 24 | 32 | 48 |
|---|---|---|---|---|---|---|---|---|
| eta (chain R, N=6..11, identical to <=3%) | 0.202 | 0.029 | 0.030 | 0.014 | 0.008 | 0.006 | 0.005 | 0.004 |
| <|f|^2> = first-order root spread | 0.0059 | 0.0030 | 0.010 | 0.013 | 0.017 | 0.018 | 0.019 | 0.022 |
| tau(F^dag F) = first-order depolarization | 0.029 | 0.10 | 0.34 | 0.91 | 2.08 | 3.03 | 3.8 | 5.5 |
In words, eta ~ 1/T. The first-order root spread grows about logarithmically, while the depolarization grows
linearly. The disc test `<|f|^4>/<|f|^2>^2` = 1.0-1.4 (disc 4/3, Gaussian 2) shows a ring- or disc-like eigenvalue cloud.
In the gapped G case, eta is 0.03-0.23 but tauFF is bounded.
**Failure of classical-noise reductions for the chain.** PROVED by counterexample. In the CG/GCG classes (e.g. a U(1)
chain with flip-flop coupling, `g_x = g_y`) the bath is two-point-"classical" at infinite temperature, because
`tau([B(t), B]) = 0`, and it relaxes the qubit at the golden-rule rate. Yet the law is exactly delta. Any reduction
driven by the tracial two-point function (classical Gaussian noise) instead predicts isotropic transverse diffusion.
In the h0hat basis that is the axisymmetric S^2 heat kernel `e^{s Delta} delta_{h0hat}` with `s = D_perp T/2`, because
`L_3^2` annihilates axisymmetric functions. **That family is never Born.** An axisymmetric law `sum_l a_l P_l` is Born about n iff `rho0/(1+u)` is even. The first two
conditions are `a_1 = a_0 + (2/5)a_2` and `a_3 = (3/5)a_2 + (4/9)a_4`. For the heat kernel (`a_l ∝ (2l+1)x^{l(l+1)/2}`,
`x = e^{-2s}`) the first is exactly the B1 = 1 condition `3x = 1 + 2x^3`. At that point the second fails:
`7x^6 = 0.017`, against `3x^3 + 4x^10 = 0.147`. The family tends to uniform. It crosses B1 = 1 once, at `s* = 0.5025` (`<P1> = (sqrt3-1)/2`), where S = 0.918 on 100k samples against an
exact-Born floor of 0.975 (`heatkernel.py`). So the BRIEF candidates C1.2/C6.1 (a classical reduction and a flow to
uniform on the gapless side) are wrong for the chain in the secular regime.
**Ring caution (for WP1-3).** The same first-order index for the 1/sqrtN collective ring with the same detector is
eta = 0.036, 0.010, 0.0075 at T = 4, 8, 16, identical at N = 6, 8, 10 (`fstar2_ring.log`). At accessible N the ring's
transfer operator is as non-normal as the chain's; nothing yet shows the classical (normal, eta -> 1) limit that C1.2
assumes.

### Late-time predictions in the self-consistent basis (question (c))
- **Gapped** (2|h0| outside supp S_e). A cap about `n* = h0hat + O(g)` with radius `O(g/Delta)`, quasi-periodic in T
  with no limit, and a cap as its Cesaro law. Degenerate pass, not Born. [PROVED at first order; HEURISTIC beyond,
  since interacting tails give prethermal-slow leakage.]
- **Gapless** (2|h0| inside). The qubit relaxes on T1, but the law stays a cap about n* far beyond T1, because the
  secular part is energy-graded. [first order PROVED + NUMERICAL, all orders NUMERICAL in P4.13]. As T -> inf at fixed
  g (SPEC order) the two candidates are (A) a cap whose radius grows only logarithmically, or (B) at `T >> T1/eta`,
  non-secular processes spread it toward uniform (ratio 1/2). **Neither is Born.** (A) fails coverage and (B) gives
  R = 1/2. [CONJECTURE; which of the two holds is OPEN.]
- The candidate "latitude/one-radius" law occurs only in the matchgate class (P4.7), and "uniform 1/2" only under
  mixing that no computation here reaches. "Born" would need `<P1> = 1/3` and `<P2> = 0` with full coverage in an
  attracting fixed-point basis, and no mechanism found here supplies it.

---
## Part (d): numerics in the SPEC order

### Disclosure (applies to P4.13-P4.14)
- **Hamiltonian** (SPEC positive convention, open chain, builder `bk.build_H('chain', N, p)`, exact dense evolution):
  `H = h0 (sin20 X_0 + cos20 Z_0) + sum_{i=1}^N (0.6 X_i + 0.8 Z_i) + sum_{i=1}^{N-1} (0.15 X_iX_{i+1} + 0.10 Y_iY_{i+1} +
  0.20 Z_iZ_{i+1}) + s (0.15 X_0X_1 + 0.10 Y_0Y_1 + 0.08 Z_0Z_1)`. The two configurations are h0 = 1.0 ("R": `2|h0| = 2`,
  inside the boundary band) and h0 = 2.5 ("G": `2|h0| = 5`, outside). The coupling scale is s in {0.5, 1, 2}.
- **Zero parameters.** `h_y = h_0y = 0` makes H real, which gives an antiunitary symmetry: fixed-input roots are the
  complex conjugates of forward ones (BRIEF 1.8). It creates **no conserved quantity**. Pi parity is broken by
  `h_0x, h_x`, X0 by `h_0z`, U(1) by `J_xx != J_yy` and the tilted field, and `Z_{i>=2}` by `h_x, J_xx, J_yy`.
- **Coupling scaling.** Chain, O(1) in N (`SPEC.md:701-707`).
- **Perturbative gate: VIOLATED ON PURPOSE (labelled separate regime).** `max|g|/min|non-g| = 1.5 s` against the code
  gate 0.1. Under the gate, `T1/T_LC ~ (W/g)^2 v/(W N)` is scale-invariant and about 10^2 at N = 10, so T1 can never
  enter the light-cone window at N <= 10. This is the same obstruction BRIEF BC-C found for screen_00 (N ~ 500). Here
  `g/|h0| = 0.15 s` (R) and `0.06 s` (G). The golden-rule parameter is Gamma/bandwidth ~ 0.05 at s = 1. The first-order
  law (P4.8) reproduces the full numerics at s = 1 (below), so the regime is perturbative for the roots.
- **Times and T/t_H.** Single instantaneous T in {1, 2, 3, 4, 6, 8, 12}, with **no pooling** in the SPEC-order runs.
  They straddle the measured T1: with `(1-|w|)/2 = D_inf (1 - e^{-T/T1})`, T1 is about 14 (s = 0.5), 3.4 (s = 1) and
  about 1 (s = 2). All T lie inside the numerically verified light-cone window. `T/t_H <= 0.08` (N = 8) and `<= 0.02`
  (N = 10), with `t_H = 2pi 2^{N+1}/W` = 57 / 178 / 590 at N = 6 / 8 / 10 for R.
- **N-ladder** 4, 6, 8 for all (h0, s); N = 10 for s = 1 at T = 2, 4, 6, 8, 12.
- **Output basis.** The self-consistent basis n*, solved by Newton for `Phi_res(n) = n` (`Phi_res` = normalized
  resultant of the outcome-0 cloud in basis n; residual 0.000 deg in every row). The dipole-based Phi is
  ill-conditioned on near-point clouds, and plain Phi-iteration of a near-rotation never converges. The dipole-map
  step at n* (0-5 deg, up to 28 deg on the tightest clouds) is recorded in the jsonl files. Lab-z statistics are
  reported next to it, with `B1_kin = 1/cos 20 = 1.064`.
- **Scripts/data**: `main.py`, `ladder.sh`, `main_*.jsonl`, `summarize.py` -> `summary_tables.md`; `l1_cauchy.py`.

### P4.13 SPEC-order law: light-cone saturation, then a cap that does not relax with the qubit
**Statement (NUMERICAL).** For the slow XYZ chain at weak coupling:
(i) **Light-cone saturation.** The fixed-T law is N-independent between N and N+2. At s = 1 the moments `P_l(n*.Omega)`,
l <= 3, differ between N = 6 and 8 by <= 4.5e-4 for T <= 12, and agree between N = 8 and 10 to 4 digits at
T = 2-12. The potentials are Cauchy in L1, faster than exponentially (`l1_cauchy.py`, lab basis):
`||L1^{(6)}-L1^{(4)}||_1, ||L1^{(8)}-L1^{(6)}||_1` = 3e-8, 7e-13 (T=2); 3e-5, 1e-8 (T=4); 6.5e-3, 5.9e-5 (T=8);
4.1e-2, 1.7e-3 (T=12). This is the behaviour P4.5 predicts, and saturation comes much earlier than the rigorous LR
bound would give.
(ii) **The law in the self-consistent basis is a cap about `n* ≈ h0hat` (0.1-7 deg) at every T.** It stays a cap even
at `T ≈ 3.5 T1` (s = 1) and `≈ 10 T1` (s = 2), where the qubit is largely depolarized.
Key rows (R, s = 1, N = 8, identical at N = 10):
| T | T/T1 | <sin^2(gamma/2)> | (1-|w|)/2 | ratio | res | f90 | coverage | S (n*) | B1 (n*) | FR = -<x>/var x | Jensen gap G | lab S / cov / B1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.3 | 0.0059 | 0.028 | 0.21 | 0.988 | 1.00 | 4 | 0.019 | refused | 428 | 0.10 | 0.081/8/1.279 |
| 4 | 1.2 | 0.0115 | 0.251 | 0.046 | 0.977 | 1.00 | 8 | 0.047 | 1.025 | 43 | 0.60 | 0.101/12/1.040 |
| 8 | 2.4 | 0.0116 | 0.356 | 0.033 | 0.977 | 1.00 | 18 | 0.084 | 1.025 | 6.5 | 0.90 | 0.284/28/1.050 |
| 12 | 3.5 | 0.0109 | 0.364 | 0.030 | 0.978 | 1.00 | 22 | 0.111 | 1.023 | 7.4 | 0.98 | 0.345/42/1.058 |
Reference values for the uniform-prior Born law `(1+cos)/4pi`: `<sin^2> = 1/3`, res = 1/3, and
`FR = -E[x]/Var[x] = 0.873` for `x = log tan(theta/2)` (computed by quadrature; FR = 1 holds only for Gaussian x).
At the same budget (d = 256 roots) i.i.d. Born gives S ≈ 1 - 7.9/16 = 0.51 at full coverage. Non-uniform-prior Born
laws can have any res; that is why coverage is the decisive column. G (gapped) at s = 1: `<sin^2> = 0.0007-0.0012` for all T, coverage 4-6, depolarization <= 0.012.
The s = 2 extreme is T = 8: `<sin^2> = 0.038`, res 0.924, f90 0.75, coverage 34, S = 0.30. **Nothing is Born-like.**
Every row fails coverage (<= 36/100), has res >= 0.84 (a near-point) and FR >> 1. The B1 values near 1 are vacuous
(near-point clouds, BRIEF 1.4). Full tables: `summary_tables.md`.
**Log-radius statistics and the fluctuation relation** (`x = log tan(gamma/2)` about n*; N = 8). Weak Born requires
`P0(-dx) = e^{2x} P0(dx)`, hence the integral form `E[e^{2x}] = E[tan^2(gamma/2)] = 1`. The uniform-prior Born law has
`E[x] = -0.50`, `Var[x] = 0.57`. Measured values:
| case | E[x] | Var[x] | E[tan^2] |
|---|---|---|---|
| R, s = 1, T = 1-12 | -2.3 to -2.6 | 0.006-0.37 | 0.006-0.012 |
| G, s = 1 | -3.6 to -4.0 | | 0.0004-0.0008 |
| R, s = 2 | -1.8 to -2.0 | | 0.026-0.051 |
| R, s = 1, reverse order | -2.20 | 0.78 | 0.17 |
The integral fluctuation relation fails by 1-3 orders of magnitude in the SPEC order.
(iii) **Perturbative structure.** `<sin^2(gamma/2)>` scales as `g^2 phi(T)`, not as a function of `g^2 T` (van Hove).
At T = 1-8: s = 0.5 gives 0.0015, 0.0008, 0.0026, 0.0033 = (1/4) x s = 1; s = 2 gives 0.025, 0.019, 0.047, 0.038 ≈ 4x.
It matches the first-order transfer-operator prediction `<|f|^2>` of P4.12 (0.0059, 0.0030, 0.010, 0.013 at
T = 1, 2, 4, 8) while the reduced dynamics is non-perturbative (first-order tauFF = 0.91 against the actual 0.356 at
T = 8). **The roots are perturbatively controlled after the qubit has depolarized**, which is the secular
suppression of P4.12 seen at all orders. The Schur ratio `<sin^2>/((1-|w|)/2)` is 0.02-0.05 (R) and 0.1 (G).
(iv) **Jensen gap.** G grows to O(1) (0.98 at T = 12) while the law is a cap. **An O(1) Jensen gap is not evidence of
Born**: it tracks depolarization (`log p1 -> log 1/2`), not root spreading. This complements BRIEF 2.1(v), where an
O(1) gap is only necessary.
**Status.** NUMERICAL (finite N, but saturated in N at fixed T; finite T <= 12).
**Failure modes.** (1) The window ends at about 3.5 T1 (s = 1) and 10 T1 (s = 2). Candidate (B) of the late-time
conjecture, eventual spreading at `T >> T1/eta`, cannot be excluded numerically: at s = 1, `T1/eta(12) ~ 3.4/0.006 ~ 600`.
(2) The regime violates the repository's code gate (by construction; see the disclosure).

### P4.14 SPEC order vs reverse order
**Statement (NUMERICAL).** In the gapless case the two orders differ and the reverse-order law depends on N. In the
gapped case they agree.
The reverse order uses the canonical 6-time pool `T = 1000..10000` (repository TIMES in units 1/min|non-g|), with
`T/t_H` = 17-174 (N = 6) and 6-56 (N = 8). This is pooled, as the campaigns do, and is neither instantaneous nor Cesaro.
| config | order | N | <sin^2> (n*) | res | f90 | coverage | S (n*) | lab S / coverage / B1 |
|---|---|---|---|---|---|---|---|---|
| R, s=1 | SPEC, T=12 | 6, 8, 10 | 0.0109 | 0.978 | 1.00 | 22 | 0.111 | 0.345 / 42 / 1.058 |
| R, s=1 | reverse | 6 | 0.0281 | 0.944 | 0.88 | 62 | 0.246 | 0.448 / 96 / 1.069 |
| R, s=1 | reverse | 8 | 0.0425 | 0.915 | 0.84 | 98 | 0.317 | 0.652 / 100 / 1.006 |
| G, s=1 | SPEC, T=12 | 6, 8, 10 | 0.0007 | 0.9987 | 1.00 | 6 | 0.009 | 0.248 / 26 / 1.061 |
| G, s=1 | reverse | 6, 8 | 0.0007 | 0.9986 | 1.00 | 6-8 | 0.009-0.017 | 0.395-0.420 / 48-54 / 1.064 |
Gapless: the reverse-order cap is 2.6x (N = 6) and 3.9x (N = 8) broader in `<sin^2>` and grows with N. Its lab-z S
rises 0.45 -> 0.65 from N = 6 to 8, the same pattern as the campaign's "0.557 -> 0.707 with N". The SPEC-order law
is N-independent. Gapped: the two orders agree to 4 digits in the n* basis (a bound state has nothing to
equilibrate), and the lab-z differences come only from pooling six kinematic points on the cone.
**Status.** NUMERICAL.
**Consequence.** A rising lab-z S under the canonical pool with growing N is a reverse-order phenomenon. It does not
indicate an approach to a SPEC-order Born limit, and in the fixed-point basis even the reverse-order law remains a
cap here.

**Preferred axis (addresses the GOAL note).** The self-consistent axis is `n* = h0hat + O(g)`, which is kinematic.
Proof: in the h0hat basis the kinematic point is h0hat for every T (P4.8), so `Phi(h0hat) = h0hat + O(g)`. Numerically
the offset is 0.1-7 deg (up to 33 deg only at s = 2, T = 3, where f90 = 0.38). The offset changes sign with T and
lies mostly **away from** the detector field `h_D` (component along `h_D - h0hat`: -6.9 ... +0.8 deg at s = 1).
The detector enters only as an O(g) T-dependent dressing. The chain data therefore support "qubit self-field axis
(kinematic)", not "detector-field axis".

---
## Part (e): reinterpretation of the chain campaign (0.72 plateau, 0.12 deficit, screen_00)

### P4.15 The campaign numbers are reverse-order, lab-basis objects; the SPEC-order screen_00 law is a cap about h0hat
**Statement.**
- (i) Every screen_00 campaign number is a reverse-order, lab-basis quantity.
  - The window is T = 100-1000 with `t_H` = 60/193/651 at N = 8/10/12 (BRIEF 4). My P4.1 check shows that screen_00's
    operator-norm light cone already exceeds 9 sites at T = 1-2.
  - The cloud is pooled over six times and read in the lab z basis. In that basis the kinematic precession cone about
    h0hat (47.1 deg from z, `B1_kin = 1.469`) spreads the six time-slices over lab polar angles 0-94 deg.
  - Hence the 0.72 plateau, the 0.12 deficit against same-budget Born and the rise of S with N measure how a finite,
    equilibrated chain smears a cap along a kinematic cone. None of them approximates the SPEC-order law.
  - In the campaign's own fixed-point basis the same clouds are caps: f90 ≈ 1, S = 0.13-0.35 (BRIEF 4, row 6.5phi).
- (ii) The slow-detector analogue reproduces the pattern under the SPEC/reverse contrast (P4.14).
  - Reverse-order lab-z S rises 0.45 -> 0.65 with N (N = 6 -> 8), while the SPEC-order law is N-independent.
  - In both orders the n*-basis law is a cap.
- (iii) Prediction for screen_00 in the SPEC order (first order, `screen00_fstar.py`, SPEC signs, h0hat basis).
  - The qubit frequency `2|h0| = 5.905` lies inside the boundary band of this fast detector (`S_aa(5.9)` = 0.37, 0.23,
    0.37 for a = x, y, z; N = 9, broadening 0.1), so screen_00 is **gapless**.
  - tauFF = 0.0097, 0.020, 0.041, 0.082, 0.161 at T = 2, 4, 8, 16, 32 (N = 8 and 10 agree to 2%). This is linear, so
    `T1 ~ 10^2`: the campaign window straddles T1, but in the reverse order.
  - The first-order root spread is only `<|f|^2>` = 0.0007, 0.0010, 0.0016, 0.0024, 0.0037, with eta = 0.07 -> 0.02.
  - So the SPEC-order screen_00 law at every T is a **tight cap about `n* ≈ h0hat`**: `<sin^2(gamma/2)> ~ 10^-3 - 10^-2`,
    which is degenerate and not Born.
  - Its lab-z image at a single T is a cap around `u_q(T)^dag z` on the kinematic cone.
- (iv) Axis and B1 readings.
  - The campaign's "axis 1.5-3 deg from h0hat" is this kinematic fixed point.
  - B1 = 1.302/1.150/0.880 corresponds to `B1/B1_kin` = 0.886/0.783/0.599. This is an N-dependent reverse-order
    departure from the cone value, and its crossing of 1 between N = 10 and 12 is codimension-one (BRIEF 1.4).
  - The N = 10-12 flatness of the deficit coincides with T/t_H crossing 1 (BRIEF 5.2.5), i.e. with a change of order,
    not with convergence.
**Status.** (i), (ii) and (iv) are NUMERICAL, using BRIEF data plus P4.1 and P4.14. (iii) is PROVED at first order, with
NUMERICAL values of eta and tauFF; at all orders it rests on the P4.13 evidence that the first-order transfer operator
predicts the roots after depolarization.
**Failure mode.** (iii) is first order at T <= 32. screen_00 has g/|h0| ~ 0.04, smaller than my s = 1 runs, where the
first-order law was quantitatively accurate. Candidate (B) of P4.12 (eventual non-secular spreading at T >> T1/eta)
is untested for screen_00 as well.

---
## Part (f): ring vs chain

### P4.16 Comparison theorem (composite)
**Statement.**
- (1) **Shared exact structure** [PROVED, geometry-independent]. Antipodality; the QND-cone lemma; the GCG lemma
  (P4.12); the exact transfer-operator form with its first-order law (P4.8); and the Schur bound (P4.9). All hold for
  the ring (collective `L_a = sum_i sigma_i^a` with any scaling) and for the chain (`sigma_1^a`). In both geometries the
  weak-coupling self-consistent axis is `h0hat + O(g)` (kinematic). The law in that basis is the stereographic image of
  spec(X), with `X = i F* + O(g^2)`.
- (2) **Chain-specific advantages.**
  - (a) No coupling-scaling hypothesis is needed, and the N-first law is non-trivial at O(1) coupling. The 1/N ring is
    trivialized instead, since its HS norm is `|g|/sqrt N -> 0` (BRIEF 1.2).
  - (b) The N-first limit exists by the light cone, with a superexponential Cauchy rate, modulo the light-cone-local
    tail hypothesis H1 (P4.5). It is saturated numerically at N ≈ 6 for T <= 12 in slow detectors. The ring has no
    light cone, so its N-first limit needs the global log-tail control G1.
  - (c) There is an exactly solvable interacting-free class, the matchgate chain, with an unconditional N-first limit
    and a complete late-time classification (P4.7).
  - (d) The SPEC order is numerically reachable (P4.13).
- (3) **Chain-specific obstructions.**
  - (a) Single-spin coupling: there is no CLT, the classical-label reduction is false (P4.12 counterexample), and F* is
    strongly non-normal.
  - (b) Finite-bandwidth boundary spectra give gapped bound-state caps (P4.11). Free chains can also have Majorana zero
    modes, which force an equatorial pair (P4.7).
  - (c) The Ising resonance set is `|h0| = |h_z +- J_zz|` (codimension 1, P4.6), versus `{h_z, h_z +- 2J_zz}` for the ring.
- (4) **Mechanism: the same in both geometries** [PROVED components + NUMERICAL]. In the fixed-point basis, weak
  coupling produces a first-order dressing cap. Its size is set by the non-normal (eigenvalue) part of the qubit-frequency
  spectral weight. Golden-rule relaxation does not spread the roots, because the secular part is energy-graded. At
  N <= 10 the index eta is equally small for the 1/sqrtN ring (0.036 -> 0.0075, T = 4 -> 16) and for the chain
  (0.030 -> 0.008). Degenerate passes (caps, equator) come from symmetry, gaps or zero modes. Uniform 1/2 would need
  full mixing. **Neither geometry has a mechanism that selects Born.**
- (5) **Differences are bookkeeping.** The ring's collective F* at 1/sqrtN has tauFF = O(1), the same order as the
  chain's (e.g. 1.58 vs 0.91 at T = 8 with the same detector). The ring differs only through the scaling hypothesis and
  the absence of a light cone. The chain differs through its non-trivial O(1) N-first limit and its bound states.
**Status.** (1) and (2a-c) PROVED. (2d), (3b-c) and (4) PROVED or NUMERICAL as marked in P4.5-P4.13. The claim "same
mechanism, no Born selection" as T -> inf in the SPEC order is a CONJECTURE (P4.12, late-time candidates A/B).
**Chain go/no-go.**
- **No-go** [PROVED] on: the Ising h_D || z class (P4.6); the matchgate class (P4.7; the late-time law is equatorial, a
  cap, or a non-Born oscillation); the QND, CG and GCG classes; gapped couplings at first order (P4.11); and any
  first-order weak-coupling regime at fixed T (the law is a cap of radius O(g), a degenerate pass).
- **No-go** [NUMERICAL] in the SPEC order for generic interacting slow chains up to T ≈ 3.5-10 T1.
- **OPEN:** the SPEC-order T -> inf law of generic gapless interacting chains beyond `T1/eta`. Both candidates are
  non-Born.

---
## Answers to the GOAL questions assigned to WP4 (Tier 6)

**(1) Tier 1-5 analogues on the endpoint chain.**
- **Tiers 1-3 with detector field || z and Ising bonds** (any h0, any g_x, g_y, g_z). `Z_{i>=2}` are conserved, so the
  law is exactly 4 atoms per time and identical for every N >= 2. The SPEC and reverse orders therefore coincide.
  Strong Born and coverage fail at every T. The chain resonance set is `|h0| = |h_z +- J_zz|` (P4.6).
- **GOAL Q5 for the chain.** `h_0z = h_z` is neither necessary nor sufficient. It is not even resonant for the chain,
  whose resonances sit at `h_z +- J_zz`.
- **Tier 2 (transverse qubit field).** The axis is `n* = h0hat + O(g)`, kinematic, and in that basis the law is a cap.
- **Tier 3 (multichannel).** It stays in the same classes (P4.6, or GCG when a grading exists).
- **Tier 4 (XXZ/XY).**
  - U(1) with `g_x = g_y` and `h0 || z` is charge-graded, so the law is delta.
  - XY + h_z with h_0z and (g_x, g_y) is matchgate: one radius per time, and a late-time law that is equatorial (zero
    mode), a cap (bound state) or a non-Born oscillation (P4.7).
  - Interacting XXZ belongs to the generic class.
- **Tier 5 (XYZ, generic).** The impurity law (P4.8-P4.12) applies. Numerically, in the SPEC order, the law in n* is a
  cap up to T ≈ 3.5-10 T1 (P4.13).

**(2) Mechanisms compared.** The mechanism is the same in both geometries (P4.16):
- a kinematic fixed point h0hat;
- a first-order dressing cap set by the eigenvalues (not the singular values) of the qubit-frequency transfer operator
  F*;
- relaxation that does not spread the roots, because the secular dynamics is energy-graded (GCG, P4.12).
Degenerate passes come from symmetry, gaps and zero modes. The chain does not realize "Dephasing -> 1/2" in the SPEC
order at accessible T. Pure dephasing is inert in the fixed-point basis (P4.10).

**(3) Chain-specific obstruction and advantage.**
- **Advantages:** an O(1) coupling with a non-trivial N-first limit and no scaling hypothesis; a light-cone
  existence theorem (P4.5, modulo H1); an exactly solvable matchgate class; and an SPEC order that numerics can reach.
- **Obstructions:** no CLT and no classical reduction (P4.12); strongly non-normal F* (eta ~ 1/T); bound states and
  zero modes that give degenerate laws; and a code perturbative gate that places T1 outside every accessible light-cone
  window (a scale-invariant factor of about 10^2 at N = 10).

**(4) Conditions for chain stability.**
- No open region of Born stability was found or derived.
- Open, stable regions of **non-Born** behaviour do exist:
  - gapped caps (`dist(2|h0|, supp S_e) > 0` is an open condition; P4.11);
  - generic weak-coupling caps at fixed T (P4.8);
  - within the matchgate class, the topological equatorial pair (P4.7).
- **Chain go/no-go:** NO-GO on every controlled regime. The OPEN residual is the SPEC-order T -> inf law of gapless
  interacting chains beyond `T1/eta`. Both candidate outcomes are non-Born: (A) a cap growing ~ log T; (B) eventual
  uniform 1/2.

**Preferred axis (GOAL note).** On the chain it is the qubit self-field axis h0hat to O(g). This is kinematic. The
offset from h0hat is not toward the detector field (P4.13 addendum).

## Open items
1. The SPEC-order T -> inf law of gapless interacting chains beyond `T1/eta(T)` (P4.12 candidates A/B). This needs
   either a proof of secular suppression at all orders with the finite-T energy blur, or N ~ 20-40 methods (tensor
   networks) at T ~ 30-100.
2. A proof of H1 (light-cone-local small-eigenvalue log tail) for the approved families. The observed growth of the
   condition number is about x2.5 per site at T = 4, i.e. exponential, which H1 tolerates.
3. The asymptotics of eta(T) (observed ~1/T) and of `<|f|^2>` (observed ~log T). The Brown measure of `F*^inf(T)` in
   the tracial half-chain algebra (disc test 1.0-1.4: ring- or disc-like).
4. The ring's eta at large N. At N <= 10 it is as small as the chain's, so the classical-reduction premise of C1.2
   (eta -> 1) is unverified. This belongs to WP1-3.
5. A stationary-phase proof of matchgate regime (ii-c): a quasi-periodic ratio with band-edge frequencies.
6. An all-orders SPEC-order check for screen_00 itself, whose fast detector puts the light cone beyond 9 sites at T = 1-2.

## Surprises
1. The qubit depolarizes (|w| drops to 0.27) while the collapse law stays a cap with `<sin^2> ≈ 0.011`. Past T1 the
   roots are still predicted by the FIRST-order transfer operator. The explanation is exact energy grading of the
   secular dynamics (GCG).
2. BRIEF's matchgate late-time claim is wrong. A decaying boundary return gives a non-convergent O(1) oscillation
   (pooled S = 0.67 at full coverage). The equatorial delta comes from Majorana zero modes.
3. screen_00's operator-norm light cone exceeds 9 sites by T = 1-2, whereas slow detectors saturate at N ≈ 6 for T <= 12.
4. The first-order non-normality index of the 1/sqrtN ring is as small as the chain's at N <= 10.
5. An O(1) Jensen gap (≈ 1) coexists with a near-point cap law.
6. The reverse-order lab-z S rises with N (0.45 -> 0.65), reproducing the campaign's pattern, while the SPEC-order
   law is N-independent.
7. A lab-z S of 0.858 at full coverage arises from a law that is a polar cap in its own fixed-point basis (Ising
   chain, tilted resonant h0; P4.6).

## Corrections to BRIEF / digests
1. `BRIEF.md:431-432` (Tier 6 "Settled", matchgate) "T -> inf law is delta_{pi/2} if the boundary return decays" is
   REFUTED (P4.7). A decaying return gives a stationary non-degenerate oscillation (theta*/pi in [0.08, 0.54]). The
   equatorial delta requires a Majorana zero mode on the qubit.
2. `BRIEF.md:439-442` (C6.1), "if a.c. at 2|h_eff| the law flows to uniform", is not supported in the SPEC order. At
   T up to 3.5-10 T1 the law stays a cap despite relaxation (P4.13). GCG shows why the secular part cannot spread
   roots. The final T -> inf law remains OPEN.
3. `BRIEF.md:259-262` (BC-C). The "N-independence at N >= 6-9, T <= 4" for screen_00 concerns low moments of the law.
   Operator-norm light-cone saturation fails at N <= 9 even at T = 1 (P4.1).
4. The Tier-1 resonance set `{h_z, h_z +- 2J_zz}` (C1.1) is ring-specific. The chain's is `{h_z +- J_zz}` (P4.6).
5. `BRIEF.md:141-142` (2.1 v). The O(1) Jensen gap is necessary but far from sufficient: caps show G ≈ 1 (P4.13).
