# WP3 mathematics referee report

> Source: Agent work-package report, go/no-go derivation workflow (scratchpad `gonogo/wp/WP3/referee_math/REFEREE.md`), 2026-09-24. Derivations and bornkit numerics (N <= 10); not refereed unless stated. The report was interrupted by a usage limit in places; content preserved verbatim.
> Collected: 2026-09-24
> Published: 2026-09-24

# WP3 referee report, mathematics lens

Referee: fresh-context, independent. Report under review: `wp/WP3/REPORT_full.md`. Repository was only read.
All decisive checks use the referee's own code (`own.py`: dense Pauli builder, `eigh` propagator, and
`scipy.linalg.eig(U10, -U11, homogeneous_eigvals=True)`, SPEC positive convention, qubit first, Z|0> = +|0>).
Logs are next to each script in this folder.

Verdicts are written as they are reached.

---

## P0 (dihedral parity-imbalance north atoms), claimed PROVED: **CONFIRMED-WITH-CORRECTIONS**

**Proof check.** With [H, Pi] = 0 (Pi = Z_0 prod Z_i), U10 anticommutes with P = prod Z_i and U11 commutes with it.
The dihedral group acts on the detector only and commutes with H and with P, so each block U_ab is G-equivariant.
By Schur, on the multiplicity space of each irrep rho, U10 is block-off-diagonal between the P = +1 and P = -1
parts, so rank U10|_rho <= 2 min(m_+, m_-). Hence dim ker U10 >= D(N). Every step is correct. The count is a
**kernel dimension**, so it holds with SPEC kernel weights, and it does not even need U11 invertible (that is needed
only for the pencil to be regular).

**Own check** (`c0_parity_atoms.py`, character theory written independently, own builder, QZ):
- D(N) = 6, 12, 26, 56, 116, 236 for N = 4, 6, ..., 14, matching the report.
- **D(N) = 0 for every odd N** (N = 3, ..., 13). For odd N every group element has a cycle of odd length, so
  tr(g P) = 0 and m_+ = m_- for every irrep. The report lists only even N and does not say this.
- dim ker U10 = number of roots with theta < 1e-8 = D(N) at four Tier-1 points (including h0z = 1.74, Jzz = -0.5,
  g = 0.3) for N = 4, 5, 6, 7.
- **At Jzz = 0 (the Dicke slice, symmetry S_N) the count is larger**: 20 at N = 6, against D(6) = 12. This equals
  the C(N, N/2) zero eigenvalue of the P3(b) law, and equals sum_j d_j over S_N irreps.

**Corrections.**
1. State that D(N) = 0 for odd N, so the atom is an even-N artefact, and the 2^{-N/2} decay is along even N.
2. "Attained exactly in every Tier-1 run" holds for Jzz != 0 only. On the Jzz = 0 slice the larger S_N symmetry gives
   more atoms (for N = 6, 20 rather than 12). The theorem's "at least" is correct as stated.
3. The theorem is irrelevant for the N-first law, since D(N)/2^N -> 0. The report says this, and it is correct.

---

## P1 (graded-RWA theorem), claimed PROVED: **CONFIRMED** (scope remarks only)

**Proof check.** In the frame where n = z, H_0 = h Q with Q = Z_0 + H_D/h, and [H_sec, H_0] = 0, so U commutes with Q.
From the (1,1) and (1,0) blocks of QU = UQ: [H_D, U11] = 0, and H_D U10 = U10 (H_D + 2h). Hence K = U11^{-1} U10
maps the H_D/h eigenvalue q to q + 2. It is nilpotent, and det(U10 + lam U11) = lam^d det U11. The output-basis
change is (V_n^dag x I)U, and the input frame rotation is rigid, so the law is delta at +n for either sign of h.
The pencil is singular exactly when det U11 = 0. Correct. Part (b) is the repository charge-grading theorem, and
(g/2)(X0 X_i + Y0 Y_i) = g(s0+ s_i- + s0- s_i+) is correctly identified as the co-rotating part of g X0 X_i.

**Own check** (`c1_graded_rwa.py`). Test statistic: ptp over 300 random Omega of L1(Omega) - log(1 - n.Omega), which
is 0 for an exact delta at +n. It uses the lab-frame U and an explicit output-basis rotation.
- Tier-2 tilted field (30 deg with |h0| = 1, and 60 deg with |h0| = 1.74, both on R1), N = 4 and 5, T = 20 and 100:
  secular RWA 2.8e-14 to 1.5e-7, against 1.7 to 4.0 for the full model. The secular flip block is nonzero
  (0.07-0.24), so the delta is not trivial.
- **Arbitrary detector** (random XYZ fields and bonds, random qubit axis, h set to half a Bohr frequency of H_D,
  random three-channel coupling plus a detector-only perturbation), N = 4: 2e-14 to 1.2e-12, against 0.09 to 1.6 for
  the full model. The claim "any detector, any coupling, tilted fields" holds.

**Scope remarks (no change to the verdict).**
1. This is an exact statement about the model H_sec, which uses the exact spectral projectors of H_0. H_sec is
   therefore discontinuous in the parameters, and in N once the detector spectrum becomes dense. P1 says nothing by
   itself about open parameter sets or about the physical model at N -> infinity. Its role in P8 is motivation, not a
   proof step (see P8).
2. K is nilpotent, so the pencil is maximally non-semisimple: the kernel weight at lam = 0 is dim ker U10, which is
   less than d in general. This does not matter because the normalized law is a single point, but "algebraic = kernel
   weights" fails here.
3. Wording: "longitudinal" is listed among the grading-breaking terms. In (b), g_z Z0 M is charge-neutral. In (a),
   the secular part of every term is kept. A lab-longitudinal coupling breaks the grading only through its component
   transverse to n (tilted frame).

---

## P2 (exact counter-rotating gauge identity and sqrt(kappa) corollary), claimed PROVED: **CONFIRMED-WITH-CORRECTIONS**

**Proof check.** For S = e^{s(Z0+M)}, the co-rotating terms have Q-charge 0, s0+A+ has +4 and s0-A- has -4, so the
three terms scale by 1, e^{4s} and e^{-4s}. The block computation (SUS^-1)_10 = e^{-2s} e^{sM} U10 e^{-sM} and
(SUS^-1)_11 = e^{sM} U11 e^{-sM} is correct. Since S acts blockwise as a similarity, kernel dimensions are preserved as
well as the root multiset. The Tier-1 decomposition u = g_x + g_y, v = g_x - g_y is correct: with
Y = -i(s+ - s-), g_x XX' + g_y YY' = u(s+s'- + s-s'+) + v(s+s'+ + s-s'-). The choice e^{4s} = kappa gives the corollary
lam(u; kappa u, kappa u) = sqrt(kappa) lam(u; kappa^2 u, u).

**Own check** (`c2_gauge.py`, `c2b_gauge_matrix.py`).
- Operator identity ||U_B - S U_A S^-1|| / ||U_B|| = 3e-14 to 2.6e-13 (N = 4 and 6; kappa = 0.3 and 0.05; including
  Jzz = -0.5, g_z = 0.2, h0z = 1.74).
- As kappa -> 0, the maximal relative deviation of lam/sqrt(kappa) from the one-sided roots is 2.6e-2 / 2.7e-4
  (N = 4) and 1.1e-2 / 1.1e-4 (N = 6) at kappa = 0.1 / 0.01. This is O(kappa^2).
- The one-sided model's zero roots are semisimple: their count equals dim ker U10 = D(N) (6 and 12). The nonzero
  roots are separated.

**Corrections.**
1. "Up to a relative O(kappa^2) correction" holds when the one-sided model's roots at kappa = 0 are semisimple. This
   is true at N = 4, 5 and 6 here. Otherwise the correction is O(kappa^{2/s}). Nothing is proved uniformly in N. What
   is exact at every N is the factorization lam = sqrt(kappa) lam_1(kappa^2). Its kappa^2 -> 0 behaviour uniformly in
   N is an assumption of the same kind as H2.
2. **The correction to BRIEF C3.2 overreaches.** C3.2 and its check K3.1 concern grading breaking by h_0x ("h_0x = eps
   near g_y = g_x"), which the hypothesis "qubit field along z only" excludes. The same gauge does extend to it.
   **Referee's extension, verified:** on the charge-graded slice, h_0x s0+/- have Q-charge +/-2, and e^{2s} = eps
   gives lam(eps) = eps lam'(eps^2) exactly. Here lam' belongs to the one-sided model with h_0x s0- of unit amplitude
   (1e-13 at N = 4 and 5). So h_0x breaking is linear in eps times a one-sided model, conditional on that model's
   semisimplicity. At N = 5 the eps -> 0 convergence stalls at 3e-3 (eps = 1e-3), unresolved between conditioning and
   near-defective roots. When both v and h_0x are present the two gauges cannot be applied together, so the generic
   case stays open. The report should restrict the C3.2 correction to kappa-breaking, or add this extension.
3. Numerical caution: extracting roots from the unitary model near the graded slice is conditioning-limited. At
   N = 6 and kappa = 1e-3 the own deviation rises to 3e-3. For kappa <= 0.01 at N >= 8, slopes are better computed
   from the gauge-transformed one-sided model.

---

## P3 (sqrt(g/omega) bulk on R1; leading-order Dicke law), claimed PROVED-CONDITIONAL: **CONFIRMED-WITH-CORRECTIONS** for (a) and (b); STATUS-OVERCLAIM for the Jzz != 0 radius claim in (a); (c) is accepted as numerics, with one wrong inference

**Proof check.**
- Dyson: U10 = -i int e^{-iH_-(T-s)} g L_x e^{-iH_+ s} ds + O(g^3), U11 = e^{-iH_- T} + O(g^2), which gives
  K = -ig int e^{-2i h0z s} L_x(s) ds + O(g^3). K is exactly odd in g, since Z0 H(g) Z0 = H(-g).
- The filters F(eps_i - h0z) and F(-eps_i - h0z) are correct, with eps_i = h_z + Jzz(Z_{i-1} + Z_{i+1}).
- At Jzz = 0, K = (c S+ + d S-)/sqrtN. The conjugation t^{S_z/2} with t^2 = d/c gives sqrt(cd) S_x/sqrtN, which is
  diagonalizable, so kernel weights equal algebraic ones. Hence lam = -sqrt(cd) xi with xi binomial on a single
  meridian. The resonant modulus g sqrt(T |sin 2hT| / 2h) is correct.

**Own check** (`c3_dicke_law.py`: Jzz = 0, h_z = 1, g_x = g/sqrtN, own builder and QZ).
- g = 0.02, T = 10 on R1: median relative radius error 5.4e-3 (N = 6) and 4.0e-3 (N = 8). All nonzero roots lie on
  the predicted meridian within 1.2e-2 rad. The number of zero roots is exactly C(N, N/2) (20 and 70).
- Off R1 (h0z = 0.6): median error 7e-5.
- gT = 0.6: median error 0.23 / 0.135, maximum 0.9 / 1.4.
- gT = 1 (g = 0.1): median error 0.14 / 0.10, but the maximum grows from 6.0 to 40 between N = 6 and N = 8.
- This confirms the report's caveat directly: the bulk is N-stable, while the extreme roots lose uniformity quickly
  in N once gT = O(1).

**Corrections.**
1. The radius statements in (a) (g sqrt(T/omega_cr) on R1, g/sqrt(delta omega_cr) off R1) are **proved only at
   Jzz = 0** through (b). At Jzz != 0, write K_1 = K_+ + K_- (the M-raising and M-lowering parts). The similarity
   t^{M/2} gives spec(K_1) = spec(t K_+ + t^{-1} K_-), hence spec = sqrt(a b) spec(K_+/a + K_-/b) with a = ||K_+||
   and b = ||K_-||. That the balanced operator has an O(1), N-tight spectrum is an assumption. Label the Jzz != 0
   radius law HEURISTIC.
2. **Add a rigorous leading-order non-Born statement that the report missed.** For the law in (b), let
   x = log|lam| = log tan(theta/2), with |xi| half-normal and s = |sqrt(cd)|. The weak-Born fluctuation relation
   p(-x) = e^{2x} p(x) (BRIEF 2.1 iii) is equivalent to sinh(2x) = 4 s^2 x for all x, which is impossible.
   - So the leading-order Dicke law is **never weak-Born**, at any T, on or off R1, whatever its concentration.
   - This test uses the ratio rather than the mass, which is the kind of argument P8 needs (see P8).
3. (c) states that "as g -> 0 ... coverage going to zero". This contradicts the report's own observation that the
   tail's theta-extent is g-independent (2.7-2.97 rad). The mass of the tail shrinks, but its support does not.
   The consequences are in P8.

---

## P4 (refutation of the classical-label reduction C1.2 for root laws), claimed REFUTED: **STATUS-OVERCLAIM**, with one WRONG detail

**Proof check.** Own derivation at leading order, Jzz = 0:
- Write xi(s) = Re(w e^{2i h_z s}) with E|w|^2 = 2. Then lam_C12 = i g int xi(s) e^{-2i h0z s} ds = -(c w + d w-bar)/2.
- This real-linear image of a complex Gaussian has singular values |c| +/- |d|. It equals the quantum law
  -sqrt(cd) N(0,1) in distribution if and only if |c| = |d|.
- The mechanism, that roots see the geometric mean sqrt(cd) and not the classical sum, is correct.

**WRONG detail.** "They agree iff |c| = |d| for all T, which happens iff h0z = 0." In fact
|F(h_z - h0z)| = |F(h_z + h0z)| for all T holds iff h_z h0z = 0. The second branch, **h_z = 0** (with Jzz = 0, the
zero-detector slice), is where [H, L_x] = 0 and C1.2 is exact: the label is static, as in Theorems D and E. Replace
"iff h0z = 0" with "iff h0z = 0 or h_z = 0". The same fix applies to "for h0z != 0, C1.2 overestimates ..." and to the
"Corrections to BRIEF" item.

**Status.**
- **Exact refutation on the charge-graded slice (kappa = 0).** For every N and T the quantum law is delta_N, while
  the classical co-rotating label gives a nondegenerate Rabi law. This is the only unconditional refutation, and it
  lies on the slice the BRIEF rationale had already exempted ("defective pencils").
- **For the Tier-1 target (g_x only, kappa = 1), the refutation is leading-order in g.** It is conditional on the
  uniform-in-N spectral stability of the leading-order operator, whose similarity has condition number |t|^N. That is
  exactly the P3 caveat, and the own P3 check shows extreme-root errors growing with N at gT ~ 1.
- The small-kappa extension is conditional on tightness, as the report says.
- The header should read: "C1.2 refuted exactly at kappa = 0; refuted at leading order at kappa = 1, conditional on
  spectral stability; strongly disfavoured by N <= 10 numerics".
- The statement "C1.2 is exact for trace quantities (infinite-temperature quantum CLT)" is asserted, not proved here.
  Label it standard or heuristic; the numerical support is 3 digits.

---

## P5 (Jensen gap), claimed PROVED: **CONFIRMED-WITH-CORRECTIONS**

1. **"Necessary ... for a nondegenerate law" is false as stated at large N.**
   - Jensen saturation L1 -> log p1 yields the aberration law (1 - m^2)/(4 pi (1 - m cos theta')^2), which is
     nondegenerate for 0 < |m| < 1 (BRIEF 2.1 ii).
   - The correct statement is BRIEF 2.1(v): an O(1) gap is necessary for a nondegenerate **Born** law.
   - At finite N, G = 0 forces E1 to be scalar almost everywhere, hence delta. That argument gives only G > 0, not
     G = O(1).
2. **Non-sufficiency can be proved analytically, with no numerics.**
   - E1(Omega) = 1/2[(1+z)A + (1-z)B + (x+iy)C + (x-iy)C^dag] is affine in the Cartesian components of Omega.
     Therefore it is scalar either on the whole sphere or on a null set.
   - In any P1 model with a nonzero secular flip, det U10 = det U11 det K = 0 and U10 != 0. So E1(north) = U10^dag U10
     is not scalar, and G > 0 strictly.
   - Only the value G = O(1) (1.69-1.70) is numerical.
3. "Carries no information about calibration" is rhetorical. State instead that G is not a Born indicator.

---

## P6 (repelling fixed point on R1), NUMERICAL: **accepted for Tier 1; STATUS-OVERCLAIM for the Tier-2 "does not exist"**

1. **Topology.** Antipodality gives C_0(-n) = -C_0(n), so Phi(-n) = -Phi(n): Phi is odd. A continuous odd map
   S^2 -> S^2 has odd degree. By Lefschetz (L(f) = 1 + deg f, and deg(-f) = -deg f), there is always an n with
   Phi(n) = +n or Phi(n) = -n.
   - `v8_phi_scan.py` measures arccos(Phi(n).n), a signed angle, and prints only the minima.
   - If deg Phi = -1, the fixed points are anti-fixed points. These are not Born-consistent, but they must exist and
     should be reported (maximum residual near 180 deg).
   - If deg Phi = +1 (its value at g -> 0, where Phi is a rotation), a fixed point exists and the 200-point grid
     (spacing about 14 deg, local Lipschitz constant up to 55) missed it.
   - The degree can change only through singular n, where n_raw = 0 or the guard refuses. So the claim needs either
     the maximum residual plus a search for B1 -> 0, or a continuation in g from g = 0.
2. The Tier-2 claim rests on a single (N, T) = (6, 100) and on 15-step non-convergence. The Tier-1 finite-difference
   Jacobian at 0.5 deg with |rho| up to 55 is outside the linear regime, so quote angle(Phi(n), z)/delta against delta,
   as v9 does.
3. The N-trend 8.1 / 4.0 / 2.9 at T = 100 points toward marginality (the report says so). Replace "does not exist on
   R1 at accessible N" with "not found at N = 6 (Tier 2); z is non-attracting at N <= 10 at most T (Tier 1)".

---

## P7 (XXZ band, Tier-5 energy grading), HEURISTIC: **plausible; (a) exact part and (b) CONFIRMED**

- (a) XXZ = Jp(XX + YY + ZZ) + (Jzz - Jp) ZZ, and [S^+, Heisenberg] = 0, so only the anisotropy dresses L_+. This is
  exact. The reported widths scale linearly: sd/|Jzz - Jp| = 2.85, 2.65, 2.78. The width statement itself is
  numerical.
- (b) Follows from P1 and P2, since M is conserved when Jxx = Jyy and there is no transverse detector field.
- (d) is the Tier-5 claim and is correctly labelled HEURISTIC. **A route to a proof, verified.** In the qubit-field
  frame the energy gauge S = e^{s(Z0 + H_D/h)} = e^{s H_0/h} is an exact similarity for **any** detector, since
  [Z0, H_D] = 0. It rescales each Bohr component V_omega by e^{s omega/h} and the roots by e^{-2s}, so
  lam(V) = e^{2s} lam(V_s). Own check: 8e-14 and 5e-13 with a random XYZ detector and random three-channel coupling
  (`c5_energy_gauge.py`).
  - P2 is the special case obtained by replacing H_D/h with M.
  - If the coupling's Bohr frequencies split into a co-rotating band near 0 and counter-rotating bands near
    +/-(2|h0| + band), separated by a gap, the gauge produces the sqrt(g/omega_off) dilation structure. It rests on
    the same one-sided-model hypothesis as P2.
  - Without such a gap there is no dilation structure, and (d) is genuinely open.

---

## P8 (late-time law and go/no-go verdict), claimed PROVED-CONDITIONAL under H1 + H2: **GAP** (not closable with H1 + H2), plus STATUS-OVERCLAIM

**1. The central inference is invalid.** P8 argues that H2 gives weak convergence to delta as g -> 0, and that a
delta law is Born only vacuously and fails coverage. Both SPEC criteria are density ratios, rho0/(rho0 + rho1) and the
ratio of the normalized polar marginals (`SPEC.md` §5.1-5.2). They do not depend on how mass is split between a
concentrated bulk and a tail, and Born laws can be arbitrarily concentrated while keeping full coverage.

**Counterexample family** (exactly strong-Born, hence weak-Born, at every g):
- Take any density on the northern hemisphere, for example f_g = (1 - eps_g) cap_{r_g} + eps_g Unif(north), with
  r_g = sqrt(g) and eps_g = g^{1/2}.
- Put rho0(Omega) = Z^{-1}[f_g(Omega) 1{theta < pi/2} + tan^2(theta*/2) f_g(-Omega) 1{theta > pi/2}], where theta* is
  the polar angle of -Omega.
- Then rho0(-Omega) = tan^2(theta/2) rho0(Omega), so the law is strong-Born exactly.
- Its support is all of S^2 (coverage 100/100). Its bulk radius scales as sqrt(g), and it converges weakly to delta_N
  as g -> 0.

So "tight at scale sqrt(g/omega)" plus "tends to delta" is fully compatible with exact Born. The verdict does not
follow from H1 + H2. What does exclude Born is a **ratio defect**: the south-hemisphere mass must equal
E[e^{2x}; x < 0] (the Born fluctuation relation), and more finely, bin by bin. H2 says nothing about this, because it
constrains only the bulk. The same objection applies to P3(c) ("degenerate pass with coverage going to zero") and to
the GOAL answer "Both tend to delta ... degenerate pass that fails coverage".

**2. Own reproduction of the ratio defect** (`c4_fr_test.py`: own builder and QZ, R1 with h0z = h_z = 1, Jzz = 0.37,
g_x = 0.1/sqrtN, single times, z basis, which is the exact Pi fixed point).
- South mass / Born prediction is 0.97 / 1.53 / 2.19 at T = 20 and 2.92 / 0.64 / 0.22 at T = 100, for N = 6 / 8 / 10.
  This reproduces the report's numbers to the digit.
- E tan^2(theta/2) is 4.21 / 2.10 / 1.42 (T = 20) and 0.137 / 0.238 / 0.119 (T = 100). The Born value is
  1 - (north atom) = 0.81 / 0.90 / 0.945.
- The defect is real at N <= 10, but its **sign depends on T** (the south is too heavy at the swap time and too light
  at T = 100).
- At T = 20, E tan^2 trends toward its Born value as N grows, while the hemisphere ratio trends away from it. The
  data therefore do not determine the N -> infinity outcome.
- This is the right evidence, but it is NUMERICAL at 64-1024 roots.

**3. Order of limits.**
- H2 is stated at fixed tau = gT, with g -> 0. That is a van Hove-type scaling.
- The SPEC order is N -> infinity at fixed T, then T -> infinity at **fixed g** (`SPEC.md` §7.1; T does not scale
  with g, `SPEC.md:65`). That order needs control uniformly in tau in [tau_0, infinity), which H2 does not provide.
- The report labels the T -> infinity statements HEURISTIC, but the headline verdict is itself a T -> infinity
  statement, so it cannot be PROVED-CONDITIONAL under H1 + H2.
- Even granting everything, the argument excludes Born only for g < g_0(tau, ...), with g_0 unspecified. The code's
  perturbative gate of 0.1 is covered only by numerics.

**4. H2 carries the conclusion for the bulk.** Tightness of r/sqrt(g/omega) uniformly in g is essentially the
bulk statement itself. P1 is about a different model (H_sec), and P2 relates models along kappa, not along g, so
neither is a step in a proof of the g -> 0 statement. They motivate it.

**5. The codimension-1-in-kappa claim is only asymptotic.** The correct part is a lemma, with proof supplied here.
- *Lemma.* Let P be a law on x = log tan(theta/2) in [-inf, inf] that satisfies the Born fluctuation relation
  P(-dx) = e^{2x} P(dx). Suppose its shift by c != 0 (the dilation lam -> e^c lam) satisfies it too. Then
  P(A + 2c) = e^{-2c} P(A) for every Borel A. Summing over the translates of a fundamental domain forces P(R) = 0,
  so P = delta_N.
- *Consequence.* An exact dilation family is Born for at most one dilation.
- *Limitation.* The kappa-family is D_{sqrt kappa} mu_1(kappa^2), a dilation only up to O(kappa^2). The lemma
  therefore excludes a Born interval only as kappa -> 0, and says nothing near kappa = 1, the Tier-1 point. Label
  the claim HEURISTIC.

**Fix.** Replace H2 by a ratio hypothesis, for example
(H2') liminf_N |P_N(x > 0) / E_N[e^{2x}; x < 0] - 1| >= eta > 0 uniformly for T >= T_0, at fixed small g, or a binned
version. Add H1. The verdict is then conditional on H1 + H2', and H2' is the substantive open claim, supported only by
N <= 10 numerics. In the leading-order regime the P3 correction 2 (sinh(2x) != 4 s^2 x) proves non-Born rigorously at
Jzz = 0. That is the model for a ratio-based argument. **Overall status of P8: HEURISTIC with NUMERICAL support**
(N <= 10). The exact ingredients (P1, P2) are correct but do not carry the no-go.

---

## Answers-to-GOAL and "Corrections to BRIEF": mathematical issues

- **Q5, "h0z = h_z is neither necessary nor sufficient".** Under the report's own no-go, every condition is
  vacuously necessary (Born implies anything). The content is "not sufficient", together with the heuristic
  statement that R1 membership, on any of its three sheets, separates the sqrt(g) regime from the O(g) regime.
- **"Do N -> infinity and g -> 0 commute? For the bulk, yes."** The support is the exact finite-N factorization
  (P2) plus N <= 10 numerics. Say "numerically consistent at N <= 10". The own P3 check shows extreme-root errors
  growing from 6 to 40 between N = 6 and 8 at gT = 1.
- **"Upgrades Theorem I's leading-order statement to all orders."** What is exact at all orders is the sqrt(kappa)
  factorization. "Radii depend only on sqrt|g_x^2 - g_y^2|" is not upgraded, because the O(kappa^2) term depends on
  kappa separately. "g_y enters only through kappa" holds at fixed u = g_x + g_y.
- **"Multichannel coupling cannot seed a Born region"** and **"it disappears"** both rest on P8, so both are
  HEURISTIC.
- **Correction to C3.2:** it covers kappa-breaking only (see P2, correction 2).
- **Correction to C1.2:** amend it to "iff h0z = 0 or h_z = 0" (see P4).

---

## Summary

| Prop | Claimed | Verdict |
|---|---|---|
| P0 | PROVED | CONFIRMED-WITH-CORRECTIONS (D(N) = 0 for odd N; more atoms on the S_N slice Jzz = 0) |
| P1 | PROVED | CONFIRMED (own check, including an arbitrary detector; statement about H_sec only) |
| P2 | PROVED | CONFIRMED-WITH-CORRECTIONS (O(kappa^2) needs semisimple one-sided roots; no N-uniformity; C3.2 correction covers only kappa-breaking; referee's h_0x extension lam = eps lam'(eps^2) verified) |
| P3 | PROVED-COND. | (a), (b) CONFIRMED at Jzz = 0; the Jzz != 0 radius law is HEURISTIC (STATUS-OVERCLAIM); "coverage -> 0" is wrong; add the rigorous leading-order non-Born result sinh(2x) != 4 s^2 x |
| P4 | REFUTED | STATUS-OVERCLAIM (exact only at kappa = 0; leading-order and conditional at kappa = 1); WRONG detail: agreement iff h0z = 0 **or h_z = 0** |
| P5 | PROVED | CONFIRMED-WITH-CORRECTIONS ("necessary for nondegenerate *Born*", not "for nondegenerate": aberration counterexample; non-sufficiency provable analytically) |
| P6 | NUMERICAL | accepted for Tier 1; the Tier-2 "no fixed point" is STATUS-OVERCLAIM (odd-degree/Lefschetz: a fixed or anti-fixed point exists wherever Phi is continuous; coarse grid, one (N, T)) |
| P7 | HEURISTIC | plausible; (a) exact part and (b) CONFIRMED; proof route for (d) via the exact energy gauge e^{s H_0/h} (verified) |
| P8 | PROVED-COND. | GAP: H2 does not imply non-Born (explicit exactly-Born, fully covered, delta-converging family); the fixed-tau scaling does not reach the SPEC order; the codimension-1-in-kappa claim is asymptotic only. Correct status: HEURISTIC + NUMERICAL (N <= 10) |

Scripts: `own.py`, `c0_parity_atoms.py`, `c1_graded_rwa.py`, `c2_gauge.py`, `c2b_gauge_matrix.py`, `c3_dicke_law.py`,
`c4_fr_test.py`, `c5_energy_gauge.py`, each with a `.log` file. All use N <= 10 and single runs of 80 s or less.
