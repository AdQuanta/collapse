"""
Text-level checks for the manual Zeus postprocess handoff.

The Windows local shell used in this workspace does not always provide bash,
so these tests verify the important handoff invariants without executing any
cluster commands.
"""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_submit_helper_preserves_required_qsub_inputs_and_logs():
    text = _read("hpc/submit_zeus_born_postprocess.sh")
    assert "qsub -v \"$stability_vars\" hpc/zeus_born_postprocess_stability.pbs" in text
    assert "qsub -v \"$diagnostics_vars\" hpc/zeus_born_postprocess_diagnostics.pbs" in text
    assert 'SUMMARY_CSV="${SUMMARY_CSV:-$RUN_ROOT/summary_rows.csv}"' in text
    assert 'PRIMARY_QUEUE_CSV="${PRIMARY_QUEUE_CSV:-$RUN_ROOT/shortlist_primary_n13_n14.csv}"' in text
    assert 'OFF_RESONANCE_CSV="${OFF_RESONANCE_CSV:-$RUN_ROOT/shortlist_off_resonance_controls.csv}"' in text
    assert "qsub_jobid.txt" in text
    assert "verify_zeus_born_postprocess.sh" in text


def test_verify_helper_checks_all_required_postprocess_outputs():
    text = _read("hpc/verify_zeus_born_postprocess.sh")
    required = [
        "metric_stability_primary_N13_N14/stability_summary.csv",
        "metric_stability_primary_N13_N14/run.log",
        "metric_stability_off_resonance_controls_N12_N13/stability_summary.csv",
        "metric_stability_off_resonance_controls_N12_N13/run.log",
        "diagnostics_primary_N13_N14/index.md",
        "diagnostics_primary_N13_N14/run.log",
        "diagnostics_off_resonance_controls/index.md",
        "diagnostics_off_resonance_controls/run.log",
        "scripts/evaluate_born_postprocess_gate.py",
    ]
    for item in required:
        assert item in text
    assert "check_scheduler_log_prefixes" in text
    assert 'metric_stability_primary_N13_N14' in text
    assert 'metric_stability_off_resonance_controls_N12_N13' in text
    assert 'diagnostics_primary_N13_N14' in text
    assert 'diagnostics_off_resonance_controls' in text
    assert 'find "$path" -maxdepth 1 -name "${prefix}.*.log" -type f -size +0c' in text


def test_runbook_keeps_helper_and_exact_qsub_paths_visible():
    text = _read("hpc/zeus_born_postprocess.md")
    assert "bash hpc/submit_zeus_born_postprocess.sh" in text
    assert "bash hpc/verify_zeus_born_postprocess.sh" in text
    assert "qsub -v RUN_ROOT=\"$RUN_ROOT\",LOG_ROOT=\"$STABILITY_LOG_ROOT\"" in text
    assert "qsub -v RUN_ROOT=\"$RUN_ROOT\",LOG_ROOT=\"$DIAGNOSTICS_LOG_ROOT\"" in text
    assert "scripts/evaluate_born_postprocess_gate.py" in text
    assert "metric_stability_primary_N13_N14.<PBS_JOBID>.1.log" in text
    assert "diagnostics_off_resonance_controls.<PBS_JOBID>.2.log" in text


def test_anisotropic_larger_n_handoff_has_pbs_commands_and_logs():
    runbook = _read("hpc/zeus_born_anisotropic_largerN.md")
    scan_pbs = _read("hpc/zeus_born_anisotropic_largerN.pbs")
    post_pbs = _read("hpc/zeus_born_anisotropic_postprocess.pbs")

    assert 'qsub -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT"' in runbook
    assert 'qsub -J 1-6,8-9 -v RUN_ROOT="$RUN_ROOT",LOG_ROOT="$LOG_ROOT"' in runbook
    assert "hpc/zeus_born_anisotropic_largerN.pbs | tee \"$LOG_ROOT/qsub_jobid.txt\"" in runbook
    assert "hpc/zeus_born_anisotropic_postprocess.pbs | tee \"$LOG_ROOT/qsub_jobid.txt\"" in runbook
    assert "<LOG_ROOT>/<run_name>.<PBS_JOBID>.<TASK_ID>.log" in runbook
    assert "--Jxx" in scan_pbs
    assert "--Jyy" in scan_pbs
    assert "--jy-unscaled" in scan_pbs
    assert "chain_transverse_perturbative_N15" in scan_pbs
    assert "RUN_LOG=\"$LOG_ROOT/${RUN_NAME}.${PBS_JOBID:-local}.${TASK_ID}.log\"" in scan_pbs
    assert "--extra-distribution-plots" in post_pbs
    assert "shortlist_primary_n15_n16.csv" in post_pbs


if __name__ == "__main__":
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        name = test.__name__
        try:
            test()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {name}: {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
