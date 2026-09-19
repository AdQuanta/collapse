#!/usr/bin/env python3.11
"""Compare reduced-qubit memory against Born-like root statistics.

Exploratory mechanism study.  It claims no `SPEC.md` paper-readiness gate, and
no verifier is frozen for it.  Every measure definition below is fixed here,
before the first production run, so that nothing is tuned after seeing results.

Sign convention.  `SinglePixelHamiltonian*` builds

    H = -J sum_<ij> Z_i Z_j - J_z Z_0 sum_{i in targets} Z_i
        - sum_i (h_x X_i + h_z Z_i) - h_x0 X_0 - h_z0 Z_0,

so the coefficients here are the negatives of the `SPEC.md` section 9 ones:
`J_SPEC = -J_code` and `g_SPEC = -Jz_code`.  Every packet records this.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work/_mplconfig"))

from core.born import born_ratio_from_radii  # noqa: E402
from core.hamiltonians.numpy_hamiltonians import (  # noqa: E402
    SinglePixelHamiltonianNumpy,
    _central_targets,
)
from core.hamiltonians.quspin_hamiltonians import (  # noqa: E402
    SinglePixelHamiltonianQuSpin,
)
from core.markovianity import (  # noqa: E402
    blp_backflow,
    bloch_series_from_spectrum,
    fibonacci_directions,
    rhp_divisibility,
    volume_measure,
)
from core.projective_roots import production_root_spectrum  # noqa: E402
from core.sobol_coupling_scan import _diagnostics, fit_distributions  # noqa: E402

# ── Frozen measure definitions (fixed before the first production run) ──────
PLOT_BINS = 64          # plotted P/R resolution, matching the ring catalog
SBORN_BINS = 100        # S_born resolution, matching core.born's default
EARLY_WINDOW = (0.0, 60.0)
LATE_WINDOW = (100.0, 160.0)
WINDOW_STEP = 0.1       # both memory windows share length and sampling
BORN_TIMES = np.geomspace(100.0, 1000.0, 6)   # repo long-time convention
DIRECTION_COUNT = 512   # Fibonacci grid for the BLP direction maximisation
DETECTOR_J = 1.0        # energy unit
BUILDER_TOLERANCE = 1.0e-12

CELLS = (
    ("ring", "all", "SPEC 9.1 production"),
    ("chain", "first", "SPEC 9.2 production"),
    ("ring", "first", "control"),
    ("chain", "all", "control"),
)
HX_OVER_J = (0.5, 1.0, 1.5)
HX0 = (0.0, 0.5)
SCALINGS = ("norm", "fluctuation")


def coupling_for(epsilon, targets, hx, hz, scaling):
    """Per-edge J_z giving the requested matched effective coupling.

    ``norm`` matches the total coupling operator norm ``|J_z| * targets`` across
    geometries, which for the collective ring is exactly the conservative
    ``g_N ~ 1/N`` baseline of `SPEC.md` section 9.  ``fluctuation`` matches the
    typical magnetization fluctuation instead, the ``alpha = 1/2`` case of the
    commuting/QND trichotomy.
    """

    scale = max(abs(DETECTOR_J), abs(hx), abs(hz))
    divisor = targets if scaling == "norm" else np.sqrt(targets)
    return epsilon * scale / divisor


def configurations(sizes, epsilon, hz):
    for connectivity, central, role in CELLS:
        for ratio in HX_OVER_J:
            for hx0 in HX0:
                for scaling in SCALINGS:
                    for size in sizes:
                        targets = len(
                            _central_targets(1, size, connectivity, central)
                        )
                        hx = ratio * DETECTOR_J
                        yield {
                            "connectivity": connectivity,
                            "central_coupling": central,
                            "role": role,
                            "N": int(size),
                            "hx_over_J": float(ratio),
                            "hx0": float(hx0),
                            "scaling": scaling,
                            "epsilon": float(epsilon),
                            "central_targets": int(targets),
                            "J": DETECTOR_J,
                            "hx": float(hx),
                            "hz": float(hz),
                            "Jz": float(
                                coupling_for(epsilon, targets, hx, hz, scaling)
                            ),
                        }


def build_parameters(config):
    return dict(
        N_pixel=config["N"], J=config["J"], Jpm=0.0, Jxx=0.0, Jyy=0.0,
        Jx=0.0, Jy=0.0, Jz=config["Jz"], Jzx=0.0, Jcpm=0.0,
        hx=config["hx"], hz=config["hz"], hx0=config["hx0"], hz0=0.0,
        connectivity=config["connectivity"],
        central_coupling=config["central_coupling"],
    )


def memory_metrics(eigenvalues, eigenvectors, directions, detector_state, label):
    start, stop = EARLY_WINDOW if label == "early" else LATE_WINDOW
    times = np.arange(start, stop + 0.5 * WINDOW_STEP, WINDOW_STEP)
    matrices, translations = bloch_series_from_spectrum(
        eigenvalues, eigenvectors, times, detector_state
    )
    result = {"window": [float(start), float(stop)], "samples": int(times.size)}
    result.update(blp_backflow(matrices, directions))
    result.update(volume_measure(matrices))
    result.update(rhp_divisibility(matrices, translations))
    return result


def born_metrics(eigenvalues, eigenvectors):
    """Pool projective roots over the fixed long-time grid, then diagnose."""

    pooled = []
    residuals = []
    for time in BORN_TIMES:
        unitary = (eigenvectors * np.exp(-1j * eigenvalues * time)) @ eigenvectors.conj().T
        spectrum = production_root_spectrum(unitary)
        pooled.append(spectrum.eigenvalues)
        residuals.append(spectrum.maximum_homogeneous_residual)
    values = np.concatenate(pooled)
    metrics, arrays = _diagnostics(values, PLOT_BINS)
    theta = 2.0 * np.arctan(np.abs(values[np.isfinite(values)]))
    _, fit_arrays = fit_distributions(theta, PLOT_BINS, 512, 32, 1.0e-10)
    arrays.update(fit_arrays)
    metrics["maximum_homogeneous_residual"] = float(np.max(residuals))
    metrics["born_times"] = BORN_TIMES.tolist()
    metrics["S_born_bins"] = SBORN_BINS
    metrics["plot_bins"] = PLOT_BINS
    return metrics, arrays


def run_case(config, output_root, directions, *, cross_check):
    parameters = build_parameters(config)
    hamiltonian = np.asarray(
        SinglePixelHamiltonianQuSpin(**parameters).generate(), dtype=np.complex128
    )
    builder_residual = float("nan")
    if cross_check:
        reference = SinglePixelHamiltonianNumpy(**parameters).generate()
        builder_residual = float(np.abs(hamiltonian - reference).max())
        if not builder_residual < BUILDER_TOLERANCE:
            raise RuntimeError(
                f"QuSpin and NumPy builders disagree by {builder_residual:.3e} "
                f"for {config}"
            )

    hermiticity = float(np.abs(hamiltonian - hamiltonian.conj().T).max())
    eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)

    memory = {
        "mixed_early": memory_metrics(
            eigenvalues, eigenvectors, directions, None, "early"
        ),
        "mixed_late": memory_metrics(
            eigenvalues, eigenvectors, directions, None, "late"
        ),
    }
    up = np.zeros(hamiltonian.shape[0] // 2)
    up[0] = 1.0
    memory["up_early"] = memory_metrics(
        eigenvalues, eigenvectors, directions, up, "early"
    )

    born, arrays = born_metrics(eigenvalues, eigenvectors)

    name = (
        f"{config['connectivity']}_{config['central_coupling']}"
        f"__hx{config['hx_over_J']:.2f}__hx0{config['hx0']:.2f}"
        f"__{config['scaling']}__N{config['N']:02d}"
    )
    case_dir = output_root / name
    case_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(case_dir / "results.npz", **arrays)
    (case_dir / "metrics.json").write_text(
        json.dumps({"born": born, "memory": memory}, indent=2, sort_keys=True)
    )
    (case_dir / "metadata.json").write_text(
        json.dumps(
            {
                "config": config,
                "builder": "SinglePixelHamiltonianQuSpin",
                "cross_check_builder": "SinglePixelHamiltonianNumpy",
                "builder_max_abs_difference": builder_residual,
                "hermiticity_residual": hermiticity,
                "sign_convention": (
                    "H = -J sum ZZ - Jz Z0 sum Z - sum (hx X + hz Z) - hx0 X0; "
                    "J_SPEC = -J_code and g_SPEC = -Jz_code"
                ),
                "frozen_definitions": {
                    "plot_bins": PLOT_BINS,
                    "s_born_bins": SBORN_BINS,
                    "early_window": list(EARLY_WINDOW),
                    "late_window": list(LATE_WINDOW),
                    "window_step": WINDOW_STEP,
                    "born_times": BORN_TIMES.tolist(),
                    "direction_count": DIRECTION_COUNT,
                },
                "gate_credit": "none; exploratory mechanism study",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return {
        "name": name,
        **config,
        "S_born": born["S_born"],
        "born_RMSE_occupied": born["born_RMSE_occupied"],
        "occupied_fraction": born["occupied_fraction"],
        "n_blp_mixed_early": memory["mixed_early"]["n_blp"],
        "n_blp_mixed_late": memory["mixed_late"]["n_blp"],
        "n_blp_up_early": memory["up_early"]["n_blp"],
        "rhp_early": memory["mixed_early"]["rhp_violation"],
        "volume_backflow_early": memory["mixed_early"]["volume_backflow"],
    }


def parser():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--sizes", type=int, nargs="+", default=[4, 5, 6, 7, 8, 9])
    ap.add_argument("--epsilon", type=float, default=0.10)
    ap.add_argument("--hz", type=float, default=0.3)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-cross-check", action="store_true")
    return ap


def main():
    args = parser().parse_args()
    cases = list(configurations(args.sizes, args.epsilon, args.hz))
    if args.dry_run:
        print(f"configurations: {len(cases)}")
        print(f"cells: {len(CELLS)}  hx/J: {HX_OVER_J}  hx0: {HX0}")
        print(f"scalings: {SCALINGS}  sizes: {args.sizes}")
        print(f"epsilon: {args.epsilon}  hz: {args.hz}")
        for case in cases[:4]:
            print("  ", case)
        return 0

    args.output_root.mkdir(parents=True, exist_ok=True)
    directions = fibonacci_directions(DIRECTION_COUNT)
    summary = []
    for index, config in enumerate(cases, start=1):
        record = run_case(
            config, args.output_root, directions, cross_check=not args.no_cross_check
        )
        summary.append(record)
        print(
            f"[{index:4d}/{len(cases)}] {record['name']}  "
            f"S_born={record['S_born']:.4f}  "
            f"N_BLP={record['n_blp_mixed_early']:.4f}",
            flush=True,
        )
    (args.output_root / "summary.json").write_text(
        json.dumps(
            {
                "generated_utc": datetime.now(timezone.utc).isoformat(),
                "configuration_count": len(summary),
                "records": summary,
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.output_root/'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
