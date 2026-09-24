# Independent analysis of the rotated-self-field figure (Matan, 2026-09-23)

Model (repo convention, `core/hamiltonians/numpy_hamiltonians.py`): H = −|h₀| n̂·σ₀ − h_z ΣZ_i − J ΣZ_iZ_{i+1} − (g/√N) X₀ ΣX_i,
n̂ = (sin θ, 0, cos θ). Outcome basis = eigenbasis of h₀·σ. Both SPEC outcome pencils solved directly; R(θ') = ρ₀/(ρ₀+ρ₁)
about the fitted dipole axis, 24 bins. "Dephased ensemble" = one random phase per distinct energy level (verified to
reproduce single very long times: KS 0.08–0.20 between t=10⁶ and random draws). Steepness k fits R = c^{2k}/(c^{2k}+s^{2k}),
c = cos(θ'/2), s = sin(θ'/2); k = 1 is Born, k → ∞ is "collapse to the nearer pole", k → 0 is R ≡ ½.
Born sampling floor at 4096 iid roots, 24 bins: MAE 0.013 [0.009, 0.017] (adversarial agent). Haar null: MAE 0.32, k = 0.5.

## 1. Reproduction (N = 8–10, t = 10⁶ and dephased)
| θ (deg) | axis→ĥ₀ (deg) | MAE | pole frac | coverage |
|---|---|---|---|---|
| 0 | 0.0 | 0.076 | 0.30 | 24 |
| 20 | 0.3 | 0.094 | 0.35 | 24 |
| 45 | 1.0 | 0.078 | 0.32 | 24 |
| 70 | 1.7 | 0.111 | 0.42 | 24 |
| 85 | 2.0 | 0.137 | 0.52 | 22 |
| 89.5 | 0.9 | 0.181 | 0.69 | 24 |
| 90 | — | — | 1.00 | 2 (QND, exact) |
(N = 9, single t = 10⁶.) Pole fraction rises smoothly with θ (the QND component g sinθ σ_∥ L pins roots); axis stays on ĥ₀.

## 2. Resonance is the operative property (N = 9, θ = 0, h_z = J = 1, g = 0.1)
| \|h₀\| | 0.3 | 0.5 | 0.7 | 0.8 | 0.9 | 0.95 | **1.0** | 1.05 | 1.1 | 1.2 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pole frac | 1.00 | 1.00 | 0.97 | 0.95 | 0.79 | 0.57 | **0.30** | 0.58 | 0.79 | 0.96 | 1.00 | 1.00 | 0.93 |
| coverage | 6 | 6 | 8 | 8 | 12 | 14 | **24** | 12 | 12 | 8 | 4 | 4 | 16 |
Qubit gap 2|h₀| must match a pixel transition (2 h_z for domain-wall flips; 6 for bulk flips → partial recovery at |h₀| = 3).
Width ∝ g: at |h₀| = 0.9, g = 0.03/0.1/0.3 gives pole fraction 1.00/0.76/0.32.
Eigenvector check: at resonance 75–78 % of exact eigenstates have qubit-up weight ½ ± 0.05 (dressed pairs), 0 % at |h₀| = 0.8.

## 3. Steepness k versus coupling and size (dephased ensemble, θ = 0, J = h_z = |h₀| = 1)
| g (collective) | 0.03 | 0.1 | 0.2 | 0.3 | 0.5 | 0.7 | 1.0 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| k, N = 8 | 1.62 | 1.53 | 1.27 | 1.12 | 1.12 | 0.96 | 0.88 | 0.77 | 0.64 | 0.50 |
| k, N = 9 | — | 1.73 | — | 1.48 | 1.13 | 1.12 | 0.84 | 0.68 | 0.56 | — |
Born crossing g*: N = 5/6/7/8/9 → 0.96/0.93/0.87/0.65/0.83 (K = 6 draws; noise ≈ ±0.15 in k). J-dependence at N = 8:
J = 0.5 → g* ≈ 1.2; J = 1 → ≈ 0.7; J = 2 → k ≈ 1 over g ∈ [0.5, 1.0]. θ = 45° gives the same g* as θ = 0.
At fixed weak g = 0.1 (K = 16): k(N=5..10) = 2.23, 1.47, 1.63, 1.53, 1.43, 1.50 (θ=0); 1.82, 2.12, 1.80, 1.72, 1.57, 1.57 (θ=45).
→ k plateaus at ≈1.5, does not approach 1 with N. Azimuthal anisotropy m₂ falls with N (0.055 → 0.004 at θ = 45): cloud
becomes axisymmetric about ĥ₀. Matan's N = 12 panels: MAE 0.030–0.049 (3–4× the Born floor), all northern bins above cos²,
k ≈ 1.2–1.5 (adversarial replication and PDF-vector extraction agree).

## 4. Broadband (disordered) free-pixel bath, J = 0, h_z,i ~ U[0.6, 1.4], no tuning
| N | g | pixels within g | mixed eigenstates | MAE | k | pole | cov | axis→ĥ₀ |
|---|---|---|---|---|---|---|---|---|
| 7–10 | 0.1 | 0–1 | ≤ 0.03 | — | 4.0 (pinned) | 0.90–1.00 | 6–12 | 0 |
| 7 / 8 / 9 | 0.5 | 3 / 4 / 5 | 0.31 / 0.42 / 0.48 | 0.043 / 0.056 / 0.037 | 1.27 / 1.22 / 1.13 | 0.13 / 0.12 / 0.12 | 24 | 0 |
| 7 / 8 | 1.0 | 7 / 8 | 0.34 / 0.43 | 0.072 / 0.074 | 0.76 / 0.64 | 0.07 / 0.08 | 24 | 0 |
| off-band [1.6, 2.4] | 0.5 | 0 | 0 | 0.067 | 4.0 | 0.61 | 14 | 0 |
The same phenomenology without interactions or a matched flat band, once several partners sit within the coupling width.

## 5. Structure (my derivation; independently found by the analytic agent; refereed)
Long-time U = V W V†, W conserves the bare energy H₀ exactly, V = e^{−iS} a small t-independent dressing (‖S‖ ≈ 0.04–0.10,
= first-order Schrieffer–Wolff). Theorem (upheld): W's outcome pencil is nilpotent (energy grading) → every root of the
purely resonant dynamics sits at the +n̂ pole; resonant exchange alone collapses no superposition. Axis = n̂ because the
grading is diagonal in the qubit's own energy basis (Paz–Zurek 1999; θ = 90° is Zurek 1981's QND limit). J = 0 with RWA is
an excitation-conserving spin-½ ⊗ spin-S exchange model: exactly solvable and root-free off the pole.
REFUTED by referee: the "generic Jordan-chain amplification" reading. ‖M_U − M_W‖₂ = 0.70 (N=6), 9.05 (N=8) — 9–100× ‖S‖,
amplified by ‖W₋₋⁻¹‖ — and a random perturbation of the nilpotent M_W with the same norm throws 96 % of roots into the far
hemisphere at N=8 (exact dynamics: 6 %). The cloud depends on the STRUCTURE of the dressing V, not on its size and the chain
lengths. The block-Haar surrogate (F2) reproduces coverage, axis and the Born-leaning sign but is measurably more Born than
the exact dynamics (E₂ 0.05 vs 0.08 at equal root budget). "Why Born" therefore = the root law of V·W·V† with the actual
Schrieffer–Wolff V, not a universality statement about perturbed nilpotents.
Also from the referees: t = 10⁶ is a favourable draw for the N=12 panels (minimum of six window times at θ = 20°, 45°, second
lowest at 70°); the systematic over-steepness (v₁ − 1 ≈ 0.09–0.12) is N-independent for N = 6–12 while E₂ falls only at the
2^N sampling-floor rate; "no N-trend" is scoped to this parameter point — the manuscript's N = 11–16 trend is at
h₀ = h_z = 0.1, J = 1, g = 0.01 (manuscript/main.tex:19, supplement.tex:136) and was not re-examined here.

## 6. Falsifiable predictions for the N = 12 pipeline
(a) |h₀| = 3 gives a second (partial) collapse window; |h₀| = 0.8 or 1.2 gives pole caps of half-angle ≲ 0.3 rad.
(b) The ratio steepness k decreases through 1 as the collective g is raised from 0.1 to ≈ 0.8 and continues below 1.
(c) The fitted axis leaves ĥ₀ toward the coupling axis only for g ≳ |h₀| (≈ 11° at g = 1, 25° at g = 3, 40° at g = 10).
(d) k(N) at fixed g = 0.1 stays ≈ 1.5 for N = 12–18 (Zeus); if instead k(N) → 1 for a range of g, Born is universal.
(e) A disordered free-spin bath with ~5 near-resonant spins reproduces the figure with no matched field.

Files: h0rot_probe.py, run_dephased.py, run_broadband.py, reduction.py, fit_steepness.py; raw results in batch_*.jsonl,
deph_*.jsonl, broadband*.jsonl (scratchpad).
