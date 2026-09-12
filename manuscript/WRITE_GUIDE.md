# Paper-Writing Operating Manual

This manual provides the concrete, operational workflow for drafting and refining manuscripts in the `unitary-collapse` research program (targeting *Physical Review Letters* and *Nature Physics*). It bridges the overarching doctrine of the **Scientific Writing Skill** with the specific technical evidence, matrix-pencil formulations, and numerical datasets of this repository.

---

## 1. Source of Truth Hierarchy & Integrity Boundary

To ensure absolute scientific integrity, every factual assertion, parameter value, and data point in the manuscript must be strictly traceable down to raw verified code outputs:

$$\text{\bf Manuscript Claim} \longrightarrow \text{\bf EVIDENCE\_REGISTRY.md} \longrightarrow \text{\bf NUMERICAL\_PROVENANCE.md} \longrightarrow \text{\bf Raw Data / Source Run}$$

### The Seven Evidence States
Every statement must be internally designated by its exact evidential state:
$$\text{measured} \mid \text{simulated} \mid \text{analytically derived} \mid \text{literature-established} \mid \text{inferred} \mid \text{hypothesized} \mid \text{projected}$$

- **Strict Wording Ceilings**: Never draft above the evidentiary floor:
  $$\text{is consistent with} < \text{suggests} < \text{supports} < \text{demonstrates/shows} < \text{establishes}$$
- **Zero Fabrication**: Never invent parameters, seeds, error bars, or priority claims.
- **Unverified Claims**: Any claim not grounded in `EVIDENCE_REGISTRY.md` with verified provenance in `NUMERICAL_PROVENANCE.md` is classified as `hypothesized` or `inferred` and cannot be stated as established fact in the main text.

---

## 2. The Scientific Story Model

A successful high-impact paper addresses six linked questions in a coherent chain:
1. **Territory**: What fundamental problem in quantum dynamics is at stake? (The persistent non-unitary treatment of measurement vs. unitary accounts of thermalization and spontaneous emission).
2. **Tension**: What precise assumption or limitation blocks progress? (Linearity: an unrestricted superposition principle maps superpositions of inputs to superpositions of macroscopic detector states).
3. **Advance**: What do we show, derive, or observe? (We formulate a restricted-state framework where definite-outcome inputs are projective pencil roots, and demonstrate Born-like dipolar geometries in structured spin rings).
4. **Mechanism**: Which physical degree of freedom enables the advance? (Relative-propagator spectral structure, Jacobi complementary-minor duality, and reciprocal branch balance).
5. **Proof**: What decisive evidence distinguishes the claim from plausible alternatives? (Exact antipodal duality; an exact isotropic null for Haar scramblers; monotonic rise of polar score from $0.192$ to $0.807$ with unit coverage in $N=11\text{--}16$ rings).
6. **Horizon**: What broader physics or capability becomes accessible? (A rigorous structural classification of "measurement-capable" unitary Hamiltonians).

---

## 3. The Four-Phase Drafting Pipeline

Do not draft linearly from start to finish. Follow this four-phase sequence:

### Phase I: Architecture (The Logical Blueprint)
1. **The Pitch** (`manuscript/drafts/architecture/pitch.md`): Formulate a single-sentence internal pitch following the template:
   > *Because [context], [gap] matters. Here we [advance], enabled by [mechanism], established by [decisive evidence], which makes possible [broader consequence].*
2. **The Claim Ladder** (`manuscript/drafts/architecture/claim_ladder.md`): Construct an ordered sequence of 3–7 claims:
   $$\text{phenomenon/platform} \longrightarrow \text{decisive observation} \longrightarrow \text{mechanism} \longrightarrow \text{robustness} \longrightarrow \text{significance}$$
   Record for every claim: `evidence | comparator | caveat | figure/equation | confidence | wording ceiling`.

### Phase II: Figure-First Design (The Visual Proof)
1. **Four-Figure Narrative**: Organize figures according to the four pillars:
   - **Fig. 1 Concept**: System schematic, block partitioning $U(t)$, pencil roots on the Bloch sphere, and antipodal partner pairs.
   - **Fig. 2 Proof**: Decisive numerical observation of the Born profile $\cos^2(\theta/2)$ in $N=16$ spin rings contrasted with the flat Haar-random null.
   - **Fig. 3 Robustness & Scaling**: Monotonic polar score convergence ($N=11\to16$), unit full-sphere coverage, and suppression of azimuthal harmonics.
   - **Fig. 4 Boundaries & Certification**: Analytic constructive family ($C_B$ gate) juxtaposed against rigorous no-gos (detuning intervals and non-normal limits).
2. **Figure Cards** (`manuscript/drafts/figures/figX_*.md`): Complete all 9 items for each main figure before drafting prose.
3. **The "Champ" Vector Pipeline**:
   - Render headless raw curves/scatter points to vector PDF/SVG from Python (no titles, no legends, outside ticks).
   - Compose final typography, panel labels, and layout in a vector editor (PowerPoint or Illustrator).
4. **Self-Contained Captions**: Follow the caption recipe: `title → system/condition → panel sequence → encoding/normalization → key comparison`.

### Phase III: Section-by-Section Prose Construction
1. **Results First** (`manuscript/drafts/sections/results.md`): Write in figure-driven modular units:
   $$\text{scientific question} \longrightarrow \text{minimum required theory} \longrightarrow \text{result} \longrightarrow \text{quantitative evidence} \longrightarrow \text{interpretation} \longrightarrow \text{transition}$$
2. **Introduction** (`manuscript/drafts/sections/introduction.md`): Follow the Swales-like sequence:
   $$\text{territory} \longrightarrow \text{tension/gap} \longrightarrow \text{why gap matters} \longrightarrow \text{announce present work} \longrightarrow \text{reveal intuition} \longrightarrow \text{announce principal findings}$$
3. **Discussion** (`manuscript/drafts/sections/discussion.md`): Widen outward in 5 controlled rings:
   1. Result established in the matched spin ring.
   2. Principle of pencil root geometry and antipodality.
   3. Essential caveats: root counts are not a physical preparation measure; record stability is unproven.
   4. Compelling next steps: experimental realization in Rydberg/superconducting architectures.
   5. Broader perspective: Hamiltonian classification of unitary measurement.
4. **Abstract** (`manuscript/drafts/sections/abstract.md`): Draft long for completeness, then cut down to the 600-character / 150-word journal limit using the move sequence:
   $$\text{context} \longrightarrow \text{gap} \longrightarrow \text{early here-we} \longrightarrow \text{strongest results} \longrightarrow \text{mechanism} \longrightarrow \text{implication}$$

### Phase IV: Multi-Perspective Completion Audits
Before final package assembly, evaluate the manuscript against five critical personas:
- **Editor**: Is the breakthrough obvious within the first page? Is Figure 1 accessible to a general physicist?
- **Skeptical Expert**: Is the Haar null respected? Are finite-size limitations clearly marked? Is the distinction between algebraic multiplicity and physical probability maintained?
- **Adjacent-Field Scientist**: Can a quantum optics or condensed matter researcher follow the notation without reading specialized literature?
- **Figure-First Reader**: Can the complete argument be extracted from the figures and captions alone?
- **Integrity Auditor**: Does every sentence stay below its wording ceiling? Are null results and open problems explicitly stated?

---

## 4. Reference Strategy

Organize citations into four functional sets (see `wiki/concepts/literature-map.md`):
- **Foundations**: Field-defining benchmarks (Born 1926, Zurek 2003, Deutsch 1991, Srednicki 1994, Gleason 1957).
- **Nearest Prior Art**: Close precedents (Schulman 1997/2012/2017, Brandão et al. 2015, Qi & Ranard 2021, Hamid 2025, Guttel 2026).
- **Contrast / Limitations**: Conventional barriers and alternative paradigms (GRW 1986, Bassi et al. 2013, Diósi-Penrose, Hossenfelder & Palmer 2020).
- **Implications / Generalization**: Broader connections (Palmer 2026, Doucet & Deffner 2024, Popescu-Short-Winter 2006, Atas et al. 2013, Many-Body Scars).

---

## 5. Reviewer-Response Protocol

When responding to peer review:
- Complete the 5-step loop for every comment: `acknowledge → answer scientifically → make/justify change → identify modified text/figure → cite evidence`.
- When handling disagreements: `appreciation → shared ground → evidence/reasoning → narrow disagreement → manuscript clarification`.
- Use consistent terminology (`Referee` or `Reviewer`), hyperlink cited papers via DOI, and quote revised passages in full.

---

## 6. Project-Specific Notation & Conventions

- **Relative Propagator**: $W = A^{-1}C$, where $U = \begin{pmatrix} A & B \\ C & D \end{pmatrix}$.
- **Projective Pencil**: $(C, A)$ or $C + z D$.
- **Bloch Coordinates**: Polar angle $\theta = 2 \arctan |\lambda|$, azimuthal phase $\phi = \arg \lambda$, with $\mu = \cos \theta$.
- **Target Distribution**: The qubit Born profile $P(\theta) \propto \cos^2(\theta/2)$.
- **Polar Symmetry / Asymmetry**: $a(\Omega) = \frac{\rho_0(\Omega) - \rho_0(-\Omega)}{\rho_0(\Omega) + \rho_0(-\Omega)}$ with antipodal relation $\rho_1(\Omega) = \rho_0(-\Omega)$.
- **Diagnostics**: Polar score $S_{\mathrm{B}}$, count-weighted residual, coverage gate ($\ge 0.5$ or $1.0$), azimuthal second-harmonic $|c_2| \le 0.25$.
