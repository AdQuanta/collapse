# Method v5: general detector endpoint echo and replica contraction

Separate method extension; v1–v4 are unchanged. This series tests the exact
Liouvillian and replica identities proposed for the general central-X chain,
not a quadratic detector slice. Candidate formulas enter as JSON data.
The verifier imports only the frozen v1 dense Pauli construction.

Fixed coverage: endpoint sizes 1, 2, 3, all detector field/NN/NNN XYZ axes
nonzero when the geometry admits them, echo derivatives through order four,
moments ell=1,2,3, plus coupling-zero and commuting controls. The independent
reference is the direct product of the two conditional propagator series.
Replica cyclic traces and their Hilbert-space norms are checked separately.
An exact single-pixel integral tests why higher moments need signed spectral
weights. There are no numerical tolerances, random seeds, candidate imports,
or changes to the production root observable.

Pre-freeze checks: compilation, an exact scalar equality and deliberate
inequality, a 2x2 cyclic trace, and the zero generator. Freeze source hashes
before candidate evaluation. Negative candidates change the right-action
sign and the replica normalization independently. All failures are logged.

A PASS covers finite algebra only. The infinite-volume self-adjointness,
first-moment mean, and conditional Fourier-variation theorem need proofs.
Neither this checker nor a finite-size PASS proves the higher-moment bound.
