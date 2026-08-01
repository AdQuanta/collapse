"""Numerically validate the exact Cayley bridge and leading Magnus reduction."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collapse.relative_unitary_theory import (  # noqa: E402
    cayley_matrix,
    exact_relative_objects,
    folded_angles_from_relative_unitary,
    leading_cayley_approximation,
)


def _hermitian(rng: np.random.Generator, dimension: int) -> np.ndarray:
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension))
    return 0.5 * (raw + raw.conj().T)


def main() -> None:
    output = ROOT / "reports" / "detector_gap_matrix_study_2026-07-21"
    figure_root = output / "figures"
    data_root = output / "data"
    figure_root.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(20260721)
    detector = _hermitian(rng, 5)
    coupling = _hermitian(rng, 5)
    detector /= np.linalg.norm(detector, ord=2)
    coupling /= np.linalg.norm(coupling, ord=2)
    time = 2.3
    strengths = np.asarray([0.08, 0.04, 0.02, 0.01, 0.005], dtype=float)
    rows: list[dict[str, float]] = []
    exact_bridge_errors: list[float] = []
    weak_errors: list[float] = []
    angle_errors: list[float] = []

    for strength in strengths:
        _u00, _u10, relative, exact_m = exact_relative_objects(detector, coupling, strength, time)
        bridge = cayley_matrix(relative)
        _kernel, approximate_relative, approximate_m = leading_cayley_approximation(detector, coupling, strength, time)
        bridge_error = float(np.linalg.norm(exact_m - bridge, ord=2))
        weak_error = float(np.linalg.norm(exact_m - approximate_m, ord=2))
        exact_theta = folded_angles_from_relative_unitary(relative)
        approximate_theta = folded_angles_from_relative_unitary(approximate_relative)
        angle_error = float(np.max(np.abs(exact_theta - approximate_theta)))
        exact_bridge_errors.append(bridge_error)
        weak_errors.append(weak_error)
        angle_errors.append(angle_error)
        rows.append(
            {
                "g": float(strength),
                "time": time,
                "exact_cayley_operator_error": bridge_error,
                "leading_magnus_operator_error": weak_error,
                "leading_magnus_max_theta_error": angle_error,
            }
        )

    slope = float(np.polyfit(np.log(strengths), np.log(weak_errors), 1)[0])
    with (data_root / "relative_unitary_validation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    phase = np.linspace(-np.pi + 0.015, np.pi - 0.015, 1200)
    radius = np.abs(np.tan(phase / 2.0))
    theta = 2.0 * np.arctan(radius)
    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.25))
    order = np.argsort(strengths)
    axes[0].loglog(strengths[order], np.asarray(weak_errors)[order], "o-", color="#2563eb", label=r"$\|M-M_{\rm Magnus}\|_2$")
    axes[0].loglog(strengths[order], np.asarray(angle_errors)[order], "s--", color="#dc2626", label=r"$\max|\theta-\theta_{\rm Magnus}|$")
    axes[0].set_xticks(strengths[order])
    axes[0].set_xticklabels([f"{value:g}" for value in strengths[order]])
    axes[0].xaxis.set_minor_formatter(NullFormatter())
    axes[0].set(xlabel="coupling $g$", ylabel="absolute error", title=rf"Fixed $t={time:g}$; fitted operator-error slope ${slope:.2f}$")
    axes[0].grid(alpha=0.25)
    axes[0].legend(frameon=False)

    axes[1].plot(phase, radius, color="#7c3aed", linewidth=1.5, label=r"$|\lambda|=|\tan(\varphi/2)|$")
    twin = axes[1].twinx()
    twin.plot(phase, theta, color="#059669", linewidth=1.3, linestyle="--", label=r"$\theta=|\varphi|$")
    axes[1].set(xlabel=r"relative-unitary eigenphase $\varphi$", ylabel=r"radius $|\lambda|$", title="Exact Cayley/tangent map")
    twin.set_ylabel(r"polar angle $\theta$")
    axes[1].set_ylim(0.0, 25.0)
    twin.set_ylim(0.0, np.pi)
    lines = axes[1].lines + twin.lines
    axes[1].legend(lines, [line.get_label() for line in lines], frameon=False, loc="upper center")
    axes[1].grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(figure_root / "relative_unitary_validation.png", dpi=220, bbox_inches="tight")
    plt.close(figure)

    payload = {
        "dimension": 5,
        "time": time,
        "strengths": strengths.tolist(),
        "maximum_exact_cayley_operator_error": max(exact_bridge_errors),
        "leading_magnus_operator_error_loglog_slope": slope,
        "figure": str((figure_root / "relative_unitary_validation.png").relative_to(ROOT)),
        "table": str((data_root / "relative_unitary_validation.csv").relative_to(ROOT)),
    }
    (data_root / "relative_unitary_validation.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
