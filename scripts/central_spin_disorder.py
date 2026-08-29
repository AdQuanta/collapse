"""
Central Spin Model with Disorder — Example Script
===================================================

Demonstrates the full analysis pipeline:

1. Build a central-spin Hamiltonian with Lorentzian disorder.
2. Generate the time-evolution operator  U = exp(-i H t).
3. Analyse disentanglement: extract per-qubit initial states.
4. Visualise the results on the Bloch sphere, z-histograms,
   and the combined ratio+histogram plot.

Usage::

    python scripts/central_spin_disorder.py
"""

import sys
from pathlib import Path

# Ensure the project root is on the path so `core` is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time

import numpy as np

from core.analysis import DisentanglementAnalyzer
from core.hamiltonians import CentralSpinHamiltonianQuSpin
from core.quantum_utils import generate_time_evolution_operator
from core.visualization import DisentanglementVisualizer


def main() -> None:
    # ---- Configuration -------------------------------------------------
    N_star = 12  # Number of satellite qubits
    Jx = 0.0  # XX coupling strength
    Jz = 1.0  # ZZ coupling strength
    disorder_name = "lorentzian"  # "uniform", "gaussian", or "lorentzian"
    disorder_strength_Jx = 2.0 / N_star  # Disorder width in the x-direction
    disorder_strength_Jz = 0.0  # No disorder in z
    t_evolve = 1.0  # Evolution time
    seed = 421
    # --------------------------------------------------------------------

    N_total = N_star + 1
    D = 2**N_total

    print(f"=== Central Spin Model (N_star={N_star}, D={D}) ===")
    print(f"    Jx={Jx}, Jz={Jz}")
    print(
        f"    Disorder: {disorder_name}, "
        f"σ_Jx={disorder_strength_Jx}, σ_Jz={disorder_strength_Jz}"
    )
    print(f"    Seed: {seed}")
    print()

    # 1. Build Hamiltonian ------------------------------------------------
    print("1. Generating Hamiltonian...")
    t0 = time.time()
    ham_gen = CentralSpinHamiltonianQuSpin(
        N_star=N_star,
        Jx=Jx,
        Jz=Jz,
        disorder=disorder_name,
        disorder_strength_Jx=disorder_strength_Jx,
        disorder_strength_Jz=disorder_strength_Jz,
        seed=seed,
    )
    H = ham_gen.generate()
    print(
        f"   Done in {time.time() - t0:.2f}s  |  "
        f"shape={H.shape}, symmetric={np.allclose(H, H.T)}"
    )

    # 2. Time-evolution operator ------------------------------------------
    print("2. Computing U = exp(-i H t)...")
    t0 = time.time()
    U = generate_time_evolution_operator(H, t_evolve)
    print(
        f"   Done in {time.time() - t0:.2f}s  |  "
        f"unitary check: {np.allclose(U @ U.conj().T, np.eye(D))}"
    )

    # 3. Disentanglement analysis -----------------------------------------
    print("3. Running disentanglement analysis...")
    t0 = time.time()
    analyzer = DisentanglementAnalyzer(U)
    analyzer.diagonalize_subblocks_product(verbose=False)
    analyzer.get_initial_qubit_states_from_eigenvalues()
    print(
        f"   Done in {time.time() - t0:.2f}s  |  " f"phi0 shape={analyzer.phi0.shape}"
    )

    # 4. Visualisation ----------------------------------------------------
    print("4. Plotting results...\n")
    vis = DisentanglementVisualizer(analyzer)

    # vis.plot_bloch_sphere()
    # vis.plot_z_histograms()
    # vis.plot_z_histograms_ratio(bins=30)
    vis.plot_z_combined(bins=30, use_theta=True)

    print("Done.")


if __name__ == "__main__":
    main()
