"""Completeness and path gates for publication Figure A--D generation."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "plot_zeus_hamiltonian_classification.py"
)
SPEC = importlib.util.spec_from_file_location("classification_figures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _write_collection(root: Path, *, complete: int, expected: int) -> None:
    aggregate = root / "aggregated"
    aggregate.mkdir(parents=True)
    (aggregate / "collection_summary.json").write_text(
        json.dumps(
            {
                "complete": complete,
                "expected": expected,
                "missing": expected - complete,
                "corrupt": 0,
            }
        ),
        encoding="utf-8",
    )
    with (aggregate / "classification_results.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=["point_id"])
        writer.writeheader()
        for index in range(complete):
            writer.writerow({"point_id": index})


def test_incomplete_collection_is_rejected(tmp_path: Path) -> None:
    _write_collection(tmp_path, complete=2, expected=3)

    with pytest.raises(RuntimeError, match="campaign is incomplete"):
        MODULE.load_complete_results(tmp_path)


def test_complete_collection_cardinality_is_checked(tmp_path: Path) -> None:
    _write_collection(tmp_path, complete=2, expected=2)

    rows = MODULE.load_complete_results(tmp_path)

    assert len(rows) == 2


def test_figure_c_includes_explicit_physical_architectures(tmp_path: Path) -> None:
    rows = []
    point_id = 0
    for architecture in MODULE.ARCHITECTURE_LABELS:
        if architecture in {
            "erdos_renyi",
            "watts_strogatz",
            "barabasi_albert",
            "expander",
        }:
            campaign = "cross_network_matched"
            scan_value = architecture
        elif architecture == "cross_architecture_ring_control":
            campaign = architecture
            scan_value = "ring"
        elif architecture == "haar_unitary_null":
            campaign = architecture
            scan_value = "0"
        else:
            campaign = "cross_physical_architectures"
            scan_value = architecture
        for detector_n in (8, 10):
            rows.append(
                {
                    "point_id": str(point_id),
                    "campaign": campaign,
                    "scan_value": scan_value,
                    "N": str(detector_n),
                    "coverage": "1.0",
                    "higher_harmonic_leakage": "0.1",
                    "dipole_sharpness": "1.0",
                    "axis_fidelity": "1.0",
                    "epsilon_B": "0.1",
                }
            )
            point_id += 1

    MODULE._style()
    MODULE.plot_figure_c(
        rows,
        tmp_path / "figure_C",
        tmp_path / "figure_C_source.csv",
    )

    assert (tmp_path / "figure_C.png").is_file()
    assert (tmp_path / "figure_C.pdf").is_file()
    with (tmp_path / "figure_C_source.csv").open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))
    assert len(source_rows) == 20
