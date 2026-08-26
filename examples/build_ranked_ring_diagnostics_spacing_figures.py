"""Combine source P(theta), R(theta) diagnostics with N=17 spacing panels.

This is a rendering-only follow-up to
``build_ranked_ring_momentum_spacing_figures.py``.  It does not diagonalise the
Hamiltonian again.  The left column is reconstructed from each original N=14
Sobol ``results.npz`` file, while the right 3x3 grid uses the stored N=17
symmetry-resolved unfolded spacings.  Input checksums, normalisations, and
source S_Born values are validated before rendering.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from collapse.level_spacing import (  # noqa: E402
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)


DEFAULT_SPACING_ROOT = (
    ROOT / "reports" / "ranked_ring_symmetry_resolved_spacings_N17_2026-08-25"
)
DEFAULT_OUTPUT = (
    ROOT
    / "reports"
    / "ranked_ring_diagnostics_and_symmetry_spacings_N17_2026-08-26"
)
BLUE = "#4c9ed9"
RED = "#e88484"
RATIO = "#6b3f7c"
MODEL_BLUE = "#1f77b4"
MODEL_ORANGE = "#e68a00"
SCHEMA_VERSION = 1


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_source_diagnostics(case: dict[str, Any]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Load and validate the canonical diagnostic arrays for one source case."""
    source_dir = _resolve_repo_path(case["source_dir"])
    results_path = source_dir / "results.npz"
    metrics_path = source_dir / "metrics.json"
    complete_path = source_dir / "COMPLETE.json"
    complete = _load_json(complete_path)
    metrics = _load_json(metrics_path)
    for path in (results_path, metrics_path):
        expected = complete.get("files", {}).get(path.name)
        if not expected or _sha256(path) != expected:
            raise ValueError(f"source checksum mismatch or omission: {path}")
    if not math.isclose(
        float(metrics["S_born"]), float(case["s_born"]), rel_tol=0.0, abs_tol=1e-13
    ):
        raise ValueError(f"stored S_Born mismatch for {source_dir}")

    required = (
        "edges",
        "centers",
        "p_theta",
        "p_pi_minus_theta",
        "R",
        "R_occupied",
        "R_born",
        "fit_grid",
        "wg_density",
        "wc_density",
    )
    with np.load(results_path) as archive:
        missing = set(required).difference(archive.files)
        if missing:
            raise ValueError(f"{results_path} lacks {sorted(missing)}")
        arrays = {key: np.asarray(archive[key]).copy() for key in required}
    always_finite = set(required).difference(("R", "R_occupied"))
    if not all(np.all(np.isfinite(arrays[key])) for key in always_finite):
        raise ValueError(f"nonfinite diagnostic data in {results_path}")
    occupied = arrays["R_occupied"].astype(bool)
    if not np.all(np.isfinite(arrays["R"][occupied])):
        raise ValueError(f"nonfinite occupied-bin R values in {results_path}")
    edges = arrays["edges"]
    if edges.size != arrays["p_theta"].size + 1:
        raise ValueError(f"inconsistent histogram shapes in {results_path}")
    widths = np.diff(edges)
    for key in ("p_theta", "p_pi_minus_theta"):
        integral = float(np.sum(arrays[key] * widths))
        if not math.isclose(integral, 1.0, rel_tol=0.0, abs_tol=2e-12):
            raise ValueError(f"{key} is not normalized in {results_path}: {integral}")
    expected_born = np.cos(arrays["centers"] / 2.0) ** 2
    if not np.allclose(arrays["R_born"], expected_born, rtol=0.0, atol=2e-14):
        raise ValueError(f"Born reference mismatch in {results_path}")
    metadata = {
        "source_results": _relative(results_path),
        "source_metrics": _relative(metrics_path),
        "results_sha256": _sha256(results_path),
        "metrics_sha256": _sha256(metrics_path),
        "S_born": float(metrics["S_born"]),
        "born_RMSE_occupied": float(metrics["born_RMSE_occupied"]),
        "occupied_fraction": float(metrics["occupied_fraction"]),
    }
    return arrays, metadata


def _sector_key(sector: dict[str, Any]) -> str:
    parity = sector["reflection_parity"]
    parity_label = "none" if parity is None else f"{int(parity):+d}"
    return (
        f"k{int(sector['momentum']):02d}_q{int(sector['n_up']):02d}_"
        f"p{parity_label}"
    )


def load_spacing_data(case: dict[str, Any]) -> tuple[dict[int, list[dict[str, Any]]], dict[str, Any]]:
    """Load and validate all 45 stored resolved spacing blocks."""
    archive_path = _resolve_repo_path(case["spectral_archive"])
    grouped: dict[int, list[dict[str, Any]]] = {}
    with np.load(archive_path) as archive:
        for sector in case["sectors"]:
            key = _sector_key(sector)
            energy_key = f"{key}__energies"
            spacing_key = f"{key}__unfolded_spacings"
            if energy_key not in archive or spacing_key not in archive:
                raise ValueError(f"missing {key} arrays in {archive_path}")
            energies = np.asarray(archive[energy_key])
            spacings = np.asarray(archive[spacing_key]).copy()
            if energies.size != int(sector["dimension"]):
                raise ValueError(f"dimension mismatch for {key} in {archive_path}")
            if spacings.size != int(sector["spacing_count"]):
                raise ValueError(f"spacing-count mismatch for {key} in {archive_path}")
            if not np.all(np.isfinite(energies)) or not np.all(np.isfinite(spacings)):
                raise ValueError(f"nonfinite spectrum for {key} in {archive_path}")
            grouped.setdefault(int(sector["momentum"]), []).append(
                {**sector, "unfolded_spacings": spacings}
            )
    if sorted(grouped) != list(range(9)) or any(len(rows) != 5 for rows in grouped.values()):
        raise ValueError(f"expected five blocks at each k=0,...,8 in {archive_path}")
    return grouped, {
        "source_spectral_archive": _relative(archive_path),
        "spectral_archive_sha256": _sha256(archive_path),
        "sector_count": sum(map(len, grouped.values())),
    }


def _plot_diagnostics(
    probability_axis: plt.Axes,
    ratio_axis: plt.Axes,
    arrays: dict[str, np.ndarray],
    diagnostic_metadata: dict[str, Any],
) -> None:
    probability_axis.stairs(
        arrays["p_theta"],
        arrays["edges"],
        color=BLUE,
        linewidth=1.55,
        fill=True,
        alpha=0.17,
        label=r"$P(\theta)$",
    )
    probability_axis.stairs(
        arrays["p_pi_minus_theta"],
        arrays["edges"],
        color=RED,
        linewidth=1.45,
        fill=True,
        alpha=0.13,
        label=r"$P(\pi-\theta)$",
    )
    probability_axis.plot(
        arrays["fit_grid"],
        arrays["wg_density"],
        color=MODEL_BLUE,
        linewidth=1.35,
        label="wrapped Gaussian",
    )
    probability_axis.plot(
        arrays["fit_grid"],
        arrays["wc_density"],
        color=MODEL_ORANGE,
        linewidth=1.35,
        linestyle="--",
        label="wrapped Cauchy",
    )
    probability_axis.set(
        title=r"Angular distribution $P(\theta)$",
        ylabel="density",
        xlim=(0.0, np.pi),
    )
    probability_axis.grid(alpha=0.16)
    probability_axis.legend(ncol=2, frameon=False, fontsize=8.5, loc="upper center")

    occupied = arrays["R_occupied"].astype(bool)
    ratio_axis.plot(
        arrays["centers"][occupied],
        arrays["R"][occupied],
        "o-",
        color=RATIO,
        markersize=3.2,
        linewidth=1.05,
        label=r"$R(\theta)$ (occupied bins)",
    )
    ratio_axis.plot(
        arrays["centers"],
        arrays["R_born"],
        "k--",
        linewidth=1.35,
        label=r"$\cos^2(\theta/2)$",
    )
    ratio_axis.set(
        title=r"Born-ratio diagnostic $R(\theta)$",
        xlabel=r"$\theta$",
        ylabel=r"$R(\theta)$",
        ylim=(-0.04, 1.04),
        xlim=(0.0, np.pi),
    )
    ratio_axis.grid(alpha=0.16)
    ratio_axis.legend(frameon=False, ncol=2, fontsize=8.5, loc="upper center")
    ratio_axis.text(
        0.03,
        0.07,
        rf"$S_{{\rm Born}}={diagnostic_metadata['S_born']:.3f}$"
        + "\n"
        + rf"$\mathrm{{RMSE}}={diagnostic_metadata['born_RMSE_occupied']:.3f}$",
        transform=ratio_axis.transAxes,
        va="bottom",
        fontsize=9.5,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.5},
    )


def _plot_spacings(
    figure: plt.Figure,
    grid: Any,
    grouped: dict[int, list[dict[str, Any]]],
) -> None:
    colors = plt.get_cmap("tab10").colors[:5]
    s_grid = np.linspace(0.0, 4.0, 600)
    shared_x: plt.Axes | None = None
    shared_y: plt.Axes | None = None
    for momentum in range(9):
        row, column = divmod(momentum, 3)
        axis = figure.add_subplot(
            grid[row, column], sharex=shared_x, sharey=shared_y
        )
        if shared_x is None:
            shared_x = axis
            shared_y = axis
        for color, sector in zip(colors, grouped[momentum], strict=True):
            spacings = sector["unfolded_spacings"]
            counts, edges = np.histogram(spacings, bins=np.linspace(0.0, 4.0, 33))
            density = counts / (spacings.size * np.diff(edges))
            centers = 0.5 * (edges[:-1] + edges[1:])
            parity = sector["reflection_parity"]
            parity_text = "" if parity is None else f", p={'+' if parity > 0 else '-'}"
            axis.step(
                centers,
                density,
                where="mid",
                color=color,
                linewidth=1.1,
                alpha=0.92,
                label=(
                    rf"$N_\uparrow={int(sector['n_up'])}{parity_text}$, "
                    f"d={int(sector['dimension'])}, "
                    rf"$\langle\tilde r\rangle={float(sector['mean_r']):.3f}$"
                ),
            )
        axis.plot(
            s_grid,
            poisson_spacing_distribution(s_grid),
            "k--",
            linewidth=1.1,
            label="Poisson",
        )
        axis.plot(
            s_grid,
            wigner_spacing_distribution(s_grid, beta=1),
            "k:",
            linewidth=1.2,
            label="GOE",
        )
        momentum_label = "0" if momentum == 0 else rf"\pm{momentum}"
        axis.set_title(rf"$k={momentum_label}$", fontsize=10.5)
        axis.set_xlim(0.0, 4.0)
        axis.set_ylim(bottom=0.0)
        axis.grid(alpha=0.18)
        axis.legend(loc="upper right", fontsize=5.8, framealpha=0.88)
        if row == 2:
            axis.set_xlabel(r"unfolded spacing $s$", fontsize=9.5)
        else:
            axis.tick_params(labelbottom=False)
        if column == 0:
            axis.set_ylabel(r"density $P(s)$", fontsize=9.5)
        else:
            axis.tick_params(labelleft=False)
        axis.tick_params(labelsize=8.5)


def render_case(
    case: dict[str, Any],
    output_root: Path,
    detector_n: int,
    dpi: int,
    force: bool,
) -> dict[str, Any]:
    diagnostic_arrays, diagnostic_metadata = load_source_diagnostics(case["case"])
    grouped, spacing_metadata = load_spacing_data(case)
    case_info = case["case"]
    target_dir = output_root / case_info["family"] / case_info["tail"]
    target_dir.mkdir(parents=True, exist_ok=True)
    stem = (
        f"rank_{int(case_info['rank_within_tail']):02d}__{case_info['config_id']}__"
        f"N{detector_n}_diagnostics_and_momentum_spacings.png"
    )
    target = target_dir / stem
    if target.exists() and not force:
        return {
            "case": case_info,
            "figure": _relative(target),
            **diagnostic_metadata,
            **spacing_metadata,
            "figure_sha256": _sha256(target),
            "runtime_seconds": 0.0,
            "resumed": True,
        }

    started = time.perf_counter()
    figure = plt.figure(figsize=(26.0, 14.5))
    outer = figure.add_gridspec(
        1,
        2,
        width_ratios=(1.08, 3.0),
        left=0.035,
        right=0.99,
        bottom=0.055,
        top=0.855,
        wspace=0.075,
    )
    diagnostic_grid = outer[0, 0].subgridspec(2, 1, hspace=0.22)
    spacing_grid = outer[0, 1].subgridspec(3, 3, hspace=0.30, wspace=0.13)
    probability_axis = figure.add_subplot(diagnostic_grid[0, 0])
    ratio_axis = figure.add_subplot(diagnostic_grid[1, 0])
    _plot_diagnostics(
        probability_axis, ratio_axis, diagnostic_arrays, diagnostic_metadata
    )
    _plot_spacings(figure, spacing_grid, grouped)

    parameters = case_info["parameters"]
    second_text = ""
    if parameters["j2"] or parameters["jpm2"]:
        second_text = (
            rf", $J_2={float(parameters['j2']):.6g}$, "
            rf"$J_{{\pm2}}={float(parameters['jpm2']):.6g}$"
        )
    tail_label = (
        "most Born-like" if case_info["tail"] == "highest" else "least Born-like"
    )
    figure.suptitle(
        "\n".join(
            (
                f"{case_info['family_description']}: {tail_label} rank "
                f"{int(case_info['rank_within_tail'])}, {case_info['config_id']}",
                rf"source $N={int(case_info['source_n'])}$: "
                rf"$S_{{\rm Born}}={float(case_info['s_born']):.6f}$; "
                rf"$h_z={float(parameters['hz']):.6g}$, "
                rf"$J={float(parameters['j']):.6g}$, "
                rf"$J_{{\pm}}={float(parameters['jpm']):.6g}${second_text}",
                rf"collective coupling: $J_{{x,\rm unscaled}}="
                rf"{float(case_info['jx_unscaled']):.6g}$, "
                rf"$J_{{x,\rm eff}}=J_x/\sqrt{{{int(case_info['source_n'])}}}="
                rf"{float(case_info['jx_unscaled']) / math.sqrt(int(case_info['source_n'])):.6g}$",
            )
        ),
        fontsize=14,
        y=0.982,
    )
    figure.text(
        0.165,
        0.88,
        rf"Dynamical diagnostics (source $N={int(case_info['source_n'])}$)",
        ha="center",
        fontsize=12.5,
        fontweight="bold",
    )
    figure.text(
        0.69,
        0.88,
        rf"Symmetry-resolved detector spacings ($N_D={detector_n}$)",
        ha="center",
        fontsize=12.5,
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.015,
        (
            rf"Exact spacing sectors: fixed $N_\uparrow$ and $D_{{{detector_n}}}$; "
            r"each nonzero-k pane represents the equivalent $\pm k$ pair. "
            r"Exact degeneracies merged; cubic unfolding with 10% edge trim."
        ),
        ha="center",
        fontsize=9,
    )
    temporary = target.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=dpi, bbox_inches="tight")
    plt.close(figure)
    temporary.replace(target)
    return {
        "case": case_info,
        "figure": _relative(target),
        **diagnostic_metadata,
        **spacing_metadata,
        "figure_sha256": _sha256(target),
        "runtime_seconds": time.perf_counter() - started,
        "resumed": False,
    }


def run(
    spacing_root: Path,
    output_root: Path,
    workers: int,
    dpi: int,
    force: bool,
) -> dict[str, Any]:
    spacing_root = spacing_root.resolve()
    summary_path = spacing_root / "summary_N17.json"
    summary = _load_json(summary_path)
    detector_n = int(summary["detector_n"])
    if detector_n != 17:
        raise ValueError(f"expected the N=17 spacing report, found N={detector_n}")
    cases = summary["cases"]
    if len(cases) != 40:
        raise ValueError(f"expected 40 ranked cases, found {len(cases)}")
    if workers < 1:
        raise ValueError("workers must be positive")
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rendered: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=min(workers, len(cases))) as pool:
        futures = {
            pool.submit(render_case, case, output_root, detector_n, dpi, force): case
            for case in cases
        }
        for index, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            rendered.append(row)
            info = row["case"]
            print(
                f"[{index:02d}/{len(cases)}] {info['family']} {info['tail']} "
                f"rank {int(info['rank_within_tail']):02d} {info['config_id']}"
                + (" (resumed)" if row["resumed"] else ""),
                flush=True,
            )
    rendered.sort(
        key=lambda row: (
            row["case"]["family"],
            0 if row["case"]["tail"] == "highest" else 1,
            int(row["case"]["rank_within_tail"]),
        )
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "detector_n": detector_n,
        "diagnostic_source_n": 14,
        "spacing_summary": _relative(summary_path),
        "spacing_summary_sha256": _sha256(summary_path),
        "rendering": (
            "Left: canonical source P(theta) with WG/WC fits and occupied-bin "
            "R(theta) with Born reference. Right: five largest exact blocks at "
            "each nonredundant N=17 momentum."
        ),
        "jx_title_convention": (
            "Jx_unscaled is the stored campaign input; Jx_eff is the coupling "
            "used in the source dynamics after division by sqrt(source N)."
        ),
        "runtime_seconds": time.perf_counter() - started,
        "case_count": len(rendered),
        "cases": rendered,
    }
    _write_json_atomic(output_root / "render_manifest.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spacing-root", type=Path, default=DEFAULT_SPACING_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = run(
        spacing_root=args.spacing_root,
        output_root=args.output,
        workers=args.workers,
        dpi=args.dpi,
        force=args.force,
    )
    print(
        f"Rendered {manifest['case_count']} combined figures in "
        f"{manifest['runtime_seconds']:.1f}s: {args.output.resolve()}",
        flush=True,
    )


if __name__ == "__main__":
    main()
