"""Exact detector-translation blocks for the complete uniform XYZ ring.

No magnetization, spin parity, or reflection reduction is imposed. Every
momentum is retained, so all 15 RingChainSpec coefficients remain independent.
Sector matrices use QuSpin's descending-state order and central bit 1 for
physical |0>. Production QZ always sees physical |0>, |1> slices in that order.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from quspin.basis import spin_basis_general
from quspin.operators import hamiltonian
from scipy.linalg import eigh

from core.born_phase_verifier import evaluate_angles, evaluate_spectrum
from core.relative_evolution_pencil import generalized_relative_evolution_spectrum
from core.ring_chain_family import RingChainSpec
from core.translation_sector_roots import cyclic_translation_multiplicities

METHOD_VERSION = "ring-translation-qz-v1"


@dataclass(frozen=True)
class RingTranslationBlock:
    """One complete momentum block, including both central-qubit slices."""

    detector_n: int
    momentum: int
    matrix: np.ndarray
    basis: Any
    top: np.ndarray
    bottom: np.ndarray


def ring_static_terms(spec: RingChainSpec) -> list:
    """Translate positive Pauli coefficients without changing normalization."""
    if spec.topology != "ring":
        raise ValueError("detector translation requires the periodic ring family")
    n = spec.detector_n
    static = []
    for axis, hq, hd, j1, j2, g in zip("xyz", spec.qubit_field, spec.detector_field,
                                      spec.nearest, spec.second, spec.edge_couplings):
        one = ([[hq, 0]] if hq else []) + ([[hd, i] for i in range(1,n+1)] if hd else [])
        if one:
            static.append([axis, one])
        two = []
        for distance, strength in ((1,j1),(2,j2)):
            if strength:
                two.extend([strength,i,1+(i-1+distance)%n] for i in range(1,n+1))
        if g:
            two.extend([g,0,i] for i in range(1,n+1))
        if two:
            static.append([axis*2,two])
    return static


def build_ring_translation_block(spec: RingChainSpec, momentum: int) -> RingTranslationBlock:
    """Construct only one sector; do not allocate a full 2^(N+1) matrix."""
    static = ring_static_terms(spec)
    n = spec.detector_n
    if not isinstance(momentum,int) or not 0 <= momentum < n:
        raise ValueError("momentum must be an integer in [0,N)")
    translation = np.r_[0,1+(np.arange(n)+1)%n]
    basis = spin_basis_general(n+1,pauli=1,kblock=(translation,momentum))
    matrix = hamiltonian(static,[],basis=basis,dtype=np.complex128,
                         check_symm=False,check_herm=False,check_pcon=False).toarray()
    states = np.asarray(basis.states,dtype=np.int64)
    top = np.flatnonzero((states >> n)&1)
    bottom = np.flatnonzero(((states >> n)&1)==0)
    expected = cyclic_translation_multiplicities(n)[momentum]
    if len(top)!=expected or len(bottom)!=expected:
        raise ArithmeticError("translation sector has incorrect central-slice dimensions")
    # Representatives and orbit phases must agree between the two slices.
    mask = (1<<n)-1
    if not np.array_equal(states[top]&mask,states[bottom]&mask):
        raise ArithmeticError("central slices use different detector representative order")
    return RingTranslationBlock(n,momentum,matrix,basis,top,bottom)


def diagonalize_ring_translation_block(block: RingTranslationBlock) -> tuple[np.ndarray,np.ndarray,dict]:
    """Diagonalize one block and record dimensionless backward checks."""
    h = block.matrix
    energies,vectors = eigh(h,driver="evr")
    scale = max(1.,float(np.linalg.norm(h)))
    diagnostics = dict(
        hermiticity=float(np.linalg.norm(h-h.conj().T)/scale),
        eigen_residual=float(np.linalg.norm(h@vectors-vectors*energies)/scale),
        orthogonality=float(np.linalg.norm(vectors.conj().T@vectors-np.eye(len(h)))/np.sqrt(len(h))),
    )
    return energies,vectors,diagnostics


def evaluate_ring_translation_time(
    block: RingTranslationBlock, energies: np.ndarray, vectors: np.ndarray, time: float,
) -> tuple[dict,dict[str,np.ndarray]]:
    """Use the same homogeneous QZ and frozen v1 diagnostics in one block."""
    if not np.isfinite(time):
        raise ValueError("time must be finite")
    evolved = (vectors*np.exp(-1j*time*energies))@vectors[block.top,:].conj().T
    a,c = evolved[block.top,:],evolved[block.bottom,:]
    roots = generalized_relative_evolution_spectrum(a,c)
    dimension = len(block.top)
    diagnostic = evaluate_spectrum(roots,expected_count=dimension)
    diagnostic["column_isometry"] = float(np.linalg.norm(a.conj().T@a+c.conj().T@c-np.eye(dimension))/np.sqrt(dimension))
    diagnostic["momentum"] = block.momentum
    arrays = dict(alpha=roots.alpha,beta=roots.beta,theta=roots.theta,
                  right_residuals=roots.homogeneous_residuals,left_residuals=roots.left_homogeneous_residuals)
    return diagnostic,arrays


def combine_ring_translation_diagnostics(
    detector_n: int, sectors: list[tuple[dict,dict[str,np.ndarray]]],
) -> dict:
    """Pool roots with algebraic multiplicity, never average sector ratios.

    This exact direct-sum adapter does not change frozen v1 angle diagnostics
    or acceptance thresholds. Full per-sector QZ diagnostics remain attached.
    Missing or duplicated sectors are rejected, not renormalized away.
    """
    dimensions = cyclic_translation_multiplicities(detector_n)
    if len(sectors)!=detector_n or sorted(d["momentum"] for d,_ in sectors)!=list(range(detector_n)):
        raise ValueError("exactly one result for every momentum is required")
    ordered = sorted(sectors,key=lambda s:s[0]["momentum"])
    for momentum,(diagnostic,arrays) in enumerate(ordered):
        if diagnostic["root_count"]!=dimensions[momentum] or len(arrays["theta"])!=dimensions[momentum]:
            raise ValueError("sector root multiplicity mismatch")
    valid = all(d["qz_validity"] is True for d,_ in ordered)
    determined = all(d["angle_validity"] for d,_ in ordered)
    result = (evaluate_angles(np.concatenate([a["theta"] for _,a in ordered]),expected_count=2**detector_n)
              if determined else dict(angle_validity=False,structural_gate=False,profile=None))
    result.update(method_version=METHOD_VERSION,sector_dimensions=list(dimensions),
                  qz_validity=valid,qz_scope="Complete direct sum of production homogeneous QZ sectors",
                  numerical_and_structural_gate=bool(valid and result["structural_gate"]),
                  sectors=[d for d,_ in ordered])
    for key in ("qz_zero_fraction","qz_infinite_fraction","qz_indeterminate_fraction"):
        result[key] = float(sum(d[key]*d["root_count"] for d,_ in ordered)/2**detector_n)
    for key in ("qz_max_right_residual","qz_max_left_residual","column_isometry"):
        values = [d[key] for d,_ in ordered]
        result[key] = max(values) if all(v is not None for v in values) else None
    return result
