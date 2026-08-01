"""Build an all-case detector-gap/diagnostic atlas for the N=14 campaign.

For every completed parameter triple in the transferred anisotropic campaign,
this script:

1. diagonalizes the detector Hamiltonian at the same N_D=8 used by the
   three-case ``vab_activation_brief_2026-07-22`` comparison;
2. saves the normalized minus-log pair-energy-gap heatmap; and
3. crops the existing N=14 dynamical diagnostic to retain only
   P(theta), P(pi-theta), and R(theta) versus the Born curve.

The expensive N=14 dynamics are never recomputed.  The workflow is
restartable and writes a LaTeX atlas with one readable page per case.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.anisotropic_sweep import AnisotropicCase, AnisotropicRepository  # noqa: E402
from collapse.detector_resonance import DenseRingDetectorBuilder, DetectorSpec  # noqa: E402


DEFAULT_CAMPAIGN = ROOT / "work" / "zeus_single_pixel_anisotropic_20260718_130606"
DEFAULT_METRICS = (
    ROOT
    / "reports"
    / "anisotropic_parameter_study_2026-07-21"
    / "data"
    / "spectrum_metrics.csv"
)
DEFAULT_OUTPUT = ROOT / "reports" / "vab_activation_all_cases_2026-07-27"
DEFAULT_TEX = DEFAULT_OUTPUT / "vab_activation_all_cases_2026-07-27.tex"


@dataclass(frozen=True)
class AtlasCase:
    """One detector configuration and its already-computed dynamical metrics."""

    ordinal: int
    total: int
    detector_n: int
    dynamics_n: int
    hz: float
    j: float
    jpm: float
    evolution_time: float
    born_score: float
    born_rmse: float
    angular_coverage: float
    power_law_alpha: float
    power_law_js: float
    power_law_log10_span: float
    source_diagnostic: str
    heatmap_output: str
    diagnostic_output: str

    @property
    def key(self) -> str:
        return f"hz={self.hz:g},J={self.j:g},Jpm={self.jpm:g}"


@dataclass(frozen=True)
class AtlasResult:
    """One completed, reusable atlas entry."""

    case: AtlasCase
    dimension: int
    bandwidth: float
    distinct_energies: int
    maximum_multiplicity: int
    minimum_nonzero_gap: float
    heatmap_sha256_pending: bool = True

    def row(self) -> dict[str, object]:
        output = asdict(self.case)
        output.update(
            {
                "dimension": self.dimension,
                "bandwidth": self.bandwidth,
                "distinct_energies": self.distinct_energies,
                "maximum_multiplicity": self.maximum_multiplicity,
                "minimum_nonzero_gap": self.minimum_nonzero_gap,
            }
        )
        output.pop("heatmap_sha256_pending", None)
        return output


def _float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value else float("nan")


def _multiplicities(energies: np.ndarray, tolerance: float) -> list[int]:
    groups: list[int] = []
    start = 0
    while start < energies.size:
        stop = start + 1
        while stop < energies.size and abs(float(energies[stop] - energies[start])) <= tolerance:
            stop += 1
        groups.append(stop - start)
        start = stop
    return groups


def _render_gap_heatmap(
    energies: np.ndarray,
    case: AtlasCase,
    output: Path,
    near_zero_decades: float,
) -> tuple[float, float]:
    """Render the brief-report minus-log heatmap with a physical bandwidth."""

    gaps = energies[:, None] - energies[None, :]
    bandwidth = max(float(np.ptp(energies)), np.finfo(float).eps)
    relative = np.abs(gaps) / bandwidth
    near = -np.log10(np.maximum(relative, 10.0 ** (-near_zero_decades)))
    np.fill_diagonal(near, np.nan)

    nonzero = np.abs(gaps[np.abs(gaps) > 1.0e-12])
    minimum_nonzero_gap = float(np.min(nonzero)) if nonzero.size else float("nan")

    cmap = plt.get_cmap("magma").copy()
    cmap.set_bad("#f7f7f7")
    figure, axis = plt.subplots(figsize=(6.6, 5.65))
    image = axis.imshow(
        near,
        origin="lower",
        interpolation="nearest",
        cmap=cmap,
        vmin=0.0,
        vmax=near_zero_decades,
        rasterized=True,
    )
    axis.set(
        xlabel="sorted detector-energy eigenstate index $b$",
        ylabel="sorted detector-energy eigenstate index $a$",
        title=(
            rf"$-\log_{{10}}(|E_a-E_b|/B)$, diagonal blank"
            "\n"
            rf"$h_z={case.hz:g},\ J={case.j:g},\ J_{{\pm}}={case.jpm:g}$; "
            rf"$N_D={case.detector_n},\ B=E_{{\max}}-E_{{\min}}$"
        ),
    )
    colorbar = figure.colorbar(image, ax=axis, fraction=0.047, pad=0.035)
    colorbar.set_label(r"$-\log_{10}(|E_a-E_b|/B)$")
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=185, bbox_inches="tight")
    plt.close(figure)
    return bandwidth, minimum_nonzero_gap


def _crop_diagnostic(source: Path, output: Path, retained_fraction: float) -> None:
    """Keep the two upper panels and remove the Bloch-sphere panel."""

    if not source.is_file():
        raise FileNotFoundError(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.load()
        stop = max(1, min(image.height, int(round(retained_fraction * image.height))))
        cropped = image.crop((0, 0, image.width, stop))
        cropped.save(output, format="PNG", optimize=True, compress_level=7)


def _analyze_case(
    case: AtlasCase,
    *,
    degeneracy_tolerance: float,
    near_zero_decades: float,
    retained_fraction: float,
    force: bool,
) -> AtlasResult:
    """Worker entry point: one small detector diagonalization and two assets."""

    heatmap = Path(case.heatmap_output)
    diagnostic = Path(case.diagnostic_output)
    source = Path(case.source_diagnostic)

    builder = DenseRingDetectorBuilder()
    operators = builder.build(DetectorSpec(case.detector_n, case.hz, case.j, case.jpm))
    energies = np.asarray(np.linalg.eigvalsh(operators.hamiltonian), dtype=float)
    if not np.all(np.diff(energies) >= -10.0 * np.finfo(float).eps):
        raise RuntimeError(f"eigenvalue ordering failed for {case.key}")

    if force or not heatmap.is_file():
        bandwidth, minimum_nonzero_gap = _render_gap_heatmap(
            energies,
            case,
            heatmap,
            near_zero_decades,
        )
    else:
        bandwidth = max(float(np.ptp(energies)), np.finfo(float).eps)
        gaps = np.abs(energies[:, None] - energies[None, :])
        nonzero = gaps[gaps > 1.0e-12]
        minimum_nonzero_gap = float(np.min(nonzero)) if nonzero.size else float("nan")

    if force or not diagnostic.is_file():
        _crop_diagnostic(source, diagnostic, retained_fraction)

    multiplicities = _multiplicities(energies, degeneracy_tolerance)
    return AtlasResult(
        case=case,
        dimension=int(energies.size),
        bandwidth=bandwidth,
        distinct_energies=len(multiplicities),
        maximum_multiplicity=max(multiplicities),
        minimum_nonzero_gap=minimum_nonzero_gap,
    )


def _load_cases(
    *,
    metrics_path: Path,
    campaign_root: Path,
    output_root: Path,
    detector_n: int,
    dynamics_n: int,
    evolution_time: float,
) -> list[AtlasCase]:
    repository = AnisotropicRepository(campaign_root)
    with metrics_path.open(newline="", encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if int(row["detector_n"]) == dynamics_n
            and math.isclose(float(row["evolution_time"]), evolution_time)
        ]
    rows.sort(key=lambda row: (float(row["hz"]), float(row["J"]), float(row["Jpm"])))
    if not rows:
        raise RuntimeError(f"no N={dynamics_n}, t={evolution_time:g} rows in {metrics_path}")

    cases: list[AtlasCase] = []
    for ordinal, row in enumerate(rows, start=1):
        dynamic_case = AnisotropicCase(
            detector_n=dynamics_n,
            hz=float(row["hz"]),
            j=float(row["J"]),
            jpm=float(row["Jpm"]),
            evolution_time=evolution_time,
            jx=float(row["Jx"]),
            hz0=float(row["hz0"]),
        )
        relative = repository.case_relative_dir(dynamic_case)
        cases.append(
            AtlasCase(
                ordinal=ordinal,
                total=len(rows),
                detector_n=detector_n,
                dynamics_n=dynamics_n,
                hz=dynamic_case.hz,
                j=dynamic_case.j,
                jpm=dynamic_case.jpm,
                evolution_time=evolution_time,
                born_score=_float(row, "S_born"),
                born_rmse=_float(row, "born_rmse"),
                angular_coverage=_float(row, "angular_bin_coverage"),
                power_law_alpha=_float(row, "theta_power_law_alpha"),
                power_law_js=_float(row, "theta_power_law_js"),
                power_law_log10_span=_float(row, "theta_power_law_log10_span"),
                source_diagnostic=str(repository.figure_path(dynamic_case).resolve()),
                heatmap_output=str((output_root / "figures" / relative / "energy_gap_minus_log.png").resolve()),
                diagnostic_output=str((output_root / "figures" / relative / "diagnostic_P_and_R.png").resolve()),
            )
        )
    missing = [case.source_diagnostic for case in cases if not Path(case.source_diagnostic).is_file()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} source diagnostics are missing; first: {missing[0]}")
    return cases


def _write_csv(path: Path, results: Iterable[AtlasResult]) -> None:
    rows = [result.row() for result in results]
    if not rows:
        raise ValueError("results must not be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _tex_path(path: str | Path) -> str:
    return Path(path).resolve().relative_to(ROOT).as_posix()


def _fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = min(width / image.width, height / image.height)
    size = (
        max(1, int(round(scale * image.width))),
        max(1, int(round(scale * image.height))),
    )
    return image.resize(size, Image.Resampling.LANCZOS)


def _contact_sheets(
    results: list[AtlasResult],
    output_root: Path,
    *,
    cases_per_page: int = 24,
    columns: int = 4,
) -> list[Path]:
    """Compose 24 labeled case pairs on each high-resolution A4 page."""

    rows = cases_per_page // columns
    if rows * columns != cases_per_page:
        raise ValueError("cases_per_page must be divisible by columns")
    sheet_root = output_root / "figures" / "contact_sheets"
    sheet_root.mkdir(parents=True, exist_ok=True)
    width, height = 3508, 2480  # A4 landscape at 300 dpi.
    margin_x, margin_y, header_h = 28, 24, 42
    tile_w = (width - 2 * margin_x) // columns
    tile_h = (height - 2 * margin_y - header_h) // rows
    font_path = font_manager.findfont("DejaVu Sans")
    header_font = ImageFont.truetype(font_path, 25)
    title_font = ImageFont.truetype(font_path, 18)
    sheets: list[Path] = []

    for page_index, start in enumerate(range(0, len(results), cases_per_page), start=1):
        page_results = results[start : start + cases_per_page]
        canvas = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(canvas)
        heading = (
            f"Cases {page_results[0].case.ordinal}-{page_results[-1].case.ordinal} "
            f"of {len(results)}: left = -log10 energy-gap heatmap; "
            "right = P(theta), P(pi-theta), and R(theta) vs Born"
        )
        draw.text((margin_x, 5), heading, fill="#111827", font=header_font)

        for local_index, result in enumerate(page_results):
            row, column = divmod(local_index, columns)
            x0 = margin_x + column * tile_w
            y0 = margin_y + header_h + row * tile_h
            x1 = x0 + tile_w - 5
            y1 = y0 + tile_h - 5
            draw.rectangle((x0, y0, x1, y1), outline="#cbd5e1", width=2)
            case = result.case
            title = (
                f"#{case.ordinal}  hz={case.hz:g}, J={case.j:g}, Jpm={case.jpm:g}; "
                f"S_B={case.born_score:.3f}, alpha={case.power_law_alpha:.3f}"
            )
            draw.text((x0 + 7, y0 + 3), title, fill="#111827", font=title_font)

            image_top = y0 + 28
            image_height = tile_h - 36
            gap = 8
            box_width = (tile_w - 3 * gap) // 2
            with Image.open(case.heatmap_output) as source:
                heatmap = _fit_image(source.convert("RGB"), box_width, image_height)
            with Image.open(case.diagnostic_output) as source:
                diagnostic = _fit_image(source.convert("RGB"), box_width, image_height)
            heat_x = x0 + gap + (box_width - heatmap.width) // 2
            diag_x = x0 + 2 * gap + box_width + (box_width - diagnostic.width) // 2
            canvas.paste(heatmap, (heat_x, image_top + (image_height - heatmap.height) // 2))
            canvas.paste(diagnostic, (diag_x, image_top + (image_height - diagnostic.height) // 2))

        path = sheet_root / (
            f"page_{page_index:02d}_cases_{page_results[0].case.ordinal:03d}_"
            f"{page_results[-1].case.ordinal:03d}.png"
        )
        canvas.save(path, format="PNG", optimize=True, compress_level=7, dpi=(300, 300))
        sheets.append(path)
    return sheets


def _write_latex(path: Path, results: list[AtlasResult], sheets: list[Path]) -> None:
    """Write a compact figure-only atlas capped below 40 pages."""

    lines = [
        r"\documentclass[10pt]{article}",
        r"\usepackage[a4paper,landscape,margin=0.24in,headheight=12pt,headsep=4pt,footskip=12pt]{geometry}",
        r"\usepackage{amsmath,graphicx,xcolor,microtype,fancyhdr,hyperref}",
        r"\hypersetup{colorlinks=true,linkcolor=blue!55!black,urlcolor=blue!55!black}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\parskip}{0pt}",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\fancyhead[L]{\footnotesize All-case detector energy-gap atlas}",
        r"\fancyhead[R]{\footnotesize $N_D=8$ spectra; $N=14$, $t=10^6$ dynamics}",
        r"\cfoot{\footnotesize\thepage}",
        r"\begin{document}",
        r"\begin{center}",
        r"{\LARGE\bfseries Detector energy-gap heatmaps and dynamical diagnostics}\\[0.4em]",
        r"{\large All 880 anisotropic single-pixel configurations}\\[0.6em]",
        r"{\small Generated 27 July 2026}",
        r"\end{center}",
        r"\vspace{1em}",
        (
            r"For each parameter triple $(h_z,J,J_{\pm})$, the left figure shows "
            r"$-\log_{10}(|E_a-E_b|/B)$ for the fully diagonalized $N_D=8$ detector, "
            r"where $B=E_{\max}-E_{\min}$ and the trivial diagonal is blank. "
            r"The right figure is the existing $N=14$, $t=10^6$ diagnostic cropped "
            r"to retain only the blue/red $P(\theta)$ and $P(\pi-\theta)$ histograms "
            r"and $R(\theta)$ versus the Born curve $\cos^2(\theta/2)$. "
            r"No $N=14$ dynamics were recomputed."
        ),
        r"\vspace{0.7em}",
        (
            r"The common Hamiltonian parameters are $J_x=0.01$, $h_{z0}=0$, "
            r"and the physical central-detector edge coupling is $J_x/\sqrt N$. "
            r"Heatmaps use the same $N_D=8$ convention as "
            r"\texttt{vab\_activation\_brief\_2026-07-22}."
        ),
        r"\vfill",
        r"\begin{center}\fcolorbox{blue!60!black}{blue!4}{\begin{minipage}{0.88\linewidth}",
        r"\textbf{Reading guide.} Brighter heatmap pixels mean smaller normalized energy gaps. "
        r"The color scale is clipped at 12 decades. Cases are ordered by $h_z$, then $J$, "
        r"then $J_{\pm}$. Each tile places the energy-gap heatmap "
        r"on the left and the cropped $P(\theta)$/$R(\theta)$ diagnostic on the right. "
        r"Zoom the vector PDF when inspecting fine plot labels.",
        r"\end{minipage}}\end{center}",
    ]
    for sheet in sheets:
        lines.extend(
            [
                r"\clearpage",
                r"\begin{center}",
                (
                    rf"\includegraphics[width=\textwidth,height=0.92\textheight,"
                    rf"keepaspectratio]{{{_tex_path(sheet)}}}"
                ),
                r"\end{center}",
            ]
        )
    lines.append(r"\end{document}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _result_from_row(row: dict[str, str]) -> AtlasResult:
    case_fields = {field: row[field] for field in AtlasCase.__dataclass_fields__}
    integer_fields = {"ordinal", "total", "detector_n", "dynamics_n"}
    string_fields = {"source_diagnostic", "heatmap_output", "diagnostic_output"}
    for key in integer_fields:
        case_fields[key] = int(case_fields[key])
    for key in set(case_fields) - integer_fields - string_fields:
        case_fields[key] = float(case_fields[key])
    case = AtlasCase(**case_fields)
    return AtlasResult(
        case=case,
        dimension=int(row["dimension"]),
        bandwidth=float(row["bandwidth"]),
        distinct_energies=int(row["distinct_energies"]),
        maximum_multiplicity=int(row["maximum_multiplicity"]),
        minimum_nonzero_gap=float(row["minimum_nonzero_gap"]),
    )


def _load_checkpoint(path: Path) -> dict[str, AtlasResult]:
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        results = [_result_from_row(row) for row in csv.DictReader(handle)]
    return {result.case.key: result for result in results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detector-n", type=int, default=8)
    parser.add_argument("--dynamics-n", type=int, default=14)
    parser.add_argument("--time", type=float, default=1.0e6)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--campaign-root", type=Path, default=DEFAULT_CAMPAIGN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tex", type=Path, default=DEFAULT_TEX)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--degeneracy-tolerance", type=float, default=1.0e-9)
    parser.add_argument("--near-zero-decades", type=float, default=12.0)
    parser.add_argument("--diagnostic-retained-fraction", type=float, default=0.625)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="Optional smoke-test case limit.")
    args = parser.parse_args()

    started = time.perf_counter()
    cases = _load_cases(
        metrics_path=args.metrics,
        campaign_root=args.campaign_root,
        output_root=args.output,
        detector_n=args.detector_n,
        dynamics_n=args.dynamics_n,
        evolution_time=args.time,
    )
    if args.limit is not None:
        cases = cases[: args.limit]
    checkpoint_path = args.output / "data" / "atlas_cases.csv"
    checkpoint = {} if args.force else _load_checkpoint(checkpoint_path)
    results: dict[str, AtlasResult] = {
        case.key: checkpoint[case.key]
        for case in cases
        if case.key in checkpoint
        and Path(checkpoint[case.key].case.heatmap_output).is_file()
        and Path(checkpoint[case.key].case.diagnostic_output).is_file()
    }
    pending = [case for case in cases if case.key not in results]

    print(
        f"[{datetime.now().astimezone().isoformat()}] "
        f"cases={len(cases)} reused={len(results)} pending={len(pending)} workers={args.workers}",
        flush=True,
    )
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                _analyze_case,
                case,
                degeneracy_tolerance=args.degeneracy_tolerance,
                near_zero_decades=args.near_zero_decades,
                retained_fraction=args.diagnostic_retained_fraction,
                force=args.force,
            ): case
            for case in pending
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            case = futures[future]
            result = future.result()
            results[case.key] = result
            ordered = [results[item.key] for item in cases if item.key in results]
            _write_csv(checkpoint_path, ordered)
            print(
                f"[{datetime.now().astimezone().isoformat()}] "
                f"completed={completed}/{len(pending)} case={case.key}",
                flush=True,
            )

    ordered_results = [results[case.key] for case in cases]
    _write_csv(checkpoint_path, ordered_results)
    sheets = _contact_sheets(ordered_results, args.output)
    _write_latex(args.tex, ordered_results, sheets)
    elapsed = time.perf_counter() - started
    manifest = {
        "created_at": datetime.now().astimezone().isoformat(),
        "case_count": len(ordered_results),
        "detector_n": args.detector_n,
        "dynamics_n": args.dynamics_n,
        "evolution_time": args.time,
        "workers": args.workers,
        "degeneracy_tolerance": args.degeneracy_tolerance,
        "near_zero_decades": args.near_zero_decades,
        "diagnostic_retained_fraction": args.diagnostic_retained_fraction,
        "elapsed_seconds": elapsed,
        "source_metrics": _tex_path(args.metrics),
        "source_campaign": _tex_path(args.campaign_root),
        "latex": _tex_path(args.tex),
        "checkpoint_csv": _tex_path(checkpoint_path),
        "contact_sheet_count": len(sheets),
        "expected_pdf_pages": 1 + len(sheets),
        "contact_sheets": [_tex_path(path) for path in sheets],
        "heatmap_definition": "-log10(max(|Ea-Eb|/(Emax-Emin),1e-12)); diagonal blank",
        "diagnostic_definition": "top 62.5% of the existing blue/red diagnostic; Bloch panel excluded",
        "dynamics_recomputed": False,
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
