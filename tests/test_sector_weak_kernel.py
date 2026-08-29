"""Tests for sector-aware weak-kernel diagnostics."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from born_hamiltonian_search import Candidate
from detector_spectral_response import spectral_response, weak_relative_evolution_matrix
from sector_weak_kernel_diagnostics import (
    central_flip_operator,
    diagonalize_detector_sectors,
    weak_kernel_eigenvalues_by_momentum,
)


def test_sector_weak_kernel_matches_dense_small_ring():
    candidate = Candidate(
        model="single_pixel",
        N=6,
        J=1.0,
        Jpm=0.05,
        Jx_unscaled=0.05,
        hz=0.1,
        hz0_mode="zero",
        connectivity="ring",
        central_coupling="all",
        seed=44,
    )
    t_value = 100.0

    dense_response = spectral_response(
        candidate,
        bins=20,
        delta_max=None,
        windows=[1.0 / t_value],
    )
    dense_matrix = weak_relative_evolution_matrix(dense_response, t_value)
    dense_radii = np.sort(np.abs(np.linalg.eigvals(dense_matrix)))

    sectors = diagonalize_detector_sectors(candidate)
    sector_values, _block_rows = weak_kernel_eigenvalues_by_momentum(
        sectors,
        central_flip_operator(candidate),
        hz0=0.0,
        t_value=t_value,
    )
    sector_radii = np.sort(np.abs(sector_values))

    assert sector_radii.shape == dense_radii.shape
    assert np.allclose(sector_radii, dense_radii, atol=1e-8, rtol=1e-8)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL {test.__name__}: {exc}")
            failed += 1
    print(f"{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
