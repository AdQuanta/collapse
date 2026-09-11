# Structural conditions for the projective-root Born profile

Updated 11 September 2026. Exact statements below concern the repository's root-count
observable. Numerical results are finite-size results, not a thermodynamic
theorem. The analysis uses 116 checksum-verified stored profiles and 180 reduced
snapshots of the existing Hamiltonian at detector sizes 6, 8 and 10, plus 219
exact conditional-phase reconstructions at N=15 and 17.

## Result and observable

The strongest structural conclusion is that **bidirectional detector-charge
transfer is necessary in the magnetization-conserving detector/longitudinal-qubit
class, but does not suffice for a Born profile**. The remaining requirement is a
specific balance between the reflection-even and reflection-odd parts of the
projective-root measure. Ordinary symmetry fixes the offset and harmonic parity;
it does not set the Born visibility or eliminate higher odd harmonics.

The production diagnostic is not a probability obtained by preparing an arbitrary
input qubit angle and applying a fixed POVM. Its angle is an output coordinate of
the generalized eigenproblem

\[
U_{10}v_j=\lambda_jU_{00}v_j,\qquad
\theta_j=2\arctan|\lambda_j|,\qquad
U=e^{-itH},\quad \hbar=1.
\]

The homogeneous pencil uses \(\theta=2\operatorname{atan2}(|\alpha|,|\beta|)\)
when an infinite root is present. Indeterminate roots are rejected. Algebraic
multiplicity is retained. The polar histogram and response are

\[
P(\theta)=d^{-1}\sum_{j=1}^d\delta(\theta-\theta_j),\qquad
R(\theta)=\frac{P(\theta)}{P(\theta)+P(\pi-\theta)},\quad d=2^N.
\]

For a finite atomic measure the ratio is understood through reflection-pair
weights, or through the specified histogram. Smooth-density claims concern a
limiting/smoothed distribution, not an exactly continuous finite spectrum.
Consequently the usual affine Bloch-vector formula for a qubit measurement does
not by itself derive this R. Source: `core/relative_evolution_pencil.py`,
`core/sobol_coupling_scan.py::_diagnostics`, and `core/born.py`.

## Exact distribution and harmonic characterization

Put \(A=(P+P\circ\mathcal R)/2\), \(B=(P-P\circ\mathcal R)/2\), with
\(\mathcal R\theta=\pi-\theta\). Then

\[
R=\tfrac12+\frac{B}{2A}.
\]

Thus the necessary and sufficient condition on supported reflection pairs is

\[
\boxed{B(\theta)=A(\theta)\cos\theta},\qquad
\boxed{P(\theta)=(1+\cos\theta)A(\theta),\quad
A(\pi-\theta)=A(\theta)\ge0,\quad\int A=1.}
\]

The constant envelope \(A=1/\pi\) gives the familiar cardioid density, but is
only one sufficient example. Requiring that particular P would incorrectly
reject other Born-like responses. In radius coordinates \(r=\tan(\theta/2)\),
with radial density q, the equivalent condition is \(q(1/r)=r^4q(r)\).
For approximate behavior, write \(B=A\cos\theta+\epsilon\); then exactly
\(R-R_B=\epsilon/(2A)\). Small absolute density errors can therefore create
large response errors in low-mass angular regions.

Independently of H, the ratio definition enforces
\(R(\theta)+R(\pi-\theta)=1\). With full support its cosine expansion is

\[
R(\theta)=\frac12+\frac12\left[
v_1\cos\theta+v_3\cos3\theta+v_5\cos5\theta+\cdots\right].
\]

Exact Born requires \(v_1=1\) and all higher coefficients zero. The offset
is fixed at 1/2 and even cosine harmonics vanish. A shifted fundamental
\(\cos(\theta-\delta)\) would introduce a reflection-even sine component;
there is no freely adjustable phase shift of R within this definition. A fitted
fundamental amplitude larger than one is possible when higher harmonics keep
the complete response between zero and one. Missing support cannot be filled
silently to estimate these coefficients.

A bin-free test follows from \(a_n=\langle\cos n\theta\rangle_P\):

\[
\boxed{d_m=2a_{2m+1}-a_{2m}-a_{2m+2}=0\quad(m=0,1,\ldots).}
\]

Proof: A is reflection-even, so its odd cosine moments vanish; multiply
\(P=(1+\cos\theta)A\) by \(\cos n\theta\) and use the cosine product identity.
Conversely these relations equate every odd cosine moment of B and A cos(theta),
while their even moments vanish by reflection. Completeness of cosine
polynomials on [0,pi] gives equality of the measures. This is necessary and
sufficient for the full hierarchy, not for eight tested moments. An atom at
theta=0 passes the hierarchy but has no broad support: coverage remains a
separate requirement. Tests use independent quadrature for nonconstant A.

## A microscopic Hamiltonian obstruction: one-way charge transfer

In the studied rings and networks,

\[
H_D=-h_z\sum_i Z_i-J\sum_{(ij)}Z_iZ_j
-J_{\pm}\sum_{(ij)}(\sigma_i^+\sigma_j^-+\mathrm{h.c.})
\]

with analogous second-neighbor terms, and

\[
H_q=-h_{z0}Z_0-h_{x0}X_0,\quad
H_{qd}=-g_xX_0\sum_iX_i-g_yY_0\sum_iY_i,
\quad g_{x,y}=J_{x,y}/\sqrt N.
\]

The qubit and detector Pauli eigenvalues are +/-1; sigma^+=(X+iY)/2.
The detector commutes with \(Q_D=\sum_i Z_i\). The qubit-flip block is

\[
(H_{qd})_{10}=-(g_x+g_y)\sum_i\sigma_i^+
                 -(g_x-g_y)\sum_i\sigma_i^-.
\]

If h_x0=0 and g_y=g_x, total \(Z_0+Q_D\) is conserved. U00 preserves
detector charge while U10 raises it by two. If U00 is invertible,

\[
[Q_D,M]=2M,\qquad M=U_{00}^{-1}U_{10},\qquad M^{N+1}=0.
\]

All relative eigenvalues are zero and theta=0. For g_y=-g_x the conserved
charge is \(Z_0-Q_D\); M only lowers detector charge and is again nilpotent.
This is not absence of physical qubit transitions: U10 can have nonzero norm.
The obstruction concerns the spectrum used by this diagnostic. Exceptional
singular-U00 times require a regularity audit; they are not evidence of a broad
well-defined Born spectrum.

For this class, a regular broad root spectrum therefore needs both ladder
directions (g_x unequal to +/-g_y), **or a term breaking the charge grading**.
A transverse qubit field, transverse detector field, or suitable other
charge-changing term can lift it. Changing h_z0, graph connectivity, ZZ
strengths, or magnetization-conserving exchange does not lift it. A longitudinal
Z0 coupling to a detector operator commuting with Q_D also preserves it.
Having both directions does not guarantee Born: the original X-only model
already has both and contains many non-Born examples.

This proves that detector level statistics alone cannot be a sufficient
condition when Hqd is allowed to vary: keep the identical Hd and set g_y=g_x.
It does not by itself falsify a conjecture restricted to g_y=0.

## Exact qubit-axis dependence in the conditional-unitary class

For h_z0=0 and X-only interaction, X0 is conserved. Define

\[
U_\pm=e^{-it(H_D\pm V)},\quad W=U_+^\dagger U_-,\quad
M=(I+W)^{-1}(I-W).
\]

Thus \(\lambda=-i\tan(\varphi/2)\) and
\(\theta=|\operatorname{wrap}\varphi|\). This is exact even when [Hd,V] is
nonzero. It fixes meridional root geometry, but does not imply Born or any
particular P. Azimuthal mixing is not necessary for the polar R requested here.

An additional qubit term -h_x0 X0 gives the exact rigid phase translation

\[
W(h_{x0})=e^{-2ih_{x0}t}W(0).
\]

For the present magnetization-conserving detectors, detector parity flips V
and preserves Hd, giving conjugation-symmetric W spectra. Consequently

\[
a_n(h_{x0})=a_n(0)\cos(2nh_{x0}t).
\]

This directly predicts the response changes without fitting. In the special
sufficient cardioid phase law \(\rho=(1+\cos\varphi)/(2\pi)\), the shift
gives \(R=\tfrac12[1+\cos(2h_{x0}t)\cos\theta]\): a visibility change with
fixed offset. For a general envelope, different harmonic multipliers break
the Born moment recurrence and produce higher response harmonics. A phase
shift of W must therefore not be confused with a free angular phase of R.

A mathematical sufficient Hamiltonian construction also exists: take
[Hd,V]=0, Hq=0, and choose the folded spectrum of 2tV to have
P=(1+cos theta)A with reflection-symmetric A. Then the Cayley identity proves
Born at that time. For example, the continuum density of V on
0<=v<=pi/(2t) can be \(f_V(v)=2t[1+\cos(2tv)]/\pi\).
This is a deliberately prescribed coupling spectrum, not a proof that a local
spin network naturally realizes it or a prescription stable under arbitrary
changes of time and couplings.

## A sufficient phase-law mechanism for approximate Born behavior

In the conditional-unitary class, suppose the auxiliary phase density is the
Poisson kernel, equivalently a centered wrapped Cauchy, with 0<rho<1. Its folded
density and response satisfy exactly

\[
P_\rho(\theta)=\frac{1-\rho^2}{\pi(1+\rho^2-2\rho\cos\theta)},\qquad
R_\rho(\theta)=\frac12\left[1+\frac{2\rho}{1+\rho^2}\cos\theta\right].
\]

This phase law is a sufficient spectral condition for a pure fundamental with
no higher response harmonics. It gives near-unit visibility when rho approaches
one, with maximum Born error (1-rho)^2/[2(1+rho^2)]. Equivalently, a signed Cauchy
relative-root scale a=(1-rho)/(1+rho) gives visibility (1-a^2)/(1+a^2).
The auxiliary moment condition is Re tau(W^n)=rho^n for every n>=0.
Three independent density/ratio checks verify this formula. It is a sufficient
spectral mechanism, not an established universal law for a local spin Hamiltonian.

This also explains why a heavy-tailed P can give a smoother, more Born-like R
than a narrow Gaussian P: a narrow folded Gaussian instead produces, away from
the endpoint image corrections, a sharp logistic crossover around pi/2. The
Gaussian law does not automatically cancel higher response harmonics. At
rho=1 the Poisson-kernel measure collapses to an atom: the pointwise limit of
R and the ratio formed from the weak limiting P do not commute. Finite angular
support must therefore still be checked. A narrow core alone is insufficient.

The best actual ring is not exactly Poisson-kernel distributed: its stored
wrapped-Cauchy fit has rho about 0.6921, which would predict visibility about
0.936 rather than the observed 0.9946. The general reflection-envelope law is
needed even for that case. A good P-family fit cannot replace the R diagnostics.

## Finite longitudinal field, detector dynamics, and coupling scale

A longitudinal qubit field breaks X0 conservation but leaves the charge
obstruction above intact when the coupling is exchange-only. For the X-only
weak-coupling expansion, in the detector energy basis,

\[
M^{(1)}_{ab}=-i e^{-2ih_{z0}t}V_{ab}F_t(E_a-E_b+2h_{z0}),\quad
F_t(\Delta)=t e^{i\Delta t/2}\operatorname{sinc}(\Delta t/2).
\]

This identifies the relevant quantities: accessible detunings and coupling
matrix elements, not unweighted nearest-neighbor level spacings. It explains
suppression of off-resonant contributions and shifts of resonant support. It
does not prove a Gaussian shape or the Born recurrence. Near resonance,
resummation or exact evolution is required; the weak expansion cannot be
extrapolated to arbitrarily long times.

Hd terms and connectivity change both energies and eigenvectors, hence V_ab,
selection rules, and the distribution of conditional eigenphases. Scaling V
changes mixing and phases; it need not improve Born agreement monotonically.
At fixed Hamiltonian ratios, scaling all energies by c is exactly equivalent
to replacing t by ct. Evolution time is part of every condition.

### Why a finite longitudinal field can make P look Gaussian

The evidence supports a crossover in some fixed-detector scans, not a theorem
that every nonzero hz0 produces a wrapped Gaussian. Two logically separate
effects are involved: suppression of large projective roots, and an
approximately Gaussian distribution of the remaining small fluctuations.

An exact solvable limit isolates the first effect. Take
H=Hd-hZ0+X0 V with [Hd,V]=0, h=hz0, and a simultaneous detector eigenstate
with V eigenvalue v. The Hd phase cancels from U10/U00. With
Omega=sqrt(h^2+v^2),

\[
U_{00}\propto\cos(\Omega t)+i\frac{h}{\Omega}\sin(\Omega t),\qquad
U_{10}\propto-i\frac{v}{\Omega}\sin(\Omega t),
\]
\[
\boxed{|\lambda|^2=
\frac{v^2\sin^2(\Omega t)}{h^2+v^2\cos^2(\Omega t)}.}
\]

At h=0 this is the tangent-pole law |lambda|=|tan(vt)|. At h!=0,
|lambda|<=|v/h| and theta<=2 atan(|v/h|): the field removes those poles.
For a bounded finite detector, theta<=2 atan(||V||/|h|). These bounds and the
formula are **exact only in this commuting class**. They provide a concrete
mechanism, not an operator bound for the interacting scans where [Hd,V]!=0.
The general weak-coupling detuning kernel above supplies the corresponding
resonance filtering mechanism; shifting hz0 can also move transitions *into*
resonance and increase spreading. A nonzero field does not uniformly add a
positive floor to every interacting energy denominator.

The second effect needs extra assumptions. For example, in the native Hd=0
limit V=-(Jx/sqrt(N)) sum_i X_i has eigenvalues
v_m=-(Jx/sqrt(N))(N-2m), with multiplicity binomial(N,m). Under normalized
root counting this spectral measure converges to a real Gaussian of variance
Jx^2. If the typical |v|/|h| is small, v^2|t|/|h| is small, and the time is
away from zeros of sin(|h|t), the exact solution gives

\[
\theta\simeq\frac{2|\sin(ht)|}{|h|}|v|,\qquad
\sigma_\theta\simeq\frac{2|J_x\sin(ht)|}{|h|}.
\]

The leading polar law is a **half-normal**. A narrow folded wrapped normal
is indistinguishable from it up to small image contributions. The sequence
of limits matters: the Gaussian limit of v does not justify linearizing its
angle map at arbitrary width or long time. The conditions apply on the bulk
spectral weight; the Gaussian tails require a separate tail estimate for a
uniform error claim. No such uniform estimate is claimed here. At long times
Omega(v)t varies across the spectrum and produces a nonlinear oscillatory
pushforward, which need not be Gaussian even in this simple class.

For interacting detectors, a similar central-limit picture requires weak
enough connected correlations and control of higher cumulants for the
*relevant root-generating variable*. Merely having many spins, chaotic level
spacings, or a Gaussian Hd density of states does not establish that property.
For context, [Hartmann, Mahler and Hess](https://arxiv.org/abs/math-ph/0312045)
prove a Gaussian limit for an energy distribution under specified assumptions;
their theorem is not a theorem for this nonnormal projective pencil. In
particular a circular complex Gaussian lambda would have a Rayleigh modulus,
not a half-normal modulus. Breaking X0 conservation makes this distinction
essential: a Gaussian matrix-entry argument cannot determine P(theta).

There is a direct bin-free shape test. A centered folded wrapped normal obeys

\[
a_n=\langle\cos(n\theta)\rangle=e^{-n^2\sigma^2/2}.
\]

Rechecking the three complete N=17 field scans, including every marker-listed
source checksum, gives the following maximum discrepancy for n=1,...,16 from
the already saved fitted sigma. No width was refitted for this audit.

| nearest-neighbor hz0/hz | WG moment discrepancy | WG sigma (rad) | occupied R RMSE |
|---|---:|---:|---:|
| 0 | 0.270638 | 0.577364 | 0.015923 |
| 0.01 | 0.060634 | 0.436841 | 0.156544 |
| 0.1 | 0.048534 | 0.292165 | 0.227619 |

Thus the Gaussian family describes the moments better as the Born response
deteriorates in these examples; even the finite-field curves are not exact
Gaussians. This is descriptive finite-size evidence, not proof of the
commuting mechanism in an interacting ring. Many other finite-field source
eigenproblems are severely ill-conditioned; the plots retain their caution
markers. In very narrow distributions all fixed-order cosine moments approach
one, so a small absolute moment discrepancy alone is weak shape evidence.
Density overlays and the saved finite-width fit must be inspected as well.
The logarithmic overlays reveal substantial excess tails even when the core
and low-order moments look Gaussian: the field-induced crossover should not
be described as a verified Gaussian law over the full angular range. The
representative P panels use the same displayed density range, 1e-5 to 10 per
radian, to expose that discrepancy without an effectively empty far-tail axis.

Finally, Gaussianization itself does not generate the Born law. Neglecting
wrapped images for a narrow core,

\[
R(\theta)\simeq
\left[1+\exp\left(\frac{\pi(\theta-\pi/2)}{\sigma^2}\right)\right]^{-1},
\]

which is a steep crossover with higher odd cosine harmonics. The expression
assumes the exponentially small tails are actually represented; it cannot
fill unoccupied histogram bins. Detuning can therefore remove the tails that
maintained the Born reflection balance while leaving an apparently Gaussian
central peak.

The exact commuting formula passed nine tests: independent full exponentials
with a nontrivial commuting Hd, the native N=5 ring solver with Hd=0, zero
field/pole/zero-mode limits, the field bound, and input validation. These
checks validate the stated limit; they do not establish an interacting
central-limit theorem or repair ill-conditioned production roots.

## Numerical evidence and diagnostics

The source audit checks every file listed by each case's COMPLETE marker,
normalization, the stored response identity, and occupied-bin RMSE. All 116
profiles are retained, including unfavorable cases. Four network references
and the 40 ring extremes are selected examples, not an unbiased sample for
causal correlation analysis. Histograms use 64 bins; the stored canonical
S_born uses 100. Rebinning explicitly reports the changed score bin count.

The best reviewed second-neighbor ring, config 353, N=17 and t=10^6, has:

| quantity | value |
|---|---:|
| stored S_born (100 bins) | 0.9562368 |
| occupied R RMSE (64 bins) | 0.0081371 |
| reflection coverage | 1.000 |
| fundamental visibility v1 | 0.9945551 |
| norm of v3,v5,v7,v9 | 0.0083287 |
| maximum first-eight Born moment residual | 0.0082162 |
| first two nonconstant P moments a1, a2 | 0.7049283, 0.4180727 |

The last row is far from the cardioid's (0.5,0), while R closely follows Born.
The general-envelope characterization is therefore necessary for interpreting
the actual good cases. Across all fully occupied stored profiles, the maximum
offset deviation is 1.11e-16 and even-cosine coefficient magnitude 8.33e-17,
confirming the algebraic constraints independently of Born agreement.

For config 353, at 32/64/100/128/256 bins, R RMSE is respectively
0.00545/0.00814/0.01176/0.01466/0.01967, with full reflection coverage throughout.
This supports finite-resolution approximate agreement; it does not establish
an exact limiting density. Its unscaled parameters are J=0.2294543588,
Jpm=0.9302783003, J2=0.2112783697, Jpm2=0.9309148623,
hz=0.3344245347, Jx=0.0123335033, Jy=hz0=hx0=0. The actual edge coupling
is Jx/sqrt(17)=0.0029913139. Full precision is in the control config.

The completed N=17 fixed-detector scans supply direct Hq comparisons:

| detector | hz0/hz | stored S_born | 64-bin R RMSE | coverage |
|---|---:|---:|---:|---:|
| nearest-neighbor ring | 0 | 0.9316 | 0.0159 | 1.000 |
| same nearest-neighbor detector | 0.01 | 0.3274 | 0.1565 | 1.000 |
| second-neighbor ring | 0 | 0.9296 | 0.0176 | 1.000 |
| same second-neighbor detector | 0.01 | 0.6139 | 0.0934 | 1.000 |
| pure-Ising ablation of the second-neighbor setup | 0 | 0.1111 | 0.0130 | 0.219 |

The Ising ablation preserves J,hz,Jx and removes Jpm,J2,Jpm2 together. It is a
joint detector ablation, not an isolated attribution to any one removed term.
Its small occupied RMSE is misleading without coverage. Many near-hz0/hz=1
source profiles have severely ill-conditioned relative eigenvector matrices
(maximum 6.20e15); their curves are plotted with explicit caution and are not
treated as verified fine-scale resonance behavior. The descriptive condition
flag at 1e8 is not a forward-error bound or an accuracy guarantee below it.

The controlled local experiment uses the same production ring implementation,
not a surrogate. It fixes config 353's parameters, varies one specified term
at a time (plus two explicit charge-breaking joint controls), and evaluates
N=6,8,10 at t=0.9e6,1e6,1.1e6: 180 snapshots. These are reduced validation
calculations, not replacements for production or a claimed size extrapolation.

- All root counts and homogeneous-pencil/isometry gates pass; maximum
  homogeneous residual 1.07e-14 and column-isometry residual 3.61e-15.
- The parallel-qubit-field prediction agrees in moments through n=16 to
  1.18e-9; maximum angular Wasserstein discrepancy is 5.08e-10 radians.
  The tolerance allows long-time eigenphase roundoff; no fit is performed.
- For Jy=+/-Jx, independently checked charge-grading error is at most 2.46e-8
  and normalized ||(M/||M||)^(N+1)|| at most 2.18e-16. U10 remains nonzero.
  The eigensolver can nevertheless return spurious angles up to about 0.0032
  radians in representative defective cases. Large eigenvector conditioning
  and direct/generalized solver disagreement are recorded, not hidden.
- At N=10,t=1e6, adding a transverse qubit field to the exchange-only model
  restores full coverage but gives R RMSE 0.3765; adding a transverse detector
  field gives full coverage and RMSE 0.2015. Removing the obstruction does
  not establish the Born law.
- The unchanged config-353 coefficients at N=10 have only 0.813 coverage and
  RMSE 0.2633 at t=1e6. The large-N profile is not fixed by symmetry alone.
  Coupling and detector-term perturbations show substantial time dependence
  and no uniformly improving direction in these reduced tests.

## Large-N robustness from the exact qubit-field identity

The identity above permits a controlled Hq perturbation without new large-N
diagonalization: take the complete stored root spectra of nearest-ring config
060 (N=17), second-neighbor config 353 (N=17), and an Erdos-Renyi reference
(N=15), reconstruct the conjugate-paired auxiliary phases, translate by
delta=-2 hx0 t and fold. The 73 fixed shifts per case give 219 reconstructed
profiles. The zero-shift P and canonical score reproduce the saved outputs;
the method was independently checked against full Hamiltonian evolutions at
N=6,8,10 above. Doubling the signed phases preserves normalized multiplicity;
it does not manufacture additional independent samples.

For *any* conjugation-symmetric baseline phase measure, delta=pi/2 makes the
folded P reflection-symmetric, and therefore R=1/2 on support. Delta=pi reflects
the original P and gives R_new=1-R_old. At t=10^6 these shifts require
|hx0|=7.8539816e-7 and 1.5707963e-6 respectively. The source detector and
interaction are unchanged. All three full-support numerical reconstructions
verify R=1/2 at the quarter-circle shift to the 1e-12 gate.

| config-353 perturbation | phase shift | 64-bin R RMSE | coverage |
|---|---:|---:|---:|
| hx0=0 | 0 | 0.008137 | 1.000 |
| magnitude hx0=1.5e-8 | 0.03 | 0.005058 | 1.000 |
| magnitude hx0=5e-8 | 0.10 | 0.006182 | 1.000 |
| magnitude hx0=7.8539816e-7 | pi/2 | 0.353553 | 1.000 |
| magnitude hx0=1.5707963e-6 | pi | 0.705226 | 1.000 |

Thus approximate agreement is not confined to a single sampled hx0 value,
yet is not protected against arbitrary small energy-scale perturbations at a
long fixed time. The relevant small parameter is hx0*t. The family is periodic
in hx0 with period pi/t. These are deterministic fixed-time sensitivities,
not evidence of dephasing, a converged time average, or independent realizations.
The sign of hx0 gives the same folded density for a conjugate-paired baseline.

## Hamiltonian-property map

| property | exact implication or supported effect on R | status |
|---|---|---|
| Definition P/(P+P_reflected) | Offset 1/2, only odd cosine harmonics; no free fundamental phase | exact, independent of H |
| Hq longitudinal and [Hd,Q_D]=0, Hqd one-way ladder | Nilpotent relative matrix; no broad root distribution | exact for regular invertible-U00 times |
| Hqd contains both charge-transfer directions | Removes that particular obstruction; does not set v1=1 | necessary within the stated class, not sufficient |
| Transverse Hq or charge-breaking Hd | Can remove one-way grading; can yield broad non-Born profiles | exact symmetry change, controlled numerical counterexamples to sufficiency |
| Hq field parallel to X in the X-conserving class | Exact auxiliary-phase translation; explicit cosine-moment multipliers | exact, numerically verified |
| Hq longitudinal splitting | Shifts coupling-accessible resonance; modifies visibility and higher odd harmonics | perturbative mechanism plus fixed-detector data |
| Hd exchange, next-neighbor terms, graph | Change transition energies and coupling matrix elements; no universal one-term direction | structural dependence; observational and reduced ablation evidence |
| Hqd scale and evolution time | Control accumulated mixing and conditional phases; effects can be nonmonotonic | exact time/energy scaling plus reduced controls |
| Hd WD versus Poisson spacings | Does not fix interaction selection rules or root reflection balance | not a sufficient descriptor when Hqd varies |
| Full Born moment hierarchy / reciprocal root density | Sets v1=1 and eliminates all higher odd harmonics on support | exact necessary and sufficient spectral condition |
| Poisson-kernel auxiliary phase law | Pure cosine R, visibility 2 rho/(1+rho^2); near-Born for rho close to one | exact sufficient spectral mechanism, microscopic origin not assumed |

## Robustness and what is not established

The reflection construction fixes the offset/harmonic parity. Hamiltonian
symmetry can prohibit broadness, but does not generally protect unit visibility
or the vanishing higher odd coefficients.
The successful finite-size cases are consistent with a particular dynamical
spectral balance and occur in different graph families; they are not evidence
for a universal symmetry-enforced Born phase. The large-N phase reconstruction
demonstrates finite tolerance along a specific Hq direction, together with
complete loss of Born visibility on an energy scale of order 1/t. It rules out
general perturbation protection in Hq and also shows that an isolated sampled
parameter value is not required. Establishing a multidimensional robust region
in local detector/coupling parameters still requires matched production-size
perturbations and stable projective solves. The N=6--10 controls cannot settle
that stronger claim.

No universal sufficient criterion in the bare local couplings is claimed.
The precise necessary/sufficient spectral criterion, the charge obstruction,
and the qubit-axis identity are the established analytical results. The
Hamiltonian-to-Born spectral law for generic interacting networks remains the
unresolved scientific step. Full Bloch-sphere isotropy and a derivation of
measurement probabilities are outside what this polar root diagnostic proves.

## Artifacts and reproduction

- [Representative ring P, R, residual and Fourier panels](reports/born_structure_audit_2026-09-10_v2/ring_representatives.pdf)
- [All three 20-value qubit-field scans and error measures](reports/born_structure_audit_2026-09-10_v2/field_scan_comparison.pdf)
- [General Born-moment test versus the cardioid](reports/born_structure_audit_2026-09-10_v2/ring_moment_tests.pdf)
- [Controlled Hamiltonian error versus parameters, including coverage](reports/born_structure_control_figures_2026-09-10/parameter_errors.pdf)
- [Charge-breaking controls: P, R, residuals and harmonics](reports/born_structure_controls_2026-09-10_v2/controlled_diagnostics.pdf)
- [Exact qubit-field prediction versus numerical R](reports/born_structure_validation_2026-09-10/qubit_phase_shift_prediction.pdf)
- [Large-N qubit-field robustness and visibility loss](reports/born_qubit_phase_robustness_2026-09-10_final/qubit_field_errors.pdf)
- [High-Born, flat-response and reversed-response regimes at N=17](reports/born_qubit_phase_robustness_2026-09-10_final/second_diagnostics.pdf)
- [Finite-field Gaussian agreement, Born error and coverage](reports/finite_field_gaussian_mechanism_2026-09-11_tables_fixed/field_gaussian_audit.pdf)
- [P and R overlays with the Gaussian moment test](reports/finite_field_gaussian_mechanism_2026-09-11_tables_fixed/gaussian_representatives.pdf)
- [Exact commuting-detector field regularization](reports/finite_field_gaussian_mechanism_2026-09-11_tables_fixed/commuting_field_regularization.pdf)
- Network panels: `barabasi_albert_diagnostics`, `erdos_renyi_diagnostics`,
  `random_regular_diagnostics`, and `watts_strogatz_diagnostics` in the audit
  directory, each as PDF/PNG. These pairs differ in realization/parameters and
  sometimes N; they are descriptive examples, not controlled graph substitutions.
- Every stored case has PGFPlots-ready `profile.dat`, `histogram_steps.dat`,
  `R_harmonics.dat`, `P_moments.dat`, and `born_moments.dat`. The best ring is
  `reports/born_structure_audit_2026-09-10_v2/case_082/`.
- `case_metrics.csv`, `bin_sensitivity.csv`, the two source/output manifests,
  control `metrics.csv`, and `identity_checks.json` contain the numeric evidence.

Run under Python 3.11. Output paths must be fresh; earlier data are immutable.
Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 and a writable MPLCONFIGDIR.

```bash
python scripts/analyze_born_structure.py --output reports/<new-audit-directory>
python scripts/run_born_structure_controls.py --output reports/<new-control-directory>
python scripts/validate_born_structure_identities.py \
  --controls reports/<new-control-directory> --output reports/<new-validation-directory>
python scripts/analyze_born_qubit_phase_robustness.py --output reports/<new-phase-directory>
python scripts/run_born_structure_controls.py \
  --from-results reports/<new-control-directory> --output reports/<new-parameter-figures-directory>
python -m pytest -q tests/test_born_reciprocity.py tests/test_born_profile_export.py
python scripts/analyze_finite_field_gaussian.py --output reports/<new-field-directory>
python -m pytest -q tests/test_commuting_detector_field.py
```

The configs fix scope, parameters, sizes, times and bins. Manifests retain input
hashes, source hashes and effective configurations. Raw angles permit bin-free
moments and 32--256-bin sensitivity checks; histogram-only network controls
carry conservative within-bin moment bounds. No random resampling, smoothing,
or fitted parameter search is used by this audit. Three sampled times are a
sensitivity check, not a converged time average. Earlier exploratory output
directories without the `_v2` suffix are superseded by the linked versions.

Validation: 24 focused tests passed; all eight new Python modules compile. The four CLIs pass their help checks. Figures were visually checked, including coverage and the full reversed-response residual range. Generated reports/data remain uncommitted.

The 11 September finite-field addition has nine further focused tests (33
combined), an independent native-solver limit check, and a 60-case source
checksum recheck. Its `_tables_fixed` directory supersedes the earlier versions:
the prior finite-field DAT files were transposed. The figures and numerical
conclusions are unchanged. A regression now rejects header/data column-count
mismatches, and every corrected DAT file was checked by reading named columns.
The new figures, metrics and PGFPlots tables remain generated local artifacts;
the derivation, configuration, analysis code and tests are versioned.
