"""Reproducible h_z resonance study for the clean single-pixel ZZ ring.

This module deliberately implements the ``h_z0 = 0`` case separately from
older project scripts whose convention was ``h_z0 = h_z``.  ``N`` always means
the number of detector spins; the full system has ``N + 1`` spins.  The
physical collective scale is fixed at ``Jx = 0.01`` and each XX edge has
coefficient ``Jx / sqrt(N)``.

The project Hamiltonian convention is

    H = -h_z sum_i Z_i - J sum_i Z_i Z_{i+1}
        - Jx/sqrt(N) X_0 sum_i X_i ,

with no central field.  The overall signs do not change the resonance lines
or the wrapped-Gaussian variance used here.  With h_z0=0 the exact X_0-sector
reduction is used: H_+/- = H_D +/- g sum_i X_i, U00=(U_++U_-)/2 and
U10=(U_+-U_-)/2.  This is equivalent to the full Hamiltonian propagation but
keeps the largest dense matrices at detector dimension 2**N.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from typing import Any

import numpy as np
from scipy import linalg, optimize, special

from collapse.analysis import evolution_subblocks_from_eigenbasis
from collapse.born import born_ratio_from_radii
try:  # QuSpin is preferred; its compiled extension is unavailable on some Windows installs.
    from collapse.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin as _SinglePixelHamiltonian
    HAMILTONIAN_BACKEND = "quspin"
    # ``use_symmetry`` exists only on the QuSpin generator.  This study needs the
    # full basis so that the central-qubit slices of ``(U00, U10)`` stay local to
    # the relative-evolution pencil.
    _FULL_BASIS_KWARGS: dict[str, Any] = {"use_symmetry": False}
except ImportError:
    from collapse.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy as _SinglePixelHamiltonian
    HAMILTONIAN_BACKEND = "numpy_fallback_quspin_extension_unavailable"
    # The dense NumPy generator has no sector machinery, so it already *is* the
    # full-basis construction that ``use_symmetry=False`` selects on QuSpin.
    # Passing the flag would raise TypeError and kill this fallback path.
    _FULL_BASIS_KWARGS: dict[str, Any] = {}
from collapse.level_spacing import (
    compute_unfolded_spacings,
    mean_level_spacing_ratio,
    poisson_spacing_distribution,
    wigner_spacing_distribution,
)


REQUIRED_JX = 0.01
SOLVE_CONDITION_LIMIT = 1.0e10
PHI_UNDEFINED_RADIUS = 1.0e-12
LONG_TIME_LOWER_BOUND = 1.0e3


@dataclass(frozen=True)
class StudyConfig:
    detector_n: int
    hz: float
    times: tuple[float, ...]
    j: float = 1.0
    jx: float = REQUIRED_JX
    hz0: float = 0.0
    seed: int = 20260712

    @property
    def detector_dimension(self) -> int:
        return 2 ** self.detector_n

    @property
    def full_dimension(self) -> int:
        return 2 ** (self.detector_n + 1)

    @property
    def edge_jx(self) -> float:
        return self.jx / np.sqrt(self.detector_n)


@dataclass
class RelativeData:
    eigenvalues: np.ndarray
    theta: np.ndarray
    phi: np.ndarray
    condition_number: float
    solve_residual: float
    eigen_residual_max: float
    solver: str
    infinite_count: int


def detector_energies(n: int, hz: float, j: float = 1.0) -> np.ndarray:
    """Return the diagonal energies of the project's periodic ZZ detector."""
    if n < 3:
        raise ValueError("The periodic-ZZ resonance formula is used only for N >= 3")
    states = np.arange(2**n, dtype=np.int64)
    z = np.empty((n, states.size), dtype=np.float64)
    for site in range(n):
        z[site] = 1.0 - 2.0 * ((states >> (n - 1 - site)) & 1)
    energy = -hz * np.sum(z, axis=0)
    for site in range(n):
        energy -= j * z[site] * z[(site + 1) % n]
    return energy


def relative_data(u00: np.ndarray, u10: np.ndarray, *, condition_limit: float = SOLVE_CONDITION_LIMIT) -> RelativeData:
    """Obtain M eigenvalues using a solve or a generalized pencil if needed."""
    cond = float(np.linalg.cond(u00))
    if np.isfinite(cond) and cond <= condition_limit:
        matrix = np.linalg.solve(u00, u10)
        solve_residual = float(np.linalg.norm(u00 @ matrix - u10) / max(np.linalg.norm(u10), np.finfo(float).tiny))
        vals, vecs = np.linalg.eig(matrix)
        residuals = np.linalg.norm(matrix @ vecs - vecs * vals[np.newaxis, :], axis=0)
        residuals /= np.maximum(np.linalg.norm(vecs, axis=0) * np.maximum(1.0, np.abs(vals)), np.finfo(float).tiny)
        solver = "solve"
        infinite_count = 0
    else:
        # A projectively correct fallback: finite roots solve U10 v=lambda U00 v.
        alpha_beta, vecs = linalg.eig(u10, u00, homogeneous_eigvals=True, check_finite=False)
        alpha, beta = alpha_beta
        finite = np.abs(beta) > np.finfo(float).eps * np.maximum(1.0, np.abs(alpha))
        vals = np.empty(alpha.size, dtype=np.complex128)
        vals[finite] = alpha[finite] / beta[finite]
        vals[~finite] = np.inf + 0j
        finite_residual = np.linalg.norm(u10 @ vecs[:, finite] - (u00 @ vecs[:, finite]) * vals[finite][np.newaxis, :], axis=0) if np.any(finite) else np.array([0.0])
        residuals = finite_residual / max(np.linalg.norm(u10), np.finfo(float).tiny)
        solve_residual = float("nan")
        solver = "generalized_eig"
        infinite_count = int(np.count_nonzero(~finite))

    radii = np.abs(vals)
    theta = np.where(np.isfinite(radii), 2.0 * np.arctan(radii), np.pi)
    phi = np.angle(vals)
    phi[radii <= PHI_UNDEFINED_RADIUS] = np.nan
    return RelativeData(
        eigenvalues=vals,
        theta=theta,
        phi=phi,
        condition_number=cond,
        solve_residual=solve_residual,
        eigen_residual_max=float(np.max(residuals)),
        solver=solver,
        infinite_count=infinite_count,
    )


def wrapped_variance(hz: float, t: float, *, j: float = 1.0, jx: float = REQUIRED_JX) -> float:
    """Equation (7.8) of four_model_finite_time_eigenvalue_derivation."""
    def f(omega: float) -> float:
        return t * t if abs(omega) < 1.0e-14 else 2.0 * (1.0 - np.cos(omega * t)) / omega**2
    v = 0.5 * f(2.0 * hz) + 0.25 * f(2.0 * hz + 4.0 * j) + 0.25 * f(2.0 * hz - 4.0 * j)
    return float(4.0 * jx**2 * v)


def folded_wrapped_gaussian(theta: np.ndarray, variance: float, harmonics: int = 400) -> np.ndarray:
    """Normalized density on dtheta in [0, pi], Eq. (7.1)."""
    theta = np.asarray(theta, dtype=float)
    if variance <= 1.0e-14:
        return np.zeros_like(theta)
    if variance < 0.05:
        # The Fourier series converges very slowly for a narrow peak and a
        # finite truncation develops unphysical Gibbs oscillations.  The
        # equivalent image sum is exponentially convergent in this regime.
        images = np.arange(-3, 4, dtype=float)
        offsets = theta[None, :] + 2.0 * np.pi * images[:, None]
        wrapped = np.sum(np.exp(-0.5 * offsets**2 / variance), axis=0) / np.sqrt(2.0 * np.pi * variance)
        return 2.0 * wrapped
    n = np.arange(1, harmonics + 1, dtype=float)
    terms = np.exp(-0.5 * variance * n * n)[:, None] * np.cos(n[:, None] * theta[None, :])
    return (1.0 + 2.0 * np.sum(terms, axis=0)) / np.pi


def folded_wrapped_gaussian_bin_density(edges: np.ndarray, variance: float, harmonics: int = 800) -> np.ndarray:
    """Return exact bin-averaged density, including narrow endpoint peaks."""
    edges = np.asarray(edges, dtype=float)
    lower, upper = edges[:-1], edges[1:]
    if variance <= 1.0e-14:
        result = np.zeros_like(lower)
        result[0] = 1.0 / (upper[0] - lower[0])
        return result
    if variance < 1.0:
        sigma = np.sqrt(variance)
        probabilities = np.zeros_like(lower)
        for image in range(-5, 6):
            shift = 2.0 * np.pi * image
            probabilities += special.ndtr((upper + shift) / sigma) - special.ndtr((lower + shift) / sigma)
            probabilities += special.ndtr((-lower + shift) / sigma) - special.ndtr((-upper + shift) / sigma)
    else:
        n = np.arange(1, harmonics + 1, dtype=float)
        coefficients = np.exp(-0.5 * variance * n * n) / n
        probabilities = (upper - lower) / np.pi
        probabilities += (2.0 / np.pi) * np.sum(
            coefficients[:, None] * (np.sin(n[:, None] * upper) - np.sin(n[:, None] * lower)), axis=0,
        )
    probabilities = np.maximum(probabilities, 0.0)
    probabilities /= probabilities.sum()
    return probabilities / (upper - lower)


def _hist_density(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    width = np.diff(edges)
    return counts / max(values.size, 1) / width


def _circular_statistics(phi: np.ndarray) -> dict[str, float]:
    finite = phi[np.isfinite(phi)]
    if finite.size == 0:
        return {"phi_n": 0, "phi_mean": float("nan"), "phi_resultant": float("nan"), "phi_variance": float("nan"), "phi_rayleigh_p": float("nan"), "phi_harmonic_2": float("nan")}
    mean_vector = np.mean(np.exp(1j * finite))
    resultant = float(abs(mean_vector))
    rayleigh_z = finite.size * resultant**2
    # Standard leading Rayleigh approximation, reported as a diagnostic only.
    return {
        "phi_n": int(finite.size),
        "phi_mean": float(np.angle(mean_vector)),
        "phi_resultant": resultant,
        "phi_variance": float(1.0 - resultant),
        "phi_rayleigh_p": float(np.exp(-rayleigh_z)),
        "phi_harmonic_2": float(abs(np.mean(np.exp(2j * finite)))),
    }


def _spacing_metrics(levels: np.ndarray) -> dict[str, float]:
    unfolded = compute_unfolded_spacings(levels, tol=1e-9, degree=3, trim_fraction=0.1)
    if unfolded.size < 8:
        return {"detector_resolved_levels": int(np.unique(np.round(levels, 9)).size), "spacing_count": int(unfolded.size), "mean_r": float("nan"), "spacing_l1_poisson": float("nan"), "spacing_l1_goe": float("nan"), "spacing_l1_gue": float("nan")}
    edges = np.linspace(0.0, max(3.5, float(np.quantile(unfolded, 0.99))), 31)
    center = (edges[:-1] + edges[1:]) / 2.0
    density = _hist_density(unfolded, edges)
    dx = np.diff(edges)
    return {
        "detector_resolved_levels": int(np.unique(np.round(levels, 9)).size),
        "spacing_count": int(unfolded.size),
        "mean_r": float(mean_level_spacing_ratio(levels, tol=1e-9)),
        "spacing_l1_poisson": float(np.sum(np.abs(density - poisson_spacing_distribution(center)) * dx)),
        "spacing_l1_goe": float(np.sum(np.abs(density - wigner_spacing_distribution(center, beta=1)) * dx)),
        "spacing_l1_gue": float(np.sum(np.abs(density - wigner_spacing_distribution(center, beta=2)) * dx)),
    }


def detector_sector_spectrum(n: int, hz: float, j: float = 1.0) -> tuple[np.ndarray, dict[str, Any]]:
    """Diagonalise one explicitly resolved detector symmetry sector.

    The periodic clean detector always has translation and reflection symmetry.
    At zero longitudinal field it additionally has global spin inversion.  We
    use the real ``k=0, p=+1`` sector and add ``z=+1`` only when it commutes
    with the Hamiltonian.  This avoids combining independent sectors in the
    spacing diagnostic.
    """
    try:
        from quspin.basis import spin_basis_1d
        from quspin.operators import hamiltonian
    except ImportError:
        return np.array([], dtype=float), {"status": "unavailable", "reason": "QuSpin import failed"}
    blocks: dict[str, int] = {"kblock": 0, "pblock": 1}
    if abs(hz) < 1.0e-14:
        blocks["zblock"] = 1
    basis = spin_basis_1d(n, **blocks)
    static = [
        ["zz", [[-j, site, (site + 1) % n] for site in range(n)]],
        ["z", [[-hz, site] for site in range(n)]],
    ]
    operator = hamiltonian(
        static, [], basis=basis, dtype=np.float64,
        check_herm=False, check_symm=False, check_pcon=False,
    )
    levels = np.asarray(operator.eigvalsh(), dtype=float)
    return levels, {
        "status": "completed", "basis": "spin_basis_1d", "blocks": blocks,
        "dimension": int(basis.Ns), "sectors_combined": False,
    }


def _angular_metrics(theta: np.ndarray, eigenvalues: np.ndarray, *, bins: int = 48) -> dict[str, float]:
    edges = np.linspace(0.0, np.pi, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0
    p_theta = _hist_density(theta, edges)
    p_reflected = _hist_density(np.pi - theta, edges)
    denominator = p_theta + p_reflected
    ratio = np.divide(p_theta, denominator, out=np.full_like(p_theta, np.nan), where=denominator > 0)
    born = np.cos(centers / 2.0) ** 2
    valid = np.isfinite(ratio)
    radii = np.abs(eigenvalues)
    finite = np.isfinite(radii)
    metric = born_ratio_from_radii(radii[finite], n_theta=100)
    return {
        "S_born": float(metric.similarity),
        "born_rmse": float(np.sqrt(np.mean((ratio[valid] - born[valid]) ** 2))) if np.any(valid) else float("nan"),
        "born_l1_mean": float(np.sum(np.abs(ratio[valid] - born[valid]) * np.diff(edges)[valid]) / np.pi) if np.any(valid) else float("nan"),
        "angular_asymmetry_l1_half": float(np.sum(np.abs(p_theta - p_reflected) * np.diff(edges)) / 2.0),
        "angular_normalization_error": float(abs(np.sum(p_theta * np.diff(edges)) - 1.0)),
    }


def _runtime_metadata() -> dict[str, Any]:
    distributions = {}
    for name in ("quspin", "quspin-extensions", "numpy", "scipy", "matplotlib"):
        try:
            distributions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            distributions[name] = "not-installed"
    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5,
        )
        git_value = git_commit.stdout.strip() if git_commit.returncode == 0 else "unavailable: invalid restored .git metadata"
    except (OSError, subprocess.SubprocessError):
        git_value = "unavailable"
    return {
        "python": sys.version,
        "distributions": distributions,
        "numpy_module": np.__version__,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "git_commit": git_value,
        "git_dirty_state": "unavailable because restored .git metadata is invalid" if git_value.startswith("unavailable") else "not-recorded",
    }


def _fit_variance(theta: np.ndarray, initial: float) -> tuple[float, float]:
    finite = theta[np.isfinite(theta)]
    if finite.size < 8:
        return float("nan"), float("nan")
    def objective(log_variance: float) -> float:
        density = folded_wrapped_gaussian(finite, float(np.exp(log_variance)))
        return float(-np.sum(np.log(np.maximum(density, 1e-300))))
    result = optimize.minimize_scalar(objective, bounds=(np.log(1e-8), np.log(100.0)), method="bounded")
    # Curvature-based uncertainty is only diagnostic because time samples correlate.
    step = 1e-3
    curvature = (objective(result.x + step) - 2 * objective(result.x) + objective(result.x - step)) / step**2
    sigma_log = float(np.sqrt(1.0 / curvature)) if curvature > 0 else float("nan")
    return float(np.exp(result.x)), float(np.exp(result.x) * sigma_log)


def run_case(config: StudyConfig, output_dir: Path) -> dict[str, Any]:
    """Run one (N,hz) case, save raw per-time arrays, and return one summary record."""
    if config.jx != REQUIRED_JX or config.j != 1.0 or config.hz0 != 0.0:
        raise ValueError("Main study is fixed to J=1, Jx=0.01, hz0=0; use a separately labelled validation study for changes.")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    # The production path constructs the existing canonical single-pixel
    # Hamiltonian.  The conditional reduction above remains an independent
    # small-system validation route, not a second Hamiltonian implementation.
    full_hamiltonian = _SinglePixelHamiltonian(
        N_pixel=config.detector_n,
        J=config.j,
        Jpm=0.0,
        Jx=config.edge_jx,
        Jy=0.0,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=config.hz,
        hx0=0.0,
        hz0=0.0,
        connectivity="ring",
        central_coupling="all",
        **_FULL_BASIS_KWARGS,
    ).generate()
    build_seconds = time.perf_counter() - started
    t_diag = time.perf_counter()
    full_levels, full_vectors = linalg.eigh(full_hamiltonian, check_finite=False)
    diagonalization_seconds = time.perf_counter() - t_diag
    detector_levels = detector_energies(config.detector_n, config.hz, config.j)
    detector_sector_levels, detector_sector = detector_sector_spectrum(config.detector_n, config.hz, config.j)

    all_theta: list[np.ndarray] = []
    all_phi: list[np.ndarray] = []
    all_lambda: list[np.ndarray] = []
    condition_numbers: list[float] = []
    solve_residuals: list[float] = []
    eig_residuals: list[float] = []
    theory_variances: list[float] = []
    fitted_variances: list[float] = []
    fitted_uncertainties: list[float] = []
    solvers: list[str] = []
    infinite_count = 0
    time_rows: list[dict[str, Any]] = []

    for time_value in config.times:
        t_prop = time.perf_counter()
        u00, u10 = evolution_subblocks_from_eigenbasis(full_levels, full_vectors, time_value)
        data = relative_data(u00, u10)
        propagation_seconds = time.perf_counter() - t_prop
        variance = wrapped_variance(config.hz, time_value, j=config.j, jx=config.jx)
        fitted, fitted_uncertainty = _fit_variance(data.theta, variance)
        np.savez_compressed(
            output_dir / f"raw_N{config.detector_n}_hz{config.hz:+.3f}_t{time_value:.12g}.npz",
            eigenvalues=data.eigenvalues,
            theta=data.theta,
            phi=data.phi,
            condition_number=data.condition_number,
            solve_residual=data.solve_residual,
            eigen_residual_max=data.eigen_residual_max,
            theory_variance=variance,
            fitted_variance=fitted,
        )
        all_lambda.append(data.eigenvalues)
        all_theta.append(data.theta)
        all_phi.append(data.phi)
        condition_numbers.append(data.condition_number)
        solve_residuals.append(data.solve_residual)
        eig_residuals.append(data.eigen_residual_max)
        theory_variances.append(variance)
        fitted_variances.append(fitted)
        fitted_uncertainties.append(fitted_uncertainty)
        solvers.append(data.solver)
        infinite_count += data.infinite_count
        time_rows.append({"t": time_value, "propagation_and_extraction_s": propagation_seconds, "condition_number": data.condition_number, "solve_residual": data.solve_residual, "eigen_residual_max": data.eigen_residual_max, "solver": data.solver, "infinite_eigenvalues": data.infinite_count, "theory_variance": variance, "fitted_variance": fitted, "fitted_variance_diagnostic_se": fitted_uncertainty})
        time_rows[-1].update(_angular_metrics(data.theta, data.eigenvalues))
        time_rows[-1].update(_circular_statistics(data.phi))

    theta = np.concatenate(all_theta)
    phi = np.concatenate(all_phi)
    eigenvalues = np.concatenate(all_lambda)
    edges = np.linspace(0.0, np.pi, 49)
    p_theta = _hist_density(theta, edges)
    p_reflected = _hist_density(np.pi - theta, edges)
    centers = (edges[:-1] + edges[1:]) / 2.0
    ratio = p_theta / np.maximum(p_theta + p_reflected, np.finfo(float).tiny)
    born = np.cos(centers / 2.0) ** 2
    angular_asymmetry = float(np.sum(np.abs(p_theta - p_reflected) * np.diff(edges)) / 2.0)
    born_rmse = float(np.sqrt(np.mean((ratio - born) ** 2)))
    born_l1 = float(np.sum(np.abs(ratio - born) * np.diff(edges)) / np.pi)
    radii = np.abs(eigenvalues)
    finite_lambda = np.isfinite(radii)
    # Project-standard S_Born, based on paired theta and pi-theta samples.
    born_metric = born_ratio_from_radii(radii[finite_lambda], n_theta=100)
    theta_finite = theta[finite_lambda]
    phi_stats = _circular_statistics(phi)
    # phi is undefined at lambda=0, but the associated Bloch state is the
    # physical north pole.  Use an arbitrary zero azimuth only for that
    # coordinate reconstruction, never for circular statistics.
    phi_for_bloch = np.nan_to_num(phi[finite_lambda], nan=0.0)
    bloch_x = np.sin(theta_finite) * np.cos(phi_for_bloch)
    bloch_y = np.sin(theta_finite) * np.sin(phi_for_bloch)
    bloch_z = np.cos(theta_finite)
    norm_error = float(np.max(np.abs(np.sqrt(bloch_x**2 + bloch_y**2 + bloch_z**2) - 1.0))) if bloch_x.size else float("nan")
    spacing = _spacing_metrics(detector_sector_levels)
    np.savez_compressed(output_dir / "aggregate.npz", theta=theta, phi=phi, eigenvalues=eigenvalues, detector_spectrum=detector_levels, detector_sector_spectrum=detector_sector_levels, full_spectrum=full_levels, theta_edges=edges, p_theta=p_theta, p_reflected=p_reflected, born_ratio=ratio, bloch_x=bloch_x, bloch_y=bloch_y, bloch_z=bloch_z)

    long_indices = [index for index, value in enumerate(config.times) if value > LONG_TIME_LOWER_BOUND]
    long_time_summary: dict[str, Any] | None = None
    if long_indices:
        block_hist = np.stack([_hist_density(all_theta[index], edges) for index in long_indices])
        block_reflected = np.stack([_hist_density(np.pi - all_theta[index], edges) for index in long_indices])
        long_p = block_hist.mean(axis=0)
        long_reflected = block_reflected.mean(axis=0)
        long_se = block_hist.std(axis=0, ddof=1) / np.sqrt(len(long_indices)) if len(long_indices) > 1 else np.full(edges.size - 1, np.nan)
        long_denominator = long_p + long_reflected
        long_ratio = np.divide(long_p, long_denominator, out=np.full_like(long_p, np.nan), where=long_denominator > 0)
        pooled_theta = np.concatenate([all_theta[index] for index in long_indices])
        pooled_eigenvalues = np.concatenate([all_lambda[index] for index in long_indices])
        long_time_summary = {
            "definition": f"equal-weight average of per-time densities for t>{LONG_TIME_LOWER_BOUND:g}",
            "time_count": len(long_indices),
            "times": [config.times[index] for index in long_indices],
            **_angular_metrics(pooled_theta, pooled_eigenvalues),
        }
        if len(long_indices) >= 4:
            even = block_hist[::2].mean(axis=0)
            odd = block_hist[1::2].mean(axis=0)
            long_time_summary["alternate_grid_l1"] = float(np.sum(np.abs(even - odd) * np.diff(edges)))
        else:
            long_time_summary["alternate_grid_l1"] = float("nan")
        later = [index for index in long_indices if config.times[index] > 1.0e4]
        long_time_summary["lower_edge_sensitivity_l1"] = float(
            np.sum(np.abs(long_p - np.stack([_hist_density(all_theta[index], edges) for index in later]).mean(axis=0)) * np.diff(edges))
        ) if later else float("nan")
        long_time_summary["binning_born_rmse"] = {
            str(bin_count): _angular_metrics(pooled_theta, pooled_eigenvalues, bins=bin_count)["born_rmse"]
            for bin_count in (32, 48, 64)
        }
        np.savez_compressed(
            output_dir / "long_time_average.npz", times=np.asarray(long_time_summary["times"]),
            theta_edges=edges, p_theta=long_p, p_theta_time_se=long_se,
            p_reflected=long_reflected, born_ratio=long_ratio,
        )
        (output_dir / "long_time_summary.json").write_text(json.dumps(long_time_summary, indent=2), encoding="utf-8")

    summary: dict[str, Any] = {
        "N": config.detector_n, "dimension_detector": config.detector_dimension, "dimension_full": config.full_dimension, "hamiltonian_backend": HAMILTONIAN_BACKEND,
        "hz": config.hz, "hz0": config.hz0, "J": config.j, "Jx": config.jx, "effective_edge_Jx": config.edge_jx,
        "time_start": min(config.times), "time_end": max(config.times), "time_count": len(config.times),
        "eigenvalue_count": int(theta.size), "finite_eigenvalue_count": int(np.count_nonzero(finite_lambda)), "infinite_eigenvalue_count": infinite_count,
        "condition_number_max": float(np.nanmax(condition_numbers)), "condition_number_median": float(np.nanmedian(condition_numbers)),
        "solve_residual_max": float(np.nanmax(solve_residuals)), "eigen_residual_max": float(np.nanmax(eig_residuals)),
        "angular_normalization_error": float(abs(np.sum(p_theta * np.diff(edges)) - 1.0)), "angular_asymmetry_l1_half": angular_asymmetry,
        "S_born": float(born_metric.similarity), "born_rmse": born_rmse, "born_l1_mean": born_l1, "bloch_norm_error_max": norm_error,
        "theory_variance_median": float(np.median(theory_variances)), "fit_variance_median": float(np.nanmedian(fitted_variances)), "fit_variance_diagnostic_se_median": float(np.nanmedian(fitted_uncertainties)),
        "build_seconds": build_seconds, "diagonalization_seconds": diagonalization_seconds, "runtime_seconds": time.perf_counter() - started,
        "solver_methods": ";".join(sorted(set(solvers))), "status": "completed", "warnings": "detector level statistics mix unresolved translation/reflection sectors; classify as inconclusive",
        **phi_stats, **spacing, "detector_spacing_sector": detector_sector,
        "long_time_summary": long_time_summary, "time_diagnostics": time_rows,
    }
    runtime = _runtime_metadata()
    (output_dir / "metadata.json").write_text(json.dumps({"config": asdict(config), "summary": summary, "runtime": runtime}, indent=2, default=str), encoding="utf-8")
    with (output_dir / "time_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = sorted({key for row in time_rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(time_rows)
    return summary


def write_summary(records: list[dict[str, Any]], path: Path) -> None:
    """Write flat run-level CSV plus JSON with the complete time diagnostics."""
    path.parent.mkdir(parents=True, exist_ok=True)
    (path.with_suffix(".json")).write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")
    flattened = [{key: value for key, value in row.items() if key != "time_diagnostics"} for row in records]
    fields = sorted({key for row in flattened for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(flattened)
