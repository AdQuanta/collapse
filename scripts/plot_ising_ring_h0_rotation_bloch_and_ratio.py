"""Ising-ring detector, single long evolution time, h_0 rotated: Bloch clouds + ratio-vs-Born.

Ad hoc exploratory figure, not a campaign result. No historical "Born-like Ising
ring" candidate with h_0z = h_z could be located in `reports/` (searched, not
found), so this configuration is constructed directly rather than reused:

- Ring detector, qubit coupled to *every* detector site (`connectivity="ring"`,
  `central_coupling="all"`).
- Pure Ising intra-detector interaction: only `J_zz` is nonzero (`J_xx=J_yy=0`).
- Detector field along z only (`h_x=h_y=0`, `h_z` nonzero).
- Qubit self-field along z only at the "original" direction (`h_0x=h_0y=0`,
  `h_0z = h_z`) -- this is the point being rotated away from.
- Coupling: only `g_x` nonzero (`g_y=g_z=0`), base magnitude `0.1`. A single
  nonzero coupling channel is already enough to avoid the trivial degeneracy
  `wiki/campaigns/chain-born-regions.md` item 1 documents (`h_0x=h_0y=g_x=
  g_y=0` makes the qubit's `Z` exactly conserved): with `g_x != 0` the
  coupling itself breaks `Z_0` conservation regardless of `h_0`'s direction.
  With `central_coupling="all"`, the builder adds the coupling term once
  *per detector site* (`core/hamiltonians/quspin_hamiltonians.py`'s
  `_central_targets`), so a raw per-site `g_x` would make the total
  qubit-detector coupling grow with `N` -- the same effect documented in
  `plot_h0_rotation_summary_figure_ring.py`'s module docstring. This script
  applies the same fix: `g_x = g_base/sqrt(N)` (the standard "hopping"-type
  collective-coupling normalization, since `X_0X_i` is off-diagonal), so
  `max|g_effective|/min|nonzero non-g|` stays at the project's `0.1`
  perturbative ceiling regardless of `N`.
- A single evolution time (not the campaign's usual 6-time pooled window,
  since the request was for one long time), long enough to be well past any
  short-time transient.

h_0 is swept over the same angle convention used throughout this session's
other h_0-rotation figures (`theta` in the x-z plane, `phi=0`), including
`theta=0` (the "original" h_0z=h_z direction) as one column.

Row 1: pooled outcome-0/outcome-1 Bloch clouds (`_scatter_panel`, reused
unmodified from `plot_preferred_basis_bloch_sphere.py`), axis line = the
fitted preferred axis n_hat (not h_0's direction), matching the campaign's own
convention of scoring against the fitted axis.

Row 2: the reused ratio-vs-Born diagnostic (`angular_profile`, imported
unmodified from `export_preferred_basis_profile.py`): `R(theta') = rho_0 /
(rho_0+rho_1)` against `cos^2(theta'/2)`, `theta'` measured from the same
fitted axis. At "very small N" the root count per panel is tiny (at most
`2^N` per outcome from one time, not the usual `6 x 2^N` pooled budget), so
bins are kept few and occupancy is reported, not hidden.

Usage::

    python scripts/plot_ising_ring_h0_rotation_bloch_and_ratio.py --n-pixel 4
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
from core.outcome_measures import (  # noqa: E402
    antipodal_bloch_cloud,
    outcome_bloch_cloud,
    preferred_axis_from_cloud,
)
from core.projective_roots import bloch_vectors_from_homogeneous  # noqa: E402
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum  # noqa: E402
from core.relative_evolution_sector import (  # noqa: E402
    _central_indices,
    generalized_relative_evolution_from_sectors,
)
from eval_preferred_basis import MAX_HERMITICITY_RESIDUAL, PENCIL_SOLVER_OPTIONS  # noqa: E402
from export_preferred_basis_profile import angular_profile  # noqa: E402
from h0_basis_outcome_clouds import (  # noqa: E402
    qubit0_pole_rotation,
    rotate_qubit0_output_basis,
)
from plot_preferred_basis_bloch_sphere import _scatter_panel  # noqa: E402

#: Fixed cell: pure Ising ring detector, h_0z = h_z at theta=0.
JZZ = 1.0
HZ = 1.0
G = 0.1  # base g_x magnitude before the 1/sqrt(N) collective-coupling scaling.

#: Same angle convention (x-z plane, phi=0) as every other h_0-rotation figure
#: in this session; theta=0 is the "original" h_0z=h_z direction.
ANGLES_DEG = (0.0, 20.0, 45.0, 70.0, 90.0)


def _scaled_coupling(n_pixel: int) -> float:
    return G / np.sqrt(n_pixel)


def _hamiltonian_and_basis(n_pixel: int, h0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    gx = _scaled_coupling(n_pixel)
    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=n_pixel, connectivity="ring", central_coupling="all",
        J=JZZ, Jxx=0.0, Jyy=0.0,
        Jx=gx, Jy=0.0, Jz=0.0,
        hx=0.0, hy=0.0, hz=HZ,
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


def _sector_hamiltonian(n_pixel: int, h0: np.ndarray) -> SinglePixelHamiltonianQuSpin:
    gx = _scaled_coupling(n_pixel)
    return SinglePixelHamiltonianQuSpin(
        N_pixel=n_pixel, connectivity="ring", central_coupling="all",
        J=JZZ, Jxx=0.0, Jyy=0.0,
        Jx=gx, Jy=0.0, Jz=0.0,
        hx=0.0, hy=0.0, hz=HZ,
        hx0=float(h0[0]), hy0=float(h0[1]), hz0=float(h0[2]),
        use_symmetry=True,
    )


def _points_at_angle_sectors_lab_basis(n_pixel: int, theta_deg: float, time_value: float,
                                       h0: np.ndarray) -> np.ndarray:
    """Outcome-0 Bloch points (lab Z basis) via the pixel-translation symmetry sectors.

    Uses the *fixed-input* pencil, conjugated to outcome-0 (real Hamiltonian,
    `U^T=U`; see `_points_at_angle_sectors_h0_basis`'s docstring for the same
    reasoning applied to the rotated case). Verified against the direct dense
    outcome-0 solve to ~1.7e-9 at N=4 before use.
    """

    hamiltonian = _sector_hamiltonian(n_pixel, h0)
    sectors = hamiltonian.diagonalize_sectors()
    aggregate = generalized_relative_evolution_from_sectors(sectors, time_value, n_pixel + 1)

    valid = ~aggregate.indeterminate
    alpha = np.where(aggregate.finite[valid], aggregate.eigenvalues[valid], 1.0)
    beta = np.where(aggregate.finite[valid], 1.0, 0.0)
    points = bloch_vectors_from_homogeneous(np.conj(alpha), np.conj(beta))
    return points[np.all(np.isfinite(points), axis=1)]


def _points_at_angle_sectors_h0_basis(n_pixel: int, theta_deg: float, time_value: float,
                                      h0_direction: np.ndarray, h0: np.ndarray) -> np.ndarray:
    """Outcome-0 Bloch points, "collapse" redefined against h_0's own eigenbasis,
    via the pixel-translation symmetry sectors.

    Rotating qubit 0's output basis by `R^dagger` (`h0_basis_outcome_clouds`'s
    convention: `R|0>=|+h0_hat>`) makes the propagator `U'=(R^dagger tensor
    I)U` non-symmetric even though `U` is (`U'^T=U` residual ~0.26 measured
    directly, not ~0), so the fixed-input/outcome-0 conjugate shortcut used
    by `_points_at_angle_sectors_lab_basis` does *not* apply to `U'` -- the
    genuine rotated outcome-0 pencil is needed. `R` acts only on qubit 0,
    which commutes with the pixel-translation operator (acting only on the
    detector), so `U'` inherits the *same* translation-sector block structure
    as `U`: within each sector, this builds the sector-local propagator
    `U_sector = V diag(e^{-iEt}) V^dagger` (dimension = sector size, indexed
    by that sector's own `states`), mixes its `top`/`bottom` (qubit-0
    output-pole) row blocks by `R^dagger`, and solves the outcome-0 pencil
    `(D, -C)` locally (`D`=rotated-bottom-rows/bottom-cols,
    `C`=rotated-bottom-rows/top-cols) -- exactly `core.projective_roots.
    forward_pole_root_spectrum`'s outcome-0 construction, applied per sector
    instead of to one dense matrix. Verified against the direct dense
    rotated-outcome-0 solve to ~1.5e-9 at N=4 before use here.
    """

    hamiltonian = _sector_hamiltonian(n_pixel, h0)
    sectors = hamiltonian.diagonalize_sectors()
    rotation_dagger = qubit0_pole_rotation(h0_direction).conj().T
    r10, r11 = rotation_dagger[1, 0], rotation_dagger[1, 1]
    total_qubits = n_pixel + 1

    all_alpha: list[np.ndarray] = []
    all_beta: list[np.ndarray] = []
    for sector in sectors:
        if not bool(sector.get("relative_evolution_local", False)):
            raise ValueError("sector not safe for a local relative-evolution pencil")
        energies = np.asarray(sector["E"], dtype=float)
        vectors = np.asarray(sector["V"], dtype=np.complex128)
        top, bottom = _central_indices(sector, total_qubits)
        if top.size == 0 or bottom.size == 0:
            continue
        if top.size != bottom.size:
            raise ValueError("sector central slices have mismatched dimensions")

        phases = np.exp(-1j * energies * time_value)
        u_sector = (vectors * phases) @ vectors.conj().T
        top_rows, bottom_rows = u_sector[top, :], u_sector[bottom, :]
        rotated_bottom = r10 * top_rows + r11 * bottom_rows

        denominator = rotated_bottom[:, bottom]
        numerator = -rotated_bottom[:, top]
        spectrum = generalized_relative_evolution_spectrum(
            denominator, numerator, compute_left_eigenvectors=False,
            maximum_duplicate_roots=8192,
        )
        all_alpha.append(spectrum.alpha)
        all_beta.append(spectrum.beta)

    alpha = np.concatenate(all_alpha)
    beta = np.concatenate(all_beta)
    points = bloch_vectors_from_homogeneous(alpha, beta)
    return points[np.all(np.isfinite(points), axis=1)]


def _points_at_angle_sectors(n_pixel: int, theta_deg: float, time_value: float,
                             basis: str = "z") -> np.ndarray:
    theta = np.radians(theta_deg)
    h0_direction = np.array([np.sin(theta), 0.0, np.cos(theta)])
    h0_direction[np.abs(h0_direction) < 1.0e-9] = 0.0
    h0 = HZ * h0_direction

    if basis == "h0":
        return _points_at_angle_sectors_h0_basis(n_pixel, theta_deg, time_value, h0_direction, h0)
    return _points_at_angle_sectors_lab_basis(n_pixel, theta_deg, time_value, h0)


def _points_at_angle(n_pixel: int, theta_deg: float, time_value: float,
                     use_symmetry: bool = False, basis: str = "z") -> tuple[np.ndarray, np.ndarray]:
    if use_symmetry:
        points_0 = _points_at_angle_sectors(n_pixel, theta_deg, time_value, basis=basis)
        return points_0, -points_0  # antipodal pushforward, exact for any unitary

    theta = np.radians(theta_deg)
    h0_direction = np.array([np.sin(theta), 0.0, np.cos(theta)])
    h0_direction[np.abs(h0_direction) < 1.0e-9] = 0.0
    h0 = HZ * h0_direction

    energies, vectors = _hamiltonian_and_basis(n_pixel, h0)
    phases = np.exp(-1j * energies * time_value)
    unitary = (vectors * phases) @ vectors.conj().T
    if basis == "h0":
        unitary = rotate_qubit0_output_basis(unitary, h0_direction)

    cloud_0 = outcome_bloch_cloud(unitary, outcome=0, **PENCIL_SOLVER_OPTIONS)
    cloud_1 = antipodal_bloch_cloud(cloud_0)
    return cloud_0.points, cloud_1.points


def _ratio_panel(axis, points_0: np.ndarray, points_1: np.ndarray, n_hat: np.ndarray | None,
                  n_bins: int) -> None:
    if n_hat is None or points_0.shape[0] == 0:
        axis.text(0.5, 0.5, "axis refused\n(no ratio)", ha="center", va="center",
                   transform=axis.transAxes, fontsize=8, color="0.4")
        axis.set_xticks([]); axis.set_yticks([])
        return
    theta_0 = np.arccos(np.clip(points_0 @ n_hat, -1.0, 1.0))
    theta_1 = np.arccos(np.clip(points_1 @ n_hat, -1.0, 1.0))
    profile = angular_profile(theta_0, theta_1, n_bins)
    occupied = profile["R_occupied"]
    grid = np.linspace(0.0, np.pi, 256)
    axis.plot(grid, np.cos(grid / 2.0) ** 2, color="0.6", linewidth=1.2, linestyle="--",
              label="Born $\\cos^2(\\theta'/2)$")
    axis.plot(profile["centers"][occupied], profile["R"][occupied], "o-", color="#8e44ad",
              markersize=2.5, linewidth=1.0, label="$R(\\theta')$")
    axis.set_ylim(-0.05, 1.05)
    axis.set_xlim(0.0, np.pi)
    axis.set_xticks([0, np.pi / 2, np.pi])
    axis.set_xticklabels(["0", "$\\pi/2$", "$\\pi$"], fontsize=7)
    axis.tick_params(labelsize=7)
    coverage = int(np.sum(occupied))
    axis.text(0.5, -0.24, f"coverage {coverage}/{n_bins}", transform=axis.transAxes,
               ha="center", fontsize=6.5, color="0.4")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-pixel", type=int, default=4)
    parser.add_argument("--time", type=float, default=1.0e6)
    parser.add_argument("--n-bins", type=int, default=10)
    parser.add_argument("--symmetry", action="store_true",
                        help="Use the pixel-translation symmetry sectors (fixed-input pencil, "
                             "conjugated) instead of the direct dense outcome-0 solve; see "
                             "_points_at_angle_sectors's docstring.")
    parser.add_argument("--basis", choices=("z", "h0"), default="z",
                        help="'z': outcome = lab-frame Z pole of qubit 0 (original convention); "
                             "'h0': outcome = h_0's own eigenbasis pole at each panel's theta.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-points", type=int, default=1200)
    args = parser.parse_args()

    n_cols = len(ANGLES_DEG)
    figure = plt.figure(figsize=(2.3 * n_cols + 0.6, 7.0))
    grid = figure.add_gridspec(2, n_cols, height_ratios=[1.6, 1.0])
    axes_top = [figure.add_subplot(grid[0, i], projection="3d") for i in range(n_cols)]
    axes_bottom = [figure.add_subplot(grid[1, i]) for i in range(n_cols)]

    legend_handles = None
    for col, theta_deg in enumerate(ANGLES_DEG):
        points_0, points_1 = _points_at_angle(args.n_pixel, theta_deg, args.time,
                                              use_symmetry=args.symmetry, basis=args.basis)
        axis_result = preferred_axis_from_cloud(points_0, np.ones(points_0.shape[0]))
        n_hat = axis_result.n_hat if axis_result.status == "ok" else None

        _scatter_panel(axes_top[col], points_0, points_1, n_hat, elev=14.0, azim=-60.0,
                        max_points=args.max_points, seed=col,
                        axis_line_label=r"fitted axis $\hat n$")
        axes_top[col].set_title(f"$\\theta={theta_deg:.0f}\\degree$"
                                 + ("  (original)" if theta_deg == 0.0 else ""),
                                 fontsize=9.5, pad=2.0)
        if legend_handles is None:
            legend_handles = axes_top[col].get_legend_handles_labels()

        _ratio_panel(axes_bottom[col], points_0, points_1, n_hat, args.n_bins)
        if col == 0:
            axes_bottom[col].set_ylabel("$R(\\theta')$", fontsize=8)
        status = f"B1={axis_result.B1:.3f}" if axis_result.status == "ok" else "refused"
        print(f"[*] theta={theta_deg:5.1f} deg: {points_0.shape[0]} roots/label, {status}")

    if legend_handles is not None:
        handles, labels = legend_handles
        figure.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
                      fontsize=8.5, bbox_to_anchor=(0.5, 0.0))
    ratio_handles, ratio_labels = axes_bottom[0].get_legend_handles_labels()
    figure.legend(ratio_handles, ratio_labels, loc="lower center", ncol=2, frameon=False,
                  fontsize=7.5, bbox_to_anchor=(0.5, 0.045))

    basis_title = "" if args.basis == "z" else ", outcome defined in $\\hat h_0$'s own eigenbasis"
    figure.suptitle(
        "Ising ring detector ($J_{zz}$ only, $h\\parallel z$), $\\hat h_0$ rotated off its "
        f"original $h_{{0z}}=h_z$ direction{basis_title}\nsingle long time -- row 1: Bloch clouds, "
        "row 2: ratio vs. Born",
        fontsize=10.0, y=0.99,
    )
    gx = _scaled_coupling(args.n_pixel)
    solve_label = (
        "pixel-translation symmetry sectors, fixed-input pencil conjugated (see script docstring)"
        if args.symmetry else "direct dense solve, no symmetry exploited"
    )
    basis_label = (
        "outcome = lab-frame Z pole of qubit 0 (original convention)" if args.basis == "z"
        else "outcome = $\\hat h_0$'s own eigenbasis pole of qubit 0 at each panel's $\\theta$"
    )
    figure.text(
        0.5, 0.885,
        f"N={args.n_pixel};  $J_{{zz}}={JZZ:g}$, $h_z={HZ:g}$, $|h_0|={HZ:g}$, "
        f"$g_x={gx:.4f}$ ($=0.1/\\sqrt{{N}}$), $g_y=g_z=0$;  "
        f"t={args.time:g};  single time, not the usual pooled 6-time window\n{solve_label};  {basis_label}",
        ha="center", fontsize=7.8, color="0.35",
    )
    figure.subplots_adjust(left=0.05, right=0.99, top=0.80, bottom=0.12, wspace=0.15, hspace=0.3)

    suffix = "_sectors" if args.symmetry else ""
    suffix += "" if args.basis == "z" else "_h0basis"
    out = args.out or Path(
        f"reports/preferred_basis/ising_ring_h0_rotation_N{args.n_pixel}_t{args.time:g}{suffix}.pdf"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(out, dpi=220)
    plt.close(figure)
    print(f"[*] wrote {out}")


if __name__ == "__main__":
    main()
