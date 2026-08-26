"""
Test symmetry-aware diagonalisation for all QuSpin Hamiltonians.

Compares eigenvalues from ``ham.diagonalize()`` (symmetry path) against
``np.linalg.eigh(ham.generate())`` (full path) for various parameter
configurations.

Also tests ``DisentanglementAnalyzer.from_eigenbasis`` against the
standard constructor path.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import numpy as np

from collapse.analysis import DisentanglementAnalyzer
from collapse.hamiltonians.quspin_hamiltonians import (
    CentralSpinHamiltonianQuSpin,
    DimerizedPixelHamiltonianQuSpin,
    MixedFieldIsingHamiltonianQuSpin,
    SinglePixelHamiltonianQuSpin,
    TwoPixelHamiltonianQuSpin,
)


TOL = 1e-10


def _max_unordered_complex_diff(a, b):
    """Return max nearest-neighbour mismatch for two unordered complex spectra."""

    left = np.asarray(a, dtype=np.complex128).ravel()
    remaining = list(np.asarray(b, dtype=np.complex128).ravel())
    if left.size != len(remaining):
        raise AssertionError(f"spectrum sizes differ: {left.size} != {len(remaining)}")

    max_diff = 0.0
    for value in left:
        distances = np.abs(np.asarray(remaining) - value)
        idx = int(np.argmin(distances))
        max_diff = max(max_diff, float(distances[idx]))
        remaining.pop(idx)
    return max_diff


def _compare_eigenvalues(ham, label):
    """Compare diagonalize() eigenvalues with eigh(generate())."""
    E_sym, V_sym = ham.diagonalize()
    H = ham.generate()
    E_full = np.sort(np.linalg.eigvalsh(H))
    E_sym_sorted = np.sort(E_sym.real)

    max_diff = np.max(np.abs(E_full - E_sym_sorted))
    assert max_diff < TOL, f"{label}: eigenvalue diff = {max_diff:.2e}"

    # Also check V_sym is orthonormal
    I_check = V_sym.conj().T @ V_sym
    ortho_err = np.max(np.abs(I_check - np.eye(len(E_sym))))
    assert ortho_err < TOL, f"{label}: orthonormality error = {ortho_err:.2e}"


def _compare_z_distributions(ham, t, label):
    """Compare from_eigenbasis path against standard U-based path."""
    # Standard path
    H = ham.generate()
    E_full, V_full = np.linalg.eigh(H)
    from collapse.quantum_utils import time_evolution_from_eigenbasis

    U = time_evolution_from_eigenbasis(E_full, V_full, t)
    analyzer_std = DisentanglementAnalyzer(U)
    analyzer_std.diagonalize_subblocks_product()
    analyzer_std.get_initial_qubit_states_from_eigenvalues()
    z0_std = np.sort(
        np.abs(analyzer_std.phi0[:, 0]) ** 2 - np.abs(analyzer_std.phi0[:, 1]) ** 2
    )
    z1_std = np.sort(
        np.abs(analyzer_std.phi1[:, 0]) ** 2 - np.abs(analyzer_std.phi1[:, 1]) ** 2
    )

    # from_eigenbasis path (using symmetry diagonalisation)
    E_sym, V_sym = ham.diagonalize()
    analyzer_eig = DisentanglementAnalyzer.from_eigenbasis(E_sym, V_sym, t)
    analyzer_eig.get_initial_qubit_states_from_eigenvalues()
    z0_eig = np.sort(
        np.abs(analyzer_eig.phi0[:, 0]) ** 2 - np.abs(analyzer_eig.phi0[:, 1]) ** 2
    )
    z1_eig = np.sort(
        np.abs(analyzer_eig.phi1[:, 0]) ** 2 - np.abs(analyzer_eig.phi1[:, 1]) ** 2
    )

    d0 = np.max(np.abs(z0_std - z0_eig))
    d1 = np.max(np.abs(z1_std - z1_eig))
    assert d0 < 1e-8, f"{label}: z0 diff = {d0:.2e}"
    assert d1 < 1e-8, f"{label}: z1 diff = {d1:.2e}"


def _compare_sector_relative_spectrum(ham, n_qubits, label, t=1.25):
    """Compare sector-derived M(t) eigenvalues with the full dense path."""

    H = ham.generate()
    E_full, V_full = np.linalg.eigh(H)
    analyzer_full = DisentanglementAnalyzer.from_eigenbasis(E_full, V_full, t)

    sectors = ham.diagonalize_sectors()
    analyzer_sector = DisentanglementAnalyzer.from_sectors(sectors, t, n_qubits)

    full_eigs = np.asarray(analyzer_full.D0)
    sector_eigs = np.asarray(analyzer_sector.D0)
    max_complex_diff = _max_unordered_complex_diff(full_eigs, sector_eigs)
    assert (
        max_complex_diff < 1e-8
    ), f"{label}: sector/full M eigenvalue diff = {max_complex_diff:.2e}"

    full_radii = np.sort(np.abs(full_eigs))
    sector_radii = np.sort(np.abs(sector_eigs))
    max_diff = np.max(np.abs(full_radii - sector_radii))
    assert max_diff < 1e-8, f"{label}: sector/full M radii diff = {max_diff:.2e}"


# ---- CentralSpin tests ----
def test_cs_magnetization_symmetry():
    """CentralSpin with Jx=0, hx=0 should use magnetisation symmetry."""
    ham = CentralSpinHamiltonianQuSpin(N_star=6, Jx=0.0, Jz=1.0, seed=42)
    _compare_eigenvalues(ham, "CS mag")


def test_cs_no_symmetry_fallback():
    """CentralSpin with Jx!=0 should fall back to full diag."""
    ham = CentralSpinHamiltonianQuSpin(N_star=6, Jx=0.5, Jz=1.0, seed=42)
    _compare_eigenvalues(ham, "CS no-sym")


def test_cs_use_symmetry_false():
    """CentralSpin with use_symmetry=False."""
    ham = CentralSpinHamiltonianQuSpin(
        N_star=6, Jx=0.0, Jz=1.0, seed=42, use_symmetry=False
    )
    _compare_eigenvalues(ham, "CS flag-off")


def test_cs_z_distributions():
    ham = CentralSpinHamiltonianQuSpin(N_star=6, Jx=0.0, Jz=1.0, seed=42)
    _compare_z_distributions(ham, 10.0, "CS z-dist")


# ---- MixedFieldIsing tests ----
def test_mfi_no_hx():
    """MFI with hx=0 should use magnetisation symmetry."""
    ham = MixedFieldIsingHamiltonianQuSpin(N=7, J=1.0, hx=0.0, hz=0.5, seed=42)
    _compare_eigenvalues(ham, "MFI mag")


def test_mfi_with_hx():
    """MFI with hx!=0 falls back."""
    ham = MixedFieldIsingHamiltonianQuSpin(N=7, J=1.0, hx=1.0, hz=0.5, seed=42)
    _compare_eigenvalues(ham, "MFI no-sym")


def test_mfi_z_distributions():
    ham = MixedFieldIsingHamiltonianQuSpin(N=7, J=1.0, hx=0.0, hz=0.5, seed=42)
    _compare_z_distributions(ham, 10.0, "MFI z-dist")


# ---- SinglePixel tests ----
def test_sp_ring_shift():
    """SinglePixel ring with uniform couplings should use cyclic shift."""
    ham = SinglePixelHamiltonianQuSpin(
        N_pixel=4, J=1.0, Jx=0.5, Jz=0.3, connectivity="ring", seed=42
    )
    _compare_eigenvalues(ham, "SP ring shift")


def test_sp_ring_shift_and_mag():
    """SinglePixel ring, Jx=0 should use both magnetisation + shift."""
    ham = SinglePixelHamiltonianQuSpin(
        N_pixel=4, J=1.0, Jx=0.0, Jz=0.3, connectivity="ring", seed=42
    )
    _compare_eigenvalues(ham, "SP ring shift+mag")


def test_sp_chain_mag_only():
    """SinglePixel chain, Jx=0 should use magnetisation only."""
    ham = SinglePixelHamiltonianQuSpin(
        N_pixel=4, J=1.0, Jx=0.0, Jz=0.3, connectivity="chain", seed=42
    )
    _compare_eigenvalues(ham, "SP chain mag")


def test_sp_chain_no_symmetry():
    """SinglePixel chain, Jx!=0 should fall back."""
    ham = SinglePixelHamiltonianQuSpin(
        N_pixel=4, J=1.0, Jx=0.5, Jz=0.3, connectivity="chain", seed=42
    )
    _compare_eigenvalues(ham, "SP chain no-sym")


def test_sp_z_distributions():
    ham = SinglePixelHamiltonianQuSpin(
        N_pixel=4, J=1.0, Jx=0.5, Jz=0.3, connectivity="ring", seed=42
    )
    _compare_z_distributions(ham, 10.0, "SP z-dist")


# ---- Dimerized single-pixel tests ----
def test_sp_ring_local_central_coupling_breaks_shift():
    """Local central coupling should not use pixel-ring momentum sectors."""
    ham = SinglePixelHamiltonianQuSpin(
        N_pixel=4,
        J=1.0,
        Jx=0.3,
        Jz=0.2,
        connectivity="ring",
        central_coupling="first",
        seed=42,
    )
    _compare_eigenvalues(ham, "SP local central no-shift")
    sectors = ham.diagonalize_sectors()
    assert len(sectors) == 2
    assert {sector["symmetry_label"] for sector in sectors} == {
        "magnetization_parity"
    }


def test_dimerized_all_central_coupling_uses_dimer_symmetry():
    """Uniform central coupling may use dimer-shift/swap sectors."""
    ham = DimerizedPixelHamiltonianQuSpin(
        N_pixel=4,
        J=1.0,
        Jx=0.2,
        Jz=0.3,
        central_coupling="all",
        seed=42,
    )
    _compare_eigenvalues(ham, "Dimerized all central symmetry")
    assert len(ham.diagonalize_sectors()) > 1


def test_dimerized_local_central_coupling_breaks_dimer_symmetry():
    """Local central coupling should fall back when no Sz symmetry remains."""
    ham = DimerizedPixelHamiltonianQuSpin(
        N_pixel=4,
        J=1.0,
        Jx=0.2,
        Jz=0.3,
        central_coupling="first",
        seed=42,
    )
    _compare_eigenvalues(ham, "Dimerized local central no dimer symmetry")
    assert len(ham.diagonalize_sectors()) == 1


# ---- TwoPixel tests ----
def test_tp_ring_dual_shift():
    """TwoPixel ring with uniform couplings should use dual cyclic shift."""
    ham = TwoPixelHamiltonianQuSpin(
        N_pixel=3, J=1.0, Jx=0.3, Jz=0.3, connectivity="ring", seed=42
    )
    _compare_eigenvalues(ham, "TP ring dual-shift")


def test_tp_ring_shift_and_mag():
    """TwoPixel ring, Jx=0 should use both magnetisation + dual shift."""
    ham = TwoPixelHamiltonianQuSpin(
        N_pixel=3, J=1.0, Jx=0.0, Jz=0.3, connectivity="ring", seed=42
    )
    _compare_eigenvalues(ham, "TP ring shift+mag")


def test_tp_chain_mag_only():
    """TwoPixel chain, Jx=0 should use magnetisation only."""
    ham = TwoPixelHamiltonianQuSpin(
        N_pixel=3, J=1.0, Jx=0.0, Jz=0.3, connectivity="chain", seed=42
    )
    _compare_eigenvalues(ham, "TP chain mag")


def test_tp_chain_no_symmetry():
    """TwoPixel chain, Jx!=0 should fall back."""
    ham = TwoPixelHamiltonianQuSpin(
        N_pixel=3, J=1.0, Jx=0.3, Jz=0.3, connectivity="chain", seed=42
    )
    _compare_eigenvalues(ham, "TP chain no-sym")


def test_tp_all_to_all():
    """TwoPixel all-to-all, Jx=0 should use magnetisation only."""
    ham = TwoPixelHamiltonianQuSpin(
        N_pixel=3, J=1.0, Jx=0.0, Jz=0.3, connectivity="all_to_all", seed=42
    )
    _compare_eigenvalues(ham, "TP all-to-all mag")


def test_tp_use_symmetry_false():
    """TwoPixel with use_symmetry=False."""
    ham = TwoPixelHamiltonianQuSpin(
        N_pixel=3,
        J=1.0,
        Jx=0.0,
        Jz=0.3,
        connectivity="ring",
        seed=42,
        use_symmetry=False,
    )
    _compare_eigenvalues(ham, "TP flag-off")


def test_tp_z_distributions():
    ham = TwoPixelHamiltonianQuSpin(
        N_pixel=3, J=1.0, Jx=0.3, Jz=0.3, connectivity="ring", seed=42
    )
    _compare_z_distributions(ham, 10.0, "TP z-dist")


def test_sector_relative_spectrum_matches_full_for_symmetry_configurations():
    cases = [
        (
            "CS magnetization",
            CentralSpinHamiltonianQuSpin(N_star=3, Jx=0.0, Jz=0.3, seed=42),
            4,
        ),
        (
            "CS no symmetry",
            CentralSpinHamiltonianQuSpin(N_star=3, Jx=0.2, Jz=0.3, seed=42),
            4,
        ),
        (
            "CS symmetry disabled",
            CentralSpinHamiltonianQuSpin(
                N_star=3, Jx=0.0, Jz=0.3, seed=42, use_symmetry=False
            ),
            4,
        ),
        (
            "MFI magnetization",
            MixedFieldIsingHamiltonianQuSpin(N=4, J=1.0, hx=0.0, hz=0.2, seed=42),
            4,
        ),
        (
            "MFI no symmetry",
            MixedFieldIsingHamiltonianQuSpin(N=4, J=1.0, hx=0.4, hz=0.2, seed=42),
            4,
        ),
        (
            "SP ring shift",
            SinglePixelHamiltonianQuSpin(
                N_pixel=3, J=1.0, Jx=0.2, Jz=0.3, connectivity="ring", seed=42
            ),
            4,
        ),
        (
            "SP ring shift with Jx=0",
            SinglePixelHamiltonianQuSpin(
                N_pixel=3, J=1.0, Jx=0.0, Jz=0.3, connectivity="ring", seed=42
            ),
            4,
        ),
        (
            "SP chain magnetization",
            SinglePixelHamiltonianQuSpin(
                N_pixel=3, J=1.0, Jx=0.0, Jz=0.3, connectivity="chain", seed=42
            ),
            4,
        ),
        (
            "SP chain no symmetry",
            SinglePixelHamiltonianQuSpin(
                N_pixel=3, J=1.0, Jx=0.2, Jz=0.3, connectivity="chain", seed=42
            ),
            4,
        ),
        (
            "SP local central no shift",
            SinglePixelHamiltonianQuSpin(
                N_pixel=3,
                J=1.0,
                Jx=0.2,
                Jz=0.3,
                connectivity="ring",
                central_coupling="first",
                seed=42,
            ),
            4,
        ),
        (
            "Dimer spatial",
            DimerizedPixelHamiltonianQuSpin(
                N_pixel=4, J=1.0, Jx=0.2, Jz=0.3, central_coupling="all", seed=42
            ),
            5,
        ),
        (
            "Dimer magnetization",
            DimerizedPixelHamiltonianQuSpin(
                N_pixel=4, J=1.0, Jx=0.0, Jz=0.3, central_coupling="first", seed=42
            ),
            5,
        ),
        (
            "Dimer no symmetry",
            DimerizedPixelHamiltonianQuSpin(
                N_pixel=4, J=1.0, Jx=0.2, Jz=0.3, central_coupling="first", seed=42
            ),
            5,
        ),
        (
            "TP dual shift",
            TwoPixelHamiltonianQuSpin(
                N_pixel=2, J=1.0, Jx=0.2, Jz=0.3, connectivity="ring", seed=42
            ),
            5,
        ),
        (
            "TP dual shift with Jx=0",
            TwoPixelHamiltonianQuSpin(
                N_pixel=2, J=1.0, Jx=0.0, Jz=0.3, connectivity="ring", seed=42
            ),
            5,
        ),
        (
            "TP chain magnetization",
            TwoPixelHamiltonianQuSpin(
                N_pixel=2, J=1.0, Jx=0.0, Jz=0.3, connectivity="chain", seed=42
            ),
            5,
        ),
        (
            "TP chain no symmetry",
            TwoPixelHamiltonianQuSpin(
                N_pixel=2, J=1.0, Jx=0.2, Jz=0.3, connectivity="chain", seed=42
            ),
            5,
        ),
        (
            "TP all-to-all magnetization",
            TwoPixelHamiltonianQuSpin(
                N_pixel=2, J=1.0, Jx=0.0, Jz=0.3, connectivity="all_to_all", seed=42
            ),
            5,
        ),
    ]

    for label, ham, n_qubits in cases:
        _compare_sector_relative_spectrum(ham, n_qubits, label)


# ---- Benchmark ----
def benchmark_tp_ring():
    """Benchmark symmetry vs full diag for TwoPixel ring."""
    ham_sym = TwoPixelHamiltonianQuSpin(
        N_pixel=3,
        J=1.0,
        Jx=0.3,
        Jz=0.3,
        connectivity="ring",
        seed=42,
        use_symmetry=True,
    )
    ham_full = TwoPixelHamiltonianQuSpin(
        N_pixel=3,
        J=1.0,
        Jx=0.3,
        Jz=0.3,
        connectivity="ring",
        seed=42,
        use_symmetry=False,
    )

    t0 = time.time()
    E_full, V_full = ham_full.diagonalize()
    t_full = time.time() - t0

    t0 = time.time()
    E_sym, V_sym = ham_sym.diagonalize()
    t_sym = time.time() - t0

    print(
        f"  TwoPixel ring (N=7): full={t_full:.4f}s  sym={t_sym:.4f}s  "
        f"speedup={t_full/t_sym:.1f}x"
    )


# ---- Runner ----
if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed\n")

    if failed == 0:
        print("--- Benchmark ---")
        benchmark_tp_ring()

    sys.exit(1 if failed else 0)
