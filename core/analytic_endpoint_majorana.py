"""Candidate exact Jacobi reduction for the transverse XX endpoint slice.

H=eta X_Q+g X_Q X_1+h sum Z_i+J sum X_i X_(i+1). No verifier imports.
The return spectrum is a Majorana/Jacobi spectral measure, not root weights.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import comb
import numpy as np
from numpy.polynomial import Chebyshev,Polynomial
from scipy.linalg import eigh_tridiagonal


@dataclass(frozen=True)
class BoundaryAtoms:
    zero_weight: float
    pair_energy: float | None
    pair_weight_each: float

    @property
    def total_weight(self) -> float:
        return self.zero_weight+2*self.pair_weight_each


def _parameters(g: float,h: float,j: float) -> tuple[float,float,float]:
    values=np.asarray([g,h,j],dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError('coefficients must be finite')
    return tuple(2*abs(float(value)) for value in values)


def jacobi_links(n: int,g: float,h: float,j: float) -> np.ndarray:
    """Off-diagonal coefficients for 2N+1 coupled Majoranas, central Y first."""
    if not isinstance(n,int) or n<1:
        raise ValueError('detector size must be a positive integer')
    a,b,c=_parameters(g,h,j)
    links=np.empty(2*n)
    links[0]=a
    links[1::2]=b
    links[2::2]=c
    return links


def endpoint_return(n: int,t: float,g: float,h: float,j: float) -> float:
    """Exact finite-N boundary return via an O(N) Jacobi matrix."""
    if not np.isfinite(t):raise ValueError('time must be finite')
    links=jacobi_links(n,g,h,j)
    energies,vectors=eigh_tridiagonal(np.zeros(2*n+1),links)
    return float(np.dot(vectors[0]**2,np.cos(energies*t)))


def root_atoms(n: int,t: float,g: float,h: float,j: float,eta: float=0.) -> np.ndarray:
    """The two equally weighted polar atoms, coinciding when eta=0."""
    if not np.isfinite(eta):raise ValueError('central field must be finite')
    chi=np.arccos(np.clip(endpoint_return(n,t,g,h,j),-1.,1.))
    return np.arccos(np.clip(np.cos(2*eta*t+np.array([-chi,chi])),-1.,1.))


def boundary_atoms(g: float,h: float,j: float) -> BoundaryAtoms:
    """Discrete part of the infinite half-chain Jacobi spectral measure.

Threshold equalities have zero residue and are not bound states. Degenerate
zero couplings are evaluated as disconnected finite chains before division.
"""
    a,b,c=_parameters(g,h,j)
    A,B,C=a*a,b*b,c*c
    if a==0:return BoundaryAtoms(1.,None,0.)
    if b==0:return BoundaryAtoms(0.,a,.5)
    if c==0:return BoundaryAtoms(B/(A+B),np.sqrt(A+B),A/(2*(A+B)))
    w0=(B-C)/(A+B-C) if b>c else 0.
    bound=A>C+b*c or (c>b and A<C-b*c)
    if not bound:return BoundaryAtoms(w0,None,0.)
    energy=np.sqrt(A*(A+B-C)/(A-C))
    weight=((A-C)**2-B*C)/(2*(A-C)*(A+B-C))
    return BoundaryAtoms(w0,float(energy),float(weight))


def return_spectral_density(omega: np.ndarray,g: float,h: float,j: float) -> np.ndarray:
    """Continuous Jacobi density with respect to d omega; atoms kept separately."""
    a,b,c=_parameters(g,h,j)
    values=np.asarray(omega,dtype=float)
    if not np.all(np.isfinite(values)):raise ValueError('frequencies must be finite')
    density=np.zeros_like(values)
    if a*b*c==0:return density
    active=(np.abs(values)>abs(b-c)) & (np.abs(values)<b+c)
    x=values[active]
    delta=np.sqrt(((b+c)**2-x*x)*(x*x-(b-c)**2))
    real=(x*x+c*c-b*b)/(2*x*c*c)
    imaginary=delta/(2*np.abs(x)*c*c)
    density[active]=a*a*imaginary/(np.pi*((x-a*a*real)**2+(a*a*imaginary)**2))
    return density


def zero_field_cesaro_moments(g: float,h: float,j: float,maximum_order: int) -> np.ndarray:
    """Exact algebraic moment formula evaluated in float; central eta=0 only."""
    if not isinstance(maximum_order,int) or maximum_order<0:
        raise ValueError('maximum_order must be nonnegative')
    atoms=boundary_atoms(g,h,j)
    w,p=atoms.zero_weight,atoms.pair_weight_each
    powers=[]
    for m in range(maximum_order+1):
        powers.append(sum(comb(m,2*k)*w**(m-2*k)*p**(2*k)*comb(2*k,k)
                          for k in range(m//2+1)))
    moments=[]
    for ell in range(maximum_order+1):
        coefficients=Chebyshev.basis(ell).convert(kind=Polynomial).coef
        moments.append(float(np.dot(coefficients,powers[:len(coefficients)])))
    return np.asarray(moments)
