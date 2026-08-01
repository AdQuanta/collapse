"""Architecture checks for the SOLID single-pixel atlas services."""

from __future__ import annotations

import numpy as np

from collapse.single_pixel_atlas import (
    AngularDiagnosticCalculator,
    DetectorSpectralVarianceProvider,
    FieldRunMetadata,
    PlusMinusSpectralVarianceProvider,
    SinglePixelSpec,
    SpectrumSample,
    SweepRunner,
    central_field_wrapped_variance,
)


class FakeComputer:
    def __init__(self):
        self.calls: list[tuple[float, tuple[float, ...]]] = []

    def compute_field(self, spec, hz, times):
        self.calls.append((hz, tuple(times)))
        samples = [
            SpectrumSample(
                hz=hz,
                t=t,
                eigenvalues=np.array([0.0, 1.0j, 2.0, -0.5j]),
                theta=2.0 * np.arctan(np.array([0.0, 1.0, 2.0, 0.5])),
                theory_variance=0.2,
            )
            for t in times
        ]
        return samples, FieldRunMetadata(hz=hz, sector_count=1, diagonalization_seconds=0.0)


class InMemoryRepository:
    def __init__(self):
        self.samples = {}
        self.metadata = {}

    def has_sample(self, detector_n, hz, t):
        return (detector_n, hz, t) in self.samples

    def save_sample(self, spec, sample):
        self.samples[(spec.detector_n, sample.hz, sample.t)] = sample

    def load_sample(self, detector_n, hz, t):
        return self.samples[(detector_n, hz, t)]

    def save_field_metadata(self, spec, metadata, times):
        self.metadata[metadata.hz] = metadata


def test_sweep_runner_depends_on_interfaces_not_quspin_or_npz():
    computer = FakeComputer()
    repository = InMemoryRepository()
    spec = SinglePixelSpec(detector_n=3, jx=0.01, hz0=0.0)
    SweepRunner(computer, repository).run(spec, (-2.0, 0.0, 2.0), (10.0, 20.0))
    assert len(computer.calls) == 3
    assert len(repository.samples) == 6
    assert set(repository.metadata) == {-2.0, 0.0, 2.0}


def test_resumability_is_repository_driven():
    computer = FakeComputer()
    repository = InMemoryRepository()
    spec = SinglePixelSpec(detector_n=3)
    runner = SweepRunner(computer, repository)
    runner.run(spec, (0.0,), (10.0,))
    runner.run(spec, (0.0,), (10.0,))
    assert len(computer.calls) == 1


def test_diagnostic_calculator_has_one_analysis_responsibility():
    sample = SpectrumSample(
        hz=0.0,
        t=10.0,
        eigenvalues=np.exp(1j * np.linspace(0.0, 2.0 * np.pi, 32, endpoint=False)),
        theta=np.full(32, np.pi / 2.0),
        theory_variance=0.5,
    )
    diagnostic = AngularDiagnosticCalculator(bins=12).calculate(sample)
    assert np.isclose(np.sum(diagnostic.p_theta * np.diff(diagnostic.edges)), 1.0)
    assert diagnostic.finite_eigenvalues == 32
    assert diagnostic.preferred_wrapped_model in {
        "wrapped_gaussian", "wrapped_cauchy", "indistinguishable"
    }
    assert diagnostic.best_fit_wrapped_gaussian_l1 >= 0.0
    assert diagnostic.best_fit_wrapped_cauchy_l1 >= 0.0


def test_plus_minus_reference_fields_include_requested_neighborhoods():
    spec = SinglePixelSpec(detector_n=4, j=0.0, jpm=1.0, jx=0.01)
    assert spec.reference_fields == (-2.0, -1.0, 0.0, 1.0, 2.0)
    assert np.isclose(spec.edge_jx, 0.005)


def test_plus_minus_spectral_variance_reduces_to_free_spin_formula():
    spec = SinglePixelSpec(detector_n=3, j=0.0, jpm=0.0, jx=0.01, hz0=0.0)
    time_value = 7.0
    expected = central_field_wrapped_variance(spec, hz=0.37, t=time_value)
    actual = PlusMinusSpectralVarianceProvider().variances(spec, 0.37, (time_value,))[0]
    assert np.isclose(actual, expected, rtol=1e-11, atol=1e-13)


def test_detector_spectral_variance_matches_zz_local_formula():
    spec = SinglePixelSpec(detector_n=4, j=1.0, jpm=0.0, jx=0.01, hz0=0.0)
    time_value = 3.7
    expected = central_field_wrapped_variance(spec, hz=0.1, t=time_value)
    actual = DetectorSpectralVarianceProvider().variances(spec, 0.1, (time_value,))[0]
    assert np.isclose(actual, expected, rtol=1e-11, atol=1e-13)


def test_detector_spectral_variance_supports_mixed_zz_and_plus_minus():
    spec = SinglePixelSpec(detector_n=4, j=1.0, jpm=1.0, jx=0.01, hz0=0.0)
    values = DetectorSpectralVarianceProvider().variances(spec, 0.1, (1.0, 10.0))
    assert len(values) == 2
    assert all(np.isfinite(value) and value >= 0.0 for value in values)
