import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# Simulate notebook environment where current working directory is added
sys.path.append(os.getcwd())

try:
    import disentanglement as dis
    print("Successfully imported disentanglement module.")
except ImportError as e:
    print(f"Failed to import disentanglement: {e}")
    sys.exit(1)

# System Parameters
N_star = 4          
Jx_base = 1.0
Jz_base = 1.0
time_t = 1.0       
disorder_str = 0.5
seed = 42

disorder_types = ["uniform", "gaussian", "lorentzian"]

print("Starting notebook simulation...")

for dtype in disorder_types:
    print(f"\n--- Analyzing {dtype.capitalize()} Disorder ---")
    
    try:
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
        print(f"Generated Hamiltonian with shape {H_mat.shape}")
        
        # 2. Time Evolution U = exp(-iHt)
        print(f"Computing time evolution (t={time_t})...")
        U = expm(-1j * H_mat * time_t)
        
        # 3. Disentanglement Analysis
        print("Running Disentanglement Analyzer...")
        analyzer = dis.DisentanglementAnalyzer(U)
        analyzer.get_initial_qubit_states_from_eigenvalues()
        
        if analyzer.phi0 is None:
             print("ERROR: phi0 is None after analysis")
        else:
             print(f"Analysis successful. phi0 shape: {analyzer.phi0.shape}")
        
        # 4. Visualization
        print("Initializing Visualizer...")
        visualizer = dis.DisentanglementVisualizer(analyzer)
        # Check if method exists
        if hasattr(visualizer, 'plot_z_histograms'):
            print("Visualizer has plot_z_histograms method.")
             # We trigger it but catch plot errors since we are headless
            try:
                visualizer.plot_z_histograms()
                print("plot_z_histograms executed successfully (in theory)")
            except Exception as e:
                # If it's just a display error, that's fine for script
                print(f"Plotting raised exception (expected in headless): {e}")
        else:
            print("ERROR: Visualizer MISSING plot_z_histograms method.")
            
    except Exception as e:
        print(f"CRITICAL ERROR during {dtype} processing: {e}")
        import traceback
        traceback.print_exc()

print("\nNotebook simulation complete.")
