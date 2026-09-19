# Evidence Registry & Audit Framework

## The Audit Philosophy
To avoid "cherry-picking" and ensure scientific rigor, the project uses a triple-lock audit system. No claim is promoted to a "Result" without passing through this framework.

Under SPEC v1.0, this historical triple lock is replaced for readiness purposes by a hybrid frozen verifier. Its executable layer checks exact collapse residuals, both generalized-eigenvalue pencils, kernel multiplicities, normalization, distribution construction, all Born metrics, estimator dependence, finite-size and long-time behavior, parameter-region robustness, preferred-axis stability, and result-packet completeness. Its fresh-context referee layer judges the mechanism, controls, preferred basis, detector-state interpretation, robustness, claim strength, and fair treatment of negative evidence. Neither layer may be edited after a run begins without explicit user approval.

## 1. Legacy Evidence Registry (`EVIDENCE_REGISTRY.md`)
The manuscript-era registry is a useful inventory of claims and artifacts, but it is not the complete append-only evidence ledger required by `SPEC.md` v1.0. Its entries must be freshly verified before they can satisfy a paper-readiness gate. Each entry is tagged with an evidence label:
- **PROVED**: Analytic theorem.
- **VERIFIED_NUMERICALLY**: Reproducible calculation with a production-grade pipeline.
- **PRELIMINARY_NUMERIC**: Useful but not yet validated.
- **FALSIFIED**: Controlled counterexample exists.
- **CONJECTURE**: Working hypothesis.

## 2. Numerical Provenance (`NUMERICAL_PROVENANCE.md`)
Every numerical claim must be linked to a provenance record containing:
- **Git SHA**: The exact code version used.
- **Config Hash**: The exact parameters.
- **Seed & Hardware**: RNG seed and runtime environment.
- **Output Path**: The raw data file used for the analysis.

The current append-only evidence ledger must additionally record the Hamiltonian family and exact parameters, detector size (N), fixed time (T), coupling and scaling convention, result status, verifier outputs, result-packet path, and a brief interpretation. Candidate packets must include exact roots, kernel multiplicities, reconstructed collapsible states, both normalized outcome distributions, the full metric suite, estimator checks, asymptotic analyses, preferred-axis stability, controls, detector-state diagnostics, and reproducibility metadata as applicable.

## 3. Theory and Numerical Audits
The `manuscript/audits/` directory contains historical manuscript-facing summaries:
- **Theory Audit**: Maps every theoretical claim to its proof or a specific theorem.
- **Numerical Audit**: Maps every figure and table to its provenance record and validation check.

These documents are source inventories only. They do not certify the current project. A candidate may be promoted only when the frozen executable checks pass and the independent referee finds that the claim is no stronger than its reproducible evidence. Material failures and negative candidates remain in the append-only ledger.

See also: [[production-pipeline]], [[symmetry-resolution]].
