"""Campaign-map checks for all-sector N=17 full-Hamiltonian spacings."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.run_ring_hz0_all_sector_spacings import (
    DEFAULT_CONFIG,
    all_unique_sectors,
    sector_for_array_index,
    validate_scan_config,
)


def test_array_map_contains_twenty_unique_resolved_sectors() -> None:
    sectors = all_unique_sectors()
    assert len(sectors) == 20
    assert [sector.array_index for sector in sectors] == list(range(20))
    assert len({sector.sector_id for sector in sectors}) == 20
    for excitation_parity in (0, 1):
        parity_sectors = [
            sector
            for sector in sectors
            if sector.excitation_parity == excitation_parity
        ]
        assert {
            sector.reflection_parity
            for sector in parity_sectors
            if sector.momentum == 0
        } == {-1, 1}
        assert [
            sector.momentum
            for sector in parity_sectors
            if sector.reflection_parity is None
        ] == list(range(1, 9))


def test_sector_lookup_and_reflection_partners() -> None:
    assert sector_for_array_index(0).sector_id == "k00_even_reflection_plus"
    assert sector_for_array_index(9).sector_id == "k08_even"
    assert sector_for_array_index(10).sector_id == "k00_odd_reflection_plus"
    assert sector_for_array_index(19).sector_id == "k08_odd"
    assert sector_for_array_index(2).reflection_partner_momentum(17) == 16
    assert sector_for_array_index(9).reflection_partner_momentum(17) == 9


def test_versioned_campaign_config_is_self_contained() -> None:
    config_path = Path(DEFAULT_CONFIG)
    with config_path.open("r", encoding="utf-8") as stream:
        config = json.load(stream)
    validate_scan_config(config)
    assert len(config["cases"]) == 20
    assert all("source_result" not in case for case in config["cases"])


def test_pure_ising_ablation_config_is_valid_for_all_sector_campaign() -> None:
    config_path = (
        Path(__file__).resolve().parents[1]
        / "configs/ring_pure_ising_wd_ablation_hz0_scan_N17.json"
    )
    with config_path.open("r", encoding="utf-8") as stream:
        config = json.load(stream)
    validate_scan_config(config)
    assert len(config["cases"]) == 20
    assert all("source_result" not in case for case in config["cases"])
    assert config["base_parameters"]["jpm"] == 0.0
    assert config["base_parameters"]["j2"] == 0.0
    assert config["base_parameters"]["jpm2"] == 0.0
