
import sys
import os
import numpy as np

# Add the directory containing the original file to the python path
sys.path.append(r"c:\Users\matan\OneDrive - Technion\Graduate\Research\1 Projects\Collapse and Chaos\Code\Python\collapse")

import disentanglement as dis

def verify_quspin_optimization():
    print("Verifying QuSpin optimization...")
    
    # 1. Verify Central Spin Hamiltonian
    print("\n--- Verifying Central Spin Hamiltonian ---")
    N_star = 6
    gen_np = dis.CentralSpinHamiltonianNumpy(N_star, Jx=1.2, Jz=0.8)
    gen_qs = dis.CentralSpinHamiltonianQuSpin(N_star, Jx=1.2, Jz=0.8)
    
    H_np = gen_np.generate()
    H_qs = gen_qs.generate()
    
    if np.allclose(H_np, H_qs):
        print("PASS: Central Spin Hamiltonians match.")
    else:
        print("FAIL: Central Spin Hamiltonians do NOT match.")
        print(f"Max diff: {np.max(np.abs(H_np - H_qs))}")
        
    # 2. Verify Single Pixel Hamiltonian
    # Note: I haven't implemented SinglePixelHamiltonianQuSpin in the file yet, 
    # but I did implement it in the replace_file_content call.
    # Wait, I need to check if I actually added it. Yes I did.
    
    print("\n--- Verifying Single Pixel Hamiltonian ---")
    N_pixel = 4
    gen_np = dis.SinglePixelHamiltonianNumpy(N_pixel, J=1.0, Jx=0.5, Jz=0.3)
    gen_qs = dis.SinglePixelHamiltonianQuSpin(N_pixel, J=1.0, Jx=0.5, Jz=0.3)
    
    H_np = gen_np.generate()
    H_qs = gen_qs.generate()
    
    if np.allclose(H_np, H_qs):
        print("PASS: Single Pixel Hamiltonians match.")
    else:
        print("FAIL: Single Pixel Hamiltonians do NOT match.")
        print(f"Max diff: {np.max(np.abs(H_np - H_qs))}")

    # 3. Verify Two Pixel Hamiltonian
    print("\n--- Verifying Two Pixel Hamiltonian ---")
    N_pixel = 3
    # Use fixed seed or no disorder for direct comparison (disorder=False)
    gen_np = dis.TwoPixelHamiltonianNumpy(N_pixel, J=1.0, Jx=0.5, Jz=0.3, disorder=False)
    gen_qs = dis.TwoPixelHamiltonianQuSpin(N_pixel, J=1.0, Jx=0.5, Jz=0.3, disorder=False)
    
    H_np = gen_np.generate()
    H_qs = gen_qs.generate()
    
    if np.allclose(H_np, H_qs):
        print("PASS: Two Pixel Hamiltonians match.")
    else:
        print("FAIL: Two Pixel Hamiltonians do NOT match.")
        print(f"Max diff: {np.max(np.abs(H_np - H_qs))}")

    # 4. Verify Mixed Field Ising Hamiltonian
    print("\n--- Verifying Mixed Field Ising Hamiltonian ---")
    N = 6
    gen_np = dis.MixedFieldIsingHamiltonianNumpy(N, J=1.0, hx=0.5, hz=0.8)
    gen_qs = dis.MixedFieldIsingHamiltonianQuSpin(N, J=1.0, hx=0.5, hz=0.8)
    
    H_np = gen_np.generate()
    H_qs = gen_qs.generate()
    
    if np.allclose(H_np, H_qs):
        print("PASS: Mixed Field Ising Hamiltonians match.")
    else:
        print("FAIL: Mixed Field Ising Hamiltonians do NOT match.")
        print(f"Max diff: {np.max(np.abs(H_np - H_qs))}")

if __name__ == "__main__":
    verify_quspin_optimization()
