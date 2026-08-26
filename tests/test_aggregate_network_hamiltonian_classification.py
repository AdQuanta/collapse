"""Tests for adapting saved network roots to the common classification."""

import importlib.util
import json
from pathlib import Path

import numpy as np


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "aggregate_network_hamiltonian_classification.py"
)
SPEC = importlib.util.spec_from_file_location("network_classification", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_saved_network_adapter_preserves_provenance_and_withholds_qz(tmp_path: Path) -> None:
    config = tmp_path / "config_000"
    config.mkdir()
    rng = np.random.default_rng(17)
    blue = rng.normal(size=(5000, 3))
    blue /= np.linalg.norm(blue, axis=1)[:, None]
    red = -blue
    np.savez(config / "results.npz", bloch_blue=blue, bloch_red=red)
    metadata = {
        "N": 6,
        "evolution_time": 3.0,
        "hz0": 0.0,
        "Jx_effective": 0.01,
        "Jy_effective": 0.0,
        "central_coupling": "all detector qubits",
        "scaling": "test",
        "configuration": {"j": 1.0, "hz": 0.1},
        "detector_graph": {
            "edge_count": 7,
            "mean_degree": 2.3,
            "degree_variance": 0.2,
            "laplacian_algebraic_connectivity": 0.4,
            "connected": True,
            "spec": {"kind": "erdos_renyi", "seed": 123},
        },
    }
    (config / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (config / "validation.json").write_text(
        json.dumps({"passed": True}), encoding="utf-8"
    )
    (config / "metrics.json").write_text(
        json.dumps({"S_born": 0.25}), encoding="utf-8"
    )

    row = MODULE.classify_saved_network_config(
        config, "erdos_renyi", n_phi=8, n_mu=4, l_max=3
    )

    assert row["family"] == "network_erdos_renyi"
    assert row["seed"] == 123
    assert row["qz_valid"] is False
    assert row["root_count"] == 5000
    assert float(row["coverage"]) == 1.0
    assert set(row) == set(MODULE.FIELDS)
