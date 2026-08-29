"""Build reproducible three-row assets for the Zeus-atlas Beamer deck.

Each output keeps one representative Hamiltonian point and all three
diagnostic rows: angular histograms, the connected Born ratio, and the Bloch
sphere.  Cropping is intentionally separate from the scientific plotters so
the presentation never recomputes or alters completed Zeus results.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "figures/zeus_single_pixel_atlas_presentation_2026-07-16"


@dataclass(frozen=True)
class CropSpec:
    """Describe a normalized crop of one atlas column."""

    source: Path
    destination: Path
    left: float
    right: float
    top: float = 0.045

    def validate(self) -> None:
        if not (0.0 <= self.left < self.right <= 1.0):
            raise ValueError(f"Invalid horizontal crop for {self.destination}: {self.left}, {self.right}")
        if not (0.0 <= self.top < 1.0):
            raise ValueError(f"Invalid top crop for {self.destination}: {self.top}")


def equal_column_spec(
    source: Path,
    destination: Path,
    column: int,
    columns: int,
    *,
    left_pad: float = 0.004,
    right_pad: float = 0.002,
) -> CropSpec:
    """Create a crop spec for one column in an equal-width atlas grid."""
    if not 0 <= column < columns:
        raise ValueError(f"column {column} is outside a {columns}-column atlas")
    left = 0.0 if column == 0 else column / columns + left_pad
    right = 1.0 if column == columns - 1 else (column + 1) / columns + right_pad
    return CropSpec(source=source, destination=destination, left=left, right=right)


HZ0_SOURCE = ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/figures/N16_hz0_diagnostic_atlas_t1e3.png"
HZ_RESONANCE_SOURCE = ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/hz_resonance/N15/figures/N15_hz_atlas_center_0_t1e3.png"
JPM_SOURCE = ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/jpm_coupling/N15/figures/N15_jpm_sweep_atlas_t1e3.png"
JPM_HZ_ROOT = ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/jpm_hz/N14/figures"
TWO_PIXEL_HZ0_SOURCE = ROOT / "figures/conjecture_two_pixel_comparison_2026-07-16/atlases/hz0_t1e6_page01.png"


SPECS: dict[str, CropSpec] = {
    "matched_hz0": CropSpec(
        source=ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/hz0/N16/figures/N16_hz0_diagnostic_atlas_t1e3.png",
        destination=OUTPUT_ROOT / "N16_matched_hz0_t1e3.png",
        left=0.435,
        right=0.575,
    ),
    "hz_resonance": CropSpec(
        source=ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/hz_resonance/N15/figures/N15_hz_atlas_center_0_t1e3.png",
        destination=OUTPUT_ROOT / "N15_hz_resonance_p0p01_t1e3.png",
        left=0.604,
        right=0.802,
    ),
    "jpm_coupling": CropSpec(
        source=ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/jpm_coupling/N15/figures/N15_jpm_sweep_atlas_t1e3.png",
        destination=OUTPUT_ROOT / "N15_jpm_1_t1e3.png",
        left=0.671,
        right=0.752,
    ),
    "jpm_hz": CropSpec(
        source=ROOT / "work/zeus_single_pixel_atlas_scaling_2026-07-14/jpm_hz/N14/figures/N14_jpm_hz_atlas_center_p1_t1e3.png",
        destination=OUTPUT_ROOT / "N14_jpm_hz_p1_t1e3.png",
        left=0.404,
        right=0.602,
    ),
    "hz0_0": equal_column_spec(HZ0_SOURCE, OUTPUT_ROOT / "N16_hz0_0_t1e3.png", 0, 7, left_pad=0.006, right_pad=0.004),
    "hz0_0p09": equal_column_spec(HZ0_SOURCE, OUTPUT_ROOT / "N16_hz0_0p09_t1e3.png", 2, 7, left_pad=0.006, right_pad=0.004),
    "hz0_0p1": equal_column_spec(HZ0_SOURCE, OUTPUT_ROOT / "N16_hz0_0p1_t1e3.png", 3, 7, left_pad=0.006, right_pad=0.004),
    "hz0_0p2": equal_column_spec(HZ0_SOURCE, OUTPUT_ROOT / "N16_hz0_0p2_t1e3.png", 6, 7, left_pad=0.006, right_pad=0.004),
    "hz_m0p05": equal_column_spec(HZ_RESONANCE_SOURCE, OUTPUT_ROOT / "N15_hz_m0p05_t1e3.png", 0, 5, left_pad=0.010, right_pad=0.0),
    "hz_m0p01": equal_column_spec(HZ_RESONANCE_SOURCE, OUTPUT_ROOT / "N15_hz_m0p01_t1e3.png", 1, 5, left_pad=0.010, right_pad=0.0),
    "hz_0": equal_column_spec(HZ_RESONANCE_SOURCE, OUTPUT_ROOT / "N15_hz_0_t1e3.png", 2, 5, left_pad=0.010, right_pad=0.0),
    "hz_p0p01": equal_column_spec(HZ_RESONANCE_SOURCE, OUTPUT_ROOT / "N15_hz_p0p01_t1e3.png", 3, 5, left_pad=0.010, right_pad=0.0),
    "jpm_0": equal_column_spec(JPM_SOURCE, OUTPUT_ROOT / "N15_jpm_0_t1e3.png", 0, 12, left_pad=0.005, right_pad=0.0),
    "jpm_0p1": equal_column_spec(JPM_SOURCE, OUTPUT_ROOT / "N15_jpm_0p1_t1e3.png", 4, 12, left_pad=0.005, right_pad=0.0),
    "jpm_1": equal_column_spec(JPM_SOURCE, OUTPUT_ROOT / "N15_jpm_1_range_t1e3.png", 8, 12, left_pad=0.005, right_pad=0.0),
    "jpm_2": equal_column_spec(JPM_SOURCE, OUTPUT_ROOT / "N15_jpm_2_t1e3.png", 10, 12, left_pad=0.005, right_pad=0.0),
    "jpm_hz_m2": equal_column_spec(JPM_HZ_ROOT / "N14_jpm_hz_atlas_center_m2_t1e3.png", OUTPUT_ROOT / "N14_jpm_hz_m2_t1e3.png", 2, 5, left_pad=0.010, right_pad=0.0),
    "jpm_hz_0": equal_column_spec(JPM_HZ_ROOT / "N14_jpm_hz_atlas_center_0_t1e3.png", OUTPUT_ROOT / "N14_jpm_hz_0_t1e3.png", 2, 5, left_pad=0.010, right_pad=0.0),
    "jpm_hz_p1": equal_column_spec(JPM_HZ_ROOT / "N14_jpm_hz_atlas_center_p1_t1e3.png", OUTPUT_ROOT / "N14_jpm_hz_p1_range_t1e3.png", 2, 5, left_pad=0.010, right_pad=0.0),
    "jpm_hz_p2": equal_column_spec(JPM_HZ_ROOT / "N14_jpm_hz_atlas_center_p2_t1e3.png", OUTPUT_ROOT / "N14_jpm_hz_p2_t1e3.png", 2, 5, left_pad=0.010, right_pad=0.0),
    "two_hz0_0p09": equal_column_spec(TWO_PIXEL_HZ0_SOURCE, OUTPUT_ROOT / "ND8_two_hz0_0p09_t1e6.png", 2, 5, left_pad=0.010, right_pad=0.0),
    "two_hz0_0p1": equal_column_spec(TWO_PIXEL_HZ0_SOURCE, OUTPUT_ROOT / "ND8_two_hz0_0p1_t1e6.png", 3, 5, left_pad=0.010, right_pad=0.0),
}

ROW_RANGES: dict[str, tuple[float, float]] = {
    "p": (0.0, 0.305),
    "r": (0.325, 0.61),
    "bloch": (0.67, 0.95),
}


def row_destination(column_destination: Path, row_name: str) -> Path:
    return column_destination.with_name(f"{column_destination.stem}_{row_name}.png")


def crop_diagnostic_rows(column_destination: Path) -> None:
    """Split a tall 3-row column into slide-readable P, R, and Bloch panels."""
    with Image.open(column_destination) as image:
        width, height = image.size
        for row_name, (top, bottom) in ROW_RANGES.items():
            row = image.crop((0, round(top * height), width, round(bottom * height)))
            row.save(
                row_destination(column_destination, row_name),
                dpi=image.info.get("dpi", (150, 150)),
            )


def crop_atlas_column(spec: CropSpec) -> None:
    """Crop one atlas column while retaining its three diagnostic rows."""
    spec.validate()
    if not spec.source.is_file():
        raise FileNotFoundError(spec.source)
    with Image.open(spec.source) as image:
        width, height = image.size
        crop_box = (
            round(spec.left * width),
            round(spec.top * height),
            round(spec.right * width),
            height,
        )
        cropped = image.crop(crop_box)
        spec.destination.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(spec.destination, dpi=image.info.get("dpi", (150, 150)))
    crop_diagnostic_rows(spec.destination)


def crop_matched_column(source: Path, destination: Path) -> None:
    """Backward-compatible entry point for the original matched-field crop."""
    base = SPECS["matched_hz0"]
    crop_atlas_column(
        CropSpec(source=source, destination=destination, left=base.left, right=base.right, top=base.top)
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        action="append",
        choices=tuple(SPECS),
        help="Build only the selected case; repeat for multiple cases. Default: all four.",
    )
    parser.add_argument("--source", type=Path, help="Legacy matched-field source override.")
    parser.add_argument("--output", type=Path, help="Legacy matched-field output override.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.source is not None or args.output is not None:
        base = SPECS["matched_hz0"]
        crop_matched_column(args.source or base.source, args.output or base.destination)
        return
    names = args.case or list(SPECS)
    for name in names:
        crop_atlas_column(SPECS[name])
        print(SPECS[name].destination)


if __name__ == "__main__":
    main()
