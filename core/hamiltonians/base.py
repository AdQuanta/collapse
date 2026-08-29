"""
Hamiltonian Generator — Abstract Base Class
============================================

All concrete Hamiltonian generators (NumPy and QuSpin backends) must
implement this interface, ensuring they can be used interchangeably.
"""

from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np


class HamiltonianGenerator(ABC):
    """
    Interface for Hamiltonian matrix generators.

    Subclasses store model parameters and produce a dense matrix
    representation of the Hamiltonian via :meth:`generate`.
    """

    @abstractmethod
    def generate(self) -> np.ndarray:
        """
        Build and return the Hamiltonian as a dense NumPy array.

        Returns
        -------
        np.ndarray
            Hermitian matrix of shape ``(D, D)`` where ``D = 2**N``.
        """

    def diagonalize(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Diagonalise the Hamiltonian, returning eigenvalues and
        eigenvectors in the full computational basis.

        Subclasses (e.g. QuSpin backends) may override this to exploit
        symmetries for faster block-diagonal diagonalisation.

        Returns
        -------
        E : np.ndarray
            Eigenvalues, shape ``(D,)``.
        V : np.ndarray
            Eigenvectors (columns), shape ``(D, D)``, in the full
            computational basis.
        """
        H = self.generate()
        return np.linalg.eigh(H)

    def diagonalize_sectors(self) -> list:
        """
        Return per-symmetry-sector eigenbasis data.

        Each element is a dict with keys ``'E'`` (eigenvalues),
        ``'V'`` (eigenvectors in the *reduced* sector basis), and
        ``'states'`` (computational-basis state integers).

        The default implementation returns a single sector that spans
        the full Hilbert space.  QuSpin subclasses override this to
        provide genuinely reduced sectors.
        """
        H = self.generate()
        D = H.shape[0]
        E, V = np.linalg.eigh(H)
        return [
            {
                "E": E,
                "V": V,
                "states": np.arange(D),
                "central_top_bit": 0,
                "relative_evolution_local": True,
                "symmetry_label": "full",
            }
        ]
