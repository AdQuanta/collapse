"""Bloch-sphere scatter of the two labelled outcome root clouds.

Companion to `scripts/plot_preferred_basis_diagnostics.py`'s polar-angle
panels: this shows the same two labelled sets (outcome 0 in blue, outcome 1
in red -- the same house colors `_plot_angular` uses for `P(theta)` and
`P(pi - theta)`) as points on the sphere itself, rather than folded into a
polar histogram. Outcome 1's points are the exact antipodal reflection of
outcome 0's (`core.outcome_measures.antipodal_bloch_cloud`), so the two
clouds are point-for-point antipodal by construction -- visible directly here
as the red cloud being the blue cloud's mirror image through the origin.

Points are plotted as genuine `mplot3d` 3D scatter (real depth, rotatable
view), with just enough sphere geometry to read as a sphere: the equator
plus one meridian ("main circle frame"), thin light-gray lines, no
latitude/longitude grid and no filled surface.

The fitted preferred axis n_hat (goal_preferred_basis.md's `B1` estimator) is
drawn as a diameter line for reference.

Usage::

    python scripts/plot_preferred_basis_bloch_sphere.py \
        --profile reports/preferred_basis/screen_00_N10
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers the '3d' projection)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]

BLUE = "#2389c9"
RED = "#e45756"


def _sphere_contour(axis) -> None:
    """Just enough geometry to read as a sphere: no lat/long grid, no filled
    surface -- the equator plus one meridian ("main circle frame") in thin
    light gray."""

    t = np.linspace(0.0, 2.0 * np.pi, 200)
    zero = np.zeros_like(t)
    circles = [
        (np.cos(t), np.sin(t), zero),   # xy-plane (equator)
        (np.cos(t), zero, np.sin(t)),   # xz-plane (frame meridian)
    ]
    for x, y, z in circles:
        axis.plot(x, y, z, color="0.75", linewidth=0.3, zorder=1)


def _scatter_panel(axis, points_0: np.ndarray, points_1: np.ndarray, n_hat: np.ndarray,
                    elev: float, azim: float, max_points: int, seed: int,
                    sphere_style: str = "contour",
                    axis_line_label: str = r"fitted axis $\hat n$") -> None:
    rng = np.random.default_rng(seed)

    def _thin(points: np.ndarray) -> np.ndarray:
        if points.shape[0] <= max_points:
            return points
        return points[rng.choice(points.shape[0], size=max_points, replace=False)]

    if sphere_style == "contour":
        _sphere_contour(axis)
    elif sphere_style != "none":
        raise ValueError(f"unknown sphere_style {sphere_style!r}")
    p0 = _thin(points_0)
    p1 = _thin(points_1)
    axis.scatter(p0[:, 0], p0[:, 1], p0[:, 2], s=2.5, color=BLUE, alpha=0.55,
                 linewidths=0.0, label=r"outcome 0 ($\rho_0$)", zorder=3)
    axis.scatter(p1[:, 0], p1[:, 1], p1[:, 2], s=2.5, color=RED, alpha=0.55,
                 linewidths=0.0, label=r"outcome 1 ($\rho_1$)", zorder=3)
    if n_hat is not None:
        axis.plot([-n_hat[0], n_hat[0]], [-n_hat[1], n_hat[1]], [-n_hat[2], n_hat[2]],
                  color="black", linewidth=1.3, zorder=4, label=axis_line_label)
    axis.set_box_aspect((1, 1, 1))
    axis.set_xlim(-1.05, 1.05)
    axis.set_ylim(-1.05, 1.05)
    axis.set_zlim(-1.05, 1.05)
    axis.set_axis_off()
    axis.view_init(elev=elev, azim=azim)


def _plot_pooled(arrays: dict, metadata: dict, output: Path, max_points: int) -> None:
    points_0 = arrays["points_0"]
    points_1 = arrays["points_1"]
    n_hat = arrays["n_hat"]

    figure = plt.figure(figsize=(7.6, 4.2))
    views = [("front", 18.0, -60.0), ("along $\\hat n$", 18.0, -60.0 + 90.0)]
    axes = [figure.add_subplot(1, 2, i + 1, projection="3d") for i in range(2)]
    for axis, (label, elev, azim) in zip(axes, views):
        _scatter_panel(axis, points_0, points_1, n_hat, elev, azim, max_points, seed=0)
        axis.set_title(label, fontsize=8.0, pad=-6.0)

    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
                  fontsize=7.0, bbox_to_anchor=(0.5, 0.045))

    params = metadata["parameters"]
    active = " ".join(f"{k}={v:+.2f}" for k, v in params.items() if v != 0.0)
    figure.suptitle(f"{metadata['name']}  N={metadata['n_pixel']}  (pooled over 6 times)",
                     fontsize=9.0, y=0.98)
    figure.text(
        0.5, 0.005,
        active
        + f"\n{metadata['n_roots_0']} roots per label over 6 times in [100, 1000];"
        + f" B1={metadata['B1']:.4f}, axis err={metadata['axis_angle_deg_from_reference']:.3f} deg"
        + f" ({points_0.shape[0]} points per label shown, up to {max_points} subsampled)",
        ha="center", va="bottom", fontsize=5.0,
    )
    figure.subplots_adjust(left=0.01, right=0.99, top=0.90, bottom=0.14, wspace=0.02)
    figure.savefig(output, dpi=220)
    plt.close(figure)
    print(f"[*] wrote {output}")


def _plot_per_time(arrays: dict, metadata: dict, output: Path, max_points: int) -> None:
    """One panel per evolution time, each the *instantaneous* labelled cloud.

    Unlike the pooled view, this shows what SPEC.md section 7.2 distinguishes
    from a time average: whether the same axis-aligned structure is already
    present at each individual time, or only emerges after pooling.
    """

    times = arrays["times_array"]
    n_hat = arrays["n_hat"]
    n_times = len(times)

    figure, axes = plt.subplots(
        2, 3, figsize=(10.2, 6.8), subplot_kw={"projection": "3d"},
    )
    for index, axis in enumerate(axes.ravel()):
        if index >= n_times:
            axis.set_axis_off()
            continue
        points_0 = arrays[f"points_0_time{index}"]
        points_1 = arrays[f"points_1_time{index}"]
        _scatter_panel(axis, points_0, points_1, n_hat, elev=18.0, azim=-60.0,
                        max_points=max_points, seed=index)
        axis.set_title(f"t = {times[index]:.1f}  ({points_0.shape[0]} roots/label)",
                        fontsize=7.5, pad=-4.0)

    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
                  fontsize=7.5, bbox_to_anchor=(0.5, 0.015))

    params = metadata["parameters"]
    active = " ".join(f"{k}={v:+.2f}" for k, v in params.items() if v != 0.0)
    figure.suptitle(
        f"{metadata['name']}  N={metadata['n_pixel']}  (per evolution time, not pooled)",
        fontsize=10.0, y=0.98,
    )
    figure.text(0.5, 0.055, active, ha="center", va="bottom", fontsize=5.5)
    figure.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.10,
                            wspace=0.02, hspace=0.12)
    figure.savefig(output, dpi=220)
    plt.close(figure)
    print(f"[*] wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True,
                        help="Directory holding results.npz (with points_0/points_1/n_hat) "
                             "and metadata.json, from export_preferred_basis_profile.py.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-points", type=int, default=1200,
                        help="Per-label subsample cap so dense clouds stay legible.")
    parser.add_argument("--per-time", action="store_true",
                         help="Plot each evolution time's instantaneous cloud in its own "
                              "panel instead of the pooled cloud (needs results.npz written "
                              "with keep_per_time_points=True, i.e. a current export).")
    args = parser.parse_args()

    arrays = dict(np.load(args.profile / "results.npz"))
    if "points_0" not in arrays:
        raise SystemExit(
            f"{args.profile / 'results.npz'} has no raw points; re-run "
            "export_preferred_basis_profile.py to regenerate it."
        )
    metadata = json.loads((args.profile / "metadata.json").read_text(encoding="utf-8"))

    if args.per_time:
        if "times_array" not in arrays or "points_0_time0" not in arrays:
            raise SystemExit(
                f"{args.profile / 'results.npz'} has no per-time points; re-run "
                "export_preferred_basis_profile.py (current version) to regenerate it."
            )
        output = args.out or (args.profile / "bloch_sphere_per_time.pdf")
        _plot_per_time(arrays, metadata, output, args.max_points)
    else:
        output = args.out or (args.profile / "bloch_sphere.pdf")
        _plot_pooled(arrays, metadata, output, args.max_points)


if __name__ == "__main__":
    main()
