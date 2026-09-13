"""Check the scientific comparison contract and perturbation normalization."""
from dataclasses import asdict

import numpy as np

from core.ring_chain_family import RingChainSpec
from scripts.run_born_multichannel_sensitivity import variants, paired_decisions


def test_longitudinal_ring_perturbation_is_scaled_once():
    spec = RingChainSpec(7,"ring",(0,0,0),(0,0,.2),(.3,.3,.5),(0,0,0),(.02,.1,0))
    rows = variants(spec,dict(relative_amplitude=.05,directions=["coupling_2","qubit_field_1"],signs=[-1,1]))
    assert len(rows)==5
    for label,other in rows[1:]:
        assert sum(np.count_nonzero(np.array(asdict(other)[k])-np.array(asdict(spec)[k]))
                   for k in ("qubit_field","detector_field","nearest","second","coupling"))==1
        if label.startswith("coupling"):
            assert np.isclose(abs(other.edge_couplings[2]),.005/7,atol=1e-16,rtol=0)
        else:
            assert np.isclose(abs(other.qubit_field[1]),.005,atol=1e-16,rtol=0)


def test_worst_time_and_validation_failures_cannot_be_hidden():
    rows = []
    for n in (5,6,7):
        for label in ("baseline","field"):
            for time in (1.,10.):
                rows.append(dict(candidate="seed",N=n,time=time,perturbation=label,
                    diagnostics=dict(qz_validity=True,balance_binned_relative=.4 if label=="baseline" else .3,
                                     moment_max=.1,coverage=.5)))
    assert paired_decisions(rows)[0]["decision"]=="KEEP"
    rows[-1]["diagnostics"]["balance_binned_relative"] = .5
    assert paired_decisions(rows)[0]["decision"]=="REJECT"
    rows[-1]["validation_failure"] = "cross-driver mismatch"
    assert paired_decisions(rows)[0]["decision"]=="INCONCLUSIVE"


def test_balance_improvement_cannot_hide_a_coverage_regression():
    rows = [dict(candidate="seed",N=5,time=1.,perturbation=label,
        diagnostics=dict(qz_validity=True,balance_binned_relative=balance,moment_max=.1,coverage=coverage))
        for label,balance,coverage in [("baseline",.5,.7),("field",.2,.5)]]
    assert paired_decisions(rows)[0]["decision"]=="REJECT"
