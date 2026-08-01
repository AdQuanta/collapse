from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "expanded_hamiltonian_sweep_2026-07-16.json"
ANALYZER = ROOT / "examples" / "analyze_expanded_hamiltonian_sweep.py"
ATLAS = ROOT / "examples" / "plot_expanded_hamiltonian_atlases.py"
PBS = ROOT / "hpc" / "zeus_expanded_hamiltonian_sweep_N11_N18.pbs"


def _load_analyzer():
    spec = importlib.util.spec_from_file_location("expanded_sweep_analyzer", ANALYZER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_atlas():
    spec = importlib.util.spec_from_file_location("expanded_sweep_atlas", ATLAS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_design_covers_multiple_independent_hamiltonian_dimensions():
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    cases = payload["cases"]
    assert len(cases) == 20
    assert sum(bool(case["local"]) for case in cases) == 17
    assert all(case["zeus"] for case in cases)
    assert payload["default_times"] == [100, 316, 1000, 10000]
    assert payload["zeus_N"] == list(range(11, 19))
    atlas_cases = [case_id for group in payload["atlas_groups"] for case_id, _label in group["cases"]]
    assert {case["id"] for case in cases} <= set(atlas_cases)
    flattened = " ".join(" ".join(case["args"]) for case in cases)
    for factor in (
        "--Jpm", "--Jxx", "--Jyy", "--jy-unscaled", "--hx", "--Jz",
        "--Jzx", "--jcpm-unscaled", "--disorder-strength-hz",
        "--disorder-strength-Jpm", "all_to_all", "chain", "half", "zero",
    ):
        assert factor in flattened


def test_every_central_coupling_is_perturbative_and_collectively_scaled():
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    for case in payload["cases"]:
        args = case["args"]
        assert "--jx-unscaled" in args
        for flag in ("--jx-unscaled", "--jy-unscaled", "--jcpm-unscaled"):
            if flag in args:
                assert abs(float(args[args.index(flag) + 1])) <= 0.01
        assert "--Jx" not in args


def test_joint_score_rewards_born_heavy_continuous_uniform_rows():
    module = _load_analyzer()
    base = {
        "born_similarity": "0.8",
        "phi_uniformity_score": "0.9",
        "tail_density_exponent": "2.05",
        "radius_q99_over_q50": "40",
        "radius_atomic_fraction": "0.01",
        "reciprocity_error": "0.2",
    }
    good = module.score_row(base)
    poor = module.score_row(base | {"tail_density_exponent": "7", "phi_uniformity_score": "0.1"})
    assert math.isfinite(good["joint_score"])
    assert good["joint_score"] > poor["joint_score"]
    assert good["heavy_score"] > poor["heavy_score"]


def test_atlas_distribution_rows_are_normalized_and_antipodal():
    module = _load_atlas()
    eigenvalues = np.array([0.0 + 0.0j, 0.5 + 0.25j, 1.0j, 2.0 - 0.5j])
    distributions = module.DistributionService(16).calculate(eigenvalues)
    widths = np.diff(distributions.edges)
    assert np.isclose(np.sum(distributions.p_theta * widths), 1.0)
    assert np.isclose(np.sum(distributions.p_reflected * widths), 1.0)
    assert np.allclose(distributions.p_reflected, distributions.p_theta[::-1])
    assert np.allclose(distributions.gaussian_reflected, distributions.gaussian[::-1])
    assert np.all((distributions.born >= 0.0) & (distributions.born <= 1.0))


def test_pbs_matches_zeus_requirements_and_runs_post_analysis():
    text = PBS.read_text(encoding="utf-8")
    assert "#PBS -q zeus_new_q" in text
    assert "#PBS -l select=1:ncpus=8:mem=128gb" in text
    assert "#PBS -J 11-18" in text
    assert "#PBS -m abe" in text
    assert "#PBS -M matanhaller@campus.technion.ac.il" in text
    assert 'PYTHON_BIN="${PYTHON_BIN:-python3.11}"' in text
    assert "expanded_hamiltonian_sweep_2026-07-16.json" in text
    assert "analyze_expanded_hamiltonian_sweep.py" in text
    assert "plot_expanded_hamiltonian_atlases.py" in text
    assert '"$PYTHON_BIN" "$ATLAS"' in text
    assert "--workers 1" in text
    assert "Results and plots were checkpointed after every Hamiltonian" in text
