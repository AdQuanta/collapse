# PROVED: the central-X endpoint root measure has a thermodynamic limit

2026-09-13. This establishes the N-first limit for arbitrary fixed detector
fields and finite-range NN/NNN XYZ coefficients, with only gx central
coupling and a central h0x field. It does **not** establish the subsequent
Cesàro average for the general interacting endpoint chain.

Write D_N for the open detector Hamiltonian and

    H_N=D_N+X_Q(a+gX_1).

The finite-N conditional-unitary reduction, normalization, atomic support,
reflection test and Pauli/Newton root recurrence in report 05 Section 1
apply verbatim, replacing F_N by X_1. Thus every finite-time pencil in this
scope is regular and the polar moments are Re tau_N(W_N(t)^ell).

Use the half-infinite detector chain with the tracial product state tau.
Finite-range locality gives norm convergence X_1^(N)(s)→X_1^(infinity)(s)
uniformly on every compact time interval. The conditional interaction-picture
unitaries have bounded generators ±g X_1^(N)(s). Duhamel gives

    ||V_±^(N)(t)-V_±^(infinity)(t)||
      <= |g| integral_0^|t| ||X_1^(N)(s)-X_1^(infinity)(s)|| ds -> 0.

The limiting V_± are unitary elements of the quasi-local half-chain algebra.
It follows that W_N=e^(-2iat)V_-^dagger V_+ converges in **operator norm**
to the unitary W_infinity(t), after the natural spectator embedding.
Norm continuity of trace and polynomial functional calculus imply

    m_ell^infinity(t)=Re tau(W_infinity(t)^ell), ell>=0.

These moments uniquely determine a normalized polar probability measure on
[0,pi], so P_N(t) converges weakly at every fixed t. No nonnormal logarithmic
tail assumption is needed because the exact relative unitary is normal.
Atoms and poles remain whatever the unitary spectral measure assigns them.

This is also constructive: truncate the half-chain at distance L from the
endpoint, use the finite Pauli recurrence, then take L→infinity. Locality
bounds its fixed-time operator-norm error by a quantity exponentially small
outside the light cone. This spatial truncation has a uniform finite-time
error bound; it is stronger than an arbitrary formal spectral decomposition.
The coefficient-zero limits commute with this fixed-time construction because
the local dynamics depends continuously on bounded interaction coefficients.

The locality input is the same bounded finite-range theorem identified in
report 05. Here the perturbation is local and has bounded norm independent
of N, unlike the collectively scaled ring perturbation. Time ordering does
not disappear: the endpoint commutator generally has O(1) norm.

**OPEN:** fixed-time locality is not uniform for arbitrarily long times and
does not justify interchanging N→infinity with Cesàro averaging. Nor does
finite-N recurrence prove that the limiting moments have time means. An
exact boundary-mode or other spectral representation is still needed.
The restricted Majorana benchmark is now parked following the user's focus
correction. Report 09 keeps the general detector coefficients, proves the
first-moment mean, and isolates the unbounded replica trace functional
which prevents an immediate all-moment mean-ergodic argument. Its conditional
total-variation criterion is not established by the reduced numerical tests.

**Update, report 10:** the full Cesàro probability law is now PROVED to be
dtheta/pi for Lebesgue-almost every central h0x, for each fixed arbitrary
detector/coupling vector. This uses bounded scalar modulation and Plancherel,
not the replica bound. Exceptional prescribed fields remain OPEN, so the
arbitrary-parameter goal is not complete.
