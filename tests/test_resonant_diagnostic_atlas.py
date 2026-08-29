from pathlib import Path

import numpy as np

from scripts.plot_resonant_diagnostic_atlas import _bloch_branches, _density, _raw_path


def test_bloch_branches_are_unit_and_antipodal() -> None:
    eigenvalues = np.array([0.0, 1.0, 1.0j, 2.0 - 0.5j, np.inf], dtype=np.complex128)
    blue, red = _bloch_branches(eigenvalues)
    assert blue.shape == (4, 3)
    assert np.allclose(np.linalg.norm(blue, axis=1), 1.0, atol=1e-14)
    assert np.allclose(red, -blue, atol=0.0)


def test_histogram_density_normalizes() -> None:
    values = np.array([0.1, 0.2, 0.8, 1.7, 2.9])
    edges = np.linspace(0.0, np.pi, 13)
    density = _density(values, edges)
    assert np.isclose(np.sum(density * np.diff(edges)), 1.0)


def test_raw_path_requires_the_requested_saved_time(tmp_path: Path) -> None:
    np.savez(tmp_path / "raw_N10_hz+0.000_t1000.npz", theta=np.array([0.0]))
    assert _raw_path(tmp_path, 1_000.0).name.endswith("t1000.npz")
    try:
        _raw_path(tmp_path, 10_000.0)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("nearest-time substitution must not be accepted")
