# WP5: necessary conditions and Born-achieving ensembles

> Source: Agent work-package report, go/no-go derivation workflow (scratchpad `gonogo/wp/WP5/REPORT.md`), 2026-09-24. Derivations and bornkit numerics (N <= 10); not refereed unless stated. The report was interrupted by a usage limit in places; content preserved verbatim.
> Collected: 2026-09-24
> Published: 2026-09-24

# WP5 — What a go would require: necessary conditions and Born-achieving ensembles

Agent report, 2026-09-24. READ-ONLY on the repository; all files under this folder. Status labels: PROVED,
PROVED-CONDITIONAL, HEURISTIC, NUMERICAL, CONJECTURE, REFUTED. Conventions follow BRIEF §1 (SPEC positive sign,
qubit first, outcome-0 pencil `U10 + lambda U11`, `lambda = e^{i phi} tan(theta/2)`).

## Contents
(Resumed run, 2026-09-24 afternoon. Scope narrowed by the orchestrator: task (c) is covered by WP4 P4.12 and WP3
P1-P3, P5, P7, and is only cited here, in P5.6.)
- P5.1 Necessary-conditions theorem (a), with corollary P5.1a (fixed-T weak coupling is Jensen-saturated)
- P5.2 Sharp Jensen-gap floor G_* in closed form: `(1/2)coth(1/2) - 1 = 0.08198` (quantitative form of (a)(ii))
- P5.3 CS reduction: every root law is the eigenvalue law of `W tan(Theta)`; exact mean-sigma identity (b, d)
- P5.4 Existence I: classical-label ensembles, exactly Born at every d, and why the approved families cannot supply them (b)
- P5.5 Existence II: a unitarily invariant (R-diagonal) Born ensemble via Haagerup-Larsen; uniqueness in its class;
  finite-d check; physical requirements (b)
- P5.6 Energy-graded pencils (c): cited, not redone
- P5.7 Fluctuation-theorem and calibration statistics across regimes, N = 4..10 (d)
- P5.8 Martingale route: verdict (e)
- P5.9 Assessment for the approved families (N first, then T -> infinity)
- Answers to GOAL questions, open items, surprises, corrections to BRIEF

---

## Standing setting and notation (used by every proposition)

- `U_N(T) = e^{-i H_N T}` on `C^2 (x) C^d`, `d = 2^N`; output axis `n` (outcome 0 = collapse to `|+n>`); rotate so
  `n = z` when convenient (`U -> (V^dag (x) I) U`, BRIEF §1.7). `rho0,N(T)` = outcome-0 root measure (algebraic weights;
  equal to SPEC kernel weights when roots are semisimple, BRIEF §2.1). `L1 = (1/d) log det E1(Omega)`,
  `p1 = (1/d) Tr E1 = (1 + w.Omega)/2`, `h = log p1 - L1 >= 0` (Jensen), mean Jensen gap `G = <h>_{S^2}`.
- `U_mu(Omega) := int log((1 - m.Omega)/2) dmu(m)` (logarithmic potential of a probability measure). By ID Lemma A,
  `L1 = C_N + U_{rho0}` with a constant `C_N` (BRIEF §2.1; `identity/NOTE.md` §1).
- **(H-lim)** (the hypothesis of every "go" statement): for all `T` in an unbounded set, `rho0,N(T) => rho0(T)` weakly as
  `N -> infinity` (N first), the pencils are regular, and `rho0(T) => rho0^inf` as `T -> infinity`. (Cesaro fallback:
  replace `rho0(T)` by its time average; everything below goes through because potentials are linear in the measure and
  `avg L1 <= avg log p1 <= log avg p1`.)
- **Go at axis n** (strong): `rho0^inf = (1 + n.Omega) E` with `E` an inversion-even probability measure and
  **coverage** `supp E = S^2` (BRIEF §2.1 vii). Weak: the same for the polar marginals with polar support `[0, pi]`.

---

## P5.1 Necessary-conditions theorem (task a)

**Statement (Theorem N).** Assume (H-lim) and a strong go at axis `n` with coverage. Then all of the following hold.
- **(N1) No exact cone or grading symmetry along the way.** There is no `a != 0` with `[H_N, a.sigma_0] = 0` for
  infinitely many N (in particular no X0-, Z0- or h0-hat-conserving point), and no conserved
  `K_N = alpha (n.sigma_0) (x) I + I (x) Q_N` with `alpha != 0` and `Q_N` Hermitian (charge grading, and, new here,
  *any* energy-type grading such as `Q_N = H_D/h`) for infinitely many N.
- **(N2) O(1) Jensen gap, with a sharp floor.** `liminf_{T->inf} liminf_{N->inf} G_N(T) >= G_*(rho0^inf) > 0`, where
  `G_*(rho) := inf_{|w|<=1} [ <f_w> - essinf f_w ]`, `f_w := log((1 + w.Omega)/2) - U_rho`. For the Born law with
  uniform prior, **`G_* = (1/2)coth(1/2) - 1 = 0.08198`** (P5.2), attained at `w = -tanh(1/2) n`. If the
  infinite-temperature qubit channel is fully depolarizing (`w = 0`, the generic ergodic late-time situation) the floor
  for the uniform-prior Born law is **1/2**. **The gap is necessary, not sufficient:** exactly graded pencils (Lemma G
  below; WP3 P1, P5; WP4 P4.12 GCG) have `rho0 = delta_n` with `G = 1.69-1.70` (WP3 P5, exact RWA Tier-1 models on R1,
  T = 20, N = 6/8), because a graded `E1(Omega)` is far from scalar while its log-determinant is exactly
  `d log sin^2(theta_n/2) + const`.
- **(N3) Non-uniform, with the Born dipole.** `rho0^inf` is not uniform (so no Haar-like/spherical limit, R = 1/2);
  its dipole is `m = M n` with `M = int Omega Omega^T dE` positive definite, second moment `S = M`, hence `B1 = 1`,
  `n_hat = n`, and resultant `|M n| in [lambda_min(M), lambda_max(M)]` (= 1/3 for uniform prior). In potential form:
  `int L1^inf Omega dA = -2 pi M n`.
- **(N4) Born functional identity (logit-linearity).** `Od_N -> Od` and `Ev_N - <Ev_N> -> Ev` in `L^1(S^2)` and
  `Lap Od = (n.Omega)(1 + Lap Ev)` in `D'(S^2)`. With uniform prior this is: the mean effect log-odds
  `(1/d) sum_k log(e_k/(1 - e_k))(Omega)` converges in `L^1` to exactly `-n.Omega`, and `(1/d) log det(E1 E0)` to a
  constant. At the pole: mean log-odds `-1`; at the antipode `+1`.
- **(N5) Fixed point.** The go axis is a fixed point of the limiting axis map, `Phi_inf(n) = n`, with `B1 = 1` and a
  resultant bounded away from 1 (a near-point-mass or cone fixed point, including the kinematic QND-cone fixed point
  `+-h0-hat`, is excluded by coverage).
- **(N6) Coverage and calibration.** `supp(rho0^inf + rho1^inf) = S^2`; equivalently for the polar law, the Born
  log-likelihood ratio `sigma = log cot^2(theta/2)` obeys `P(-sigma) = e^{-sigma} P(sigma)`; its calibration slope
  `b_hat` (P5.7) equals 1, and the outcome-0 mass in the southern hemisphere equals `int_{u<0}(1+u) dE_u > 0`
  (= 1/4 for uniform prior). Integral form: `E_{rho0}[tan^2(theta/2)] = E_{rho0}|lambda|^2 = 1`. Mean form (exact
  for every unitary, P5.3): `E_{rho0}[sigma] = -(1/d) sum_k log(e_k/(1-e_k))` at the pole `Omega = n`, which Born with
  uniform prior forces to equal 1. Caps and poles give `b_hat = +inf`; symmetric equatorial bands and Haar give
  `b_hat = 0`; so, unlike S_Born, the calibration slope is not passed vacuously by caps or bands. **Correction to my
  earlier draft:** an *exact* equatorial atom (`sigma = 0` identically) still satisfies the FT vacuously (b_hat is then
  undefined), so coverage must be reported with it, as for S_Born.

**Status.** PROVED (every item, under (H-lim)); the value in (N2) is the closed form of P5.2 (axial optimum PROVED,
global optimality over non-axial `w` NUMERICAL).

**Proof.**
- *(N1).* QND-cone lemma (BRIEF §2.4, OWN-proof): `supp rho0,N(T) ⊂ {a.Omega = a.n}` for every N, T. A closed set
  containing the supports of a weakly convergent sequence contains the support of the limit (portmanteau), twice
  (N, then T), so `supp rho0^inf` lies in a cone or great circle, of empty interior: coverage fails. Grading:
  **Lemma G (generalized grading, OWN-proof).** If `[U, alpha Z_0 (x) I + I (x) Q] = 0` with `alpha != 0`, order the
  eigenspaces `P_q` of `Q`. Then `U (|0> (x) P_q) ⊂ (|0> (x) P_q) + (|1> (x) P_{q + 2 alpha})` and
  `U (|1> (x) P_q) ⊂ (|1> (x) P_q) + (|0> (x) P_{q - 2 alpha})`, so `U11` is block diagonal in the `Q`-grading and `U10`
  is strictly block-shifting (`P_q -> P_{q+2alpha}`). Hence `U10 + lambda U11` is block-triangular with diagonal blocks
  `lambda U11|_q`, and `det(U10 + lambda U11) = lambda^d det U11`: either `rho0 = delta_n` (all roots at the pole) or the
  pencil is singular. The repository charge-grading item (BRIEF §2.7) is the case `Q` = a charge; `Q = 0` is pointer-QND;
  **`Q = H_D/h` is exact energy conservation of an RWA (rotating-wave) coupling**. `delta_n` fails coverage.
  (Lemma G was derived independently in three WPs: it is WP4 P4.12 "GCG" and WP3 P1(a); the statements agree.) Scope
  note: Lemma G forbids a grading along the *go axis* n. A grading along `a != n` does not trivialise the n-basis
  pencil (it becomes block-tridiagonal, a Hatano-Nelson-type problem), so (N1) does not exclude it; P5.6 cites the
  weak-coupling analysis of that case. ∎(N1)
- *(N2).* Finite-N lower bound (exact, new): since `h_N = f_N - C_N >= 0` with `f_N := log p1,N - U_{rho0,N}`, we have
  `C_N <= essinf f_N` and `G_N = <f_N> - C_N >= <f_N> - essinf f_N`. Limit: `n -> G(n, .)` is continuous into `L^1`, so
  `U_{mu_k} -> U_mu` in `L^1` for `mu_k => mu` (ID §1.6.5). Along a subsequence `w_N -> w_T` (compact ball), and
  `log(1 + w.Omega)` is uniformly integrable over `|w| <= 1`, so `f_N -> f_T := log p1(w_T) - U_{rho0(T)}` in `L^1`.
  `L^1` convergence gives a.e. convergence of a further subsequence, hence `limsup essinf f_N <= essinf f_T`; with
  `<f_N> -> <f_T>` this gives `liminf_N G_N(T) >= <f_T> - essinf f_T >= G_*(rho0(T))` (apply to the subsequence that
  realizes the liminf). The same argument in `T` (with near-optimal `w_T`) gives lower semicontinuity,
  `liminf_T G_*(rho0(T)) >= G_*(rho0^inf)`. (The `L^1` convergence of `U_{mu_k}` is norm convergence of a Bochner
  integral of the continuous map `m -> G(m, .)` from S^2 into `L^1`; approximate that map uniformly by a finite
  partition of unity, on which weak convergence acts termwise.) Positivity: for a Born law whose prior `E` has a
  bounded density, `U_rho` is continuous, so `w -> <f_w> - essinf f_w` is continuous on the open ball and tends to
  `+inf` at `|w| = 1` (the `log p1` singularity at `-w_hat` is not compensated); hence `G_*` is attained at some
  `|w| < 1`. `G_*(rho) = 0` then means `f_w` is a.e. constant, i.e. `U_rho = log p1(w) + c`, i.e. `rho` is the
  aberration law of `w` (ID ii a). Aberration laws are never Born for `0 < |w| < 1`, and `w = 0` is uniform (not Born)
  (ID ii b). So `G_*(Born with bounded-density prior) > 0`. ∎(N2)
- *(N3).* `m = int Omega (1 + n.Omega) dE = M n` (odd moments of `E` vanish), `S = int Omega Omega^T (1 + n.Omega) dE = M`
  (third moments vanish), `n_raw = S^{-1} m = n`. `M` is positive definite because `supp E = S^2`. Uniform `rho0`
  has `m = 0 != M n`. Potential form: ID (iv). ∎(N3)
- *(N4).* `Od_N` is free of the constant `C_N`, so it converges in `L^1` whenever the measures converge; ID (i) gives
  `4 pi (rho0 - rho1)/2 = Lap Od` and `4 pi (rho0 + rho1)/2 = 1 + Lap Ev`; Born `rho0 = (1 + n.Omega)E` is then exactly
  `Lap Od = (n.Omega)(1 + Lap Ev)`. Uniform prior: `Lap Ev = 0` so Ev is constant; `Lap Od = n.Omega` has the unique
  odd solution `Od = -(1/2) n.Omega`; `2 Od = (1/d) sum log(e_k/(1-e_k))` (ID §1.6.2). ∎(N4)
- *(N5).* Born in output basis `n` means `p0 = |<+n|Omega>|^2`, i.e. Born about `n` itself; (N3) gives `n_hat = n`,
  i.e. `Phi_inf(n) = n`. A fixed point whose cloud has resultant -> 1 or lies on a cone has no coverage (N1, N6). ∎(N5)
- *(N6).* ID (iii) and (vii). Integral form: strong Born is `rho0(-Omega) = tan^2(theta/2) rho0(Omega)` (BRIEF 1.6), so
  `E_{rho0} tan^2(theta/2) = int rho0(-Omega) dOmega = 1`; the weak version gives the same with the polar law. The mean
  form is the identity of P5.3 combined with (N4) at `Omega = n`. The calibration slope `b_hat` solves
  `E[sigma/(1 + e^{b sigma})] = 0`, and `b = 1` is a root under the FT because `sigma/(1+e^sigma)` is odd-weighted:
  `g(sigma) + e^{-sigma} g(-sigma) = 0` for `g(s) = s/(1+e^s)`. ∎

**Intuition.** Roots see the *geometric* mean of the detector's effect spectrum; any linear (trace) functional sees the
arithmetic mean. Born needs the two to differ by at least 0.08 nats on average, forever, while the geometric-mean log-odds
must be an exactly linear, bounded function `-n.Omega` of the input, and the conditional-prior part must be flat.
Symmetry (N1) makes the log-odds infinite on a set (poles, cones); scalar effects (Jensen saturation) make it an
aberration law; full scrambling (Haar) makes it zero. Born sits strictly between "one-bit readout" and "total mixing".

**Failure modes of the theorem.** It is conditional on (H-lim): it says nothing if the N-first limit does not exist
(BRIEF G1). It uses algebraic weights; for defective pencils with `k_j/K != m_j/d` the SPEC law can differ (ID §1.5).

### P5.1a Corollary: fixed-T weak coupling is Jensen-saturated (chain and 1/N ring)
**Statement.** Let `delta := ||H_qD|| T <= 1/4`. Then `G_N(T) <= (32/3) delta + O(delta^2 log(1/delta))` uniformly in N.
For the endpoint chain `||H_qD|| <= |g_x| + |g_y| + |g_z|`; for the 1/N ring the same bound holds (`||(1/N) sum sigma_i|| = 1`);
for the 1/sqrt(N) ring `||H_qD|| = sqrt(N) sum|g_a|` and the bound is void. Hence a go needs `T >= G_*/(11 ||H_qD||)`
at least, and every `g -> 0` limit at fixed T is Jensen-saturated (the kinematic point mass).
**Status.** PROVED. **Proof.** Duhamel: `||U - u_q (x) U_D|| <= delta`. `M0(Omega) = a(Omega) e^{i chi} U_D + Delta`,
`a = |<1|u_q|Omega>| = sin(theta'/2)` (theta' from the kinematic root `u_q^dag|0>`), `||Delta|| <= delta`. Weyl:
every singular value of `M0` lies in `[a - delta, a + delta]`, so for `a > 2 delta`,
`h <= 2 log((a+delta)/(a-delta)) <= (16/3) delta/a`, and `(1/4pi) int dA / sin(theta'/2) = 2`. On the cap `a <= 2 delta`
(area `O(delta^2)`) use `L1 = C + (1/d) sum_j log((1 - n_j.Omega)/2)` with `C >= L1(Omega_0) >= 2 log(1 - delta)` at the
antipode `Omega_0` of the kinematic root; `int_cap -log((1 - n.Omega)/2) = O(delta^2 log(1/delta))`. ∎
**Intuition.** Born cannot be established before the coupling has acted for a time of order `1/g`; the 1/sqrt(N) ring
escapes this bound only because its collective coupling is not small in operator norm.

---

## P5.2 Sharp Jensen-gap floor in closed form (quantitative (a)(ii))

**Statement.** Let `rho0 = (1 + n.Omega)/(4 pi)` (Born, uniform prior). Then
`G_*(rho0) = inf_{|w| <= 1} [<f_w> - essinf f_w] = (1/2) coth(1/2) - 1 = 0.0819767`, attained at `w = -tanh(1/2) n`,
and for the fully depolarized channel `w = 0` the floor is exactly `1/2`. Consequently any N-first law that is
Born with uniform prior needs `liminf G_N(T) >= 0.082` (and `>= 1/2` if the qubit's infinite-temperature channel is
fully depolarizing), in the limit of Theorem N (N2).
**Status.** PROVED on the axial line `w = c n`; that the axial line contains the global optimum is NUMERICAL (2-D grid
over `(w_par, w_perp)` plus Nelder-Mead, which is exhaustive by axial symmetry; `jensen_floor.json`).
**Proof (axial).** With `u = n.Omega`, the Born potential is `U_rho = -u/2 + const` (ID (i), uniform prior), so
`f(u) = log((1 + c u)/2) + u/2` up to a constant. `f'' = -c^2/(1 + cu)^2 < 0`, so `f` is concave in `u` and its
essential infimum over the sphere is `min(f(1), f(-1))`. `<f> - min(f(1), f(-1))` is minimised where
`f(1) = f(-1)`, i.e. `log((1-c)/(1+c)) = 1`, `c = -tanh(1/2) =: -t`. There `log(1 - t) = log(1 + t) - 1`, and
`<log(1 + cu)>_u = [(1+t) log(1+t) - (1-t) log(1-t)]/(2t) - 1 = log(1+t) + (1-t)/(2t) - 1`. Hence
`G_* = log(1+t) + (1-t)/(2t) - 1 - log 2 - [log((1-t)/2) + 1/2] = 1 + (1-t)/(2t) - 3/2 = 1/(2t) - 1`. At `c = 0`:
`<f> = -log 2`, `essinf f = -log 2 - 1/2`, so the floor is `1/2`. ∎
**Numerical check.** `scripts/jensen_floor.py` (200 x 200 Gauss-Legendre x uniform grid): global 2-D optimum
0.081959 at `w = (0, 0, -0.46212)`, i.e. `w_perp = 0` and `w_par = -tanh(1/2)` to 5 digits; the 2e-5 deficit is the
grid missing the endpoints `u = +-1` where the infimum sits. Closed form 0.0819767 (fine quadrature agrees).
**Reference values of the actual gap `G` in the two Born-achieving ensembles below** (both exceed the floor, as they
must): classical-label model `G = log(4/3) = 0.2877` exactly (P5.4); R-diagonal model `G = 0.6230` (d -> inf, from
`E_{mu_B} log e = -1.8256`; `rdiag_analytic.json`), measured 0.6174 / 0.6195 at d = 64 / 256 by `bk.log_potential`.
**Intuition.** Born needs the geometric mean of the effect spectrum to lag the arithmetic mean by at least 0.08 nats
on average; for a fully scrambled qubit channel the lag must be at least half a nat.
**Failure modes.** The floor is for uniform prior; a strongly non-uniform prior `E` changes the number (not its
positivity). Necessary only: the RWA delta laws of WP3 P5 have `G ~ 1.7`.

---

## P5.3 CS reduction: every root law is the eigenvalue law of `W tan(Theta)`; exact mean-sigma identity

**Statement.** Let `U in U(2d)` with `U11` invertible (regular pencil, no root at infinity), in output basis `n`
(rotate `n -> z`, and rotate the input by the same qubit rotation, which only rigidly rotates the cloud, BRIEF 1.7).
(i) CS decomposition: `U10 = Q2 sin(Theta) P1^dag`, `U11 = Q2 cos(Theta) P2^dag` with `Q2, P1, P2` unitary and
`Theta = diag(theta_k) in [0, pi/2)^d`. The outcome-0 roots, with algebraic multiplicities, are
`spec(W tan Theta)` with `W := -P1^dag P2 in U(d)`. `Q1, Q2` drop out.
(ii) `sin^2 theta_k` is the spectrum of the pole effect `E1(n) = U10^dag U10 = P1 sin^2 Theta P1^dag`, and
`E1(-n) = U11^dag U11 = P2 cos^2 Theta P2^dag`; `W` is the relative unitary between their eigenbases. Conversely,
every pair `(W, Theta)` is realised by some U. So **the root law is a function of the pole-effect spectrum and of the
relative position of the two pole-effect eigenbases, nothing else.**
(iii) Exact identities (every d):
`E_{rho0}[sigma] = -(1/d) sum_j log|lambda_j|^2 = -(1/d) sum_k log(e_k/(1 - e_k))`, `e_k = sin^2 theta_k` (the mean
of the Born log-likelihood ratio over the roots equals minus the mean pole log-odds of the effect);
`E_{rho0}|lambda|^2 <= (1/d) sum_k tan^2 theta_k` (Schur), with equality iff `W tan Theta` is normal;
Weyl log-majorisation `sum_{j<=k} log|lambda|_(j) <= sum_{j<=k} log tan theta_(j)` (both sorted decreasingly),
with equality at `k = d`.
(iv) Two extreme positions: if `W` commutes with `Theta` (up to degeneracies), the roots have `|lambda_k| = tan theta_k`
exactly (the "classical" case, P5.4); if `W` is Haar and free from `Theta` as `d -> inf`, `W tan Theta` is
R-diagonal and its root law is given by the Haagerup-Larsen formula (P5.5).
**Status.** PROVED ((i)-(iii) elementary; (iv) cites the Haagerup-Larsen theorem for the free case).
**Proof.** (i) The CS decomposition of a 2x2 block unitary with d x d blocks is standard. Then
`U10 + lambda U11 = Q2 cos(Theta) [tan(Theta) P1^dag P2 + lambda] P2^dag`, whose determinant vanishes iff
`-lambda in spec(tan Theta P1^dag P2) = spec(P1^dag P2 tan Theta)`, with the same algebraic multiplicities.
(ii) Direct; at `Omega = -n` the pencil matrix is `M0 = e^{i phi} U11`. Realisation: take `P1 = I`, `P2 = -W`,
`Q1 = Q2 = I`. (iii) `(1/d) log|det(W tan Theta)|^2 = (2/d) sum log tan theta_k`, and `sigma = -log|lambda|^2` because
`|lambda| = tan(theta/2)` measured from `n`. Schur's inequality `sum |lambda_j|^2 <= ||T||_F^2` and Weyl's
majorant theorem for `T = W tan Theta`. ∎
**Graph-operator form (the brief's suggestion).** `V_0 := U^dag(|0> (x) C^d)` is the space of inputs that end in
outcome 0; it is the graph `{|0> (x) v + |1> (x) K v}` of `K = U01^dag (U00^dag)^{-1} = -P2 tan(Theta) P1^dag`, and a
product state lies in `V_0` iff `lambda = q1/q0 in spec K`. So `K = -U11^{-1} U10`: the graph operator of the
outcome-0 subspace is exactly the root operator.
**Numerical check.** The identity (iii) is checked on every RMT record of P5.7 (`ft_rmt.jsonl`: `mu` versus
`-mean_logodds_pole`, equal to all printed digits, e.g. Haar d = 16: -0.0025 / -0.0025; R-diagonal d = 1024:
1.0009 / 1.0009).
**Consequences for (a).** Born with uniform prior forces, at every large d, the geometric-mean pole odds of the
effect to be `e^{-1}` (mean pole log-odds `-1`, the pole value of (N4)); any Born law forces `E[sigma] > 0` (mean
pole log-odds negative). **Haar-like pole statistics are therefore incompatible with Born in any relative basis:** the
arcsine CS law has mean log-odds 0, so no choice of `W` can make its root law Born (it gives `E[sigma] = 0`).
**Intuition.** The collapse problem is a non-normal eigenvalue problem whose singular values are the pole odds of
the detector effect; Born is a statement about how the eigenvalues of `W tan Theta` spread relative to its singular
values, which depends on how "free" the two pole-effect eigenbases are.
**Failure modes.** Roots at infinity (`U11` singular) need the reversed chart; defective pencils: algebraic
multiplicities are used (ID §1.5).

---

## P5.4 Existence I: classical-label ensembles (exact Born at every d) and why the approved families cannot host them

**Statement.** (i) Let `U = sum_{j=1}^d u_j (x) |j><j|` (the detector is a static classical label, every `|j><j|`
conserved) with qubit unitaries `u_j`. The outcome-0 roots are exactly the Bloch points `m_j` of `u_j^dag|0>`, one per
label, with kernel = algebraic weight 1. Choosing `{m_j}` i.i.d. Born-uniform about `n` (or a deterministic Born
quadrature) gives an ensemble whose root law is exactly Born with full coverage (strong criterion), weakly
converging as `d -> inf` to `(1 + n.Omega)/(4 pi)`. Its Jensen gap is `G = log(4/3)` in the limit, its channel has
`w = -n/3`, and its pole CS law is `e ~ Beta(1, 2)` (mean 1/3); `W` commutes with `Theta`.
(ii) In the approved families (GOAL Hamiltonian, ring or chain, any scaling), a complete set of conserved detector
projectors `[H, I (x) |j><j|] = 0` forces all coupling operators and `H_D` to be diagonal in one detector basis;
since `[Sigma X_i, Sigma Y_i] != 0` and `[X_1, Y_1] != 0`, at most one coupling axis `a` survives, and then the
qubit sees `h0 + g_a m_j a` with a **scalar** label `m_j`. The fixed-T root set then lies on the one-parameter curve
`{Bloch(e^{iT(h0.sigma + g m sigma^a)}|0>) : m in R}`, so the N-first law at every fixed T has 1-D support and fails
strong coverage; this is the commuting-QND class, whose weak and Cesaro no-gos are already PROVED (BRIEF §2.4,
Theorems B, D, E, H/H1, CQ; all-axis version WM D2-D3).
**Status.** (i) PROVED. (ii) PROVED for the fixed-T statement; the T -> infinity statement is the cited ledger.
**Proof.** (i) `U10 = diag(<1|u_j|0>)`, `U11 = diag(<1|u_j|1>)`, so `(U10 + lambda U11)|j> = 0` iff
`<1|u_j|psi(lambda)> = 0` iff `u_j|psi> ∝ |0>`. `E1(Omega) = diag((1 - m_j.Omega)/2)`, so
`L1 = (1/d) sum_j log((1 - m_j.Omega)/2) = U_{rho0}` exactly (C = 0). For Born `m`: `U_Born = -1 - (n.Omega)/2`
(the uniform part gives `<log sin^2(gamma/2)> = -1`, the dipole part `(n.Omega)(1/2) int_{-1}^1 x log((1-x)/2) dx
= -(n.Omega)/2`), `p1 = (1 - <m>.Omega)/2` with `<m> = n/3`, and
`<log p1 - L1> = <log(1 - u/3)> - log 2 + 1 = log(4/3)`. `tan^2 theta_j = |lambda_j|^2`, and under Born
`P(|lambda|^2 <= x) = 1 - (1+x)^{-2}`, i.e. `e = x/(1+x) ~ Beta(1,2)`. (ii) A complete set of commuting conserved
projectors on the detector makes `H = sum_j h_j (x) |j><j|`, so each coupling operator `B_a` (with
`H_qD = sum_a sigma_0^a (x) B_a`) is diagonal in the `|j>` basis; two of `Sigma_i X_i, Sigma_i Y_i, Sigma_i Z_i` (ring)
or of `X_1, Y_1, Z_1` (chain) do not commute, so at most one has nonzero `g`. Then `h_j = h0.sigma + g_a b_j sigma^a`
with real eigenvalues `b_j` of `B_a`. ∎
**Numerical check.** Not needed for (i) (exact); `jensen_floor.json` reproduces `G = log(4/3) = 0.28768` by quadrature.
**Intuition.** A classical label can encode any law, Born included, but only by putting it in by hand as the
distribution of kinematic rotations; physically the label is a static random field, and the approved Hamiltonians
provide only a one-parameter field, so the rotations sweep a curve.
**Failure modes.** None within its scope; it shows that "exact Born with coverage" is not forbidden by unitarity
itself, so a no-go must use the structure of the families.

---

## P5.5 Existence II: a unitarily invariant (R-diagonal) Born ensemble; uniqueness; physical requirements

**Statement.** Let `mu_B` be the probability law on `(0, inf)` with S-transform `S_B(z) = sqrt(-z)/(1 - sqrt(-z))`,
`z in (-1, 0)`. Let `Theta_d` be deterministic with the empirical law of `tan^2 theta_k` converging to `mu_B`, and
`P1, P2, Q1, Q2` independent Haar on U(d); build `U_d` from the CS form of P5.3.
(i) (Haagerup-Larsen) The limit `T = W tan Theta` is R-diagonal and its Brown measure is rotation invariant with
`mu_T(|lambda| <= r) = 1 - (1 + r^2)^{-2}`, which is exactly the Born-uniform law about `n` on the Bloch sphere
(`1 - cos^4(theta/2)`), strong and weak, with full coverage.
(ii) (Uniqueness) Within the R-diagonal class (W Haar and free from Theta) the root law is Born-uniform **iff** the
CS law is `mu_B`; the Haar unitary's arcsine CS law gives the spherical law instead (`F = r^2/(1 + r^2)`, R = 1/2).
(iii) Properties of `mu_B`: explicit Cauchy transform `G(zeta) = (1 - s^2)/zeta` with
`(zeta + 1) s^3 - s^2 - s + 1 = 0`; support all of `(0, inf)`; density `~ (sqrt2/pi) x^{-1/2}` at 0 and
`~ 0.2757 x^{-5/3}` at infinity; `E log x = -1`; mean pole flip probability `<e> = (3 - sqrt5)/2 = 1/phi^2 = 0.381966`
exactly (phi = golden ratio), so the channel has `w = -(sqrt5 - 2) n`, `|w| = 0.2361`; `G = 0.6230`.
(iv) (Finite d) The eigenvalue law of `U_d`'s outcome-0 pencil converges to Born-uniform.
**Status.** (i) PROVED given `mu_B` is a probability measure (Haagerup-Larsen, J. Funct. Anal. 176 (2000), main theorem
on Brown measures of R-diagonal elements, applied with `S_{T*T} = S_B`; I did not re-derive it). Caveat: here
`tan Theta` is unbounded (`P(tan theta > y) ~ y^{-4/3}`, so `E tan^2 theta = inf`), as it already is for Haar (arcsine
tail `y^{-1}`); the formula is then needed for unbounded, `log^+`-integrable R-diagonal operators, the extension I
attribute to Haagerup-Schultz (2007) from memory and have not re-checked. The formula is confirmed numerically on both
the Haar and the Born case below). (ii) PROVED given (i) (the radial CDF determines `S` on
`(-1, 0)`, hence `psi`, hence the law, by analytic continuation of a Stieltjes-type transform). (iii) `<e>`,
`E log x` and the cubic are PROVED; positivity of the inverted density on all of `(0, inf)` is NUMERICAL (plus the
exact statement that the cubic's discriminant `22(x+1) + 5 - 27(x+1)^2 < 0` for all `x > 0`, so there is exactly
one complex-conjugate pair of branches and no spectral gap). (iv) PROVED-CONDITIONAL on the single-ring convergence of
empirical eigenvalue laws to the Brown measure for Haar-rotated matrices with **unbounded** singular values
(to my knowledge Guionnet-Krishnapur-Zeitouni 2011 and Rudelson-Vershynin 2014 cover bounded ones; the named hypothesis is uniform
integrability of `log s_min`-type tails of `W tan Theta - z`), and NUMERICAL (below).
**Proof.** (i) HL: for R-diagonal `T` with `T*T` not a point mass, `mu_T(B(0, [S_{T*T}(t-1)]^{-1/2})) = t`,
`t in (0,1)`. Born: `F(r) = t` gives `r^2 = (1-t)^{-1/2} - 1`, so `S(t - 1) = sqrt(1-t)/(1 - sqrt(1-t))`, i.e.
`S_B(z) = s/(1-s)` with `s = sqrt(-z)`. Haar check: `F = r^2/(1+r^2)` gives `S_H(z) = -z/(1+z)`, the S-transform
of `tan^2` of arcsine-distributed CS angles. (iii) `chi(z) = z S(z)/(1+z) = -s^3/((1-s)^2(1+s))` (strictly
monotone in `s in (0,1)`), `psi = chi^{-1}`, `G(zeta) = (1 + psi(1/zeta))/zeta` gives the cubic.
`<e> = -psi(-1)`: `chi = -1` iff `s^3 = (1-s)^2(1+s)` iff `s^2 + s - 1 = 0`, so `s = 1/phi` and `<e> = s^2 = 1/phi^2`.
`E log x = -1` is the HL total mass statement `(1/d) sum log tan^2 = E_rho0 log|lambda|^2 = -1` (P5.3 (iii)). ∎
**Numerical check (finite d; separate random-matrix experiment, not a Hamiltonian).** `scripts/muB.py`: density by
Stieltjes inversion on 1601 log-spaced points; min 1.3e-14 > 0 (far tail), mass 1 - 4e-9, S-transform reproduced
to 2e-6 at s = 0.1..0.9, tail constants `a0 = 0.45014` vs `sqrt2/pi = 0.45016`. `scripts/rdiag_check.py`
(one sample each, deterministic quantiles of `mu_B`):
| d | KS radial vs Born | KS vs spherical | S_Born (i.i.d.-Born floor) | coverage | resultant (1/3) | B1 | south frac (0.25) | b_hat (1) |
|---|---|---|---|---|---|---|---|---|
| 128 | 0.036 | 0.274 | 0.236 (0.094) | 82 | 0.332 | 0.991 | 0.234 | 0.994 |
| 512 | 0.0135 | 0.264 | 0.642 (0.627) | 98 | 0.334 | 1.004 | 0.240 | 1.004 |
| 2048 | 0.0056 | 0.253 | 0.852 (0.817) | 100 | 0.3334 | 0.9996 | 0.252 | 0.998 |
The Haar control (arcsine CS law, same code) gives KS vs spherical 0.043 / 0.018 / 0.0054 and S_Born -0.30 / -0.07 /
-0.007 (R = 1/2). The KS distance falls faster than the i.i.d. `d^{-1/2}` (roots repel), so S_Born sits at or above
the i.i.d. floor. More rows (d = 16..1024, pooled to 4096 roots) are in P5.7.
**Other constructions tried.** Products of `k` free spherical (Haar-type) factors have `S = S_H^k`, hence
`F(r) = r^{2/k}/(1 + r^{2/k})` with tail `1 - F ~ r^{-2/k}`; Born's tail is `(1 + r^2)^{-2} ~ r^{-4}`, lighter than
Haar's `r^{-2}`, so no product of spherical factors (nor any heavier-tailed free product) gives Born. Born's law is,
in distribution, the minimum of two independent spherical radii (`1 - F_B = (1 - F_H)^2`), which has no free-probability
counterpart I know of; the S-transform inversion above is the direct route.
**Physical requirements (what a Hamiltonian would have to supply).**
- (R1) *Freeness*: the eigenbases of `E1(n)` and `E1(-n)` in generic (asymptotically free) relative position. Any
  exact grading along n (Lemma G) or QND symmetry destroys it (W block-triangular relative to Theta).
- (R2) *The specific CS law `mu_B`*: infinite-temperature flip probability from `|+n>` exactly `1/phi^2 = 0.382`,
  geometric-mean pole odds `e^{-1}`, and the full shape of `mu_B` (not just its mean: the same mean with a point-mass
  CS law gives a single latitude circle; P5.8 uses this).
- (R3) *Stationarity*: (R1)-(R2) must hold at all late T, N first.
- In the other extreme position (W commuting with Theta, P5.4) the required CS law is Beta(1, 2) (mean 1/3). For
  intermediate positions the required law is something else. **Born is therefore a fine-tuning of the pole-effect
  spectrum against the relative position of the pole eigenbases.** Within the R-diagonal class it is a single point of
  the (infinite-dimensional) space of CS laws.
**Can the approved families supply it (N first, then T -> inf)?** The only universality mechanisms known for the CS
law of `e^{-iHT}` are: (a) weak coupling at fixed T, which drives `Theta -> 0` (P5.1a: Jensen-saturated, delta);
(b) energy-graded secular dynamics at resonance, which violates (R1) and leaves the roots at the pole (WP3 P1, WP4
P4.12); (c) full scrambling without conservation laws, whose attractor is the Haar/arcsine point (spherical, R = 1/2;
BRIEF 2.7 Haar, Theorem D). None has `mu_B` as its attractor. A go region would need the CS law to be locally
constant and equal to `mu_B` on an open parameter set at all late T, which none of (a)-(c) provides. [CONJECTURE for
the families; PROVED within the R-diagonal class that Born is a single, non-generic CS law.]
**Intuition.** Born is achievable by unitary dynamics, but only as a finely tuned middle ground: less mixing than
Haar (mean pole flip 0.382 < 1/2), yet with generic relative bases; the dynamical attractors sit at the two ends.
**Failure modes.** The R-diagonal model is a random-matrix ensemble, not a Hamiltonian; (iv) is conditional as stated;
the "no attractor at mu_B" statement for (a)-(c) is a survey of known mechanisms, not a theorem about all Hamiltonians.

---

## P5.6 Energy-graded pencils (task c): cited, not redone

Per the orchestrator, (c) is covered elsewhere; I only record how it plugs into Theorem N and P5.5.
- **Exact grading (any conserved `c a.sigma_0 + Q_D`, including `Q_D = H_D`):** all outcome-0 roots at `+a` in basis
  `a` (WP4 P4.12 "GCG", PROVED; WP3 P1(a), PROVED; my Lemma G in P5.1). This is (N1).
- **Near-graded weak coupling:** the secular (golden-rule) part of the dynamics is energy-graded and leaves the roots at
  the kinematic pole; roots move only through non-secular terms and the `1/T` energy blur (WP4 P4.12, HEURISTIC with exact
  first order); counter-rotating strength `kappa` moves radii rigidly as `sqrt(kappa)` (WP3 P2, PROVED gauge identity),
  so radii are `~ sqrt(g/omega)` (WP3 P3, P8). In the CS language of P5.3: grading makes `W` block-triangular relative to
  `Theta`, which is the opposite of the freeness (R1) that the R-diagonal Born mechanism needs, and it keeps `Theta`
  small (pole flip probability `<< 1/phi^2`), violating (R2).
- **Prediction for the N -> infinity law** (answering (c) by citation): a pole-concentrated cap about `n* = h0hat + O(g)`
  (neither a latitude, nor uniform, nor broad), with an O(1) Jensen gap on resonance that nevertheless carries no
  calibration (WP3 P5). My P5.7 numbers for the resonant ring are consistent with this (resultant 0.53-0.78, south
  fraction 0.04-0.16 at N = 8-10).

---

## P5.8 Martingale route (task e): verdict

**Statement (Proposition M).** The stochastic/martingale route (`wiki/concepts/theorem-targets.md:45-56`: a branch
coordinate `Z_t` with zero drift `L z = 0` and absorbing boundaries, so optional stopping gives `P(+1) = (1+z0)/2`)
cannot apply to the exact collapsible-state measure. Precisely:
- **(M1) Exact zero drift is pointer-QND and gives a delta.** Let `tau` be any faithful detector state and
  `Phi_tau(rho) = Tr_D[U (rho (x) tau) U^dag]`. If the qubit's z-polarisation has zero drift,
  `Tr[sigma_z Phi_tau(rho)] = Tr[sigma_z rho]` for all `rho`, then `U10 = U01 = 0`, hence (for every N and T at which it
  holds) `rho0 = delta_N` in the z basis. The same holds in any output basis `n` for zero drift of `n.sigma`.
- **(M2) The data a martingale controls do not decide Born.** Everything a zero-drift argument constrains is linear in
  the input state (the instrument `rho -> Tr_D[(|b><b| (x) I) U (rho (x) tau) U^dag]`). In the R-diagonal class of
  P5.5, as `d -> inf` the whole infinite-temperature qubit channel depends on the CS law only through its mean `<e>`:
  `Phi(rho) = diag(rho00 <c^2> + rho11 <e>, rho00 <e> + rho11 <c^2>)` (full dephasing plus a binary symmetric flip).
  The CS law `mu_B` (root law exactly Born) and the point mass at `e = 1/phi^2` (all roots on the single latitude
  `|lambda|^2 = e/(1-e) = 1/phi`, a degenerate, non-Born law) therefore have **identical** channels.
- **(M3) There is no filtration.** `rho0,N(T)` is a deterministic function of `U_N(T)` (P5.3: of `(W, Theta)`), with
  finitely many atoms per `(N, T)`. A fixed input `Omega` is collapsible with probability zero, and Born is a statement
  about the density ratio `rho0/(rho0 + rho1)` (a Radon-Nikodym derivative), not about the expectation of a stopped
  process started at `Omega`. Roots at `T + s` are not a function of roots at `T` (they need all of `U(T)`), so the root
  clouds carry no Markov or martingale structure in T either.
- **(M4) What survives.** The only martingale-like identity is the integral fluctuation theorem
  `E_{rho0}[e^{-sigma}] = E_{rho0}|lambda|^2 = 1` of (N6). It is a *constraint* that Born imposes, not a consequence of
  any dynamics: Haar gives `+inf` (spherical tail), the off-resonant ring 0.001, the Born R-diagonal ensemble 1.07 at
  d = 1024 (P5.7).
(For a *pure* detector state `|D0>`, zero drift only says `U10|D0> = U01|D0> = 0`, which constrains one detector
direction; the collapsible-state measure is built from the whole detector space, its identity being the
infinite-temperature `(1/d) log det` of ID, so the faithful-state version is the relevant one.)
**Status.** (M1) PROVED. (M2) PROVED in the `d -> inf` limit of the R-diagonal class (exact finite-d version not
attempted). (M3) PROVED (structural). **Verdict: no zero-drift structure exists in the exact root problem; route 4 does
not apply to the collapsible-state measure.** The one genuine martingale in the setting, the conditional qubit state
of a quantum-trajectory unravelling of a detector readout, reproduces Born for every unitary because its path measure is
Born-weighted by construction; it computes a different measure and is circular for this programme.
**Proof.** (M1) Take `rho = |0><0|`: `0 = <1|Phi_tau(|0><0|)|1> = Tr[U10 tau U10^dag]`, so `U10 tau^{1/2} = 0` and
`U10 = 0` since `tau` is faithful; `rho = |1><1|` gives `U01 = 0`. Then `U11` is unitary and
`det(U10 + lambda U11) = lambda^d det U11`: every root at `lambda = 0`. (For `tau = I/d`, zero drift is `w = -z`,
`|w| = 1`, the Jensen endpoint.) (M2) With the CS form and independent Haar `P1, P2, Q1, Q2`, every term of
`Phi(rho)` other than `<c^2>`, `<s^2>` is a normalised trace of a product containing `P1^dag P2` or `Q2^dag Q1`, which
vanishes as `d -> inf` (asymptotic freeness of Haar unitaries from deterministic matrices). A point-mass CS law gives
`T = W tan(theta0)`, whose eigenvalues all have modulus `tan theta0` (unitary times scalar). (M3) Definitions and P5.3. ∎
**Numerical check of (M2)** (`scripts/m2_channel.py`, random-matrix experiment, d = 512, same Haar `P1, P2, Q1, Q2`):
the Pauli transfer matrices of the two unitaries agree to 1.1e-3 (O(d^{-1/2}) fluctuations), both with `R_zz = 0.2361
= sqrt5 - 2` and transverse entries <= 3e-3; the Born model's radial KS distance to Born is 0.019, while the point-mass
model's 512 roots all have `|lambda| = 0.786151 = tan(theta0)` to 1e-14.
**Intuition.** Martingale arguments derive Born from the *linearity* of averaged quantum dynamics; the collapsible-state
measure is governed by a log-determinant (P5.3, ID), which is blind to exactly that linear data. The Born-achieving
unitary ensembles are, in fact, maximally far from zero drift: their channels keep only `|w| = 1/3` (classical label)
or `sqrt5 - 2 = 0.236` (R-diagonal) of the polarisation.
**Failure modes.** A reformulation of the collapse criterion in which each root carries a stochastic history (e.g.
roots of a monitored, non-unitary evolution) could admit a martingale; that would be a different measure from SPEC's.
