# RESEARCH_STATE.md — Canonical Shared Research Memory

Last updated: 2026-08-29 (section 10b added; see also sections 14a, 15, and 17)

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
- `core/relative_evolution_pencil.py`
- `core/analysis.py`
- `core/projective_roots.py`
- `core/hamiltonian_classification.py`

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

## Declared polar acceptance gate for the September 11 structural study

On 2026-09-11 the user selected the following finite-resolution definition for
the iff/universal-family task: full reflected polar coverage in 64 uniform
theta bins, bin-center R RMSE at most 0.05 against cos²(theta/2), and
maximal absolute Born moment residual at most 0.05 over the first eight
relations `2 a_(2m+1) - a_(2m) - a_(2m+2)`, m=0,...,7, where
`a_n = mean(cos(n theta))` uses all algebraic roots. No pseudocount is used.
This is a declared study gate, not exact equality on a continuous interval
or a claim of full-sphere Born geometry. The canonical 100-bin `S_born`
is reported alongside it and is not an additional acceptance threshold.

See [the constructive finite-family study](BORN_LIKE_CONSTRUCTIVE_FAMILY.md)
for the effective iff condition, an analytically certified family using
the native X/XX channels, numerical validation, and limitations.

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

Consult `manuscript/audits/THEORY_AUDIT.md` for the manuscript-facing audit.

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
- `core/hamiltonians/numpy_hamiltonians.py`
- `core/hamiltonians/quspin_hamiltonians.py`
- `core/detector_graphs.py`
- `core/hamiltonian_classification.py`

---

# 10. Current best conjecture about level statistics

This was the highest-priority research direction as of 2026-08-27. Section
10b records the later N=17 evidence and narrows the conjecture.

**CONJECTURE (Ido):**
After resolving all exact detector symmetries and examining one irreducible sector at a time, a detector with **Wigner–Dyson level-spacing statistics** may be sufficient for Born-like root statistics.

Possible additional condition:

**OPEN / POSSIBLE:** the qubit energy splitting may matter.

A second observed possibility:

**CONJECTURE (Ido):**
A detector with **Poissonian** level-spacing statistics may also give Born-like behavior, but perhaps only when the qubit energy splitting is zero.

These are hypotheses, not validated sufficiency results.

---

# 10a. First direct test of the WD conjecture: it survives, against expectation

**PRELIMINARY_NUMERIC (Claude Code, 2026-08-27).** Not production pipeline output,
single time, single size. Do not cite as finite-size evidence.

Before committing to the four-size scan of section 15, the conjecture was attacked
directly and cheaply: put a WD-like detector and an integrable clean ring through
the *same* classification pipeline at the same size and ask which produces better
Born-like geometry. The prior expectation, stated before running, was that the
clean matched ring would win, which would have bracketed the conjecture between an
integrable best case and a Haar worst case. **That expectation was wrong.**

`N_D = 9`, `t = 100`, `J = 1`, `hz = 0.1`, `hz0 = 0.1`, `Jx = 0.2` with `1/sqrt(N)`
scaling, `16 x 8` equal-area grid, `l_max = 5`. Gap ratios are taken inside the
largest resolved detector magnetization sector (dimension 126), never across
sectors. Poisson reference `0.386`, GOE reference `0.531`.

| family | sector `<r>` | coverage | polar `S_born` | harmonic leakage | dipole sharpness |
|---|---:|---:|---:|---:|---:|
| clean matched ring (`Jpm = 0`) | degenerate | 1.000 | 0.179 | 0.126 | 1.049 |
| exchange ring (`Jpm = 0.7`) | 0.420 | 0.969 | 0.205 | gated out | gated out |
| Erdos-Renyi `p = 0.4` (`Jpm = 0.7`) | 0.482 - 0.539 | 1.000 | 0.402 - 0.435 | 0.025 - 0.070 | 0.840 - 0.953 |
| Haar unitary | n/a | 1.000 | -0.045 | 0.939 | 0.029 |

The Erdos-Renyi row spans seeds 3, 11, 29 and 47. The ordering is stable across all
four: the WD-like detector beats the clean ring on `S_born` by roughly a factor of
two and has roughly half its harmonic leakage, with no seed overlap.

**Reading.**

1. The WD-like detector is the best Born-like case here, not the integrable ring.
   This is the first direct evidence *for* the direction of the section 10
   conjecture rather than against it.
2. The relation is **not monotonic in randomness**. Haar is maximally random and is
   decisively the worst: `S_born` at zero and 94% of the angular power outside the
   dipole. Section 7 stands unchanged; "more random" is still not "more Born."
3. The clean ring wins on *dipole sharpness* while losing on `S_born` and leakage.
   The scalar diagnostics disagree about which family is better, which is exactly
   the situation the repository's rule against single-score Born claims exists for.
4. The exchange ring fell below full coverage (`0.969`) and its full-sphere
   diagnostics were correctly refused rather than reported. The coverage gate works.

**What this does not show.** The two families differ in connectivity *and* in `Jpm`,
so level statistics are confounded with everything else that changed. This is a
correlation across two points, not a controlled test of WD sufficiency.

**OPEN, and the natural next experiment:** tune level statistics while holding the
rest of the Hamiltonian fixed, so `<r>` is the only thing that moves, and check
whether `S_born` tracks it. That isolates what this test could not.

**Note on the clean-ring gap ratio.** Its detector spectrum is massively degenerate,
so the adjacent-gap ratio is not a meaningful WD/Poisson diagnostic there and is
recorded as "degenerate" rather than as the `1.0000` the estimator returns.

Script: `work/wd_discriminator_2026-08-27/run_discriminator.py` (under gitignored
`work/`, so it is not in the repository; rerun to regenerate).


## 10b. N=17 spacing/Born comparison: detector statistics are not sufficient

**VERIFIED_NUMERICALLY (Codex, 2026-08-29).** Finite-size, symmetry-resolved
evidence; not an asymptotic universality statement.

The recent N=17 paired study resolves fixed `N_up`, momentum, and reflection
parity at `k=0`, merges exact numerical degeneracies, and compares both the
unfolding-free adjacent-gap ratio and unfolded-spacing KS distances. Its main
result is that detector level statistics alone do not determine the Born
profile.

- In 20 nearest-neighbor `hz0=0` cases, all gap-ratio classifications are
  Poisson-like while `S_born` spans `0.020` to `0.938`. The within-family
  Spearman correlation between `S_born` and pooled mean gap ratio is `-0.125`
  (`p=0.60`).
- In 20 second-neighbor `hz0=0` cases, stronger Born similarity is associated
  with more GOE-like statistics: Spearman `rho=+0.696`
  (`p=6.5e-4`). This is a selected finite sample and a family-level
  association, not a sufficiency result.
- Pooled across both families, the rank association is weak: `rho=+0.212`
  (`p=0.189`).
- The decisive control varies only the central field. A fixed Poisson-like
  detector (`mean r=0.3843`, KS Poisson/GOE `0.007/0.215`) spans
  `S_born=0.015..0.932`; a fixed GOE-like detector (`mean r=0.5264`, KS
  Poisson/GOE `0.207/0.015`) spans `S_born=0.055..0.930`. The detector spectra
  are unchanged throughout each scan.

**Consequence.** A detector-only claim that Wigner-Dyson statistics are
sufficient is falsified at finite N, and Wigner-Dyson statistics are not
necessary for a high polar Born score. The narrower conjecture still worth
testing is that, under fixed compatible dynamical conditions and full-sphere
coverage, moving a detector family toward Wigner-Dyson statistics improves
Born-like geometry. That requires tuning detector statistics while holding
the qubit field, coupling operators, time protocol, and other microscopic
ratios fixed.

Primary records:

- `reports/ranked_ring_symmetry_resolved_spacings_N17_2026-08-25/summary_N17.json`
- `reports/ranked_ring_N17_fresh_diagnostics_and_symmetry_spacings_2026-08-27/render_manifest.json`
- `reports/ring_activation_hz0_diagnostics_2026-08-24/hz0_scan_summary.json`
- `reports/ring_second_neighbor_wd_hz0_scan_N17_2026-08-26/hz0_scan_summary.json`
- `reports/N17_hz0_0_spacing_born_quadrants_2026-08-29/manifest.json`


---

# 11. Correct rule for level-spacing sectors

For random-matrix/level-spacing diagnostics:

\[
\boxed{\text{Never mix eigenvalues from independent exact irreducible sectors before forming spacings.}}
\]

Mixing independent spectra can make a chaotic Hamiltonian look artificially Poissonian.

The modern detector analysis in `scripts/analyze_zeus_spectral_relations.py` follows the correct sector-by-sector rule.

Some older atlas/diagnostic code uses full detector spectra with mixed sectors and explicitly labels the RMT comparison as descriptive only. Those plots must **not** be used to establish WD/Poisson universality.

Also audit any scalar metric that concatenates sector eigenvalues before taking spacings.

---

# 12. Role of `V_ab` / coupling between sectors

**ADDRESSED METHODOLOGICALLY; MECHANISM REMAINS FINITE-SIZE AND
OBSERVATIONAL.**

For the central interaction

\[
V=-J_x^{\rm eff}X_0\sum_j X_j,
\]

the isolated detector conserves magnetization `N_up` and translation momentum
`k`.  The uniform collective operator preserves `k` but changes `N_up` by one,
so the exact detector selection rule is

\[
(k,N_\uparrow)\longrightarrow(k,N_\uparrow\pm1).
\]

This information must not be used by mixing independent sector spectra before
forming spacings.  Level repulsion is still evaluated within each exact
irreducible detector sector.  The complementary dynamical object is instead a
matrix-element- and finite-time-weighted cross-sector transition measure,

\[
\left|\langle b,k,N_\uparrow\!\pm\!1|\sum_jX_j|
a,k,N_\uparrow\rangle\right|^2
K_t(E_b-E_a\pm2h_{z0}),
\qquad
K_t(\Delta)=\frac{4\sin^2(\Delta t/2)}{\Delta^2}.
\]

`core/activation_resolved_projective.py` implements this rule explicitly in
`(k,N_up)` blocks.  It diagonalizes the positive activation operator inside
each degenerate detector-energy subspace, so the result is invariant under an
arbitrary eigensolver rotation within that subspace.  The completed N=17
three-ring campaign is in
`work/zeus_three_ring_activation_resolved_N17_20260823_125039`, with summary
figures in `reports/ring_activation_hz0_diagnostics_2026-08-24`.

The activation-conditioned root distributions differ strongly from the global
distribution, establishing that the qubit does not sample detector states
uniformly.  Activation strength is not, however, monotonically equivalent to
Born similarity across the three cases.  The current evidence therefore
supports using cross-sector activation as a required diagnostic, not as an
established single-variable mechanism.

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
circle. The full-sphere requirements in `manuscript/audits/THEORY_AUDIT.md`
make clear that this is not evidence of Born-compatible sphere geometry.

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

**RESOURCE/VALIDATION DECISION (Matan, 2026-08-29):** keep the canonical
transverse-chain anisotropic control at `N=13,14`. The branch lacks the sector
reductions used by the larger ring cases, and `N=15` would require the full
dense/QZ path on the current 96 GB workflow. The memory-saving mode without
left eigenvectors cannot establish the repository's `qz_valid` diagnostic, so
it is not a substitute for a validated run. Summary tooling may retain the
legacy `chain_transverse_perturbative_N15` label, but current PBS jobs use
`chain_transverse_perturbative_N13_N14`. Treat comparisons with the primary
`N=15,16` ring families as finite-size-confounded.

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
with `compute_left_eigenvectors=False` in `core/relative_evolution_pencil.py`. Plan the size
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

- `scripts/sp_ring_hz0_sweep.py`
  - already supports multiple sizes in one run;
  - sweeps `hz0`;
  - uses symmetry sectors.

- `scripts/analyze_zeus_spectral_relations.py`
  - modern symmetry-resolved detector spectral analysis.

- `core/level_spacing.py`
  - adjacent-gap ratios;
  - unfolded spacings;
  - Poisson / GOE / GUE reference distributions.

- `core/hamiltonians/quspin_hamiltonians.py`
  - symmetry-aware exact diagonalization.

- `core/hamiltonian_classification.py`
  - root classification and modern diagnostics.

- `core/relative_evolution_pencil.py`
  - production projective-root QZ solver.

- `core/relative_unitary_theory.py`
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

---

## 22. Exact long-time Born objective: partial asymptotic obstructions

**PROVED (Codex, 2026-09-11; scoped results).** The new objective permits
N->infinity and demands exact instantaneous long-time Born behavior. The
finite gate in section 3 is unchanged and does not settle this objective.
See [BORN_ASYMPTOTIC_OBSTRUCTIONS.md](BORN_ASYMPTOTIC_OBSTRUCTIONS.md) for
five theorems, proofs, all reciprocal-coordinate Jacobians and limitations.

- Finite-dimensional unitary recurrence sends every projective root back
  arbitrarily close to the north pole. A nontrivial t-first weak root limit
  cannot exist; an unrestricted continuous-support joint limit cannot be
  independent of all late-time subsequences. N-first limits still require proof.
- For H_N=K_N-X_q(V_N+h_N) with [K_N,V_N]=0, any existing N-first then
  long-time weak root law is L delta_0+(1-L)dtheta/pi. Its exact Born moment
  identity requires L=1, which has no continuous angular coverage.
- Even without [K,V]=0, an X-conserving family K_N-X_q(V_N+h) can satisfy
  the necessary asymptotic first Born moment only on a measure-zero set of
  central-X fields h (assuming the stated N-first moment limits). Thus no
  open field interval works in this class. This is not a full-model no-go.
- Collective commuting g/sqrt(N) coupling has an exact folded-Gaussian
  N-first law and a uniform late-time response R->1/2. Its derived fixed-time
  correction is O(1/N), with O(1/N^2) remainder after correction.
- With nonzero central-Z detuning and [K,V]=0, an absolutely continuous
  limiting coupling law with finite third absolute moment cannot yield
  exact Born. Tight native linear-X spectral limits are sub-Gaussian. An
  explicit non-native heavy-tail spectrum does yield Born, demonstrating
  why unitarity alone is insufficient for a general no-go.

**VERIFIED_NUMERICALLY.** Six saved random seeds, three native topologies,
N=3,4,5 and times 0.2 through 300 give 504 production-QZ snapshots including
central-field perturbations and X-breaking controls. Maximum QZ residual
2.23e-15; in-scope trace discrepancy below 4.43e-12. Coverage is only
0.03125--0.71875; global finite-bin errors remain undefined, not filled.
All eight raw Born residuals and unchanged canonical S_born are saved.
Six analytic-count sizes 32--1024 check the derived correction. Sixteen
new tests pass; the combined relevant suite passes 60 tests. Eight figure
sets and provenance are in `reports/born_asymptotic_2026-09-11_final/`.
Code/config: `core/born_asymptotic.py`, `core/born_asymptotic_plotting.py`,
`scripts/analyze_born_asymptotic.py`, `configs/born_asymptotic_2026-09-11.json`.

**OPEN / NEXT.** The original full goal remains active. No non-tautological
full-model dynamical C_B, full microscopic preimage, or general open-phase
theorem/no-go has been established. The next unresolved class has central-Z
detuning with genuinely noncommuting detector/coupling operators, or central
YY/ZZ/ZX channels. Singular or escaping coupling spectra also need separate
treatment. Do not generalize the excluded X-conserving subspace to all native
Hamiltonians, or substitute the existing geometric iff for the requested
new structural condition. The research target remains root statistics,
not operational measurement probabilities.

---

## 23. Exact root-limit potential and native nonnormal counterexample

**PROVED (Codex, 2026-09-12; full Born objective remains OPEN).**
[BORN_NONNORMAL_LIMIT.md](BORN_NONNORMAL_LIMIT.md) extends section 22 with
an all-regular-pencils limit criterion and a native counterexample.

- The circle-averaged log determinant of C-exp(x+i phi)A, normalized by
  detector dimension and its x=0 value, is a bounded-kernel scalar potential
  J(x). Its right derivative is the radial CDF; endpoint slopes retain zero
  and infinite roots. Weak polar-root convergence is equivalent to local
  uniform J convergence, and convergence at all rational x is sufficient.
  This is a structural limit reduction, not the final requested Born C_B.
- Weak circle-averaged singular-value limits plus uniform integrability of
  their negative logarithmic tails suffice to pass to the correct J limit.
  Weak singular-value convergence alone is insufficient; common divergent
  terms may also require a separate cancellation argument.
- Native H_N=-(g/sqrt(N))(X_q sum X_i+Y_q sum Y_i), with zero detector and
  central fields, has all roots exactly zero at common regular times by
  charge grading. Yet its detector variables converge in all ordered trace
  moments to independent real Gaussians and their commutator has normalized
  squared Hilbert--Schmidt norm 4/N. All bounded propagator trace observables
  and singular-value statistics have the Gaussian limit. The roots of those
  Gaussian blocks are nontrivial. Consequently a Gaussian operator-moment
  limit cannot be substituted into the nonnormal native root problem, and
  logarithmic uniform integrability fails on at least one pencil circle.

**VERIFIED_NUMERICALLY.** At g=0.7, t=0.61 the normalized transition trace
at N=128 is 0.2876171138189103 versus the proved limit 0.2876935987125207.
The native first root moment remains 1 versus the Gaussian-block root value
0.4246128025749586. Six exact-sector sizes 4--128 retain all spin-sector
multiplicities; the largest matrix is 129 by 129. Sixteen production-QZ
snapshots at N=2--5 and times 0.3,0.61,1.3,3.0 have zero angles and maximum
residual 2.221e-16. Full native propagator comparisons, random-pencil Jensen
checks, and endpoint tests are included. Fourteen new tests and the combined
74-test relevant suite pass with runtime warnings treated as errors.
The pole-only law has coverage 2/64; all eight moment residuals vanish but
global errors remain null. No Born phase is inferred from this diagnostic.

Code/config: `core/projective_potential.py`, `core/collective_exchange.py`,
`core/projective_potential_plotting.py`, `scripts/analyze_born_nonnormal_limit.py`,
`configs/born_nonnormal_limit_2026-09-12.json`.
Two verified PDF/PNG figure sets, arrays, QZ records, and source/config/output
hashes are in `reports/born_nonnormal_limit_2026-09-12/` (uncommitted outputs).

**FALSIFIED / NEXT.** Asymptotic commutativity in normalized trace norm and
all operator moments do not establish the noncommuting thermodynamic root
law. Do not extend a commuting effective-field no-go through that shortcut.
Control normalized determinant differences or the needed small-singular-value
logarithmic tails for genuinely noncommuting native dynamics. No full-model
non-tautological Born iff, open microscopic phase, or full-model no-go is
established; the original exact long-time objective remains active.

---

## 24. Detuning-interval obstruction with commuting detector vector fields

**PROVED (Codex, 2026-09-12; scoped no-go).**
[BORN_DETUNING_INTERVAL.md](BORN_DETUNING_INTERVAL.md) proves Theorem H for
H_N(b)=K_N-X_q V_N-Z_q(W_N+b), with K_N,V_N,W_N commuting. If the joint
spectral law has finite transverse second moment and a nonzero active
fraction, and ordinary N-first then late-time phase mixing holds, exact
Born balance cannot hold throughout any open central-Z detuning interval.
No independence, spectral density, or longitudinal moment is assumed.

The exact root coordinate is x=sin²(theta/2)=k_b sin²(t Omega), with
k_b=v²/(v²+(w+b)²). In the mixed active law, Born requires south-cap mass
o(epsilon). Any positive field mass whose resonance lies inside a putative
Born interval gives an integrated south-cap lower bound C epsilon, a
contradiction. If the interval contains no resonances, an interior detuning
has a uniform gap. Finite E v² then gives south mass o(epsilon^(3/2)), while
Born requires at least c epsilon^(3/2). These two cases exhaust the interval.
This strengthens the earlier finite-third-moment gap obstruction to a finite
second moment; the earlier heavy-tail Born construction has infinite second
moment and shows the gap argument's moment order is sharp.

**PROVED (native pointwise corollary).** For V_N=h+g sum X_i/sqrt(N),
W_N=c sum X_i/sqrt(N), g!=0, every real h,b,c has an ordinary N-first then
late-time weak root limit, and none is continuous full-support exact Born.
For c!=0 and v0=h-gb/c!=0, the south cap divided by epsilon tends to
|v0|/|c| times the standard Gaussian density at -b/c, which is positive.
Coincident zeros instead give a strict support gap. The c=0 cases reduce
to the gap obstruction or the uniform polar law. This is an actual commuting
spectral CLT, not the invalid noncommuting substitution falsified in section 23.

**VERIFIED_NUMERICALLY.** Nine new tests pass; the combined relevant suite
passes 92 tests. At g=0.7,h=0.2,c=0.5,detector X field=0.13, 36 full native
QZ checks cover N=2,3,4, times 0.3,1.7,11.3,83 and b=-0.6,0.3,0.8.
Maximum angle-formula error is 8.072e-14; homogeneous residual 6.956e-16.
The exact resonance coefficients are 0.4039069944,0.1466188253,0.2040943358;
13 cap refinements from 1e-2 to 1e-5 verify the predicted limits. Coverage
is 0.0625--0.15625 and global histogram errors remain null. All eight raw
moment residuals and canonical S_born are saved without diagnostic changes.

Code/config: `core/commuting_vector_field.py`,
`core/commuting_vector_field_plotting.py`, `scripts/analyze_born_detuning_interval.py`,
`configs/born_detuning_interval_2026-09-12.json`.
The verified PDF/PNG figure, arrays, QZ records and checked provenance hashes
are in `reports/born_detuning_interval_2026-09-12/` (uncommitted).

**OPEN / NEXT.** This excludes a broader native XX/ZX preimage and any
commuting-vector detuning interval under the stated assumptions. It does
not resolve genuinely noncommuting detector fields or non-phase-mixing
spectral limits. A full-model non-tautological C_B, microscopic preimage,
robust positive phase or full-model no-go is still unproved. Continue with
noncommuting determinant limits; do not generalize this scoped exclusion.

---

## 25. Positive weak-coupling search: corrected ring and chain families

**USER DIRECTION (2026-09-12).** Prioritize constructing robust, stable Born
families with perturbative qubit–detector coupling, using existing `work/`
and `reports/` numerical evidence. Start from uniform XYZ fields and first-
and second-neighbor XYZ ring/chain Hamiltonians. The final ring normalization
is gx/sqrt(N), gy/sqrt(N), gz/N, superseding the earlier all-1/N clarification.
The open chain attaches only to detector site 1 with gx,gy,gz unscaled.
Readout remains central Z and coefficients use positive Pauli signs.

**VERIFIED NUMERICAL LEADS.** [BORN_WEAK_COUPLING_SEARCH.md](BORN_WEAK_COUPLING_SEARCH.md)
audits the nearest- and second-neighbor interacting ring sequences at
N=14,15,16,17, fixed microscopic parameters and t=1e6. Source-manifest
hashes and recomputed raw-angle metrics agree. The respective 64-bin
ratio RMSE sequences are 0.051086,0.046515,0.033764,0.015923 and
0.057754,0.050724,0.024587,0.017574; all have full reflected polar coverage.
At N=17 the eight-moment maxima are 0.014054 and 0.015164. These X-only,
zero-central-field references have great-circle support. Existing field
scans show sensitivity; no finite-width phase or long-time law is inferred.
Keep their interacting detectors as positive leads and extend independent
central channels and fields, rather than broadening narrow no-go classes.

**PROVED FINITE-TIME REFERENCE.** The phase-retaining interaction-picture
kernel uses the entire sinc energy filter, including exact degeneracies.
First Magnus exponentiation has fixed-time error bounded by t²||V||² in
operator norm and t²||V||_(4,tau)² in normalized Hilbert--Schmidt norm.
The latter bound is uniform in N under the corrected ring normalization.
This does not establish root convergence or a kinetic-time approximation.
Resonant resummation and determinant/logarithmic-tail control remain open.

Code/config: `core/ring_chain_family.py`, `core/weak_coupling_picture.py`,
`core/weak_coupling_evidence_plotting.py`, `scripts/audit_born_weak_coupling.py`,
`configs/born_weak_coupling_2026-09-12.json`. Six new focused tests and the
39-test relevant suite pass. Verified derived JSON/PDF/PNG outputs and
provenance are in `reports/born_weak_coupling_2026-09-12_final/` (uncommitted).
No production calculation was submitted. The original exact-Born goal
remains active; neither its positive nor negative completion test is met.
