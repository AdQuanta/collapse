"""Deterministic wrapped-Gaussian reanalysis of the relative-scale Zeus run.

All stored eigenvalues and algebraic multiplicities are retained.  No
resampling, inferential statistics, or randomized numerical procedure is used.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from scipy import optimize, signal, special


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv_typed(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            row: dict[str, Any] = {}
            for key, value in raw.items():
                if value == "":
                    row[key] = None
                elif value == "True":
                    row[key] = True
                elif value == "False":
                    row[key] = False
                else:
                    try:
                        row[key] = float(value)
                    except ValueError:
                        row[key] = value
            rows.append(row)
    return rows


def resolve(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def finite_number(value: float | None) -> float | None:
    if value is None:
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def circular_difference(left: float, right: float, period: float) -> float:
    return float((left - right + period / 2.0) % period - period / 2.0)


@dataclass(frozen=True)
class Regime:
    case_id: str
    regime: str
    description: str
    hz: float
    j: float
    jpm: float


@dataclass(frozen=True)
class RawRecord:
    regime: Regime
    detector_n: int
    raw_path: Path
    metadata_path: Path


@dataclass(frozen=True)
class WrappedGaussianFit:
    mu: float
    sigma: float
    fourier_discrepancy: float
    maximum_harmonic_mismatch: float
    empirical_moments: np.ndarray
    fitted_moments: np.ndarray
    residuals: np.ndarray
    optimizer_success: bool
    optimizer_method: str
    optimizer_message: str
    optimizer_iterations: int
    initialization_objective_spread: float


class RawInventory:
    def __init__(self, source: Path, campaign: Path):
        self.source = source
        cases = load_json(campaign)["cases"]
        self.regimes = [
            Regime(
                case_id=str(item["case_id"]),
                regime=str(item["regime"]),
                description=str(item["description"]),
                hz=float(item["hz"]),
                j=float(item["J"]),
                jpm=float(item["Jpm"]),
            )
            for item in cases
        ]

    def match(self, hz: float, j: float, jpm: float) -> Regime:
        matches = [
            item
            for item in self.regimes
            if np.allclose((item.hz, item.j, item.jpm), (hz, j, jpm), rtol=0.0, atol=1e-12)
        ]
        if len(matches) != 1:
            raise RuntimeError(f"parameter tuple {(hz, j, jpm)} matched {len(matches)} regimes")
        return matches[0]

    def discover(self) -> list[RawRecord]:
        records: list[RawRecord] = []
        for path in sorted((self.source / "raw").rglob("spectrum_t1000000.npz")):
            with np.load(path, allow_pickle=False) as raw:
                regime = self.match(float(raw["hz"]), float(raw["J"]), float(raw["Jpm"]))
                detector_n = int(raw["detector_n"])
            records.append(regime and RawRecord(regime, detector_n, path, path.with_name("metadata.json")))
        keys = [(item.detector_n, item.regime.case_id) for item in records]
        if len(keys) != len(set(keys)):
            raise RuntimeError("duplicate raw files were discovered for the same (N, regime)")
        return records


class WrappedGaussian:
    def __init__(self, period: float, sigma_bounds: tuple[float, float], weights: str):
        self.period = float(period)
        self.sigma_bounds = sigma_bounds
        if weights != "inverse_square":
            raise ValueError("only the pre-registered inverse-square weights are supported")

    def moments(self, angles: np.ndarray, nmax: int) -> np.ndarray:
        n = np.arange(1, nmax + 1, dtype=float)
        return np.mean(np.exp(1j * 2.0 * np.pi * angles[:, None] * n[None, :] / self.period), axis=0)

    def model_moments(self, mu: float, sigma: float, nmax: int) -> np.ndarray:
        n = np.arange(1, nmax + 1, dtype=float)
        omega = 2.0 * np.pi * n / self.period
        return np.exp(1j * omega * mu) * np.exp(-0.5 * (omega * sigma) ** 2)

    def fit(self, angles: np.ndarray, nmax: int) -> WrappedGaussianFit:
        empirical = self.moments(angles, nmax)
        n = np.arange(1, nmax + 1, dtype=float)
        weights = 1.0 / n**2
        lower, upper = self.sigma_bounds

        mu_grid = np.linspace(0.0, self.period, 64, endpoint=False)
        sigma_grid = np.geomspace(lower, upper, 32)
        phase = np.exp(1j * 2.0 * np.pi * mu_grid[:, None] * n[None, :] / self.period)
        damping = np.exp(
            -0.5
            * (
                2.0
                * np.pi
                * sigma_grid[:, None]
                * n[None, :]
                / self.period
            )
            ** 2
        )
        candidates = damping[:, None, :] * phase[None, :, :]
        objectives = np.sum(weights[None, None, :] * np.abs(empirical - candidates) ** 2, axis=2)
        flat_order = np.argsort(objectives, axis=None)[:6]

        def objective(vector: np.ndarray) -> float:
            mu = float(vector[0] % self.period)
            sigma = float(math.exp(vector[1]))
            model = self.model_moments(mu, sigma, nmax)
            return float(np.sum(weights * np.abs(empirical - model) ** 2))

        results: list[tuple[str, optimize.OptimizeResult]] = []
        for flat_index in flat_order:
            s_index, m_index = np.unravel_index(flat_index, objectives.shape)
            results.append(
                (
                    "L-BFGS-B",
                    optimize.minimize(
                        objective,
                        x0=np.array([mu_grid[m_index], math.log(sigma_grid[s_index])]),
                        method="L-BFGS-B",
                        bounds=((0.0, self.period), (math.log(lower), math.log(upper))),
                        options={"ftol": 1e-14, "gtol": 1e-10, "maxiter": 1000},
                    ),
                )
            )
        preliminary = min(results, key=lambda item: float(item[1].fun))[1]
        if not bool(preliminary.success):
            # L-BFGS-B can report line-search precision loss after reaching a
            # stable minimum.  A bounded, derivative-free Powell refinement
            # supplies an independent deterministic convergence check.
            results.append(
                (
                    "Powell fallback",
                    optimize.minimize(
                        objective,
                        x0=np.asarray(preliminary.x, dtype=float),
                        method="Powell",
                        bounds=((0.0, self.period), (math.log(lower), math.log(upper))),
                        options={"xtol": 1e-12, "ftol": 1e-14, "maxiter": 2000},
                    ),
                )
            )
        successful = [item for item in results if bool(item[1].success)]
        method, best = min(successful or results, key=lambda item: float(item[1].fun))
        mu = float(best.x[0] % self.period)
        sigma = float(math.exp(best.x[1]))
        fitted = self.model_moments(mu, sigma, nmax)
        residuals = empirical - fitted
        converged_objectives = [
            float(item.fun) for _, item in results if math.isfinite(float(item.fun))
        ]
        spread = max(converged_objectives) - min(converged_objectives)
        return WrappedGaussianFit(
            mu=mu,
            sigma=sigma,
            fourier_discrepancy=float(np.sum(weights * np.abs(residuals) ** 2)),
            maximum_harmonic_mismatch=float(np.max(np.abs(residuals))),
            empirical_moments=empirical,
            fitted_moments=fitted,
            residuals=residuals,
            optimizer_success=bool(best.success),
            optimizer_method=method,
            optimizer_message=str(best.message),
            optimizer_iterations=int(best.nit),
            initialization_objective_spread=float(spread),
        )

    def bin_probabilities(
        self,
        edges: np.ndarray,
        mu: float,
        sigma: float,
        extra_images: int = 0,
    ) -> np.ndarray:
        lower, upper = edges[:-1], edges[1:]
        images = int(math.ceil(9.0 * sigma / self.period)) + 3 + extra_images
        probabilities = np.zeros_like(lower)
        for k in range(-images, images + 1):
            shift = k * self.period
            probabilities += special.ndtr((upper - mu + shift) / sigma)
            probabilities -= special.ndtr((lower - mu + shift) / sigma)
        probabilities = np.maximum(probabilities, 0.0)
        probabilities /= probabilities.sum()
        return probabilities

    def grid_metrics(
        self,
        angles: np.ndarray,
        fit: WrappedGaussianFit,
        bins: int,
    ) -> dict[str, float]:
        edges = np.linspace(0.0, self.period, bins + 1)
        counts, _ = np.histogram(angles, bins=edges)
        empirical = counts / counts.sum()
        model = self.bin_probabilities(edges, fit.mu, fit.sigma)
        width = self.period / bins
        return {
            "real_space_l1": float(np.sum(np.abs(empirical - model))),
            "real_space_linf_density": float(np.max(np.abs(empirical - model)) / width),
        }

    def circular_transport(
        self,
        angles: np.ndarray,
        fit: WrappedGaussianFit,
        bins: int,
    ) -> float:
        edges = np.linspace(0.0, self.period, bins + 1)
        counts, _ = np.histogram(angles, bins=edges)
        empirical = counts / counts.sum()
        model = self.bin_probabilities(edges, fit.mu, fit.sigma)
        cumulative = np.cumsum(empirical - model)
        offset = float(np.median(cumulative))
        return float((self.period / bins) * np.sum(np.abs(cumulative - offset)))


class DetectorIntegrator:
    def __init__(self, atlas: Path, tolerances: Sequence[float], nonzero_relative: float):
        self.atlas = atlas
        self.tolerances = [float(value) for value in tolerances]
        self.nonzero_relative = float(nonzero_relative)

    @staticmethod
    def group_ids(energies: np.ndarray, tolerance: float) -> np.ndarray:
        output = np.empty(energies.size, dtype=np.int32)
        start = 0
        group = 0
        while start < energies.size:
            stop = start + 1
            while stop < energies.size and energies[stop] - energies[start] <= tolerance:
                stop += 1
            output[start:stop] = group
            start = stop
            group += 1
        return output

    def analyze(self, case_id: str, output: Path, copy_arrays: bool) -> dict[str, Any]:
        source = self.atlas / "regimes" / case_id
        metadata = load_json(source / "metadata.json")
        with np.load(source / "spectral_data.npz", allow_pickle=False) as raw:
            energies = np.asarray(raw["eigenvalues"], dtype=float)
            vab = np.asarray(raw["energy_basis_coupling"])
        magnitude = np.abs(vab)
        total_weight = float(np.sum(magnitude**2))
        threshold = self.nonzero_relative * max(float(np.max(magnitude)), 1.0)
        tolerance_rows: list[dict[str, Any]] = []
        primary: dict[str, Any] | None = None
        for tolerance in self.tolerances:
            ids = self.group_ids(energies, tolerance)
            multiplicities = np.bincount(ids)
            same = ids[:, None] == ids[None, :]
            within_weight = float(np.sum(magnitude[same] ** 2))
            within_values = magnitude[same]
            between_values = magnitude[~same]
            row = {
                "tolerance": tolerance,
                "distinct_energies": int(multiplicities.size),
                "degenerate_subspaces": int(np.count_nonzero(multiplicities > 1)),
                "maximum_multiplicity": int(np.max(multiplicities)),
                "degenerate_state_count": int(np.sum(multiplicities[multiplicities > 1])),
                "f_deg": within_weight / total_weight if total_weight else 0.0,
                "within_frobenius_norm": math.sqrt(within_weight),
                "between_frobenius_norm": math.sqrt(max(total_weight - within_weight, 0.0)),
                "within_max_abs": float(np.max(within_values)),
                "within_rms": float(np.sqrt(np.mean(within_values**2))),
                "within_nonzero_pair_fraction": float(np.mean(within_values > threshold)),
                "between_max_abs": float(np.max(between_values)) if between_values.size else 0.0,
                "between_nonzero_pair_fraction": float(np.mean(between_values > threshold)) if between_values.size else 0.0,
            }
            tolerance_rows.append(row)
            if math.isclose(tolerance, 1e-9, rel_tol=0.0, abs_tol=1e-16):
                # Keep the returned primary summary independent of
                # ``tolerance_rows``.  The latter is embedded below as a
                # sensitivity table, so reusing the same dictionary would
                # create a circular object graph that JSON cannot serialize.
                primary = dict(row)
        if primary is None:
            raise RuntimeError("primary detector tolerance was not evaluated")
        distinct = np.unique(np.round(energies, decimals=9))
        spacings = np.diff(distinct)
        primary.update(
            {
                "detector_n": int(metadata["detector_n"]),
                "detector_dimension": int(metadata["dimension"]),
                "detector_bandwidth": float(np.ptp(energies)),
                "minimum_distinct_spacing": float(np.min(spacings)) if spacings.size else None,
                "median_distinct_spacing": float(np.median(spacings)) if spacings.size else None,
                "near_spacing_fraction_1e6_bandwidth": (
                    float(np.mean(spacings <= 1e-6 * max(float(np.ptp(energies)), 1.0)))
                    if spacings.size
                    else 0.0
                ),
                "validation_passed": bool(metadata["validation"]["passed"]),
                "basis_convention": metadata["basis_convention"],
                "tolerance_sensitivity": tolerance_rows,
            }
        )
        output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / "spectral_heatmaps.png", output / "detector_N11_spectral_heatmaps.png")
        shutil.copy2(source / "degenerate_blocks.csv", output / "detector_N11_degenerate_blocks.csv")
        shutil.copy2(source / "metadata.json", output / "detector_N11_metadata.json")
        if copy_arrays:
            shutil.copy2(source / "spectral_data.npz", output / "detector_N11_spectral_data.npz")
        return primary


class Reanalysis:
    def __init__(self, config: dict[str, Any], output: Path):
        self.config = config
        self.output = output
        self.period = float(config["period"])
        self.model = WrappedGaussian(
            self.period,
            tuple(float(value) for value in config["sigma_bounds"]),
            str(config["fourier_weights"]),
        )
        self.nmax = int(config["fourier_nmax"])
        self.primary_n = int(config["primary_n"])

    @staticmethod
    def reconstruct(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
        nan_mask = np.isnan(values.real) | np.isnan(values.imag)
        infinite_mask = ~nan_mask & (~np.isfinite(values.real) | ~np.isfinite(values.imag))
        valid = ~nan_mask & ~infinite_mask
        finite_values = values[valid]
        radii = np.abs(finite_values)
        theta = 2.0 * np.arctan(radii)
        phi = np.angle(finite_values)
        reconstructed = np.tan(theta / 2.0) * np.exp(1j * phi)
        scale = np.maximum(np.abs(finite_values), 1.0)
        relative = np.abs(reconstructed - finite_values) / scale
        return radii, theta, phi, {
            "stored_count": int(values.size),
            "finite_included_count": int(finite_values.size),
            "nan_excluded_count": int(np.count_nonzero(nan_mask)),
            "infinite_excluded_count": int(np.count_nonzero(infinite_mask)),
            "reconstruction_max_relative_error": float(np.max(relative)) if relative.size else 0.0,
            "zero_eigenvalue_count": int(np.count_nonzero(radii == 0.0)),
        }

    def radial_structure(self, radii: np.ndarray, theta: np.ndarray, fit: WrappedGaussianFit) -> dict[str, Any]:
        rounded = np.round(radii, decimals=12)
        _, multiplicities = np.unique(rounded, return_counts=True)
        positive = radii[radii > 0.0]
        log_values = np.log10(positive) if positive.size else np.array([], dtype=float)
        radial_branches = 0
        if log_values.size and np.ptp(log_values) > 1e-12:
            counts, _ = np.histogram(log_values, bins=96)
            peaks, _ = signal.find_peaks(counts, prominence=max(1.0, 0.05 * counts.max()))
            radial_branches = int(peaks.size)
        theta_counts, _ = np.histogram(theta, bins=np.linspace(0.0, self.period, 129))
        peaks, _ = signal.find_peaks(theta_counts, prominence=max(1.0, 0.05 * theta_counts.max()))
        top_harmonic = int(np.argmax(np.abs(fit.residuals)) + 1)
        atomic_fraction = float(np.max(multiplicities) / radii.size)
        if atomic_fraction >= 0.05:
            dominant = "repeated-radius groups"
        elif peaks.size >= 2 or radial_branches >= 2:
            dominant = "multiple radial/angular branches"
        elif top_harmonic >= 3:
            dominant = f"higher-harmonic deformation (n={top_harmonic})"
        elif float(np.median(theta)) < fit.mu:
            dominant = "excess concentration below the fitted center"
        else:
            dominant = "broad one-peak residual deformation"
        return {
            "radius_min": float(np.min(radii)),
            "radius_median": float(np.median(radii)),
            "radius_q95": float(np.quantile(radii, 0.95)),
            "radius_q99": float(np.quantile(radii, 0.99)),
            "radius_max": float(np.max(radii)),
            "zero_radius_count": int(np.count_nonzero(radii == 0.0)),
            "unique_radius_count_rounded_1e12": int(multiplicities.size),
            "largest_repeated_radius_fraction": atomic_fraction,
            "radial_branch_count": radial_branches,
            "angular_peak_count_fixed_grid": int(peaks.size),
            "dominant_deviation_structure": dominant,
        }

    def one_record(self, record: RawRecord) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        with np.load(record.raw_path, allow_pickle=False) as raw:
            eigenvalues = np.asarray(raw["eigenvalues"], dtype=np.complex128)
            saved_theta = np.asarray(raw["theta"], dtype=float)
        radii, theta, phi, validation = self.reconstruct(eigenvalues)
        saved_finite = saved_theta[np.isfinite(saved_theta)]
        validation["saved_theta_max_abs_error"] = (
            float(np.max(np.abs(saved_finite - theta)))
            if saved_finite.size == theta.size and theta.size
            else None
        )
        fit = self.model.fit(theta, self.nmax)
        grid = self.model.grid_metrics(theta, fit, int(self.config["real_space_bins"]))
        transport = self.model.circular_transport(theta, fit, int(self.config["transport_bins"]))
        structure = self.radial_structure(radii, theta, fit)
        phase_resultant = np.mean(np.exp(1j * phi))

        robustness: dict[str, Any] = {}
        for nmax in self.config["fourier_check_nmax"]:
            check = self.model.fit(theta, int(nmax))
            robustness[f"nmax_{nmax}_mu"] = check.mu
            robustness[f"nmax_{nmax}_sigma"] = check.sigma
            robustness[f"nmax_{nmax}_fourier"] = check.fourier_discrepancy
        for bins in (128, 512):
            check = self.model.grid_metrics(theta, fit, bins)
            robustness[f"grid_{bins}_l1"] = check["real_space_l1"]
            robustness[f"grid_{bins}_linf"] = check["real_space_linf_density"]
        for bins in (2048, 8192):
            robustness[f"transport_{bins}"] = self.model.circular_transport(theta, fit, bins)
        shifted_checks: list[dict[str, float]] = []
        for shift in self.config["origin_shifts"]:
            shifted = (theta + float(shift)) % self.period
            shifted_fit = self.model.fit(shifted, self.nmax)
            shifted_transport = self.model.circular_transport(
                shifted, shifted_fit, int(self.config["transport_bins"])
            )
            shifted_checks.append(
                {
                    "shift": float(shift),
                    "mu_shift_error": abs(
                        circular_difference(shifted_fit.mu, fit.mu + float(shift), self.period)
                    ),
                    "sigma_change": abs(shifted_fit.sigma - fit.sigma),
                    "fourier_change": abs(
                        shifted_fit.fourier_discrepancy - fit.fourier_discrepancy
                    ),
                    "transport_change": abs(shifted_transport - transport),
                }
            )
        robustness["origin_shift_max_mu_error"] = max(item["mu_shift_error"] for item in shifted_checks)
        robustness["origin_shift_max_sigma_change"] = max(item["sigma_change"] for item in shifted_checks)
        robustness["origin_shift_max_fourier_change"] = max(item["fourier_change"] for item in shifted_checks)
        robustness["origin_shift_max_transport_change"] = max(item["transport_change"] for item in shifted_checks)
        edges = np.linspace(0.0, self.period, int(self.config["real_space_bins"]) + 1)
        p_a = self.model.bin_probabilities(edges, fit.mu, fit.sigma, extra_images=0)
        p_b = self.model.bin_probabilities(edges, fit.mu, fit.sigma, extra_images=3)
        robustness["wrapped_sum_max_probability_change"] = float(np.max(np.abs(p_a - p_b)))

        regime_dir = self.output / "regimes" / record.regime.case_id
        regime_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            regime_dir / f"reconstructed_N{record.detector_n}.npz",
            eigenvalues=eigenvalues,
            radius=radii,
            theta=theta,
            phi=phi,
            empirical_moments=fit.empirical_moments,
            wrapped_gaussian_moments=fit.fitted_moments,
            harmonic_residuals=fit.residuals,
        )
        harmonics = [
            {
                "case_id": record.regime.case_id,
                "N": record.detector_n,
                "harmonic": index + 1,
                "empirical_abs": float(abs(fit.empirical_moments[index])),
                "fitted_abs": float(abs(fit.fitted_moments[index])),
                "residual_abs": float(abs(fit.residuals[index])),
                "phase_difference": circular_difference(
                    float(np.angle(fit.empirical_moments[index])),
                    float(np.angle(fit.fitted_moments[index])),
                    2.0 * np.pi,
                ),
            }
            for index in range(self.nmax)
        ]
        top = sorted(harmonics, key=lambda item: item["residual_abs"], reverse=True)[:3]
        row = {
            "case_id": record.regime.case_id,
            "regime": record.regime.regime,
            "description": record.regime.description,
            "N": record.detector_n,
            "hz": record.regime.hz,
            "J": record.regime.j,
            "Jpm": record.regime.jpm,
            "raw_path": str(record.raw_path.relative_to(ROOT)),
            "metadata_path": (
                str(record.metadata_path.relative_to(ROOT))
                if record.metadata_path.is_file()
                else ""
            ),
            **validation,
            "mu": fit.mu,
            "sigma": fit.sigma,
            "fourier_discrepancy": fit.fourier_discrepancy,
            "maximum_harmonic_mismatch": fit.maximum_harmonic_mismatch,
            "circular_transport": transport,
            **grid,
            "optimizer_success": fit.optimizer_success,
            "optimizer_method": fit.optimizer_method,
            "optimizer_message": fit.optimizer_message,
            "optimizer_iterations": fit.optimizer_iterations,
            "initialization_objective_spread": fit.initialization_objective_spread,
            "phase_resultant": float(abs(phase_resultant)),
            "phase_mean": float(np.angle(phase_resultant)),
            "top_harmonics": ",".join(str(item["harmonic"]) for item in top),
            "top_harmonic_residuals": ",".join(f"{item['residual_abs']:.6g}" for item in top),
            **structure,
            **robustness,
        }
        return row, harmonics

    def plot_regime(
        self,
        regime: Regime,
        primary: dict[str, Any],
        all_rows: Sequence[dict[str, Any]],
        detector: dict[str, Any],
    ) -> None:
        regime_dir = self.output / "regimes" / regime.case_id
        with np.load(regime_dir / f"reconstructed_N{self.primary_n}.npz") as raw:
            values = np.asarray(raw["eigenvalues"])
            radii = np.asarray(raw["radius"])
            theta = np.asarray(raw["theta"])
            phi = np.asarray(raw["phi"])
            empirical_moments = np.asarray(raw["empirical_moments"])
            fitted_moments = np.asarray(raw["wrapped_gaussian_moments"])
            residuals = np.asarray(raw["harmonic_residuals"])
        fit = WrappedGaussianFit(
            mu=float(primary["mu"]),
            sigma=float(primary["sigma"]),
            fourier_discrepancy=float(primary["fourier_discrepancy"]),
            maximum_harmonic_mismatch=float(primary["maximum_harmonic_mismatch"]),
            empirical_moments=empirical_moments,
            fitted_moments=fitted_moments,
            residuals=residuals,
            optimizer_success=True,
            optimizer_method=str(primary["optimizer_method"]),
            optimizer_message=str(primary["optimizer_message"]),
            optimizer_iterations=0,
            initialization_objective_spread=0.0,
        )
        plot_bins = int(self.config["plot_bins"])
        edges = np.linspace(0.0, self.period, plot_bins + 1)
        centers = (edges[:-1] + edges[1:]) / 2.0
        counts, _ = np.histogram(theta, bins=edges)
        empirical_probability = counts / counts.sum()
        fitted_probability = self.model.bin_probabilities(edges, fit.mu, fit.sigma)
        density_emp = empirical_probability / np.diff(edges)
        density_fit = fitted_probability / np.diff(edges)

        figure = plt.figure(figsize=(15.5, 14.5), constrained_layout=True)
        grid = figure.add_gridspec(4, 3)
        axes = [figure.add_subplot(grid[i, j], projection="polar" if (i, j) == (1, 1) else None) for i in range(4) for j in range(3)]

        axis = axes[0]
        if values.size > 2000:
            axis.hexbin(values.real, values.imag, gridsize=85, bins="log", mincnt=1, cmap="viridis")
        else:
            axis.scatter(values.real, values.imag, s=4, alpha=0.5)
        axis.set(title=r"raw $\lambda$ plane", xlabel=r"$\Re\lambda$", ylabel=r"$\Im\lambda$")
        real_span = float(np.ptp(values.real))
        imaginary_span = float(np.ptp(values.imag))
        span_ratio = max(real_span, imaginary_span) / max(min(real_span, imaginary_span), 1e-300)
        if span_ratio <= 50.0:
            axis.set_aspect("equal", adjustable="box")
        else:
            axis.set_aspect("auto")
            axis.text(
                0.02,
                0.98,
                rf"anisotropic axes: $\Delta\Re={real_span:.2g}$, $\Delta\Im={imaginary_span:.2g}$",
                transform=axis.transAxes,
                ha="left",
                va="top",
                fontsize=8,
            )

        positive = radii[radii > 0.0]
        axes[1].hist(radii, bins=plot_bins, histtype="stepfilled", alpha=0.75, color="#4c78a8")
        axes[1].set(title=r"complete $|\lambda|$ distribution", xlabel=r"$|\lambda|$", ylabel="count")
        if positive.size:
            axes[2].hist(np.log10(positive), bins=plot_bins, histtype="stepfilled", alpha=0.75, color="#59a14f")
        axes[2].set(title=r"$\log_{10}|\lambda|$ (positive radii)", xlabel=r"$\log_{10}|\lambda|$", ylabel="count")

        axes[3].stairs(density_emp, edges, color="#4c78a8", linewidth=1.4, label=r"$P_{\rm emp}$")
        axes[3].plot(centers, density_fit, color="#e15759", linewidth=1.7, label="best-fit WG")
        axes[3].set(title=rf"$P(\theta)$; $\mu={fit.mu:.3g}$, $\sigma={fit.sigma:.3g}$", xlabel=r"$\theta$", ylabel="density", xlim=(0, self.period))
        axes[3].legend(frameon=False)

        polar = axes[4]
        polar.bar(centers, density_emp, width=np.diff(edges), color="#4c78a8", alpha=0.5)
        polar.plot(centers, density_fit, color="#e15759", linewidth=1.4)
        polar.set_title("polar empirical / WG")

        axes[5].plot(centers, density_emp - density_fit, color="#b279a2")
        axes[5].axhline(0.0, color="0.3", linewidth=0.8)
        axes[5].set(title="fixed-grid density residual", xlabel=r"$\theta$", ylabel=r"$P_{\rm emp}-P_{\rm WG}$", xlim=(0, self.period))

        n = np.arange(1, self.nmax + 1)
        axes[6].plot(n, np.abs(empirical_moments), "o-", ms=3, label="empirical")
        axes[6].plot(n, np.abs(fitted_moments), "s-", ms=3, label="WG")
        axes[6].set(title="circular-moment magnitudes", xlabel="harmonic n", ylabel=r"$|m_n|$", yscale="log")
        axes[6].legend(frameon=False)

        axes[7].stem(n, np.abs(residuals), basefmt=" ")
        axes[7].set(title=rf"harmonic residuals; $D_F={fit.fourier_discrepancy:.3g}$", xlabel="harmonic n", ylabel=r"$|\Delta m_n|$", yscale="log")

        axes[8].hist(phi, bins=int(self.config["phase_bins"]), range=(-np.pi, np.pi), histtype="stepfilled", color="#f28e2b", alpha=0.75)
        axes[8].set(title=r"phase distribution $P(\phi)$", xlabel=r"$\phi$", ylabel="count")

        joint = axes[9].hist2d(theta, phi, bins=(96, 72), range=((0, self.period), (-np.pi, np.pi)), norm=LogNorm(), cmap="magma")
        figure.colorbar(joint[3], ax=axes[9], label="count")
        axes[9].set(title=r"joint $(\theta,\phi)$", xlabel=r"$\theta$", ylabel=r"$\phi$")

        detector_npz = regime_dir / "detector_N11_spectral_data.npz"
        with np.load(detector_npz) as raw:
            detector_energies = np.asarray(raw["eigenvalues"])
        axes[10].plot(np.arange(detector_energies.size), detector_energies, linewidth=0.8)
        axes[10].set(
            title=rf"detector spectrum (N={int(detector['detector_n'])})",
            xlabel="sorted eigenstate index",
            ylabel="energy",
        )

        selected = sorted((row for row in all_rows if row["case_id"] == regime.case_id), key=lambda item: int(item["N"]))
        axes[11].plot([row["N"] for row in selected], [row["fourier_discrepancy"] for row in selected], "o-", color="#4c78a8", label=r"$D_F$")
        axes[11].set(title="available-N stability", xlabel="N", ylabel=r"$D_F$")
        second = axes[11].twinx()
        second.plot([row["N"] for row in selected], [row["sigma"] for row in selected], "s--", color="#e15759", label=r"$\sigma$")
        second.set_ylabel(r"$\sigma$")

        for axis in axes:
            if axis is not polar:
                axis.grid(alpha=0.16)
        figure.suptitle(
            f"{regime.case_id}: {regime.regime}; primary N={self.primary_n}, "
            f"{primary['classification']}",
            fontsize=13,
        )
        figure.savefig(regime_dir / f"wrapped_gaussian_diagnostics_N{self.primary_n}.png", dpi=int(self.config["figure_dpi"]))
        plt.close(figure)

    def cross_regime_plots(self, rows: Sequence[dict[str, Any]]) -> None:
        ordered = sorted(rows, key=lambda item: item["fourier_discrepancy"])
        colors = {"closely wrapped-Gaussian": "#59a14f", "moderately deviating": "#f28e2b", "strongly deviating": "#e15759"}
        figure, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)
        pairs = [
            ("f_deg", "within-degenerate weight fraction"),
            ("maximum_multiplicity", "maximum detector multiplicity"),
            ("minimum_distinct_spacing", "minimum distinct spacing"),
            ("within_frobenius_norm", r"$\|P_gVP_g\|_F$ combined"),
            ("within_nonzero_pair_fraction", "active within-block pair fraction"),
            ("near_spacing_fraction_1e6_bandwidth", "near-spacing fraction"),
        ]
        for axis, (key, label) in zip(axes.ravel(), pairs):
            for row in ordered:
                value = row.get(key)
                if value is None or not math.isfinite(float(value)):
                    continue
                axis.scatter(float(value), row["fourier_discrepancy"], s=30, color=colors[row["classification"]], alpha=0.85)
            axis.set(xlabel=label, ylabel=r"$D_{\rm Fourier}$")
            if key in {"f_deg", "minimum_distinct_spacing", "within_nonzero_pair_fraction", "near_spacing_fraction_1e6_bandwidth"}:
                positive = [float(row[key]) for row in ordered if row.get(key) not in (None, 0.0) and math.isfinite(float(row[key]))]
                if positive and max(positive) / min(positive) > 100:
                    axis.set_xscale("log")
            axis.grid(alpha=0.16)
        handles = [
            plt.Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                color=colors[label],
                label=label,
            )
            for label in colors
        ]
        axes[0, 0].legend(
            handles=handles,
            loc="upper left",
            fontsize=8,
            frameon=True,
        )
        figure.savefig(self.output / "cross_regime_detector_relationships.png", dpi=int(self.config["figure_dpi"]))
        plt.close(figure)

        figure, axis = plt.subplots(figsize=(11, 10), constrained_layout=True)
        y = np.arange(len(ordered))
        axis.barh(y, [row["fourier_discrepancy"] for row in ordered], color=[colors[row["classification"]] for row in ordered])
        axis.set_yticks(y, [row["case_id"] for row in ordered], fontsize=8)
        axis.invert_yaxis()
        axis.set(xlabel=r"$D_{\rm Fourier}$", title="N=16 ordering: closest to farthest from wrapped Gaussian")
        axis.grid(axis="x", alpha=0.16)
        figure.savefig(self.output / "wrapped_gaussian_ordering_N16.png", dpi=int(self.config["figure_dpi"]))
        plt.close(figure)

        case_order = [row["case_id"] for row in ordered]
        available_n = sorted({int(row["N"]) for row in self.all_rows})
        matrix = np.full((len(available_n), len(case_order)), np.nan)
        lookup = {(int(row["N"]), row["case_id"]): row for row in self.all_rows}
        for i, detector_n in enumerate(available_n):
            for j, case in enumerate(case_order):
                if (detector_n, case) in lookup:
                    matrix[i, j] = lookup[(detector_n, case)]["fourier_discrepancy"]
        figure, axis = plt.subplots(figsize=(16, 4.6), constrained_layout=True)
        image = axis.imshow(np.ma.masked_invalid(matrix), aspect="auto", cmap="viridis")
        axis.set_xticks(np.arange(len(case_order)), case_order, rotation=75, ha="right", fontsize=7)
        axis.set_yticks(np.arange(len(available_n)), [f"N={value}" for value in available_n])
        axis.set_title(r"finite-size stability of $D_{\rm Fourier}$ (blank = unavailable)")
        figure.colorbar(image, ax=axis, label=r"$D_{\rm Fourier}$")
        figure.savefig(self.output / "fourier_discrepancy_across_N.png", dpi=int(self.config["figure_dpi"]))
        plt.close(figure)

    def write_report(self, primary: Sequence[dict[str, Any]], inventory: Sequence[RawRecord]) -> None:
        ordered = sorted(primary, key=lambda item: item["fourier_discrepancy"])
        close = ordered[:10]
        strong = ordered[-10:]
        detector_keys = [
            "f_deg",
            "maximum_multiplicity",
            "minimum_distinct_spacing",
            "within_frobenius_norm",
            "within_nonzero_pair_fraction",
            "near_spacing_fraction_1e6_bandwidth",
        ]
        correlations: dict[str, float | None] = {}
        for key in detector_keys:
            pairs = [
                (float(row[key]), float(row["fourier_discrepancy"]))
                for row in ordered
                if row.get(key) is not None and math.isfinite(float(row[key]))
            ]
            correlations[key] = (
                float(np.corrcoef(np.asarray(pairs).T)[0, 1])
                if len(pairs) >= 3 and np.std([value[0] for value in pairs]) > 0
                else None
            )
        counts_by_n = {
            detector_n: sum(item.detector_n == detector_n for item in inventory)
            for detector_n in sorted({item.detector_n for item in inventory})
        }
        maximum_checks = {
            key: max(float(row[key]) for row in self.all_rows if row.get(key) is not None)
            for key in (
                "reconstruction_max_relative_error",
                "saved_theta_max_abs_error",
                "origin_shift_max_mu_error",
                "origin_shift_max_sigma_change",
                "origin_shift_max_fourier_change",
                "origin_shift_max_transport_change",
                "wrapped_sum_max_probability_change",
            )
        }
        lines = [
            "# Deterministic wrapped-Gaussian reanalysis of the relative-scale regimes",
            "",
            "## 1. Executive conclusion",
            "",
            "The common comparison uses all 65,536 stored eigenvalues of each N=16 regime. "
            "From closest to farthest by the pre-registered Fourier discrepancy, the ordering is:",
            "",
            "1. " + " -> ".join(f"`{row['case_id']}`" for row in ordered),
            "",
            "The ten closest regimes are "
            + ", ".join(f"`{row['case_id']}`" for row in close)
            + "; the ten strongest deviations are "
            + ", ".join(f"`{row['case_id']}`" for row in strong)
            + ". Classification is descriptive and uses fixed rank tertiles determined before "
            "joining detector properties.",
            "",
            "## 2. Eigenvalue-to-angle reconstruction",
            "",
            r"For each finite stored eigenvalue, \(r=|\lambda|\), "
            r"\(\theta=2\arctan r\), and \(\phi=\arg\lambda\). The reconstruction "
            r"\(\tan(\theta/2)e^{i\phi}\) was checked against every finite eigenvalue. "
            "Algebraic multiplicities are retained; repeated, conjugate, and symmetry-related "
            "eigenvalues remain separate entries. No Jacobian is applied.",
            "",
            f"The available raw files are {counts_by_n}. N=13--16 are complete at 30 regimes "
            "each; N=17 contains six raw spectra, five of which reached the old metrics checkpoint; "
            "N=18 contains no raw spectrum. NaN or infinite complex values are excluded and counted "
            "explicitly. The reconstructed polar angle lies in [0,pi], and the requested circular "
            "comparison uses period L=2pi with values represented on [0,2pi).",
            "",
            "## 3. Wrapped-Gaussian comparison method",
            "",
            "The normalized reference, evaluated by a converged periodic normal image sum, is",
            "",
            r"\[P_{\rm WG}(\theta|\mu,\sigma)=\frac{1}{\sqrt{2\pi}\sigma}"
            r"\sum_{k\in\mathbb Z}\exp[-(\theta-\mu+2\pi k)^2/(2\sigma^2)].\]",
            "",
            r"Its circular moments are \(m_n^{\rm WG}=\exp(in\mu-n^2\sigma^2/2)\). "
            "The primary deterministic objective is",
            "",
            r"\[D_F=\sum_{n=1}^{32}n^{-2}|m_n^{\rm emp}-m_n^{\rm WG}|^2.\]",
            "",
            "A deterministic 64x32 (mu, sigma) grid supplies six starts to bounded L-BFGS-B; "
            "mu is bounded to [0,2pi] and sigma to [1e-4,4pi]. Termination uses ftol=1e-14, "
            "gtol=1e-10, and at most 1000 iterations. If its line search reports precision loss, "
            "a bounded deterministic Powell refinement is required to converge. Checks use "
            "nmax=16,64, fixed grids "
            "of 128,256,512 bins, circular-transport grids of 2048,4096,8192 bins, two angular "
            "origin shifts, and three extra wrapped images.",
            "",
            "The principal distances are Fourier discrepancy, maximum harmonic mismatch, "
            "grid-converged circular W1 transport distance, and fixed-256-bin L1 and Linfinity "
            "density residuals. Only the latter two depend directly on binning.",
            "",
            "## 4. Regime-by-regime results",
            "",
            "|rank|regime|hz|J|Jpm|M|mu|sigma|D_F|max harmonic|W1|L1|Linf|class|deviation/radial structure|top residual harmonics|phase resultant|repeat-radius fraction|radial branches|N16/N13 D_F|detector max mult|min distinct gap|f_deg|within-block Frobenius|",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for rank, row in enumerate(ordered, start=1):
            lines.append(
                f"|{rank}|`{row['case_id']}`|{row['hz']:.4g}|{row['J']:.4g}|{row['Jpm']:.4g}|"
                f"{int(row['finite_included_count'])}|{row['mu']:.6g}|{row['sigma']:.6g}|"
                f"{row['fourier_discrepancy']:.6g}|{row['maximum_harmonic_mismatch']:.6g}|"
                f"{row['circular_transport']:.6g}|{row['real_space_l1']:.6g}|"
                f"{row['real_space_linf_density']:.6g}|{row['classification']}|"
                f"{row['dominant_deviation_structure']}|{row['top_harmonics']}|"
                f"{row['phase_resultant']:.6g}|{row['largest_repeated_radius_fraction']:.6g}|"
                f"{int(row['radial_branch_count'])}|{row['fourier_N16_over_N13']:.6g}|"
                f"{int(row['maximum_multiplicity'])}|"
                f"{row['minimum_distinct_spacing'] if row['minimum_distinct_spacing'] is not None else 'n/a'}|"
                f"{row['f_deg']:.6g}|{row['within_frobenius_norm']:.6g}|"
            )
        lines.extend(
            [
                "",
                "Complete harmonic values, phases, radial summaries, robustness checks, and raw "
                "paths are in `all_results.csv`, `primary_N16_summary.csv`, and `harmonic_residuals.csv`.",
                "The finite-size column is the exact endpoint ratio D_F(N=16)/D_F(N=13); the CSV "
                "also records the log10 slope and whether the four values are monotone.",
                "",
                "## 5. Detector-spectrum relationship",
                "",
                "The detector comparison uses the common N=11 full-spectrum atlas because it is "
                "the largest size with complete dense Vab matrices for all 30 regimes. Individual "
                "within-degenerate-block heatmaps are solver-basis dependent; Frobenius norms, "
                "ranks, singular values, block spectra, and f_deg are basis invariant. The primary "
                "absolute degeneracy tolerance is 1e-9 in the detector energy units; 1e-10 and "
                "1e-8 are recorded as deterministic sensitivity checks.",
                "",
                "Descriptive Pearson coefficients with D_F (no inferential interpretation) are: "
                + ", ".join(
                    f"{key}={value:.4g}" if value is not None else f"{key}=undefined"
                    for key, value in correlations.items()
                )
                + ".",
                "",
                "Strongly deviating regimes have median f_deg="
                f"{np.median([row['f_deg'] for row in strong]):.6g}, compared with "
                f"{np.median([row['f_deg'] for row in close]):.6g} among the closest group. "
                "The regime-level table must be used to distinguish degeneracy itself from active "
                "within-degenerate coupling: large multiplicity can occur with f_deg=0.",
                "",
                "## 6. Proposed mechanism",
                "",
                "The directly observed chain is: detector degeneracies and selection rules determine "
                "which projector blocks PgVPg are active; this changes the radial branches and repeated "
                "radii of the full relative-unitary eigenvalues; theta=2 arctan|lambda| compresses the "
                "large-radius end toward pi; the resulting branch weights appear as shoulders, repeated "
                "angles, or higher circular harmonics. This is a deterministic mechanism proposal, not "
                "a causal proof. Degeneracy without active coupling does not supply the intermediate step.",
                "",
                "## 7. Numerical robustness and limitations",
                "",
                "Maximum validation changes across every available raw file are: "
                + ", ".join(f"{key}={value:.3g}" for key, value in maximum_checks.items())
                + ".",
                "",
                "Detector degeneracy summaries were repeated at absolute tolerances 1e-10, 1e-9, "
                "and 1e-8; each per-regime JSON records the resulting changes. The angular analysis "
                "is complete through N=16, with only six N=17 spectra and no N=18 data. Detector Vab "
                "matrices are N=11, so cross-size monotonicity of the coupling blocks is not established. "
                "The literal 2pi fit also sees that reconstructed polar angles occupy [0,pi]; the older "
                "project folded-WG diagnostic is retained in the source metrics but is not the primary fit.",
                "",
                "## 8. Further calculations",
                "",
                "The smallest discriminating additions are: complete the remaining N=17 and N=18 raw "
                "spectra; compute selected N=13 detector Vab blocks for the closest and strongest groups; "
                "and track identified radial branches continuously while detuning hz, J, or Jpm across "
                "the corresponding degeneracy surfaces.",
                "",
                "## Figure index",
                "",
                "- `wrapped_gaussian_ordering_N16.png`: common ordering and classification.",
                "- `fourier_discrepancy_across_N.png`: finite-size behavior and missing-data pattern.",
                "- `cross_regime_detector_relationships.png`: principal detector comparisons.",
                "- `regimes/<case>/wrapped_gaussian_diagnostics_N16.png`: complete eigenvalue-to-angle diagnostics.",
                "- `regimes/<case>/detector_N11_spectral_heatmaps.png`: energy gaps, full Vab, and degenerate-block Vab.",
                "- `regimes/<case>/detector_N11_degenerate_blocks.csv`: basis-invariant block ranks, singular values, spectra, and Frobenius norms.",
                "- `regimes/<case>/reconstructed_N<N>.npz`: complete complex spectrum and reconstructed polar arrays.",
                "",
            ]
        )
        (self.output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    def rerender_only(self) -> None:
        """Regenerate figures and the report from a completed checkpoint."""
        source = resolve(self.config["source_run"])
        campaign = resolve(self.config["campaign_config"])
        inventory = RawInventory(source, campaign)
        records = inventory.discover()
        rows = read_csv_typed(self.output / "all_results.csv")
        if len(rows) != len(records):
            raise RuntimeError(
                f"rerender checkpoint has {len(rows)} rows, but inventory has {len(records)}"
            )
        primary = [row for row in rows if int(row["N"]) == self.primary_n]
        if len(primary) != 30:
            raise RuntimeError(f"expected 30 primary N={self.primary_n} rows, found {len(primary)}")
        self.all_rows = rows
        regime_lookup = {item.case_id: item for item in inventory.regimes}
        primary_lookup = {str(item["case_id"]): item for item in primary}
        for case_id in sorted(regime_lookup):
            self.plot_regime(
                regime_lookup[case_id],
                primary_lookup[case_id],
                rows,
                primary_lookup[case_id],
            )
        self.cross_regime_plots(primary)
        self.write_report(primary, records)
        shutil.copy2(Path(__file__), self.output / Path(__file__).name)
        write_json(self.output / "analysis_config.json", self.config)
        manifest = load_json(self.output / "run_manifest.json")
        manifest["figures_and_report_rerendered_at"] = datetime.now().isoformat(timespec="seconds")
        write_json(self.output / "run_manifest.json", manifest)

    def run(self) -> None:
        source = resolve(self.config["source_run"])
        campaign = resolve(self.config["campaign_config"])
        atlas = resolve(self.config["detector_atlas"])
        inventory = RawInventory(source, campaign)
        records = inventory.discover()
        self.output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(__file__), self.output / Path(__file__).name)
        write_json(self.output / "analysis_config.json", self.config)

        rows: list[dict[str, Any]] = []
        harmonics: list[dict[str, Any]] = []
        for index, record in enumerate(records, start=1):
            print(f"[{index}/{len(records)}] N={record.detector_n} {record.regime.case_id}", flush=True)
            row, harmonic_rows = self.one_record(record)
            rows.append(row)
            harmonics.extend(harmonic_rows)
            write_csv(self.output / "all_results.csv", rows)
            write_csv(self.output / "harmonic_residuals.csv", harmonics)
        for case_id in sorted({str(row["case_id"]) for row in rows}):
            common = sorted(
                (
                    row
                    for row in rows
                    if row["case_id"] == case_id and 13 <= int(row["N"]) <= self.primary_n
                ),
                key=lambda item: int(item["N"]),
            )
            if len(common) != 4:
                continue
            values = np.asarray([float(item["fourier_discrepancy"]) for item in common])
            slope = float(np.polyfit(np.arange(13, 17), np.log10(np.maximum(values, 1e-300)), 1)[0])
            ratio = float(values[-1] / values[0]) if values[0] else None
            differences = np.diff(values)
            if np.all(differences >= 0.0):
                monotonicity = "monotone increasing"
            elif np.all(differences <= 0.0):
                monotonicity = "monotone decreasing"
            else:
                monotonicity = "nonmonotone"
            for row in rows:
                if row["case_id"] == case_id:
                    row["fourier_N16_over_N13"] = ratio
                    row["fourier_log10_slope_per_N_13_16"] = slope
                    row["fourier_N13_16_monotonicity"] = monotonicity
        self.all_rows = rows

        primary = [row for row in rows if int(row["N"]) == self.primary_n]
        if len(primary) != 30:
            raise RuntimeError(f"expected 30 primary N={self.primary_n} rows, found {len(primary)}")
        ordered = sorted(primary, key=lambda item: item["fourier_discrepancy"])
        labels = (
            ["closely wrapped-Gaussian"] * 10
            + ["moderately deviating"] * 10
            + ["strongly deviating"] * 10
        )
        classification = {row["case_id"]: label for row, label in zip(ordered, labels)}
        for row in rows:
            row["classification"] = classification[row["case_id"]]

        integrator = DetectorIntegrator(
            atlas,
            self.config["degeneracy_tolerances"],
            float(self.config["matrix_nonzero_relative_tolerance"]),
        )
        detector_rows: list[dict[str, Any]] = []
        regime_lookup = {item.case_id: item for item in inventory.regimes}
        primary_lookup = {item["case_id"]: item for item in primary}
        for case_id in sorted(regime_lookup):
            detector = integrator.analyze(
                case_id,
                self.output / "regimes" / case_id,
                bool(self.config["copy_detector_arrays"]),
            )
            detector_rows.append({"case_id": case_id, **detector})
            for row in rows:
                if row["case_id"] == case_id:
                    row.update({key: value for key, value in detector.items() if key != "tolerance_sensitivity"})
            write_json(
                self.output / "regimes" / case_id / "detector_tolerance_sensitivity.json",
                detector["tolerance_sensitivity"],
            )
            self.plot_regime(regime_lookup[case_id], primary_lookup[case_id], rows, detector)

        primary = [row for row in rows if int(row["N"]) == self.primary_n]
        write_csv(self.output / "all_results.csv", rows)
        write_csv(
            self.output / "primary_N16_summary.csv",
            sorted(primary, key=lambda item: item["fourier_discrepancy"]),
        )
        write_csv(self.output / "detector_summary_N11.csv", detector_rows)
        write_csv(self.output / "source_inventory.csv", [
            {
                "case_id": item.regime.case_id,
                "N": item.detector_n,
                "raw_path": str(item.raw_path.relative_to(ROOT)),
                "metadata_exists": item.metadata_path.is_file(),
            }
            for item in records
        ])
        self.cross_regime_plots(primary)
        self.write_report(primary, records)

        failures = [
            row
            for row in rows
            if not row["optimizer_success"]
            or row["reconstruction_max_relative_error"] > 1e-10
            or (row["saved_theta_max_abs_error"] is not None and row["saved_theta_max_abs_error"] > 1e-12)
        ]
        write_json(
            self.output / "run_manifest.json",
            {
                "status": "complete" if not failures else "validation_failed",
                "source_run": str(source),
                "raw_spectra_analyzed": len(rows),
                "primary_n": self.primary_n,
                "primary_regime_count": len(primary),
                "available_counts_by_n": {
                    str(n): sum(int(row["N"]) == n for row in rows)
                    for n in sorted({int(row["N"]) for row in rows})
                },
                "validation_failure_count": len(failures),
                "validation_failures": [
                    {"case_id": row["case_id"], "N": row["N"]} for row in failures
                ],
                "report": "REPORT.md",
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="configs/relative_scale_wrapped_gaussian_reanalysis.json",
    )
    parser.add_argument("--output")
    parser.add_argument(
        "--rerender-only",
        action="store_true",
        help="regenerate figures and report from an existing complete output checkpoint",
    )
    args = parser.parse_args()
    config = load_json(resolve(args.config))
    if args.output:
        output = resolve(args.output)
    else:
        stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
        output = ROOT / "reports" / f"relative_scale_wrapped_gaussian_{stamp}"
    print(f"OUTPUT_DIRECTORY={output}", flush=True)
    analysis = Reanalysis(config, output)
    if args.rerender_only:
        analysis.rerender_only()
    else:
        analysis.run()


if __name__ == "__main__":
    main()
