"""Verify the key Majorana operator identity Y(t)^2 = sigma^2(t) I.

This verifies the critical structural result for the endpoint chain:
because X_1 = gamma_1 is a single Majorana fermion, its time integral
Y(t) = integral_0^t X_1(s) ds is also a linear Majorana operator,
and hence Y(t)^2 is exactly proportional to the identity.

This script is a research verification, not a production tool.
"""
from __future__ import annotations

import sys
sys.path.insert(0, '.')

import numpy as np
from scipy.linalg import expm
from functools import reduce

# ── Build detector-only chain Hamiltonians ──

I2 = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron_list(ops):
    return reduce(np.kron, ops)

def det_pauli(n, site, op):
    factors = [I2] * n
    factors[site] = op
    return kron_list(factors)

def build_detector(n, hz, j1x):
    """D = hz sum Z_i + J1x sum X_i X_{i+1}, open BC, sites 0..N-1."""
    d = 2**n
    h = np.zeros((d, d), dtype=complex)
    for i in range(n):
        h += hz * det_pauli(n, i, Z)
    for i in range(n - 1):
        h += j1x * det_pauli(n, i, X) @ det_pauli(n, i+1, X)
    return h

def build_x1(n):
    """X at site 0 (detector site 1 in 1-indexed)."""
    return det_pauli(n, 0, X)

# ── Verify Y(t)^2 = sigma^2(t) I ──

def verify_y_squared_identity(n, hz, j1x, t, n_steps=200):
    """Verify that Y(t) = int_0^t X_1(s) ds satisfies Y(t)^2 = sigma^2(t) I."""
    D = build_detector(n, hz, j1x)
    X1 = build_x1(n)
    d = 2**n
    
    # Numerical integration of X_1(s) = e^{iDs} X_1 e^{-iDs}
    dt = t / n_steps
    Y = np.zeros((d, d), dtype=complex)
    for k in range(n_steps):
        s = (k + 0.5) * dt  # midpoint rule
        U = expm(-1j * D * s)
        X1_s = U.conj().T @ X1 @ U
        Y += X1_s * dt
    
    # Check Y^2 vs scalar * I
    Y2 = Y @ Y
    # Extract the scalar (should be sigma^2)
    sigma_sq = np.real(Y2[0, 0])
    residual = np.max(np.abs(Y2 - sigma_sq * np.eye(d)))
    
    # Also compute sigma^2 from single-particle formula
    h_sp = np.zeros((n, n))
    for i in range(n):
        h_sp[i, i] = -2 * hz
    for i in range(n - 1):
        h_sp[i, i+1] = j1x
        h_sp[i+1, i] = j1x
    
    evals, evecs = np.linalg.eigh(h_sp)
    weights = np.abs(evecs[0, :])**2  # |u_k(1)|^2
    
    # sigma^2(t) = sum_k w_k * 4 sin^2(eps_k t/2) / eps_k^2
    sigma_sq_sp = 0.0
    for ek, wk in zip(evals, weights):
        if abs(ek) < 1e-14:
            sigma_sq_sp += wk * t**2
        else:
            sigma_sq_sp += wk * 4 * np.sin(ek * t / 2)**2 / ek**2
    
    return sigma_sq, residual, sigma_sq_sp


def verify_conditional_unitary_root_moments(n, hz, j1x, gx, t, n_steps=200):
    """Verify that tau(W^ell) = cos(2*ell*gx*sigma(t)) for the endpoint chain.
    
    W = U_-^dag U_+, where H_pm = D +- gx X_1 +- a I (set a=0 for simplicity).
    """
    D = build_detector(n, hz, j1x)
    X1 = build_x1(n)
    d = 2**n
    
    H_plus = D + gx * X1
    H_minus = D - gx * X1
    
    U_plus = expm(-1j * H_plus * t)
    U_minus = expm(-1j * H_minus * t)
    
    W = U_minus.conj().T @ U_plus
    
    # Compute tau(W^ell) for several ell
    tau_W = []
    W_power = np.eye(d, dtype=complex)
    for ell in range(6):
        trace_val = np.trace(W_power) / d
        tau_W.append(trace_val)
        W_power = W_power @ W
    
    # Compute sigma(t) from single-particle
    h_sp = np.zeros((n, n))
    for i in range(n):
        h_sp[i, i] = -2 * hz
    for i in range(n - 1):
        h_sp[i, i+1] = j1x
        h_sp[i+1, i] = j1x
    
    evals, evecs = np.linalg.eigh(h_sp)
    weights = np.abs(evecs[0, :])**2
    
    sigma_sq = 0.0
    for ek, wk in zip(evals, weights):
        if abs(ek) < 1e-14:
            sigma_sq += wk * t**2
        else:
            sigma_sq += wk * 4 * np.sin(ek * t / 2)**2 / ek**2
    sigma = np.sqrt(sigma_sq)
    
    results = []
    for ell in range(6):
        predicted = np.cos(2 * ell * gx * sigma)
        actual = np.real(tau_W[ell])
        err = abs(predicted - actual)
        results.append((ell, actual, predicted, err))
    
    return results


if __name__ == '__main__':
    print("=== VERIFICATION 1: Y(t)^2 = sigma^2(t) I ===")
    print("  (the key operator identity for the Majorana endpoint chain)\n")
    
    all_ok = True
    for n in [2, 3, 4, 5, 6]:
        for hz, j1x in [(1.0, 0.5), (0.5, 1.0), (1.0, 1.0), (0.3, 0.7)]:
            for t in [0.5, 1.0, 2.0]:
                sig2, res, sig2_sp = verify_y_squared_identity(n, hz, j1x, t)
                sp_err = abs(sig2 - sig2_sp)
                ok = res < 1e-8 and sp_err < 1e-4
                if not ok or (n <= 3 and t == 1.0):
                    label = "OK" if ok else "FAIL"
                    print(f"  N={n}, hz={hz}, J1x={j1x}, t={t}: "
                          f"sigma^2={sig2:.6f}, |Y^2-sigma^2 I|={res:.2e}, "
                          f"sp_formula_err={sp_err:.2e} [{label}]")
                if not ok:
                    all_ok = False
    
    if all_ok:
        print("  ALL PASSED\n")
    else:
        print("  SOME FAILED\n")
    
    print("=== VERIFICATION 2: tau(W^ell) = cos(2*ell*gx*sigma(t)) ===")
    print("  (the exact root moments for the interacting endpoint chain)\n")
    
    all_ok2 = True
    for n in [2, 3, 4, 5]:
        for hz, j1x, gx in [(1.0, 0.5, 0.3), (0.5, 1.0, 0.5), (1.0, 1.0, 0.1)]:
            for t in [0.5, 1.0, 2.0, 5.0]:
                results = verify_conditional_unitary_root_moments(n, hz, j1x, gx, t)
                max_err = max(r[3] for r in results)
                ok = max_err < 1e-8
                if not ok or (n == 3 and t == 1.0):
                    label = "OK" if ok else "FAIL"
                    print(f"  N={n}, hz={hz}, J1x={j1x}, gx={gx}, t={t}: max_err={max_err:.2e} [{label}]")
                    if not ok or n == 3:
                        for ell, actual, predicted, err in results:
                            print(f"    ell={ell}: actual={actual:.8f}, predicted={predicted:.8f}, err={err:.2e}")
                if not ok:
                    all_ok2 = False
    
    if all_ok2:
        print("  ALL PASSED\n")
    else:
        print("  SOME FAILED\n")
    
    print("=== VERIFICATION 3: Cesaro behavior in two phases ===")
    print("  Paramagnetic (hz > J1x): sigma(t) saturates")
    print("  Topological (J1x > hz): sigma(t) ~ sqrt(w0) t\n")
    
    n = 8
    
    for label, hz, j1x in [("Paramagnetic", 1.0, 0.5), ("Critical", 1.0, 1.0), ("Topological", 0.5, 1.0)]:
        h_sp = np.zeros((n, n))
        for i in range(n):
            h_sp[i, i] = -2 * hz
        for i in range(n - 1):
            h_sp[i, i+1] = j1x
            h_sp[i+1, i] = j1x
        
        evals, evecs = np.linalg.eigh(h_sp)
        weights = np.abs(evecs[0, :])**2
        
        print(f"  {label} phase: hz={hz}, J1x={j1x}")
        print(f"    Smallest |eps|: {min(abs(evals)):.6e}")
        if j1x > hz:
            w0 = 1 - (hz/j1x)**2
            print(f"    Expected w0 = 1 - (hz/J1x)^2 = {w0:.6f}")
        
        times = [1, 10, 100, 1000]
        for t in times:
            sigma_sq = 0.0
            for ek, wk in zip(evals, weights):
                if abs(ek) < 1e-14:
                    sigma_sq += wk * t**2
                else:
                    sigma_sq += wk * 4 * np.sin(ek * t / 2)**2 / ek**2
            sigma = np.sqrt(sigma_sq)
            print(f"    t={t:6d}: sigma={sigma:.6f}, sigma/t={sigma/t:.6f}")
        print()
    
    print("=== VERIFICATION 4: Single-particle spectrum boundary mode ===\n")
    for n in [10, 20, 50, 100]:
        hz, j1x = 0.5, 1.0  # topological phase
        h_sp = np.zeros((n, n))
        for i in range(n):
            h_sp[i, i] = -2 * hz
        for i in range(n - 1):
            h_sp[i, i+1] = j1x
            h_sp[i+1, i] = j1x
        
        evals, evecs = np.linalg.eigh(h_sp)
        weights = np.abs(evecs[0, :])**2
        
        # Sort by absolute energy
        order = np.argsort(np.abs(evals))
        smallest_eps = evals[order[0]]
        smallest_w = weights[order[0]]
        
        w0_exact = 1 - (hz/j1x)**2
        print(f"  N={n:4d}: smallest |eps| = {abs(smallest_eps):.6e}, "
              f"its weight = {smallest_w:.6f}, "
              f"w0_exact = {w0_exact:.6f}")
    
    print("\n=== DONE ===")
