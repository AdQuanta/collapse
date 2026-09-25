"""Bloch-sphere point clouds for an endpoint chain, several h_0 directions.

Ad hoc exploratory visualization, not a campaign result: rotates `h_0` over
several directions at fixed `|h_0|` on a chosen `SPEC.md` section 9.2/10.1
endpoint-chain cell (`connectivity="chain"`, `central_coupling="first"`), and
plots each direction's outcome-0/outcome-1 root clouds (blue/red, matching
`scripts/plot_preferred_basis_bloch_sphere.py`'s house colors) at every one of
the six frozen evolution times, with the light three-great-circle sphere
contour (no wireframe grid, no filled surface).

Two families are built in:

- ``--family xxz``: the section 10.1 tier-3 XXZ cell from
  `wiki/campaigns/chain-born-regions.md` (`Delta = J_zz / J_xx = 0.5`,
  `J_xx = J_yy = 2.0`, `J_zz = 1.0`).
- ``--family xyz``: the general (fully anisotropic) XYZ `screen_00` cell from
  the same page (`J_xx=1.32, J_yy=2.53, J_zz=1.10`), the preferred-basis
  campaign's own region center.

Both hold every non-`h_0` parameter fixed at the family's cell and only
rotate `h_0`'s direction; no perturbative-ratio gate is applied here (unlike
the frozen preferred-basis campaign evaluator) -- this is a picture, not a
certified WP5 measurement.

Usage::

    python scripts/plot_h0_directions_bloch_sphere.py --family xyz --n-pixel 8
"""

from __future__ import annotations

import argparse
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

from eval_chain_born import ChainConfig  # noqa: E402
from eval_preferred_basis import TIMES, pooled_outcome_clouds  # noqa: E402
from core.outcome_measures import preferred_axis_from_cloud  # noqa: E402
from plot_preferred_basis_bloch_sphere import _scatter_panel  # noqa: E402

#: `wiki/campaigns/chain-born-regions.md`'s best XXZ cell (Delta = 0.5):
#: J_xx = J_yy = J_perp = 2.0, J_zz = Delta * J_perp = 1.0. h_0 magnitude is
#: the cell's own h0x=h0y=h0z=1.
XXZ_FIXED = dict(Jxx=2.0, Jyy=2.0, Jzz=1.0, hx=1.4, hy=0.0, hz=1.0, gx=0.0, gy=0.0, gz=0.1)
XXZ_H0_MAGNITUDE = float(np.linalg.norm([1.0, 1.0, 1.0]))

#: The general XYZ `screen_00` region center. h_0 magnitude is the cell's own
#: |h_0| = 2.9527.
XYZ_FIXED = dict(Jxx=1.32, Jyy=2.53, Jzz=1.10, hx=-1.34, hy=0.0, hz=1.00,
                  gx=0.10, gy=0.05, gz=0.06)
XYZ_H0_MAGNITUDE = float(np.linalg.norm([-1.35, -1.69, 2.01]))

FAMILIES: dict[str, dict] = {
    "xxz": dict(label="XXZ endpoint chain (Delta=0.5)", fixed=XXZ_FIXED,
                h0_magnitude=XXZ_H0_MAGNITUDE, out_dir="xxz_h0_directions"),
    "xyz": dict(label="general XYZ endpoint chain (screen_00 cell)", fixed=XYZ_FIXED,
                h0_magnitude=XYZ_H0_MAGNITUDE, out_dir="xyz_h0_directions"),
}

DIRECTIONS: dict[str, np.ndarray] = {
    "x": np.array([1.0, 0.0, 0.0]),
    "y": np.array([0.0, 1.0, 0.0]),
    "z": np.array([0.0, 0.0, 1.0]),
    "(1,1,1)": np.array([1.0, 1.0, 1.0]) / np.sqrt(3.0),
    #: The zero vector: h0_magnitude * 0 = h0 = 0 regardless of magnitude, so
    #: this is the h0=0 control, not a fifth direction -- the fitted axis
    #: n_hat (plotted, as for every other case here) is then set by h/g alone.
    "zero": np.array([0.0, 0.0, 0.0]),
}


def _build_config(family_key: str, family: dict, name: str, direction: np.ndarray) -> ChainConfig:
    h0 = family["h0_magnitude"] * direction
    return ChainConfig(
        name=f"{family_key}_h0_{name}", hypothesis=f"{family['label']}: h_0 direction {name}",
        rung=f"{family_key}_h0_sweep",
        h0x=float(h0[0]), h0y=float(h0[1]), h0z=float(h0[2]), **family["fixed"],
    )


def _plot_direction(family_label: str, label: str, points_0_per_time: list[np.ndarray],
                     points_1_per_time: list[np.ndarray], times: np.ndarray,
                     n_hat: np.ndarray | None, out_path: Path, max_points: int) -> None:
    n_times = len(times)
    figure, axes = plt.subplots(2, 3, figsize=(10.2, 6.8), subplot_kw={"projection": "3d"})
    for index, axis in enumerate(axes.ravel()):
        if index >= n_times:
            axis.set_axis_off()
            continue
        _scatter_panel(
            axis, points_0_per_time[index], points_1_per_time[index], n_hat,
            elev=18.0, azim=-60.0, max_points=max_points, seed=index,
        )
        axis.set_title(f"t = {times[index]:.1f}  ({points_0_per_time[index].shape[0]} roots/label)",
                        fontsize=7.5, pad=-4.0)

    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
                  fontsize=7.5, bbox_to_anchor=(0.5, 0.015))
    figure.suptitle(f"{family_label}, $\\hat h_0 \\parallel$ {label}  (per evolution time)",
                     fontsize=10.0, y=0.98)
    figure.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.10, wspace=0.02, hspace=0.12)
    figure.savefig(out_path, dpi=220)
    plt.close(figure)
    print(f"[*] wrote {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=sorted(FAMILIES), default="xyz")
    parser.add_argument("--n-pixel", type=int, default=8)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--max-points", type=int, default=1200)
    args = parser.parse_args()

    family = FAMILIES[args.family]
    out_dir = args.out_dir or Path("reports/preferred_basis") / family["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    for label, direction in DIRECTIONS.items():
        config = _build_config(args.family, family, label, direction)
        pooled = pooled_outcome_clouds(config, args.n_pixel, TIMES, keep_per_time_points=True)
        axis_result = preferred_axis_from_cloud(pooled["points_0"], pooled["weights_0"])
        n_hat = axis_result.n_hat if axis_result.status == "ok" else None
        if n_hat is None:
            print(f"[*] h_0 || {label}: axis refused ({axis_result.refusal_reason})")
        else:
            print(f"[*] h_0 || {label}: B1={axis_result.B1:.4f}")

        safe_label = label.replace("(", "").replace(")", "").replace(",", "")
        out_path = out_dir / f"bloch_sphere_h0_{safe_label}.pdf"
        _plot_direction(
            family["label"], label, pooled["per_time_points_0"], pooled["per_time_points_1"],
            np.asarray(TIMES), n_hat, out_path, args.max_points,
        )


if __name__ == "__main__":
    main()
