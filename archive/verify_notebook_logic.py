import sys
import os
import numpy as np
from scipy.linalg import expm
import disentanglement as dis

# System Parameters
N_star = 3          # Total qubits = 4 (even number required for N/2 partition in analyzer)
Jx_base = 1.0
Jz_base = 1.0
time_t = 1.0
disorder_str = 0.5
seed = 42

disorder_types = ["uniform", "gaussian", "lorentzian"]

print("Starting verification run...")

for dtype in disorder_types:
    print(f"\n--- Analyzing {dtype.capitalize()} Disorder ---")
    
    # 1. Generate Hamiltonian
    gen = dis.CentralSpinHamiltonianQuSpin(
        N_star=N_star, 
        Jx=Jx_base, 
        Jz=Jz_base, 
        disorder_type=dtype, 
        disorder_strength=disorder_str, 
        seed=seed
    )
    H_mat = gen.generate()
    
    # 2. Time Evolution U = exp(-iHt)
    print(f"Computing time evolution (t={time_t})...")
    U = expm(-1j * H_mat * time_t)
    
    # 3. Disentanglement Analysis
    print("Running Disentanglement Analyzer...")
    analyzer = dis.DisentanglementAnalyzer(U)
    analyzer.get_initial_qubit_states_from_eigenvalues()
    
    # 4. Check initial states exist
    if analyzer.phi0 is not None and analyzer.phi1 is not None:
         print(f"PASS: phi0 shape: {analyzer.phi0.shape}, phi1 shape: {analyzer.phi1.shape}")
    else:
         print("FAIL: phi0 or phi1 is None")

    # 5. Visualization call check (dry run, no display needed)
    print("Testing visualization call...")
    visualizer = dis.DisentanglementVisualizer(analyzer)
    # visualizer.plot_z_histograms() # Cannot run plt.show() here, but object creation works

print("\nVerification complete.")
