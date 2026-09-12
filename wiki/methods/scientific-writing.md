# Scientific Writing & Communication

This hub defines the operational standards for translating research results into high-impact scientific publications (e.g., *Physical Review Letters*, *Nature Physics*). It operationalizes the core principles of high-impact scientific storytelling, evidence synthesis, figure-first design, and multi-perspective completion auditing.

---

## 1. Outcome Contract & Scientific Integrity

The objective of scientific writing is to produce the **strongest scientifically defensible paper story supported by the available evidence**. 

### The Evidence Boundary
Never invent or "complete" missing science. Statements must be strictly categorized into one of seven distinct evidence states:
$$\text{measured} \mid \text{simulated} \mid \text{analytically derived} \mid \text{literature-established} \mid \text{inferred} \mid \text{hypothesized} \mid \text{projected}$$

Never silently advance a statement to a stronger state. In particular:
- **No fabricated data, uncertainties, parameters, equations, methods, or citations.**
- **No priority inflation**: Words like "first," "unprecedented," or "universal" require an exhaustive literature basis.
- **No causal leaps**: Correlation or numerical coincidence never establishes causation without an explicit physical mechanism.
- **No disguised caveats**: Do not omit boundary conditions, model assumptions, or finite-size limitations to strengthen the pitch.
- **Wording Ceilings**: Calibrate verbs strictly to the evidence level:
  $$\text{is consistent with} < \text{suggests} < \text{supports} < \text{demonstrates/shows} < \text{establishes}$$

---

## 2. The Scientific Story Model

A high-impact manuscript answers six linked questions:
1. **Territory**: What fundamental scientific problem, capability, or mystery is at stake?
2. **Tension**: What standard assumption, limitation, inaccessible regime, or missing observation blocks progress?
3. **Advance**: What do we show, demonstrate, derive, or observe?
4. **Mechanism**: Which physical degree of freedom or principle makes the advance possible?
5. **Proof**: What decisive evidence distinguishes the claim from plausible alternatives and controls?
6. **Horizon**: What broader physics or capability becomes accessible because the mechanism now exists?

Use this chain as a live model of the manuscript. Every paragraph and figure must serve one of these functions.

---

## 3. Corpus-Derived High-Impact Motifs

These transferable structural motifs are distilled from top-tier publications in quantum physics, photonics, and many-body dynamics:

1. **Mature Field, Missing Regime**: Start from an established paradigm (e.g., ETH, spontaneous emission, decoherence), then expose a precise missing regime (e.g., global unitary account of definite outcome records) rather than a vague "lack of understanding."
2. **"Here We" as a Claim Boundary**: State the new contribution immediately after the gap using active present-tense verbs. Place physical intuition *after* the contribution to preserve perceived novelty.
3. **Unlocking Degree of Freedom**: Identify the specific physical or mathematical handle that resolves the tension (e.g., projective pencil roots, relative propagator eigenphases, symmetry-resolved sector decomposition).
4. **Counterintuitive but Diagnostic Result**: Elevate results that violate default expectations (e.g., antipodal minor duality, structured rings producing Born dipoles while Haar scrambling yields flat isotropy) to decisively discriminate between mechanisms.
5. **Cross-Field Analogy with Added Capability**: Map concepts across disciplines (e.g., mapping pencil roots in matrix analysis to quantum state selection; connecting measurement-capable states to many-body quantum scars).
6. **Theory and Experiment Form One Proof**: Interleave theory to predict scaling and distinctive signatures with numerics/experiment to test them and identify boundaries.
7. **Fundamental Physics Plus Capability**: Pair the conceptual advance with a concrete diagnostic, classification, or protocol.
8. **Generalize Only After the Decisive Result**: Prove the core effect rigorously in a concrete model before widening the scope to broader Hamiltonian classes or thermodynamic limits.

---

## 4. Section-by-Section Drafting Architecture

### Step 1: The Pitch
Draft and stress-test a single-sentence internal pitch:
> *Because [important context], [gap] matters. Here we [advance], enabled by [mechanism], established by [decisive evidence], which makes possible [broader consequence].*

### Step 2: The Claim Ladder
Build an ordered ladder of 3–7 sequential claims:
$$\text{phenomenon/platform} \longrightarrow \text{decisive observation} \longrightarrow \text{mechanism} \longrightarrow \text{robustness/generality} \longrightarrow \text{significance}$$
For each claim, record: `evidence | comparator | caveat | figure/equation | confidence | wording ceiling`.

### Step 3: Figure-First Design
Design figures before drafting prose. Each figure represents a decisive pillar of the proof. See [[figure-design]].

### Step 4: Abstract Drafting (Long $\to$ Cut)
Follow the move sequence:
$$\text{broad context} \longrightarrow \text{sharply motivated gap} \longrightarrow \text{early here-we} \longrightarrow \text{strongest result(s)} \longrightarrow \text{mechanism} \longrightarrow \text{final implication}$$
Draft for completeness and force first, then edit ruthlessly for length.

### Step 5: Introduction (Motivate, Then Occupy)
Follow a Swales-like sequence:
$$\text{establish territory} \longrightarrow \text{identify tension/gap} \longrightarrow \text{explain why gap matters} \longrightarrow \text{announce present work} \longrightarrow \text{reveal intuition} \longrightarrow \text{announce principal findings}$$
Avoid sterile roadmaps ("In Section II we..."). Announce discoveries rather than document layout.

### Step 6: Results (Figure-Driven Units)
Structure results into self-contained figure units:
$$\text{scientific question} \longrightarrow \text{minimum required theory} \longrightarrow \text{result} \longrightarrow \text{quantitative evidence} \longrightarrow \text{interpretation} \longrightarrow \text{transition}$$
Interleave theory directly before the numerical evidence it explains.

### Step 7: Discussion (Widening in Controlled Rings)
Move outward in 5 deliberate concentric rings:
1. What is decisively established in the immediate model/system.
2. What underlying physical principle generalizes.
3. What boundary conditions, obstructions, or limitations apply.
4. What new numerical or experimental test becomes compelling.
5. What broader capability or conceptual perspective emerges.

---

## 5. Scientific Prose Rules

- **Tense**: Present tense default for established facts, displayed figures, and active claims ("Figure 2 reveals...", "Equation (3) implies..."). Past tense only for chronological procedures.
- **Voice**: Prefer direct, active constructions over passive nominalizations.
- **Clarity**: One to three connected ideas per sentence; one main topic per paragraph with explicit transitions.
- **Typography & Units**: Upright units with proper spacing ($10\,\text{nm}$, $10^4\,\hbar/J$); italic variables, upright descriptive subscripts ($S_{\mathrm{B}}$, $H_{\mathrm{D}}$); no backslashes in prose.
- **Equations**: Equations are grammatical components of sentences; punctuate them with commas or periods.

---

## 6. Reference Strategy

Citations are integral components of the scientific argument. Categorize all references into four functional sets:
1. **Foundations**: Field-defining papers and authoritative reviews establishing accepted context.
2. **Nearest Prior Art**: Closest physical effects, methods, models, or competitive claims.
3. **Contrast / Limitations**: Works defining the standard limitation, no-go theorem, or alternative non-unitary paradigm that the paper addresses.
4. **Implications / Generalization**: Works establishing why the demonstrated mechanism or capability matters to broader physics.

See [[literature-map]] for the project's strategic citation graph.

---

## 7. Multi-Perspective Completion Audit

Before finalizing any manuscript draft or major research deliverable, stress-test the work through five independent personas:
- **The Editor**: Is the central advance obvious within the first two paragraphs? Does Figure 1 make the conceptual breakthrough immediately accessible? Why is this urgent for the venue?
- **The Skeptical Expert**: What is the nearest competing interpretation or null hypothesis? Which control rules it out? Does every claim stay below its wording ceiling?
- **The Adjacent-Field Scientist**: Is the narrative clear without specialized jargon? Are axes, units, and symbols immediately interpretable?
- **The Figure-First Reader**: Can the complete scientific story be reconstructed from the figures and captions alone?
- **The Integrity Auditor**: Are all evidence states accurately designated? Are null results, finite-size limits, and open questions surfaced transparently?

---

## Cross-References
- [[figure-design]] — Standards for figures, Figure Cards, and vector pipelines.
- [[reviewer-responses]] — Protocol for handling referee comments and revisions.
- [[scientific-contract]] — Rigor standards, exact limits, and invariants.
- [[literature-map]] — Four-quadrant citation architecture.
