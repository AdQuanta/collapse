# Independent analytic P(theta) verifier

`v1/reference.py` builds exact positive-sign Pauli Hamiltonians from scratch.
It imports neither production Hamiltonians nor candidate implementations.
`v1/check.py` receives formula **data** in JSON. Candidate derivation code must
not import this verifier. Its fixed checks cover X-sector reductions, Taylor
orders 0–6, normalization, sign reflection, zero-coefficient reductions,
binomial characteristic functions, and exchange singularity certificates.

`v1/manifest.json` freezes every verifier Python source SHA256 before judging
the first candidate. Source changes require a new version, a method-change
justification, regression checks, and restarted comparisons. A pass proves only
the exact checked identities; infinite-size/time claims require the report's
analytical argument. No QZ gates, observables or production code are modified.

Runtime: Python 3.11; SymPy 1.14.0. Numerical crosschecks additionally use
NumPy 2.3.3 and SciPy 1.16.2. No stochastic tests or production HPC jobs.

Run from repository root:

```sh
python verifier/analytic_p_theta/v1/check.py --candidate research_reports/analytic_p_theta/commuting_x_v1.json --log reports/analytic_p_theta/verifier_log.jsonl
```

Subsequent separately versioned series:

- v2: independent noninteracting-field SU2 identities; see `v2/METHOD.md`.
- v3: interacting detector Liouvillian moments and echo coefficients; see
  `v3/METHOD.md`. Its matched series uses the eight-case parameter list in
  frozen `interacting_echo_v1.json`; candidate/control comparisons retain
  that list. Changing the comparison cases must be explicitly documented.

Every version keeps its own source-hash manifest. No previous version was
edited to make a later candidate pass.
