#!/usr/bin/env python3.11
"""Plot the four hz0=0 ring spacing/Born categories as diagnostic atlases.

Each atlas row shows one selected configuration: the two antipodal angular
densities, the occupied-bin Born-ratio diagnostic, and the detector spacing
density obtained only after resolving and unfolding symmetry sectors
separately.  Individual-sector spacing densities are retained as faint traces;
the prominent histogram is their pooled, spacing-count-weighted density.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from core.level_spacing import (  # noqa: E402
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)


DEFAULT_CATALOG = (
    ROOT / "reports" / "hz0_0_ring_spacing_born_10x4_2026-09-05" / "manifest.json"
)
CATEGORY_TITLES = {
    "wd_born": "Wigner–Dyson and Born-like",
    "poisson_born": "Poisson and Born-like",
    "wd_clearly_nonborn": "Wigner–Dyson and clearly non-Born",
    "poisson_clearly_nonborn": "Poisson and clearly non-Born",
}
BLUE = "#2878b5"
RED = "#d9534f"
PURPLE = "#6f3c8a"
GOE = "#e45756"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _spacing_histograms(
    spacing_path: Path,
    *,
    edges: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return individual-sector and pooled counts on ``edges``.

    New lower-N archives already contain sufficient histogram statistics and
    deliberately omit eigenvalues and individual spacings.  The earlier N=17
    archive stores sectorwise unfolded spacings, which are histogrammed here.
    """
    with np.load(spacing_path) as arrays:
        names = set(arrays.files)
        if {"bin_edges", "sector_histogram_counts", "pooled_histogram_counts"} <= names:
            saved_edges = np.asarray(arrays["bin_edges"], dtype=np.float64)
            if saved_edges.shape != edges.shape or not np.allclose(saved_edges, edges):
                raise ValueError(f"unexpected histogram edges in {spacing_path}")
            sectors = np.asarray(arrays["sector_histogram_counts"], dtype=np.float64)
            pooled = np.asarray(arrays["pooled_histogram_counts"], dtype=np.float64)
            return sectors, pooled

        unfolded = [
            np.asarray(arrays[name], dtype=np.float64)
            for name in arrays.files
            if name.endswith("__unfolded_spacings")
        ]
    if not unfolded:
        raise ValueError(f"no symmetry-resolved spacings in {spacing_path}")
    sectors = np.asarray([np.histogram(values, bins=edges)[0] for values in unfolded])
    return sectors, np.sum(sectors, axis=0)


def _density(counts: np.ndarray, edges: np.ndarray) -> np.ndarray:
    total = float(np.sum(counts))
    if total <= 0.0:
        raise ValueError("spacing histogram is empty")
    return np.asarray(counts, dtype=np.float64) / (total * np.diff(edges))


def _plot_angular(
    axis: plt.Axes,
    arrays: Any,
    *,
    show_legend: bool,
) -> None:
    centers = np.asarray(arrays["centers"], dtype=np.float64)
    axis.fill_between(
        centers,
        np.asarray(arrays["p_theta"], dtype=np.float64),
        step="mid",
        color=BLUE,
        alpha=0.18,
    )
    axis.fill_between(
        centers,
        np.asarray(arrays["p_pi_minus_theta"], dtype=np.float64),
        step="mid",
        color=RED,
        alpha=0.13,
    )
    axis.step(
        centers,
        arrays["p_theta"],
        where="mid",
        color=BLUE,
        linewidth=0.9,
        label=r"$P(\theta)$",
    )
    axis.step(
        centers,
        arrays["p_pi_minus_theta"],
        where="mid",
        color=RED,
        linewidth=0.8,
        label=r"$P(\pi-\theta)$",
    )
    axis.plot(
        arrays["fit_grid"],
        arrays["wg_density"],
        color=BLUE,
        linewidth=0.7,
        linestyle="--",
        label="wrapped Gaussian",
    )
    axis.plot(
        arrays["fit_grid"],
        arrays["wc_density"],
        color="#e89017",
        linewidth=0.7,
        linestyle=":",
        label="wrapped Cauchy",
    )
    axis.set_xlim(0.0, np.pi)
    axis.set_ylim(bottom=0.0)
    axis.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
    axis.set_ylabel("density")
    axis.grid(alpha=0.16)
    if show_legend:
        axis.legend(frameon=False, fontsize=6.7, ncol=2, loc="upper center")


def _plot_ratio(
    axis: plt.Axes,
    arrays: Any,
    record: dict[str, Any],
    *,
    show_legend: bool,
) -> None:
    occupied = np.asarray(arrays["R_occupied"], dtype=bool)
    centers = np.asarray(arrays["centers"], dtype=np.float64)
    axis.plot(
        centers[occupied],
        np.asarray(arrays["R"], dtype=np.float64)[occupied],
        "o-",
        color=PURPLE,
        markersize=1.7,
        linewidth=0.75,
        label=r"$R(\theta)$",
    )
    axis.plot(
        centers,
        arrays["R_born"],
        color="black",
        linestyle="--",
        linewidth=0.9,
        label=r"$\cos^2(\theta/2)$",
    )
    axis.set_xlim(0.0, np.pi)
    axis.set_ylim(-0.04, 1.04)
    axis.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
    axis.set_ylabel(r"$R(\theta)$")
    axis.grid(alpha=0.16)
    axis.text(
        0.03,
        0.07,
        rf"$S_{{\rm Born}}={float(record['S_born']):.3f}$"
        + "\n"
        + rf"RMSE$={float(record['born_RMSE_occupied']):.3f}$",
        transform=axis.transAxes,
        fontsize=7.0,
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78},
    )
    if show_legend:
        axis.legend(frameon=False, fontsize=7.0, loc="upper right")


def _plot_spacings(
    axis: plt.Axes,
    sectors: np.ndarray,
    pooled: np.ndarray,
    edges: np.ndarray,
    record: dict[str, Any],
    *,
    show_legend: bool,
) -> None:
    centers = 0.5 * (edges[:-1] + edges[1:])
    for counts in sectors:
        if np.sum(counts) > 0:
            axis.step(
                centers,
                _density(counts, edges),
                where="mid",
                color="#718096",
                linewidth=0.35,
                alpha=0.14,
            )
    axis.bar(
        centers,
        _density(pooled, edges),
        width=0.90 * np.diff(edges),
        color="#9ecae1",
        edgecolor="#4b7ba6",
        linewidth=0.28,
        alpha=0.88,
        label="pooled resolved sectors",
    )
    reference = np.linspace(0.0, 4.0, 500)
    axis.plot(
        reference,
        poisson_spacing_distribution(reference),
        color="#222222",
        linestyle="--",
        linewidth=0.9,
        label="Poisson",
    )
    axis.plot(
        reference,
        wigner_spacing_distribution(reference, beta=1),
        color=GOE,
        linewidth=0.9,
        label="GOE",
    )
    axis.set_xlim(0.0, 4.0)
    axis.set_ylim(bottom=0.0)
    axis.set_xlabel(r"unfolded spacing $s$")
    axis.set_ylabel(r"density $p(s)$")
    axis.grid(alpha=0.16)
    spacing_name = (
        "WD" if record["spacing_class"] == "wigner_dyson" else "Poisson"
    )
    axis.text(
        0.97,
        0.93,
        spacing_name
        + "\n"
        + rf"$\langle\tilde r\rangle={float(record['mean_adjacent_gap_ratio']):.3f}$"
        + "\n"
        + rf"$D_{{KS}}(P/G)={float(record['ks_poisson']):.3f}/{float(record['ks_goe']):.3f}$",
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=6.8,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82},
    )
    if show_legend:
        axis.legend(frameon=False, fontsize=6.5, loc="upper center")


def _parameter_label(record: dict[str, Any]) -> str:
    parameters = record["parameters"]
    return (
        rf"$h_z={float(parameters['hz']):.3g}$, $J={float(parameters['j']):.3g}$, "
        rf"$J_{{\pm}}={float(parameters['jpm']):.3g}$, "
        rf"$J_2={float(parameters['j2']):.3g}$, "
        rf"$J_{{\pm2}}={float(parameters['jpm2']):.3g}$"
    )


def plot_category(
    category: str,
    records: list[dict[str, Any]],
    output: Path,
    *,
    dpi: int,
) -> dict[str, Any]:
    figure, axes = plt.subplots(
        len(records),
        3,
        figsize=(15.5, 3.05 * len(records)),
        squeeze=False,
    )
    edges = np.linspace(0.0, 4.0, 41)
    provenance = []
    for row_index, (record, row_axes) in enumerate(zip(records, axes)):
        dynamics_path = ROOT / record["source_dir"] / "results.npz"
        spacing_path = ROOT / record["spacing_source"]
        if not dynamics_path.is_file() or not spacing_path.is_file():
            raise FileNotFoundError(f"missing source for {record['config_id']}")
        with np.load(dynamics_path) as dynamics:
            _plot_angular(row_axes[0], dynamics, show_legend=row_index == 0)
            _plot_ratio(
                row_axes[1], dynamics, record, show_legend=row_index == 0
            )
        sectors, pooled = _spacing_histograms(spacing_path, edges=edges)
        _plot_spacings(
            row_axes[2],
            sectors,
            pooled,
            edges,
            record,
            show_legend=row_index == 0,
        )
        family = "2NN" if record["family"] == "second_neighbor" else "NN"
        row_axes[0].set_title(
            f"#{int(record['rank'])}: {family}, N={int(record['detector_n'])}, "
            f"{record['config_id']}\n{_parameter_label(record)}",
            fontsize=8.4,
            loc="left",
            pad=4.0,
        )
        if row_index < len(records) - 1:
            for axis in row_axes[:2]:
                axis.set_xlabel("")
        else:
            row_axes[0].set_xlabel(r"$\theta$")
            row_axes[1].set_xlabel(r"$\theta$")
        provenance.append(
            {
                "rank": int(record["rank"]),
                "family": record["family"],
                "detector_n": int(record["detector_n"]),
                "config_id": record["config_id"],
                "dynamics": str(dynamics_path.relative_to(ROOT)),
                "dynamics_sha256": _sha256(dynamics_path),
                "spacing": str(spacing_path.relative_to(ROOT)),
                "spacing_sha256": _sha256(spacing_path),
                "resolved_sector_count": int(sectors.shape[0]),
                "plotted_spacing_count": int(np.sum(pooled)),
            }
        )

    figure.suptitle(
        CATEGORY_TITLES[category]
        + r": clean 1D rings, $h_{z0}=0$; dynamics and detector spacings at the same $N$",
        fontsize=14,
        y=0.998,
    )
    figure.text(
        0.5,
        0.002,
        (
            "Spacing sectors are unfolded separately before pooling; faint curves are "
            "individual sectors. Exact degeneracies were merged; cubic unfolding used "
            "a 10% edge trim. NN/2NN denote nearest-/second-neighbor Hamiltonians."
        ),
        ha="center",
        fontsize=8.0,
    )
    figure.tight_layout(rect=(0.02, 0.012, 0.995, 0.985), h_pad=1.25, w_pad=1.0)
    temporary = output.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=dpi, bbox_inches="tight")
    plt.close(figure)
    temporary.replace(output)
    return {"figure": str(output.relative_to(ROOT)), "cases": provenance}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--dpi", type=int, default=180)
    return result


def main() -> None:
    args = parser().parse_args()
    catalog_path = args.catalog.resolve()
    catalog = _read_json(catalog_path)
    records = catalog.get("examples", [])
    if len(records) != 40:
        raise ValueError(f"catalog has {len(records)} examples, expected 40")
    by_category = {
        category: sorted(
            [record for record in records if record["category"] == category],
            key=lambda record: int(record["rank"]),
        )
        for category in CATEGORY_TITLES
    }
    if any(len(category_records) != 10 for category_records in by_category.values()):
        raise ValueError("each category must contain exactly ten examples")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    figures = []
    for category, category_records in by_category.items():
        figure_path = output / f"{category}__diagnostics_and_resolved_spacings.png"
        figures.append(
            {
                "category": category,
                **plot_category(
                    category,
                    category_records,
                    figure_path,
                    dpi=args.dpi,
                ),
            }
        )
        print(figure_path)
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "clean one-dimensional rings with hz0=0",
        "catalog": str(catalog_path.relative_to(ROOT)),
        "catalog_sha256": _sha256(catalog_path),
        "spacing_plot": (
            "individual resolved-sector densities as faint traces; pooled after "
            "sectorwise unfolding as the prominent histogram"
        ),
        "figures": figures,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
