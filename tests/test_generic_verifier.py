"""Tests for the generic numerical verifier using QuSpin Hamiltonians."""
from __future__ import annotations

import numpy as np
import pytest
import sympy as sp

from verifier.analytic_p_theta.generic_verifier import (
    GenericNumericalVerifier,
    evaluate_symbolic_expression,
    build_quspin_hamiltonian,
    check_physical_assumptions,
)


def test_evaluate_symbolic_expression_string() -> None:
    context = {"t": 1.5, "g": 0.2, "N": 4}
    res = evaluate_symbolic_expression("2 * arctan(abs(sin(g * t)))", context)
    expected = 2.0 * np.arctan(np.abs(np.sin(0.2 * 1.5)))
    assert np.isclose(res, expected)


def test_evaluate_symbolic_expression_sympy() -> None:
    t, g = sp.symbols("t g", real=True)
    expr = 2 * sp.atan(sp.Abs(sp.sin(g * t)))
    context = {"t": 1.5, "g": 0.2, "N": 4}
    res = evaluate_symbolic_expression(expr, context)
    expected = 2.0 * np.arctan(np.abs(np.sin(0.2 * 1.5)))
    assert np.isclose(res, expected)


def test_evaluate_symbolic_expression_callable() -> None:
    func = lambda t, g, **kw: 2.0 * np.arctan(np.abs(np.sin(g * t)))
    context = {"t": 1.5, "g": 0.2, "N": 4}
    res = evaluate_symbolic_expression(func, context)
    expected = 2.0 * np.arctan(np.abs(np.sin(0.2 * 1.5)))
    assert np.isclose(res, expected)


def test_generic_verifier_case0_longitudinal_ring() -> None:
    """Case 0 (longitudinal coupling gz only, gx=gy=0, h0x=h0y=0) has exact theta=0."""
    verifier = GenericNumericalVerifier(angle_tolerance=1.0e-10)
    spec = {
        "topology": "ring",
        "J": 1.0,
        "Jx": 0.0,
        "Jy": 0.0,
        "Jz": 0.05,
        "hx": 0.0,
        "hz": 0.2,
        "hx0": 0.0,
        "hz0": 0.1,
    }
    result = verifier.verify(
        candidate_expr="0",
        base_spec=spec,
        times=(0.5, 1.0, 2.0),
        n_values=(2, 3, 4),
        candidate_summary="Case 0 exact theta=0",
    )
    assert result.passed
    assert result.max_angle_error < 1.0e-12
    assert result.physical_assumptions_passed
    assert result.max_column_isometry_residual < 1.0e-12


def test_generic_verifier_case0_chain() -> None:
    """Case 0 on open chain geometry with exact theta=0."""
    verifier = GenericNumericalVerifier(angle_tolerance=1.0e-10)
    spec = {
        "topology": "chain",
        "J": 1.0,
        "Jx": 0.0,
        "Jy": 0.0,
        "Jz": 0.1,
        "hx": 0.0,
        "hz": 0.3,
        "hx0": 0.0,
        "hz0": 0.1,
    }
    result = verifier.verify(
        candidate_expr="0",
        base_spec=spec,
        times=(0.5, 1.5),
        n_values=(2, 3),
        candidate_summary="Chain Case 0 theta=0",
    )
    assert result.passed
    assert result.max_angle_error < 1.0e-12


def test_generic_verifier_detects_wrong_candidate() -> None:
    """Verifier must reject an incorrect candidate formula."""
    verifier = GenericNumericalVerifier(angle_tolerance=1.0e-4)
    # With transverse coupling Jx!=0, angles are non-zero
    spec = {
        "topology": "ring",
        "J": 1.0,
        "Jx": 0.3,
        "Jy": 0.0,
        "Jz": 0.0,
        "hx": 0.0,
        "hz": 0.2,
        "hx0": 0.0,
        "hz0": 0.1,
    }
    # Propose theta=0 which is wrong for Jx!=0
    result = verifier.verify(
        candidate_expr="0",
        base_spec=spec,
        times=(1.0,),
        n_values=(3,),
        candidate_summary="False candidate theta=0",
    )
    assert not result.passed
    assert len(result.failures) > 0
    assert result.max_angle_error > 1.0e-3
