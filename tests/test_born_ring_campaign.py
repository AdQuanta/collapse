"""Production shard ownership and checkpoint integrity on reduced systems."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.run_born_ring_campaign import campaign_tasks,verify_marker
from scripts.audit_born_ring_campaign import audit_campaign

ROOT=Path(__file__).resolve().parents[1]


def config():
    return json.loads((ROOT/"configs/born_ring_baseline_campaign_v1.json").read_text())


def test_campaign_has_unique_six_task_ownership_and_disjoint_times():
    cfg=config()
    seed=json.loads((ROOT/cfg["seed_config"]).read_text())
    tasks=campaign_tasks(cfg,seed)
    assert [(name,s.detector_n) for name,s in tasks]==[(name,n) for name in ("config_079","config_047") for n in (13,14,15)]
    cfg["heldout_times"].append(cfg["discovery_times"][0])
    with pytest.raises(ValueError):campaign_tasks(cfg,seed)


def test_reduced_worker_completes_resumes_and_detects_corrupt_root_checkpoint(tmp_path):
    cfg=config();cfg.update(sizes=[5],seed_names=["config_079"],discovery_times=[.31],heldout_times=[.79])
    path=tmp_path/"config.json";path.write_text(json.dumps(cfg))
    output=tmp_path/"output"
    command=[sys.executable,str(ROOT/"scripts/run_born_ring_campaign.py"),"--config",str(path),
             "--output-root",str(output),"--array-index","0"]
    first=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    assert first.returncode==0,first.stdout+first.stderr
    task=output/"task_000_config_079_N5"
    marker=verify_marker(task)
    assert marker["root_count_per_time"]==32
    assert marker["momentum_count"]==5
    rows=json.loads((task/"results.json").read_text())["records"]
    assert [r["split"] for r in rows]==["discovery","heldout"]
    assert all(r["diagnostics"]["qz_validity"] for r in rows)
    audit=audit_campaign(output,path)
    assert audit["audited_conditions"]==2
    assert audit["status"]=="complete"
    assert len(audit["summary"]["groups"])==2
    second=subprocess.run(command+["--resume"],cwd=ROOT,capture_output=True,text=True)
    assert second.returncode==0,second.stdout+second.stderr
    assert "Already complete" in second.stdout
    root=task/"k00/time_0.npz";root.write_bytes(root.read_bytes()+b"corrupt")
    third=subprocess.run(command+["--resume"],cwd=ROOT,capture_output=True,text=True)
    assert third.returncode!=0
    assert "checkpoint hash mismatch" in third.stderr
    with pytest.raises(ValueError,match="checkpoint hash mismatch"):
        audit_campaign(output,path)
