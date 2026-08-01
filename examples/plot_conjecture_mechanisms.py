"""Draw the mechanism-level diagrams used in the conjecture explainer.

The plotting layer is intentionally separate from the report source so the
scientific picture can be regenerated and tested independently.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _resonant_graph(ax: plt.Axes) -> None:
    left = np.array([-1.25, -0.45, 0.35, 1.15])
    right = left + np.array([0.05, -0.03, 0.02, 0.55])
    for y in left:
        ax.plot([-1.0, -0.35], [y, y], color="#2563eb", lw=2)
    for y in right:
        ax.plot([0.35, 1.0], [y, y], color="#dc2626", lw=2)
    for i in range(3):
        ax.annotate(
            "",
            xy=(0.35, right[i]),
            xytext=(-0.35, left[i]),
            arrowprops={"arrowstyle": "-|>", "color": "#555555", "lw": 1.4},
        )
    ax.annotate(
        "off-resonant",
        xy=(0.35, right[3]),
        xytext=(-0.35, left[0]),
        arrowprops={"arrowstyle": "-|>", "color": "#aaaaaa", "lw": 1.0, "ls": "--"},
        color="#777777",
        fontsize=8,
    )
    ax.text(-0.68, 1.48, r"$|\uparrow\rangle\otimes|a\rangle$", ha="center", fontsize=9)
    ax.text(0.68, 1.48, r"$|\downarrow\rangle\otimes|b\rangle$", ha="center", fontsize=9)
    ax.text(0, -1.58, r"keep edges with $|E_b-E_a\pm2h_{z0}|\lesssim\delta_t$", ha="center", fontsize=8)
    ax.set_title("A. Accessible resonant graph", loc="left", fontweight="bold")
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.8, 1.8)
    ax.axis("off")


def _tangent_pole(ax: plt.Axes) -> None:
    eps = np.logspace(-3, -0.05, 300)
    radius = 1.0 / np.tan(eps / 2.0)
    ax.loglog(eps, radius, color="#7c3aed", lw=2.2, label=r"$r=|\tan(\phi/2)|$")
    ax.loglog(eps, 2.0 / eps, color="#444444", lw=1.2, ls="--", label=r"$2/|\pi-\phi|$")
    ax.set_xlabel(r"distance from pole $|\pi-\phi|$")
    ax.set_ylabel(r"radius $r$")
    ax.invert_xaxis()
    ax.grid(alpha=0.22)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("B. Tangent pole makes large radii", loc="left", fontweight="bold")


def _reciprocity(ax: plt.Axes) -> None:
    r = np.logspace(-2, 2, 600)
    q_born = 4.0 / (np.pi * (1.0 + r**2) ** 2)
    q_cauchy = 2.0 / (np.pi * (1.0 + r**2))
    ax.loglog(r, q_born, color="#059669", lw=2.2, label=r"Born $q_B(r)$")
    ax.loglog(r, q_cauchy, color="#d97706", lw=1.8, ls="--", label="half-Cauchy")
    ax.axvline(1.0, color="#777777", lw=0.8)
    ax.annotate("pair $r$ with $1/r$", xy=(8, 8e-4), xytext=(0.13, 8e-4),
                arrowprops={"arrowstyle": "<->", "color": "#333333"}, ha="center", fontsize=8)
    ax.text(1.05, 1.4e-7, r"Born: $q(1/r)=r^4q(r)$", fontsize=8, color="#047857")
    ax.text(1.05, 3e-6, r"pole weight: $q(r)\sim r^{-2}$", fontsize=8, color="#b45309")
    ax.set_xlabel(r"radius $r=\tan(\theta/2)$")
    ax.set_ylabel(r"density $q(r)$")
    ax.set_ylim(1e-9, 2)
    ax.grid(alpha=0.22)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("C. Born reciprocity is stronger than a heavy tail", loc="left", fontweight="bold")


def create_figure(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.0), constrained_layout=True)
    _resonant_graph(axes[0])
    _tangent_pole(axes[1])
    _reciprocity(axes[2])
    fig.savefig(destination, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("figures/conjecture_explainer_2026-07-16/mechanisms.png"),
    )
    args = parser.parse_args()
    create_figure(args.output)


if __name__ == "__main__":
    main()
