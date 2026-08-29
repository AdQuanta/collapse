"""Build momentum-resolved P(theta) and R(theta) for three N=17 rings.

The expensive N=17 runs saved their projective roots after concatenating the
translation-sector pencils in increasing ``kblock`` order.  This script uses
the exact cyclic-representation dimensions to recover those sectors.  It does
not rediagonalise a Hamiltonian.

Every output figure contains the nonredundant momentum channels.  Generic
``k`` and ``-k`` roots are pooled because reflection makes them equivalent;
the archived ``k=0`` roots are shown as a momentum block with reflection
parity unresolved, since parity labels cannot be recovered from eigenvalues
without the sector eigenvectors.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work" / "_mplconfig"))
warnings.filterwarnings("ignore", message=r".*font family.*not found.*")
warnings.filterwarnings("ignore", message=r".*Glyph.*missing from font.*")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from core.sobol_coupling_scan import _diagnostics, fit_distributions  # noqa: E402
from core.translation_sector_roots import (  # noqa: E402
    nonredundant_momentum_roots,
    split_concatenated_translation_roots,
)
from scripts.build_three_ring_momentum_spacing_figures import (  # noqa: E402
    DEFAULT_CASES,
    CaseSource,
    HamiltonianParameters,
    _load_case,
)


DEFAULT_OUTPUT = ROOT / "work" / "ring_momentum_relative_diagnostics_three_cases_20260823"
BLUE = "#1f77b4"
RED = "#d95f5f"
RATIO = "#6b3f7c"
MODEL_BLUE = "#2a80c9"
MODEL_ORANGE = "#ef8a00"


def _json_float(value: Any) -> Any:
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _validate_source(case: CaseSource, detector_n: int) -> tuple[np.ndarray, dict[str, Any]]:
    metadata_path = case.diagnostics_path / "metadata.json"
    results_path = case.diagnostics_path / "results.npz"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if int(metadata["target_N"]) != detector_n:
        raise ValueError(f"{case.case_id} is not an N={detector_n} result")
    if metadata.get("symmetry_labels") != ["pixel_shift"]:
        raise ValueError(f"{case.case_id} was not saved from pixel-shift sectors")
    if int(metadata.get("sector_count", -1)) != detector_n:
        raise ValueError(f"{case.case_id} does not contain all momentum sectors")
    with np.load(results_path, allow_pickle=False) as archive:
        eigenvalues = np.asarray(archive["eigenvalues"], dtype=np.complex128)
        stored = {
            key: np.asarray(archive[key])
            for key in (
                "p_theta",
                "p_pi_minus_theta",
                "R",
                "R_occupied",
                "theta",
            )
        }
    return eigenvalues, stored


def _plot_case(
    case: CaseSource,
    parameters: HamiltonianParameters,
    provenance: dict[str, Any],
    paired: list[dict[str, Any]],
    detector_n: int,
    output: Path,
    dpi: int,
) -> None:
    figure = plt.figure(figsize=(18.0, 14.5), constrained_layout=False)
    outer = figure.add_gridspec(3, 3, hspace=0.38, wspace=0.24)
    for panel_index, row in enumerate(paired):
        cell = outer[panel_index // 3, panel_index % 3].subgridspec(
            2, 1, height_ratios=(1.0, 0.92), hspace=0.08
        )
        ax_p = figure.add_subplot(cell[0, 0])
        ax_r = figure.add_subplot(cell[1, 0], sharex=ax_p)
        arrays = row["arrays"]
        metrics = row["metrics"]
        fit_arrays = row["fit_arrays"]
        momenta = row["momenta"]
        ax_p.stairs(
            arrays["p_theta"], arrays["edges"], color=BLUE,
            linewidth=1.25, fill=True, alpha=0.18,
        )
        ax_p.stairs(
            arrays["p_pi_minus_theta"], arrays["edges"], color=RED,
            linewidth=1.15, fill=True, alpha=0.13,
        )
        ax_p.plot(
            fit_arrays["fit_grid"], fit_arrays["wg_density"],
            color=MODEL_BLUE, linewidth=1.2,
        )
        ax_p.plot(
            fit_arrays["fit_grid"], fit_arrays["wc_density"],
            color=MODEL_ORANGE, linewidth=1.15, linestyle="--",
        )
        mask = arrays["R_occupied"]
        ax_r.plot(
            arrays["centers"][mask], arrays["R"][mask], "o-",
            color=RATIO, markersize=2.1, linewidth=0.9,
        )
        ax_r.plot(
            arrays["centers"], arrays["R_born"], "k--", linewidth=1.05,
        )
        if len(momenta) == 1:
            title = rf"$k=0$, $d={row['root_count']}$"
        else:
            title = rf"$k=\pm{momenta[0]}$, $d_{{\rm pooled}}={row['root_count']}$"
        ax_p.set_title(title, fontsize=10.2, pad=5)
        ax_p.set_ylabel(r"$P$", fontsize=9)
        ax_r.set_ylabel(r"$R$", fontsize=9)
        ax_r.set_xlabel(r"$\theta$", fontsize=9)
        ax_p.set_xlim(0.0, np.pi)
        ax_p.set_ylim(bottom=0.0)
        ax_r.set_ylim(-0.04, 1.04)
        ax_r.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
        ax_p.tick_params(labelbottom=False, labelsize=8)
        ax_r.tick_params(labelsize=8)
        ax_p.grid(alpha=0.15)
        ax_r.grid(alpha=0.15)
        ax_r.text(
            0.035,
            0.08,
            rf"$S_{{\rm Born}}={metrics['S_born']:.3f}$" + "\n"
            + rf"RMSE$={metrics['born_RMSE_occupied']:.3f}$",
            transform=ax_r.transAxes,
            fontsize=8.0,
            va="bottom",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.0},
        )

    second = ""
    if parameters.j2 or parameters.jpm2:
        second = rf", $J_2={parameters.j2:.5g}$, $J_{{\pm2}}={parameters.jpm2:.5g}$"
    figure.suptitle(
        case.description + "\n"
        + rf"momentum-resolved projective diagnostics, $N_D={detector_n}$, "
        + f"global $S_{{\\rm Born}}={provenance['N17_S_born']:.4f}$\n"
        + rf"$h_z={parameters.hz:.5g}$, $J={parameters.j:.5g}$, "
        + rf"$J_{{\pm}}={parameters.jpm:.5g}${second}",
        fontsize=14,
        y=0.992,
    )
    handles = (
        Line2D([], [], color=BLUE, linewidth=5, alpha=0.35, label=r"$P_k(\theta)$"),
        Line2D([], [], color=RED, linewidth=5, alpha=0.30, label=r"$P_k(\pi-\theta)$"),
        Line2D([], [], color=MODEL_BLUE, label="wrapped Gaussian"),
        Line2D([], [], color=MODEL_ORANGE, linestyle="--", label="wrapped Cauchy"),
        Line2D([], [], color=RATIO, marker="o", markersize=3, label=r"$R_k(\theta)$"),
        Line2D([], [], color="black", linestyle="--", label=r"$\cos^2(\theta/2)$"),
    )
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.935), ncol=6, frameon=False)
    figure.text(
        0.5,
        0.012,
        (
            rf"Momentum labels are integer indices in units of $2\pi/{detector_n}$. "
            r"Each generic pane pools the reflection-equivalent $k$ and $-k$ roots; "
            r"the $k=0$ pane pools reflection parities. "
            r"All distributions are normalized conditionally within the displayed channel; "
            r"64 common bins on $[0,\pi]$."
        ),
        ha="center",
        fontsize=9,
    )
    figure.subplots_adjust(left=0.055, right=0.985, bottom=0.055, top=0.90)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(figure)


def analyze_case(
    case: CaseSource,
    detector_n: int,
    bins: int,
    output_dir: Path,
    dpi: int,
) -> dict[str, Any]:
    parameters, provenance = _load_case(case)
    eigenvalues, stored = _validate_source(case, detector_n)
    sectors = split_concatenated_translation_roots(eigenvalues, detector_n)
    reconstructed = np.concatenate([sector.eigenvalues for sector in sectors])
    if not np.array_equal(reconstructed, eigenvalues):
        raise RuntimeError("translation split did not exactly reconstruct the archived roots")

    global_metrics, global_arrays = _diagnostics(eigenvalues, bins)
    validation_differences: dict[str, float] = {}
    for key in ("p_theta", "p_pi_minus_theta", "theta"):
        validation_differences[key] = float(np.max(np.abs(global_arrays[key] - stored[key])))
    common = global_arrays["R_occupied"] & stored["R_occupied"].astype(bool)
    validation_differences["R"] = float(
        np.max(np.abs(global_arrays["R"][common] - stored["R"][common]))
    )
    if max(validation_differences.values()) > 1.0e-12:
        raise RuntimeError(f"archived global diagnostics were not reproduced: {validation_differences}")

    archive_payload: dict[str, np.ndarray] = {}
    sector_records: list[dict[str, Any]] = []
    for sector in sectors:
        metrics, arrays = _diagnostics(sector.eigenvalues, bins)
        prefix = f"k{sector.momentum_index:02d}"
        archive_payload[f"{prefix}__eigenvalues"] = sector.eigenvalues
        for key in ("theta", "edges", "centers", "p_theta", "p_pi_minus_theta", "R", "R_occupied", "R_born", "R_residual"):
            archive_payload[f"{prefix}__{key}"] = arrays[key]
        sector_records.append(
            {
                "momentum_index": sector.momentum_index,
                "momentum": f"2*pi*{sector.momentum_index}/{detector_n}",
                "root_count": sector.dimension,
                "metrics": metrics,
            }
        )

    paired_records: list[dict[str, Any]] = []
    pair_symmetry_errors: list[float] = []
    for momenta, roots in nonredundant_momentum_roots(sectors):
        metrics, arrays = _diagnostics(roots, bins)
        fit, fit_arrays = fit_distributions(
            arrays["theta"],
            bins,
            plot_grid=720,
            nmax=32,
            tol=1.0e-10,
        )
        if len(momenta) == 2:
            first = 2.0 * np.arctan(np.abs(sectors[momenta[0]].eigenvalues))
            second = 2.0 * np.arctan(np.abs(sectors[momenta[1]].eigenvalues))
            symmetry_error = float(np.max(np.abs(np.sort(first) - np.sort(second))))
            pair_symmetry_errors.append(symmetry_error)
        else:
            symmetry_error = 0.0
        paired_records.append(
            {
                "momenta": momenta,
                "root_count": int(roots.size),
                "metrics": metrics,
                "arrays": arrays,
                "fit": fit,
                "fit_arrays": fit_arrays,
                "paired_theta_max_abs_difference": symmetry_error,
            }
        )
        pair_key = "_".join(f"k{momentum:02d}" for momentum in momenta)
        for key in ("fit_grid", "wg_density", "wc_density", "wg_residual", "wc_residual"):
            archive_payload[f"paired_{pair_key}__{key}"] = fit_arrays[key]

    case_dir = output_dir / case.case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    archive_path = case_dir / f"momentum_projective_diagnostics_N{detector_n}.npz"
    np.savez_compressed(archive_path, **archive_payload)
    figure_path = case_dir / f"momentum_P_R_diagnostics_N{detector_n}.png"
    _plot_case(case, parameters, provenance, paired_records, detector_n, figure_path, dpi)
    metrics_path = case_dir / f"momentum_projective_metrics_N{detector_n}.json"
    serializable_pairs = [
        {
            key: value
            for key, value in row.items()
            if key not in {"arrays", "fit_arrays"}
        }
        for row in paired_records
    ]
    payload = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "case_id": case.case_id,
        "description": case.description,
        "detector_n": detector_n,
        "parameters": parameters.__dict__,
        "provenance": provenance,
        "source_results": str((case.diagnostics_path / "results.npz").relative_to(ROOT)),
        "root_order_contract": "increasing QuSpin detector kblock, k=0,...,N-1",
        "normalization": "each P_k integrates to one within its momentum channel",
        "fits": (
            "same reflection-augmented wrapped-Gaussian and wrapped-Cauchy "
            "fits as the established diagnostics; period 2*pi, 32 harmonics"
        ),
        "global_metrics_recomputed": global_metrics,
        "individual_momentum_sectors": sector_records,
        "nonredundant_reflection_paired_channels": serializable_pairs,
        "validation": {
            "exact_root_reconstruction": True,
            "archived_global_array_max_abs_differences": validation_differences,
            "maximum_paired_theta_difference": max(pair_symmetry_errors, default=0.0),
            "reflection_parity_at_k0": (
                "not recoverable from archived roots alone; the displayed k=0 distribution pools p=+/-"
            ),
        },
        "figure": str(figure_path.relative_to(ROOT)),
        "archive": str(archive_path.relative_to(ROOT)),
    }
    metrics_path.write_text(json.dumps(payload, indent=2, default=_json_float), encoding="utf-8")
    return {
        "case_id": case.case_id,
        "figure": str(figure_path.relative_to(ROOT)),
        "metrics": str(metrics_path.relative_to(ROOT)),
        "archive": str(archive_path.relative_to(ROOT)),
        "global_S_born": float(global_metrics["S_born"]),
        "sector_S_born_min": min(float(row["metrics"]["S_born"]) for row in paired_records),
        "sector_S_born_max": max(float(row["metrics"]["S_born"]) for row in paired_records),
        "maximum_paired_theta_difference": max(pair_symmetry_errors, default=0.0),
    }


def run(output_dir: Path, detector_n: int, bins: int, dpi: int, force: bool) -> dict[str, Any]:
    if detector_n != 17:
        raise ValueError("the identified archived cases are specifically N=17")
    summary_path = output_dir / f"summary_N{detector_n}.json"
    if summary_path.exists() and not force:
        raise FileExistsError(f"{summary_path} already exists; pass --force to replace it")
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for index, case in enumerate(DEFAULT_CASES, start=1):
        print(f"[{index}/{len(DEFAULT_CASES)}] {case.case_id}", flush=True)
        record = analyze_case(case, detector_n, bins, output_dir, dpi)
        records.append(record)
        print(
            f"  global S_born={record['global_S_born']:.6f}; "
            f"sector range=[{record['sector_S_born_min']:.6f}, "
            f"{record['sector_S_born_max']:.6f}]",
            flush=True,
        )
    summary = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "detector_n": detector_n,
        "bins": bins,
        "method": "exact split of archived projective roots by cyclic character multiplicities",
        "cases": records,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--n", type=int, default=17)
    parser.add_argument("--bins", type=int, default=64)
    parser.add_argument("--dpi", type=int, default=190)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.output.resolve(), args.n, args.bins, args.dpi, args.force)
    print(f"Completed {len(summary['cases'])} cases in {args.output.resolve()}", flush=True)


if __name__ == "__main__":
    main()
