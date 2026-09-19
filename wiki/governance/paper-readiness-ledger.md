# Paper Readiness Ledger

> Sources: Repository research specification, Unknown; User instruction, 2026-09-15
> Raw: [Research specification v1.0](../../raw/project-governance/research-spec-v1.md); [Paper readiness reset](../../raw/project-governance/2026-09-15-paper-readiness-reset.md)
> Updated: 2026-09-15

## Reset state

By explicit user instruction, every `SPEC.md` v1.0 paper-readiness requirement starts **INCOMPLETE**. Existing analytical, numerical, and manuscript-era results are historical inputs only and must be verified again under the frozen v1.0 contract before they can satisfy a gate.

$$
\boxed{\texttt{paper\_ready = false}}
$$

No prior status label such as `PROVED`, `VERIFIED_NUMERICALLY`, `Production-Grade`, or a favorable finite-resolution score is carried into this ledger automatically.

## Mandatory gates

| Gate                                    | Status       | Fresh evidence required                                                                                                          |
| --------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| Exact collapse-like formalism           | `INCOMPLETE` | Re-derive the definition and validate exact output factorization without replacing it by fidelity.                               |
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

