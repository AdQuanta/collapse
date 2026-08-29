"""Diagnostic atlases for the J=0, plus-minus single-pixel detector.

The detector Hamiltonian is

    H_D = hz sum_i Z_i
          + Jpm sum_i (sigma_i^+ sigma_{i+1}^- + h.c.),

with ``hz0=0``, collective ``Jx=0.01``, and per-edge central coupling
``Jx/sqrt(N)``.  Five-point neighborhoods are sampled around
``hz=0,+/-Jpm,+/-2Jpm`` at the four requested late times.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.single_pixel_atlas import (
    NpzSpectrumRepository,
    PlusMinusSpectralVarianceProvider,
    QuSpinSectorBackend,
    RelativeSpectrumComputer,
    SinglePixelSpec,
    SweepRunner,
)
from scripts.plot_single_pixel_hz_resonance_atlas import (
    DEFAULT_OFFSETS,
    DEFAULT_TIMES,
    atlas_for_resonance,
    field_grid,
    summary_plot,
)


DEFAULT_CENTERS = (-2.0, -1.0, 0.0, 1.0, 2.0)


def raw_path(raw_root: Path, detector_n: int, hz: float, t: float) -> Path:
    return NpzSpectrumRepository(raw_root).sample_path(detector_n, hz, t)


def compute_sweep(
    raw_root: Path,
    *,
    detector_n: int,
    hz_values: tuple[float, ...],
    times: tuple[float, ...],
    hz0: float,
    j: float,
    jpm: float,
    jx: float,
    force: bool,
) -> None:
    spec = SinglePixelSpec(
        detector_n=detector_n,
        j=j,
        jpm=jpm,
        jx=jx,
        hz0=hz0,
    )
    repository = NpzSpectrumRepository(raw_root)
    computer = RelativeSpectrumComputer(
        QuSpinSectorBackend(),
        PlusMinusSpectralVarianceProvider(),
    )
    SweepRunner(computer, repository).run(spec, hz_values, times, force=force)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-out", type=Path, default=Path("work/single_pixel_jpm_hz_sweep_2026-07-14"))
    parser.add_argument("--fig-out", type=Path, default=Path("figures/single_pixel_jpm_hz_atlas_2026-07-14"))
    parser.add_argument("--N", type=int, default=10, dest="detector_n")
    parser.add_argument("--centers", type=float, nargs="+", default=DEFAULT_CENTERS)
    parser.add_argument("--offsets", type=float, nargs="+", default=DEFAULT_OFFSETS)
    parser.add_argument("--times", type=float, nargs="+", default=DEFAULT_TIMES)
    parser.add_argument("--hz0", type=float, default=0.0)
    parser.add_argument("--J", type=float, default=0.0, dest="j")
    parser.add_argument("--Jpm", type=float, default=1.0, dest="jpm")
    parser.add_argument(
        "--Jx",
        type=float,
        default=0.01,
        dest="jx",
        help="collective coupling; each X0 Xi edge uses Jx/sqrt(N)",
    )
    parser.add_argument("--bins", type=int, default=48)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.j != 0.0:
        raise ValueError("this requested plus-minus study fixes J=0")
    if args.jpm <= 0.0:
        raise ValueError("Jpm must be positive")
    centers = tuple(float(value) for value in args.centers)
    offsets = tuple(float(value) for value in args.offsets)
    times = tuple(float(value) for value in args.times)
    hz_values = field_grid(centers, offsets)
    if len(set(hz_values)) != len(hz_values):
        raise ValueError("center/offset grid contains duplicate h_z values")
    args.raw_out.mkdir(parents=True, exist_ok=True)
    args.fig_out.mkdir(parents=True, exist_ok=True)

    compute_sweep(
        args.raw_out,
        detector_n=args.detector_n,
        hz_values=hz_values,
        times=times,
        hz0=args.hz0,
        j=args.j,
        jpm=args.jpm,
        jx=args.jx,
        force=args.force,
    )

    records: list[dict[str, float]] = []
    atlas_paths: list[str] = []
    for time_value in times:
        for center in centers:
            path, atlas_records = atlas_for_resonance(
                args.raw_out,
                args.fig_out,
                detector_n=args.detector_n,
                center=center,
                offsets=offsets,
                time_value=time_value,
                hz0=args.hz0,
                j=args.j,
                jpm=args.jpm,
                jx=args.jx,
                bins=args.bins,
                exact_label="reference",
                filename_prefix="jpm_hz_atlas",
            )
            atlas_paths.append(str(path))
            records.extend(atlas_records)

    summary = summary_plot(
        args.fig_out,
        records,
        centers,
        offsets,
        times,
        args.detector_n,
        title=rf"Plus-minus detector field neighborhoods, $N={args.detector_n}$, $J=0$, $J_{{\pm}}={args.jpm:g}$, $h_{{z0}}=0$",
        filename=f"N{args.detector_n}_jpm_hz_summary.png",
    )
    metrics = args.fig_out / f"N{args.detector_n}_jpm_hz_metrics.csv"
    with metrics.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    manifest = {
        "raw_root": str(args.raw_out.resolve()),
        "figure_root": str(args.fig_out.resolve()),
        "detector_n": args.detector_n,
        "total_qubits": args.detector_n + 1,
        "hamiltonian": "hz0 Z0 + hz sum Zi + Jpm sum (sigma+_i sigma-_{i+1} + h.c.) + (Jx/sqrt(N)) X0 sum Xi",
        "overall_sign": "repository generators construct the negative of the displayed Hamiltonian; theta and R are invariant",
        "fixed_parameters": {
            "J": args.j,
            "Jpm": args.jpm,
            "Jx": args.jx,
            "Jx_edge": args.jx / math.sqrt(args.detector_n),
            "hz0": args.hz0,
            "connectivity": "ring",
            "central_coupling": "all",
        },
        "reference_centers": centers,
        "reference_roles": {
            "-2Jpm": "outside the free-fermion active band",
            "-Jpm": "lower band edge",
            "0": "inside the active band",
            "+Jpm": "upper band edge",
            "+2Jpm": "outside the free-fermion active band",
        },
        "offsets": offsets,
        "hz": hz_values,
        "times": times,
        "bins": args.bins,
        "wrapped_gaussian_reference": "no-fit exact finite-N spectral variance from Eq. (6.4) of reports/four_model_finite_time_eigenvalue_derivation_2026-07-10.md",
        "empirical_distribution_rendering": "stairs histograms for P(theta) and P(pi-theta)",
        "ratio_rendering": "occupied-bin points connected by lines",
        "atlases": atlas_paths,
        "summary_plot": str(summary),
        "metrics_csv": str(metrics),
    }
    (args.fig_out / "jpm_hz_atlas_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
