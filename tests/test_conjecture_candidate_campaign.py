from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "conjecture_candidate_campaign_2026-07-16.json"
RUNNER = ROOT / "scripts" / "run_conjecture_candidate_campaign.py"
PBS = ROOT / "hpc" / "zeus_conjecture_candidate_campaign_N11_N18.pbs"


def _load_runner():
    spec = importlib.util.spec_from_file_location("candidate_campaign", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_candidate_catalog_is_unique_and_covers_conjecture_branches():
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    cases = payload["cases"]
    identifiers = [case["id"] for case in cases]
    assert len(identifiers) == len(set(identifiers)) == 12
    assert sum(bool(case["local"]) for case in cases) == 8
    assert payload["zeus_N"] == list(range(11, 19))
    targets = {case["target"] for case in cases}
    assert {"Born", "wrapped-heavy-tail", "hybrid", "control"} <= targets
    assert any("dimerized" in case["id"] for case in cases)
    assert any("all_to_all" in case["id"] for case in cases)


def test_every_collective_coupling_uses_unscaled_cli_and_required_value():
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    for case in payload["cases"]:
        args = case["args"]
        assert "--jx-unscaled" in args
        value = args[args.index("--jx-unscaled") + 1]
        assert value in {"0", "0.01"}
        assert "--Jx" not in args
    hybrid = next(case for case in payload["cases"] if case["id"] == "hybrid_matched_ising_jpm")
    assert hybrid["args"][hybrid["args"].index("--Jpm") + 1] == "1"
    assert hybrid["args"][hybrid["args"].index("--J") + 1] == "1"


def test_command_factory_preserves_times_scaling_and_checkpoint_path(tmp_path):
    module = _load_runner()
    repository = module.CampaignRepository(CONFIG)
    case = repository.cases("local", {"born_matched_xy"})[0]
    factory = module.SearchCommandFactory("python3.11", 11, repository.times, 8)
    command = factory.build(case, tmp_path / case.case_id, 1)
    assert command[:3] == ["python3.11", str(module.SEARCH), "--N"]
    assert command[3] == "11"
    assert command[command.index("--times") + 1:command.index("--model")] == [
        "1000", "10000", "100000", "1e+06"
    ]
    assert command[command.index("--jx-unscaled") + 1] == "0.01"
    assert command[command.index("--workers") + 1] == "8"
    assert command[-2:] == ["--log-file", str(tmp_path / case.case_id / "run.log")]


def test_pbs_matches_zeus_requirements_and_saves_case_checkpoints():
    text = PBS.read_text(encoding="utf-8")
    assert "#PBS -q zeus_new_q" in text
    assert "#PBS -l select=1:ncpus=8:mem=128gb" in text
    assert "#PBS -J 11-18" in text
    assert "#PBS -m abe" in text
    assert "#PBS -M matanhaller@campus.technion.ac.il" in text
    assert 'PYTHON_BIN="${PYTHON_BIN:-python3.11}"' in text
    assert '"$PROJECT_ROOT/scripts/run_conjecture_candidate_campaign.py"' in text
    assert "Each case has its own results.csv, run.log" in text
