"""Analyze a completed anisotropic single-pixel Zeus parameter sweep."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.anisotropic_analysis import (  # noqa: E402
    CampaignInspector,
    MetricTableRepository,
    ParameterRegimeSummarizer,
    PowerLawRelationshipPlotter,
    SpectrumMetricCalculator,
    ThetaPowerLawHeatmapPlotter,
    completeness_payload,
    iter_expected_cases,
)
from core.anisotropic_sweep import AnisotropicRepository, AnisotropicSweepConfig  # noqa: E402


DEFAULT_CONFIG = Path("configs/zeus_single_pixel_anisotropic_j_jpm_hz_t1e6.json")
DEFAULT_RUN_ROOT = Path("work/zeus_single_pixel_anisotropic_20260718_130606")
DEFAULT_OUTPUT = Path("reports/anisotropic_parameter_study_2026-07-20")


def _calculate(arguments: tuple[str, int]) -> object:
    path, bins = arguments
    return SpectrumMetricCalculator(bins).calculate(Path(path))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Analyze existing spectra for development only; final studies must omit this flag.",
    )
    parser.add_argument("--inspect-only", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    config = AnisotropicSweepConfig.from_json(args.config)
    repository = AnisotropicRepository(args.run_root)
    completeness = CampaignInspector(repository, config).inspect_all()
    payload = completeness_payload(completeness)
    print(json.dumps(payload, indent=2), flush=True)
    if args.inspect_only:
        return
    if not payload["complete"] and not args.allow_incomplete:
        raise RuntimeError("campaign is incomplete; wait for every raw, metrics, figure, DONE, and aggregate file")

    cases = [case for case in iter_expected_cases(config) if repository.raw_path(case).is_file()]
    work = [(str(repository.raw_path(case)), args.bins) for case in cases]
    if not work:
        raise RuntimeError("no raw spectra are available")
    if args.workers <= 1:
        rows = [_calculate(item) for item in work]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(_calculate, work, chunksize=8))
    rows.sort(key=lambda row: (row.detector_n, row.hz, row.J, row.Jpm))

    data_root = args.output / "data"
    figure_root = args.output / "figures" / "theta_power_law_alpha_heatmaps"
    MetricTableRepository.write(data_root / "spectrum_metrics.csv", rows)
    plotter = ThetaPowerLawHeatmapPlotter()
    heatmaps: list[str] = []
    for detector_n in config.detector_sizes:
        for hz in config.hz_values:
            if any(row.detector_n == detector_n and row.hz == hz for row in rows):
                path = figure_root / f"theta_power_law_alpha_N{detector_n:02d}_hz_{hz:+g}.png"
                plotter.plot(rows, config.j_values, config.jpm_values, detector_n, hz, path)
                heatmaps.append(str(path))

    summary = ParameterRegimeSummarizer().summarize(rows)
    MetricTableRepository.write_dicts(data_root / "best_by_n_hz.csv", summary["best_by_n_hz"])
    MetricTableRepository.write_dicts(data_root / "spearman_correlations.csv", summary["spearman_correlations"])
    if summary["top_born"]:
        MetricTableRepository.write_dicts(data_root / "top_born_regimes.csv", summary["top_born"])
    if summary["top_wrapped_heavy"]:
        MetricTableRepository.write_dicts(data_root / "top_wrapped_heavy_regimes.csv", summary["top_wrapped_heavy"])
    (data_root / "regime_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    relationship_path = args.output / "figures" / "theta_power_law_alpha_vs_born.png"
    PowerLawRelationshipPlotter().plot(rows, relationship_path)

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(args.run_root.resolve()),
        "config": str(args.config.resolve()),
        "completeness": payload,
        "spectra_analyzed": len(rows),
        "bins": args.bins,
        "theta_definition": "theta = 2 arctan(abs(lambda)); recomputed from every raw spectrum",
        "theta_power_law_fit": (
            "P_b(alpha) proportional to width_b * max(d_2pi(theta_b,0), Delta/2)^(-alpha); "
            "alpha is fitted by multinomial maximum likelihood on the theta histogram"
        ),
        "metrics_csv": str(data_root / "spectrum_metrics.csv"),
        "regime_summary": str(data_root / "regime_summary.json"),
        "relationship_figure": str(relationship_path),
        "heatmaps": heatmaps,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "analysis_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"spectra_analyzed": len(rows), "heatmaps": len(heatmaps)}, indent=2))


if __name__ == "__main__":
    main()
