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

## Interacting central-X extension, 2026-09-13

Frozen v3 independently passed eight dense-Pauli certificate cases: symbolic
ring/chain Liouvillian moments, the ring commutator coefficient, full detector
NN/NNN XYZ moments at two distinct sizes, the independent-spin limit, and
the echo Taylor coefficients through order four. A deliberate candidate
omitting the interaction contribution was rejected with the exact residual
32 J²h²; that FAIL is retained. The candidate's eight-case parameter list
was frozen before evaluation and was unchanged in the negative control.
The source baseline for this series is commit
5616aa0883e9764e323f86ee10ce116f962d0f5b; candidate/verification files and
their SHA256 values are retained with the results. The isolated reduced
dependency set is `verifier/analytic_p_theta/requirements-reduced.txt`.

Five focused tests of the sparse candidate recurrence passed. They check
the complete symbolic second-moment formula, the collective/endpoint
distinction, conserved X with YY+ZZ bonds, the independent-spin sixth
moment, and the production minimum ring size. Pytest reported 14 dependency
deprecation warnings from Matplotlib/Pyparsing, with no test failures.

Production QZ checks of the exact interacting conditional-unitary reduction:

- 27 ring conditions: N=5,6,7, three times, transverse Ising/full NN/full
  NNN detector models. Maximum angular error 7.105427357601002e-15 radians;
  maximum homogeneous residual 7.128921365589886e-15. All passed.
- Nine endpoint-chain conditions: N=2,3,4, three times, full detector fields
  and NN/NNN XYZ coefficients. Maximum angular error 1.3322676295501878e-15
  radians. All passed. These check finite identities, not the chain time mean.

The ring snapshot also retains approximation errors against the Gaussian
using the **finite-N** integrated variance. These are diagnostics, with no
fitted gate. At t=1.33 the maximum error over six cosine moments is not
monotone with N; for full NN it is .20591425, .21439798, .34461740.
These small sizes do not demonstrate Gaussian convergence. The theorem
instead follows from the explicit fixed-time locality/blocking proof.
At the same time the sqrt(N)-scaled echo error is .45104935, .42595504,
.40406557; this is compatible finite-size evidence, not a measured
asymptotic exponent. No contrary high-harmonic errors were omitted.

New evidence files:

- `reports/analytic_p_theta/interacting_ring_echo_crosscheck_v1.json`
- `reports/analytic_p_theta/interacting_chain_norm_limit_crosscheck_v1.json`
- `reports/analytic_p_theta/wrong_interacting_moment.json`
- The existing append-only verifier/experiment logs.

Proof and scope audit: reports 05–07. The norm-limit result for chains does
not establish their generic Cesàro average. No claim is made for additional
central coupling axes. Full completion remains OPEN.
