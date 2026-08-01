"""
Verify correctness and benchmark the optimized pipeline against the original.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import numpy as np
from scipy.linalg import expm


# ---- Original (old) implementations ----
def old_generate_time_evolution_operator(H, t):
    return expm(-1j * H * t)


def old_diagonalize(U):
    N = U.shape[0]
    half = N // 2
    U00 = U[:half, :half]
    U01 = U[:half, half:]
    U10 = U[half:, :half]
    U11 = U[half:, half:]
    W0 = np.linalg.pinv(U00) @ U10
    W1 = np.linalg.pinv(U11) @ U01
    D0, V0 = np.linalg.eig(W0)
    D1, V1 = np.linalg.eig(W1)
    return D0, D1


def old_get_states(D0, D1):
    half = len(D0)
    phi0 = np.zeros((half, 2), dtype=np.complex128)
    phi1 = np.zeros((half, 2), dtype=np.complex128)
    norm0 = np.sqrt(1 + np.abs(D0) ** 2)
    norm1 = np.sqrt(1 + np.abs(D1) ** 2)
    phi0[:, 0] = 1.0 / norm0
    phi0[:, 1] = D0 / norm0
    phi1[:, 0] = D1 / norm1
    phi1[:, 1] = 1.0 / norm1
    return phi0, phi1


# ---- New (optimized) implementations ----
def new_generate_time_evolution_operator(E, V, t):
    return (V * np.exp(-1j * E * t)) @ V.conj().T


def new_diagonalize(U):
    N = U.shape[0]
    half = N // 2
    U00 = U[:half, :half]
    U10 = U[half:, :half]
    W0 = np.linalg.solve(U00, U10)
    D0 = np.linalg.eigvals(W0)
    D1 = -np.conj(D0)
    return D0, D1


def new_get_states(D0, D1):
    return old_get_states(D0, D1)  # same logic


def compare_z_distributions(z_old, z_new, label):
    """Compare sorted |z| distributions (eigenvalue ordering may differ)."""
    z_old_sorted = np.sort(z_old)
    z_new_sorted = np.sort(z_new)
    max_diff = np.max(np.abs(z_old_sorted - z_new_sorted))
    return max_diff


# ---- Build a realistic Hermitian Hamiltonian ----
np.random.seed(42)
N = 256
H = np.random.normal(size=(N, N)) + 1j * np.random.normal(size=(N, N))
H = H + H.conj().T  # Hermitian
times = [1.0, 10.0, 100.0]

print(f"=== Verification & Benchmark (N={N}, {len(times)} time points) ===\n")

# ---- Correctness ----
print("--- Correctness Check ---")
E, V = np.linalg.eigh(H)

for t in times:
    U_old = old_generate_time_evolution_operator(H, t)
    U_new = new_generate_time_evolution_operator(E, V, t)

    # Check U matrices are close
    u_diff = np.max(np.abs(U_old - U_new))
    print(f"  t={t:6.1f}  ||U_old - U_new||_max = {u_diff:.2e}", end="")

    # Check eigenvalues / z-distributions
    D0_old, D1_old = old_diagonalize(U_old)
    D0_new, D1_new = new_diagonalize(U_new)

    phi0_old, phi1_old = old_get_states(D0_old, D1_old)
    phi0_new, phi1_new = new_get_states(D0_new, D1_new)

    z0_old = np.abs(phi0_old[:, 0]) ** 2 - np.abs(phi0_old[:, 1]) ** 2
    z1_old = np.abs(phi1_old[:, 0]) ** 2 - np.abs(phi1_old[:, 1]) ** 2
    z0_new = np.abs(phi0_new[:, 0]) ** 2 - np.abs(phi0_new[:, 1]) ** 2
    z1_new = np.abs(phi1_new[:, 0]) ** 2 - np.abs(phi1_new[:, 1]) ** 2

    d0 = compare_z_distributions(z0_old, z0_new, "z0")
    d1 = compare_z_distributions(z1_old, z1_new, "z1")
    print(f"  |dz0|_max={d0:.2e}  |dz1|_max={d1:.2e}")

# ---- Benchmark ----
print("\n--- Full Pipeline Benchmark ---")

# Old pipeline
t0 = time.time()
for t in times:
    U = old_generate_time_evolution_operator(H, t)
    D0, D1 = old_diagonalize(U)
    phi0, phi1 = old_get_states(D0, D1)
    z0 = np.abs(phi0[:, 0]) ** 2 - np.abs(phi0[:, 1]) ** 2
    z1 = np.abs(phi1[:, 0]) ** 2 - np.abs(phi1[:, 1]) ** 2
elapsed_old = time.time() - t0
print(f"  Old pipeline: {elapsed_old:.4f} s")

# New pipeline
t0 = time.time()
E, V = np.linalg.eigh(H)  # one-time cost
for t in times:
    U = new_generate_time_evolution_operator(E, V, t)
    D0, D1 = new_diagonalize(U)
    phi0, phi1 = new_get_states(D0, D1)
    z0 = np.abs(phi0[:, 0]) ** 2 - np.abs(phi0[:, 1]) ** 2
    z1 = np.abs(phi1[:, 0]) ** 2 - np.abs(phi1[:, 1]) ** 2
elapsed_new = time.time() - t0
print(f"  New pipeline: {elapsed_new:.4f} s")
print(f"  Speedup:      {elapsed_old / elapsed_new:.2f}x")
