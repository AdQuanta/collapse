"""Explicit positive-sign XYZ ring/chain families for weak-coupling research.

The central qubit is first. Ring x/y edges scale as 1/sqrt(N), z edges as
1/N. Chain coupling is to detector site 1, without collective scaling.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from core.pauli import build_pauli_operators, build_pauli_y

Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class RingChainSpec:
    """Uniform fields/bonds in energy units; Pauli eigenvalues +/-1."""

    detector_n: int
    topology: Literal["ring", "chain"]
    qubit_field: Vector3
    detector_field: Vector3
    nearest: Vector3
    second: Vector3
    coupling: Vector3

    def __post_init__(self) -> None:
        if not isinstance(self.detector_n, int) or self.detector_n < 1:
            raise ValueError("detector_n must be a positive integer")
        if self.topology not in ("ring", "chain"):
            raise ValueError("topology must be ring or chain")
        if self.topology == "ring" and self.detector_n < 5:
            raise ValueError("rings require N>=5 to avoid small-ring bond ambiguity")
        for name in ("qubit_field", "detector_field", "nearest", "second", "coupling"):
            values = tuple(getattr(self, name))
            if len(values) != 3 or not np.all(np.isfinite(values)):
                raise ValueError(f"{name} must contain three finite components")
            object.__setattr__(self, name, values)

    @property
    def edge_couplings(self) -> Vector3:
        """Actual coefficients of each central-detector Pauli product."""
        gx, gy, gz = self.coupling
        if self.topology == "chain":
            return gx, gy, gz
        return (
            gx / np.sqrt(self.detector_n),
            gy / np.sqrt(self.detector_n),
            gz / self.detector_n,
        )


def build_ring_chain_parts(spec: RingChainSpec) -> tuple[np.ndarray, np.ndarray]:
    """Return H0=HQ+HD and V=HQD, with every requested XYZ term explicit.

    Dense reference for reduced verification, not a production HPC solver.
    All fields and bonds have the user's positive sign convention.
    """
    n = spec.detector_n
    xs, zs = build_pauli_operators(n + 1)
    ys = [build_pauli_y(i, n + 1) for i in range(n + 1)]
    axes = (xs, ys, zs)
    h0 = np.zeros((2**(n + 1),) * 2, dtype=complex)
    interaction = np.zeros_like(h0)
    for axis, hq, hd in zip(axes, spec.qubit_field, spec.detector_field):
        h0 += hq * axis[0]
        for i in range(1, n + 1):
            h0 += hd * axis[i]
    for distance, strengths in [(1, spec.nearest), (2, spec.second)]:
        stop = n + 1 if spec.topology == "ring" else n + 1 - distance
        sites = range(1, stop)
        for i in sites:
            j = 1 + (i - 1 + distance) % n
            for axis, strength in zip(axes, strengths):
                if strength:
                    h0 += strength * (axis[i] @ axis[j])
    targets = range(1, n + 1) if spec.topology == "ring" else (1,)
    for axis, strength in zip(axes, spec.edge_couplings):
        if strength:
            for i in targets:
                interaction += strength * (axis[0] @ axis[i])
    return h0, interaction
