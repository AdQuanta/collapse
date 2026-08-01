"""
Disentanglement Analysis
=========================

Core algorithm for decomposing a unitary matrix into per-qubit initial
states via sub-block diagonalisation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class RelativeEvolutionSpectrum:
    """Eigenvalue data from ``M(t) = U00(t)^(-1) U10(t)``."""

    eigenvalues: np.ndarray
    radii: np.ndarray
    theta: np.ndarray
    theta_reflected: np.ndarray
    condition_number: float
    solver: str


def relative_evolution_matrix(
    U00: np.ndarray,
    U10: np.ndarray,
    *,
    solver: str = "solve",
    rcond: float | None = None,
) -> np.ndarray:
    r"""
    Form the relative evolution matrix ``M(t) = U00(t)^(-1) U10(t)``.

    ``solver="solve"`` uses ``numpy.linalg.solve``. ``solver="pinv"``
    uses the Moore-Penrose pseudoinverse. ``solver="auto"`` tries the
    direct solve and falls back to the pseudoinverse if ``U00`` is
    singular.
    """

    A = np.asarray(U00)
    B = np.asarray(U10)
    if A.ndim != 2 or B.ndim != 2:
        raise ValueError("U00 and U10 must be two-dimensional arrays")
    if A.shape[0] != A.shape[1]:
        raise ValueError("U00 must be square")
    if B.shape != A.shape:
        raise ValueError("U10 must have the same shape as U00")
    if solver not in {"solve", "pinv", "auto"}:
        raise ValueError("solver must be 'solve', 'pinv', or 'auto'")

    if solver in {"solve", "auto"}:
        try:
            return np.linalg.solve(A, B)
        except np.linalg.LinAlgError:
            if solver == "solve":
                raise

    if rcond is None:
        return np.linalg.pinv(A) @ B
    return np.linalg.pinv(A, rcond=rcond) @ B


def diagonalize_relative_evolution(
    U00: np.ndarray,
    U10: np.ndarray,
    *,
    solver: str = "solve",
    rcond: float | None = None,
) -> RelativeEvolutionSpectrum:
    r"""
    Diagonalize ``M(t) = U00(t)^(-1) U10(t)`` and map it to angles.

    The returned samples obey

    ``x_k = |lambda_k(M(t))| = tan(theta_k / 2)``.
    """

    matrix = relative_evolution_matrix(U00, U10, solver=solver, rcond=rcond)
    eigenvalues = np.linalg.eigvals(matrix)
    radii = np.abs(eigenvalues)
    theta = 2.0 * np.arctan(radii)
    try:
        condition_number = float(np.linalg.cond(np.asarray(U00)))
    except np.linalg.LinAlgError:
        condition_number = np.inf

    used_solver = solver
    if solver == "auto":
        try:
            np.linalg.solve(np.asarray(U00), np.asarray(U10))
            used_solver = "solve"
        except np.linalg.LinAlgError:
            used_solver = "pinv"

    return RelativeEvolutionSpectrum(
        eigenvalues=eigenvalues,
        radii=radii,
        theta=theta,
        theta_reflected=np.pi - theta,
        condition_number=condition_number,
        solver=used_solver,
    )


def diagonalize_relative_evolution_from_unitary(
    U: np.ndarray,
    *,
    solver: str = "solve",
    rcond: float | None = None,
) -> RelativeEvolutionSpectrum:
    """Partition a full evolution matrix and diagonalize its ``M(t)`` block."""

    unitary = np.asarray(U)
    if unitary.ndim != 2 or unitary.shape[0] != unitary.shape[1]:
        raise ValueError("U must be a square matrix")
    if unitary.shape[0] % 2:
        raise ValueError("U dimension must be even")
    half = unitary.shape[0] // 2
    return diagonalize_relative_evolution(
        unitary[:half, :half],
        unitary[half:, :half],
        solver=solver,
        rcond=rcond,
    )


def evolution_subblocks_from_eigenbasis(
    E: np.ndarray,
    V: np.ndarray,
    t: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(U00, U10)`` without materialising the full propagator.

    The partition follows the contiguous first-qubit blocks used by
    :class:`DisentanglementAnalyzer` throughout this module.
    """
    eigenvalues = np.asarray(E)
    eigenvectors = np.asarray(V)
    if eigenvectors.ndim != 2 or eigenvectors.shape[0] != eigenvectors.shape[1]:
        raise ValueError("V must be a square eigenvector matrix")
    if eigenvalues.shape != (eigenvectors.shape[0],):
        raise ValueError("E must have one entry per row of V")
    half = eigenvectors.shape[0] // 2
    if 2 * half != eigenvectors.shape[0]:
        raise ValueError("Evolution dimension must be even")
    phases = np.exp(-1j * eigenvalues * t)
    u_columns = (eigenvectors * phases) @ eigenvectors[:half, :].conj().T
    return u_columns[:half, :], u_columns[half:, :]


def _sector_central_top_bit(sector: dict, states: np.ndarray) -> int:
    """Return the central-bit value occupying the first full-basis block."""

    if "central_top_bit" in sector:
        return int(sector["central_top_bit"])
    if states.size >= 2 and states[0] > states[-1]:
        return 1
    return 0


def _central_top_indices(sector: dict, N: int) -> tuple[np.ndarray, np.ndarray]:
    states = np.asarray(sector["states"], dtype=np.int64)
    top_bit = _sector_central_top_bit(sector, states)
    central_bits = (states >> (N - 1)) & 1
    idx_top = np.where(central_bits == top_bit)[0]
    idx_bottom = np.where(central_bits != top_bit)[0]
    return idx_top, idx_bottom


def _project_sector_to_full_basis(sector: dict, N: int) -> np.ndarray:
    """Project a sector eigenvector matrix into the common full basis."""

    V_k = np.asarray(sector["V"])
    basis = sector.get("basis")
    if basis is not None:
        return np.asarray(basis.project_from(V_k, sparse=False))

    D = 2**N
    states = np.asarray(sector["states"], dtype=np.int64)
    top_bit = _sector_central_top_bit(sector, states)
    full_states = (
        np.arange(D - 1, -1, -1, dtype=np.int64)
        if top_bit == 1
        else np.arange(D, dtype=np.int64)
    )
    row_lookup = {int(state): idx for idx, state in enumerate(full_states)}
    rows = np.array([row_lookup[int(state)] for state in states], dtype=np.int64)
    V_full = np.zeros((D, V_k.shape[1]), dtype=np.result_type(V_k, np.complex128))
    V_full[rows, :] = V_k
    return V_full


def _relative_eigenvalues_from_local_sectors(
    sectors: list,
    t: float,
    N: int,
) -> np.ndarray:
    """Compute relative-evolution eigenvalues independently in each sector."""

    all_D0: list[np.ndarray] = []
    for sec in sectors:
        E_k = np.asarray(sec["E"])
        V_k = np.asarray(sec["V"])
        idx_top, idx_bottom = _central_top_indices(sec, N)

        if len(idx_top) == 0 or len(idx_bottom) == 0:
            continue

        phase_k = np.exp(-1j * E_k * t)
        V_top = V_k[idx_top, :]
        U_cols = (V_k * phase_k) @ V_top.conj().T
        A_k = U_cols[idx_top, :]
        C_k = U_cols[idx_bottom, :]
        if A_k.shape != C_k.shape:
            raise ValueError(
                "Sector central split is not square; mark this sector data "
                "with relative_evolution_local=False so the projected full-block "
                "path is used."
            )
        spectrum_k = diagonalize_relative_evolution(A_k, C_k)
        all_D0.append(spectrum_k.eigenvalues)

    if not all_D0:
        return np.array([], dtype=np.complex128)
    return np.concatenate(all_D0)


def _relative_eigenvalues_from_projected_sectors(
    sectors: list,
    t: float,
    N: int,
) -> np.ndarray:
    """Form exact full-basis U00/U10 blocks from projected sector data."""

    D = 2**N
    half = D // 2
    U_cols = np.zeros((D, half), dtype=np.complex128)

    for sec in sectors:
        E_k = np.asarray(sec["E"])
        V_full = _project_sector_to_full_basis(sec, N)
        if V_full.shape[0] != D:
            raise ValueError(
                f"Projected sector has {V_full.shape[0]} rows, expected {D}"
            )
        phase_k = np.exp(-1j * E_k * t)
        V_top = V_full[:half, :]
        U_cols += (V_full * phase_k) @ V_top.conj().T

    spectrum = diagonalize_relative_evolution(
        U_cols[:half, :],
        U_cols[half:, :],
    )
    return spectrum.eigenvalues


class DisentanglementAnalyzer:
    """
    Analyse a unitary matrix *U* to extract per-qubit initial states by
    diagonalising products of its sub-blocks.

    The procedure is:

    1. Partition *U* into four equal sub-blocks: U00, U01, U10, U11.
    2. Form  W0 = U00⁻¹ U10.
    3. Compute eigenvalues D0 of W0; derive D1 = −conj(D0).
    4. Map the eigenvalues to qubit states on the Bloch sphere.

    Parameters
    ----------
    U : np.ndarray
        Unitary matrix of shape ``(N, N)`` with *N* even.
    check_unitary : bool
        If *True*, verify that *U* is unitary (up to numerical tolerance).

    Attributes
    ----------
    D0, D1 : np.ndarray or None
        Eigenvalues of W0 and W1 (populated after :meth:`diagonalize_subblocks_product`).
    phi0, phi1 : np.ndarray or None
        Per-qubit initial states, shape ``(N/2, 2)``
        (populated after :meth:`get_initial_qubit_states_from_eigenvalues`).
    """

    def __init__(self, U: np.ndarray, check_unitary: bool = False):
        if check_unitary and not np.allclose(U @ U.conj().T, np.eye(U.shape[0])):
            raise ValueError("Input must be a unitary matrix.")
        self.U = U
        self.N = U.shape[0]

        self.D0: Optional[np.ndarray] = None
        self.D1: Optional[np.ndarray] = None
        self.phi0: Optional[np.ndarray] = None
        self.phi1: Optional[np.ndarray] = None

    # -----------------------------------------------------------------
    @classmethod
    def from_eigenbasis(
        cls,
        E: np.ndarray,
        V: np.ndarray,
        t: float,
    ) -> "DisentanglementAnalyzer":
        """
        Create an analyser directly from a pre-computed eigenbasis,
        avoiding construction of the full *D × D* unitary.

        Only the sub-blocks *U00* and *U10* are formed (each *D/2 × D/2*).

        Parameters
        ----------
        E : np.ndarray
            Eigenvalues of the Hamiltonian, shape ``(D,)``.
        V : np.ndarray
            Eigenvectors (columns) in the full computational basis,
            shape ``(D, D)``.
        t : float
            Evolution time.

        Returns
        -------
        DisentanglementAnalyzer
            Ready-to-use analyser (call
            :meth:`get_initial_qubit_states_from_eigenvalues` next).
        """
        D = V.shape[0]
        U00, U10 = evolution_subblocks_from_eigenbasis(E, V, t)

        spectrum = diagonalize_relative_evolution(U00, U10)
        D0 = spectrum.eigenvalues

        obj = cls.__new__(cls)
        obj.U = None
        obj.N = D
        obj.D0 = D0
        obj.D1 = -np.conj(D0)
        obj.phi0 = None
        obj.phi1 = None
        return obj

    # -----------------------------------------------------------------
    @classmethod
    def from_sectors(
        cls,
        sectors: list,
        t: float,
        N: int,
    ) -> "DisentanglementAnalyzer":
        """
        Create an analyser from symmetry-sector data, performing all
        computation in the reduced sector bases.

        This is the most efficient path: it never constructs the full
        eigenvector matrix or D/2 × D/2 sub-blocks.  Within each
        sector the time-evolution matrix *U_k* is built, split by the
        first-qubit (site 0) state, and the sector's *W_k* eigenvalues
        are computed independently.

        If sector metadata marks this local split as unsafe, the method
        instead projects sector eigenvectors back to the common full basis and
        forms the exact full ``U00`` and ``U10`` blocks before diagonalizing.

        Parameters
        ----------
        sectors : list of dict
            Each dict has keys ``'E'`` (eigenvalues), ``'V'``
            (eigenvectors in the *reduced* basis), and ``'states'``
            (computational-basis state integers from QuSpin).
        t : float
            Evolution time.
        N : int
            Total number of qubits (needed to identify site 0).

        Returns
        -------
        DisentanglementAnalyzer
        """
        D = 2**N
        if not sectors:
            raise ValueError("sectors must contain at least one sector")

        if all(sec.get("relative_evolution_local", True) for sec in sectors):
            D0 = _relative_eigenvalues_from_local_sectors(sectors, t, N)
        else:
            D0 = _relative_eigenvalues_from_projected_sectors(sectors, t, N)

        if D0.size != D // 2:
            raise ValueError(
                f"Sector relative-evolution path produced {D0.size} eigenvalues, "
                f"expected {D // 2}"
            )

        obj = cls.__new__(cls)
        obj.U = None
        obj.N = D
        obj.D0 = D0
        obj.D1 = -np.conj(D0)
        obj.phi0 = None
        obj.phi1 = None
        return obj

    # -----------------------------------------------------------------
    def diagonalize_subblocks_product(self, verbose: bool = False) -> None:
        """
        Diagonalise the product  W0 = U00⁻¹ U10  and derive the
        eigenvalues of  W1 = U11⁻¹ U01  via the relation  D1 = −conj(D0).

        Results are stored in :attr:`D0`, :attr:`D1`.
        """
        import time

        half = self.N // 2
        U00 = self.U[:half, :half]
        U10 = self.U[half:, :half]

        if verbose:
            print("Diagonalizing M(t)=U00(t)^(-1)U10(t)...")
            t0 = time.time()

        spectrum = diagonalize_relative_evolution(U00, U10)
        self.D0 = spectrum.eigenvalues
        self.D1 = -np.conj(self.D0)

        if verbose:
            print(f"Elapsed time: {time.time() - t0:.4f} seconds")

    # -----------------------------------------------------------------
    def get_initial_qubit_states_from_eigenvalues(self) -> None:
        """
        Compute initial qubit states on the Bloch sphere from the
        eigenvalues of W0 and W1.

        Results are stored in :attr:`phi0` and :attr:`phi1`.
        """
        if self.D0 is None:
            self.diagonalize_subblocks_product()

        half = self.N // 2
        self.phi0 = np.zeros((half, 2), dtype=np.complex128)
        self.phi1 = np.zeros((half, 2), dtype=np.complex128)

        norm0 = np.sqrt(1 + np.abs(self.D0) ** 2)
        norm1 = np.sqrt(1 + np.abs(self.D1) ** 2)

        self.phi0[:, 0] = 1.0 / norm0
        self.phi0[:, 1] = self.D0 / norm0
        self.phi1[:, 0] = self.D1 / norm1
        self.phi1[:, 1] = 1.0 / norm1
