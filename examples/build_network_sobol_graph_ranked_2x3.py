"""Render four network-connectivity Sobol campaigns as ranked 2x3 atlases.

Each campaign is ranked independently by decreasing stored ``S_born``.  The
approved 18-by-10-inch diagnostics block is retained and the exact N=12
detector graph is appended on the right.  Detector spectral diagnostics use
N_D=10.  For every configuration separately, the lower-right 2x2 inset uses
the four largest nonredundant sectors obtained from fixed Hamming weight and
the complete automorphism group of that configuration's N=12 graph, together
with global spin reversal in the half-filled block.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-network-sobol-ranked-atlas")
)

from collapse.detector_graphs import DetectorGraphSpec  # noqa: E402
from collapse.graph_spectral_sectors import (  # noqa: E402
    largest_detector_symmetry_sectors,
)
from examples.build_network_sobol_graph_sample_2x3 import (  # noqa: E402
    SPECTRAL_N,
    compute_network_spectral,
    render_sample,
)
from examples.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    _load_result_arrays,
    inventory,
)


CAMPAIGNS = {
    "erdos_renyi": ROOT
    / "work/zeus_sobol_erdos_renyi_hz0_0_N12_20260809_150226",
    "watts_strogatz": ROOT
    / "work/zeus_sobol_watts_strogatz_hz0_0_N12_20260809_150226",
    "barabasi_albert": ROOT
    / "work/zeus_sobol_barabasi_albert_hz0_0_N12_20260809_150226",
    "expander": ROOT
    / "work/zeus_sobol_expander_hz0_0_N12_20260809_150228",
}
DEFAULT_OUTPUT = ROOT / "reports/network_sobol_graph_ranked_2x3_2026-08-12"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def rank_records(
    source: Path,
    output: Path,
    *,
    limit: int | None = None,
) -> tuple[list[CaseRecord], list[dict[str, Any]]]:
    """Rank all validated ``jy_zero/N12`` cases in one campaign."""

    records, unavailable = inventory(source)
    candidates: list[CaseRecord] = []
    for record in records:
        if record.family != "jy_zero" or record.dynamics_n != 12:
            continue
        case_dir = Path(record.source_dir)
        metadata = _read_json(case_dir / "metadata.json")
        validation_path = case_dir / "validation.json"
        if not validation_path.is_file() or not bool(
            _read_json(validation_path).get("passed", False)
        ):
            unavailable.append(
                {
                    "family": record.family,
                    "N": record.dynamics_n,
                    "config_id": record.config_id,
                    "reason": "source validation is missing or did not pass",
                }
            )
            continue
        graph = metadata.get("detector_graph")
        if not isinstance(graph, dict) or int(graph.get("nodes", -1)) != 12:
            unavailable.append(
                {
                    "family": record.family,
                    "N": record.dynamics_n,
                    "config_id": record.config_id,
                    "reason": "exact N=12 detector graph metadata is unavailable",
                }
            )
            continue
        if abs(float(metadata.get("hz0", float("nan")))) > 1.0e-14:
            unavailable.append(
                {
                    "family": record.family,
                    "N": record.dynamics_n,
                    "config_id": record.config_id,
                    "reason": "campaign case does not have hz0=0",
                }
            )
            continue
        candidates.append(record)
    candidates.sort(key=lambda record: (-record.s_born, record.config_id))
    if limit is not None:
        candidates = candidates[: max(0, limit)]
    ranked: list[CaseRecord] = []
    for rank, record in enumerate(candidates, start=1):
        score_token = f"{record.s_born:.6f}".replace(".", "p")
        filename = (
            f"rank_{rank:04d}__{record.config_id}__Sborn_{score_token}.png"
        )
        ranked.append(
            CaseRecord(
                **{
                    **asdict(record),
                    "rank": rank,
                    "within_n_rank": rank,
                    "output_path": str((output / filename).resolve()),
                }
            )
        )
    return ranked, unavailable


def _render_one(
    payload: tuple[dict[str, Any], int, bool],
) -> dict[str, Any]:
    record_data, dpi, force = payload
    record = CaseRecord(**record_data)
    target = Path(record.output_path)
    metadata_target = target.parent / "metadata" / f"{target.stem}.json"
    if target.is_file() and metadata_target.is_file() and not force:
        return {**_read_json(metadata_target), "status": "existing"}

    source_dir = Path(record.source_dir)
    source_metadata = _read_json(source_dir / "metadata.json")
    graph_metadata = source_metadata["detector_graph"]
    graph_spec = DetectorGraphSpec(**graph_metadata["spec"])
    spectral = compute_network_spectral(
        record,
        graph_spec,
        detector_n=SPECTRAL_N,
    )
    sector_spectra, sector_validation = largest_detector_symmetry_sectors(
        int(graph_metadata["nodes"]),
        [tuple(edge) for edge in graph_metadata["edges_zero_based"]],
        hz=record.hz,
        j=record.j,
        jpm=record.jpm,
        count=4,
    )
    arrays = _load_result_arrays(source_dir)
    rendered = render_sample(
        record,
        spectral,
        arrays,
        graph_metadata,
        sector_spectra,
        sector_validation,
        target,
        dpi=dpi,
        approval_sample=False,
    )
    result = {
        **asdict(record),
        **rendered,
        "status": "rendered",
        "source_graph_automorphism_group_order": sector_validation[
            "automorphism_group_order"
        ],
        "half_filling_spin_reversal_resolved": sector_validation[
            "half_filling_spin_reversal_resolved"
        ],
        "selected_sector_dimensions": [
            sector.dimension for sector in sector_spectra
        ],
        "selected_sector_labels": [
            sector.symmetry_label for sector in sector_spectra
        ],
    }
    metadata_target.parent.mkdir(parents=True, exist_ok=True)
    temporary = metadata_target.with_name(
        metadata_target.name + f".tmp.{os.getpid()}"
    )
    temporary.write_text(json.dumps(result, indent=2), encoding="utf-8")
    temporary.replace(metadata_target)
    return result


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    simple_rows = []
    fields: set[str] = set()
    for row in rows:
        simple = {
            key: (
                json.dumps(value, sort_keys=True)
                if isinstance(value, (dict, list, tuple))
                else value
            )
            for key, value in row.items()
        }
        simple_rows.append(simple)
        fields.update(simple)
    ordered_fields = sorted(fields)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ordered_fields)
        writer.writeheader()
        for row in simple_rows:
            writer.writerow({key: row.get(key, "") for key in ordered_fields})


def _checkpoint(
    output: Path,
    *,
    completed: int,
    requested: int,
    results: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> None:
    payload = {
        "completed_attempts": completed,
        "requested": requested,
        "successful": len(results),
        "failure_count": len(failures),
        "failed_ranks": sorted(int(row["rank"]) for row in failures),
    }
    temporary = output / f".checkpoint.{os.getpid()}.tmp"
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(output / "checkpoint.json")


def build_campaign(
    name: str,
    source: Path,
    output: Path,
    *,
    workers: int,
    dpi: int,
    force: bool,
    limit: int | None,
) -> dict[str, Any]:
    """Render and checkpoint one independently ranked network campaign."""

    output.mkdir(parents=True, exist_ok=True)
    ranked, unavailable = rank_records(source, output, limit=limit)
    _write_csv(output / "ranking_plan.csv", [asdict(record) for record in ranked])
    payloads = [(asdict(record), dpi, force) for record in ranked]
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(_render_one, payload): payload[0] for payload in payloads}
        for completed, future in enumerate(as_completed(futures), start=1):
            record = futures[future]
            try:
                results.append(future.result())
            except BaseException as exc:
                failures.append(
                    {
                        "rank": int(record["rank"]),
                        "config_id": record["config_id"],
                        "source_dir": record["source_dir"],
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )
            if completed == 1 or completed % 10 == 0 or completed == len(futures):
                print(
                    f"{name}: completed {completed}/{len(futures)}; "
                    f"failures={len(failures)}",
                    flush=True,
                )
                _checkpoint(
                    output,
                    completed=completed,
                    requested=len(futures),
                    results=results,
                    failures=failures,
                )
                _write_csv(
                    output / "ranked_index.partial.csv",
                    sorted(results, key=lambda row: int(row["rank"])),
                )

    results.sort(key=lambda row: int(row["rank"]))
    failures.sort(key=lambda row: int(row["rank"]))
    _write_csv(output / "ranked_index.csv", results)
    case_unavailable = [row for row in unavailable if "config_id" in row]
    _write_csv(output / "unavailable_or_failed.csv", [*case_unavailable, *failures])
    manifest = {
        "created": "2026-08-14",
        "campaign": name,
        "source": str(source.resolve()),
        "output": str(output.resolve()),
        "rank_definition": (
            "decreasing finite stored S_born among validated jy_zero/N12 results; "
            "config_id breaks exact ties"
        ),
        "requested_valid_records": len(ranked),
        "completed_records": len(results),
        "render_failures": len(failures),
        "unavailable_source_configurations": len(case_unavailable),
        "spectral_detector_n": SPECTRAL_N,
        "symmetry_detector_n": 12,
        "dpi": dpi,
        "workers": workers,
        "layout_inches": {
            "approved_2x3_block": [18.0, 10.0],
            "complete_figure": [23.0, 10.0],
        },
        "symmetry_sector_method": {
            "performed_per_configuration": True,
            "conserved_quantity": "computational-basis Hamming weight",
            "graph_symmetry": "complete automorphism group of the exact saved N=12 graph",
            "half_filling_symmetry": (
                "global spin-reversal Z2 resolved explicitly in N_up=N/2"
            ),
            "reduction": (
                "deterministic generic Hermitian group-algebra element; equivalent "
                "irrep rows identified by centered isospectrality"
            ),
            "selection": "four largest nonredundant sectors by dimension",
            "complementary_weights": (
                "N_up>N/2 omitted because global spin reversal changes only the "
                "constant field shift within a fixed-weight block"
            ),
        },
        "results": results,
        "failures": failures,
        "unavailable": case_unavailable,
    }
    (output / "render_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (output / "README.md").write_text(
        f"# {name} network Sobol ranked atlas\n\n"
        "Configurations are ranked independently by decreasing stored S_born. "
        "The first spectral panels use N_D=10. For each exact N=12 graph, the "
        "bottom-right 2x2 inset contains the four largest nonredundant sectors "
        "after fixed-weight and full graph-automorphism reduction, including "
        "global spin-reversal parity at half filling.\n",
        encoding="utf-8",
    )
    return manifest


def build_all(
    campaigns: list[str],
    output_root: Path,
    *,
    workers: int,
    dpi: int,
    force: bool,
    limit: int | None,
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    manifests = []
    for name in campaigns:
        manifests.append(
            build_campaign(
                name,
                CAMPAIGNS[name],
                output_root / name,
                workers=workers,
                dpi=dpi,
                force=force,
                limit=limit,
            )
        )
    summary = {
        "created": "2026-08-14",
        "campaigns": [
            {
                key: manifest[key]
                for key in (
                    "campaign",
                    "source",
                    "output",
                    "requested_valid_records",
                    "completed_records",
                    "render_failures",
                    "unavailable_source_configurations",
                )
            }
            for manifest in manifests
        ],
    }
    (output_root / "render_manifest.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--campaign",
        action="append",
        choices=tuple(CAMPAIGNS),
        help="campaign to render; repeat as needed (default: all four)",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=220)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    campaigns = args.campaign or list(CAMPAIGNS)
    summary = build_all(
        campaigns,
        args.output,
        workers=args.workers,
        dpi=args.dpi,
        force=args.force,
        limit=args.limit,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
