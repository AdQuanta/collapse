"""Check commutator [X_1(s), X_1(u)] for the endpoint chain.

For the endpoint chain, X_1 = gamma_1 is a Majorana fermion. Under free
detector dynamics, X_1(s) = sum_j O_{1j}(s) gamma_j remains a linear
Majorana operator. The commutator of two linear Majorana operators is:

[sum_j a_j gamma_j, sum_k b_k gamma_k] = 2 sum_{j<k} (a_j b_k - a_k b_j) gamma_j gamma_k

This is a BILINEAR Majorana operator (quadratic), not zero! So the time
ordering in W = T exp(-2ig int X_1(s) ds) is nontrivial.

However, for the ring with 1/sqrt(N) scaling, the commutator is O(1/N)
in the tracial 2-norm (report 05, eq. 4). For the chain, the commutator
is O(1) — there is NO N suppression. This is exactly the obstacle identified
in report 05 Section 10.

The question is: can we compute tau(W^ell) exactly despite this?
"""
import sys
sys.path.insert(0, '.')

import numpy as np
from scipy.linalg import expm
from functools import reduce

I2 = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron_list(ops):
    return reduce(np.kron, ops)

def det_pauli(n, site, op):
    factors = [I2] * n
    factors[site] = op
    return kron_list(factors)

def build_detector(n, hz, j1x):
    d = 2**n
    h = np.zeros((d, d), dtype=complex)
    for i in range(n):
        h += hz * det_pauli(n, i, Z)
    for i in range(n - 1):
        h += j1x * det_pauli(n, i, X) @ det_pauli(n, i+1, X)
    return h

def build_x1(n):
    return det_pauli(n, 0, X)


# Check commutator norm
print("=== Commutator [X_1(s), X_1(u)] for endpoint chain ===\n")

for n in [3, 4, 5, 6]:
    D = build_detector(n, 1.0, 0.5)
    X1 = build_x1(n)
    d = 2**n
    
    for s, u in [(0.5, 1.0), (0.0, 1.0), (1.0, 3.0)]:
        Us = expm(1j * D * s)
        Uu = expm(1j * D * u)
        X1_s = Us @ X1 @ Us.conj().T
        X1_u = Uu @ X1 @ Uu.conj().T
        
        comm = X1_s @ X1_u - X1_u @ X1_s
        
        # Operator norm
        op_norm = np.linalg.norm(comm, ord=2)
        # Tracial 2-norm
        tr_norm = np.sqrt(np.real(np.trace(comm.conj().T @ comm)) / d)
        
        print(f"  N={n}, s={s}, u={u}: ||[X1(s),X1(u)]|| = {op_norm:.6f}, "
              f"||...||_2 = {tr_norm:.6f}")
    print()


# Now let's understand the exact structure differently.
# Since H_pm = D +- gx X_1 are BOTH quadratic Majorana Hamiltonians,
# U_pm are both Gaussian unitaries (they map Majorana operators to
# linear combinations of Majorana operators under conjugation).
#
# W = U_-^dag U_+ is therefore also a Gaussian unitary.
# Its action on Majorana operators is described by an orthogonal matrix:
# W gamma_j W^dag = sum_k R_jk gamma_k, where R is in O(2N).
#
# The tracial moments tau(W^ell) can be expressed in terms of this
# orthogonal matrix R. For a Gaussian unitary with orthogonal matrix R,
# tau(W) = prod_{j=1}^N cos(phi_j/2) where phi_j are the eigenangles of R.
#
# Actually, the Gaussian unitary associated to an antisymmetric matrix A
# (via exp(-i sum A_{jk} gamma_j gamma_k / 4)) has the property that
# W = exp(i phi_j / 2) in each normal mode.
#
# But we should think about this more carefully.

print("=== Exact structure via Majorana rotation matrices ===\n")

def majorana_rotation(H, n, t):
    """Compute the O(2N) rotation matrix for exp(-iHt) on Majorana operators.
    
    If U = exp(-iHt), then U gamma_j U^dag = sum_k R_{kj} gamma_k.
    """
    d = 2**n
    U = expm(-1j * H * t)
    
    # Build all 2N Majorana operators
    gammas = []
    for site in range(n):
        # gamma_{2*site} = X with Jordan-Wigner string
        ops = [I2] * n
        for j in range(site):
            ops[j] = Z
        ops[site] = X
        gammas.append(kron_list(ops))
        
        # gamma_{2*site+1} = Y with Jordan-Wigner string
        ops2 = [I2] * n
        for j in range(site):
            ops2[j] = Z
        ops2[site] = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Y
        gammas.append(kron_list(ops2))
    
    # Compute rotation matrix
    R = np.zeros((2*n, 2*n))
    for j in range(2*n):
        evolved = U.conj().T @ gammas[j] @ U
        for k in range(2*n):
            # R_{kj} = (1/d) Tr(gamma_k evolved_gamma_j) / Tr(gamma_k^2)
            # Since Tr(gamma_k^2) = d and Tr(gamma_k gamma_l) = d delta_{kl}
            R[k, j] = np.real(np.trace(gammas[k] @ evolved) / d)
    
    return R


for n in [3, 4, 5]:
    D = build_detector(n, 1.0, 0.5)
    X1 = build_x1(n)
    gx = 0.3
    t = 1.0
    d = 2**n
    
    H_plus = D + gx * X1
    H_minus = D - gx * X1
    
    # Many-body W
    U_plus = expm(-1j * H_plus * t)
    U_minus = expm(-1j * H_minus * t)
    W = U_minus.conj().T @ U_plus
    
    # Get the Majorana rotation matrix of W
    R_W = majorana_rotation(H_plus, n, t) @ majorana_rotation(H_minus, n, t).T
    # R_W should be the O(2N) matrix for W: W gamma_j W^dag = sum_k (R_W)_{kj} gamma_k
    
    # Actually, let me compute R_W directly
    R_plus = majorana_rotation(H_plus, n, t)
    R_minus = majorana_rotation(H_minus, n, t)
    
    # W = U_-^dag U_+
    # W gamma_j W^dag = U_-^dag U_+ gamma_j U_+^dag U_-
    #                 = U_-^dag (sum_k R+_{kj} gamma_k) U_-
    #                 = sum_k R+_{kj} (sum_l R-_{lk}^T gamma_l)
    #                 = sum_l (R-^T R+)_{lj} gamma_l
    # Wait: U_-^dag gamma_k U_- = sum_l (R_-^{-1})_{lk} gamma_l = sum_l (R_-^T)_{lk} gamma_l
    # since R_- is orthogonal.
    
    R_W = R_minus.T @ R_plus
    
    # Check that R_W is orthogonal
    orth_err = np.max(np.abs(R_W @ R_W.T - np.eye(2*n)))
    
    # Eigenvalues of R_W should come in conjugate pairs e^{+- i phi_j}
    evals_R = np.linalg.eigvals(R_W)
    phases = np.sort(np.angle(evals_R))
    
    # tau(W) from R_W
    # For a Gaussian unitary with rotation matrix R in SO(2N), 
    # the trace is: tau(W) = prod_{j=1}^N cos(phi_j / 2)
    # where exp(i phi_j) are the eigenvalues of R (paired).
    
    # Actually this needs to be more careful. Let me just check numerically.
    tau_W_direct = np.trace(W) / d
    
    # Extract the N angles from the 2N eigenvalues
    pos_phases = sorted([p for p in np.angle(evals_R) if p > 1e-10], reverse=True)
    if len(pos_phases) < n:
        # Include zero phases
        pos_phases = sorted([abs(p) for p in np.angle(evals_R)])[-n:]
    
    # Actually, pair them properly
    angles = np.angle(evals_R)
    angles_sorted = np.sort(angles)
    # Pair: angles_sorted[0] with angles_sorted[2N-1], etc.
    paired_angles = []
    for j in range(n):
        phi = (angles_sorted[2*n - 1 - j] - angles_sorted[j]) / 2
        paired_angles.append(phi)
    
    tau_W_formula = np.prod([np.cos(phi/2) for phi in paired_angles])
    
    print(f"  N={n}: tau(W) direct = {tau_W_direct.real:.8f}, "
          f"orthogonality error = {orth_err:.2e}")
    print(f"         R_W eigenvalues (angles): {np.sort(np.angle(evals_R))}")
    print(f"         paired angles: {paired_angles}")
    print(f"         tau(W) from formula = {tau_W_formula:.8f}")
    print()


# Now let's understand what determines the eigenangles of R_W.
# R_W = R_-^T R_+ where R_pm are the rotation matrices for H_pm.
# H_pm are both quadratic Majorana Hamiltonians.
# The rotation matrix for exp(-iHt) where H = -i sum A_{jk} gamma_j gamma_k / 4
# is R = exp(2At) where A is the real antisymmetric matrix.
#
# For H_+ = D + gx X_1 and H_- = D - gx X_1:
# The difference is 2gx X_1 = 2gx gamma_1.
# But X_1 = gamma_1 is a LINEAR Majorana, not bilinear!
# So H_+ - H_- = 2gx gamma_1 is NOT quadratic.
#
# Wait, that's the full qubit+detector Hamiltonian. In the detector-only
# sector (after projecting onto X_0 = +-1), H_pm = D +- gx X_1 acts on
# the detector Hilbert space alone. And X_1 on the detector space IS
# det_pauli(n, 0, X), which IS the first Majorana gamma_1.
#
# H_pm = quadratic + LINEAR Majorana term.
#
# A LINEAR Majorana perturbation to a quadratic Hamiltonian takes us
# OUTSIDE the Gaussian (free-fermion) realm. H_+ and H_- are NOT
# quadratic in fermions! The gx X_1 = gx gamma_1 term is a single
# Majorana operator, which is a fermion creation/annihilation operator.
#
# This means U_pm are NOT Gaussian unitaries and W is not a Gaussian unitary.
# The Majorana rotation picture breaks down.

print("=== Key insight: H_pm are NOT quadratic in Majoranas ===\n")
print("H_pm = D +- gx X_1 where D is quadratic and X_1 = gamma_1 is LINEAR.")
print("A linear Majorana term makes H_pm non-quadratic (it doesn't conserve")
print("fermion parity). This is why the simple Gaussian result fails.")
print()
print("However, the FULL qubit+detector system IS quadratic:")
print("H = gx X_0 X_1 + ... = -i gx b_0 a_1 + ..., which is bilinear.")
print()
print("The key: we should NOT project onto X_0 sectors if we want to")
print("use the Majorana/free-fermion structure. Instead, we should work")
print("with the FULL qubit+detector system as a free-fermion problem,")
print("and extract the root moments from the full (2N+1)-Majorana system.")
print()
print("The root moments are tau(W^ell) = Re tau_Q_D(U^ell |+><+| U^{-ell} |+><+|)")
print("which involves projection onto qubit X states within the full system.")
