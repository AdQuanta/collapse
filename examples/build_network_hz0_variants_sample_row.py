"""Build one approval row for the N=12 network ``hz0`` variants.

The dynamics panes are ordered by increasing central-qubit field ``hz0``.
The detector Hamiltonian is unchanged across those panes, so one independently
generated N_D=11 graph, its four largest fully resolved spectral sectors, and
its network diagram are shown to their right.
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
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-network-hz0-variants-sample")
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
from examples.build_network_extremes_largerN_sample_row import (  # noqa: E402
    _family_label,
    _manifest_entry,
    _read_json,
    _record,
    _validate_result,
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
    _load_result_arrays,
)


DEFAULT_SOURCE = (
    ROOT / "work" / "zeus_network_top_hz0_variants_N12_20260820_210913"
)
DEFAULT_SELECTION = "family_00_erdos_renyi/highest_01"
DEFAULT_OUTPUT = (
    ROOT
    / "reports"
    / "network_top_hz0_variants_sample_2026-08-20"
    / "erdos_renyi_highest_01_hz0_variants_with_N11_spacings_and_graph.png"
)
TARGET_N = 12
DEFAULT_SPECTRAL_N = 11


def _variant_title(metadata: dict[str, Any], hz: float) -> str:
    alias = str(metadata.get("hz0_aliases", [""])[0])
    hz0 = float(metadata["hz0"])
    relation = {
        "zero": r"0",
        "matched_m1em03": r"h_z-10^{-3}",
        "matched_m1em04": r"h_z-10^{-4}",
        "matched": r"h_z",
        "matched_p1em04": r"h_z+10^{-4}",
        "matched_p1em03": r"h_z+10^{-3}",
    }.get(alias)
    if alias == "zero":
        return r"$h_{z0}=0$"
    if relation is None:
        delta = hz0 - hz
        relation = rf"h_z{delta:+.3g}"
    return rf"$h_{{z0}}={relation}={hz0:.6g}$"


def _variant_entries(
    source_root: Path,
    selection: str,
    *,
    family: str,
    source: dict[str, Any],
) -> list[dict[str, Any]]:
    variant_root = source_root / Path(selection) / f"N{TARGET_N}"
    if not variant_root.is_dir():
        raise FileNotFoundError(f"missing variant directory: {variant_root}")
    entries: list[dict[str, Any]] = []
    for case_dir in variant_root.iterdir():
        if not case_dir.is_dir():
            continue
        _validate_result(case_dir, TARGET_N)
        metadata = _read_json(case_dir / "metadata.json")
        metrics = _read_json(case_dir / "metrics.json")
        if int(metadata["target_N"]) != TARGET_N:
            raise ValueError(f"unexpected detector size in {case_dir}")
        if not bool(metadata["graph_provenance"]["is_same_edge_set_as_source"]):
            raise RuntimeError(f"variant did not retain the source graph: {case_dir}")
        entries.append(
            {
                "case_dir": case_dir,
                "metadata": metadata,
                "metrics": metrics,
                "record": _record(
                    case_dir,
                    family=family,
                    detector_n=TARGET_N,
                    source=source,
                    metrics=metrics,
                ),
                "arrays": _load_result_arrays(case_dir),
            }
        )
    entries.sort(
        key=lambda item: (
            float(item["metadata"]["hz0"]),
            item["case_dir"].name,
        )
    )
    if len(entries) < 2:
        raise RuntimeError(f"expected multiple hz0 variants, found {len(entries)}")
    return entries


def build_sample(
    source_root: Path,
    selection: str,
    output: Path,
    *,
    dpi: int,
    spectral_n: int = DEFAULT_SPECTRAL_N,
) -> dict[str, Any]:
    """Render one fixed-N comparison ordered by increasing ``hz0``."""

    if spectral_n < 4:
        raise ValueError("spectral_n must be at least four")
    manifest = _read_json(source_root / "selection_manifest.json")
    entry = _manifest_entry(manifest, selection)
    source = entry["source"]
    family = str(entry["family"])
    variants = _variant_entries(
        source_root,
        selection,
        family=family,
        source=source,
    )

    density_limit = 1.06 * max(
        max(
            float(np.max(item["arrays"][name]))
            for name in ("p_theta", "p_pi_minus_theta", "wg_density", "wc_density")
        )
        for item in variants
    )
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
    diagnostic_count = len(variants)
    figure_width = 31.5 + 4.75 * max(0, diagnostic_count - 4)
    figure = plt.figure(
        figsize=(figure_width, 6.8), dpi=dpi, constrained_layout=False
    )
    grid = figure.add_gridspec(
        1,
        diagnostic_count + 2,
        left=0.035,
        right=0.992,
        bottom=0.105,
        top=0.815,
        wspace=0.23,
        width_ratios=tuple([1.0] * diagnostic_count + [1.42, 1.05]),
    )
    hz = float(source["hz"])
    for column, item in enumerate(variants):
        _plot_diagnostics(
            figure,
            grid[0, column],
            item["arrays"],
            item["record"],
            density_limit=density_limit,
            first_column=column == 0,
        )
        bounds = grid[0, column].get_position(figure)
        figure.text(
            bounds.x0 + 0.5 * bounds.width,
            bounds.y1 + 0.018,
            _variant_title(item["metadata"], hz)
            + "\n"
            + rf"$S_{{\rm Born}}={item['record'].s_born:.3f}$",
            ha="center",
            va="bottom",
            fontsize=9.6,
            fontweight="bold",
        )

    spacing_column = diagnostic_count
    spacing_metadata = _plot_spacing_grid(
        figure,
        grid[0, spacing_column],
        sectors,
        x_limit=spacing_limit,
        first_column=True,
    )
    spacing_bounds = grid[0, spacing_column].get_position(figure)
    figure.text(
        spacing_bounds.x0 + 0.5 * spacing_bounds.width,
        spacing_bounds.y1 + 0.028,
        rf"Symmetry-resolved detector spacings ($N_D={spectral_n}$)",
        ha="center",
        va="bottom",
        fontsize=10.0,
        fontweight="bold",
    )
    graph_axis = figure.add_subplot(grid[0, diagnostic_count + 1])
    _plot_graph(graph_axis, graph_metadata)
    graph_bounds = grid[0, diagnostic_count + 1].get_position(figure)
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
        + f"highest source rank {int(entry['family_rank'])} "
        + rf"($S_{{\rm Born}}^{{\rm source}}={float(source['source_s_born']):.3f}$)"
        + rf" — fixed $N={TARGET_N}$, varying $h_{{z0}}$"
        + "\n"
        + rf"$h_z={hz:.4g}$, $J={float(source['j']):.4g}$, "
        + rf"$J_\pm={float(source['jpm']):.4g}$, "
        + rf"$J_x^{{\rm source}}={float(source['jx']):.4g}$; "
        + "same detector graph and all other Hamiltonian parameters",
        fontsize=13.0,
        fontweight="bold",
        y=0.985,
    )
    figure.text(
        0.014,
        0.46,
        rf"Dynamics diagnostics ($N={TARGET_N}$)",
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
        "source_rank": int(entry["family_rank"]),
        "target_detector_n": TARGET_N,
        "diagnostic_order": "increasing hz0",
        "hz0_variants": [
            {
                "directory": item["case_dir"].name,
                "hz0": float(item["metadata"]["hz0"]),
                "hz0_aliases": list(item["metadata"].get("hz0_aliases", [])),
                "S_born": item["record"].s_born,
                "born_RMSE_occupied": item["record"].born_rmse,
            }
            for item in variants
        ],
        "spectral_detector_n": spectral_n,
        "spectral_graph": graph_metadata,
        "spectral_graph_policy": (
            f"regenerate N_D={spectral_n} graph from the saved graph-family "
            "parameters and seed; the detector spectrum is independent of hz0"
        ),
        "symmetry_resolution": sector_validation,
        "selected_sector_dimensions": [sector.dimension for sector in sectors],
        "selected_sector_labels": [sector.symmetry_label for sector in sectors],
        "spacing_statistics": spacing_metadata,
        "source_parameters": source,
        "figure_size_inches": [figure_width, 6.8],
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
