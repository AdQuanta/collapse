"""Plots of the analytically derived phase-mixed resonance cap."""
from pathlib import Path

import numpy as np

from core.born_structure_plotting import plt, save_figure


def plot_resonant_caps(
    output: Path, epsilons: np.ndarray, detunings: list[float],
    caps: np.ndarray, coefficients: np.ndarray, *, g: float, h: float, c: float,
) -> None:
    """Display numerical caps and exact positive resonance coefficients."""
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for b, values, coefficient in zip(detunings, caps, coefficients):
        line, = ax.semilogx(epsilons, values / epsilons, "o-", label=f"b={b:g}")
        ax.axhline(coefficient, color=line.get_color(), ls="--", lw=1)
    ax.axhline(0., color="black", ls=":", label="required Born limit")
    ax.set(xlabel=r"south-cap size $\epsilon$ in $x=\sin^2(\theta/2)$",
           ylabel=r"$\Pr(x>1-\epsilon)/\epsilon$",
           title=f"Native collective XX/ZX: resonance obstruction\n(g={g:g}, h={h:g}, c={c:g}; dashed: exact limits)")
    ax.legend()
    ax.grid(alpha=.2)
    fig.tight_layout()
    save_figure(fig, output / "resonant_south_caps")
