# Exact noncommuting field slice, thermodynamic-first limits

2026-09-13. Candidate frozen before independent v2 evaluation.

Scope: central gx coupling only, zero central fields, zero detector bonds.
This is a **side branch** through rung 4 at J1x=J2x=0. It is not a solution
of the interacting transverse rung. It reduces to the commuting field rung
when the transverse field vanishes. Positive signs and production ring
scaling remain unchanged.

Hypothesis: a purely transverse field prevents unbounded collective phase
dispersion. Alternative: any nonzero coupling still gives a uniform polar
Cesàro law. Prediction: the exact relative-unitary phase has finite-time
variance proportional to sin²(ht), rather than t².

## PROVED: exact finite-N sector/product representation

Central X_Q is conserved. With epsilon=gx/sqrt(N) on the ring, the two
conditional detector Hamiltonians are sums of single-site terms

    h_± = h_vector dot sigma ± epsilon X,
    u_± = exp(-it h_±), U_± = u_± tensor ... tensor u_±.

On the chain, only detector 1 receives ±gx X; identical spectator unitaries
cancel from the relative unitary. Let W=U_-^dagger U_+. Then

    A=U_-(W+I)/2, C=U_-(W-I)/2.

W is unitary, so its eigenvalues give regular homogeneous roots
(alpha,beta)=(w-1,w+1). The two coordinates cannot vanish together.
Detector conjugations do not change the pencil roots. Rotate the detector
field around X to h_vector=(p,0,q), q>=0, with p=hx and q²=hy²+hz².

Define r_±=sqrt((p±epsilon)²+q²). The single-site relative unitary
w=u_-^dagger u_+ has determinant one, eigenvalues exp(±i phi), and

    cos(phi)=cos(r_+ t)cos(r_- t)
      + (p²+q²-epsilon²)/(r_+ r_-) sin(r_+ t)sin(r_- t), phi in [0,pi].

At r_±=0 use sin(r_± t)/r_±=t. This is a two-by-two Pauli identity, not
a formal spectral decomposition of the many-body Hamiltonian.

Let F(u)=arccos(cos(2u)). Then, exactly,

    mu_N^ring(t)=2^(-N) sum_{k=0}^N binom(N,k) delta_{F((N-2k)phi_N(t)/2)},
    mu_N^chain(t)=delta_{phi_gx(t)}.

Both signs of each chain eigenphase map to the same angle. Degeneracies,
zero and infinite roots are retained. Normalization is binomial/two-root
counting; support is exactly the listed atoms. In particular, finite-time
reflection symmetry is not general. Reflection changes the signs of odd
cosine moments. The ring moments are cos(ell phi_N)^N, and the chain moments
are cos(ell phi_gx). Setting q=0 recovers the X-only field cancellation;
setting all detector fields to zero recovers report 01's minimal rung.

## PROVED: ring thermodynamic limit at every fixed t

Write h=sqrt(p²+q²). The independent small-epsilon expansion is

    cos(phi)=1-2 epsilon² B(t)²+O(epsilon^4),
    B(t)²=(p²/h²)t²+(q²/h^4)sin²(ht), h>0,
    B(t)²=t², h=0.

One derivation is first-order interaction-picture perturbation of w:
the vector integral of the rotated X axis has parallel length pt/h and
transverse squared length q² sin²(ht)/h^4. An independent check takes the
second epsilon derivative of the exact SU2 trace. The remainder is at
fixed t; no uniform-in-time approximation is assumed.

For every fixed integer ell, the Chebyshev identity yields

    cos(ell phi_N)^N -> exp(-2 ell² gx² B(t)²).

Indeed cos(ell phi)=1-ell²(1-cos(phi))+O((1-cos(phi))²). If B(t)=0 the
same expansion gives a limit of one, including exact refocusing times.
These moments determine a unique measure on [0,pi], and tightness is
automatic on that compact interval. Equivalently the limiting measure is

    mu_infinity^ring(t)=Law(F(gx B(t) G)), G standard Gaussian.

For gx B(t)!=0 the density is report 01's wrapped Gaussian with variance
gx² B(t)². For gx B(t)=0 it is delta_0. This resolves the thermodynamic
limit before considering large time. No CLT for a nonnormal pencil is
being assumed: the reduction to a normal relative unitary is exact here.

## PROVED: ring Cesàro average and canonical R

If gx=0 the measure stays delta_0. For gx!=0 and p!=0, B(t) grows at least
|p|t/h, and all nonconstant cosine moments vanish. The weak limiting and
Cesàro measures are dtheta/pi, with R=1/2. This includes q=0 and extends
the earlier parallel-field rung. If h=0 the same result follows from B=t.

For a purely transverse nonzero field $p=0,q=h>0$, B(t)=|sin(ht)|/h.
The limiting measure is periodic, with exact delta_0 refocusing times of
zero time measure. Put rho=|gx|/h. Its Cesàro average is exactly

    mu_bar = $1/pi$ integral_0^pi Law(F(rho sin(u) G)) du.

This mixture is a probability measure. Every non-refocusing constituent
is absolutely continuous, so Tonelli proves the mixture is absolutely
continuous too: there is **no** surviving atom at theta=0. Its density is
the same integral of the wrapped-Gaussian densities (defined almost
everywhere). It is positive on $0,pi$ and has full support. Its cosine
moments are

    c_ell = $1/pi$ integral_0^pi exp(-2 ell² rho² sin²(u)) du
          = exp(-ell² rho²) I_0(ell² rho²), ell>=0,

where I_0(x)=(1/pi) integral_0^pi exp(x cos(v)) dv. The last equality is a
substitution using sin²(u)=(1-cos(2u))/2 and periodicity. In particular
c_0=1 and c_1>0, so the measure is not reflection symmetric or uniform.

An exact canonical R is

    R(theta)=p_bar(theta)/(p_bar(theta)+p_bar(pi-theta)), 0<theta<pi,

with p_bar given by the positive one-dimensional mixture above. Equivalently
its cosine series has coefficients c_ell; that series need not converge
absolutely and is not used to exchange sums at the refocusing singularity.
The positive density integral is the defining formula. The density diverges
logarithmically at theta=0: near u=0,pi its central Gaussian term integrates
u^(-1) exp[-theta²/(8 rho² u²)]. Away from theta=0 all wrapped images are
integrably suppressed as u tends to a refocusing point. Hence p_bar(pi) is
finite and positive, but endpoint singleton masses remain zero.

The exact long-time answer is discontinuous at p=0 as a parameter limit:
any fixed p!=0 gives the uniform measure, whereas p=0 gives this nonuniform
mixture. Finite-time dependence remains continuous. This is a concrete
reason to respect the specified order of limits.

## PROVED: chain transverse-field limit, average and R

The chain measure is already independent of N. For p=0, h=q, define
omega=sqrt(h²+gx²), k=gx²/(h²+gx²). The exact trace simplifies to

    theta(t)=2 asin(sqrt(k)*abs(sin(omega t))).

If gx=0 the law is delta_0, including omega=0. For gx!=0 the time-averaged
variable z=sin²(theta/2) has the arcsine density on $0,k$. The polar density is

    p_k(theta)=cos(theta/2)/(pi sqrt(k-sin²(theta/2))),
    0<theta<theta_max=2 asin(sqrt(k)),

and zero outside this interval. It integrates to one by z=k sin²(u).
There are no atoms. For k=1 this reduces to the uniform 1/pi density on
$0,pi$, recovering h=0. For 0<k<1 the upper edge singularity is integrable.

Set p_k to zero off its support and compute

    R(theta)=p_k(theta)/(p_k(theta)+p_k(pi-theta))

where the denominator is nonzero. With theta_max<pi/2, a central interval
has no reflected support and R is undefined there (production empty-bin
display: 1/2). On support belonging only to the original measure R=1;
on only reflected support R=0. The overlap uses the explicit density ratio.
These are cap-supported root statistics, not measurement probabilities.

## OPEN boundary

Nonzero J1x together with a transverse detector field destroys the
single-site product representation: conditional H_± contain both a
transverse field and a longitudinal ±gx field in the interacting Ising
chain/ring. The separately solvable transverse-field Ising model at gx=0
does not solve the required two conditional propagators at gx!=0. A
controlled relative-propagator representation is still required. The
full interacting XYZ family and requested limits remain OPEN.
