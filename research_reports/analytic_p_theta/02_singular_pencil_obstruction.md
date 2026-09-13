# PROVED: the full-family observable is undefined at some allowed times

Frozen prediction, 2026-09-13: isotropic central-detector XY exchange has an
exact bright-state swap at t=pi/(4g), producing a singular homogeneous
production pencil. Strongest alternative: only ordinary infinite roots
occur, so a normalized 2^N-root measure remains defined. The discriminant
is whether det(beta C-alpha A) is the zero polynomial.

This is a domain obstruction to the arbitrary-coefficient/arbitrary-time
request, not a nonintegrability argument or a completed analytic solution.

## Endpoint chain, every N>=1

Set all fields/bonds and gz to zero and gx=gy=g!=0. The only interacting
spins are Q and detector 1; all other spins are spectators. With g=1,

    U_1(pi/4) = [[1,0,0,0], [0,0,-i,0], [0,-i,0,0], [0,0,0,1]],
    A = [[1,0],[0,0]], C = [[0,-i],[0,0]].

Thus det(beta C-alpha A)=0 identically. The stacked columns (A;C) still
form an isometry: unitarity does not imply regularity of the square pencil.
Every projective coordinate has a null vector, but there is no finite
algebraic 2-root multiset. Tensoring spectators preserves this singularity.

## Ring, every production size N>=5

Use exactly production scaling:

    H=(g/sqrt(N))(X_Q sum X_i + Y_Q sum Y_i).

Total Z charge is conserved. Let psi=|0>_Q |1...1>_D, and let phi be the
normalized state |1>_Q times the uniform superposition of detector strings
with one spin changed from 1 to 0. Pauli matrix elements give

    H psi=2g phi, H phi=2g psi.

Therefore A(t)|1...1>=cos(2gt)|1...1>, which vanishes at t=pi/(4g).
Charge conservation makes A block diagonal by detector charge, whereas C
strictly raises detector Z charge by two. Ordering detector basis by charge
makes beta C-alpha A block triangular. Its determinant is

    det(beta C-alpha A)=(-alpha)^(2^N) det A.

At the swap time det A=0, so again the whole homogeneous determinant is
identically zero. No spectrum of an exponentially large arbitrary matrix
is used in this proof. Negative g gives the same conclusion at the positive
time pi/(4|g|).

## No unique continuous extension even within the chain family

Allow independent gx,gy and set a=gx-gy, b=gx+gy. The two parity blocks
oscillate with frequencies a and b. Exactly,

    A=diag(cos(at),cos(bt)),
    C=[[0,-i sin(bt)],[-i sin(at),0]],
    det(beta C-alpha A)=alpha^2 cos(at)cos(bt)+beta^2 sin(at)sin(bt).

At gx=gy=1, t=pi/4 both coefficients vanish. Along a=0 and bt!=pi/2
approaching pi/2, the two regular roots are zero and the measure is delta_0.
Along bt=pi/2 and a!=0 approaching zero, the two regular roots are infinite
and the measure is delta_pi. Both paths converge to the same implemented
Hamiltonian and time. Consequently no continuous assignment of a root
measure exists there that agrees with all nearby regular cases.

PROVED: canonical P_N cannot be a probability measure for **every** allowed
finite N,t and coefficient choice under the production singular-root policy.
The verifier marks indeterminate roots; discarding or replacing them would
change the observable. A regular-domain characterization can still be
pursued. Neither this obstruction nor solved commuting subfamilies meet the
goal's six completion conditions. The goal remains OPEN; its universal
domain would need an explicit amendment before an everywhere-defined P can
be claimed.
