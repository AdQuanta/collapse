# Analytical ring/chain root measures

Active analytic contract: `goal-analytic.md`. It requests N→∞ first, then
an infinite-time Cesàro average. The separate older Born-phase objective
uses instantaneous limits; do not mix the two objectives.

**PROVED:** in the gx X-coupled family, detector hx, NN XX and NNN XX
coefficients cancel from the production pencil. Exact ring measures are
binomial folded phases and converge at fixed time to a folded Gaussian.
Endpoint chains have a single moving atom (two with a central X field).
The ordinary nonzero-coupling averaged measure is dtheta/pi and R=1/2.
Zero-frequency exceptions retain atoms. See
[commuting derivation](../../research_reports/analytic_p_theta/01_conventions_and_commuting_ladder.md).

**PROVED:** with no detector interactions and a purely transverse field,
the ring's limiting Gaussian phase variance is gx² sin²(ht)/h². The
Cesàro measure is nonuniform, with cosine moments
exp(-ell² gx²/h²) I0(ell² gx²/h²). The endpoint chain has an explicit
arcsine cap density. No operational probability interpretation is implied.
See [field derivation](../../research_reports/analytic_p_theta/03_independent_transverse_field.md).

**PROVED:** allowed central XY exchange creates a singular pencil at
t=pi/(4|g|), for every endpoint-chain size and ring N>=5. Indeterminate
roots have no canonical angle. The chain singularity has incompatible
regularizing paths yielding delta_0 and delta_pi, so continuity cannot
repair it. The requested everywhere-defined probability measure therefore
has a domain obstruction. See
[singular cases](../../research_reports/analytic_p_theta/02_singular_pencil_obstruction.md).

**PROVED, central-X rings:** arbitrary fixed detector fields and NN/NNN XYZ
interactions admit an exact local Pauli/Newton recurrence. The N-first root
law is a folded Gaussian whose variance is the integrated tracial detector
X autocorrelation. Locality bounds the fluctuation commutators in normalized
2-norm, which controls time ordering; exact unitary normality then transfers
trace moments to roots. The detector spectral measure is determined by a
local commutator recurrence and Carleman determinacy. The Cesàro moments are
explicit atom weights of associated Gaussian/compound-Poisson limits.
If detector hx!=0, conserved-energy overlap gives a positive zero-frequency
mass and hence an explicitly uniform late-time law, R=1/2, for gx!=0.
See [theorem](../../research_reports/analytic_p_theta/05_interacting_ring_echo_theorem.md)
and [proof audit](../../research_reports/analytic_p_theta/06_echo_proof_audit.md).

**PROVED, central-X endpoint chains:** the finite-time relative unitary has
an operator-norm half-chain limit, so its actual root measure has a
thermodynamic limit for arbitrary detector fields/NN/NNN XYZ coefficients.
The subsequent average at arbitrary prescribed fields is OPEN. See
[endpoint limit](../../research_reports/analytic_p_theta/07_endpoint_norm_limit.md).

**PROVED, all detector coefficients retained:** the endpoint first root
moment has a self-adjoint local generator K=[D,.]+g{X1,.}+2h0x and its
thermodynamic-first mean is the nonnegative zero-frequency spectral atom
in the tracial identity vector. This is only one moment. Exact replication
of higher moments needs a trace functional of norm 2^(N(ell-1)); hence its
finite-volume mean-ergodic theorem cannot simply be passed to infinite N.
A uniform bound on the actual signed frequency measures would suffice,
but remains OPEN. Reduced second-moment variations grow from 2.14 to 6.27
at N=2–5, with the commuting control at 1 and 24 production-QZ comparisons
passing. This is not a divergence proof. The next target is a weaker
near-zero cancellation/locality argument. See
[general-chain analysis](../../research_reports/analytic_p_theta/09_general_chain_cesaro_obstruction.md).

**PROVED, report 10:** for each fixed choice of all detector fields/NN/NNN
XYZ and gx, the central-X chain has uniform thermodynamic-first Cesàro law
dtheta/pi and R=1/2 for Lebesgue-almost every h0x. The exact scalar phase
exp(-2i ell h0x t), bounded echo moments, Plancherel, summable square times,
and interpolation control **all** moments without a global frequency-
variation bound. The field is fixed in the observable; field integration
is only a proof device. A null exceptional set remains, can depend on the
detector, and includes actual nonzero resonances. Thus this is not an
all-parameter or open-region theorem. The same argument applies to rings,
whose central-X result was already stronger. See
[a.e.-field theorem](../../research_reports/analytic_p_theta/10_almost_every_central_field.md).

**OPEN:** endpoint-chain Cesàro statistics at exceptional prescribed fields and additional central coupling
axes/non-X central fields in both families. The ring theorem cannot be
transferred to a nonnormal multichannel pencil or to unscaled endpoint
coupling. The quadratic boundary-Majorana slice is parked per the user's
focus correction; its v4 candidate check failed and was not promoted.
Retained hx and general XYZ remain part of the full objective.

Frozen independent SymPy v1/v2/v3 records, negative controls and reduced
production-QZ comparisons are in
[validation](../../research_reports/analytic_p_theta/VALIDATION.md).
Track atomic case progress in the dedicated master ledgers:
[[analytic_distribution_ring_master_ledger]] (ring) and
[[analytic_distribution_chain_master_ledger]] (endpoint chain).
The full goal remains OPEN.
