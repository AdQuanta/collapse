"""
Level Spacing Distribution Demo
===============================

Demonstrate level-spacing diagnostics on the mixed-field Ising model.
With the parameters chosen here (J=1, hx=1.3, hz=0.3, N=10) the model
is in a chaotic regime and should yield <r> ~= 0.53 (GOE).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from collapse import (
    MEAN_R_GOE,
    MEAN_R_GUE,
    MEAN_R_POISSON,
    MixedFieldIsingHamiltonianQuSpin,
    mean_level_spacing_ratio,
)
from collapse.visualization import LevelSpacingPlotter

# ------------------------------------------------------------------
# 1.  Build and diagonalise the Hamiltonian
# ------------------------------------------------------------------
N = 10
ham = MixedFieldIsingHamiltonianQuSpin(
    N=N, J=1.0, hx=1.3, hz=0.3, disorder="uniform", disorder_strength_hz=1.0
)
H = ham.generate()
eigenvalues = np.linalg.eigvalsh(H)

print(f"Mixed-field Ising: N = {N}, D = {2**N}")
print(f"  Eigenvalue range: [{eigenvalues[0]:.3f}, {eigenvalues[-1]:.3f}]")

# ------------------------------------------------------------------
# 2.  Compute and print the mean level spacing ratio
# ------------------------------------------------------------------
mean_r = mean_level_spacing_ratio(eigenvalues)
print(f"\n  <r> = {mean_r:.4f}")
print(
    f"  Reference: Poisson = {MEAN_R_POISSON:.4f}, "
    f"GOE = {MEAN_R_GOE:.4f}, GUE = {MEAN_R_GUE:.4f}"
)

reference_means = {
    "Poisson (integrable)": MEAN_R_POISSON,
    "GOE (chaotic)": MEAN_R_GOE,
    "GUE (chaotic)": MEAN_R_GUE,
}
closest_ensemble = min(
    reference_means,
    key=lambda label: abs(mean_r - reference_means[label]),
)
print(f"  -> Spectrum is closest to {closest_ensemble}")

# ------------------------------------------------------------------
# 3.  Plot the spacing distribution with reference curves
# ------------------------------------------------------------------
LevelSpacingPlotter.plot_spacing_distribution(
    eigenvalues,
    bins=40,
    ensembles=("poisson", "goe", "gue"),
)
