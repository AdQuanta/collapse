"""Generate detector pair-gap matrices for three anisotropic dynamical regimes."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.anisotropic_sweep import AnisotropicCase, AnisotropicRepository  # noqa: E402
from core.detector_gap_matrix import (  # noqa: E402
    DetectorGapMatrixAnalyzer,
    DetectorGapMatrixPlotter,
    GapMatrixCase,
)


REPRESENTATIVES = (
    ("heavy_born", "heavy-tailed and Born-like", 0.01, 0.75, 0.5),
    ("heavy_not_born", r"heavy-tailed, not Born-like ($h_z=2J$)", 2.0, 1.0, 0.0),
    ("wrapped_gaussian_control", "non-heavy non-Born control", 1.0, 0.25, 0.0),
)


def _metric_rows(path: Path, dynamics_n: int) -> dict[tuple[float, float, float], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            (float(row["hz"]), float(row["J"]), float(row["Jpm"])): row
            for row in csv.DictReader(handle)
            if int(row["detector_n"]) == dynamics_n
        }


def _case(key: str, regime: str, detector_n: int, dynamics_n: int, evolution_time: float, row: dict[str, str]) -> GapMatrixCase:
    return GapMatrixCase(
        key=key,
        regime=regime,
        detector_n=detector_n,
        hz=float(row["hz"]),
        j=float(row["J"]),
        jpm=float(row["Jpm"]),
        evolution_time=evolution_time,
        collective_jx=0.01,
        dynamics_n=dynamics_n,
        born_score=float(row["S_born"]),
        born_rmse=float(row["born_rmse"]),
        angular_coverage=float(row["angular_bin_coverage"]),
        power_law_alpha=float(row["theta_power_law_alpha"]),
        power_law_js=float(row["theta_power_law_js"]),
        power_law_log10_span=float(row["theta_power_law_log10_span"]),
        wrapped_gaussian_js=float(row["wrapped_gaussian_js"]),
    )


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _diagnostic_montage(cases: list[GapMatrixCase], repository: AnisotropicRepository, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, len(cases), figsize=(15.0, 5.2))
    for axis, item in zip(axes, cases, strict=True):
        source_case = AnisotropicCase(
            detector_n=item.dynamics_n,
            hz=item.hz,
            j=item.j,
            jpm=item.jpm,
            evolution_time=item.evolution_time,
            jx=0.01,
            hz0=0.0,
        )
        image_path = repository.figure_path(source_case)
        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        axis.imshow(plt.imread(image_path))
        axis.axis("off")
        axis.set_title(
            f"{item.regime}\n"
            rf"$h_z={item.hz:g}, J={item.j:g}, J_{{\pm}}={item.jpm:g}$; "
            rf"$S_{{\rm Born}}={item.born_score:.3f}, \alpha={item.power_law_alpha:.3f}$",
            fontsize=9.5,
        )
    figure.suptitle(r"N=14 dynamical evidence used to label the detector-gap cases", fontsize=13)
    figure.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.88, wspace=0.04)
    figure.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detector-n", type=int, default=8)
    parser.add_argument("--dynamics-n", type=int, default=14)
    parser.add_argument("--time", type=float, default=1.0e6)
    parser.add_argument(
        "--metrics",
        type=Path,
        default=ROOT / "reports" / "anisotropic_parameter_study_2026-07-21" / "data" / "spectrum_metrics.csv",
    )
    parser.add_argument(
        "--campaign-root",
        type=Path,
        default=ROOT / "work" / "zeus_single_pixel_anisotropic_20260718_130606",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "detector_gap_matrix_study_2026-07-21",
    )
    args = parser.parse_args()

    metrics = _metric_rows(args.metrics, args.dynamics_n)
    cases: list[GapMatrixCase] = []
    for key, regime, hz, j, jpm in REPRESENTATIVES:
        row = metrics.get((hz, j, jpm))
        if row is None:
            raise KeyError(f"missing N={args.dynamics_n} metrics for {(hz, j, jpm)}")
        cases.append(_case(key, regime, args.detector_n, args.dynamics_n, args.time, row))

    analyzer = DetectorGapMatrixAnalyzer()
    results = [analyzer.analyze(case) for case in cases]
    figure_root = args.output / "figures"
    data_root = args.output / "data"
    comparison = DetectorGapMatrixPlotter().plot_comparison(results, figure_root / "detector_pair_gap_comparison.png")
    interaction = DetectorGapMatrixPlotter().plot_interaction_comparison(
        results,
        figure_root / "detector_interaction_matrix_comparison.png",
    )
    diagnostics = _diagnostic_montage(cases, AnisotropicRepository(args.campaign_root), figure_root / "regime_diagnostic_montage.png")
    summaries = [result.summary() for result in results]
    _write_csv(data_root / "detector_gap_summary.csv", summaries)
    for result in results:
        npz_path = data_root / f"{result.case.key}_gap_matrix.npz"
        import numpy as np

        np.savez_compressed(
            npz_path,
            energies=result.energies,
            signed_gaps=result.signed_gaps,
            energy_basis_coupling=result.energy_basis_coupling,
        )

    manifest = {
        "method": "full dense detector spectrum at N_D=8; sorted signed pair gaps delta_ab=E_a-E_b",
        "dynamics_source": "N=14, t=1e6 metrics and blue/red diagnostics from the transferred anisotropic campaign",
        "finite_time_window": "near-zero means |delta| <= max(1/t, 1e-9)",
        "heavy_definition": "resolved periodic power-law fit with alpha <= 2; Born gate follows the registered score/RMSE/coverage criteria",
        "interaction_basis": (
            "sorted numerical energy eigenbasis with each eigenvector phase fixed by making its largest "
            "computational-basis component real and non-negative; entries inside exactly degenerate "
            "energy blocks remain basis dependent"
        ),
        "figures": [
            str(comparison.relative_to(ROOT)),
            str(interaction.relative_to(ROOT)),
            str(diagnostics.relative_to(ROOT)),
        ],
        "data": [str((data_root / "detector_gap_summary.csv").relative_to(ROOT))]
        + [str((data_root / f"{result.case.key}_gap_matrix.npz").relative_to(ROOT)) for result in results],
        "cases": summaries,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
