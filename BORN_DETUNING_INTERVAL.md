# Detuning excludes an open Born phase for commuting detector fields

12 September 2026. **PROVED within the stated class; the full native
noncommuting-detector objective remains OPEN.** This report extends Theorem E
of [the asymptotic study](BORN_ASYMPTOTIC_OBSTRUCTIONS.md). The determinant
counterexample in [the nonnormal study](BORN_NONNORMAL_LIMIT.md) prevents
extending this result through a trace-moment approximation alone.

## 1. Theorem H: no detuning interval

Consider the native-sign conditional dynamics

\[
H_N(b)=I\otimes K_N-X_q\otimes V_N-Z_q\otimes(W_N+bI),
\qquad [K_N,V_N]=[K_N,W_N]=[V_N,W_N]=0.
\tag{1}
\]

Use the first-qubit Z basis, U=exp(-itH), A=U00, C=U10, and production
homogeneous roots Cv=lambda Av with theta=2 atan|lambda|. Pauli eigenvalues
are +/-1 and hbar=1. Detector eigenvalues have their full algebraic
multiplicities; initial detector probabilities do not reweight them.

Assume the joint normalized spectral laws of (V_N,W_N) converge to a
probability law nu of finite real (v,w). Assume E_nu v^2<infinity and
nu(v!=0)>0. Suppose that, after N->infinity, ordinary late-time root
measures have the phase-mixed form derived below at every b in a proposed
open interval I. Then **there is no nonempty open interval I on which all
these limiting laws satisfy exact continuous Born reflection balance**.

This is an open-phase no-go for the full class (1), including correlated
transverse and longitudinal detector fields and arbitrary commuting K.
It does not require independence, a density of nu, or a moment bound on w.
The microscopic detuning change has operator norm |delta b| for every N.
It is not a full-model no-go: simultaneous detector commutation and the
ordinary phase-mixing limit are material assumptions.

**Corollary H1 (an entire native XX/ZX collective family).** Let

\[
V_N=h+gS_N,\quad W_N=cS_N,\quad
S_N=N^{-1/2}\sum_{i=1}^N X_i,\quad g\ne0,
\tag{2}
\]

with any K_N commuting with S_N. For every real h,b,c, the N-first root law
has an ordinary weak long-time limit. None of these limits is a continuous
full-support exact-Born law. Thus this family is excluded pointwise, not only
as an open phase. The native implementation uses Jx=g/sqrt(N),
Jzx=c/sqrt(N), hx0=h, hz0=b, all attachments. K_N=0 or detector X fields
and XX bonds are directly implemented examples of the commuting spectator.
No Gaussian substitution for noncommuting detector operators is involved.

## 2. Exact reduction and limiting object

Simultaneously diagonalize the detector operators. For an eigenvalue pair
(v,w), put z=w+b, Omega=sqrt(v^2+z^2). The common K eigenphase cancels, and

\[
a=\cos(t\Omega)+iz\frac{\sin(t\Omega)}{\Omega},\qquad
c_0=iv\frac{\sin(t\Omega)}{\Omega}.
\tag{3}
\]

The values at Omega=0 are a=1,c_0=0. Since |a|^2+|c_0|^2=1, the polar
coordinate x=sin^2(theta/2) is exactly

\[
x=k_b\sin^2(t\Omega),\qquad k_b=\frac{v^2}{v^2+(w+b)^2}.
\tag{4}
\]

Here x lies in [0,1]; it is different from the log-radius variable called x
in the nonnormal report. The ratio uses root counts, not a transition-trace
weight. Formula (4) is continuous in the field pair at each finite t, so
joint weak spectral convergence proves the N-first polar-root limit.

A phase-mixed limit means that bounded continuous tests of (4) converge as
t->infinity to the tests of X=k_b sin^2(phi), phi uniform on [0,pi] and
independent of the field pair. This is an ordinary instantaneous weak limit,
not a definition by time averaging. One sufficient condition is that the
pushforwards in Omega of every k_b^m-weighted field measure, m>=0, are
absolutely continuous away from inactive v=0 sectors. Fourier expansion of
sin^(2m), the Riemann--Lebesgue lemma, and polynomial approximation then
prove the limit for every continuous test on [0,1]. A singular frequency law
may fail this condition; Theorem H assumes the phase-mixed limit rather than
silently replacing a nonmixing trajectory by its average.

Condition on v!=0. The discarded v=0 fraction is a fixed north-pole atom;
it does not affect interior reflection balance. Now k_b>0 almost surely and
the mixed active law has no atom at either endpoint. Its density is

\[
q_b(x)=\mathbb E\frac{\mathbf 1_{0<x<k_b}}
{\pi\sqrt{x}\sqrt{k_b-x}}.
\tag{5}
\]

The Jacobian dx/dtheta=sqrt(x(1-x)) is reflection symmetric. Consequently
exact Born balance in theta is exactly

\[
q_b(1-x)=\frac{x}{1-x}q_b(x)\quad\text{for almost every }0<x<1.
\tag{6}
\]

Equation (6) is used as a necessary geometric identity, not advertised as a
new independently structural C_B. The new structural obstruction is the
response of the joint field law to microscopic detuning.

## 3. Proof: resonance supplies too much south-pole mass

Write N_b(epsilon)=Pr(X<epsilon) and S_b(epsilon)=Pr(X>1-epsilon) for the
active phase-mixed law. From (6),

\[
S_b(\epsilon)=\int_0^\epsilon\frac{x}{1-x}q_b(x)dx
\le\frac{\epsilon}{1-\epsilon}N_b(\epsilon)=o(\epsilon).
\tag{7}
\]

The last equality follows from the absence of an active north-pole atom.
It holds even when q_b diverges at that pole. If Born held at every b in a
bounded open interval I, dominated convergence would give

\[
\int_I S_b(\epsilon)db=o(\epsilon),
\tag{8}
\]

because S_b(epsilon)/epsilon<=2 for epsilon<1/2 under (7). Measurability
follows directly from the field integral and the phase probability.

Suppose the active field law assigns positive mass to -w in I. There is a
compact subinterval I0 strictly inside I and constants 0<v0<v1<infinity
such that the event -w in I0 and v0<=|v|<=v1 has positive mass. For every
such field pair and sufficiently small epsilon, the b interval

\[
|w+b|\le\tfrac12|v|\sqrt\epsilon
\]

lies inside I and has length |v|sqrt(epsilon). In it k_b>=1-epsilon/4.
The independent phase event sin^2(phi)>=1-epsilon/4 has probability at
least sqrt(epsilon)/pi. On their intersection X>1-epsilon. Integrating
first in b and then in the field law therefore yields

\[
\int_I S_b(\epsilon)db\ge C\epsilon,\quad C>0,
\tag{9}
\]

contradicting (8). Thus an interval of Born laws would require the active
field law to give **zero** mass to -w in I. This conclusion requires no
smoothness or tail hypothesis.

## 4. Proof: a detuning gap supplies too little south-pole mass

Choose b0 in the interior of I. The conclusion of section 3 supplies a
uniform active detuning gap |w+b0|>=delta>0 almost surely. Then

\[
X>1-\epsilon\ \Longrightarrow\
|v|>\delta\sqrt{(1-\epsilon)/\epsilon},\qquad
\sin^2\phi>1-\epsilon.
\]

The latter event has probability (2/pi)arcsin(sqrt(epsilon))=O(sqrt(epsilon))
and is independent of the field pair. Finite E v^2 gives
Pr(|v|>R)=o(R^-2). Therefore

\[
S_{b_0}(\epsilon)=o(\epsilon^{3/2}).
\tag{10}
\]

But k_b0>0 almost surely, so some k0>0 has mass m=Pr(k_b0>=k0)>0.
For 0<x<k0, (5) implies q_b0(x)>=m/(pi sqrt(x)), since k_b0<=1.
Born balance would then require

\[
S_{b_0}(\epsilon)\ge\frac{m}{\pi}\int_0^\epsilon\sqrt{x}\,dx
=\frac{2m}{3\pi}\epsilon^{3/2},\quad\epsilon<k_0.
\tag{11}
\]

Equations (10) and (11) contradict each other. Combined with section 3,
this proves Theorem H. It also improves the fixed-detuning obstruction
from a finite third absolute moment to a finite second moment.

The moment threshold for this gap argument is sharp in order. At fixed
nonzero detuning b, the non-native density
f(v)=b^2|v|/(v^2+b^2)^2 has every moment of order p<2 finite but its second
moment diverges. Its k=v^2/(v^2+b^2) distribution is uniform, and (5) gives
q(x)=2 sqrt((1-x)/x)/pi, hence P(theta)=(1+cos(theta))/pi and exact Born
balance. This is the earlier verified heavy-tail counterexample, not an
admissible native tight Rademacher spectrum or an open detuning phase.

## 5. Native collective XX/ZX family: proof of H1

In (2), the full normalized spectral distribution of S_N is the centered
Rademacher sum and converges to a standard real Gaussian G. At fixed t,
(3)--(4) therefore give the actual native root limit with
v=h+gG and z=b+cG. The radial frequency

\[
\Omega(s)=\sqrt{(h+gs)^2+(b+cs)^2}
\]

is nonconstant for g!=0. Splitting the real line at its at most one turning
point makes its Gaussian weighted pushforwards absolutely continuous; any
inverse-square-root singularity at the minimum is integrable. Thus the
Fourier argument in section 2 proves ordinary late-time phase mixing.
Weak convergence on the compact polar interval is equivalent to convergence
in the determinant-potential metric of Theorem F, and ordinary convergence
also gives the corresponding sup over all sufficiently late times. No
claim of uniform density convergence is needed for this negative result.

For c!=0, the resonance is s0=-b/c. If v0=h+g s0!=0, a direct local
rescaling s=s0+(|v0|/|c|)sqrt(epsilon)y gives

\[
\lim_{\epsilon\downarrow0}\frac{S_b(\epsilon)}\epsilon
=\frac{|v_0|}{|c|}\frac{e^{-s_0^2/2}}{\sqrt{2\pi}}>0.
\tag{12}
\]

Indeed the allowed y interval tends to [-1,1], and the phase cap probability
divided by sqrt(epsilon) tends to (2/pi)sqrt(1-y^2). Its integral is one.
The resonance interval is bounded and shrinks to s0, justifying dominated
convergence after rescaling. Equation (12) contradicts (7).

If v0=0, the fields are proportional: k_b=g^2/(g^2+c^2)<1 almost surely.
The limiting law has a strict south support gap and fails full-support Born
balance. For c=0 and b!=0, section 4 applies because h+gG has finite second
moment. For c=b=0, k=1 and the folded polar phase is uniform, giving R=1/2.
These cases exhaust all h,b,c for g!=0 and prove H1.

## 6. Verification and limits

Verification code is in `core/commuting_vector_field.py` and
`tests/test_commuting_vector_field.py`. It uses the native NumPy Hamiltonian,
full propagator exponentiation, production homogeneous QZ, exact joint-field
columns, and independently integrated phase caps. Numerical results and
artifact links follow. These checks validate the reduction and the derived
coefficient; they do not establish the theorem by extrapolation.

**VERIFIED_NUMERICALLY.** The saved configuration uses g=0.7, h=0.2, c=0.5,
detector X field 0.13, and the three detunings below. The cap is evaluated
at 13 logarithmically spaced epsilon values from 1e-5 through 1e-2.

| b | Exact coefficient in (12) | Numerical S(epsilon)/epsilon at epsilon=1e-5 |
|---:|---:|---:|
| -0.6 | 0.4039069943650830 | 0.4039058316187629 |
| 0.3 | 0.1466188252723918 | 0.1466214678555534 |
| 0.8 | 0.2040943358101982 | 0.2040936499967418 |

All three exact coefficients are positive; Born would require a zero limit.
The maximum reported cap quadrature error is 8.274e-14. This is an adaptive
quadrature estimate, not an interval-arithmetic certificate. Near coincident
field zeros, the integral is evaluated in a rescaled resonance coordinate
to avoid catastrophic subtraction. Both exact proportional fields and a
1e-12 departure are covered by tests.

Thirty-six full native propagator/QZ snapshots cover N=2,3,4 and times
0.3,1.7,11.3,83 at all three detunings. Maximum sorted polar-angle error
against (3) is 8.072e-14 and maximum homogeneous backward residual is
6.956e-16. All eight repository Born residuals and canonical S_born are
saved unchanged. Coverage is only 0.0625--0.15625, so global histogram RMSE
and maximum error remain null; occupied-bin values are labelled separately.

Nine new tests pass with all warnings treated as errors. The combined
92-test relevant suite passes with runtime warnings treated as errors.
Python compilation and CLI help checks also pass. Reproduction, using the
repository Python 3.11 environment and one BLAS/OpenMP thread:

```bash
python -m py_compile core/commuting_vector_field.py core/commuting_vector_field_plotting.py scripts/analyze_born_detuning_interval.py
python scripts/analyze_born_detuning_interval.py --help
python -m pytest -q -W error tests/test_commuting_vector_field.py
python -m pytest -q -W error::RuntimeWarning tests/test_commuting_vector_field.py tests/test_commuting_detector_field.py tests/test_projective_potential.py tests/test_born_asymptotic.py tests/test_born_reciprocity.py tests/test_projective_root_conventions.py tests/test_exact_born_limits.py
python scripts/analyze_born_detuning_interval.py --output reports/born_detuning_interval_2026-09-12
```

The [resonance-cap figure](reports/born_detuning_interval_2026-09-12/resonant_south_caps.pdf)
has a visually verified PNG counterpart. The output directory also contains
`caps.npz`, `qz_snapshots.json`, and `summary.json`. Seven source hashes,
the configuration hash, and all four output hashes were independently
verified. Provenance records Python 3.11.16, NumPy 2.4.6, SciPy 1.17.1,
UTC time, effective parameters and the base commit; source hashes identify
the uncommitted-at-execution implementation. Outputs remain uncommitted.

No symbolic-software validation is claimed: SymPy was unavailable in both
the project and bundled runtimes. The Jacobian, cap threshold, and resonance
area integral are shown explicitly in the proof and checked through the
independent numerical formulations above. No dependency was changed.

Theorems H/H1 supply broader microscopic exclusions, the correct N-first
limit for (2), and a sharp moment-order improvement. They do not establish a
full-model Born iff or exclude genuinely noncommuting detector fields.
In particular, [V_N,W_N] small in normalized trace norm is not sufficient.
The full exact robust Born objective remains active; its noncommuting
microscopic preimage and determinant limits remain unresolved.
