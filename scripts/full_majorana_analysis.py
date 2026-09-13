"""Exact endpoint chain root moments via full free-fermion system.

The full qubit+detector Hamiltonian with central X conservation and
XX+transverse-field detector is quadratic in 2(N+1) Majorana fermions:

H = -i sum_{j,k} A_{jk} gamma_j gamma_k / 4

where A is a real antisymmetric (2N+2) x (2N+2) matrix. The central
qubit Majorana a_0 = X_0 is decoupled (doesn't appear in H at all when
h0x=0), so the actual coupled system uses 2N+1 Majoranas: b_0, a_1, b_1,
..., a_N, b_N.

The root moments are:
m_ell(t) = Re tau(W^ell) where W = U_-^dag U_+

In terms of the full system (report 05 / subagent analysis):
W = P_D e^{iH_+t} P_D e^{-iH_+t}

where P_D = prod Z_j is detector parity. This is a "parity echo".

For a free-fermion system, tau(W^ell) can be computed from the
single-particle rotation matrices.

Key insight: H_+ = D + gx X_1. Write this in Majorana form using
the DETECTOR-ONLY Hilbert space. X_1 = gamma_1 is a linear Majorana.
This perturbation DOES break the free-fermion structure of the
conditional Hamiltonian.

However, we can use the FULL qubit+detector free-fermion system.
In that system, X_0 X_1 = -i b_0 a_1 is bilinear, so the full H is
quadratic. The time evolution maps Majoranas to Majoranas linearly.

The question: how do we express tau_det(W^ell) in terms of the full
system's Majorana rotation?

Since X_0 is conserved and equals a_0, and the full tracial state
has tau(a_0) = 0, tau(a_0^2) = 1, we can write:

tau_det(W^ell) = tau_full((1+a_0)/2 W^ell (1+a_0)/2) * 2

Wait, this isn't right. Let me think more carefully.

In the X_0 = +1 sector: H_+ = D + gx X_1
In the X_0 = -1 sector: H_- = D - gx X_1

The full unitary is U_full = exp(-iHt) = |+><+| ⊗ U_+ + |-><-| ⊗ U_-

W = U_-^dag U_+ acts on the detector space.
tau_det(W^ell) = (1/2^N) Tr_det(W^ell)

In the full space:
tau_full(U_full^ell |+><+| U_full^{-ell} |+><+|)
= tau_full(|+><+| U_+^ell |+><+| U_+^{-ell}) (wrong, projectors don't work this way)

Actually, let's use:
|+><+| = (I + X_0)/2 = (I + a_0)/2

tau_full((I+a_0)/2 U^ell (I+a_0)/2 U^{-ell})
= (1/4) tau_full((I+a_0)(I+a_0(ell t)))
where a_0(t) = U^dag a_0 U = a_0 (conserved!)

So this is just (1/4) tau_full((I+a_0)^2) = (1/4) tau_full(2(I+a_0)) = 1/2.

That's trivial. The issue is we need the DETECTOR trace of W^ell,
not the full trace.

Let's think again. Define P_+ = |+><+|_Q = (I+X_0)/2 on the full space.

tau_full(P_+ U^ell P_+ U^{-ell})
= (1/2^{N+1}) Tr(P_+ U^ell P_+ U^{-ell})
= (1/2^{N+1}) sum_{|psi>} <psi| P_+ U^ell P_+ U^{-ell} |psi>

This should give us (1/2) * (1/2^N) Tr_det(U_+^ell U_+^{-ell}) = 1/2.
Not helpful.

OK so let me try a different decomposition. What we actually need:

tau_det(W^ell) = (1/2^N) Tr_det((U_-^dag U_+)^ell)
              = (1/2^N) Tr_det(U_-^dag U_+ U_-^dag U_+ ... U_-^dag U_+)

In the full system, U_- = <-|_Q U_full |->`_Q and U_+ = <+|_Q U_full |+>_Q.
Since X_0 is conserved, these are just the sector propagators.

Another approach: Use the fact that the full system is free-fermion,
and the relative unitary W can be expressed in terms of single-particle
data of the FULL system.

Actually, for a free-fermion system with 2M Majorana modes, the
Pfaffian formula gives:
tau(prod gamma_{i_1} gamma_{i_2} ... gamma_{i_{2k}}) = Pf(C)
where C_{ab} = tau(gamma_{i_a} gamma_{i_b}).

The key objects are the Majorana covariance matrix and evolved operators.

Let me try a completely different tactic: just compute things numerically
for the full free-fermion system and see what patterns emerge.
"""
import numpy as np
from scipy.linalg import expm
from functools import reduce

I2 = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron_list(ops):
    return reduce(np.kron, ops)

def build_full_system(n, hz, j1x, gx, h0x=0):
    """Build full (N+1)-spin Hamiltonian: qubit + detector.
    H = h0x X_0 + gx X_0 X_1 + hz sum_{j=1}^N Z_j + J1x sum X_j X_{j+1}
    """
    ntot = n + 1  # total spins
    d = 2**ntot
    H = np.zeros((d, d), dtype=complex)
    
    def full_pauli(site, op):
        factors = [I2] * ntot
        factors[site] = op
        return kron_list(factors)
    
    # Central qubit field
    if h0x != 0:
        H += h0x * full_pauli(0, X)
    
    # Central coupling
    if gx != 0:
        H += gx * full_pauli(0, X) @ full_pauli(1, X)
    
    # Detector transverse field
    for j in range(1, ntot):
        H += hz * full_pauli(j, Z)
    
    # Detector NN XX coupling
    for j in range(1, n):  # j=1..N-1 means bonds (1,2),...,(N-1,N)
        H += j1x * full_pauli(j, X) @ full_pauli(j+1, X)
    
    return H


def build_full_majorana(n):
    """Build all 2(N+1) Majorana operators for the full system.
    
    For site s = 0, 1, ..., N (qubit is site 0):
    gamma_{2s} = (prod_{j<s} Z_j) X_s  ("a" type)
    gamma_{2s+1} = (prod_{j<s} Z_j) Y_s ("b" type)
    """
    ntot = n + 1
    gammas = []
    for s in range(ntot):
        # a-type: (prod Z) X
        ops_a = [I2] * ntot
        for j in range(s):
            ops_a[j] = Z
        ops_a[s] = X
        gammas.append(kron_list(ops_a))
        
        # b-type: (prod Z) Y
        ops_b = [I2] * ntot
        for j in range(s):
            ops_b[j] = Z
        ops_b[s] = Y
        gammas.append(kron_list(ops_b))
    
    return gammas


def full_majorana_coupling_matrix(n, hz, j1x, gx, h0x=0):
    """Build the real antisymmetric matrix A such that H = -i/4 sum A_{jk} gamma_j gamma_k.
    
    H = h0x a_0 + gx (-i b_0 a_1) + hz sum(-i a_j b_j) + J1x sum(-i b_j a_{j+1})
    
    The quadratic terms are:
    gx X_0 X_1 = gx a_0 * (Z_0 X_1) = gx a_0 * (-i a_0 b_0)(prod ... ) ...
    
    Wait, this is getting complicated. Let me use the Majorana operators directly.
    
    From the subagent report:
    X_0 X_1 = -i b_0 a_1  (using a_0 = X_0, b_0 = Y_0 * ... wait)
    
    Let me re-derive from first principles.
    gamma_0 = X_0 (a_0), gamma_1 = Y_0 (b_0)
    gamma_2 = Z_0 X_1 (a_1), gamma_3 = Z_0 Y_1 (b_1)
    gamma_4 = Z_0 Z_1 X_2 (a_2), etc.
    
    Z_0 = -i gamma_0 gamma_1 = -i a_0 b_0
    Z_j = -i gamma_{2j} gamma_{2j+1} for j >= 1 also.
    
    X_0 X_1: X_0 = gamma_0 = a_0. X_1 = Z_0 * a_1'... 
    Actually X_1 on the full space is the operator X acting on site 1, 
    but with the Jordan-Wigner string through site 0:
    X_1 = Z_0 * (X acting on site 1, identity elsewhere)
    Wait no. In the standard JW:
    c_1 = Z_0 sigma_1^-
    So X_1 in the spin representation is just X on site 1.
    But in the Majorana representation:
    gamma_{2*1} = Z_0 X_1 = a_1 (the a-type Majorana for site 1)
    gamma_{2*1+1} = Z_0 Y_1 = b_1
    
    So X_1 = Z_0 * gamma_2 = (-i gamma_0 gamma_1) * gamma_2
    This is a CUBIC Majorana term, not bilinear!
    
    Unless... X_0 X_1 = gamma_0 * Z_0 X_1 = gamma_0 * gamma_2 = a_0 * a_1.
    
    a_0 a_1 = gamma_0 gamma_2. Their anticommutator is 0 (different modes),
    so gamma_0 gamma_2 = -i * (something bilinear).
    
    Actually, in the Hamiltonian:
    X_0 X_1 = a_0 * (Z_0 X_1) = gamma_0 * gamma_2
    This IS bilinear in Majorana operators!
    
    gx X_0 X_1 = gx gamma_0 gamma_2
    
    And -i gamma_0 gamma_2 is a Hermitian bilinear. So:
    gx X_0 X_1 = gx gamma_0 gamma_2 = -i gx * (-i gamma_0 gamma_2)
    Hmm, let me be more careful.
    
    gamma_0 gamma_2 = a_0 a_1. As operators:
    (gamma_0 gamma_2)^dag = gamma_2^dag gamma_0^dag = gamma_2 gamma_0 = -gamma_0 gamma_2
    So gamma_0 gamma_2 is anti-Hermitian.
    
    X_0 X_1 = gamma_0 gamma_2 is anti-Hermitian? That can't be right since
    X_0 X_1 is Hermitian!
    
    Let me just verify numerically.
    """
    ntot = n + 1
    gammas = build_full_majorana(n)
    d = 2**ntot
    
    # Verify: is X_0 X_1 = gamma_0 gamma_2?
    X0X1 = kron_list([X if i == 0 else (X if i == 1 else I2) for i in range(ntot)])
    product_02 = gammas[0] @ gammas[2]
    err = np.max(np.abs(X0X1 - product_02))
    print(f"  X_0 X_1 == gamma_0 gamma_2? error = {err:.2e}")
    
    # Check Hermiticity
    print(f"  X_0 X_1 Hermitian? {np.allclose(X0X1, X0X1.conj().T)}")
    print(f"  gamma_0 gamma_2 Hermitian? {np.allclose(product_02, product_02.conj().T)}")
    
    # So X_0 X_1 IS gamma_0 gamma_2. Let me check:
    # gamma_0 = X_0 (real, symmetric), gamma_2 = Z_0 X_1 (real, symmetric)
    # (gamma_0 gamma_2)^T = gamma_2^T gamma_0^T = gamma_2 gamma_0 = -gamma_0 gamma_2
    # So gamma_0 gamma_2 is antisymmetric as a matrix, but...
    # As an operator, Hermitian conjugate: (AB)^dag = B^dag A^dag = BA (since self-adjoint)
    # But BA = -AB (anti-commuting), so (gamma_0 gamma_2)^dag = -gamma_0 gamma_2.
    # So it IS anti-Hermitian!
    
    # But X_0 X_1 should be Hermitian...
    # X_0 = sigma_x on site 0, X_1 = sigma_x on site 1.
    # X_0 X_1 = (X ⊗ X ⊗ I ⊗ ...) is clearly Hermitian.
    
    # The confusion: gamma_0 = X_0 tensor I_rest, gamma_2 = Z_0 tensor X_1 tensor I_rest
    # gamma_0 gamma_2 = X_0 Z_0 tensor X_1 tensor I = (XZ) tensor X tensor I
    # XZ = [[0,1],[1,0]][[1,0],[0,-1]] = [[0,-1],[1,0]] = iY
    # So gamma_0 gamma_2 = iY_0 X_1 = i Y_0 X_1
    # This is i times a Hermitian operator, hence anti-Hermitian. ✓
    
    # But X_0 X_1 is NOT gamma_0 gamma_2!
    # X_0 X_1 = (X ⊗ X ⊗ I ⊗ ...) while gamma_0 gamma_2 = (iY ⊗ X ⊗ I ⊗ ...)
    # They are DIFFERENT operators.
    
    return None


# Let me redo the Majorana analysis correctly.
print("=== Correct Majorana identification ===\n")

for n in [2, 3]:
    ntot = n + 1
    d = 2**ntot
    gammas = build_full_majorana(n)
    
    # X_0 = sigma_x on site 0
    X0 = kron_list([X if i == 0 else I2 for i in range(ntot)])
    # X_1 = sigma_x on site 1
    X1 = kron_list([X if i == 1 else I2 for i in range(ntot)])
    # Z_0
    Z0 = kron_list([Z if i == 0 else I2 for i in range(ntot)])
    
    print(f"N={n} (ntot={ntot}):")
    print(f"  gamma_0 = a_0:")
    print(f"    == X_0? {np.allclose(gammas[0], X0)}")
    print(f"  gamma_1 = b_0:")
    print(f"    == Y_0? {np.allclose(gammas[1], kron_list([Y if i==0 else I2 for i in range(ntot)]))}")
    print(f"  gamma_2 = a_1:")
    print(f"    == Z_0 X_1? {np.allclose(gammas[2], Z0 @ X1)}")
    
    # So X_1 = Z_0^{-1} gamma_2 = Z_0 gamma_2 (since Z_0^2 = I)
    #        = (-i gamma_0 gamma_1) gamma_2
    # And X_0 X_1 = gamma_0 (-i gamma_0 gamma_1) gamma_2
    #             = -i gamma_0^2 gamma_1 gamma_2
    #             = -i gamma_1 gamma_2
    #             = -i b_0 a_1
    
    X0X1 = X0 @ X1
    minus_i_b0_a1 = -1j * gammas[1] @ gammas[2]
    print(f"  X_0 X_1 == -i b_0 a_1? {np.allclose(X0X1, minus_i_b0_a1)}")
    
    # Good! So gx X_0 X_1 = -i gx gamma_1 gamma_2 = -i gx b_0 a_1
    # This IS bilinear in Majorana operators.
    
    # Similarly, Z_j for j>=1:
    # gamma_{2j} = (prod_{k<j} Z_k) X_j, gamma_{2j+1} = (prod_{k<j} Z_k) Y_j
    # Z_j = ... need to compute in terms of gammas
    # gamma_{2j} gamma_{2j+1} = (prod Z_k) X_j (prod Z_k) Y_j = X_j Y_j = iZ_j
    # So Z_j = -i gamma_{2j} gamma_{2j+1}
    
    for j in range(ntot):
        Zj = kron_list([Z if i == j else I2 for i in range(ntot)])
        minus_i_aj_bj = -1j * gammas[2*j] @ gammas[2*j+1]
        ok = np.allclose(Zj, minus_i_aj_bj)
        if j <= 2:
            print(f"  Z_{j} == -i gamma_{2*j} gamma_{2*j+1}? {ok}")
    
    # X_j X_{j+1} for detector:
    # X_j = (prod_{k<j} Z_k) gamma_{2j}^{-string} ... 
    # Actually X_j X_{j+1}:
    # In terms of JW fermions: c_j = (prod Z_k) sigma_j^-
    # X_j X_{j+1} = ... from the subagent: = -i gamma_{2j+1} gamma_{2(j+1)} = -i b_j a_{j+1}
    # Wait, the subagent says:
    # X_i X_{i+1} = -i gamma_{2i} gamma_{2i+1} ... no, that's Z_i.
    # Actually: gamma_{2i} gamma_{2i+1} = (prod Z)(X_i)(prod Z)(Y_i) = X_i Y_i = i Z_i
    # And: gamma_{2i+1} gamma_{2(i+1)} = (prod Z)(Y_i)(prod Z up to i)(X_{i+1})
    #     = Y_i Z_i X_{i+1} = (i X_i)(X_{i+1})... 
    # Hmm let me just verify.
    
    for j in range(1, n):  # detector bonds (j, j+1), j=1..N-1
        Xj = kron_list([X if i == j else I2 for i in range(ntot)])
        Xjp1 = kron_list([X if i == j+1 else I2 for i in range(ntot)])
        XjXjp1 = Xj @ Xjp1
        
        # Try -i gamma_{2j+1} gamma_{2(j+1)}
        candidate = -1j * gammas[2*j+1] @ gammas[2*(j+1)]
        ok = np.allclose(XjXjp1, candidate)
        if j <= 2:
            print(f"  X_{j} X_{j+1} == -i gamma_{2*j+1} gamma_{2*(j+1)}? {ok}")
    
    # h0x X_0 = h0x gamma_0 = h0x a_0  (LINEAR, not bilinear!)
    # This is a linear Majorana term. When h0x != 0, the Hamiltonian has
    # a linear term and is NOT purely quadratic.
    
    print(f"  X_0 == gamma_0? {np.allclose(X0, gammas[0])}")
    print(f"  -> h0x X_0 = h0x gamma_0 is LINEAR (not bilinear)!")
    
    print()


print("=== Full Hamiltonian in Majorana form (h0x=0) ===\n")
print("H = gx(-i gamma_1 gamma_2) + hz sum_j(-i gamma_{2j} gamma_{2j+1})")
print("  + J1x sum_j(-i gamma_{2j+1} gamma_{2(j+1)})")
print()
print("All terms are bilinear! gamma_0 = a_0 = X_0 doesn't appear -> conserved.")
print("The coupling matrix A is (2N+2) x (2N+2) antisymmetric, but the a_0 row/col is zero.")
print("Effective: (2N+1) x (2N+1) antisymmetric on {b_0, a_1, b_1, ..., a_N, b_N}.")
print()

# Now build the antisymmetric coupling matrix and verify
print("=== Build and verify coupling matrix A ===\n")

def build_coupling_matrix(n, hz, j1x, gx):
    """Build the (2N+2) x (2N+2) real antisymmetric matrix A such that
    H = (-i/4) sum_{j,k} A_{jk} gamma_j gamma_k.
    
    Actually H = -i sum_{j<k} A_{jk} gamma_j gamma_k / 2 with A antisymmetric.
    Or equivalently H = sum_{j<k} A_{jk} (-i gamma_j gamma_k / 2).
    
    Let me use the convention: H = -i/4 sum_{j,k} A_{jk} gamma_j gamma_k
    where A is antisymmetric. Then for each bilinear -i c gamma_a gamma_b (a<b):
    We need -i/4 (A_{ab} gamma_a gamma_b + A_{ba} gamma_b gamma_a) 
          = -i/4 (A_{ab} - A_{ba}) gamma_a gamma_b (using anticommutation)
          = -i/2 A_{ab} gamma_a gamma_b
    
    So if H contains a term -i c gamma_a gamma_b, then A_{ab} = 2c, A_{ba} = -2c.
    
    Our terms:
    gx X_0 X_1 = -i gx gamma_1 gamma_2  -> A[1,2] = 2gx, A[2,1] = -2gx
    hz Z_j     = -i hz gamma_{2j} gamma_{2j+1} -> A[2j,2j+1] = 2hz
    J1x X_j X_{j+1} = -i J1x gamma_{2j+1} gamma_{2(j+1)} -> A[2j+1,2j+2] = 2J1x
    """
    ntot = n + 1
    m = 2 * ntot  # 2(N+1) Majorana modes
    A = np.zeros((m, m))
    
    # gx coupling: -i gx gamma_1 gamma_2
    A[1, 2] = 2 * gx
    A[2, 1] = -2 * gx
    
    # hz transverse field on all spins (including qubit! No - only detector)
    for j in range(1, ntot):  # detector sites 1..N
        A[2*j, 2*j+1] = 2 * hz
        A[2*j+1, 2*j] = -2 * hz
    
    # J1x NN XX coupling on detector
    for j in range(1, n):  # bonds (j, j+1)
        A[2*j+1, 2*(j+1)] = 2 * j1x
        A[2*(j+1), 2*j+1] = -2 * j1x
    
    return A


for n in [2, 3, 4]:
    gx, hz, j1x = 0.3, 1.0, 0.5
    A = build_coupling_matrix(n, hz, j1x, gx)
    
    # Verify: reconstruct H from A
    ntot = n + 1
    d = 2**ntot
    gammas = build_full_majorana(n)
    m = 2 * ntot
    
    H_from_A = np.zeros((d, d), dtype=complex)
    for j in range(m):
        for k in range(m):
            if A[j, k] != 0:
                H_from_A += (-1j / 4) * A[j, k] * gammas[j] @ gammas[k]
    
    H_direct = build_full_system(n, hz, j1x, gx)
    err = np.max(np.abs(H_from_A - H_direct))
    print(f"  N={n}: H reconstruction error = {err:.2e}")
    
    # Verify antisymmetry
    assert np.allclose(A, -A.T), f"A not antisymmetric at N={n}"
    
    # Check row 0 (gamma_0 = a_0 = X_0)
    assert np.allclose(A[0, :], 0) and np.allclose(A[:, 0], 0), "a_0 not decoupled"
    print(f"         gamma_0 (=X_0) decoupled: True")
    print(f"         A shape: {A.shape}, nonzero A[0,:] count: {np.count_nonzero(A[0,:])}")


print("\n=== Free-fermion time evolution ===\n")

def majorana_evolution_matrix(A, t):
    """For H = -i/4 sum A gamma gamma, the Heisenberg evolution is:
    gamma_j(t) = sum_k R_{jk}(t) gamma_k
    where R(t) = exp(A t / 2) ... let me derive.
    
    d gamma_j / dt = i[H, gamma_j] = i(-i/4) sum_{k,l} A_{kl} [gamma_k gamma_l, gamma_j]
    [gamma_k gamma_l, gamma_j] = gamma_k {gamma_l, gamma_j} - {gamma_k, gamma_j} gamma_l
                                = 2 delta_{lj} gamma_k - 2 delta_{kj} gamma_l
    
    d gamma_j / dt = (1/4) sum_{k,l} A_{kl} (2 delta_{lj} gamma_k - 2 delta_{kj} gamma_l)
                   = (1/2) sum_k A_{kj} gamma_k - (1/2) sum_l A_{jl} gamma_l
                   = (1/2) sum_k (A_{kj} - A_{jk}) gamma_k    (A antisymmetric: A_{kj} = -A_{jk})
                   = sum_k A_{kj} gamma_k
    
    So d/dt gamma(t) = A gamma(t), giving gamma(t) = exp(At) gamma(0) = R(t) gamma(0).
    R(t) = exp(At).
    """
    return expm(A * t)

# Verify the rotation matrix
for n in [2, 3]:
    gx, hz, j1x = 0.3, 1.0, 0.5
    t = 1.0
    
    A = build_coupling_matrix(n, hz, j1x, gx)
    R = majorana_evolution_matrix(A, t)
    
    ntot = n + 1
    d = 2**ntot
    gammas = build_full_majorana(n)
    H = build_full_system(n, hz, j1x, gx)
    U = expm(-1j * H * t)
    m = 2 * ntot
    
    # Check gamma_j(t) = U^dag gamma_j U = sum_k R_{jk} gamma_k
    max_err = 0
    for j in range(m):
        evolved = U.conj().T @ gammas[j] @ U
        reconstructed = sum(R[j, k] * gammas[k] for k in range(m))
        err = np.max(np.abs(evolved - reconstructed))
        max_err = max(max_err, err)
    
    # Check R is orthogonal
    orth_err = np.max(np.abs(R @ R.T - np.eye(m)))
    
    print(f"  N={n}: rotation matrix error = {max_err:.2e}, orthogonality = {orth_err:.2e}")


print("\n=== Root moments via full free-fermion system ===\n")
print("Key question: express tau_det(W^ell) using full-system Majorana data.\n")

for n in [2, 3, 4, 5]:
    gx, hz, j1x = 0.3, 1.0, 0.5
    h0x = 0.0
    
    for t in [0.5, 1.0, 2.0]:
        ntot = n + 1
        d_full = 2**ntot
        d_det = 2**n
        
        # Direct: build W and compute moments
        H_det = np.zeros((d_det, d_det), dtype=complex)
        for i in range(n):
            ops = [I2] * n
            ops[i] = Z
            H_det += hz * kron_list(ops)
        for i in range(n-1):
            ops = [I2] * n
            ops[i] = X
            ops[i+1] = X
            H_det += j1x * kron_list(ops)
        
        X1_det = kron_list([X if i == 0 else I2 for i in range(n)])
        
        H_plus = H_det + gx * X1_det
        H_minus = H_det - gx * X1_det
        
        U_plus = expm(-1j * H_plus * t)
        U_minus = expm(-1j * H_minus * t)
        W = U_minus.conj().T @ U_plus
        
        moments_direct = []
        W_power = np.eye(d_det, dtype=complex)
        for ell in range(5):
            moments_direct.append(np.real(np.trace(W_power) / d_det))
            W_power = W_power @ W
        
        # Full system approach
        H_full = build_full_system(n, hz, j1x, gx, h0x)
        U_full = expm(-1j * H_full * t)
        
        # In the full system, the projector onto X_0 = +1 is P_+ = (I + X_0)/2
        X0_full = kron_list([X if i == 0 else I2 for i in range(ntot)])
        P_plus = (np.eye(d_full) + X0_full) / 2
        P_minus = (np.eye(d_full) - X0_full) / 2
        
        # W = U_-^dag U_+ acts on detector space
        # In the full space: U_full = P_+ U_+ + P_minus U_-
        # So: P_+ U_full P_+ = P_+ U_+ P_+ = P_+ * (P_+ U_+ P_+) 
        # Actually P_+ U_full = P_+ * (P_+ U_+ + P_- U_-) = U_+ P_+
        # since P_+ P_- = 0.
        # Similarly P_- U_full = U_- P_-
        
        # Then W = U_-^dag U_+ 
        # P_+ W_{embedded} P_+ = P_+ (U_- P_-)^dag (U_+ P_+) = ... 
        # Hmm this doesn't work nicely because U_- and U_+ live in different sectors.
        
        # Alternative: use detector parity echo
        # W = P_D U_+^dag P_D U_+ where P_D = prod Z_j (detector only)
        P_D_det = np.eye(d_det, dtype=complex)
        for i in range(n):
            ops = [I2] * n
            ops[i] = Z
            P_D_det = P_D_det @ kron_list(ops)
        
        W_echo = P_D_det @ U_plus.conj().T @ P_D_det @ U_plus
        echo_err = np.max(np.abs(W - W_echo))
        
        if t == 1.0:
            print(f"  N={n}, t={t}: moments = {[f'{m:.6f}' for m in moments_direct[:4]]}")
            print(f"                echo_err = {echo_err:.2e}")
    print()

print("=== Summary ===")
print("The endpoint chain with central-X coupling and XX+hz detector is:")
print("1. Quadratic in Majoranas for the FULL (qubit+detector) system")
print("2. NOT quadratic in the detector-only sector (H_pm has linear gamma_1 term)")
print("3. The relative unitary W = U_-^dag U_+ is NOT a Gaussian unitary")
print("4. Root moments tau(W^ell) cannot be computed from a simple cos formula")
print("5. But the full free-fermion structure may still help via Pfaffian formulas")
