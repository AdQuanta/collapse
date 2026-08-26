from __future__ import annotations

from pathlib import Path

from examples.build_network_extremes_resampled_all_3x5 import (
    discover_selections,
    output_path,
)
from examples.build_network_extremes_resampled_sample_3x5 import _realization_dirs


def test_realization_dirs_require_five_complete_results(tmp_path: Path) -> None:
    selection = "family_00_example/highest_01"
    for index in range(1, 6):
        target = tmp_path / selection / f"realization_{index:02d}" / "N12"
        target.mkdir(parents=True)
        (target / "COMPLETE.json").write_text("{}", encoding="utf-8")
    directories = _realization_dirs(tmp_path, selection)
    assert len(directories) == 5
    assert directories[0].parts[-2:] == ("realization_01", "N12")


def test_batch_discovery_requires_all_five_realizations(tmp_path: Path) -> None:
    complete_selection = "family_00_example/highest_01"
    incomplete_selection = "family_00_example/lowest_01"
    for selection, count in ((complete_selection, 5), (incomplete_selection, 4)):
        for index in range(1, count + 1):
            marker = (
                tmp_path
                / selection
                / f"realization_{index:02d}"
                / "N12"
                / "COMPLETE.json"
            )
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("{}", encoding="utf-8")

    assert discover_selections(tmp_path) == (complete_selection,)


def test_batch_output_path_separates_graph_families(tmp_path: Path) -> None:
    assert output_path(
        tmp_path, "family_03_expander/lowest_10"
    ) == tmp_path / "03_expander" / "lowest_10.png"
