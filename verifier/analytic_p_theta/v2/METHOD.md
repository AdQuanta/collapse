# Method extension v2

v1's fixed comparison series solves commuting X sectors. The next candidate
has noncommuting single-detector terms, so v1 does not test its new identities.
v2 adds an independent Pauli trace, its exact epsilon second derivative,
conditional product generators, and the chain density Jacobian. This is a
separate series. v1 files, tests, definitions and logs remain unchanged;
the manifest hashes both v2 and the reused v1 reference/helper files.

Self-validation before freeze: source compilation; independent explicit
two-spin reference self-checks already passed in v1. Regressions after
freeze: rerun the unchanged v1 candidate and reject deliberate sign, scale
and trace-coefficient mutations. No production observable/gate is changed.

v2 does not prove the limit by finite-size testing: that proof is in report 03.
Exact symbolic PASS labels apply only to the enumerated identities.
