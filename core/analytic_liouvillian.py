"""Exact local Pauli-word recurrence for detector fluctuation moments.

This candidate derivation module is independent of all verifier code. It
does not compute or replace production QZ roots. Pauli sites start at zero;
an infinite-chain word has only finitely many nonidentity factors.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from typing import Literal

import sympy as sp

Word = tuple[tuple[int, int], ...]  # (site, axis); 1=X, 2=Y, 3=Z
Polynomial = dict[Word, sp.Expr]


@lru_cache(maxsize=None)
def pauli_product(left: Word, right: Word) -> tuple[sp.Expr, Word]:
    """Multiply canonical sparse Pauli words, retaining the exact phase."""
    factors = dict(left)
    phase = sp.S.One
    for site, axis in right:
        other = factors.get(site)
        if other is None:
            factors[site] = axis
        elif other == axis:
            del factors[site]
        else:
            phase *= sp.I if (other,axis) in ((1,2),(2,3),(3,1)) else -sp.I
            factors[site] = 6-other-axis
    return phase, tuple(sorted(factors.items()))


def liouvillian_moments(
    detector_field: tuple,
    nearest: tuple,
    second: tuple,
    *,
    maximum_even_order: int,
    topology: Literal['infinite', 'ring', 'chain'] = 'infinite',
    detector_n: int | None = None,
    observable: Literal['collective_x', 'endpoint_x'] = 'collective_x',
) -> tuple[sp.Expr, ...]:
    """Return mu_0,mu_2,... for the tracial Liouvillian spectral measure.

For rings/infinite chains, collective_x means the zero-momentum normalized
X fluctuation: mu_2k=sum_j tau(X_j ad_D^(2k)(X_0)). For an endpoint chain,
endpoint_x means tau(X_0 ad_D^(2k)(X_0)). Infinite recurrences do not truncate
the spatial support: only bonds overlapping the current word can contribute.
"""
    if maximum_even_order < 0 or maximum_even_order % 2:
        raise ValueError('maximum_even_order must be a nonnegative even integer')
    if topology not in ('infinite','ring','chain'):
        raise ValueError('unknown topology')
    if topology == 'infinite':
        if detector_n is not None:
            raise ValueError('infinite topology has no finite detector_n')
    elif not isinstance(detector_n,int) or detector_n < (5 if topology=='ring' else 1):
        raise ValueError('ring requires N>=5, endpoint chain N>=1')
    if ((observable == 'endpoint_x') != (topology == 'chain')):
        raise ValueError('endpoint_x is required only for finite endpoint chains')
    if observable not in ('collective_x','endpoint_x'):
        raise ValueError('unknown observable')
    coefficients=[]
    for vector in (detector_field,nearest,second):
        if len(vector)!=3:
            raise ValueError('fields and bonds must have three Pauli components')
        values=tuple(sp.sympify(value) for value in vector)
        if any(value.is_finite is False for value in values):
            raise ValueError('coefficients must be finite')
        coefficients.append(values)
    field,j1,j2=coefficients

    def terms_touching(word: Word):
        sites={site for site,_ in word}
        for site in sites:
            for axis,value in enumerate(field,1):
                if value != 0:
                    yield ((site,axis),),value
        for distance,strengths in ((1,j1),(2,j2)):
            starts=sites | {site-distance for site in sites}
            if topology=='ring':
                starts={site % detector_n for site in starts}
            elif topology=='chain':
                starts={site for site in starts if 0<=site<detector_n-distance}
            for site in starts:
                target=(site+distance)%detector_n if topology=='ring' else site+distance
                for axis,value in enumerate(strengths,1):
                    if value != 0:
                        yield tuple(sorted(((site,axis),(target,axis)))),value

    current: Polynomial={((0,1),): sp.S.One}
    moments=[]
    for order in range(maximum_even_order+1):
        if order%2==0:
            value=(sum(coefficient for word,coefficient in current.items()
                       if len(word)==1 and word[0][1]==1)
                   if observable=='collective_x' else current.get(((0,1),),sp.S.Zero))
            moments.append(sp.factor(value))
        if order==maximum_even_order:
            break
        following=defaultdict(lambda: sp.S.Zero)
        for word,coefficient in current.items():
            axes=dict(word)
            for term,strength in terms_touching(word):
                odd=sum(site in axes and axes[site]!=axis for site,axis in term)%2
                if odd:
                    phase,result=pauli_product(term,word)
                    following[result] += 2*phase*strength*coefficient
        current={word:sp.expand(value) for word,value in following.items() if value!=0}
    return tuple(moments)
