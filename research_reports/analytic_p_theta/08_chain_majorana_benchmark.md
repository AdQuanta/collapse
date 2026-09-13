# OPEN: exploratory endpoint Majorana benchmark — audited continuation

2026-09-13. This draft explored, but did not establish, the exact Cesàro-averaged root measure
for the endpoint chain in the XX+transverse-field detector slice:

    H = h0x X_0 + gx X_0 X_1 + hz sum Z_j + J1x sum X_j X_{j+1}

with h0x = central qubit field, gx = central coupling, hz = transverse
detector field, J1x = detector NN XX coupling, open boundary conditions,
gy=gz=J1y=J1z=J2=0. This is the quadratic boundary-Majorana benchmark
identified in reports 05 and 07. It does NOT settle the retained hx or
general XYZ detector.

## 1. Full system as a Majorana chain (h0x = 0 scope)

### 1.1 Majorana representation

CONJECTURE in this exploratory draft: the full (N+1)-spin Hamiltonian (qubit site 0,
detector sites 1..N) in Jordan-Wigner Majorana operators
gamma_{2j} = (prod_{k<j} Z_k) X_j, gamma_{2j+1} = (prod_{k<j} Z_k) Y_j is:

    H = gx(-i gamma_1 gamma_2) + hz sum_{j=1}^N (-i gamma_{2j} gamma_{2j+1})
      + J1x sum_{j=1}^{N-1} (-i gamma_{2j+1} gamma_{2(j+1)})

All terms are bilinear. The Majorana gamma_0 = X_0 does not appear in H
and is exactly conserved: [X_0, H] = 0. The nontrivial dynamics involves
2N+1 coupled Majorana modes: {gamma_1, gamma_2, ..., gamma_{2N+1}}
= {b_0, a_1, b_1, a_2, b_2, ..., a_N, b_N}.

These form a one-dimensional tight-binding chain with alternating
on-site/hopping couplings:

    b_0 --(gx)--> a_1 --(hz)--> b_1 --(J1x)--> a_2 --(hz)--> b_2 -- ...

The coupling matrix A (antisymmetric, (2N+2) × (2N+2)) has A[0,:] = 0,
and the reduced (2N+1) × (2N+1) antisymmetric matrix on the remaining modes
determines all dynamics. The Heisenberg evolution is gamma(t) = R(t) gamma(0)
where R(t) = exp(At) is an orthogonal matrix.

### 1.2 Conditional Hamiltonians and the non-Gaussian obstruction

The conditional detector Hamiltonians H_pm = D ± gx X_1 (where
D = hz sum Z_j + J1x sum X_j X_{j+1}) have a LINEAR Majorana term
gx X_1 = gx a_1 in detector-only Jordan–Wigner variables. Audit correction:
the full-system gamma_2 is Z_0 X_1 and must not be identified with X_1.
A linear Majorana perturbation breaks
fermion parity conservation and makes H_pm non-quadratic in the
detector-only Fock space.

CONSEQUENCE: The sector propagators U_pm and the relative unitary
W = U_-^dag U_+ are NOT Gaussian/free-fermion unitaries on the detector
Hilbert space. The naive formula tau(W^ell) = cos(2 ell gx sigma(t))
derived from Y(t)^2 = sigma^2(t) I is INCORRECT for the interacting chain.

PRELIMINARY_NUMERIC, reported by the continuation and not independently
re-audited here: at (N=5, hz=1, J1x=0.5, gx=0.3, t=1), the
naive cos formula gives m_1 = 0.87641 while the exact value is 0.87504;
the error grows with ell and t.

### 1.3 Tracial locality and N-convergence

PRELIMINARY_NUMERIC, reported by the continuation and not independently
re-audited here: the finite-size moments are close at
(hz=1, J1x=0.5, gx=0.3, t=1):

    N=2: m_1 = 0.8750417, m_2 = 0.5313970, m_3 = 0.0549480
    N=3: m_1 = 0.8750408, m_2 = 0.5313928, m_3 = 0.0549399
    N=4: m_1 = 0.8750408, m_2 = 0.5313927, m_3 = 0.0549396
    N=5: m_1 = 0.8750408, m_2 = 0.5313927, m_3 = 0.0549396

Agreement to 6+ digits from N=3 onward. This is the content of report 07's
operator-norm convergence theorem, here observed numerically. The convergence
is driven by Lieb-Robinson light-cone locality: at fixed t, the endpoint
dynamics cannot distinguish a chain of length N from an infinite chain when
N is larger than the effective light-cone radius.

## 2. OPEN: exact Cesàro average

### 2.1 Numerical exploration

[To be filled with the results of chain_cesaro_moments.py]

### 2.2 Analytical structure

The time-dependent cosine moments m_ell(t) = Re tau(W(t)^ell) are
real-analytic functions of t. For the free-fermion full system, they
are determined by the (2N+1)-dimensional antisymmetric coupling matrix
via Pfaffian/correlation-function formulas involving the detector parity
operator P_D and the unitary conjugation.

The Cesàro average b_ell = lim_{T->inf} (1/T) integral_0^T m_ell(t) dt
extracts the zero-frequency component of the Fourier transform of m_ell(t).

For the conditional approach:
W(t) = exp(-2i h0x t) exp(it(D - gx X_1)) exp(-it(D + gx X_1))

**OPEN — audit correction:** a uniform law at generic h0x was proposed,
but this draft does not establish the required infinite-volume frequency
representation or the absence of resonant contributions for every ell.
Finite-N frequency matching does not justify the requested order of limits.

Subsequently, report 10 proves uniformity for Lebesgue-a.e. h0x by a
bounded-signal modulation argument that applies even to the general
interacting detector. That theorem does not validate this draft's mode
formulas or eliminate the exceptional fixed-field problem.

For h0x = 0: the Cesàro moments depend on the spectral properties of the
detector-coupled dynamics. This requires understanding the discrete
spectrum of the time-quasiperiodic function t -> tau_det(W(t)^ell).

## 3. OPEN boundary for the full goal

This Majorana benchmark slice leaves OPEN:
- The hx != 0 detector (breaking the free-fermion representation)
- General XYZ detector interactions (J1y, J1z, J2)
- Additional central coupling axes (gy, gz)
- The full parametric extension

The ring case is separately PROVED in report 05 through the locality/CLT
mechanism, which does not require free-fermion structure. The chain lacks
the 1/sqrt(N) collective scaling that suppresses time-ordering errors.

Audit: the original draft/scripts are preserved under `reports/analytic_p_theta/claude_continuation_snapshot/` and in the versioned `claude_continuation_snapshot.tar.gz` archive beside it. The title-level completion claim is withdrawn. The candidate v4 run failed at its bound-pole equation and is not promoted. Per the user's focus correction, this benchmark is parked. Report 09 addresses the general interacting chain and the obstacle to passing finite-volume replica averages to the thermodynamic limit; it does not claim to complete this benchmark.
