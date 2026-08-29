"""Render readable four-case panels from a completed relative-evolution study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from core.relative_evolution_study import angular_histogram
from scripts.build_relative_evolution_matrix_study import plot_histogram


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path)
    return parser.parse_args()


def render(path: Path, keys: list[str], histograms: dict, title: str) -> None:
    fig, axes = plt.subplots(4, 2, figsize=(10.5, 10.5), constrained_layout=True)
    for row, key in enumerate(keys):
        plot_histogram(axes[row, 0], axes[row, 1], histograms[key], key.replace("_", " "))
    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.savefig(path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    study = args.study.resolve()
    config = json.loads((study / "effective_configuration.json").read_text(encoding="utf-8"))
    keys = [item["key"] for item in config["cases"]]
    maximum_n = max(config["sizes"])
    average_n = config["time_average_n"]
    snapshot = {}
    average = {}
    for key in keys:
        with np.load(study / "data" / f"snapshot_{key}_N{maximum_n}.npz") as payload:
            snapshot[key] = angular_histogram(payload["theta"], bins=48)
        with np.load(study / "data" / f"time_average_{key}_N{average_n}.npz") as payload:
            average[key] = angular_histogram(payload["theta"], bins=48)
    halves = (keys[:4], keys[4:])
    for index, selected in enumerate(halves, start=1):
        render(
            study / "figures" / f"snapshot_diagnostics_part{index}.png",
            selected,
            snapshot,
            rf"Exact finite-$N$ projective spectra, $N={maximum_n}$, $t={config['snapshot_time']:g}$",
        )
        render(
            study / "figures" / f"time_average_diagnostics_part{index}.png",
            selected,
            average,
            rf"Finite-window averages, $N={average_n}$, $T={config['final_time']:g}$, {config['time_samples']} samples",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
