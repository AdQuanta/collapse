"""Load and continue exact resampled-network cases at new detector sizes.

At the source size, the saved graph is reconstructed exactly from its stored
generator specification and seed and checked against the saved edge list.  A
random graph has no canonical continuation to a different node count, so at a
new size the same graph family, generator parameters, and realization seed are
used to generate a new graph.  Provenance records this distinction explicitly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Any

from core.detector_graphs import DetectorGraphSpec, detector_graph_edges
from core.ranked_born_campaign import RankedHamiltonianCase


@dataclass(frozen=True)
class ResampledNetworkCase:
    """One saved ``(Hamiltonian configuration, graph realization)`` pair."""

    selection_key: str
    realization_index: int
    source_case_dir: str
    original_collective_jx: float
    case: RankedHamiltonianCase
    saved_edges_n12: tuple[tuple[int, int], ...]
    saved_graph_provenance: dict[str, Any]

    @property
    def sample_key(self) -> str:
        return f"{self.selection_key}/realization_{self.realization_index:02d}"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _finite_float(payload: dict[str, Any], key: str, source: Path) -> float:
    try:
        value = float(payload[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"missing or invalid {key!r} in {source}") from exc
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key!r} in {source}")
    return value


def _saved_edges(graph: dict[str, Any], source: Path) -> tuple[tuple[int, int], ...]:
    raw_edges = graph.get("edges_zero_based")
    if not isinstance(raw_edges, list):
        raise ValueError(f"missing detector graph edge list in {source}")
    try:
        edges = tuple(sorted(tuple(int(value) for value in edge) for edge in raw_edges))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid detector graph edge list in {source}") from exc
    if any(len(edge) != 2 or edge[0] >= edge[1] for edge in edges):
        raise ValueError(f"invalid zero-based undirected edge in {source}")
    return edges


def load_resampled_network_cases(
    source_root: Path,
    *,
    jx_scale_factor: float,
    expected_count: int | None = 400,
) -> tuple[ResampledNetworkCase, ...]:
    """Load saved graph samples and reduce collective ``Jx`` exactly once."""

    source_root = Path(source_root).resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(f"source campaign does not exist: {source_root}")
    if not math.isfinite(jx_scale_factor) or not 0.0 < jx_scale_factor < 1.0:
        raise ValueError("jx_scale_factor must be finite and lie strictly in (0, 1)")

    loaded: list[ResampledNetworkCase] = []
    pattern = "family_*/*/realization_*/N12/metadata.json"
    for metadata_path in sorted(source_root.glob(pattern)):
        case_dir = metadata_path.parent
        required = (
            case_dir / "COMPLETE.json",
            case_dir / "metrics.json",
            case_dir / "validation.json",
        )
        if not all(path.is_file() for path in required):
            continue
        validation = _read_json(case_dir / "validation.json")
        if not bool(validation.get("passed", False)):
            raise ValueError(f"source scientific validation failed: {case_dir}")
        metadata = _read_json(metadata_path)
        metrics = _read_json(case_dir / "metrics.json")
        source = metadata.get("source")
        graph = metadata.get("detector_graph")
        if not isinstance(source, dict) or not isinstance(graph, dict):
            raise ValueError(f"missing source or detector_graph in {metadata_path}")
        if int(metadata.get("target_N", -1)) != 12 or int(graph.get("nodes", -1)) != 12:
            raise ValueError(f"expected an N=12 source realization in {metadata_path}")
        raw_spec = graph.get("spec")
        if not isinstance(raw_spec, dict):
            raise ValueError(f"missing detector_graph.spec in {metadata_path}")
        graph_spec = DetectorGraphSpec(**raw_spec)
        saved_edges = _saved_edges(graph, metadata_path)
        reconstructed_edges = detector_graph_edges(12, graph_spec)
        if reconstructed_edges != saved_edges:
            raise ValueError(
                f"saved N=12 graph is not reproduced by its specification: {case_dir}"
            )

        relative = case_dir.relative_to(source_root)
        if len(relative.parts) != 4:
            raise ValueError(f"unexpected source layout: {case_dir}")
        family_dir, cohort_dir, realization_dir, n_dir = relative.parts
        if n_dir != "N12" or not realization_dir.startswith("realization_"):
            raise ValueError(f"unexpected source layout: {case_dir}")
        realization_index = int(realization_dir.removeprefix("realization_"))
        original_jx = _finite_float(source, "jx", metadata_path)
        reduced_jx = original_jx * jx_scale_factor
        connectivity = str(graph.get("canonical_kind", raw_spec.get("kind")))
        ranked_case = RankedHamiltonianCase(
            source_root=str(source_root),
            source_case=relative.as_posix(),
            source_metric_file=(relative / "metrics.json").as_posix(),
            source_s_born=_finite_float(metrics, "S_born", case_dir / "metrics.json"),
            source_n=12,
            hz=_finite_float(source, "hz", metadata_path),
            hz0=_finite_float(metadata, "hz0", metadata_path),
            j=_finite_float(source, "j", metadata_path),
            jpm=_finite_float(source, "jpm", metadata_path),
            jx=reduced_jx,
            jy=float(source.get("jy", 0.0)),
            j2=float(source.get("j2", 0.0)),
            jpm2=float(source.get("jpm2", 0.0)),
            connectivity=connectivity,
            central_coupling=str(metadata.get("central_coupling", "all")),
            evolution_time=_finite_float(source, "evolution_time", metadata_path),
            model_seed=int(source.get("model_seed", 44)),
            graph_spec=asdict(graph_spec),
            source_graph_metadata=dict(graph),
        )
        provenance = metadata.get("graph_provenance")
        loaded.append(
            ResampledNetworkCase(
                selection_key=f"{family_dir}/{cohort_dir}",
                realization_index=realization_index,
                source_case_dir=str(case_dir.resolve()),
                original_collective_jx=original_jx,
                case=ranked_case,
                saved_edges_n12=saved_edges,
                saved_graph_provenance=(
                    dict(provenance) if isinstance(provenance, dict) else {}
                ),
            )
        )

    loaded.sort(key=lambda item: (item.selection_key, item.realization_index))
    keys = [item.sample_key for item in loaded]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate configuration/realization keys in source campaign")
    if expected_count is not None and len(loaded) != expected_count:
        raise ValueError(
            f"expected {expected_count} validated graph samples, found {len(loaded)}"
        )
    return tuple(loaded)


def graph_spec_and_provenance(
    item: ResampledNetworkCase,
    detector_n: int,
    *,
    jx_scale_factor: float,
) -> tuple[DetectorGraphSpec, dict[str, Any]]:
    """Return the saved sample specification and honest size provenance."""

    if detector_n < 3:
        raise ValueError("detector_n must be at least three")
    if item.case.graph_spec is None:
        raise ValueError(f"missing graph specification for {item.sample_key}")
    spec = DetectorGraphSpec(**item.case.graph_spec)
    common = {
        "source_sample_key": item.sample_key,
        "source_case_dir": item.source_case_dir,
        "source_detector_n": 12,
        "target_detector_n": detector_n,
        "realization_index_one_based": item.realization_index,
        "realization_seed": spec.seed,
        "effective_graph_spec": asdict(spec),
        "original_collective_Jx": item.original_collective_jx,
        "jx_scale_factor": jx_scale_factor,
        "reduced_collective_Jx": item.case.jx,
        "collective_Jx_change": "reduced once before the usual Jx/sqrt(N) scaling",
    }
    if detector_n == 12:
        return spec, {
            **common,
            "mode": "exact_saved_N12_graph_realization",
            "is_same_edge_set_as_source": True,
            "saved_source_graph_provenance": item.saved_graph_provenance,
        }
    return spec, {
        **common,
        "mode": "same_generator_parameters_and_realization_seed_at_new_N",
        "is_same_edge_set_as_source": False,
        "note": (
            "Random-network connectivity has no canonical scaling across N. "
            "This graph is deterministically regenerated at target N from the "
            "saved sample's family parameters and seed; it is not an extension "
            "or induced subgraph of the N=12 edge set."
        ),
        "saved_source_graph_provenance": item.saved_graph_provenance,
    }


def campaign_manifest(
    items: tuple[ResampledNetworkCase, ...],
    *,
    jx_scale_factor: float,
    target_sizes: tuple[int, ...],
    evolution_times_by_n: dict[int, tuple[float, ...]],
    target_time_averaged_sample_count: int,
) -> dict[str, Any]:
    """Serialize the exact input ordering and coupling transformation."""

    return {
        "sample_count": len(items),
        "target_detector_sizes": list(target_sizes),
        "hamiltonian_size_case_count": len(items) * len(target_sizes),
        "target_time_averaged_sample_count_per_case_and_N": (
            target_time_averaged_sample_count
        ),
        "evolution_times_by_N": {
            f"N{detector_n}": list(evolution_times_by_n[detector_n])
            for detector_n in target_sizes
        },
        "time_counts_by_N": {
            f"N{detector_n}": len(evolution_times_by_n[detector_n])
            for detector_n in target_sizes
        },
        "time_evaluation_count": len(items)
        * sum(len(evolution_times_by_n[detector_n]) for detector_n in target_sizes),
        "time_average_definition": (
            "equal-weight average of normalized P(theta;t) over the configured "
            "times, followed by R=P_bar/(P_bar+P_bar_reflected)"
        ),
        "jx_scale_factor": jx_scale_factor,
        "jx_transformation": (
            "Jx_collective_new = 0.1 * Jx_collective_source; "
            "Jx_edge_new(N) = Jx_collective_new / sqrt(N)"
        ),
        "graph_size_policy": (
            "exact saved edge set at N=12; same graph generator parameters and "
            "sample seed at N>12, producing a new deterministic edge set"
        ),
        "samples": [
            {
                "global_index": index,
                "sample_key": item.sample_key,
                "source_case_dir": item.source_case_dir,
                "source_S_born": item.case.source_s_born,
                "graph_seed": item.case.graph_spec["seed"],
                "original_collective_Jx": item.original_collective_jx,
                "reduced_collective_Jx": item.case.jx,
            }
            for index, item in enumerate(items)
        ],
    }
