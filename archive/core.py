import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.stats import gaussian_kde
from tqdm import tqdm

from quspin.basis import spin_basis_1d, tensor_basis
from quspin.operators import hamiltonian
from quspin.tools.measurements import ent_entropy, obs_vs_time


# Set default plot parameters
plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Arial"

# Set random seed for reproducibility
rng = np.random.default_rng(42)


def scatter_density(ax, x, y, **kwargs):
    """
    Scatter plot with density coloring.

    Parameters:
    - ax: matplotlib.axes.Axes, the axes to plot on.
    - x: numpy.ndarray, x-coordinates.
    - y: numpy.ndarray, y-coordinates.
    - kwargs: additional keyword arguments for scatter.
    """
    # Compute density via kernel density estimation (KDE)
    xy = np.vstack([x, y])
    kde = gaussian_kde(xy)

    ax.scatter(x, y, c=kde(xy), **kwargs)


class HamiltonianAnalyzer:
    def __init__(self, L=None, basis_type="spin", pauli=False, basis_list=None, **basis_kwargs):
        """
        Initialize the HamiltonianAnalyzer class.

        Parameters:
        - L: int or None, number of sites (ignored if basis_list is provided).
        - basis_type: str, type of basis (default is "spin").
        - pauli: bool, whether to use Pauli matrices (default: False).
        - basis_list: list or None, if provided, a list of (basis_type, bL, bpauli, bkwargs) tuples for tensor product bases.
        - basis_kwargs: additional arguments for the basis constructor.
        """
        if basis_list is not None:
            # Tensor product of spin bases
            bases = []
            for btype, bL, bpauli, bkwargs in basis_list:
                if btype == "spin":
                    bases.append(spin_basis_1d(bL, pauli=bpauli, **bkwargs))
                else:
                    raise ValueError(
                        f"Unsupported basis type in tensor: {btype}")
            self.basis = tensor_basis(*bases)
            self.L = sum(bL for _, bL, _, _ in basis_list)
        elif basis_type == "spin":
            if L is None:
                raise ValueError(
                    "L must be specified if basis_list is not provided.")
            self.basis = spin_basis_1d(L, pauli=pauli, **basis_kwargs)
            self.L = L
        else:
            raise ValueError("Unsupported basis type.")

        self.static = []

    def add_static_term(self, coeff, op_str, sites):
        """
        Add a static term to the Hamiltonian.

        Parameters:
        - coeff: float or list, coefficient(s) of the term.
        - op_str: str, operator string (e.g., "zz", "x").
        - sites: list of tuples, sites where the operator acts.
        """
        coeff_sites = [[coeff] + site for site in sites]

        # Shorthand for (isotropic) Heisenberg interaction
        if op_str == "heis":
            for op in ["xx", "yy", "zz"]:
                self.static.append([op, coeff_sites])
        else:
            self.static.append([op_str, coeff_sites])

    # TODO add a function to add dynamic terms

    def construct_hamiltonian(self, **kwargs):
        """
        Construct the Hamiltonian using the static term.

        Parameters:
        - kwargs: additional arguments for the hamiltonian constructor.

        Returns:
        - ham: quspin.operators.hamiltonian, the constructed Hamiltonian.
        """
        return hamiltonian(static_list=self.static, dynamic_list=[], basis=self.basis, dtype=np.float64, **kwargs)

    def diagonalize(self, timeit=False):
        """
        Diagonalize the system's Hamiltonian.

        Parameters:
        - timeit: bool, if True, print the elapsed time for diagonalization.

        Returns:
        - eigvals: numpy.ndarray, eigenvalues of the Hamiltonian.
        - eigvecs: numpy.ndarray, eigenvectors of the Hamiltonian.
        """
        start = time.time() if timeit else None
        eigvals, eigvecs = self.construct_hamiltonian(check_symm=False, check_herm=False, check_pcon=False).eigh()
        if timeit:
            elapsed = time.time() - start
            print(f"Diagonalization took {elapsed:.4f} seconds.")
        return eigvals, eigvecs

    def compute_time_evolution(self, psi0, times, eigvals, eigvecs, observables=None):
        """
        Compute the time evolution of expectation values for given observables.

        Parameters:
        - psi0: numpy.ndarray, initial state vector.
        - times: numpy.ndarray, array of time points.
        - eigvals: numpy.ndarray, eigenvalues of the Hamiltonian.
        - eigvecs: numpy.ndarray, eigenvectors of the Hamiltonian (each column is an eigenvector).
        - observables: dict or None, keys are observable names and values are quspin.operators.hamiltonian objects.
          If None, defaults to {X0, Y0, Z0} for the first qubit.

        Returns:
        - dict: keys are observable names, values are arrays of expectation values at each time point.
        """

        if observables is None:
            observables = {
                "X0": hamiltonian([["x", [[1.0, 0]]]], [], basis=self.basis, dtype=np.complex128, check_symm=False, check_herm=False),
                "Y0": hamiltonian([["y", [[1.0j, 0]]]], [], basis=self.basis, dtype=np.complex128, check_symm=False, check_herm=False),
                "Z0": hamiltonian([["z", [[1.0, 0]]]], [], basis=self.basis, dtype=np.complex128, check_symm=False, check_herm=False),
            }

        # Compute time evolution of observables
        obs_time = obs_vs_time(
            psi_t=(psi0, eigvals, eigvecs), Obs_dict=observables, times=times)

        # Convert the Y0 observables back to real-valued
        if "Y0" in obs_time:
            obs_time["Y0"] *= -1j

        # Remove spurious imaginary components
        for obs in obs_time.keys():
            obs_time[obs] = np.real(obs_time[obs])

        return obs_time

    def compute_bipartite_entanglement_entropy(self, eigvecs):
        """
        Compute the bipartite entanglement entropy for all eigenvectors,
        using an equal bipartition of the system.

        Parameters:
        - eigvecs: numpy.ndarray, eigenvectors of the Hamiltonian (each column is an eigenvector).

        Returns:
        - numpy.ndarray, entanglement entropy for each eigenvector.
        """
        entropies = []

        for i in tqdm(range(eigvecs.shape[1]), desc="Entanglement"):
            state = eigvecs[:, i]
            ent = self.basis.ent_entropy(state, density=False)
            entropies.append(ent['Sent_A'])

        return np.array(entropies)

    def compute_local_expectation_values(self, eigvec, operators):
        """
        Compute local expectation values on a given eigenstate.

        Parameters:
        - eigvec: numpy.ndarray, eigenvector of the Hamiltonian.
        - operators: list of quspin.operators.hamiltonian, local operators.

        Returns:
        - list, expectation values for each operator.
        """
        return [op.expt_value(eigvec) for op in operators]

    def plot_density_of_states(self, eigvals, bins=30):
        """
        Plot the density of states (DOS) of the Hamiltonian.

        Parameters:
        - eigvals: numpy.ndarray, eigenvalues of the Hamiltonian.
        - bins: int, number of bins for the histogram (default: 30).
        """
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.hist(eigvals, bins=bins, density=True, alpha=0.7)
        ax.set_xlabel("Energy")
        ax.set_ylabel("Density")
        ax.set_title("Density of States")
        plt.tight_layout()
        plt.show()

    def plot_level_spacing_distribution(self, eigvals, bins=30, fit=None):
        """
        Plot the normalized level spacing distribution, with optional fit to Poisson, GOE, or GUE.

        Parameters:
        - eigvals: numpy.ndarray, eigenvalues of the Hamiltonian.
        - bins: int, number of bins for the histogram (default: 30).
        - fit: str or None, fit distribution: "poisson", "goe", or "gue" (default: None).
        """
        # Compute level spacings
        eigvals_sorted = np.sort(eigvals)
        spacings = np.diff(eigvals_sorted)

        # Remove degeneracies
        eps = 1e-6  # Small threshold to discard near-zero spacings
        spacings = spacings[spacings > eps]
        print(len(spacings), "spacings after removing degeneracies")

        # Plot spacings
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.plot(spacings, "o", markersize=3)
        ax.set_xlabel("Index")
        ax.set_ylabel("Level Spacing")
        ax.set_title("Level Spacing Distribution")
        plt.tight_layout()
        plt.show()

        # Normalize spacings (unfolding)
        spacings /= np.mean(spacings)

        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        counts, bin_edges, _ = ax.hist(
            spacings, bins=bins, density=True, alpha=0.7, label="Data")

        # Fit distributions
        s = np.linspace(0, 5, 200)
        if fit is not None:
            if fit.lower() == "poisson":
                # Poisson: P(s) = exp(-s)
                P = np.exp(-s)
                ax.plot(s, P, "r--", label="Poisson")
            elif fit.lower() == "goe":
                # GOE (Wigner-Dyson): P(s) = (π/2) s exp(-π s^2 / 4)
                P = (np.pi / 2) * s * np.exp(-np.pi * s ** 2 / 4)
                ax.plot(s, P, "g--", label="GOE")
            elif fit.lower() == "gue":
                # GUE: P(s) = (32/π^2) s^2 exp(-4 s^2 / π)
                P = (32 / (np.pi ** 2)) * s ** 2 * np.exp(-4 * s ** 2 / np.pi)
                ax.plot(s, P, "b--", label="GUE")
            else:
                raise ValueError(
                    "fit must be one of: None, 'poisson', 'goe', 'gue'.")

        ax.set_xlabel("Level Spacing")
        ax.set_ylabel("Probability Density")
        ax.set_title("Level Spacing Distribution")
        ax.legend()
        plt.tight_layout()
        plt.show()

    def plot_time_evolution(self, times, observables):
        """
        Plot the time evolution of observables.

        Parameters:
        - times: numpy.ndarray, array of time points.
        - observables: dict, keys are observable names and values are their time evolution.
        """
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        for name, values in observables.items():
            ax.plot(times, values, label=name)
        ax.set_ylim(-1.1, 1.1)
        ax.set_xlabel("Time")
        ax.set_ylabel("Observable")
        ax.set_title("Time Evolution of Observables")
        ax.legend()
        plt.tight_layout()
        plt.show()

    def plot_entanglement_entropy(self, Sent, eigvals=None):
        """
        Plot the entanglement entropy of Hamiltonian eigenstates.

        Parameters:
        - Sent: numpy.ndarray, entanglement entropy for each eigenstate.
        - eigvals: numpy.ndarray or None, eigenvalues of the Hamiltonian (optional).
        """
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        if eigvals is not None:
            scatter_density(ax, eigvals, Sent, cmap="plasma")
            ax.set_xlabel("Eigenvalue")
        else:
            scatter_density(ax, range(len(Sent)), Sent, cmap="plasma")
            ax.set_xlabel("Eigenstate Index")
        ax.set_ylim(0, self.L // 2 * np.log(2))
        ax.set_ylabel("Entanglement Entropy")
        ax.set_title("Entanglement Entropy of Eigenstates")
        plt.tight_layout()
        plt.show()

    def verify_eth(self, eigvecs, obs=None):
        """
        Verify the Eigenstate Thermalization Hypothesis (ETH) by computing
        the expectation value of a local observable for each eigenstate.

        Parameters:
        - eigvecs: numpy.ndarray, eigenvectors of the Hamiltonian (each column is an eigenvector).
        - obs: quspin.operators.hamiltonian or None, the local observable operator.
          If None, the default observable is the x-magnetization operator.

        Returns:
        - numpy.ndarray, expectation values of the observable for each eigenstate.
        """
        if obs is None:
            # Default observable: x-magnetization operator
            obs = hamiltonian([["x", [[1.0, i] for i in range(self.L)]]], [
            ], basis=self.basis, dtype=np.float64)

        expectations = []
        for i in tqdm(range(eigvecs.shape[1]), desc="ETH Verification"):
            state = eigvecs[:, i]
            expectation = obs.expt_value(state)
            expectations.append(expectation)

        return np.array(expectations)

    def plot_eth_verification(self, eigvals, expectations):
        """
        Scatter plot of local expectation values against eigenvalues for ETH verification.

        Parameters:
        - eigvals: numpy.ndarray, eigenvalues of the Hamiltonian.
        - expectations: numpy.ndarray, expectation values of the observable for each eigenstate.
        """
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        scatter_density(ax, eigvals, expectations, cmap="plasma")
        ax.set_xlabel("Energy")
        ax.set_ylabel("Expectation Value")
        ax.set_title("ETH Verification")
        plt.tight_layout()
        plt.show()


class StateGenerator:

    def create_product_state(self, local_coeffs):
        """
        Create a product state as a tensor product of local 2D complex vectors.

        Parameters:
        - local_coeffs: list of list/tuple/np.ndarray, each element is a length-2 array of complex coefficients
          for a single spin (e.g., [[a0, b0], [a1, b1], ..., [aL, bL]] for L+1 sites).

        Returns:
        - numpy.ndarray, the product state vector in the full Hilbert space.
        """
        state = np.array(local_coeffs[-1], dtype=np.complex128)

        for coeffs in local_coeffs[-2::-1]:
            state = np.kron(np.array(coeffs, dtype=np.complex128), state)

        return state

    def create_random_product_state(self, L):
        """
        Create a random product state as a tensor product of local 2D complex vectors.

        Each local vector is sampled uniformly from the complex unit sphere.

        Parameters:
        - L (int): Number of qubits (log2 of the Hilbert space dimension).

        Returns:
        - numpy.ndarray: A normalized complex vector of length 2**L representing the random product state.
        """
        local_coeffs = [self.create_haar_random_state(1) for _ in range(L)]
        return self.create_product_state(local_coeffs)

    def create_haar_random_state(self, L, seed=None):
        """
        Generates a Haar-random pure quantum state vector for a Hilbert space of 2^L dimensions.

        A Haar-random state is sampled uniformly from the surface of the complex unit sphere in Hilbert space,
        which is commonly used in quantum information theory for simulating random pure states.

        Parameters:
        - L (int): Number of qubits (log2 of the Hilbert space dimension).
        - seed (int or None): Random seed for reproducibility (default is None).

        Returns:
        - numpy.ndarray: A normalized complex vector of length 2**L representing the Haar-random state.
        """
        # Initialize pseudo-random number generator
        rng = np.random.default_rng(seed)

        Ns = 2 ** L  # Number of states in the Hilbert space
        state = rng.normal(loc=0, scale=1, size=Ns) + 1j * \
            rng.normal(loc=0, scale=1, size=Ns)
        return state / np.linalg.norm(state)

    def create_qubit_tensor_haar_state(self, L, qubit_index, qubit_state, seed=None):
        """
        Create a state comprised of a pure qubit state at a specific index in tensor product
        with the other L-1 qubits in a Haar random state.

        Parameters:
        - L: int, total number of qubits.
        - qubit_index: int, the index of the qubit with the pure state.
        - qubit_state: list or numpy.ndarray, the pure state of the qubit (e.g., [1, 0] for |0>).
        - seed: int or None, random seed for reproducibility (default is None).

        Returns:
        - numpy.ndarray, the combined state vector in the full Hilbert space.
        """
        # Create Haar random state for the remaining L-1 qubits
        haar_state = self.create_haar_random_state(L - 1, seed=seed)

        # Tensor product the pure qubit state with the Haar random state
        state = np.kron(np.array(qubit_state, dtype=np.complex128), haar_state)

        # Permute the qubit to the correct position
        if qubit_index != 0:
            state = np.reshape(state, [2] * L)
            state = np.moveaxis(state, 0, qubit_index)
            state = state.flatten()

        return state

    def create_tensor_product_state(self, state1, state2):
        """
        Create a state which is the tensor product of two other states or density matrices.

        Parameters
        ----------
        state1 (numpy.ndarray): The first state vector or density matrix.
        state2 (numpy.ndarray): The second state vector or density matrix.

        Returns
        -------
        numpy.ndarray: The tensor product state vector or density matrix.
        """
        # If both are vectors, use np.kron directly
        if state1.ndim == 1 and state2.ndim == 1:
            return np.kron(state1, state2)
        # If both are matrices (density matrices), use np.kron for matrices
        elif state1.ndim == 2 and state2.ndim == 2:
            return np.kron(state1, state2)
        # If one is a vector and one is a matrix, convert the vector to a density matrix
        elif state1.ndim == 2 and state2.ndim == 1:
            state2_dm = np.outer(state2, state2.conj())
            return np.kron(state1, state2_dm)
        elif state1.ndim == 1 and state2.ndim == 2:
            state1_dm = np.outer(state1, state1.conj())
            return np.kron(state1_dm, state2)

    def create_thermal_state(self, beta, E, V):
        """
        Create a thermal state for a system at inverse temperature beta.

        Parameters:
        - beta: float, inverse temperature (1/kT).
        - E: numpy.ndarray, energy eigenvalues.
        - V: numpy.ndarray, eigenstates corresponding to the energy eigenvalues.

        Returns:
        - numpy.ndarray, the thermal density matrix.
        """
        # Compute the partition function
        exp_diag = np.exp(-beta * E)
        exp_diag_mat = np.diag(exp_diag)
        Z = np.sum(exp_diag)

        # Compute the thermal state as a weighted sum of the eigenstates
        thermal_state = (1 / Z) * V @ exp_diag_mat @ V.conj().T

        return thermal_state

    def create_thermal_state_pure(self, beta, E, V, seed=None):
        """
        Create a pure thermal state for a system at inverse temperature beta.

        Parameters:
        - beta: float, inverse temperature (1/kT).
        - E: numpy.ndarray, energy eigenvalues.
        - V: numpy.ndarray, eigenstates corresponding to the energy eigenvalues.
        - seed: int or None, random seed for reproducibility (default is None).

        Returns:
        - numpy.ndarray, the pure thermal state vector.
        """
        # Compute the partition function
        exp_diag = np.exp(-beta * E)
        Z = np.sum(exp_diag)

        # Generate random phases
        rng = np.random.default_rng(seed)
        phases = np.exp(1j * 2 * np.pi * rng.random(len(E)))

        # Compute the thermal state as a weighted sum of the eigenstates
        thermal_state = (1 / np.sqrt(Z)) * np.sum(V * np.sqrt(exp_diag) * phases, axis=1)

        return thermal_state


# Usage example
if __name__ == "__main__":
    L = 12  # Number of sites

    # Create Hamiltonian analyzer for bath spins
    ha = HamiltonianAnalyzer(L=L, basis_type="spin", pauli=True)

    # Nearest-neighbor Ising interaction (open BC)
    ha.add_static_term(1.0, "zz", [[i, i + 1] for i in range(L - 1)])

    # Tilted magnetic field on the xz plane
    ha.add_static_term(1.1, "x", [[i] for i in range(L)])
    ha.add_static_term(0.3, "z", [[i] for i in range(L)])

    # Inversion symmetry breaking
    ha.add_static_term(0.25, "z", [[0]])
    ha.add_static_term(-0.25, "z", [[L - 1]])

    # Diagonalize the Hamiltonian
    eigvals, eigvecs = ha.diagonalize(timeit=True)
    ha.plot_density_of_states(eigvals)

    # Compute bipartite entanglement entropy
    Sent = ha.compute_bipartite_entanglement_entropy(eigvecs)
    ha.plot_entanglement_entropy(Sent)

    # Verify eigenstate thermalization hypothesis (ETH)
    expectations = ha.verify_eth(eigvecs)
    ha.plot_eth_verification(eigvals, expectations)

    # Compute matrix elements of Sx with eigenstates
    Sx = hamiltonian([["x", [[1.0, 0]]]], [], basis=ha.basis, dtype=np.float64)
    Sx_mat = []
    for i in tqdm(range(eigvecs.shape[1]), desc="Sx Expectation"):
        Sx_mat.append(Sx.matrix_ele(eigvecs[:, i], eigvecs[:, 15]))

    # Plot matrix elements
    # Convert Sx_mat to numpy array for easier processing
    Sx_mat = np.array(Sx_mat)
    energy_diff = eigvals - eigvals[15]
    sx_vals = np.abs(Sx_mat) ** 2

    # Convolve with a Gaussian
    sigma = 10.  # Adjust for desired smoothing
    sx_vals_smooth = gaussian_filter1d(sx_vals, sigma=sigma)

    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    ax.plot(energy_diff, sx_vals, '.', label="Raw", markersize=3)
    ax.plot(energy_diff, sx_vals_smooth, '-',
            label=f"Gaussian smoothed (σ={sigma})", linewidth=2)
    ax.set_xlabel("Energy Difference")
    ax.set_ylabel("Sx Expectation Value")
    ax.set_title("Sx Expectation Values for Eigenstates")
    ax.legend()
    plt.tight_layout()
    plt.show()
