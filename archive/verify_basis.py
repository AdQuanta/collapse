from quspin.basis import spin_basis_1d
from quspin.operators import hamiltonian
import numpy as np

N = 2
basis = spin_basis_1d(L=N)
print(f"Basis states: {basis.states}")

# Create Z_0 operator
# If index 0 is MSB, this should be diag(1, 1, -1, -1) (or similar block structure)
# If index 0 is LSB, this should be diag(1, -1, 1, -1) (alternating)
H_z0 = hamiltonian([['z', [[1.0, 0]]]], [], basis=basis, dtype=np.float64, check_symm=False, check_herm=False)
diag_z0 = H_z0.toarray().diagonal()
print(f"Z_0 diagonal: {diag_z0}")

# Create Z_1 operator (MSB in 2-qubit system if 0 is LSB)
H_z1 = hamiltonian([['z', [[1.0, 1]]]], [], basis=basis, dtype=np.float64, check_symm=False, check_herm=False)
diag_z1 = H_z1.toarray().diagonal()
print(f"Z_1 diagonal: {diag_z1}")
