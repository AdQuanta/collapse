# Figure Design Doctrine

Figures in a high-impact paper are not decorative summaries of the text—they are the primary vehicle of the scientific argument. A figure-first reader should be able to reconstruct the complete logical progression and core conclusions from the figures and captions alone.

---

## 1. Core Principles

- **Readable Before the Caption**: A reader inspecting the visual panels must immediately understand what variables are plotted, which curve represents which condition, where the diagnostic signature lies, and what the quantitative comparison demonstrates. Never use a long caption to compensate for an ambiguous figure.
- **Single Dominant Takeaway**: Each main-text figure must embody exactly one dominant scientific advance.
- **Narrative Panel Flow**: Panels must be arranged so that visual attention follows a logical story (e.g., system/concept $\to$ primary observation $\to$ mechanism/control).
- **Dominant Panel**: Give visual prominence (size, contrast, central placement) to the decisive data panel that establishes the figure's claim.
- **Instant Comparison**: Make key physical distinctions immediately visible through aligned axes, matching scales, direct labels, and consistent encoding.

---

## 2. The Four-Figure Architecture

For high-impact letters (e.g., *PRL*, *Nature Physics*), align the visual story to a four-pillar sequence:

1. **Figure 1 — Concept**: Intuitive physical schematic, Hamiltonian/system architecture, mathematical engine, and predicted contrast. Must be immediately comprehensible to a non-specialist editor.
2. **Figure 2 — Proof**: Decisive empirical or numerical observation. Features the primary quantitative signature contrasted directly against natural null models (e.g., Haar-random isotropic baseline).
3. **Figure 3 — Mechanism & Robustness**: Physical degree of freedom driving the effect, finite-size scaling, coverage gates, and suppression of competing artifacts.
4. **Figure 4 — Horizon & Theoretical Boundaries**: Analytic certification of constructive families, rigorous no-go boundaries, and broader generalization across parameter space.

---

## 3. The Figure Card Specification

Before creating or revising any figure, formalize its logic in a dedicated Figure Card (`manuscript/drafts/figures/figX_*.md`) containing nine explicit items:

1. **Claim-like Title**: A declarative sentence stating the exact finding demonstrated by the figure.
2. **One-Sentence Takeaway**: The core scientific message delivered to a skimming reader.
3. **Question Answered**: The precise physical doubt, gap, or theoretical question addressed.
4. **Panel Flow**: The logical sequence from panel (a) through the final panel.
5. **Dominant Panel**: The single panel that carries the heaviest evidential weight.
6. **Instant Comparison**: The visual juxtaposition the reader must notice without reading the caption.
7. **Quantitative Anchor**: The exact metric, scaling exponent, residual, or error bound that substantiates the claim.
8. **Alternative Explanation Addressed**: The competing hypothesis or artifact ruled out by the controls.
9. **Why Main Text vs. SI**: The justification for keeping this figure in the main letter rather than the Supplemental Material.

---

## 4. The Vector Graphics Pipeline ("Champ" Workflow)

To achieve publication-quality typography and visual coherence across all figures, decouple raw data rendering from layout composition:

### Step 1: Headless Data Rendering (Python / Matplotlib)
- Export graph primitives as vector assets (`.svg`, `.pdf`, or `.emf`) directly from Python.
- Strip all software-generated titles, legends, axis titles, and redundant tick labels.
- Preserve only raw curve data, scatter points, heatmaps, error bands, and essential axis lines with outside ticks.
- Save intermediate processed data so visual adjustments never require rerunning expensive simulation pipelines.

### Step 2: Vector Layout & Composition (Illustrator / PowerPoint)
- Import vector primitives into a dedicated vector editor.
- Add all panel labels (`(a)`, `(b)`, `(c)`), axis titles, units, callout arrows, schematics, and text annotations.
- Enforce strict typeface and size consistency across all figures in the manuscript.

### Step 3: High-Resolution Publication Export
- Export composite plates as vector PDFs (or $600+\,\text{dpi}$ TIFF/PNG if required by the publisher).

---

## 5. Visual Standards & Aesthetics

- **Typography**: Single sans-serif family (e.g., Helvetica, Arial, or TeX Gyre Heros) across all figures.
  - Panel labels: Bold uppercase or bold lowercase `(a)`, $10\text{--}12\,\text{pt}$.
  - Axis titles & dominant annotations: $8\text{--}9\,\text{pt}$.
  - Tick labels & secondary notes: $7\text{--}8\,\text{pt}$ (minimum legible size at printed column width).
- **Direct Labeling**: Direct-label curves and regimes whenever possible to eliminate tedious legend lookup.
- **Axes & Ticks**: Place ticks outside axes. Never use default interior ticks that collide with data. Omit background gridlines unless evaluating fine numerical coordinates.
- **Color Palettes**:
  - Never use raw RGB primaries (harsh red `#FF0000`, harsh blue `#0000FF`).
  - Use perceptually uniform colormaps (`viridis`, `inferno`, `cividis`) for 2D density or potential data.
  - Maintain color semantics throughout the paper (e.g., if blue represents the matched ring in Fig. 2, use the same blue for the matched ring in Figs. 3 and 4).
  - Support color distinctions with line styles (solid, dashed) and marker shapes for colorblind accessibility.
- **Breathing Room**: Maintain generous whitespace between subpanels to prevent visual crowding.

---

## 6. The Caption Recipe

A self-contained figure caption follows a four-part sequence:
1. **Informative Title**: Bold declarative title stating the primary takeaway.
2. **System & Conditions**: Physical Hamiltonian, parameter values, system sizes ($N$, $d$), and time ($t$).
3. **Panel-by-Panel Walkthrough**: Explicit description of each panel `(a)`, `(b)`, `(c)`, defining all axes, encodings, and normalization.
4. **Key Comparison & Quantitative Anchor**: Highlight the decisive contrast and report exact quantitative residuals or scores.

---

## Cross-References
- [[scientific-writing]] — Overall manuscript architecture and prose standards.
- [[numerical-provenance]] — Linking figure panels to underlying data runs and Git commits.
- [[coverage-gates]] — Mathematical definitions of coverage and diagnostic gates.
