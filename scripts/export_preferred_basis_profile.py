"""Export the house-style angular profile for a preferred-basis campaign record.

Companion to ``scripts/export_chain_born_region_profile.py``. Reuses the same
``results.npz``/``_plot_angular``/``_plot_ratio`` machinery, but the polar
angle plotted is ``theta'``, measured from the *fitted preferred axis*
``n_hat``, not from an arbitrary lab-frame pole. ``P(pi - theta')`` is outcome
1's genuine marginal: since outcome 1's cloud is the exact antipodal
pushforward of outcome 0's (``core.outcome_measures.antipodal_bloch_cloud``),
its polar marginal relative to any fixed axis is identically outcome 0's
marginal reflected at ``pi - theta'``, so this is not a synthetic stand-in
the way the historical single-pencil shortcut was (goal section 4, WP1).

The reused ``_plot_ratio`` text box prints its legacy field names
(``S_born``/``born_RMSE_occupied``); here those two slots carry ``B1`` and the
occupied-bin RMSE of the strong-criterion ratio against
``cos^2(theta'/2)`` respectively, and this substitution is recorded explicitly
in ``metadata.json`` and the figure caption text -- the chart is reused
unmodified, not its meaning.

Usage::

    python scripts/export_preferred_basis_profile.py --name screen_00 \
        --n-pixel 10 --out reports/preferred_basis/screen_00_N10
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from core.distribution_fit import fit_folded_circular_models
from core.outcome_measures import (
    odd_harmonic_power,
    preferred_axis_from_cloud,
    spec_quartet,
)
from eval_chain_born import PARAMETER_NAMES, ChainConfig
from eval_preferred_basis import TIMES, pooled_outcome_clouds

DEFAULT_LOG = Path("reports/preferred_basis/experiment_log.jsonl")


def load_config(name: str, log_path: Path) -> tuple[ChainConfig, list]:
    record = None
    with open(log_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            candidate = json.loads(line)
            if candidate.get("name") == name:
                record = candidate
    if record is None:
        raise SystemExit(f"no record named {name!r} in {log_path}")
    params = {k: v for k, v in record["parameters"].items() if k in PARAMETER_NAMES}
    config = ChainConfig(
        name=record["name"], hypothesis=record.get("hypothesis", ""),
        rung=record.get("rung", ""), **params,
    )
    return config, record["reference_axis"]


def angular_profile(theta_0: np.ndarray, theta_1: np.ndarray, n_bins: int) -> dict[str, np.ndarray]:
    edges = np.linspace(0.0, np.pi, n_bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    counts_0, _ = np.histogram(theta_0, bins=edges)
    counts_1, _ = np.histogram(theta_1, bins=edges)
    width = edges[1] - edges[0]
    total = counts_0 + counts_1
    occupied = total > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(occupied, counts_0 / np.maximum(total, 1), np.nan)
    denom_0 = max(float(theta_0.size) * width, np.finfo(float).tiny)
    denom_1 = max(float(theta_1.size) * width, np.finfo(float).tiny)
    return {
        "edges": edges, "centers": centers,
        "p_theta": counts_0 / denom_0,
        "p_pi_minus_theta": counts_1 / denom_1,
        "R": ratio, "R_occupied": occupied,
        "R_born": np.cos(centers / 2.0) ** 2,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--n-pixel", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--profile-bins", type=int, default=64)
    args = parser.parse_args()

    config, reference_axis = load_config(args.name, args.log)
    pooled = pooled_outcome_clouds(config, args.n_pixel, TIMES, keep_per_time_points=True)
    axis_result = preferred_axis_from_cloud(pooled["points_0"], pooled["weights_0"])
    if axis_result.status != "ok":
        raise SystemExit(f"axis refused: {axis_result.refusal_reason}")
    n_hat = axis_result.n_hat

    theta_0 = np.arccos(np.clip(pooled["points_0"] @ n_hat, -1.0, 1.0))
    theta_1 = np.arccos(np.clip(pooled["points_1"] @ n_hat, -1.0, 1.0))
    arrays = angular_profile(theta_0, theta_1, args.profile_bins)

    fit = fit_folded_circular_models(theta_0, arrays["edges"])
    grid = np.linspace(0.0, np.pi, 512)
    width = arrays["edges"][1] - arrays["edges"][0]
    arrays["fit_grid"] = grid
    arrays["wg_density"] = np.interp(grid, arrays["centers"], fit.wrapped_gaussian_probabilities / width)
    arrays["wc_density"] = np.interp(grid, arrays["centers"], fit.wrapped_cauchy_probabilities / width)

    occupied = arrays["R_occupied"]
    rmse = float(np.sqrt(np.mean((arrays["R"][occupied] - arrays["R_born"][occupied]) ** 2)))

    harmonics = odd_harmonic_power(pooled["points_0"], pooled["weights_0"], n_hat, l_max=7)
    quartet = spec_quartet(
        pooled["points_0"], pooled["weights_0"], pooled["points_1"], pooled["weights_1"], n_hat,
    )
    axis_hat = np.asarray(reference_axis, dtype=float)
    axis_hat = axis_hat / np.linalg.norm(axis_hat)
    axis_angle_deg = float(np.degrees(np.arccos(np.clip(abs(np.dot(n_hat, axis_hat)), -1.0, 1.0))))

    args.out.mkdir(parents=True, exist_ok=True)
    arrays["points_0"] = pooled["points_0"]
    arrays["points_1"] = pooled["points_1"]
    arrays["n_hat"] = n_hat
    for index, (per_time_0, per_time_1) in enumerate(
        zip(pooled["per_time_points_0"], pooled["per_time_points_1"])
    ):
        arrays[f"points_0_time{index}"] = per_time_0
        arrays[f"points_1_time{index}"] = per_time_1
    arrays["times_array"] = np.asarray(TIMES, dtype=float)
    np.savez(args.out / "results.npz", **arrays)
    metadata = {
        "name": args.name,
        "n_pixel": args.n_pixel,
        "parameters": config.parameters(),
        "times": list(TIMES),
        "n_roots_0": int(pooled["points_0"].shape[0]),
        "n_roots_1": int(pooled["points_1"].shape[0]),
        "profile_bins": args.profile_bins,
        "n_hat": n_hat.tolist(),
        "B1": axis_result.B1,
        "condition_number_S": axis_result.condition_number,
        "reference_axis": reference_axis,
        "axis_angle_deg_from_reference": axis_angle_deg,
        "odd_harmonic_l3_l5_l7_leakage": harmonics["higher_odd_l3_l5_l7_leakage"],
        "power_by_l": harmonics["power_by_l"].tolist(),
        "quartet": {k: v for k, v in quartet.items() if k != "quartet_resolution"} | {
            "quartet_resolution": list(quartet["quartet_resolution"]) if quartet["quartet_resolution"] else None,
        },
        "occupied_bin_RMSE_vs_born": rmse,
        "coverage_fraction_profile": float(np.mean(occupied)),
        "wrapped_gaussian_sigma": fit.wrapped_gaussian_sigma,
        "wrapped_cauchy_gamma": fit.wrapped_cauchy_gamma,
        "preferred_model": fit.preferred_model,
        "criterion_tested": (
            "strong (full-sphere, outcome-resolved, binning-free axis fit); "
            "P(pi-theta') is outcome 1's genuine marginal, exact via the "
            "antipodal pushforward theorem, not a single-pencil proxy"
        ),
        "legacy_plot_field_note": (
            "the reused _plot_ratio text box prints its legacy keys S_born and "
            "born_RMSE_occupied; here they hold B1 and occupied_bin_RMSE_vs_born "
            "respectively, not the histogram S_born statistic"
        ),
        "sign_convention": (
            "builder carries an overall minus sign; code coefficients are the "
            "negatives of the SPEC.md section 9 coefficients"
        ),
        "hermiticity_residual": pooled["hermiticity_residual"],
        "max_unitary_residual": pooled["max_unitary_residual"],
    }
    (args.out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    print(f"[*] {args.name} at N={args.n_pixel}: B1={axis_result.B1:.4f}"
          f"  axis_err={axis_angle_deg:.3f} deg  cond(S)={axis_result.condition_number:.3e}")
    print(f"    odd(l>=3) leakage={harmonics['higher_odd_l3_l5_l7_leakage']:.4f}"
          f"  quartet: {quartet['quartet_status']}")
    print(f"[*] wrote {args.out/'results.npz'} and {args.out/'metadata.json'}")


if __name__ == "__main__":
    main()
