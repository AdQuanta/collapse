# Materials and narrative audit

Audit date: 2026-08-14 (Asia/Jerusalem)

Scope: independent inventory of the attached `C:\Users\matan\Downloads\main.pdf` and the repository's report, figure, notebook, and bibliography materials. This is a diagnostic pass only; it does not draft or edit the manuscript.

## Executive finding

The repository supports a strong but narrower Letter than the title of the attached research map suggests. The most defensible result chain is:

1. an exact projective generalized-eigenvalue construction for separable qubit outputs from a fixed pole input (and, by inverse evolution, pole-boundary preimages);
2. an exact Haar/Stiefel reduction to the complex spherical ensemble for that production pencil, giving an isotropic one-point null law; and
3. post-cutoff finite-size evidence that one clean matched-field spin ring develops a Born-like **polar root-count statistic** with broad full-sphere support.

The repository does **not** yet establish operational Born probabilities, a physical measure selecting roots, a common apparatus-ready detector state, stable macroscopic records, or a direct same-time forward-pencil validation at the highlighted many-body points. Exact complementary-minor duality makes the second forward outcome root multiset the antipode of the first, so two independent coordinate calculations are neither expected nor required. These are not rhetorical caveats: they determine which narratives are publishable.

## 1. Attached `main.pdf`

- File: `C:\Users\matan\Downloads\main.pdf`
- PDF metadata: 36 pages; created 2026-08-12 02:39 UTC; pdfTeX/LaTeX.
- Character: a long research map/review-style draft, not a PRL Letter. It contains 15 main sections, seven appendices, 65 references, four conceptual/schematic figures, evidence labels, proposed tests, and numerous author-input placeholders.
- Strong content: the two forward pole conditions `(C+zD)|eta>=0` and `(A+zB)|eta>=0`; projective/homogeneous-coordinate cautions; regular-versus-singular pencils; the SU(2)/Möbius Haar-isotropy argument; explicit separation of existence, statistics, and ontology/preparation.
- Unsupported content for a final Letter: broad statements that structured Ising/XY/tube/pixel families approach Born statistics; a transverse-field Born-to-uniform crossover; spectral-statistics explanations; density/covering claims; experimental and quantum-computing predictions. The PDF itself calls many of these preliminary or proposed.
- Figure status in the PDF:
  - Fig. 1 is a conceptual arrow-of-time schematic, not data.
  - Fig. 2 is a block-pencil schematic, not data.
  - Fig. 3 is an architecture cartoon, not data.
  - Fig. 4 is explicitly a schematic proposed correlation and must never be presented as measured data.
- Critical mismatch with production code: the PDF's numerical story is written around the same-propagator forward pencils. The production campaigns instead solve `U10 v = lambda U00 v`, then construct the exact companion antipodal branch. Complementary-minor duality also makes the two genuine forward outcome root multisets exact antipodes. The remaining mismatch is time direction: the production object has an exact separable-output interpretation for `U(t)` and a forward-preimage interpretation for `U(-t)`, but it is not generically the forward pencil of the same `U(t)`.

## 2. Repository inventory and source reliability

The `reports/` tree is very large (roughly 15,000 files because it includes per-case metadata and rendered atlases). The scientifically useful material falls into the following tiers.

### Tier 1: strongest analytical sources

| Source | What is reliable | Important limitation |
|---|---|---|
| `reports/four_model_finite_time_eigenvalue_derivation_2026-07-10.md` | Most complete code-aligned analytical note. Defines the production pencil, regularity/infinite roots, atomic empirical measures, exact Cayley relation for zero central field, exact noninteracting spectrum, ZZ wrapped-Gaussian limit under stated hypotheses, and careful resonant caveats. | It studies `U10 v=lambda U00 v`, not the full two-forward-pencil measurement construction. Several large-`N`/long-time steps retain explicit remainder hypotheses. |
| `reports/perturbative_wrapped_gaussian_heavy_tail_proof_2026-07-05.md` | Precise Cayley/tangent heavy-tail conditions and the reciprocal-density condition needed for a Born-like polar ratio. | The microscopic finite-range tracial CLT and resonant spectral-convergence inputs are not fully mechanized. |
| `proofs/BornHeavyTailCore.lean`, `proofs/README.md`, `proofs/completion_audit.md`, `proofs/verification_summary.json` | Machine-checked deterministic Cayley/tangent and inverse-square-tail core; numerical comparators record 15 passing checks. | This is a theorem about the production relative-evolution/Cayley object, not a derivation of Born probabilities. The completion audit explicitly marks microscopic inputs as external/unformalized. |
| `collapse/analysis.py` and `collapse/relative_evolution_pencil.py` | Canonical production definitions and stable homogeneous generalized eigensolver. Code explicitly documents `U10 v=lambda U00 v`, `theta=2 atan|lambda|`, and the antipodal second branch. | Older paths in `analysis.py` still expose direct solves/pseudoinverse fallbacks; publication claims should use the homogeneous solver and residual diagnostics. |
| `tests/test_relative_evolution_pencil.py` and adjacent analysis tests | Regression coverage for projective roots, infinite/indeterminate cases, angle matching, and diagnostics. | Tests validate the numerical object, not the physical selection hypothesis. |

Older analytical working notes such as `reports/diagonalizing_M_working_note_2026-06-19.md`, `reports/analytical_wrapped_gaussian_xx_ising_plusminus_2026-06-27.md`, and `reports/ising_J0_wrapped_gaussian_derivation_2026-06-30.md` are useful history but are superseded where the July 5/10 notes disagree or add caveats.

### Tier 2: strongest post-cutoff numerical/report sources

| Source | Evidence | Suitability |
|---|---|---|
| `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/DONE.json` and `raw/N16/hz0_+0.1000/` | Zeus run started 2026-07-14 and finished 2026-07-15; Python 3.11.5; dependency versions recorded; deterministic matched case `hz0=hz=0.1`, `J=1`, `Jpm=0`, collective `Jx=0.01`; four times; each N=16 raw file contains 65,536 complex roots and polar angles. | **POST-CUTOFF VERIFIED.** Strongest single full-sphere dataset. No seed is needed, but no git commit is recorded. |
| `reports/zeus_single_pixel_analysis_2026-07-16/manifest.json`, `conclusions.md`, `jointly_gated_born_candidates.csv`, `spectrum_metrics.csv` | Created 2026-07-17 from 1,208 complete spectra only. Exactly 24 rows pass the coverage/azimuth gates; all are matched-field rows for N=11--16 and four times. Median `S_born` rises 0.192 to 0.807. | **POST-CUTOFF VERIFIED derived analysis.** Best main-text numerical source if called a polar root-count statistic, with no thermodynamic extrapolation. |
| `reports/anisotropic_parameter_study_2026-07-21/analysis_manifest.json` and report/data/figures | 3,722 spectra analyzed; N=11--14 complete (880 cases each), larger sizes incomplete. Supplies high-scoring controls and full Bloch plots showing that good polar ratios can remain meridional (`phi_harmonic_2` near one). | Strong control/supplement source. Do not turn incomplete N=15--18 into scaling evidence. |
| `reports/born_similarity_relation_2026-07-31/analysis_summary.json` and `coverage_rmse_map.*` | 1,425 rows show the repository `S_born` score is largely a combination of angular coverage and occupied-bin ratio error (grouped-CV R2 about 0.91). | Essential interpretive caution. This score is not an independent probability metric or mechanism. |
| `reports/three_sobol_born_relations_final_v2_2026-08-09/` | 1,072 N=14 dynamics configurations joined to N_D=10 spectral features; within-campaign correlations, bootstrap intervals, deterministic nested CV, explicit provenance. | Good supplement/mechanism exploration. Observational only; original N=14 dynamics were not rerun in August, and no causal or universality claim follows. |
| `reports/detector_gap_matrix_study_2026-07-21/`, `reports/detector_degeneracy_group_atlas_2026-07-28/`, `reports/vab_coupling_group_atlas_2026-07-28/` | Post-cutoff targeted controls show raw degeneracy is neither necessary nor sufficient; finite-time resonant weight broadens support but is nearly independent of Born similarity within broad cases. | Valuable negative/control results, primarily Supplement or a separate paper. |

### Tier 3: untrusted or unsuitable materials

- All nine notebooks are pre-cutoff (2025 through February 2026): `disentanglement_notebook.ipynb`, `disentanglement_demo.ipynb`, `disorder_demo.ipynb`, `disorder_ratio_demo.ipynb`, and five notebooks under `archive/`. They contain executed outputs but are **PRE-CUTOFF / UNTRUSTED** for paper numerics and import active ideas from an older workflow.
- `figures/haar_random_unitary/haar_N13_seed44.png` was generated 2026-03-12 and is **PRE-CUTOFF / UNTRUSTED**. It cannot appear as empirical evidence without a post-cutoff rerun. The exact Haar theorem makes a data panel unnecessary.
- Root-level `tp_size_scan_ring.png`, `tp_size_scan_chain.png`, and `tp_size_scan_all_to_all.png` are dated 2026-03-01 and are **PRE-CUTOFF / UNTRUSTED**.
- Most historical `figures/` campaign folders copied into the workspace on July 11 retain pre-cutoff generation dates. A July copy time is not a valid post-cutoff generation date.
- `archive/` is useful only for historical context and must not be cited as the source of an active numerical claim.

## 3. Existing figures and provenance assessment

| Figure asset | Assessment | Recommended use |
|---|---|---|
| `work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/figures/N16_hz0_diagnostic_atlas_t1e3.png` | Directly tied to post-cutoff raw roots and `DONE.json`. The matched `hz0=0.1` column shows broad two-dimensional Bloch coverage, `S_born=0.840`, and RMSE 0.031. The other columns are useful detuning controls. Current seven-column layout is too dense for PRL. | Regenerate a cropped/vector-quality matched-versus-detuned panel from the raw NPZ/metrics. Label it explicitly as one root cloud plus antipodes, not two independently solved outcomes. |
| `reports/zeus_single_pixel_analysis_2026-07-16/finite_size_diagnostics.png` | Post-cutoff and traceable, but mixes four studies and its family medians hide the exceptional matched subfamily. | Supplement/control. For main text regenerate a matched-only scaling panel from `jointly_gated_born_candidates.csv`. |
| `reports/zeus_single_pixel_analysis_2026-07-16/regime_tradeoffs.png` | Post-cutoff, traceable, and scientifically useful: heavy tails and polar Born score are distinct; coverage can make a high score misleading. | Supplement or one small control inset. |
| `reports/anisotropic_parameter_study_2026-07-21/figures/representative_diagnostics.png` | Post-cutoff. Visually demonstrates the central full-sphere risk: several apparently Born-like polar profiles live on nearly one meridian. | Strong Supplement figure or a compact main-text negative control after relabeling. |
| `reports/born_similarity_relation_2026-07-31/coverage_rmse_map.pdf` | Reproducible post-cutoff derived summary over 1,425 cases. | Supplement. It audits the score rather than advancing the central PRL story. |
| `reports/prl_unitary_collapse_2026-08-14/figures/matched_field_scaling.pdf` | Regenerated 2026-08-14 from the post-cutoff 24-row CSV by a local script. Scientifically traceable, though it belongs to an earlier draft directory rather than the canonical analysis tree. | May be reused or regenerated in `prl_draft/figures`; verify every plotted definition and retain source comments. |
| `reports/prl_unitary_collapse_2026-08-14/figures/haar_N13_seed44.png` | A copied March 2026 figure. The copy does not cure its pre-cutoff provenance. | Reject from main and Supplement unless reproduced post-cutoff. |

No existing empirical figure directly validates the same-time forward pencil at the highlighted `U(t)`; once one forward root multiset is known, the other follows exactly by antipodes. No existing figure demonstrates the associated companion detector vectors, a physical sampling measure, a fixed detector-ready state, or macroscopic record stability.

## 4. Bibliography quality and citation issues

### Inventory

- The attached PDF contains a manually typeset 65-item reference list with generally useful DOI metadata, but no corresponding source `.bib` was found in the historical repository materials.
- The only located standalone bibliography is `reports/prl_unitary_collapse_2026-08-14/references.bib`, containing nine entries. It is a minimal draft bibliography, not a publication-ready project bibliography.
- One concrete metadata error is already present there: DOI `10.3390/e19070343` is Schulman's **“Program for the Special State Theory of Quantum Measurement,”** not “Special States Demand a Force for the Observer.”

### Claims that require primary-source verification before submission

1. **Schulman special states.** Verify exactly what future boundary condition is imposed, what Cauchy/Lorentzian assumption produces the Stern--Gerlach probabilities in the 2012 paper, and what the 2017 program claims about state abundance and the arrow of time. Do not claim Schulman's admissible set is or is not a vector space without a direct passage.
2. **Linearity/macro-objectification.** Bassi--Ghirardi can support a no-go statement only with its actual assumptions. The Letter should give the elementary measurement-map argument directly and use the citation for the broader theorem.
3. **Haar-to-spherical-ensemble identity.** Krishnapur and Alishahi--Zamani support the independent-Ginibre spherical ensemble and uniform one-point density. The stronger claim that the production Haar block column has exactly the same generalized roots needs the repository's Stiefel/Gaussian-factor proof and a citation for Gaussian QR/Haar-Stiefel representation. Do not cite the spherical-ensemble papers as if they already prove the Haar-block identity.
4. **Haar label fraction.** Equal ensemble one-point intensities support an isotropic/equal-intensity null law. They do not automatically justify replacing an expected ratio by a ratio of expectations for a finite local count. State the ensemble claim precisely.
5. **Qi--Ranard.** The published abstract does support an `O(1)` quantum Markov blanket outside which locally accessible information is approximately classical and obtainable from a fixed measurement. It does not imply pole disentanglement or definite global outcomes.
6. **Doucet--Deffner.** The PRX paper supports a commutation-based classification of two-body Hamiltonians for quantum Darwinism. Its objectivity/redundancy condition must not be conflated with this paper's product-boundary condition.
7. **Decoherence and quantum Darwinism.** Zurek/Schlosshauer support suppression of local interference and pointer/objectivity statements, not selection of one global branch. Attach citations sentence by sentence.
8. **Spontaneous emission.** Lindblad, GKSL, and Kraus are general reduced-dynamics references, not direct evidence for the historical atom-plus-field spontaneous-emission statement. Add a primary atom--field/unitary treatment or phrase the claim through a standard open-systems source.
9. **Generalized eigenproblems.** Add a standard source for regular/singular matrix pencils, homogeneous eigenvalues, algebraic multiplicity, and the QZ algorithm. The attached bibliography lacks one.
10. **Gleason/Busch.** Verify the precise effect/POVM assumptions under which Busch includes qubits; these theorems constrain probability assignments and do not supply a Hamiltonian or root-selection measure.
11. **Recent/peripheral items.** Hamid arXiv:2509.12280 and Guttel et al. arXiv:2602.02672 exist, but both are peripheral to the central result and should be omitted unless a specific sentence needs them. Palmer's 2026 PNAS metadata and the exact computational-limit claim require direct publisher verification before use.
12. **Covering radius.** The heuristic `sqrt(log d/d)` empty-cap scale needs a precise random-point-process citation and does not establish density for the correlated production roots. Prefer omission from the Letter until measured or proved.

### Recommended bibliography policy

Build a compact primary-source bibliography around: decoherence/global-branch distinction; Schulman; matrix pencils/QZ; Haar/Stiefel and spherical ensemble; and, if retained, one quantum-Darwinism Hamiltonian-classification paper. ETH/MBL, scars, collapse-model panoramas, monitored jumps, superdeterminism, and quantum-computing speculation dilute the PRL story unless they support a necessary sentence.

## 5. Narrative comparison

Scores below assess the repository as it exists, not rhetorical attractiveness.

| Rank | Narrative | Central claim available now | Strongest support | Principal risk | Decision |
|---:|---|---|---|---|---|
| 1 | **D: Relative-evolution geometry, exact Haar null, and a matched-field many-body exception** | A code-aligned unitary boundary-value spectrum has exact projective structure; Haar dynamics gives an isotropic null; one matched ring develops a Born-like polar root-count profile with size. | Exact block algebra and Stiefel/spherical-ensemble proof; post-cutoff matched sequence N=11--16; N=16 full complex root cloud. | It is not yet an operational probability law, and the production-to-same-time-forward bridge needs direct validation or the stated real-Hamiltonian time-reversal argument. | **Selected. Highest evidentiary strength and best PRL contrast if title/claims are narrowed.** |
| 2 | **B: Structure versus randomness in many-body measurement** | Generic Haar dynamics cannot select an axis, while a particular structured ring produces an axis-dependent root geometry. | Exact Haar isotropy plus matched-field full-sphere/scaling data; strong structured counterexamples. | “Structured detectors” is too broad; only one clean family clears all gates. Haar finite-realization data are pre-cutoff. | **Retain as conceptual organization and analytical null model, but not as a universal classification claim.** |
| 3 | **C: Exact state geometry on the Bloch sphere** | A regular production pencil yields `d` projective roots; full complex roots define an outcome-labelled/antipodal geometry. | Exact generalized-eigenvalue construction and homogeneous solver; full-sphere data exist. | Geometry alone may be too narrow for PRL. The exact antipodal outcome duality must be proved rather than described as two independent clouds; density/concentration is unproved. | **Useful theorem spine, not the whole Letter.** |
| 4 | **A: Quantum arrow of time to constructive unitary measurement states** | Measurement motivates a restricted-state loophole; exact pole-compatible boundary states can be enumerated. | Strong conceptual opening and exact forward-pencil algebra. | The numerical evidence is for a different production pencil; no selection measure, ready state, record stability, or definite-outcome mechanism. “Born probabilities” and “collapse” invite a fatal foundational objection. | **Use as motivation only. As the principal claim it is BLOCKED.** |

### Why narrative D is strongest

It survives the largest repository correction instead of hiding it. It can state a new exact null model, a finite-size many-body counterpoint, and the precise open gap between root counting and physical probability. The arrow-of-time frame can still open and close the Letter, but should not carry the evidentiary burden.

## 6. Recommended four-figure main-text story

### Figure 1 - Quantum arrows and the unresolved measurement step

Reproducible vector schematic:

`spontaneous emission -> decoherence -> thermalization -> measurement?`

Show “local/reduced irreversibility + global unitarity” under the first three and “definite global record still open” under measurement. Mark the restricted-state loophole as a hypothesis. This figure contains no empirical content.

### Figure 2 - Exact construction and the production/forward distinction

One compact diagram/equation figure:

- forward pole equations `(alpha C+beta D)eta=0` and `(alpha A+beta B)eta=0`;
- exact complementary-minor antipodality between their projective root multisets;
- production pencil `U10 v=lambda U00 v`, with exact factorization of `U(|0>v)`;
- inverse-time bridge to a pole preimage;
- `d` projective roots for a regular pencil, with singular/infinite-root caveat.

This figure prevents the most damaging mathematical misreading and makes the exact result independently publishable.

### Figure 3 - Full-sphere structured geometry versus the isotropic null

Main empirical figure. Regenerate from the N=16 matched-field raw NPZ at `t=10^3` and an adjacent detuned control (`hz0=0.09` or `0.11`). Use an equal-area `(phi, cos theta)` map or clearly visible sphere plus density/residual panel. Add an analytic Haar panel labeled “uniform one-point intensity,” not a pre-cutoff sampled cloud. Explicitly label blue roots and red antipodes.

This figure satisfies the mandatory full-`Omega=(theta,phi)` requirement and visually separates the matched two-dimensional cloud from meridional or narrow false positives.

### Figure 4 - Matched-field finite-size trend and falsification gates

Regenerate from `reports/zeus_single_pixel_analysis_2026-07-16/jointly_gated_born_candidates.csv`:

- `S_born` or, preferably, occupied-bin RMSE versus N for all four stored times plus median;
- coverage and `phi_harmonic_2` versus N;
- no extrapolation line or statistical error bar unless computed;
- caption: deterministic times are not disorder realizations.

This is the positive many-body result. A small inset may show a high polar-score meridional control, demonstrating why the full-sphere gate matters.

## 7. Risks and submission blockers

1. **Probability/selection blocker:** equal algebraic root counting is not a derived physical probability measure.
2. **Forward-pencil bridge blocker:** production numerics solve the fixed-input-pole `(C,A)` pencil for `U(t)`, not directly the forward pencil for the same `U(t)`. One forward-root validation or the fully documented real-Hamiltonian `U(-t)=U(t)^*` bridge is needed; the other outcome root locations then follow exactly by antipodes.
3. **Ready-state blocker:** different roots generally require different detector vectors; no fixed apparatus-ready state samples them.
4. **Record blocker:** instantaneous separability is not a stable, distinguishable, redundant macroscopic record.
5. **Finite-size blocker:** six sizes and four deterministic times do not establish an asymptotic Born limit; bin/KDE/time-window convergence is incomplete.
6. **Metric blocker:** `S_born` mixes support coverage with occupied-bin agreement. Report both ingredients and a full-sphere residual.
7. **Haar evidence blocker:** the only stored Haar realization is pre-cutoff; use the exact theorem or rerun a post-cutoff multi-seed concentration study.
8. **Provenance gap:** the matched Zeus runs record environment, command, host, and timestamps but not a git commit hash.
9. **Title risk:** “collapse” and “Born probabilities” are stronger than the verified result. A safer evidentiary title would foreground special product-state preimages/relative-evolution spectra and Born-like root-count geometry.

## 8. Bottom line for the root drafting process

Use the attached PDF as a conceptual map, not as an evidence source. Anchor every main numerical panel in the July 14--17 matched-field artifacts, use the exact Haar result instead of the March figure, and state both the antipodal outcome theorem and the production/forward time-direction distinction on page one or in Fig. 2. The sharpest defensible PRL claim is a new unitary boundary-value geometry with exact antipodal outcome duality, an exact isotropic random-unitary null, and a post-cutoff matched-field many-body sequence that develops a Born-like **geometric counting profile**; operational measurement probabilities remain an explicit open problem.
