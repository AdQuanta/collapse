
import sys
import os

# Add the directory containing the original file to the python path
sys.path.append(r"c:\Users\matan\OneDrive - Technion\Graduate\Research\1 Projects\Collapse and Chaos\Code\Python\collapse")

import disentanglement
import matplotlib.pyplot as plt
import numpy as np
import time

def verify_original_code():
    print("Verifying original code...")
    
    # Using the same logic as the original __main__ block
    N_star = 6 # Reduced size for speed
    N = N_star + 1
    D = 2**N

    print("Generating central-spin Hamiltonian...")
    t0 = time.time()
    H = disentanglement.generate_central_qubit_hamiltonian(N_star, Jx=1.0, Jz=1.0)
    t1 = time.time()
    print(f"Elapsed time for Hamiltonian generation: {t1 - t0} seconds")

    # Generate time evolution operator
    t = -1  # Short time for speed
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

if __name__ == "__main__":
    verify_original_code()
