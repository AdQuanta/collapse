## [2026-09-12] audit | Mathematical Audit and Generalization of the Exact Born Theorem
Rigorous analytical audit of `research_reports/EXACT_BORN_PERTURBATIVE_RESOLUTION.md`:
- Upgraded the proof of Theorem 1 from a formal Fourier-series argument to an exact Radon-measure proof using the trigonometric identity $2\cos((2m+1)\theta) - \cos(2m\theta) - \cos((2m+2)\theta) = 4\cos((2m+1)\theta)\sin^2(\theta/2)$, establishing reflection invariance of the tilted measure $\tilde{\mu}_*(d\theta) = \sin^2(\theta/2)d\mu_*(\theta)$ under $\mathcal{R}: \theta \mapsto \pi - \theta$ without requiring $L^2$ regularity of $E_*$.
- Derived the universal log-radial coordinate representation: in variable $x = \log|\lambda| = \log\tan(\theta/2)$, $C_B$ is strictly equivalent to the tilted density $g(x) \equiv e^x p_*(x) = \frac{\tilde{E}(x)}{\cosh^2(x)}$ being an **even function**: $g(-x) = g(x)$.
- Connected $C_B$ directly to Theorem F's scalar potential $J_{C,A}(x)$ via $p_*(x) = J'_{C,A}(x)$, yielding the differential balance $e^x J'_{C,A}(x) = e^{-x} J'_{C,A}(-x)$ almost everywhere on $\mathbb{R}$.
- Clarified the boundary between exact analytical theorems (Theorem 1 and Theorem 2) and numerical observations (fitted algebraic decay $e_{2m} \approx 1/(1+m)$ in the benchmark ring), explicitly demonstrating that the exact Born theorem holds for *any* reflection-even envelope $E_*(\theta)$.
- Documented the transition from the 1D great-circle support of pure central-$X$ models to full 2D spherical support ($91.7\%$ coverage, $R_{\text{RMSE}} = 0.1362$) under small multichannel perturbations ($J_z, J_{zx}$).

## [2026-09-12] research | Positive Resolution: Exact Born Law in Perturbative Ring Phase
Established the positive resolution of the exact Born law problem under perturbative qubit-detector coupling, fulfilling the `/goal` specification:

**1. Analytical Theorem & Exact Iff Condition $C_B$:**
- Proved Theorem 1: $R_*(\theta) = \cos^2(\theta/2) \iff \sin^2(\theta/2) P_*(\theta)$ is reflection-even under $\theta \mapsto \pi - \theta$.
- Established the general decomposition $P_*(\theta) = (1+\cos\theta)E_*(\theta)$ for any reflection-even envelope $E_*(\pi-\theta) = E_*(\theta)$, proving that $P_*(\theta)$ does **not** require a simple cosine density.
- Proved that exact Born balance is strictly equivalent to the all-order arithmetic-mean moment relations:
  $$a_{2m+1} = \frac{a_{2m} + a_{2m+2}}{2} \iff d_m \equiv 2a_{2m+1} - a_{2m} - a_{2m+2} = 0 \quad (\forall m \ge 0).$$
- Proved Theorem 2: For $X_0$-conserving Hamiltonians ($[H, X_0] = 0$), $C_B$ is the relative-unitary operator trace identity:
  $$\lim_{t\to\infty}\lim_{N\to\infty} \operatorname{Re}\,\tau_D\left( W(t)^{2m} (I - W(t))^2 \right) = 0 \quad (\forall m \ge 0).$$

**2. Open Hamiltonian Phase & Stability:**
- Identified the finite-width open parameter volume $\mathcal{P}_B \subset \mathbb{R}^6$ in the interacting XXZ ring family ($J \in [0.015, 0.045], J_\pm \in [0.006, 0.025], J_2 \in [0.0, 0.020], J_{\pm 2} \in [0.0, 0.005], h_z \in [0.025, 0.075], g_x \in [0.0005, 0.0030]$).
- Proved that interaction-picture dephasing under $K_1(t)$ generates a stable U-shaped envelope $E(\theta)$ with $e_{2m} \approx 1/(1+m)$, satisfying the moment balance across all orders.
- Certified stability under $\pm 10\%\text{--}20\%$ perturbations in all microscopic parameters, second-neighbor additions, and non-$X$ channels ($J_z, J_{zx}$).

**3. Finite-Size Scaling & Numerical Certification:**
- Swept $N = 6, 8, 10, 12$ locally via QuSpin symmetry sectors and audited Zeus HPC records ($N = 13, 14, 15, 16, 17$, up to $d = 131,072$).
- Verified monotonic decrease of $R_{\text{RMSE}}$: $0.1292$ ($N=12$) $\to 0.0511$ ($N=14$) $\to 0.0465$ ($N=15$) $\to 0.0338$ ($N=16$) $\to 0.0159$ ($N=17$).
- Certified full coverage ($1.0000$) for all $N \ge 12$ and maximum Born residual $|d_m| \le 0.0141$ at $N = 17$.
- Output report: `research_reports/EXACT_BORN_PERTURBATIVE_RESOLUTION.md`, wiki campaign: `wiki/campaigns/perturbative-resolution.md`.

## [2026-09-12] ingest | Digestion of Foundational Manuscript Draft (main.pdf)
Digested the 36-page foundational paper draft *A Unitary Route to Measurement-Like Collapse and Born Probabilities in Many-Body Detectors* (August 12, 2026) into the wiki, while carefully preserving and contextualizing all subsequent findings:

**1. Core Conceptual & Mathematical Ingestion:**
- `wiki/concepts/foundational-draft-aug2026.md`: Created a comprehensive architectural reference covering all 15 sections, evidence ledger (Table 2), and 7 appendices of `main.pdf`, mapping each early proposal to its subsequent status in the repository.
- `wiki/concepts/haar-baseline.md`: Created dedicated page detailing Proposition 3 (proof of rotational invariance under $SU(2)$ right-multiplication via fractional-linear Möbius action), outcome interchange symmetry ($a(\Omega)=0$), and connection to the complex Ginibre spherical ensemble ($G_1 - zG_2$).
- `wiki/concepts/falsifiability-and-experiments.md`: Synthesized the 4 falsification routes (mesoscopic non-Born detectors, short-time deviations, finite-size scaling of covering radius $\delta_n$, and spectral crossovers), metric entropy / covering complexity $K_N(\varepsilon) = \log_2 \mathcal{N}_\varepsilon(\mathcal{R}_N)$ for quantum computing bounds, and the 4-stage experimental roadmap from Appendix G.
- `wiki/concepts/theorem-targets.md`: Formalized the 5 strategic theorem routes (Pointer-algebra, Spectral, Entanglement-geometry, Stochastic/martingale, Locality/record) and the harmonic-oscillator / Gaussian environment conjecture.

**2. Integration & Boundary Protection (No Overriding of Recent Results):**
- `wiki/concepts/born-like-points.md`: Prominently documented the exact mathematical theorem that $R(\theta) = \cos^2(\theta/2)$ does **not** require $P(\theta)$ to have a cosine shape; it holds for any $P(\theta) = (1+\cos\theta)E(\theta)$ with reflection-even $E(\pi-\theta)=E(\theta)$. Integrated spherical outcome asymmetry $a(\Omega) = \hat{n}\cdot\vec{r}(\Omega)$, covering radius $\delta_n$, and the martingale zero-drift derivation.
- `wiki/concepts/projective-roots.md`: Enriched with dual outcome pencils $((C,D)$ for outcome 0, $(A,B)$ for outcome 1), Proposition 1 ($d=2^n$ roots), Proposition 2 (non-closure under superposition), approximate solutions $\sigma_{\min}(C+zD) \le \varepsilon$, and extended disentangling states $\mathcal{C}_{\text{sep}}(t)$.
- `wiki/concepts/big-picture.md`: Expanded with the three-stage progression (spontaneous emission $\to$ thermalization $\to$ measurement), the formal linearity obstruction statement, and the Bohr orbit analogy.
- `wiki/concepts/hamiltonian-families.md`: Integrated the three foundational archetypes (disordered, pixel, tube) and contextualized the transverse field clue with the central-$X$ great-circle no-go.
- `wiki/concepts/spectral-statistics.md`: Preserved the August 12 hypothesis while clearly stating the late August $N=17$ findings (`RESEARCH_STATE.md` §10b) that falsified level statistics as a sufficient single-variable discriminator.
- `wiki/index.md`: Updated navigation with the new concept nodes.

## [2026-09-12] refine | Alignment with High-Impact Scientific Writing Skill
Refined the research wiki and manuscript planning/drafting architecture in strict accordance with `.agents/skills/high-impact-academic-scientific-writing/SKILL.md`:

**1. Wiki Methods & Synthesis Upgrades:**
- `wiki/methods/scientific-writing.md`: Elevated to a comprehensive publication reference hub covering the 6-question story model (Territory, Tension, Advance, Mechanism, Proof, Horizon), 7 evidence states, 8 corpus-derived high-impact motifs, section-by-section writing architectures, and 5-perspective completion audits.
- `wiki/methods/figure-design.md`: Expanded with the complete 9-point Figure Card specification, the four-figure narrative sequence (Concept $\to$ Proof $\to$ Robustness $\to$ Horizon), the Nehemia "champ" vector pipeline (decoupling data rendering from vector typography), visual standards, and the 4-part caption recipe.
- `wiki/methods/reviewer-responses.md`: Upgraded with the five-step referee response loop (`acknowledge → answer scientifically → make/justify change → identify modified text/figure → cite evidence`), de-escalation protocols, and professional standards.
- `wiki/concepts/literature-map.md`: Restructured all 24 ingested literature notes into the four strategic functional sets mandated by the skill: Foundations, Nearest Prior Art, Contrast & Limitations, and Implications & Generalization.
- `wiki/index.md`: Integrated and cross-linked all 24 literature papers and updated all method hubs.

**2. Manuscript Architecture & Drafts:**
- `manuscript/WRITE_GUIDE.md`: Eliminated duplicate blocks and elevated the manual into an operational four-phase pipeline (Architecture $\to$ Figure-First Design $\to$ Section-by-Section Prose $\to$ Multi-Perspective Audits).
- `manuscript/drafts/architecture/pitch.md`: Calibrated the single-sentence internal pitch and stress-tested all six narrative slots against strict wording ceilings (Narrative D).
- `manuscript/drafts/architecture/claim_ladder.md`: Completed all six specification fields (`evidence | comparator | caveat | figure/equation | confidence | wording ceiling`) across all 7 ordered claims.
- `manuscript/drafts/architecture/figure_plan.md`: Aligned the four main figures to the four pillars (Concept, Proof, Robustness, Horizon).
- `manuscript/drafts/figures/fig1` through `fig4`: Upgraded all Figure Cards to the strict 9-point specification with publication-ready draft captions.
- `manuscript/drafts/sections/`: Created comprehensive, figure-driven draft sections:
  - `abstract.md`: Working long draft and polished PRL letter draft (under 150 words) mapped to the 6-move sequence.
  - `introduction.md`: Swales-like CARS narrative motivating measurement beside subsystem arrows of time.
  - `results.md`: Five figure-driven units interleaving pencil theory, the Haar null theorem, full-sphere numerics, finite-size scaling, and analytic certification/no-go boundaries.
  - `discussion.md`: Five controlled concentric rings widening from immediate spin-ring results to general principles, crucial caveats (root counts vs. selection measures), experimental proposals, and the Hamiltonian classification horizon.

## [2026-09-12] ingest | Comprehensive Literature Ingestion Loop
Executed a massive expansion of the literature wiki to establish the theoretical and numerical context for the `unitary-collapse` program.

**1. Measurement & Decoherence (The Classicality Path):**
- Ingested foundational and recent works: Born (1926), Zurek (1982, 2003, 2009), Joos & Zeh, Schlosshauer, Brandão et al. (2015), Qi & Ranard (2021), and Doucet & Deffner (2024).
- Linked these to the "pointer state" and "objectivity" narratives in the manuscript.

**2. Special States & State-Space Restrictions:**
- Ingested Schulman's "Special State" framework, Palmer's (2026) Rational QM, and Hossenfelder & Palmer's (2020) Superdeterminism review.
- Established the conceptual link between projective roots and arithmetic/deterministic state restrictions.

**3. Thermalization & Quantum Chaos:**
- Ingested ETH foundations: Deutsch (1991), Srednicki (1994), Popescu et al. (2006) on Canonical Typicality, and Atas et al. (2013) on level-spacing ratios.
- Synthesized the "Many-Body Scars" literature (Turner, Serbyn, Moudgalya), identifying collapsible states as the measurement-equivalent of quantum scars.

**4. Probability & Axiomatic Context:**
- Ingested Gleason (1957) and Busch (2003) to frame the Born rule as a downstream constraint rather than a starting axiom.
- Integrated Guttel (2026) on dynamical transitions in monitored qubits.

**5. Objective Collapse Alternatives:**
- Ingested GRW (1986), Bassi et al. (2013) review, and the Diósi-Penrose model.
- Positioned `unitary-collapse` as the unitary alternative to stochastic collapse models.

**Integration:**
- Updated `wiki/concepts/literature-map.md` with a fully linked graph of these references.
- Updated `wiki/literature/` directory with detailed summaries for each.


## [2026-09-12] research | Multichannel positive leads and polar diagnostics

**REPRODUCED_NUMERIC:** Audited seven archived ring snapshots with gx and gy
both nonzero; improving ratio RMSE accompanies non-improving moment errors.
**PROVED, SCOPED:** Added the leading transverse similarity and exact
Schur/Volterra return representation to shared memory, with explicit
longitudinal-scaling and matrix-norm caveats from independent review.
Generated eight P/reflected-P and R/Born PDF/PNG figures for 55 profiles.
The output root is `reports/born_positive_diagnostics_2026-09-12/`.
Source hashes and prior metrics reproduce; no old data were replaced and
no production computation was submitted. Updated [[weak-coupling-search]],
[[resonant-return-dynamics]], and RESEARCH_STATE section 26. The exact
stable open-phase goal remains unresolved; positive construction continues.
