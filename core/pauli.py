"""
Pauli Matrix Utilities
======================

Efficient construction of single-qubit Pauli operators embedded in an
N-qubit Hilbert space.  These are used by every Hamiltonian generator
to avoid duplicating the same Kronecker-product boilerplate.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Single-qubit Pauli matrices (constant, never mutated)
# ---------------------------------------------------------------------------
SIGMA_X: np.ndarray = np.array([[0, 1], [1, 0]], dtype=np.float64)
SIGMA_Y: np.ndarray = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
SIGMA_Z: np.ndarray = np.array([[1, 0], [0, -1]], dtype=np.float64)


# ---------------------------------------------------------------------------
# Embedded Pauli operators
# ---------------------------------------------------------------------------
def build_pauli_x(qubit_index: int, num_qubits: int) -> np.ndarray:
    """
    Build the Pauli-X operator acting on *qubit_index* inside a
    ``num_qubits``-qubit Hilbert space.

    Parameters
    ----------
    qubit_index : int
        Zero-based index of the target qubit.
    num_qubits : int
        Total number of qubits in the system.

    Returns
    -------
    np.ndarray
        A ``(2**num_qubits, 2**num_qubits)`` real matrix.
    """
    return np.kron(
        np.eye(2**qubit_index),
        np.kron(SIGMA_X, np.eye(2 ** (num_qubits - qubit_index - 1))),
    )


def build_pauli_y(qubit_index: int, num_qubits: int) -> np.ndarray:
    """
    Build the Pauli-Y operator acting on *qubit_index* inside a
    ``num_qubits``-qubit Hilbert space.

    Parameters
    ----------
    qubit_index : int
        Zero-based index of the target qubit.
    num_qubits : int
        Total number of qubits in the system.

    Returns
    -------
    np.ndarray
        A ``(2**num_qubits, 2**num_qubits)`` complex matrix.
    """
    return np.kron(
        np.eye(2**qubit_index),
        np.kron(SIGMA_Y, np.eye(2 ** (num_qubits - qubit_index - 1))),
    )


def build_pauli_z(qubit_index: int, num_qubits: int) -> np.ndarray:
    """
    Build the Pauli-Z operator acting on *qubit_index* inside a
    ``num_qubits``-qubit Hilbert space.

    Parameters
    ----------
    qubit_index : int
        Zero-based index of the target qubit.
    num_qubits : int
        Total number of qubits in the system.

    Returns
    -------
    np.ndarray
        A ``(2**num_qubits, 2**num_qubits)`` real matrix.
    """
    return np.kron(
        np.eye(2**qubit_index),
        np.kron(SIGMA_Z, np.eye(2 ** (num_qubits - qubit_index - 1))),
    )


def build_pauli_operators(
    num_qubits: int,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """
    Pre-compute embedded Pauli-X and Pauli-Z operators for every qubit.

    Parameters
    ----------
    num_qubits : int
        Total number of qubits.

    Returns
    -------
    Xs : list[np.ndarray]
        ``Xs[i]`` is the Pauli-X on qubit *i*.
    Zs : list[np.ndarray]
        ``Zs[i]`` is the Pauli-Z on qubit *i*.
    """
    Xs = [build_pauli_x(i, num_qubits) for i in range(num_qubits)]
    Zs = [build_pauli_z(i, num_qubits) for i in range(num_qubits)]
    return Xs, Zs
