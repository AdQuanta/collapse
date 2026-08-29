"""Small-system tests for the unified classification point workflow."""

from core.hamiltonian_classification import (
    SinglePixelClassificationPoint,
    classify_single_pixel_point,
)


def test_qnd_point_is_qz_valid_but_not_full_sphere_resolved() -> None:
    point = SinglePixelClassificationPoint(
        detector_n=3,
        time=1.7,
        J=1.0,
        Jpm=0.2,
        Jx=0.0,
        Jz=0.3,
        hx=0.1,
        hz=0.1,
        hz0=0.1,
        central_scale="none",
        n_phi=8,
        n_mu=4,
        l_max=3,
    )
    result = classify_single_pixel_point(point)

    assert result.summary["qz_valid"] is True
    assert result.summary["coverage"] < 1.0
    assert result.summary["higher_harmonic_leakage"] is None
    assert result.summary["representative_root_nullity"] == 8


def test_transverse_point_has_expected_root_count_and_small_qz_residuals() -> None:
    point = SinglePixelClassificationPoint(
        detector_n=3,
        time=7.0,
        J=1.0,
        Jx=0.05,
        hz=0.1,
        hz0=0.1,
        n_phi=8,
        n_mu=4,
        l_max=3,
    )
    result = classify_single_pixel_point(point)

    assert result.summary["root_count"] == 8
    assert result.summary["qz_valid"] is True
    assert result.summary["maximum_qz_backward_residual"] < 1.0e-12
    assert result.summary["maximum_qz_left_backward_residual"] < 1.0e-12


def test_quspin_translation_sectors_match_dense_classification_roots() -> None:
    shared = dict(
        detector_n=4,
        time=17.0,
        J=1.0,
        Jpm=0.1,
        Jx=0.03,
        hz=0.1,
        hz0=0.1,
        n_phi=8,
        n_mu=4,
        l_max=3,
    )
    dense = classify_single_pixel_point(
        SinglePixelClassificationPoint(**shared, backend="numpy_dense")
    )
    sector = classify_single_pixel_point(
        SinglePixelClassificationPoint(**shared, backend="quspin_sectors")
    )

    from core.projective_roots import matched_bloch_distance

    maximum, rms = matched_bloch_distance(
        dense.bloch_vectors_0,
        sector.bloch_vectors_0,
    )
    assert maximum < 1.0e-10
    assert rms < 1.0e-11
    assert sector.summary["qz_valid"] is True
    assert sector.summary["sector_count"] == 4
    assert sector.summary["maximum_column_isometry_residual"] < 1.0e-12


def test_dense_network_point_records_complete_graph_specification() -> None:
    point = SinglePixelClassificationPoint(
        detector_n=4,
        time=3.0,
        J=1.0,
        Jpm=0.2,
        Jx=0.04,
        hz=0.1,
        hz0=0.1,
        connectivity="erdos_renyi",
        seed=314159,
        erdos_renyi_p=0.8,
        n_phi=8,
        n_mu=4,
        l_max=3,
    )
    result = classify_single_pixel_point(point)

    assert point.detector_graph_spec().seed == 314159
    assert point.detector_graph_spec().erdos_renyi_p == 0.8
    assert result.summary["parameters"]["erdos_renyi_p"] == 0.8
    assert result.summary["qz_valid"] is True


def test_haar_unitary_null_is_reproducible_and_qz_valid() -> None:
    point = SinglePixelClassificationPoint(
        detector_n=3,
        time=0.0,
        backend="haar_unitary",
        seed=271828,
        n_phi=8,
        n_mu=4,
        l_max=3,
    )
    first = classify_single_pixel_point(point)
    second = classify_single_pixel_point(point)

    from core.projective_roots import matched_bloch_distance

    maximum, rms = matched_bloch_distance(
        first.bloch_vectors_0,
        second.bloch_vectors_0,
    )
    assert first.summary["family"] == "haar_unitary_null"
    assert first.summary["root_count"] == 8
    assert first.summary["qz_valid"] is True
    assert first.summary["maximum_column_isometry_residual"] < 1.0e-14
    assert maximum < 1.0e-12
    assert rms < 1.0e-13
