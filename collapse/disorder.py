"""
Disorder Sampling Strategies
=============================

Strategy pattern for generating disordered coupling constants in
Hamiltonian models.  Adding a new disorder distribution requires
only a new ``DisorderStrategy`` subclass — no modification of the
Hamiltonian generators themselves.
"""

from abc import ABC, abstractmethod

import numpy as np


# ---------------------------------------------------------------------------
# Abstract strategy
# ---------------------------------------------------------------------------
class DisorderStrategy(ABC):
    """
    Interface for sampling a disordered coupling value.

    Every concrete strategy perturbs a *base_value* using randomness
    controlled by a *strength* parameter.
    """

    @abstractmethod
    def sample(self, base_value: float, strength: float) -> float:
        """
        Return a perturbed copy of *base_value*.

        Parameters
        ----------
        base_value : float
            The clean (disorder-free) coupling constant.
        strength : float
            Width / scale of the disorder distribution.

        Returns
        -------
        float
            The disordered coupling value.
        """


# ---------------------------------------------------------------------------
# Concrete strategies
# ---------------------------------------------------------------------------
class UniformDisorder(DisorderStrategy):
    """Additive uniform disorder:  J' = J + U(-strength, +strength)."""

    def sample(self, base_value: float, strength: float) -> float:
        return base_value + np.random.uniform(-strength, strength)


class GaussianDisorder(DisorderStrategy):
    """Additive Gaussian disorder:  J' = J + N(0, strength)."""

    def sample(self, base_value: float, strength: float) -> float:
        return base_value + np.random.normal(0, strength)


class LorentzianDisorder(DisorderStrategy):
    """Additive Lorentzian (Cauchy) disorder:  J' = J + strength * Cauchy."""

    def sample(self, base_value: float, strength: float) -> float:
        return base_value + strength * np.random.standard_cauchy()


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
_REGISTRY: dict[str, type[DisorderStrategy]] = {
    "uniform": UniformDisorder,
    "gaussian": GaussianDisorder,
    "lorentzian": LorentzianDisorder,
}


def create_disorder_strategy(name: str) -> DisorderStrategy:
    """
    Instantiate a disorder strategy by its short name.

    Parameters
    ----------
    name : str
        One of ``"uniform"``, ``"gaussian"``, ``"lorentzian"``.

    Returns
    -------
    DisorderStrategy

    Raises
    ------
    ValueError
        If *name* is not registered.
    """
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown disorder type '{name}'. " f"Available: {sorted(_REGISTRY)}"
        )
    return cls()
