"""Checks for the 23-case N=17 ring catalog continuation."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import requires_paths
from scripts.run_zeus_ring_catalog_missing_n17 import (
    _ranked_case,
    _validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "zeus_ring_catalog_missing_n17.json"


def test_config_has_exact_non_n17_partition() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    _validate_config(config)
    cases = config["cases"]
    assert len(cases) == 23
    assert {case["source_detector_n"] for case in cases} == {13, 14, 16}
    assert sum(case["source_detector_n"] == 13 for case in cases) == 3
    assert sum(case["source_detector_n"] == 14 for case in cases) == 17
    assert sum(case["source_detector_n"] == 16 for case in cases) == 3
    assert sum(case["family"] == "nearest_neighbor" for case in cases) == 3
    assert sum(case["family"] == "second_neighbor" for case in cases) == 20
    assert all(case["hz0"] == 0.0 for case in cases)


@requires_paths(
    "work/zeus_top20_last5_largerN_20260810_001532",
    "work/zeus_sobol_second_neighbor_hz0_0_N14_20260805_224342",
    "work/zeus_sobol_coupling_scans_20260726_200003",
)
def test_all_frozen_source_hashes_and_physics_validate() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    cases = [_ranked_case(case) for case in config["cases"]]
    assert len(cases) == 23
    assert all(case.connectivity == "ring" for case in cases)
    assert all(case.hz0 == 0.0 for case in cases)
    assert all(case.evolution_time == 1.0e6 for case in cases)
