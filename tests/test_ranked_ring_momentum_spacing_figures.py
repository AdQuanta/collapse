from pathlib import Path

from scripts.build_ranked_ring_momentum_spacing_figures import (
    HamiltonianParameters,
    RankedCase,
    _analysis_digest,
    select_ranked_tails,
)
from scripts.build_ranked_ring_diagnostics_spacing_figures import (
    ROOT,
    _resolve_repo_path,
    _sector_key,
)


def _case(config_id: str, score: float) -> RankedCase:
    return RankedCase(
        family="nearest_neighbor",
        family_description="Nearest-neighbor ring",
        tail="unranked",
        rank_within_tail=0,
        config_id=config_id,
        source_dir=Path(config_id),
        source_n=14,
        s_born=score,
        born_rmse=0.1,
        occupied_fraction=1.0,
        parameters=HamiltonianParameters(hz=0.1, j=0.2, jpm=0.3, j2=0.0, jpm2=0.0),
        jx_unscaled=0.001,
        source_sobol_index=1,
    )


def test_select_ranked_tails_is_deterministic_and_disjoint() -> None:
    cases = [_case(f"config_{index:03d}", float(index)) for index in range(8)]

    selected = select_ranked_tails(list(reversed(cases)), count=2)

    lowest = [case for case in selected if case.tail == "lowest"]
    highest = [case for case in selected if case.tail == "highest"]
    assert [case.config_id for case in lowest] == ["config_000", "config_001"]
    assert [case.config_id for case in highest] == ["config_007", "config_006"]
    assert [case.rank_within_tail for case in lowest] == [1, 2]
    assert [case.rank_within_tail for case in highest] == [1, 2]
    assert {case.config_id for case in lowest}.isdisjoint(
        case.config_id for case in highest
    )


def test_analysis_digest_changes_with_physical_parameters_and_detector_n() -> None:
    original = _case("config_001", 0.7)
    changed = RankedCase(
        **{
            **original.__dict__,
            "parameters": HamiltonianParameters(
                hz=0.1,
                j=0.2,
                jpm=0.3,
                j2=0.05,
                jpm2=0.0,
            ),
        }
    )

    assert _analysis_digest(original, 17) != _analysis_digest(changed, 17)
    assert _analysis_digest(original, 17) != _analysis_digest(original, 15)


def test_combined_figure_sector_keys_match_spacing_archive_convention() -> None:
    base = {"momentum": 0, "n_up": 8}
    assert _sector_key({**base, "reflection_parity": 1}) == "k00_q08_p+1"
    assert _sector_key({**base, "reflection_parity": -1}) == "k00_q08_p-1"
    assert _sector_key(
        {"momentum": 7, "n_up": 6, "reflection_parity": None}
    ) == "k07_q06_pnone"


def test_combined_figure_resolves_transferred_windows_paths() -> None:
    resolved = _resolve_repo_path(
        r"reports\ranked_ring_spacings\case_N17_spectra.npz"
    )

    assert resolved == (
        ROOT / "reports" / "ranked_ring_spacings" / "case_N17_spectra.npz"
    )
