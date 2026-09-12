# Manuscript Drafting Workspace

This directory is dedicated to the iterative construction of the final scientific paper. It follows the `high-impact-scientific-papers-astra` workflow, which prioritizes evidence-based storytelling and figure-first architecture over linear drafting.

## Structure

- `/architecture`: The "blueprint" of the paper.
    - `pitch.md`: The one-sentence core narrative.
    - `claim_ladder.md`: The sequence of 3–7 major claims and their evidence support.
    - `figure_plan.md`: The Figure Graph—takeaways, panel flows, and quantitative anchors.
- `/sections`: Iterative drafts of the prose.
    - `abstract.md`
    - `introduction.md`
    - `results.md`
    - `discussion.md`
- `/figures`: Figure Cards and visual specifications.
    - Individual files for each figure (e.g., `fig1_concept.md`) containing the takeaway and layout.
- `/si`: Supplementary Information.
    - Technical derivations, extended data, and robustness checks.
- `/reviews`: Audit logs and reviewer response drafts.
    - `evidence_graph.md`: Mapping claims to datasets and figures.
    - `reviewer_responses/`: Threaded responses to specific referee comments.

## Workflow
1. **Pitch & Ladder**: Define the core advance and the evidence chain in `/architecture`.
2. **Figure Design**: Design the figures in `/figures` before writing a single word of prose.
3. **Drafting**: Build the `results.md` and `introduction.md` around the figures.
4. **Refining**: Audit against the "Skeptical Expert" and "Integrity Auditor" perspectives.
5. **SI**: Move supporting technical detail to `/si` to maintain the main narrative's flow.

## Integrity Boundary
All claims in `/sections` must be traceable to a "Wording Ceiling" defined in `claim_ladder.md`, which in turn must be anchored to an entry in `manuscript/EVIDENCE_REGISTRY.md`.
