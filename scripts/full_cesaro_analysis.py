"""Correct Cesàro formula accounting for spectrum structure.

The Cesàro average of tau(W^ell) requires the FULL overlap matrix M
and the energy differences. The naive diagonal formula fails because
the off-diagonal overlaps M_{jk} contribute when summed.

For W = sum_{j,k} M_{jk}^2 e^{i(E_j-E_k)t}, the Cesàro of tau(W)
picks out E_j = E_k, giving sum_j M_{jj}^2 = sum p_j^2. WRONG!

Actually tau(W) = sum |M_{jk}|^2 e^{i(E_j-E_k)t} where we used
|j-> = P_D|j+>. Since M is real symmetric, M_{jk} = M_{kj}.

The Cesàro average of e^{i omega t} is delta_{omega,0}. For a
non-degenerate spectrum, this means j=k ONLY. But I need to check
what the correct formula is for W^ell by deriving it carefully.

Let me work in the |k+> eigenbasis of H_+.

W_{jk} = <j+|W|k+> = <j+|P_D U_+^dag P_D U_+|k+>
       = e^{-iE_kt} <j+|P_D (sum_m e^{iE_mt} |m+><m+|) P_D |k+>
       = e^{-iE_kt} sum_m e^{iE_mt} <j+|P_D|m+> <m+|P_D|k+>
       = e^{-iE_kt} sum_m e^{iE_mt} M_{jm} M_{mk}
       = e^{-iE_kt} [M^2 D(t)]_{jk}
where D(t) = diag(e^{iE_jt}).

Actually, M = P_D matrix in the eigenbasis, so M^2 = I (since P_D^2 = I).
This gives W_{jk} = e^{-iE_kt} D(t)_{jk} = e^{i(E_j-E_k)t} delta_{jk}.

WAIT: that would mean W is diagonal in the H_+ eigenbasis, which is wrong!

Let me recheck. M_{jk} = <j+|P_D|k+> where both |j+> and |k+> are
eigenstates of H_+. Now M^2 = <j+|P_D^2|k+> = <j+|k+> = delta_{jk}.
So M is an involution: M^2 = I. ✓

But W = P_D U_+^dag P_D U_+ is NOT U_+^dag U_+ = I.
The issue: W = P_D U_+^dag P_D U_+ where the MIDDLE P_D U_+ is
not the same as P_D applied before U_+.

Let me be very careful:
W = P_D * exp(it H_+) * P_D * exp(-it H_+)

In the H_+ eigenbasis {|k+>}:
exp(-it H_+)|k+> = e^{-iE_kt}|k+>
P_D|k+> = sum_m M_{mk} |m+>

So:
exp(it H_+) P_D exp(-it H_+) |k+> = exp(it H_+) P_D (e^{-iE_kt}|k+>)
= e^{-iE_kt} exp(it H_+) sum_m M_{mk} |m+>
= e^{-iE_kt} sum_m M_{mk} e^{iE_mt} |m+>

Then:
W|k+> = P_D * [e^{-iE_kt} sum_m M_{mk} e^{iE_mt} |m+>]
= e^{-iE_kt} sum_{m,l} M_{mk} e^{iE_mt} M_{lm} |l+>
= e^{-iE_kt} sum_l [sum_m M_{lm} M_{mk} e^{iE_mt}] |l+>
= e^{-iE_kt} sum_l [M D(t) M]_{lk} |l+>

So W = M D(t) M D(-t) in the eigenbasis (where D(t) = diag(e^{iE_jt})).

Since M^2 = I, this is a "similarity transform" of D(t) by M, then
multiplied by D(-t). Not diagonal.

W_{lk} = e^{-iE_kt} [M D(t) M]_{lk}
        = e^{-iE_kt} sum_m M_{lm} e^{iE_mt} M_{mk}
        = sum_m M_{lm} M_{mk} e^{i(E_m-E_k)t}

So: tau(W^ell) = (1/2^N) Tr(W^ell) = (1/2^N) sum_{k_1,...,k_ell}
  prod_{r=1}^ell W_{k_r, k_{r+1}} (cyclic: k_{ell+1} = k_1)

W_{k_r, k_{r+1}} = sum_{m_r} M_{k_r, m_r} M_{m_r, k_{r+1}} e^{i(E_{m_r}-E_{k_{r+1}})t}

The Cesàro average requires sum_r (E_{m_r} - E_{k_{r+1}}) = 0.

For non-degenerate spectrum and generic (incommensurate) energy differences,
the only solutions are m_r = k_{r+1} for all r. This gives:

b_ell = (1/2^N) sum_{k_1,...,k_ell} prod_r M_{k_r, k_{r+1}} M_{k_{r+1}, k_{r+1}}
      = (1/2^N) sum_{k_1,...,k_ell} prod_r M_{k_r, k_{r+1}} p_{k_{r+1}}
      = (1/2^N) Tr(A^ell) where A_{jk} = M_{jk} p_k.

Wait, that's exactly what I had before! Let me check why it's failing.

The issue might be near-degeneracies. Let me check the energy differences
more carefully.
"""
import numpy as np
from scipy.linalg import expm
from functools import reduce

I2 = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron_list(ops):
    return reduce(np.kron, ops)


def full_cesaro_analysis(n, hz, j1x, gx, T=1000, n_samples=5000, max_ell=8):
    d = 2**n
    
    # Build H_+
    H_det = np.zeros((d, d), dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; H_det += hz * kron_list(ops)
    for i in range(n-1):
        ops = [I2] * n; ops[i] = X; ops[i+1] = X; H_det += j1x * kron_list(ops)
    
    X1 = kron_list([X if i==0 else I2 for i in range(n)])
    H_p = H_det + gx * X1
    
    # Build P_D
    P_D = np.eye(d, dtype=complex)
    for i in range(n):
        ops = [I2] * n; ops[i] = Z; P_D = P_D @ kron_list(ops)
    
    # Eigendecompose
    evals, evecs = np.linalg.eigh(H_p.real)
    
    # Overlap matrix M_{jk} = <j+|P_D|k+>
    M = evecs.T @ P_D.real @ evecs
    
    # Check M^2 = I
    print(f"  M^2 = I check: {np.max(np.abs(M @ M - np.eye(d))):.2e}")
    
    # Check: W = M D(t) M D(-t) formula
    t_test = 1.7
    D = np.diag(np.exp(1j * evals * t_test))
    Dm = np.diag(np.exp(-1j * evals * t_test))
    W_formula = M @ D @ M @ Dm
    
    # Direct W
    H_m = H_det - gx * X1
    Up = expm(-1j * H_p * t_test)
    Um = expm(-1j * H_m * t_test)
    W_direct = Um.conj().T @ Up
    # Transform to eigenbasis
    W_eigenbasis = evecs.T @ W_direct @ evecs
    
    print(f"  W formula vs direct: {np.max(np.abs(W_formula - W_eigenbasis)):.2e}")
    
    # Now: ALL energy differences
    omega = evals[:, None] - evals[None, :]  # omega[m,k] = E_m - E_k
    
    # Near-zero frequencies
    omega_flat = omega.flatten()
    small = np.abs(omega_flat) < 0.1
    print(f"  Energy differences < 0.1: {np.sum(small)} out of {len(omega_flat)}")
    print(f"  Near-zero (< 0.01): {np.sum(np.abs(omega_flat) < 0.01)}")
    
    # For the Cesàro formula, we need all resonance conditions:
    # sum_r (E_{m_r} - E_{k_{r+1}}) = 0
    # For ell=1: E_{m_1} = E_{k_1}, so m_1 = k_1 (non-degenerate).
    # For ell=2: E_{m_1} - E_{k_2} + E_{m_2} - E_{k_1} = 0
    #            i.e., E_{m_1} + E_{m_2} = E_{k_1} + E_{k_2}
    
    # The issue: for ell=2, there may be OFF-DIAGONAL resonances where
    # E_{m_1} + E_{m_2} = E_{k_1} + E_{k_2} with m_1 != k_2 or m_2 != k_1.
    
    # These are "spectral sum resonances" and they're generically absent
    # for incommensurate spectra. But the XX chain has special structure!
    
    # Specifically, for the XX chain without coupling (gx=0), the spectrum
    # has exact additive structure: energies are sums of single-particle
    # energies. This creates many exact resonances.
    
    # With small gx, these resonances are split but remain closely spaced.
    # The Cesàro average at finite T doesn't fully resolve them.
    
    # Let me check: how many ell=2 resonances exist?
    # E_{m_1} + E_{m_2} = E_{k_1} + E_{k_2}
    sum_pairs = np.add.outer(evals, evals).flatten()  # all E_i + E_j
    sum_pairs_sorted = np.sort(sum_pairs)
    gaps = np.diff(sum_pairs_sorted)
    n_near = np.sum(gaps < 1e-6)
    print(f"  Number of near-degenerate E_i+E_j pairs (gap<1e-6): {n_near}")
    
    # Exact Cesàro average using T-averaging, not the diagonal formula
    print(f"\n  Computing exact Cesàro by time-averaging (T={T}, samples={n_samples})...")
    dt = T / n_samples
    b_avg = np.zeros(max_ell)
    for k in range(n_samples):
        t = (k + 0.5) * dt
        D_t = np.diag(np.exp(1j * evals * t))
        D_mt = np.diag(np.exp(-1j * evals * t))
        W_t = M @ D_t @ M @ D_mt
        W_power = np.eye(d, dtype=complex)
        for ell in range(max_ell):
            b_avg[ell] += np.real(np.trace(W_power) / d) * dt
            W_power = W_power @ W_t
    b_avg /= T
    
    # Diagonal (non-degenerate) prediction
    pj = np.diag(M)
    b_diag = np.array([np.mean(pj**(2*ell)) for ell in range(max_ell)])
    # Actually for ell=1: b_1 = sum M_{jk}^2 * delta_{E_j,E_k} / 2^N
    # = sum_j M_{jj}^2 / 2^N (non-degenerate) = sum p_j^2 / 2^N ✓
    
    # The improved formula A = M * diag(p):
    A = M * pj[None, :]  # A_{jk} = M_{jk} * p_k
    b_A = np.array([np.real(np.trace(np.linalg.matrix_power(A, ell))) / d
                     for ell in range(max_ell)])
    
    print(f"\n  Results:")
    print(f"  {'ell':>3}  {'time_avg':>12}  {'diag_p^ell':>12}  {'Tr(A^ell)':>12}")
    for ell in range(1, max_ell):
        print(f"  {ell:3d}  {b_avg[ell]:12.8f}  {b_diag[ell]:12.8f}  {b_A[ell]:12.8f}")
    
    return b_avg, b_diag, b_A, M, evals


if __name__ == '__main__':
    print("=== Full Cesàro analysis: paramagnetic case ===\n")
    b, bd, bA, M, E = full_cesaro_analysis(5, 1.0, 0.5, 0.3, T=2000, n_samples=5000)
    
    print("\n=== Full Cesàro analysis: topological case ===\n")
    b2, bd2, bA2, M2, E2 = full_cesaro_analysis(5, 0.5, 1.0, 0.3, T=2000, n_samples=5000)
    
    print("\n=== Full Cesàro analysis: gx=0 check (should give delta_0, all b=1) ===\n")
    b3, bd3, bA3, M3, E3 = full_cesaro_analysis(4, 1.0, 0.5, 0.0, T=200, n_samples=1000)
    
    print("\n=== Eigenvalue pair structure in paramagnetic case ===\n")
    print("Energy levels and their P_D expectations:")
    n = 5
    E_sorted = np.sort(E)
    M_in_order = M[np.argsort(E)][:, np.argsort(E)]
    pj_sorted = np.diag(M_in_order)
    for j in range(min(16, len(E_sorted))):
        print(f"  E_{j} = {E_sorted[j]:10.6f}, p_j = {pj_sorted[j]:8.5f}")
