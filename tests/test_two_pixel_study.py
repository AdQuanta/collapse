from __future__ import annotations

import numpy as np

from core.two_pixel_study import (
    AngularDiagnosticService,
    ComparisonSimulator,
    default_specs,
    load_raw,
)


def test_default_specs_use_equal_total_collective_normalization():
    specs = default_specs(detector_spins=8)
    assert len(specs) == 4
    assert {spec.total_qubits for spec in specs} == {9}
    assert {spec.edge_jx for spec in specs} == {0.01 / np.sqrt(8)}
    assert {spec.n_pixel for spec in specs if spec.kind == "two"} == {4}
    assert {spec.n_pixel for spec in specs if spec.kind == "single"} == {8}


def test_small_comparison_checkpoints_and_analyzes(tmp_path):
    specs = default_specs(detector_spins=4)[:2]
    simulator = ComparisonSimulator(tmp_path)
    service = AngularDiagnosticService(bins=12)
    for spec in specs:
        simulator.run(spec, (3.0,))
        path = simulator.raw_path(spec, 3.0)
        assert path.is_file()
        raw = load_raw(path)
        assert raw["eigenvalues"].shape == (2**4,)
        assert np.all(np.isfinite(raw["theta"]))
        record = service.calculate(spec, 3.0, raw)
        assert record.finite_eigenvalues == 2**4
        assert 0.0 <= record.born_similarity <= 1.0
