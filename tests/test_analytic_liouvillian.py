"""Exact scientific controls for the candidate local recurrence."""
import pytest
import sympy as sp

from core.analytic_liouvillian import liouvillian_moments


def test_full_xyz_collective_second_moment():
    hx,hy,hz,jx,jy,jz,kx,ky,kz=sp.symbols('hx hy hz jx jy jz kx ky kz',real=True)
    values=liouvillian_moments((hx,hy,hz),(jx,jy,jz),(kx,ky,kz),maximum_even_order=2)
    expected=4*(hy**2+hz**2)+8*(jy-jz)**2+8*(ky-kz)**2
    assert values[0]==1
    assert sp.expand(values[1]-expected)==0


def test_collective_and_endpoint_are_different_observables():
    h,j=sp.symbols('h J',real=True)
    ring=liouvillian_moments((0,0,h),(j,0,0),(0,0,0),maximum_even_order=4)
    chain=liouvillian_moments((0,0,h),(j,0,0),(0,0,0),maximum_even_order=4,
                              topology='chain',detector_n=3,observable='endpoint_x')
    assert sp.expand(ring[2]-chain[2])==16*h**2*j**2


def test_conserved_collective_x_with_transverse_exchange_block():
    # YY+ZZ conserves total X even though neither bond commutes with each Xi.
    values=liouvillian_moments((sp.Rational(2,3),0,0),(1,2,2),(3,4,4),maximum_even_order=6)
    assert values==(1,0,0,0)


def test_independent_spin_control_through_sixth_moment():
    h=sp.symbols('h',real=True)
    values=liouvillian_moments((0,0,h),(0,0,0),(0,0,0),maximum_even_order=6)
    assert values==(1,4*h**2,16*h**4,64*h**6)


def test_small_ring_bond_convention_is_not_silently_changed():
    with pytest.raises(ValueError,match='N>=5'):
        liouvillian_moments((0,0,1),(1,1,1),(1,1,1),maximum_even_order=2,
                            topology='ring',detector_n=4)
