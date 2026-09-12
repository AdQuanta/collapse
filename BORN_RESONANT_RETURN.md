# Transverse families and resonant return dynamics

12 September 2026. **Partial analytical construction; the exact-Born phase
goal remains open.** This continues the positive ring/chain search in
[BORN_WEAK_COUPLING_SEARCH.md](BORN_WEAK_COUPLING_SEARCH.md). It gives an
exact equivalence of leading transverse responses, an exact return-kernel
representation beyond that approximation, and a physically scaled candidate
neighborhood for the next construction. It does not establish Born behavior
for that neighborhood.

## 1. A constructive extension of the leading response

Use positive Hamiltonian coefficients, Pauli spins, hbar=1, central qubit
first, and its fixed Z readout. Define the detector attachment operators

\[
(L_x,L_y,L_z)=
\begin{cases}
(\sum_iX_i/\sqrt N,\sum_iY_i/\sqrt N,\sum_iZ_i/N),&\text{ring},\\
(X_1,Y_1,Z_1),&\text{chain}.
\end{cases}
\]

Let Mz=sum_i Zi and L±=(Lx±iLy)/2. The detector conserves Mz when its
transverse fields vanish and each bond has Jrx=Jry. Arbitrary longitudinal
fields, interacting ZZ bonds, and first/second-neighbor exchange are allowed.
Both previously audited positive ring leads belong to this detector class.

**Theorem I (leading transverse equivalence).** Suppose [HD,Mz]=0,
[Mz,L±]=±2L±, and consider

\[
H(\epsilon)=I_0H_D+bZ_0+
\epsilon(g_x X_0L_x+g_y Y_0L_y).
\tag{1}
\]

At fixed finite N,t, A is invertible for sufficiently small epsilon, and

\[
A^{-1}C=\epsilon M_1+O(\epsilon^3),\qquad
M_1=-i e^{2ibt}\int_0^t e^{-2ibs}e^{iH_Ds}Qe^{-iH_Ds}ds,
\quad Q=(g_x+g_y)L_++(g_x-g_y)L_-.
\tag{2}
\]

For u=gx+gy and v=gx-gy nonzero, set

\[
a=\tfrac14\log(v/u),\quad D=e^{aM_z},\quad s=u e^{2a},
\qquad s^2=g_x^2-g_y^2.
\tag{3}
\]

The logarithm may be complex. Then the following **matrix identity** holds:

\[
D M_1(g_x,g_y)D^{-1}=s M_1(1,0).
\tag{4}
\]

Consequently the leading projective-root radii, with algebraic multiplicity,
depend on gx,gy through sqrt(|gx²-gy²|). This covers open transverse cones,
not only the gy=0 slice. It is an equivalence of perturbative coefficients,
not an equivalence of the full propagators or a Born theorem.

**Proof.** The first Dyson term gives U10 to first order and U00 to zeroth
order, yielding (2). Conjugation by Z0 changes epsilon to -epsilon, so A
is even and C odd; the matrix remainder is O(epsilon³). The time integral
is a linear map commuting with conjugation by D because [HD,Mz]=0.
Meanwhile D L± D^-1=e^(±2a)L±, and u e^(2a)=v e^(-2a)=s. Applying this
identity under the integral proves (4), including degeneracies and arbitrary
real t,b. No nondegenerate energy-denominator expansion is used. Matrix
error order does not imply the same eigenvalue error order at defective
roots; no such claim is made.

In the HD eigenbasis the filter in (2) is the entire function
t exp(i Delta t/2) sinc(Delta t/(2pi)), Delta=Ea-Eb-2b. Complex phases are
retained. The unitary spectral basis change is common to the two matrices.

A convenient comparison holds g_eff fixed and varies
gx=g_eff cosh(eta), gy=g_eff sinh(eta). Then D=exp(-eta Mz/2), s=g_eff,
and every leading spectrum is identical. The condition number of D on the
full detector space is exp(N|eta|); it is not uniformly well-conditioned in
N. Exact finite-N spectral equality remains true, but small matrix errors
cannot be transported through this similarity with a size-independent bound.

Adding a weak gz term leaves the first derivative (2) unchanged, but generally
introduces a second-order matrix correction. Generic transverse detector
fields or Jrx!=Jry remove the charge condition. These are directions the
open-phase proof must eventually cover, not directions excluded from the
positive search.

## 2. Exact return dynamics for the full requested families

For arbitrary XYZ detector terms and arbitrary central field, write

\[
H=\begin{pmatrix}H_+&Q^\dagger\\Q&H_-\end{pmatrix},\quad
H_\pm=H_D\pm(h_{0z}I+g_zL_z),\quad
Q=(h_{0x}+ih_{0y})I+g_xL_x+i g_yL_y.
\tag{5}
\]

This is an exact decomposition of the user's models, including gz/N on the
ring and the unscaled chain endpoint. No charge symmetry is required.
For z off the real axis, define

\[
T(z)=(z-H_-)^{-1}Q,\qquad
\Sigma(z)=Q^\dagger T(z),
\]
\[
G_{00}(z)=[z-H_+-\Sigma(z)]^{-1},\qquad
G_{10}(z)=T(z)G_{00}(z).
\tag{6}
\]

**Exact resummation.** These are the first block column of (z-H)^-1.
Multiplying by z-H proves both identities: the lower equation gives
G10=T G00 and the upper equation gives the Schur complement in (6).
Because H is Hermitian, all inverses exist off the real axis. This remains
valid at exact degeneracies, arbitrarily small real spectral spacings and
finite coupling. Sigma is quadratic in Q for fixed H-, while its retention
inside the inverse includes all repeated returns; truncating that inverse
would lose the resummation.

The imaginary part obeys the exact causality identity

\[
\operatorname{Im}\Sigma(E+i\delta)
=-\delta Q^\dagger[(E-H_-)^2+\delta^2]^{-1}Q\le0,
\quad\delta>0.
\tag{7}
\]

The positive operator-valued measure Q† P_-(dE) Q determines Sigma. The
transfer T must also be retained to reconstruct C; scalar spectral weights
alone do not specify this first block column.

The equivalent exact time-domain equations, with A(0)=I,C(0)=0, are

\[
C(t)=-i\int_0^t e^{-iH_-(t-s)}Q A(s)ds,
\]
\[
\dot A(t)=-iH_+A(t)-\int_0^t
Q^\dagger e^{-iH_-(t-s)}Q A(s)ds.
\tag{8}
\]

Equations (6) or (8) are constructive starting points for resonant dynamics
without assuming a real-axis gap. For finite N the time-domain blocks can
also be recovered by integrating e^-izt G(z)/(2pi i) on a counterclockwise
contour enclosing the full spectrum. One must reconstruct A(t),C(t) before
taking their generalized roots: the roots of a resolvent pencil at one z
are not the physical time-evolution roots. Delta in (7) is a resolvent
evaluation coordinate, not a physical damping term or a time average.

## 3. Which terms the leading equivalence omits

In the charge-conserving setting with zero transverse central fields,
write R_-=(z-H_-)^-1. With real u,v, direct expansion gives

\[
\Sigma=u^2 L_-R_-L_+ +v^2 L_+R_-L_-
+uv(L_-R_-L_-+L_+R_-L_+).
\tag{9}
\]

Along gx=g cosh(eta), gy=g sinh(eta), uv=g² is fixed, but

\[
\Sigma_\eta-\Sigma_0=g^2\big[
(e^{2\eta}-1)L_-R_-L_+
+(e^{-2\eta}-1)L_+R_-L_-\big].
\tag{10}
\]

Thus equal leading transverse spectra still permit different second-order
return operators. This identifies the matrix terms to keep when extending
the positive X-only leads to independent coupling directions. It does not
determine the eventual Born profile, and neither (9) nor (10) replaces the
full self-consistent inverse in (6) near resonance.

## 4. A candidate scale for a finite-width search

**Dimensional estimate and hypothesis, not a derived relaxation rate.**
For a fixed microscopic detector energy E_D, a return self-energy away
from singular spectral structure has the scale g²/E_D. Its actual value
depends on the matrix spectral measure in (7); E_D does not substitute for
a gap or a detector correlation-time calculation.

The two saved positive ring references were previously compared using
h0z/hz. Choose, solely for a reproducible dimensional comparison, E_D as
the largest absolute detector field or Pauli bond coefficient of each
reference. Their scales are:

| Reference | E_D | |gx|/E_D | gx²/E_D | t gx²/E_D at t=10^6 |
|---|---:|---:|---:|---:|
| Nearest ring | 0.04697738 | 0.02228805 | 2.333636e-5 | 23.33636 |
| Second-neighbor ring | 0.16899859 | 0.00710316 | 8.526796e-6 | 8.526796 |

The scan values h0z/hz=10^-4 and 10^-3 correspond to |h0z|/(gx²/E_D)
of 0.2013 and 2.0131 for the nearest ring, and 0.1683 and 1.6833 for the
second-neighbor ring. Their apparently tiny detunings therefore already
probe an order-one range of the second-order energy estimate. This is
consistent with return dynamics mattering; it is not proof that those
scans measure a Lamb shift or a kinetic limit.

The resulting **candidate family to construct and assess** is

\[
H_D=E_D\widehat H_D,\qquad
g_\alpha=\epsilon E_D c_\alpha,\qquad
h_{0\alpha}=\epsilon^2 E_D b_\alpha,
\tag{11}
\]

with small fixed epsilon, independent c_x,c_y,c_z and b_x,b_y,b_z in
finite intervals, and generic XYZ detector parameters near the interacting
references. Ring and chain normalizations remain those in section 1.
For fixed epsilon>0, an open box in these coordinates has finite physical
width independent of N, including all three qubit-field directions. It
does not impose an exact resonance or a coupling-ratio equality. This
describes a legitimate candidate neighborhood; **no point in its generic
interior is yet certified to satisfy the exact-Born law**.

The auxiliary time tau=epsilon² E_D t organizes the return dynamics. A
weak-coupling kinetic limit epsilon->0 at fixed tau would not by itself
prove the requested N-first, t->infinity law at fixed weak epsilon. That
additional uniformity and the root logarithmic-tail control remain required.

## 5. Numerical verification and limits

Eleven focused tests verify (6) against an independent full solve at exact
degeneracy and three complex spectral points, (7), (4) for interacting
ring/chain detectors and three sign regimes, the derivative (2) at three
coupling refinements, and exclusion of the singular gauge boundary from
the invertible formula. They pass; the combined relevant suite passes 50 tests.

A reduced verification uses the actual second-neighbor reference detector
coefficients, ring N=5,6,7 and matched open-chain N=3,4,5, eta=0,0.5 and
t=10^3,10^4,10^5,10^6. Each of the 48 snapshots uses production homogeneous
QZ for the full propagator and leading pencil. All algebraic roots are
retained. The invariant comparison is the bounded radial potential J of
[BORN_NONNORMAL_LIMIT.md](BORN_NONNORMAL_LIMIT.md), on nine specified
log-radius points from -4 to 4; it is not a supremum over the continuous axis.

The leading gauge potentials agree to 8.89e-16. Full-dynamics potentials
along the same leading-equivalent directions differ by up to 0.226755 for
the ring and 0.655162 for the chain. This verifies that return dynamics
cannot be omitted in these late-time comparisons. Maximum full/leading
potential differences are 0.288424 and 0.477046. These reduced sizes are
not evidence against a thermodynamic positive phase.

Maximum left/right homogeneous-QZ residual is 2.311e-15; the exact
Schur-column residual is 2.209e-15 and its relative difference from an
independent eigensystem resolvent is 4.870e-14. The normalized Hamiltonian
eigen-residual is at most 3.214e-15 and orthogonality error 1.801e-14.

Reflected polar coverage is only 0.0625–0.3125, so all global histogram
errors remain undefined, without empty-bin replacement. Every record
includes occupied errors, all eight raw moment residuals and canonical
100-bin S_born. The saved high-N ring results remain the positive leads;
these new small systems verify the analytical reduction and its limitations.

Reproduce using Python 3.11:

```bash
python -m pytest -q tests/test_resonant_return.py tests/test_ring_chain_weak_coupling.py tests/test_born_reciprocity.py tests/test_relative_evolution_pencil.py
python scripts/verify_born_resonant_return.py --output reports/born_resonant_return_fresh
```

Configuration: `configs/born_resonant_return_2026-09-12.json`. Exact
coefficients, all times and sizes, code/config/source hashes, package
versions, eigensystem/resolvent/QZ residuals and output hashes are saved.
Derived arrays, JSON and PDF/PNG are in
`reports/born_resonant_return_2026-09-12_verified/`; prior data are untouched.
No production campaign was submitted.

**Remaining proof obligation.** Determine the thermodynamic matrix transfer
and return structure for a nonempty neighborhood in (11), prove that its
time-domain pencil obeys an independently characterized Born condition,
and establish late-time and perturbation stability. The transverse
equivalence and Schur resummation are tools for that positive construction,
not substitutes for the requested iff/open-phase theorem.
