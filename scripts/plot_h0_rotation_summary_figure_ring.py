"""Ring-topology counterpart of `plot_h0_rotation_summary_figure.py`.

Same exercise (sweep h_0's direction, plot the pooled outcome-0/outcome-1
Bloch clouds, black line = h_0's own direction, not the fitted axis), but the
central qubit now couples collectively to *every* detector site
(`connectivity="ring"`, `central_coupling="all"`, `SPEC.md` section 9.1's
ring family) instead of to a single chain endpoint.

Collective coupling grows with the number of terms summed, so the campaign
convention used elsewhere in this file (a coupling magnitude chosen once and
reused at every N) would not describe the same physical regime at different
sizes. The base (N-independent) coupling magnitudes below are scaled down by
``1/sqrt(N)`` for `g_x, g_y` and ``1/N`` for `g_z` before being passed to the
builder -- the standard collective-coupling normalization (`g_x, g_y` are
"hopping"-type collective operators, whose natural norm grows as `sqrt(N)`;
`g_z` is a diagonal collective operator, whose natural norm grows as `N`) --
so the *effective* per-generator coupling strength stays comparable to the
chain figure's at the one size (N=8) both are evaluated at. Because this
scaling is size-dependent, unlike the chain figure's fixed couplings, it is
specific to N=8 and would need to be recomputed, not merely reused, at any
other N.

Does not reuse `eval_chain_born.ChainConfig` (hardwired to
`connectivity="chain", central_coupling="first"`) or the `eval_preferred_
basis.py` pipeline built on it; the Hamiltonian is built directly, and no
perturbative-ratio gate is applied (every panel is plotted regardless).

Usage::

    python scripts/plot_h0_rotation_summary_figure_ring.py
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

from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin  # noqa: E402
from core.outcome_measures import outcome_bloch_cloud  # noqa: E402
from eval_preferred_basis import (  # noqa: E402
    MAX_HERMITICITY_RESIDUAL,
    PENCIL_SOLVER_OPTIONS,
    unitary_at_time,
)
from h0_basis_outcome_clouds import rotate_qubit0_output_basis  # noqa: E402
from plot_preferred_basis_bloch_sphere import _scatter_panel  # noqa: E402

#: Base (N-independent) collective coupling magnitudes, one order of
#: magnitude above the original design. At N=8 these scale down to
#: gx=gy=0.1/sqrt(8)=0.0354, gz=0.05/8=0.00625 (family 2) etc.
RING_G = dict(gx=0.0, gy=0.0, gz=0.1)
RING_ENDPOINT_G = dict(gx=0.1, gy=0.1, gz=0.05)
RING_XYZ_G = dict(gx=0.10, gy=0.05, gz=0.06)

#: Three dynamical regimes, each six log-spaced times -- see
#: `plot_h0_rotation_summary_figure.py`'s module docstring/`TIME_REGIMES` for
#: the same convention on the chain figure.
TIME_REGIMES: dict[str, tuple[float, float]] = {
    "short": (1.0, 10.0),
    "intermediate": (100.0, 1000.0),
    "long": (10000.0, 100000.0),
}

#: See `plot_h0_rotation_summary_figure.py`'s `DETECTOR_H_CASES` for the same
#: convention: "tilted" is fixed at 45 degrees in the y-z plane, out of h_0's
#: own x-z sweep plane, so it differs from h_0's direction at every theta.
DETECTOR_H_CASES: dict[str, tuple[float, float, float]] = {
    "z": (0.0, 0.0, 1.0),
    "zero": (0.0, 0.0, 0.0),
    "tilted": (0.0, float(np.sin(np.radians(45.0))), float(np.cos(np.radians(45.0)))),
}

#: hx, hy, hz are filled in per `--detector-h` case at Hamiltonian-construction
#: time (see `_hamiltonian_and_basis`), not hardcoded here.
FAMILIES: dict[str, dict] = {
    "xxz": dict(
        fixed=dict(Jxx=2.0, Jyy=2.0, Jzz=1.0, **RING_G),
        h0_magnitude=float(np.linalg.norm([1.0, 1.0, 1.0])),
        title="1. XXZ ring ($\\Delta=0.5$), all-to-all coupling",
    ),
    "xxz_endpoint": dict(
        fixed=dict(Jxx=2.0, Jyy=2.0, Jzz=1.0, **RING_ENDPOINT_G),
        h0_magnitude=float(np.linalg.norm([1.0, 1.0, 1.0])),
        title="2. XXZ ring, $\\Delta=0.5$ intra-detector & collective coupling",
    ),
    "xyz_endpoint": dict(
        fixed=dict(Jxx=1.32, Jyy=2.53, Jzz=1.10, **RING_XYZ_G),
        h0_magnitude=float(np.linalg.norm([-1.35, -1.69, 2.01])),
        title="3. General XYZ ring, all-to-all coupling (screen_00 cell)",
    ),
}

ANGLES_DEG = (0.0, 20.0, 45.0, 70.0, 90.0)

#: See ``h0_basis_outcome_clouds`` module docstring / the chain figure's own
#: ``BASIS_CHOICES`` for the same convention.
BASIS_CHOICES = ("z", "h0")


def _scaled_coupling(fixed: dict, n_pixel: int) -> tuple[float, float, float]:
    return (
        fixed["gx"] / np.sqrt(n_pixel),
        fixed["gy"] / np.sqrt(n_pixel),
        fixed["gz"] / n_pixel,
    )


def _hamiltonian_and_basis(family: dict, n_pixel: int, h0: np.ndarray,
                           detector_h: tuple[float, float, float]) -> tuple[np.ndarray, np.ndarray]:
    fixed = family["fixed"]
    gx, gy, gz = _scaled_coupling(fixed, n_pixel)
    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=n_pixel, connectivity="ring", central_coupling="all",
        J=fixed["Jzz"], Jxx=fixed["Jxx"], Jyy=fixed["Jyy"],
        Jx=gx, Jy=gy, Jz=gz,
        hx=detector_h[0], hy=detector_h[1], hz=detector_h[2],
        hx0=float(h0[0]), hy0=float(h0[1]), hz0=float(h0[2]),
        use_symmetry=False,
    )
    dense = hamiltonian.generate()
    scale = max(float(np.linalg.norm(dense)), 1.0)
    hermiticity = float(np.linalg.norm(dense - dense.conj().T) / scale)
    if hermiticity > MAX_HERMITICITY_RESIDUAL:
        raise RuntimeError(f"hermiticity violation {hermiticity:.3e} at N={n_pixel}")
    energies, vectors = np.linalg.eigh(dense)
    return energies, vectors


def _pooled_points(family: dict, n_pixel: int, theta_deg: float,
                   times: tuple[float, ...],
                   detector_h: tuple[float, float, float],
                   basis: str = "z") -> tuple[np.ndarray, np.ndarray]:
    theta = np.radians(theta_deg)
    h0_direction = np.array([np.sin(theta), 0.0, np.cos(theta)])
    h0_direction[np.abs(h0_direction) < 1.0e-9] = 0.0
    h0 = family["h0_magnitude"] * h0_direction

    energies, vectors = _hamiltonian_and_basis(family, n_pixel, h0, detector_h)
    points_0: list[np.ndarray] = []
    points_1: list[np.ndarray] = []
    for time_value in times:
        unitary = unitary_at_time(energies, vectors, float(time_value))
        if basis == "h0":
            unitary = rotate_qubit0_output_basis(unitary, h0_direction)
        cloud_0 = outcome_bloch_cloud(unitary, outcome=0, **PENCIL_SOLVER_OPTIONS)
        points_0.append(cloud_0.points)
        points_1.append(-cloud_0.points)  # antipodal pushforward, see core.outcome_measures
    return np.concatenate(points_0, axis=0), np.concatenate(points_1, axis=0)


def _param_text(family: dict, n_pixel: int, detector_h: tuple[float, float, float]) -> str:
    fixed = family["fixed"]
    gx, gy, gz = _scaled_coupling(fixed, n_pixel)
    return (
        f"$J_{{xx}}={fixed['Jxx']:g}$, $J_{{yy}}={fixed['Jyy']:g}$, $J_{{zz}}={fixed['Jzz']:g}$\n"
        f"$h_x={detector_h[0]:g}$, $h_y={detector_h[1]:g}$, $h_z={detector_h[2]:g}$\n"
        f"base $g_x={fixed['gx']:g}$, $g_y={fixed['gy']:g}$, $g_z={fixed['gz']:g}$\n"
        f"at N={n_pixel}: $g_x={gx:.5f}$, $g_y={gy:.5f}$, $g_z={gz:.6f}$\n"
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
    out = args.out or Path(f"reports/preferred_basis/h0_rotation_summary_figure_ring_{suffix}.pdf")

    n_rows = len(FAMILIES)
    n_cols = len(ANGLES_DEG)
    figure, axes = plt.subplots(
        n_rows, n_cols, figsize=(2.15 * n_cols + 2.6, 2.55 * n_rows),
        subplot_kw={"projection": "3d"},
    )

    for row, (family_key, family) in enumerate(FAMILIES.items()):
        for col, theta_deg in enumerate(ANGLES_DEG):
            axis = axes[row, col]
            points_0, points_1 = _pooled_points(
                family, args.n_pixel, theta_deg, times, detector_h, basis=args.basis,
            )
            theta = np.radians(theta_deg)
            h0_direction = np.array([np.sin(theta), 0.0, np.cos(theta)])
            _scatter_panel(axis, points_0, points_1, h0_direction,
                           elev=14.0, azim=-60.0, max_points=args.max_points, seed=col,
                           axis_line_label=r"$\hat h_0$ direction")
            print(f"[*] {family_key} theta={theta_deg:5.1f} deg: plotted "
                  f"({points_0.shape[0]} roots/label)")
            if row == 0:
                axis.set_title(f"$\\theta={theta_deg:.0f}\\degree$", fontsize=9.5, pad=2.0)

        figure.text(
            0.015, 1.0 - (row + 0.5) / n_rows,
            family["title"] + "\n\n" + _param_text(family, args.n_pixel, detector_h),
            transform=figure.transFigure, ha="left", va="center", fontsize=7.2,
            linespacing=1.6,
        )

    handles, labels = axes[0, 1].get_legend_handles_labels()
    figure.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
                  fontsize=8.5, bbox_to_anchor=(0.58, 0.005))

    detector_h_label = {
        "z": "detector field $h \\parallel z$",
        "zero": "detector field $h = 0$",
        "tilted": "detector field $h$ fixed at 45 deg in the $y$-$z$ plane",
    }[args.detector_h]
    basis_title = "" if args.basis == "z" else ", outcome defined in $\\hat h_0$'s own eigenbasis"
    figure.suptitle(
        "Ring topology, collective (all-to-all) qubit-detector coupling: the collapsible-state "
        f"cloud as $\\hat h_0$ rotates (black line = $\\hat h_0$, not the fitted axis) -- "
        f"{args.time_regime} times, {args.detector_h} detector field{basis_title}",
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
        "$g_x, g_y \\propto 1/\\sqrt{N}$, $g_z \\propto 1/N$",
        ha="center", fontsize=8.0, color="0.35",
    )
    figure.subplots_adjust(left=0.235, right=0.99, top=0.90, bottom=0.045,
                            wspace=0.05, hspace=0.15)
    figure.savefig(out, dpi=220)
    plt.close(figure)
    print(f"[*] wrote {out}")


if __name__ == "__main__":
    main()
