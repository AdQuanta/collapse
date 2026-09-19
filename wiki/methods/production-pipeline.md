# SPEC v1.0 Production and Verification Pipeline

> Sources: `SPEC.md` v1.0, 2026-09-15
> Raw: [Research specification snapshot](../../raw/project-governance/research-spec-v1.md)
> Updated: 2026-09-19

The existing code is not yet certified as the frozen v1.0 verifier. The required end-to-end pipeline is below; each stage must be implemented and validated before its paper-readiness gate can change from `INCOMPLETE`.

## Required stages

1. **Versioned input.** Record the Hamiltonian family/tier, basis, $N$, $T$, parameter ranges, coupling scaling, random seeds, code revision, and verifier version.
2. **Propagator blocks.** Construct $U_{00},U_{01},U_{10},U_{11}$ in the declared tensor ordering and in every relevant exact symmetry sector.
3. **Dual homogeneous solve.** Solve both outcome pencils $U_{10}+\lambda U_{11}$ and $U_{00}+\lambda U_{01}$ without matrix inversion.
4. **Root classification.** Retain finite, infinite, multiple, singular, and indeterminate cases. Compute null vectors, algebraic multiplicities where relevant, kernel dimensions, and homogeneous backward residuals.
5. **Independent checks.** Compare against direct small-$N$ solutions, reconstruct the exact final pole condition, verify sector completeness, and test known analytic models.
6. **Outcome measures.** Build $\rho_0^{(N)}$ and $\rho_1^{(N)}$ separately, weighted by kernel dimension and normalized independently.
7. **Preferred basis.** Search or validate the candidate axis, check uniqueness up to sign, and perturb it and the Hamiltonian to measure stability.
8. **Born diagnostics.** Report $E_2$, supported $E_\infty$, $E_{\mathrm{harm}}$, and $E_{\mathrm{marg}}$, plus support/coverage and estimator sensitivity.
9. **Ordered asymptotics.** Establish the $N\to\infty$ trend at fixed $T$ before testing $T\to\infty$. Distinguish instantaneous convergence from a Cesàro fallback.
10. **Physical robustness.** Demonstrate an open weak-coupling parameter region, finite-size and time robustness, detector-state diagnostics, a proposed mechanism, and decisive controls.
11. **Result packet.** Save machine-readable roots and metrics, configuration, environment, plots, logs, failure modes, and a concise claim limited to what the verifier established.

## Frozen-verifier rule

Search logic may adapt inside an approved family. Success definitions may not. Any proposed change to thresholds, metrics, family scope, or the verifier remains inactive until the user approves a versioned specification change. Results from different verifier versions cannot be silently pooled.

## Legacy tools

Historical coverage gates, reflected-ratio RMSE, $S_{\mathrm{born}}$, and isometry checks may remain useful diagnostics. None is sufficient alone. Existing solver output receives no v1.0 credit until the dual-pencil and complete metric suite above are independently verified.

See also: [[research-specification-v1]], [[paper-readiness-ledger]], [[projective-roots]], [[born-like-points]], [[homogeneous-qz]].
