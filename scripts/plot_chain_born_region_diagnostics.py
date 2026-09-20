"""Two-panel angular diagnostic for a chain-Born region, in the house style.

Reuses the ring-catalog plotters rather than defining a new chart: `_plot_angular`
from `build_network_wd_nonborn_size_spacing_figures` for the stacked `P(theta)`
against `P(pi - theta)` panel with its wrapped-Gaussian and wrapped-Cauchy
overlays, and `_plot_ratio` from `plot_hz0_0_ring_spacing_born_catalog` for the
`R(theta)` panel against `cos^2(theta/2)` with the in-panel score box.

Plotting the reflected pair on one axis, rather than outcome 0 against outcome 1,
is what makes the reflection asymmetry legible, so the panel pairing is kept.

Usage::

    python scripts/plot_chain_born_region_diagnostics.py \
        --profile reports/chain_born_regions/screen_00
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from build_network_wd_nonborn_size_spacing_figures import _plot_angular  # noqa: E402
from plot_hz0_0_ring_spacing_born_catalog import _plot_ratio  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True,
                        help="Directory holding results.npz and metadata.json.")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    arrays = dict(np.load(args.profile / "results.npz"))
    metadata = json.loads((args.profile / "metadata.json").read_text(encoding="utf-8"))
    output = args.out or (args.profile / "diagnostics.pdf")

    # Explicit margins rather than tight_layout: the reused ring-catalog axes set
    # their own labels and tight_layout cannot place them without clipping.
    figure, axes = plt.subplots(
        2, 1, figsize=(4.6, 4.8), sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.0], "hspace": 0.08},
    )
    figure.subplots_adjust(left=0.155, right=0.975, top=0.935, bottom=0.165)
    _plot_angular(axes[0], arrays)
    axes[0].set_ylabel(r"$P(\theta)$")
    axes[0].legend(frameon=False, fontsize=6.5, loc="upper right")
    _plot_ratio(axes[1], arrays, metadata, show_legend=True)
    axes[1].set_xlabel(r"$\theta$", labelpad=1.5)

    params = metadata["parameters"]
    active = " ".join(
        f"{k}={v:+.2f}" for k, v in params.items() if v != 0.0
    )
    figure.suptitle(
        f"{metadata['name']}  N={metadata['n_pixel']}", fontsize=8.0, y=0.98
    )
    figure.text(
        0.5, 0.012,
        active
        + f"\n{metadata['n_roots']} roots over 6 times in [100, 1000]"
        + f";  $S_{{\\rm Born}}$ on {metadata['S_born_bins']} bins,"
        + f" $P$/$R$ on {metadata['profile_bins']} bins;"
        + f" coverage {metadata['coverage_bins_100']}/{metadata['S_born_bins']}",
        ha="center", va="bottom", fontsize=5.2,
    )
    figure.savefig(output, dpi=200)
    plt.close(figure)
    print(f"[*] wrote {output}")


if __name__ == "__main__":
    main()
