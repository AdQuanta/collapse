"""Tests for network finite-size dynamics/spacing figures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from scripts.build_network_wd_nonborn_size_spacing_figures import _load_spacing


def test_load_spacing_retains_distinct_sector_histograms(tmp_path: Path) -> None:
    records = [
        {
            "key": "sector_00",
            "symmetry_label": "weight 3",
            "dimension": 12,
            "mean_adjacent_gap_ratio": 0.51,
        },
        {
            "key": "sector_01",
            "symmetry_label": "weight 4",
            "dimension": 15,
            "mean_adjacent_gap_ratio": 0.53,
        },
    ]
    (tmp_path / "detector_spacing_metadata.json").write_text(
        json.dumps({"sectors": records}), encoding="utf-8"
    )
    np.savez_compressed(
        tmp_path / "detector_spacing_summary.npz",
        sector_00__edges=np.asarray([0.0, 1.0, 2.0]),
        sector_00__density=np.asarray([0.2, 0.8]),
        sector_01__edges=np.asarray([0.0, 0.5, 2.0]),
        sector_01__density=np.asarray([0.6, 0.4]),
    )

    loaded = _load_spacing(tmp_path)

    assert [item["metadata"]["dimension"] for item in loaded] == [12, 15]
    np.testing.assert_allclose(loaded[1]["edges"], [0.0, 0.5, 2.0])
    np.testing.assert_allclose(loaded[0]["density"], [0.2, 0.8])
