"""Fixed Verifier / Evaluator for Born-Similarity Optimization at N=11.

Evaluates a candidate Hamiltonian configuration implemented via SinglePixelHamiltonianQuSpin
over an ensemble of long evolution times, computes the time-averaged P(theta) and R(theta),
and reports the canonical 100-bin S_born similarity metric.

Usage:
    python scripts/eval_born_n11.py --candidate candidate.json --log reports/born_optimization/experiment_log.jsonl
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Sequence

# Ensure repository root is in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from core.analysis import evolution_subblocks_from_eigenbasis
from core.born import born_ratio_from_theta, theta_pair_from_radii
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum


# Fixed default long-time collection (50 points between 100.0 and 1000.0)
DEFAULT_LONG_TIMES = tuple(np.geomspace(100.0, 1000.0, 50))


def build_candidate_hamiltonian(config: dict[str, Any], n_pixel: int = 11) -> SinglePixelHamiltonianQuSpin:
    """Build SinglePixelHamiltonianQuSpin with parameters from candidate config."""
    allowed_keys = {
        "J", "Jpm", "Jxx", "Jyy", "Jx", "Jy", "Jz", "Jzx", "Jcpm",
        "hx", "hz", "hx0", "hz0", "connectivity", "central_coupling",
        "J2", "Jpm2", "seed", "use_symmetry"
    }
    filtered_kwargs = {k: v for k, v in config.items() if k in allowed_keys}
    filtered_kwargs.setdefault("connectivity", "ring")
    filtered_kwargs.setdefault("central_coupling", "auto")
    filtered_kwargs.setdefault("use_symmetry", True)
    return SinglePixelHamiltonianQuSpin(N_pixel=n_pixel, **filtered_kwargs)


def evaluate_born_score_n11(
    config: dict[str, Any],
    n_pixel: int = 11,
    times: Sequence[float] = DEFAULT_LONG_TIMES,
    n_bins: int = 100,
    max_epsilon: float = 0.150,
) -> dict[str, Any]:
    """Execute the fixed evaluation protocol on a candidate configuration."""
    # 0. Perturbative validity check: g << Lambda_detector
    detector_scale = max(
        abs(config.get("J", 1.0)),
        abs(config.get("Jxx", 0.0)),
        abs(config.get("Jyy", 0.0)),
        abs(config.get("Jpm", 0.0)),
        abs(config.get("J2", 0.0)),
        abs(config.get("Jpm2", 0.0)),
        abs(config.get("hx", 0.0)),
        abs(config.get("hz", 0.0)),
    )
    g_max = max(
        abs(config.get("Jx", 0.0)),
        abs(config.get("Jy", 0.0)),
        abs(config.get("Jz", 0.0)),
        abs(config.get("Jzx", 0.0)),
        abs(config.get("Jcpm", 0.0)),
    )
    if detector_scale == 0.0:
        return {
            "passed": False,
            "error": "Unphysical configuration: Intrinsic detector scale is zero.",
            "S_born": -1.0,
            "epsilon": float("inf"),
        }

    epsilon = g_max / detector_scale
    if epsilon > max_epsilon:
        return {
            "passed": False,
            "error": f"Non-perturbative coupling violation: epsilon = {epsilon:.3f} > {max_epsilon:.3f} (g_max={g_max:.3e}, Lambda_det={detector_scale:.3e})",
            "S_born": -1.0,
            "epsilon": float(epsilon),
            "detector_scale": float(detector_scale),
            "g_max": float(g_max),
        }

    hamiltonian = build_candidate_hamiltonian(config, n_pixel=n_pixel)

    # 1. Hermiticity check
    h_dense = hamiltonian.generate()
    scale = max(float(np.linalg.norm(h_dense)), 1.0)
    hermiticity_res = float(np.linalg.norm(h_dense - h_dense.conj().T) / scale)
    if hermiticity_res > 1.0e-12:
        return {
            "passed": False,
            "error": f"Hermiticity violation: {hermiticity_res:.3e}",
            "S_born": -1.0,
            "hermiticity_residual": hermiticity_res,
        }

    # 2. Diagonalize once
    try:
        energies, vectors = hamiltonian.diagonalize()
    except Exception as err:
        return {
            "passed": False,
            "error": f"Diagonalization failure: {err}",
            "S_born": -1.0,
        }

    # 3. Accumulate polar angles over the long-time grid
    all_theta0: list[np.ndarray] = []
    all_theta1: list[np.ndarray] = []
    max_isometry_residual = 0.0

    for t in times:
        u00, u10 = evolution_subblocks_from_eigenbasis(energies, vectors, float(t))
        identity = np.eye(u00.shape[1], dtype=np.complex128)
        isometry = float(np.linalg.norm(u00.conj().T @ u00 + u10.conj().T @ u10 - identity))
        max_isometry_residual = max(max_isometry_residual, isometry)
        if isometry > 1.0e-9:
            return {
                "passed": False,
                "error": f"Column isometry broken at t={t}: residual={isometry:.3e}",
                "S_born": -1.0,
                "max_isometry_residual": max_isometry_residual,
            }

        spectrum = generalized_relative_evolution_spectrum(u00, u10)
        radii = spectrum.radii
        th0, th1 = theta_pair_from_radii(radii)
        all_theta0.append(th0)
        all_theta1.append(th1)

    theta0 = np.concatenate(all_theta0)
    theta1 = np.concatenate(all_theta1)

    # 4. Canonical Born Ratio & Similarity Metric (100 bins)
    ratio_result = born_ratio_from_theta(theta0, theta1, n_theta=n_bins)
    s_born = float(ratio_result.similarity)
    mean_abs_err = float(ratio_result.mean_abs_error)
    coverage = int(np.count_nonzero(ratio_result.counts_0 + ratio_result.counts_1))

    # Quality gates
    passed = True
    rejection_reasons = []
    if coverage < 20:
        passed = False
        rejection_reasons.append(f"Insufficient angular coverage: {coverage} bins occupied (minimum 20 required).")

    if not np.isfinite(s_born):
        passed = False
        rejection_reasons.append("S_born is not finite.")

    return {
        "passed": passed,
        "S_born": s_born,
        "mean_abs_error": mean_abs_err,
        "coverage_bins": coverage,
        "epsilon": float(epsilon),
        "max_isometry_residual": max_isometry_residual,
        "hermiticity_residual": hermiticity_res,
        "n_samples": len(theta0),
        "rejection_reasons": rejection_reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Born-similarity at N=11 for a candidate Hamiltonian.")
    parser.add_argument("--candidate", type=Path, required=True, help="Path to candidate JSON config.")
    parser.add_argument("--log", type=Path, default=Path("reports/born_optimization/experiment_log.jsonl"))
    parser.add_argument("--champion", type=Path, default=Path("reports/born_optimization/champion.json"))
    parser.add_argument("--hypothesis", type=str, default="", help="Physical rationale for this candidate.")
    parser.add_argument("--max-epsilon", type=float, default=0.150, help="Maximum allowed perturbative ratio g_max / Lambda_det.")
    args = parser.parse_args()

    if not args.candidate.is_file():
        sys.exit(f"Candidate file not found: {args.candidate}")

    with open(args.candidate, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    print(f"[*] Evaluating candidate {args.candidate.name} at N=11 across {len(DEFAULT_LONG_TIMES)} long times...")
    result = evaluate_born_score_n11(config_data, n_pixel=11, max_epsilon=args.max_epsilon)

    status_str = "PASSED" if result["passed"] else "REJECTED"
    s_born = result.get("S_born", -1.0)
    print(f"[{status_str}] S_Born = {s_born:.6f} | Mean Abs Error = {result.get('mean_abs_error', 1.0):.6f} | Coverage = {result.get('coverage_bins', 0)}/100 bins")

    # Read current champion
    current_best_s = -1.0
    if args.champion.is_file():
        try:
            champ = json.loads(args.champion.read_text(encoding="utf-8"))
            current_best_s = float(champ.get("metrics", {}).get("S_born", -1.0))
        except Exception:
            pass

    decision = "REJECT"
    if result["passed"] and s_born > current_best_s:
        decision = "PROMOTE"
        print(f"[!] NEW CHAMPION: S_Born improved from {current_best_s:.6f} to {s_born:.6f}!")
        args.champion.parent.mkdir(parents=True, exist_ok=True)
        champ_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": config_data,
            "metrics": result,
            "hypothesis": args.hypothesis,
        }
        with open(args.champion, "w", encoding="utf-8") as f:
            json.dump(champ_payload, f, indent=2)

    # Append to log
    args.log.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidate": str(args.candidate),
        "decision": decision,
        "config": config_data,
        "metrics": result,
        "hypothesis": args.hypothesis,
    }
    with open(args.log, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
