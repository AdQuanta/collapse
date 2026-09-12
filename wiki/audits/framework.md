# Evidence Registry & Audit Framework

## The Audit Philosophy
To avoid "cherry-picking" and ensure scientific rigor, the project uses a triple-lock audit system. No claim is promoted to a "Result" without passing through this framework.

## 1. The Evidence Registry (`EVIDENCE_REGISTRY.md`)
The registry is the canonical log of all claims. Each entry is tagged with an evidence label:
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

## 3. Theory and Numerical Audits
The `manuscript/audits/` directory contains the final, manuscript-facing summaries:
- **Theory Audit**: Maps every theoretical claim to its proof or a specific theorem.
- **Numerical Audit**: Maps every figure and table to its provenance record and validation check.

See also: [[production-pipeline]], [[symmetry-resolution]].
