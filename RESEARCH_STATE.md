# RESEARCH_STATE.md — Canonical Shared Research Memory

Last updated: 2026-08-27 (section 14a added; see also sections 15 and 17)

This is the **single canonical research-memory file** for this project. It is intended to transfer context between Ido, Claude Code, ChatGPT/Codex, and future agents.

**Instruction to every agent:** read this file before substantive research work. After a substantive discussion, new simulation, theoretical development, or decision, update this file before ending the session. Do not silently promote conjectures to results. Keep this file concise enough to remain readable, but detailed enough that a new agent can reconstruct the current scientific state without access to previous chat history.

Existing repository documents remain authoritative for implementation details and validated derivations. This file records the project-wide scientific context, current hypotheses, interpretation, and priorities.

---

## 0. Evidence labels

Use these labels explicitly:

- **PROVED** — analytic theorem/identity with checked assumptions.
- **VERIFIED_NUMERICALLY** — reproducible repository calculation with appropriate validation.
- **PRELIMINARY_NUMERIC** — useful calculation/stress test not yet validated through the production pipeline.
- **FALSIFIED** — a previously stated conjecture has a controlled counterexample.
- **CONJECTURE** — current working hypothesis.
- **OPEN** — unresolved.
- **DEFERRED** — potentially relevant but intentionally not a current priority.

Never describe a finite-size numerical trend as a theorem or asymptotic law without evidence.

---

# 1. Big-picture scientific question

The project asks whether measurement-like collapse and Born-like outcome statistics can arise from **pure unitary dynamics** of a qubit coupled to a complex detector, if one relaxes the assumption that every formal superposition in Hilbert space must correspond to a physically realized global state.

The conceptual motivation is:

- spontaneous emission and thermalization look irreversible but can be embedded in unitary dynamics on a larger Hilbert space;
- measurement/collapse is still usually treated as a separate postulate or interpretational issue;
- the standard linearity objection is real: if all physically realized states are closed under arbitrary superposition, unitary evolution of outcome-producing states generates superpositions of macroscopically distinct outcomes;
- the loophole explored here is **not breaking unitarity**, but allowing the physically realized set of states/trajectories to be a restricted subset of Hilbert space that need not itself be closed under superposition.

This is conceptually related to, but not identical with:

- Schulman's “special states”;
- superselection/restricted-state ideas;
- decoherence/einselection and Quantum Darwinism;
- emergent classicality/Markov-blanket results;
- superdeterministic/invariant-set ideas;
- objective-collapse models (as a contrast, not as the mechanism here).

Do not claim the project has solved the measurement problem. The operational physical selection/preparation measure over special states is still open.

---

# 2. Core mathematical object

The system is a central qubit plus detector,

\[
H = H_Q + H_D + H_{QD}.
\]

With the central qubit first in the tensor-product basis,

\[
U(t)=e^{-iHt}
=
\begin{pmatrix}
A & B\\
C & D
\end{pmatrix}.
\]

For the production fixed-input-pole convention, projective disentanglement roots are obtained from the generalized eigenvalue problem

\[
Cv=\lambda Av.
\]

A finite root defines the initial qubit state

\[
|\phi_0(\lambda)\rangle
=
\frac{|0\rangle+\lambda|1\rangle}
{\sqrt{1+|\lambda|^2}},
\]

with Bloch polar angle

\[
\theta = 2\arctan |\lambda|.
\]

The production solver uses homogeneous generalized eigenvalues / QZ so that finite, infinite, and indeterminate projective roots are treated correctly.

Key implementation:
- `collapse/relative_evolution_pencil.py`
- `collapse/analysis.py`
- `collapse/projective_roots.py`
- `collapse/hamiltonian_classification.py`

The relevant observable is the distribution of these special/disentangling states on the Bloch sphere and, in particular, whether the relative abundance of the two output branches approximates the qubit Born rule.

---

# 3. What “Born-like” means here

The legacy polar reflected-density ratio is

\[
R(\theta)=\frac{P(\theta)}
{P(\theta)+P(\pi-\theta)}.
\]

The qubit Born curve is

\[
R_{\rm Born}(\theta)=\cos^2(\theta/2).
\]

The repository contains scalar diagnostics such as `S_Born`, RMSE, coverage, phase uniformity, and modern full-sphere harmonic diagnostics.

Important limitation:

**Root geometry is not yet an operational probability measure.**

Counting algebraic roots equally is a mathematical/statistical construction. A physical derivation still requires a preparation/selection measure over detector microstates, root multiplicities/fibers, ready states, and times.

This distinction is central and should never be hidden.

---

# 4. Closest prior work and literature map

These papers/works are part of the conceptual background and should be available to every research agent at least by citation; ideally the most important ones should also be stored locally in a literature folder.

## Measurement / decoherence / classicality
- Born 1926 — probability rule.
- Zurek 1982 — environment-induced superselection.
- Zurek 2003 RMP — decoherence, einselection, quantum origins of classicality.
- Zurek 2009 — Quantum Darwinism.
- Joos & Zeh — decoherence.
- Schlosshauer — decoherence and measurement.
- Brandão, Piani, Horodecki 2015 — generic emergence of classicality.
- Qi & Ranard 2021, *Quantum* 5, 555 — emergent classicality / quantum Markov blanket.
- Doucet & Deffner 2024, *PRX* — Hamiltonian conditions for Quantum Darwinism.

## Special states / restricted physical-state ideas
- Lawrence S. Schulman, *Time's Arrows and Quantum Measurement* (1997).
- Schulman 2012, *Entropy* 14, 665–699, “Experimental Test of the ‘Special State’ Theory of Quantum Measurement.”
- Schulman 2017, *Entropy* 19, 343, “Program for the Special State Theory of Quantum Measurement.”
- Palmer 2026 / arXiv:2510.02877v3 — Rational Quantum Mechanics / finite arithmetic state-space restriction.
- Hossenfelder & Palmer 2020 — superdeterminism review.

## Thermalization / chaos / many-body structure
- Deutsch 1991 — ETH.
- Srednicki 1994 — quantum chaos and thermalization.
- Popescu, Short, Winter 2006 — canonical typicality.
- Atas et al. 2013 — level-spacing ratio distributions.
- Standard MBL / Poisson–Wigner-Dyson literature as needed.
- Turner et al. 2018 — quantum many-body scars.
- Serbyn, Abanin, Papić 2021 — scars review.
- Moudgalya, Bernevig, Regnault 2022 — scars review.

## Probability-theorem context
- Gleason 1957.
- Busch 2003 PRL — POVM/effect version including qubits.

These are uniqueness/consistency theorems for probability assignments, not mechanisms deriving the Born rule from a Hamiltonian.

## Quantum jumps
- Dalibard, Castin, Mølmer 1992.
- Plenio & Knight 1998.
- Minev et al. 2019.
- Barkay Guttel et al. 2026, arXiv:2602.02672 — monitored superconducting qubit.

## Objective collapse / alternatives
- GRW 1986.
- Bassi et al. 2013 RMP.
- Penrose/Diósi as background if relevant.
- Everett, Bohm, consistent histories as interpretational contrasts.
- Nonlinear quantum mechanics only as contrast.

## Recent computational classicality
- Hamid 2025, arXiv:2509.12280, “The Emergence of Objective Classicality: A Computational First-Principles Study of Observer-Induced Decoherence in Unitary Quantum Mechanics.”

### Full-text availability
At least Palmer's paper and an internal note on level statistics/MBL have previously been available locally in the ChatGPT workspace. Most other papers are currently represented by citation, not guaranteed local PDF access.

**Recommended later action:** create a shared local/Dropbox literature folder with full PDFs of the highest-priority papers:
Schulman 2012/2017, Zurek 2003/2009, Qi–Ranard 2021, Doucet–Deffner 2024, Guttel et al. 2026, Hamid 2509.12280, ETH/level-statistics references, and the main scar references.

---

# 5. Relation to Schulman

Schulman is the closest conceptual precursor and should be cited generously.

The current project differs by focusing on a **constructive many-body Hamiltonian procedure** for identifying special/collapsible/disentangling states through a generalized-eigenvalue problem and then statistically classifying their Bloch-sphere distribution across detector Hamiltonians.

Be cautious about claims such as “Schulman retains full vector-space superposition structure” unless verified directly from primary sources.

---

# 6. Important exact / robust results already in the repository

Consult `THEORETICAL_CONCLUSIONS.md` for the validated version.

Current strong results include:

- **PROVED:** a regular degree-\(d\) projective pencil has \(d\) roots counted with algebraic multiplicity.
- **PROVED:** unitary complementary-minor duality pairs the two forward branch label multisets by exact Bloch antipodes.
- **PROVED:** strict pointer-QND evolution, `[H,Z_Q]=0`, gives only the two poles in this construction.
- **PROVED:** adding an uncoupled tensor-factor spectator repeats roots but does not change normalized root geometry.
- **VERIFIED_NUMERICALLY:** the highlighted matched-ring finite-size examples exhibit a strong dipolar/Born-like structure, but are not Born-exact at the strict density level.
- **PROVED/VERIFIED:** common `hz0=hx0=0`, central-X-only models conserve `X_Q`, forcing roots onto a great circle and preventing full-sphere support.
- **VERIFIED_NUMERICALLY:** generic graph randomization alone does not repair that obstruction.
- **NOT SUPPORTED:** generic scrambling/chaos alone guarantees Born geometry.
- **NOT SUPPORTED:** resonance/heavy tails alone guarantee Born geometry.
- **NOT SUPPORTED:** field matching alone is sufficient.
- **NOT SUPPORTED:** two pixels automatically improve Born behavior.

---

# 7. Random-unitary baseline

A global Haar-random unitary is expected, by qubit-basis invariance, to produce an ensemble-averaged isotropic distribution of special states rather than a Born dipole.

This is important conceptually:

> “more random” is not automatically “more Born.”

The physics appears to require structure that preserves/selects a preferred measurement axis while still allowing nontrivial mixing.

Do not equate “chaotic” with “Haar-random.”

---

# 8. Controlled-unitary / dephasing contrast

For

\[
U=|0\rangle\langle0|\otimes W_0+
|1\rangle\langle1|\otimes W_1,
\]

an input

\[
(\alpha|0\rangle+\beta|1\rangle)\otimes|\eta\rangle
\]

evolves to

\[
\alpha|0\rangle W_0|\eta\rangle+
\beta|1\rangle W_1|\eta\rangle.
\]

Qubit populations \(|\alpha|^2,|\beta|^2\) are unchanged. This can cause dephasing/premeasurement but does not generically move a qubit to the poles.

Use this as a clean contrast between ordinary decoherence/premeasurement and the special-state construction.

---

# 9. Current Hamiltonian families in the project

The codebase supports several detector architectures, including:

- noninteracting / simple central-spin detectors;
- single-pixel detector models;
- dimerized pixels;
- two-pixel detectors;
- periodic rings;
- chains;
- all-to-all coupling;
- random graphs: Erdős–Rényi, Watts–Strogatz, Barabási–Albert, random-regular/expander candidates;
- mixed-field Ising-type models;
- exchange/XY channels;
- second-neighbor couplings;
- anisotropic central couplings.

Important implementation files:
- `collapse/hamiltonians/numpy_hamiltonians.py`
- `collapse/hamiltonians/quspin_hamiltonians.py`
- `collapse/detector_graphs.py`
- `collapse/hamiltonian_classification.py`

---

# 10. Current best conjecture about level statistics

This is the highest-priority research direction as of 2026-08-27.

**CONJECTURE (Ido):**
After resolving all exact detector symmetries and examining one irreducible sector at a time, a detector with **Wigner–Dyson level-spacing statistics** may be sufficient for Born-like root statistics.

Possible additional condition:

**OPEN / POSSIBLE:** the qubit energy splitting may matter.

A second observed possibility:

**CONJECTURE (Ido):**
A detector with **Poissonian** level-spacing statistics may also give Born-like behavior, but perhaps only when the qubit energy splitting is zero.

These are hypotheses, not validated sufficiency results.

---

# 11. Correct rule for level-spacing sectors

For random-matrix/level-spacing diagnostics:

\[
\boxed{\text{Never mix eigenvalues from independent exact irreducible sectors before forming spacings.}}
\]

Mixing independent spectra can make a chaotic Hamiltonian look artificially Poissonian.

The modern detector analysis in `examples/analyze_zeus_spectral_relations.py` follows the correct sector-by-sector rule.

Some older atlas/diagnostic code uses full detector spectra with mixed sectors and explicitly labels the RMT comparison as descriptive only. Those plots must **not** be used to establish WD/Poisson universality.

Also audit any scalar metric that concatenates sector eigenvalues before taking spacings.

---

# 12. Role of `V_ab` / coupling between sectors

**DEFERRED.**

There is a mathematically valid observation that the qubit coupling can connect detector sectors that are distinct under `H_D`. For example, a central XX term can change detector magnetization by one.

However, the project currently lacks sufficient evidence that this inter-sector coupling structure is the mechanism controlling Born behavior.

**Decision:** do not center the next analysis or explanation around `V_ab` or sector-connectivity. Return to it only if the simpler spectral program requires it.

For now, sectors are primarily important because level spacings must be computed inside irreducible sectors.

---

# 13. Qubit-energy / finite-size question

A small preliminary simulation showed significant dependence of Born quality on qubit splitting for a WD-like finite detector.

But this may be a finite-size artifact.

**OPEN QUESTION:**
For a detector family whose symmetry-resolved level statistics approach Wigner–Dyson as \(N\) grows, does the sensitivity to qubit energy disappear?

Let \(E_N(\Delta_Q)\) be a declared Born-error metric over a fixed microscopic qubit-gap window.

Define

\[
E_{\min}(N)=\min_{\Delta_Q} E_N(\Delta_Q),
\]

\[
E_{\max}(N)=\max_{\Delta_Q} E_N(\Delta_Q),
\]

and

\[
A(N)=E_{\max}(N)-E_{\min}(N).
\]

Interpretation:

1. If \(E_{\max}(N)\to0\), Born behavior becomes good uniformly over the tested qubit-gap range. Then qubit-energy sensitivity is asymptotically irrelevant.
2. If \(E_{\min}(N)\to0\) but \(E_{\max}(N)\) stays finite, a genuine qubit-gap condition survives.
3. If \(A(N)\to0\) but both errors approach a nonzero value, the gap sensitivity disappears but WD alone still does not generate Born.
4. If neither settles, accessible sizes are insufficient or the conjecture is wrong for that family.

This finite-size test is now the **top computational priority**.

---

# 14. Preliminary finite-size-independent stress test already done outside production pipeline

**PRELIMINARY_NUMERIC only.**

A small independent calculation used:
- detector \(N_D=9\);
- connected Erdős–Rényi graph, \(p=0.4\), seed 3;
- \(J=1\), \(J_\pm=0.7\), \(h_z=0.1\);
- source central coupling \(J_x=0.2\), scaled as \(J_x/\sqrt{N_D}\);
- \(t=100\).

Large detector magnetization sectors gave mean adjacent-gap ratios around \(0.51\), i.e. finite-size WD-like/intermediate.

Changing only the qubit longitudinal field changed the root Born-ratio RMSE substantially while the full-system gap ratio changed much less.

This is not yet evidence for a separate qubit-gap condition because:
- \(N_D=9\) is small;
- the detector is only approximately WD-like;
- the calculation did not use the production homogeneous-QZ pipeline;
- no finite-size scaling was performed.

Use this only as motivation for the controlled multi-\(N\) experiment.

---

# 14a. The qubit-gap scan is confounded by the central-X no-go

**VERIFIED_NUMERICALLY (Claude Code, 2026-08-27).**

The section 14 observation — "changing only the qubit longitudinal field changed the root Born-ratio
RMSE substantially" — is at least partly an artifact of the exact no-go recorded in section 6, not a
qubit-gap effect.

For central-X-only coupling with `hz0 = hx0 = 0` the Hamiltonian commutes with `X_Q`, so `Re(lambda) = 0`
and every root lies on the `y-z` great circle. The qubit gap `Delta_Q` in this family *is* `hz0`.
Therefore taking `Delta_Q -> 0` does not just close the gap: it re-imposes an exact symmetry that
forbids full-sphere support. Any "Born" score measured there is a polar statistic on a one-dimensional
circle, which section 13 of `GLEASON_BORN_CLASSIFICATION.md` explicitly warns is not evidence of
Born-compatible sphere geometry.

Reproduced on the section 14 detector (`N_D = 8`, Erdos-Renyi `p = 0.4`, seed 3, `J = 1`, `Jpm = 0.7`,
`hz = 0.1`, `Jx = 0.2` with `1/sqrt(N)` scaling, `t = 100`), on the `8 x 4` equal-area grid:

| central-qubit term | max abs `r_x` | coverage |
|---|---:|---:|
| `hz0 = 0` (X-only) | `1.1e-13` | 0.5625 |
| `hz0 = 1e-6` | `7.0e-05` | 0.4375 |
| `hz0 = 1e-3` | `7.2e-02` | 0.3750 |
| `hz0 = 0.05` | `9.96e-01` | 1.0000 |
| `hz0 = 0.2` | `9.77e-01` | 1.0000 |

**A transverse qubit field does not fix this.** `hx0 * X_0` also commutes with `X_Q`, so `hx0 = 0.3` at
`hz0 = 0` still gives `max abs r_x = 1.2e-14`. Only a non-X central channel breaks the symmetry at zero
qubit splitting: adding `Jz = 0.1` gives `max abs r_x = 0.986` with coverage `1.0`, and `Jzx = 0.1` gives
`0.80` with coverage `0.75`.

**Consequence for the section 15 program.** As designed, Priority 2's cleanest test — `Delta_Q = 0`
versus `Delta_Q != 0` at otherwise identical parameters — cannot separate a qubit-gap condition from the
no-go, because in the X-only family the two are the same knob. Priority 1 has the same problem at the
low end of its gap grid.

**Required design change before running either:** add a fixed non-X central channel (`Jz` is the clean
choice; `Jzx` only partly lifts the constraint) held constant across the whole gap grid, so that
full-sphere support survives at `Delta_Q = 0`. Then report `max abs r_x` and coverage alongside every
Born metric, and discard any grid point that fails the coverage gate rather than reporting its polar
score.

**OPEN:** whether any residual qubit-gap dependence survives once the no-go is lifted this way. That is
the question section 13 actually intends to ask, and it has not yet been asked.

---

# 15. Immediate computational program

## Priority 1 — WD family: finite-size qubit-gap scaling

Choose a detector family that is demonstrably WD-like after exact symmetry resolution.

Requirements:
- at least 4 system sizes;
- include the largest size practical with the validated production workflow;
- target the existing repository production regime, roughly \(N\sim14\)–\(16\), when feasible;
- preserve microscopic Hamiltonian ratios as \(N\) changes;
- use the same qubit-gap grid in fixed microscopic units such as \(\Delta_Q/J\);
- use a preregistered time protocol consistently across sizes;
- verify the detector remains WD-like at every size;
- **hold a fixed non-X central channel (e.g. `Jz`) across the whole gap grid** — see section 14a;
  without it the small-gap end of the grid re-imposes the central-X no-go;
- record `max abs r_x` and coverage at every grid point and discard points failing the coverage gate.

Produce:
- \(E_N(\Delta_Q)\) curves for all \(N\);
- \(E_{\min}(N)\);
- \(E_{\max}(N)\);
- \(A(N)\);
- detector sector-resolved \(\langle\tilde r\rangle\) at each \(N\).

Memory note: the production QZ path cannot reach `N = 16` on a 128 GB node, and `N = 15` fits only
with `compute_left_eigenvectors=False` in `collapse/relative_evolution_pencil.py`. Plan the size
sequence accordingly.

A useful candidate size sequence is around
\[
N=9,11,13,15
\]
or the nearest symmetry/computation-compatible sequence.

Do not overinterpret the smallest sizes.

## Priority 2 — Poisson family: same finite-size experiment

Pick a detector family that is convincingly Poisson **within resolved sectors**.

Run the same multi-\(N\) qubit-gap scan.

The cleanest test is:
\[
\Delta_Q=0
\]
versus finite
\[
\Delta_Q\neq0
\]
at otherwise identical parameters.

Ask whether “Poisson works only at zero qubit spacing” survives increasing \(N\).

**Blocking caveat:** in the central-X-only family, `Delta_Q = 0` is exactly the point where the
no-go of section 6 confines roots to a great circle, so this comparison is confounded as written.
Apply the section 14a design change before running it.

## Priority 3 — full combined-system spectrum

At the same points, compute level statistics of the full qubit+detector Hamiltonian, again sector by sector using exact symmetries of the **full** Hamiltonian.

Treat this as a diagnostic, not yet as the mechanism.

Compare:
- detector-only sector statistics;
- combined-system sector statistics;
- Born-error metrics.

Do not mix sectors.

## Priority 4 — only if needed, revisit mechanism

If the simple WD/Poisson + finite-size program fails to organize the data, revisit:
- coupling-accessible transitions;
- `V_ab`;
- resonance;
- information backflow;
- relative-unitary eigenphases;
- ETH/eigenstate diagnostics;
- operator spreading.

These are currently secondary.

---

# 16. Existing code that already helps with the next program

Relevant scripts/modules already present:

- `examples/sp_ring_hz0_sweep.py`
  - already supports multiple sizes in one run;
  - sweeps `hz0`;
  - uses symmetry sectors.

- `examples/analyze_zeus_spectral_relations.py`
  - modern symmetry-resolved detector spectral analysis.

- `collapse/level_spacing.py`
  - adjacent-gap ratios;
  - unfolded spacings;
  - Poisson / GOE / GUE reference distributions.

- `collapse/hamiltonians/quspin_hamiltonians.py`
  - symmetry-aware exact diagonalization.

- `collapse/hamiltonian_classification.py`
  - root classification and modern diagnostics.

- `collapse/relative_evolution_pencil.py`
  - production projective-root QZ solver.

- `collapse/relative_unitary_theory.py`
  - useful later for analytic mechanism studies.

Before writing new infrastructure, reuse these.

---

# 17. Computational standards

The computational challenge is a core part of the research.

Dense Hilbert-space dimension grows as
\[
2^N.
\]

Dense matrices scale in memory as approximately
\[
O(4^N),
\]
and full dense eigendecompositions as approximately
\[
O(8^N)
\]
in naive complexity.

Therefore:
- exploit exact symmetries aggressively;
- use QuSpin sector decomposition when valid;
- preserve a small-system NumPy reference implementation;
- use Zeus/HPC for production;
- record every configuration, seed, commit, solver, tolerance, and symmetry convention;
- never interpret a visually plausible plot without residual/convergence checks;
- do not claim convergence from a single \(N\).

Potential later accelerations:
- sparse/Krylov methods;
- matrix-free time evolution;
- tensor networks where entanglement permits;
- symmetry-resolved partial spectra for RMT diagnostics;
- optimized projective-root calculations.

Do not refactor the entire computational stack until the current scientific discriminators are established.

---

# 18. Research questions that remain important but are not current priority

- Is the set of collapsible states dense on the Bloch sphere as detector size grows?
- What is its measure / metric entropy?
- Is there a natural physical preparation/selection measure?
- Can a common detector ready macrostate support many input qubit states?
- How stable and redundant are the final detector records?
- Are locality and limited backflow important?
- Is there a theorem connecting detector spectral structure to suppression of higher odd multipoles?
- Can the framework yield experimentally observable non-Born deviations in mesoscopic detectors?
- Does the restriction of physically realized states have consequences for coherent quantum computation?
- Could harmonic-oscillator/Gaussian environments produce a special vector-subspace limit?

These should remain clearly marked OPEN or SPECULATIVE.

---

# 19. Possible falsifiability / experiments

Potential signatures:
- finite-size non-Born deviations;
- short-time deviations;
- detector-architecture dependence;
- qubit-gap dependence if it survives \(N\to\infty\);
- controlled crossover between spectral universality classes;
- mesoscopic detector tests;
- programmable quantum-simulator realizations.

Do not claim experimental feasibility until concrete parameter estimates are supplied.

---

# 20. Manuscript framing

The strongest current framing is:

- measurement is not usually described on the same footing as ordinary unitary many-body dynamics;
- universal superposition is the standard obstacle to definite outcome selection;
- this work explores a loophole: retain unitarity while restricting the physically realized state set;
- identify special/disentangling states constructively in many-body qubit–detector dynamics;
- use large-scale simulations and analytical treatment to determine which Hamiltonians produce Born-like statistics;
- emphasize that a broad classification is still being developed and that deviations are in principle falsifiable.

Preferred cautious title family:
- “Measurement-Like Dynamics from Unitary Qubit–Detector Evolution”
- “A Unitary Route to Measurement-Like Collapse”
- “Special States and Measurement-Like Dynamics in Unitary Many-Body Systems”

Avoid claiming a complete derivation of collapse or the Born rule until the physical selection measure is established.

---

# 21. Shared-memory protocol

This file replaces the need to transfer chat histories manually.

Whenever a new substantive discussion occurs:
1. record any new hypothesis or decision here;
2. tag its evidence status;
3. add exact parameter values/results if a calculation was run;
4. add links/paths to scripts, figures, reports, or papers;
5. note what was falsified or deprioritized;
6. update the priority list.

A new Claude Code session should begin with:

> Read `AGENTS.md`, then read `RESEARCH_STATE.md`. Treat `RESEARCH_STATE.md` as the canonical project memory. Inspect linked repository files before making claims. At the end of substantive research work, update `RESEARCH_STATE.md` with new results, decisions, and evidence status.

This is the only extra memory-transfer instruction that should be necessary.
