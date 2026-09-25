"""Frozen evaluator for the preferred-basis / strong-Born-criterion campaign.

Companion to ``scripts/eval_chain_born.py``, which scores only the weak
(polar-marginal) criterion from a single relative-evolution operator. This
evaluator builds both ``SPEC.md`` section 3 outcome pencils
(``core.outcome_measures``, via ``forward_pole_root_spectrum``) and reports
the binning-free preferred axis, ``B1``, the odd-``l`` leakage, and the
``SPEC.md`` section 6 quartet -- the observable of
``goal_preferred_basis.md``.

Model, sign convention, and the twelve campaign parameters are unchanged from
``eval_chain_born.py`` and reused directly from it: ``ChainConfig``,
``PARAMETER_NAMES``, ``detector_scale``/``coupling_scale``/
``perturbative_ratio``/``normalize``. Only the scoring differs.

Times are pooled across the frozen six-time window as in ``eval_chain_born``
(``TIMES``), but pooling here concatenates each time's *labelled* root cloud
(outcome 0 and outcome 1 separately) rather than one time-sliced pencil's
angles; the preferred axis is fit once from the pooled outcome-0 cloud, not
per time, since ``goal_preferred_basis.md`` section 3 requires "no time
average" while still using all six times' roots as one measurement of the
same underlying law.

Cost: each time step needs the full ``2^(N+1)``-dimensional propagator (both
outcome pencils use different blocks of it, unlike the weak-only evaluator,
which needs only the ``U00``/``U10`` sub-blocks) and two non-Hermitian
generalized eigenvalue solves of the ``2^N``-dimensional detector block.
``goal_preferred_basis.md`` section 4, WP2 requires probing the cost at a
single time before launching a full ``N`` in a sweep.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np
from scipy.linalg import eigh as scipy_eigh

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.outcome_measures import (
    PREFERRED_AXIS_COND_MAX,
    antipodal_bloch_cloud,
    odd_harmonic_power,
    outcome_bloch_cloud,
    preferred_axis_from_cloud,
    spec_quartet,
)

from eval_chain_born import (  # noqa: E402
    ChainConfig,
    COUPLING_NAMES,
    FIXED_ZERO,
    MAX_HERMITICITY_RESIDUAL,
    NON_COUPLING_NAMES,
    PARAMETER_NAMES,
    PERTURBATIVE_RATIO,
    PERTURBATIVE_TOLERANCE,
    coupling_scale,
    detector_scale,
    normalize,
    perturbative_ratio,
)

# ---------------------------------------------------------------------------
# Frozen campaign constants
# ---------------------------------------------------------------------------

CAMPAIGN_VERSION = "preferred-basis-v1"

#: Same frozen window as eval_chain_born.py: six log-spaced times, fixed and
#: independent of N, pooled but never averaged.
TIMES: tuple[float, ...] = tuple(float(t) for t in np.geomspace(100.0, 1000.0, 6))

L_MAX = 7
MARGINAL_BINS = 100

#: The QZ solve skips its O(n^2) duplicate-cluster pairwise work above this
#: many roots by default (relative_evolution_pencil.py); raised so the
#: duplicate-detection guard (goal section 4, WP1) still runs at N=12
#: (detector dimension 4096).
MAXIMUM_DUPLICATE_ROOTS = 8192

#: Left eigenvectors are not used by any measure in core.outcome_measures;
#: skipping them saves 33-36% of QZ time (relative_evolution_pencil.py).
PENCIL_SOLVER_OPTIONS: dict[str, Any] = {
    "compute_left_eigenvectors": False,
    "maximum_duplicate_roots": MAXIMUM_DUPLICATE_ROOTS,
}


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def _hamiltonian_and_basis(config: ChainConfig, n_pixel: int) -> tuple[np.ndarray, np.ndarray, float]:
    hamiltonian = SinglePixelHamiltonianQuSpin(**config.builder_kwargs(n_pixel))
    dense = hamiltonian.generate()
    scale = max(float(np.linalg.norm(dense)), 1.0)
    hermiticity = float(np.linalg.norm(dense - dense.conj().T) / scale)
    if hermiticity > MAX_HERMITICITY_RESIDUAL:
        raise RuntimeError(f"hermiticity violation {hermiticity:.3e} at N={n_pixel}")
    try:
        energies, vectors = np.linalg.eigh(dense)
    except np.linalg.LinAlgError:
        # Apple Accelerate's zheevd fails on complex Hermitian matrices at
        # dimension >= 4096 (N >= 11 once a Y self-field makes H complex);
        # the relatively-robust driver handles the same matrix (eval_chain_born.py).
        energies, vectors = scipy_eigh(dense, driver="evr")
    return energies, vectors, hermiticity


def unitary_at_time(energies: np.ndarray, vectors: np.ndarray, t: float) -> np.ndarray:
    phases = np.exp(-1j * energies * t)
    return (vectors * phases) @ vectors.conj().T


def pooled_outcome_clouds(
    config: ChainConfig, n_pixel: int, times: Sequence[float] = TIMES,
    *, keep_per_time_points: bool = False,
) -> dict[str, Any]:
    """Return the pooled labelled Bloch clouds and per-time diagnostics.

    Roots from every time in ``times`` are pooled into one outcome-0 cloud and
    one outcome-1 cloud (weight 1 per raw non-indeterminate root, goal section
    4 WP1's cost-limited convention), matching ``eval_chain_born.py``'s pooling
    of the weak criterion's angles. Outcome 1's cloud at each time is the exact
    antipodal pushforward of outcome 0's (``core.outcome_measures.
    antipodal_bloch_cloud``), not an independent QZ solve -- see that
    function's docstring for the certified theorem this relies on. This halves
    the pencil-solving cost of every time step, which matters at the N=12 end
    of the WP2 size ladder (goal section 4, WP2).

    ``keep_per_time_points=True`` additionally returns the unpooled per-time
    clouds (``per_time_points_0``/``per_time_points_1``, one array per entry
    in ``times``) for diagnostics that plot the instantaneous distribution
    rather than the pooled one; it costs no extra pencil solves, only the
    (negligible) cost of not discarding the per-time arrays before pooling.
    """

    energies, vectors, hermiticity = _hamiltonian_and_basis(config, n_pixel)

    points_0: list[np.ndarray] = []
    points_1: list[np.ndarray] = []
    per_time_diagnostics: list[dict[str, Any]] = []
    for time_value in times:
        unitary = unitary_at_time(energies, vectors, float(time_value))
        identity = np.eye(unitary.shape[0], dtype=np.complex128)
        isometry = float(np.linalg.norm(unitary.conj().T @ unitary - identity))

        cloud_0 = outcome_bloch_cloud(unitary, outcome=0, **PENCIL_SOLVER_OPTIONS)
        cloud_1 = antipodal_bloch_cloud(cloud_0)
        points_0.append(cloud_0.points)
        points_1.append(cloud_1.points)
        per_time_diagnostics.append({
            "time": float(time_value),
            "unitary_residual": isometry,
            "n_roots_0": cloud_0.n_raw_roots,
            "n_indeterminate_0": cloud_0.n_indeterminate,
            "largest_cluster_multiplicity_0": cloud_0.largest_cluster_multiplicity,
            "distinct_root_count_0": cloud_0.distinct_root_count,
            "n_roots_1": cloud_1.n_raw_roots,
            "n_indeterminate_1": cloud_1.n_indeterminate,
            "largest_cluster_multiplicity_1": cloud_1.largest_cluster_multiplicity,
            "distinct_root_count_1": cloud_1.distinct_root_count,
        })

    pooled_points_0 = np.concatenate(points_0, axis=0)
    pooled_points_1 = np.concatenate(points_1, axis=0)
    result = {
        "points_0": pooled_points_0,
        "weights_0": np.ones(pooled_points_0.shape[0], dtype=float),
        "points_1": pooled_points_1,
        "weights_1": np.ones(pooled_points_1.shape[0], dtype=float),
        "hermiticity_residual": hermiticity,
        "max_unitary_residual": max(d["unitary_residual"] for d in per_time_diagnostics),
        "per_time": per_time_diagnostics,
    }
    if keep_per_time_points:
        result["per_time_points_0"] = points_0
        result["per_time_points_1"] = points_1
    return result


def score_pooled_clouds(pooled: dict[str, Any]) -> dict[str, Any]:
    axis_result = preferred_axis_from_cloud(
        pooled["points_0"], pooled["weights_0"], cond_max=PREFERRED_AXIS_COND_MAX,
    )
    metrics: dict[str, Any] = {
        "n_roots_0": int(pooled["points_0"].shape[0]),
        "n_roots_1": int(pooled["points_1"].shape[0]),
        "hermiticity_residual": pooled["hermiticity_residual"],
        "max_unitary_residual": pooled["max_unitary_residual"],
        "condition_number_S": axis_result.condition_number,
        "axis_status": axis_result.status,
    }
    if axis_result.status != "ok":
        metrics["refusal_reason"] = axis_result.refusal_reason
        return metrics

    n_hat = axis_result.n_hat
    metrics["n_hat"] = n_hat.tolist()
    metrics["B1"] = axis_result.B1
    harmonics = odd_harmonic_power(pooled["points_0"], pooled["weights_0"], n_hat, l_max=L_MAX)
    metrics["odd_harmonic"] = {
        key: (value.tolist() if isinstance(value, np.ndarray) else value)
        for key, value in harmonics.items()
    }
    metrics["quartet"] = spec_quartet(
        pooled["points_0"], pooled["weights_0"],
        pooled["points_1"], pooled["weights_1"],
        n_hat, l_max=L_MAX, marginal_bins=MARGINAL_BINS,
    )
    return metrics


def evaluate_config(
    config: ChainConfig, n_values: Sequence[int], reference_axis: np.ndarray,
    times: Sequence[float] = TIMES,
) -> dict[str, Any]:
    """Evaluate one candidate across a size ladder against a reference axis.

    ``reference_axis`` is the physical axis the hypothesis predicts (h_0_hat
    for goal_preferred_basis.md); every size's fitted axis is compared to it.
    """

    ratio = perturbative_ratio(config)
    record: dict[str, Any] = {
        "campaign_version": CAMPAIGN_VERSION,
        "name": config.name,
        "rung": config.rung,
        "hypothesis": config.hypothesis,
        "parameters": config.parameters(),
        "scale_factor": 1.0,
        "perturbative_ratio": ratio,
        "reference_axis": np.asarray(reference_axis, dtype=float).tolist(),
        "times": list(times),
        "frozen_window": len(times) == len(TIMES) and bool(
            np.allclose(np.asarray(times, dtype=float), np.asarray(TIMES), rtol=1e-9)
        ),
        "by_size": {},
        "passed": False,
        "rejection_reasons": [],
        "sign_convention": (
            "builder carries an overall minus sign; code coefficients are the "
            "negatives of the SPEC.md section 9 coefficients"
        ),
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
        record["rejection_reasons"].append("qubit and detector are decoupled: every g is zero")
        return record

    axis_hat = np.asarray(reference_axis, dtype=float)
    axis_hat = axis_hat / np.linalg.norm(axis_hat)

    for n_pixel in n_values:
        try:
            pooled = pooled_outcome_clouds(normalized, n_pixel, times)
        except RuntimeError as error:
            record["by_size"][str(n_pixel)] = {"error": str(error)}
            record["rejection_reasons"].append(f"N={n_pixel}: {error}")
            return record

        metrics = score_pooled_clouds(pooled)
        metrics["per_time"] = pooled["per_time"]
        if metrics.get("axis_status") == "ok":
            metrics["axis_dot_reference"] = float(np.dot(metrics["n_hat"], axis_hat))
            metrics["axis_angle_deg_from_reference"] = float(
                np.degrees(np.arccos(np.clip(abs(metrics["axis_dot_reference"]), -1.0, 1.0)))
            )
        record["by_size"][str(n_pixel)] = metrics

    record["passed"] = not record["rejection_reasons"]
    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a preferred-basis candidate across a size ladder."
    )
    parser.add_argument("--candidate", type=Path, required=True,
                        help="JSON file holding one ChainConfig plus reference_axis.")
    parser.add_argument("--log", type=Path,
                        default=Path("reports/preferred_basis/experiment_log.jsonl"))
    parser.add_argument("--n-ladder", type=int, nargs="+", default=[8])
    args = parser.parse_args()

    payload = json.loads(args.candidate.read_text(encoding="utf-8"))
    reference_axis = payload.pop("reference_axis")
    config = ChainConfig(**payload)
    record = evaluate_config(config, tuple(args.n_ladder), np.asarray(reference_axis, dtype=float))

    status = "PASSED" if record["passed"] else "REJECTED"
    print(f"[{status}] {config.name}  (rung {config.rung})")
    for n_pixel in args.n_ladder:
        block = record["by_size"].get(str(n_pixel), {})
        if "error" in block:
            print(f"  N={n_pixel:2d}  ERROR {block['error']}")
            continue
        if block.get("axis_status") != "ok":
            print(f"  N={n_pixel:2d}  axis refused: {block.get('refusal_reason')}")
            continue
        quartet = block["quartet"]
        print(
            f"  N={n_pixel:2d}  B1={block['B1']:+.4f}"
            f"  axis_err={block['axis_angle_deg_from_reference']:.3f} deg"
            f"  odd(l>=3)={block['odd_harmonic']['higher_odd_l3_l5_l7_leakage']:.4f}"
            f"  E_marg={quartet['E_marg']:.4f}  quartet={quartet['quartet_status']}"
        )
    for reason in record["rejection_reasons"]:
        print(f"  reject: {reason}")

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with open(args.log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
