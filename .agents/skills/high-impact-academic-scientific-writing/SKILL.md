---
name: high-impact-scientific-papers-astra
description: Use with GPT-6 Astra when autonomously planning, researching, drafting, revising, or auditing a high-impact scientific paper, abstract, figure narrative, Supplementary Information, or reviewer response; especially for complex physics, photonics, quantum science, and engineering projects that benefit from long-horizon evidence synthesis, parallel literature/critique work, figure-first storytelling, and end-to-end scientific document completion.
---

# High-Impact Scientific Papers — GPT-6 Astra

## Outcome contract

Produce the **strongest scientifically defensible paper story supported by the available evidence**. Carry authorized work through to a reviewable result rather than stopping at planning.

Success means:

- the paper's central novelty is explicit and fairly positioned against prior art;
- every headline claim is traceable to evidence;
- the figures form a coherent scientific argument that works for a figure-first reader;
- mechanism, evidence, caveats, and significance are correctly separated;
- the abstract and introduction make the gap and contribution clear early;
- results interleave theory and evidence where that improves comprehension;
- the discussion generalizes only after the core effect is established;
- visual and textual conventions are consistent and publication-ready;
- unsupported claims, ambiguous terminology, weak controls, and citation gaps are surfaced rather than hidden.

The user's explicit instructions take precedence over this skill except where scientific integrity or platform policy requires otherwise.

Use transferable structural motifs from the Kaminer/Segev corpus, but **do not imitate distinctive wording or copy signature phrases from living authors**. Reproduce the argument architecture, not a personal prose style.

---

## Scientific integrity boundary

Never invent or “complete” missing science.

Treat these as distinct evidence states:

`measured | simulated | analytically derived | literature-established | inferred | hypothesized | projected`

Do not silently move a statement to a stronger state.

In particular:

- no fabricated data, uncertainties, parameter values, equations, methods, citations, or priority claims;
- no “first/unprecedented/universal” without a literature basis adequate to the requested venue;
- no causal language from correlation alone;
- no loaded quantum/topological/entanglement/strong-coupling terminology without the operational criterion used in the field or manuscript;
- no removal of limitations that change interpretation;
- no application claim that lacks a mechanistic bridge from the demonstrated result.

When evidence is missing, either retrieve it from authorized sources/tools or mark the gap explicitly. If the requested claim remains unsupported, rewrite it to the strongest defensible form.

---

## Scientific story model

A high-impact paper usually answers six linked questions:

1. **Territory:** What important scientific problem or capability is at stake?
2. **Tension:** What standard assumption, limitation, inaccessible regime, or missing observation blocks progress?
3. **Advance:** What do we show, demonstrate, derive, or observe?
4. **Mechanism:** Which physical degree of freedom or principle makes the advance possible?
5. **Proof:** What decisive evidence distinguishes the claim from plausible alternatives?
6. **Horizon:** What broader physics or capability becomes accessible because the mechanism now exists?

Use this chain as a live model of the manuscript. If a paragraph or figure does not serve one of these functions, challenge its inclusion.

---

## Autonomous workflow

Astra should infer routine details and proceed. Ask the user only when an unknown could materially alter scientific meaning, attribution, confidentiality, or an irreversible external action. Before asking, complete all useful analysis that does not depend on the missing answer.

For substantial tasks, maintain three internal artifacts (they may remain implicit unless useful to show):

### A. Evidence graph

Nodes:

`claims, datasets, figures, equations, controls, literature, assumptions, caveats, applications`

Edges:

`supports, contradicts, explains, bounds, compares-to, generalizes-to, depends-on`

A headline claim is ready only when its support path is clear and its nearest contradiction/alternative explanation has been considered.

### B. Story graph

Represent the reader's logical journey:

`importance → gap → here-we → mechanism → evidence → robustness → consequence`

Find and repair jumps where the manuscript asks the reader to accept an unstated inference.

### C. Figure graph

For each figure:

`single takeaway → panels → visual comparison → quantitative anchor → transition to next figure`

The figure graph and story graph should be isomorphic enough that a figure-first reader recovers the same core argument as a full-text reader.

---

## Parallelization policy

If the harness supports subagents or parallel tool calls and the task is large enough to benefit, delegate independent tracks while preserving one final scientific voice.

Useful tracks include:

- **Novelty scout:** nearest prior art, competing claims, priority language, field-level gap.
- **Evidence skeptic:** claim-evidence consistency, alternative explanations, controls, statistical/model assumptions.
- **Figure editor:** panel logic, visual hierarchy, caption independence, notation/color consistency.
- **Outsider reader:** jargon, missing motivation, conceptual leaps, figure readability.
- **Venue editor:** word limits, article type, figure count, style and reference constraints when a target journal is known.

Do not delegate merely to create activity. Synthesize all tracks and resolve contradictions before drafting final prose.

---

## Research and stopping rule

When literature positioning is requested or necessary for a novelty claim, search enough to identify:

- foundational concept;
- nearest methodological or physical precedent;
- strongest competing interpretation;
- recent work that could weaken or qualify novelty;
- reviews/perspectives that establish accepted context.

Prefer primary papers for specific priority or result claims and authoritative reviews for field context.

**Stop researching when additional sources are unlikely to change the claim boundary, novelty comparator, or citation set.** Do not expand a bibliography merely because more papers exist.

Maintain a provenance distinction between user-supplied material, retrieved literature, and model inference.

---

## Paper architecture

### Step 1 — Define the pitch

Generate and test a one-sentence internal pitch:

`Because [important context], [gap] matters. Here we [advance], enabled by [mechanism], established by [decisive evidence], which makes possible [broader consequence].`

Stress-test each slot:

- Is the context broad enough for the venue but specific enough to be meaningful?
- Is the gap factual rather than rhetorical?
- Does the advance use the strongest accurate verb?
- Is the mechanism causal or merely correlated?
- Is the evidence decisive?
- Is the consequence enabled by the mechanism rather than aspirational?

### Step 2 — Build the claim ladder

Prefer 3–7 major claims. Order them so each earns the next:

`phenomenon/platform → decisive observation → mechanism → robustness/generality → scientific capability/significance`

For each claim record internally:

`evidence | comparator | caveat | figure/equation | confidence | wording ceiling`

The **wording ceiling** is the strongest verb/adjective justified by the evidence. Never draft above it.

### Step 3 — Design figures before section prose

Each main figure should express one dominant scientific idea.

Default narrative, when the science fits it:

- **Fig. 1 Concept:** intuitive schematic, system, geometry, mechanism, predicted contrast.
- **Fig. 2 Proof:** most decisive observation/calculation and quantitative signature.
- **Fig. 3 Why / robustness:** mechanism, scaling, control, competing explanation, theory-experiment comparison.
- **Fig. 4 Horizon:** tunability, generality, new capability, application-relevant consequence.

Do not force this template. Reorder to match the actual logic.

Create a Figure Card for every main figure:

`Claim-like title`  
`One-sentence takeaway`  
`Question answered`  
`Panel flow`  
`Dominant panel`  
`Instant comparison the reader must notice`  
`Quantitative anchor`  
`What alternative explanation this figure addresses`  
`Why this belongs in main text rather than SI`

### Step 4 — Write the abstract long, then cut

First draft for completeness and force; second draft for length.

Preferred move sequence:

`broad context → sharply motivated gap → early here-we → strongest result(s) → mechanism → final implication`

When two results are independently strong, give them separate sentences rather than compressing them into one overloaded clause.

The final sentence may widen the horizon, but must remain plausible from the demonstrated direction.

### Step 5 — Introduction: motivate, then occupy the niche

Use a flexible Swales-like sequence:

`establish territory → identify tension/gap → explain why gap matters → announce present work → reveal intuition → announce principal findings`

A long introduction is acceptable only if every paragraph is easy to follow, has an obvious reason for being there, and increases motivation or understanding.

Avoid a sterile section-by-section roadmap. If orientation is needed, announce findings rather than document structure.

### Step 6 — Results: argument, not lab notebook

Use figure-driven units:

`scientific question → minimum required setup/theory → result → quantitative evidence → interpretation → consequence/transition`

Interleave theory and results rather than separating them when local explanation makes the mechanism clearer.

Each paragraph should have one main topic. Use direct verbs and simpler sentence structure in dense sections.

### Step 7 — Discussion: widen in controlled rings

Move outward:

1. what is established in this system;
2. what principle generalizes;
3. what boundary conditions or limitations matter;
4. what new experiment or regime becomes scientifically compelling;
5. what plausible technology/capability could emerge.

The farther the claim is from direct evidence, the more carefully calibrate modality (`could`, `may`, `suggests`, `provides a route to`).

---

## Corpus-derived high-impact motifs

These are structural motifs repeatedly visible in representative Kaminer/Segev-group work.

### 1. Mature field, missing regime

Start from something the reader already accepts, then expose a precise missing regime: a classical description where quantum statistics have not been observed; a topological concept not yet realized in a synthetic photonic dimension; a wave phenomenon predicted across systems but not observed optically; a core interaction limited by dimensionality or resolution.

This produces a clean novelty sentence because the gap is an actual boundary, not generic “limited understanding.”

### 2. “Here we” as a claim boundary

State the new contribution immediately after the gap. Use present-tense active verbs. Do not bury the advance in methodological detail.

Put the new intuition after the contribution when presenting it earlier could make the novelty sound like prior knowledge.

### 3. Unlocking degree of freedom

Identify the controllable physical handle that changes the old limitation:

`wavefunction shaping | synthetic dimension | gauge field | band engineering | disorder correlation | nonlinearity | ultrafast field | geometry | velocity/trajectory | collective interaction`

Explain the paper through that handle, not through a list of apparatus components.

### 4. Counterintuitive but diagnostic result

When genuinely present, elevate one result that violates the reader's default model: a backward cone, unexpected cutoff, disorder-induced yet collimated flow, protection against imperfections, a quantum-to-classical transition, or a “lossless” functionality with a clear operational definition.

The counterintuitive result should also discriminate between explanations; surprise alone is not enough.

### 5. Cross-field analogy with added capability

Translate a powerful concept from one domain into another, then show what the new platform adds. Examples of the underlying move include condensed-matter/topological ideas mapped into photonics, Schrödinger-like wave behavior accessed optically, or free electrons recast as quantum-optical probes.

Always state the physical mapping, not merely the vocabulary.

### 6. Theory and experiment form one proof

Use theory to predict the distinctive signature or scaling and experiment to test it. Use experiment to reveal where idealized theory needs refinement. The reader should see one argument rather than two parallel sections.

### 7. Fundamental physics plus capability

Pair the conceptual advance with a concrete new operation: sensing, tomography, control, protected transport, compact radiation, acceleration, imaging, or state preparation. The capability is most persuasive when it emerges naturally from the same mechanism that produced the fundamental result.

### 8. Generalize only after the decisive result

After proving the effect in one platform, connect it to other wave systems, materials, dimensions, energy scales, or quantum technologies. This is the correct place for ambition.

---

## Scientific prose rules

Default to present tense for claims and displayed results. Use past tense where chronology or completed procedures genuinely matter.

Prefer active constructions:

- `Figure 2 reveals a shift…`
- `The interaction suppresses…`
- `The measured scaling agrees with…`
- `The calculation predicts…`

Avoid “In Figure 2, a shift is shown…” unless there is a reason to foreground the location rather than the finding.

Use direct, assertive language when certainty is established. Do not use `will be` when `is` is both shorter and scientifically accurate.

Prefer:

- short familiar words over inflated synonyms;
- verbs over nominalizations;
- content verbs over empty `be/have/do/make` constructions;
- one to three connected ideas per sentence;
- paragraphs with one main topic and an explicit logical link to neighboring paragraphs.

Formatting/notation defaults:

- no backslashes in prose; avoid slashes where ordinary wording is clearer;
- spell out `Figure`/`Equation` when beginning a sentence;
- use one consistent convention for figure and equation references;
- equations are grammatical parts of sentences and need punctuation;
- descriptive subscripts upright/roman, variable subscripts italic;
- number–unit spacing (`300 nm`) and upright units;
- avoid large blocks of italic text;
- avoid casual claims that a structure or experiment is “easy” to fabricate/produce.

---

## Figure doctrine

### Make the figure readable before the caption

Assume the reader may inspect the figure without reading the surrounding paragraph or even the caption. Put enough information in the figure to understand:

- what variables are shown;
- which curve/panel corresponds to which condition;
- what comparison matters;
- where the predicted or observed feature is;
- what the units are;
- which visual encoding is meaningful.

Do not solve poor figure design by writing a longer caption.

### First figure sells the idea

Figure 1 should usually clarify the idea/phenomenon/mechanism, not begin with a dense parameter sweep. Use a schematic, conceptual contrast, geometry, expected signature, or intuitive model if appropriate.

### Panel flow

Panel order should tell a story. Make the most important graph dominant. If two graphs must be compared, make differences visible immediately through aligned axes, annotations, consistent scales, direct labels, or other scientifically honest cues.

### Visual style

- consistent sans-serif typeface and font sizes;
- largest legible text that fits the final figure size;
- small but visible annotations;
- consistent color semantics across figures;
- avoid harsh pure RGB colors;
- use perceptually sensible colormaps for 2D data;
- support color distinctions with markers/line styles/annotations when possible;
- direct-label lines when this reduces legend lookup;
- place ticks outside axes;
- avoid gridlines and decorative table rules unless they encode useful structure;
- use human-readable axis labels plus symbols and units;
- do not italicize ordinary text;
- leave breathing room between subpanels;
- preserve vector graphics and editable source layers.

### Editable vector pipeline

The source group workflow exports graph primitives from MATLAB as vector files and performs text/layout/annotation work in PowerPoint before vector export to the manuscript. Preserve that logic even if using another modern vector editor: **data rendering and figure composition should remain separable and editable**.

For expensive computations, save processed data and build figures from the saved output so aesthetic revisions do not require rerunning the science.

### Caption recipe

Begin with an informative caption title. Then explain:

`system/condition → panel sequence → encoding/normalization/error representation → key comparison`

Keep the caption self-contained enough to decode the figure, but do not duplicate the entire Results discussion.

---

## Evidence-aware editing

When revising an existing manuscript, do not optimize sentences independently. First determine what each sentence is trying to do:

`motivate | position | claim | describe method | report result | interpret | qualify | generalize`

Then edit it to serve that function.

### Claim-strength ladder

Use the strongest justified verb:

`is consistent with < suggests < supports < demonstrates/shows < establishes`

This is not a universal ordering; field conventions matter. Calibrate to evidence, controls, uncertainty, and venue.

For quantitative claims, prefer a number or scaling relation when it carries the significance better than an adjective.

---

## Reference strategy

Treat citations as part of the argument.

Build four sets:

- **foundations:** reviews and/or original field-defining papers;
- **nearest prior art:** closest physical effect, method, platform, or claim;
- **contrast:** literature representing the limitation or conventional expectation the paper overcomes;
- **implications:** work showing why the new capability matters.

For basic topics, a strong review and the original landmark paper are often complementary.

Do not use citations merely to associate the paper with famous names or journals. Relevance, priority fairness, and scientific accuracy dominate.

Before submission, check that literature discussed in a cover letter or reviewer exchange is represented in the manuscript when scientifically appropriate.

---

## Supplementary Information

Treat SI as independently readable technical support:

- redefine acronyms and symbols;
- state assumptions and conventions;
- include derivations, calibration, controls, sensitivity analysis, algorithm details, reproducibility information, and extended data that would interrupt the main narrative;
- keep central evidence in the main paper when the headline claim depends on it;
- use consistent tense and notation with the manuscript.

---

## Reviewer-response mode

For every reviewer comment, complete the loop:

`acknowledge → answer scientifically → make/justify change → identify modified text/figure → cite evidence`

Be generous in tone and exact in substance. If the reviewer identifies a misunderstanding, treat the manuscript's clarity as part of the problem even when the science is correct.

When disagreeing:

`appreciation → shared ground → evidence/reasoning → narrow disagreement → manuscript clarification`

Use one consistent term (`reviewer` or `referee`) within a response document.

When practical, hyperlink cited papers by DOI in the response document so the reviewer can inspect them quickly.

Do not describe a tiny change in a way that minimizes a substantial reviewer concern; show the revised paragraph or the full relevant change when that communicates responsiveness better.

---

## Multi-perspective completion audit

Before finalizing a substantial deliverable, simulate these perspectives and revise where they identify real problems.

### Editor

- Is the central claim obvious early?
- Why now, and why this venue?
- Is the advance broader than one device/sample without overstating universality?
- Does Figure 1 make the paper legible to a non-specialist editor?

### Skeptical expert

- What is the strongest competing explanation?
- Which result actually rules it out?
- Which term or novelty claim is vulnerable?
- Are model assumptions and experimental uncertainties visible enough?

### Adjacent-field scientist

- Can the motivation be understood without specialist shorthand?
- Does the analogy to another field explain physics rather than import jargon?
- Which axes, symbols, or acronyms block understanding?

### Figure-first reader

- Can the abstract + figures reconstruct the main argument?
- Is each figure's one-sentence takeaway obvious?
- Does any panel require body-text archaeology to interpret?

### Integrity auditor

- Does every headline sentence stay within its wording ceiling?
- Are measurement, calculation, inference, and outlook distinguishable?
- Are negative/null results represented fairly?
- Is any caveat hidden because it weakens the pitch?

Stop revising when these audits no longer reveal changes likely to alter comprehension, scientific correctness, or editorial impact. Do not polish indefinitely.

---

## Deliverable behavior

Infer what the user wants and return the finished artifact, not an essay about how to write it.

Common modes:

- full paper architecture;
- abstract or title options;
- introduction/results/discussion draft;
- figure plan or figure audit;
- caption rewrite;
- literature-positioning map;
- reviewer response;
- end-to-end manuscript revision.

For an end-to-end task, Astra should autonomously move from evidence graph → story/figure graph → draft → critique → revision → final audit, using tools and parallel research where helpful.

When new user instructions arrive mid-task, incorporate them without losing the original scientific objective or already-established constraints. Recompute only the parts of the evidence/story/figure graph affected by the change.

Default to concise, cohesive scientific prose. Avoid excessive headings, repeated summaries, generic “key takeaways,” and ornamental formatting in manuscript text.

---

## Provenance and reference corpus

This skill synthesizes two internal research-group guides supplied by the user:

- *Writing rules – Written via e-mails by Ido and Thomas, Edited by Yaniv* (“writing articles like a champ”).
- Saar Nehemia, *How to make figures like a champ* (last updated 14 Dec 2022).

Transferable corpus motifs were triangulated from representative publications and publication lists associated with Ido Kaminer, Mordechai (Moti) Segev, and their collaborators/groups, including work on quantum Čerenkov radiation, accelerating wave packets, free-electron quantum optics, quantum state tomography and sensing, photon-statistics/free-electron interactions, photonic flatbands, topological photonics in synthetic dimensions, topological lasers, Anderson localization, and branched flow of light.

The corpus is used for **argument structure, novelty framing, mechanism/evidence coupling, figure narrative, and controlled generalization**. It is not a license to imitate phrase-level style.
