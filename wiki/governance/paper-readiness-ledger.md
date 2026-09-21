# Paper Readiness Ledger

> Sources: Repository research specification, Unknown; User instruction, 2026-09-15; User instruction, 2026-09-19; User instruction, 2026-09-20
> Raw: [Exact formalism validation](../../raw/campaigns/2026-09-19-exact-formalism-validation.md); [Exact-formalism gate activation approval](../../raw/project-governance/2026-09-19-exact-formalism-gate-activation-approval.md); [Research specification v1.0](../../raw/project-governance/research-spec-v1.md); [Paper readiness reset](../../raw/project-governance/2026-09-15-paper-readiness-reset.md)
> Updated: 2026-09-20

## Reset state

By explicit user instruction, every `SPEC.md` v1.0 paper-readiness requirement starts **INCOMPLETE**. Existing analytical, numerical, and manuscript-era results are historical inputs only and must be verified again under the frozen v1.0 contract before they can satisfy a gate.

$$
\boxed{\texttt{paper\_ready = false}}
$$

No prior status label such as `PROVED`, `VERIFIED_NUMERICALLY`, `Production-Grade`, or a favorable finite-resolution score is carried into this ledger automatically. One gate has since been promoted on fresh v1.0 evidence; see below. `paper_ready` remains `false` because every other mandatory gate remains `INCOMPLETE`.

## Mandatory gates

| Gate                                    | Status       | Fresh evidence required                                                                                                          |
| --------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| Exact collapse-like formalism           | `COMPLETE`   | Satisfied; see "Exact-formalism gate: promoted" below.                                                                            |
| Complete matrix-pencil characterization | `COMPLETE`   | Satisfied for non-singular, non-degenerate, non-exotic Hamiltonians; see "Matrix-pencil gate: promoted" below. |
| Outcome measures and multiplicities     | `INCOMPLETE` | Reconstruct both outcome sets, kernel dimensions, weights, and separate normalizations.                                          |
| Strong and weak Born criteria           | `INCOMPLETE` | Evaluate and report the two criteria separately.                                                                                 |
| Complementary Born metrics              | `INCOMPLETE` | Fresh values for $E_2$, $E_\infty$, $E_{\mathrm{harm}}$, and $E_{\mathrm{marg}}$.                                        |
| Estimator robustness                    | `INCOMPLETE` | Demonstrate stability under reasonable binning, KDE, harmonic, or other estimator choices.                                       |
| Controlled finite-size convergence      | `INCOMPLETE` | Systematic increasing sizes, resolution control, stable extrapolation, and region-wide behavior.                                 |
| Ordered asymptotic structure            | `INCOMPLETE` | Address $N\to\infty$ before $T\to\infty$ without silent interchange.                                                         |
| Long-time behavior                      | `INCOMPLETE` | Establish instantaneous convergence or explicitly justify and label the permitted time-average fallback.                         |
| Controlled weak coupling                | `INCOMPLETE` | Identify a relevant dimensionless small parameter and handle resonant/degenerate sectors correctly.                              |
| Finite robust parameter region          | `INCOMPLETE` | Verify an open non-fine-tuned region rather than an isolated point or manifold.                                                  |
| Unique stable preferred basis           | `INCOMPLETE` | Estimate the axis, show uniqueness up to sign, perturbative stability, and physical selection.                                   |
| Physical mechanism                      | `INCOMPLETE` | Establish the causal chain from many-body property through root statistics to the Born profile.                                  |
| Mechanism-to-Born derivation            | `INCOMPLETE` | Supply the primary analytic/semi-analytic derivation or the approved analytic-root-statistics plus controlled-numerics fallback. |
| Matched noninteracting control          | `INCOMPLETE` | Remove detector interactions while preserving the remaining architecture and compare all required observables.                   |
| Mechanism-breaking control              | `INCOMPLETE` | Suppress the proposed mechanism and verify the predicted degradation.                                                            |
| Detector-state characterization         | `INCOMPLETE` | Reconstruct relevant null vectors and apply physically appropriate state diagnostics.                                            |
| Local many-body realization             | `INCOMPLETE` | Certify at least one approved local ring or endpoint-chain realization.                                                          |
| Post-discovery disorder robustness      | `INCOMPLETE` | After clean discovery, test weak physically reasonable imperfections.                                                            |
| Reproducibility and bookkeeping         | `INCOMPLETE` | Complete the append-only run ledger and standardized result packets with traceable artifacts.                                    |
| No unresolved hard failure              | `INCOMPLETE` | Audit all ten hard-failure conditions against fresh positive and negative evidence.                                              |
| Executable verifier                     | `INCOMPLETE` | Pass the approved frozen objective layer for every applicable gate.                                                              |
| Fresh-context referee                   | `INCOMPLETE` | Pass an independent scientific audit of mechanism, basis, records, robustness, claim strength, and limitations.                  |

## Promotion rule

A gate may leave `INCOMPLETE` only when a fresh result packet identifies the exact configuration and code state, records the applicable verifier output, links all artifacts, and survives an independent review against the specification. Reproducing an old result is useful but does not certify a different gate by implication.

If fresh evidence supports only a robust approximate Born law, the exact claim remains incomplete. A weaker manuscript claim requires explicit wording and verifier alignment; favorable closeness cannot be promoted to exact convergence.

## Exact-formalism gate: promoted

The [state-level validation packet and plots](../campaigns/exact-collapse-formalism.md)
were built under `verifier/exact_formalism/v1/` (`exact-formalism-v1`). Promotion required, and now has, all of the following:

1. **Fresh certification.** The frozen checker independently reruns to `status: PASS`, `certification: true` against `reports/exact_formalism/2026-09-19-candidate-v1-review/`: 122/122 fixture states (88 accepted, 34 correctly rejected), 26/26 focused tests (`tests/test_collapse_state_reconstruction.py`, `tests/test_exact_formalism_verifier.py`), and hash-bound to `SPEC.md` and the verifier source.
2. **Independent scientific review.** A Codex verifier referee reviewed the proof, evidence, provenance, and limitations and returned PASS, correctly scoped to this row only.
3. **Explicit user activation approval.** Recorded in [the activation approval record](../../raw/project-governance/2026-09-19-exact-formalism-gate-activation-approval.md), which also documents an agent-side independent reproduction of every claim above (not merely trusting the referee) and a disclosed process irregularity in how the verifier's own manifest was first marked "activated" (a self-referential code edit, not a separately authorized external flag). The verification math was unaffected and independently reproduced; the approval record is now the traceable authorization that was previously missing.

**Resolved 2026-09-20.** The matched-ring and independent-spin numerical failures (`tests/test_projective_root_conventions.py::test_small_matched_ring_obeys_real_hamiltonian_forward_bridge`, `tests/test_relative_evolution_study.py::test_zero_field_independent_spin_formula_matches_exact_sector_pencil`) are closed, and the full suite is green at 691 passed, 0 failed. The cause was not the repeated-root handling recorded below but LAPACK `zggev` in Apple Accelerate losing six to nine digits on exactly structured blocks; the pipeline now solves the unitarily equivalent DFT-preconditioned pencil, which is exact in exact arithmetic and moved no tolerance. The frozen `exact-formalism-v1` checker reruns to `status: PASS`, `certification: true`, 122/122, against `reports/exact_formalism/2026-09-20-recertification-dft-preconditioner/`; note this evidences non-regression only, since that checker imports no `core/` module and passes identically with the change disabled.

*(Superseded for the matrix-pencil row by "Matrix-pencil gate: promoted, 2026-09-21" below; the statements about the other two gates stand.)* **No gate changed status on that work**, and an independent fresh-context referee reviewed the change on 2026-09-20 and endorsed that call for all three gates. Clearing a blocker is not evidence for a gate: "Complete matrix-pencil characterization," "No unresolved hard failure," and "Executable verifier" each still require their own fresh result packet and independent review under the promotion rule above. The referee ruled `DO NOT PROMOTE` on each, on these grounds: the matrix-pencil gate asks for fresh evidence on **finite, infinite, degenerate and singular** cases, and the degenerate case is now demonstrably mishandled — the solver returns silently wrong roots on a defective pencil with a clean residual and no guard — while the singular case still awaits a specification decision and the §3 kernel-multiplicity weighting is unimplemented; the hard-failure gate asks for an audit of all ten `SPEC.md` §23 conditions, which was not performed, and a live condition-6 finding stands in the 2026-09-20 markovianity record; and the executable-verifier gate requires a frozen objective layer for every applicable gate, which does not exist for matrix-pencil characterization, while `verifier/analytic_p_theta/v4` reruns to FAIL/REJECT/OPEN.

**Governance finding raised by the same review.** `verifier/analytic_p_theta/generic_verifier.py` imports `core/relative_evolution_pencil.py`, and no verifier manifest hashes any `core/` file. Hash-binding `SPEC.md` and a verifier's own sources is therefore **not sufficient** to freeze its behaviour: a change to `core/` — such as this one — can alter frozen-verifier output while every recorded hash still matches. Any verifier that depends on `core/` must hash those dependencies before its output can be treated as frozen evidence. Closing this is a prerequisite for the "Executable verifier" gate and needs explicit approval under `SPEC.md` §0.1.

The original description of the failures follows.

*Superseded, retained for provenance:* the two failures were recorded as root-matching/numerical-rank issues in the generalized eigenvalue solver under symmetry-driven eigenvalue clustering, separable from the state-level factorization identity this gate certifies, and as continuing to block "Complete matrix-pencil characterization," "No unresolved hard failure," and "Executable verifier." The clustering attribution was wrong; see [homogeneous QZ](../methods/homogeneous-qz.md) and the 2026-09-20 correction in `research_reports/EXACT_FOUNDATIONS_CONTRACT_2026-09-19.md`. Those three gates remained `INCOMPLETE` at that time for want of their own fresh evidence rather than for want of a passing test; the matrix-pencil row has since been promoted under a user-set scope, and the other two remain `INCOMPLETE`. No gate besides this one receives credit from this work.

## Matrix-pencil gate: promoted, 2026-09-21

The **Complete matrix-pencil characterization** row is `COMPLETE`, **scoped by explicit user
decision to non-singular, non-degenerate, non-exotic Hamiltonians**. `paper_ready` stays `false`;
every other mandatory gate remains `INCOMPLETE`, and no other gate takes credit from this work.

### The scope, and who set it

Three independent fresh-context referees refused three earlier submissions, each time on a
pathological pencil — Jordan blocks under arbitrary changes of basis, singular Kronecker
structure, a regular pencil with roots placed on the regularity sampler's own points. Every
finding was real and each was fixed. None was reachable from an approved Hamiltonian. The user
ruled that this was disproportionate effort relative to the physics and set the scope directly:
*"If the codebase can compute the projective roots properly for all non-singular, non-degenerate,
non-'exotic' Hamiltonians, I explicitly APPROVE promoting the corresponding ledger gate."*
Recorded at [the promotion approval](../../raw/project-governance/2026-09-21-matrix-pencil-gate-promotion-approval.md).

### Evidence in the approved domain

A 512-configuration sweep of the approved families — rings and endpoint chains,
`central_coupling` in {all, first}, `N = 3..6`, four field settings spanning zero and nonzero
`h_x`/`h_0x`, `t` in {1, 37, 211, 500}, both `SPEC.md` §3 outcome pencils — gives
**498/512 certified** `regular` with weights summing to the detector dimension. Kernel residuals
are below `1e-12` in 478 of the 498 and bounded by the certification band in the rest.

The **14 exceptions are refusals, never wrong answers**, and both classes fall outside the scope
above: two have root condition numbers of `5.8e27` and `3.8e28`, so their roots are not determined
at any precision; twelve are short-time endpoint-coupled cases whose roots cluster within
`sqrt(eps)` of one another, which is degeneracy beyond double-precision resolution. In no
configuration does the characterization report a measure it should not.

Two physics-domain defects were found and fixed while establishing this, both of which had been
missed by all three referee rounds because the referees were probing pathologies rather than the
approved families:

1. **Kernel dimension by absolute threshold was wrong at a computed root.** A root is located only
   to `kappa * eps`, so its kernel singular values sit at that level, not at zero. An `n * eps`
   threshold refused genuine twofold roots whose singular values were `4.6e-15` against a tolerance
   of `2.3e-15` — a factor of two — while the gap to the rest of the spectrum was thirteen orders
   wide. This alone refused **145 of 512** approved configurations. The scale is now
   `sqrt(eps) * formation_scale`, the same scale at which a root stops being determined.
2. **A cluster whose representative is not a root was not a cluster.** Weak, localized coupling at
   short evolution time places genuinely distinct ring/first roots within `1e-8`, and grouping them
   put the representative between two roots where the pencil is not singular. Such a group is now
   split back into singletons, recovering a further 32 configurations.

### Supporting evidence

- Verifier `matrix-pencil-v1`: `status: PASS`, **45/45** cases, five families (finite, infinite,
  degenerate, defective, singular), four exact symbolic checks. It reports `certification: false`
  and `status: candidate`, because `SPEC.md` §0.1 reserves activation to the user and activation
  was not requested. **The separate "Executable verifier" gate therefore remains `INCOMPLETE`.**
- Population certificate: **8,607 defective pencils** drawn behind random two-sided equivalences of
  condition up to `1e6`, **zero certified**. This is the property a fixture list cannot establish,
  since the failure is reachable from any fixture by a change of basis.
- 38 characterization tests with answers known in closed form or by exact construction; full suite
  **729 passed, 0 failed**. Mutation testing kills the substantive mutants, including
  weight-by-multiplicity, bound deletion, clustering removal and the superseded rank tolerance.
- Contract fixtures F0–F6 present. **F7 and F8 cannot be supplied**: both require both forward
  outcome measures compared between the full basis and a symmetry-sector path, and that path solves
  only the fixed-input `(A,C)` pencil.

### What this promotion does not claim

- **Nothing about singular pencils beyond refusal.** `SPEC.md` supplies no measure rule for a
  singular continuum and the 2026-09-19 contract names that user decision as still owed.
- **Nothing about arbitrary Kronecker structure.** The guarantee is one-sided: certification by
  refusal. A staircase/GUPTRI computation is what would settle the general case.
- **No verifier activation**, and therefore no credit toward "Executable verifier".
- Three earlier submissions in this row were refused; their withdrawn claims are preserved in the
  git history of this file rather than restated here.

## Gate dependencies

The practical order is:

1. revalidate the exact algebra and numerical root pipeline;
2. define the complete outcome measures and diagnostics;
3. reverify candidate regions across size, time, and estimators;
4. establish basis selection, mechanism, detector interpretation, and causal controls;
5. run robustness, reproducibility, the frozen verifier, and the independent referee.

This ordering is operational, not a relaxation of any gate.

## See Also

- [Research specification v1.0](research-specification-v1.md)
- [Research control center](research-control-center.md)
- [Audit framework](../audits/framework.md)
- [Production pipeline](../methods/production-pipeline.md)

