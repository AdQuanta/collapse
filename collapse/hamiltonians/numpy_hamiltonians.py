"""
NumPy-Based Hamiltonian Generators
====================================

Dense-matrix implementations of various spin-model Hamiltonians using
only NumPy.  Each class stores model parameters and produces the full
Hamiltonian via :meth:`generate`.

All classes delegate Pauli-operator construction to
:mod:`collapse.pauli` and disorder sampling to
:mod:`collapse.disorder`, satisfying the Single Responsibility
and Dependency Inversion principles.

Every Hamiltonian supports optional disorder on both **coupling
strengths** (spin–spin interactions) and **self-energies** (on-site
fields) via a :class:`~collapse.disorder.DisorderStrategy`.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from collapse.disorder import DisorderStrategy, create_disorder_strategy
from collapse.hamiltonians.base import HamiltonianGenerator
from collapse.pauli import build_pauli_operators, build_pauli_y


# ===================================================================
# Helper: resolve a disorder constructor argument
# ===================================================================
def _resolve_disorder(
    disorder: Optional[DisorderStrategy | str],
) -> Optional[DisorderStrategy]:
    """Return a *DisorderStrategy* instance or *None*."""
    if disorder is not None:
        return (
            create_disorder_strategy(disorder)
            if isinstance(disorder, str)
            else disorder
        )
    return None


def _val(
    disorder: Optional[DisorderStrategy],
    base: float,
    strength: float,
) -> float:
    """Return a (possibly disordered) value."""
    if disorder is not None and strength != 0.0:
        return disorder.sample(base, strength)
    return base


_VALID_CONNECTIVITIES = {"chain", "ring", "all_to_all"}
_VALID_CENTRAL_COUPLINGS = {"auto", "all", "first", "last", "ends"}


def _pixel_bonds(
    pixel_start: int, n_pixel: int, connectivity: str
) -> list[tuple[int, int]]:
    """Return intra-pixel bond pairs ``(i, j)``.

    Parameters
    ----------
    pixel_start : int
        Index of the first qubit in the pixel.
    n_pixel : int
        Number of qubits in the pixel.
    connectivity : {"chain", "ring", "all_to_all"}
        Topology of intra-pixel couplings.
    """
    if connectivity not in _VALID_CONNECTIVITIES:
        raise ValueError(
            f"Unknown connectivity {connectivity!r}; "
            f"choose from {sorted(_VALID_CONNECTIVITIES)}"
        )
    if connectivity == "chain":
        return [(pixel_start + k, pixel_start + k + 1) for k in range(n_pixel - 1)]
    if connectivity == "ring":
        bonds = [(pixel_start + k, pixel_start + k + 1) for k in range(n_pixel - 1)]
        if n_pixel > 1:
            bonds.append((pixel_start + n_pixel - 1, pixel_start))
        return bonds
    # all_to_all
    return [
        (pixel_start + a, pixel_start + b)
        for a in range(n_pixel)
        for b in range(a + 1, n_pixel)
    ]


def _central_targets(
    pixel_start: int,
    n_pixel: int,
    connectivity: str,
    central_coupling: str = "auto",
) -> list[int]:
    """Return pixel sites coupled directly to the central qubit.

    ``"auto"`` preserves the historical convention: open chains couple only to
    the first pixel site, while ring/all-to-all detectors couple to every pixel
    site.
    """

    if central_coupling not in _VALID_CENTRAL_COUPLINGS:
        raise ValueError(
            f"Unknown central_coupling {central_coupling!r}; "
            f"choose from {sorted(_VALID_CENTRAL_COUPLINGS)}"
        )
    if n_pixel < 1:
        return []
    if central_coupling == "auto":
        central_coupling = "first" if connectivity == "chain" else "all"
    if central_coupling == "all":
        return [pixel_start + k for k in range(n_pixel)]
    if central_coupling == "first":
        return [pixel_start]
    if central_coupling == "last":
        return [pixel_start + n_pixel - 1]
    # ends
    first = pixel_start
    last = pixel_start + n_pixel - 1
    return [first] if first == last else [first, last]


# ===================================================================
# Mixed-field Ising model
# ===================================================================
class MixedFieldIsingHamiltonianNumpy(HamiltonianGenerator):
    r"""
    Mixed-field Ising Hamiltonian with periodic boundary conditions.

    .. math::
        H = -\sum_i J_i\, Z_i Z_{i+1}
            -\sum_i h_{x,i}\, X_i
            -\sum_i h_{z,i}\, Z_i

    Parameters
    ----------
    N : int
        Number of qubits.
    J : float
        Nearest-neighbour ZZ coupling strength.
    hx : float
        Transverse-field strength (X direction).
    hz : float
        Longitudinal-field strength (Z direction).
    disorder : DisorderStrategy or str or None
        Disorder strategy.
    disorder_strength : float
        Global disorder width (fallback for per-parameter widths).
    disorder_strength_J : float or None
        Disorder width for ZZ couplings.
    disorder_strength_hx : float or None
        Disorder width for transverse-field self-energies.
    disorder_strength_hz : float or None
        Disorder width for longitudinal-field self-energies.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        N: int,
        J: float = 1.0,
        hx: float = 0.0,
        hz: float = 0.0,
        disorder: Optional[DisorderStrategy | str] = None,
        disorder_strength: float = 0.0,
        disorder_strength_J: Optional[float] = None,
        disorder_strength_hx: Optional[float] = None,
        disorder_strength_hz: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        self.N = N
        self.J = J
        self.hx = hx
        self.hz = hz
        self.seed = seed

        self.disorder_strength_J = (
            disorder_strength_J
            if disorder_strength_J is not None
            else disorder_strength
        )
        self.disorder_strength_hx = (
            disorder_strength_hx
            if disorder_strength_hx is not None
            else disorder_strength
        )
        self.disorder_strength_hz = (
            disorder_strength_hz
            if disorder_strength_hz is not None
            else disorder_strength
        )
        self._disorder = _resolve_disorder(disorder)

    def generate(self) -> np.ndarray:
        N = self.N
        D = 2**N
        H = np.zeros((D, D), dtype=np.complex128)
        Xs, Zs = build_pauli_operators(N)

        if self.seed is not None:
            np.random.seed(self.seed)

        # Nearest-neighbour ZZ interaction (periodic BC)
        for i in range(N):
            j_val = _val(self._disorder, self.J, self.disorder_strength_J)
            H -= j_val * (Zs[i] @ Zs[(i + 1) % N])

        # External field terms (self-energies)
        for i in range(N):
            hx_val = _val(self._disorder, self.hx, self.disorder_strength_hx)
            hz_val = _val(self._disorder, self.hz, self.disorder_strength_hz)
            H -= hx_val * Xs[i]
            H -= hz_val * Zs[i]

        return H


# ===================================================================
# Single-pixel model
# ===================================================================
class SinglePixelHamiltonianNumpy(HamiltonianGenerator):
    r"""
    Single-pixel Hamiltonian: central qubit (index 0) coupled to a pixel
    of *N_pixel* qubits.

    .. math::
        H = -J\sum_{\langle i,j\rangle_\text{pixel}} Z_i Z_j
            -J_{\pm}\sum_{\langle i,j\rangle_\text{pixel}}
                (\sigma^+_i \sigma^-_j + \sigma^-_i \sigma^+_j)
            -\sum_i \bigl(J_x\, X_0 X_i + J_z\, Z_0 Z_i
                         + J_{zx}\, Z_0 X_i\bigr)
            -\sum_i \bigl(h_{x,i}\, X_i + h_{z,i}\, Z_i\bigr)

    Parameters
    ----------
    N_pixel : int
        Number of pixel qubits.
    J : float
        Intra-pixel ZZ coupling.
    Jpm : float
        Intra-pixel +− (XY) coupling.
    Jx : float
        Central–pixel XX coupling.
    Jz : float
        Central–pixel ZZ coupling.
    Jzx : float
        Central–pixel ZX coupling (Z on central, X on pixel).
    hx : float
        Transverse self-energy field (pixel qubits, and central when
        *hx0* is *None*).
    hz : float
        Longitudinal self-energy field (pixel qubits, and central when
        *hz0* is *None*).
    hx0 : float or None
        Transverse field on the central qubit.  Falls back to *hx* when
        *None*.
    hz0 : float or None
        Longitudinal field on the central qubit.  Falls back to *hz*
        when *None*.
    connectivity : {"chain", "ring", "all_to_all"}
        Intra-pixel coupling topology.  ``"chain"`` gives an open 1-D
        chain, ``"ring"`` (default) adds a periodic closing bond, and
        ``"all_to_all"`` couples every pair of pixel qubits.
    disorder, disorder_strength, disorder_strength_J, disorder_strength_Jpm,
    disorder_strength_Jx, disorder_strength_Jz, disorder_strength_Jzx,
    disorder_strength_hx, disorder_strength_hz :
        See :class:`MixedFieldIsingHamiltonianNumpy`.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        N_pixel: int,
        J: float = 1.0,
        Jpm: float = 0.0,
        Jxx: float = 0.0,
        Jyy: float = 0.0,
        Jx: float = 0.0,
        Jy: float = 0.0,
        Jz: float = 0.0,
        Jzx: float = 0.0,
        Jcpm: float = 0.0,
        hx: float = 0.0,
        hz: float = 0.0,
        hx0: Optional[float] = None,
        hz0: Optional[float] = None,
        connectivity: str = "ring",
        central_coupling: str = "auto",
        disorder: Optional[DisorderStrategy | str] = None,
        disorder_strength: float = 0.0,
        disorder_strength_J: Optional[float] = None,
        disorder_strength_Jpm: Optional[float] = None,
        disorder_strength_Jx: Optional[float] = None,
        disorder_strength_Jz: Optional[float] = None,
        disorder_strength_Jzx: Optional[float] = None,
        disorder_strength_Jcpm: Optional[float] = None,
        disorder_strength_hx: Optional[float] = None,
        disorder_strength_hz: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        self.N_pixel = N_pixel
        self.J = J
        self.Jpm = Jpm
        self.Jxx = Jxx
        self.Jyy = Jyy
        self.Jx = Jx
        self.Jy = Jy
        self.Jz = Jz
        self.Jzx = Jzx
        self.Jcpm = Jcpm
        self.hx = hx
        self.hz = hz
        self.hx0 = hx0
        self.hz0 = hz0
        self.connectivity = connectivity
        self.central_coupling = central_coupling
        self.seed = seed

        ds = disorder_strength
        self.disorder_strength_J = (
            disorder_strength_J if disorder_strength_J is not None else ds
        )
        self.disorder_strength_Jpm = (
            disorder_strength_Jpm if disorder_strength_Jpm is not None else ds
        )
        self.disorder_strength_Jx = (
            disorder_strength_Jx if disorder_strength_Jx is not None else ds
        )
        self.disorder_strength_Jz = (
            disorder_strength_Jz if disorder_strength_Jz is not None else ds
        )
        self.disorder_strength_Jzx = (
            disorder_strength_Jzx if disorder_strength_Jzx is not None else ds
        )
        self.disorder_strength_Jcpm = (
            disorder_strength_Jcpm if disorder_strength_Jcpm is not None else ds
        )
        self.disorder_strength_hx = (
            disorder_strength_hx if disorder_strength_hx is not None else ds
        )
        self.disorder_strength_hz = (
            disorder_strength_hz if disorder_strength_hz is not None else ds
        )
        self._disorder = _resolve_disorder(disorder)

    def generate(self) -> np.ndarray:
        N = self.N_pixel + 1  # qubit 0 = central, 1…N_pixel = ring
        D = 2**N
        H = np.zeros((D, D), dtype=np.float64)
        Xs, Zs = build_pauli_operators(N)

        if self.seed is not None:
            np.random.seed(self.seed)

        # Intra-pixel ZZ interactions
        pixel_bonds = _pixel_bonds(1, self.N_pixel, self.connectivity)
        for i, j in pixel_bonds:
            j_val = _val(self._disorder, self.J, self.disorder_strength_J)
            H -= j_val * (Zs[i] @ Zs[j])

        needs_y = (
            self.Jpm != 0.0
            or self.Jxx != 0.0
            or self.Jyy != 0.0
            or self.Jy != 0.0
            or self.Jcpm != 0.0
            or (
                self._disorder is not None
                and (
                    self.disorder_strength_Jpm != 0.0
                    or self.disorder_strength_Jcpm != 0.0
                )
            )
        )
        Ys = [build_pauli_y(i, N) for i in range(N)] if needs_y else None

        # Intra-pixel +− (XY) interactions
        if self.Jpm != 0.0 or (
            self._disorder is not None and self.disorder_strength_Jpm != 0.0
        ):
            for i, j in pixel_bonds:
                jpm = _val(self._disorder, self.Jpm, self.disorder_strength_Jpm)
                # σ+σ- + σ-σ+ = (XX + YY) / 2
                H -= jpm * (Xs[i] @ Xs[j] + np.real(Ys[i] @ Ys[j])) / 2

        if self.Jxx != 0.0:
            for i, j in pixel_bonds:
                H -= self.Jxx * (Xs[i] @ Xs[j])
        if self.Jyy != 0.0:
            for i, j in pixel_bonds:
                H -= self.Jyy * np.real(Ys[i] @ Ys[j])

        # Central ↔ pixel interactions
        # For chain connectivity, couple central qubit only to the
        # start of the chain (qubit 1); otherwise to all pixel qubits.
        central_targets = _central_targets(
            1,
            self.N_pixel,
            self.connectivity,
            self.central_coupling,
        )
        for i in central_targets:
            jx = _val(self._disorder, self.Jx, self.disorder_strength_Jx)
            jy = self.Jy
            jz = _val(self._disorder, self.Jz, self.disorder_strength_Jz)
            jzx = _val(self._disorder, self.Jzx, self.disorder_strength_Jzx)
            jcpm = _val(self._disorder, self.Jcpm, self.disorder_strength_Jcpm)
            H -= jx * (Xs[0] @ Xs[i])
            if jy != 0.0:
                H -= jy * np.real(Ys[0] @ Ys[i])
            H -= jz * (Zs[0] @ Zs[i])
            H -= jzx * (Zs[0] @ Xs[i])
            if jcpm != 0.0:
                H -= jcpm * (Xs[0] @ Xs[i] + np.real(Ys[0] @ Ys[i])) / 2

        # Self-energy fields (on-site)
        # Central qubit (i=0) may have its own field values
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx0_val = _val(self._disorder, hx0_base, self.disorder_strength_hx)
        hz0_val = _val(self._disorder, hz0_base, self.disorder_strength_hz)
        H -= hx0_val * Xs[0]
        H -= hz0_val * Zs[0]
        for i in range(1, N):
            hx_val = _val(self._disorder, self.hx, self.disorder_strength_hx)
            hz_val = _val(self._disorder, self.hz, self.disorder_strength_hz)
            H -= hx_val * Xs[i]
            H -= hz_val * Zs[i]

        return H


# ===================================================================
# Dimerized single-pixel model
# ===================================================================
class DimerizedPixelHamiltonianNumpy(HamiltonianGenerator):
    r"""
    Dimerized single-pixel Hamiltonian: central qubit (index 0) coupled
    to a pixel of *N_pixel* qubits with **dimerized** intra-pixel ZZ
    interactions.

    The intra-pixel ZZ coupling pairs nearest-neighbour qubits into
    non-overlapping dimers:

    .. math::
        H_\text{intra} = -J \sum_{i=1}^{N_\text{pixel}/2}
                         \sigma^z_{2i-1}\,\sigma^z_{2i}

    so that pixel qubits (1,2), (3,4), … form independent pairs.
    *N_pixel* must be even.

    All other terms (central–pixel XX/ZZ, on-site fields) are identical
    to :class:`SinglePixelHamiltonianNumpy`.

    Parameters
    ----------
    N_pixel : int
        Number of pixel qubits (**must be even**).
    J : float
        Intra-pixel dimerized ZZ coupling.
    Jx : float
        Central–pixel XX coupling.
    Jz : float
        Central–pixel ZZ coupling.
    hx : float
        Transverse self-energy field (pixel qubits, and central when
        *hx0* is *None*).
    hz : float
        Longitudinal self-energy field (pixel qubits, and central when
        *hz0* is *None*).
    hx0 : float or None
        Transverse field on the central qubit.  Falls back to *hx* when
        *None*.
    hz0 : float or None
        Longitudinal field on the central qubit.  Falls back to *hz*
        when *None*.
    disorder, disorder_strength, disorder_strength_J,
    disorder_strength_Jx, disorder_strength_Jz, disorder_strength_hx,
    disorder_strength_hz :
        See :class:`MixedFieldIsingHamiltonianNumpy`.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        N_pixel: int,
        J: float = 1.0,
        Jx: float = 0.0,
        Jz: float = 0.0,
        hx: float = 0.0,
        hz: float = 0.0,
        hx0: Optional[float] = None,
        hz0: Optional[float] = None,
        central_coupling: str = "all",
        disorder: Optional[DisorderStrategy | str] = None,
        disorder_strength: float = 0.0,
        disorder_strength_J: Optional[float] = None,
        disorder_strength_Jx: Optional[float] = None,
        disorder_strength_Jz: Optional[float] = None,
        disorder_strength_hx: Optional[float] = None,
        disorder_strength_hz: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        if N_pixel % 2 != 0:
            raise ValueError(
                f"DimerizedPixelHamiltonian requires even N_pixel, got {N_pixel}"
            )
        self.N_pixel = N_pixel
        self.J = J
        self.Jx = Jx
        self.Jz = Jz
        self.hx = hx
        self.hz = hz
        self.hx0 = hx0
        self.hz0 = hz0
        self.central_coupling = central_coupling
        self.seed = seed

        ds = disorder_strength
        self.disorder_strength_J = (
            disorder_strength_J if disorder_strength_J is not None else ds
        )
        self.disorder_strength_Jx = (
            disorder_strength_Jx if disorder_strength_Jx is not None else ds
        )
        self.disorder_strength_Jz = (
            disorder_strength_Jz if disorder_strength_Jz is not None else ds
        )
        self.disorder_strength_hx = (
            disorder_strength_hx if disorder_strength_hx is not None else ds
        )
        self.disorder_strength_hz = (
            disorder_strength_hz if disorder_strength_hz is not None else ds
        )
        self._disorder = _resolve_disorder(disorder)

    def _dimer_bonds(self) -> list[tuple[int, int]]:
        """Return dimerized bond pairs for pixel qubits.

        Pixel qubits are indexed 1 … N_pixel.  Dimers are
        (1,2), (3,4), …, (N_pixel-1, N_pixel).
        """
        return [(2 * k + 1, 2 * k + 2) for k in range(self.N_pixel // 2)]

    def generate(self) -> np.ndarray:
        N = self.N_pixel + 1  # qubit 0 = central, 1…N_pixel = pixel
        D = 2**N
        H = np.zeros((D, D), dtype=np.float64)
        Xs, Zs = build_pauli_operators(N)

        if self.seed is not None:
            np.random.seed(self.seed)

        # Intra-pixel dimerized ZZ interactions
        for i, j in self._dimer_bonds():
            j_val = _val(self._disorder, self.J, self.disorder_strength_J)
            H -= j_val * (Zs[i] @ Zs[j])

        # Central ↔ pixel interactions (all pixel qubits)
        for i in _central_targets(1, self.N_pixel, "dimerized", self.central_coupling):
            jx = _val(self._disorder, self.Jx, self.disorder_strength_Jx)
            jz = _val(self._disorder, self.Jz, self.disorder_strength_Jz)
            H -= jx * (Xs[0] @ Xs[i])
            H -= jz * (Zs[0] @ Zs[i])

        # Self-energy fields (on-site)
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx0_val = _val(self._disorder, hx0_base, self.disorder_strength_hx)
        hz0_val = _val(self._disorder, hz0_base, self.disorder_strength_hz)
        H -= hx0_val * Xs[0]
        H -= hz0_val * Zs[0]
        for i in range(1, N):
            hx_val = _val(self._disorder, self.hx, self.disorder_strength_hx)
            hz_val = _val(self._disorder, self.hz, self.disorder_strength_hz)
            H -= hx_val * Xs[i]
            H -= hz_val * Zs[i]

        return H


# ===================================================================
# Two-pixel model
# ===================================================================
class TwoPixelHamiltonianNumpy(HamiltonianGenerator):
    r"""
    Two-pixel Hamiltonian: central qubit (index 0) sandwiched between two
    pixels of *N_pixel* qubits each.

    The central qubit couples with *opposite signs* to the two pixels.

    Parameters
    ----------
    N_pixel : int
        Number of qubits in each pixel.
    J : float
        Intra-pixel ZZ coupling.
    Jpm : float
        Intra-pixel +− (XY) coupling.
    Jx : float
        Central–pixel XX coupling.
    Jz : float
        Central–pixel ZZ coupling.
    hx : float
        Transverse self-energy field (pixel qubits, and central when
        *hx0* is *None*).
    hz : float
        Longitudinal self-energy field (pixel qubits, and central when
        *hz0* is *None*).
    hx0 : float or None
        Transverse field on the central qubit.  Falls back to *hx* when
        *None*.
    hz0 : float or None
        Longitudinal field on the central qubit.  Falls back to *hz*
        when *None*.
    connectivity : {"chain", "ring", "all_to_all"}
        Intra-pixel coupling topology.  ``"chain"`` gives an open 1-D
        chain, ``"ring"`` (default) adds a periodic closing bond, and
        ``"all_to_all"`` couples every pair of pixel qubits.
    disorder, disorder_strength, disorder_strength_J, disorder_strength_Jpm,
    disorder_strength_Jx, disorder_strength_Jz, disorder_strength_hx,
    disorder_strength_hz :
        See :class:`MixedFieldIsingHamiltonianNumpy`.
    seed : int or None
        Random seed.
    """

    def __init__(
        self,
        N_pixel: int,
        J: float = 1.0,
        Jpm: float = 0.0,
        Jxx: float = 0.0,
        Jyy: float = 0.0,
        Jx: float = 0.0,
        Jy: float = 0.0,
        Jz: float = 0.0,
        Jzx: float = 0.0,
        Jcpm: float = 0.0,
        hx: float = 0.0,
        hz: float = 0.0,
        hx0: Optional[float] = None,
        hz0: Optional[float] = None,
        connectivity: str = "ring",
        central_coupling: str = "auto",
        disorder: Optional[DisorderStrategy | str] = None,
        disorder_strength: float = 0.0,
        disorder_strength_J: Optional[float] = None,
        disorder_strength_Jpm: Optional[float] = None,
        disorder_strength_Jx: Optional[float] = None,
        disorder_strength_Jz: Optional[float] = None,
        disorder_strength_Jzx: Optional[float] = None,
        disorder_strength_Jcpm: Optional[float] = None,
        disorder_strength_hx: Optional[float] = None,
        disorder_strength_hz: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        self.N_pixel = N_pixel
        self.J = J
        self.Jpm = Jpm
        self.Jxx = Jxx
        self.Jyy = Jyy
        self.Jx = Jx
        self.Jy = Jy
        self.Jz = Jz
        self.Jzx = Jzx
        self.Jcpm = Jcpm
        self.hx = hx
        self.hz = hz
        self.hx0 = hx0
        self.hz0 = hz0
        self.connectivity = connectivity
        self.central_coupling = central_coupling
        self.seed = seed

        ds = disorder_strength
        self.disorder_strength_J = (
            disorder_strength_J if disorder_strength_J is not None else ds
        )
        self.disorder_strength_Jpm = (
            disorder_strength_Jpm if disorder_strength_Jpm is not None else ds
        )
        self.disorder_strength_Jx = (
            disorder_strength_Jx if disorder_strength_Jx is not None else ds
        )
        self.disorder_strength_Jz = (
            disorder_strength_Jz if disorder_strength_Jz is not None else ds
        )
        self.disorder_strength_Jzx = (
            disorder_strength_Jzx if disorder_strength_Jzx is not None else ds
        )
        self.disorder_strength_Jcpm = (
            disorder_strength_Jcpm if disorder_strength_Jcpm is not None else ds
        )
        self.disorder_strength_hx = (
            disorder_strength_hx if disorder_strength_hx is not None else ds
        )
        self.disorder_strength_hz = (
            disorder_strength_hz if disorder_strength_hz is not None else ds
        )

        self._disorder = _resolve_disorder(disorder)

    def generate(self) -> np.ndarray:
        N = 2 * self.N_pixel + 1
        D = 2**N
        H = np.zeros((D, D), dtype=np.float64)
        Xs, Zs = build_pauli_operators(N)

        if self.seed is not None:
            np.random.seed(self.seed)

        # Intra-pixel ZZ interactions
        all_pixel_bonds = []
        for pixel_start in [1, self.N_pixel + 1]:
            bonds = _pixel_bonds(pixel_start, self.N_pixel, self.connectivity)
            all_pixel_bonds.extend(bonds)
            for i, j in bonds:
                H -= _val(self._disorder, self.J, self.disorder_strength_J) * (
                    Zs[i] @ Zs[j]
                )

        # Intra-pixel +− (XY) interactions
        needs_y = (
            self.Jpm != 0.0
            or self.Jxx != 0.0
            or self.Jyy != 0.0
            or self.Jy != 0.0
            or self.Jcpm != 0.0
            or (
                self._disorder is not None
                and (
                    self.disorder_strength_Jpm != 0.0
                    or self.disorder_strength_Jcpm != 0.0
                )
            )
        )
        Ys = [build_pauli_y(i, N) for i in range(N)] if needs_y else None

        if self.Jpm != 0.0 or (
            self._disorder is not None and self.disorder_strength_Jpm != 0.0
        ):
            for i, j in all_pixel_bonds:
                jpm = _val(self._disorder, self.Jpm, self.disorder_strength_Jpm)
                # σ+σ- + σ-σ+ = (XX + YY) / 2
                H -= jpm * (Xs[i] @ Xs[j] + np.real(Ys[i] @ Ys[j])) / 2

        if self.Jxx != 0.0:
            for i, j in all_pixel_bonds:
                H -= self.Jxx * (Xs[i] @ Xs[j])
        if self.Jyy != 0.0:
            for i, j in all_pixel_bonds:
                H -= self.Jyy * np.real(Ys[i] @ Ys[j])

        # Central ↔ pixel interactions
        # For chain connectivity, couple central qubit only to the
        # start of each chain; otherwise to all pixel qubits.
        p1_targets = _central_targets(
            1, self.N_pixel, self.connectivity, self.central_coupling
        )
        p2_targets = _central_targets(
            self.N_pixel + 1,
            self.N_pixel,
            self.connectivity,
            self.central_coupling,
        )

        # Central ↔ pixel 1  (negative sign)
        for i in p1_targets:
            jx = _val(self._disorder, self.Jx, self.disorder_strength_Jx)
            jz = _val(self._disorder, self.Jz, self.disorder_strength_Jz)
            jzx = _val(self._disorder, self.Jzx, self.disorder_strength_Jzx)
            jcpm = _val(self._disorder, self.Jcpm, self.disorder_strength_Jcpm)
            H -= jx * (Xs[0] @ Xs[i])
            if self.Jy != 0.0:
                H -= self.Jy * np.real(Ys[0] @ Ys[i])
            H -= jz * (Zs[0] @ Zs[i])
            H -= jzx * (Zs[0] @ Xs[i])
            if jcpm != 0.0:
                H -= jcpm * (
                    Xs[0] @ Xs[i] + np.real(Ys[0] @ Ys[i])
                ) / 2

        # Central ↔ pixel 2  (positive sign — opposite coupling)
        for i in p2_targets:
            jx = _val(self._disorder, self.Jx, self.disorder_strength_Jx)
            jz = _val(self._disorder, self.Jz, self.disorder_strength_Jz)
            jzx = _val(self._disorder, self.Jzx, self.disorder_strength_Jzx)
            jcpm = _val(self._disorder, self.Jcpm, self.disorder_strength_Jcpm)
            H += jx * (Xs[0] @ Xs[i])
            if self.Jy != 0.0:
                H += self.Jy * np.real(Ys[0] @ Ys[i])
            H += jz * (Zs[0] @ Zs[i])
            H += jzx * (Zs[0] @ Xs[i])
            if jcpm != 0.0:
                H += jcpm * (
                    Xs[0] @ Xs[i] + np.real(Ys[0] @ Ys[i])
                ) / 2

        # Self-energy fields (on-site)
        # Central qubit (i=0) may have its own field values
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx0_val = _val(self._disorder, hx0_base, self.disorder_strength_hx)
        hz0_val = _val(self._disorder, hz0_base, self.disorder_strength_hz)
        H -= hx0_val * Xs[0]
        H -= hz0_val * Zs[0]
        for i in range(1, N):
            hx_val = _val(self._disorder, self.hx, self.disorder_strength_hx)
            hz_val = _val(self._disorder, self.hz, self.disorder_strength_hz)
            H -= hx_val * Xs[i]
            H -= hz_val * Zs[i]

        return H


# ===================================================================
# Central-spin (star) model
# ===================================================================
class CentralSpinHamiltonianNumpy(HamiltonianGenerator):
    r"""
    Central-spin (star) Hamiltonian: qubit 0 is coupled to *N_star*
    satellite qubits via XX and ZZ interactions, with optional on-site
    fields.

    .. math::
        H = -\sum_{i=1}^{N^*}\bigl(J_{x,i}\, X_0 X_i + J_{z,i}\, Z_0 Z_i\bigr)
            -\sum_{i=0}^{N}\bigl(h_{x,i}\, X_i + h_{z,i}\, Z_i\bigr)

    Parameters
    ----------
    N_star : int
        Number of satellite qubits.
    Jx, Jz : float
        Clean coupling constants.
    hx, hz : float
        On-site (self-energy) field strengths (satellite qubits, and
        central when *hx0* / *hz0* are *None*).
    hx0 : float or None
        Transverse field on the central qubit.  Falls back to *hx* when
        *None*.
    hz0 : float or None
        Longitudinal field on the central qubit.  Falls back to *hz*
        when *None*.
    disorder : DisorderStrategy or str or None
        Strategy for generating disordered values.
    disorder_strength : float
        Global disorder width (used for all terms unless overridden).
    disorder_strength_Jx, disorder_strength_Jz : float or None
        Per-axis coupling disorder widths.
    disorder_strength_hx, disorder_strength_hz : float or None
        Per-axis self-energy disorder widths.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        N_star: int,
        Jx: float = 0.0,
        Jz: float = 0.0,
        hx: float = 0.0,
        hz: float = 0.0,
        hx0: Optional[float] = None,
        hz0: Optional[float] = None,
        disorder: Optional[DisorderStrategy | str] = None,
        disorder_strength: float = 0.0,
        # Preferred per-parameter names
        disorder_strength_Jx: Optional[float] = None,
        disorder_strength_Jz: Optional[float] = None,
        disorder_strength_hx: Optional[float] = None,
        disorder_strength_hz: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        self.N_star = N_star
        self.Jx = Jx
        self.Jz = Jz
        self.hx = hx
        self.hz = hz
        self.hx0 = hx0
        self.hz0 = hz0
        self.seed = seed

        ds = disorder_strength
        self.disorder_strength_Jx = (
            disorder_strength_Jx if disorder_strength_Jx is not None else ds
        )
        self.disorder_strength_Jz = (
            disorder_strength_Jz if disorder_strength_Jz is not None else ds
        )
        self.disorder_strength_hx = (
            disorder_strength_hx if disorder_strength_hx is not None else ds
        )
        self.disorder_strength_hz = (
            disorder_strength_hz if disorder_strength_hz is not None else ds
        )

        self._disorder = _resolve_disorder(disorder)

    def generate(self) -> np.ndarray:
        N = self.N_star + 1
        D = 2**N
        H = np.zeros((D, D), dtype=np.float64)
        Xs, Zs = build_pauli_operators(N)

        if self.seed is not None:
            np.random.seed(self.seed)

        # Coupling terms
        for i in range(1, N):
            jx = _val(self._disorder, self.Jx, self.disorder_strength_Jx)
            jz = _val(self._disorder, self.Jz, self.disorder_strength_Jz)
            H -= jx * (Xs[0] @ Xs[i])
            H -= jz * (Zs[0] @ Zs[i])

        # Self-energy fields (on-site)
        # Central qubit (i=0) may have its own field values
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx0_val = _val(self._disorder, hx0_base, self.disorder_strength_hx)
        hz0_val = _val(self._disorder, hz0_base, self.disorder_strength_hz)
        H -= hx0_val * Xs[0]
        H -= hz0_val * Zs[0]
        for i in range(1, N):
            hx_val = _val(self._disorder, self.hx, self.disorder_strength_hx)
            hz_val = _val(self._disorder, self.hz, self.disorder_strength_hz)
            H -= hx_val * Xs[i]
            H -= hz_val * Zs[i]

        return H
