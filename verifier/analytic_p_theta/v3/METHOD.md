# Method extension v3: interacting detector moments

This is a separate comparison series, not a change to v1/v2 gates. The new
candidate is a sparse Pauli-word Liouvillian recurrence and a tracial echo
limit. A dense exact Hamiltonian independently checks supplied even spectral
moments, the leading normalized commutator, and finite-time echo coefficients.
The verifier imports only the original frozen Pauli reference, never the
candidate recurrence or production implementation. Formulas enter as data.

Freeze before evaluating candidates. Pre-freeze checks: Python compilation,
scalar/Pauli Frobenius norms, exact zero-identity rejection. After freeze:
compare the existing noninteracting limit and reject a deliberately wrong
interaction contribution. Previous v1/v2 source manifests remain unchanged.

A symbolic PASS proves the finite identities checked. It does not prove
the locality/CLT/time-average argument; that must be audited analytically.
