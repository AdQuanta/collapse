#!/usr/bin/env python3.11
"""Plot compact P(theta) and R(theta) diagnostics from a Zeus collection."""

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
    "MPLCONFIGDIR", str(ROOT / ".mplconfig-network-wd-nonborn-diagnostics")
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from core.sobol_coupling_scan import _atomic_json, _sha256, timestamp  # noqa: E402


FAMILY_LABELS = {
    "erdos_renyi": "Erdős–Rényi",
    "watts_strogatz": "Watts–Strogatz",
    "barabasi_albert": "Barabási–Albert",
    "expander": "random regular / Expander",
}
BLUE = "#2389c9"
RED = "#e45756"
RATIO = "#71427c"
MODEL_BLUE = "#0072b2"
MODEL_ORANGE = "#e69f00"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.name


def _validate_marker(case_dir: Path, marker_name: str) -> dict[str, Any]:
    marker_path = case_dir / marker_name
    marker = _read_json(marker_path)
    if marker.get("status") != "complete":
        raise RuntimeError(f"non-complete marker: {marker_path}")
    for name, expected in marker["files"].items():
        artifact = case_dir / str(name)
        if not artifact.is_file():
            raise FileNotFoundError(f"marker-listed artifact is absent: {artifact}")
        actual = _sha256(artifact)
        if actual != expected:
            raise RuntimeError(
                f"hash mismatch for {artifact}: {actual} != {expected}"
            )
    return marker


def _load_case(case_dir: Path) -> dict[str, Any]:
    completion = _validate_marker(case_dir, "COMPLETE.json")
    spacing_completion = _validate_marker(
        case_dir, "detector_spacing_COMPLETE.json"
    )
    validation = _read_json(case_dir / "validation.json")
    if not bool(validation.get("passed", False)):
        raise RuntimeError(f"scientific validation failed: {case_dir}")
    metadata = _read_json(case_dir / "metadata.json")
    metrics = _read_json(case_dir / "metrics.json")
    archive_path = case_dir / "results_summary.npz"
    required = {
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
    }
    with np.load(archive_path) as archive:
        missing = required - set(archive.files)
        if missing:
            raise ValueError(f"{archive_path} lacks arrays: {sorted(missing)}")
        arrays = {name: np.asarray(archive[name]) for name in required}
    family_dir_name = case_dir.parents[1].name
    family_parts = family_dir_name.split("_", 2)
    if len(family_parts) != 3 or family_parts[0] != "family":
        raise ValueError(f"unexpected campaign family directory: {family_dir_name}")
    family = family_parts[2]
    return {
        "case_dir": case_dir,
        "family": family,
        "N": int(metadata["target_N"]),
        "arrays": arrays,
        "metrics": metrics,
        "completion": completion,
        "spacing_completion": spacing_completion,
        "metadata": metadata,
    }


def _inventory(source: Path) -> tuple[list[dict[str, Any]], list[int]]:
    config = _read_json(source / "campaign_manifest.json")["config"]
    target_sizes = [int(value) for value in config["target_detector_sizes"]]
    case_dirs = sorted(source.glob("family_*/wd_nonborn_01/N*"))
    cases = [_load_case(path) for path in case_dirs if path.is_dir()]
    if not cases:
        raise FileNotFoundError(f"no completed case directories under {source}")
    keys = [(str(case["family"]), int(case["N"])) for case in cases]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate family/size case in collection")
    task_markers = tuple(sorted((source / "tasks").glob("task_*/COMPLETE.json")))
    if len(task_markers) != len(cases):
        raise ValueError(
            f"found {len(cases)} cases but {len(task_markers)} task markers"
        )
    return cases, target_sizes


def build_figure(
    source: Path,
    output_dir: Path,
    *,
    dpi: int = 180,
) -> dict[str, Any]:
    cases, target_sizes = _inventory(source)
    families = sorted(
        {str(case["family"]) for case in cases},
        key=lambda family: next(
            int(path.name.split("_")[1])
            for path in source.glob(f"family_*_{family}")
        ),
    )
    sizes = sorted({int(case["N"]) for case in cases})
    expected = {(family, size) for family in families for size in sizes}
    actual = {(str(case["family"]), int(case["N"])) for case in cases}
    if actual != expected:
        raise ValueError(f"incomplete rectangular collection: {expected - actual}")
    lookup = {(str(case["family"]), int(case["N"])): case for case in cases}
    density_limits = {
        family: 1.06
        * max(
            float(np.max(lookup[(family, size)]["arrays"][key]))
            for size in sizes
            for key in ("p_theta", "p_pi_minus_theta", "wg_density", "wc_density")
        )
        for family in families
    }

    figure = plt.figure(
        figsize=(5.3 * len(sizes), 4.25 * len(families)),
        constrained_layout=False,
    )
    outer = figure.add_gridspec(
        len(families),
        len(sizes),
        left=0.075,
        right=0.985,
        bottom=0.055,
        top=0.925,
        wspace=0.16,
        hspace=0.25,
    )
    for row, family in enumerate(families):
        for column, size in enumerate(sizes):
            case = lookup[(family, size)]
            arrays = case["arrays"]
            metrics = case["metrics"]
            inner = outer[row, column].subgridspec(
                2, 1, height_ratios=(1.0, 0.92), hspace=0.13
            )
            axis_p = figure.add_subplot(inner[0, 0])
            axis_p.stairs(
                arrays["p_theta"],
                arrays["edges"],
                color=BLUE,
                linewidth=0.9,
                fill=True,
                alpha=0.20,
                label=r"$P(\theta)$",
            )
            axis_p.stairs(
                arrays["p_pi_minus_theta"],
                arrays["edges"],
                color=RED,
                linewidth=0.85,
                fill=True,
                alpha=0.14,
                label=r"$P(\pi-\theta)$",
            )
            axis_p.plot(
                arrays["fit_grid"],
                arrays["wg_density"],
                color=MODEL_BLUE,
                linewidth=0.9,
                label="WG",
            )
            axis_p.plot(
                arrays["fit_grid"],
                arrays["wc_density"],
                color=MODEL_ORANGE,
                linewidth=0.9,
                linestyle="--",
                label="WC",
            )
            axis_p.set_xlim(0.0, np.pi)
            axis_p.set_ylim(0.0, density_limits[family])
            axis_p.tick_params(labelbottom=False, labelsize=7.5)
            axis_p.grid(alpha=0.16)
            axis_p.set_ylabel("density" if column == 0 else "", fontsize=8.5)
            axis_p.set_title(
                f"{FAMILY_LABELS.get(family, family)} — N={size}",
                fontsize=10.5,
                fontweight="bold",
            )
            if row == 0 and column == 0:
                axis_p.legend(ncol=2, frameon=False, fontsize=7.0)

            axis_r = figure.add_subplot(inner[1, 0])
            occupied = arrays["R_occupied"].astype(bool)
            axis_r.plot(
                arrays["centers"][occupied],
                arrays["R"][occupied],
                "o-",
                color=RATIO,
                markersize=2.1,
                linewidth=0.75,
                label=r"$R(\theta)$",
            )
            axis_r.plot(
                arrays["centers"],
                arrays["R_born"],
                color="black",
                linestyle="--",
                linewidth=1.0,
                label=r"$\cos^2(\theta/2)$",
            )
            axis_r.set_xlim(0.0, np.pi)
            axis_r.set_ylim(-0.04, 1.04)
            axis_r.set_xticks(
                (0.0, np.pi / 2.0, np.pi),
                ("0", r"$\pi/2$", r"$\pi$"),
            )
            axis_r.set_xlabel(r"$\theta$", fontsize=8.5)
            axis_r.set_ylabel(r"$R(\theta)$" if column == 0 else "", fontsize=8.5)
            axis_r.tick_params(labelsize=7.5)
            axis_r.grid(alpha=0.16)
            axis_r.text(
                0.035,
                0.08,
                rf"$S_{{\rm Born}}={float(metrics['S_born']):.3f}$"
                + "\n"
                + rf"RMSE$={float(metrics['born_RMSE_occupied']):.3f}$",
                transform=axis_r.transAxes,
                fontsize=7.5,
                va="bottom",
                bbox={
                    "facecolor": "white",
                    "edgecolor": "none",
                    "alpha": 0.78,
                    "pad": 0.8,
                },
            )
            if row == 0 and column == 0:
                axis_r.legend(frameon=False, fontsize=7.2, loc="upper right")

    missing_sizes = sorted(set(target_sizes) - set(sizes))
    status = (
        f"partial collection; N={','.join(map(str, missing_sizes))} still running"
        if missing_sizes
        else "complete collection"
    )
    figure.suptitle(
        "WD-selected, non-Born network configurations: dynamics diagnostics\n"
        + f"completed detector sizes N={','.join(map(str, sizes))} ({status})",
        fontsize=14.0,
        fontweight="bold",
        y=0.985,
    )
    output_dir.mkdir(parents=True, exist_ok=False)
    figure_path = output_dir / "network_wd_nonborn_diagnostics.png"
    temporary = figure_path.with_name(figure_path.stem + f".tmp.{os.getpid()}.png")
    figure.savefig(temporary, dpi=dpi, facecolor="white")
    plt.close(figure)
    temporary.replace(figure_path)

    metadata_path = output_dir / "provenance.json"
    _atomic_json(
        metadata_path,
        {
            "schema_version": 1,
            "created": timestamp(),
            "source_collection": _repo_relative(source),
            "source_submission": (source / "submitted_jobs.txt").read_text().strip(),
            "figure": _repo_relative(figure_path),
            "figure_sha256": _sha256(figure_path),
            "plot_script": _repo_relative(Path(__file__)),
            "plot_script_sha256": _sha256(Path(__file__)),
            "collection_status": status,
            "completed_sizes": sizes,
            "missing_target_sizes": missing_sizes,
            "families": families,
            "validated_case_count": len(cases),
            "validation": (
                "Every dynamics and detector-spacing completion marker was "
                "complete; every marker-listed artifact hash matched; every "
                "scientific validation.json passed."
            ),
            "cases": [
                {
                    "family": case["family"],
                    "N": case["N"],
                    "case_dir": _repo_relative(case["case_dir"]),
                    "S_born": float(case["metrics"]["S_born"]),
                    "born_RMSE_occupied": float(
                        case["metrics"]["born_RMSE_occupied"]
                    ),
                }
                for case in cases
            ],
        },
    )
    return {
        "figure": str(figure_path.resolve()),
        "metadata": str(metadata_path.resolve()),
        "case_count": len(cases),
        "completed_sizes": sizes,
        "missing_target_sizes": missing_sizes,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source", type=Path, required=True)
    result.add_argument("--output-dir", type=Path, required=True)
    result.add_argument("--dpi", type=int, default=180)
    return result


def main() -> None:
    args = parser().parse_args()
    outcome = build_figure(
        args.source.resolve(),
        args.output_dir.resolve(),
        dpi=args.dpi,
    )
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()
