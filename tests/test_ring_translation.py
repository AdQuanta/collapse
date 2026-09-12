"""Independent dense checks of all coefficients, sectors and projective rays."""
from dataclasses import replace

import numpy as np
import pytest
from scipy.linalg import expm

from core.projective_roots import production_root_spectrum, bloch_vectors_from_homogeneous, matched_bloch_distance
from core.ring_chain_family import RingChainSpec, build_ring_chain_parts
from core.ring_translation import (
    ring_static_terms,build_ring_translation_block,diagonalize_ring_translation_block,
    evaluate_ring_translation_time,combine_ring_translation_diagnostics,
)


def generic_spec(n):
    return RingChainSpec(n,"ring",(.13,-.07,.11),(.29,.17,-.31),
                         (.41,-.23,.37),(-.19,.09,.15),(.12,-.08,.06))


@pytest.mark.parametrize("n",[5,6,7])
def test_every_momentum_projects_the_full_generic_hamiltonian(n):
    spec=generic_spec(n)
    h0,v=build_ring_chain_parts(spec)
    h=h0+v
    projectors=[]
    count=0
    for k in range(n):
        block=build_ring_translation_block(spec,k)
        p=block.basis.get_proj(np.complex128).toarray()
        np.testing.assert_allclose(p.conj().T@h@p,block.matrix,atol=3e-14,rtol=0)
        np.testing.assert_allclose(h@p,p@block.matrix,atol=3e-14,rtol=0)
        projectors.append(p)
        count+=len(block.top)
    p=np.hstack(projectors)
    np.testing.assert_allclose(p.conj().T@p,np.eye(len(h)),atol=3e-14,rtol=0)
    assert count==2**n


@pytest.mark.parametrize("field",["qubit_field","detector_field","nearest","second","coupling"])
@pytest.mark.parametrize("axis",range(3))
def test_each_independent_coefficient_has_native_positive_normalization(field,axis):
    spec=RingChainSpec(5,"ring",(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0))
    values=[0.,0.,0.];values[axis]=.37
    spec=replace(spec,**{field:tuple(values)})
    h0,v=build_ring_chain_parts(spec)
    for k in (0,1):
        block=build_ring_translation_block(spec,k)
        p=block.basis.get_proj(np.complex128).toarray()
        np.testing.assert_allclose(p.conj().T@(h0+v)@p,block.matrix,atol=1e-14,rtol=0)


@pytest.mark.parametrize("n",[5,6,7])
@pytest.mark.parametrize("time",[.31,37.])
def test_union_of_sector_roots_matches_full_complex_projective_rays(n,time):
    spec=generic_spec(n)
    h0,v=build_ring_chain_parts(spec)
    full=production_root_spectrum(expm(-1j*time*(h0+v)))
    sectors=[]
    for k in range(n):
        block=build_ring_translation_block(spec,k)
        e,v,check=diagonalize_ring_translation_block(block)
        assert max(check.values())<1e-12
        sectors.append(evaluate_ring_translation_time(block,e,v,time))
    combined=combine_ring_translation_diagnostics(n,sectors)
    assert combined["qz_validity"]
    a=np.concatenate([s[1]["alpha"] for s in sectors])
    b=np.concatenate([s[1]["beta"] for s in sectors])
    maximum,_=matched_bloch_distance(bloch_vectors_from_homogeneous(full.alpha,full.beta),
                                    bloch_vectors_from_homogeneous(a,b))
    assert maximum<2e-10
    assert sum(combined["sector_dimensions"])==2**n
    with pytest.raises(ValueError):
        combine_ring_translation_diagnostics(n,sectors[:-1])
    with pytest.raises(ValueError):
        combine_ring_translation_diagnostics(n,sectors[:-1]+[sectors[0]])


def test_sector_adapter_preserves_zero_poles_and_missing_qz_failure():
    spec=replace(generic_spec(5),coupling=(0,0,0),qubit_field=(0,0,0))
    sectors=[]
    for k in range(5):
        b=build_ring_translation_block(spec,k)
        e,v,_=diagonalize_ring_translation_block(b)
        sectors.append(evaluate_ring_translation_time(b,e,v,.5))
    result=combine_ring_translation_diagnostics(5,sectors)
    assert result["qz_validity"]
    assert result["qz_zero_fraction"]==1
    assert not result["numerical_and_structural_gate"]
    sectors[0][0]["qz_validity"]=False
    assert combine_ring_translation_diagnostics(5,sectors)["qz_validity"] is False


def test_open_chain_cannot_be_silently_sectorized():
    with pytest.raises(ValueError):
        ring_static_terms(replace(generic_spec(5),topology="chain"))
