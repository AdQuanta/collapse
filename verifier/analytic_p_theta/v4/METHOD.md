# Independent extension v4: endpoint Majorana benchmark and audit

The previous v1–v3 sources are unchanged. v4 adds fixed N=1,2,3 full-Pauli
Hamiltonians with interacting and zero-coefficient controls, Majorana generator
identities, and the root anticommutator through six time derivatives. It also
checks an exact one-pixel Cesàro counterexample and candidate Jacobi pole
formulas. Cases and derivative orders are fixed in the verifier, not supplied
by the candidate. Derivation code cannot import this verifier.

Compilation and exact zero/rejection checks precede freezing. After freezing,
the candidate and an intentionally wrong moment are evaluated with the same
checks. Algebraic residues do not select the physical resolvent branch:
that branch and pole-existence inequalities require the report's proof.
