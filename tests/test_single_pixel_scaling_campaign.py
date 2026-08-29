"""Checks for the checkpointed N=11..18 atlas campaign launchers."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from core.scaling_campaign import (
    COLLECTIVE_JX,
    DEFAULT_SIZES,
    STUDIES,
    TaskSpec,
    build_command,
    run_campaign,
    task_layout,
    validate_completed_task,
)


ROOT = Path(__file__).resolve().parents[1]


def test_all_four_today_studies_have_explicit_correct_scaling():
    assert set(STUDIES) == {"hz0", "hz_resonance", "jpm_hz", "jpm_coupling"}
    assert DEFAULT_SIZES == tuple(range(11, 19))
    for definition in STUDIES.values():
        arguments = list(definition.fixed_arguments)
        index = arguments.index("--Jx")
        assert float(arguments[index + 1]) == COLLECTIVE_JX == 0.01


def test_command_and_layout_are_isolated_per_n(tmp_path):
    spec = TaskSpec(
        repository_root=ROOT,
        campaign_root=tmp_path,
        python_executable="python3.12",
        study_name="jpm_coupling",
        detector_n=18,
    )
    command = build_command(spec)
    assert command[0] == "python3.12"
    assert "--N" in command and command[command.index("--N") + 1] == "18"
    assert "--Jx" in command and command[command.index("--Jx") + 1] == "0.01"
    assert "--Jpm" not in command  # the driver supplies the complete default grid including Jpm=J
    layout = task_layout(tmp_path, "jpm_coupling", 18)
    assert layout.task_root.name == "N18"
    assert layout.stdout_log.name == "stdout.log"
    assert layout.stderr_log.name == "stderr.log"


def test_dry_run_checkpoints_after_each_size(tmp_path):
    results = run_campaign(
        repository_root=ROOT,
        campaign_root=tmp_path,
        python_executable="python3.12",
        study_name="hz0",
        sizes=(11, 12),
        workers=2,
        force=False,
        dry_run=True,
        allow_small_smoke=False,
    )
    assert [row["detector_n"] for row in results] == [11, 12]
    summary = json.loads((tmp_path / "hz0" / "campaign_summary.json").read_text(encoding="utf-8"))
    assert len(summary["results"]) == 2
    assert summary["edge_scaling"] == "Jx/sqrt(N)"


def test_production_grid_rejects_unrequested_sizes(tmp_path):
    with pytest.raises(ValueError, match="N=11"):
        run_campaign(
            repository_root=ROOT,
            campaign_root=tmp_path,
            python_executable="python3.12",
            study_name="hz0",
            sizes=(10,),
            workers=1,
            force=False,
            dry_run=True,
            allow_small_smoke=False,
        )


def test_completion_validation_checks_outputs_and_edge_scaling(tmp_path):
    definition = STUDIES["hz0"]
    spec = TaskSpec(
        repository_root=ROOT,
        campaign_root=tmp_path,
        python_executable="python3.12",
        study_name="hz0",
        detector_n=11,
    )
    layout = task_layout(tmp_path, "hz0", 11)
    layout.figure_root.mkdir(parents=True)
    layout.raw_root.mkdir(parents=True)
    atlases = []
    for index in range(definition.expected_atlases):
        path = layout.figure_root / f"atlas_{index}.png"
        path.touch()
        atlases.append(str(path))
    summary = layout.figure_root / "summary.png"
    metrics = layout.figure_root / "metrics.csv"
    summary.touch()
    metrics.touch()
    for index in range(definition.expected_raw_spectra):
        (layout.raw_root / f"raw_{index}.npz").touch()
    manifest = {
        "detector_n": 11,
        "fixed_parameters": {
            "Jx": 0.01,
            "Jx_edge": 0.01 / math.sqrt(11),
        },
        "atlases": atlases,
        "summary_plot": str(summary),
        "metrics_csv": str(metrics),
    }
    (layout.figure_root / definition.manifest_name).write_text(json.dumps(manifest), encoding="utf-8")
    checked = validate_completed_task(spec)
    assert checked["raw_spectrum_count"] == definition.expected_raw_spectra
    assert math.isclose(checked["edge_Jx"], 0.01 / math.sqrt(11))


def test_four_pbs_arrays_cover_n11_through_n18_and_use_shared_logging():
    pbs_files = {
        "hz0": "zeus_hz0_atlas_N11_N18.pbs",
        "hz_resonance": "zeus_hz_resonance_atlas_N11_N18.pbs",
        "jpm_hz": "zeus_jpm_hz_atlas_N11_N18.pbs",
        "jpm_coupling": "zeus_jpm_coupling_atlas_N11_N18.pbs",
    }
    for study, filename in pbs_files.items():
        source = (ROOT / "hpc" / filename).read_text(encoding="utf-8")
        assert "#PBS -J 11-18" in source
        assert "#PBS -q zeus_new_q" in source
        assert "#PBS -l select=1:ncpus=8:mem=128gb" in source
        assert "#PBS -m abe" in source
        assert "#PBS -M matanhaller@campus.technion.ac.il" in source
        assert f'STUDY="{study}"' in source
        assert "zeus_single_pixel_atlas_common.sh" in source
        assert 'source "$REPO_ROOT/hpc/zeus_single_pixel_atlas_common.sh"' in source
        assert 'SUBMIT_DIR="${PBS_O_WORKDIR:' in source
    common = (ROOT / "hpc" / "zeus_single_pixel_atlas_common.sh").read_text(encoding="utf-8")
    assert 'PYTHON_BIN="${PYTHON_BIN:-python3.11}"' in common
    assert "sys.version_info[:2] == (3, 11)" in common
    assert '"quspin":"1.0.0"' in common
    assert '"quspin-extensions":"0.1.6"' in common
    assert "COLLECTIVE_JX=0.01" in common
    assert "EDGE_COUPLING_FORMULA=0.01/sqrt(N)" in common
    assert "PBS_LOG=" in common
    assert "DONE.json" in common
    assert "Missing core/scaling_campaign.py" in common
    assert "synchronize the study launchers to Zeus" in common
