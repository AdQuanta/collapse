# PROVED: uniform ordered time average for almost every central X field

2026-09-13. For each fixed choice of **all detector fields and NN/NNN XYZ
interactions**, and fixed gx, both central-X endpoint chains and central-X
rings have

    lim_(T→infinity) (1/T) integral_0^T P_infinity(dtheta,t)dt = dtheta/pi

for Lebesgue-almost every h0x. Consequently their canonical R is 1/2
almost everywhere on [0,pi]. The N limit is taken first. This does not
require integrability, mixing, a finite frequency measure, or the total-
variation hypothesis of report 09.

The exceptional set may depend on the fixed detector parameters. The
theorem does not identify that set, does not cover every nonzero h0x,
and does not settle the additional central coupling axes or non-X central
fields. The full arbitrary-parameter goal remains **OPEN**.

## 1. The remaining scalar field gives an exact modulation

Continue the existing central-X family, without removing any detector term:

    H_N(a)=D_N+X_Q(a+gF_N), a=h0x,
    F_N=X_1 (chain), or sum_j X_j/sqrt(N) (ring, N>=5).

Only the central gx coupling and h0x field are present; detector fields and
NN/NNN XYZ coefficients are arbitrary real fixed values. All production
Pauli, open/periodic boundary, tensor ordering and homogeneous-root
conventions remain as in report 01.

Because a is scalar within each conditional sector,

    U_±,a(t)=exp(∓iat) U_±,0(t),
    W_N,a(t)=exp(-2iat) W_N,0(t).

Writing c_ell,N(t)=tau_N(W_N,0(t)^ell), every polar moment is exactly

    m_ell,N,a(t)=Re[exp(-2i ell a t)c_ell,N(t)], ell>=1.

Do not replace this by cos(2 ell a t) Re c unless reality of c has been
proved. The argument below allows arbitrary complex c. Unitarity gives
|c_ell,N(t)|<=1.

Reports 05 and 07 establish the fixed-time thermodynamic root/echo-moment
limits in these two families. In particular c_ell,N(t) has a bounded,
continuous limit c_ell(t). For chains this follows from norm convergence
of W; for rings the relative-unitary trace-moment limit is given by the
proved fluctuation theorem. Therefore, **before any time averaging**,

    m_ell,infinity,a(t)=Re[exp(-2i ell a t)c_ell(t)].

The central-field modulation commutes with this fixed-time limit because
it is an N-independent scalar. No finite-N Cesàro limit is used.

## 2. Bounded-signal modulation lemma

**PROVED.** Let f:[0,infinity)→C be measurable with |f|<=1. Then for
Lebesgue-almost every real omega,

    A_T(omega)=(1/T) integral_0^T f(t)exp(-i omega t)dt → 0

as real T→infinity, not just along a subsequence.

Proof. With Fourier convention fhat(omega)=integral exp(-i omega t)f(t)dt,
Plancherel applied to f 1_[0,T] gives

    integral_R |A_T(omega)|² domega
       = (2pi/T²) integral_0^T |f(t)|²dt <= 2pi/T.

Take T_n=n². Tonelli's theorem yields

    integral_R sum_(n>=1) |A_(n²)(omega)|² domega
       <= 2pi sum_(n>=1) n^(-2) < infinity.

Hence A_(n²)(omega)→0 outside a Lebesgue-null set. For n²<=T<(n+1)²,
boundedness of f gives uniformly in omega

    |A_T(omega)-A_(n²)(omega)|
       <= 2(T-n²)/T
       <= 2(2n+1)/n² → 0.

This fills every gap between subsequence times and proves the full limit.
There is no assumption about existence of an unmodulated mean of f.

The only harmonic-analysis input is the standard L2 Plancherel identity;
the summable-time and interpolation argument is given in full here.
For background on that identity, see the University of Kentucky
[harmonic analysis lecture notes](https://www.ms.uky.edu/~rbrown/courses/ma773/notes.pdf),
Theorem 3.2. Constants above use the explicitly stated Fourier convention.

## 3. All moments at once, then the actual probability measure

Apply the lemma to f=c_ell for each positive integer ell. Scaling
omega=2 ell a preserves Lebesgue-null sets. Let E_ell be the exceptional
set of a for that moment and E=union_(ell>=1) E_ell. This countable union
is null. For every fixed a outside E, **all** averaged cosine moments
exist and vanish:

    b_ell(a)=lim_(T→infinity) (1/T) integral_0^T
                m_ell,infinity,a(t)dt = 0, ell>=1.

The moment of order zero is one. The time-averaged probability measures
on [0,pi] are tight by compactness. Each weak subsequential limit has
exactly these moments. Polynomials in cos(theta) are uniformly dense in
C([0,pi]), so these are precisely the moments of dtheta/pi and uniquely
determine it. It follows that the entire Cesàro family converges weakly.

This proves normalization, full polar support, reflection invariance,
absence of surviving atoms, and the density 1/pi in the stated a.e.-field
scope. The density is with respect to dtheta, not sphere area. The canonical
ratio is computed after averaging:

    R=dmu/d(mu+S_*mu)=1/2, S(theta)=pi-theta.

No observable was averaged over a field distribution. Integration over a
appears only inside the proof that almost every **fixed** field works.
No operational measurement-probability interpretation is asserted.

## 4. A useful finite-time bound, and its precise quantifiers

Let B_ell,T(a)=(1/T) integral_0^T exp(-2i ell a t)c_ell(t)dt. A change
of Fourier variable gives the exact bound

    integral_R |B_ell,T(a)|² da <= pi/(ell T).

Consequently the Lebesgue measure of central fields for which any of the
first L averaged cosine moments exceeds epsilon in magnitude is at most

    pi H_L/(T epsilon²), H_L=sum_(ell=1)^L 1/ell.

This bound also holds for the measure of that set inside any finite field
interval. It is uniform in the fixed detector coefficients and gx because
only |c_ell|<=1 was used. It is a measure bound over fields, not a
pointwise convergence rate for a prescribed field, and it is not a
finite-N convergence estimate.

For each fixed detector/coupling vector, the exceptional field set is null.
The fixed-time moments depend continuously on finite coefficients by
local dynamics (or the ring moment construction); the limit events are
measurable using rational times. Fubini on bounded parameter boxes thus
also gives a Lebesgue-a.e. statement jointly in those coefficients and a
within the central-X family. It does not produce a single exceptional
set that works simultaneously for every detector, nor an open region on
which every parameter point is covered.

## 5. Exact exceptions and zero-coefficient reductions must remain

The finite-N conditional-unitary formulas are unchanged, so all earlier
coefficient-zero reductions still hold exactly. The a.e. theorem must be
restricted to the surviving coefficient slice again; a null exceptional
set in a larger parameter space says nothing about a chosen slice.

1. In the commuting chain, the exact previous law is
   w0 delta_0+(1-w0)dtheta/pi, with
   w0=(1_(a+g=0)+1_(a-g=0))/2. It is uniform for a!=±g,
   but at a=g!=0 it has half its mass at theta=0. This is a genuine
   nonzero-field exception within the implemented family, at every N.
2. With g=0, a!=0 gives the uniform orbit average; a=0 gives delta_0.
3. For the allowed one-pixel control g=hz=1, let u=sqrt(2)t. At a=0,
   c_1=cos²u and c_2=2cos⁴u-1. At the nonzero field a=sqrt(2)/2,
   the exact averages are b_1=0 and b_2=1/2. Thus checking the first
   moment alone, or merely requiring a!=0, would falsely assert uniformity.
   Here averages may be evaluated over u∈[0,2pi].

The two scalar controls are checks of the theorem's exceptions, not a
return to the Majorana benchmark. Finite-volume resonances are not used
to guess the thermodynamic exceptional set.

## 6. Decision and remaining full-goal gaps

PROMOTE the a.e.-central-field theorem for both central-X families. It
controls every moment and the actual ordered limiting probability law,
including R, while retaining all detector coefficients. The global
frequency-variation criterion from report 09 is unnecessary for this
a.e.-field result; it remains one possible sufficient condition at an
exceptional fixed field.

**OPEN:** prescribed exceptional fields, especially h0x=0 for generic
interacting chains; additional central coupling axes and non-X central
fields; and the singular-pencil domain already identified in report 02.
The goal requests arbitrary coefficients, so an almost-everywhere theorem
cannot be marked as full completion. The next task is to characterize the
exceptional fixed-field contribution or cross the next central-axis
obstruction, rather than spend more work on global total variation.

Finite sector/modulation identities are supported by frozen v5. The new
scalar averaging and resonance controls are isolated in frozen v6; that
checker cannot prove the measure-theoretic lemma. The proof above, not
numerical sampling of central fields, establishes the a.e. statement.
