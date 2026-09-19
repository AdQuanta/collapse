# Paper Readiness Ledger

> Sources: Repository research specification, Unknown; User instruction, 2026-09-15; User instruction, 2026-09-19
> Raw: [Exact formalism validation](../../raw/campaigns/2026-09-19-exact-formalism-validation.md); [Exact-formalism gate activation approval](../../raw/project-governance/2026-09-19-exact-formalism-gate-activation-approval.md); [Research specification v1.0](../../raw/project-governance/research-spec-v1.md); [Paper readiness reset](../../raw/project-governance/2026-09-15-paper-readiness-reset.md)
> Updated: 2026-09-19

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
| Complete matrix-pencil characterization | `INCOMPLETE` | Fresh derivation and tests covering finite, infinite, degenerate, and singular cases.                                            |
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

The matched-ring and independent-spin numerical failures (`tests/test_projective_root_conventions.py::test_small_matched_ring_obeys_real_hamiltonian_forward_bridge`, `tests/test_relative_evolution_study.py::test_zero_field_independent_spin_formula_matches_exact_sector_pencil`) remain open. Both are root-matching/numerical-rank issues in the generalized eigenvalue solver under symmetry-driven eigenvalue clustering (see [homogeneous QZ](../methods/homogeneous-qz.md) and `research_reports/EXACT_FOUNDATIONS_CONTRACT_2026-09-19.md`), separable from the state-level factorization identity this gate certifies. They continue to block "Complete matrix-pencil characterization," "No unresolved hard failure," and "Executable verifier," which all remain `INCOMPLETE`. No gate besides this one receives credit from this work.

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

