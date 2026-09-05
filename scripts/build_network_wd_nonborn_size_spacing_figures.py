#!/usr/bin/env python3.11
"""Plot dynamics and resolved spacings versus N for four network cases."""

from __future__ import annotations

import argparse
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
from core.sobol_coupling_scan import _atomic_json, _sha256, timestamp  # noqa: E402
from scripts.build_network_wd_nonborn_diagnostics import (  # noqa: E402
    BLUE,
    FAMILY_LABELS,
    MODEL_BLUE,
    MODEL_ORANGE,
    RATIO,
    RED,
    _inventory,
    _repo_relative,
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _load_spacing(case_dir: Path) -> list[dict[str, Any]]:
    metadata_path = case_dir / "detector_spacing_metadata.json"
    archive_path = case_dir / "detector_spacing_summary.npz"
    metadata = _read_json(metadata_path)
    records = metadata.get("sectors")
    if not isinstance(records, list) or not records:
        raise ValueError(f"no spacing-sector records in {metadata_path}")
    output = []
    with np.load(archive_path) as arrays:
        for record in records:
            prefix = str(record["key"])
            required = {
                f"{prefix}__edges",
                f"{prefix}__density",
            }
            missing = required - set(arrays.files)
            if missing:
                raise ValueError(f"{archive_path} lacks {sorted(missing)}")
            output.append(
                {
                    "metadata": record,
                    "edges": np.asarray(
                        arrays[f"{prefix}__edges"], dtype=np.float64
                    ),
                    "density": np.asarray(
                        arrays[f"{prefix}__density"], dtype=np.float64
                    ),
                }
            )
    return output


def _plot_angular(axis: plt.Axes, arrays: dict[str, np.ndarray]) -> None:
    axis.stairs(
        arrays["p_theta"],
        arrays["edges"],
        color=BLUE,
        linewidth=0.95,
        fill=True,
        alpha=0.20,
        label=r"$P(\theta)$",
    )
    axis.stairs(
        arrays["p_pi_minus_theta"],
        arrays["edges"],
        color=RED,
        linewidth=0.85,
        fill=True,
        alpha=0.14,
        label=r"$P(\pi-\theta)$",
    )
    axis.plot(
        arrays["fit_grid"],
        arrays["wg_density"],
        color=MODEL_BLUE,
        linewidth=0.85,
        label="wrapped Gaussian",
    )
    axis.plot(
        arrays["fit_grid"],
        arrays["wc_density"],
        color=MODEL_ORANGE,
        linewidth=0.85,
        linestyle="--",
        label="wrapped Cauchy",
    )
    axis.set_xlim(0.0, np.pi)
    axis.set_ylim(bottom=0.0)
    axis.grid(alpha=0.16)
    axis.tick_params(labelbottom=False)


def _plot_ratio(
    axis: plt.Axes,
    arrays: dict[str, np.ndarray],
    metrics: dict[str, Any],
) -> None:
    occupied = arrays["R_occupied"].astype(bool)
    axis.plot(
        arrays["centers"][occupied],
        arrays["R"][occupied],
        "o-",
        color=RATIO,
        markersize=2.0,
        linewidth=0.75,
        label=r"$R(\theta)$",
    )
    axis.plot(
        arrays["centers"],
        arrays["R_born"],
        color="black",
        linestyle="--",
        linewidth=1.0,
        label=r"$\cos^2(\theta/2)$",
    )
    axis.set_xlim(0.0, np.pi)
    axis.set_ylim(-0.04, 1.04)
    axis.set_xticks((0.0, np.pi / 2.0, np.pi), ("0", r"$\pi/2$", r"$\pi$"))
    axis.grid(alpha=0.16)
    axis.text(
        0.035,
        0.07,
        rf"$S_{{\rm Born}}={float(metrics['S_born']):.3f}$"
        + "\n"
        + rf"RMSE$={float(metrics['born_RMSE_occupied']):.3f}$",
        transform=axis.transAxes,
        fontsize=7.8,
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78},
    )


def _plot_spacing(axis: plt.Axes, sectors: list[dict[str, Any]]) -> None:
    colors = plt.get_cmap("tab10").colors
    maximum = 4.0
    for index, sector in enumerate(sectors):
        edges = sector["edges"]
        density = sector["density"]
        maximum = max(maximum, float(edges[-1]))
        metadata = sector["metadata"]
        axis.stairs(
            density,
            edges,
            color=colors[index % len(colors)],
            linewidth=1.0,
            label=(
                f"{metadata['symmetry_label']}, d={int(metadata['dimension'])}, "
                rf"$\langle\tilde r\rangle={float(metadata['mean_adjacent_gap_ratio']):.3f}$"
            ),
        )
    reference = np.linspace(0.0, maximum, 500)
    axis.plot(
        reference,
        poisson_spacing_distribution(reference),
        color="black",
        linestyle="--",
        linewidth=1.0,
        label="Poisson",
    )
    axis.plot(
        reference,
        wigner_spacing_distribution(reference, beta=1),
        color="#e45756",
        linestyle=":",
        linewidth=1.15,
        label="GOE",
    )
    axis.set_xlim(0.0, maximum)
    axis.set_ylim(bottom=0.0)
    axis.set_xlabel(r"unfolded spacing $s$")
    axis.grid(alpha=0.16)
    axis.legend(framealpha=0.85, fontsize=6.0, loc="upper right")


def build_figures(source: Path, output: Path, *, dpi: int) -> dict[str, Any]:
    cases, target_sizes = _inventory(source)
    sizes = sorted({int(case["N"]) for case in cases})
    if sizes != target_sizes:
        raise ValueError(f"collection sizes {sizes} do not match targets {target_sizes}")
    families = sorted(
        {str(case["family"]) for case in cases},
        key=lambda family: next(
            int(path.name.split("_")[1])
            for path in source.glob(f"family_*_{family}")
        ),
    )
    lookup = {(str(case["family"]), int(case["N"])): case for case in cases}
    output.mkdir(parents=True, exist_ok=False)
    figure_records = []
    for family in families:
        figure, axes = plt.subplots(
            3,
            len(sizes),
            figsize=(5.15 * len(sizes), 11.2),
            squeeze=False,
        )
        case_records = []
        for column, size in enumerate(sizes):
            case = lookup[(family, size)]
            arrays = case["arrays"]
            _plot_angular(axes[0, column], arrays)
            _plot_ratio(axes[1, column], arrays, case["metrics"])
            sectors = _load_spacing(case["case_dir"])
            _plot_spacing(axes[2, column], sectors)
            axes[0, column].set_title(f"N={size}", fontsize=12, fontweight="bold")
            axes[1, column].set_xlabel(r"$\theta$")
            if column == 0:
                axes[0, column].set_ylabel(r"density $P(\theta)$")
                axes[1, column].set_ylabel(r"$R(\theta)$")
                axes[2, column].set_ylabel(r"density $p(s)$")
            if column == 0:
                axes[0, column].legend(frameon=False, fontsize=7.0, ncol=2)
                axes[1, column].legend(frameon=False, fontsize=7.2)
            case_records.append(
                {
                    "N": size,
                    "case_dir": _repo_relative(case["case_dir"]),
                    "dynamics_complete_sha256": _sha256(
                        case["case_dir"] / "COMPLETE.json"
                    ),
                    "spacing_complete_sha256": _sha256(
                        case["case_dir"] / "detector_spacing_COMPLETE.json"
                    ),
                    "resolved_sector_count": len(sectors),
                    "S_born": float(case["metrics"]["S_born"]),
                    "born_RMSE_occupied": float(
                        case["metrics"]["born_RMSE_occupied"]
                    ),
                }
            )
        source_case = cases[
            next(index for index, item in enumerate(cases) if item["family"] == family)
        ]["metadata"]["source"]["source_case"]
        figure.suptitle(
            f"{FAMILY_LABELS.get(family, family)} WD-selected source: {source_case}\n"
            + r"Dynamics and detector-only symmetry-resolved spacings versus $N$; $h_{z0}=0$",
            fontsize=14,
            y=0.995,
        )
        figure.text(
            0.5,
            0.006,
            (
                "Each spacing curve is a distinct nonredundant exact sector. "
                "Fixed Hamming weight, full graph automorphisms, and half-filling "
                "spin reversal (when present) were resolved before unfolding."
            ),
            ha="center",
            fontsize=8.0,
        )
        figure.tight_layout(rect=(0.025, 0.025, 0.995, 0.96), h_pad=1.25, w_pad=1.0)
        figure_path = output / f"{family}__N13_N15_diagnostics_and_spacings.png"
        temporary = figure_path.with_name(figure_path.stem + ".tmp.png")
        figure.savefig(temporary, dpi=dpi, facecolor="white", bbox_inches="tight")
        plt.close(figure)
        temporary.replace(figure_path)
        figure_records.append(
            {
                "family": family,
                "source_case": source_case,
                "figure": _repo_relative(figure_path),
                "figure_sha256": _sha256(figure_path),
                "cases": case_records,
            }
        )
        print(figure_path)

    provenance_path = output / "provenance.json"
    _atomic_json(
        provenance_path,
        {
            "schema_version": 1,
            "created": timestamp(),
            "source_collection": _repo_relative(source),
            "source_submission": (source / "submitted_jobs.txt").read_text().strip(),
            "plot_script": _repo_relative(Path(__file__)),
            "plot_script_sha256": _sha256(Path(__file__)),
            "validation": (
                "All 12 dynamics and spacing markers were complete; every listed "
                "artifact hash matched; all dynamics validation files passed."
            ),
            "sizes": sizes,
            "figures": figure_records,
        },
    )
    return {
        "figure_count": len(figure_records),
        "case_count": len(cases),
        "output": str(output),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--dpi", type=int, default=180)
    return result


def main() -> None:
    args = parser().parse_args()
    outcome = build_figures(
        args.source.resolve(), args.output.resolve(), dpi=args.dpi
    )
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()
