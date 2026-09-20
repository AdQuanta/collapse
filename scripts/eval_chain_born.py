"""Frozen evaluator for the open endpoint-chain Born region campaign.

This is a *campaign* verifier, separate from ``scripts/eval_born.py``. The older
script scores a single configuration at a single size against a champion; this
one scores a configuration across a ladder of sizes and reports, alongside the
raw score, a root-budget-controlled score that is comparable across sizes.

Why the budget control exists
-----------------------------
The finite root count grows as ``K * 2^N``, so bin occupancy — and with it
``S_born`` — rises with ``N`` for reasons unrelated to convergence toward Born.
``research_reports/MARKOVIANITY_BORN_2026-09-20.md`` §12 showed that thinning an
``N = 9`` root set back to the ``N = 4`` budget erased an apparent finite-size
improvement entirely, which is ``SPEC.md`` hard-FAIL condition 6. Any statement
this campaign makes about an ``N``-trend therefore reads the thinned column, not
the raw one.

The frozen contract
-------------------
Everything in the "Frozen campaign constants" block below is fixed for the
duration of the campaign. Per ``SPEC.md`` §23 hard-FAIL 9 and the project's
standing rule against tuning acceptance gates after seeing results, these values
must not be changed to rescue a candidate. A genuine change of contract means a
new campaign version and a fresh governance record.

Model
-----
The family is the ``SPEC.md`` §9.2 endpoint chain: ``connectivity="chain"`` with
``central_coupling="first"``. With the central qubit indexed ``0`` and detector
spins ``i = 1..N``, the builder carries an overall minus sign, so it constructs

    H = -[ J_zz sum_{i=1}^{N-1} Z_i Z_{i+1}
           + J_xx sum_{i=1}^{N-1} X_i X_{i+1}
           + J_yy sum_{i=1}^{N-1} Y_i Y_{i+1} ]
        -[ g_z Z_0 Z_1 + g_x X_0 X_1 + g_y Y_0 Y_1 ]
        -[ h_0x X_0 + h_0y Y_0 + h_0z Z_0 ]
        - sum_{i=1}^{N} ( h_x X_i + h_y Y_i + h_z Z_i )

The code coefficients are therefore the negatives of the ``SPEC.md`` §9 ones.
Because the qubit couples to a single edge, the total qubit-detector coupling is
independent of ``N`` and no size scaling of ``g`` is applied or needed.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scipy.linalg import eigh as scipy_eigh

from core.analysis import (
    diagonalize_relative_evolution,
    evolution_subblocks_from_eigenbasis,
)
from core.born import (
    born_ratio_from_theta,
    phase_angles_from_eigenvalues,
    theta_pair_from_radii,
)
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


# ---------------------------------------------------------------------------
# Frozen campaign constants
# ---------------------------------------------------------------------------

CAMPAIGN_VERSION = "chain-born-v1"

#: Sizes every candidate is evaluated at, chosen so one candidate fits the
#: 15 s budget: measured 0.52 s + 2.95 s + 8.38 s on this machine.
N_LADDER: tuple[int, ...] = (8, 9, 10)

#: Six logarithmically spaced times, fixed and independent of ``N`` so that the
#: ``N -> infinity`` before ``T -> infinity`` ordering of ``SPEC.md`` §7.1 is
#: preserved. Roots from all six are pooled into one histogram; this is not a
#: time average.
TIMES: tuple[float, ...] = tuple(float(t) for t in np.geomspace(100.0, 1000.0, 6))

#: ``S_born`` uses 100 bins; plotted profiles use 64. The split is the house
#: convention of the ring catalog figures and the two must never be mixed.
S_BORN_BINS = 100
PROFILE_BINS = 64

#: Additional bin counts scored as a diagnostic only. The campaign metric stays
#: at S_BORN_BINS; these exist so that estimator dependence is visible in every
#: record rather than discovered later. SPEC.md 6.5 requires apparent agreement
#: to be checked against reasonable estimator choices, and hard-FAIL 6 treats
#: estimator dependence mistaken for convergence as disqualifying.
DIAGNOSTIC_BIN_COUNTS = (50, 64, 128, 200)

#: Fixed root budget for the size-comparable score: the ``N = 8`` root count,
#: ``len(TIMES) * 2**8``.
ROOT_BUDGET = len(TIMES) * 2**8
BOOTSTRAP_DRAWS = 200

#: The qubit-detector coupling must be at least one order of magnitude below
#: *every* other nonzero parameter, per user instruction.
PERTURBATIVE_RATIO = 0.1

#: Relative slack on the comparison only, not on the threshold. A candidate
#: constructed as ``g = PERTURBATIVE_RATIO * scale`` can divide back to
#: ``0.10000000000000002``, and rejecting it would be a floating-point artifact
#: rather than a physical judgement. The slack is far below any parameter
#: resolution the campaign uses, so it cannot admit a genuinely stronger
#: coupling.
PERTURBATIVE_TOLERANCE = 1.0e-9

#: Overall energy scale convention: the smallest nonzero non-coupling parameter
#: is normalized to 1. Since ``H -> lambda H`` is equivalent to ``t -> t/lambda``
#: and the time window is fixed in absolute units, this convention is what makes
#: ``TIMES`` mean the same thing for every candidate.
SCALE_REFERENCE = 1.0

#: Quality gates.
MIN_COVERAGE_BINS = 20
MAX_ISOMETRY_RESIDUAL = 1.0e-9
MAX_HERMITICITY_RESIDUAL = 1.0e-12
ILL_CONDITIONED_THRESHOLD = 1.0e6

#: Parameters held at zero for the whole campaign, with the reason.
FIXED_ZERO = {
    "Jpm": "redundant with Jxx = Jyy",
    "Jcpm": "redundant with gx = gy",
    "Jzx": "cross-axis Z_0 X_i is outside the approved search space (SPEC 10.3)",
    "J2": "no next-nearest-neighbour terms (SPEC 9.3)",
    "Jpm2": "no next-nearest-neighbour terms (SPEC 9.3)",
}


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: The twelve campaign parameters, in the order they are reported.
PARAMETER_NAMES = (
    "h0x", "h0y", "h0z",
    "hx", "hy", "hz",
    "Jxx", "Jyy", "Jzz",
    "gx", "gy", "gz",
)
COUPLING_NAMES = ("gx", "gy", "gz")
NON_COUPLING_NAMES = tuple(n for n in PARAMETER_NAMES if n not in COUPLING_NAMES)


@dataclass(frozen=True)
class ChainConfig:
    """One endpoint-chain candidate, with every parameter stated explicitly.

    No value is left to a builder default. That matters here specifically:
    ``SinglePixelHamiltonian*`` treats an unset ``hx0``/``hy0``/``hz0`` as
    inheriting ``hx``/``hy``/``hz``, so an omitted qubit field silently produces
    a different model from the one the caller intended.
    """

    name: str
    hypothesis: str
    rung: str
    h0x: float = 0.0
    h0y: float = 0.0
    h0z: float = 0.0
    hx: float = 0.0
    hy: float = 0.0
    hz: float = 0.0
    Jxx: float = 0.0
    Jyy: float = 0.0
    Jzz: float = 0.0
    gx: float = 0.0
    gy: float = 0.0
    gz: float = 0.0

    def parameters(self) -> dict[str, float]:
        return {name: float(getattr(self, name)) for name in PARAMETER_NAMES}

    def builder_kwargs(self, n_pixel: int) -> dict[str, Any]:
        """Map campaign parameters onto ``SinglePixelHamiltonianQuSpin``."""

        return dict(
            N_pixel=n_pixel,
            connectivity="chain",
            central_coupling="first",
            J=self.Jzz,
            Jxx=self.Jxx,
            Jyy=self.Jyy,
            Jx=self.gx,
            Jy=self.gy,
            Jz=self.gz,
            hx=self.hx,
            hy=self.hy,
            hz=self.hz,
            hx0=self.h0x,
            hy0=self.h0y,
            hz0=self.h0z,
            use_symmetry=False,
            **{name: 0.0 for name in FIXED_ZERO},
        )


def detector_scale(config: ChainConfig) -> float:
    """Return the smallest nonzero non-coupling parameter magnitude.

    This is the denominator of the perturbative ratio. The *minimum* is used, not
    the maximum: the coupling must be small compared with every scale the rest of
    the model contains, not merely with the largest one.
    """

    magnitudes = [
        abs(value)
        for name, value in config.parameters().items()
        if name in NON_COUPLING_NAMES and value != 0.0
    ]
    return min(magnitudes) if magnitudes else 0.0


def coupling_scale(config: ChainConfig) -> float:
    return max(abs(getattr(config, name)) for name in COUPLING_NAMES)


def perturbative_ratio(config: ChainConfig) -> float:
    """Return ``max|g| / min|nonzero non-g|``, or infinity when undefined."""

    scale = detector_scale(config)
    if scale == 0.0:
        return float("inf")
    return coupling_scale(config) / scale


def normalize(config: ChainConfig) -> tuple[ChainConfig, float]:
    """Rescale so the smallest nonzero non-coupling parameter equals 1.

    Returns the rescaled configuration and the factor applied. Rescaling every
    parameter by the same factor leaves the perturbative ratio invariant and
    leaves the physics invariant up to ``t -> t / factor``; since the time window
    is frozen in absolute units, fixing the scale is what puts every candidate at
    the same dynamical stage.
    """

    scale = detector_scale(config)
    if scale == 0.0:
        raise ValueError(
            f"configuration {config.name!r} has no nonzero non-coupling parameter, "
            "so its energy scale is undefined"
        )
    factor = SCALE_REFERENCE / scale
    if factor == 1.0:
        return config, 1.0
    rescaled = {name: value * factor for name, value in config.parameters().items()}
    return (
        ChainConfig(
            name=config.name,
            hypothesis=config.hypothesis,
            rung=config.rung,
            **rescaled,
        ),
        factor,
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _weighted_marginal_error(ratio: np.ndarray, born: np.ndarray, occupied: np.ndarray,
                             centers: np.ndarray) -> float:
    """Return the ``SPEC.md`` §6.4 weak-marginal error over supported bins.

    A normalized ``sin(theta)``-weighted L2 deviation, evaluated only where the
    estimator has support. Empty bins are never imputed: ``born_ratio_from_theta``
    would otherwise fill them with the uninformative value ``0.5``, which makes
    the score depend on coverage through an arbitrary fill rather than through
    the measure itself.
    """

    if not np.any(occupied):
        return float("nan")
    weights = np.sin(centers[occupied])
    total = float(np.sum(weights))
    if total <= 0.0:
        return float("nan")
    squared = (ratio[occupied] - born[occupied]) ** 2
    return float(np.sqrt(np.sum(squared * weights) / total))


def _score_theta(theta: np.ndarray, n_bins: int = S_BORN_BINS) -> dict[str, float]:
    """Score one pooled set of polar roots."""

    result = born_ratio_from_theta(theta, np.pi - theta, n_theta=n_bins, empty_value=0.5)
    occupied = (result.counts_0 + result.counts_1) > 0
    return {
        "S_born": float(result.similarity),
        "mean_abs_error": float(result.mean_abs_error),
        "E_marg_occupied": _weighted_marginal_error(
            result.ratio, result.born, occupied, result.theta_centers
        ),
        "coverage_bins": int(np.count_nonzero(occupied)),
        "coverage_fraction": float(np.mean(occupied)),
    }


def _thinned_score(theta: np.ndarray, budget: int, draws: int,
                   seed: int) -> dict[str, float]:
    """Return the mean and spread of ``S_born`` at a fixed root budget.

    When the sample already sits at or below the budget the score is exact and
    the spread is zero, which is the intended behaviour at the bottom of the
    ladder: that rung *defines* the budget.
    """

    n_samples = int(theta.size)
    if n_samples <= budget:
        exact = _score_theta(theta)
        return {
            "S_born_thinned_mean": exact["S_born"],
            "S_born_thinned_sd": 0.0,
            "thinning_applied": False,
        }
    rng = np.random.default_rng(seed)
    scores = np.empty(draws, dtype=float)
    for draw in range(draws):
        subset = rng.choice(n_samples, size=budget, replace=False)
        scores[draw] = _score_theta(theta[subset])["S_born"]
    return {
        "S_born_thinned_mean": float(np.mean(scores)),
        "S_born_thinned_sd": float(np.std(scores, ddof=1)),
        "thinning_applied": True,
    }


def born_profile(theta: np.ndarray, n_bins: int = PROFILE_BINS) -> dict[str, np.ndarray]:
    """Return the house-style angular profile arrays for plotting and export.

    The key names match the existing ``results.npz`` schema so that
    ``core.born_profile_export.load_profile`` and the ring-catalog plotters work
    unchanged.
    """

    edges = np.linspace(0.0, np.pi, n_bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0
    counts_0, _ = np.histogram(theta, bins=edges)
    counts_1, _ = np.histogram(np.pi - theta, bins=edges)
    width = edges[1] - edges[0]
    total = counts_0 + counts_1
    occupied = total > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(occupied, counts_0 / np.maximum(total, 1), np.nan)
    denominator = max(float(theta.size) * width, np.finfo(float).tiny)
    return {
        "edges": edges,
        "centers": centers,
        "p_theta": counts_0 / denominator,
        "p_pi_minus_theta": counts_1 / denominator,
        "R": ratio,
        "R_occupied": occupied,
        "R_born": np.cos(centers / 2.0) ** 2,
    }


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def pooled_roots(config: ChainConfig, n_pixel: int,
                 times: Sequence[float] = TIMES
                 ) -> tuple[list[np.ndarray], list[np.ndarray], dict[str, float]]:
    """Return the per-time polar root sets at one size, plus diagnostics.

    The sets are returned separately rather than concatenated so the caller can
    both pool them for the campaign score and score each time on its own. The
    pooled score is the frozen metric; the per-time spread is the diagnostic that
    tells whether that pooled number describes a stationary law or an average
    over a wandering one, which ``SPEC.md`` §7.2 requires be distinguished.

    Raises ``RuntimeError`` when a frozen numerical gate fails, so that a broken
    candidate is recorded as a failure rather than silently scored.
    """

    hamiltonian = SinglePixelHamiltonianQuSpin(**config.builder_kwargs(n_pixel))
    dense = hamiltonian.generate()
    scale = max(float(np.linalg.norm(dense)), 1.0)
    hermiticity = float(np.linalg.norm(dense - dense.conj().T) / scale)
    if hermiticity > MAX_HERMITICITY_RESIDUAL:
        raise RuntimeError(f"hermiticity violation {hermiticity:.3e} at N={n_pixel}")

    try:
        energies, vectors = np.linalg.eigh(dense)
    except np.linalg.LinAlgError:
        # Apple Accelerate's divide-and-conquer zheevd fails on complex Hermitian
        # matrices at dimension 4096 and above ("illegal value in argument 10",
        # an LRWORK workspace bug), which is reached at N >= 11 once a Y self-field
        # makes the Hamiltonian complex. The relatively-robust driver handles the
        # same matrix and is roughly four times faster than the QR driver. Any
        # orthonormal basis of a degenerate eigenspace gives the same propagator,
        # so the fallback does not change results.
        try:
            energies, vectors = scipy_eigh(dense, driver="evr")
        except Exception as error:
            raise RuntimeError(
                f"Hamiltonian eigensolve failed at N={n_pixel}: {error}"
            ) from error

    collected: list[np.ndarray] = []
    azimuths: list[np.ndarray] = []
    worst_isometry = 0.0
    worst_condition = 0.0
    pencil_fallbacks = 0
    for time_value in times:
        u00, u10 = evolution_subblocks_from_eigenbasis(energies, vectors, float(time_value))
        identity = np.eye(u00.shape[1], dtype=np.complex128)
        isometry = float(
            np.linalg.norm(u00.conj().T @ u00 + u10.conj().T @ u10 - identity)
        )
        worst_isometry = max(worst_isometry, isometry)
        if isometry > MAX_ISOMETRY_RESIDUAL:
            raise RuntimeError(
                f"column isometry broken at N={n_pixel}, t={time_value}: {isometry:.3e}"
            )

        radii = None
        eigenvalues = None
        try:
            spectrum = diagonalize_relative_evolution(u00, u10, solver="solve")
            worst_condition = max(worst_condition, float(spectrum.condition_number))
            if spectrum.condition_number < ILL_CONDITIONED_THRESHOLD:
                radii = spectrum.radii
                eigenvalues = spectrum.eigenvalues
        except np.linalg.LinAlgError:
            # Singular U00, or a non-Hermitian eigensolve that did not converge.
            # Both are recoverable here by falling through to the pencil.
            worst_condition = float("inf")
        if radii is None:
            # The direct solve either was ill-conditioned or failed to converge.
            # The homogeneous pencil is the fallback, and if it also fails the
            # candidate is recorded as a numerical failure rather than crashing
            # the batch around it.
            pencil_fallbacks += 1
            try:
                fallback = generalized_relative_evolution_spectrum(
                    u00, u10, compute_left_eigenvectors=False
                )
                radii = fallback.radii
                eigenvalues = getattr(fallback, "eigenvalues", None)
            except np.linalg.LinAlgError as error:
                raise RuntimeError(
                    f"both the direct solve and the QZ pencil failed at "
                    f"N={n_pixel}, t={time_value}: {error}"
                ) from error

        theta, _ = theta_pair_from_radii(radii)
        collected.append(theta)
        if eigenvalues is not None:
            azimuths.append(
                phase_angles_from_eigenvalues(eigenvalues, include_antipodes=False)
            )

    diagnostics = {
        "hermiticity_residual": hermiticity,
        "max_isometry_residual": worst_isometry,
        "max_condition_number": worst_condition,
        "pencil_fallbacks": pencil_fallbacks,
    }
    return collected, azimuths, diagnostics


def evaluate_config(config: ChainConfig, n_values: Sequence[int] = N_LADDER,
                    times: Sequence[float] = TIMES) -> dict[str, Any]:
    """Evaluate one candidate across the size ladder.

    The returned record is self-describing: it carries the normalized parameters,
    the scale factor applied, the perturbative ratio, the frozen contract, and a
    per-size metric block. Nothing downstream should need the caller's context to
    interpret it.
    """

    # The ratio is scale invariant, so it is computed before normalizing. That
    # order matters: a configuration with no nonzero non-coupling parameter has
    # no energy scale to normalize against, and it must come back as an ordinary
    # rejection record rather than raising and aborting the surrounding batch.
    ratio = perturbative_ratio(config)

    record: dict[str, Any] = {
        "campaign_version": CAMPAIGN_VERSION,
        "name": config.name,
        "rung": config.rung,
        "hypothesis": config.hypothesis,
        "parameters": config.parameters(),
        "parameters_as_given": config.parameters(),
        "scale_factor": 1.0,
        "perturbative_ratio": ratio,
        "detector_scale": detector_scale(config),
        "coupling_scale": coupling_scale(config),
        "times": list(times),
        # A candidate may be run on a diagnostic window instead of the frozen
        # one, to separate a genuine parameter dependence from a window effect.
        # Such a record is marked so it can never be ranked against frozen-window
        # scores by accident.
        "frozen_window": len(times) == len(TIMES) and bool(
            np.allclose(np.asarray(times, dtype=float), np.asarray(TIMES), rtol=1e-9)
        ),
        "root_budget": ROOT_BUDGET,
        "by_size": {},
        "passed": False,
        "rejection_reasons": [],
    }

    if not np.isfinite(ratio):
        record["rejection_reasons"].append(
            "energy scale undefined: every non-coupling parameter is zero"
        )
        return record

    normalized, factor = normalize(config)
    record["parameters"] = normalized.parameters()
    record["scale_factor"] = factor
    record["detector_scale"] = detector_scale(normalized)
    record["coupling_scale"] = coupling_scale(normalized)

    if ratio > PERTURBATIVE_RATIO * (1.0 + PERTURBATIVE_TOLERANCE):
        record["rejection_reasons"].append(
            f"non-perturbative coupling: ratio {ratio:.6f} > {PERTURBATIVE_RATIO}"
        )
        return record
    if coupling_scale(normalized) == 0.0:
        record["rejection_reasons"].append(
            "qubit and detector are decoupled: every g is zero"
        )
        return record

    seed = abs(hash((CAMPAIGN_VERSION, config.name))) % (2**32)
    for n_pixel in n_values:
        try:
            per_time, per_time_phi, diagnostics = pooled_roots(normalized, n_pixel, times)
        except RuntimeError as error:
            record["by_size"][str(n_pixel)] = {"error": str(error)}
            record["rejection_reasons"].append(f"N={n_pixel}: {error}")
            return record

        theta = np.concatenate(per_time)
        metrics = _score_theta(theta)
        metrics.update(_thinned_score(theta, ROOT_BUDGET, BOOTSTRAP_DRAWS, seed + n_pixel))
        metrics.update(diagnostics)
        metrics["n_roots"] = int(theta.size)

        # Per-time scores. The pooled metric above averages the six instantaneous
        # densities before scoring; a pooled value can therefore look smooth
        # merely because the instantaneous law wanders. Reporting the individual
        # scores and their spread keeps time-averaged agreement distinguishable
        # from actual convergence.
        # Estimator sweep: the same roots scored at other bin counts. A score
        # that moves materially with the binning is not evidence of anything.
        by_bins = {
            str(bins): _score_theta(theta, n_bins=bins)["S_born"]
            for bins in DIAGNOSTIC_BIN_COUNTS
        }
        metrics["S_born_by_bins"] = by_bins
        spread = max(by_bins.values()) - min(by_bins.values())
        metrics["S_born_bin_spread"] = float(spread)

        # Azimuthal structure. The exact Born profile contains only the (0,0) and
        # (1,0) spherical-harmonic sectors, so a nonzero circular moment in phi is
        # m != 0 leakage and a strong-Born failure even when the polar marginal
        # looks right (SPEC.md 6.3). Uniform phi gives moments near zero, of order
        # 1/sqrt(n) from finite sampling.
        if per_time_phi:
            phi = np.concatenate(per_time_phi)
            moments = {
                str(m): float(abs(np.mean(np.exp(1j * m * phi))))
                for m in (1, 2, 3, 4)
            }
            metrics["azimuthal_moments"] = moments
            metrics["azimuthal_moment_max"] = float(max(moments.values()))
            metrics["azimuthal_noise_floor"] = float(1.0 / np.sqrt(phi.size))

        per_time_scores = [_score_theta(single)["S_born"] for single in per_time]
        metrics["S_born_per_time"] = [float(value) for value in per_time_scores]
        metrics["S_born_time_mean"] = float(np.mean(per_time_scores))
        metrics["S_born_time_sd"] = float(np.std(per_time_scores, ddof=1))
        # A pooled score far above every individual time is produced by the
        # averaging, not by any instantaneous distribution.
        metrics["pooling_gain"] = float(
            metrics["S_born"] - float(np.max(per_time_scores))
        )
        record["by_size"][str(n_pixel)] = metrics

    coverages = [
        block["coverage_bins"]
        for block in record["by_size"].values()
        if "coverage_bins" in block
    ]
    if coverages and min(coverages) < MIN_COVERAGE_BINS:
        record["rejection_reasons"].append(
            f"insufficient angular coverage: {min(coverages)} bins "
            f"(minimum {MIN_COVERAGE_BINS})"
        )

    scores = [
        block["S_born"] for block in record["by_size"].values() if "S_born" in block
    ]
    if any(not np.isfinite(value) for value in scores):
        record["rejection_reasons"].append("S_born is not finite")

    record["passed"] = not record["rejection_reasons"]
    if record["passed"]:
        largest = str(max(n_values))
        thinned = [
            record["by_size"][str(n)]["S_born_thinned_mean"] for n in n_values
        ]
        record["summary"] = {
            "S_born_at_largest_N": record["by_size"][largest]["S_born"],
            "S_born_thinned_at_largest_N": record["by_size"][largest][
                "S_born_thinned_mean"
            ],
            # The budget-controlled trend. A positive value is the only kind of
            # finite-size improvement this campaign treats as meaningful.
            "thinned_trend": float(thinned[-1] - thinned[0]),
            "raw_trend": float(
                record["by_size"][largest]["S_born"]
                - record["by_size"][str(min(n_values))]["S_born"]
            ),
        }
    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate an endpoint-chain candidate across the size ladder."
    )
    parser.add_argument("--candidate", type=Path, required=True,
                        help="JSON file holding one ChainConfig.")
    parser.add_argument("--log", type=Path,
                        default=Path("reports/chain_born_regions/experiment_log.jsonl"))
    parser.add_argument("--n-ladder", type=int, nargs="+", default=list(N_LADDER))
    args = parser.parse_args()

    payload = json.loads(args.candidate.read_text(encoding="utf-8"))
    config = ChainConfig(**payload)
    record = evaluate_config(config, n_values=tuple(args.n_ladder))

    status = "PASSED" if record["passed"] else "REJECTED"
    print(f"[{status}] {config.name}  (rung {config.rung})")
    print(f"  perturbative ratio {record['perturbative_ratio']:.4f}"
          f"   scale factor {record['scale_factor']:.4g}")
    for n_pixel in args.n_ladder:
        block = record["by_size"].get(str(n_pixel), {})
        if "error" in block:
            print(f"  N={n_pixel:2d}  ERROR {block['error']}")
            continue
        print(
            f"  N={n_pixel:2d}  S_born={block['S_born']:+.4f}"
            f"  thinned={block['S_born_thinned_mean']:+.4f}"
            f" +/- {block['S_born_thinned_sd']:.4f}"
            f"  E_marg={block['E_marg_occupied']:.4f}"
            f"  cov={block['coverage_bins']}/{S_BORN_BINS}"
        )
    for reason in record["rejection_reasons"]:
        print(f"  reject: {reason}")

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with open(args.log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")

    sys.exit(0 if record["passed"] else 1)


if __name__ == "__main__":
    main()
