from __future__ import annotations

import csv
from pathlib import Path

from collapse.anisotropic_sweep import AnisotropicSweepConfig
from examples.run_zeus_vab_atlas_hz0_0p1_N14 import (
    SHARD_COUNT,
    _configuration_payloads,
    build_batch_plan,
    validate_production_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "zeus_vab_atlas_hz0_0p1_N14.json"
ATLAS = ROOT / "reports" / "vab_coupling_group_atlas_2026-07-28" / "data" / "case_index.csv"
PBS = ROOT / "hpc" / "zeus_vab_atlas_hz0_0p1_N14_array.pbs"
SUBMIT = ROOT / "hpc" / "submit_zeus_vab_atlas_hz0_0p1_N14.sh"


def test_campaign_reproduces_the_atlas_grid_with_only_hz0_changed() -> None:
    config = AnisotropicSweepConfig.from_json(CONFIG)
    validate_production_config(config)
    assert config.detector_sizes == (14,)
    assert config.hz0 == 0.1
    assert config.jx == 0.01
    assert config.evolution_time == 1.0e6

    planned = []
    ordinals = []
    shard_sizes = []
    task_indices = []
    for batch_index in range(SHARD_COUNT):
        plan = build_batch_plan(config, batch_index)
        payloads = _configuration_payloads(config, plan)
        planned.extend((row["hz"], row["J"], row["Jpm"]) for row in payloads)
        ordinals.extend(int(row["ordinal"]) for row in payloads)
        shard_sizes.append(plan.configuration_count)
        task_indices.extend(plan.task_indices)
        assert all(row["N"] == 14 for row in payloads)
        assert all(row["hz0"] == 0.1 for row in payloads)
        assert all(row["Jx"] == 0.01 and row["Jy"] == 0.0 for row in payloads)
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


def test_pbs_and_submit_wrapper_encode_the_nine_shards() -> None:
    pbs = PBS.read_text(encoding="utf-8")
    submit = SUBMIT.read_text(encoding="utf-8")
    assert "#PBS -J 0-8" in pbs
    assert "#PBS -l select=1:ncpus=8:mem=128gb" in pbs
    assert "python3.11 examples/run_zeus_vab_atlas_hz0_0p1_N14.py" in pbs
    assert "--workers 2" in pbs
    assert "--resume" in pbs
    assert "activate" not in pbs.lower()
    assert "100x8+80" in submit
    assert "zeus_vab_atlas_hz0_0p1_N14_array.pbs" in submit
