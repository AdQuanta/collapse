# Exact asymptotic Born law: proved obstructions and the remaining problem

11 September 2026. **Partial analytical resolution; the full goal is OPEN.**
The finite acceptance gate is unchanged. The theorems here concern the native
equal-algebraic-root measure, not operational outcome probabilities.

**Continuation, 12 September 2026:**
[BORN_NONNORMAL_LIMIT.md](BORN_NONNORMAL_LIMIT.md) proves an exact scalar
determinant-potential criterion for weak polar-root convergence and a native
exchange counterexample to replacing noncommuting roots by a Gaussian
trace-moment limit. These results constrain the next thermodynamic argument;
they do not close the full-model Born phase question.

## 1. The theorems

**Theorem A (recurrence, all finite native Hamiltonians).** For every finite
Hermitian H and every eta>0 there are arbitrarily late times at which all
production projective roots satisfy theta<eta. Thus any ordinary long-time
weak root-measure limit is delta_0. If a regular time has a different root
measure, that long-time limit does not exist. For any sequence H_N there
are joint sequences N,t_N->infinity with root measures tending to delta_0.
Consequently a joint root-measure limit with continuous full angular support
cannot be independent of all late-time subsequences.

**Theorem B (commuting conditional dynamics).** Let

\[
H_N=I\otimes K_N-X_q\otimes(V_N+h_N I),\qquad [K_N,V_N]=0.
\]

Suppose the root measures have a weak N-first limit at every t>0, followed
by an ordinary weak long-time limit. That final measure necessarily is

\[
P_*=L\delta_0+(1-L)\,d\theta/\pi,\qquad 0\le L\le1.
\]

It obeys the exact Born reflection identity only for L=1. Thus **no member
of this entire commuting class has a continuous, fully supported exact
Born long-time limit**. No hypothesis about graph, spectral gaps, degeneracy,
randomness, coupling scaling, or absolute continuity is needed beyond the
stated existence of the two limits. This class contains the zero-central-
detuning construction in the pre-existing workspace study
`BORN_LIKE_CONSTRUCTIVE_FAMILY.md` (uncommitted when this analysis began).

**Theorem C (central-X field obstruction, without [K,V]=0).** Fix any
sequence of detector Hermitian pairs K_N,V_N and consider

\[
H_N(h)=I\otimes K_N-X_q\otimes(V_N+hI).
\]

Let E be a measurable set of fields for which the first Born residual has
an N-first limit for each t>0 and that limit tends to zero as t->infinity.
Then E has Lebesgue measure zero. In particular a robust exact-Born phase
cannot contain a field interval in this X-conserving class. This applies
to noncommuting, interacting, disordered detectors too. Changing h costs
exactly |delta h| in full-Hamiltonian operator norm, independently of N.

**Theorem D (explicit native thermodynamic control).** For V_N equal to
g/sqrt(N) sum_i X_i, g!=0, h_N=0, and any commuting K_N, the N-first root
density is a folded wrapped Gaussian. At late times it converges uniformly
to 1/pi and its reflected response converges uniformly to 1/2. It does
not converge to Born. Its finite-size and late-time corrections are given
below, without fitting their form.

**Theorem E (detuned commuting, light spectral tails).** Let
H_N=I K_N-X_q(V_N+hI)-b Z_q I with [K_N,V_N]=0 and b!=0. Suppose the
normalized counting laws of u=V_N+h converge weakly to an absolutely
continuous probability law with finite third absolute moment. Then the
N-first root measure has an ordinary weak long-time limit, but that limit
does not obey exact Born. In particular this excludes collective
g/sqrt(N) X couplings with any fixed central-X field and nonzero central-Z
detuning. More generally every tight convergent sequence of native linear-X
coupling spectra has sub-Gaussian tails; if its limit is absolutely
continuous, Theorem E applies. The proof is in section 8.

These results **do not prove** that a robust phase is impossible in the
full native model: nonzero central-Z field, central YY, ZZ or ZX interactions
can break X conservation. A lower-dimensional excluded class is not a
dense obstruction in that larger parameter space. No positive theorem or
full-model no-go is claimed.

## 2. Asymptotic object and order of limits

Use hbar=1 and Pauli eigenvalues +/-1. Site zero is the first tensor factor,
and U_N=exp(-itH_N) has blocks (A,B;C,D). On a regular pencil define

\[
\mu_{N,t}=2^{-N}\sum_{j=1}^{2^N}\delta_{\theta_j},\qquad
\theta_j=2\operatorname{atan2}(|\alpha_j|,|\beta_j|),
\quad \beta_j C v_j=\alpha_j A v_j.
\]

Keep multiplicities, zero roots and infinite roots. Indeterminate pencils
do not define this probability measure. The production QZ audit detects
numerical indeterminacy; a finite numerical regularity check is not a proof
for every time. See `core/relative_evolution_pencil.py` and
`core/projective_roots.py`. The source of propagator blocks is
`core/analysis.py::evolution_subblocks_from_eigenbasis`. Its qubit kets are
derived from roots, not drawn from an input preparation density matrix.
Native operator signs and exchange normalization were checked in both
`core/hamiltonians/numpy_hamiltonians.py` and `quspin_hamiltonians.py`.

Weak convergence of probability measures on [0,pi] is the natural first
topology: it is equivalent to convergence of all cosine moments. Finite
atomic measures cannot converge in total variation to a continuous law.
Write S(theta)=pi-theta and define the continuum response as the
Radon--Nikodym derivative dP/d(P+S_*P). To assert equality Lebesgue-a.e.
on the entire open interval also require its reference measure to have a
density positive Lebesgue-a.e.; mere topological full support is weaker.

Weak root convergence alone does **not** give response convergence. For
example p_j=(1+epsilon cos((2j+1)theta))/pi converges weakly to 1/pi,
but R_j=1/2+(epsilon/2)cos((2j+1)theta) has a nonvanishing L2 oscillation.
Theorem D proves uniform convergence of densities and a positive denominator,
so it establishes uniform response convergence as well. More general positive
claims will need comparable denominator control, not just moment convergence.

Theorem A prevents reversing the limits for nonconstant finite root dynamics.
Theorem D supplies a family in which the N-first iterated limit exists but
the t-first inner limit fails. The two orders therefore cannot be declared
commuting in the model. Theorem A also prohibits a continuous-support joint
limit independent of all t_N. A physically restricted joint window would need
an explicitly proved N-dependent time bound. The finite 64/100-bin gate is
kept for verification; it is not used to define a continuous limiting density.

The repository admits different size scalings and graph sequences; these
do not specify one common thermodynamic theory. The general existence of an
N-first limit for arbitrary native noncommuting sequences remains unproved.

## 3. Minimal effective objects

For general H the regular projected pencil determines the root multiset.
Its normalized radial projective measure, including endpoint masses, already
determines the polar response; azimuth and detector eigenvectors of that
pencil are unnecessary for this statistic. A detector-state quantum channel
does not replace this equal-root measure.

When [H,X_q]=0, write U_+=exp(-it(K-V)) and U_-=exp(-it(K+V)). Then

\[
A=(U_++U_-)/2=U_+(I+W)/2,\qquad
C=(U_+-U_-)/2=U_+(I-W)/2,\quad W=U_+^\dagger U_-.
\]

The common invertible factor cancels in the homogeneous pencil. Since W
is unitary, its eigenvalues w=exp(i phi) give lambda=(1-w)/(1+w)
=-i tan(phi/2) and theta=|wrap(phi)|. At w=-1 this statement uses
the homogeneous pair (1-w,1+w), so it includes infinite roots. There are
no indeterminate pairs. Consequently

\[
a_n(N,t)=\operatorname{Re}\tau_N(W_N(t)^n),\qquad \tau_N=2^{-N}\operatorname{tr}.
\]

This normalized phase-trace hierarchy is an independent effective-dynamics
test of necessary moment conditions without histogram construction. When
[K,V]=0, W=exp(-2itV), so only the counting spectral law of V matters.

## 4. Exact geometric condition and its present limitation

For any polar probability measure the Born response identity is equivalent to

\[
P=(1+\cos\theta)E,\qquad S_*E=E,\qquad E=(P+S_*P)/2.
\]

On 0<r<infinity it is also equivalent to invariance, under r->1/r, of
the tilted radial measure r Q(dr). South-pole mass must vanish; an unpaired
north-pole atom is allowed. The tilt is finite for a Born measure, since
r/(1+r^2) is bounded. Equivalently every Born residual

\[
d_m=2a_{2m+1}-a_{2m}-a_{2m+2}
\]

vanishes. In the X-conserving class a_n=Re tau(W^n) makes these testable
directly from effective dynamics. A finite prefix is never sufficient.

These are exact **geometric equivalents**, not a newly established microscopic
condition C_B. The objective explicitly excludes an equivalent restatement
as its final structural answer. We therefore do not rename the tilt symmetry
or the existing moment hierarchy as a completed solution to that requirement.
Finding an independently predictive condition for the full model remains OPEN.

## 5. Sufficiency of the geometric equivalent

If P=(1+cos theta)E with E symmetric, its reflection is (1-cos theta)E,
and P+S_*P=2E. The derivative dP/d(2E)=(1+cos theta)/2 is Born.
This proof includes atoms and needs no density or finite-bin approximation.
For the radial tilt version, let M=rQ and I(r)=1/r. If I_*M=M then
I_*Q=r^2 Q, so Q/(Q+I_*Q)=1/(1+r^2). Endpoints require the separate
mass conditions stated above. None of these steps proves microscopic
realizability or stability in time.

## 6. Necessity of the geometric equivalent

If dP/d(P+S_*P)=B, multiply by its reference measure and set
E=(P+S_*P)/2. Reflection symmetry of E follows by construction, and
P=(1+cos theta)E. In radius coordinates the same derivative yields
I_*Q=r^2 Q. Therefore I_*(rQ)=(1/r)I_*Q=rQ.

For the hierarchy, decompose P into its reflection-even and odd parts.
Testing the odd part minus cos(theta)E against cos((2m+1)theta) gives
d_m/2 using the cosine product identity. Its even tests vanish by parity.
Cosine polynomials are dense in continuous functions on [0,pi]: substitute
z=cos(theta) and approximate continuous functions of z by polynomials.
All residuals vanishing therefore implies the equality of signed measures.

In particular d_0 is necessary. Quantitatively
d_0=2 integral cos(theta)[R-B] d(P+S_*P), so |d_0|<=4||R-B||_infinity.
This explains why failure of this single moment can disprove a uniform
Born limit even though success of finitely many moments cannot prove one.

## 7. Reciprocal geometry and all Jacobians

For a planar root density f(lambda) relative to area d^2lambda, write
lambda=r exp(i phi). The area element is r dr dphi and the radial density
is q(r)=r integral_0^{2pi} f(r exp(i phi)) dphi. With x=log r,

\[
\frac{d\theta}{dr}=\frac{2}{1+r^2},\quad
\frac{dr}{dx}=r,\quad
P_\theta(2\arctan r)=\frac{1+r^2}{2}q(r),\quad
\ell(x)=e^x q(e^x).
\]

Reflection theta->pi-theta has absolute Jacobian one, whereas radial
inversion has |d(1/r)/dr|=r^-2. Thus

\[
R(2\arctan r)=\frac{q(r)}{q(r)+q(1/r)/r^2}
=\frac1{1+r^2}
\iff q(1/r)=r^4q(r).
\]

In logarithmic coordinates this becomes ell(-x)=exp(2x)ell(x), or evenness
of exp(x)ell(x). An atom obeys Q({1/r})=r^2 Q({r}); the density Jacobian
r^-2 must **not** be applied to point masses.

Planar inversion lambda->1/conjugate(lambda) has absolute area Jacobian
r^-4. A full planar covariance I_*mu=r^2 mu would require
f(1/conjugate(lambda))=r^6 f(lambda). That condition is sufficient but
stronger than polar Born: polar Born constrains only the angular integral
of f. The transformations 1/lambda and -1/conjugate(lambda) respectively
reverse azimuth and shift it by pi; their absolute area Jacobians agree.
There is no justification for imposing angular covariance from radial data.
For the meridional X-conserving roots no planar density exists; use Q directly.

## 8. Recurrence and long-time proofs

### Proof of Theorem A

In finite dimension the phases exp(-itE_j) admit arbitrarily late simultaneous
returns to one. One elementary construction samples integer times in the
compact phase torus: pigeonholing finer finite partitions gives return
differences. If these differences remain bounded while their error tends to
zero, an exact integer period exists, whose multiples give late returns;
otherwise an unbounded subsequence supplies them directly.

Choose a return with ||U-I||_2<=epsilon<1. Its blocks obey
||A-I||<=epsilon, ||C||<=epsilon, so A is invertible and

\[
|\lambda_j|\le\|A^{-1}C\|\le\frac{\epsilon}{1-\epsilon},\qquad
\theta_j\le2\arctan\frac{\epsilon}{1-\epsilon}.
\]

No diagonalizability assumption about A^-1 C enters. Returns with epsilon->0
therefore force mu->delta_0. For any regular time s, U(t_k+s)->U(s), and
roots of a regular homogeneous determinant polynomial converge as a multiset
on the projective sphere. If mu_s!=delta_0 this gives a second accumulation
measure, contradicting a long-time limit. For each N choose a return t_N>N
with epsilon_N->0 to obtain the joint obstruction. At these times every
interior fixed histogram bin is empty for sufficiently large N. A filled
default value in the software does not turn missing support into a Born law.

This argument does not assert that every coarse finite histogram changes
in time: a coarse bin can conceal moving roots. It concerns the full root
measure and the requested continuous-support limit. The pole measure itself
obeys a supported Born identity, which is why the coverage qualification matters.

### Proof of Theorem B

Cancellation of K gives a_n(N,t)=tau_N cos(2nt(V_N+h_N)), hence the exact
identity a_n(N,t)=a_1(N,nt) for every integer n>=1. Passing to the stated
N-first and then long-time limits shows all nonzero limiting cosine moments
equal one number L. The unique finite signed measure with these moments and
zeroth moment one is L delta_0+(1-L)dtheta/pi. Uniqueness follows from the
cosine-polynomial argument in section 6. Positivity of the actual limit gives
0<=L<=1. The necessary Born residual is d_0=L-1, so L=1 is the only Born
possibility. No time averaging, dephasing assumption, or favorable sequence
was used. The case of nonexistent limits does not provide a positive phase.

### Proof of Theorem D and correction laws

Independent counting of the detector X signs gives, exactly,

\[
a_n(N,t)=\cos(2ngt/\sqrt N)^N
\longrightarrow e^{-2n^2g^2t^2}.
\]

Compactness and moment uniqueness prove weak N-first convergence at every
t. For t>0 the limiting moments give the uniformly convergent series

\[
p_t(\theta)=\frac1\pi\left[1+2\sum_{n\ge1}
e^{-2n^2g^2t^2}\cos(n\theta)\right].
\]

It is the folded wrapped Gaussian, with an everywhere positive density
also obtained by summing Gaussian images of variance 4g^2t^2. Set
q=exp(-2g^2t^2). Since n^2>=n,

\[
\|p_t-1/\pi\|_\infty\le\frac{2q}{\pi(1-q)},\qquad
\|R_t-1/2\|_\infty\le\frac{q}{1-3q}\quad(q<1/3).
\]

The bounds hold at **every** sufficiently late time and decrease with t,
so they prove a strong tail limit. Consequently ||R_t-B||_infinity->1/2
and its uniform-angular RMS tends to 1/sqrt(8). Every fixed Born residual
tends to -1 for m=0 and zero for m>=1; checking the maximum still detects
failure. The first residual is exactly 2q-1-q^4.

For fixed n,t, expanding log cos x=-x^2/2-x^4/12+O(x^6) gives

\[
\log a_n(N,t)=-2n^2g^2t^2-
\frac{4n^4g^4t^4}{3N}+O(n^6g^6t^6/N^2).
\]

This is an asymptotic expansion on the small-phase branch, not a uniform
statement over all late times. For fixed n, relative leading-order agreement
holds in the sufficient window t=o(N^(1/4)); no universal window is claimed.
At t_N=pi sqrt(N)/|g|, all roots are exactly at zero, whereas the N-first
late-time limit is uniform. The finite-size law therefore must not be
extrapolated to recurrence scales. Commuting K can change the full-unitary
recurrence time without changing this exact pencil recurrence.

### Proof of Theorem E: detuning imposes a tail requirement

For each conditional eigenvalue u and Omega=sqrt(u^2+b^2), the homogeneous
root is alpha=i u sin(t Omega)/Omega,
beta=cos(t Omega)+i b sin(t Omega)/Omega. Its squared projective population

\[
x=\sin^2(\theta/2)=k(u)\sin^2(t\Omega(u)),\qquad
k(u)=\frac{u^2}{u^2+b^2}
\]

is continuous in u for every finite t. Weak convergence of the u law
therefore proves the N-first root-measure limit by testing continuous
functions on [0,1]. This is the same conditional-qubit block and sign
convention as the native finite construction, with no replacement of roots
by singular values.

There is an ordinary instantaneous weak long-time limit, obtained as
follows. For any continuous test F, uniformly approximate the continuous
function F(k sin^2(phi)) on [0,1] times the phase circle by finite sums of
polynomials in k times exp(2im phi). The pushforward of an absolutely
continuous u law under Omega=sqrt(u^2+b^2) has an L1 density on
[|b|,infinity). The inverse derivative at |b| is integrably singular and
introduces no atom. Multiplying by a bounded polynomial of k preserves L1.
Every nonzero m term thus tends to zero by the oscillatory-integral
argument of section 9, now on the frequency variable. The zero mode remains.
Uniform approximation controls the error at all times. This proves weak
convergence at every sufficiently late time, not just after a time average.

The resulting x law is a mixture of the exact arcsine kernels

\[
f_{x\mid k}(x)=\frac{\mathbf1_{0<x<k}}{\pi\sqrt{x(k-x)}}.
\]

Since the absolutely continuous u law is nontrivial, there is k0>0 and
positive mass m0 with k>=k0. For epsilon<k0, its limiting x density
therefore satisfies f_x(x)>=m0/(pi sqrt(x)) on 0<x<epsilon.

Under exact Born, reflection is x->1-x and
d(S_*P_x)=x/(1-x)dP_x. Applying this identity to [epsilon/2,epsilon]
would force

\[
P_x([1-\epsilon,1-\epsilon/2])\ge
\frac{2m_0}{3\pi}\left(1-2^{-3/2}\right)\epsilon^{3/2}.
\]

But x<=k implies

\[
P_x([1-\epsilon,1])\le
\Pr\!\left\{|u|\ge |b|\sqrt{\frac{1-\epsilon}{\epsilon}}\right\}
=o(\epsilon^{3/2}).
\]

The last equality follows from finite E|u|^3: R^3 Pr(|u|>=R)
is bounded by the third-moment tail integral, which tends to zero.
The two inequalities contradict each other. Thus any Born law generated
by this phase-mixed conditional mechanism would require an infinite third
absolute coupling moment. This is a restricted microscopic necessity, not
a necessity for the general noncommuting model.

For native V_N=sum_i g_(N,i) X_i, counting its spectrum is exactly a
Rademacher sum. Put sigma_N^2=sum_i g_(N,i)^2. Its fourth moment is at
most 3 sigma_N^4. Cauchy--Schwarz on the event V_N^2>sigma_N^2/2 gives
Pr(|V_N|>sigma_N/sqrt(2))>=1/12. Tightness therefore forces sigma_N
to remain bounded. Moreover E exp(s V_N)=product_i cosh(s g_(N,i))
<=exp(s^2 sigma_N^2/2). The bound passes to a weak limit by truncation
and implies sub-Gaussian tails and all finite moments. A fixed scalar
shift h does not change moment finiteness. Hence an absolutely continuous
tight native spectral limit cannot supply the heavy tail required above.

**Scope check by an explicit non-native construction.** If one were allowed
to prescribe the arbitrary conditional spectral density

\[
f_u(u)=\frac{b^2|u|}{(u^2+b^2)^2},\qquad u\in\mathbb R,
\]

then k=u^2/(u^2+b^2) is uniform on [0,1]. Its arcsine mixture is exactly
f_x(x)=2 sqrt((1-x)/x)/pi, giving p_theta=(1+cos theta)/pi and Born.
It has infinite second and third moments, so it cannot be the tight weak
limit of the native linear-X Rademacher spectra. This is an analytical
counterexample to a proposed no-go based on unitarity or two-dimensional
conditional blocks alone. It is **not** a native Hamiltonian solution,
and is not counted as a phase or an additional numerical realization.

## 9. Field robustness proof

Adding -hX shifts W exactly to exp(-2iht)W_0. With z_n(N,t)=tau_N(W_0^n),

\[
d_0(N,h,t)=2\operatorname{Re}(e^{-2iht}z_1)-1
-\operatorname{Re}(e^{-4iht}z_2),\qquad |z_n|\le1.
\]

For an interval of full width w and center c, its field mean is

\[
\overline d_0=-1+
2\operatorname{sinc}(tw)\operatorname{Re}(e^{-2ict}z_1)
-\operatorname{sinc}(2tw)\operatorname{Re}(e^{-4ict}z_2),
\quad |\overline d_0+1|\le\frac{5}{2w|t|},
\]

where sinc(y)=sin(y)/y. This bound is independent of N and of the detector.
It already excludes convergence to zero throughout any field interval by
bounded convergence, first in N, then in t. Field integration is a proof
over perturbations, **not a time-averaged replacement for instantaneous R**.

For the stronger measure-zero assertion, restrict any positive-measure E
to a bounded positive-measure subset. Integrating d_0+1 gives a modulus at
most 2|integral_E exp(-2iht)dh|+|integral_E exp(-4iht)dh|. Each integral
tends to zero: approximate the integrable indicator of E in L1 by finite
linear combinations of interval indicators, whose oscillatory integrals
decay explicitly as 1/t; the L1 approximation bounds the remaining error.
The bound is uniform in N. Bounded convergence passes N->infinity on E.
If the resulting d_0 tends to zero at each h in E, bounded convergence in t
makes the integral of d_0+1 tend to |E|, a contradiction. Thus |E|=0.

This proof needs no parity symmetry and no convergence of the complex trace
z_n itself. It requires the stated N-first limit of d_0 on the tested fields.
It excludes any phase open under the permitted -hX perturbation **within
the X-conserving class**. It does not establish what happens once X is broken.

## 10. Microscopic preimages established so far

The continuous-support long-time Born preimage of Theorem B is empty.
In Theorem C the possible fields have measure zero for each fixed detector/
coupling sequence. Neither result supplies the broadest full-model H_B.

The proofs include all native graph topologies, attachment sites, coupling
signs and nonuniform strengths that satisfy the displayed operator hypotheses.
Theorem C allows all detector fields and interactions, including ones not
commuting with V. Theorem B permits arbitrary detector terms in the commutant
of V, not only explicit X/XX terms. Uncoupled tensor-factor spectators,
detector conjugations and site permutations preserve the root measure when
they remain admissible. Direct-sum sectors with different laws change counting
weights and cannot be discarded merely because a chosen preparation avoids them.

The new field obstruction applies to the central-X native families highlighted
in the earlier structural study. The finite construction's nonzero central-Z
neighborhood is outside Theorem B. Theorem E excludes its extensions with
absolutely continuous tight limiting coupling spectra; embeddings with only
a fixed finite active set have atomic spectra and are not covered by E.
There is no claim that the fixed-time tolerance radius stays useful at
arbitrarily late times.

## 11. Classification, with scope

| Feature | What is proved for the asymptotic target |
|---|---|
| Tilted radial inversion symmetry and full moment hierarchy | Necessary and sufficient geometrically on supported pairs; not the requested new dynamical C_B. |
| Positive a.e. continuous reference density | Necessary for the stated global density interpretation; atoms alone do not suffice. |
| Finite-dimensional recurrence | Universal obstruction to a nontrivial ordinary t-first root limit and an unrestricted joint continuous-support limit. |
| [K,V]=0 with central X and hz0=0 | Sufficient obstruction to a continuous-support Born long-time limit, when limits exist; not necessary for failure. |
| [H,X_q]=0 and freely perturbed hx0 | Sufficient obstruction to an open exact-Born field interval; detuning is not covered. |
| Spectra, gaps, degeneracies, resonances | Enter through effective dynamics; no gap or nondegeneracy assumption is needed for A--C. |
| Graph, graph spectrum, attachment sites | Irrelevant to the stated universal bounds within their operator hypotheses; generally influence the pencil. |
| Detector eigenvectors/localization | Enter W for noncommuting dynamics; not independently classified in the full model. |
| Commuting detector-only terms and tensor spectators | Irrelevant to normalized roots in the exact cancellation cases. |
| Coupling strengths/signs | Enter V; unrestricted in B/C. Theorem D additionally specifies g/sqrt(N). |
| Coupling phases and central YY/ZZ/ZX terms | Can leave the X-conserving hypotheses; no general asymptotic classification proved. |
| hx0 | A root-changing perturbation with a proved measure-zero field constraint in C. |
| hz0 and other symmetry-breaking fields | E excludes detuned commuting limits with absolutely continuous light-tailed coupling spectra; the general preimage remains open. |
| Infinite third absolute coupling moment | Necessary only for the detuned phase-mixed scalar mechanism to produce exact Born; excluded by tight native linear-X spectral limits. |
| Detector preparation | Not an input to equal algebraic root counts; needed separately for operational probabilities. |
| Initial qubit/readout convention | Fixed by the chosen columns and Z block basis; general rotations change the problem. |
| N and t | Order is essential; finite-N agreement and favorable times do not imply the target. |

## 12. Numerical verification

Reproduction code: `core/born_asymptotic.py`,
`scripts/analyze_born_asymptotic.py`, `configs/born_asymptotic_2026-09-11.json`,
and `tests/test_born_asymptotic.py`. **VERIFIED_NUMERICALLY:** 16 new focused
tests pass; the combined relevant suite passes 60 tests. The finite gate and
canonical S_born are unchanged; unoccupied-bin errors are not presented as
global errors.

The reduced study contains 504 native QZ snapshots: six independent saved
parameter seeds, N=3,4,5, chain/ring/all-to-all graphs, seven times from 0.2
to 300, three central-X fields and one central-Z control per baseline.
It verifies QZ against conditional traces and includes X-breaking controls.
These controls test the proof's domain;
failure of a trace formula outside its hypotheses is not a no-go theorem.
The N-first Gaussian limit and its derived 1/N correction are evaluated
without treating analytic multiplicities as independent samples. All seeds,
effective parameters, root audits and source hashes are saved. The largest
QZ backward residual is 2.23e-15; the largest in-scope trace discrepancy is
4.43e-12. The deliberately out-of-scope central-Z controls give discrepancies
from 4.10e-5 to 1.43, demonstrating that the conditional-X formula must not
be reused when its symmetry is broken. These are deterministic discrepancy
bounds in the sampled cases, not statistical error bars on a phase.

Finite-bin coverage ranges from 0.03125 to 0.71875; no reduced snapshot has
global 64-bin coverage. Global RMSE and whole-interval epsilon_infinity are
therefore recorded as undefined (JSON null), alongside occupied-bin RMSE,
occupied-center maximum error, every one of the eight residuals, their maximum,
coverage, and the unchanged canonical 100-bin S_born. No near-pole favorable
occupied-bin score is promoted to a global Born claim.

The exact collective moment formula is checked against native QuSpin
exponentials and production QZ at N=3,4,5, including a pencil recurrence.
The derived 1/N correction is evaluated at six sizes 32 through 1024 using
analytic multiplicities, not large local simulations. Three refinements in
the tests verify the O(1/N^2) corrected remainder. The formal log-cosine
series was also expanded with exact rational polynomial arithmetic through
degree six, giving coefficients -1/2, -1/12, -1/45. No symbolic package was
available in either inspected Python runtime; no dependency was installed.

Theorem E has separate checks at b=0.03,0.4,1.1 using detuned native
conditional blocks, plus instantaneous frequency-integral checks for the
Gaussian spectrum at t=10,30,100. The phase-mixture cap obstruction and
the explicit non-native heavy-tail counterexample are independently checked
by quadrature. These checks validate the formulas; the proof of E supplies
the tail conclusion and does not infer it from the selected times.

```bash
python -m py_compile core/born_asymptotic.py core/born_asymptotic_plotting.py scripts/analyze_born_asymptotic.py
python scripts/analyze_born_asymptotic.py --help
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q tests/test_born_asymptotic.py tests/test_born_reciprocity.py tests/test_projective_root_conventions.py tests/test_exact_born_limits.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/analyze_born_asymptotic.py --output reports/<fresh-asymptotic-audit>
```

Executed with the repository Python 3.11 environment. The full repository
suite was not run: no existing numerical API or diagnostic was modified.
Generated data remain ignored and uncommitted. Source hashes supplement the
pre-edit HEAD recorded by the numerical run.

## 13. Diagnostic plots

The reproduction script produces separate plots of P and its reflection,
R versus Born, R residuals, widely separated times, finite-size corrections,
independent microscopic perturbations, and the first-moment obstruction.
They illustrate proved obstructions and controls. There is no predicted
positive phase with interior Hamiltonians to plot, and no complete C_B
invariant to certify. Coverage and finite-resolution errors stay explicit.

Artifacts in `reports/born_asymptotic_2026-09-11_final/`:

- [P and reflected P](reports/born_asymptotic_2026-09-11_final/polar_densities.pdf)
- [R against Born](reports/born_asymptotic_2026-09-11_final/polar_response.pdf)
- [R residual](reports/born_asymptotic_2026-09-11_final/polar_residual.pdf)
- [Native finite-N P/R/residual profiles](reports/born_asymptotic_2026-09-11_final/native_polar_profiles.pdf)
- [Widely separated native times](reports/born_asymptotic_2026-09-11_final/long_time_native.pdf)
- [Derived finite-size corrections](reports/born_asymptotic_2026-09-11_final/finite_size_correction.pdf)
- [Microscopic perturbations and controls](reports/born_asymptotic_2026-09-11_final/microscopic_perturbations.pdf)
- [Necessary field-moment obstruction](reports/born_asymptotic_2026-09-11_final/field_moment_obstruction.pdf)
- [Summary and hashes](reports/born_asymptotic_2026-09-11_final/summary.json)

Each PDF has a PNG preview. Continuum curves are Fourier evaluations of the
proved N-first density, with positive floating estimates of the analytical
truncation bound; underflow is floored and never reported as an exactly zero
tail. Floating-point rounding is separate from that truncation estimate.
The first three figures show the collective control at g=0.7 and
t=0.7,1.5,4. The native-profile columns use the first three seeds, one per
graph, at t=30,100,300 with N=5 and hx0=0; no score-based selection is made.
Line segments on time/size plots only connect evaluated points. No smoothing,
root filtering, pseudocount, or fitted convergence exponent is used. All roots
and numerical figure inputs are saved as NPZ, JSON or named-column DAT files.

## 14. Remaining requirements and next analytical problem

The following goal requirements remain **unachieved**: a non-tautological
dynamical iff condition for the full model; existence and strong tail control
of general noncommuting thermodynamic root limits; a full-model robust-phase
proof or no-go; the broadest microscopic preimage and its full classification;
and numerical verification of that eventual theorem across its entire
predicted scope. The current tests and plots cannot substitute for them.

The next unresolved operator class includes central-Z detuning with genuinely
noncommuting detector/coupling operators and central YY/ZZ/ZX terms. In that
class a rigid W-phase translation need not exist, so the field proof cannot
simply be reused. Theorem E resolves one detuned commuting extension; singular
or escaping coupling spectral laws still require separate treatment.
A definition of thermodynamic Hamiltonian sequences
and topology is required for any eventual open-phase claim. This report
records progress toward the original objective and does not mark it complete.
