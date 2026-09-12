# Figure Design Doctrine

Figures in a high-impact paper are not just illustrations of the text; they are the primary vehicle of the scientific argument. A "figure-first" reader should be able to reconstruct the core claim just by inspecting the visuals.

## Core Principles
- **Self-Sufficiency**: Figures must be readable *before* the caption. Labels, units, and conditions must be explicit.
- **Dominant Takeaway**: Each figure should have one dominant scientific idea.
- **Panel Flow**: Panels should tell a story (e.g., Concept $\to$ Proof $\to$ Robustness $\to$ Horizon).
- **Visual Hierarchy**: Use consistent sans-serif typefaces, perceptually sensible colormaps, and clear annotations.

## The Figure Card Process
Before creating a visual, a "Figure Card" is used to define the logic:
- **One-sentence takeaway**: What is the point of this figure?
- **Question answered**: What specific doubt or gap does this address?
- **Panel flow**: The logical sequence of panels.
- **Quantitative anchor**: The specific value or scaling relation that proves the claim.
- **Alternative explanation**: Which competing interpretation does this figure rule out?

## Technical Standards
- **Vector Pipeline**: Data rendering and figure composition must remain separable and editable. 
    - **Step 1**: Export raw graphs from the source tool as vector files (SVG, PDF, EMF) **without** labels, ticks, or legends.
    - **Step 2**: Import these primitives into a vector editor (e.g., PowerPoint).
    - **Step 3**: Add all text, axes, and layout in the vector editor to ensure absolute consistency in font and size.
- **Consistent Semantics**: Use the same colors and markers for the same conditions across all figures.
- **Axis & Ticks**: Ticks should be outside axes; use human-readable labels with symbols and units.

See also: [[scientific-writing]].
