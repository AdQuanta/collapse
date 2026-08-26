"""Build one approval figure for the N=12--15 network continuation.

The four dynamics-diagnostics panes use the original selected N=12 result and
the N=13,14,15 continuation results.  The right-hand 2x2 block is deliberately
independent of those dynamics sizes: it resolves the N_D=11 detector
Hamiltonian into the four largest nonredundant exact symmetry sectors.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(ROOT / ".mplconfig-network-extremes-largerN-sample"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collapse.detector_graphs import (  # noqa: E402
    DetectorGraphSpec,
    detector_graph_edges,
    detector_graph_metadata,
)
from collapse.graph_spectral_sectors import (  # noqa: E402
    largest_detector_symmetry_sectors,
)
from examples.build_network_extremes_resampled_sample_3x5 import (  # noqa: E402
    _plot_diagnostics,
    _plot_graph,
    _plot_spacing_grid,
)
from examples.build_network_sobol_graph_sample_2x3 import (  # noqa: E402
    _sector_spacing_data,
)
from examples.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    _load_result_arrays,
)


DEFAULT_SOURCE = (
    ROOT / "work" / "zeus_network_extremes_largerN_20260813_233000"
)
DEFAULT_SELECTION = "family_00_erdos_renyi/highest_01"
DEFAULT_OUTPUT = (
    ROOT
    / "reports"
    / "network_extremes_largerN_graph_sample_2026-08-20"
    / "erdos_renyi_highest_01_N12_N15_with_N11_spacings_and_graph.png"
)
DYNAMICS_SIZES = (12, 13, 14, 15)
DEFAULT_SPECTRAL_N = 11


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _manifest_entry(
    manifest: dict[str, Any], selection: str
) -> dict[str, Any]:
    matches = [
        item for item in manifest["cases"] if item["selection_key"] == selection
    ]
    if len(matches) != 1:
        raise ValueError(
            f"selection {selection!r} has {len(matches)} manifest matches"
        )
    return matches[0]


def _source_case_dir(
    manifest: dict[str, Any], entry: dict[str, Any]
) -> Path:
    family = str(entry["family"])
    family_configs = [
        item
        for item in manifest["config"]["families"]
        if str(item["name"]) == family
    ]
    if len(family_configs) != 1:
        raise ValueError(f"family {family!r} has no unique source-root mapping")
    return (
        ROOT
        / str(family_configs[0]["source_root"])
        / str(entry["source"]["source_case"])
    ).resolve()


def _validate_result(case_dir: Path, detector_n: int) -> None:
    required = (
        case_dir / "COMPLETE.json",
        case_dir / "validation.json",
        case_dir / "metrics.json",
        case_dir / "results.npz",
    )
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"N={detector_n} result is incomplete: {missing}")
    if not bool(_read_json(case_dir / "validation.json").get("passed", False)):
        raise RuntimeError(f"N={detector_n} source validation failed: {case_dir}")


def _record(
    case_dir: Path,
    *,
    family: str,
    detector_n: int,
    source: dict[str, Any],
    metrics: dict[str, Any],
) -> CaseRecord:
    return CaseRecord(
        family=family,
        dynamics_n=detector_n,
        config_id=str(source["source_case"]).split("/")[-1],
        s_born=float(metrics["S_born"]),
        born_rmse=float(metrics["born_RMSE_occupied"]),
        hz=float(source["hz"]),
        j=float(source["j"]),
        jpm=float(source["jpm"]),
        jx=float(source["jx"]),
        jy=float(source.get("jy", 0.0)),
        j2=float(source.get("j2", 0.0)),
        jpm2=float(source.get("jpm2", 0.0)),
        source_dir=str(case_dir),
    )


def _family_label(family: str) -> str:
    return {
        "erdos_renyi": "Erdős–Rényi",
        "watts_strogatz": "Watts–Strogatz",
        "barabasi_albert": "Barabási–Albert",
        "expander": "random regular / Expander",
    }.get(family, family)


def build_sample(
    source_root: Path,
    selection: str,
    output: Path,
    *,
    dpi: int,
    spectral_n: int = DEFAULT_SPECTRAL_N,
) -> dict[str, Any]:
    """Render and record one size-continuation comparison."""

    if spectral_n < 4:
        raise ValueError("spectral_n must be at least four")

    manifest = _read_json(source_root / "selection_manifest.json")
    entry = _manifest_entry(manifest, selection)
    source = entry["source"]
    family = str(entry["family"])
    case_dirs = {
        12: _source_case_dir(manifest, entry),
        **{
            detector_n: source_root / Path(selection) / f"N{detector_n}"
            for detector_n in DYNAMICS_SIZES[1:]
        },
    }

    entries: list[dict[str, Any]] = []
    density_limit = 0.0
    for detector_n in DYNAMICS_SIZES:
        case_dir = case_dirs[detector_n]
        _validate_result(case_dir, detector_n)
        metrics = _read_json(case_dir / "metrics.json")
        record = _record(
            case_dir,
            family=family,
            detector_n=detector_n,
            source=source,
            metrics=metrics,
        )
        arrays = _load_result_arrays(case_dir)
        density_limit = max(
            density_limit,
            float(np.max(arrays["p_theta"])),
            float(np.max(arrays["p_pi_minus_theta"])),
            float(np.max(arrays["wg_density"])),
            float(np.max(arrays["wc_density"])),
        )
        entries.append(
            {
                "detector_n": detector_n,
                "case_dir": case_dir,
                "record": record,
                "arrays": arrays,
            }
        )
    density_limit *= 1.06

    graph_spec = DetectorGraphSpec(**source["graph_spec"])
    spectral_edges = detector_graph_edges(spectral_n, graph_spec)
    sectors, sector_validation = largest_detector_symmetry_sectors(
        spectral_n,
        spectral_edges,
        hz=float(source["hz"]),
        j=float(source["j"]),
        jpm=float(source["jpm"]),
        count=4,
    )
    expected_half_filling_resolution = spectral_n % 2 == 0
    if (
        bool(sector_validation["half_filling_spin_reversal_resolved"])
        != expected_half_filling_resolution
    ):
        raise RuntimeError(
            "half-filling spin-reversal resolution is inconsistent with "
            f"spectral N_D={spectral_n}"
        )
    spacing_limit = min(
        max(
            4.0,
            *(
                float(_sector_spacing_data(sector.energies)["edges"][-1])
                for sector in sectors
            ),
        ),
        5.5,
    )
    graph_metadata = detector_graph_metadata(spectral_n, graph_spec)

    output.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(31.5, 6.8), dpi=dpi, constrained_layout=False)
    grid = figure.add_gridspec(
        1,
        6,
        left=0.045,
        right=0.988,
        bottom=0.105,
        top=0.815,
        wspace=0.23,
        width_ratios=(1.0, 1.0, 1.0, 1.0, 1.42, 1.05),
    )
    for column, item in enumerate(entries):
        record = item["record"]
        _plot_diagnostics(
            figure,
            grid[0, column],
            item["arrays"],
            record,
            density_limit=density_limit,
            first_column=column == 0,
        )
        bounds = grid[0, column].get_position(figure)
        figure.text(
            bounds.x0 + 0.5 * bounds.width,
            bounds.y1 + 0.018,
            rf"$N={item['detector_n']}$"
            + "\n"
            + rf"$S_{{\rm Born}}={record.s_born:.3f}$",
            ha="center",
            va="bottom",
            fontsize=10.0,
            fontweight="bold",
        )

    spacing_metadata = _plot_spacing_grid(
        figure,
        grid[0, 4],
        sectors,
        x_limit=spacing_limit,
        first_column=True,
    )
    spacing_bounds = grid[0, 4].get_position(figure)
    figure.text(
        spacing_bounds.x0 + 0.5 * spacing_bounds.width,
        spacing_bounds.y1 + 0.028,
        rf"Symmetry-resolved detector spacings ($N_D={spectral_n}$)",
        ha="center",
        va="bottom",
        fontsize=10.0,
        fontweight="bold",
    )
    graph_axis = figure.add_subplot(grid[0, 5])
    _plot_graph(graph_axis, graph_metadata)
    graph_bounds = grid[0, 5].get_position(figure)
    figure.text(
        graph_bounds.x0 + 0.5 * graph_bounds.width,
        graph_bounds.y1 + 0.028,
        rf"Detector interaction graph ($N_D={spectral_n}$)",
        ha="center",
        va="bottom",
        fontsize=10.0,
        fontweight="bold",
    )

    figure.suptitle(
        f"{_family_label(family)}: {source['source_case'].split('/')[-1]}, "
        + f"{entry['cohort']} source rank {entry['cohort_rank']} "
        + rf"($S_{{\rm Born}}^{{\rm source}}={float(source['source_s_born']):.3f}$)"
        + " — detector-size continuation\n"
        + rf"$h_z={float(source['hz']):.4g}$, $h_{{z0}}={float(source['hz0']):.4g}$, "
        + rf"$J={float(source['j']):.4g}$, $J_\pm={float(source['jpm']):.4g}$, "
        + rf"$J_x^{{\rm source}}={float(source['jx']):.4g}$; "
        + "same graph-family parameters and seed at each N",
        fontsize=13.0,
        fontweight="bold",
        y=0.985,
    )
    figure.text(
        0.017,
        0.46,
        "Dynamics diagnostics",
        rotation=90,
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold",
    )

    temporary = output.with_name(output.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temporary, dpi=dpi, facecolor="white")
    plt.close(figure)
    temporary.replace(output)

    result = {
        "output": str(output.resolve()),
        "source_root": str(source_root.resolve()),
        "selection": selection,
        "family": family,
        "cohort": entry["cohort"],
        "cohort_rank": int(entry["cohort_rank"]),
        "dynamics_detector_sizes": list(DYNAMICS_SIZES),
        "dynamics": [
            {
                "N": item["detector_n"],
                "case_dir": str(item["case_dir"].resolve()),
                "S_born": item["record"].s_born,
                "born_RMSE_occupied": item["record"].born_rmse,
            }
            for item in entries
        ],
        "spectral_detector_n": spectral_n,
        "includes_network_graph": True,
        "spectral_graph": graph_metadata,
        "spectral_graph_policy": (
            f"regenerate N_D={spectral_n} graph from the selected source graph-family "
            "parameters and saved seed; this is not a scaled N=12--15 graph"
        ),
        "symmetry_resolution": sector_validation,
        "selected_sector_dimensions": [sector.dimension for sector in sectors],
        "selected_sector_labels": [sector.symmetry_label for sector in sectors],
        "spacing_statistics": spacing_metadata,
        "source_parameters": source,
        "figure_size_inches": [31.5, 6.8],
        "dpi": dpi,
    }
    metadata_path = output.with_suffix(".json")
    temporary_metadata = metadata_path.with_name(
        metadata_path.name + f".tmp.{os.getpid()}"
    )
    temporary_metadata.write_text(json.dumps(result, indent=2), encoding="utf-8")
    temporary_metadata.replace(metadata_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--selection", default=DEFAULT_SELECTION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--spectral-n", type=int, default=DEFAULT_SPECTRAL_N)
    args = parser.parse_args()
    result = build_sample(
        args.source.resolve(),
        args.selection,
        args.output.resolve(),
        dpi=args.dpi,
        spectral_n=args.spectral_n,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
