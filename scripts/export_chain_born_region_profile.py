"""Export the house-style angular profile for a chain-Born region center.

Emits the `results.npz` array schema the ring-catalog diagnostics use, so that
`_plot_angular` in `build_network_wd_nonborn_size_spacing_figures.py`,
`_plot_ratio` in `plot_hz0_0_ring_spacing_born_catalog.py`, and
`core.born_profile_export.load_profile` all work on it unchanged. No new plotting
style is introduced.

Binning follows the house convention and the two counts are never mixed:
`S_born` is computed on 100 bins, while the plotted `P` and `R` use 64. Empty
bins are masked through `R_occupied` rather than imputed, so the reported error
is the occupied-bin RMSE and the bin coverage is reported beside it.

Usage::

    python scripts/export_chain_born_region_profile.py --name b11_screen_00 \
        --out reports/chain_born_regions/screen_00
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

from core.distribution_fit import fit_folded_circular_models
from scripts.eval_chain_born import (
    PARAMETER_NAMES,
    PROFILE_BINS,
    S_BORN_BINS,
    TIMES,
    ChainConfig,
    born_profile,
    _score_theta,
    normalize,
    pooled_roots,
)

DEFAULT_LOG = Path("reports/chain_born_regions/experiment_log.jsonl")


def load_config(name: str, log_path: Path) -> ChainConfig:
    """Rebuild a configuration from its logged record."""

    record = None
    with open(log_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            candidate = json.loads(line)
            if candidate.get("name") == name:
                record = candidate  # keep the last, which is the newest
    if record is None:
        raise SystemExit(f"no record named {name!r} in {log_path}")
    params = {k: v for k, v in record["parameters"].items() if k in PARAMETER_NAMES}
    return ChainConfig(
        name=record["name"],
        hypothesis=record.get("hypothesis", ""),
        rung=record.get("rung", ""),
        **params,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Candidate name in the log.")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--n-pixel", type=int, default=10)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    config, factor = normalize(load_config(args.name, args.log))
    per_time, per_time_phi, diagnostics = pooled_roots(config, args.n_pixel, TIMES)
    theta = np.concatenate(per_time)

    # The frozen score, on its own bin count.
    score = _score_theta(theta, n_bins=S_BORN_BINS)
    # The plotted profile, on the house plotting bin count.
    arrays = born_profile(theta, n_bins=PROFILE_BINS)

    # Wrapped-Gaussian and wrapped-Cauchy overlays, on a fine grid for plotting.
    fit = fit_folded_circular_models(theta, arrays["edges"])
    grid = np.linspace(0.0, np.pi, 512)
    width = arrays["edges"][1] - arrays["edges"][0]
    # Convert fitted bin probabilities to a density on the plotting grid by
    # interpolating at bin centres; this is a display overlay, not a fit statistic.
    arrays["fit_grid"] = grid
    arrays["wg_density"] = np.interp(
        grid, arrays["centers"], fit.wrapped_gaussian_probabilities / width
    )
    arrays["wc_density"] = np.interp(
        grid, arrays["centers"], fit.wrapped_cauchy_probabilities / width
    )

    if per_time_phi:
        phi = np.concatenate(per_time_phi)
        azimuthal_moments = {
            str(m): float(abs(np.mean(np.exp(1j * m * phi)))) for m in (1, 2, 3, 4)
        }
        azimuthal_floor = float(1.0 / np.sqrt(phi.size))
    else:
        azimuthal_moments, azimuthal_floor = {}, float("nan")

    occupied = arrays["R_occupied"]
    rmse = float(
        np.sqrt(np.mean((arrays["R"][occupied] - arrays["R_born"][occupied]) ** 2))
    )

    args.out.mkdir(parents=True, exist_ok=True)
    np.savez(args.out / "results.npz", **arrays)
    metadata = {
        "name": args.name,
        "n_pixel": args.n_pixel,
        "scale_factor": factor,
        "parameters": config.parameters(),
        "times": list(TIMES),
        "n_roots": int(theta.size),
        "S_born_bins": S_BORN_BINS,
        "profile_bins": PROFILE_BINS,
        "S_born": score["S_born"],
        "E_marg_occupied": score["E_marg_occupied"],
        "born_RMSE_occupied": rmse,
        "coverage_bins_100": score["coverage_bins"],
        "coverage_fraction_profile": float(np.mean(occupied)),
        "wrapped_gaussian_sigma": fit.wrapped_gaussian_sigma,
        "wrapped_cauchy_gamma": fit.wrapped_cauchy_gamma,
        "preferred_model": fit.preferred_model,
        # Azimuthal structure, recorded beside the polar score so the artifact
        # cannot be read as a strong-Born result. The Born profile is azimuthally
        # symmetric, so a moment far above the noise floor is m != 0 leakage that
        # the polar marginal hides (SPEC.md 5.2, 6.3).
        "azimuthal_moments": azimuthal_moments,
        "azimuthal_noise_floor": azimuthal_floor,
        "criterion_tested": "weak (polar marginal) only; strong Born not evaluated",
        "sign_convention": (
            "builder carries an overall minus sign; code coefficients are the "
            "negatives of the SPEC.md section 9 coefficients"
        ),
        **diagnostics,
    }
    (args.out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    print(f"[*] {args.name} at N={args.n_pixel}: {theta.size} roots")
    print(f"    S_born ({S_BORN_BINS} bins) = {score['S_born']:+.4f}"
          f"   coverage {score['coverage_bins']}/{S_BORN_BINS}")
    print(f"    occupied-bin RMSE ({PROFILE_BINS} bins) = {rmse:.4f}"
          f"   coverage {np.count_nonzero(occupied)}/{PROFILE_BINS}")
    if azimuthal_moments:
        print(f"    azimuthal moments {azimuthal_moments}"
              f"  (noise floor {azimuthal_floor:.4f}) -> weak criterion only")
    print(f"    fitted sigma={fit.wrapped_gaussian_sigma:.4f} "
          f"gamma={fit.wrapped_cauchy_gamma:.4f} preferred={fit.preferred_model}")
    print(f"[*] wrote {args.out/'results.npz'} and {args.out/'metadata.json'}")


if __name__ == "__main__":
    main()
