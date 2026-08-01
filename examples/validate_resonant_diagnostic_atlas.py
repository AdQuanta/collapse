"""Validate the 2026-07-13 diagnostic-atlas extension and its deliverables."""

from __future__ import annotations

import csv
import json
import math
import re
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures" / "single_pixel_quspin_diagnostic_atlas_2026-07-13"
MANIFEST = FIGURES / "diagnostic_atlas_manifest.json"
METRICS = FIGURES / "N10_diagnostic_atlas_metrics.csv"
PDF = ROOT / "output" / "pdf" / "single_pixel_diagnostic_atlas_2026-07-13.pdf"
TEX = ROOT / "reports" / "single_pixel_diagnostic_atlas_2026-07-13.tex"
PPTX = ROOT / "presentations" / "single_pixel_diagnostic_atlas_2026-07-13.pptx"
NOTES = ROOT / "presentations" / "single_pixel_diagnostic_atlas_2026-07-13_speaker_notes.txt"
OUT = ROOT / "reports" / "single_pixel_diagnostic_atlas_validation_2026-07-13.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pdf_page_count(path: Path) -> int:
    try:
        from pypdf import PdfReader

        return len(PdfReader(path).pages)
    except ImportError:
        # Count leaf page dictionaries, excluding the /Pages tree node.
        data = path.read_bytes()
        return len(re.findall(rb"/Type\s*/Page(?!s)", data))


def pptx_slide_count(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        return sum(
            bool(re.fullmatch(r"ppt/slides/slide\d+\.xml", name))
            for name in archive.namelist()
        )


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["N"] == 10, "atlas must use the largest completed local N=10 run")
    require(manifest["hz"] == [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0], "unexpected hz grid")
    require(manifest["times"] == [1e3, 1e4, 1e5, 1e6], "unexpected requested-time grid")
    require(manifest["bins"] == 48, "unexpected theta-bin count")
    source = Path(manifest["source"])
    require(source.is_dir(), "fresh N=10 source directory is missing")
    require("single_pixel_quspin_fresh_2026-07-12" in str(source), "manifest does not point to the fresh study")

    image_checks: dict[str, dict[str, int]] = {}
    for relative in [*manifest["atlases"], manifest["summary_heatmap"]]:
        path = ROOT / relative
        require(path.is_file() and path.stat().st_size > 100_000, f"missing or undersized figure: {path}")
        with Image.open(path) as image:
            width, height = image.size
        require(width >= 2400 and height >= 1000, f"figure resolution is too low: {path}")
        image_checks[path.name] = {"width": width, "height": height, "bytes": path.stat().st_size}

    with METRICS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 28, "metrics table must contain 4 times x 7 fields")
    require({float(row["t"]) for row in rows} == {1e3, 1e4, 1e5, 1e6}, "metrics times are incomplete")
    require({float(row["hz"]) for row in rows} == {-3, -2, -1, 0, 1, 2, 3}, "metrics hz values are incomplete")
    numeric_columns = [
        "S_born",
        "born_rmse",
        "condition_number",
        "phi_harmonic_2",
        "theory_variance",
        "fitted_variance",
        "wrapped_gaussian_l1",
        "angular_bin_coverage",
        "finite_eigenvalues",
    ]
    require(
        all(math.isfinite(float(row[column])) for row in rows for column in numeric_columns),
        "metrics contain non-finite values",
    )
    require(all(0 <= float(row["angular_bin_coverage"]) <= 1 for row in rows), "coverage is outside [0,1]")
    require(all(float(row["finite_eigenvalues"]) == 1024 for row in rows), "not all mapped eigenvalues are finite")
    resonant = [row for row in rows if float(row["hz"]) in {-2.0, 0.0, 2.0}]
    require(all(float(row["S_born"]) < 0 for row in resonant), "a resonant S_born is unexpectedly non-negative")
    require(
        min(float(row["phi_harmonic_2"]) for row in rows) >= 0.95,
        "azimuthal localization is weaker than the reported bound",
    )

    for path in (PDF, TEX, PPTX, NOTES):
        require(path.is_file() and path.stat().st_size > 0, f"missing deliverable: {path}")
    pages = pdf_page_count(PDF)
    slides = pptx_slide_count(PPTX)
    require(pages == 13, f"expected a 13-page report, found {pages}")
    require(slides == 16, f"expected a 16-slide deck, found {slides}")

    result = {
        "status": "passed",
        "source": str(source),
        "N": manifest["N"],
        "hz": manifest["hz"],
        "times": manifest["times"],
        "metric_rows": len(rows),
        "figures": image_checks,
        "pdf_pages": pages,
        "pptx_slides": slides,
        "minimum_phi_harmonic_2": min(float(row["phi_harmonic_2"]) for row in rows),
        "maximum_angular_bin_coverage": max(float(row["angular_bin_coverage"]) for row in rows),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
