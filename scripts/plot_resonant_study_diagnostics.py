"""Render saved resonance runs with the project's born_hamiltonian_search panels."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from core.born import diagnostics_from_radii
from scripts.born_hamiltonian_search import (
    _plot_theta_mirror_panel, _plot_ratio_panel, _plot_radius_tail_panel,
    _plot_phi_histogram_panel, _plot_bloch_sphere_panel,
    _plot_spectrum_histogram_panel, _plot_level_spacing_panel,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bins", type=int, default=48)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for case in sorted(args.root.glob("N*/hz_*")):
        aggregate = np.load(case / "aggregate.npz")
        full, detector = aggregate["full_spectrum"], aggregate["detector_spectrum"]
        raw_files = sorted(case.glob("raw_*.npz"), key=lambda item: float(item.stem.split("_t")[-1]))
        for raw_path in raw_files:
            raw = np.load(raw_path)
            eigenvalues = raw["eigenvalues"]
            radii = np.abs(eigenvalues)
            finite = radii[np.isfinite(radii)]
            fig = plt.figure(figsize=(18, 13), dpi=160)
            grid = fig.add_gridspec(3, 3)
            axes = [fig.add_subplot(grid[index // 3, index % 3]) for index in range(9)]
            axes[4].remove()
            axes[4] = fig.add_subplot(grid[1, 1], projection="3d")
            _plot_theta_mirror_panel(axes[0], finite, args.bins, 0.5)
            _plot_ratio_panel(axes[1], finite, args.bins, 0.5)
            _plot_radius_tail_panel(axes[2], finite, 0.1, 40)
            _plot_phi_histogram_panel(axes[3], eigenvalues, bins=24)
            _plot_bloch_sphere_panel(axes[4], eigenvalues, max_points=3000)
            _plot_spectrum_histogram_panel(axes[5], full, args.bins, "Full Hamiltonian spectrum")
            _plot_spectrum_histogram_panel(axes[6], detector, args.bins, "Detector spectrum")
            _plot_level_spacing_panel(axes[7], full, args.bins, "Full spacing (sector mixed)")
            _plot_level_spacing_panel(axes[8], detector, args.bins, "Detector spacing (sector mixed)")
            core = diagnostics_from_radii(finite, n_theta=100)
            fig.suptitle(
                f"Saved resonance diagnostic | {case.parent.name} {case.name} | "
                f"t={raw_path.stem.split('_t')[-1]} | S_Born={core.born_similarity:.4g}",
                fontsize=13,
            )
            fig.tight_layout(rect=(0, 0, 1, 0.96))
            fig.savefig(args.out / f"{case.parent.name}_{case.name}_{raw_path.stem}.png", bbox_inches="tight")
            plt.close(fig)


if __name__ == "__main__":
    main()
