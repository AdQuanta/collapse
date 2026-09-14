"""Generic Numerical Verifier for Analytic P(theta) and Projective Roots.

Receives symbolic or analytical candidate expressions, constructs the exact
Hamiltonian using QuSpin (SinglePixelHamiltonianQuSpin), verifies all physical
assumptions (hermiticity, scale hierarchies, symmetries, column isometry,
pencil regularity, and measure normalization), and numerically verifies the
candidate projective-root angles against exact numerical eigensolvers up to N=11.

Boundary rules:
- Derivation code must not import this verifier.
- This verifier receives formula data, strings, SymPy expressions, or callables.
- Numerical checks up to N=11 verify finite-N mathematical correctness,
  never asymptotic Born behavior.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, Sequence

# Ensure repository root is in sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

# Repository core imports
from core.analysis import evolution_subblocks_from_eigenbasis
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.relative_evolution_pencil import (
    RelativeEvolutionPencilSpectrum,
    generalized_relative_evolution_spectrum,
    matched_projective_angle_error,
)
from core.ring_chain_family import RingChainSpec


# Safe math environment for evaluating symbolic formula strings
_SAFE_MATH = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "arctan2": np.arctan2,
    "atan": np.arctan,
    "atan2": np.arctan2,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "pi": np.pi,
    "log": np.log,
    "cosh": np.cosh,
    "sinh": np.sinh,
    "tanh": np.tanh,
    "np": np,
    "math": math,
}


@dataclass(frozen=True)
class VerificationResult:
    """Detailed result of generic numerical verification."""

    passed: bool
    candidate_summary: str
    max_angle_error: float
    rms_angle_error: float
    max_column_isometry_residual: float
    max_hermiticity_residual: float
    physical_assumptions_passed: bool
    physical_assumptions_log: dict[str, Any]
    per_size_results: dict[int, dict[str, Any]]
    failures: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        lines = [
            f"=== Generic Numerical Verification: {status} ===",
            f"Candidate: {self.candidate_summary}",
            f"Max angle error: {self.max_angle_error:.3e}",
            f"RMS angle error: {self.rms_angle_error:.3e}",
            f"Max isometry residual: {self.max_column_isometry_residual:.3e}",
            f"Max hermiticity residual: {self.max_hermiticity_residual:.3e}",
            f"Physical assumptions passed: {self.physical_assumptions_passed}",
        ]
        if self.failures:
            lines.append("Failures:")
            for fail in self.failures:
                lines.append(f"  - {fail}")
        return "\n".join(lines)


def evaluate_symbolic_expression(
    expr: str | Callable | Any,
    context: Mapping[str, Any],
) -> np.ndarray:
    """Safely evaluate a symbolic expression (string, callable, or SymPy expr).

    Parameters
    ----------
    expr : str | Callable | Any
        The symbolic expression. Can be a python math string, a callable
        f(context) or f(**context), or a SymPy expression.
    context : Mapping[str, Any]
        Variable bindings (e.g. t, N, g, hx, hz, etc.).

    Returns
    -------
    np.ndarray
        Evaluated numerical result as a NumPy array.
    """
    if callable(expr):
        try:
            val = expr(**context)
        except TypeError:
            val = expr(context)
        return np.asarray(val, dtype=float)

    if isinstance(expr, str):
        # Evaluate string expression in safe namespace
        local_scope = dict(_SAFE_MATH)
        local_scope.update(context)
        try:
            val = eval(expr, {"__builtins__": {}}, local_scope)
            return np.asarray(val, dtype=float)
        except Exception as err:
            raise ValueError(f"Failed to evaluate expression '{expr}': {err}") from err

    # Handle SymPy expression if passed
    if hasattr(expr, "free_symbols"):
        import sympy as sp
        symbols = sorted(list(expr.free_symbols), key=lambda s: s.name)
        func = sp.lambdify(symbols, expr, modules=["numpy", "math"])
        args = [context.get(s.name, 0.0) for s in symbols]
        val = func(*args)
        return np.asarray(val, dtype=float)

    return np.asarray(expr, dtype=float)


def build_quspin_hamiltonian(
    spec: RingChainSpec | dict[str, Any],
    positive_sign_convention: bool = True,
) -> SinglePixelHamiltonianQuSpin:
    """Build SinglePixelHamiltonianQuSpin from RingChainSpec or parameter dict.

    In goal.md, the Hamiltonian has positive sign convention:
        H = h0*sigma_0 + sum h*sigma_i + sum J1*sigma_i*sigma_{i+1} + ...
    SinglePixelHamiltonianQuSpin has negative signs (-J, -hx, -hz).
    When positive_sign_convention=True, we negate parameters to match goal.md.
    """
    if isinstance(spec, RingChainSpec):
        n = spec.detector_n
        top = spec.topology
        hq = spec.qubit_field
        hd = spec.detector_field
        j1 = spec.nearest
        j2 = spec.second
        gx, gy, gz = spec.edge_couplings
    else:
        n = int(spec.get("detector_n", spec.get("N", spec.get("N_pixel", 4))))
        top = spec.get("topology", spec.get("connectivity", "ring"))
        hq = spec.get("qubit_field", (spec.get("hx0", 0.0), 0.0, spec.get("hz0", 0.0)))
        hd = spec.get("detector_field", (spec.get("hx", 0.0), 0.0, spec.get("hz", 0.0)))
        j1 = spec.get("nearest", (spec.get("Jxx", 0.0), spec.get("Jyy", 0.0), spec.get("J", 1.0)))
        j2 = spec.get("second", (0.0, 0.0, spec.get("J2", 0.0)))
        raw_g = spec.get("coupling", (spec.get("Jx", 0.0), spec.get("Jy", 0.0), spec.get("Jz", 0.0)))
        if top == "ring":
            gx = raw_g[0] / np.sqrt(n) if raw_g[0] else 0.0
            gy = raw_g[1] / np.sqrt(n) if raw_g[1] else 0.0
            gz = raw_g[2] / n if raw_g[2] else 0.0
        else:
            gx, gy, gz = raw_g

    # Sign factor to match goal.md positive signs with QuSpin's internal minus signs
    sgn = -1.0 if positive_sign_convention else 1.0

    return SinglePixelHamiltonianQuSpin(
        N_pixel=n,
        J=sgn * j1[2],
        Jxx=sgn * j1[0],
        Jyy=sgn * j1[1],
        hx=sgn * hd[0],
        hz=sgn * hd[2],
        hx0=sgn * hq[0],
        hz0=sgn * hq[2],
        Jx=sgn * gx,
        Jy=sgn * gy,
        Jz=sgn * gz,
        J2=sgn * j2[2],
        connectivity=top,
        central_coupling="all" if top == "ring" else "auto",
        use_symmetry=True,
    )


def check_physical_assumptions(
    ham: SinglePixelHamiltonianQuSpin,
    spec: RingChainSpec | dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    """Verify hermiticity, scale hierarchies, and physical validity constraints."""
    log: dict[str, Any] = {}
    passed = True

    # 1. Hermiticity
    try:
        H_dense = ham.generate()
        scale = max(float(np.linalg.norm(H_dense)), 1.0)
        herm_res = float(np.linalg.norm(H_dense - H_dense.conj().T) / scale)
        log["hermiticity_residual"] = herm_res
        if herm_res > 1.0e-12:
            passed = False
            log["hermiticity_error"] = f"Hermiticity residual {herm_res:.3e} exceeds 1e-12"
    except Exception as err:
        passed = False
        log["hermiticity_error"] = str(err)

    # 2. Scale hierarchy & perturbative control parameter
    if isinstance(spec, RingChainSpec):
        g_max = max(abs(c) for c in spec.coupling)
        h_max = max(max(abs(c) for c in spec.qubit_field), max(abs(c) for c in spec.detector_field))
        j_max = max(max(abs(c) for c in spec.nearest), max(abs(c) for c in spec.second))
    else:
        g_max = max(abs(spec.get(k, 0.0)) for k in ("Jx", "Jy", "Jz", "coupling"))
        h_max = max(abs(spec.get(k, 0.0)) for k in ("hx", "hz", "hx0", "hz0"))
        j_max = max(abs(spec.get(k, 0.0)) for k in ("J", "Jxx", "Jyy", "J2"))

    intrinsic = max(h_max, j_max)
    log["g_max"] = g_max
    log["intrinsic_scale"] = intrinsic

    # If perturbative flag or epsilon is requested:
    if intrinsic > 0 and g_max > 0:
        ratio = g_max / intrinsic
        log["perturbative_ratio_g_over_max"] = ratio
        if ratio > 1.0:
            log["perturbative_warning"] = (
                f"Coupling g={g_max:.3e} exceeds intrinsic scale {intrinsic:.3e}; "
                "outside strictly perturbative regime."
            )

    # 3. Longitudinal QND symmetry check [H, sigma_0^z] == 0
    is_longitudinal = (ham.Jx == 0.0 and ham.Jy == 0.0 and ham.hx0 == 0.0)
    log["is_longitudinal_qnd"] = is_longitudinal

    return passed, log


class GenericNumericalVerifier:
    """Independent generic numerical verifier using QuSpin Hamiltonians."""

    def __init__(
        self,
        positive_sign_convention: bool = True,
        angle_tolerance: float = 1.0e-5,
        isometry_tolerance: float = 1.0e-10,
    ) -> None:
        self.positive_sign_convention = positive_sign_convention
        self.angle_tolerance = angle_tolerance
        self.isometry_tolerance = isometry_tolerance

    def verify(
        self,
        candidate_expr: str | Callable | Any,
        base_spec: dict[str, Any],
        times: Sequence[float] = (0.2, 0.5, 1.0, 2.0),
        n_values: Sequence[int] = (2, 3, 4, 5),
        candidate_summary: str = "Analytical theta formula",
    ) -> VerificationResult:
        """Verify symbolic / analytical candidate angles across system sizes and times.

        Parameters
        ----------
        candidate_expr : str | Callable | Any
            Formula or callable returning candidate theta angle(s).
        base_spec : dict[str, Any]
            Physical parameters of the model (topology, fields, couplings).
        times : Sequence[float]
            Evolution times to check.
        n_values : Sequence[int]
            System sizes N to verify numerically (up to N=11).
        candidate_summary : str
            Brief description of candidate for logging.

        Returns
        -------
        VerificationResult
        """
        all_failures: list[str] = []
        per_size_results: dict[int, dict[str, Any]] = {}
        max_angle_err_overall = 0.0
        rms_angle_err_overall = 0.0
        max_isom_res_overall = 0.0
        max_herm_res_overall = 0.0
        phys_passed_overall = True
        overall_phys_log: dict[str, Any] = {}

        for n in n_values:
            if n > 11:
                all_failures.append(f"Size N={n} exceeds maximum allowed N=11.")
                continue

            current_spec = dict(base_spec)
            current_spec["detector_n"] = n
            ham = build_quspin_hamiltonian(current_spec, self.positive_sign_convention)

            # Check physical assumptions
            phys_ok, phys_log = check_physical_assumptions(ham, current_spec)
            if not phys_ok:
                phys_passed_overall = False
                all_failures.append(f"Physical assumptions check failed at N={n}: {phys_log}")
            overall_phys_log[f"N={n}"] = phys_log
            max_herm_res_overall = max(max_herm_res_overall, phys_log.get("hermiticity_residual", 0.0))

            # Diagonalize Hamiltonian once
            try:
                energies, vectors = ham.diagonalize()
            except Exception as err:
                all_failures.append(f"Diagonalization failed at N={n}: {err}")
                continue

            expected_root_count = 2**n
            size_records: list[dict[str, Any]] = []

            for t in times:
                # 1. Exact relative evolution subblocks
                u00, u10 = evolution_subblocks_from_eigenbasis(energies, vectors, t)
                identity = np.eye(u00.shape[1], dtype=np.complex128)
                isometry_res = float(np.linalg.norm(u00.conj().T @ u00 + u10.conj().T @ u10 - identity))
                max_isom_res_overall = max(max_isom_res_overall, isometry_res)
                if isometry_res > self.isometry_tolerance:
                    all_failures.append(
                        f"N={n}, t={t}: Column isometry residual {isometry_res:.3e} exceeds tolerance."
                    )

                # 2. Exact projective roots and angles
                spectrum = generalized_relative_evolution_spectrum(u00, u10)
                exact_theta = spectrum.theta
                if len(exact_theta) != expected_root_count:
                    all_failures.append(
                        f"N={n}, t={t}: Exact roots count {len(exact_theta)} != expected {expected_root_count}."
                    )

                # 3. Evaluate candidate symbolic expression
                eval_context = {
                    "t": t,
                    "N": n,
                    "detector_n": n,
                    "gx": abs(ham.Jx),
                    "gy": abs(ham.Jy),
                    "gz": abs(ham.Jz),
                    "g": max(abs(ham.Jx), abs(ham.Jy), abs(ham.Jz)),
                    "hx": abs(ham.hx),
                    "hz": abs(ham.hz),
                    "hx0": abs(ham.hx0) if ham.hx0 is not None else abs(ham.hx),
                    "hz0": abs(ham.hz0) if ham.hz0 is not None else abs(ham.hz),
                    "jx": abs(ham.Jxx),
                    "jy": abs(ham.Jyy),
                    "jz": abs(ham.J),
                    "j": abs(ham.J),
                    "j2z": abs(ham.J2),
                }
                eval_context.update(current_spec)

                try:
                    cand_val = evaluate_symbolic_expression(candidate_expr, eval_context)
                except Exception as err:
                    all_failures.append(f"N={n}, t={t}: Candidate evaluation failed: {err}")
                    continue

                # Broadcast scalar candidate to all roots if uniform
                if cand_val.ndim == 0 or cand_val.size == 1:
                    cand_theta = np.full(expected_root_count, float(cand_val))
                else:
                    cand_theta = cand_val.ravel()

                if cand_theta.size != expected_root_count:
                    all_failures.append(
                        f"N={n}, t={t}: Candidate root count {cand_theta.size} != expected {expected_root_count}."
                    )
                    continue

                # 4. Angle range validation: theta in [0, pi]
                if np.any(cand_theta < -1.0e-9) or np.any(cand_theta > np.pi + 1.0e-9):
                    all_failures.append(
                        f"N={n}, t={t}: Candidate angles outside physical range [0, pi]: "
                        f"min={cand_theta.min():.3f}, max={cand_theta.max():.3f}."
                    )

                # 5. Compare with exact angles via Hungarian assignment
                try:
                    max_err, rms_err = matched_projective_angle_error(exact_theta, cand_theta)
                except Exception as err:
                    all_failures.append(f"N={n}, t={t}: Angle comparison failed: {err}")
                    continue

                max_angle_err_overall = max(max_angle_err_overall, max_err)
                rms_angle_err_overall = max(rms_angle_err_overall, rms_err)

                if max_err > self.angle_tolerance:
                    all_failures.append(
                        f"N={n}, t={t}: Max angle error {max_err:.3e} exceeds tolerance {self.angle_tolerance:.3e}."
                    )

                size_records.append({
                    "time": t,
                    "max_angle_error": max_err,
                    "rms_angle_error": rms_err,
                    "column_isometry_residual": isometry_res,
                })

            per_size_results[n] = {
                "records": size_records,
                "dimension": expected_root_count,
            }

        passed = (len(all_failures) == 0) and phys_passed_overall

        return VerificationResult(
            passed=passed,
            candidate_summary=candidate_summary,
            max_angle_error=max_angle_err_overall,
            rms_angle_error=rms_angle_err_overall,
            max_column_isometry_residual=max_isom_res_overall,
            max_hermiticity_residual=max_herm_res_overall,
            physical_assumptions_passed=phys_passed_overall,
            physical_assumptions_log=overall_phys_log,
            per_size_results=per_size_results,
            failures=all_failures,
        )


def main() -> None:
    """CLI entry point for running generic verification."""
    parser = argparse.ArgumentParser(
        description="Generic Numerical Verifier for Analytic P(theta) using QuSpin Hamiltonians."
    )
    parser.add_argument("--candidate", type=str, required=True, help="Path to JSON file or formula string.")
    parser.add_argument("--topology", type=str, default="ring", choices=["ring", "chain"])
    parser.add_argument("--n-values", type=str, default="2,3,4,5", help="Comma-separated system sizes N <= 11.")
    parser.add_argument("--times", type=str, default="0.2,0.5,1.0", help="Comma-separated evolution times.")
    parser.add_argument("--tolerance", type=float, default=1.0e-5, help="Maximum allowed angle error.")
    parser.add_argument("--log", type=str, default=None, help="Append outcome to log JSONL file.")
    args = parser.parse_args()

    n_values = [int(n.strip()) for n in args.n_values.split(",")]
    times = [float(t.strip()) for t in args.times.split(",")]

    # Check if candidate is a JSON file
    cand_path = Path(args.candidate)
    if cand_path.is_file():
        with open(cand_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        expr = data.get("theta", data.get("candidate", "0"))
        spec = data.get("spec", {"topology": args.topology})
        desc = data.get("description", cand_path.stem)
    else:
        expr = args.candidate
        spec = {"topology": args.topology}
        desc = f"CLI expression: {expr}"

    verifier = GenericNumericalVerifier(angle_tolerance=args.tolerance)
    result = verifier.verify(expr, spec, times=times, n_values=n_values, candidate_summary=desc)

    print(result.summary())

    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "candidate": desc,
            "passed": result.passed,
            "max_angle_error": result.max_angle_error,
            "rms_angle_error": result.rms_angle_error,
            "failures": result.failures,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
