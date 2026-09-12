# Paper-Writing Operating Manual

This document provides the concrete, operational workflow for drafting the manuscript. It bridges the general principles of high-impact scientific writing with the specific technical evidence of the `unitary-collapse` research program.

## 1. The Source of Truth Hierarchy
To ensure absolute scientific integrity, every sentence in the manuscript must be traceable through this hierarchy. **Never write a claim that cannot be traced to the bottom.**

**Manuscript Claim** $\longrightarrow$ **`manuscript/EVIDENCE_REGISTRY.md`** $\longrightarrow$ **`manuscript/NUMERICAL_PROVENANCE.md`** $\longrightarrow$ **Raw Data / Code Output**

- If a claim is not in the `EVIDENCE_REGISTRY.md`, it is a **CONJECTURE** and must be labeled as such.
- If a registry entry lacks provenance, it is **UNVERIFIED** and cannot be used in the main text.

---

## 2. The Drafting Pipeline (Step-by-Step)

Do not write linearly. Follow this sequence to ensure the argument is logically sound before investing time in prose.

### Phase I: Architecture (The Blueprint)
1. **The Pitch**: Write a one-sentence internal pitch in `manuscript/drafts/architecture/pitch.md`.
2. **The Claim Ladder**: Break the pitch into 3–7 sequential claims in `claim_ladder.md`.
3. **Wording Ceilings**: For each claim, assign the strongest verb justified by the evidence (e.g., `suggests` vs `establishes`).

## 2. The Drafting Pipeline (Step-by-Step)

Do not write linearly. Follow this sequence to ensure the argument is logically sound before investing time in prose.

### Phase I: Architecture (The Blueprint)
1. **The Pitch**: Write a one-sentence internal pitch in `manuscript/drafts/architecture/pitch.md`.
2. **The Claim Ladder**: Break the pitch into 3–7 sequential claims in `claim_ladder.md`.
3. **Wording Ceilings**: For each claim, assign the strongest verb justified by the evidence (e.g., `suggests` vs `establishes`).

### Phase II: Figure-First Design (The Visual Proof)
1. **Figure Cards**: Create a `.md` file for each figure in `manuscript/drafts/figures/`.
2. **Define the Takeaway**: Every figure must answer one specific scientific question.
3. **Panel Flow**: Design the panels to guide the reader from "Observation" $\to$ "Mechanism" $\to$ "Robustness."
4. **Quantitative Anchors**: Identify the exact number (e.g., RMSE $\le 0.05$) that makes the figure a "proof."
5. **The "Champ" Workflow**: 
    - Render graphs in the source tool (NumPy/Matplotlib) as **vector graphics** (.svg, .pdf, .emf).
    - Do **not** include labels, legends, or ticks in the source tool.
    - Compose the final figure layout (axes, text, annotations) in a vector editor (e.g., PowerPoint, Illustrator).
    - This ensures that font sizes and line weights remain consistent across the entire paper.

### Phase III: Iterative Drafting (The Prose)
1. **Results First**: Draft the `results.md` by describing the figures. The figures are the primary argument; the text provides the context and interpretation.
2. **Introduction**: Move from "Broad Territory" $\to$ "Specific Tension" $\to$ "Our Advance" $\to$ "Principal Findings."
3. **Discussion**: Move from "Local Result" $\to$ "General Principle" $\to$ "Boundaries/Limits" $\to$ "Future Horizon."

### Phase III: Iterative Drafting (The Prose)
1. **Results First**: Draft the `results.md` by describing the figures. The figures are the primary argument; the text provides the context and interpretation.
2. **Introduction**: Move from "Broad Territory" $\to$ "Specific Tension" $\to$ "Our Advance" $\to$ "Principal Findings."
3. **Discussion**: Move from "Local Result" $\to$ "General Principle" $\to$ "Boundaries/Limits" $\to$ "Future Horizon."

---

## 3. Operational Integrity Checks

Before finalizing any section, perform the following audits:

### The "Skeptical Expert" Audit
- For every headline claim, ask: *"What is the strongest plausible alternative explanation for this result?"*
- Ensure the manuscript explicitly addresses this alternative using a control (e.g., comparing interacting rings to Haar-random unitaries).

### The "Integrity Auditor" Audit
- Check that no "numerical trend" is described as a "theorem."
- Verify that "Born-like" is not used as a synonym for "exact Born rule" without explicitly stating the finite-resolution gate used.
- Ensure all $\cos^2(\theta/2)$ and $W = A^{-1}C$ notation is consistent throughout.

### The "Figure-First" Audit
- Read only the figures and their captions. Can you reconstruct the core claim? If not, the figures are failing to carry the argument.

---

## 4. Project-Specific Notation & Conventions
To maintain a professional, publication-ready style, use these defaults:
- **Relative Propagator**: Always refer to $W = A^{-1}C$.
- **Born Profile**: Use $\cos^2(\theta/2)$ as the target distribution.
- **Root Angles**: $\theta = 2 \arctan |\lambda|$.
- **Symmetry**: Refer to "symmetry-resolved sectors" when discussing level statistics.
- **Pencils**: Use "projective pencil $(C, A)$" when discussing the generalized eigenvalue problem.
