"""
Verification tests for intra-pixel connectivity support.

Tests the ``connectivity`` parameter for SinglePixel and TwoPixel
Hamiltonians (both NumPy and QuSpin backends).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from collapse.pauli import build_pauli_z
from collapse.hamiltonians.numpy_hamiltonians import (
    _central_targets,
    _pixel_bonds,
    DimerizedPixelHamiltonianNumpy,
    SinglePixelHamiltonianNumpy,
    TwoPixelHamiltonianNumpy,
)

try:
    from collapse.hamiltonians.quspin_hamiltonians import (
        SinglePixelHamiltonianQuSpin,
        DimerizedPixelHamiltonianQuSpin,
        TwoPixelHamiltonianQuSpin,
    )

    HAS_QUSPIN = True
except ImportError:
    HAS_QUSPIN = False


# ── helpers ──────────────────────────────────────────────────────────
def _assert_hermitian(H, label=""):
    assert np.allclose(H, H.conj().T), f"Not Hermitian: {label}"


def _total_z_operator(N: int) -> np.ndarray:
    total = np.zeros((2**N, 2**N), dtype=np.float64)
    for site in range(N):
        total += build_pauli_z(site, N)
    return total


# ── 1. _pixel_bonds bond-count checks ───────────────────────────────
def test_pixel_bonds_chain():
    bonds = _pixel_bonds(1, 4, "chain")
    assert len(bonds) == 3, f"chain: expected 3 bonds, got {len(bonds)}"
    # Should be open: (1,2), (2,3), (3,4)
    assert bonds == [(1, 2), (2, 3), (3, 4)]


def test_pixel_bonds_ring():
    bonds = _pixel_bonds(1, 4, "ring")
    assert len(bonds) == 4, f"ring: expected 4 bonds, got {len(bonds)}"
    # Last bond closes the ring
    assert bonds[-1] == (4, 1)


def test_pixel_bonds_all_to_all():
    bonds = _pixel_bonds(1, 4, "all_to_all")
    # 4 choose 2 = 6
    assert len(bonds) == 6, f"all_to_all: expected 6 bonds, got {len(bonds)}"


def test_pixel_bonds_invalid():
    try:
        _pixel_bonds(0, 3, "star")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_central_targets_modes():
    assert _central_targets(1, 4, "chain", "auto") == [1]
    assert _central_targets(1, 4, "ring", "auto") == [1, 2, 3, 4]
    assert _central_targets(1, 4, "ring", "first") == [1]
    assert _central_targets(1, 4, "ring", "last") == [4]
    assert _central_targets(1, 4, "ring", "ends") == [1, 4]
    assert _central_targets(1, 1, "chain", "ends") == [1]


# ── 2. Backward compatibility: default "ring" ─────────────────────
def test_single_pixel_default_is_ring():
    """Omitting connectivity should give ring (same as explicit ring)."""
    params = dict(N_pixel=3, J=1.0, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42)
    H_default = SinglePixelHamiltonianNumpy(**params).generate()
    H_ring = SinglePixelHamiltonianNumpy(connectivity="ring", **params).generate()
    assert np.allclose(H_default, H_ring), "Default should equal ring"


def test_two_pixel_default_is_ring():
    params = dict(N_pixel=3, J=1.0, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42)
    H_default = TwoPixelHamiltonianNumpy(**params).generate()
    H_ring = TwoPixelHamiltonianNumpy(connectivity="ring", **params).generate()
    assert np.allclose(H_default, H_ring), "Default should equal ring"


# ── 3. Different connectivities give different matrices ────────────
def test_single_pixel_connectivities_differ():
    params = dict(N_pixel=4, J=1.0, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42)
    matrices = {}
    for conn in ("chain", "ring", "all_to_all"):
        H = SinglePixelHamiltonianNumpy(connectivity=conn, **params).generate()
        _assert_hermitian(H, f"SinglePixel({conn})")
        matrices[conn] = H

    assert not np.allclose(
        matrices["chain"], matrices["ring"]
    ), "chain and ring should differ"
    assert not np.allclose(
        matrices["ring"], matrices["all_to_all"]
    ), "ring and all_to_all should differ"


def test_single_pixel_central_coupling_modes_differ():
    params = dict(N_pixel=4, J=1.0, Jx=0.5, Jy=0.2, Jz=0.3, hx=0.2, hz=0.1, seed=42)
    H_all = SinglePixelHamiltonianNumpy(connectivity="ring", central_coupling="all", **params).generate()
    H_first = SinglePixelHamiltonianNumpy(connectivity="ring", central_coupling="first", **params).generate()
    H_ends = SinglePixelHamiltonianNumpy(connectivity="ring", central_coupling="ends", **params).generate()
    _assert_hermitian(H_all, "SinglePixel central all")
    _assert_hermitian(H_first, "SinglePixel central first")
    _assert_hermitian(H_ends, "SinglePixel central ends")
    assert not np.allclose(H_all, H_first)
    assert not np.allclose(H_first, H_ends)


def test_two_pixel_connectivities_differ():
    # N_pixel must be >= 4 so ring and all_to_all differ (for 3 they coincide)
    params = dict(N_pixel=4, J=1.0, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42)
    matrices = {}
    for conn in ("chain", "ring", "all_to_all"):
        H = TwoPixelHamiltonianNumpy(connectivity=conn, **params).generate()
        _assert_hermitian(H, f"TwoPixel({conn})")
        matrices[conn] = H

    assert not np.allclose(matrices["chain"], matrices["ring"])
    assert not np.allclose(matrices["ring"], matrices["all_to_all"])


# ── 4. NumPy ↔ QuSpin agreement ──────────────────────────────────
def test_numpy_quspin_agreement_single_pixel():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for conn in ("chain", "ring", "all_to_all"):
        params = dict(
            N_pixel=3,
            J=1.0,
            Jx=0.5,
            Jz=0.3,
            hx=0.2,
            hz=0.1,
            connectivity=conn,
            seed=42,
        )
        H_np = SinglePixelHamiltonianNumpy(**params).generate()
        H_qs = SinglePixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(H_np, H_qs), f"SinglePixel NumPy/QuSpin mismatch for {conn}"


def test_numpy_quspin_agreement_single_pixel_central_coupling_modes():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for central_coupling in ("first", "last", "ends", "all"):
        params = dict(
            N_pixel=3,
            J=1.0,
            Jx=0.5,
            Jy=0.1,
            Jz=0.3,
            hx=0.2,
            hz=0.1,
            connectivity="ring",
            central_coupling=central_coupling,
            seed=42,
        )
        H_np = SinglePixelHamiltonianNumpy(**params).generate()
        H_qs = SinglePixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(H_np, H_qs), f"central_coupling={central_coupling}"


def test_numpy_quspin_agreement_dimerized_central_coupling_modes():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for central_coupling in ("first", "last", "ends", "all"):
        params = dict(
            N_pixel=4,
            J=1.0,
            Jx=0.2,
            Jz=0.3,
            hx=0.1,
            hz=0.2,
            central_coupling=central_coupling,
            seed=42,
        )
        H_np = DimerizedPixelHamiltonianNumpy(**params).generate()
        H_qs = DimerizedPixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(H_np, H_qs), f"dimerized central_coupling={central_coupling}"


def test_numpy_quspin_agreement_two_pixel():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for conn in ("chain", "ring", "all_to_all"):
        params = dict(
            N_pixel=3,
            J=1.0,
            Jx=0.5,
            Jz=0.3,
            hx=0.2,
            hz=0.1,
            connectivity=conn,
            seed=42,
        )
        H_np = TwoPixelHamiltonianNumpy(**params).generate()
        H_qs = TwoPixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(H_np, H_qs), f"TwoPixel NumPy/QuSpin mismatch for {conn}"


def test_two_pixel_central_coupling_modes_differ():
    params = dict(N_pixel=3, J=1.0, Jx=0.2, hz=0.1, connectivity="ring")
    matrices = {
        mode: TwoPixelHamiltonianNumpy(central_coupling=mode, **params).generate()
        for mode in ("first", "last", "ends", "all")
    }
    assert not np.allclose(matrices["first"], matrices["last"])
    assert not np.allclose(matrices["ends"], matrices["all"])


def test_numpy_quspin_agreement_two_pixel_single_pixel_channels():
    """The modern two-pixel API mirrors every single-pixel channel."""
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for conn in ("chain", "ring", "all_to_all"):
        for central_coupling in ("first", "ends", "all"):
            params = dict(
                N_pixel=2,
                J=1.0,
                Jpm=0.17,
                Jxx=0.08,
                Jyy=-0.04,
                Jx=0.11,
                Jy=-0.03,
                Jz=0.07,
                Jzx=0.05,
                Jcpm=0.09,
                hx=0.02,
                hz=0.1,
                hx0=-0.01,
                hz0=0.03,
                connectivity=conn,
                central_coupling=central_coupling,
                seed=42,
            )
            H_np = TwoPixelHamiltonianNumpy(**params).generate()
            H_qs = TwoPixelHamiltonianQuSpin(**params).generate()
            assert np.allclose(H_np, H_qs), (
                f"TwoPixel channel mismatch for {conn}/{central_coupling}"
            )
            _assert_hermitian(H_np, "TwoPixel modern channels")


# ── 5. Jpm (XY / +−) interaction support ────────────────────────
def test_single_pixel_pm_changes_matrix():
    """Jpm != 0 should give a different matrix than Jpm == 0."""
    params = dict(N_pixel=3, J=1.0, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42)
    H_no_pm = SinglePixelHamiltonianNumpy(**params).generate()
    H_with_pm = SinglePixelHamiltonianNumpy(Jpm=0.5, **params).generate()
    assert not np.allclose(H_no_pm, H_with_pm), "Jpm should change the matrix"


def test_single_pixel_pm_hermitian():
    """H with Jpm should still be Hermitian."""
    H = SinglePixelHamiltonianNumpy(
        N_pixel=3, J=1.0, Jpm=0.5, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42
    ).generate()
    _assert_hermitian(H, "SinglePixel+Jpm")


def test_two_pixel_pm_changes_matrix():
    params = dict(N_pixel=3, J=1.0, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42)
    H_no_pm = TwoPixelHamiltonianNumpy(**params).generate()
    H_with_pm = TwoPixelHamiltonianNumpy(Jpm=0.5, **params).generate()
    assert not np.allclose(H_no_pm, H_with_pm), "Jpm should change 2P matrix"


def test_two_pixel_pm_hermitian():
    H = TwoPixelHamiltonianNumpy(
        N_pixel=3, J=1.0, Jpm=0.5, Jx=0.5, Jz=0.3, hx=0.2, hz=0.1, seed=42
    ).generate()
    _assert_hermitian(H, "TwoPixel+Jpm")


def test_numpy_quspin_agreement_single_pixel_pm():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for conn in ("chain", "ring", "all_to_all"):
        params = dict(
            N_pixel=3,
            J=1.0,
            Jpm=0.5,
            Jx=0.5,
            Jz=0.3,
            hx=0.2,
            hz=0.1,
            connectivity=conn,
            seed=42,
        )
        H_np = SinglePixelHamiltonianNumpy(**params).generate()
        H_qs = SinglePixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(
            H_np, H_qs
        ), f"SinglePixel+Jpm NumPy/QuSpin mismatch for {conn}"


def test_numpy_quspin_agreement_single_pixel_anisotropic_xy():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for conn in ("chain", "ring", "all_to_all"):
        params = dict(
            N_pixel=3,
            J=1.0,
            Jpm=0.2,
            Jxx=0.15,
            Jyy=-0.07,
            Jx=0.11,
            Jy=-0.05,
            Jz=0.3,
            Jzx=0.04,
            hx=0.02,
            hz=0.1,
            connectivity=conn,
            seed=42,
        )
        H_np = SinglePixelHamiltonianNumpy(**params).generate()
        H_qs = SinglePixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(
            H_np, H_qs
        ), f"SinglePixel anisotropic XY NumPy/QuSpin mismatch for {conn}"


def test_single_pixel_cpm_changes_matrix_and_is_hermitian():
    """Central-pixel flip-flop coupling should change H and remain Hermitian."""
    params = dict(N_pixel=3, J=1.0, Jz=0.3, hx=0.0, hz=0.1, seed=42)
    H_no_cpm = SinglePixelHamiltonianNumpy(**params).generate()
    H_with_cpm = SinglePixelHamiltonianNumpy(Jcpm=0.5, **params).generate()
    assert not np.allclose(H_no_cpm, H_with_cpm), "Jcpm should change the matrix"
    _assert_hermitian(H_with_cpm, "SinglePixel+Jcpm")


def test_single_pixel_cpm_conserves_total_z_when_transverse_terms_absent():
    """Jcpm is a flip-flop term and should conserve total Sz."""
    N_pixel = 3
    H = SinglePixelHamiltonianNumpy(
        N_pixel=N_pixel,
        J=1.0,
        Jpm=0.4,
        Jx=0.0,
        Jz=0.3,
        Jzx=0.0,
        Jcpm=0.5,
        hx=0.0,
        hz=0.1,
        hz0=0.2,
        seed=42,
    ).generate()
    total_z = _total_z_operator(N_pixel + 1)
    commutator = H @ total_z - total_z @ H
    assert np.allclose(commutator, 0.0), "Jcpm should conserve total Z"


def test_numpy_quspin_agreement_single_pixel_cpm():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for conn in ("chain", "ring", "all_to_all"):
        params = dict(
            N_pixel=3,
            J=1.0,
            Jpm=0.4,
            Jx=0.0,
            Jz=0.3,
            Jzx=0.0,
            Jcpm=0.5,
            hx=0.0,
            hz=0.1,
            connectivity=conn,
            seed=42,
        )
        H_np = SinglePixelHamiltonianNumpy(**params).generate()
        H_qs = SinglePixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(
            H_np, H_qs
        ), f"SinglePixel+Jcpm NumPy/QuSpin mismatch for {conn}"


def test_numpy_quspin_agreement_two_pixel_pm():
    if not HAS_QUSPIN:
        print("  SKIP (QuSpin not installed)")
        return
    for conn in ("chain", "ring", "all_to_all"):
        params = dict(
            N_pixel=3,
            J=1.0,
            Jpm=0.5,
            Jx=0.5,
            Jz=0.3,
            hx=0.2,
            hz=0.1,
            connectivity=conn,
            seed=42,
        )
        H_np = TwoPixelHamiltonianNumpy(**params).generate()
        H_qs = TwoPixelHamiltonianQuSpin(**params).generate()
        assert np.allclose(H_np, H_qs), f"TwoPixel+Jpm NumPy/QuSpin mismatch for {conn}"


# ── runner ───────────────────────────────────────────────────────────
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
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
