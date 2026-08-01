from quspin.operators import hamiltonian, quantum_LinearOperator, ishamiltonian
from quspin.basis import spin_basis_1d
from quspin.tools.measurements import ent_entropy, diag_ensemble, obs_vs_time
from quspin.tools.misc import mean_level_spacing

from joblib import Parallel, delayed
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Set default plot parameters
plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Arial"

if __name__ == "__main__":
    # System parameters
    N_pixel = 5  # Number of spins in pixel
    lmbda_x = 1.3  # X component of qubit-pixel coupling
    lmbda_z = 0.3  # Z component of qubit-pixel coupling
    lmbda0 = 1.0 / N_pixel  # Inter-pixel coupling strength
    # times = np.linspace(-20, 20, 201)  # Time to evolve the system
    times = [1000]

    # Construct two-pixel Hamiltonian
    H, basis = construct_two_pixel_hamiltonian(N_pixel, lmbda_x, lmbda_z, lmbda0)

    # Perform exact diagonalization
    E, V = H.eigh()
    print("Exact diagonalization completed!")
