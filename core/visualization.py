"""
Visualization Helpers
======================

Plotting classes for disentanglement analysis and wrapped-Cauchy
comparisons.  Visualization is separated from computation so that the
core algorithms can be tested and reused without a display backend.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from core.analysis import DisentanglementAnalyzer

# Set default plot parameters once on import
plt.rcParams["font.size"] = 12
plt.rcParams["font.family"] = "Arial"


# ===================================================================
# Disentanglement visualisation
# ===================================================================
class DisentanglementVisualizer:
    """
    Visualise the results produced by a
    :class:`~core.analysis.DisentanglementAnalyzer`.

    Parameters
    ----------
    analyzer : DisentanglementAnalyzer
        A fully-populated analyzer (qubit states must already be computed).
    """

    def __init__(self, analyzer: DisentanglementAnalyzer):
        self.analyzer = analyzer

    # -----------------------------------------------------------------
    def _z_components(self) -> tuple[np.ndarray, np.ndarray]:
        """Return z-components of the Bloch vectors for both outcomes."""
        z0 = (
            np.abs(self.analyzer.phi0[:, 0]) ** 2
            - np.abs(self.analyzer.phi0[:, 1]) ** 2
        )
        z1 = (
            np.abs(self.analyzer.phi1[:, 0]) ** 2
            - np.abs(self.analyzer.phi1[:, 1]) ** 2
        )
        return z0, z1

    # -----------------------------------------------------------------
    def plot_bloch_sphere(self) -> None:
        """Plot initial qubit states on the Bloch sphere."""
        D = self.analyzer.N
        half = D // 2

        fig = plt.figure(figsize=(8, 6), dpi=200)
        ax = fig.add_subplot(111, projection="3d")

        # Wire-frame sphere
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        xs = np.outer(np.cos(u), np.sin(v))
        ys = np.outer(np.sin(u), np.sin(v))
        zs = np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(xs, ys, zs, color="gray", alpha=0.15)

        for i in range(half):
            for phi, color in [
                (self.analyzer.phi0[i, :], "blue"),
                (self.analyzer.phi1[i, :], "red"),
            ]:
                bx = 2 * np.real(np.conj(phi[0]) * phi[1])
                by = 2 * np.imag(np.conj(phi[0]) * phi[1])
                bz = np.abs(phi[0]) ** 2 - np.abs(phi[1]) ** 2
                ax.scatter(bx, by, bz, color=color, alpha=0.5)

        ax.set_title("Initial Qubit States on Bloch Sphere")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.show()

    # -----------------------------------------------------------------
    def plot_z_histograms(self, bins: int = 30, use_theta: bool = False) -> None:
        """
        Plot histograms of the z-component (or θ = arccos z) of initial
        qubit states.

        Parameters
        ----------
        bins : int
            Number of histogram bins.
        use_theta : bool
            If *True*, plot in θ = arccos(z) ∈ [0, π] instead of z.
            The Born-rule curve is Jacobian-adjusted accordingly.
        """
        z0, z1 = self._z_components()

        if use_theta:
            data0, data1 = np.arccos(z0), np.arccos(z1)
            x = np.linspace(0, np.pi, 1000)
            born = np.sin(x) * (1 + np.cos(x)) / 2
            born_comp = np.sin(x) * (1 - np.cos(x)) / 2
            xlabel, title_var = r"$\theta$", r"$\theta = \arccos z$"
        else:
            data0, data1 = z0, z1
            x = np.linspace(-1, 1, 1000)
            born = (1 + x) / 2
            born_comp = (1 - x) / 2
            xlabel, title_var = "z", "z"

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.hist(data0, bins=bins, density=True, alpha=0.7, color="blue")
        ax.hist(data1, bins=bins, density=True, alpha=0.7, color="red")
        ax.plot(x, born, "k--", lw=1)
        ax.plot(x, born_comp, "k--", lw=1)
        ax.set_title(f"Histogram of {title_var} components of initial qubit states")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Density")
        plt.show()

    # -----------------------------------------------------------------
    def plot_z_histograms_ratio(
        self,
        bins: int = 30,
        use_theta: bool = False,
    ) -> None:
        """
        Plot the fraction  h0/(h0+h1)  and  h1/(h0+h1)  per bin.

        Parameters
        ----------
        bins : int
            Number of histogram bins.
        use_theta : bool
            If *True*, bin in θ = arccos(z) space.
        """
        z0, z1 = self._z_components()

        if use_theta:
            data0, data1 = np.arccos(z0), np.arccos(z1)
            bin_edges = np.linspace(0, np.pi, bins + 1)
            x = np.linspace(0, np.pi, 1000)
            # Ratios are dimensionless — Born rule is the same function
            # of the *variable*, just evaluated at θ instead of z.
            # h0/(h0+h1) should approach cos²(θ/2) = (1+cosθ)/2.
            born = (1 + np.cos(x)) / 2
            xlabel = r"$\theta$"
            title = r"Ratio of $\theta$-component histograms"
        else:
            data0, data1 = z0, z1
            bin_edges = np.linspace(-1, 1, bins + 1)
            x = np.linspace(-1, 1, 1000)
            born = (1 + x) / 2
            xlabel = "z"
            title = "Ratio of z-component histograms"

        h0, _ = np.histogram(data0, bins=bin_edges)
        h1, _ = np.histogram(data1, bins=bin_edges)
        h_sum = h0 + h1

        mask = (h0 > 0) & (h1 > 0)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        bin_width = bin_edges[1] - bin_edges[0]

        ratio0 = np.where(mask, h0 / h_sum, 0)
        ratio1 = np.where(mask, h1 / h_sum, 0)

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.plot(
            bin_centers[mask],
            ratio0[mask],
            "o-",
            color="blue",
            ms=4,
            lw=1.5,
            label=r"$h_0/(h_0{+}h_1)$",
        )
        ax.plot(
            bin_centers[mask],
            ratio1[mask],
            "o-",
            color="red",
            ms=4,
            lw=1.5,
            label=r"$h_1/(h_0{+}h_1)$",
        )
        ax.plot(x, born, "k--", lw=1)
        ax.plot(x, 1 - born, "k--", lw=1)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Fraction")
        ax.legend()
        plt.show()

    # -----------------------------------------------------------------
    def plot_z_combined(
        self,
        bins: int = 30,
        use_theta: bool = False,
    ) -> None:
        """
        Overlay density histograms (background) with bin-wise ratios
        (foreground) on a twin-axis figure.

        Parameters
        ----------
        bins : int
            Number of histogram bins.
        use_theta : bool
            If *True*, plot in θ = arccos(z) space.
        """
        z0, z1 = self._z_components()

        if use_theta:
            data0, data1 = np.arccos(z0), np.arccos(z1)
            bin_edges = np.linspace(0, np.pi, bins + 1)
            x_theory = np.linspace(0, np.pi, 1000)
            born = (1 + np.cos(x_theory)) / 2
            density_label_0 = r"$\rho_0(\theta)$ density"
            density_label_1 = r"$\rho_1(\theta)$ density"
            xlabel = r"$\theta$"
            title = r"$\theta$-component histograms and bin-wise ratios"
        else:
            data0, data1 = z0, z1
            bin_edges = np.linspace(-1, 1, bins + 1)
            x_theory = np.linspace(-1, 1, 1000)
            born = (1 + x_theory) / 2
            density_label_0 = r"$\rho_0(z)$ density"
            density_label_1 = r"$\rho_1(z)$ density"
            xlabel = "z"
            title = "z-component histograms and bin-wise ratios"

        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        bin_width = bin_edges[1] - bin_edges[0]

        # Density-normalised histograms
        h0_density, _ = np.histogram(data0, bins=bin_edges, density=True)
        h1_density, _ = np.histogram(data1, bins=bin_edges, density=True)

        # Count-based ratios
        h0_counts, _ = np.histogram(data0, bins=bin_edges)
        h1_counts, _ = np.histogram(data1, bins=bin_edges)
        h_sum = h0_counts + h1_counts
        mask = (h0_counts > 0) & (h1_counts > 0)
        ratio0 = np.where(mask, h0_counts / h_sum, np.nan)
        ratio1 = np.where(mask, h1_counts / h_sum, np.nan)

        # ---- Figure -----------------------------------------------
        fig, ax_hist = plt.subplots(figsize=(7, 4.5), dpi=120)
        ax_ratio = ax_hist.twinx()

        # Background: density histograms
        ax_hist.bar(
            bin_centers,
            h0_density,
            width=bin_width,
            alpha=0.25,
            color="blue",
            label=density_label_0,
        )
        ax_hist.bar(
            bin_centers,
            h1_density,
            width=bin_width,
            alpha=0.25,
            color="red",
            label=density_label_1,
        )

        # Foreground: ratio curves
        ax_ratio.plot(
            bin_centers[mask],
            ratio0[mask],
            "o-",
            color="blue",
            ms=4,
            lw=1.5,
            label=r"$h_0/(h_0{+}h_1)$",
        )
        ax_ratio.plot(
            bin_centers[mask],
            ratio1[mask],
            "o-",
            color="red",
            ms=4,
            lw=1.5,
            label=r"$h_1/(h_0{+}h_1)$",
        )

        # Theory curves (on ratio axis)
        ax_ratio.plot(x_theory, born, "k--", lw=1.2, label="Born rule")
        ax_ratio.plot(x_theory, 1 - born, "k--", lw=1.2)

        # Labels
        ax_hist.set_xlabel(xlabel, fontsize=12)
        ax_hist.set_ylabel("Density", fontsize=11, color="gray")
        ax_hist.tick_params(axis="y", labelcolor="gray")
        ax_ratio.set_ylabel("Fraction", fontsize=11)
        ax_ratio.set_ylim(0, 1.05)
        ax_hist.set_xlim(bin_edges[0], bin_edges[-1])

        # Combined legend
        h1_handles, h1_labels = ax_hist.get_legend_handles_labels()
        h2_handles, h2_labels = ax_ratio.get_legend_handles_labels()
        ax_ratio.legend(
            h1_handles + h2_handles,
            h1_labels + h2_labels,
            loc="upper left",
            fontsize=8,
            framealpha=0.9,
        )

        ax_hist.set_title("z-component histograms and bin-wise ratios", fontsize=13)
        plt.tight_layout()
        plt.show()


# ===================================================================
# Wrapped Cauchy visualisation
# ===================================================================
class WrappedCauchyPlotter:
    """
    Plotting helpers for the wrapped-Cauchy-sum analysis.

    All heavy computation is delegated to the functions in
    :mod:`core.wrapped_cauchy`; this class handles only rendering.
    """

    @staticmethod
    def plot_comparison(
        N: int,
        gamma: float,
        M: int = 1,
        seed: int | None = None,
        bins: int = 60,
    ) -> None:
        """
        Overlay statistical histogram of wrapped signed sums with the
        theoretical wrapped-Cauchy PDF.
        """
        from core.wrapped_cauchy import compute_wrapped_sums, wrapped_cauchy_pdf

        wrapped_sums, _ = compute_wrapped_sums(N, gamma, M=M, seed=seed)
        flat = wrapped_sums.flatten()

        gamma_eff = N * gamma
        theta = np.linspace(-np.pi, np.pi, 1000)
        pdf_vals = wrapped_cauchy_pdf(theta, gamma_eff)

        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)

        if M == 1:
            hist_label = rf"Histogram ($2^{{{N}}}={2**N}$ sums)"
            title = rf"Wrapped sums of $N={N}$ i.i.d. Cauchy RVs ($\gamma={gamma}$)"
        else:
            hist_label = rf"Histogram ($M={M}$ real., $M \times 2^{{{N}}}$ sums)"
            title = rf"Wrapped sums of $N={N}$ i.i.d. Cauchy RVs ($\gamma={gamma}$, $M={M}$)"

        ax.hist(
            flat,
            bins=bins,
            density=True,
            alpha=0.7,
            color="steelblue",
            edgecolor="white",
            label=hist_label,
        )
        ax.plot(
            theta,
            pdf_vals,
            "r-",
            lw=2,
            label=rf"Wrapped Cauchy ($\gamma_{{\mathrm{{eff}}}} = N\gamma = {gamma_eff:.2f}$)",
        )

        ax.set_xlabel(r"$\theta\;\;(\mathrm{mod}\;2\pi)$", fontsize=12)
        ax.set_ylabel("Density", fontsize=12)
        ax.set_title(title, fontsize=13)
        ax.legend(fontsize=10)
        ax.set_xlim(-np.pi, np.pi)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_ratio(
        N: int,
        gamma: float,
        M: int = 1,
        seed: int | None = None,
        bins: int = 60,
    ) -> None:
        """
        Plot the density ratio  f(θ−π)/f(θ)  against the theoretical
        tan²(θ/2).
        """
        from core.wrapped_cauchy import compute_wrapped_sums

        wrapped_sums, _ = compute_wrapped_sums(N, gamma, M=M, seed=seed)
        flat = wrapped_sums.flatten()

        hist, bin_edges = np.histogram(
            flat, bins=bins, range=(-np.pi, np.pi), density=True
        )
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

        shifted_hist = np.roll(hist, bins // 2)

        valid = hist > 0
        ratio_hist = np.full_like(hist, np.nan)
        ratio_hist[valid] = shifted_hist[valid] / hist[valid]

        theta = np.linspace(-np.pi, np.pi, 1000)
        pdf_ratio = np.tan(theta / 2.0) ** 2

        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)

        if M == 1:
            hist_label = rf"Histogram Ratio ($2^{{{N}}}={2**N}$ sums)"
            title = (
                rf"Density Ratio $f(\theta-\pi)/f(\theta)$ ($N={N}$, $\gamma={gamma}$)"
            )
        else:
            hist_label = rf"Histogram Ratio ($M={M}$ real.)"
            title = rf"Density Ratio $f(\theta-\pi)/f(\theta)$ ($N={N}$, $\gamma={gamma}$, $M={M}$)"

        ax.plot(
            bin_centers, ratio_hist, "o", color="steelblue", alpha=0.8, label=hist_label
        )
        ax.plot(theta, pdf_ratio, "r-", lw=2, label=rf"Theoretical $\tan^2(\theta/2)$")

        ax.set_ylim(1e-3, 5)
        ax.set_xlabel(r"$\theta\;\;(\mathrm{mod}\;2\pi)$", fontsize=12)
        ax.set_ylabel(r"$f(\theta - \pi) / f(\theta)$", fontsize=12)
        ax.set_title(title, fontsize=13)
        ax.legend(fontsize=10)
        ax.set_xlim(-np.pi, np.pi)
        plt.tight_layout()
        plt.show()


# ===================================================================
# Level spacing visualisation
# ===================================================================
class LevelSpacingPlotter:
    """
    Plotting helpers for level-spacing diagnostics.

    All heavy computation is delegated to functions in
    :mod:`core.level_spacing`; this class handles only rendering.
    """

    #: Human-readable labels for each ensemble / Dyson index
    _ENSEMBLE_LABELS = {
        "poisson": "Poisson",
        "goe": "GOE (β=1)",
        "gue": "GUE (β=2)",
        "gse": "GSE (β=4)",
    }
    _ENSEMBLE_BETA = {"goe": 1, "gue": 2, "gse": 4}
    _ENSEMBLE_COLORS = {
        "poisson": "green",
        "goe": "red",
        "gue": "orange",
        "gse": "purple",
    }
    @classmethod
    def _spacing_curve(cls, ensemble: str, s: np.ndarray) -> np.ndarray | None:
        """Return the reference spacing curve for a requested ensemble."""
        from core.level_spacing import (
            poisson_spacing_distribution,
            wigner_spacing_distribution,
        )

        ensemble = ensemble.lower()
        if ensemble == "poisson":
            return poisson_spacing_distribution(s)
        if ensemble in cls._ENSEMBLE_BETA:
            return wigner_spacing_distribution(s, cls._ENSEMBLE_BETA[ensemble])
        return None

    @staticmethod
    def plot_spacing_distribution(
        eigenvalues: np.ndarray,
        bins: int = 50,
        ensembles: tuple[str, ...] = ("poisson", "goe"),
        tol: float = 1e-12,
        unfolding_degree: int = 3,
        trim_fraction: float = 0.1,
        ax=None,
    ) -> None:
        """
        Histogram of unfolded level spacings overlaid with reference curves.

        Parameters
        ----------
        eigenvalues : np.ndarray
            Energy eigenvalues.
        bins : int
            Number of histogram bins.
        ensembles : tuple of str
            Which reference curves to overlay. Choose from
            ``"poisson"``, ``"goe"``, ``"gue"``, ``"gse"``.
        tol : float
            Degeneracy tolerance.
        unfolding_degree : int
            Polynomial degree used for the smooth staircase unfolding.
        trim_fraction : float
            Fraction of levels discarded from each spectral edge after
            unfolding to reduce boundary artefacts.
        ax : matplotlib.axes.Axes or None
            If provided, plot onto this axes; otherwise create a new
            figure.
        """
        from core.level_spacing import compute_unfolded_spacings

        spacings = compute_unfolded_spacings(
            eigenvalues,
            tol=tol,
            degree=unfolding_degree,
            trim_fraction=trim_fraction,
        )
        if len(spacings) == 0:
            return

        own_fig = ax is None
        if own_fig:
            fig, ax = plt.subplots(figsize=(7, 4.5), dpi=120)

        ax.hist(
            spacings,
            bins=bins,
            density=True,
            alpha=0.6,
            color="steelblue",
            edgecolor="white",
            label="Data",
        )

        x_max = max(4.0, float(np.percentile(spacings, 99.5)))
        s_theory = np.linspace(0.0, x_max, 500)

        for ens in ensembles:
            ens_lower = ens.lower()
            color = LevelSpacingPlotter._ENSEMBLE_COLORS.get(ens_lower, "gray")
            label = LevelSpacingPlotter._ENSEMBLE_LABELS.get(ens_lower, ens)

            curve = LevelSpacingPlotter._spacing_curve(ens_lower, s_theory)
            if curve is None:
                continue

            ax.plot(s_theory, curve, "-", color=color, lw=2, label=label)

        ax.set_xlabel(r"$s$", fontsize=12)
        ax.set_ylabel("Density", fontsize=12)
        ax.set_title("Unfolded Level Spacing Distribution", fontsize=13)
        ax.set_xlim(0, x_max)
        ax.legend(fontsize=9, framealpha=0.9)

        if own_fig:
            plt.tight_layout()
            plt.show()
