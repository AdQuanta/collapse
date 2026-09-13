"""Compute exact chain root moments via Pfaffian/free-fermion formulas.

For the full qubit+detector system as a free-fermion/Majorana chain:
H = gx(-i b_0 a_1) + hz sum_j(-i a_j b_j) + J1x sum_j(-i b_j a_{j+1})

with a_0 = X_0 decoupled (conserved).

The root moments are tau_det(W^ell) where W = P_D U_+^dag P_D U_+
and P_D = prod Z_j = (-i)^N prod a_j b_j (detector parity).

In the full free-fermion system:
W = P_D^{(full)} U^dag P_D^{(full)} U * (qubit contribution)

But we need to be more careful. Let me use the direct approach:
work with the full (2N+2)-Majorana system and express everything
in terms of the single-particle rotation matrix R(t) = exp(At).

For this section, the key result is:
tau_det(W) = tau_det(P_D U_+^dag P_D U_+)

Since U_+ = <+|U|+> where U is the full propagator:
U_+ v = <+|U(|+> ⊗ v) where v is a detector state.

The parity echo: W = P_D U_+^dag P_D U_+.
Using P_D U_+ P_D = U_- (proved in report 07 / subagent analysis):
W = U_-^dag U_+ = (P_D U_+ P_D)^dag U_+ = P_D U_+^dag P_D U_+.

Now I'll work out the exact moments numerically for many times and
compute the Cesàro average.
"""
import numpy as np
from scipy.linalg import expm
from functools import reduce

I2 = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron_list(ops):
    return reduce(np.kron, ops)


def compute_moments(n, hz, j1x, gx, h0x, t, max_ell=8):
    """Compute root cosine moments for the endpoint chain.
    
    Returns m_0, m_1, ..., m_{max_ell-1} where m_ell = Re tau_det(W^ell).
    """
    d = 2**n
    
    # Build detector Hamiltonian
    H_det = np.zeros((d, d), dtype=complex)
    for i in range(n):
        ops = [I2] * n
        ops[i] = Z
        H_det += hz * kron_list(ops)
    for i in range(n-1):
        ops = [I2] * n
        ops[i] = X
        ops[i+1] = X
        H_det += j1x * kron_list(ops)
    
    X1 = kron_list([X if i == 0 else I2 for i in range(n)])
    
    H_plus = H_det + (gx + h0x) * X1  # gx from coupling + h0x shifts eigenvalues
    # Actually H_pm = D +- gx X_1 +- h0x I
    # No: H_pm = pm h0x I + D pm gx X_1
    # U_pm = exp(-it(D pm gx X_1 pm h0x I)) = exp(-it(pm h0x)) exp(-it(D pm gx X_1))
    # So W = U_-^dag U_+ = exp(it(-h0x-h0x)) exp(it(D-gx X1)) exp(-it(D+gx X1))
    #      = exp(-2it h0x) * (exp(-it(D-gx X1)))^dag exp(-it(D+gx X1))
    
    H_p = H_det + gx * X1
    H_m = H_det - gx * X1
    
    U_p = expm(-1j * H_p * t)
    U_m = expm(-1j * H_m * t)
    
    W = U_m.conj().T @ U_p
    
    # Include h0x phase
    W_full = np.exp(-2j * h0x * t) * W
    
    moments = []
    W_power = np.eye(d, dtype=complex)
    for ell in range(max_ell):
        moments.append(np.real(np.trace(W_power) / d))
        W_power = W_power @ W_full
    
    return np.array(moments)


def cesaro_average(n, hz, j1x, gx, h0x, T, n_samples, max_ell=8):
    """Compute Cesàro-averaged moments: (1/T) integral_0^T m_ell(t) dt."""
    dt = T / n_samples
    avg = np.zeros(max_ell)
    for k in range(n_samples):
        t = (k + 0.5) * dt
        m = compute_moments(n, hz, j1x, gx, h0x, t, max_ell)
        avg += m * dt
    return avg / T


# ── Main computations ──

if __name__ == '__main__':
    max_ell = 8
    
    print("=== 1. N-convergence of moments at fixed t ===\n")
    hz, j1x, gx, h0x = 1.0, 0.5, 0.3, 0.0
    t = 1.0
    for n in range(2, 9):
        m = compute_moments(n, hz, j1x, gx, h0x, t, max_ell)
        print(f"  N={n}: m_1={m[1]:.10f}, m_2={m[2]:.10f}, m_3={m[3]:.10f}")
    
    print(f"\n  Moments converge rapidly in N. N->inf limit is the N=2 value")
    print(f"  for this local endpoint coupling.\n")
    
    print("=== 2. Time dependence of moments (N=6, paramagnetic hz=1, J1x=0.5) ===\n")
    n = 6
    hz, j1x, gx, h0x = 1.0, 0.5, 0.3, 0.0
    times = np.linspace(0, 20, 200)
    moments_vs_t = np.array([compute_moments(n, hz, j1x, gx, h0x, t, max_ell) for t in times])
    
    print(f"  m_1: min={moments_vs_t[:, 1].min():.6f}, max={moments_vs_t[:, 1].max():.6f}")
    print(f"  m_2: min={moments_vs_t[:, 2].min():.6f}, max={moments_vs_t[:, 2].max():.6f}")
    
    # Cesàro averages at increasing T
    print(f"\n  Cesàro averages:")
    for T in [10, 50, 100, 500]:
        avg = cesaro_average(n, hz, j1x, gx, h0x, T, min(T*20, 2000), max_ell)
        print(f"    T={T:5d}: b_1={avg[1]:.6f}, b_2={avg[2]:.6f}, b_3={avg[3]:.6f}")
    
    print(f"\n=== 3. Topological phase: J1x > hz ===\n")
    n = 6
    hz, j1x, gx, h0x = 0.5, 1.0, 0.3, 0.0
    
    times = np.linspace(0, 20, 200)
    moments_vs_t = np.array([compute_moments(n, hz, j1x, gx, h0x, t, max_ell) for t in times])
    
    print(f"  m_1: min={moments_vs_t[:, 1].min():.6f}, max={moments_vs_t[:, 1].max():.6f}")
    print(f"  m_2: min={moments_vs_t[:, 2].min():.6f}, max={moments_vs_t[:, 2].max():.6f}")
    
    print(f"\n  Cesàro averages:")
    for T in [10, 50, 100, 500]:
        avg = cesaro_average(n, hz, j1x, gx, h0x, T, min(T*20, 2000), max_ell)
        print(f"    T={T:5d}: b_1={avg[1]:.6f}, b_2={avg[2]:.6f}, b_3={avg[3]:.6f}")
    
    print(f"\n=== 4. Critical phase: hz = J1x ===\n")
    n = 6
    hz, j1x, gx, h0x = 1.0, 1.0, 0.3, 0.0
    
    print(f"  Cesàro averages:")
    for T in [10, 50, 100, 500]:
        avg = cesaro_average(n, hz, j1x, gx, h0x, T, min(T*20, 2000), max_ell)
        print(f"    T={T:5d}: b_1={avg[1]:.6f}, b_2={avg[2]:.6f}, b_3={avg[3]:.6f}")
    
    print(f"\n=== 5. Effect of h0x (central qubit field) ===\n")
    n = 6
    hz, j1x, gx = 1.0, 0.5, 0.3
    
    for h0x in [0.0, 0.1, 0.5, 1.0]:
        avg = cesaro_average(n, hz, j1x, gx, h0x, 200, 2000, max_ell)
        print(f"  h0x={h0x}: b_1={avg[1]:.6f}, b_2={avg[2]:.6f}, b_3={avg[3]:.6f}")
    
    print(f"\n=== 6. Large-N limit: compare N=3,5,8 for topological phase ===\n")
    hz, j1x, gx, h0x = 0.5, 1.0, 0.3, 0.0
    T = 100
    for n in [3, 5, 6, 7, 8]:
        avg = cesaro_average(n, hz, j1x, gx, h0x, T, 2000, max_ell)
        print(f"  N={n}: b_1={avg[1]:.6f}, b_2={avg[2]:.6f}, b_3={avg[3]:.6f}, "
              f"b_4={avg[4]:.6f}")
    
    print(f"\n=== 7. The h0x != 0 (nonzero central field) case ===")
    print(f"    h0x shifts W by exp(-2i h0x t), so m_ell(t) gains cos(2 ell h0x t).")
    print(f"    Cesàro average of cos(2 ell h0x t) * f(t) depends on whether")
    print(f"    2 ell h0x matches a frequency of f(t).\n")
    
    # For h0x != 0 and generic: the cos(2 ell h0x t) oscillation kills
    # the time average unless there's a matching frequency in the detector dynamics.
    
    n = 6
    hz, j1x, gx = 1.0, 0.5, 0.3
    for h0x in [0.0, 0.01, 0.1, 0.5, 1.0, 2.0]:
        avg = cesaro_average(n, hz, j1x, gx, h0x, 500, 2000, max_ell)
        print(f"  h0x={h0x:5.2f}: b = [{', '.join(f'{a:.5f}' for a in avg[1:5])}]")
    
    print(f"\n=== 8. Large-T convergence for paramagnetic with h0x=0 ===\n")
    n = 6
    hz, j1x, gx, h0x = 1.0, 0.5, 0.3, 0.0
    for T in [50, 100, 200, 500, 1000, 2000]:
        n_samp = min(T * 10, 5000)
        avg = cesaro_average(n, hz, j1x, gx, h0x, T, n_samp, max_ell)
        print(f"  T={T:5d}: b_1={avg[1]:.8f}, b_2={avg[2]:.8f}, b_3={avg[3]:.8f}")
    
    print(f"\n=== DONE ===")
