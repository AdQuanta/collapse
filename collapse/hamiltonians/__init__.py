"""
Hamiltonians Subpackage
========================

Re-exports all Hamiltonian generators for convenient access::

    from collapse.hamiltonians import CentralSpinHamiltonianNumpy
"""

from collapse.hamiltonians.base import HamiltonianGenerator
from collapse.detector_graphs import DetectorGraphSpec
from collapse.hamiltonians.numpy_hamiltonians import (
    CentralSpinHamiltonianNumpy,
    DimerizedPixelHamiltonianNumpy,
    MixedFieldIsingHamiltonianNumpy,
    SinglePixelHamiltonianNumpy,
    TwoPixelHamiltonianNumpy,
)

# QuSpin imports are deferred: they fail if QuSpin is not installed.
try:
    from collapse.hamiltonians.quspin_hamiltonians import (
        CentralSpinHamiltonianQuSpin,
        DimerizedPixelHamiltonianQuSpin,
        MixedFieldIsingHamiltonianQuSpin,
        SinglePixelHamiltonianQuSpin,
        TwoPixelHamiltonianQuSpin,
    )

    _QUSPIN_AVAILABLE = True
except ImportError:
    _QUSPIN_AVAILABLE = False

__all__ = [
    "HamiltonianGenerator",
    "DetectorGraphSpec",
    # NumPy backends (always available)
    "CentralSpinHamiltonianNumpy",
    "DimerizedPixelHamiltonianNumpy",
    "MixedFieldIsingHamiltonianNumpy",
    "SinglePixelHamiltonianNumpy",
    "TwoPixelHamiltonianNumpy",
]

if _QUSPIN_AVAILABLE:
    __all__ += [
        "CentralSpinHamiltonianQuSpin",
        "DimerizedPixelHamiltonianQuSpin",
        "MixedFieldIsingHamiltonianQuSpin",
        "SinglePixelHamiltonianQuSpin",
        "TwoPixelHamiltonianQuSpin",
    ]
