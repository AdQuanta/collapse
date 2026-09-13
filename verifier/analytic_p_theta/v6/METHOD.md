# Method v6: scalar modulation and exact resonant exceptions

This separate scalar series supports report 10's a.e.-central-field proof.
It does not alter v1–v5 or claim to mechanize a measure-theoretic theorem.
Candidate expressions are JSON data. The checker imports only frozen v1
Pauli matrices and independently constructs the single-pixel conditional
unitaries, their scalar central-field phases, and the resonant time means.

Fixed exact tests: scalar sector modulation; Fourier-window derivative and
zero-frequency limit; frequency Jacobian constant; square-time interpolation
bound; a nonzero-field exception with b1=0,b2=1/2; and the commuting a=g
exception for harmonics 1–4. Negative controls alter the phase factor and
incorrectly set the resonant second moment to zero. All outcomes are logged.

Compile and check exact scalar rejection before freezing the source hashes.
No numerical tolerances, random sampling, production changes, or candidate
implementation imports. The all-T/a.e. argument remains the explicit proof
in report 10. Existing v5 finite detector identities are reused unchanged.
