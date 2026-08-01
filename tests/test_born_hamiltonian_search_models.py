"""Smoke tests for Born-search Hamiltonian model plumbing."""

import math
import sys
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

import numpy as np

from born_hamiltonian_search import (
    Candidate,
    energy_degeneracy_metrics,
    evaluate_candidate,
    generate_candidates,
)


def test_energy_degeneracy_metrics_detects_clusters():
    metrics = energy_degeneracy_metrics(np.array([0.0, 0.0, 1.0, 2.0, 2.0]))
    assert metrics["energy_level_count"] == 5.0
    assert metrics["energy_resolved_level_count"] == 3.0
    assert math.isclose(metrics["energy_degenerate_fraction"], 4.0 / 5.0)
    assert metrics["energy_max_multiplicity"] == 2.0


def test_dimerized_pixel_candidate_generation_requires_even_pixel_count():
    base = dict(
        model="dimerized_pixel",
        N=[5],
        J=1.0,
        Jpm=[0.0],
        Jxx=[0.0],
        Jyy=[0.0],
        jx_unscaled=[0.01],
        jy_unscaled=[0.0],
        Jz=[0.0],
        Jzx=[0.0],
        jcpm_unscaled=[0.0],
        hx=[0.0],
        hz=[0.1],
        hz0_modes=["matched"],
        connectivity="ring",
        central_coupling=["auto"],
        seed=44,
    )
    candidates = generate_candidates(Namespace(**base))
    assert len(candidates) == 1
    assert candidates[0].model == "dimerized_pixel"

    invalid = dict(base)
    invalid["N"] = [6]
    try:
        generate_candidates(Namespace(**invalid))
    except ValueError as exc:
        assert "even N_pixel" in str(exc)
    else:
        raise AssertionError("Expected odd N_pixel to be rejected")


def test_dimerized_pixel_numpy_evaluation_smoke():
    candidate = Candidate(
        model="dimerized_pixel",
        N=5,
        J=1.0,
        Jx_unscaled=0.01,
        hz=0.1,
        hz0_mode="matched",
    )
    rows = evaluate_candidate(
        candidate,
        times=[10.0],
        n_bins=20,
        backend="numpy",
        tail_fraction=0.20,
        n_log_bins=12,
        energy_degeneracy_tol=1e-9,
    )
    assert len(rows) == 1
    metrics = rows[0]["metrics"]
    assert math.isfinite(metrics["born_similarity"])
    assert math.isfinite(metrics["phi_uniformity_score"])
    assert "energy_degenerate_fraction" in metrics


def test_single_pixel_disorder_candidate_generation_and_evaluation_smoke():
    args = Namespace(
        model="single_pixel",
        N=[4],
        J=1.0,
        Jpm=[0.0],
        Jxx=[0.0],
        Jyy=[0.0],
        jx_unscaled=[0.02],
        jy_unscaled=[0.0],
        Jz=[0.0],
        Jzx=[0.0],
        jcpm_unscaled=[0.0],
        hx=[0.0],
        hz=[0.1],
        hz0_modes=["matched"],
        connectivity="ring",
        central_coupling=["all"],
        seed=7,
        disorder="uniform",
        disorder_strength=0.0,
        disorder_strength_J=[0.01],
        disorder_strength_Jpm=[0.0],
        disorder_strength_Jx=[0.0],
        disorder_strength_Jz=[0.0],
        disorder_strength_Jzx=[0.0],
        disorder_strength_Jcpm=[0.0],
        disorder_strength_hx=[0.0],
        disorder_strength_hz=[0.0],
    )
    candidates = generate_candidates(args)
    assert len(candidates) == 1
    assert candidates[0].disorder == "uniform"
    assert math.isclose(candidates[0].disorder_strength_J, 0.01)

    rows = evaluate_candidate(
        candidates[0],
        times=[3.0],
        n_bins=12,
        backend="numpy",
        tail_fraction=0.25,
        n_log_bins=8,
        energy_degeneracy_tol=1e-9,
    )
    assert len(rows) == 1
    assert rows[0]["candidate"]["disorder"] == "uniform"
    assert math.isfinite(rows[0]["metrics"]["born_similarity"])
    assert "phi_entropy_score" in rows[0]["metrics"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL {test.__name__}: {exc}")
            failed += 1
    print(f"{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
