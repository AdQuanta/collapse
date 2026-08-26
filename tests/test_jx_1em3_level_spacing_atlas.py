from __future__ import annotations

from pathlib import Path

from examples.build_jx_1em3_level_spacing_atlas import (
    AtlasCase,
    _local_raw_path,
    summarize_scores,
)


def _case(score: float, *, hz: float, jpm: float, coverage: float = 1.0) -> AtlasCase:
    return AtlasCase(
        ordinal=1,
        dynamics_n=14,
        hz=hz,
        j=1.0,
        jpm=jpm,
        jx=0.001,
        hz0=0.0,
        evolution_time=1.0e6,
        source_s_born=score,
        source_rmse=0.03,
        angular_bin_coverage=coverage,
        raw_path="unused.npz",
    )


def test_zeus_raw_path_is_rebased_to_downloaded_campaign(tmp_path: Path) -> None:
    source = (
        "/home/user/repo/work/campaign/raw/N14/hz_p0p01/J_p1/"
        "Jpm_p0p1/spectrum_t1000000.npz"
    )
    expected = (
        tmp_path / "raw" / "N14" / "hz_p0p01" / "J_p1" / "Jpm_p0p1"
        / "spectrum_t1000000.npz"
    ).resolve()
    assert _local_raw_path(tmp_path, source) == expected


def test_high_score_summary_uses_declared_threshold_and_full_coverage() -> None:
    cases = [
        _case(0.90, hz=0.01, jpm=0.10),
        _case(0.80, hz=-0.01, jpm=0.25),
        _case(0.70, hz=1.00, jpm=1.00, coverage=0.5),
    ]
    summary = summarize_scores(cases)
    assert summary["high_definition"] == "S_born >= 0.75"
    assert summary["high_count"] == 2
    assert summary["high_small_field_count"] == 2
    assert summary["all_high_have_full_angular_coverage"] is True
