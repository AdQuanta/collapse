"""
QuSpin-Based Hamiltonian Generators
====================================

Sparse-matrix implementations of various spin-model Hamiltonians using
the `QuSpin <https://quspin.github.io/QuSpin/>`_ library.  Each class
mirrors its NumPy counterpart in :mod:`collapse.hamiltonians.numpy_hamiltonians`
but delegates the operator algebra to QuSpin for better scalability.

The dense matrix is returned via ``H.toarray()`` so that the
:class:`~collapse.hamiltonians.base.HamiltonianGenerator` interface
is satisfied uniformly.

Every Hamiltonian supports optional disorder on both **coupling
strengths** and **self-energies** (on-site fields) via a
:class:`~collapse.disorder.DisorderStrategy`.

Symmetry-aware diagonalisation
------------------------------
Each class exposes a :meth:`diagonalize` method that can exploit
conserved symmetries (magnetisation, cyclic pixel-ring shift) to
decompose the Hilbert space into smaller blocks, dramatically
accelerating exact diagonalisation.  The behaviour is controlled by the
``use_symmetry`` constructor flag (default *True*).
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
from quspin.basis import spin_basis_1d, spin_basis_general
from quspin.operators import hamiltonian

from collapse.disorder import DisorderStrategy
from collapse.detector_graphs import DetectorGraphSpec
from collapse.hamiltonians.base import HamiltonianGenerator
from collapse.hamiltonians.numpy_hamiltonians import (
    _resolve_disorder,
    _val,
    _central_targets,
    _pixel_bonds,
    _pixel_ring_second_neighbor_bonds,
)


# ===================================================================
# Shared helpers
# ===================================================================
def _has_xx_or_x(
    Jx: float,
    hx: float,
    disorder: Optional[DisorderStrategy],
    ds_Jx: float,
    ds_hx: float,
    hx0: Optional[float] = None,
) -> bool:
    """Return *True* if the Hamiltonian contains XX or X terms that
    break total-Sz conservation."""
    if Jx != 0.0:
        return True
    if hx != 0.0:
        return True
    if hx0 is not None and hx0 != 0.0:
        return True
    # Even with Jx==0 or hx==0, active disorder on those channels
    # can generate non-zero XX / X terms.
    if disorder is not None and ds_Jx != 0.0:
        return True
    if disorder is not None and ds_hx != 0.0:
        return True
    return False


def _has_disorder(
    disorder: Optional[DisorderStrategy],
    *strengths: float,
) -> bool:
    """Return *True* if any disorder channel is active."""
    if disorder is None:
        return False
    return any(s != 0.0 for s in strengths)


def _central_couples_to_all_sites(
    n_pixel: int,
    connectivity: str,
    central_coupling: str,
) -> bool:
    """Return whether the central coupling preserves pixel-site permutations."""
    targets = _central_targets(1, n_pixel, connectivity, central_coupling)
    return targets == list(range(1, n_pixel + 1))


def _diag_in_sectors(
    N: int,
    static: list,
    sector_bases: list,
) -> Tuple[np.ndarray, np.ndarray]:
    """Diagonalise *H* block-by-block over *sector_bases* and
    concatenate eigenvectors projected into the full computational
    basis.

    Returns ``(E, V)`` with shapes ``(D,)`` and ``(D, D)``."""
    all_E: list[np.ndarray] = []
    all_V: list[np.ndarray] = []

    for basis_k in sector_bases:
        if basis_k.Ns == 0:
            continue
        H_k = hamiltonian(
            static,
            [],
            basis=basis_k,
            dtype=np.complex128,
            check_symm=False,
            check_herm=False,
        )
        Ek, Vk = np.linalg.eigh(H_k.toarray())
        # Project eigenvectors back to the full computational basis
        Vk_full = basis_k.project_from(Vk, sparse=False)
        all_E.append(Ek)
        all_V.append(Vk_full)

    E = np.concatenate(all_E)
    V = np.hstack(all_V)
    return E, V


def _collect_sectors(
    static: list,
    sector_bases: list,
    *,
    relative_evolution_local: bool,
    symmetry_label: str,
) -> list:
    """Diagonalise *H* in each sector and return per-sector data
    (E, V in reduced basis, states) without projecting to the full
    computational basis."""
    sectors: list[dict] = []
    for basis_k in sector_bases:
        if basis_k.Ns == 0:
            continue
        H_k = hamiltonian(
            static,
            [],
            basis=basis_k,
            dtype=np.complex128,
            check_symm=False,
            check_herm=False,
        )
        Ek, Vk = np.linalg.eigh(H_k.toarray())
        sectors.append(
            {
                "E": Ek,
                "V": Vk,
                "states": basis_k.states.copy(),
                "basis": basis_k,
                "central_top_bit": 1,
                "relative_evolution_local": relative_evolution_local,
                "symmetry_label": symmetry_label,
            }
        )
    return sectors


def _collect_full_sector_quspin(static: list, N: int) -> list:
    """Return a single dense QuSpin-basis sector with correct basis metadata."""

    basis = spin_basis_1d(L=N)
    H = hamiltonian(
        static,
        [],
        basis=basis,
        dtype=np.complex128,
        check_symm=False,
        check_herm=False,
    )
    E, V = np.linalg.eigh(H.toarray())
    return [
        {
            "E": E,
            "V": V,
            "states": basis.states.copy(),
            "basis": basis,
            "central_top_bit": 1,
            "relative_evolution_local": True,
            "symmetry_label": "full",
        }
    ]


# ===================================================================
# Central-spin model (QuSpin)
# ===================================================================
class CentralSpinHamiltonianQuSpin(HamiltonianGenerator):
    r"""
    Central-spin Hamiltonian built with QuSpin.

    See :class:`~collapse.hamiltonians.numpy_hamiltonians.CentralSpinHamiltonianNumpy`
    for parameter documentation.
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
        central_coupling: str = "all",
        disorder: Optional[DisorderStrategy | str] = None,
        disorder_strength: float = 0.0,
        disorder_strength_Jx: Optional[float] = None,
        disorder_strength_Jz: Optional[float] = None,
        disorder_strength_hx: Optional[float] = None,
        disorder_strength_hz: Optional[float] = None,
        seed: Optional[int] = None,
        use_symmetry: bool = True,
    ):
        self.N_star = N_star
        self.Jx = Jx
        self.Jz = Jz
        self.hx = hx
        self.hz = hz
        self.hx0 = hx0
        self.hz0 = hz0
        self.central_coupling = central_coupling
        self.seed = seed
        self.use_symmetry = use_symmetry

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

    def _build_static(self) -> Tuple[list, int]:
        """Build the static operator list and return ``(static, N)``."""
        N = self.N_star + 1
        if self.seed is not None:
            np.random.seed(self.seed)

        jx_list: list[list] = []
        jz_list: list[list] = []
        for i in range(1, N):
            jx_val = _val(self._disorder, self.Jx, self.disorder_strength_Jx)
            jz_val = _val(self._disorder, self.Jz, self.disorder_strength_Jz)
            jx_list.append([-jx_val, 0, i])
            jz_list.append([-jz_val, 0, i])

        hx_list: list[list] = []
        hz_list: list[list] = []
        # Central qubit (i=0) may have its own field values
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx_list.append([-_val(self._disorder, hx0_base, self.disorder_strength_hx), 0])
        hz_list.append([-_val(self._disorder, hz0_base, self.disorder_strength_hz), 0])
        for i in range(1, N):
            hx_val = _val(self._disorder, self.hx, self.disorder_strength_hx)
            hz_val = _val(self._disorder, self.hz, self.disorder_strength_hz)
            hx_list.append([-hx_val, i])
            hz_list.append([-hz_val, i])

        static = [["xx", jx_list], ["zz", jz_list]]
        if any(v[0] != 0 for v in hx_list):
            static.append(["x", hx_list])
        if any(v[0] != 0 for v in hz_list):
            static.append(["z", hz_list])

        return static, N

    def generate(self) -> np.ndarray:
        static, N = self._build_static()
        basis = spin_basis_1d(L=N)
        H = hamiltonian(
            static,
            [],
            basis=basis,
            dtype=np.float64,
            check_symm=False,
            check_herm=False,
        )
        return H.toarray()

    def diagonalize(self) -> Tuple[np.ndarray, np.ndarray]:
        static, N = self._build_static()

        # Check if magnetisation symmetry can be used
        has_xx_x = _has_xx_or_x(
            self.Jx,
            self.hx,
            self._disorder,
            self.disorder_strength_Jx,
            self.disorder_strength_hx,
            hx0=self.hx0,
        )

        if not self.use_symmetry or has_xx_x:
            # Fallback: full diagonalisation
            return super().diagonalize()

        # Sz-conserving: diagonalise per magnetisation sector
        bases = [spin_basis_general(N, Nup=m) for m in range(N + 1)]
        return _diag_in_sectors(N, static, bases)

    def diagonalize_sectors(self) -> list:
        static, N = self._build_static()
        has_xx_x = _has_xx_or_x(
            self.Jx,
            self.hx,
            self._disorder,
            self.disorder_strength_Jx,
            self.disorder_strength_hx,
            hx0=self.hx0,
        )

        if not self.use_symmetry or has_xx_x:
            return _collect_full_sector_quspin(static, N)

        bases = [spin_basis_general(N, Nup=m) for m in range(N + 1)]
        return _collect_sectors(
            static,
            bases,
            relative_evolution_local=False,
            symmetry_label="magnetization",
        )


# ===================================================================
# Mixed-field Ising model (QuSpin)
# ===================================================================
class MixedFieldIsingHamiltonianQuSpin(HamiltonianGenerator):
    r"""
    Mixed-field Ising Hamiltonian built with QuSpin.

    See :class:`~collapse.hamiltonians.numpy_hamiltonians.MixedFieldIsingHamiltonianNumpy`
    for parameter documentation.
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
        use_symmetry: bool = True,
    ):
        self.N = N
        self.J = J
        self.hx = hx
        self.hz = hz
        self.seed = seed
        self.use_symmetry = use_symmetry

        ds = disorder_strength
        self.disorder_strength_J = (
            disorder_strength_J if disorder_strength_J is not None else ds
        )
        self.disorder_strength_hx = (
            disorder_strength_hx if disorder_strength_hx is not None else ds
        )
        self.disorder_strength_hz = (
            disorder_strength_hz if disorder_strength_hz is not None else ds
        )
        self._disorder = _resolve_disorder(disorder)

    def _build_static(self) -> list:
        """Build the static operator list."""
        if self.seed is not None:
            np.random.seed(self.seed)

        j_list = [
            [
                -_val(self._disorder, self.J, self.disorder_strength_J),
                i,
                (i + 1) % self.N,
            ]
            for i in range(self.N)
        ]
        hx_list = [
            [-_val(self._disorder, self.hx, self.disorder_strength_hx), i]
            for i in range(self.N)
        ]
        hz_list = [
            [-_val(self._disorder, self.hz, self.disorder_strength_hz), i]
            for i in range(self.N)
        ]
        return [["zz", j_list], ["x", hx_list], ["z", hz_list]]

    def generate(self) -> np.ndarray:
        static = self._build_static()
        basis = spin_basis_1d(L=self.N)
        H = hamiltonian(
            static,
            [],
            basis=basis,
            dtype=np.complex128,
            check_symm=False,
            check_herm=False,
        )
        return H.toarray()

    def diagonalize(self) -> Tuple[np.ndarray, np.ndarray]:
        static = self._build_static()
        N = self.N

        # MFI has X terms (transverse field) — check if hx==0
        has_x = (self.hx != 0.0) or (
            self._disorder is not None and self.disorder_strength_hx != 0.0
        )

        if not self.use_symmetry or has_x:
            return super().diagonalize()

        # Sz-conserving: diagonalise per magnetisation sector
        bases = [spin_basis_general(N, Nup=m) for m in range(N + 1)]
        return _diag_in_sectors(N, static, bases)

    def diagonalize_sectors(self) -> list:
        static = self._build_static()
        N = self.N
        has_x = (self.hx != 0.0) or (
            self._disorder is not None and self.disorder_strength_hx != 0.0
        )

        if not self.use_symmetry or has_x:
            return _collect_full_sector_quspin(static, N)

        bases = [spin_basis_general(N, Nup=m) for m in range(N + 1)]
        return _collect_sectors(
            static,
            bases,
            relative_evolution_local=False,
            symmetry_label="magnetization",
        )


# ===================================================================
# Single-pixel model (QuSpin)
# ===================================================================
class SinglePixelHamiltonianQuSpin(HamiltonianGenerator):
    r"""
    Single-pixel Hamiltonian built with QuSpin.

    See :class:`~collapse.hamiltonians.numpy_hamiltonians.SinglePixelHamiltonianNumpy`
    for parameter documentation.
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
        use_symmetry: bool = True,
        J2: float = 0.0,
        Jpm2: float = 0.0,
        disorder_strength_J2: Optional[float] = None,
        disorder_strength_Jpm2: Optional[float] = None,
        graph_spec: DetectorGraphSpec | None = None,
    ):
        self.N_pixel = N_pixel
        self.J = J
        self.Jpm = Jpm
        self.J2 = J2
        self.Jpm2 = Jpm2
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
        self.graph_spec = graph_spec or DetectorGraphSpec(kind=connectivity)
        self.central_coupling = central_coupling
        self.seed = seed
        self.use_symmetry = use_symmetry

        ds = disorder_strength
        self.disorder_strength_J = (
            disorder_strength_J if disorder_strength_J is not None else ds
        )
        self.disorder_strength_Jpm = (
            disorder_strength_Jpm if disorder_strength_Jpm is not None else ds
        )
        self.disorder_strength_J2 = (
            disorder_strength_J2 if disorder_strength_J2 is not None else ds
        )
        self.disorder_strength_Jpm2 = (
            disorder_strength_Jpm2 if disorder_strength_Jpm2 is not None else ds
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

        if self.connectivity != "ring" and (
            self.J2 != 0.0
            or self.Jpm2 != 0.0
            or (self._disorder is not None and self.disorder_strength_J2 != 0.0)
            or (self._disorder is not None and self.disorder_strength_Jpm2 != 0.0)
        ):
            raise ValueError("J2 and Jpm2 are defined only for ring connectivity")

    def _build_static(self) -> Tuple[list, int]:
        """Build static operator list and return ``(static, N)``."""
        N = self.N_pixel + 1
        if self.seed is not None:
            np.random.seed(self.seed)

        pixel_zz = []
        pixel_xx = []
        pixel_yy = []
        pm_list = []
        second_zz = []
        second_pm = []
        for i, j in _pixel_bonds(
            1, self.N_pixel, self.connectivity, self.graph_spec
        ):
            pixel_zz.append(
                [-_val(self._disorder, self.J, self.disorder_strength_J), i, j]
            )
            if self.Jxx != 0.0:
                pixel_xx.append([-self.Jxx, i, j])
            if self.Jyy != 0.0:
                pixel_yy.append([-self.Jyy, i, j])
            jpm_val = _val(self._disorder, self.Jpm, self.disorder_strength_Jpm)
            if jpm_val != 0.0:
                pm_list.append([-jpm_val / 4, i, j])
        if self.connectivity == "ring":
            for i, j in _pixel_ring_second_neighbor_bonds(1, self.N_pixel):
                j2_val = _val(
                    self._disorder, self.J2, self.disorder_strength_J2
                )
                if j2_val != 0.0:
                    second_zz.append([-j2_val, i, j])
                jpm2_val = _val(
                    self._disorder, self.Jpm2, self.disorder_strength_Jpm2
                )
                if jpm2_val != 0.0:
                    second_pm.append([-jpm2_val / 4, i, j])
        central_targets = _central_targets(
            1,
            self.N_pixel,
            self.connectivity,
            self.central_coupling,
        )
        jx_list = [
            [-_val(self._disorder, self.Jx, self.disorder_strength_Jx), 0, i]
            for i in central_targets
        ]
        jy_list = [
            [-self.Jy, 0, i]
            for i in central_targets
        ]
        jz_list = [
            [-_val(self._disorder, self.Jz, self.disorder_strength_Jz), 0, i]
            for i in central_targets
        ]
        jzx_list = [
            [-_val(self._disorder, self.Jzx, self.disorder_strength_Jzx), 0, i]
            for i in central_targets
        ]
        cpm_list = []
        for i in central_targets:
            jcpm_val = _val(self._disorder, self.Jcpm, self.disorder_strength_Jcpm)
            if jcpm_val != 0.0:
                cpm_list.append([-jcpm_val / 4, 0, i])
        # Central qubit (i=0) may have its own field values
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx_list = [
            [-_val(self._disorder, hx0_base, self.disorder_strength_hx), 0]
        ] + [
            [-_val(self._disorder, self.hx, self.disorder_strength_hx), i]
            for i in range(1, N)
        ]
        hz_list = [
            [-_val(self._disorder, hz0_base, self.disorder_strength_hz), 0]
        ] + [
            [-_val(self._disorder, self.hz, self.disorder_strength_hz), i]
            for i in range(1, N)
        ]

        static = [["zz", pixel_zz], ["xx", jx_list], ["zz", jz_list]]
        if pixel_xx:
            static.append(["xx", pixel_xx])
        if pixel_yy:
            static.append(["yy", pixel_yy])
        if any(v[0] != 0 for v in jy_list):
            static.append(["yy", jy_list])
        if any(v[0] != 0 for v in jzx_list):
            static.append(["zx", jzx_list])
        if pm_list:
            static.append(["+-", pm_list])
            static.append(["-+", pm_list])
        if second_zz:
            static.append(["zz", second_zz])
        if second_pm:
            static.append(["+-", second_pm])
            static.append(["-+", second_pm])
        if cpm_list:
            static.append(["+-", cpm_list])
            static.append(["-+", cpm_list])
        if any(v[0] != 0 for v in hx_list):
            static.append(["x", hx_list])
        if any(v[0] != 0 for v in hz_list):
            static.append(["z", hz_list])

        return static, N

    def generate(self) -> np.ndarray:
        static, N = self._build_static()
        basis = spin_basis_1d(L=N)
        H = hamiltonian(
            static,
            [],
            basis=basis,
            dtype=np.float64,
            check_symm=False,
            check_herm=False,
        )
        return H.toarray()

    def diagonalize(self) -> Tuple[np.ndarray, np.ndarray]:
        static, N = self._build_static()

        has_xx_x = _has_xx_or_x(
            self.Jx,
            self.hx,
            self._disorder,
            self.disorder_strength_Jx,
            self.disorder_strength_hx,
            hx0=self.hx0,
        )
        # ZX interaction also breaks Sz conservation (X on pixel)
        has_zx = self.Jzx != 0.0 or (
            self._disorder is not None and self.disorder_strength_Jzx != 0.0
        )
        has_pairing = self.Jxx != 0.0 or self.Jyy != 0.0 or self.Jy != 0.0
        has_disord = _has_disorder(
            self._disorder,
            self.disorder_strength_J,
            self.disorder_strength_Jpm,
            self.disorder_strength_J2,
            self.disorder_strength_Jpm2,
            self.disorder_strength_Jx,
            self.disorder_strength_Jz,
            self.disorder_strength_Jzx,
            self.disorder_strength_Jcpm,
            self.disorder_strength_hx,
            self.disorder_strength_hz,
        )
        central_preserves_shift = _central_couples_to_all_sites(
            self.N_pixel,
            self.connectivity,
            self.central_coupling,
        )
        can_use_shift = (
            self.connectivity == "ring"
            and self.N_pixel > 1
            and not has_disord
            and central_preserves_shift
        )
        can_use_mag = not has_xx_x and not has_zx and not has_pairing
        has_single_x = (
            self.hx != 0.0
            or (self.hx0 is not None and self.hx0 != 0.0)
            or (
                self._disorder is not None
                and self.disorder_strength_hx != 0.0
            )
            or has_zx
        )
        can_use_mag_parity = not has_single_x

        if not self.use_symmetry or (
            not can_use_shift and not can_use_mag and not can_use_mag_parity
        ):
            return super().diagonalize()

        # Build cyclic-shift permutation for pixel sites 1..N_pixel
        T_pixel = None
        if can_use_shift:
            T_pixel = list(range(N))
            for k in range(self.N_pixel):
                T_pixel[1 + k] = 1 + (k + 1) % self.N_pixel
            T_pixel = np.array(T_pixel)

        # Enumerate symmetry sectors
        bases: list = []
        if can_use_mag and can_use_shift:
            for m in range(N + 1):
                for kp in range(self.N_pixel):
                    bases.append(spin_basis_general(N, Nup=m, kblock=(T_pixel, kp)))
        elif can_use_shift:
            for kp in range(self.N_pixel):
                bases.append(spin_basis_general(N, kblock=(T_pixel, kp)))
        elif can_use_mag:
            for m in range(N + 1):
                bases.append(spin_basis_general(N, Nup=m))
        else:
            for parity in (0, 1):
                bases.append(
                    spin_basis_general(N, Nup=list(range(parity, N + 1, 2)))
                )

        return _diag_in_sectors(N, static, bases)

    def diagonalize_sectors(self) -> list:
        static, N = self._build_static()
        has_xx_x = _has_xx_or_x(
            self.Jx,
            self.hx,
            self._disorder,
            self.disorder_strength_Jx,
            self.disorder_strength_hx,
            hx0=self.hx0,
        )
        has_zx = self.Jzx != 0.0 or (
            self._disorder is not None and self.disorder_strength_Jzx != 0.0
        )
        has_pairing = self.Jxx != 0.0 or self.Jyy != 0.0 or self.Jy != 0.0
        has_disord = _has_disorder(
            self._disorder,
            self.disorder_strength_J,
            self.disorder_strength_Jpm,
            self.disorder_strength_J2,
            self.disorder_strength_Jpm2,
            self.disorder_strength_Jx,
            self.disorder_strength_Jz,
            self.disorder_strength_Jzx,
            self.disorder_strength_Jcpm,
            self.disorder_strength_hx,
            self.disorder_strength_hz,
        )
        central_preserves_shift = _central_couples_to_all_sites(
            self.N_pixel,
            self.connectivity,
            self.central_coupling,
        )
        can_use_shift = (
            self.connectivity == "ring"
            and self.N_pixel > 1
            and not has_disord
            and central_preserves_shift
        )
        can_use_mag = not has_xx_x and not has_zx and not has_pairing
        has_single_x = (
            self.hx != 0.0
            or (self.hx0 is not None and self.hx0 != 0.0)
            or (
                self._disorder is not None
                and self.disorder_strength_hx != 0.0
            )
            or has_zx
        )
        can_use_mag_parity = not has_single_x
        if not self.use_symmetry or (
            not can_use_shift and not can_use_mag and not can_use_mag_parity
        ):
            return _collect_full_sector_quspin(static, N)

        T_pixel = None
        if can_use_shift:
            T_pixel = list(range(N))
            for k in range(self.N_pixel):
                T_pixel[1 + k] = 1 + (k + 1) % self.N_pixel
            T_pixel = np.array(T_pixel)

        bases: list = []
        if can_use_shift:
            for kp in range(self.N_pixel):
                bases.append(spin_basis_general(N, kblock=(T_pixel, kp)))
            return _collect_sectors(
                static,
                bases,
                relative_evolution_local=True,
                symmetry_label="pixel_shift",
            )

        # Magnetisation or magnetisation-parity sectors are valid for H, but
        # U10 connects different central-spin slices. The analyzer reconstructs
        # the exact full U00/U10 blocks by projection.
        if can_use_mag:
            for m in range(N + 1):
                bases.append(spin_basis_general(N, Nup=m))
            label = "magnetization"
        else:
            for parity in (0, 1):
                bases.append(
                    spin_basis_general(N, Nup=list(range(parity, N + 1, 2)))
                )
            label = "magnetization_parity"
        return _collect_sectors(
            static,
            bases,
            relative_evolution_local=False,
            symmetry_label=label,
        )


# ===================================================================
# Dimerized single-pixel model (QuSpin)
# ===================================================================
class DimerizedPixelHamiltonianQuSpin(HamiltonianGenerator):
    r"""
    Dimerized single-pixel Hamiltonian built with QuSpin.

    See :class:`~collapse.hamiltonians.numpy_hamiltonians.DimerizedPixelHamiltonianNumpy`
    for parameter documentation.
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
        use_symmetry: bool = True,
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
        self.use_symmetry = use_symmetry

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
        """Return dimerized bond pairs: (1,2), (3,4), …"""
        return [(2 * k + 1, 2 * k + 2) for k in range(self.N_pixel // 2)]

    def _build_static(self) -> Tuple[list, int]:
        """Build static operator list and return ``(static, N)``."""
        N = self.N_pixel + 1
        if self.seed is not None:
            np.random.seed(self.seed)

        # Intra-pixel dimerized ZZ
        pixel_zz = [
            [-_val(self._disorder, self.J, self.disorder_strength_J), i, j]
            for i, j in self._dimer_bonds()
        ]

        # Central ↔ all pixel qubits
        central_targets = _central_targets(
            1,
            self.N_pixel,
            "dimerized",
            self.central_coupling,
        )
        jx_list = [
            [-_val(self._disorder, self.Jx, self.disorder_strength_Jx), 0, i]
            for i in central_targets
        ]
        jz_list = [
            [-_val(self._disorder, self.Jz, self.disorder_strength_Jz), 0, i]
            for i in central_targets
        ]

        # Self-energy fields
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx_list = [
            [-_val(self._disorder, hx0_base, self.disorder_strength_hx), 0]
        ] + [
            [-_val(self._disorder, self.hx, self.disorder_strength_hx), i]
            for i in range(1, N)
        ]
        hz_list = [
            [-_val(self._disorder, hz0_base, self.disorder_strength_hz), 0]
        ] + [
            [-_val(self._disorder, self.hz, self.disorder_strength_hz), i]
            for i in range(1, N)
        ]

        static = [["zz", pixel_zz], ["xx", jx_list], ["zz", jz_list]]
        if any(v[0] != 0 for v in hx_list):
            static.append(["x", hx_list])
        if any(v[0] != 0 for v in hz_list):
            static.append(["z", hz_list])

        return static, N

    def generate(self) -> np.ndarray:
        static, N = self._build_static()
        basis = spin_basis_1d(L=N)
        H = hamiltonian(
            static,
            [],
            basis=basis,
            dtype=np.float64,
            check_symm=False,
            check_herm=False,
        )
        return H.toarray()

    # ---------------------------------------------------------------
    # Symmetry helpers
    # ---------------------------------------------------------------
    def _symmetry_info(self) -> dict:
        """Determine which symmetries can be exploited.

        Returns a dict with keys ``can_use_mag``, ``can_use_dimer_shift``,
        ``can_use_swap``, ``T_dimer``, ``P_all``, ``n_d``, ``N``.

        Three mutually commuting symmetries are available:

        1. **Magnetisation (Nup)** — conserved when all X / XX terms
           vanish (``Jx = hx = hx0 = 0``).
        2. **Cyclic dimer shift** T_dimer — cyclically permutes entire
           dimers: (1,2)→(3,4)→…→(1,2).  Gives ``n_d`` momentum
           sectors.  Requires no disorder *and* ``n_d > 1``.
        3. **Simultaneous intra-dimer swap** P_all — swaps both qubits
           inside every dimer at once (1↔2, 3↔4, …).  This is a Z₂
           parity and gives 2 sectors.  Requires no disorder.

        Because the central qubit couples identically to every pixel
        qubit (XX and ZZ) and the dimer ZZ couplings are all equal
        (when disorder-free), both T_dimer and P_all commute with the
        Hamiltonian even when Jx != 0 or hx != 0.  Local central-coupling
        geometries break those detector permutations, so then only valid
        remaining symmetries such as magnetisation may be used.
        """
        N = self.N_pixel + 1
        n_d = self.N_pixel // 2

        has_xx_x = _has_xx_or_x(
            self.Jx,
            self.hx,
            self._disorder,
            self.disorder_strength_Jx,
            self.disorder_strength_hx,
            hx0=self.hx0,
        )
        has_disord = _has_disorder(
            self._disorder,
            self.disorder_strength_J,
            self.disorder_strength_Jx,
            self.disorder_strength_Jz,
            self.disorder_strength_hx,
            self.disorder_strength_hz,
        )

        central_preserves_dimer_sym = _central_couples_to_all_sites(
            self.N_pixel,
            "ring",
            self.central_coupling,
        )
        can_use_mag = not has_xx_x
        can_use_swap = not has_disord and central_preserves_dimer_sym
        can_use_dimer_shift = can_use_swap and n_d > 1

        # Build permutation arrays (only when needed)
        T_dimer = None
        if can_use_dimer_shift:
            T = list(range(N))
            for k in range(n_d):
                # Dimer k → dimer (k+1) % n_d
                T[2 * k + 1] = 2 * ((k + 1) % n_d) + 1
                T[2 * k + 2] = 2 * ((k + 1) % n_d) + 2
            T_dimer = np.array(T)

        P_all = None
        if can_use_swap:
            P = list(range(N))
            for k in range(n_d):
                P[2 * k + 1], P[2 * k + 2] = 2 * k + 2, 2 * k + 1
            P_all = np.array(P)

        return dict(
            can_use_mag=can_use_mag,
            can_use_dimer_shift=can_use_dimer_shift,
            can_use_swap=can_use_swap,
            T_dimer=T_dimer,
            P_all=P_all,
            n_d=n_d,
            N=N,
        )

    def _build_sector_bases(self, info: dict, *, include_mag: bool = True) -> list:
        """Enumerate symmetry-sector bases from *info* dict."""
        N = info["N"]
        n_d = info["n_d"]
        can_use_mag = include_mag and info["can_use_mag"]
        can_use_dimer_shift = info["can_use_dimer_shift"]
        can_use_swap = info["can_use_swap"]
        T_dimer = info["T_dimer"]
        P_all = info["P_all"]

        bases: list = []

        # Helper: keyword dict for spin_basis_general
        def _make_basis(**extra_kw):
            bases.append(spin_basis_general(N, **extra_kw))

        mag_range = range(N + 1) if can_use_mag else [None]
        shift_range = range(n_d) if can_use_dimer_shift else [None]
        swap_range = range(2) if can_use_swap else [None]

        for m in mag_range:
            for k in shift_range:
                for p in swap_range:
                    kw: dict = {}
                    if m is not None:
                        kw["Nup"] = m
                    if k is not None:
                        kw["kblock"] = (T_dimer, k)
                    if p is not None:
                        kw["pblock"] = (P_all, p)
                    _make_basis(**kw)

        return bases

    # ---------------------------------------------------------------
    # Diagonalisation
    # ---------------------------------------------------------------
    def diagonalize(self) -> Tuple[np.ndarray, np.ndarray]:
        static, N = self._build_static()
        info = self._symmetry_info()

        any_sym = (
            info["can_use_mag"]
            or info["can_use_dimer_shift"]
            or info["can_use_swap"]
        )
        if not self.use_symmetry or not any_sym:
            return super().diagonalize()

        bases = self._build_sector_bases(info)
        return _diag_in_sectors(N, static, bases)

    def diagonalize_sectors(self) -> list:
        static, N = self._build_static()
        info = self._symmetry_info()

        any_sym = (
            info["can_use_mag"]
            or info["can_use_dimer_shift"]
            or info["can_use_swap"]
        )
        if not self.use_symmetry or not any_sym:
            return _collect_full_sector_quspin(static, N)

        spatial_sym = info["can_use_dimer_shift"] or info["can_use_swap"]
        bases = self._build_sector_bases(info, include_mag=not spatial_sym)
        return _collect_sectors(
            static,
            bases,
            relative_evolution_local=spatial_sym,
            symmetry_label=(
                "dimer_spatial" if spatial_sym else "magnetization"
            ),
        )


# ===================================================================
# Two-pixel model (QuSpin)
# ===================================================================
class TwoPixelHamiltonianQuSpin(HamiltonianGenerator):
    r"""
    Two-pixel Hamiltonian built with QuSpin.

    See :class:`~collapse.hamiltonians.numpy_hamiltonians.TwoPixelHamiltonianNumpy`
    for parameter documentation.
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
        use_symmetry: bool = True,
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
        self.use_symmetry = use_symmetry

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

    def _build_static(self) -> Tuple[list, int]:
        """Build static operator list and return ``(static, N)``."""
        N = 2 * self.N_pixel + 1
        if self.seed is not None:
            np.random.seed(self.seed)

        static: list = []

        # Intra-pixel ZZ interactions and +- (XY) interactions
        pm_list: list[list] = []
        pixel_xx: list[list] = []
        pixel_yy: list[list] = []
        for pixel_start in [1, self.N_pixel + 1]:
            interactions: list[list] = []
            for i, j in _pixel_bonds(pixel_start, self.N_pixel, self.connectivity):
                interactions.append(
                    [-_val(self._disorder, self.J, self.disorder_strength_J), i, j]
                )
                jpm_val = _val(self._disorder, self.Jpm, self.disorder_strength_Jpm)
                if jpm_val != 0.0:
                    pm_list.append([-jpm_val / 4, i, j])
                if self.Jxx != 0.0:
                    pixel_xx.append([-self.Jxx, i, j])
                if self.Jyy != 0.0:
                    pixel_yy.append([-self.Jyy, i, j])
            static.append(["zz", interactions])

        if pm_list:
            static.append(["+-", pm_list])
            static.append(["-+", pm_list])
        if pixel_xx:
            static.append(["xx", pixel_xx])
        if pixel_yy:
            static.append(["yy", pixel_yy])

        # Central <-> pixel interactions
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

        jx_list: list[list] = []
        jy_list: list[list] = []
        jz_list: list[list] = []
        jzx_list: list[list] = []
        cpm_list: list[list] = []

        for i in p1_targets:
            # Pixel 1 (negative sign)
            jx_list.append(
                [-_val(self._disorder, self.Jx, self.disorder_strength_Jx), 0, i]
            )
            jz_list.append(
                [-_val(self._disorder, self.Jz, self.disorder_strength_Jz), 0, i]
            )
            if self.Jy != 0.0:
                jy_list.append([-self.Jy, 0, i])
            jzx_list.append(
                [-_val(self._disorder, self.Jzx, self.disorder_strength_Jzx), 0, i]
            )
            jcpm = _val(self._disorder, self.Jcpm, self.disorder_strength_Jcpm)
            if jcpm != 0.0:
                cpm_list.append([-jcpm / 4, 0, i])
        for i in p2_targets:
            # Pixel 2 (positive sign)
            jx_list.append(
                [_val(self._disorder, self.Jx, self.disorder_strength_Jx), 0, i]
            )
            jz_list.append(
                [_val(self._disorder, self.Jz, self.disorder_strength_Jz), 0, i]
            )
            if self.Jy != 0.0:
                jy_list.append([self.Jy, 0, i])
            jzx_list.append(
                [_val(self._disorder, self.Jzx, self.disorder_strength_Jzx), 0, i]
            )
            jcpm = _val(self._disorder, self.Jcpm, self.disorder_strength_Jcpm)
            if jcpm != 0.0:
                cpm_list.append([jcpm / 4, 0, i])

        static.append(["xx", jx_list])
        static.append(["zz", jz_list])
        if jy_list:
            static.append(["yy", jy_list])
        if any(v[0] != 0 for v in jzx_list):
            static.append(["zx", jzx_list])
        if cpm_list:
            static.append(["+-", cpm_list])
            static.append(["-+", cpm_list])

        # Self-energy fields
        # Central qubit (i=0) may have its own field values
        hx0_base = self.hx0 if self.hx0 is not None else self.hx
        hz0_base = self.hz0 if self.hz0 is not None else self.hz
        hx_list = [
            [-_val(self._disorder, hx0_base, self.disorder_strength_hx), 0]
        ] + [
            [-_val(self._disorder, self.hx, self.disorder_strength_hx), i]
            for i in range(1, N)
        ]
        hz_list = [
            [-_val(self._disorder, hz0_base, self.disorder_strength_hz), 0]
        ] + [
            [-_val(self._disorder, self.hz, self.disorder_strength_hz), i]
            for i in range(1, N)
        ]
        if any(v[0] != 0 for v in hx_list):
            static.append(["x", hx_list])
        if any(v[0] != 0 for v in hz_list):
            static.append(["z", hz_list])

        return static, N

    def generate(self) -> np.ndarray:
        static, N = self._build_static()
        basis = spin_basis_1d(L=N)
        H = hamiltonian(
            static,
            [],
            basis=basis,
            dtype=np.float64,
            check_symm=False,
            check_herm=False,
        )
        return H.toarray()

    def diagonalize(self) -> Tuple[np.ndarray, np.ndarray]:
        static, N = self._build_static()

        has_xx_x = _has_xx_or_x(
            self.Jx,
            self.hx,
            self._disorder,
            self.disorder_strength_Jx,
            self.disorder_strength_hx,
            hx0=self.hx0,
        )
        has_zx = self.Jzx != 0.0 or (
            self._disorder is not None and self.disorder_strength_Jzx != 0.0
        )
        has_pairing = self.Jxx != 0.0 or self.Jyy != 0.0 or self.Jy != 0.0
        has_disord = _has_disorder(
            self._disorder,
            self.disorder_strength_J,
            self.disorder_strength_Jpm,
            self.disorder_strength_Jx,
            self.disorder_strength_Jz,
            self.disorder_strength_Jzx,
            self.disorder_strength_Jcpm,
            self.disorder_strength_hx,
            self.disorder_strength_hz,
        )
        can_use_shift = (
            self.connectivity == "ring"
            and self.N_pixel > 1
            and not has_disord
            and _central_couples_to_all_sites(
                self.N_pixel, self.connectivity, self.central_coupling
            )
        )
        can_use_mag = not has_xx_x and not has_zx and not has_pairing

        if not self.use_symmetry or (not can_use_shift and not can_use_mag):
            return super().diagonalize()

        # Build cyclic-shift permutations for pixel 1 and pixel 2
        T1 = T2 = None
        if can_use_shift:
            T1 = list(range(N))
            for k in range(self.N_pixel):
                T1[1 + k] = 1 + (k + 1) % self.N_pixel
            T1 = np.array(T1)

            T2 = list(range(N))
            for k in range(self.N_pixel):
                T2[self.N_pixel + 1 + k] = self.N_pixel + 1 + (k + 1) % self.N_pixel
            T2 = np.array(T2)

        # Enumerate symmetry sectors
        bases: list = []
        if can_use_mag and can_use_shift:
            for m in range(N + 1):
                for k1 in range(self.N_pixel):
                    for k2 in range(self.N_pixel):
                        bases.append(
                            spin_basis_general(
                                N,
                                Nup=m,
                                k1block=(T1, k1),
                                k2block=(T2, k2),
                            )
                        )
        elif can_use_shift:
            for k1 in range(self.N_pixel):
                for k2 in range(self.N_pixel):
                    bases.append(
                        spin_basis_general(
                            N,
                            k1block=(T1, k1),
                            k2block=(T2, k2),
                        )
                    )
        else:  # can_use_mag only
            for m in range(N + 1):
                bases.append(spin_basis_general(N, Nup=m))

        return _diag_in_sectors(N, static, bases)

    def diagonalize_sectors(self) -> list:
        static, N = self._build_static()
        has_xx_x = _has_xx_or_x(
            self.Jx,
            self.hx,
            self._disorder,
            self.disorder_strength_Jx,
            self.disorder_strength_hx,
            hx0=self.hx0,
        )
        has_zx = self.Jzx != 0.0 or (
            self._disorder is not None and self.disorder_strength_Jzx != 0.0
        )
        has_pairing = self.Jxx != 0.0 or self.Jyy != 0.0 or self.Jy != 0.0
        has_disord = _has_disorder(
            self._disorder,
            self.disorder_strength_J,
            self.disorder_strength_Jpm,
            self.disorder_strength_Jx,
            self.disorder_strength_Jz,
            self.disorder_strength_Jzx,
            self.disorder_strength_Jcpm,
            self.disorder_strength_hx,
            self.disorder_strength_hz,
        )
        can_use_shift = (
            self.connectivity == "ring"
            and self.N_pixel > 1
            and not has_disord
            and _central_couples_to_all_sites(
                self.N_pixel, self.connectivity, self.central_coupling
            )
        )
        can_use_mag = not has_xx_x and not has_zx and not has_pairing
        if not self.use_symmetry or (not can_use_shift and not can_use_mag):
            return _collect_full_sector_quspin(static, N)

        if not can_use_shift:
            bases = [spin_basis_general(N, Nup=m) for m in range(N + 1)]
            return _collect_sectors(
                static,
                bases,
                relative_evolution_local=False,
                symmetry_label="magnetization",
            )

        T1 = list(range(N))
        for k in range(self.N_pixel):
            T1[1 + k] = 1 + (k + 1) % self.N_pixel
        T1 = np.array(T1)

        T2 = list(range(N))
        for k in range(self.N_pixel):
            T2[self.N_pixel + 1 + k] = self.N_pixel + 1 + (k + 1) % self.N_pixel
        T2 = np.array(T2)

        bases = [
            spin_basis_general(N, k1block=(T1, k1), k2block=(T2, k2))
            for k1 in range(self.N_pixel)
            for k2 in range(self.N_pixel)
        ]
        return _collect_sectors(
            static,
            bases,
            relative_evolution_local=True,
            symmetry_label="dual_pixel_shift",
        )
