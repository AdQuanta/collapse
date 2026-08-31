"""Checks for the combined-Hamiltonian spacing strip."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose
import pytest
from quspin.basis import spin_basis_general
from quspin.operators import hamiltonian

from core.activation_resolved_projective import (
    RingActivationParameters,
    full_pixel_translation,
)
from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from scripts.build_ring_hz0_full_spacing_3x20 import (
    build_combined_sector_operator,
    central_sector_spectrum,
    excitation_parity_nups,
    expected_all_sector_ids,
    load_all_sector_campaign,
)


def _parameters() -> RingActivationParameters:
    return RingActivationParameters(
        hz=0.31,
        j=0.17,
        jpm=0.23,
        j2=0.11,
        jpm2=0.19,
        jx_unscaled=0.07,
        hz0=0.13,
        evolution_time=1.0,
    )


def test_excitation_parity_nups() -> None:
    assert excitation_parity_nups(6, 0) == [0, 2, 4, 6]
    assert excitation_parity_nups(6, 1) == [1, 3, 5]
    with pytest.raises(ValueError):
        excitation_parity_nups(6, 2)


def test_parity_blocks_reconstruct_unrestricted_momentum_spectrum() -> None:
    """The X0 Xi coupling preserves total-excitation parity exactly."""

    detector_n = 5
    parameters = _parameters()
    even_basis, even_operator = build_combined_sector_operator(
        detector_n,
        parameters,
        momentum=1,
        excitation_parity=0,
    )
    odd_basis, odd_operator = build_combined_sector_operator(
        detector_n,
        parameters,
        momentum=1,
        excitation_parity=1,
    )

    model = SinglePixelHamiltonianQuSpin(
        N_pixel=detector_n,
        J=parameters.j,
        Jpm=parameters.jpm,
        J2=parameters.j2,
        Jpm2=parameters.jpm2,
        Jx=parameters.effective_jx(detector_n),
        Jy=0.0,
        Jz=0.0,
        Jzx=0.0,
        hx=0.0,
        hz=parameters.hz,
        hx0=0.0,
        hz0=parameters.hz0,
        connectivity="ring",
        central_coupling="all",
        seed=44,
        use_symmetry=True,
    )
    static, total_qubits = model._build_static()
    unrestricted_basis = spin_basis_general(
        total_qubits,
        kblock=(full_pixel_translation(detector_n), 1),
    )
    unrestricted_operator = hamiltonian(
        static,
        [],
        basis=unrestricted_basis,
        dtype=np.complex128,
        check_symm=False,
        check_herm=False,
        check_pcon=False,
    )

    split_spectrum = np.sort(
        np.concatenate(
            (
                np.linalg.eigvalsh(even_operator.toarray()),
                np.linalg.eigvalsh(odd_operator.toarray()),
            )
        )
    )
    unrestricted_spectrum = np.linalg.eigvalsh(unrestricted_operator.toarray())
    assert even_basis.Ns + odd_basis.Ns == unrestricted_basis.Ns
    assert_allclose(split_spectrum, unrestricted_spectrum, atol=1.0e-12, rtol=0.0)


def test_reflection_blocks_reconstruct_k_zero_parity_spectrum() -> None:
    detector_n = 5
    parameters = _parameters()
    _, unrestricted = build_combined_sector_operator(
        detector_n,
        parameters,
        momentum=0,
        excitation_parity=0,
    )
    plus_basis, plus = build_combined_sector_operator(
        detector_n,
        parameters,
        momentum=0,
        excitation_parity=0,
        reflection_parity=1,
    )
    minus_basis, minus = build_combined_sector_operator(
        detector_n,
        parameters,
        momentum=0,
        excitation_parity=0,
        reflection_parity=-1,
    )
    resolved_spectrum = np.sort(
        np.concatenate(
            (np.linalg.eigvalsh(plus.toarray()), np.linalg.eigvalsh(minus.toarray()))
        )
    )
    assert plus_basis.Ns + minus_basis.Ns == unrestricted.shape[0]
    assert_allclose(
        resolved_spectrum,
        np.linalg.eigvalsh(unrestricted.toarray()),
        atol=1.0e-12,
        rtol=0.0,
    )


def test_reflection_resolution_rejects_nonzero_momentum() -> None:
    with pytest.raises(ValueError, match="only be resolved at momentum k=0"):
        build_combined_sector_operator(
            5,
            _parameters(),
            momentum=1,
            excitation_parity=0,
            reflection_parity=1,
        )


def test_central_sector_spectrum_has_small_residuals() -> None:
    detector_n = 11
    _, operator = build_combined_sector_operator(
        detector_n,
        _parameters(),
        momentum=1,
        excitation_parity=0,
    )
    result = central_sector_spectrum(
        operator,
        eigenvalue_count=40,
        solver_tolerance=1.0e-10,
    )
    assert result["energies"].shape == (40,)
    assert result["unfolded_spacings"].size >= 20
    assert result["spacing_ratios"].size >= 20
    assert result["maximum_relative_residual"] < 1.0e-8
    assert result["orthogonality_error"] < 1.0e-8


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_load_all_sector_campaign_validates_and_pools(tmp_path: Path) -> None:
    case_ids = [f"case_{index:02d}" for index in range(20)]
    config = {"cases": [{"case_id": case_id} for case_id in case_ids]}
    for sector_index, sector_id in enumerate(expected_all_sector_ids()):
        sector_dir = tmp_path / "sectors" / sector_id
        cases_dir = sector_dir / "cases"
        cases_dir.mkdir(parents=True)
        summary_cases = []
        files = {}
        for case_id in case_ids:
            archive_path = cases_dir / f"{case_id}.npz"
            np.savez_compressed(
                archive_path,
                energies=np.array([0.0, 1.0, 2.0]),
                unfolded_spacings=np.array([0.75, 1.25]),
                spacing_ratios=np.array([0.4, 0.5]),
            )
            metadata = {
                "case_id": case_id,
                "archive_sha256": _sha256(archive_path),
                "unfolded_spacing_count": 2,
                "eigenvalue_count": 3,
                "mean_r": 0.45,
                "maximum_relative_residual": 1.0e-12,
                "orthogonality_error": 2.0e-12,
                "sector_index": sector_index,
            }
            metadata_path = cases_dir / f"{case_id}.json"
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            summary_cases.append(metadata)
            files[f"cases/{case_id}.npz"] = _sha256(archive_path)
            files[f"cases/{case_id}.json"] = _sha256(metadata_path)
        summary_path = sector_dir / "sector_summary.json"
        summary_path.write_text(json.dumps({"cases": summary_cases}), encoding="utf-8")
        files["sector_summary.json"] = _sha256(summary_path)
        (sector_dir / "COMPLETE.json").write_text(
            json.dumps(
                {
                    "status": "complete",
                    "sector_id": sector_id,
                    "case_count": 20,
                    "files": files,
                }
            ),
            encoding="utf-8",
        )

    spectra, metadata, campaign = load_all_sector_campaign(tmp_path, config)

    assert len(expected_all_sector_ids()) == len(set(expected_all_sector_ids())) == 20
    assert len(spectra) == len(metadata) == 20
    assert spectra[0]["unfolded_spacings"].shape == (40,)
    assert spectra[0]["spacing_ratios"].shape == (40,)
    assert len(spectra[0]["sector_unfolded_spacings"]) == 20
    assert metadata[0]["sector_count"] == 20
    assert metadata[0]["mean_r"] == pytest.approx(0.45)
    assert campaign["npz_count"] == 400
    assert campaign["verified_artifact_count"] == 820
    assert len(campaign["completion_marker_sha256"]) == 20
