"""Independent exact Pauli construction; no production or candidate imports."""
from __future__ import annotations

from functools import reduce
from itertools import product

import sympy as sp

I2 = sp.eye(2)
X = sp.Matrix([[0, 1], [1, 0]])
Y = sp.Matrix([[0, -sp.I], [sp.I, 0]])
Z = sp.diag(1, -1)


def pauli(n: int, site: int, axis: int) -> sp.ImmutableSparseMatrix:
    factors = [I2] * (n + 1)
    factors[site] = (X, Y, Z)[axis]
    return sp.ImmutableSparseMatrix(reduce(sp.kronecker_product, factors))


def hamiltonian(n: int, family: str, fields: dict) -> sp.ImmutableSparseMatrix:
    """Positive Pauli coefficients; qubit first; ring N>=5, chain N>=1."""
    if family not in ('ring', 'chain') or n < (5 if family == 'ring' else 1):
        raise ValueError('unsupported family or detector size')
    ops = {(s, a): pauli(n, s, a) for s in range(n + 1) for a in range(3)}
    h = sp.zeros(2 ** (n + 1))
    for a in range(3):
        h += sp.sympify(fields['hq'][a]) * ops[0, a]
        for s in range(1, n + 1):
            h += sp.sympify(fields['hd'][a]) * ops[s, a]
        for distance, key in ((1, 'j1'), (2, 'j2')):
            pairs = ([(s, (s - 1 + distance) % n + 1) for s in range(1, n + 1)]
                     if family == 'ring' else [(s, s + distance) for s in range(1, n + 1 - distance)])
            for s, q in pairs:
                h += sp.sympify(fields[key][a]) * ops[s, a] * ops[q, a]
        scale = (n if a == 2 else sp.sqrt(n)) if family == 'ring' else 1
        for s in (range(1, n + 1) if family == 'ring' else (1,)):
            h += sp.sympify(fields['g'][a]) / scale * ops[0, a] * ops[s, a]
    return sp.ImmutableSparseMatrix(h)


def x_basis(n: int) -> sp.ImmutableMatrix:
    return sp.ImmutableMatrix(reduce(sp.kronecker_product,
                                    [sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)] * n))


def spins(n: int):
    return product((1, -1), repeat=n)
