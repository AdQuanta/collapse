from __future__ import annotations

import numpy as np

from core.conjecture_two_pixel_comparison import (
    all_specs,
    conjecture_families,
    pair_specs,
    paired_distance_records,
)
from core.two_pixel_study import AngularDiagnosticService, ComparisonSimulator


def test_conjecture_families_reproduce_all_four_evidence_grids():
    families = conjecture_families()
    assert [family.name for family in families] == [
        "hz0",
        "hz_resonance",
        "jpm_coupling",
        "jpm_hz",
    ]
    assert [len(family.values) for family in families] == [7, 15, 12, 25]
    assert 0.1 in families[0].values
    assert {-2.01, -2.0, -1.99, -0.01, 0.0, 0.01, 1.99, 2.0, 2.01}.issubset(
        set(families[1].values)
    )
    assert 1.0 in families[2].values
    assert {-2.01, -1.01, -0.01, 0.01, 0.99, 1.01, 1.99, 2.01}.issubset(
        set(families[3].values)
    )


def test_all_specs_pair_equal_hilbert_spaces_and_collective_scaling():
    specs = all_specs(detector_spins=8)
    pairs = pair_specs(specs)
    assert len(specs) == 118
    assert len(pairs) == 59
    assert {spec.total_qubits for spec in specs} == {9}
    assert {spec.edge_jx for spec in specs} == {0.01 / np.sqrt(8)}
    assert all(single.detector_spins == two.detector_spins == 8 for single, two in pairs)
    assert all(single.n_pixel == 8 and two.n_pixel == 4 for single, two in pairs)


def test_plus_minus_pair_simulates_and_produces_paired_metrics(tmp_path):
    family = next(item for item in conjecture_families() if item.name == "jpm_coupling")
    specs = tuple(
        spec
        for spec in all_specs(detector_spins=6)
        if spec.family == family.name and spec.parameter_value == 1.0
    )
    simulator = ComparisonSimulator(tmp_path)
    for spec in specs:
        simulator.run(spec, (3.0,))

    service = AngularDiagnosticService(bins=12)
    records = paired_distance_records(tmp_path, specs, (3.0,), service)
    assert len(records) == 1
    assert np.isfinite(records[0]["theta_wasserstein"])
    assert np.isfinite(records[0]["theta_js_divergence"])
    assert 0.0 <= records[0]["common_R_bin_fraction"] <= 1.0

    for spec in specs:
        with np.load(simulator.raw_path(spec, 3.0)) as raw:
            record = service.calculate(spec, 3.0, dict(raw))
        assert record.family == "jpm_coupling"
        assert record.jpm == 1.0
        assert np.isfinite(record.cauchy_log_likelihood_advantage_per_sample)
        assert np.isfinite(record.radius_q99_over_q50)


def test_zeus_comparison_script_has_required_resources_and_safety_controls():
    pbs = open("hpc/zeus_two_pixel_conjecture_comparison.pbs", encoding="utf-8").read()
    runbook = open("hpc/zeus_two_pixel_conjecture_comparison.md", encoding="utf-8").read()
    assert "#PBS -q zeus_new_q" in pbs
    assert "#PBS -l select=1:ncpus=8:mem=128gb" in pbs
    assert "#PBS -m abe" in pbs
    assert "#PBS -M matanhaller@campus.technion.ac.il" in pbs
    assert "python3.11" in pbs
    assert 'MODEL_WORKERS:-1' in pbs
    assert 'raw_t*.npz' in pbs and "-eq 472" in pbs
    assert "qsub hpc/zeus_two_pixel_conjecture_comparison.pbs" in runbook
    assert "No job has been" in runbook
