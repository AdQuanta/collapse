---
name: high-impact-academic-scientific-writing
description: Plan, draft, revise, and audit high-impact scientific manuscripts, including abstracts, introductions, results, discussions, captions, supplementary information, and reviewer responses. Use when writing or restructuring physics and other quantitative research papers; sharpening the pitch and novelty; building a figure-first narrative; improving scientific clarity, active voice, equations, references, and visual consistency; or preparing a manuscript for submission to selective journals.
metadata:
  author: research-group-derived
  version: "1.0.0"
  source-basis: "Research-group guides: Writing rules and How to make figures like a champ"
---

# High-impact academic scientific writing

## Purpose

Turn technically correct research into a manuscript that is easy to understand, hard to misread, and compelling to expert editors, referees, and readers outside the immediate subfield.

Optimize for four things simultaneously:

1. **Scientific correctness** — never strengthen a claim beyond the evidence.
2. **Narrative force** — every paragraph and figure advances one central scientific story.
3. **Reader efficiency** — the main point should be visible quickly from the abstract, figures, and topic sentences.
4. **Professional consistency** — notation, figures, captions, references, tense, and terminology must be coherent throughout.

Treat the manuscript as an argument, not a chronological lab notebook.

## Activation behavior

When this skill is active:

- Preserve the user's scientific content and terminology unless asked to change them.
- Distinguish clearly between **demonstrated result**, **interpretation**, **speculation**, and **outlook**.
- Do not invent data, mechanisms, citations, derivations, or significance.
- Prefer direct, active, present-tense scientific prose unless chronology or journal convention requires otherwise.
- Prefer concrete claims over vague prestige language.
- If the user provides a target journal, adapt structure and emphasis to that journal while keeping the rules below.
- If the user provides group conventions that conflict with generic advice, follow the explicit group conventions.

## Core workflow

### 1. Extract the paper's pitch before drafting prose

Write a private or explicit one-paragraph **paper pitch** containing:

- **Territory:** What broad problem or phenomenon matters?
- **Gap:** What is unknown, unresolved, inaccessible, or insufficient in the literature?
- **Here we:** What does this work do that closes or reframes the gap?
- **Principal findings:** What are the 1–3 strongest results?
- **Why it matters:** What changes conceptually, experimentally, technologically, or methodologically because of the result?

If these cannot be stated cleanly, do not optimize sentences yet. Fix the scientific story first.

### 2. Build a figure-first manuscript skeleton

Before full drafting, create a skeleton whose headings are **claims**, not generic topics.

Then create a figure plan. For each main figure, specify:

- one-sentence **figure claim**;
- what the reader must notice immediately;
- panels needed to establish that claim;
- the key comparison or contrast;
- how this figure advances the paper beyond the previous figure.

The first figure should usually explain the idea, system, mechanism, or phenomenon at a glance. Later figures should establish the specific evidence and strongest results.

Prefer one major idea per figure. If panels contain a comparison, make the difference visually obvious rather than forcing the reader to search for it.

See [references/figure-design-rules.md](references/figure-design-rules.md) and [assets/figure-plan-template.md](assets/figure-plan-template.md).

### 3. Draft the abstract long, then compress

Do not optimize the first abstract draft for the word limit. First write the strongest complete version, then compress without losing logic.

Use this sequence unless the target journal requires another structure:

1. **Broad context** — why the area matters.
2. **Gap** — the missing knowledge, capability, or unresolved question.
3. **Here we** — direct statement of what this work does.
4. **Main results** — separate distinct strengths into separate sentences when that improves clarity.
5. **Interpretation/significance** — what the result teaches or enables.
6. **Outlook** — one forward-looking sentence with justified ambition.

The gap must be strongly motivated before the paper claims to solve it.

Do not use citations in the abstract unless the journal explicitly permits them.

### 4. Write the introduction as a motivated narrowing funnel

Use the scientific-rhetorical sequence:

1. **Establish the territory.** Explain the important field/problem.
2. **Establish the niche.** Identify a specific gap, limitation, tension, or question.
3. **Occupy the niche.** State what this work does and announce its principal findings.

Put the novelty early. Prefer a direct **“Here we…” / “In this work…”** paragraph before long intuition or technical explanation when this prevents readers from confusing the new contribution with prior knowledge.

At each introduction paragraph, ask:

- Is the logic simple to follow?
- Is it clear why the reader is being told this now?
- Does the paragraph strengthen motivation or importance?

Avoid a dry roadmap paragraph such as “Section II does X, Section III does Y” unless the journal strongly benefits from it. If a roadmap is useful, turn it into a selling paragraph that states findings rather than merely listing sections.

### 5. Interleave essential theory/method with results

When possible, avoid placing all theory before all results. Introduce the minimum theory or method needed to understand a result, show the result, then introduce the next conceptual layer.

For each result block:

1. State the question or expectation.
2. Give only the setup/theory needed to interpret the evidence.
3. State the observation/result directly.
4. Explain the mechanism or interpretation.
5. Say why the result matters for the paper's central claim.

Each paragraph should have one main topic. Use a strong topic sentence and simpler supporting sentences.

### 6. Write results as actions and findings

Prefer active constructions:

- “Figure 2 reveals …”
- “The spectrum shifts …”
- “The model predicts …”
- “We observe …”
- “This suppression indicates …”

Avoid passive and descriptive scaffolding such as “In Fig. 2, a shift is shown.”

Prefer **X does Y** over **in X we show Y** when the scientific object can naturally be the subject.

Use present tense for scientific reports by default, especially for what figures, equations, and results show. Use past tense for specific completed procedures when needed.

### 7. Separate evidence, inference, and claim strength

Use calibrated language:

- **Direct evidence:** shows, demonstrates, reveals, establishes — only when genuinely supported.
- **Model-supported inference:** indicates, is consistent with, supports, suggests.
- **Speculation/outlook:** may, could, potentially, motivates future work.

Do not convert correlation into causation or a model-consistent mechanism into a demonstrated mechanism.

Avoid weak future constructions when a direct present statement is correct. Prefer “absorption is forbidden” over “there will be no possible absorption.”

### 8. Write the discussion as scientific expansion, not repetition

A strong discussion should typically:

- generalize the finding beyond the exact system studied;
- explain the most important conceptual implication;
- connect to neighboring systems or applications;
- state limitations honestly without burying the contribution;
- end with the strongest justified forward-looking implication.

Do not merely restate the results section.

### 9. Design figures to be readable before the caption

Assume many readers will first scan only the abstract and figures.

Therefore:

- Make figures as self-explanatory as possible without clutter.
- Make the most important graph or visual element dominant.
- Arrange multi-panel figures with an obvious narrative flow.
- Leave visible spacing between subfigures.
- Use meaningful axis labels containing both quantity/name and units.
- Keep tick marks outside axes.
- Avoid gridlines unless quantitative reading genuinely requires them.
- Prefer direct labels to legends when practical.
- Use consistent, readable sans-serif typography.
- Use the largest reasonable font and keep font sizes consistent across all figures.
- Do not italicize figure text except mathematical variables.
- Use a consistent color scheme across the manuscript.
- Use distinctive, non-pure/flat colors; ensure comparisons remain legible.
- Prefer perceptually sensible colormaps for 2D data.
- Prefer vector graphics for graphs, line art, and schematics.

Separate **data generation** from **figure styling** where practical: generate clean plots from saved data, then assemble labels, annotations, and layout in an editable graphics environment.

The figure caption should begin with a short informative title, then explain what is shown and what the reader should learn from it.

### 10. Treat equations as grammatical parts of sentences

- Punctuate displayed equations as part of the prose.
- Define every symbol that a target reader may not know.
- Use roman font for descriptive subscripts and italic font for variable subscripts.
- Put a space between numerical values and units: `300 nm`, not `300nm`.
- Keep units upright, not italic.
- Do not put ordinary prose inside math mode when it can be written as prose.
- Keep equation-reference style consistent throughout.
- At the beginning of a sentence, spell out abbreviations such as “Equation” and “Figure”.

### 11. Maintain notation and terminology consistency

Create or infer a consistency ledger for:

- symbols and subscripts;
- acronyms;
- hyphenation;
- capitalization;
- singular/plural technical terms;
- figure and equation reference format;
- units;
- names of methods, devices, and physical regimes.

Use one term for one concept unless a distinction is intentional.

Avoid risky or overloaded terminology when a more precise term is available.

### 12. Manage references strategically

For background claims, prefer authoritative sources such as foundational papers, leading reviews, and strong primary literature.

During drafting, use stable citation keys rather than manually renumbering references. Before submission:

- verify every factual literature claim has an appropriate citation;
- check that important prior work discussed by the team has not been omitted;
- check that works highlighted in the cover letter are cited in the manuscript;
- verify bibliographic details and journal formatting;
- never invent or guess references.

### 13. Make the supplementary information stand alone

Unless the journal dictates otherwise:

- redefine acronyms and essential notation;
- state methods and derivations sufficiently for independent reading;
- use present tense by default;
- do not make the main paper appear dependent on supplementary figures for its central claim;
- move supporting depth to the supplement, not essential proof of the headline result.

### 14. Revise in passes, not all at once

Use this order:

**Pass A — science and claims**
- Are all claims supported?
- Is the main result actually the strongest result?
- Are alternative interpretations addressed where necessary?

**Pass B — story**
- Does every paragraph have a reason to exist?
- Does the sequence create motivation → result → implication?
- Is novelty stated early enough?

**Pass C — paragraph structure**
- One main topic per paragraph.
- Strong topic sentence.
- Logical sentence-to-sentence flow.

**Pass D — sentence quality**
- Prefer active voice.
- Replace nominalizations with verbs.
- Remove redundant “which/that/who” constructions and unnecessary prepositional phrases.
- Prefer short direct words to inflated alternatives.
- Replace weak generic verbs with specific scientific verbs.
- Split sentences longer than about 40 words unless complexity genuinely requires the length.

**Pass E — consistency and typography**
- notation, units, tense, references, equations, captions, figure labels.

**Pass F — outsider test**
Ask a scientifically literate reader who did not do the work to explain:
- the main question;
- the novelty;
- what each figure proves;
- the strongest result;
- why it matters.

If they cannot, revise the manuscript rather than explaining it verbally.

## High-impact quality gates

Before calling a draft “submission-ready,” verify all of the following.

### Scientific claim gate

- The headline claim is explicit and evidence-matched.
- Necessary controls, convergence checks, uncertainty, or alternative explanations are addressed.
- No unsupported superlatives such as “first,” “unprecedented,” “universal,” or “direct proof.”
- Speculation is labeled as speculation.

### Pitch gate

- A reader can identify the gap and contribution from the first part of the abstract.
- The introduction explains why the gap matters before technical detail overwhelms it.
- The “here we” statement is specific, not generic.
- The conclusion identifies a real implication rather than vague future potential.

### Figure gate

- The figure sequence alone approximately reconstructs the scientific story.
- Each main figure has one dominant message.
- Critical comparisons are visually immediate.
- Labels, units, fonts, colors, panel letters, and line styles are consistent.
- Figures remain legible at final publication size.
- Vector output is used when appropriate.

### Prose gate

- Paragraphs have one main topic.
- Most sentences have a clear actor and action.
- Active voice dominates where natural.
- Present tense is used consistently for scientific claims and displayed results.
- Long or nested sentences have been simplified.
- No vague filler such as “it is interesting to note that,” “it can clearly be seen,” or “as is well known” unless genuinely needed.

### Technical-style gate

- Figures/equations are referenced consistently.
- Descriptive subscripts are upright/roman.
- Units are spaced and upright.
- Equations are punctuated as prose.
- Acronyms are defined at first use in each stand-alone document.
- No prose backslashes; forward slashes are minimized.

### Reference gate

- No invented references.
- Foundational and directly relevant recent work are both represented where appropriate.
- All cited claims match the cited source.
- Citation style is consistent and journal-compatible.

## Response-to-reviewers workflow

When drafting a rebuttal or revision response:

1. Open with appreciation for the reviewers' careful reading.
2. Quote or clearly delimit each comment.
3. Respond directly and scientifically; do not sound defensive or condescending.
4. If the reviewer is correct, acknowledge it and state the change.
5. If disagreeing, first acknowledge the concern, then explain the evidence-based reason.
6. Make a concrete manuscript change for every substantive comment whenever possible.
7. End each response with **what changed**, preferably giving the revised text or a precise location.
8. Use one consistent term — “reviewer” or “referee” — throughout.
9. Check whether literature raised by the reviewer should be cited in the revised manuscript.
10. Make it obvious which changes are new responses to the review.

See [assets/reviewer-response-template.md](assets/reviewer-response-template.md).

## Output modes

Choose the smallest output that satisfies the request.

### Manuscript blueprint

Return:
- one-sentence pitch;
- gap / here-we / main-claim formulation;
- figure sequence;
- paragraph-level main-text skeleton;
- missing evidence or logic risks.

### Drafting mode

Draft polished prose while preserving scientific meaning. If evidence is incomplete, use explicit placeholders such as `[quantify]`, `[citation]`, `[control needed]`, or `[mechanism not yet established]` rather than inventing content.

### Editing mode

For each substantive edit, optimize in this order:
1. scientific accuracy;
2. logical clarity;
3. force of the claim;
4. concision;
5. elegance.

Do not shorten a sentence if doing so weakens precision.

### Audit mode

Return a prioritized list of:
- **hard scientific problems**;
- **story/pitch problems**;
- **figure problems**;
- **clarity/style problems**;
- **consistency/reference problems**.

Separate changes that are essential for correctness from changes that merely improve presentation.

## Collaboration and tracked-revision behavior

When working iteratively with coauthors:

- Do not silently delete unresolved comments.
- Preserve unresolved scientific questions until explicitly closed.
- When performing a complete rewrite, make it easy to verify that no technical content was accidentally lost.
- Keep a clear distinction between proposed addition, proposed deletion, and author response when the working format supports it.
- Resolve comments only after the underlying question has been answered or intentionally rejected.

## Default manuscript philosophy

A high-impact paper should make the reader feel that the result is important because the **scientific logic forces that conclusion**, not because the prose repeatedly says it is important.

The strongest manuscript usually has:

- a sharply motivated gap;
- a direct statement of novelty;
- a figure sequence that tells the story independently;
- alternating explanation and evidence;
- disciplined claim strength;
- a final implication that is ambitious but earned.
