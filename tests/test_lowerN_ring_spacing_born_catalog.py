"""Checks for the lower-N ring spacing/Born catalog."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import requires_paths
from scripts.run_lowerN_ring_spacing_born_catalog import inventory_cases
from scripts.summarize_lowerN_ring_spacing_born_catalog import _spacing_class


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "lowerN_ring_spacing_born_catalog.json"
SELECTION = ROOT / "configs" / "hz0_0_ring_spacing_born_10x4.json"


@requires_paths(
    "work/zeus_top20_last5_largerN_20260810_001532/source_03",
    "work/zeus_sobol_second_neighbor_hz0_0_N14_20260805_224342",
    "work/zeus_sobol_coupling_scans_20260726_200003",
)
def test_inventory_has_expected_deterministic_array_partition() -> None:
    cases = inventory_cases(json.loads(CONFIG.read_text(encoding="utf-8")))
    assert len(cases) == 91
    assert [case.array_index for case in cases] == list(range(91))
    assert sum(case.source_name == "second_neighbor_born_N16" for case in cases) == 11
    assert (
        sum(
            case.source_name == "second_neighbor_clearly_nonborn_N14"
            for case in cases
        )
        == 60
    )
    assert (
        sum(
            case.source_name == "nearest_neighbor_clearly_nonborn_N13"
            for case in cases
        )
        == 20
    )
    assert all(case.hz0 == 0.0 for case in cases)


def test_spacing_class_requires_mean_and_ks_agreement() -> None:
    classification = json.loads(SELECTION.read_text(encoding="utf-8"))
    assert _spacing_class(0.525, 0.20, 0.02, classification)[0] == "wigner_dyson"
    assert _spacing_class(0.390, 0.02, 0.20, classification)[0] == "poisson"
    assert _spacing_class(0.525, 0.02, 0.20, classification)[0] == "mixed"
