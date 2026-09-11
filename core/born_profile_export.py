"""Lossless plotting tables for stored projective-root angular diagnostics.

Angles are radians, P is a density per radian, and R is dimensionless.
This module performs no evolution, fitting, smoothing, or rebinning.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def load_profile(path: Path, *, activation_global: bool = False) -> dict[str, np.ndarray]:
    """Read the saved global ensemble; never substitute an activation component."""
    names = {
        "edges": "edges", "centers": "centers", "P": "p_theta",
        "P_reflected": "p_pi_minus_theta", "R": "R",
        "occupied": "R_occupied", "Born": "R_born",
    }
    if activation_global:
        names.update(R="ratio", occupied="occupied", Born="born")
        names = {key: "global__" + value for key, value in names.items()}
    with np.load(path, allow_pickle=False) as archive:
        return {key: np.array(archive[value]) for key, value in names.items()}


def validate_profile(arrays: dict[str, np.ndarray], *, rmse: float) -> dict[str, float]:
    """Check normalization and identities to 1e-11 absolute roundoff tolerance."""
    edges, centers = arrays["edges"], arrays["centers"]
    widths = np.diff(edges)
    n = centers.size
    if edges.shape != (n + 1,) or not np.all(widths > 0):
        raise ValueError("invalid bin edges")
    for key, value in arrays.items():
        if key != "edges" and value.shape != (n,):
            raise ValueError(f"invalid {key} shape")
    np.testing.assert_allclose(edges[[0, -1]], [0, np.pi], rtol=0, atol=1e-11)
    np.testing.assert_allclose(centers, (edges[1:] + edges[:-1]) / 2, rtol=0, atol=1e-11)
    integrals = {}
    for key in ("P", "P_reflected"):
        if not np.all(np.isfinite(arrays[key])) or np.any(arrays[key] < 0):
            raise ValueError(f"invalid {key} density")
        integrals[key + "_integral"] = float(arrays[key] @ widths)
        np.testing.assert_allclose(integrals[key + "_integral"], 1, rtol=0, atol=1e-11)
    total = arrays["P"] + arrays["P_reflected"]
    occupied = arrays["occupied"].astype(bool)
    np.testing.assert_array_equal(occupied, total > 0)
    np.testing.assert_allclose(arrays["R"][occupied], arrays["P"][occupied] / total[occupied], rtol=0, atol=1e-11)
    np.testing.assert_allclose(arrays["Born"], np.cos(centers / 2) ** 2, rtol=0, atol=1e-11)
    actual_rmse = float(np.sqrt(np.mean((arrays["R"][occupied] - arrays["Born"][occupied]) ** 2)))
    np.testing.assert_allclose(actual_rmse, rmse, rtol=0, atol=1e-11)
    return {**integrals, "RMSE_recomputed": actual_rmse, "occupied_fraction": float(occupied.mean())}


def write_table(path: Path, columns: list[str], values: np.ndarray) -> None:
    """Write whitespace-separated PGFPlots data that round-trips float64."""
    values = np.asarray(values)
    if values.ndim != 2 or values.shape[1] != len(columns):
        raise ValueError("table data must have one column per header label")
    np.savetxt(path, values, fmt="%.17g", header=" ".join(columns), comments="")
    restored = np.loadtxt(path, skiprows=1, ndmin=2)
    np.testing.assert_array_equal(restored, values)


def write_profile_tables(directory: Path, arrays: dict[str, np.ndarray]) -> None:
    """Save bin centers and exact duplicated-edge histogram step coordinates."""
    e, c = arrays["edges"], arrays["centers"]
    occupied = arrays["occupied"].astype(bool)
    ratio = np.where(occupied, arrays["R"], np.nan)
    write_table(directory / "profile.dat", [
        "theta_rad", "theta_over_pi", "theta_deg", "bin_left_rad", "bin_right_rad",
        "P", "P_reflected", "R", "Born", "R_minus_Born", "occupied",
    ], np.column_stack((c, c / np.pi, np.degrees(c), e[:-1], e[1:],
                        arrays["P"], arrays["P_reflected"], ratio,
                        arrays["Born"], ratio - arrays["Born"], occupied)))
    x = np.column_stack((e[:-1], e[1:])).ravel()
    write_table(directory / "histogram_steps.dat", ["theta_rad", "theta_over_pi", "P", "P_reflected"],
                np.column_stack((x, x / np.pi, np.repeat(arrays["P"], 2),
                                 np.repeat(arrays["P_reflected"], 2))))


def graph_tables(n: int, parameters: dict[str, Any], graph: dict[str, Any] | None,
                 *, family: str, jx_effective: float, jy_effective: float) -> tuple[np.ndarray, np.ndarray]:
    """Return circular detector layout and distinct Hamiltonian bond tables.

    Detector IDs are 0..N-1; the central qubit is N. Edge kind 1 is the
    saved detector graph, 2 is the periodic distance-two ring bond set,
    and 0 is a central-detector coupling. Couplings are model parameters,
    not signed Pauli-string coefficients. Coordinates are dimensionless.
    """
    if n < 5:
        raise ValueError("export contract requires N >= 5 (distinct ring bond shells)")
    angle = 2 * np.pi * np.arange(n) / n
    nodes = np.column_stack((np.arange(n + 1), np.r_[np.cos(angle), 0],
                             np.r_[np.sin(angle), 0], np.r_[np.zeros(n), 1]))
    if graph and "edges_zero_based" in graph:
        bonds = [tuple(sorted(map(int, pair))) for pair in graph["edges_zero_based"]]
        if graph.get("nodes", n) != n:
            raise ValueError("saved detector graph has the wrong size")
    elif family.startswith("ring_"):
        bonds = sorted({tuple(sorted((i, (i + 1) % n))) for i in range(n)})
    else:
        raise ValueError("network requires the saved edge list")
    if len(set(bonds)) != len(bonds) or any(a == b or a < 0 or b >= n for a, b in bonds):
        raise ValueError("invalid or repeated detector edge")
    edges = [[a, b, 1, parameters["j"], parameters["jpm"], 0, 0] for a, b in sorted(bonds)]
    j2, jpm2 = parameters.get("j2", 0), parameters.get("jpm2", 0)
    if j2 or jpm2:
        if family != "ring_second_neighbor":
            raise ValueError("second-neighbor parameters on a non-ring graph")
        second = sorted({tuple(sorted((i, (i + 2) % n))) for i in range(n)})
        edges.extend([a, b, 2, j2, jpm2, 0, 0] for a, b in second)
    if jx_effective or jy_effective:
        edges.extend([n, i, 0, 0, 0, jx_effective, jy_effective] for i in range(n))
    return nodes, np.asarray(edges, dtype=float)
