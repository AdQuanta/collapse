"""One summary figure: how the collapsible-state cloud changes with h_0's direction.

Sweeps h_0's polar angle theta away from the detector's own field axis (z)
toward the plane orthogonal to it (phi=0, i.e. h_0 stays in the xz-plane), at
fixed |h_0|, on three endpoint-chain cells, one per row, all with the
detector field h itself held purely along z (h_x = h_y = 0):

1. ``xxz``: `wiki/campaigns/chain-born-regions.md`'s XXZ tier-3 cell
   (`Delta = J_zz/J_xx = 0.5`), single-axis qubit-endpoint coupling (`g_z`
   only).
2. ``xxz_endpoint``: the same XXZ intra-detector anisotropy, with the
   qubit-endpoint coupling `g` *also* built with the family's `Delta=0.5`
   anisotropy (`g_x = g_y`, `g_z = Delta * g_x`) -- "XXZ intra-detector &
   qubit-endpoint interaction."
3. ``xyz_endpoint``: the general (fully anisotropic) XYZ `screen_00` cell,
   `J` and `g` both taken directly from that region center -- "general XYZ
   intra-detector & qubit-endpoint interaction."

The black line in each panel is h_0's own direction at that theta (not the
fitted preferred axis): at a suppressed point the fitted axis can point
anywhere, including nearly perpendicular to h_0 (confirmed directly: at
theta=90 degrees on family 2, the angle between the fitted axis and h_0 is
89.96 degrees), so a line meant to show "where h_0 points" has to be h_0
itself, not a downstream fit of it.

Every panel is plotted regardless of the perturbative ratio
`max|g| / min|nonzero other|` (`h_0`'s own components included, per the
house `eval_chain_born.perturbative_ratio` convention): the ratio is still
computed and printed to the console for every angle, and disclosed per row
in the figure, but nothing is skipped or gated on it by request -- this
campaign's own 0.1 house ceiling does not apply to this ad hoc figure.

Usage::

    python scripts/plot_h0_rotation_summary_figure.py
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

from core.outcome_measures import outcome_bloch_cloud  # noqa: E402
from eval_chain_born import ChainConfig, perturbative_ratio  # noqa: E402
from eval_preferred_basis import (  # noqa: E402
    PENCIL_SOLVER_OPTIONS,
    _hamiltonian_and_basis,
    pooled_outcome_clouds,
    unitary_at_time,
)
from h0_basis_outcome_clouds import rotate_qubit0_output_basis  # noqa: E402
from plot_preferred_basis_bloch_sphere import _scatter_panel  # noqa: E402

#: Three dynamical regimes, each six log-spaced times, pooled the same way as
#: the campaign's own frozen window (which is exactly "intermediate" here).
#: "short"/"long" are not part of any frozen campaign contract -- ad hoc
#: choices roughly an order of magnitude below/above the detector's own
#: energy scale (|J|, |h| ~ 1-2.5) and the frozen window respectively.
TIME_REGIMES: dict[str, tuple[float, float]] = {
    "short": (1.0, 10.0),
    "intermediate": (100.0, 1000.0),
    "long": (10000.0, 100000.0),
}

#: Detector single-site field h, magnitude 1 (matching the original h_z=1
#: convention) in three cases: along z as before, off entirely, or tilted at
#: a fixed 45 degrees in the y-z plane -- deliberately out of h_0's own sweep
#: plane (h_0 stays in the x-z plane throughout), so "a different angle from
#: h_0" is true at every theta in the sweep, not just numerically at one.
DETECTOR_H_CASES: dict[str, tuple[float, float, float]] = {
    "z": (0.0, 0.0, 1.0),
    "zero": (0.0, 0.0, 0.0),
    "tilted": (0.0, float(np.sin(np.radians(45.0))), float(np.cos(np.radians(45.0)))),
}

#: Coupling magnitudes, one order of magnitude above the campaign's original
#: 0.01-ratio design (goal_preferred_basis.md's own screen_00 cell sits at
#: ratio 0.1 exactly); no perturbative gate is applied to this figure (see
#: module docstring), so these are plain fixed values, not a scale factor.
XXZ_G = dict(gx=0.0, gy=0.0, gz=0.1)
XXZ_ENDPOINT_G = dict(gx=0.1, gy=0.1, gz=0.05)
XYZ_ENDPOINT_G = dict(gx=0.10, gy=0.05, gz=0.06)

#: hx, hy, hz are filled in per `--detector-h` case at config-construction
#: time (see `_config_at_angle`), not hardcoded here.
FAMILIES: dict[str, dict] = {
    "xxz": dict(
        fixed=dict(Jxx=2.0, Jyy=2.0, Jzz=1.0, **XXZ_G),
        h0_magnitude=float(np.linalg.norm([1.0, 1.0, 1.0])),
        title="1. XXZ endpoint chain ($\\Delta=0.5$)",
    ),
    "xxz_endpoint": dict(
        fixed=dict(Jxx=2.0, Jyy=2.0, Jzz=1.0, **XXZ_ENDPOINT_G),
        h0_magnitude=float(np.linalg.norm([1.0, 1.0, 1.0])),
        title="2. XXZ intra-detector & qubit-endpoint ($\\Delta=0.5$ both)",
    ),
    "xyz_endpoint": dict(
        fixed=dict(Jxx=1.32, Jyy=2.53, Jzz=1.10, **XYZ_ENDPOINT_G),
        h0_magnitude=float(np.linalg.norm([-1.35, -1.69, 2.01])),
        title="3. General XYZ intra-detector & qubit-endpoint (screen_00 cell)",
    ),
}

#: Fixed thumbnail angles, shared across every row for direct comparison.
ANGLES_DEG = (0.0, 20.0, 45.0, 70.0, 90.0)

#: See ``h0_basis_outcome_clouds`` module docstring: "z" is the original
#: lab-frame convention (outcome = which Z pole of qubit 0 the final state
#: collapses to); "h0" redefines outcome against h_0's own (rotating)
#: eigenbasis instead, at every panel's own theta.
BASIS_CHOICES = ("z", "h0")


def pooled_outcome_clouds_h0_basis(
    config: ChainConfig, n_pixel: int, times: tuple[float, ...], h0_direction: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    energies, vectors, _ = _hamiltonian_and_basis(config, n_pixel)
    points_0: list[np.ndarray] = []
    points_1: list[np.ndarray] = []
    for time_value in times:
        unitary = unitary_at_time(energies, vectors, float(time_value))
        rotated = rotate_qubit0_output_basis(unitary, h0_direction)
        cloud_0 = outcome_bloch_cloud(rotated, outcome=0, **PENCIL_SOLVER_OPTIONS)
        points_0.append(cloud_0.points)
        points_1.append(-cloud_0.points)  # antipodal pushforward, still exact -- see module docstring
    return np.concatenate(points_0, axis=0), np.concatenate(points_1, axis=0)


def _config_at_angle(family_key: str, family: dict, theta_deg: float,
                     detector_h: tuple[float, float, float]) -> ChainConfig:
    theta = np.radians(theta_deg)
    h0 = family["h0_magnitude"] * np.array([np.sin(theta), 0.0, np.cos(theta)])
    # sin/cos of a degree-valued right angle are not exactly 0 in floating
    # point (e.g. cos(90 deg) ~ 6e-17): left alone, that noise floor is a
    # *nonzero* h_0 component, which is a physically different (and
    # misleading) configuration from "h_0 exactly in-plane"/"exactly along
    # z". Snapping it to exactly zero matches how every other exactly-zero
    # parameter in this campaign (e.g. screen_00's h_y = 0) is treated.
    h0[np.abs(h0) < 1.0e-9] = 0.0
    return ChainConfig(
        name=f"{family_key}_h0_theta{theta_deg:05.1f}", hypothesis="h_0 rotation summary sweep",
        rung="h0_rotation_summary",
        h0x=float(h0[0]), h0y=float(h0[1]), h0z=float(h0[2]),
        hx=detector_h[0], hy=detector_h[1], hz=detector_h[2], **family["fixed"],
    )


def _param_text(family: dict, detector_h: tuple[float, float, float]) -> str:
    fixed = family["fixed"]
    return (
        f"$J_{{xx}}={fixed['Jxx']:g}$, $J_{{yy}}={fixed['Jyy']:g}$, $J_{{zz}}={fixed['Jzz']:g}$\n"
        f"$h_x={detector_h[0]:g}$, $h_y={detector_h[1]:g}$, $h_z={detector_h[2]:g}$\n"
        f"$g_x={fixed['gx']:g}$, $g_y={fixed['gy']:g}$, $g_z={fixed['gz']:g}$\n"
        f"$|h_0|={family['h0_magnitude']:.4f}$"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-pixel", type=int, default=8)
    parser.add_argument("--time-regime", choices=sorted(TIME_REGIMES), default="intermediate")
    parser.add_argument("--detector-h", choices=sorted(DETECTOR_H_CASES), default="z")
    parser.add_argument("--basis", choices=BASIS_CHOICES, default="z",
                        help="'z': outcome = lab-frame Z pole (original convention); "
                             "'h0': outcome = h_0's own eigenbasis pole at each panel's theta.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-points", type=int, default=1200)
    args = parser.parse_args()
    t_min, t_max = TIME_REGIMES[args.time_regime]
    times = tuple(float(t) for t in np.geomspace(t_min, t_max, 6))
    detector_h = DETECTOR_H_CASES[args.detector_h]
    suffix = args.time_regime + ("" if args.detector_h == "z" else f"_h{args.detector_h}")
    suffix += "" if args.basis == "z" else "_h0basis"
    out = args.out or Path(f"reports/preferred_basis/h0_rotation_summary_figure_{suffix}.pdf")

    n_rows = len(FAMILIES)
    n_cols = len(ANGLES_DEG)
    figure, axes = plt.subplots(
        n_rows, n_cols, figsize=(2.15 * n_cols + 2.6, 2.55 * n_rows),
        subplot_kw={"projection": "3d"},
    )

    legend_handles = None
    for row, (family_key, family) in enumerate(FAMILIES.items()):
        for col, theta_deg in enumerate(ANGLES_DEG):
            axis = axes[row, col]
            config = _config_at_angle(family_key, family, theta_deg, detector_h)
            ratio = perturbative_ratio(config)

            theta = np.radians(theta_deg)
            h0_direction = np.array([np.sin(theta), 0.0, np.cos(theta)])
            if args.basis == "h0":
                points_0, points_1 = pooled_outcome_clouds_h0_basis(
                    config, args.n_pixel, times, h0_direction,
                )
            else:
                pooled = pooled_outcome_clouds(config, args.n_pixel, times)
                points_0, points_1 = pooled["points_0"], pooled["points_1"]
            _scatter_panel(axis, points_0, points_1, h0_direction,
                           elev=14.0, azim=-60.0, max_points=args.max_points, seed=col,
                           axis_line_label=r"$\hat h_0$ direction")
            flag = "  (non-perturbative)" if ratio > 0.1 * (1.0 + 1.0e-9) else ""
            print(f"[*] {family_key} theta={theta_deg:5.1f} deg: plotted "
                  f"(ratio={ratio:.4f}){flag}")
            if row == 0:
                axis.set_title(f"$\\theta={theta_deg:.0f}\\degree$", fontsize=9.5, pad=2.0)
            if legend_handles is None:
                legend_handles = axis.get_legend_handles_labels()

        figure.text(
            0.015, 1.0 - (row + 0.5) / n_rows,
            family["title"] + "\n\n" + _param_text(family, detector_h),
            transform=figure.transFigure, ha="left", va="center", fontsize=7.2,
            linespacing=1.6,
        )

    if legend_handles is not None:
        handles, labels = legend_handles
        figure.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
                      fontsize=8.5, bbox_to_anchor=(0.58, 0.005))

    detector_h_label = {
        "z": "detector field $h \\parallel z$",
        "zero": "detector field $h = 0$",
        "tilted": "detector field $h$ fixed at 45 deg in the $y$-$z$ plane",
    }[args.detector_h]
    basis_title = "" if args.basis == "z" else ", outcome defined in $\\hat h_0$'s own eigenbasis"
    figure.suptitle(
        "The collapsible-state cloud as $\\hat h_0$ rotates off the detector's field axis "
        f"(black line = $\\hat h_0$, not the fitted axis) -- {args.time_regime} times, "
        f"{args.detector_h} detector field{basis_title}",
        fontsize=10.5, y=0.998,
    )
    basis_label = (
        "outcome = lab-frame Z pole of qubit 0 (original convention)" if args.basis == "z"
        else "outcome = $\\hat h_0$'s own eigenbasis pole of qubit 0 at each panel's $\\theta$"
    )
    figure.text(
        0.58, 0.958,
        f"N={args.n_pixel};  blue = outcome 0, red = outcome 1;  pooled over 6 times "
        f"in $[{t_min:g},{t_max:g}]$;  {detector_h_label} throughout;  {basis_label};  "
        "no perturbative-ratio gate applied",
        ha="center", fontsize=8.0, color="0.35",
    )
    figure.subplots_adjust(left=0.235, right=0.99, top=0.90, bottom=0.045,
                            wspace=0.05, hspace=0.15)
    figure.savefig(out, dpi=220)
    plt.close(figure)
    print(f"[*] wrote {out}")


if __name__ == "__main__":
    main()
