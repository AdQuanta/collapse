import sys
import os
import numpy as np

# Ensure the local module is importable
sys.path.append(os.getcwd())

import disentanglement as dis

def test_disorder(N_star, disorder_type, disorder_strength, seed=42):
    print(f"Testing disorder_type='{disorder_type}', strength={disorder_strength}...")
    
    # Generate Hamiltonian with Numpy
    gen_np = dis.CentralSpinHamiltonianNumpy(
        N_star, Jx=1.0, Jz=1.0, 
        disorder_type=disorder_type, disorder_strength=disorder_strength, seed=seed
    )
    H_np = gen_np.generate()

    # Generate Hamiltonian with QuSpin
    gen_qs = dis.CentralSpinHamiltonianQuSpin(
        N_star, Jx=1.0, Jz=1.0, 
        disorder_type=disorder_type, disorder_strength=disorder_strength, seed=seed
    )
    H_qs = gen_qs.generate()

    # Compare
    if np.allclose(H_np, H_qs):
        print("  PASS: Numpy and QuSpin match.")
    else:
        print("  FAIL: Numpy and QuSpin do NOT match.")
        diff = np.linalg.norm(H_np - H_qs)
        print(f"  Diff norm: {diff}")
        return False

    # Check that disorder does something (if strength > 0)
    if disorder_strength > 0:
        # Generate with no disorder for comparison
        gen_clean = dis.CentralSpinHamiltonianNumpy(N_star, Jx=1.0, Jz=1.0)
        H_clean = gen_clean.generate()
        
        if not np.allclose(H_np, H_clean):
             print("  PASS: Disordered Hamiltonian is different from clean Hamiltonian.")
        else:
             print("  FAIL: Disordered Hamiltonian matches clean Hamiltonian (it shouldn't).")
             return False

        # Check seed reproducibility
        gen_np_2 = dis.CentralSpinHamiltonianNumpy(
            N_star, Jx=1.0, Jz=1.0, 
            disorder_type=disorder_type, disorder_strength=disorder_strength, seed=seed
        )
        H_np_2 = gen_np_2.generate()
        if np.allclose(H_np, H_np_2):
             print("  PASS: Seed produces reproducible results.")
        else:
             print("  FAIL: Seed does NOT produce reproducible results.")
             return False

        # Check different seed produces different results
        gen_np_3 = dis.CentralSpinHamiltonianNumpy(
            N_star, Jx=1.0, Jz=1.0, 
            disorder_type=disorder_type, disorder_strength=disorder_strength, seed=seed + 1
        )
        H_np_3 = gen_np_3.generate()
        if not np.allclose(H_np, H_np_3):
             print("  PASS: Different seeds produce different results.")
        else:
             print("  FAIL: Different seeds produce same results (unlikely).")
             return False

    return True

if __name__ == "__main__":
    N_star = 4
    
    # 1. No disorder
    print("\n--- Test 1: No Disorder ---")
    test_disorder(N_star, None, 0.0)

    # 2. Uniform Disorder
    print("\n--- Test 2: Uniform Disorder ---")
    test_disorder(N_star, "uniform", 0.1)

    # 3. Gaussian Disorder
    print("\n--- Test 3: Gaussian Disorder ---")
    test_disorder(N_star, "gaussian", 0.1)

    # 4. Lorentzian Disorder
    print("\n--- Test 4: Lorentzian Disorder ---")
    test_disorder(N_star, "lorentzian", 0.1)
