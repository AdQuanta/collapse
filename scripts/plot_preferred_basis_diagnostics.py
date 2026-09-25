"""Two-panel angular diagnostic for a preferred-basis campaign record.

Reuses the same ring-catalog plotters as
``scripts/plot_chain_born_region_diagnostics.py`` -- ``_plot_angular`` and
``_plot_ratio`` -- unmodified, rather than defining a new chart
(goal_preferred_basis.md section 7). The angle plotted is ``theta'``,
measured from the fitted preferred axis, not a lab-frame pole; see
``scripts/export_preferred_basis_profile.py`` for how the arrays were built.

``_plot_ratio``'s legacy text box prints ``S_Born`` and ``RMSE``; the values
underneath are ``B1`` and the occupied-bin RMSE against
``cos^2(theta'/2)`` respectively (adapted at this call site only, so the
reused function itself is untouched) -- both the figure caption and
``metadata.json`` disclose this substitution explicitly.

Usage::

    python scripts/plot_preferred_basis_diagnostics.py \
        --profile reports/preferred_basis/screen_00_N10
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

    legacy_record = {
        "S_born": metadata["B1"],
        "born_RMSE_occupied": metadata["occupied_bin_RMSE_vs_born"],
    }

    figure, axes = plt.subplots(
        2, 1, figsize=(4.6, 4.8), sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.0], "hspace": 0.08},
    )
    figure.subplots_adjust(left=0.155, right=0.975, top=0.935, bottom=0.165)
    _plot_angular(axes[0], arrays)
    axes[0].set_ylabel(r"$P(\theta')$")
    axes[0].legend(frameon=False, fontsize=6.5, loc="upper right")
    _plot_ratio(axes[1], arrays, legacy_record, show_legend=True)
    axes[1].set_xlabel(r"$\theta'$ (from fitted axis $\hat n$)", labelpad=1.5)
    axes[1].set_ylabel(r"$R(\theta')$")

    params = metadata["parameters"]
    active = " ".join(f"{k}={v:+.2f}" for k, v in params.items() if v != 0.0)
    figure.suptitle(f"{metadata['name']}  N={metadata['n_pixel']}", fontsize=8.0, y=0.98)
    figure.text(
        0.5, 0.012,
        active
        + f"\n{metadata['n_roots_0']} roots over 6 times in [100, 1000];"
        + f" B1={metadata['B1']:.4f}"
        + f"  axis err={metadata['axis_angle_deg_from_reference']:.3f} deg"
        + f"  odd($\\ell\\geq3$)={metadata['odd_harmonic_l3_l5_l7_leakage']:.4f}"
        + f"  cov(profile)={metadata['coverage_fraction_profile']:.2f};"
        + " legend box shows B1/RMSE(vs Born), not the histogram S_Born statistic",
        ha="center", va="bottom", fontsize=4.8,
    )
    figure.savefig(output, dpi=200)
    plt.close(figure)
    print(f"[*] wrote {output}")


if __name__ == "__main__":
    main()
