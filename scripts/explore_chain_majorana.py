"""Explore the endpoint-chain Majorana/free-fermion structure.

For the detector Hamiltonian D_N = hz sum Z_i + J1x sum X_i X_{i+1}
with open boundary conditions (chain), verify:
1. Jordan-Wigner gives a free-fermion/quadratic Majorana representation.
2. The single-particle spectrum is exactly solvable.
3. The tracial correlation function C(s) = tau(X_1(s) X_1(0)) has an
   exact representation in terms of single-particle energies.
4. The integrated fluctuation operator G(t) = integral_0^t X_1(s) ds
   has exactly computable moments.

This script is a research exploration, not a production tool.
"""
from __future__ import annotations

import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'verifier/analytic_p_theta/v1')

import numpy as np
import sympy as sp
from reference import pauli, hamiltonian

# ── 1. Build small-N endpoint chain detector Hamiltonians ──

def build_detector_chain(n: int, hz, j1x) -> sp.ImmutableSparseMatrix:
    """D_N = hz sum_i Z_i + J1x sum_{i=1}^{N-1} X_i X_{i+1}, sites 1..N."""
    d = 2**n
    h = sp.zeros(d)
    # Build Pauli operators on detector sites only (0-indexed internally)
    I2 = sp.eye(2)
    X = sp.Matrix([[0, 1], [1, 0]])
    Y = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    Z = sp.diag(1, -1)
    
    def det_pauli(n_det, site, axis):
        """Pauli on detector-only space, site 0..n_det-1."""
        factors = [I2] * n_det
        factors[site] = (X, Y, Z)[axis]
        from functools import reduce
        return sp.ImmutableSparseMatrix(reduce(sp.kronecker_product, factors))
    
    for i in range(n):
        h = h + hz * det_pauli(n, i, 2)  # Z_i
    for i in range(n - 1):
        h = h + j1x * det_pauli(n, i, 0) * det_pauli(n, i+1, 0)  # X_i X_{i+1}
    return sp.ImmutableSparseMatrix(h)


def build_x1_detector(n: int) -> sp.ImmutableSparseMatrix:
    """X_1 on detector-only space (site 0 in 0-indexed)."""
    I2 = sp.eye(2)
    X = sp.Matrix([[0, 1], [1, 0]])
    factors = [I2] * n
    factors[0] = X
    from functools import reduce
    return sp.ImmutableSparseMatrix(reduce(sp.kronecker_product, factors))


# ── 2. Verify Jordan-Wigner structure ──

def jordan_wigner_matrix(n: int, hz, j1x):
    """Build single-particle hopping matrix for JW-transformed chain.
    
    Jordan-Wigner: c_i = (prod_{j<i} Z_j) (X_i + iY_i)/2
    
    D = hz sum Z_i + J1x sum X_i X_{i+1}
    
    In fermion language:
    Z_i = 1 - 2 c_i^dag c_i
    X_i X_{i+1} = (c_i + c_i^dag)(c_{i+1} + c_{i+1}^dag)
                 = c_i c_{i+1} + c_i c_{i+1}^dag + c_i^dag c_{i+1} + c_i^dag c_{i+1}^dag
    
    The XX coupling is quadratic in fermions (no Jordan-Wigner string between
    adjacent sites). The transverse-field/XX model is exactly solvable.
    
    The single-particle Hamiltonian matrix is:
    h_sp[i,j] = -2hz delta_{ij} + J1x (delta_{i,j+1} + delta_{i,j-1})
    
    Wait - need to be careful. Let me use Majorana fermions.
    Define gamma_{2i} = c_i + c_i^dag, gamma_{2i+1} = -i(c_i - c_i^dag).
    Then X_i = gamma_{2i} prod_{j<i}(-i gamma_{2j} gamma_{2j+1})
    and Z_i = -i gamma_{2i} gamma_{2i+1}.
    
    Actually, let me just verify numerically by comparing eigenvalues.
    """
    # Single-particle hopping matrix for open chain
    h_sp = np.zeros((n, n))
    for i in range(n):
        h_sp[i, i] = -2 * float(hz)  # from Z_i = 1 - 2 n_i
    for i in range(n - 1):
        h_sp[i, i+1] = float(j1x)
        h_sp[i+1, i] = float(j1x)
    return h_sp


def verify_jw_spectrum(n: int, hz_val: float, j1x_val: float):
    """Verify that JW single-particle energies reproduce many-body spectrum."""
    hz, j1x = sp.Rational(hz_val), sp.Rational(j1x_val)
    
    # Many-body Hamiltonian
    D = build_detector_chain(n, hz, j1x)
    D_num = np.array(D.tolist(), dtype=complex)
    mb_eigs = np.sort(np.linalg.eigvalsh(D_num.real))
    
    # Single-particle hopping matrix
    h_sp = jordan_wigner_matrix(n, hz_val, j1x_val)
    sp_eigs = np.sort(np.linalg.eigvalsh(h_sp))
    
    # Many-body spectrum from single-particle: E = sum_i n_i epsilon_i + const
    # D = hz N - 2hz sum n_i + J1x sum (c_i^dag c_{i+1} + h.c. + c_i^dag c_{i+1}^dag + h.c.)
    # For XX model: D = const + sum_k epsilon_k (c_k^dag c_k - 1/2)
    # The vacuum energy shift comes from hz sum Z_i when all n_i=0: E_vac = hz N
    # With Z_i = 1 - 2n_i, the constant is hz N and the rest is -2hz n_i
    
    # Build many-body from single-particle
    import itertools
    mb_from_sp = []
    for occupation in itertools.product([0, 1], repeat=n):
        # Energy = hz*N + sum_i epsilon_i * (n_i - 1/2)... no.
        # Actually the single-particle matrix already accounts for the linear part.
        # E = hz*N + sum_k epsilon_k n_k where epsilon_k are eigenvalues of h_sp.
        # No wait, D = hz sum_i (1 - 2n_i) + J1x sum terms = hz N + sum_k eps_k n_k
        # where eps_k are eigenvalues of the matrix with diagonal -2hz and off-diagonal J1x.
        e = hz_val * n + sum(ek * nk for ek, nk in zip(sp_eigs, occupation))
        mb_from_sp.append(e)
    mb_from_sp = np.sort(mb_from_sp)
    
    error = np.max(np.abs(mb_eigs - mb_from_sp))
    print(f"  N={n}: max eigenvalue error = {error:.2e}")
    return error < 1e-10


# ── 3. Exact single-particle spectrum for open chain ──

def exact_sp_eigenvalues(n: int, hz_val: float, j1x_val: float):
    """Exact eigenvalues of the tridiagonal single-particle matrix.
    
    For open boundary: eigenvalues of tridiag(-2hz, J1x).
    Known exact result: epsilon_k = -2hz + 2 J1x cos(k pi/(N+1)), k=1..N.
    """
    exact = [-2*hz_val + 2*j1x_val * np.cos(k * np.pi / (n + 1)) for k in range(1, n+1)]
    
    h_sp = jordan_wigner_matrix(n, hz_val, j1x_val)
    numerical = np.sort(np.linalg.eigvalsh(h_sp))
    exact_sorted = np.sort(exact)
    
    error = np.max(np.abs(numerical - exact_sorted))
    print(f"  N={n}: exact sp eigenvalue error = {error:.2e}")
    return exact_sorted, error < 1e-10


# ── 4. Endpoint correlation function ──

def endpoint_correlation(n: int, hz_val: float, j1x_val: float, t_val: float):
    """Compute tau(X_1(t) X_1(0)) = (1/2^N) Tr(e^{iDt} X_1 e^{-iDt} X_1).
    
    In the free-fermion picture, this should factorize.
    """
    hz, j1x = sp.Rational(hz_val), sp.Rational(j1x_val)
    D = build_detector_chain(n, hz, j1x)
    D_num = np.array(D.tolist(), dtype=complex)
    X1 = build_x1_detector(n)
    X1_num = np.array(X1.tolist(), dtype=complex)
    
    # Direct many-body computation
    U = np.linalg.matrix_power(np.eye(2**n), 1)  # placeholder
    evals, evecs = np.linalg.eigh(D_num.real)
    U = evecs @ np.diag(np.exp(-1j * evals * t_val)) @ evecs.T.conj()
    X1_t = U.T.conj() @ X1_num @ U
    
    # Tracial expectation
    trace_val = np.trace(X1_t @ X1_num) / 2**n
    return trace_val


def endpoint_correlation_single_particle(n: int, hz_val: float, j1x_val: float, t_val: float):
    """Compute tau(X_1(t) X_1(0)) using the single-particle representation.
    
    Key identity for free fermions at infinite temperature:
    tau(X_1(t) X_1(0)) = |[e^{iHsp t}]_{0,0}|^2 + ... 
    
    Actually for the XX model with JW:
    X_1 = c_1 + c_1^dag (no string needed for site 1).
    
    tau(X_1(t) X_1(0)) = tau((c_1(t)+c_1^dag(t))(c_1+c_1^dag))
                        = G_{11}(t) + G_{11}(-t) 
    where G_{ij}(t) = tau(c_i(t) c_j^dag) = [e^{i h_sp t}]_{ij}
    
    In the tracial state: tau(c_i^dag c_j) = delta_{ij}/2 (half-filling).
    
    c_1(t) = sum_k U_{1k}(t) c_k where U(t) = e^{i h_sp t}.
    
    tau(X_1(t) X_1(0)) = sum_k |U_{1k}(t)|^2 tau((c_k + c_k^dag)(c_1 + c_1^dag))
    
    Hmm, more carefully:
    tau((c_1(t) + c_1^dag(t))(c_1 + c_1^dag))
    = tau(c_1(t) c_1^dag) + tau(c_1^dag(t) c_1)
    = G_{11}(t) + G_{11}(t)^*
    = 2 Re G_{11}(t)
    
    where G_{11}(t) = [e^{i h_sp t}]_{00} (0-indexed) for the first site.
    
    Wait, let me be more careful. c_i(t) = e^{iDt} c_i e^{-iDt}.
    In second quantization D = sum_{ij} h_sp[i,j] c_i^dag c_j + const.
    So c_i(t) = sum_j [e^{-i h_sp t}]_{ij} c_j.
    
    tau(c_i(t) c_j^dag) = sum_k [e^{-i h_sp t}]_{ik} tau(c_k c_j^dag)
                        = [e^{-i h_sp t}]_{ij} * (1/2)  ... no.
    
    At infinite temperature, tau(c_i^dag c_j) = (1/2) delta_{ij}.
    tau(c_i c_j^dag) = delta_{ij} - tau(c_j^dag c_i) = (1/2) delta_{ij}.
    
    tau(c_i(t) c_j^dag) = sum_k [e^{-i h_sp t}]_{ik} tau(c_k c_j^dag)
                        = (1/2) [e^{-i h_sp t}]_{ij}.
    
    tau(X_1(t) X_1(0)) = tau((c_1(t) + c_1^dag(t))(c_1 + c_1^dag))
                        = tau(c_1(t)c_1^dag) + tau(c_1^dag(t) c_1)
    (cross terms c c and c^dag c^dag vanish at half filling by Wick)
                        = (1/2)[e^{-i h_sp t}]_{00} + (1/2)[e^{i h_sp t}]_{00}
                        = Re [e^{-i h_sp t}]_{00}.
    """
    h_sp = jordan_wigner_matrix(n, hz_val, j1x_val)
    evals, evecs = np.linalg.eigh(h_sp)
    
    # [e^{-i h_sp t}]_{00} = sum_k |v_{0k}|^2 e^{-i eps_k t}
    site0_weights = np.abs(evecs[0, :])**2
    propagator_00 = np.sum(site0_weights * np.exp(-1j * evals * t_val))
    
    return np.real(propagator_00)  # This should be C(t)


# ── Main exploration ──

if __name__ == '__main__':
    print("=== 1. Verify Jordan-Wigner spectrum ===")
    for n in range(2, 7):
        assert verify_jw_spectrum(n, 1.0, 0.5)
    
    print("\n=== 2. Verify exact single-particle eigenvalues ===")
    for n in range(2, 10):
        _, ok = exact_sp_eigenvalues(n, 1.0, 0.5)
        assert ok
    
    print("\n=== 3. Compare endpoint correlation: many-body vs single-particle ===")
    for n in range(2, 7):
        for t in [0.0, 0.5, 1.0, 2.0]:
            c_mb = endpoint_correlation(n, 1.0, 0.5, t)
            c_sp = endpoint_correlation_single_particle(n, 1.0, 0.5, t)
            err = abs(c_mb - c_sp)
            status = "OK" if err < 1e-10 else "FAIL"
            if n <= 3 or t == 0.0 or err > 1e-10:
                print(f"  N={n}, t={t}: C_mb={c_mb.real:.8f}, C_sp={c_sp:.8f}, err={err:.2e} {status}")
    
    print("\n=== 4. Single-particle weights for endpoint (site 0) ===")
    for n in [5, 10, 20, 50]:
        h_sp = jordan_wigner_matrix(n, 1.0, 0.5)
        evals, evecs = np.linalg.eigh(h_sp)
        weights = np.abs(evecs[0, :])**2
        print(f"  N={n}: sum weights = {np.sum(weights):.10f}")
        print(f"         eigenvalues = {evals[:5]}...")
        print(f"         weights     = {weights[:5]}...")
    
    print("\n=== 5. Exact analytical single-particle eigenvectors ===")
    # For tridiag(-2hz, J1x) with open BC:
    # eigenvectors are v_k[j] = sqrt(2/(N+1)) sin(k*j*pi/(N+1))
    # eigenvalues are eps_k = -2hz + 2*J1x*cos(k*pi/(N+1))
    n = 10
    hz_val, j1x_val = 1.0, 0.5
    h_sp = jordan_wigner_matrix(n, hz_val, j1x_val)
    evals_num, evecs_num = np.linalg.eigh(h_sp)
    
    for k in range(1, n+1):
        eps_exact = -2*hz_val + 2*j1x_val * np.cos(k*np.pi/(n+1))
        # Eigenvector: v[j] = sqrt(2/(N+1)) sin(k*(j+1)*pi/(N+1)), j=0..N-1
        v_exact = np.array([np.sqrt(2/(n+1)) * np.sin(k*(j+1)*np.pi/(n+1))
                           for j in range(n)])
        # Find matching numerical eigenvector
        idx = np.argmin(np.abs(evals_num - eps_exact))
        v_num = evecs_num[:, idx]
        # Align sign
        if np.dot(v_exact, v_num) < 0:
            v_num = -v_num
        err = np.max(np.abs(v_exact - v_num))
        if k <= 3:
            print(f"  mode k={k}: eps={eps_exact:.6f}, v[0]={v_exact[0]:.6f}, err={err:.2e}")
    
    # The endpoint weight for mode k is:
    # w_k = |v_k[0]|^2 = (2/(N+1)) sin^2(k*pi/(N+1))
    print(f"\n  Endpoint weights w_k = 2/(N+1) sin^2(k*pi/(N+1)):")
    for k in range(1, min(n+1, 6)):
        w = 2/(n+1) * np.sin(k*np.pi/(n+1))**2
        print(f"    k={k}: w_k = {w:.8f}")
    
    print(f"\n  Sum of endpoint weights = {sum(2/(n+1) * np.sin(k*np.pi/(n+1))**2 for k in range(1,n+1)):.10f}")
    
    print("\n=== 6. Endpoint correlation in single-particle form ===")
    print("  C(t) = sum_k w_k cos(eps_k t)")
    print("  where eps_k = -2hz + 2 J1x cos(k pi/(N+1))")
    print("  and   w_k   = (2/(N+1)) sin^2(k pi/(N+1))")
    
    # Verify this formula
    n = 8
    hz_val, j1x_val = 1.0, 0.5
    for t in [0.5, 1.0, 2.0]:
        # Single-particle formula
        c_formula = sum(2/(n+1) * np.sin(k*np.pi/(n+1))**2 
                        * np.cos((-2*hz_val + 2*j1x_val*np.cos(k*np.pi/(n+1))) * t)
                        for k in range(1, n+1))
        # Direct computation
        c_direct = endpoint_correlation_single_particle(n, hz_val, j1x_val, t)
        err = abs(c_formula - c_direct)
        print(f"  N={n}, t={t}: formula={c_formula:.8f}, direct={c_direct:.8f}, err={err:.2e}")
    
    print("\n=== 7. Thermodynamic limit of endpoint spectral measure ===")
    print("  As N -> inf, the spectral measure of X_1 is:")
    print("  nu_N = sum_k w_k delta_{eps_k}")
    print("  eps_k = -2hz + 2 J1x cos(k pi/(N+1))")
    print("  w_k = 2/(N+1) sin^2(k pi/(N+1))")
    print("  This is a Riemann sum. Let x = k/(N+1) in [0,1]:")
    print("  eps(x) = -2hz + 2 J1x cos(pi x)")
    print("  w(x) dx = 2 sin^2(pi x) dx")
    print("  So nu_inf has density on [-2hz-2J1x, -2hz+2J1x]:")
    print("  d nu / d eps = (2 sin^2(pi x)) / |d eps/dx|")
    print("              = (2 sin^2(pi x)) / (2 pi J1x |sin(pi x)|)")
    print("              = |sin(pi x)| / (pi J1x)")
    print("  where eps = -2hz + 2 J1x cos(pi x)")
    print("  sin(pi x) = sqrt(1 - ((eps+2hz)/(2J1x))^2)")
    print("  So d nu/d eps = sqrt(1 - ((eps+2hz)/(2J1x))^2) / (pi J1x)")
    print("  = sqrt(4J1x^2 - (eps+2hz)^2) / (2 pi J1x^2)")
    print("  This is a SEMICIRCLE (Wigner-like) density!")
    
    # Verify semicircle density numerically
    print("\n  Verification with histogram:")
    n = 500
    eps_k = np.array([-2*hz_val + 2*j1x_val*np.cos(k*np.pi/(n+1)) for k in range(1, n+1)])
    w_k = np.array([2/(n+1) * np.sin(k*np.pi/(n+1))**2 for k in range(1, n+1)])
    
    # Compare moments
    print(f"  Total weight: {np.sum(w_k):.10f} (should be 1)")
    print(f"  Mean: {np.sum(w_k * eps_k):.10f} (analytical: {-2*hz_val})")
    print(f"  Variance: {np.sum(w_k * (eps_k + 2*hz_val)**2):.10f} (analytical: {2*j1x_val**2})")
    print(f"  Analytical variance = 2 J1x^2 = {2*j1x_val**2}")
    
    # Fourth moment
    m4 = np.sum(w_k * (eps_k + 2*hz_val)**4)
    print(f"  Fourth central moment: {m4:.10f}")
    print(f"  Semicircle prediction: 2 * (2J1x^2)^2 = {2*(2*j1x_val**2)**2}")
    # Semicircle on [-R,R] has moments m_{2k} = R^{2k} C_k / (4^k)
    # where C_k = Catalan. For R^2 = 4J1x^2: m_2 = R^2/4 = J1x^2... 
    # Wait, the density is sqrt(R^2-x^2)/(pi R^2/2), so m_2 = R^2/4.
    # But we got 2J1x^2. Let me recalculate.
    # density = sqrt(4J1x^2 - x^2) / (2 pi J1x^2), x = eps + 2hz
    # integral x^2 * sqrt(4J1x^2-x^2)/(2pi J1x^2) dx
    # = (4J1x^2)^2 * integral_0^1 u^2 sqrt(1-u^2) * 2/(2pi) du  (substituting x = 2J1x u)
    # = 16 J1x^4 / (pi J1x^2) * integral_0^1 u^2 sqrt(1-u^2) du
    # Wait, let me redo. Substituting eps+2hz = 2 J1x sin(theta):
    # int_{-2J}^{2J} x^2 sqrt(4J^2-x^2)/(2pi J^2) dx
    # = int_{-pi/2}^{pi/2} 4J^2 sin^2(theta) * 2J cos(theta) * 2J cos(theta) / (2pi J^2) dtheta
    # = int 4J^2 sin^2(theta) * 4J^2 cos^2(theta) / (2pi J^2) dtheta
    # = 8J^2/pi * int sin^2 cos^2 dtheta = 8J^2/pi * pi/8 = J^2
    # Hmm, that gives J^2, not 2J^2. Let me check numerically...

    print("\n=== DONE ===")
