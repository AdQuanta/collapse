"""Candidate matrix-pencil characterization verifier for `SPEC.md` §3.

STATUS: CANDIDATE. Not activated. `SPEC.md` §0.1 permits the research agent to
propose a verifier but forbids activating one without explicit user approval,
so this checker reports `certification: false` unconditionally until its
manifest is activated by the user.

It certifies the four cases the "Complete matrix-pencil characterization" gate
names — finite, infinite, degenerate, singular — against
`core.pencil_characterization.characterize_pencil_roots`, using fixtures whose
answers are known in closed form or by exact construction rather than by
snapshot.

Unlike `exact-formalism-v1`, this verifier hashes the `core/` modules it
depends on as well as `SPEC.md` and its own source. Hash-binding only the
specification and the verifier's own file is insufficient for any verifier that
imports `core/`: a change there can alter verifier output while every recorded
hash still matches.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.linalg import expm, fractional_matrix_power

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

import sys

sys.path.insert(0, str(ROOT))

from core.pencil_characterization import (  # noqa: E402
    STATUS_DEFECTIVE,
    STATUS_NOT_SEPARATED,
    STATUS_REGULAR,
    STATUS_SINGULAR,
    characterize_pencil_roots,
)
from core.projective_roots import split_qubit_first_blocks  # noqa: E402
from core.quantum_utils import generate_random_unitary  # noqa: E402

FIXED_SOURCES = (
    "SPEC.md",
    "verifier/matrix_pencil/v1/check.py",
    "verifier/matrix_pencil/v1/METHOD.md",
)

KERNEL_TOLERANCE = 1.0e-13


def symbolic_checks() -> list[str]:
    """Exact algebra behind the §3 reduction, independent of floating point."""

    names = []

    # 1. The §3 outcome pencils, derived from the block decomposition.
    lam, x, y = sp.symbols("lambda x y", complex=True)
    entries = sp.symbols("u:16", complex=True)
    u = sp.Matrix(4, 4, entries)
    detector = sp.Matrix([x, y])
    qubit = sp.Matrix([1, lam]) / sp.sqrt(1 + sp.Abs(lam) ** 2)
    evolved = u * sp.kronecker_product(qubit, detector)
    scale = 1 / sp.sqrt(1 + sp.Abs(lam) ** 2)
    outcome_0 = scale * (u[2:, :2] + lam * u[2:, 2:]) * detector
    outcome_1 = scale * (u[:2, :2] + lam * u[:2, 2:]) * detector
    assert sp.simplify(evolved[2:, :] - outcome_0) == sp.zeros(2, 1)
    assert sp.simplify(evolved[:2, :] - outcome_1) == sp.zeros(2, 1)
    names.append("outcome pencils follow from the block decomposition")

    # 2. Algebraic multiplicity is not the kernel weight: a Jordan block has
    #    determinant (lambda-1)**2 but a one-dimensional kernel.
    jordan = sp.Matrix([[1, 1], [0, 1]])
    pencil = lam * sp.eye(2) - jordan
    assert sp.expand(pencil.det()) == sp.expand((lam - 1) ** 2)
    assert pencil.subs(lam, 1).rank() == 1
    assert len(pencil.subs(lam, 1).nullspace()) == 1
    names.append("defective root: algebraic 2, kernel 1")

    # 3. A singular pencil has a kernel at every projective point, so no finite
    #    weighted sum defines a measure on it.
    alpha, beta = sp.symbols("alpha beta", complex=True)
    swap = sp.eye(4).permute_rows([0, 2, 1, 3])
    for outcome in (0, 1):
        rows = swap[2 * (1 - outcome) : 2 * (2 - outcome), :]
        block = beta * rows[:, :2] + alpha * rows[:, 2:]
        assert sp.expand(block.det()) == 0
    names.append("SWAP outcome pencils are identically singular")

    # 4. Kernels at distinct roots are independent: the identity the numerical
    #    separation test relies on, shown on the generic two-root case.
    a_val, b_val = sp.symbols("a b", complex=True)
    diag = sp.Matrix([[a_val, 0], [0, b_val]])
    first = (diag - a_val * sp.eye(2)).nullspace()[0]
    second = (diag - b_val * sp.eye(2)).nullspace()[0]
    independence = sp.Matrix.hstack(first, second).det()
    assert sp.simplify(independence) != 0
    names.append("kernels at distinct roots are independent")

    return names


def _defective_unitary(size: int = 2) -> np.ndarray:
    """Unitary whose outcome-0 pencil is ``D (lambda I - J_size(1))``."""

    m = np.eye(size, dtype=np.complex128) + np.diag(np.ones(size - 1), 1)
    d = fractional_matrix_power(np.eye(size) + m @ m.conj().T, -0.5)
    lower = np.hstack([-d @ m, d])
    _, _, right_h = np.linalg.svd(lower)
    return np.vstack([right_h[size:], lower])


def _qnd_unitary(phases_0, phases_1) -> np.ndarray:
    """Strict QND: block-diagonal in the qubit basis, detector phases only."""

    size = len(phases_0)
    zero = np.zeros((size, size), dtype=np.complex128)
    u00 = np.diag(np.exp(1j * np.asarray(phases_0, dtype=float)))
    u11 = np.diag(np.exp(1j * np.asarray(phases_1, dtype=float)))
    return np.block([[u00, zero], [zero, u11]])


def _rotation_direct_sum(angles) -> np.ndarray:
    """Direct sum of real qubit rotations, one per detector index."""

    half = np.asarray(angles, dtype=float) / 2.0
    cosine, sine = np.diag(np.cos(half)), np.diag(np.sin(half))
    return np.block([[cosine, -sine], [sine, cosine]]).astype(np.complex128)


def _matched_ring_blocks():
    from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy

    hamiltonian = SinglePixelHamiltonianNumpy(
        N_pixel=4, J=1.0, Jpm=0.0, Jx=0.005, Jy=0.0, Jz=0.0, Jzx=0.0, Jcpm=0.0,
        hx=0.0, hz=0.1, hx0=0.0, hz0=0.1,
        connectivity="ring", central_coupling="all",
    ).generate()
    return split_qubit_first_blocks(expm(-1.0j * hamiltonian * 37.0))


def _exchange_blocks(size: int):
    from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin

    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=size, J=0.0,
        Jx=0.7 / np.sqrt(size), Jy=0.7 / np.sqrt(size),
        hx=0.0, hz=0.0, hx0=0.0, hz0=0.0,
        central_coupling="all", use_symmetry=False,
    ).generate()
    unitary = expm(-1.0j * 0.61 * hamiltonian)
    dimension = 2**size
    return unitary[:dimension, :dimension], unitary[dimension:, :dimension]


def _infinite_sector_blocks(dimension: int = 6, nullity: int = 2):
    rng = np.random.default_rng(20260920)
    u00 = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    u00[:, :nullity] = 0.0
    u10 = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    return u00, u10, nullity


def fixture_cases() -> list[dict]:
    """Deterministic cases with expectations fixed by construction."""

    cases: list[dict] = []

    # --- finite -----------------------------------------------------------
    for seed in (20260920, 20260921, 20260922):
        blocks = split_qubit_first_blocks(generate_random_unitary(8, seed=seed))
        cases.append(
            dict(
                case_id=f"finite__generic_{seed}", family="finite",
                u00=blocks.A, u10=blocks.C,
                expect_status=STATUS_REGULAR, expect_complete=True,
                expect_all_simple=True, expect_infinite=0,
            )
        )

    # --- infinite ---------------------------------------------------------
    u00, u10, nullity = _infinite_sector_blocks()
    cases.append(
        dict(
            case_id="infinite__rank_deficient_u00", family="infinite",
            u00=u00, u10=u10,
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_infinite=1, expect_infinite_weight=nullity,
        )
    )

    # --- degenerate, semisimple ------------------------------------------
    blocks = _matched_ring_blocks()
    cases.append(
        dict(
            case_id="degenerate__matched_ring_sixfold", family="degenerate",
            u00=blocks.A, u10=blocks.C,
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_distinct=9, expect_heaviest_weight=6,
        )
    )

    # --- degenerate, defective (negative control) -------------------------
    blocks = split_qubit_first_blocks(_defective_unitary())
    cases.append(
        dict(
            case_id="defective__jordan_block", family="defective",
            u00=blocks.D, u10=-blocks.C,
            expect_status=STATUS_DEFECTIVE, expect_complete=False,
            expect_distinct=1, expect_heaviest_weight=1,
            expect_algebraic=2,
        )
    )
    for size in (2, 3, 4, 5):
        u00, u10 = _exchange_blocks(size)
        cases.append(
            dict(
                case_id=f"defective__nilpotent_exchange_{size}", family="defective",
                u00=u00, u10=u10,
                expect_status_in=(STATUS_DEFECTIVE, STATUS_NOT_SEPARATED),
                expect_complete=False, expect_nilpotent=True,
            )
        )

    # --- degenerate, defective at larger Jordan size (negative control) ---
    # A size-3 or larger block scatters beyond the cluster tolerance and was
    # previously reported `regular` with `size` spurious simple roots.
    for size in (3, 4, 5):
        blocks = split_qubit_first_blocks(_defective_unitary(size))
        for outcome, mapping in enumerate(
            ((blocks.D, -blocks.C), (blocks.B, -blocks.A))
        ):
            cases.append(
                dict(
                    case_id=f"defective__jordan_{size}_outcome_{outcome}",
                    family="defective",
                    u00=mapping[0], u10=mapping[1],
                    # The weights of a *scattered* defective root do sum to n --
                    # that is the phenomenon, not a defect -- so completeness is
                    # deliberately not asserted here.  The refusal comes from the
                    # kernel conditioning test.
                    expect_not_regular=True,
                )
            )
    bare = np.diag(np.ones(4), 1).astype(np.complex128)
    cases.append(
        dict(
            case_id="defective__bare_jordan_5", family="defective",
            u00=np.eye(5, dtype=np.complex128), u10=bare,
            expect_not_regular=True,
        )
    )

    # --- finite: cardinal Bloch roots must not be read as singular ---------
    cases.append(
        dict(
            case_id="finite__cardinal_bloch_roots", family="finite",
            u00=np.diag([1.0, 0.0, 1.0, 1.0, 1.0]).astype(np.complex128),
            u10=np.diag([0.0, 1.0, 1.0, -1.0, 1.0j]).astype(np.complex128),
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_all_simple=True, expect_distinct=5, expect_infinite=1,
        )
    )

    # --- degenerate: SPEC 15.1 noninteracting control, weight n ------------
    for dimension in (2, 3, 4, 8):
        for angle in (0.3, 1.0, np.pi / 4):
            identity = np.eye(dimension, dtype=np.complex128)
            cases.append(
                dict(
                    case_id=f"degenerate__uncoupled_n{dimension}_t{angle:.3f}",
                    family="degenerate",
                    u00=np.cos(angle / 2) * identity,
                    u10=-np.sin(angle / 2) * identity,
                    expect_status=STATUS_REGULAR, expect_complete=True,
                    expect_distinct=1, expect_heaviest_weight=dimension,
                )
            )

    # --- contract fixtures F0, F1, F3 --------------------------------------
    # F0: identity on qubit x 3-dim detector.  Outcome 0 sits only at the north
    # pole and outcome 1 only at the south pole, each with kernel weight three.
    identity = np.eye(6, dtype=np.complex128)
    blocks = split_qubit_first_blocks(identity)
    cases.append(
        dict(
            case_id="F0__identity_north_pole", family="degenerate",
            u00=blocks.D, u10=-blocks.C,
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_distinct=1, expect_heaviest_weight=3, expect_theta=0.0,
        )
    )
    cases.append(
        dict(
            case_id="F0__identity_south_pole", family="infinite",
            u00=blocks.B, u10=-blocks.A,
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_distinct=1, expect_heaviest_weight=3, expect_infinite=1,
        )
    )

    # F1: strict QND with nontrivial detector phases; same pole-only geometry,
    # and outcome 1 exercises the infinite root.
    blocks = split_qubit_first_blocks(
        _qnd_unitary((0.2, -0.7, 1.1), (-0.1, 0.8, 1.7))
    )
    cases.append(
        dict(
            case_id="F1__qnd_north_pole", family="degenerate",
            u00=blocks.D, u10=-blocks.C,
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_distinct=1, expect_heaviest_weight=3, expect_theta=0.0,
        )
    )
    cases.append(
        dict(
            case_id="F1__qnd_infinite_root", family="infinite",
            u00=blocks.B, u10=-blocks.A,
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_distinct=1, expect_heaviest_weight=3, expect_infinite=1,
        )
    )

    # F3: direct sum of real qubit rotations with a repeated angle.  Two
    # distinct roots at -tan(theta/2); the repeated one has weight two.
    blocks = split_qubit_first_blocks(_rotation_direct_sum((0.2, 0.2, 1.0)))
    cases.append(
        dict(
            case_id="F3__repeated_rotation_angle", family="degenerate",
            u00=blocks.D, u10=-blocks.C,
            expect_status=STATUS_REGULAR, expect_complete=True,
            expect_distinct=2, expect_heaviest_weight=2,
            expect_lambdas=(-np.tan(0.1), -np.tan(0.5)),
        )
    )

    # --- finite and degenerate, on the SPEC 3 outcome pencils ---------------
    # The historical (A, C) pencil is a derived diagnostic that the 2026-09-19
    # contract ruled cannot substitute for a forward outcome pencil, so the same
    # families are also evidenced through the (U11, -U10) and (U01, -U00) maps.
    for seed in (20260925, 20260926):
        blocks = split_qubit_first_blocks(generate_random_unitary(8, seed=seed))
        for outcome, mapping in enumerate(
            ((blocks.D, -blocks.C), (blocks.B, -blocks.A))
        ):
            cases.append(
                dict(
                    case_id=f"finite__spec_outcome_{outcome}_{seed}", family="finite",
                    u00=mapping[0], u10=mapping[1],
                    expect_status=STATUS_REGULAR, expect_complete=True,
                    expect_all_simple=True,
                )
            )
    ring = _matched_ring_blocks()
    for outcome, mapping in enumerate(((ring.D, -ring.C), (ring.B, -ring.A))):
        cases.append(
            dict(
                case_id=f"degenerate__matched_ring_spec_outcome_{outcome}",
                family="degenerate",
                u00=mapping[0], u10=mapping[1],
                expect_status=STATUS_REGULAR, expect_complete=True,
            )
        )

    # --- defective under a change of basis (referee witnesses) ------------
    # Exactly defective integer pencils: det = -14(alpha-beta)^2 with kernel
    # dimension one.  Both were reported `regular` with two spurious simple
    # roots while the guard was the conditioning of the stacked kernel matrix,
    # which is not similarity invariant although defectiveness is.
    cases.append(
        dict(
            case_id="defective__integer_witness_a", family="defective",
            u00=np.array([[-22.0, 28.0], [-49.0, 63.0]], dtype=np.complex128),
            u10=np.array([[-30.0, 28.0], [-67.0, 63.0]], dtype=np.complex128),
            expect_not_regular=True,
        )
    )
    left = np.array([[3.0, 2.0], [9.0, 5.0]], dtype=np.complex128)
    right = np.array([[9.0, 7.0], [6.0, -3.0]], dtype=np.complex128)
    jordan = np.array([[1.0, 1.0], [0.0, 1.0]], dtype=np.complex128)
    cases.append(
        dict(
            case_id="defective__integer_witness_b", family="defective",
            u00=left @ right, u10=left @ jordan @ right,
            expect_not_regular=True,
        )
    )

    # --- singular (negative control) --------------------------------------
    swap = np.eye(4)[[0, 2, 1, 3]]
    blocks = split_qubit_first_blocks(swap)
    for outcome, (num, den) in enumerate(
        ((blocks.D, -blocks.C), (blocks.B, -blocks.A))
    ):
        cases.append(
            dict(
                case_id=f"singular__swap_outcome_{outcome}", family="singular",
                u00=num, u10=den,
                expect_status=STATUS_SINGULAR, expect_no_roots=True,
            )
        )

    return cases


def evaluate(case: dict) -> dict:
    """Evaluate one fixture.  A frozen objective layer must never traceback."""

    try:
        return _evaluate(case)
    except Exception as error:  # noqa: BLE001 - fail closed, never raise
        return dict(
            case_id=case["case_id"], family=case["family"], status="exception",
            error=f"{type(error).__name__}: {error}",
            checks={"no_exception": False}, passed=False,
        )


def _evaluate(case: dict) -> dict:
    result = characterize_pencil_roots(case["u00"], case["u10"])
    checks: dict[str, bool] = {}

    if "expect_status" in case:
        checks["status"] = result.status == case["expect_status"]
    if case.get("expect_not_regular"):
        checks["not_regular"] = result.status != STATUS_REGULAR
        checks["measure_refused"] = not result.measure_is_defined
    if "expect_status_in" in case:
        checks["status"] = result.status in case["expect_status_in"]
    if "expect_complete" in case:
        checks["completeness"] = result.weights_are_complete == case["expect_complete"]
    if case.get("expect_all_simple"):
        checks["all_weights_one"] = all(r.kernel_dimension == 1 for r in result.roots)
    if "expect_infinite" in case:
        checks["infinite_count"] = result.infinite_root_count == case["expect_infinite"]
    if "expect_infinite_weight" in case:
        infinite = [r for r in result.roots if r.classification == "infinite"]
        checks["infinite_weight"] = bool(infinite) and (
            infinite[0].kernel_dimension == case["expect_infinite_weight"]
        )
    if "expect_distinct" in case:
        checks["distinct_count"] = result.distinct_root_count == case["expect_distinct"]
    if "expect_heaviest_weight" in case:
        heaviest = max((r.kernel_dimension for r in result.roots), default=0)
        checks["heaviest_weight"] = heaviest == case["expect_heaviest_weight"]
    if "expect_algebraic" in case:
        checks["algebraic_multiplicity"] = any(
            r.algebraic_multiplicity == case["expect_algebraic"] for r in result.roots
        )
        checks["defective_flagged"] = result.defective_root_count >= 1
    if "expect_theta" in case:
        checks["theta"] = bool(result.roots) and abs(
            result.roots[0].theta - case["expect_theta"]
        ) < 1.0e-12
    if "expect_lambdas" in case:
        got = sorted(
            float(np.real(root.alpha / root.beta))
            for root in result.roots
            if abs(root.beta) > 1.0e-12
        )
        checks["lambdas"] = len(got) == len(case["expect_lambdas"]) and all(
            abs(a - b) < 1.0e-12 for a, b in zip(sorted(case["expect_lambdas"]), got)
        )
    if case.get("expect_no_roots"):
        checks["no_roots"] = result.roots == () and result.total_kernel_dimension == 0
    if case.get("expect_nilpotent"):
        power = np.linalg.matrix_power(
            np.linalg.solve(case["u00"], case["u10"]), case["u00"].shape[0]
        )
        checks["nilpotency_exact"] = float(np.linalg.norm(power, 2)) == 0.0

    # Universal invariants for any case that reports roots.
    if result.roots:
        # These identities characterize a *certified* pencil.  A refused one is
        # refused precisely because they may fail, so they are asserted only
        # where the record claims a usable measure.
        if result.status == STATUS_REGULAR:
            checks["kernel_independence"] = (
                result.kernel_independence_rank == result.total_kernel_dimension
            )
            checks["weights_bounded"] = (
                result.total_kernel_dimension <= result.dimension
            )
        worst_basis = 0.0
        worst_annihilation = 0.0
        for root in result.roots:
            if not root.kernel_dimension:
                continue
            basis = root.kernel_basis
            worst_basis = max(
                worst_basis,
                float(
                    np.linalg.norm(
                        basis.conj().T @ basis - np.eye(root.kernel_dimension)
                    )
                ),
            )
            pencil = root.beta * np.asarray(case["u10"], complex) - root.alpha * np.asarray(
                case["u00"], complex
            )
            worst_annihilation = max(
                worst_annihilation, float(np.linalg.norm(pencil @ basis, ord=2))
            )
        checks["kernel_orthonormal"] = worst_basis < KERNEL_TOLERANCE
        if result.status == STATUS_REGULAR:
            checks["kernel_annihilates"] = worst_annihilation < KERNEL_TOLERANCE

    return dict(
        case_id=case["case_id"],
        family=case["family"],
        status=result.status,
        dimension=result.dimension,
        distinct_root_count=result.distinct_root_count,
        total_kernel_dimension=result.total_kernel_dimension,
        kernel_independence_rank=result.kernel_independence_rank,
        defective_root_count=result.defective_root_count,
        infinite_root_count=result.infinite_root_count,
        maximum_kernel_residual=float(result.maximum_kernel_residual)
        if np.isfinite(result.maximum_kernel_residual)
        else None,
        checks=checks,
        passed=all(checks.values()),
    )


def source_hashes() -> dict[str, str]:
    """Hash the spec, this verifier, and *every* ``core`` module actually loaded.

    Hashing a hand-written subset is not a freeze.  A verifier run imports
    `core.quantum_utils` (which determines the generic fixtures) and the two
    Hamiltonian builders (which determine the matched-ring and exchange
    fixtures); a change to any of them alters this verifier's output while a
    hand-listed hash set still matches.  The module list is therefore read from
    ``sys.modules`` after the fixtures have run, so it cannot drift from what
    was really used.
    """

    digests = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in FIXED_SOURCES
    }
    for name, module in sorted(sys.modules.items()):
        if not name.startswith("core"):
            continue
        origin = getattr(module, "__file__", None)
        if not origin:
            continue
        path = Path(origin).resolve()
        try:
            relative = path.relative_to(ROOT)
        except ValueError:
            continue
        digests[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()

    names = symbolic_checks()
    results = [evaluate(case) for case in fixture_cases()]
    families = sorted({r["family"] for r in results})
    required = {"finite", "infinite", "degenerate", "defective", "singular"}
    coverage_complete = required.issubset(set(families))
    passed = all(r["passed"] for r in results) and coverage_complete

    manifest = json.loads((HERE / "manifest.json").read_text())
    activated = manifest.get("status") == "activated"

    record = {
        "version": manifest["version"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed else "FAIL",
        # SPEC.md 0.1: a candidate verifier never certifies.
        "certification": bool(passed and activated),
        "activated": activated,
        "coverage_complete": coverage_complete,
        "families_covered": families,
        "case_count": len(results),
        "cases_passed": sum(1 for r in results if r["passed"]),
        "symbolic_checks": names,
        "kernel_tolerance": KERNEL_TOLERANCE,
        "source_hashes": source_hashes(),
        "cases": results,
    }
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k != "cases"}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
