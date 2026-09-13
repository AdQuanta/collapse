# Validation and provenance

2026-09-13. All analytical claims are scoped in reports 01–03; no numerical
test proves their infinite-size/time statements.

Independent symbolic checks:

- v1 frozen source hashes: 27 grouped identity checks passed, including 20
  all-sector Hamiltonian comparisons, Taylor orders 0–6, binomial moments,
  and exact exchange singularity certificates. The same candidate passed
  again unchanged after introducing the separate v2 series.
- v2: 10 grouped exact identity checks passed: relative SU2 trace, exact
  coupling second derivative, chain density Jacobian, six product-generator
  comparisons and zero-coefficient reductions.
- Five deliberate negative controls were rejected: wrong C sign, wrong XX
  bond multiplicity, wrong coupling scale, wrong relative-trace sign, wrong
  limiting variance. Their FAIL records are retained and are expected
  verifier checks, not discarded scientific failures.

Secondary production QZ comparison: **VERIFIED_NUMERICALLY**, 72 conditions
covering chains N=1,2,3 and rings N=5,6,7, four times (0,.13,.71,1.33),
commuting bonds and two noninteracting field directions. All passed.
Maximum matched polar-angle error: 1.0658141036401503e-14 radians.
Maximum homogeneous residual: 1.5496727399052818e-15.
The exact two-spin exchange propagator produces one indeterminate QZ pair,
confirming production does not turn that singular pencil into a full root
probability measure. No convergence claim is inferred from these small sizes.

Runtime: Python 3.11.16, SymPy 1.14.0, NumPy 2.3.3, SciPy 1.16.2,
Matplotlib 3.10.6 (required by core package imports). The startup failure
before installing Matplotlib is retained in the experiment log. This
environment is separately pinned; it is not claimed to reproduce the
repository's different production dependency pins. Solver: the unchanged
production homogeneous generalized eigensolver. Numerical comparison
tolerances were fixed before running: angle 1e-7, residual 1e-11.
No stochastic sampling, HPC submission, or production-data replacement.

Artifacts:

- `reports/analytic_p_theta/verifier_log.jsonl`: append-only exact checks and
  expected negative-control failures, candidate/source hashes and timings.
- `reports/analytic_p_theta/production_crosscheck_v1.json`: every numerical
  condition, exact parameters, solver residuals, source hashes and versions.
- `reports/analytic_p_theta/experiment_log.jsonl`: startup failure and outcome
  records, preserving non-successful attempts.
- `verifier/analytic_p_theta/v{1,2}/manifest.json`: frozen source definitions.

Reproduction from the original repository directory:

```sh
python -m py_compile verifier/analytic_p_theta/v1/reference.py verifier/analytic_p_theta/v1/check.py verifier/analytic_p_theta/v2/check.py scripts/verify_analytic_p_theta.py
python verifier/analytic_p_theta/v1/check.py --candidate research_reports/analytic_p_theta/commuting_x_v1.json --log reports/analytic_p_theta/verifier_log.jsonl
python verifier/analytic_p_theta/v2/check.py --candidate research_reports/analytic_p_theta/independent_field_v1.json --log reports/analytic_p_theta/verifier_log.jsonl
python scripts/verify_analytic_p_theta.py --help
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/verify_analytic_p_theta.py --output reports/analytic_p_theta/production_crosscheck_new.json
```

The new output path deliberately preserves the original immutable snapshot.
