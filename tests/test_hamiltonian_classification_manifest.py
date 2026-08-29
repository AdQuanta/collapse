"""Manifest cardinality and physics-definition checks."""

import importlib.util
import json
from pathlib import Path

import numpy as np

from core.hamiltonian_classification import (
    SinglePixelClassificationPoint,
    build_single_pixel_hamiltonian,
    classify_single_pixel_point,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_hamiltonian_classification_manifest.py"
SPEC = importlib.util.spec_from_file_location("classification_manifest", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_manifest_is_deterministic_and_uses_source_detuning_definition() -> None:
    config = json.loads(
        (ROOT / "configs" / "hamiltonian_classification_zeus_campaign.json").read_text()
    )
    first = MODULE.expanded_points(config)
    second = MODULE.expanded_points(config)

    assert first == second
    assert len(first) == 149
    assert [row["point_id"] for row in first] == list(range(149))
    detuned = next(
        row
        for row in first
        if row["campaign"] == "matched_detuning"
        and row["detector_n"] == 10
        and row["scan_value"] == 3.0
    )
    parameters = json.loads(detuned["parameters_json"])
    assert parameters["hz0"] == 0.13
    assert parameters["backend"] == "quspin_sectors"

    network = next(
        row
        for row in first
        if row["campaign"] == "cross_network_matched"
        and row["detector_n"] == 10
        and row["scan_value"] == "expander"
        and json.loads(row["parameters_json"])["seed"] == 20260817
    )
    network_parameters = json.loads(network["parameters_json"])
    assert network_parameters["backend"] == "numpy_dense"
    assert network_parameters["connectivity"] == "expander"
    assert network_parameters["Jpm"] == 0.25
    assert network_parameters["hz0"] == 0.1

    ring_control = next(
        row for row in first if row["campaign"] == "cross_architecture_ring_control"
    )
    ring_parameters = json.loads(ring_control["parameters_json"])
    assert ring_parameters["connectivity"] == "ring"
    assert ring_parameters["backend"] == "numpy_dense"

    xy_edge = next(
        row
        for row in first
        if row["campaign"] == "cross_physical_architectures"
        and row["scan_value"] == "xy_chain_edge"
        and row["detector_n"] == 10
    )
    xy_edge_parameters = json.loads(xy_edge["parameters_json"])
    assert xy_edge_parameters["J"] == 0.0
    assert xy_edge_parameters["Jpm"] == 1.0
    assert xy_edge_parameters["connectivity"] == "chain"
    assert xy_edge_parameters["central_coupling"] == "first"
    assert xy_edge_parameters["central_scale"] == "none"

    haar = next(row for row in first if row["campaign"] == "haar_unitary_null")
    haar_parameters = json.loads(haar["parameters_json"])
    assert haar_parameters["backend"] == "haar_unitary"
    assert haar_parameters["seed"] == 20260815


def test_cross_physical_architecture_variants_build_hermitian_small_matrices() -> None:
    config = json.loads(
        (ROOT / "configs" / "hamiltonian_classification_zeus_campaign.json").read_text()
    )
    rows = [
        row
        for row in MODULE.expanded_points(config)
        if row["campaign"] == "cross_physical_architectures"
        and row["detector_n"] == 8
    ]

    assert {row["scan_value"] for row in rows} == {
        "noninteracting_star",
        "interacting_ising_ring",
        "xy_ring_collective",
        "xy_chain_edge",
    }
    for row in rows:
        parameters = json.loads(row["parameters_json"])
        parameters["detector_n"] = 3
        parameters["n_phi"] = 4
        parameters["n_mu"] = 2
        parameters["l_max"] = 1
        point = SinglePixelClassificationPoint(**parameters)
        hamiltonian = build_single_pixel_hamiltonian(point)
        assert hamiltonian.shape == (16, 16)
        assert np.allclose(hamiltonian, hamiltonian.conj().T)
        result = classify_single_pixel_point(point)
        assert result.summary["qz_valid"] is True
        assert result.summary["root_count"] == 8
