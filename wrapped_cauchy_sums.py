"""
Wrapped Cauchy Sum Analysis — Entry Point
==========================================

Randomly samples N i.i.d. Cauchy-distributed RVs, computes all 2^N
signed sums, wraps them mod 2π, and compares against the theoretical
wrapped Cauchy PDF.

Run directly::

    python wrapped_cauchy_sums.py

All computation lives in :mod:`collapse.wrapped_cauchy`; plotting in
:class:`collapse.visualization.WrappedCauchyPlotter`.
"""

from collapse.visualization import WrappedCauchyPlotter


def main() -> None:
    """Run the default demonstration."""
    # ----- Configuration -----
    N = 15  # Number of Cauchy RVs (2^N sums per realization)
    gamma = 0.01  # Scale parameter
    M = 10000  # Number of independent realizations
    seed = 125  # Random seed
    bins = 80  # Histogram bins
    # --------------------------

    print(f"Plotting single realization (N={N}, M=1)...")
    WrappedCauchyPlotter.plot_comparison(N, gamma, M=1, seed=seed, bins=bins)

    print(f"Plotting multiple realizations (N={N}, M={M})...")
    WrappedCauchyPlotter.plot_comparison(
        N,
        gamma,
        M=M,
        seed=seed + 1 if seed else None,
        bins=bins,
    )

    print(f"Plotting ratio to cyclic shift (N={N}, M={M})...")
    bins_even = bins if bins % 2 == 0 else bins + 1
    WrappedCauchyPlotter.plot_ratio(
        N,
        gamma,
        M=M,
        seed=seed + 2 if seed else None,
        bins=bins_even,
    )


if __name__ == "__main__":
    main()
