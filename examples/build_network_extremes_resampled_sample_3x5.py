"""Build one approval 3x5 comparison of five resampled detector graphs.

Each column is one independent graph realization for a fixed selected source
configuration.  Rows contain dynamics diagnostics, four exact symmetry-sector
level-spacing distributions, and the exact interaction graph.  At even-N half
filling, global spin reversal is resolved jointly with all graph automorphisms.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-network-resampled-3x5")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
import numpy as np  # noqa: E402

from collapse.anisotropic_sweep import BLUE, RED, RATIO  # noqa: E402
from collapse.graph_spectral_sectors import (  # noqa: E402
    DetectorSymmetrySector,
    largest_detector_symmetry_sectors,
)
from collapse.level_spacing import (  # noqa: E402
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)
from examples.build_network_sobol_graph_sample_2x3 import (  # noqa: E402
    _kamada_kawai_layout,
    _sector_spacing_data,
)
from examples.build_sobol_flat_ranked_1x6_by_n import (  # noqa: E402
    CaseRecord,
    MODEL_BLUE,
    MODEL_ORANGE,
    _load_result_arrays,
)


DEFAULT_SOURCE = (
    ROOT / "work" / "zeus_network_extremes_resampled_N12_20260813_232636"
)
DEFAULT_SELECTION = "family_00_erdos_renyi/highest_01"
DEFAULT_OUTPUT = (
    ROOT
    / "reports"
    / "network_extremes_resampled_3x5_sample_2026-08-14"
    / "erdos_renyi_highest_01.png"
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _realization_dirs(source: Path, selection: str) -> list[Path]:
    case_root = source / Path(selection)
    directories = [case_root / f"realization_{index:02d}" / "N12" for index in range(1, 6)]
    missing = [path for path in directories if not (path / "COMPLETE.json").is_file()]
    if missing:
        raise FileNotFoundError(f"five completed realizations are required; missing {missing}")
    return directories


def _record(case_dir: Path, metadata: dict[str, Any], metrics: dict[str, Any]) -> CaseRecord:
    source = metadata["source"]
    return CaseRecord(
        family=str(metadata["graph_provenance"]["family"]),
        dynamics_n=int(metadata["target_N"]),
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
        source_dir=str(case_dir.resolve()),
    )


def _plot_diagnostics(
    figure: plt.Figure,
    parent: Any,
    arrays: dict[str, np.ndarray],
    record: CaseRecord,
    *,
    density_limit: float,
    first_column: bool,
) -> None:
    grid = parent.subgridspec(2, 1, height_ratios=(1.0, 0.92), hspace=0.19)
    axis_p = figure.add_subplot(grid[0, 0])
    axis_p.stairs(
        arrays["p_theta"], arrays["edges"], color=BLUE, linewidth=0.9,
        fill=True, alpha=0.19, label=r"$P(\theta)$"
    )
    axis_p.stairs(
        arrays["p_pi_minus_theta"], arrays["edges"], color=RED, linewidth=0.85,
        fill=True, alpha=0.14, label=r"$P(\pi-\theta)$"
    )
    axis_p.plot(arrays["fit_grid"], arrays["wg_density"], color=MODEL_BLUE, linewidth=0.85, label="WG")
    axis_p.plot(
        arrays["fit_grid"], arrays["wc_density"], color=MODEL_ORANGE,
        linewidth=0.85, linestyle="--", label="WC"
    )
    axis_p.set_xlim(0.0, np.pi)
    axis_p.set_ylim(0.0, density_limit)
    axis_p.set_ylabel("density" if first_column else "", fontsize=8.0)
    axis_p.tick_params(labelbottom=False, labelsize=7.0, pad=1.5)
    axis_p.grid(alpha=0.16)
    if first_column:
        axis_p.legend(ncol=2, frameon=False, fontsize=6.5, loc="upper center")

    axis_r = figure.add_subplot(grid[1, 0])
    occupied = arrays["R_occupied"].astype(bool)
    axis_r.plot(
        arrays["centers"][occupied], arrays["R"][occupied], "o-",
        color=RATIO, markersize=1.8, linewidth=0.7, label=r"$R(\theta)$"
    )
    axis_r.plot(
        arrays["centers"], arrays["R_born"], color="black", linestyle="--",
        linewidth=0.9, label=r"$\cos^2(\theta/2)$"
    )
    axis_r.set_xlim(0.0, np.pi)
    axis_r.set_ylim(-0.04, 1.04)
    axis_r.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
    axis_r.set_xlabel(r"$\theta$", fontsize=8.0, labelpad=1.0)
    axis_r.set_ylabel(r"$R(\theta)$" if first_column else "", fontsize=8.0)
    axis_r.tick_params(labelsize=7.0, pad=1.5)
    axis_r.grid(alpha=0.16)
    if first_column:
        axis_r.legend(frameon=False, fontsize=6.3, loc="upper right")
    axis_r.text(
        0.035,
        0.08,
        rf"$S_{{\rm Born}}={record.s_born:.3f}$" + "\n" + rf"RMSE$={record.born_rmse:.3f}$",
        transform=axis_r.transAxes,
        fontsize=6.7,
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.76, "pad": 0.8},
    )


def _plot_spacing_grid(
    figure: plt.Figure,
    parent: Any,
    sectors: tuple[DetectorSymmetrySector, ...],
    *,
    x_limit: float,
    first_column: bool,
) -> dict[str, Any]:
    grid = parent.subgridspec(2, 2, wspace=0.27, hspace=0.43)
    output: dict[str, Any] = {}
    for panel_index, sector in enumerate(sectors):
        axis = figure.add_subplot(grid[panel_index // 2, panel_index % 2])
        data = _sector_spacing_data(sector.energies)
        edges = np.asarray(data["edges"])
        centers = 0.5 * (edges[:-1] + edges[1:])
        axis.bar(
            centers,
            data["histogram"],
            width=0.92 * np.diff(edges),
            color="#9ecae1",
            edgecolor="white",
            linewidth=0.22,
        )
        reference_grid = np.linspace(0.0, x_limit, 350)
        axis.plot(
            reference_grid,
            poisson_spacing_distribution(reference_grid),
            color="#222222",
            linestyle="--",
            linewidth=0.75,
            label="Poisson",
        )
        axis.plot(
            reference_grid,
            wigner_spacing_distribution(reference_grid, beta=1),
            color="#e45756",
            linewidth=0.8,
            label="GOE",
        )
        axis.set_xlim(0.0, x_limit)
        axis.set_ylim(0.0, 1.08)
        axis.set_title(
            sector.symmetry_label + rf"; $d={sector.dimension}$",
            fontsize=6.7,
            pad=2.0,
        )
        axis.tick_params(labelsize=6.3, pad=1.0)
        axis.grid(axis="y", alpha=0.16)
        if panel_index // 2 == 1:
            axis.set_xlabel(r"$s$", fontsize=7.0, labelpad=0.5)
        else:
            axis.tick_params(labelbottom=False)
        if panel_index % 2 == 0 and first_column:
            axis.set_ylabel(r"$p(s)$", fontsize=7.0, labelpad=0.5)
        axis.text(
            0.96,
            0.90,
            rf"$\langle\tilde r\rangle={data['mean_ratio']:.3f}$" + "\n"
            + rf"$D_1(P/G)={data['distances']['Poisson']:.2f}/{data['distances']['GOE']:.2f}$",
            transform=axis.transAxes,
            ha="right",
            va="top",
            fontsize=5.8,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 0.5},
        )
        if panel_index == 0 and first_column:
            axis.legend(frameon=False, fontsize=5.8, loc="upper left")
        output[f"sector_{panel_index + 1}"] = {
            "hamming_weight": sector.hamming_weight,
            "sector_index": sector.sector_index,
            "dimension": sector.dimension,
            "symmetry_label": sector.symmetry_label,
            "mean_ratio": data["mean_ratio"],
            "l1_distances": data["distances"],
        }
    return output


def _plot_graph(axis: plt.Axes, graph: dict[str, Any]) -> None:
    nodes = int(graph["nodes"])
    edges = tuple(tuple(map(int, edge)) for edge in graph["edges_zero_based"])
    degrees = np.asarray(graph["degree_sequence"], dtype=float)
    positions = _kamada_kawai_layout(nodes, edges)
    axis.add_collection(
        LineCollection(
            [[positions[left], positions[right]] for left, right in edges],
            colors="#667085",
            linewidths=1.0,
            alpha=0.72,
            zorder=1,
        )
    )
    axis.scatter(
        positions[:, 0],
        positions[:, 1],
        s=74.0 + 24.0 * degrees,
        c=degrees,
        cmap="viridis",
        edgecolors="white",
        linewidths=0.9,
        zorder=2,
    )
    median_degree = float(np.median(degrees))
    for node, (x_value, y_value) in enumerate(positions):
        axis.text(
            x_value,
            y_value,
            str(node + 1),
            ha="center",
            va="center",
            color="white" if degrees[node] >= median_degree else "black",
            fontsize=6.5,
            fontweight="bold",
            zorder=3,
        )
    x_min, y_min = np.min(positions, axis=0)
    x_max, y_max = np.max(positions, axis=0)
    axis.set_xlim(float(x_min - 0.18), float(x_max + 0.18))
    axis.set_ylim(float(y_min - 0.20), float(y_max + 0.18))
    axis.set_aspect("equal")
    axis.axis("off")
    axis.set_title(
        rf"$|E|={len(edges)}$, $\lambda_2(L)={float(graph['laplacian_algebraic_connectivity']):.3f}$",
        fontsize=7.5,
        pad=2.5,
    )


def build_sample(source: Path, selection: str, output: Path, *, dpi: int) -> dict[str, Any]:
    case_dirs = _realization_dirs(source, selection)
    entries: list[dict[str, Any]] = []
    density_limit = 0.0
    spacing_limit = 4.0
    for case_dir in case_dirs:
        metadata = _read_json(case_dir / "metadata.json")
        metrics = _read_json(case_dir / "metrics.json")
        validation = _read_json(case_dir / "validation.json")
        if not bool(validation.get("passed", False)):
            raise RuntimeError(f"source validation failed: {case_dir}")
        record = _record(case_dir, metadata, metrics)
        arrays = _load_result_arrays(case_dir)
        graph = metadata["detector_graph"]
        sectors, sector_validation = largest_detector_symmetry_sectors(
            int(graph["nodes"]),
            [tuple(edge) for edge in graph["edges_zero_based"]],
            hz=record.hz,
            j=record.j,
            jpm=record.jpm,
            count=4,
        )
        if not bool(sector_validation["half_filling_spin_reversal_resolved"]):
            raise RuntimeError("half-filling spin reversal was not resolved")
        density_limit = max(
            density_limit,
            float(np.max(arrays["p_theta"])),
            float(np.max(arrays["p_pi_minus_theta"])),
            float(np.max(arrays["wg_density"])),
            float(np.max(arrays["wc_density"])),
        )
        spacing_limit = max(
            spacing_limit,
            *(float(_sector_spacing_data(sector.energies)["edges"][-1]) for sector in sectors),
        )
        entries.append(
            {
                "case_dir": case_dir,
                "metadata": metadata,
                "record": record,
                "arrays": arrays,
                "sectors": sectors,
                "sector_validation": sector_validation,
            }
        )
    density_limit *= 1.06
    spacing_limit = min(max(spacing_limit, 4.0), 5.5)

    output.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(24.0, 16.2), dpi=dpi, constrained_layout=False)
    grid = figure.add_gridspec(
        3,
        5,
        left=0.045,
        right=0.988,
        bottom=0.035,
        top=0.905,
        wspace=0.22,
        hspace=0.22,
        height_ratios=(1.05, 1.25, 0.92),
    )
    spacing_metadata: list[dict[str, Any]] = []
    for column, entry in enumerate(entries):
        metadata = entry["metadata"]
        record = entry["record"]
        graph_seed = int(metadata["graph_provenance"]["resampled_graph_seed"])
        figure.text(
            0.045 + (column + 0.5) * (0.943 / 5.0),
            0.923,
            f"Realization {column + 1}\n"
            + rf"$S_{{\rm Born}}={record.s_born:.3f}$; seed={graph_seed}",
            ha="center",
            va="bottom",
            fontsize=10.0,
            fontweight="bold",
        )
        _plot_diagnostics(
            figure,
            grid[0, column],
            entry["arrays"],
            record,
            density_limit=density_limit,
            first_column=column == 0,
        )
        spacing_metadata.append(
            _plot_spacing_grid(
                figure,
                grid[1, column],
                entry["sectors"],
                x_limit=spacing_limit,
                first_column=column == 0,
            )
        )
        graph_axis = figure.add_subplot(grid[2, column])
        _plot_graph(graph_axis, metadata["detector_graph"])

    first = entries[0]
    source_parameters = first["metadata"]["source"]
    family_name = {
        "erdos_renyi": "Erdős–Rényi",
        "watts_strogatz": "Watts–Strogatz",
        "barabasi_albert": "Barabási–Albert",
        "expander": "random 4-regular",
    }.get(str(first["metadata"]["graph_provenance"]["family"]), selection.split("/")[0])
    provenance = first["metadata"]["graph_provenance"]
    figure.suptitle(
        f"{family_name}: {source_parameters['source_case'].split('/')[-1]}, "
        + f"{provenance['cohort']} source rank {provenance['cohort_rank']} "
        + rf"($S_{{\rm Born}}^{{\rm source}}={float(source_parameters['source_s_born']):.3f}$)"
        + " — five independent graph realizations\n"
        + rf"$N=12$, $h_z={float(source_parameters['hz']):.4g}$, "
        + rf"$J={float(source_parameters['j']):.4g}$, "
        + rf"$J_\pm={float(source_parameters['jpm']):.4g}$, "
        + rf"$J_x={float(source_parameters['jx']):.4g}$",
        fontsize=14.0,
        fontweight="bold",
        y=0.982,
    )
    figure.text(0.012, 0.755, "Dynamics diagnostics", rotation=90, va="center", ha="center", fontsize=11.0, fontweight="bold")
    figure.text(0.012, 0.440, "Exact symmetry-sector spacings", rotation=90, va="center", ha="center", fontsize=11.0, fontweight="bold")
    figure.text(0.012, 0.145, "Detector interaction graph", rotation=90, va="center", ha="center", fontsize=11.0, fontweight="bold")

    temporary = output.with_name(output.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temporary, dpi=dpi, facecolor="white")
    plt.close(figure)
    temporary.replace(output)
    result = {
        "output": str(output.resolve()),
        "source": str(source.resolve()),
        "selection": selection,
        "realizations": [
            {
                "index": index + 1,
                "case_dir": str(entry["case_dir"].resolve()),
                "record": asdict(entry["record"]),
                "graph_seed": int(entry["metadata"]["graph_provenance"]["resampled_graph_seed"]),
                "selected_sector_dimensions": [sector.dimension for sector in entry["sectors"]],
                "selected_sector_labels": [sector.symmetry_label for sector in entry["sectors"]],
                "half_filling_spin_reversal_resolved": bool(
                    entry["sector_validation"]["half_filling_spin_reversal_resolved"]
                ),
                "spacing_statistics": spacing_metadata[index],
            }
            for index, entry in enumerate(entries)
        ],
        "figure_size_inches": [24.0, 16.2],
        "dpi": dpi,
    }
    output.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--selection", default=DEFAULT_SELECTION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args()
    result = build_sample(
        args.source.resolve(), args.selection, args.output.resolve(), dpi=args.dpi
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
