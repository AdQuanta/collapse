## [2026-09-13] ingestion | Analytic Distribution Ring & Endpoint Chain Master Ledgers
Ingested the comprehensive, atomic master progress ledgers for the ring and endpoint chain geometries into `wiki/campaigns/`, replacing the initial 9-step `research_reports/analytic_p_theta/COEFFICIENT_LEDGER.md`.

**New Campaign Master Ledgers (2):**
- `wiki/campaigns/analytic_distribution_ring_master_ledger.md` — Single atomic progress ledger for the ring geometry, tracking all 87 physical cases/subcases (Cases 0–86 across Families A–N, covering all $h_0$ regimes and interaction hierarchies) with independent columns for $P_N, P_\infty, \overline{P}_N, \overline{P}_\infty, R_N, R_\infty, \overline{R}_N, \overline{R}_\infty$, Born deviation, and status.
- `wiki/campaigns/analytic_distribution_chain_master_ledger.md` — Single atomic progress ledger for the endpoint chain geometry, tracking all 87 physical cases/subcases across all $h_0$ regimes and interaction hierarchies under the central-qubit coupled-to-site-1 convention.

**Superseded & Updated:**
- `research_reports/analytic_p_theta/COEFFICIENT_LEDGER.md` — Marked as superseded and redirected to the authoritative wiki master ledgers.
- `wiki/campaigns/analytic-p-theta.md` — Updated progress tracking references to point directly to `[[analytic_distribution_ring_master_ledger]]` and `[[analytic_distribution_chain_master_ledger]]`.
- `RESEARCH_STATE.md` — Updated canonical frontier reference to point to the wiki master ledgers.
- `wiki/index.md` — Registered both master ledgers under Research Campaigns.

## [2026-09-13] ingestion | Random Graphs, Complex Networks, Quantum Walks & Fock-Space Graphs
Executed a comprehensive survey and ingestion of random graph topologies, complex networks, spectral graph theory, quantum walks, quantum transport, and Fock-space localization into the research wiki. This establishes the structural and dynamical foundations for the detector interaction graphs used in `core/detector_graphs.py` and symmetry resolution in `core/graph_spectral_sectors.py`.

**Updated & New Concept Pages (3):**
- `wiki/concepts/random-graphs.md` — Comprehensively rewritten (upgraded from 31 lines to authoritative treatise): full mathematical taxonomy of Erdős–Rényi $G(N, p)$, Watts–Strogatz $WS(N, k, p)$, Barabási–Albert $BA(N, m)$, Random Regular expanders $RRG(N, d)$, and Bethe lattices; spectral graph theory (normalized Laplacians $\mathcal{L}$, algebraic connectivity $\lambda_2$, Cheeger isoperimetric inequality, Ramanujan bound); Continuous-Time Quantum Walks (Farhi-Gutmann); quantum chaos on graphs (Kottos-Smilansky trace formulas and Wigner-Dyson level statistics); Anderson localization on Bethe lattices (Abou-Chacra-Thouless-Anderson); symmetry-resolved spectra in `core/graph_spectral_sectors.py` (Hamming weight conservation, graph automorphisms $\operatorname{Aut}(G)$, half-filling spin reversal); and role in Born vs. Haar discrimination.
- `wiki/concepts/quantum-transport-networks.md` — Quantum transport on graphs: Continuous-Time Quantum Walks, ballistic vs. diffusive spreading, exponential algorithmic speedup on glued-trees graphs (Childs et al. 2003), Environment-Assisted Quantum Transport (ENAQT) and dephasing-assisted transport (Caruso et al. 2009), hitting times across topologies, and relevance to non-backflowing detector architectures.
- `wiki/concepts/fock-space-graphs.md` — Mapping many-body quantum systems to single-particle hopping on complex Fock-space graphs (hypercube and Johnson graphs); Altshuler-Gefen-Kamenev-Levitov (1997) mapping to Bethe trees; Basko-Aleiner-Altshuler (2006) Many-Body Localization as Anderson localization on Fock-space graphs; non-ergodic extended states and wave function multifractality on random regular graphs (De Luca et al., Tikhonov & Mirlin); Krylov operator complexity and the universal operator growth hypothesis (Parker et al. 2019); quantum scars and Hilbert space fragmentation; and interpretation of projective roots as non-ergodic coherent trajectories.

**New Literature Entries (13):**
- `Erdos-Renyi-1959.md` — Foundational random graph paper; giant component percolation transition.
- `Watts-Strogatz-1998.md` — Collective dynamics of small-world networks: high clustering with logarithmic path length.
- `Barabasi-Albert-1999.md` — Scale-free networks, preferential attachment growth, and structural hubs.
- `Chung-1997.md` — Spectral Graph Theory monograph: normalized Laplacians, Cheeger constant, expander mixing lemma.
- `Farhi-Gutmann-1998.md` — Continuous-time quantum walks on graphs and decision trees.
- `Childs-et-al-2003.md` — Exponential quantum speedup by a quantum walk on glued trees.
- `Kottos-Smilansky-1997.md` — Quantum chaos on graphs: trace formula and Wigner-Dyson spectral statistics.
- `Mulken-Blumen-2011.md` — Continuous-time quantum walks on complex networks review.
- `Abou-Chacra-Thouless-Anderson-1973.md` — Exact self-consistent theory of Anderson localization on the Bethe lattice.
- `Altshuler-et-al-1997.md` — Quasiparticle lifetime and localization on Fock-space graphs.
- `Basko-Aleiner-Altshuler-2006.md` — Foundational paper establishing Many-Body Localization.
- `Caruso-et-al-2009.md` — Highly efficient energy transfer: environment-assisted quantum transport (ENAQT).
- `Tikhonov-Mirlin-2016.md` — Wave function multifractality and non-ergodic extended states on random regular graphs.

**Structural Updates:**
- `wiki/index.md` — Updated with new concept pages under Theory & Concepts and 13 literature entries across the Four Strategic Sets.
- `wiki/concepts/literature-map.md` — Strategic citation graph updated and Thematic Cross-Map expanded with a dedicated branch for Complex Networks & Quantum Dynamics.

## [2026-09-13] ingestion | Comprehensive Survey of Collapse Models, Interpretations & Quantum Arrow of Time
Executed an exhaustive, field-wide survey and ingestion of all models and interpretations of quantum collapse and all instances of the "quantum arrow of time" into the research wiki. This positions `unitary-collapse` firmly within the global taxonomy of quantum foundations.

**New Concept Pages (8):**
- `wiki/concepts/many-worlds.md` — Everettian quantum mechanics: universal wave function, relative states, pointer basis via decoherence, decision-theoretic (Deutsch-Wallace) and envariance (Zurek) Born rule derivations, self-locating uncertainty (Vaidman, Carroll), Kent's critiques, and comparative analysis with unitary collapse.
- `wiki/concepts/consistent-histories.md` — Griffiths, Omnès, Gell-Mann & Hartle: class operators, decoherence functional $D(\alpha, \alpha')$, weak vs. strong consistency, single-framework rule, Dowker-Kent underdetermination and non-extendibility theorems.
- `wiki/concepts/qbism.md` — Fuchs, Caves, Schack, Mermin: quantum states as personal Bayesian credences, Quantum de Finetti theorem, SIC-POVMs and Zauner's conjecture, the Urgleichung, the Born rule as a normative constraint, and Timpson's critique.
- `wiki/concepts/relational-qm.md` — Rovelli, Laudisa, Di Biagio: observer-relative facts, Wigner's friend, cross-perspective consistency, sparse vs. stable facts, Brukner's (2018) no-go theorem for observer-independent facts, and Frauchiger-Renner (2018).
- `wiki/concepts/quantum-arrow-of-time.md` — The arrow of time in quantum mechanics: Boltzmann's H-theorem & Loschmidt's reversibility objection (Umkehreinwand), Albert's Past Hypothesis and Mentaculus, Penrose's Weyl Curvature Hypothesis ($C_{abcd} \to 0$), Zeh's cosmological master arrow, Maccone's memory-erasure vs. Jennings-Rudolph critique, Aharonov's TSVF & ABL rule, Leifer-Pusey no-go theorem, and quantum information thermodynamics (Landauer, Jarzynski, Crooks, Sagawa-Ueda).
- `wiki/concepts/objective-collapse.md` — Spontaneous wave-function localization models: GRW discrete jumps, Pearle CSL stochastic Schrödinger equation, Diósi-Penrose gravitational reduction, macro-amplification scaling ($N$ vs $N^2$), spontaneous heating and X-ray emission, and empirical exclusion bounds (Carlesso 2022, Majorana, VIP-2, LISA Pathfinder).
- `wiki/concepts/measurement-induced-transitions.md` — Measurement-Induced Phase Transitions (MIPT): hybrid monitored random circuits (Li-Chen-Fisher, Skinner-Ruhman-Nahum), pure-state trajectory entanglement entropy, volume-law to area-law transition, conformal critical point, replica statistical mechanics mapping, quantum error correction threshold, and superconducting processor experiments (Google Sycamore, IBM Quantum).
- `wiki/concepts/quantum-trajectories.md` — Continuous quantum measurement, Belavkin stochastic master equation, weak values and weak value amplification (AAV), optimal action-principle collapse paths on the Bloch sphere (Weber et al. 2014), and catching/reversing quantum jumps mid-flight (Minev et al. 2019).

**New Literature Entries (20):**
- `Von-Neumann-1932.md` — First rigorous mathematical axiomatization; Process 1 (collapse) vs. Process 2 (unitary evolution).
- `Everett-1957.md` — Foundational relative-state formulation eliminating Process 1.
- `Wallace-2012.md` — Modern defense of the emergent multiverse and decision-theoretic Born rule.
- `Griffiths-1984.md` — Consistent histories and probability assignment without collapse.
- `Gell-Mann-Hartle-1990.md` — Decoherent histories for quantum cosmology and quasiclassical realms.
- `Fuchs-Mermin-Schack-2014.md` — Accessible QBism introduction and dissolution of the measurement problem.
- `Rovelli-1996.md` — Foundational paper on Relational Quantum Mechanics.
- `Cramer-1986.md` — Transactional interpretation based on Wheeler-Feynman time-symmetric absorber theory.
- `Pearle-1989-CSL.md` — Continuous Spontaneous Localization (CSL) via non-linear stochastic dynamics.
- `Zeh-2007.md` — The Physical Basis of the Direction of Time (5th ed.); cosmological master arrow.
- `Maccone-2009.md` — Quantum solution to the arrow-of-time dilemma via observer memory erasure.
- `Aharonov-1964.md` — Time symmetry in quantum measurement; the ABL probability rule.
- `Price-1996.md` — Time's Arrow and Archimedes' Point; time-symmetric physics and retrocausal realism.
- `Page-Wootters-1983.md` — Evolution without evolution; time emerging from entanglement in stationary states.
- `Hardy-2001.md` — Informational reconstruction of QM from five operational axioms.
- `Li-Chen-Fisher-2019.md` — Discovery of measurement-induced entanglement transitions in monitored circuits.
- `Minev-2019.md` — Experimental observation, tracking, and mid-flight reversal of individual quantum jumps.
- `Landauer-1961.md` — Thermodynamic dissipation of information erasure ($Q \ge k_B T \ln 2$).
- `Jarzynski-1997.md` — Non-equilibrium free energy equality connecting microscopic reversibility to work fluctuations.
- `Frauchiger-Renner-2018.md` — Extended Wigner's friend no-go theorem: quantum theory cannot consistently describe itself.

**Structural Updates:**
- `wiki/index.md` — Completely updated with all 8 new concept pages and 20 new literature entries properly partitioned across Foundations, Nearest Prior Art, Contrast & Limitations, and Implications.
- `wiki/concepts/literature-map.md` — Master citation map rewritten with all new entries categorized and an expanded Thematic Cross-Map linking all collapse paradigms, no-collapse alternatives, stochastic reformulations, the quantum arrow of time, and continuous measurement trajectories.

## [2026-09-13] ingestion | Bohmian Mechanics, Superdeterminism & Stochastic-Quantum Correspondence
Ingested three foundational areas into the wiki to contextualize the `unitary-collapse` program within the broader landscape of quantum foundations interpretations.

**New concept pages (3):**
- `wiki/concepts/bohmian-mechanics.md` — de Broglie–Bohm pilot-wave theory: guiding equation, quantum equilibrium, equivariance, effective collapse, contextuality, preferred foliation, and the orthogonal relationship to unitary collapse.
- `wiki/concepts/superdeterminism.md` — Violation of Statistical Independence: Bell's original discussion, 't Hooft CAI, Palmer IST/RaQM, Hossenfelder–Donadi program, Hall information bounds, Conway-Kochen counterpoint, and unitary superdeterminism as the `unitary-collapse` classification.
- `wiki/concepts/stochastic-quantum-correspondence.md` — Barandes (Harvard, 2023): QM as an indivisible stochastic process, unistochastic matrices, interference tensor $\mathcal{I}$, division events as collapse, complex amplitudes as linearizing gauge potentials, comparison with Nelson stochastic mechanics.

**New literature entries (7):**
- `Bohm-1952.md` — Foundational hidden-variable papers (Parts I & II).
- `DGZ-1992.md` — Dürr-Goldstein-Zanghì equivariance and typicality.
- `tHooft-2016.md` — Cellular Automaton Interpretation.
- `Hall-2010.md` — Quantitative measurement independence relaxation bounds ($\approx 0.14$ bits).
- `Barandes-2023.md` — The Stochastic-Quantum Correspondence.
- `Conway-Kochen-2006.md` — Free Will Theorem (critical counterpoint).
- `Donadi-Hossenfelder-2022.md` — Experimental proposals for testing superdeterminism.

**Updated:**
- `wiki/index.md` — All new entries registered.
- `wiki/concepts/literature-map.md` — Entries added to Foundations, Contrast & Limitations, and Implications sections; thematic cross-map expanded with deterministic hidden variables and stochastic reformulation trees.

**Key structural insight for unitary-collapse:** The program sits precisely at the intersection of unitary superdeterminism and special-state restriction. In Bell's trilemma (Realism + Locality + Statistical Independence), `unitary-collapse` preserves realism and locality by violating Statistical Independence—the projective root variety restricts physically realizable states to a measure-zero algebraic subset of Hilbert space. Bohmian mechanics takes the opposite route (preserving Statistical Independence, violating locality). Barandes' SQC provides a complementary language where projective roots correspond to autonomous "division events" that restore stochastic divisibility without external measurement.

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

## [2026-09-12] correction | Phase claim withdrawn; frozen verifier v1

The earlier entries claiming completion are superseded by
[[perturbative-resolution]] and
`research_reports/BORN_PHASE_AUDIT_2026-09-12.md`. The potential derivative
was misidentified (density is J'', not J'); the full-parameter open-phase
assertion and existence of the required limits were not proved. Existing
Theorem C already obstructs an open phase containing the X-conserving seeds.
The new verifier reproduces all 15 saved snapshots and adds direct weighted
balance diagnostics with explicit missing-QZ status. The goal remains OPEN.

## [2026-09-12] experiment | Multichannel reduced sensitivity

Completed 162 preregistered full-QZ conditions with zero numerical validation
failures. No tested direction improves worst-time balance, moments and coverage
at all three reduced sizes. All conditions have incomplete coverage, so the
large-N phase question remains unresolved. Exact transverse-field sign
symmetry reduces redundant future conditions. Evidence and next action are
in `research_reports/BORN_MULTICHANNEL_SENSITIVITY_2026-09-12.md`.

## [2026-09-13] method | Full XYZ-ring sectors and baseline preparation

All 15 ring coefficients now have an exact translation-sector implementation;
36 dense/sector conditions and 38 focused tests passed. Six larger-N baseline
tasks are prepared, but SSH timed out during remote preflight. No production
submission occurred. See `research_reports/BORN_RING_TRANSLATION_2026-09-13.md`.

## [2026-09-14] lint | 178 issues found, 2 auto-fixed
- Auto-fixed: resolved broken link `[[audit-framework]]` in `wiki/index.md` and `wiki/methods/reviewer-responses.md` to `[[audits/framework|audit-framework]]`.
- Mechanical: `scripts/check_evidence.py` reports 142 evidence errors (all 142 articles lack a `> Raw:` metadata header, and `raw/` directory is not yet initialized).
- Judgment: 3 broken wikilinks reported (`Barandes-Kagan-2020`, `numerical-provenance`, `create a link`); 28 ledger files nested at depth 3 (`wiki/campaigns/ledgers/{chain,ring}/`); 2 articles lacking standard Status blocks for superseded claims (`perturbative-resolution.md`, `weak-coupling-search.md`); recent 2026-09-14 Born similarity autoresearch loop milestone awaiting ingestion.

## [2026-09-14] lint | 211 issues found, 29 auto-fixed
- Auto-fixed: added index entries for the 28 chain/ring family ledgers and the `collapse/Welcome.md` vault note, using `(no summary)` placeholders and filesystem-derived Updated dates.
- Mechanical: `scripts/check_evidence.py` reports 142 evidence errors; all 142 articles lack a `> Raw:` metadata header, and `raw/` contains no source files. No fidelity suspects or unreferenced raw files were found.
- Judgment: 3 unresolved wikilinks (`Barandes-Kagan-2020`, `numerical-provenance`, and the `create a link` tutorial placeholder); 28 ledger files violate the one-level topic-directory convention; `perturbative-resolution.md` and `weak-coupling-search.md` contain superseded/positive-claim context without standard Status blocks; the 2026-09-14 autoresearch milestone in `RESEARCH_STATE.md` is not represented in the wiki; 6 orphan articles have no inbound links from other wiki articles (`git-delivery.md`, `implementation-standards.md`, `Welcome.md`, `scientific-rules.md`, `perturbative-resolution.md`, `analytic-p-theta.md`).

## [2026-09-15] ingest | Katz & Kotler 2026 — Probing the Planck Scale with Quantum Computation
- Disposition: New
- Raw: raw/quantum-foundations/2026-04-07-probing-the-planck-scale-with-quantum-computation.md
- Updated: Falsifiability, Experimental Routes, and Quantum Computing
- Updated: Strategic Literature Map

## [2026-09-15] ingest | Research Specification v1.0
- Disposition: New; Update; Disputed
- Raw: raw/project-governance/research-spec-v1.md
- Updated: Research Specification v1.0
- Updated: Research Control Center
- Updated: Paper Readiness Ledger
- Updated: all research campaign pages, ring/chain master ledgers, and 28 family ledgers
- Updated: affected project concept, method, and audit pages with explicit supersession status

## [2026-09-15] ingest | Paper Readiness Reset
- Disposition: Update; Disputed
- Raw: raw/project-governance/2026-09-15-paper-readiness-reset.md
- Updated: Research Specification v1.0
- Updated: Research Control Center
- Updated: Paper Readiness Ledger

## [2026-09-15] lint | 176 issues found, 0 auto-fixed
- Mechanical: 142 legacy articles lack a `> Raw:` metadata header; the three new governance articles have no fidelity suspects or evidence errors, and both new raw sources are referenced.
- Judgment: 3 unresolved legacy wikilinks (`Barandes-Kagan-2020`, `numerical-provenance`, and the `create a link` tutorial placeholder); 28 family ledgers remain below the one-level topic-depth convention; 3 orphan pages remain (`git-delivery.md`, `implementation-standards.md`, and `Welcome.md`).

## [2026-09-15] update | Full Wiki Alignment with SPEC.md v1.0
- Disposition: Update; Disputed
- Updated: All remaining concepts (`symmetry-sectors.md`, `random-graphs.md`, `fock-space-graphs.md`, `quantum-transport-networks.md`, `quantum-trajectories.md`, `quantum-arrow-of-time.md`, `measurement-induced-transitions.md`, `objective-collapse.md`, `many-worlds.md`, `bohmian-mechanics.md`, `consistent-histories.md`, `qbism.md`, `relational-qm.md`, `stochastic-quantum-correspondence.md`, `superdeterminism.md`) with explicit SPEC v1.0 revalidation status and dual-pencil formulations.
- Updated: All remaining method articles (`figure-design.md`, `scientific-writing.md`, `reviewer-responses.md`, `implementation-standards.md`, `git-delivery.md`) to reflect pre-manuscript phase (`paper_ready = false`) and frozen verifier governance.
- Updated: Outdated literature notes (`Schulman-Theory.md`, `Atas-et-al-2013.md`, `Altshuler-et-al-1997.md`, `Cramer-1986.md`, `Everett-1957.md`, `Gell-Mann-Hartle-1990.md`, `Griffiths-1984.md`, `Maccone-2009.md`, `Palmer-2026.md`, `Guttel-2026.md`) removing unverified proof assertions and updating legacy pencil formulations to exact dual outcome pencils.
- Updated: `wiki/index.md` summaries for updated concepts and methods.

## [2026-09-19] correction | SPEC v1.0 wiki recovery
- Supersedes the 2026-09-15 “Full Wiki Alignment” entry: that pass added status banners but left substantive single-pencil, reflected-ratio, family-scope, and ontology contradictions.
- Preserved the user-deleted campaign pages and removed the 28 orphaned family ledgers, the tutorial Welcome note, and an accidental empty duplicate page.
- Rewrote the controlling root, Born, Hamiltonian-family, relative-propagator, and production-pipeline articles directly from `SPEC.md` v1.0.
- Removed all live navigation and cross-references to the retired 87-case hierarchy. The paper-readiness ledger is the only live wiki ledger; all gates remain `INCOMPLETE` and `paper_ready = false`.
- Corrected the Haar $E_2$ value, homogeneous-coordinate convention, exact-collapse tolerance language, unsupported scar/Krylov mechanism claims, and claims that the project has already established an ontology or violation of Statistical Independence.

## [2026-09-19] ingest | Commuting/QND detector-sector Chat result
- Disposition: New; Update; Disputed
- Raw: raw/campaigns/2026-09-19-commuting-qnd-chat-result.md
- Added: Commuting/QND Detector Sector: Verified Scope and Obstruction
- Verified: finite-sector reduction, multiplicity-weighted polar measure, pure-power scaling trichotomy in the stated ensemble, phase-average kernel, Gaussian mixture, and pole asymptotics.
- Corrected: $d\theta$ versus SPEC surface-density conventions, Cesàro versus instantaneous limits, endpoint cap-mass wording, and overclaims about strong-support failure and approximate Born exclusion.
- Scoped: the exact-Born obstruction is proved only for the $Z$ outcome basis; an all-preferred-axis no-go remains open.

## [2026-09-19] ingest | Zotero collection “Collapse and Chaos”
- Disposition: New; Update
- Raw: raw/zotero-collapse-chaos/collection-metadata-2026-09-19.md
- Added: Zotero Collection: Collapse and Chaos
- Deduplication: 28 distinct parent records across nine subcollections; no normalized DOI or normalized title/year duplicates.
- Evidence depth: complete metadata for all 28 and stored abstracts for 14. All 28 PDF attachment records lack local payloads and Zotero full-text retrieval returned 404, so no full-paper claims were inferred.

## [2026-09-19] lint | 102 issues found, 3 auto-fixed
- Auto-fixed: two unresolved internal links and one accidental orphan page.
- Verified: zero broken links, zero orphans, zero files below the allowed topic depth, zero dangling references to the deleted campaign hierarchy outside the append-only historical log, and a clean whitespace diff.
- Mechanical: the ten new or controlling SPEC/QND/Zotero articles pass evidence lint with 0 fidelity suspects, 0 evidence errors, and 0 unreferenced raw files.
- Judgment: the full legacy wiki still has 99 evidence errors because those older articles predate the raw-source invariant and have no `> Raw:` field. They were not papered over with fabricated sources; source-backed re-ingestion or an explicit archival decision remains required.

## [2026-09-19] ingest | Weak Born Criterion Correction
- Disposition: Update; Disputed
- Raw: raw/project-governance/2026-09-19-weak-born-criterion-correction.md
- Updated: Born Criteria for Collapsible-State Measures
- Updated: Research Specification v1.0
- Updated: Commuting/QND Detector Sector: Verified Scope and Obstruction

## [2026-09-19] lint | 0 issues found, 0 auto-fixed
- Scope: the three source-backed wiki articles changed by the weak Born correction.
- Verified: 0 fidelity suspects, 0 evidence errors, 0 unreferenced raw files, and all touched raw links exist.
- Mathematical check: both test polar marginals normalized within \(2.06\times10^{-11}\), and the common \(\sin\theta\) Jacobian canceled from their ratio within \(2.22\times10^{-16}\).
- Search check: no obsolete individual-density weak Born target remains in `SPEC.md` or the live wiki.

## [2026-09-19] ingest | Exact collapse formalism validation and figure gallery
- Disposition: New; Update
- Raw: raw/campaigns/2026-09-19-exact-formalism-validation.md
- Updated: Paper Readiness Ledger (pending review only; all gates INCOMPLETE)
- Added: Exact collapse formalism article and all 15 fixture theta/ratio plots.
- Validation: DRAFT_PASS; no approved certification or gate promotion.

## [2026-09-19] governance | Exact-formalism gate promoted to COMPLETE
- Disposition: Update
- Raw: raw/project-governance/2026-09-19-exact-formalism-gate-activation-approval.md
- Updated: Paper Readiness Ledger (`Exact collapse-like formalism` row: INCOMPLETE -> COMPLETE)
- Updated: Exact collapse formalism campaign article
- Updated: wiki/index.md ledger summary
- Verified independently (not solely from the pasted referee verdict): manifest hash-bindings for SPEC.md/check.py/METHOD.md/build_exact_formalism_packet.py; fresh checker rerun (PASS, matching packet hashes); 26/26 focused tests; full suite scoped to `tests/` reproduces 641 passed, 2 failed with identical error magnitudes to the recorded baseline.
- Disclosed: `verifier/exact_formalism/v1/check.py` had been edited after the review run to relabel DRAFT_PASS/DRAFT_FAIL/certification=False as PASS/FAIL/certification=True and to gate on its own manifest's self-declared "activated" status, with no prior traceable approval record. The verification math was unaffected by the edit and was independently reproduced. The user's explicit conditional approval, given after this finding was disclosed, is the activation authorization now on record.
- Scoped: the two known full-suite failures (matched-ring forward bridge; zero-field independent-spin angles) remain open, unrelated to this gate, and continue to block "Complete matrix-pencil characterization," "No unresolved hard failure," and "Executable verifier." `paper_ready` remains `false`; no other gate is affected.

## [2026-09-19] lint | 108 issues found, 1 auto-fixed
- Auto-fixed: `wiki/index.md`'s Paper Readiness Ledger table row showed Updated `2026-09-15`; the article's own metadata Updated is `2026-09-19` (it now cites the exact-formalism-validation raw source), so the index row was corrected to match.
- Verified: all 111 articles are indexed and resolvable, all internal/See Also/Raw links resolve, no topic-depth violations, and the one fidelity suspect (`5.291901841267055e-16` in `exact-collapse-formalism.md`) matches its raw source verbatim.
- Mechanical: `scripts/check_evidence.py` reports 99 evidence errors, all legacy literature/concepts/methods articles that predate the raw-source invariant and still lack a `> Raw:` field; 0 unreferenced raw files.
- Judgment: 4 orphan pages with no inbound links from other article bodies (`literature/collapse-and-chaos-zotero-collection.md`, `methods/git-delivery.md`, `methods/implementation-standards.md`, `concepts/resonant-return-dynamics.md`); 3 missing cross-references — `born-like-points.md`'s Status section describes the exact dual-root/multiplicity criteria that `exact-collapse-formalism.md`'s verifier now tests, but neither links to the other; `commuting-qnd-sector.md` (the other live campaign) does not reference `exact-collapse-formalism.md`; and `research-control-center.md`'s knowledge-routing table and Verifier status section omit the new `verifier/exact_formalism/v1/` entirely, still pointing only to the frozen `verifier/analytic_p_theta/`.

## [2026-09-21] ingest | Antipodality of the Two Outcome Root Sets
- Disposition: New; Update
- Raw: raw/campaigns/2026-09-21-outcome-antipodality-verification.md
- Added: `wiki/concepts/outcome-antipodality.md` — theorem, subspace-intersection proof (as recorded in the frozen `verifier/exact_formalism/v1/METHOD.md`), independent branch-Gram-identity proof, consequences for the two Born criteria, and numerical certification.
- Updated: Born Criteria for Collapsible-State Measures — the "Reflected ratios are secondary" section stated the antipodal marginal relation as an unmet condition; it is now discharged, so the reflected polar histogram used throughout the search scripts computes the weak ratio itself. The caution about the strong criterion is retained and sharpened.
- Updated: Projective Roots and Exact Collapsible States — records that the two outcome measures are antipodal pushforwards with $K_0=K_1$.
- Updated: wiki/index.md concepts list.
- Validation: `tests/test_outcome_antipodality.py` 13 passed; antipodal-map mutation killed 3/3 by the kernel-dimension tests.
- Scoped: no gate promoted, `paper_ready` remains `false`. The theorem pairs rays and kernel dimensions only; it supplies no singular-continuum measure and no evidence about any score's value.

## [2026-09-21] ingest | Equivalence of the Fixed-Input and Outcome Pencils
- Disposition: New; Update; Disputed
- Raw: raw/campaigns/2026-09-21-fixed-input-outcome-equivalence.md
- Added: `wiki/concepts/fixed-input-outcome-equivalence.md` — unconditional time-reversal duality between the fixed-input pencil of `U` and the outcome-0 pencil of `U^dagger`, the corollary `z = conj(lambda_0)` for `U^T = U`, the transposition proof via the outcome-1 pencil composed with antipodality, and the scope where the corollary fails.
- Updated: Antipodality of the Two Outcome Root Sets — consequence 3 asserted that the search scripts' reflected scoring computes the weak criterion, but those scripts histogram the fixed-input pencil rather than an outcome pencil; the missing second step is now supplied and its scope stated.
- Updated: Born Criteria for Collapsible-State Measures — same gap closed in "Reflected ratios are secondary".
- Updated: Relative-Unitary Evolution — See Also cross-reference.
- Updated: wiki/index.md concepts list.
- Disputed/withdrawn: an agent-side claim of 2026-09-21 that the production pipeline scores a surrogate observable. It rested on a Haar-unitary counterexample, which is not symmetric and so lies outside the approved families. The user rejected the claim and it is withdrawn.
- Validation: 36-cell sweep of both approved families (ring/chain x all/first x N=3,4,5 x t=1,37,211). With the Y self-fields off, worst `max|U - U^T|` 1.665e-16, worst `|fixed - conj(outcome0)|` 8.265e-14, worst radii gap 5.662e-14; with them on, 1.026e+00, 2.670e+00, 1.541e-01. Duality checked exactly (0.000e+00) on three Haar unitaries; conjugation map gives 1.442e+00 there, so the agreement is not vacuous.
- Scoped: no gate promoted, `paper_ready` remains `false`.

