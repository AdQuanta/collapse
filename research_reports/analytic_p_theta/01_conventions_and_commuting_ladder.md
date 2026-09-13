# Analytic root measure: conventions and the commuting ladder

Date: 2026-09-13. Goal: `goal-analytic.md` supplied in the original checkout.
Source baseline: c7f3caa. This goal requests thermodynamic-first **Cesàro**
averaging, unlike the older instantaneous Born-phase objective. No change to
the human-owned goal or production observable is made.

## Canonical contract

The implementation, rather than older wiki coordinate formulas, is authoritative:

| Item | Convention | Source |
|---|---|---|
| Tensor order | Q, detector 1, ..., detector N; computational Z basis, central qubit first | `core/ring_chain_family.py`, `core/projective_roots.py` |
| Operators | Pauli eigenvalues ±1; positive Hamiltonian coefficient signs; U=exp(-iHt), hbar=1 | `core/ring_chain_family.py` |
| Sizes/bonds | ring N>=5, each distance-1/distance-2 forward periodic bond once; chain N>=1, open ends | `RingChainSpec`, `build_ring_chain_parts` |
| Ring edges | gx/sqrt(N), gy/sqrt(N), gz/N | `RingChainSpec.edge_couplings` |
| Chain edges | gx,gy,gz on Q--1 only | same |
| Root | Cv=lambda Av; beta C v=alpha A v; qubit ray (beta,alpha) | `core/relative_evolution_pencil.py` |
| Angle | theta=2 atan2(abs(alpha),abs(beta)) in [0,pi] | same |
| Multiplicity/P | each algebraic root carries weight 1/2^N; repeated roots retained | `core/projective_roots.py`, `core/born_phase_verifier.py` |
| Endpoints | (0,beta!=0) gives theta=0; (alpha!=0,0) gives theta=pi | same |
| Singular pencils | (0,0) is indeterminate, theta=NaN; never assign it a root angle | `core/relative_evolution_pencil.py` |
| R | P(theta)/(P(theta)+P(pi-theta)); histogram uses equal-width bins, zero pseudocount by default | `core/born.py:born_ratio_from_theta` |

For arbitrary measures mu, the same ratio is the Radon--Nikodym derivative
R=d mu/d(mu+S_*mu), S(theta)=pi-theta, defined (mu+S_*mu)-almost everywhere.
At an atom its value is mu{theta}/(mu{theta}+mu{pi-theta}). This is the
measure form of the existing ratio, not smoothing or reweighting. Production
histograms default to 1/2 in empty bins; that convention gives no density or
support there. Finite-resolution endpoint/bin-edge allocation remains the
production NumPy histogram convention, including the closed final bin.

Regular pencils have exactly 2^N homogeneous roots with algebraic
multiplicity. A singular pencil does not canonically have this finite root
multiset. Section 02 gives an implemented-family counterexample.

Root geometry is not an operational detector-preparation probability.

## Candidate and discriminating prediction, frozen before evaluation

Hypothesis: X-only detector fields and XX bonds have no effect on the
root measure in the X-coupled rung. Alternative: their phases change radii or
root weights. Prediction: exact X-sector reduction yields K_s I+v_s X_Q;
the common exp(-itK_s) factor cancels from the homogeneous root.

Use gx X_Q sum X_i/sqrt(N) for the ring and gx X_Q X_1 for the chain.
The first added coefficient is hx, then J1x. J2x and h0x are solved commuting
extensions **before** the transverse rung because they preserve precisely
the same reduction; this does not certify intervening noncommuting rungs.

## PROVED: finite N, arbitrary real t and coefficients on this rung

Let s=(s_1,...,s_N) in {+1,-1}^N and

    K_s = hx sum_i s_i + J1x sum_NN s_i s_j + J2x sum_NNN s_i s_j,
    v_s = a + gx sum_i s_i/sqrt(N)        (ring),
    v_s = a + gx s_1                      (chain), a=h0x.

Every X_i and X_Q is conserved. The N detector X eigenvalues resolve sectors
of dimension two. Translation (ring) is also conserved but is not required.
The product Hadamard transform diagonalizes detector X operators. Exactly,

    H|_s = K_s I_2 + v_s X,
    U|_s = exp(-it K_s) [cos(tv_s) I_2 - i sin(tv_s) X].

Therefore a homogeneous root representative is

    (alpha_s,beta_s)=(-i sin(tv_s),cos(tv_s)),
    theta_s=F(tv_s), F(u)=arccos(cos(2u)).

The identity with production atan2 holds including sin(u)=0 and cos(u)=0.
These two coordinates never vanish together: all these pencils are regular.
Each diagonal scalar factor is nonzero as a homogeneous polynomial, so their
product has exactly the asserted multiplicities even at degenerate roots.

The exact measures are

    mu_N^ring(t) = 2^(-N) sum_{k=0}^N binom(N,k)
                  delta_{F(t[a+gx(N-2k)/sqrt(N)])},
    mu_N^chain(t) = (delta_{F(t[a+gx])}+delta_{F(t[a-gx])})/2.

For a=0 the two chain atoms coincide. Uncoupled spectator degeneracy is
2^(N-1) per endpoint sign, and therefore the formula holds for every chain N.
K cancels even with nonzero XX bonds to the endpoint; no independence of
detector dynamics is being assumed.

Normalization follows from the binomial theorem or the two half weights.
Support is exactly the listed atoms after merging coincidences. All poles
retain their full weight. t=0 gives delta_0. F is continuous, even, pi-periodic,
and F(u+pi/2)=pi-F(u). Thus changing v to -v preserves theta; sign pairing
does **not** imply polar reflection symmetry. General finite-time measures
are not reflection symmetric. A simultaneous phase shift pi/2 reflects
them. Their reflected measures are simply the pushforwards by S.

Setting each newly introduced coefficient to zero recovers the preceding
Hamiltonian and propagator exactly. The independence of mu from hx,J1x,J2x
is an identity, not a weak-coupling approximation.

For integer ell>=0, cos(ell F(u))=cos(2 ell u). Hence the exact cosine moments
are

    m_ell^ring = cos(2 ell a t) cos(2 ell gx t/sqrt(N))^N,
    m_ell^chain = cos(2 ell a t) cos(2 ell gx t).

Polar reflection multiplies m_ell by (-1)^ell. Vanishing of all odd moments
is equivalent to reflection symmetry, because polynomials in cos(theta)
are dense in continuous functions on [0,pi]. No generic reflection symmetry
is claimed.

## PROVED: thermodynamic-first limit

Equal algebraic multiplicity gives the unbiased product law of the signs.
Its characteristic function is cos(u/sqrt(N))^N -> exp(-u^2/2): Taylor-expand
log cos near zero for each fixed u. The continuity theorem yields the
standard Gaussian G. Since F is continuous, for every fixed t

    mu_infinity^ring(t) = Law(F(t[a+gx G])).

This proves weak convergence on the compact polar interval, including t=0.
For gx*t !=0 the wrapped Gaussian is smooth and strictly positive. Its
folded density with respect to dtheta, not sphere area, is

    p(theta,t) = (1/pi)[1 + 2 sum_{ell>=1}
         exp(-2 ell^2 gx^2 t^2) cos(2 ell a t) cos(ell theta)].

The series converges absolutely and uniformly for every such fixed t.
It follows either by wrapping the Gaussian and folding, or by its cosine
moments and uniqueness of measures. Normalization is one. Support is the
entire interval; endpoint singleton masses vanish. For gx=0 or t=0 retain
delta_{F(at)} instead of using the density series.

The chain measure is independent of N, so its thermodynamic limit is exactly
the two-atom finite-N measure above. This is not a smooth limiting density.

## PROVED: infinite-time Cesàro averages after the N limit

If gx!=0, the ring's nonconstant cosine coefficients go to zero as t grows.
For any t>=t0>0, the Gaussian summable bound justifies uniform convergence
and gives p(theta,t)->1/pi. This implies the requested Cesàro average is
dtheta/pi. If gx=0 and a!=0, the periodic folded orbit also has uniform
Cesàro measure, by substituting u=at over complete periods. If gx=a=0,
the answer is delta_0.

For a chain define

    w0 = [1_{a+gx=0}+1_{a-gx=0}]/2.

Each nonzero frequency F(omega t) is periodic and its full-period average is
uniform: F maps the two half-period branches onto [0,pi] with slopes ±2.
Zero frequencies stay at theta=0. Linearity for two terms proves

    mu_bar_infinity^chain = w0 delta_0 + (1-w0) dtheta/pi.

There is no need to interchange thermodynamic and time limits: the first
was taken explicitly, and the subsequent integrations act on that measure.
Bounded continuous test functions control all averaging statements.

## PROVED: canonical R of the averaged measure

For both families with a=0 and gx!=0, R(theta)=1/2 throughout the interval
(up to null sets); the commuting detector coefficients do not change it.
For the ring with (a,gx)!=(0,0), the same result holds. The fully static
case delta_0 has R(0)=1 and R(pi)=0; off the two-atom reflected support R is
undefined, with production empty-bin display convention 1/2.

For chains, if w0=0 then R=1/2 almost everywhere. If 0<w0<1, R=1/2 on the
continuous interior, R(0)=1 and R(pi)=0 on the reflected atoms. If w0=1,
only those endpoint values are defined. Evaluating R after averaging is
essential; no average of instantaneous ratios is substituted.

## Verification boundary and next obstruction

All statements labelled PROVED above have explicit analytic arguments here.
The frozen SymPy verifier checks finite identities independently; it does
not promote the thermodynamic statements by numerical agreement. Evaluation
records are appended to `reports/analytic_p_theta/verifier_log.jsonl`.

Turning on a transverse detector field with XX detector interactions makes
the simple K cancellation fail: [sum X_i, sum Z_i]!=0. The next question is
whether the conditional detector unitaries admit an exact mode/transfer
representation controlling their **relative-unitary eigenphases**, rather
than only their separate energy spectra. Full XYZ/NNN/multichannel limits
remain OPEN. No claim of full-goal completion is made.
