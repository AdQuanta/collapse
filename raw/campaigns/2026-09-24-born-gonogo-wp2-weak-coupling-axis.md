# WP2: weak-coupling preferred axis and off-resonance caps

> Source: Agent work-package report, go/no-go derivation workflow (scratchpad `gonogo/wp/WP2/REPORT.md`), 2026-09-24. Derivations and bornkit numerics (N <= 10); not refereed unless stated. The report was interrupted by a usage limit in places; content preserved verbatim.
> Collected: 2026-09-24
> Published: 2026-09-24

# WP2 report: weak-coupling preferred axis and the off-resonance degenerate pass

Status: COMPLETE (2026-09-24). Conventions: SPEC positive convention (BRIEF 1.1) unless "code" is
stated; bornkit `build_H` for every Hamiltonian; outcome-0 roots of the forward pencil; unit weights.
Notation: H = H_0 + V, H_0 = h0.sigma_0 + H_D, V = sum_a g_a sigma_0^a (x) B_a (ring B_a = s_a sum_i sigma_i^a,
chain B_a = sigma_1^a); u_q(T) = exp(-i T h0.sigma); R_T = its SO(3) rotation (angle 2|h0|T about h0_hat);
in an output basis n: U_{-+} = <-n|U|+n>, U_{--} = <-n|U|-n> (detector operators), d = 2^N.

## Skeleton (one heading per proposition)
- P2.1 g -> 0 fixed-point theorem (single T and six-time pool)
- P2.2 CS-angle root lemma (exact, any unitary): root half-angles are log-majorized by the CS angles of U_{-+}
- P2.3 Fixed-T cap theorem (Duhamel): chain in operator norm, ring in HS / measure form
- P2.4 Off-resonance cap uniform in T (Schrieffer-Wolff / first-order filter) and the prethermal gap
- P2.5 First and second order: what shifts the axis (trace cancellation, static-field covariance, Lamb shift)
- P2.6 h0 = 0 selection rule (secular QND axis; Mazur projection gives g o h_D) and order of limits
- P2.7 Basis dichotomy: fixed-point basis = degenerate cap; any other basis = kinematic cone + O(g)
- P2.8 Numerics: K2.1-K2.3 (Tier-2 ring), K5.1, cap radius vs g and T (screen_00 chain; tilted ring)
- P2.9 Reinterpretation of the preferred-basis campaign at screen_00
- Answers to GOAL questions, open items, surprises

---

## P2.1 g -> 0 fixed-point theorem

**Setting.** Fixed N (ring or chain), fixed T or a finite pool 𝒯 = {t_k} (canonical: the six times of BRIEF 1.3).
H = h0·σ_0 + H_D + gV, |h0| > 0, a := ĥ0 (SPEC). Two axis fits are used: the repository dipole fit
n̂_fit = S⁻¹m/|S⁻¹m| (BRIEF 1.4; this is Φ in `wiki/concepts/collapsible-basis-dependence.md:79-103`) and, as a
diagnostic, the centroid n̂_c = Σ_j u_j/|Σ_j u_j|.

**Statement.**
(i) At g = 0 every outcome-0 root in output basis n sits at R_T⁻¹n with multiplicity d (point mass), for every
detector and every N. The single-time map is Φ_T(n) = R_T⁻¹n, a rotation by −2|h0|T about a. Its fixed points are
exactly ±a when |h0|T ∉ πZ; when |h0|T ∈ πZ (u_q = ±I) every n is fixed. The tangent Jacobian at ±a is the rotation by
∓2|h0|T, so at g = 0 the fixed point is **neutral (elliptic), not attracting**.
(ii) Pool, dipole fit: the g = 0 cloud {R_{t_k}⁻¹n} lies on the cone a·Ω = a·n, so by the cone lemma
Φ_𝒯(n) = sign(a·n)·a in **one step** for every n with a·n ≠ 0, provided the phases 2|h0|t_k mod 2π take at least
three distinct values (then S is invertible). The pooled fixed points ±a are superattracting at scales large compared
with the cap radius. Exceptions: n ⊥ a (the points span a plane and S is singular); pools whose phases take ≤ 2 values.
Pool, centroid: Φ_c(n) = normalize(M n), M = (1/K)Σ_k R_{t_k}⁻¹. This contracts transverse components by
c = |(1/K)Σ_k e^{2i|h0|t_k}|, so it is attracting iff c < 1.
(iii) Small g ≠ 0 (fixed N and T): if |h0|T ∉ πZ, the equation Φ(n) = n has a unique solution n*(g) near a with
n*(g) − a = (R_T⁻¹ − I)⁻¹|_{a⊥} δ(a) + ..., where δ is the O(g) displacement of the fit and
‖(R_T⁻¹−I)⁻¹|_{a⊥}‖ = 1/(2|sin(|h0|T)|). The shift is therefore enhanced near the exceptional times. For the centroid
fit δ = O(g²), because the first-order centroid vanishes by the trace (P2.5). For the dipole fit δ = O(g) generically,
because the fit responds to the third moment of the O(g) cap (P2.5).

**Status.** (i) and (ii) PROVED. (iii) PROVED for the centroid fit by the implicit-function theorem. Roots are
continuous in g (the g = 0 pencil is regular with a single d-fold root), and the centroid is smooth wherever the
resultant is positive. For the dipole fit (iii) is PROVED-CONDITIONAL on a bounded aspect ratio of the O(g) cap as
g → 0, i.e. λ_max/λ_min of its transverse covariance stays bounded; otherwise the fit is not continuous at point masses.

**Proof.**
(i) At g = 0, <−n|U|ψ,D> = <−n|u_q|ψ>·u_D|D>. This has a kernel iff <−n|u_q|ψ> = 0, i.e. |ψ> ∝ u_q†|+n>, whose Bloch
vector is R_T⁻¹n. The rest is linear algebra of SO(3).
(ii) Cone lemma (BRIEF 1.4): if a·u_j = cos α for all j, then S(a/cos α) = Σ u_j(u_j·a)/cos α = m. Three distinct
points on a circle that does not pass through the origin (cos α ≠ 0) are linearly independent, so S is invertible.
For the centroid, M acts on a⊥ as the mean of plane rotations, (1/K)Σ e^{−2i|h0|t_k} in complex notation.
(iii) Let F(n, g) = Φ(n) − n on the tangent plane. D_nF(a, 0) = R_T⁻¹ − I is invertible on a⊥ iff
2|h0|T ∉ 2πZ. ∎

**Numerical check.** Script `t2_fixed_point.py`; output `t2_fixed_point_N6.json` and `t2b_N8.log`.
- **Hamiltonian:** screen_00 chain in SPEC convention (BRIEF 1.1, every code sign flipped) with all three g_a × ε;
  builder bornkit.build_H; no ring scaling.
- **Method:** Newton (fsolve) on Φ(n) = n in tangent coordinates about ĥ0, then a finite-difference Jacobian.
- **Times:** single T ∈ {1.2, 5, 20}, chosen short so that εgT ≪ 1 (the perturbative regime of (iii)), plus the
  canonical pool. BRIEF 4 gives screen_00 t_H = 60/193 at N = 8/10, extrapolating to ≈ 19 at N = 6. So
  T/t_H ≈ 0.06/0.26/1.0 for T = 1.2/5/20 at N = 6 (0.33 at T = 20, N = 8), while the pool (T/t_H = 5–50) is
  reverse-order.

Angles are in degrees.

| N=6 | ε=0.01 | 0.03 | 0.1 | 0.3 | 1 |
|---|---|---|---|---|---|
| T=5, centroid: ∠(n*, ĥ0) | 6.9e-6 | 6.2e-5 | 6.9e-4 | 6.2e-3 | 6.9e-2 (∝ ε²) |
| T=5, dipole fit: ∠(n*, ĥ0) | 4.9e-4 | 1.4e-3 | 4.3e-3 | 1.0e-2 | 8.0e-2 (∝ ε) |
| T=20, centroid: 1 − \|Jacobian eig\| | ≈0 | 2e-4 | 1.9e-3 | 1.7e-2 | 0.18 (∝ ε²) |
| pool, centroid: \|Jac eig\| | 0.83 | 0.74 | 0.42 | 0.11 | 0.016 |
| pool, fit: ∠(n*, ĥ0) | 1.7e-2 | 3.7e-2 | 3.6e-2 | 3.9e-2 | 8.7e-2 |

- At T = 1.2 and T = 5 the single-time centroid Jacobian has |eig| = 1.0000 for ε ≤ 0.1: neutral, as (i) says.
- The pooled centroid contraction as ε → 0 is 0.83, against the predicted c = 0.842 (`t5_pool_onestep.py`).
- One pooled step with the dipole fit (`t5_pool_onestep.py`, N = 6) starting 5° and 30° off ĥ0 lands at 1e-4° and
  1e-4° from ĥ0 at ε = 1e-4 (superattraction). The kinematic B1 values are 1.0038 = 1/cos 5° and 1.1547 = 1/cos 30°.
  At ε = 0.1 and 1 the same step gives 3.4° and 3.9°, because the caps are then wide on the pool times
  (εgT ≈ 1–100) and the cone lemma no longer controls the fit.
- **N = 8, T = 20.** At ε = 0.03/0.3/1 the centroid gives 1.4e-4/1.4e-2/0.15° and the fit 7.0e-4/2.4e-2°. These are
  the same order as N = 6; exact N-independence is expected only while N ≳ 2v_LR·T, so T = 20 is partly reverse-order.
- **N = 8, pool.**
  - ε = 0.03: fit 1.4e-2°, |J| 0.80; centroid 8.2e-3°, |J| 0.77.
  - ε = 0.3: fit 4.9e-2°, |J| 0.20.
  - **ε = 1: fit 0.515° with |J| = 1.36, a repelling focus; centroid 0.035°, |J| 0.075.**

**Intuition.** Free precession about ĥ0 is an isometry of the sphere. A single time can only rotate the basis, so
nothing attracts at g = 0. Attraction at one time comes from dephasing of the precession angle across detector blocks,
at O(g²T²). Pooling different times averages rotations, which contracts.

**Failure modes.**
- The dipole-fit fixed point carries an O(g) offset that the centroid does not. The "preferred axis" is therefore
  fit-dependent at O(g). Neither offset is Born evidence.
- Near |h0|T ∈ πZ the fixed point is ill-conditioned (enhancement 1/(2|sin |h0|T|)).
- The g → 0 statements need εgT ≪ 1. On the canonical pool with the physical g they fail: gT reaches 100.

---

## P2.2 CS-angle root lemma (exact, any unitary, any basis)

**Statement.** Let U be unitary on C²⊗C^d, fix an output axis n, and write the CS decomposition in the basis
(|+n>, |−n>): U_{-+} = W S V_1†, U_{--} = W C V_2†, with S = diag(sin Θ_j), C = diag(cos Θ_j), Θ_j ∈ [0, π/2].
Here sin²Θ_j are the eigenvalues of the flip effect E(n) = U_{-+}†U_{-+} = E1(n) in BRIEF 2.1 notation.

Assume U_{--} is invertible (all Θ_j < π/2). The outcome-0 roots in basis n are the Ω_j with tan(θ_j/2) = |λ_j|, where
θ_j = ∠(Ω_j, n) and λ_j are the eigenvalues of X = −U_{--}⁻¹U_{-+} = −V_2 (tan Θ) V_1†. The singular values of X are
exactly tan Θ_j. Consequences:
- **(a) Weyl.** Π_{j≤k} tan(θ_(j)/2) ≤ Π_{j≤k} tan Θ_(j) for all k, both sequences sorted decreasingly. In particular
  **θ_max/2 ≤ Θ_max**, i.e. sin(θ_max/2) ≤ ‖U_{-+}‖_op (all roots lie in that cap).
- **(b)** For every convex increasing f, Σ_j f(log tan(θ_j/2)) ≤ Σ_j f(log tan Θ_j). With f = exp(2·):
  Σ_j tan²(θ_j/2) ≤ Tr[E(1−E)⁻¹].
- **(c) Measure form.** For 0 < ρ' < ρ < 1,
  `#{j : tan(θ_j/2) > ρ}/d ≤ [ p(n)·log(1/ρ')/ρ'² + ½ ℓ(n) ] / log(ρ/ρ')`, where
  - `p(n) = (1/d)Tr E(n)` is the infinite-temperature flip probability, equal to p1(n) of BRIEF 2.1;
  - `ℓ(n) = −(1/d)log det(1−E(n)) ≥ p(n)` is the log tail of the other-outcome effect at the single point Ω = n.

If U_{--} is singular, dim ker U_{--} roots sit at the antipode −n; apply the lemma to the rest.

**Status.** PROVED.

**Proof.**
- **CS form of X.** From the CS decomposition, X = −V_2C⁻¹W†WSV_1† = −V_2 tan Θ V_1†.
- **Roots.** Outcome 0 in basis n requires det(αU_{-+} + βU_{--}) = 0 for |ψ> = α|+n> + β|−n>. With λ = β/α this is
  det(X − λ) = 0, and |λ| = tan(θ/2).
- **(a), (b).** Weyl's majorant theorem (log-majorization of eigenvalue moduli by singular values) and its standard
  consequence for convex increasing functions of the logarithm.
- **(c).** Take f(t) = (t − log ρ')₊ in (b). Each root with tan(θ/2) > ρ contributes at least log(ρ/ρ'). Next,
  log⁺(tan Θ/ρ') ≤ 1{sin Θ > ρ'}·log(1/ρ') + log(1/cos Θ), and Chebyshev gives #{sin Θ_j > ρ'} ≤ d·p/ρ'².
  Finally Σ_j log(1/cos Θ_j) = (d/2)ℓ. ∎

**Numerical check.** Script `t1_cs_lemma.py`.
- **Cases:** a Haar unitary (d = 64), and screen_00 (chain, SPEC, N = 6, build_H) at T = 5 and T = 300, each in bases
  z, ĥ0 and a generic axis. T = 300 is reverse-order: T/t_H ≈ 16 at N = 6.
- **Results:**
  - SVD(X) = tan Θ to ≤ 1.6e-12 (relative).
  - The Weyl partial sums hold to rounding (max +6e-14).
  - tan(θ_j/2) = |λ_j| to ≤ 4e-13.
- **The operator-norm cap can be very loose.**
  - screen_00, T = 5, ĥ0 basis: roots within sin(θ_max/2) = 0.054, but ‖U_{-+}‖ = 0.356.
  - At T = 300: 0.113 versus 0.974. A few detector states flip the qubit almost completely, while every root stays
    within 13° of the pole.

**Intuition.**
- The root radius is the flip amplitude conditioned by the no-flip block. The worst detector state bounds every root,
  and the typical state bounds the typical root, up to the log tail ℓ.
- The measure form (c) needs only the log tail at a single point (the pole). The Born question needs uniform L¹
  control of L1 over the whole sphere (the named obstruction G1).

**Failure modes.** (c) is useless when E(n) has eigenvalues exponentially close to 1, because ℓ is then unbounded
relative to p. In the ring this happens for rare, strongly magnetized detector states once gT√N ≳ 1.

---

## P2.3 Fixed-T cap theorem (Duhamel) in the fixed-point basis

**Statement.** Let a = ĥ0 and split V = V_∥ + V_⊥, where V_∥ = P_+VP_+ + P_−VP_− (P_± = |±a><±a| ⊗ I) commutes with
a·σ_0. For all T:

`‖U_{-+}(T)‖_op ≤ T‖V_⊥‖_op` and `p(a; T) = (1/d)‖U_{-+}(T)‖²_HS ≤ T²(1/d)Tr_{2d}V_⊥² = 2T²Σ_a g_a²(1−a_a²)β_a`,

where β_a = (1/d)Tr B_a²: chain 1; ring s_a²N, i.e. 1 at 1/√N and 1/N at 1/N.

- **Chain, operator norm, uniform in N.** Every root in the ĥ0 basis satisfies
  sin(θ/2) ≤ T·Σ_a|g_a|√(1−a_a²), for every N. This survives N → ∞ at fixed T (the SPEC order). screen_00: the sum is
  0.174, so the cap is nontrivial for T < 5.7.
- **Ring, HS / measure form.** p ≤ 2T²Σ g_a²(1−a_a²) at 1/√N and ≤ 2T²Σ g_a²(1−a_a²)/N at 1/N. The fraction of roots
  outside a cap follows from P2.2(c), conditional on the pole log tail ℓ(a) ≤ K·p(a). At 1/N the conditional N-first
  law at fixed T is δ_{±ĥ0}, consistent with BRIEF 1.2.

**Status.**
- Chain operator-norm bound: PROVED.
- Ring HS bound: PROVED.
- Ring measure-level cap: PROVED-CONDITIONAL on ℓ(a) ≤ K·p(a). The op-norm route fails because ‖V_⊥‖_op grows like
  g s N (g√N at 1/√N).

**Proof.** Let U_∥ = exp(−iT(H_0 + V_∥)); it is block diagonal in P_±. Duhamel gives
U(T) = U_∥(T) − i∫_0^T U_∥(T−s)V_⊥U(s)ds, so U_{-+}(T) = −i∫_0^T P_−U_∥(T−s)V_⊥U(s)P_+ ds.

Take norms under the integral: ‖·‖_op ≤ ‖V_⊥‖_op, and ‖·‖_HS ≤ ‖V_⊥U(s)P_+‖_HS ≤ ‖V_⊥‖_HS. The qubit trace gives
Tr_q((σ^a)_⊥(σ^b)_⊥) = 2(δ_ab − a_a a_b), and the B_a are HS-orthogonal for a ≠ b. For the chain,
‖σ^a_⊥ ⊗ σ_1^a‖ = √(1−a_a²). ∎

**Numerical check.** Script `t4_cap_scan.py`; data in `t4_chain.jsonl` and `t4_ring.jsonl`; discussion in P2.8.
- At T = 1 the screen_00 (ε = 1) ĥ0-basis cloud has θ_rms = 2.59° and θ_max = 3.7° at both N = 6 and N = 8.
- The theorem gives sin(θ/2) ≤ 0.174, i.e. θ_max ≤ 20°: it holds, with a factor of about 5 of slack.
- The N-independence at T = 1 (identical to 3 digits) is the light-cone statement.

---

## P2.4 Off-resonance cap uniform in T, and the prethermal gap

**Setting.**
- H = H_0 + gV with V normalized (g factored out, unlike P2.3). a = ĥ0 and H_0 = |h0| a·σ_0 + H_D, with the flip
  coupling written as P_+VP_− = |+a><−a| ⊗ Y.
- **First-order non-resonance (NR_1, margin δ).** The Sylvester equation 2|h0|Z − [Z, H_D] = Y, i.e.
  Z_{EE'} = Y_{EE'}/(2|h0| + E − E'), has a solution with ‖Z‖_op ≤ κ‖Y‖_op/δ (operator version) or
  |Z|_2 ≤ |Y|_2/δ (HS version, |X|_2² = (1/d)Tr X†X).
  - The HS version holds iff |2|h0| + E − E'| ≥ δ whenever Y_{EE'} ≠ 0.
- Set A = |+a><−a| ⊗ Z − |−a><+a| ⊗ Z†. It is anti-Hermitian, block-off-diagonal, and satisfies [A, H_0] = −V_⊥.

**Statement (SW cap).**
- **Operator version.** Under NR_1, for all T ≥ 0,
  `‖U_{-+}(T)‖_op ≤ 2g‖A‖ + g²‖A‖² + g²T(‖[A,V]‖ + ½‖[A,V_⊥]‖) ≤ 2gκ‖Y‖/δ + O(g²/δ²) + 3g²κ‖Y‖‖V‖T/δ`.
  By P2.2(a), every ĥ0-basis root obeys sin(θ/2) ≤ that bound.
- **HS version.** √p(a;T) ≤ 4g|A|_2 + g²T(|[A,V]|_2 + ½|[A,V_⊥]|_2), for the ring.
- **Consequence.** The cap grows at rate O(g²/δ), not at the Duhamel rate O(g). It stays below any fixed r while
  T ≤ rδ/(3g²κ‖Y‖‖V‖), i.e. **up to T ~ δ/g²**. The O(g/δ) offset is uniform in T.
- **k-th order.** If the Schrieffer–Wolff step can be iterated k times, i.e. NR_j holds for all processes with
  ≤ j vertices and margins δ_j (j ≤ k), the growth rate becomes O(g^{k+1}) and the window grows to T ~ g^{−(k+1)}.

**First-order filter, explicit (Ising ring, g_x only, h0 tilted by τ from z in the x–z plane).**
- The flip term X_i picks up the Bohr phase of the flip energy 2σε_m, with ε_m = h_z + mJ_zz, m = z_{i−1}+z_{i+1}
  ∈ {−2, 0, 2} (probabilities ¼, ½, ¼) and σ = ±1.
- Exactly at first order, with |F_T(Δ)| = |e^{iΔT}−1|/|Δ| ≤ 2/|Δ| and Δ'_{σm} = σε_m − |h0|:
  `p^{(1)}(a;T) = g_x² s² N cos²τ · ½Σ_σ Σ_m P(m) sin²(Δ'_{σm}T)/Δ'_{σm}² ≤ g_x² s² N cos²τ/δ_1²`,
  where δ_1 = dist(|h0|, {|ε_m|}) is the distance to the first-order resonance set R1. BRIEF C1.1 is generalized
  here: the condition is |h0| = |ε_m| for **any** tilt, since only the qubit splitting enters.
- This is uniform in T and N at 1/√N, and O(1/N) at 1/N.
- NR_1 holds in HS with δ = 2δ_1 because the Ising Bohr frequencies are exactly ±2ε_m.
- For h_z = J_zz the whole detector spectrum lies on the lattice 2Z. Multi-flip resonances then sit only at integer
  |h0|: odd ℓ-flip processes give odd |h0|; even ℓ needs a longitudinal vertex, i.e. tilt τ ≠ 0, and gives even |h0|.
  So NR_k holds **for all k with one margin** when |h0| ∉ Z, and there are no small divisors.
- For incommensurate h_z/J_zz the resonance set {p·h_z + 2q·J_zz} is dense (p odd for ℓ odd). The NR_k margins then
  shrink with k: this is the prethermal gap.

**Status.**
- SW cap (operator and HS versions, all T): PROVED under NR_1 (and NR_k for the k-th order extension).
- Explicit first-order Ising formula: PROVED.
- NR_k for all k in the commensurate Ising ring off Z: PROVED as a non-resonance statement, but only the formal SW
  series is controlled order by order. Uniform-in-T control to all orders (convergence) is **not** claimed.
- Interacting detectors: HEURISTIC; see "Where it breaks" below.

**Proof (SW cap).**
1. Let H' = e^{gA}He^{−gA}. Using the integral forms of e^{sA}Xe^{−sA} and [A, H_0] = −V_⊥ gives exactly
   H' = H_0 + gV_∥ + R, with
   `R = g∫_0^g e^{sA}[A,V]e^{−sA}ds − ∫_0^g∫_0^s e^{rA}[A,V_⊥]e^{−rA}dr ds`,
   so ‖R‖ ≤ g²‖[A,V]‖ + ½g²‖[A,V_⊥]‖. The same holds in HS norm, by unitary invariance.
2. H' − R_⊥ commutes with a·σ_0. By the Duhamel step of P2.3, ‖U'_{-+}(T)‖ ≤ T‖R_⊥‖ ≤ T‖R‖, where U' = e^{−iTH'}.
3. U = e^{−gA}U'e^{gA}. Write e^{±gA} = I + Δ_±, with ‖Δ_±‖ ≤ g‖A‖ and ‖Δ_±‖_HS ≤ g‖A‖_HS since A is normal.
   Expanding and taking the flip block gives the bound. For the HS version, ‖Δ_−U'Δ_+‖_HS ≤ 2‖Δ_+‖_HS. ∎
4. The Ising formula: W^{(1)}_{-+} = −ig_x s ε_x Σ_i ∫_0^T e^{−2i|h0|s}X_i(s)ds, with |ε_x|² = 1 − a_x² = cos²τ.
   Cross terms i ≠ j vanish under the trace because they are off-diagonal in the z basis. ∎

**Where the uniform-in-T prediction breaks.**
- **(1) First-order resonance.** Ising at |h0| = |ε_m|; an interacting detector with 2|h0| inside the local band of
  the flip operator. NR_1 then fails and the growth is secular:
  - discrete, degenerate Ising spectrum: coherent, p ∝ T²;
  - continuum (N → ∞ interacting): golden rule, p ≈ ΓT with Γ = 2πS_{O_+}(2|h0|), where
    O_+ = Σ_a g_a <−a|σ^a|+a> B_a is the flip channel.
- **(2) Near resonance.** The offset scales as g/δ, so the degenerate cap is lost once δ ≲ g·‖Y‖.
- **(3) Higher-order resonances.** They give slow growth at rate O(g^{2k}) (golden rule at order k) at the dense
  multi-flip set. This is the prethermal gap: no uniform control beyond T ~ g^{−(k+1)}.
- **(4) Interacting detector, 2|h0| above the local bandwidth.** NR_1 holds up to the high-frequency tail of the local
  spectral function. The expected result is a cap uniform up to (at least) exponentially long times.
  - [HEURISTIC; this is the standard many-body prethermalization picture. The tail bound for local operators and the
    prethermal-lifetime theorems (e.g. Abanin–De Roeck–Ho–Huveneers) are external literature, not re-derived or
    checked here.]
- **(5) Finite N (reverse order).** The spectrum is discrete, so NR_1 formally holds with δ ~ level spacing. The
  "uniform" statement is then physically vacuous for g ≫ 2^{−N/2}. What one sees instead is finite-N saturation of
  p (P2.8).

**Numerical check.** Details in P2.8.
- **Ising ring off resonance.**
  - p^{(1)} is confirmed quantitatively. At |h0| = 0.6, τ = 20°, 1/√N, ε = 1 the formula gives
    p = 4.5e-3 / 1.95e-2 / 1.22e-2 at T = 1 / 3 / 10, against measured 4.5e-3 / 1.9e-2 / 1.3e-2.
  - At T ≥ 30 formula and data agree only to a factor of about 2 (e.g. 6.8e-3 against 2.8e-3 at T = 30), consistent
    with O(g²) renormalization of the detunings dephasing the first-order phases.
  - Time average: formula 1.1e-2; mean of seven measured times 9.6e-3.
  - The cap is flat for T = 1–1000 and identical at N = 6 and N = 8.
- **screen_00 chain.** It is in band (2|h0| = 5.91; the flip-channel rms frequency is 5.95). The golden rule with
  Γ = 2π·8.2e-4 = 5.1e-3 predicts p = 1.5e-2 / 5.1e-2 at T = 3 / 10; measured 1.5e-2 / 5.7e-2 (N = 6) and 4.8e-2 (N = 8).
- **Above the band.** screen_00 with h0 × 4 (2|h0| = 23.6 > band edge ≈ 18): p ≈ 6e-5, flat over T = 1–1000, ∝ ε².

**Intuition.** Off resonance the qubit cannot give its energy 2|h0| to the detector. The flip is virtual, an admixture
of order g/δ, and it does not accumulate. The degenerate cap is the dressed ground state of a detuned two-level system,
not a measurement.

**Failure modes.**
- The operator version is useless for the ring, where ‖V‖_op ~ g√N. The HS version plus the P2.2(c) log-tail
  hypothesis is what survives.
- NR_1 fails for every interacting detector in the N → ∞ limit whenever 2|h0| is in band. That is the physically
  generic case at |h0| ~ J; screen_00 is an example.

---

## P2.5 First and second order: what shifts the axis

**Statement.** Fixed N, fixed T, basis a = ĥ0, H = H_0 + V with V = Σ_a g_a σ_0^a ⊗ B_a and the B_a traceless.
Define the two detector channels
- the flip channel O := Σ_a g_a ε_a B_a, with ε_a = <−a|σ^a|+a>;
- the longitudinal (QND) channel B_∥ := Σ_b g_b a_b B_b,

and let X = −U_{--}⁻¹U_{-+}, so that the mean root is (1/d)Tr X = (1/d)Σ_j λ_j.

- **(a) First order: the mean vanishes exactly.** (1/d)Tr X^{(1)} = 0 for every N, T, detector and basis, because
  (1/d)Tr B_a(s) = 0 (infinite-temperature weighting). The O(g) root cloud has zero mean; the Bloch-vector centroid
  moves only at O(g²).
- **(b) Second order: exact formula.**
  `(1/d)Tr X^{(2)} = 2∫_0^T ds e^{−2i|h0|s} ∫_0^s ds' (1/d)Tr[O(s−s') B_∥]`, with O(τ) = e^{iH_Dτ}Oe^{−iH_Dτ}.
  In the H_D eigenbasis (ν = E − E'):
  `2Σ_{EE'} O_{EE'}(B_∥)_{E'E}/d · [F_T(ν−2|h0|) − F_T(−2|h0|)]/(iν)`, where F_T(x) = (e^{ixT}−1)/(ix).
  Only the **cross-correlation between the flip channel and the longitudinal channel** tilts the axis. The pure
  flip–flip terms, i.e. the Lamb shift (which only renormalizes |h0| along ĥ0) and golden-rule decay (which broadens),
  cancel in the mean.
- **(c) Static (Mazur) part.** If (1/d)Tr[O(τ)B_∥] tends to a constant D_{O∥} = (1/d)Tr[P(O)P(B_∥)], with P the
  projection onto the commutant of H_D, then the ν = 0 term gives
  2D_{O∥}∫_0^T s e^{−2i|h0|s}ds = O(g²T·D_{O∥}/|h0|). This secular tilt oscillates with period π/|h0|.
  - With energy as the only conserved quantity that overlaps B_a (Mazur): P(B_a) = [(1/d)Tr(B_aH_D)/(1/d)Tr H_D²]·H_D,
    and (1/d)Tr(B_aH_D) ∝ h_a for both geometries. Then D_{O∥} ∝ (ε·(g∘h_D))(a·(g∘h_D)).
  - The O(g²) tilt therefore has magnitude ∝ |(g∘h_D)_⊥|·|a·(g∘h_D)|. Its direction in the tangent plane is
    (g∘h_D)_⊥ rotated by the T-dependent phase of ∫_0^T s e^{−2i|h0|s}ds. The fixed point adds a further
    (R_T⁻¹−I)⁻¹ rotation, so there is **no T-independent "detector direction" of the tilt**.
  - **The detector field enters the preferred axis first at second order**, through the coupling-weighted
    combination g∘h_D and only in the magnitude of an O(g²) offset.
  - Scaling of D: ring O(1) at 1/√N and O(1/N) at 1/N; chain O(1/N). In the SPEC order for the chain the static part
    therefore disappears, and the remaining O(g²) tilt is bounded in T by the regular cross-spectral density
    (≈ g²π S_{O∥}(0)/|h0|).
  - [The O(1/√T)-type hydrodynamic tail from energy diffusion is noted in P2.6.]
- **(c') Dressed qubit field (second-order SW).** After the transformation of P2.4, the infinite-temperature
  effective qubit Hamiltonian is (1/d)Tr_D H' = |h0|a·σ + g²(1/d)Tr_D R.
  - The flip–flip part ½[A, V_⊥] is along a: a Lamb shift that renormalizes |h0| only.
  - The transverse part comes from [A, V_∥], whose trace is ∝ (1/d)Tr(Z B_∥) = Σ_{EE'} Y_{EE'}(B_∥)_{E'E}/(d(2|h0|+E−E')).
    This is again the flip–longitudinal cross-correlation, frequency-filtered.
  - In the static model (qubit field h0 + p(E) in block E, p_a(E) = g_a<E|B_a|E>) this gives the dressed axis
    `a' = ĥ0 − P_⊥Σĥ0/|h0|² + O(g³)`, with Σ = Cov(p) (Mazur). For an energy-dominated Σ the dressed axis tilts
    **away from** (g∘h_D)_⊥ when ĥ0·(g∘h_D) > 0.
  - The root-cloud fixed point equals a' only without dephasing. The correlated dephasing adds the T-dependent term
    of (c).
  - Status: PROVED within the static model (exact expansion of (h0+p)/|h0+p|); relevance to the full dynamics is
    HEURISTIC.
- **(d) Vanishing condition.** If the longitudinal channel vanishes (Σ_b g_b a_b B_b = 0, e.g. single-channel coupling
  ⊥ ĥ0), then (1/d)Tr X = O(g³).
  - Tier 1 is covered by the exact Π-parity argument instead: Φ(z) = ±z at all orders (BRIEF 1.5).
- **(e) Dipole-fit fixed point.** The repository fit n̂ = S⁻¹m/|S⁻¹m| is not the centroid. For a small cap with
  transverse offsets x_j = X + y_j (<y> = 0), n̂_⊥ = X + ½<yy^T>⁻¹<y|y|²> + O(|y|²). The skewness term is O(g)
  whenever the O(g) cloud is not symmetric under λ → −λ, so the **dipole-fit fixed point moves at O(g)** while the
  centroid fixed point moves at O(g²).

**Status.**
- (a), (b), (d): PROVED (a Dyson expansion; the closed form was checked numerically).
- (c): PROVED for the exact static model; which conserved quantities control P(B_a) is a HEURISTIC input (Mazur
  with energy only).
- (e): PROVED (a Taylor expansion of the normal equations). That the skewness is generically nonzero is NUMERICAL.

**Proof of (b).**
1. X = −W_{--}⁻¹W_{-+} for W = U_0†U, since U_0 is block diagonal in the ĥ0 basis. Hence
   X^{(2)} = −W^{(2)}_{-+} + W^{(1)}_{--}W^{(1)}_{-+}.
2. Insert <±|σ_I^a(s)|±> = ±a_a and <−|σ_I^a(s)|+> = ε_a e^{−2i|h0|s}. The ε·ε̄ terms do not appear in the −+ block
   at this order.
3. Combine the two a_aε_b orderings with the full-square term.
4. Use cyclicity of the trace, Tr(B_a(s)B_b(s')) = C_ab(s−s'). ∎

**Numerical check.** Script `t6_second_order.py`: screen_00 chain, SPEC, N = 6, build_H, single T, no pooling.

| case | T | formula / ε² | exact (1/d)Tr X / ε² at ε = 0.003 | at ε = 0.1 |
|---|---|---|---|---|
| A: screen_00 | 5 | −7.3989e-4 + 6.3054e-4 i | −7.3981e-4 + 6.3062e-4 i | −7.3722e-4 + 6.3342e-4 i |
| A: screen_00 | 20 | −1.2306e-3 + 2.4457e-3 i | −1.2295e-3 + 2.4453e-3 i | −1.1920e-3 + 2.4314e-3 i |
| B: SPEC h0 = (−2, 1, 0), g_z = −0.1 only (B_∥ = 0) | 5, 20 | 0 | ∝ ε (so Tr X = O(ε³)), 4e-8 → 1.3e-6 | |

- **Magnitudes against the fixed point.** At T = 20 and ε = 0.3, the predicted centroid fixed-point tilt is
  (R_T⁻¹−I)⁻¹ applied to 2(1/d)Tr X^{(2)}, i.e. 0.023°. The Newton fixed point of P2.1 is 0.023°.
- **Case B.** The detector is the same as screen_00.

**Intuition.** An infinite-temperature detector has no mean field, so there is no first-order pull. The axis moves when
detector states that push the qubit harder along ĥ0 (and so precess it faster) are also those that tilt it sideways.
That is the covariance of the static detector fields, and for an energy-dominated diagonal ensemble it points along
g∘h_D.

**Failure modes.**
- (c) is a secular term ∝ T. Perturbation theory for the axis fails when g²T·D/|h0| ~ 1 (reverse-order times at
  finite N).
- The dipole fit adds an O(g) skewness offset that is an artefact of the fit, not a property of the dynamics.

---

## P2.6 h0 = 0 selection rule: least-flip (most-QND) axis → g∘h_D

At h0 = 0 we have u_q = I, so at g = 0 Φ is the identity and every n is fixed. The axis is chosen by the coupling at
O(g²).

**Statement.**
- **(a) Single channel.** If h0 = 0 and H_qD = (ĝ·σ_0) ⊗ B, then [H, ĝ·σ_0] = 0. By the QND-cone lemma (BRIEF 2.4),
  Φ(n) = sign(ĝ·n)ĝ: the axis is the coupling axis and the cloud is a pole. This covers the X0-conserving class
  (g_x only, h0 = 0) of Tiers 1, 2, 4 and 5.
- **(b) Multichannel, O(g²), fixed N or N-first at fixed T.** The centroid map is Φ_c(n) = n + δ(n) + O(g³), with
  - `δ(n) = 4 P_⊥ K(T) n` and `K_ab(T) = g_a g_b ∫_0^T ds ∫_0^s ds' (1/d)Tr[B_a(s−s') B_b]`;
  - K is **real**, because (1/d)Tr[X, Y] = 0 makes infinite-temperature correlations real. Write
    K = ½G + Λ, where G_ab = g_ag_b (1/d)Tr[B̄_aB̄_b] = (K + Kᵀ)_ab is the Gram matrix of the time-integrated coupled
    operators (B̄_a = ∫_0^T B_a(s)ds) and Λ is antisymmetric (a precession c × n).
  - The perturbative fixed points are the zeros of δ. If the precession is negligible they are the eigenvectors of G,
    and the attracting one is the top eigenvector.
  - The top eigenvector is exactly the minimizer of the first-order infinite-temperature flip probability,
    p^{(1)}(n) = Tr G − nᵀGn. The preferred axis is then **the basis in which the coupling is most QND-like**: a
    predictability-sieve criterion at infinite temperature.
- **(c) Long times.** G(T) ≈ T²D + (hydrodynamic) + O(T), with D_ab = g_ag_b (1/d)Tr[P(B_a)P(B_b)] (Mazur).
  - If the energy is the only conserved (and hydrodynamic) quantity that overlaps the coupled operators, then
    P(B_a) ∝ h_a H_D, because (1/d)Tr(σ_i^a H_D) = h_a. Also the slow part of B_a(t) is ∝ h_a times the local energy
    density.
  - Hence top-eig G → **g∘h_D** (componentwise product; sign-convention invariant). The detector field enters only
    through the energy projection of the coupled spins, weighted by the couplings.
  - **Order of limits.**
    - Chain: D = O(1/N), so in the SPEC order the static part vanishes. The energy-diffusion tail of the edge-spin
      autocorrelation is expected to keep the axis at g∘h_D; this last step is HEURISTIC.
    - Ring at 1/√N: D = O(1), a static Gaussian field along g∘h_D in every order of limits.
- **(d) h0 = 0 is always first-order resonant for interacting detectors.** The qubit frequency is 0, and the flip
  channel's spectral density at ω = 0 is S(0) > 0. So there is no off-resonance degenerate cap at h0 = 0: the
  fixed-point cloud is broad (mixing), except in the exact-QND case (a).
- **(e) Crossover.** For h0 ≠ 0 the precession 2|h0| competes with the O(g²) drift, or with the static field
  |g∘b(E)| in the ring at 1/√N. The axis is ĥ0 unless |h0| ≲ g²S(0) (chain, SPEC order) or
  |h0| ≲ |g∘h_D|/w (ring at 1/√N), where w² = |h_D|² + ΣJ² is the per-site HS weight of H_D and the typical
  static field is |g∘h_D|/w.

**Status.**
- (a): PROVED.
- (b): PROVED to O(g²) (Dyson, as P2.5 with R = I) and verified numerically. The minimum-flip identity is PROVED,
  since Σ_ab ε̄_aε_b G_ab = Tr G − nᵀGn for symmetric G.
- (c): HEURISTIC (Mazur with energy only; hydrodynamic tail), with NUMERICAL support.
- (d): PROVED that S(0) > 0 implies first-order resonance. Whether S(0) > 0 for the given chains is NUMERICAL: the
  screen_00 edge-spin channel carries 8–10% of its spectral weight at |ω| < 0.25 for N = 6–10 (`t3_spectral.py`).
- (e): HEURISTIC.

**Numerical check.**

*Test 1: `t10_h0zero_drift.py`.*
- **System and times:** screen_00 detector and couplings with h0 = 0, chain, SPEC, build_H. Single times T = 1–20
  (N = 8, T/t_H ≤ 0.33) and Gram matrices up to T = 1000.
- **K is real** to 1e-17.
- **Exact centroid fixed point vs the zero of δ.** At ε = 0.01 the exact fixed point (Newton) and the zero of
  δ(n) = 4P_⊥Kn agree to 0.003/0.013/0.027/0.002/0.009° at T = 1/2/5/10/20. The second-order selection rule is exact
  at small g.
- **Precession at short T.** n* sits 17.5/26.4/28.2/10.1/3.9° from top-eig G at those times.
- **Top-eig G vs g∘h_D:**

  | T | 1 | 5 | 20 | 100 | 1000 |
  |---|---|---|---|---|---|
  | angle, N = 8 | 12.3° | 4.5° | 2.4° | 1.4° | 1.2° |
  | angle, N = 10 | 12.3° | 4.6° | 2.3° | 1.4° | 1.2° |
  | eig2/eig1, N = 8 / 10 | 0.45 | 0.72 / 0.85 | | 0.040 / 0.108 | 0.017 / 0.012 |

  - The largest eigenvalue per T² falls with N (4.7e-4 → 3.0e-4 from N = 8 to 10 at T = 1000), as D ∝ 1/N predicts.
  - The top-eig G is 22.9° from the largest-coupling axis x. So the long-time axis is **not** set by the largest g.

*Test 2: `t7_h0zero.py`.*
- **Setup:** physical couplings, canonical pool, repository Φ (kit iteration, converged). Cells from
  `numerics/axis_probe.py` and `h0zero_discriminate.py`, converted to SPEC.

| cell | N | ∠(n*, g∘h_D) | ∠(n*, h_D) | ∠(top-eig Σ_diag, g∘h_D) | ∠(n*, secular-model n*) | f90 / resultant / B1 / S (cov) at n* |
|---|---|---|---|---|---|---|
| screen_00 with h0=0 | 6 / 8 | 13.8° / 3.5° | 26.4° / 16.0° | 1.2° / 1.1° | 10.7° / 2.9° | N=8: 0.575 / 0.784 / 1.082 / 0.544 (100) |
| gz-dominant (g_code = .02,.05,.10) | 6 / 8 | 11.0° / 7.5° | 44.6° / 42.8° | 0.7° / 0.6° | 7.8° / 8.3° | N=8: 0.540 / 0.783 / 1.103 / 0.488 (100) |
| gx-dominant (g_code = .10,.05,.01) | 6 / 8 | 3.9° / 9.4° | 35.3° / 35.9° | 0.3° / 0.3° | 1.5° / 5.2° | N=8: 0.589 / 0.818 / 1.090 / 0.424 (100) |
| screen_18 (Ising + tilted field, h_y ≠ 0) | 6 / 8 | 21.4° / 1.9° | 19.3° / 5.1° | 8.5° / 7.3° | 3.7° / 2.0° | N=8: 0.287 / 0.562 / 1.043 / 0.731 (100) |

- Σ_diag = g∘D∘g with D the diagonal ensemble of σ_1^a.
- The energy-linear share of the diagonal elements b_a(E) = <E|σ_1^a|E> rises with N: 0.42 → 0.51 (screen_00
  detector, N = 6 → 8).
- **Same-budget exact-Born floor** at 1536 roots (N = 8, `t9`): f90 0.098 ± 0.007, resultant 0.341 ± 0.012,
  B1 1.014 ± 0.027, S 0.798 ± 0.019.
- **Reading.**
  - At h0 = 0 the fixed point is 2–9° from g∘h_D and 5–43° from h_D (N = 8). This reproduces the record's 7.45° and
    9.44° for the two discriminate cells (`numerics/h0zero_discriminate.log:1-2`).
  - The fixed-point clouds are broad (mixing, (d)), yet still far more concentrated than Born (resultant 0.56–0.82
    against 0.34).
  - Single N-pairs only; the N-trend of the angle is not monotone in every cell (gx-dominant 3.9° → 9.4°).

**Intuition.**
- The qubit has no field of its own, so it keeps whichever pointer the detector does not scramble. The part of the
  coupled spin that survives time averaging is its overlap with the conserved energy, and that overlap is h_a.
- The qubit therefore couples QND-like to the detector energy through the vector g∘h_D.

**Failure modes.**
- At short T (≲ 5) the precession part moves the axis by tens of degrees.
- Integrable detectors (extra conserved charges) change P(B_a) and hence the axis.
- The physical-g pool results are non-perturbative (gT up to 100). They agree with the rule only to several degrees.

---

## P2.7 Basis dichotomy: the fixed-point basis carries the degenerate cap; every other basis is kinematic

**Statement.** Let |h0| ≫ g and let n be an output axis with ∠(n, ĥ0) = α ∉ {0, π}.
- **(i) Single T, g → 0.** Φ_T(n) = R_T⁻¹n ≠ n unless u_q = ±I. The fixed-point condition fails by
  ∠(n, R_T⁻¹n) = 2 arcsin(sin α·|sin(|h0|T)|).
- **(ii) Pool, g → 0.** The cloud is the kinematic cone a·Ω = cos α about a = ĥ0. So Φ(n) = ±ĥ0 ≠ n, n̂ = ±ĥ0, and
  B1 = B1_kin := 1/|cos α| exactly. These hold for **any** azimuthal law (cone lemma), including azimuthal spreading by
  QND dephasing.
- **(iii) Weak coupling.** H is QND along ĥ0 up to the SW conjugation of P2.4, i.e. exactly QND for the
  transformed H' when R_⊥ = 0. For exact QND the roots in basis n lie exactly on the cone (QND-cone lemma), with the
  azimuth set by precession and by the dephasing phases of V_∥.
  - The flip channel adds a radial broadening r about the cone.
  - Numerically, B1 = B1_kin(1 + O(r)) and n̂ = ±ĥ0 + O(r).

**Consequence.** Off resonance, in the fixed-point basis ±ĥ0 the law is a degenerate cap (P2.3–P2.4). In every other
basis the law is the kinematic cone, which violates Φ(n) = n by an O(1) angle; lab-basis B1 and axis alignment are
kinematic (BRIEF 1.4). Neither basis gives a nondegenerate Born law.

**Status.**
- (i), (ii): PROVED.
- (iii): PROVED for exact QND (cone lemma).
- (iii) at fixed T: PROVED. The roots of U in basis n are exactly the roots of W = U_0†U in basis m = R_T⁻¹n (proof of
  P2.1). P2.2 and Duhamel with zero Hamiltonian then give sin(θ/2) ≤ T‖V‖_op about the kinematic point R_T⁻¹n. For the
  chain this holds uniformly in N.
- (iii) uniformly in T: HEURISTIC. In basis m ≠ ±ĥ0 the longitudinal channel V_∥ acts as a flip and grows secularly.
  The QND-cone lemma says this growth runs **along** the cone, but no root-perturbation bound for the non-normal pencil
  is given here to show that the radial part stays O(r).

**Numerical check.** Script `t12_lab_vs_eps.py`: screen_00 chain, SPEC, canonical pool, lab-z basis, α = 47.10°
between z and −ĥ0(SPEC).

| N | ε | cone angle mean ± sd | B1/B1_kin | lab S (cov) | ĥ0-basis θ_rms |
|---|---|---|---|---|---|
| 6 | 0.01 | 47.11 ± 1.22° | 0.988 | 0.496 (70) | 0.09° |
| 6 | 0.1 | 47.67 ± 9.46° | 0.966 | 0.141 (100) | 0.90° |
| 6 | 1 | 48.98 ± 17.18° | 0.930 | 0.390 (100) | 6.94° |
| 8 | 0.01 | 47.10 ± 0.75° | 0.994 | 0.496 (68) | 0.10° |
| 8 | 0.1 | 47.36 ± 6.24° | 0.980 | 0.191 (100) | 0.99° |
| 8 | 1 | 49.98 ± 21.65° | 0.886 | 0.552 (100) | 9.27° |

- The cone is exact as ε → 0.
- The lab S is **non-monotone** in ε. Its ε → 0 value, ≈ 0.50 with coverage about 70 bins, is produced by the
  kinematic cone plus azimuthal dephasing along it.
- The lab-basis cloud is roughly twice as wide about its cone as the ĥ0-basis cap is about its pole. This is the new
  pencil of BRIEF 1.7, not a rotated cloud.

---

## P2.8 Numerics: K2.1–K2.3, K5.1, cap radius vs g and T

**Disclosure common to this section.**
- **Builder:** bornkit.build_H, SPEC positive convention, outcome-0 forward pencil, unit weights; output basis rotated
  with `axis=`.
- **Tier-2 ring:** H = Σ_i[−Z_iZ_{i+1} − Z_i] + |h0|(sin τ X_0 + cos τ Z_0) + g_x s_N X_0 Σ_i X_i, with
  g_x = −0.1·ε and periodic bonds. The ring coupling scaling is stated per row: s_N = 1/√N (the user's correction,
  BRIEF 1.2) or 1/N (SPEC §11 baseline).
- **Zeros and conservation laws:**
  - held at zero: h_x, h_y, J_xx, J_yy, g_y, g_z, h_0y;
  - the zero J_xx = J_yy and zero transverse detector field make every Z_i Z_{i+1} and Z_i conserved by H_D alone,
    so the detector is commuting (Ising);
  - the tilt breaks X0 conservation (τ < 90°) and Π parity (h_0x ≠ 0);
  - there is no conservation law involving the qubit.
- **screen_00 chain:** BRIEF 1.1 values with every code sign flipped to SPEC, g_a → εg_a. Nothing is held at zero
  except h_y (real H).
- **Times:**
  - single times T ∈ {1, 3, 10, 30, 100, 300, 1000} (no pooling), chosen to span the Duhamel, golden-rule and
    saturation regimes;
  - or the canonical six-time pool (BRIEF 1.3), used as absolute times, which is a discrete average, not Cesàro.
- **T/t_H:**
  - screen_00: t_H ≈ 19/60/193 at N = 6/8/10;
  - Ising ring: the detector alone is exactly π-periodic, since all its energies are even integers for
    h_z = J_zz = −1. Finite-N discreteness therefore enters through the resonance lattice rather than through a
    Heisenberg time, and the relevant check is N-independence at 1/√N.
  - Every chain T ≥ 100 at N ≤ 10 is **reverse order**; only the light-cone-converged short chain times are in the
    SPEC order.

### K2.1 / K2.3: off-resonance tilted Tier-2 ring, pooled (`t13_k21.py`)

f90, resultant, θ_rms and S (cov) are computed about ĥ0; the last two columns are in the lab-z basis.

| config | N | f90 | resultant | θ_rms | S (cov) | lab B1/B1_kin | lab ∠(n̂, ĥ0) |
|---|---|---|---|---|---|---|---|
| \|h0\|=0.6, τ=20°, 1/√N | 4/6/8 | 1.000/1.000/0.999 | 0.993/0.993/0.993 | 6.7/6.9/7.0° | 0.09(20)/0.13(24)/0.16(26) | 1.008/1.008/1.008 | 0.5/0.4/0.4° |
| \|h0\|=0.6, τ=20°, 1/N | 4/6/8 | 1.000 | 0.998/0.999/0.999 | 3.6/2.9/2.6° | 0.03–0.04 (10–12) | 1.002/1.001/1.001 | 0.2–0.3° |
| \|h0\|=0.6, τ=45°, 1/√N | 4/6/8 | 1.000 | 0.996 | 5.1/5.0/5.2° | 0.06–0.09 (16–20) | 1.012/1.011/1.012 | 0.5–0.8° |
| \|h0\|=1.5, τ=20°, 1/√N | 4/6/8 | 1.000 | 0.996 | 5.1/5.4/5.1° | 0.06–0.11 (16–22) | 0.998/0.998/0.998 | 0.5–1.4° |
| \|h0\|=1.5, τ=45°, 1/√N | 4/6 | 1.000 | 0.997/0.998 | 4.2/3.9° | 0.05–0.08 (14–18) | 0.995/0.996 | 0.3–0.4° |
| \|h0\|=1.5, τ=20° and 45°, 1/N | 4/6/8 | 1.000 | 0.999–0.9995 | 2.4→1.8°, 2.0→1.6° | 0.015 (8) | 0.999–1.000 | 0.1–0.4° |

- **K2.1 prediction (f90 > 0.9 in the ĥ0 basis) holds:** f90 ≥ 0.999 everywhere.
- **K2.3:** B1/B1_kin = 0.995–1.012. The lab-basis dipole is the kinematic cone to about 1%, and the lab axis is
  within 1.4° of ĥ0.
- **Scaling:** N-independent at 1/√N; θ_rms ∝ N^{−1/2} at 1/N (3.59 → 2.86 → 2.60 against the predicted
  3.59 → 2.93 → 2.54).
- **Lab S** ranges over −0.12…+0.43 (cov 42–100) with no N-trend.
- **Same-budget exact-Born floors** (`t9`, 20 i.i.d. draws):
  - S: 0.57 ± 0.04 at 384 roots (N = 6) and 0.80 ± 0.02 at 1536 roots (N = 8);
  - f90 0.098, resultant 0.34, coverage 95–99 bins.
- **A degenerate cap in the fixed-point basis, and a kinematic cone in the lab.**

### K2.2: |h0| sweep, single times, ĥ0 basis (`t8_sweep.py`; τ = 20°, 1/√N, ε = 1; N = 4, 6, 8)

| \|h0\| | 0.5–0.75 | 0.8–1.2 | 1.25–1.95 | **2.00** | 2.05–2.85 | 2.9–3.1 | 3.15–3.5 |
|---|---|---|---|---|---|---|---|
| p(T=1000), N = 8 | 0.008–0.024 | 0.04–0.33 (peak 0.33 at 1.00) | 0.003–0.036 | **0.15** (0.019 at T=100) | 0.002–0.02 | 0.03–0.16 (peak at 3.00) | 0.002–0.03 |
| f90 (T=1000), N = 8 | 1.000 | 0.55–0.99 | ≥0.996 | 1.000 (θ_rms 9.6°) | 1.000 | 0.945–1.0 | 1.000 |

- First-order peaks sit at |h0| = 1 and 3 (the set R1 = {|ε_m|} = {1, 3}), with N-independent heights.
- A second-order peak at |h0| = 2 needs the tilt (it is an even multi-flip resonance). It is absent at T = 100
  (p = 0.019) and present at T = 1000 (p = 0.075/0.12/0.15 at N = 4/6/8).
- **This locates the break of uniform-in-T control.** At a second-order resonance the cap is controlled up to
  T ~ 10² ≈ 1/g² and fails by T ~ 10³.
- No other peaks appear at non-integer |h0|, as the commensurate resonance lattice predicts.

### K5.1: pooled Φ fixed point on an N-ladder (`t11_k51.py`)

- **Method.** Newton on the repository dipole-fit Φ and on the centroid map, then the tangent Jacobian (attracting iff
  \|eig\| < 1), then the plain kit iteration (undamped, 40 steps).
- **Reference axis.** ĥ0 for the \|h0\| ≫ g points, g∘h_D for the h0 = 0 points.
- **Times.** Canonical pool; T/t_H ≫ 1 (reverse order).

| point | N = 5 / 6 / 7 / 8: ∠(n*_fit, ref), \|J_fit\| | ∠(n*_cen, ref), \|J_cen\| | kit iteration | f90 / resultant / B1 at n*_fit (N=8) |
|---|---|---|---|---|
| screen_00 chain | 0.17°, 0.18 / 0.09°, 0.24 / 0.10°, 0.25 / **0.52°, 1.36** | 0.04 / 0.05 / 0.02 / 0.035°, ≤ 0.075 | converges N ≤ 7; **fails at N = 8** (steps 3.4–5°) | 0.993 / 0.987 / 1.013 |
| ring \|h0\|=0.6, τ=20°, 1/√N | 1.10 / 1.34 / 0.91 / 0.94°, ≤ 0.49 | 0.26–0.28°, 0.22–0.25 | converges | 0.999 / 0.9925 / 1.007 |
| ring \|h0\|=1.5, τ=45°, 1/√N | 1.18 / 0.87 / 1.03 / 0.91°, ≤ 0.11 | 0.14–0.17°, 0.20–0.22 | converges | 1.000 / 0.9975 / 1.003 |
| screen_00 with h0 = 0 | 11.3 / 13.8 / 4.8 / 3.5° | 3.5 / 4.9 / 1.9 / 2.3°, ≤ 0.10 | converges (N=5: not within 40 steps) | 0.575 / 0.784 / 1.082 |
| h0=0, g_z-dominant | 5.0 / 11.0 / 5.6 / 7.5° | 1.4 / 5.0 / 3.0 / 3.4° | converges | 0.540 / 0.783 / 1.103 |
| h0=0, g_x-dominant | 4.2 / 3.9 / 1.9 / 9.4° | 1.2 / 1.4 / 1.6 / 1.9° | converges | 0.589 / 0.818 / 1.090 |

- **\|h0\| ≫ g.** The fixed point is ĥ0 to within 0.02–0.3° (centroid) or 0.1–1.3° (fit). The fit offset is the
  O(g) skewness term of P2.5(e). The cloud is a degenerate cap (f90 ≈ 1, resultant ≥ 0.987).
- **h0 = 0.** The centroid axis lies within 1.2–5.0° of g∘h_D at N = 5–8. The dipole-fit axis wanders 1.9–13.8° and is
  non-monotone in N. The clouds are broad but still far from Born (resultant 0.78–0.93 against 0.34).
- **The repository Φ (dipole fit) is not a robust preferred-axis definition at the degree level.** Its fixed point can
  be repelling (screen_00, N = 8).
- **N = 10 (ring \|h0\|=0.6, τ=20°, 1/√N, pooled):** f90 = 1.000, resultant 0.9923, θ_rms 7.13°, S 0.217 (cov 32);
  lab B1/B1_kin = 1.0084, lab ∠(n̂, ĥ0) = 0.49°. This is the same as N = 4–8, N-independent.

### Cap radius vs g and T in the fixed-point basis (`t4_cap_scan.py`; single times; ĥ0 basis)

The entry "θ_rms / θ_max / p" at T = 1, 10, 100, 1000 is shown for ε = 1 (full tables in `t4_*.jsonl`).

| system | N | T=1 | T=10 | T=100 | T=1000 | scaling |
|---|---|---|---|---|---|---|
| screen_00 chain (in band) | 6 | 2.6°/3.7°/4.3e-3 | 5.2°/8.7°/5.7e-2 | 6.9°/12°/0.12 | 8.0°/22°/0.14 | p ≈ ΓT (Γ = 5.1e-3) until saturation |
| screen_00 chain | 8 | 2.6°/3.7°/4.3e-3 | 5.0°/8.2°/4.8e-2 | 9.3°/20°/0.19 | 9.7°/38°/0.17 | saturation level grows with N |
| screen_00, h0 × 4 (above band) | 6, 8 | 0.46°/0.6°/5.8e-5 | 0.52°/0.8°/6e-5 | 0.53°/0.8°/6e-5 | 0.52°/0.8°/0.7–1.4e-4 | uniform in T, ∝ ε, N-independent |
| ring \|h0\|=0.6 τ=20° 1/√N | 6, 8 | 7.2°/18°/4.5e-3 | 7.2°/18°/1.3e-2 | 5.4°/21°/5e-3 | 6.8°/20°/1.0e-2 | uniform in T and N, ∝ ε |
| ring \|h0\|=0.6 τ=20° 1/N | 6 → 8 | 2.9 → 2.6° | 2.9 → 2.4° | 2.5 → 2.2° | 2.7 → 2.7° | ∝ N^{−1/2} |
| ring \|h0\|=1.5 τ=20° 1/√N | 6, 8 | 4.3°/…/3.8e-3 | 5.8°/…/1.1e-2 | 4.5°/…/5e-3 | 4.8–5.1°/…/6–7e-3 | uniform |
| ring \|h0\|=1.0 (resonant) τ=20° 1/√N | 6 / 8 | 6.1°/4.2e-3 | 31°/0.25 | 33–52°/0.30–0.38 | 33–38°/0.32–0.33 | p ∝ T² until saturation, f90 → 0.38–0.41 |

- **ε scaling.** For ε ∈ {0.03, 0.1, 0.3, 1}, θ_rms is linear in ε everywhere at T ≤ 10. In the screen_00 chain the
  golden-rule law p ≈ 2πS_{O_+}(2|h0|)·ε²·T holds from T ≈ 3 until finite-N saturation:
  - ε = 0.3, T = 100: predicted 4.6e-2, measured 4.9e-2 / 3.8e-2 (N = 6 / 8);
  - ε = 0.1, T = 100: predicted 5.1e-3, measured 9.4e-3 / 4.8e-3.
- **Answer to (d).** The uniform-in-T off-resonance prediction holds wherever NR_1 holds:
  - Ising ring off {1, 3}, to T = 1000 and at N = 4–8;
  - an interacting chain with 2|h0| above the local band.

  It breaks
  - at first-order resonances: immediately, coherently in the Ising ring and by golden rule in the interacting chain;
  - at second-order resonances: by T ~ 1/g³–1/g²;
  - for screen_00: screen_00 is not an off-resonance point. 2|h0| = 5.91 sits at the centre of the flip-channel
    spectrum (rms frequency 5.95; `t3_spectral.py`, N = 6/8/10: S_{O_+}(2|h0|) = 1.15e-3 / 8.5e-4 / 8.2e-4 per unit
    frequency).

---

## P2.9 Reinterpretation of the preferred-basis campaign at screen_00

**Status.** NUMERICAL (finite N, reverse order), interpreted with P2.1–P2.8.

**Setting.**
- **Hamiltonian:** screen_00 chain in SPEC convention (BRIEF 1.1); every parameter nonzero except h_y = 0, so
  H is real and there is no conservation law; endpoint coupling O(1).
- **Pencil and times:** forward outcome-0 pencil, unit weights, canonical six-time pool used as absolute times
  (min|non-g| = 1.00), which is a discrete time average.
- **T/t_H = 1.7–17 (N = 8) and 0.5–5 (N = 10).** Reverse order throughout; the SPEC order needs N ≳ 500 at T = 100
  (BRIEF 4).

**(1) What the lab-basis B1 measures.**
- At g → 0 the pooled lab-z cloud lies exactly on the kinematic cone about ĥ0. Its half-angle is 47.10°, the angle
  between z and −ĥ0(SPEC) = +ĥ0(code) (P2.7).
- The cone lemma then gives B1_kin = 1/cos 47.10° = **1.469** and n̂ ∥ ĥ0 **for any azimuthal distribution**.
- Check: at ε = 0.01, B1/B1_kin = 0.988 (N = 6) and 0.994 (N = 8); cone angle 47.11 ± 1.22° and 47.10 ± 0.75°.
- The record's values divide into a **monotone broadening sequence**:

  | N | 6 | 8 | 10 | 12 |
  |---|---|---|---|---|
  | B1 | 1.367 | 1.302 | 1.150 | 0.880 |
  | B1/B1_kin | 0.930 | 0.886 | 0.783 | 0.599 |

  - N = 6 and 8 are from this work (`t9`); N = 10 and 12 are the campaign values (`wiki/campaigns/preferred-basis-campaign.md`
    via BRIEF 6.5s).
  - The kit reproduces the N = 8 value to 5e-14 (BRIEF 7), and this work reproduces it too (1.3018).
- **"Axis error 1.5–3° from ĥ0"** is the O(r) displacement of the fitted axis of a broadened kinematic cone.
  **Alignment with ĥ0 is free precession, not detector physics.** The lab basis violates Φ(n) = n by about 47° (P2.7).
- **The B1 = 1 crossing between N = 10 and 12** is the broadening passing a codimension-one value (BRIEF 1.4). It is
  not convergence to Born: B1 overshoots to 0.88 at N = 12.

**(2) What drives the broadening.**
- screen_00 is **first-order resonant**. 2|h0| = 5.905 lies at the centre of the infinite-temperature spectral function
  of the flip channel O_+ = Σ_a g_a<−a|σ^a|+a>σ_1^a (rms frequency 5.95).
- Golden-rule flip rate: Γ↓ = Γ↑ = 2πS_{O_+}(2|h0|) = 5.1e-3, so T_1 ≈ 1/(2Γ) ≈ 100. It is converging over
  N = 6/8/10: S_{O_+}(2|h0|) = 1.15e-3 / 8.5e-4 / 8.2e-4.
- The measured single-time flip probability in the ĥ0 basis follows p = ΓT for T = 3–30. It then saturates at the
  finite-N value 0.12–0.14 (N = 6) and 0.17–0.19 (N = 8), because t_H (19/60/193/651 at N = 6/8/10/12) is below or
  near T_1.
- As N grows, t_H passes T_1 ≈ 100 between N = 8 and 10. The finite chain then stops protecting the cap, and the
  broadening grows. That is the B1/B1_kin sequence above.
- **Order of limits.** In the SPEC order the qubit at the pool times (T = 1–10 T_1) is golden-rule relaxed. The
  finite-N cap is therefore a reverse-order object.

**(3) What the lab-basis S_Born ≈ 0.72 measures.**
- It is the polar ratio, about the lab z axis, of the broadened kinematic cone paired with its antipodes. It is a
  **non-monotone** function of the broadening:
  - 0.496 at ε = 0.01, with coverage 68–70 bins: kinematic cone plus QND-dephasing azimuths, no detector-induced
    radial spread;
  - 0.14–0.19 at ε = 0.1;
  - 0.39 (N = 6) and 0.55 (N = 8) at ε = 1.
- The campaign's 0.72 at N = 10–12 is this broadening measure at larger N (a reverse-order equilibrated finite-chain
  law, BRIEF 4).
- It is computed in a basis that violates the fixed-point condition by 47°. It is not a statement about a
  measurement basis.

**(4) The fixed-point-basis cloud (the requested diagnostics).**
- Pooled, ĥ0 basis (`t9_screen00_clouds.py`). The Newton fixed point n* is 0.09–0.5° from ĥ0 (below). Evaluating at
  n* instead of ĥ0 changes f90, resultant and B1 by ≤ 0.001 and S by ≤ 0.02 (N = 8 at n*_fit: S 0.278, cov 38;
  `t11_chain.log`).

| N (roots) | f90 | resultant | θ_rms / θ_max | coverage | S_Born | E_ratio_occ | B1 | Born floor S / E_ratio / B1 / f90 / resultant |
|---|---|---|---|---|---|---|---|---|
| 6 (384) | 1.000 | 0.9927 | 6.9° / 22° | 24 | 0.132 | 0.022 | 1.007 | 0.57±0.04 / 0.134±0.015 / 1.00±0.05 / 0.098 / 0.336 |
| 8 (1536) | 0.994 | 0.9870 | 9.3° / 38° | 36 | 0.262 | 0.055 | 1.013 | 0.80±0.02 / 0.063±0.006 / 1.01±0.03 / 0.098 / 0.341 |
| 10 (6144) | 0.963 | 0.9730 | 13.4° / 83° | 68 | 0.423 | 0.186 | 1.026 | 0.90±0.01 / 0.031±0.003 / 1.00±0.01 / 0.096 / 0.333 |

- **A degenerate cap.**
  - f90 ≈ 1 and resultant ≈ 0.97–0.99, against Born's 0.10 and 0.34.
  - B1 ≈ 1 is the near-point-mass artefact (BRIEF 1.4).
  - The weak ratio passes vacuously on the few occupied bins at N = 6 (E_ratio 0.022, below the Born floor). It fails
    once the support extends (0.186 against floor 0.031 at N = 10).
- The cap is **dissolving with N**, not converging (θ_rms 6.9 → 9.3 → 13.4°), for the resonance reason in (2).
- **The Φ fixed point itself** (Newton on the repository dipole-fit Φ; P2.1, K5.1):

  | N | 5 | 6 | 7 | 8 |
  |---|---|---|---|---|
  | ∠(n*, ĥ0) | 0.166° | 0.087° | 0.104° | 0.515° |
  | tangent Jacobian \|eig\| | 0.09–0.18 | 0.24 | 0.25 | **1.36** |

  - **At N = 8 the dipole-fit fixed point is a repelling focus.** This explains the recorded non-convergent circulation,
    about 3° around ĥ0, of the undamped Φ iteration at N = 8 (BRIEF 6.5φ). The fixed point exists; it is not
    attracting. Damped iteration can still converge to it.
  - The centroid fixed point is 0.020–0.050° from ĥ0 and strongly attracting (\|eig\| ≤ 0.075).

**(5) Summary reading.** At screen_00 the "preferred axis ≈ ĥ0" is the free-precession axis (P2.1, P2.7). The
detector enters only through (a) the O(g) or O(g²) offset of the fixed point (0.02–0.5°) and (b) the resonant flip
broadening, which grows with N as the reverse-order protection lapses. Neither the lab S_Born ≈ 0.72 nor the B1 trend
is evidence of a Born basis.

---

## Answers to the GOAL questions assigned to WP2

**Does the preferred axis align with the detector field or the qubit field?**
- For |h0| ≫ g (screen_00: |h0| ≈ 30·max|g|, and every Tier-2/5 point with a qubit field) it is the **qubit field**
  ĥ0. The offset is 0.02–0.3° (centroid) or 0.1–1.3° (dipole fit), because P2.1–P2.5 give:
  - n* = ĥ0 + O(g²) for the centroid;
  - n* = ĥ0 + O(g) for the repository's dipole fit.
- The detector field enters only at second order, as the magnitude of the offset through the coupling-weighted
  combination g∘h_D. Even then its direction rotates with T (P2.5c).
- It aligns with the detector only at **h0 = 0**, and then with **g∘h_D (componentwise), not h_D** (P2.6). At N = 8
  on the pool:
  - the fixed point is 1.9–3.4° (centroid) or 1.9–9.4° (dipole fit) from g∘h_D;
  - the dipole-fit axis is 5–43° from h_D;
  - the long-time Gram axis is within 1.2° of g∘h_D.
- GOAL's wording ("aligns with the detector field rather than the qubit field alone") is false at screen_00. Its
  h0 = 0 version is correct only after replacing h_D by g∘h_D.

**Is the axis a dynamical fixed point or a static feature of H_q + H_D?**
- It is a **static feature, made a fixed point by kinematics or by a least-flip principle.**
- |h0| ≫ g: the free-precession axis of H_q. It is a fixed point because precession is a rotation about ĥ0.
  - At one time it is neutral (elliptic) at g = 0 and becomes attracting only at O(g²T²).
  - Pooled over times it is superattracting (cone lemma).
- h0 = 0: a static feature of H_D + H_qD, namely the energy (Mazur) projection of the coupled spins. It is selected
  dynamically as the attracting zero of the O(g²) drift, which is the minimum of the first-order infinite-temperature
  flip probability (the most QND basis).
- In neither case is it a feature of H_q + H_D alone at h0 = 0: the couplings select it.

**Tier 2 (1)–(4).**
- (1) The transverse qubit field rotates the preferred basis to ĥ0, i.e. n* = ĥ0 + O(g²). This is trivial and
  kinematic.
- (2) Born does not emerge in the rotated frame off resonance. The ĥ0-basis law is a degenerate cap:
  - f90 ≥ 0.999 and resultant ≥ 0.992 for N = 4–10;
  - S 0.02–0.22 with coverage 8–32, against same-budget floors 0.57–0.90.
- (3) Yes, the axis is the fixed point of Φ, with Jacobian = rotation at g → 0 (P2.1).
- (4) The **degenerate-pass region is open and stable**: every |h0| off the resonance lattice, for the Ising ring
  h_z = J_zz the complement of Z_{>0}, uniformly in T and N at 1/√N.
  - There is **no open Born region at weak coupling off resonance**. The only non-degenerate behaviour is on the
    resonance manifolds (codimension 1: |h0| = |ε_m| at first order, dense multi-flip sets at higher order), where the
    cloud spreads (f90 → 0.38) by resonant mixing.
  - Correction to BRIEF C2.1: the tilt adds even multi-flip resonances. |h0| = 2 was observed at T = 1000.

**Tier 5 (3).** Answered above: the axis is static, with a kinematic or least-flip selection.

**Tier 6 (chain).**
- The chain analogue of the off-resonance cap exists only when 2|h0| lies **above** the local band of the edge-spin
  flip channel. Example: screen_00 with h0 × 4 has θ_rms ≈ 0.5° uniform in T = 1–1000, N-independent.
- screen_00 itself is in band: first-order golden-rule resonant, Γ = 5.1e-3.

**GOAL Q5 context.** The resonance condition is |h0| = |ε_m| for **every** tilt; only the qubit splitting enters.
This supports BRIEF's answer that h_0z = h_z is neither necessary nor sufficient.

**Preferred-basis campaign (task (c)).** See P2.9.
- B1/B1_kin = 0.930 / 0.886 / 0.783 / 0.599 at N = 6/8/10/12 is monotone flip-induced broadening of the kinematic
  cone (B1_kin = 1.469).
- "Axis ≈ ĥ0" is free precession.
- S_Born(lab) is a non-monotone broadening measure (0.50 already at ε = 0.01) in a basis 47° off the fixed point.
- The fixed-point-basis cloud is a degenerate cap dissolving with N (resonance with a reverse-order cutoff):
  f90 1.000/0.994/0.963, resultant 0.993/0.987/0.973, S 0.13/0.26/0.42 (cov 24/36/68), E_ratio_occ
  0.022/0.055/0.186.

---

## Open items

1. **Ring measure-level cap in the SPEC order.** It needs the single-point log tail ℓ(ĥ0) ≤ K·p(ĥ0) (P2.2c). This is
   weaker than G1 but unproven. The operator-norm route fails since ‖V‖_op ~ g√N.
2. **All-orders uniform-in-T control.** For the commensurate Ising ring off Z the result is order-by-order only;
   convergence of the SW series is not proved. For interacting detectors above the band it relies on external
   prethermalization results that were not checked here.
3. **SPEC-order law at screen_00 for T ≫ T_1 ≈ 100** (the golden-rule-relaxed regime) is not determined here. It
   belongs to the resonant/mixing programme (C4.1/C6.1). This is the decisive regime for screen_00.
4. **h0 = 0 chain in the SPEC order.** The claim that energy-diffusion tails keep the axis at g∘h_D is HEURISTIC.
   N-converged Gram matrices are available only to T ≈ 20 at N ≤ 10.
5. **The repository Φ is fit-dependent at O(g).** It can have a repelling fixed point (screen_00, N = 8). A
   fit-independent definition, such as the centroid axis or argmin_n p(n; T), would be more robust. This is a
   recommendation, not a change: SPEC and the repository are read-only here.
6. **Coverage gaps.** K5.1 was run at N = 5–8 only; N = 9 was skipped for cost. The Tier-2 pooled N = 10 point covers
   one configuration. The h0 = 0 cells have single N-pairs and non-monotone fit angles.
7. **Root perturbation outside the fixed-point basis.** There is no rigorous bound on radial broadening about the
   kinematic cone uniformly in T (P2.7 iii).

## Surprises

1. The dipole-fit fixed point moves at O(g) while the centroid moves at O(g²). The fit responds to the third moment of
   the O(g) cap: the numbers scale exactly as ε and ε² respectively (P2.1 table).
2. At the physical screen_00 couplings (N = 8, pool) the repository Φ fixed point is a **repelling focus** (\|eig\| = 1.36).
   This explains the recorded non-convergent circulation of about 3°.
3. **screen_00 is first-order resonant.** 2|h0| = 5.905 sits at the centre of the flip-channel spectrum (rms 5.95), with
   golden-rule rate 5.1e-3 matched quantitatively. Its "QND-like" ĥ0-basis cap is a reverse-order artefact
   (t_H < T_1 ≈ 100 at N ≤ 8) and dissolves with N.
4. The lab-basis S_Born of the pooled screen_00 cloud is ≈ 0.50 already at ε = 0.01 (coverage 70 bins). It is purely
   kinematic plus dephasing, and non-monotone in g.
5. The second-order centroid tilt comes only from the flip–longitudinal cross-correlation. Lamb shift and decay cancel
   in the mean. This is verified to 1e-4 against exact roots.
6. At h0 = 0 the long-time axis is within 1.2° of g∘h_D and 23° from the largest-coupling axis. The Mazur projection
   onto the detector energy makes the qubit couple QND-like to H_D along g∘h_D.
7. A second-order (tilt-enabled) multi-flip resonance at |h0| = 2 appears only after T ~ 10³ ≈ 1/g³. It is a concrete
   instance of the prethermal gap.

## Corrections to BRIEF / digests

1. **BRIEF 1.5 and the task text: "unique attracting fixed points ±ĥ0" at g → 0.** At a single T the g = 0 map is a
   rotation, so ±ĥ0 are unique but **neutral (elliptic)**. Attraction arises only from pooling (superattracting via the
   cone lemma, at scales above the cap radius) or from O(g²T²) dephasing. At physical screen_00 couplings (N = 8) the
   dipole-fit fixed point is repelling (\|eig\| = 1.36, `t2b_N8.log`, `t11_chain.log`).
2. **BRIEF 5.1 [HEURISTIC] "mean-field axis h_eff = h0 + g∘⟨σ_D⟩".** At the infinite temperature implicit in the
   root measure, ⟨σ_D⟩ = 0 and the first-order mean root vanishes exactly (P2.5a). The g∘h_D alignment at h0 = 0 is a
   **second-moment (Gram/Mazur energy-projection)** effect, not a mean field (P2.6).
3. **BRIEF C2.1 "the longitudinal part adds only ε_m = 0".** The tilt (longitudinal vertex) also enables even
   multi-flip resonances 2|h0| = 2(±ε_m ± ε_m'). |h0| = 2 was observed for h_z = J_zz = −1 at T = 1000,
   p = 0.15 at N = 8 (`t8_sweep.jsonl`).
4. **BRIEF 5.1 / 6 Tier 2 "the Φ fixed point ≈ ±ĥ0 with f90 ≈ 1 is the degenerate QND-cone case"; "the ĥ0 basis is
   QND-like to O(g)".** This is true only off resonance (NR_1). screen_00 is in band: its f90 ≈ 1 is a finite-N
   protection that lapses (f90 1.000 → 0.963, θ_rms 6.9 → 13.4° over N = 6 → 10).
5. **The cone lemma's "any azimuthal law"** needs at least three distinct cone points, so that S is invertible. This
   is trivial but relevant for pools whose phases 2|h0|t_k mod 2π collapse.
6. **BRIEF 1.1 sign bookkeeping**: confirmed. The screen_00 lab-z cloud sits on the 47.10° cone about −ĥ0(SPEC), i.e.
   +ĥ0(code), with mean 47.1° at ε = 0.01.

## Files
- **Scripts:** `t1_cs_lemma.py`, `t2_fixed_point.py`, `t2b_fixed_point_N8.py`, `t3_spectral.py`, `t4_cap_scan.py`,
  `t5_pool_onestep.py`, `t6_second_order.py`, `t7_h0zero.py`, `t8_sweep.py`, `t9_screen00_clouds.py`,
  `t10_h0zero_drift.py`, `t11_k51.py`, `t12_lab_vs_eps.py`, `t13_k21.py`.
- **Helpers:** `wp2lib.py`, `run.sh`.
- **Data:** `*.jsonl`, `*.json`, `*.log`, all in this folder.
