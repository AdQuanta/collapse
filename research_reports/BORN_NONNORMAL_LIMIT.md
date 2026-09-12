# Thermodynamic root limits require more than operator moments

12 September 2026. **PROVED reductions and a native counterexample;
the full exact-Born phase objective remains OPEN.** This report continues
[the five scoped obstructions](BORN_ASYMPTOTIC_OBSTRUCTIONS.md). It preserves
the production homogeneous-QZ pencil, algebraic multiplicities, and the
distinction between root statistics and operational probabilities.

## 1. Result

**Theorem F (a scalar potential equivalent to the polar root measure).**
For every regular d-by-d pencil (C,A), define

\[
J_{C,A}(x)=\frac1{2\pi d}\int_0^{2\pi}
\left[\log|\det(C-e^{x+i\phi}A)|
-\log|\det(C-e^{i\phi}A)|\right]d\phi.
\tag{1}
\]

The logarithmic singularities at the finitely many possible root angles
are integrable. The function J is finite, convex, nondecreasing, 1-Lipschitz,
and J(0)=0. It determines the complete normalized polar root measure,
including zero and infinite roots. For any sequence of regular pencils,

\[
\mu_n\Rightarrow\mu
\quad\Longleftrightarrow\quad
J_n\longrightarrow J_\mu\text{ uniformly on every compact x interval}.
\tag{2}
\]

Convergence at every rational x is also sufficient. Thus this supplies an
exact scalar description and a convergence criterion for **all** regular
native noncommuting pencils, without inverting A or replacing eigenvalues
by singular values. No unbounded logarithmic moment of the root law is needed.

**Theorem G (native failure of Gaussian substitution for roots).** Let

\[
H_N=-\frac{g}{\sqrt N}\left(X_q\sum_iX_i+Y_q\sum_iY_i\right),
\quad g\ne0,\quad H_D=H_Q=0.
\tag{3}
\]

This is the implemented `Jx=Jy=g/sqrt(N)` channel, with all attachments.
The normalized detector operators S_x=N^-1/2 sum X_i and S_y=N^-1/2 sum Y_i
converge in every tracial noncommutative moment to independent standard real
Gaussians. In particular ||[S_x,S_y]||_(2,tau)^2=4/N->0. The propagator
blocks and every bounded continuous singular-value statistic of C-zA have
the corresponding Gaussian limits.

Nevertheless, at every regular time, the **native projective root law is
exactly delta_0 for every N**. The roots of the Gaussian limiting blocks
instead have radius |tan(gt R)| with R Rayleigh, and have a nontrivial
continuous polar law for every t!=0. They are different measures. Small
commutators, all operator moments, correct transition traces, and weak
singular-value convergence therefore do not justify substituting a classical
Gaussian field into this nonnormal root problem.

**Consequence.** A proof based on limiting singular-value measures needs
control of their logarithmic tails, or a different argument controlling the
normalized determinant differences in (1). Such control fails for at least
one circle in this native example. Adding a fixed numerical singular-value
cutoff before N->infinity can produce the wrong root law. This is an
obstruction to an analytical shortcut, not a full-model no-go for Born.

## 2. Source and conventions

Use the first-qubit Z basis, U=exp(-itH), A=U00, C=U10,
Cv=lambda Av, theta=2 atan2(|alpha|,|beta|), lambda=alpha/beta, hbar=1.
The root kets are derived by the pipeline; no detector preparation density
matrix weights these roots. The spin operators here are Pauli matrices.
J_+=sum_i(X_i+iY_i)/2 raises Q_D=sum_i Z_i by two.

The source of (3) is `core/hamiltonians/quspin_hamiltonians.py`, also checked
against the NumPy backend. This analysis does not change either generator,
`core/analysis.py`, the QZ solver, or the 64/100-bin diagnostics. The earlier
charge-grading result in `BORN_STRUCTURE_ANALYSIS.md` already proves root
collapse in this channel. The new point is its incompatibility with a valid
Gaussian limit of all bounded trace observables and the resulting missing
logarithmic-tail control.

The general relation between nonnormal spectra, logarithmic potentials,
and singular-value log integrability is the standard Hermitization method;
see [Chafaï's derivation](https://djalil.chafai.net/blog/2010/05/14/logarithmic-potential-and-hermitization/).
The compact radial normalization, endpoint treatment, and native exchange
example below are derived explicitly here. No random independent-entry
matrix theorem is assumed for the Hamiltonian propagator blocks.

## 3. Exact determinant reduction and proof of F

A regular homogeneous determinant factors as

\[
\det(\beta C-\alpha A)=\kappa
\prod_{j=1}^d(\beta\alpha_j-\alpha\beta_j),\quad \kappa\ne0,
\]

where each (alpha_j,beta_j) is nonzero as a pair. Finite roots contribute
linear affine factors; beta_j=0 contributes a constant affine factor and
records an infinite projective root. Averaging a single factor on a circle
gives

\[
\frac1{2\pi}\int\log|\alpha_j-e^{x+i\phi}\beta_j|d\phi
=\max(\log|\alpha_j|,x+\log|\beta_j|).
\]

For unequal moduli this follows by factoring out the larger term and
integrating the absolutely convergent power series for log(1-z). At equal
moduli it follows by the integrable limit, or the integral of log|2 sin(phi/2)|.
The common factor kappa cancels between the two circles. Consequently

\[
J_{C,A}(x)=\frac1d\sum_j K_x(\theta_j),\qquad
K_x=\max(\log|\alpha|,x+\log|\beta|)
-\max(\log|\alpha|,\log|\beta|).
\tag{4}
\]

For finite nonzero roots with ell=log|lambda| this is
K_x=max(ell,x)-max(ell,0). At theta=0 it is x; at theta=pi it is zero.
These are its continuous endpoint limits. Hence K_x is a bounded continuous
function of theta on the compact projective radial interval, with |K_x|<=|x|.
It is invariant under arbitrary nonzero rescaling of each homogeneous pair.
No undefined subtraction infinity-minus-infinity occurs in the projective
formula, because the pair (0,0) is excluded.

Each kernel is convex and nondecreasing in x with slope between zero and one.
The right derivative of J is the log-radius cumulative distribution:

\[
J'_+(x)=\mu\{\theta: \tan(\theta/2)\le e^x\}.
\tag{5}
\]

This includes all zero-root mass. Its limit as x->-infinity is mu({0});
one minus its limit as x->+infinity is mu({pi}). Thus J uniquely determines
the whole probability measure, not just its interior density. Its
distributional second derivative is the interior log-radius measure.

If mu_n converges weakly, testing K_x gives pointwise J convergence. The
common Lipschitz bound promotes this to local uniform convergence by a finite
grid argument. Conversely, probability measures on [0,pi] have weakly
convergent subsequences. Every subsequential limit has the asserted limiting
J by (4); (5) makes all such limits identical. Therefore the full sequence
converges. The same argument and the Lipschitz bound show that convergence
at every rational x is sufficient. This proves both directions of (2).

The invariant also survives strict pencil equivalence (C,A)->(LCR,LAR)
for any common invertible L,R: their log-determinant factors cancel in (1).
This is an effective-pencil equivalence, not a license to apply nonunitary
microscopic transformations and call their Hamiltonians admissible.

## 4. Limits, topology, and what this does not prove

An explicit bounded metric for the weak root topology is

\[
d_J(\mu,\nu)=\sum_{m\ge1}\frac{2^{-m}}{1+2m}
\sup_{|x|\le m}|J_\mu(x)-J_\nu(x)|.
\]

Theorem F applies first to N->infinity at each t, then to an ordinary
long-time root limit. A tail assertion in this metric requires control at
every sufficiently late t, not a time average. The previous finite-N
recurrence obstruction remains in force.

This metric does not by itself control the reflected response in a density
norm. As before, that additionally requires density and denominator control.
The exact geometric Born balance in log radius can be written
I_*(J'')=exp(2x)J'', where I(x)=-x, together with zero south-pole mass and
the required continuous support. This is the existing geometric equivalent
expressed through a dynamical determinant. **It is not claimed as the final
non-tautological C_B or as a proof of an open Hamiltonian phase.** The new
result is the exact scalar limit criterion and a way to identify invalid
thermodynamic approximations before applying that geometric test.

## 5. A sufficient route from singular values to the correct potential

Let xi_(N,x) average, over phi and normalized detector dimension, the
singular-value measure of C_N-exp(x+i phi)A_N. For unitary-column pencils,
these singular values are in [0,1+exp(x)]. Equation (1) also reads

\[
J_N(x)=\int\log s\,d\xi_{N,x}(s)-\int\log s\,d\xi_{N,0}(s).
\tag{6}
\]

Suppose xi_(N,x) converges weakly for each rational x including zero and

\[
\lim_{\epsilon\downarrow0}\limsup_{N\to\infty}
\int_{s<\epsilon}|\log s|\,d\xi_{N,x}(s)=0.
\tag{7}
\]

Then truncate log below epsilon, pass to the weak limit on the bounded
support, and remove the truncation using (7). The limiting log integrals
exist and determine J. Theorem F now proves the correct polar root limit.
The upper log tail is already bounded at fixed x. This is a sufficient
condition, not a necessary one: divergent common terms could cancel in (6).
Any replacement argument exploiting such cancellation must prove it rather
than assume it from weak singular-value data.

A small solver backward residual is also insufficient for (7). Nonnormal
eigenvalues can be highly sensitive even when the computed eigenpairs have
small residuals. Conditioning and logarithmic-tail questions are separate.

## 6. Proof of the native counterexample G

### Exact finite roots

In (3), the flip block of H raises detector charge. Conservation of
Z_q+Q_D gives [Q_D,A]=0 and [Q_D,C]=2C. At regular times A is invertible,
so A^-1 C is nilpotent of index at most N+1. Equivalently, order detector
states by charge: A is block diagonal and C strictly block triangular,
giving det(C-zA)=(-z)^d det A. All algebraic roots are zero and J_N(x)=x.

The exceptional times at which A is singular form a discrete set at each N;
their union over N is countable. All convergence claims about this native
root sequence are made at common regular times. Such times form a full-measure
set. The fixed rational g and t used below are regular at every N: nonzero
conditional frequencies are algebraic, so their products with rational t
cannot equal odd multiples of pi/2. No special recurrence is selected.

### Detector moment limit

Expand a word of length k in S_x,S_y into a sum over site labels. A site
occurring once has zero trace. Terms with fewer than k/2 distinct sites
are suppressed by powers of N; for fixed k their number is finite after
partitioning the positions. For even k, the leading terms pair positions
on distinct sites. The local pair trace is tau(sigma_a sigma_b)=delta_ab.
These are exactly Wick pairings of independent centered variance-one real
Gaussians G_x,G_y. Odd moments vanish in the limit. This proves convergence
of all ordered noncommutative moments, not merely symmetrized moments.

Directly, tau(S_x^2 S_y^2)=1 and tau(S_x S_y S_x S_y)=1-2/N, hence
||[S_x,S_y]||_(2,tau)^2=4/N. The vanishing commutator is in normalized
Hilbert--Schmidt norm, **not operator norm**.

### Passing to propagator trace observables

For every integer m, the one-channel Rademacher moment bound gives
||S_a||_(2m,tau)<=sqrt(2m). Schatten's triangle inequality therefore gives
||H_N||_(2m,tau)<=2|g|sqrt(2m), uniformly in N. The Hermitian exponential
Taylor remainder of degree m-1 has L2 norm at most

\[
\frac{|t|^m}{m!}\|H_N\|_{2m}^m
\le\frac{(2|gt|\sqrt{2m})^m}{m!}\longrightarrow0.
\]

Thus polynomial approximation and the moment limit identify exp(-itH_N)
in trace observables with exp(igt(X_q G_x+Y_q G_y)) at each fixed t.
Compression to A,C preserves this L2 approximation. To obtain arbitrary
products of blocks, one may first approximate each factor in a fixed
Schatten p norm with p at least the word length and apply Hölder's inequality;
the same moment bound controls the remainders and polynomial factors there.
Therefore all block *-moments converge. Since ||C-zA||<=1+|z|, polynomial
approximation of continuous functions of (C-zA)†(C-zA) gives convergence
of every bounded continuous singular-value statistic. The bounds are uniform
in phi, so circle-averaged singular-value measures converge as well.

### The two root laws disagree

Put R=sqrt(G_x^2+G_y^2), with density r exp(-r^2/2), r>0, and uniform
independent polar phase psi. The limiting scalar blocks are

\[
A_G=\cos(gtR),\qquad C_G=i e^{i\psi}\sin(gtR).
\]

Their root radius is |tan(gtR)|. The folded angle is continuous and
nonconstant for every t!=0. In particular its first polar cosine moment is

\[
a_1^G=\mathbb E\cos(2gtR)
=1-2\sqrt2\,gt\,D(\sqrt2 gt)<1,
\]

where D is Dawson's integral. The inequality also follows immediately from
the positive continuous Rayleigh measure without using the special-function
formula. The **native** first root moment is a_1(N,t)=1 exactly.

In contrast, the bounded physical transition trace really does converge:
tau(C_N†C_N)->E sin^2(gtR)=sqrt(2)gt D(sqrt(2)gt)>0. Hence agreement in
this trace does not validate the root distribution. This trace uses a
maximally mixed detector input; it is explicitly distinguished from equally
counted projective roots, whose first moment remains one.

If (7) held at every rational radius including zero, (6) and the Gaussian
singular-value limit would force J_N to approach the nontrivial Gaussian
root potential. The Gaussian circle log integrals are finite: circular
Jensen averaging gives log max(|sin(gtR)|,exp(x)|cos(gtR)|), whose argument
is bounded above and bounded away from zero at each fixed x. The log's
positive part is bounded, so its negative part is integrable as well.
But J_N(x)=x, which represents delta_0. Uniqueness in
Theorem F yields a contradiction. Thus (7) fails for at least one circle.
This proves that the missing logarithmic control is a real native obstruction,
not just a hypothetical caveat about arbitrary matrices.

## 7. Exact sector representation for verification

Decompose N spin-half detectors into spin-j sectors. Their multiplicity is
m_(N,j)=binom(N,N/2-j)-binom(N,N/2-j-1). In the ordered m=-j,...,j basis,

\[
\omega_{j,m}=\frac{2g}{\sqrt N}\sqrt{(j-m)(j+m+1)},\quad
A_{m,m}=\cos(t\omega_{j,m}),\quad
C_{m+1,m}=i\sin(t\omega_{j,m}).
\]

All other entries vanish. The top m=j state has omega=0, A=1 and C=0.
The columns obey A†A+C†C=I. Multiplicities satisfy
sum_j m_(N,j)(2j+1)=2^N; all trace and log statistics below use these full
weights. No large-spin sector is substituted for the maximally mixed detector.

Charge covariance makes the singular values of C-r exp(i phi)A independent
of phi: conjugating by exp(-i phi Q_D/2) changes C by exp(-i phi) and leaves
A unchanged, up to an irrelevant common phase. Thus the numerical logarithmic
test in this example needs no angular quadrature. Its exact determinant is
known from the diagonal, even if a singular value is below machine resolution.

For a positive cutoff eta, compare the sums of log(max(s,eta)) with this
exact-form determinant sum. The cutoff is a diagnostic for lost logarithmic
mass; it is never used to define production roots or to claim a Born phase.

## 8. Validation and artifacts

Implementation and verification are in `core/projective_potential.py`,
`core/collective_exchange.py`, `tests/test_projective_potential.py`, and
`scripts/analyze_born_nonnormal_limit.py`. The new routines are separate
from production QZ and the existing Born diagnostics.

**VERIFIED_NUMERICALLY.** With g=0.7, t=0.61 and exact multiplicity weights,
the normalized transition trace is 0.2876171138189103 at N=128, compared
with its proved Gaussian limit 0.2876935987125207. This is a finite-size
check, not a fitted convergence theorem. The native first root moment is
exactly 1, whereas the roots of the limiting Gaussian blocks have first
moment 0.4246128025749586. The disagreement persists in the proved limits.

Sixteen production-QZ checks cover N=2,3,4,5 and t=0.3,0.61,1.3,3.0.
All computed angles are zero; the maximum homogeneous backward residual
is 2.221e-16. Separate tests compare sector traces and determinants with
full native QuSpin propagators at N=2,3,4,5. Random native noncommuting
pencils with saved seeds 19,37,91 verify (1) against homogeneous QZ using
64,128,256 circle nodes. The endpoint and scale tests include zero and
infinite roots. No cutoff modifies these roots.

The sector audit uses N=4,8,16,32,64,128 and eta=1e-2,1e-4,1e-8. At
x=-1 and eta=1e-8, the cutoff potential changes from -1 within numerical
precision at N=4 to -0.87841054 at N=128, although the exact native value
remains -1 at every N. At N=128 the lost logarithmic integral on that
circle is 0.13887371 per detector dimension. The Gaussian root potential
there is -0.55587206. These finite trends illustrate the analytically proved
failure of log integrability; they do not identify a limiting cutoff value.
The largest Gaussian-potential quadrature error estimate, including the
explicit Rayleigh tail bound, is 4.527e-12. Quadrature error estimates are
numerical estimates, not interval-arithmetic certificates.

All eight repository Born moment residuals vanish for delta_0, but its
64-bin reflected coverage is only 2/64. Thus global RMSE and maximum error
are saved as null. Occupied-bin errors and the unchanged canonical S_born
are retained as finite diagnostics. This example does not cover a continuous
Born domain, regardless of its finite moment score.

Fourteen new tests and the combined 74-test relevant suite pass with runtime
warnings treated as errors. The commands, using the repository Python 3.11
environment and one BLAS/OpenMP thread, were:

```bash
python -m py_compile core/projective_potential.py core/collective_exchange.py core/projective_potential_plotting.py scripts/analyze_born_nonnormal_limit.py
python scripts/analyze_born_nonnormal_limit.py --help
python -m pytest -q -W error::RuntimeWarning tests/test_projective_potential.py tests/test_born_asymptotic.py tests/test_born_reciprocity.py tests/test_projective_root_conventions.py tests/test_exact_born_limits.py
python scripts/analyze_born_nonnormal_limit.py --output reports/born_nonnormal_limit_2026-09-12
```

An initial NumPy slogdet call emitted runtime warnings for a nonsingular
native N=5 block. Independent Hermitian and SciPy LU log determinants agreed
within 2e-15, with minimum absolute eigenvalue 0.41235. The check now uses
the Hermitian structure of this A; generic circle determinants use SciPy LU.
No warning was suppressed and no dependency was changed.

Both PNG figures were visually inspected; vector PDF counterparts are saved:

1. [Trace convergence and root disagreement](reports/born_nonnormal_limit_2026-09-12/native_gaussian_mismatch.pdf).
2. [Singular-value cutoff and lost logarithmic mass](reports/born_nonnormal_limit_2026-09-12/singular_log_cutoff.pdf).

The output directory also contains `potential_data.npz`, `qz_snapshots.json`,
and `summary.json`, with effective configuration, source/config/output SHA-256
hashes, UTC timestamp, base commit, Python 3.11.16, NumPy 2.4.6 and SciPy
1.17.1. Source hashes identify the new implementation before its delivery
commit. Generated data and figures remain uncommitted. The largest sector
matrix is 129 by 129; the calculation is a reduced exact-sector verification,
not a full 2^128-dimensional production simulation.

## 9. Completion audit and next requirement

The all-pencils scalar reduction and its iff convergence criterion are proved.
The exchange example proves a native failure of a proposed extension from
commuting/Gaussian approximations to noncommuting roots. It narrows the next
analytical task to determinant differences or adequately controlled small
singular values of C_N-zA_N in the genuinely noncommuting models.

Neither theorem proves a new full-model Born iff condition, its microscopic
preimage, an open positive phase, or a full-model no-go. The Gaussian proxy
is not counted as an admissible replacement model. The original objective
therefore remains active, with all previously unresolved requirements intact.
