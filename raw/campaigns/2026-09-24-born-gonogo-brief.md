# BRIEF: go/no-go theorem for Born-profile stable regions (ring and endpoint chain)

> Source: Agent synthesis brief for the go/no-go derivation workflow, 2026-09-24 (scratchpad `gonogo/BRIEF.md`).
> Collected: 2026-09-24
> Published: 2026-09-24

Shared brief for the derivation agents, 2026-09-24. Read it first and consult the digests for detail. Nothing here has
SPEC v1.0 gate credit, and every gate is `INCOMPLETE` (`wiki/governance/paper-readiness-ledger.md:9,15`). The
repository was only read: `git status` is byte-identical to `git_status_before.txt`.

**Sources:** [PT] `digest_prior_theorems.md`, [AP] `digest_analytic_p_theta.md`, [WM] `digest_wiki_math.md`,
[GV] `digest_governance.md`, [NU] `digest_numerics.md`, [ID] `identity/NOTE.md`, [KIT] `bornkit.py` with
`test_bornkit_results.json`, [BC] `brief_checks/brief_checks.{py,log}` (new checks for this brief, about 1 min).

**Tags:** **[REPO: label]** quotes a repository label verbatim; **[OWN-proof]** is a derivation made in this workflow and
not refereed; **[OWN-check]** is a computation made in this workflow; **[HEURISTIC]** and **[CONJECTURE]** are
proposals.

Repository paths are relative to `/Users/matanhaller/Projects/Research/collapse`.

---

## 1. Conventions

### 1.1 Hamiltonian and code mapping
- **SPEC/GOAL positive convention.** `H = h0·σ_0 + Σ_i h·σ_i + Σ_bonds(J_xx XX + J_yy YY + J_zz ZZ) + H_qD`, with
  ring `H_qD = Σ_a g_{a,N} σ_0^a Σ_i σ_i^a` (periodic) and chain `H_qD = Σ_a g_a σ_0^a σ_1^a` (open). The qubit comes
  first and Paulis have eigenvalues ±1; `U = e^{−iHT}`, blocks `U_ab = <a|U|b>`, `A, B, C, D = U00, U01, U10, U11`.
- **Builders.** `SinglePixelHamiltonianNumpy`/QuSpin subtract every term
  (`core/hamiltonians/numpy_hamiltonians.py:277-286,468-557`; `quspin_hamiltonians.py:596-661`), so **code parameter =
  −SPEC coefficient**. Exchange is `H -= Jpm(XX+YY)/2` (`:499`), i.e. SPEC `J_xx = J_yy = −Jpm/2`. Couplings are per
  edge with no N-scaling (`:139-170`), and `J` defaults to 1.0. `core/ring_chain_family.py:43-53` is positive with ring
  edges `g_x/√N, g_y/√N, g_z/N` (N ≥ 5).
- **Sign slips.** `H → −H` sends `U → U†`, whose outcome-0 roots are the fixed-input roots of U. Polar and weak
  statements are sign-invariant for real H (no `h_y`, `h_0y`); for complex H the root sets differ ([PT] §0.4:
  0.239 rad).
- **Bloch directions do not flip.** "+ĥ0(code)" = −ĥ0(SPEC) = the Bloch vector of the `H_q` ground state; use that
  phrase.
- **screen_00** (`goal_preferred_basis.md:105-108`), code values: `Jxx=1.32, Jyy=2.53, Jzz=1.10; hx=−1.34, hy=0,
  hz=1.00; h0x=−1.35, h0y=−1.69, h0z=2.01; gx=0.10, gy=0.05, gz=0.06` (SPEC flips every sign). `ĥ0(code) =
  (−0.4572, −0.5723, 0.6807)`, `|h0| = 2.9527`, and `max|g|/min|non-g| = 0.10` (exactly the ceiling). ĥ0 is 47.10°
  from z; the detector field `(h_x, 0, h_z)` is 53.3° from z and **39.3° from ĥ0** [WM D7].

### 1.2 Coupling scalings (always an explicit hypothesis)
- **Ring baselines.** SPEC §11.1: `g_{a,N} ∝ 1/N` (`SPEC.md:661-677`); moving to `N^{−κ/2}` needs a derived
  `Var(S_a) ~ N^κ` (`:679-699`), and "`1/sqrt N` is not an automatic default" (`wiki/concepts/hamiltonian-families.md:66-72`).
  The pre-SPEC user correction `g_x/√N, g_y/√N, g_z/N` (`research_reports/BORN_WEAK_COUPLING_SEARCH.md:10-17`) is used
  by Theorems D, G and H1, reports 01/03/05, and RLS. **Chain:** O(1) in N (`SPEC.md:701-707`).
- **1/N trivializes the ring [OWN-proof, AP D3; PT §0.5].** The HS norm is `|g|/√N → 0`. In the X0-conserving class the
  N-first law at every T is `δ_{F(h_0x T)}` unconditionally; elsewhere, given log-tail control, it is the decoupled law
  (one point per time). [BC] ring 1/N, T=20, N=4→8: the Tier-4 point's Jensen gap falls 0.31→0.15 while `|w|` rises
  0.77→0.89; the Tier-1 point is already near δ (gap 0.013, `|w|` 0.995).
- **Commuting-QND trichotomy** for `g_N = gN^{−α}` (`wiki/campaigns/commuting-qnd-sector.md:42-50`): α > ½ gives the
  uncoupled orbit, α = ½ a Gaussian, α < ½ the north pole.
- **Code perturbative gate** `max|g|/min|nonzero non-g| ≤ 0.1` (`scripts/eval_chain_born.py:107-117`). Its only
  provenance is a code comment, and it is not SPEC §8's `‖H_qD‖/Δ` (`SPEC.md:449-467`), so a theorem needs its own small
  parameter.

### 1.3 Time windows and limits
- **Target (`SPEC.md:383-428`).** N → ∞ at fixed T, then T → ∞, instantaneous preferred; Cesàro is a labelled
  fallback. A Cesàro no-go also excludes an instantaneous Born limit, but a Cesàro "go" does not give one [GV §3.4]. T
  must not scale with g (`SPEC.md:65`), so van Hove `g²T` is heuristic only. Theorem A forbids nontrivial fixed-N late
  limits and time selection.
- **Canonical pool.** `geomspace(100, 1000, 6)` = 100, 158.49, 251.19, 398.11, 630.96, 1000
  (`scripts/eval_chain_born.py:84-88`, `eval_preferred_basis.py:80-82`), in units of `1/min|nonzero non-g|`. Each time
  contributes 2^N roots, so **pooling equals the six-point discrete time average**, neither instantaneous nor Cesàro.
  Legacy ring leads and the Zeus array use a single `t = 10⁶`.

### 1.4 Observables
- **S_Born** (`core/born.py:187-240`): θ folded to [0, π], 100 bins, `ratio_k = h0_k/(h0_k+h1_k)`, **empty_value 0.5**,
  `S = 1 − 2Σ|ratio_k − cos²(c_k/2)| sin c_k·π/100`. Campaigns pass `θ1 = π − θ0`, so S is the **weak ratio in the lab-z
  output basis**. Range [−2.0002, 1]; flat R = ½ gives ≈ 0 and an all-pole cloud +0.0008, so check coverage ≥ 20/100.
  - **Exact-Born i.i.d. ceiling** [GV §10; NU §1.1], `1−S ≈ 7.9/√n`: 0.795±0.024 (n=1536), 0.899 (6144), 0.948
    (24576), 0.978 (131072). The ratio-RMSE64 floor at the same n is 0.047 / 0.0225 / 0.0115 / 0.0048.
- **B1** (`core/outcome_measures.py:3-14,33-65`): `S = Σk_j u_j u_jᵀ`, `m = Σk_j u_j`, `n_raw = S⁻¹m`, `B1 = |n_raw|`,
  refused if `cond(S) > 1e6`. Born ⇒ B1 = 1, n̂ = n; this is only necessary (l = 1), axis-agnostic and blind to north
  atoms [WM D1]. Closed form [ID iv]: `n_raw = −2(I − (12/5)Q)⁻¹a` from the l ≤ 2 parts of `L1`.
  - **Cone lemma [OWN-proof, KIT `dipole`; OWN-check BC-A].** A cloud on a cone of half-angle α about a gives
    `n̂ = sign(cos α)a` and `B1 = 1/|cos α|` for **any** azimuthal law. The guard does not refuse it.
  - Near-point clouds give B1 → 1 with cond only 141–321 [NU §1.3]. Always report `resultant_length` or f90 (the
    fraction within 25.8° of the axis).
  - B1 = 1 is codimension-one [WM D10], and a non-Born aberration law hits it at s* = 0.6348 [ID ii d].
- **SPEC §6** (`SPEC.md:315-377`).
  - Definitions: `E_2 = [(1/4π)∫(p0−cos²(θ/2))²dΩ]^{1/2}` (primary strong score); `E_∞` = ess-sup over supported regions;
    `E_harm` = leakage outside `(0,0),(1,0)`, must expose m ≠ 0; `E_marg` = sin-weighted L² deviation of the weak ratios
    on the supported domain; estimator robustness is required.
  - **AUDIT:** `core/outcome_measures.py:331-362` matches marginals separately and gives 0.206 on exact Born, so the
    preferred-basis E_marg values (0.881, 0.347, 0.222) are not SPEC E_marg [NU §1.2]. Use the ratio-based chain
    `E_marg_occupied` (`eval_chain_born.py:274-305`) or kit `E_ratio_occupied` instead.

### 1.5 Fixed-point condition (`wiki/concepts/collapsible-basis-dependence.md:79-103,124`)
- **Definition.** `Φ(n) = n̂_fit(C_0(n))`, with `C_0(n)` the outcome-0 cloud of `(V_n†⊗I)U`. Required: `Φ(n*) = n*`,
  unique up to ± and attracting. The campaigns never impose it (pencil basis hardcoded to z, axis fitted freely).
- **Exact facts:**
  - **Π parity [WM D8, OWN-proof].** `[H, Z_0Π_iZ_i] = 0` iff `h_0x = h_0y = h_x = h_y = 0`. Then λ ↦ −λ and **Φ(z) = ±z**
    for all N and T (all of Tier 1, and the z-field slices of Tiers 3–5).
  - **g → 0 [KIT].** `Φ(n) = u_q†n` is a rotation about ĥ0, with fixed point ±ĥ0 and a point-mass cloud. At N=6 with
    g×0.01: resultant 0.9999987, B1 1.0000013.
  - **Exact QND (§2.4).** `Φ(n) = sign(a·n)a` in one step.

### 1.6 Antipodality [REPO: PROVED] (`wiki/concepts/outcome-antipodality.md:21-25,62-79`)
- `dim ker M0(α,β) = dim ker M1(β̄,−ᾱ)` for every unitary, so `ρ1 = A_*ρ0` (λ ↦ −1/λ̄), `K1 = K0`, in **every** output
  basis (it cannot select an axis). Strong Born ⇔ `ρ0(−Ω) = tan²(θ/2)ρ0(Ω)`; weak ratio = `P(θ)/(P(θ)+P(π−θ))`.

### 1.7 Output-basis law (`collapsible-basis-dependence.md:21-63`; "derivations", no test)
- An output-basis change is `U → (V†⊗I)U`, so `N_b^(n) = w_b0N_0 + w_b1N_1`: a new pencil, not a rotated cloud. Input
  rotations are inert (rigid rotation). Bidegree (d, d): collapsible states are generic. Kit: `roots(..., axis=n)`.

### 1.8 Fixed-input duality [REPO: PROVED] (`wiki/concepts/fixed-input-outcome-equivalence.md:11-15,49-53`)
- Fixed-input roots of U = outcome-0 roots of U†; for real H they are `conj(λ0)` (same polar law, mirrored azimuths,
  flipped transverse axis components).
- The stored chain S values are fixed-input. Gap from the outcome pencil: screen_00 (`h_0y`) +0.0224 / +0.0097 /
  +0.0030 at N = 6 / 8 / 10; **screen_18 (detector `h_y`) −0.134 / −0.089 at N = 6 / 8** [NU §1.4]. 40 of 525 log
  entries have `h_y ≠ 0`.
- [KIT] full-precision `b15_s00_center`, N=8: 0.5566 (fixed) vs 0.5526 (forward); rounded parameters give 0.5622 vs
  0.5525. Third-digit rounding moves S by about 0.005 at T ≤ 1000, so quote S to ±0.01.

---

## 2. Exact tools

### 2.1 Spherical log-potential identity [OWN-proof; VERIFIED_NUMERICALLY, ID §1-2]
- **Statement.** For every unitary with a regular outcome-0 pencil, `ρ0^alg = (1/4π)[1 + Δ_S L1]`, where:
  - `L1 = (1/d) log det E1(Ω) = (2/d) log|det M0(Ω)|`;
  - `M0 = cos(θ/2)U10 + e^{iφ}sin(θ/2)U11`;
  - `E1 = M0†M0`, with `0 ≤ E1 ≤ I` (the detector effect operator).
- It is Poincaré–Lelong on CP¹; no novelty is claimed. Poles and ∞ are included.
- **Weights are algebraic.** They equal SPEC kernel weights iff `k_j/K = m_j/d` for every root (semisimple in all 15
  tests, or a single point). For a singular pencil `L1 ≡ −∞`.
- **Verification.** l ≤ 4 moments versus production QZ agree to relative error ≤ 1.5e-6 at N=6 (Tier-1/2/4 rings and
  screen_00).
- **Companion identities:** `spec E1(−Ω) = 1 − spec E1(Ω)` (antipodality again); `Ev = (1/2d)log det(E1E0)` and
  **`Od = (1/2d)Σ_k log(e_k/(1−e_k))`** (mean half log-odds); `p1 = (1/d)Tr E1 = (1+w·Ω)/2`; Theorem F is the azimuthal
  average; weak convergence ⇔ `L1 − ⟨L1⟩` converges in L¹.
- **Consequences:**
  - **(i) Strong Born about n** ⇔ `ΔOd = (n·Ω)(1+ΔEv)`. With a uniform even part this is **`L1 = c − ½n·Ω`**: the mean
    effect log-odds must be exactly `−n·Ω`. Bayesian form: prior `E = (ρ0+ρ1)/2` with Born likelihoods.
  - **(ii) Aberration.** `L1 = log p1` gives `(1−m²)/(4π(1−m cos θ')²)`, **never Born for 0 < |m| < 1**. An exactly
    scalar E1 forces an **ideal measurement** `|0><v⊥|⊗V0 + |1><v|⊗V1`, i.e. δ.
  - **(iii) Weak Born.** The polar CDF is `½[1 − cos θ + sin θ ∂_θL̄1]`.
    - With `x = log tan(θ/2)`: `ō'' = −tanh x(sech²x + ē'')`.
    - Equivalently **`P0(−dx) = e^{2x}P0(dx)`**, a fluctuation theorem: the Born log-likelihood ratio σ is calibrated.
    - A Gaussian σ satisfies it iff mean = var/2.
  - **(iv) Moments.** `∫ρ0Y_lm* = −(l(l+1)/4π)∫L1Y_lm*`.
  - **(v) Jensen.** `L1 ≤ log p1`, with equality iff E1 is scalar. **A Jensen-saturated large-N limit is never
    nondegenerate Born**, so a "go" needs an O(1) gap `G = ⟨log p1 − L1⟩`.
  - **(vi)** Strong about z ⇒ weak. Weak plus axial symmetry ⇒ strong. Counterexample to weak ⇒ strong:
    `ρ0 = (1/2π)cos²(θ/2)[1 + 2ε sin²(θ/2)cos φ]`.
  - **(vii) Coverage.**
    - δ_N, δ_S and ε-caps (to ε²/4) pass both criteria vacuously. Example: the Tier-1 ring at N=6, T=20 has θ ≤ 0.139
      and B1 = 1.0029.
    - **Every statement needs coverage**: polar support [0, π] (weak) or S² (strong).
- **Named obstruction** (OPEN for every approved family): uniform L¹ control of the small-eigenvalue log tail of E1(Ω)
  (Theorem F eq. 7, `research_reports/BORN_NONNORMAL_LIMIT.md:180-209`).

### 2.2 Polar detailed balance [REPO: PROVED, conditional on existence and nondegeneracy] (`RESEARCH_STATE.md:166-202`)
- Weak Born ⇔ `R = dP/d(P+S_*P) = cos²(θ/2)` ⇔ `P = (1+cos θ)E` with `S_*E = E` ⇔ `q(1/r) = r⁴q(r)` ⇔
  `ℓ(−x) = e^{2x}ℓ(x)` ⇔ `S_*[sin²(θ/2)μ] = sin²(θ/2)μ` ⇔ (atoms) `Q({1/r}) = r²Q({r})` ⇔
  `d_m = 2a_{2m+1} − a_{2m} − a_{2m+2} = 0` ∀m (`a_n = ⟨cos nθ⟩`) ⇔ `e^xJ''(x) = e^{−x}J''(−x)`. The **J' form is
  FALSIFIED**.
- `R(θ) + R(π−θ) = 1` always, so Born ⇔ `v1 = 1, v_odd≥3 = 0` (`BORN_STRUCTURE_ANALYSIS.md:70-107`).
- `|d0| ≤ 4‖R−B‖_∞`. No finite prefix of the `d_m` suffices, and δ0 passes vacuously.

### 2.3 Reflected-ratio lemma (`wiki/concepts/born-like-points.md:85-93`)
- `P(θ)/(P(θ)+P(π−θ)) = cos²(θ/2)` ⇔ `P = (1+cos θ)E` with E reflection-even.
- This is SPEC's weak ratio via antipodality.

### 2.4 Commuting/QND sector and the QND-cone lemma
- **Reduction** (`wiki/campaigns/commuting-qnd-sector.md:9-124`; "verified", Z basis, Cesàro). For `[H_D, M] = 0`,
  `H = H_D + h⊥X_0 + h_0zZ_0 + g_NZ_0M`, the atoms sit at `Θ_m = 2arcsin[(h⊥/Ω_m)|sin tΩ_m|]`. At `g/√N`,
  `R = 1 − (a/B)θ` against Born's `1 − θ²/4`, so **weak Born fails at every finite h_0z/g**.
- **All-axis version** [OWN-proof, WM D2-D3, unreviewed]: `θ_{n,m} = 2arcsin(|n×a_m||sin ω_mt|)`; weak Born fails in
  **every** output basis (N-first Cesàro, α = ½).
- **QND-cone lemma [OWN-proof, new; OWN-check BC-A: deviation ≤ 4.5e-15, fit = sign(a·n)a, B1 = 1/|a·n|].**
  - *Statement.* If `[H, a·σ_0] = 0`, then in every output basis n every outcome-0 root lies on the cone `a·Ω = a·n`.
    This holds for all N, T, detectors and scalings, with kernel weights equal to algebraic ones.
  - *Proof.* `U = P_+^a⊗W_+ + P_−^a⊗W_−`. A root requires `<−n|−a><−a|Ω>/(<−n|+a><+a|Ω>)` to be minus an eigenvalue of
    the unitary `W_−†W_+`. Taking moduli gives `(1+a·n)(1−a·Ω) = (1−a·n)(1+a·Ω)`. ∎
  - *Special cases:* pointer-QND (a = n = z) gives the pole; central-X (a = x, n = z) the y–z great circle; the SPEC
    first tier in a rotated basis a latitude [GV §13.1].
  - *Consequences:* 1D support, so **strong fails**; Φ(n) = sign(a·n)a with a degenerate pole fixed point; at weak
    coupling H is QND along `h_eff` to O(g), hence the |h0| ≫ g phenomenology of §5.1.

### 2.5 Resonant return [REPO: PROVED, SCOPED] (`wiki/concepts/resonant-return-dynamics.md:3-23`; `BORN_RESONANT_RETURN.md:97-161`)
- `H = [[H_+,Q†],[Q,H_−]]`, `H_± = H_D ± (h_0z + g_zL_z)`, `Q = (h_0x+ih_0y) + g_xL_x + ig_yL_y` (ring
  `L_{x,y} = Σσ/√N`, `L_z = ΣZ/N`; chain: site-1 Paulis). `G00 = [z − H_+ − Q†(z−H_−)⁻¹Q]⁻¹`,
  `C(t) = −i∫e^{−iH_−(t−s)}QA(s)ds`, `Ȧ = −iH_+A − ∫Q†e^{−iH_−(t−s)}QA(s)ds`. Exact for all families; resolvent roots
  are not physical roots; leading and full potentials differ by 0.227 (ring) and 0.655 (chain).

### 2.6 Theorem I [REPO: PROVED, SCOPED] (`BORN_RESONANT_RETURN.md:29-65`)
- For `[H_D, M_z] = 0`, `H = H_D + bZ_0 + ε(g_xX_0L_x + g_yY_0L_y)` and no transverse central fields:
  `A⁻¹C = εM_1 + O(ε³)` with `Q = (g_x+g_y)L_+ + (g_x−g_y)L_−`, and `e^{aM_z}M_1e^{−aM_z} = sM_1(1,0)`,
  `s² = g_x² − g_y²`. Leading radii depend only on `√|g_x² − g_y²|`; `cond = e^{N|η|}`; filter
  `t e^{iΔt/2}sinc(Δt/2π)`, `Δ = E_a − E_b − 2b`. Fixed t only.

### 2.7 Others
- **F** [REPO: PROVED]: `J(x)` fixes the polar law, and `J'_+` is the log-radius CDF.
- **Haar** [REPO: PROVED]: the outcome-0 roots form the exact spherical ensemble, with ratio ½
  (`manuscript/audits/THEORY_AUDIT.md:385-434`).
- **Charge grading** [REPO: PROVED]: `[H, Z_0±Q_D] = 0` ⇒ `det = λ^d det U11` ⇒ ρ0 = δ_N for every N and T.
- **Matchgate** [OWN-proof, PT §2.4]: a Gaussian chain has ≤ 2 roots ±λ* per time.
- **Ising ν** [OWN-proof, AP D4]: `¼δ_{±2h_z} + ⅛δ_{±2(h_z±2J_zz)}`. It is pure point, and `ν{0} > 0` iff
  `h_z ∈ {0, ±2J_zz}`.

---

## 3. Theorem ledger

**Key.**
- **X0?** Y means the hypotheses force `[H,X_0] = 0` (great circle; Theorem-C class).
- **Basis** Z means the qubit-Z output basis.
- **Order:** I = N-first then instantaneous T→∞; C = N-first Cesàro; t = fixed t.
- All REPO items are pre-reset except antipodality and duality (2026-09-21).

| ID | Statement | Hypotheses | Scaling | Basis/order | Status | X0? | Tiers |
|---|---|---|---|---|---|---|---|
| A | recurrence; no nontrivial fixed-N late limit | any finite H | any | any | PROVED | – | all; forces N-first |
| B | `Lδ0+(1−L)dθ/π`; Born only at L=1 | `[K,V]=0`, X coupling, central X field | any | Z/I | PROVED | Y | T1/T2 zero detector; T4 isotropic + x-field |
| C | **d0→0 only on a null set of central-X fields**; `|d̄0+1| ≤ 5/(2w|t|)` | `I⊗K − X_q⊗(V+hI)`, any detector | any | Z/I | PROVED; excludes open sets **containing** X0 seeds only | Y | T1(h0z=0), **T2(h0z=0)**, central-X of T4–6 |
| D, E, H/H1 | D: folded Gaussian → uniform (h=0); E: detuned (`bZ_q`, light tails) limit not Born; H/H1: no open detuning interval (H1 pointwise) | commuting detector | 1/√N | Z/I | PROVED (D also VERIFIED_NUMERICALLY) | D: Y; E, H: no | T1/T2 zero-detector slices |
| F | potential determines the law; log-tail route | regular pencil | – | any | PROVED | – | tool |
| G | Gaussian substitution fails: native law δ0 | `(g/√N)(XΣX+YΣY)`, `H_D=H_q=0` | 1/√N | Z/t | PROVED, VERIFIED_NUMERICALLY | no | T3/T4 warning |
| I | radii depend only on `√|g_x²−g_y²|` | charge-conserving detector, no transverse central fields | ring/chain | Z/t, O(ε) | PROVED, SCOPED | no | T3, T4, T6 |
| W/S/iff | no finite-N histogram is Born; azimuthal TV = 1; finite-support iff `tan²(θ/2) = m(π−θ)/m(θ)` (equatorial atom passes) | finite N | – | – | exact | – | any go is asymptotic |
| QND | pointer-QND: poles only | `[H,Z_0]=0` | any | Z | PROVED | no | SPEC tier 1; chain rung 0 |
| GC | great circle: roots on the y–z circle, so strong fails at every N, t | `[H,X_0]=0` (any `h_0x`) | any | Z | PROVED (`RESEARCH_STATE.md:233`) | Y | T1(h0z=0), T2(h0z=0), central-X slices |
| RP/LS | equal-multiplicity pairing gives R=½, not Born; level statistics neither necessary nor sufficient | – | – | – | listed (`RESEARCH_STATE.md:238-245`), elementary/finite-size | – | T7 |
| CG | ρ0 = δ_N; singular at `t=π/(4g)` | `h_0x=h_0y=0`, `g_y=±g_x`, U(1) detector, no transverse detector field | any | Z/all t | PROVED | no | T3(|g_y|=|g_x|), T4 |
| MG | one radius per time (atomic) | chain with `h_z, J_xx, J_yy, g_x, g_y, h_0z` only | chain | Z/t | listed PROVED (`RESEARCH_STATE.md:236`); source a REJECTED v4 candidate; OWN-proof supplied | no | T6 XY |
| Haar | R = ½ | Haar | – | any | PROVED | – | mixing gives ½ |
| R01 | commuting X ladder: binomial atoms; Cesàro uniform | `h_x, J_1x, J_2x, g_x, h_0x` | 1/√N | Z/t,C | PROVED | Y | T4/5 corner |
| R03 | `p≠0` gives uniform; `p=0` gives Cesàro `e^{−ℓ²ρ²}I0(ℓ²ρ²)`, not Born for ρ ∈ (0,6] (OWN F); chain arcsine cap | zero bonds, `g_x`, h0=0 | 1/√N | Z/C | PROVED | Y | **T1 slice J_zz=h0z=0** |
| R05 | **`m_ℓ = cos(2ℓat)e^{−2ℓ²g²σ(t)²}`**; detector `h_x≠0` gives R=½ (I and C) | ring N≥5, real uniform field + NN/NNN XYZ, `g_x`, `a=h_0x` | 1/√N | Z/t,C,I | PROVED (reports; audit 06; v3 PASS re-run) | Y | T1/T2 (h0z=0), T4/5 `g_x`-only |
| R07 / R09 | chain N-first law exists; `b1 = ν{0}`; all moments conditional (TV); replica shortcut FALSIFIED | central-X chain | chain | Z/t,C | PROVED / conditional | Y | T6 |
| R10 | **Cesàro uniform for a.e. `h_0x`** | central-X chain and ring, any detector | 1/√N | Z/C | PROVED (reports); Ising exceptions ⊂ `{(mh+2nJ)/ℓ}` (AP D4) | Y | **T2**, T6 |
| RLS | ring `g_z` irrelevant given log-tail control | ring `g_z/N` | g_z/N | any/t | PROVED, conditional | – | T3/T5 |
| QAI | `W(h_0x) = e^{−2ih_0xt}W(0)`; fragility scale 1/t | central-X, h0z=0 | any | Z | exact, VERIFIED_NUMERICALLY | Y | T2, T4 leads |
| ISO | isotropic Heisenberg drops out | `J_xx=J_yy=J_zz`, uniform field and couplings | ring | any | exact | – | T4 isotropic = free |
| CQ | Z-basis weak obstruction | `[H_D,M]=0`, `Z_0M` | α=½ | Z/C | "verified" | no | SPEC tier 1 + h⊥ |
| – | **Withdrawn/falsified:** perturbative completion (SUPERSEDED/REJECT); `J'` relation; open phase `P_B` (contradicts C); report-08 completion (v4 REJECT); replica shortcut; "surrogate observable"; "`h_0x` rescues plain QZ"; WP5 misalignment reading ("Disputed"); preferred-basis prediction ("neither half ... confirmed") | | | | | | |

**Own entries.**
- **Tier-1 ring, slice `h_0z = 0`** [PT G; AP D4, D6]: pure-point ν, so no ordinary limit; Cesàro
  `d0 = 8g²I + O(g⁴) > 0` with `I = 1/(8h_z²) + ¼[(2h_z+4J)⁻² + (2h_z−4J)⁻²]`, so weak fails at O(g²); Cesàro S ≤ 0.06
  at g/h ≤ 0.05, with peaks of 0.93–0.95 only at g ~ the smallest detector frequency.
- **Folded-Gaussian family** [AP D5]: never Born; best S = 0.944 at v = 0.358 (a non-perturbative window).
- **Other slices:** chain Tier-1 at `h_0z = 0` gives solvable caps, S ≤ 0.51 [AP D7]; the Tier-1 base
  (h_z = J_zz = 0) gives caps of radius ~2g|G|/|h_0z| [AP D8].
- **Tier 1–3 Ising chain with `h_D ∥ z`** [PT §5; NU 6.1]: `Z_{i≥2}` are conserved, giving ≤ 4 roots per time,
  identical for every N, so never Born.
- **Also:** QND all-axis, QND cone, Π parity, and ID (i)–(vii).

---

## 4. Numerical-evidence ledger (SPEC convention unless "code"; all PRELIMINARY_NUMERIC/legacy; full tables NU §3)

- **The SPEC order has never been probed** [NU §2]. Chain windows have `T/t_LR = 20–63` and `T ≥ t_H = 2π2^{N+1}/W`
  for N ≤ 10 (screen_00 `t_H` = 60 / 193 / 651 at N = 8 / 10 / 12); the SPEC order needs `N ≳ v_LR T ≈ 500` at
  T = 100. N=12 per-time scores are flat (0.72–0.83), so the chain measures an **equilibrated finite-chain law**. Ring
  leads at `t=10⁶` have `T/t_H(sector) = 18–2×10³`.
- **The orders differ in the ring [OWN inference].** Config 353 (N=17, `t=10⁶`, inside R05 scope) has
  `(a1,a2) = (0.7049, 0.4181)` (`BORN_STRUCTURE_ANALYSIS.md:109,405`). R05's N-first law is a folded Gaussian at every
  t, forcing `a2 = a1⁴ = 0.247`, so this near-Born law (d0 ≈ −0.008) is not the N-first law at any t.
- **Chain in the SPEC order at accessible T [OWN-check BC-C]** (screen_00, lab z). The dipole is N-independent to 1e-5
  at N ≥ 6–7 for T = 1, 2, and to ~1e-4 at N = 8–9 for T = 4. The cloud is a near-point mass (`1−resultant` =
  1.8e-3 / 4.3e-3 / 1.1e-2): kinematic plus O(gT). Born-relevant `T ≳ 1/g²` needs N ~ 500, so only analysis reaches it.

| Tier | Evidence | Budget-controlled trend | Reading |
|---|---|---|---|
| 1 ring | **1a** isotropy-grid ZZ slice: h0=0, `g_x=−0.01/√N`, N=11–14, `t=10⁶`; 0 near-Born cells. **1b** probe: `J_zz=h_z=−1`, `h_0z=−r`, `g_x=−0.1/√N`, N=6–10, pooled window | off resonance (r = 0.5, 2, 3): f90 0.9–1.0, S ≤ 0.22. At r=1: thinned-384 S 0.11/0.16/0.30 (i.i.d.-Born ≈ 0.6). At r = 0.97, 1.03: flat 0.34–0.47 | signal **only at resonance** (codimension 1); 1a is X0-conserving |
| 2 ring | **2a** h0 tilt 10–90° at `|h0| = 1 = |h_z|`. **2b** QAI on config 353: RMSE 0.0081 → 0.353 at `h_0x = 7.85e-7` | thinned 0.18→0.32 (θ ≤ 20°), flat ≈ 0.42 (45°); θ=90°: S ≈ −0.6, refused (X0) | all probes **on the resonance `|h0|=|h_z|`**; fragility scale 1/t |
| 3 ring | **3a–c** `g_y` probes: thinned S 0.25–0.43. **3d** Markovianity: best S +0.325, a budget artefact (−0.39±0.13 thinned). **3e** 079/047 perturbations at N=5–7: INCONCLUSIVE | flat or weak | nothing Born-like |
| 4 ring | **4a/4b** X-only NN/NNN leads: RMSE 0.051→0.027 thinned (floor 0.016), N=14→17. **4c** config 353: S 0.956, RMSE 0.0081 (floor 0.0055). **4d** grid: near-Born 0/0/10/35 at N=11–14, 30/45 at non-perturbative `|h_z|=0.01`. **4e/4f** 079 plateau ≈ 0.70, 047 improving. **4g** XXZ + h0: 0.35→0.14 | only X0-conserving leads improve | **4a–4d are X0-conserving** (not seeds, by C), h0=0, single t, NNN outside GOAL |
| 5 ring | **5a** XYZ probe: thinned 0.33/0.25/0.24; h0-basis f90 0.95. **5c** N10 champions: no scaling, X0-conserving | flat or declining | no evidence |
| 6 chain | **6.1–6.2** Ising `h_D∥z`: bit-identical across N. **6.3'/6.4** TFIM + `g_z` 0.759 thinned (N=10); XXZ Δ=0.5 cloud 0.650. **6.5 screen_00**: cloud 0.717±0.033; centre thinned 0.557→0.707 (N=8–12), **deficit ≈ 0.12 vs same-budget Born, flat at N=10–12**. **6.5s** strong: B1 1.302/1.150/0.880 (+21σ/+11σ/−27σ); odd leakage 10×/13×/31× floor; axis 3.0° resolved at N=12. **6.5φ** fixed point ≈ ĥ0, f90 ≈ 1, S 0.13–0.35. **6.6** screen_18 (h0=0) fixed point, N=8: B1 1.043, odd 0.035 (floor 0.025), S 0.745, f90 0.29 | plateau | resolved non-Born (reverse order); strong non-Born at every N; one near-strong h0=0 datum at one size |

**Rules for every new number:** same-budget Born floors or thinning; f90 or resultant beside B1; never the
preferred-basis E_marg; the outcome pencil when `h_y ≠ 0`; state the scaling, sign convention, time object and `T/t_H`.

---

## 5. Conflicts and open gaps

### 5.1 Preferred axis
GOAL says the axis "aligns with the detector field". At screen_00 this is **false**, and the alignment that exists is
kinematic.
- **The g → 0 cone [OWN-check, KIT `g0_kinematic_baseline`].** The pooled lab-z cloud is a cone about ĥ0, so by the
  cone lemma `n̂ = −ĥ0(SPEC)` and `B1 = 1/cos 47.10° = 1.469` exactly. At g×1 / 0.1 / 0.01: B1 = 1.367 / 1.419 / 1.452
  (N=6) and 1.302 / 1.439 / 1.459 (N=8).
- The campaign's "1.5–3° from ĥ0" is therefore free precession; the detector shows up only in the departure from 1.469.
  The Φ fixed point ≈ ±ĥ0 with f90 ≈ 1 is the degenerate QND-cone case.
- **Detector alignment appears only at h0 = 0:** the fixed point is 5–26° from `h_D` and 7–9° from `g∘h_D` (two cells,
  N=8) [NU §4.3]. [HEURISTIC] This is the mean-field axis `h_eff = h0 + g∘⟨σ_D⟩`.
- **WP5 is flawed.** Its "`h_z` is the only detector field" contradicts `h_x = −1.34`
  (`wiki/campaigns/preferred-basis-campaign.md:74,268`), and its `h0 ∥ z` "B1 = 1.011" is a pole cloud (f90 1.0,
  S 0.13, 24 bins).

### 5.2 Conflicts
1. **Degenerate passes.** SPEC's weak wording (`SPEC.md:309`) passes δ, caps and equatorial atoms. Every off-resonance
   weak-coupling limit tends to such a pass. Coverage (§2.1 vii) must be added.
2. **Scaling.** Every nontrivial ring theorem is at 1/√N, while SPEC's 1/N trivializes the ring. A "go" at 1/√N needs a
   §11.2 justification.
3. **Pencil and weights.** Prior theorems use the fixed-input pencil with algebraic weights, SPEC the outcome pencils
   with kernel weights. They agree for real H with semisimple roots, and differ for `h_y`, `h_0y` and defective
   pencils. The singular-continuum rule is still owed (`paper-readiness-ledger.md:134-135`).
4. `RESEARCH_STATE.md:220-221` ("no time averaging") conflicts with SPEC's Cesàro fallback; SPEC controls, and
   `goal.md` (Cesàro-primary, ledger retired) is subordinate. `RESEARCH_STATE.md:40-41` ("pure transverse coupling ...
   mandatory") is contradicted by `R(θ)+R(π−θ)=1` and Theorem C. `RESEARCH_STATE.md:50-52` ("`h_x≠0` forces R=½") means
   the detector `h_x`, ring only.
5. The chain N-trend at fixed T crosses from `T ≫ t_H` (N=8) to `T < t_H` (N=12).
6. **Probe placement.** Every Tier 2–4 ring probe has `|h0| ≈ |h_z|`, a resonance under §6 T2; off-resonance tilts are
   untested.
7. The best weak cases use NNN terms, the non-approved chain/all geometry, or no g-scaling.

### 5.3 Open gaps
- **G1.** N-first limits and **log-tail control** outside the X0 and commuting classes: THE obstruction.
- **G2.** No theorem for the generic interior (Tier 1/2 with `h_0z ≠ 0`, multichannel Tiers 3–5, interacting chains
  beyond matchgate and Ising).
- **G3.** No all-axis obstruction outside QND; Φ never imposed with an N-trend or cloud; uniqueness and attractivity
  unstudied.
- **G4.** Whether the reverse and SPEC orders commute is untested (config 353 suggests not).
- **G5.** The strong criterion has only negative results.
- **G6.** Resonance manifolds are known only at first order; multi-flip resonances are unanalysed.
- **G7.** Chain Cesàro laws are open: matchgate `θ*(t)`, the Tier-1 torus, interacting chains at `h_0x = 0`.

---

## 6. Per-tier programme

For each tier: settled, open, candidates (C), attack, and checks (K). Rings use
`{'x':'1/sqrtN','y':'1/sqrtN','z':'1/N'}` and are repeated with `'1/N'`.

### Tier 1: Ising ring `{J_zz, h_z, h_0z, g_x}`
**Settled.** Π-symmetric, so z is an exact fixed point and B1(z) is genuine. **Slice `h_0z = 0`** (X0-conserving, so
strong fails): `J_zz = 0` gives R03 (not Born); `J_zz ≠ 0` gives R05 with pure-point ν (no ordinary limit), Cesàro
`d0 = 8g²I > 0`, and R = ½ at resonant `h_z ∈ {0, ±2J_zz}`. Zero detector: E and H1. Under 1/N: δ_N (conditional).

**Open.** Generic `h_0z ≠ 0`.

**Candidates.**
- **C1.1 [CONJECTURE; first order HEURISTIC, WM D6].** *Resonance selection.* The flip `X_0X_i` costs
  `2[h_0z z_0 + z_iε_m]`, with `ε_m = h_z + mJ_zz`, `m ∈ {−2, 0, 2}`. Off `R1 = {|h_0z| = |ε_m|}` (distance δ), typical
  roots stay within `O(g/δ)` of the pole uniformly in t and tend to δ_N as g → 0 (a degenerate pass). On R1 the spread
  is secular, but R1 has codimension 1, so there is **no open weak-coupling Born region at first order**.
  **GOAL Q5:** `h_0z = h_z` is **neither necessary nor sufficient**; it is one member of R1, and the multi-flip
  resonances `2h_0z = Σ_odd ±2ε_{m_j}` are dense.
- **C1.2 [CONJECTURE].** *Classical-label (Gaussian-bath) reduction at 1/√N, given log-tail control.* The N-first law at
  fixed T is `Law(u_ξ(T)†|0>)` with `i∂u = (h_0zZ + gξ(s)X)u`, where ξ is the classical Gaussian process with
  covariance `C(s) = cos(2h_zs)cos²(2J_zzs)` (quasi-periodic, three frequencies). Rationale: at the infinite detector
  temperature implicit in `L1`, collective commutators vanish in HS norm; R05 proves the X0 case; Theorem G fails only
  for defective (charge-graded) pencils. As T → ∞ this is a torus average: pole-concentrated off R1, a cap or uniform
  on R1. **Not Born** [HEURISTIC].

**Attack.** Prove C1.1 off the small-divisor set with the hypercube-flip structure and Theorem I or Volterra, or prove
C1.2 and analyse the one-qubit problem. Hard point: uniform-in-T control of the O(g³) terms near multi-flip resonances.

**Checks.**
- **K1.1.** T ∈ {20, 50}, N = 4..10: sweep `h_0z` through `{h_z, h_z ± 2J_zz}` (step 0.02), recording mean `sin²(θ/2)`,
  coverage and B1(z). The peak positions should not depend on N.
- **K1.2.** Compare l ≤ 4 moments from `log_potential` at fixed T, N = 4..10, with a C1.2 Monte Carlo (labelled as a
  separate surrogate experiment). A gap shrinking like `N^{−1/2}` supports C1.2.
- **K1.3.** [BC] Jensen gap at 1/√N: 0.39 → 0.27 for N = 4 → 8 at T = 20. Does it plateau above 0?

### Tier 2: `{J_zz, h_z, h_0x (+h_0z), g_x}`
**Ambiguity.** Is `h_0z` retained? As posed, Tier 2 is X0-broken and Π-broken; its `h_0z = 0` slice is X0-conserving.
**Treat both.**

**Settled.**
- **On `h_0z = 0`, a Z-basis NO-GO:** C (no open `h_0x` set); R10 (Cesàro uniform for a.e. `h_0x`; Ising exceptions
  ⊂ `{(mh_z+2nJ_zz)/ℓ}`, with nonzero resonant ones at S ≤ 0.04, while the exception `h_0x = 0` is the Tier-1 slice,
  S = 0.90 only at non-perturbative g/h = 0.4 [AP D4]); great circle; QAI fragility 1/t.
- **For all h0** [OWN]: at g → 0 the axis is ±ĥ0 (kinematic), and the ĥ0 basis is QND-like to O(g). "`h_0x` rotates the
  preferred basis" is thus the trivial n* ≈ ĥ0 + O(g), and that basis is degenerate.

**Candidates.**
- **C2.1 [HEURISTIC].** The resonance condition becomes the qubit splitting `|h0| = |ε_m|`, independent of tilt; the
  longitudinal part adds only `ε_m = 0`.
- **C2.2 [CONJECTURE].** In the ĥ0 basis the law tends to δ as g → 0 off resonance, so the Ising detector has no open
  Born region in any basis; the stability region shrinks to the resonance manifolds.

**Attack.** Work in the ĥ0 frame: the longitudinal part feeds R05-type dephasing, and the transverse part feeds the
Tier-1 resonance machinery with `h_0z → |h0|`.

**Checks.** **K2.1** off-resonance `|h0|` (0.6, 1.5; `h_z = J_zz = −1`) at tilts 20° and 45°, N = 6..10, in the lab
and ĥ0 bases (prediction: f90 > 0.9 in the ĥ0 basis). **K2.2** sweep `|h0|` for peaks at 1 and 3. **K2.3** report
`B1/B1_kin` with `B1_kin = 1/|cos∠(ĥ0,z)|`.

### Tier 3: add `g_y`
**Settled.** Charge-graded slice (`h_0x = h_0y = 0`, `g_y = ±g_x`, no transverse detector field): δ_N for every N and T
(degenerate, codimension ≥ 2). Singular pencils at `t = π/(4g)`. Theorem I: leading dependence only on `√|g_x²−g_y²|`.
Theorem G: shortcuts fail. RLS: ring `g_z/N` conditionally irrelevant. No positive result.

**Open.** `h_0x ≠ 0`, i.e. the tier as posed.

**Candidates.**
- **C3.1 [OWN-proof via I].** At leading order with `h_0x = h_0y = 0`, multichannel coupling is single-channel with
  `g_eff = √|g_x²−g_y²|`. Any multichannel advantage must come from return terms or from `h_0x` breaking the grading.
- **C3.2 [HEURISTIC, ID §4].** Near the graded slice, Jordan blocks of size up to N+1 split as `ε^{1/s}`, so the limits
  ε → 0 and N → ∞ may not commute.

**Attack.** Imaginary gauge with O(ε³) control uniform in N, or show that `cond = e^{N|η|}` defeats it.

**Checks.** **K3.1** `h_0x = ε ∈ {0.01, 0.05}` near `g_y = g_x`, N = 4..10, T = 20: max θ, the `log_potential` dipole,
and the fraction of E1 eigenvalues below 1e-8; a spread growing with N means the limits do not commute.

### Tier 4: XXZ ring
**Settled.** The isotropic point is the free detector (ISO). `M_z` conservation brings in charge grading and Theorem I.
The central-X subfamily is covered by C, R05 and R10. The X-only leads 4a–4d are X0-conserving, so they **cannot seed an
open phase**.

**Open.** h0 ≠ 0 with `g_x ≠ ±g_y`; the probes decline.

**C4.1 [CONJECTURE].** Exchange turns the flip energies into a band, so resonance `|h0| ∈ band` is open, but with a
golden-rule rate `Γ ∝ g²ν_ac(2|h0|) > 0`. Under C1.2 the T → ∞ flow goes to uniform (½), not to Born, so XXZ does not
beat Ising.

**Checks.** **K4.1** Jensen gap and `|w|` at fixed T, N = 4..10, with h0 inside and outside the band ([BC] Tier-4 point
at 1/√N: gap 0.39–0.56, non-monotone). **K4.2** harmonic moments at N=8 for T = 10–100: do they flow toward 0?

### Tier 5: XYZ ring
**Settled.** Central-X subfamily with detector `h_x ≠ 0` gives R = ½ (R05); C for every detector; RLS.

**Open.** The multichannel X0-broken interior.

**Current reading.** *Load-bearing:* h0 (the QND axis), the g components transverse to `h_eff`, the detector
spectral weight at `2|h0|`, and exact conserved quantities (X0, Z0, `Z_0±Q_D`, Π), each a no-go or a degeneracy.
*Decorative at leading order:* `g_z/N`, `g_x` versus `g_y` beyond `√|g_x²−g_y²|`, and isotropic exchange.

**Checks.** **K5.1** `fixed_point_axis` at N = 6..9 for three `|h0| ≫ g` and three h0 = 0 points (report f90,
resultant, B1). **K5.2** Jensen gap versus N.

### Tier 6: endpoint chain
**Settled.**
- **Ising `h_D ∥ z` analogues of Tiers 1–3:** ≤ 4 atoms per time, identical for every N, never Born.
- **Matchgate (XY + `h_z`):** one radius per time; the T → ∞ law is `δ_{π/2}` (an equatorial degenerate pass) if the
  boundary return decays, and quasi-periodic with bound states [HEURISTIC].
- **Central-X:** R07, R10 and C. `g_z` has no N-decay, and the QND-chain Z-basis obstruction holds.
- **Chain specifics:** no CLT (so C1.2 fails), but a light cone, so the SPEC order is reached at `N ≳ 2v_LR T` ([BC]:
  exact by N = 6–9 for T ≤ 4).

**Open.** Interacting chains at `T ≳ 1/g²`. The 0.12 plateau is a reverse-order object.

**C6.1 [HEURISTIC].** In the SPEC order the qubit is an impurity on a semi-infinite chain, seeing the
infinite-temperature boundary spectral function of `σ_1^a`. If it is a.c. at `2|h_eff|` the law flows to uniform (½); if
gapped, it stays near the kinematic cone. Neither is Born, so ring and chain would share one mechanism, differing only by
1/N suppression and the light cone.

**Checks.** **K6.1** screen_00 and XXZ Δ=0.5 at T ∈ {1, 2, 4, 8}: raise N from 3 to convergence, then follow the
dipole, `1−resultant` and Jensen gap in T.

### Tier 7: unified statement (target form)
**T7 dichotomy [CONJECTURE; components marked].** Fix the geometry, the scaling hypothesis, `g ∈ (0, g0)` and coverage.

**(a) Exact no-go classes [PROVED].** No open Born region contains a point of the X0-conserving class (C, R10, GC),
the commuting or detuned-commuting classes (B, D, E, H), the charge-graded class (δ), any exact-QND class
`[H, a·σ_0] = 0` (cone law, degenerate fixed point), the Tier-1 Ising chain or the matchgate chain, or the 1/N ring
(unconditionally in the X0 class, conditionally elsewhere).

**(b) Conditional no-go [PROVED modulo G1].** Any Jensen-saturated N-first limit is an aberration law, never
nondegenerate Born.

**(c) Generic interior [CONJECTURE].** Off resonance: near-QND about `h_eff`, a pole or cone (degenerate pass).
Resonant or mixing: flow to uniform ½ (the Haar/Theorem D paradigm). Born would need an O(1) Jensen gap with mean effect
log-odds exactly `−n·Ω` in an attracting Φ-fixed basis; no approved mechanism gives this stationarily.

**Expected honest outcome.** A no-go on every controlled regime, plus a named OPEN residual: G1, and C1.2/C6.1 for the
T → ∞ flow.

**Mechanism answers.** Dephasing gives ½; symmetry protection gives degenerate passes; level statistics are
irrelevant; near-Born finite-size values are reverse-order equilibrated objects.

---

## 7. bornkit usage

**Command.** Scratch scripts go only in the gonogo folder. The system `python3.11` lacks NumPy. Keep N ≤ 10 and runs
under ~10 min.
```
OMP_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1 \
NUMBA_CACHE_DIR=/private/tmp/claude-501/-Users-matanhaller-Projects-Research-collapse/a80d1dd1-a402-486a-a849-db2bbda07b88/scratchpad/gonogo/numba_cache \
/Users/matanhaller/Projects/Research/collapse/.venv/bin/python script.py
# in script: import sys; sys.dont_write_bytecode=True; sys.path.insert(0,"<gonogo dir>"); import bornkit as bk
```

**API** (SPEC convention; keys `h0x h0y h0z hx hy hz Jxx Jyy Jzz gx gy gz`, missing = 0, unknown keys raise).
- `code_to_spec(p)`, `perturbative_ratio(p)` (chain rule, before scaling), `normalize(p)`, `ring_scale_factors(N, s)`.
- `build_H(topology, N, p, ring_scaling=None)`: dense, float64 when H is real. The ring needs N ≥ 3 and an explicit
  scaling (`'none'`, `'1/N'`, `'1/sqrtN'` or a dict with keys x, y, z); the chain takes none. `evolve(H)` gives
  `.U(T)` and `.Us(times=TIMES)`.
- `roots(U or [U...], outcome=0, axis=None, pencil='forward'|'fixed_input', weights='unit'|'kernel',
  solve_directly=False, return_info=False)` returns lab-frame Bloch points and weights. Lists are pooled; `axis=n`
  rotates the output basis (outcome 0 = collapse to |+n>); outcome 1 is the antipode; `'kernel'` needs N ≤ 6 and a
  regular pencil.
- Scores: `s_born(bloch, w, bins=100, axis)` (repository S plus coverage); `polar_ratio(...)` (R with NaN in empty
  bins, `E_ratio_occupied`); `resultant_length` (point-mass guard); `dipole` → `(n̂ or None, B1, cond)`;
  `fixed_point_axis(U, n_init, iters=30)` (Φ iteration, trajectory carries resultant and cond).
- `log_potential(U, grid or (θ, φ))` = `(2/d)log|det(q0U10 + q1U11)|`: −inf on roots (mask them); lists give the
  mean. The kit calls this pencil "M1" where ID calls it "M0"; same object.
- Constants: `TIMES`, `S_BORN_BINS = 100`, `PERTURBATIVE_RATIO = 0.1`, `PENCIL_SOLVER_OPTIONS`.

**Validated** (`test_bornkit_results.json`):
- `build_H` matches both builders with negated parameters (≤ 8.9e-15) and `ring_chain_family` (3.6e-15).
- Kernel residuals ≤ 4.1e-14 (24 cases; no infinite roots encountered); antipodality in rotated bases ≤ 2.3e-14;
  fixed-input = forward(U†) to ≤ 2.5e-14.
- Reproduces the stored B1 at N=8 (1.3018211, to 5e-14) and N=10 (1.1495865, 281 s), and `b15_s00_center` S at N=8
  (0.5566085) exactly.
- Haar gives B1 = 0.0012, S ≈ 0; `log_potential` moments agree to ≤ 1.5e-5 (l ≤ 4); Φ converges to ±ĥ0 for screen_00.

**Timings** (per T, 2 threads). N=8: eigh 0.02–0.34 s, pencil 0.5–0.7 s, `log_potential` 1.2 ms/point. **N=10:** eigh
1.2–6.5 s, pencil **40–51 s**, `log_potential` 53 ms/point. N=6: 0.07 ms/point. Six pooled times at N=10 ≈ 5 min;
avoid N ≥ 11.

**Caveats.** `k_j = 1` is the campaign convention (use `'kernel'` when defectiveness matters). QZ scatters defective
clusters (charge-graded N=5: 26/32 within 1.4e-3) and the B1 guard then says `ok`, so use `log_potential` on degenerate
slices. `dipole` does not refuse cones or near-points: print the resultant and f90. Φ convergence is not Born evidence
(kinematic at g → 0). `fixed_input` = forward only for real H. Pooled is a discrete time average, not Cesàro. Parameter
rounding moves S by ≈ 0.005. Accurate `log_potential` moments need a ~200×400 Gauss–Legendre grid.
