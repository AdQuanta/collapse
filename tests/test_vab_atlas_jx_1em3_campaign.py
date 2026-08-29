from __future__ import annotations

import csv
import math
from pathlib import Path

from core.anisotropic_sweep import AnisotropicSweepConfig
from scripts.run_zeus_vab_atlas_hz0_0p1_N14 import (
    SHARD_COUNT,
    _configuration_payloads,
)
from scripts.run_zeus_vab_atlas_jx_1em3_N14 import (
    COLLECTIVE_JX,
    HZ0,
    build_batch_plan,
    validate_production_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "zeus_vab_atlas_jx_1em3_N14.json"
ATLAS = (
    ROOT / "reports" / "vab_coupling_group_atlas_2026-07-28"
    / "data" / "case_index.csv"
)
PBS = ROOT / "hpc" / "zeus_vab_atlas_jx_1em3_N14_array.pbs"
SUBMIT = ROOT / "hpc" / "submit_zeus_vab_atlas_jx_1em3_N14.sh"


def test_campaign_preserves_atlas_grid_and_changes_only_collective_jx() -> None:
    config = AnisotropicSweepConfig.from_json(CONFIG)
    validate_production_config(config)
    assert config.detector_sizes == (14,)
    assert config.hz0 == HZ0 == 0.0
    assert config.jx == COLLECTIVE_JX == 1.0e-3
    assert math.isclose(config.jx / math.sqrt(14), 1.0e-3 / math.sqrt(14))
    assert config.evolution_time == 1.0e6

    planned: list[tuple[float, float, float]] = []
    ordinals: list[int] = []
    shard_sizes: list[int] = []
    task_indices: list[int] = []
    for batch_index in range(SHARD_COUNT):
        plan = build_batch_plan(config, batch_index)
        payloads = _configuration_payloads(config, plan)
        planned.extend((row["hz"], row["J"], row["Jpm"]) for row in payloads)
        ordinals.extend(int(row["ordinal"]) for row in payloads)
        shard_sizes.append(plan.configuration_count)
        task_indices.extend(plan.task_indices)
        assert all(row["N"] == 14 for row in payloads)
        assert all(row["hz0"] == 0.0 for row in payloads)
        assert all(row["Jx"] == 1.0e-3 and row["Jy"] == 0.0 for row in payloads)
        assert all(row["t"] == 1.0e6 for row in payloads)

    with ATLAS.open(newline="", encoding="utf-8-sig") as handle:
        source = [
            (float(row["hz"]), float(row["j"]), float(row["jpm"]))
            for row in csv.DictReader(handle)
        ]
    assert planned == source
    assert ordinals == list(range(1, 881))
    assert task_indices == list(range(1, 89))
    assert shard_sizes == [100] * 8 + [80]


def test_jx_1em3_pbs_and_submit_wrapper_encode_resources_and_shards() -> None:
    pbs = PBS.read_text(encoding="utf-8")
    submit = SUBMIT.read_text(encoding="utf-8")
    assert "#PBS -J 0-8" in pbs
    assert "#PBS -l select=1:ncpus=8:mem=128gb" in pbs
    assert "python3.11 scripts/run_zeus_vab_atlas_jx_1em3_N14.py" in pbs
    assert "--workers 2" in pbs
    assert "--resume" in pbs
    assert "activate" not in pbs.lower()
    assert "Jx_unscaled=1e-3" in pbs
    assert "100x8+80" in submit
    assert "zeus_vab_atlas_jx_1em3_N14_array.pbs" in submit

