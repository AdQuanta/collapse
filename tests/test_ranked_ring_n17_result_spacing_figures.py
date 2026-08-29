from pathlib import Path

import pytest

from scripts.build_ranked_ring_n17_result_spacing_figures import (
    _runtime_provenance,
    fresh_result_dir,
    validate_detector_parameters,
)


def _case_info() -> dict[str, object]:
    return {
        "family": "second_neighbor",
        "tail": "highest",
        "rank_within_tail": 3,
        "config_id": "config_353",
        "parameters": {
            "hz": 0.1,
            "j": 0.2,
            "jpm": 0.3,
            "j2": 0.4,
            "jpm2": 0.5,
        },
    }


def test_fresh_result_dir_matches_campaign_layout() -> None:
    result = fresh_result_dir(Path("campaign"), _case_info(), 17)

    assert result == (
        Path("campaign")
        / "second_neighbor"
        / "highest"
        / "rank_03__config_353"
        / "N17"
    )


def test_detector_parameter_validation_accepts_identical_hamiltonian() -> None:
    metadata = {"source": dict(_case_info()["parameters"])}

    validate_detector_parameters(_case_info(), metadata)


def test_detector_parameter_validation_rejects_mismatched_hamiltonian() -> None:
    metadata = {"source": {**dict(_case_info()["parameters"]), "j2": 0.41}}

    with pytest.raises(ValueError, match="j2"):
        validate_detector_parameters(_case_info(), metadata)


def test_runtime_provenance_records_scientific_stack() -> None:
    runtime = _runtime_provenance()

    assert runtime["python"]
    assert Path(runtime["executable"]).is_absolute()
    assert Path(runtime["prefix"]).is_absolute()
    assert runtime["platform"]
    assert set(runtime["packages"]) == {
        "numpy",
        "scipy",
        "matplotlib",
        "pytest",
        "quspin",
        "quspin-extensions",
    }
