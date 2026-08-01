# To-Do List

<!--
Add new work under "User tasks".
Unchecked user tasks always take priority over automation-generated next steps.
The automation may mark tasks complete and add result or blocker notes, but it must not delete or materially rewrite user instructions.
-->

## User tasks — highest priority

<!-- Add tasks in this format:
- [ ] Describe the required outcome and any important constraints.
-->

- [x] Go over the concise three-page `V_ab` activation report and ensure every term and notion is explained so the report is self-contained; modify the LaTeX source and PDF accordingly while preserving the three-page portrait-report constraint.
  - Completed 2026-07-22 21:18 +03:00. Reworked the report into a self-contained account: explicitly defined the anisotropic single-pixel Hamiltonian and every parameter, propagator blocks and `M(t)`, Cayley/angle mapping, reflected branches, finite-time kernel and activated `V_ab`, periodic power-law model and resolution gates, Born score and classification gates, basis-invariant activation metrics, sweep domain, and all statistical quantities. Preserved the requested three-page portrait format. Files: `reports/vab_activation_brief_2026-07-22/vab_activation_brief_2026-07-22.tex` and `output/pdf/vab_activation_brief_2026-07-22.pdf`. Validation: compiled twice with MiKTeX; PDF is exactly three portrait A4 pages; log has no LaTeX, package, box, reference, or PDF warnings; all three final pages were rendered at 140 dpi and visually inspected with no clipping, overlap, or unreadable content.
- [x] Analytically derive an expression for the eigenvalues of the matrix M(t)=U00(t)^(-1)U10(t) which are denoted {\lambda_i}, with \lambda_i(t)=\tan(\theta_i(t)/2)e^i\phi_i(t), and for their distribution P(\theta). Assume the system Hamiltonian takes the form H=H_D+H_I, where H_D is the detector-only component and H_I is the qubit-detector interaction (assume it's weak, but derive expressions which are valid for any time t). Perhaps you can utilize previous reports in this codebase wherever appropriate.
  - Completed 2026-07-21 21:39 +03:00. Derived the exact relative-unitary Cayley spectrum and the arbitrary-finite-time weak-coupling kernel/pushforward law. Validation: exact operator error `2.04e-16`; symmetric-coupling Magnus error slope `3.005`; focused tests passed.
- [x] For the Hamiltonian configurations from the last numerical study, create heatmaps of the energy difference \delta between any two pairs of detector eigenvalues (it should look like a matrix) for the various Hamiltonian configurations. Compare between cases where P(\theta) is: 1) Heavy-tailed and Born-like; 2) Heavy-tailed but not Born-like; 3) Not heavy-tailed and not Born-like (e.g. P(\theta) is a wrapped Gaussian).
  - Completed 2026-07-21 21:39 +03:00. Generated full `256x256` signed/near-zero gap matrices for three regimes, using the requested exact-resonant heavy non-Born counterexample `h_z=2J`; saved PNG, CSV, NPZ, and manifest outputs. Validation: Hermiticity/gap invariants and focused tests passed.
- [x] Document your findings in a LaTeX report (save as PDF).
  - Completed 2026-07-21 21:39 +03:00; expanded and revalidated 2026-07-21 22:15 +03:00. Produced the self-contained 11-page PDF `output/pdf/relative_unitary_gap_report_2026-07-21.pdf`; compiled without LaTeX/box/reference warnings and visually inspected every rendered page.
- [x] Compute additional heatmaps (amplitude and phase) of the detector-energy-basis matrix elements V_ab for the considered representative examples and incorporate them into the study.
  - Completed 2026-07-21 21:39 +03:00. Added normalized amplitude and convention-fixed phase heatmaps, machine-readable `V_ab` matrices, gauge caveats, and interaction-selection-rule conclusions to the study. Validation: coupling matrices are finite and Hermitian; focused suite `10 passed in 13.52s`.
- [x] Using the derived mechanism, formulate a falsifiable conjecture for Hamiltonians that yield wrapped heavy-tailed P(theta) and Born-like R(theta), verify it against additional Hamiltonian configurations/families, deliver a validated collection of successful Hamiltonians, and add the conjecture and verification to the LaTeX report/PDF.
  - Completed 2026-07-21 22:15 +03:00. Formulated and successively falsified simpler alternatives before retaining the resonance--mixing--reciprocity conjecture; classified 3,722 delivered spectra; delivered 131 validated successful rows and a 35-triple cross-size-robust collection. Translated the third ingredient into the executable small-kernel parameter certificate `S_B^(K)>=0.05`, coverage `>=0.60`, and distinct-angle fraction `>=0.70`, together with the resonance corridor and `Jpm>0`. The frozen strict rule selected `(hz,J,Jpm)=(+/-0.01,2,0.05)` at both N=13 and N=14 with zero false positives; its held-out recall is 2.2%, so the report explicitly identifies it as sufficient but not necessary. Updated the LaTeX source/PDF and produced verification figures plus CSV/JSON collections. Validation: all 34 N=13 successes persisted at N=14; strict-rule precision was 1.00 on training and held-out grids; Python compilation passed; focused suite `14 passed in 51.28s`; the 11-page PDF compiled without LaTeX/box/reference warnings and every rendered page was visually inspected.
- [x] Perform a more thorough study of the extent to which `V_ab` is activated for degenerate detector eigenvalues and its relation to wrapped heavy-tailedness of `P(theta)` and Born similarity of `R(theta)`. Add necessary figures and discussion, and update both the LaTeX report/PDF and the group-meeting presentation.
  - Completed 2026-07-22 19:51 +03:00. Implemented a basis-invariant projector-block audit with exact weight, activated-state coverage, block rank, spectral and block participation, largest-block share, cumulative gap-window activation, and finite-time kernel power. Evaluated all 880 anisotropic triples at detector sizes N_D=6,7,8 and joined N_D=8 to the complete N=14 dynamics. After censoring blocks below `1e-12 Tr(V^2)`, exact activation raises heavy-tail odds by 7.88 (Fisher p=2.1e-18) but has no Born association (odds ratio 0.81, p=0.624; ROC AUC 0.489). Finite-time kernel power strongly predicts broadness (rho with alpha -0.736; heavy-tail AUC 0.937), but is uncorrelated with Born score within heavy cases (rho=0.045, p=0.348), confirming that reciprocal branch balance is an independent requirement. Produced four new figures, machine-readable CSV/NPZ/JSON outputs, updated both LaTeX reports and the 22-slide Beamer presentation. Validation: Python compilation passed; focused suite `14 passed in 27.50s`; all three PDFs compiled without LaTeX/box/reference warnings; every page of both reports (14 and 8 pages) and every presentation slide (22) was rendered and visually inspected with no cropping or overlap.

## Automation next steps

<!-- The automation maintains this section. -->

## Blockers

* None.

## Last run

* Time: 2026-07-27 21:24 +03:00
* Status: No actionable work.
* Completed: No actionable tasks; awaiting user input.
* Validation: Re-read the durable state file and verified that every actual item under **User tasks** is checked, **Automation next steps** is empty, and **Blockers** is `None`. Confirmed that the sole unchecked checkbox is the commented task-format example; inspected the current worktree and available project instruction/documentation inventory.
* Blockers: None.
* Next run: No actionable tasks; awaiting user input.
* Files/resources: Updated `to-do-list.md` only.

## Recurring run instructions

At the beginning of every run:

1. Read `./to-do-list.md`.
2. Read relevant project instructions, including `AGENTS.md`, repository documentation, and applicable configuration files.
3. Inspect the current project state before making changes.
4. Determine which tasks are actionable and what evidence will prove each task is complete.

### Priority

Process work in this order:

1. unchecked items under **User tasks**, in file order;
2. incomplete work already started for a user task;
3. unchecked items under **Automation next steps**.

User tasks always outrank automation-generated work.

Re-read `./to-do-list.md` after completing each task and before starting an automation-generated next step. If I added a new user task during the run, process it before continuing with generated work.

### Execution

For each actionable task:

1. Preserve the task’s requested outcome, constraints, and explicit values.
2. Resolve required discovery, retrieval, and validation before acting.
3. Perform all authorized, in-scope local work needed to complete it.
4. Use efficient tool calls, parallelizing independent reads when useful.
5. After a failed attempt, diagnose the cause and try a meaningful alternative.
6. Retry transient failures no more than twice before recording a blocker.
7. Run the most relevant available validation.
8. Mark the task complete only when its requested outcome is achieved and supported by validation or other concrete evidence.
9. Append a concise completion note containing the completion time, result, and validation evidence.

For code or project changes, validation should normally include the most relevant combination of:

* targeted tests;
* type checking or linting;
* affected build checks;
* a minimal smoke test when broader validation is unavailable or disproportionately expensive.

If validation cannot be run, state why and record the best available alternative check. Never report an unvalidated assumption as confirmed completion.

Before writing `./to-do-list.md`, re-read its latest contents and merge your updates without overwriting concurrent user edits.

### Authorization boundaries

An unchecked item under **User tasks** authorizes ordinary in-scope local file changes and non-destructive validation required to complete that task.

Do not perform destructive, irreversible, financial, public, credential-related, or materially scope-expanding actions unless the user task explicitly authorizes that exact action and the required permissions are available.

Never invent credentials, approvals, results, evidence, or task completion.

### Genuine blockers

A genuine blocker is limited to circumstances such as:

* required information that cannot be derived from available project materials;
* missing credentials, access, permission, or explicit approval;
* an unavailable external dependency or service;
* a safety or policy restriction;
* an external, destructive, costly, or irreversible action requiring approval;
* repeated tool or environment failure after meaningful retries and fallbacks;
* a platform runtime or resource limit that prevents further work.

Difficulty, uncertainty that can be resolved through inspection, a failed first attempt, or the existence of additional steps is not by itself a blocker.

A blocker affecting one task does not end the run while other tasks remain actionable. Complete every unblocked task first. Stop only when no actionable work remains.

For each blocked task:

1. leave it unchecked;
2. record the exact blocker;
3. record completed partial work;
4. identify the smallest user action or missing input needed to unblock it;
5. avoid repeatedly attempting the same blocked action on later runs unless relevant conditions changed.

### Maintaining next steps

After completing the current actionable work:

1. Add automation-generated next steps only when they are necessary to complete an existing user-requested outcome, address a discovered defect, finish required validation, or resume meaningful partial work.
2. Give each generated task a concrete outcome and completion criterion.
3. Deduplicate generated tasks against existing open and completed items.
4. Remove or mark completed generated tasks when they are finished.
5. Never move generated tasks into **User tasks**.
6. Never invent optional improvements merely to keep the automation busy.
7. When the user-requested outcome is fully complete and no necessary follow-up remains, leave **Automation next steps** empty.

### File update and run report

Before finishing each run, update:

* task checkboxes and result notes;
* **Automation next steps**;
* **Blockers**;
* **Last run**.

The **Last run** section must include:

* execution time;
* whether the run completed, partially completed, was blocked, or found no actionable work;
* completed tasks;
* validation performed;
* unresolved blockers;
* tasks queued for the next run.

Then return a concise report with these headings:

* **Completed**
* **Validation**
* **Blockers**
* **Next run**
* **Files or resources changed**

If no actionable tasks exist, do not generate unnecessary work. Update the last-run status and report: **No actionable tasks; awaiting user input.**
