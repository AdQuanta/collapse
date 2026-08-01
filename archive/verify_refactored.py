
import sys
import os

# Add the directory containing the original file to the python path
sys.path.append(r"c:\Users\matan\OneDrive - Technion\Graduate\Research\1 Projects\Collapse and Chaos\Code\Python\collapse")

import disentanglement
import matplotlib.pyplot as plt
import numpy as np
import time

def verify_refactored_code():
    print("Verifying refactored code...")
    
    N_star = 6 
    N = N_star + 1
    D = 2**N

    print("Generating central-spin Hamiltonian...")
    t0 = time.time()
    # New API usage
    generator = disentanglement.CentralSpinHamiltonian(N_star, Jx=1.0, Jz=1.0)
    H = generator.generate()
    t1 = time.time()
    print(f"Elapsed time for Hamiltonian generation: {t1 - t0} seconds")

    # Generate time evolution operator
    t = -1 
    print("Generating time evolution operator...")
    t0 = time.time()
    U = disentanglement.generate_time_evolution_operator(H, t)
    t1 = time.time()
    print(f"Elapsed time for time evolution operator generation: {t1 - t0} seconds")

    # Analyze disentanglement
    analyzer = disentanglement.DisentanglementAnalyzer(U)
    analyzer.diagonalize_sublocks_product(verbose=True)
    analyzer.get_initial_qubit_states_from_eigenvalues()
    
    print("Verification successful: Code runs without errors.")
    print(f"Analyzer output shape D0: {analyzer.D0.shape}")
    print(f"Analyzer output shape phi0: {analyzer.phi0.shape}")
    
    # Test Visualizer instantiation (headless, so no show)
    vis = disentanglement.DisentanglementVisualizer(analyzer)
    print("Visualizer instantiated successfully.")

if __name__ == "__main__":
    verify_refactored_code()
