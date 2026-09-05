"""Selection and graph provenance for ranked network follow-up campaigns."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
from pathlib import Path
from typing import Any

from core.detector_graphs import DetectorGraphSpec, detector_graph_edges
from core.ranked_born_campaign import (
    RankedHamiltonianCase,
    graph_spec_for_case,
    load_ranked_cases,
)


@dataclass(frozen=True)
class ExtremeNetworkCase:
    """One high- or low-``S_born`` source case with deterministic rank."""

    family: str
    family_index: int
    cohort: str
    cohort_rank: int
    case: RankedHamiltonianCase

    @property
    def selection_key(self) -> str:
        return (
            f"family_{self.family_index:02d}_{self.family}/"
            f"{self.cohort}_{self.cohort_rank:02d}"
        )


def select_extreme_cases(
    source: Path,
    *,
    family: str,
    family_index: int,
    count_per_tail: int,
) -> tuple[ExtremeNetworkCase, ...]:
    """Select disjoint upper and lower tails of stored source ``S_born``."""

    if count_per_tail < 1:
        raise ValueError("count_per_tail must be positive")
    ranked = load_ranked_cases(source)
    if len(ranked) < 2 * count_per_tail:
        raise ValueError(
            f"{source} has {len(ranked)} eligible cases; "
            f"at least {2 * count_per_tail} are required"
        )
    highest = ranked[:count_per_tail]
    lowest = sorted(
        ranked,
        key=lambda case: (case.source_s_born, case.source_case),
    )[:count_per_tail]
    overlap = {case.identity_digest for case in highest} & {
        case.identity_digest for case in lowest
    }
    if overlap:
        raise RuntimeError("highest and lowest selections unexpectedly overlap")
    return tuple(
        [
            ExtremeNetworkCase(
                family=family,
                family_index=family_index,
                cohort="highest",
                cohort_rank=rank_index,
                case=case,
            )
            for rank_index, case in enumerate(highest, start=1)
        ]
        + [
            ExtremeNetworkCase(
                family=family,
                family_index=family_index,
                cohort="lowest",
                cohort_rank=rank_index,
                case=case,
            )
            for rank_index, case in enumerate(lowest, start=1)
        ]
    )


def select_top_cases(
    source: Path,
    *,
    family: str,
    family_index: int,
    count: int,
) -> tuple[ExtremeNetworkCase, ...]:
    """Select the highest stored-``S_born`` cases from one graph family."""

    if count < 1:
        raise ValueError("count must be positive")
    ranked = load_ranked_cases(source)
    if len(ranked) < count:
        raise ValueError(
            f"{source} has {len(ranked)} eligible cases; {count} are required"
        )
    return tuple(
        ExtremeNetworkCase(
            family=family,
            family_index=family_index,
            cohort="highest",
            cohort_rank=rank_index,
            case=case,
        )
        for rank_index, case in enumerate(ranked[:count], start=1)
    )


def select_top_all_families(
    families: list[dict[str, Any]],
    *,
    repository_root: Path,
    count_per_family: int,
) -> tuple[ExtremeNetworkCase, ...]:
    """Select the highest stored-``S_born`` cases independently per family."""

    selected: list[ExtremeNetworkCase] = []
    for family_index, item in enumerate(families):
        name = str(item["name"])
        source = (repository_root / str(item["source_root"])).resolve()
        selected.extend(
            select_top_cases(
                source,
                family=name,
                family_index=family_index,
                count=count_per_family,
            )
        )
    return tuple(selected)


def select_all_families(
    families: list[dict[str, Any]],
    *,
    repository_root: Path,
    count_per_tail: int,
) -> tuple[ExtremeNetworkCase, ...]:
    """Select both tails independently for each configured graph family."""

    selected: list[ExtremeNetworkCase] = []
    for family_index, item in enumerate(families):
        name = str(item["name"])
        source = (repository_root / str(item["source_root"])).resolve()
        selected.extend(
            select_extreme_cases(
                source,
                family=name,
                family_index=family_index,
                count_per_tail=count_per_tail,
            )
        )
    return tuple(selected)


def select_named_cases(
    cases: list[dict[str, Any]],
    *,
    repository_root: Path,
) -> tuple[ExtremeNetworkCase, ...]:
    """Resolve an explicit, validated source case from each configured family."""

    if not cases:
        raise ValueError("cases must be nonempty")
    selected: list[ExtremeNetworkCase] = []
    seen: set[str] = set()
    for family_index, item in enumerate(cases):
        family = str(item["family"])
        source_root = (repository_root / str(item["source_root"])).resolve()
        source_case = str(item["source_case"])
        key = f"{family}:{source_case}"
        if key in seen:
            raise ValueError(f"duplicate named case {key}")
        seen.add(key)
        matches = [
            case
            for case in load_ranked_cases(source_root)
            if case.source_case == source_case
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected exactly one match for {key} in {source_root}; "
                f"found {len(matches)}"
            )
        case = matches[0]
        expected_digest = str(item["expected_scientific_identity_digest"])
        if case.scientific_identity_digest != expected_digest:
            raise ValueError(
                f"scientific identity mismatch for {key}: "
                f"{case.scientific_identity_digest} != "
                f"{expected_digest}"
            )
        expected_score = float(item["expected_source_S_born"])
        if abs(case.source_s_born - expected_score) > 1.0e-12:
            raise ValueError(
                f"source S_born mismatch for {key}: {case.source_s_born} != "
                f"{expected_score}"
            )
        selected.append(
            ExtremeNetworkCase(
                family=family,
                family_index=family_index,
                cohort="wd_nonborn",
                cohort_rank=1,
                case=case,
            )
        )
    return tuple(selected)


def resampled_graph_spec(
    selected: ExtremeNetworkCase,
    realization_index: int,
) -> tuple[DetectorGraphSpec, dict[str, Any]]:
    """Return a reproducible new graph realization with unchanged parameters."""

    if realization_index < 0:
        raise ValueError("realization_index must be nonnegative")
    source_spec = graph_spec_for_case(selected.case)
    source_metadata = selected.case.source_graph_metadata or {}
    raw_source_edges = source_metadata.get("edges_zero_based")
    source_edges = (
        tuple(tuple(int(value) for value in edge) for edge in raw_source_edges)
        if isinstance(raw_source_edges, list)
        else detector_graph_edges(selected.case.source_n, source_spec)
    )
    accepted: list[tuple[DetectorGraphSpec, tuple[tuple[int, int], ...], int]] = []
    used_edges = {source_edges}
    for current_index in range(realization_index + 1):
        for rejection_index in range(10_000):
            digest_input = (
                f"network-extremes-resample-v1|{selected.case.identity_digest}|"
                f"{current_index}|{rejection_index}"
            ).encode("utf-8")
            new_seed = int.from_bytes(
                hashlib.sha256(digest_input).digest()[:4], "little"
            )
            if new_seed == source_spec.seed:
                continue
            candidate = replace(source_spec, seed=new_seed)
            candidate_edges = detector_graph_edges(selected.case.source_n, candidate)
            if candidate_edges in used_edges:
                continue
            accepted.append((candidate, candidate_edges, rejection_index))
            used_edges.add(candidate_edges)
            break
        else:
            raise RuntimeError(
                "failed to generate a graph distinct from the source and prior "
                "realizations after 10000 deterministic seed candidates"
            )
    specification, _, rejection_index = accepted[realization_index]
    new_seed = specification.seed
    return specification, {
        "mode": "independent_resample_same_family_parameters",
        "source_graph_seed": source_spec.seed,
        "realization_index_zero_based": realization_index,
        "realization_index_one_based": realization_index + 1,
        "resampled_graph_seed": new_seed,
        "seed_derivation": (
            "first 32 bits of SHA256(network-extremes-resample-v1, "
            "source case identity digest, realization index, rejection index)"
        ),
        "rejection_index": rejection_index,
        "edge_distinctness": (
            "edge set differs from the saved source graph and all lower-indexed "
            "realizations for this source case"
        ),
        "source_graph_spec": asdict(source_spec),
        "effective_graph_spec": asdict(specification),
    }


def same_seed_larger_n_provenance(
    selected: ExtremeNetworkCase,
    detector_n: int,
) -> tuple[DetectorGraphSpec, dict[str, Any]]:
    """Reuse graph generator parameters and seed at a different node count."""

    source_spec = graph_spec_for_case(selected.case)
    return source_spec, {
        "mode": "same_generator_spec_and_seed_at_new_node_count",
        "source_detector_n": selected.case.source_n,
        "target_detector_n": detector_n,
        "source_graph_seed": source_spec.seed,
        "effective_graph_spec": asdict(source_spec),
        "is_scaled_source_graph": False,
        "note": (
            "Random-network connectivity does not scale canonically. The graph "
            "is regenerated deterministically at target N using the saved "
            "family parameters and seed; it is not a subgraph or extension of "
            "the source N=12 realization."
        ),
    }


def selection_manifest(selected: tuple[ExtremeNetworkCase, ...]) -> dict[str, Any]:
    """Serialize the exact high/low selection and its deterministic ordering."""

    return {
        "ranking": (
            "per graph family; highest cohort uses decreasing stored S_born, "
            "lowest cohort uses increasing stored S_born; source path breaks ties"
        ),
        "selected_count": len(selected),
        "cases": [
            {
                "global_index": index,
                "family": item.family,
                "family_index": item.family_index,
                "cohort": item.cohort,
                "cohort_rank": item.cohort_rank,
                "selection_key": item.selection_key,
                "source": asdict(item.case),
            }
            for index, item in enumerate(selected)
        ],
    }


def top_selection_manifest(
    selected: tuple[ExtremeNetworkCase, ...],
) -> dict[str, Any]:
    """Serialize an independently ranked top-only network selection."""

    return {
        "ranking": (
            "independently within each graph family by decreasing stored "
            "canonical S_born; source case path breaks exact ties"
        ),
        "selection_metric": "stored canonical S_born from each source campaign",
        "selected_count": len(selected),
        "cases": [
            {
                "global_index": index,
                "family": item.family,
                "family_index": item.family_index,
                "family_rank": item.cohort_rank,
                "selection_key": item.selection_key,
                "source": asdict(item.case),
            }
            for index, item in enumerate(selected)
        ],
    }
