"""Tests for strict reclassification of saved Sobol ring roots."""

import importlib.util
import json
from pathlib import Path

import numpy as np


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "aggregate_sobol_ring_hamiltonian_classification.py"
)
SPEC = importlib.util.spec_from_file_location("sobol_ring_classification", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _write_case(path: Path, *, hz0: float) -> None:
    path.mkdir()
    rng = np.random.default_rng(29)
    blue = rng.normal(size=(5000, 3))
    blue /= np.linalg.norm(blue, axis=1)[:, None]
    np.savez(path / "results.npz", bloch_blue=blue, bloch_red=-blue)
    metadata = {
        "N": 6,
        "evolution_time": 4.0,
        "hz0": hz0,
        "Jx_effective": 0.01,
        "Jy_effective": 0.0,
        "Jy_unscaled": 0.0,
        "scaling": "test",
        "configuration": {"j": 1.0, "hz": 0.1},
        "second_neighbor_ring": False,
        "second_neighbor_bond_convention": None,
    }
    (path / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (path / "validation.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
    (path / "metrics.json").write_text(json.dumps({"S_born": 0.4}), encoding="utf-8")


def test_nonzero_hz0_saved_adapter_emits_common_schema(tmp_path: Path) -> None:
    case = tmp_path / "config_000"
    _write_case(case, hz0=0.1)

    row = MODULE.classify_saved_sobol_config(
        case, "sobol_ring_hz0_0p1_matched_band", n_phi=8, n_mu=4, l_max=3
    )

    assert set(row) == set(MODULE.FIELDS)
    assert row["qz_valid"] is False
    assert row["coverage"] == 1.0
    assert np.isfinite(row["higher_harmonic_leakage"])


def test_zero_hz0_row_records_conserved_x_theorem(tmp_path: Path) -> None:
    case = tmp_path / "config_001"
    _write_case(case, hz0=0.0)

    row = MODULE.classify_saved_sobol_config(
        case, "sobol_ring_hz0_0", n_phi=8, n_mu=4, l_max=3
    )
    parameters = json.loads(row["parameters"])

    assert parameters["central_x_conservation_theorem_applies"] is True
    assert "PROVED ANALYTICALLY" in row["status"]
