# Exact weak and strong Born: limits of the finite root-count model

11 September 2026. This answers the revised weak/strong-Born objective with
the user's clarification: **preserve the finite model and prove its exact
limits**. No continuum limit, continuous ensemble average, smoothing kernel
or alternative measurement probability is introduced.

**Result:** neither an exact Born curve on an angular interval nor an exactly
uniform continuous azimuth can be produced by the implemented finite
root-count/histogram outputs. Consequently the requested global weak- and
strong-Born realization classes are both empty. This is a property of this
diagnostic, not a limitation on ordinary quantum Born probabilities: a finite
qubit can have an exactly cos-squared measurement probability as a function
of a continuously varied *input* state. That is not the observable computed
here.

## 1. Model-native measures, preparation and readout

For N detector spins let d=2^N and U=exp(-itH). The code partitions U in the
qubit Z basis and solves U10 v=lambda U00 v. A regular generalized pencil
has d roots with algebraic multiplicities, allowing infinite projective
roots. Indeterminate roots must be rejected. The production raw-count
diagnostics use finite roots and record any exclusions.

The blue branch maps a root to

\[
|q(\lambda)\rangle=(|0\rangle+\lambda|1\rangle)/\sqrt{1+|\lambda|^2},
\quad \theta=2\arctan|\lambda|,\quad \phi=\arg\lambda.
\]

Its red branch is antipodal: (theta,phi)->(pi-theta,phi+pi). Define

\[
\mu_b=\frac1d\sum_j\delta_{(\theta_j,\phi_j)},\qquad
\mu_r=T_*\mu_b,\qquad \nu=\tfrac12(\mu_b+\mu_r).
\]

P is the theta marginal of mu_b. R is the ratio of blue counts to total
blue-plus-red counts in a theta bin. It can be interpreted as a conditional
branch-label frequency under this *chosen equal-root, equal-branch measure*.
It is not derived from a supplied detector density matrix, detector-state
sampling distribution or measurement instrument.

Source tracing:

- `core/analysis.py::get_initial_qubit_states_from_eigenvalues` derives the
  qubit states from roots; `phi0` and `phi1` there denote kets, not azimuths.
- `core/anisotropic_sweep.py::_bloch_branches` constructs blue points and
  their negatives.
- `core/sobol_coupling_scan.py::_diagnostics` uses equal root counts, stores
  phi=arg(lambda), and reports the second azimuthal harmonic.
- `core/born.py::phase_angles_from_eigenvalues` optionally pools antipodes;
  `phase_uniformity_from_eigenvalues` defaults to that pooled **marginal**
  azimuth distribution. Its histogram score is a finite-resolution proxy.

Accordingly the directly implemented azimuth measure is nu_phi, the pooled
marginal. Native operational strong Born would require weak Born and
nu_phi=dphi/(2pi). Requiring uniformity conditional on theta or branch is
stronger than the current marginal diagnostic; those variants are also
treated below and have the same finite-model impossibility result. The code
does not specify a physical preparation prior that selects a different
continuous azimuth measure.

At the north/south poles azimuth is undefined. Assigning arg(0)=0, or an
arbitrary label to an infinite root, does not give physical phase data.
Azimuth statements apply to nonpolar roots. An all-polar distribution has
no physically meaningful azimuth distribution and cannot supply the required
global Born curve. The plotted azimuth diagnostics exclude sin(theta)<=1e-6
and report the excluded fraction; P and R are not changed by that plot cut.

The Bloch azimuth phi must also not be confused with the auxiliary-unitary
eigenphase varphi in W=U+ dagger U-. At hz0=0 with X-only coupling,
lambda=-i tan(varphi/2): a broad varphi spectrum still confines phi to two
meridians.

## 2. The nontrivial iff identity, and its domain

Write R=dP/d(P+reflection(P)), defined almost everywhere with respect to
that finite positive measure. For an arbitrary probability measure P,

\[
R=\frac{1+\cos\theta}{2}\quad(P+\mathcal RP)\text{-a.e.}
\iff P=(1+\cos\theta)A,\quad
A=\mathcal RA\ge0,\quad A([0,\pi])=1.
\]

Proof: take A=(P+reflection(P))/2 and solve the Radon-Nikodym identity;
reflection symmetry proves the converse and normalization. With
a_n=integral cos(n theta) dP, equivalently all cosine moments satisfy
2a_(2m+1)-a_(2m)-a_(2m+2)=0 for every m>=0. Indeed, the odd part
of P must equal cos(theta) times its even part; testing against every odd
cosine gives this hierarchy by the cosine product identity. Even tests
vanish by reflection parity, and completeness of cosine polynomials on
[0,pi] gives the converse.
The existing `born_reciprocity` tests verify this law independently for
nonconstant envelopes. A finite prefix is necessary, not sufficient.

For the finite root measure, let m(theta) be the integer multiplicity of an
angle. At a nonempty reflected pair this iff reduces to

\[
\frac{m(\theta)}{m(\theta)+m(\pi-\theta)}
=\cos^2\frac\theta2.
\]

At an interior pair with nonzero counts, this requires
tan^2(theta/2)=m(pi-theta)/m(theta). At zero, mass may occur without a
reflected pi atom; a pi atom alone violates the identity. An equatorial
atom obeys it automatically. These are exact **finite-support** conditions,
but do not determine R on an interval outside that finite support. The
revised objective explicitly excludes equality only at sampled angles.
Choosing a Born-valued extension on unobserved angles would add a readout
rule rather than establish it from the code.

There is even a native family with exact equatorial support: Hq=0, hz=0,
uniform X coupling, odd N, arbitrary isotropic detector exchange, and
g t=pi/4. The exact isotropic formula puts all roots at theta=pi/2, where
the finite-support response equals 1/2. It is neither a global Born curve
nor azimuthally uniform. It illustrates why support qualifications matter.

## 3. Global weak-Born no-go theorem

**Theorem W.** For any finite number of bins of positive width, no choice of
finite Hamiltonian, propagator, graph, couplings, time or root weights makes
the histogram ratio equal cos^2(theta/2) throughout an occupied nontrivial
interval. Missing bins do not supply an equality there.

Proof: the histogram ratio is constant in each bin. The Born target is
strictly decreasing on (0,pi). These cannot agree throughout any bin of
positive width. The statement also holds if real-valued root weights replace
counts, so it is not only a counting-arithmetic effect.

There is a stronger arithmetic obstruction at the code's bin centers. A
count ratio is rational. At theta_k=(2k+1)pi/(2B), a rational Born value
would require rational cos(theta_k). Since exp(i theta_k) is a root of
unity, 2 cos(theta_k) is an algebraic integer. If rational it must be one
of -2,-1,0,1,2. Midpoints cannot be 0,pi/3,2pi/3 or pi; pi/2 is a midpoint
only for odd B. Therefore:

- For **even B**, exact equality at even one occupied bin center is
  impossible for ideal real-number Born values and integer root counts.
- For **odd B**, the central pi/2 bin is the only possible exception.

This applies to the routine 48-, 64- and 100-bin analyses. Floating-point
coincidence or rounded printed values cannot establish exact real equality.

The best possible uniform-bin errors, even allowing arbitrary real bin
constants, quantify the obstruction. For B>=2, x=pi/(2B),

\[
\epsilon_{\infty,\min}=
\begin{cases}\frac14\sin(\pi/B),&B\ \text{even},\\
\frac12\sin(\pi/(2B)),&B\ \text{odd},\end{cases}
\qquad
\epsilon_{\mathrm{RMS},\min}
=\sqrt{\frac{1-(\sin x/x)^2}{8}}.
\]

Supremum and RMS optima use different constants. The supremum-optimal
constant is the mean of the two endpoint target values; the RMS-optimal
constant is the integral mean in each bin. Integrating the squared target
and summing cosine squares gives the RMS expression. RMS here is with
respect to uniform dtheta/pi, over entire bins, not bin centers. At B=1
the two bounds are 1/2 and sqrt(1/8).

At B=64 these lower bounds are **0.0122669** in supremum and **0.00500976**
in RMS. A numerical center-error below either bound is not a contradiction:
it measures a different object. Refining B can reduce these step-function
bounds, but with a fixed finite root count eventually leaves missing bins.

## 4. Strong-Born no-go theorem

**Theorem S.** Any nonempty finite azimuthal root measure differs from Haar
measure dphi/(2pi), with exact total variation distance 1.

Proof: the finite support F has empirical probability one and Haar measure
zero. The supremum-over-events definition of total variation therefore
attains one. Arbitrary positive state weights, degeneracies, graph changes
and pooling antipodes do not change this argument. The same proof applies
after conditioning on any theta bin or branch with nonzero finite support.

For a general circle measure nu, the exact harmonic iff is

\[
\nu=\frac{d\phi}{2\pi}
\iff \int e^{im\phi}\,d\nu=0\quad\text{for every }m\ne0.
\]

Completeness of trigonometric polynomials proves the converse. Thus the
formal native strong criterion is C_W plus this full hierarchy for nu_phi;
conditional versions require it for each relevant conditional measure.
All are unattainable by a finite nonpolar root cloud. Conditional uniformity
would imply marginal uniformity, so it cannot evade the no-go result.

Finite checks can be misleading. A uniform M-point circular grid has zero
harmonics 1,...,M-1 and a perfectly flat M-bin histogram, but its Mth
harmonic has magnitude one and its continuous TV distance is still one.
Pooling antipodes sets every odd azimuthal harmonic to zero automatically;
the first harmonic alone is therefore particularly weak evidence.

For L samples in B_phi bins, even a flat histogram is attainable only if
B_phi divides L. Its minimum histogram TV is

\[
\mathrm{TV}_{\mathrm{bins},\min}
=\frac{r(B_\phi-r)}{B_\phi L},\qquad r=L\bmod B_\phi.
\]

This follows by assigning floor(L/B_phi) or ceil(L/B_phi) samples per bin.
For the standard full-root antipodal cloud L=2^(N+1), the default 36-bin
histogram cannot be exactly flat. Excluding roots changes L but never
removes the continuous-measure obstruction. Continuous TV remains one at
every finite size even for sequences converging weakly to Haar measure.

## 5. Complete realization classification under the preserved finite model

For the stipulated global definitions,

\[
\mathcal H_{\rm strong}=\mathcal H_{\rm weak}=\varnothing,
\qquad \mathcal H_{\rm strong}\subseteq\mathcal H_{\rm weak}.
\]

There is no constructive nonempty weak or strong family to supply without
changing the observable or taking an expressly excluded limit. Likewise
continuous-uniform-phi-only is unrealizable. Every admissible finite output
is in the **neither** class under these exact global definitions. The
equatorial example above belongs only to a weaker finite-support notion;
the flat 32-bin phase example belongs only to a finite-resolution notion.
Neither is relabeled as a solution to the stronger target.

Calling a microscopic feature "necessary" for a nonexistent class would
be vacuous. The useful classification instead distinguishes the universal
obstruction from effects on the attainable finite diagnostics:

| property | weak diagnostic | strong/azimuth diagnostic |
|---|---|---|
| Finite bin widths | universally prohibit the exact global curve | already violate weak requirement |
| Finite nonpolar root support | only finite-support equality is meaningful before binning | universally prohibits continuous uniformity |
| Hq/Hd/Hqd symmetries, conserved charges, invariant subspaces | act through the block pencil; can restrict roots or make terms cancel | can confine phases or force some harmonics to vanish, never all Haar conditions |
| Gaps, degeneracies, resonances, detuning | influence the propagator; no choice removes the finite-output obstruction | same; degeneracy does not create a continuous measure |
| Eigenvectors/localization | projected blocks depend on eigenvectors, not just eigenvalues; localization is basis dependent | can affect phase correlations through those blocks |
| Graph topology, connectivity, graph spectrum | relevant through Hamiltonian blocks; graph spectrum alone is insufficient | no topology bypasses finite support |
| Attachment sites and coupling magnitudes/signs/phases | can alter radii, reflected counts, and finite-resolution R | can alter arg(lambda), preferred directions and conditional anisotropy |
| Detector initial state | not an input probability weight in this root-count statistic | assigning finite state-dependent weights still leaves a finite measure |
| Qubit initial state | kets are derived from roots rather than scanned as the independent input theta | phi is a coordinate of those derived kets |
| Readout | qubit Z block basis and branch construction are fixed; changing them changes the diagnostic | same, including pole-coordinate conventions |
| Time | affects U and all finite profiles; no special time evades Theorems W/S | recurrence or dephasing at one finite time is not Haar uniformity |

## 6. Preserved equivalences and deformations

Detector-unitary conjugation, including site permutations, gives simultaneous
similarity of U00 and U10 and preserves every root. Global energy shifts,
inverse Hamiltonian/time rescaling, and detector-only terms commuting with
the rest of H also preserve the pencil spectrum. A tensor-product spectator
replicates roots with equal multiplicity and preserves the normalized
measure. An arbitrary direct-sum extra sector need not do so. Different
unitary propagators with equivalent projected pencils have the same root
diagnostic even if their other spectral/topological details differ.

A qubit Z-axis basis rotation shifts every root azimuth by a common angle,
preserving radii and azimuthal uniformity/nonuniformity. More general qubit
rotations or readout changes need not preserve the polar profile. Changing
phases at fixed root radii preserves weak *finite-resolution* diagnostics
while changing azimuthal ones; it does not create a global exact weak case.
No transformation can preserve an existing exact weak case while destroying
exact strong behavior here, because no such exact global cases exist.

At the measure level reflection pairing fixes R(theta)+R(pi-theta)=1,
hence offset 1/2 and zero even cosine modes. The natural even 2pi extension
of the polar function has zero sine modes by definition. On [0,pi], using
both arbitrary sine and cosine series without an extension convention is
redundant and does not uniquely define the requested coefficients. The
remaining Born requirement is unit fundamental visibility and zero higher
odd cosine modes; reflection alone does not enforce it. Atomic mass exactly
on bin boundaries can introduce additional half-open-bin artifacts, which
must not be interpreted as physical symmetry breaking.

Writing P=(1+cos(theta))A+epsilon with reflection-even A gives
R-R_B=(1/2)d epsilon/dA when epsilon is the reflection-odd imbalance.
For densities this is epsilon(theta)/(2A(theta)) wherever A>0. Finite
sampling, narrow tails and unoccupied regions can amplify ratio deviations.
Changing finite root angles across a bin edge produces discontinuous count
changes; a universal differentiable response of the *histogram* to a
Hamiltonian parameter cannot be assumed. The earlier analytical field and
isotropic-cancellation identities describe actual microscopic deformations
without implying exact global equality.

## 7. Validation and artifacts

Fourteen focused tests check the optimal bounds by independent quadrature,
count-TV minima by exhaustive small count inventories, an antipodal
first-harmonic false positive, the 32-point circular-grid adversary, and the
native equatorial-support family with a generalized-pencil residual below
1e-11. The combined focused suite passes **57 tests**.
Four checksum-verified N=17 native cases are reanalyzed, including the
best reviewed second-neighbor ring. Whole-bin errors are integrated
analytically and maximized at bin endpoints, stronger than a dense-grid
approximation. Native phase plots include harmonics and a conditional
theta/phi visualization; exact continuous TV is reported as an analytical
result, separately from numerical histogram TV.

All four native cases have 131,072 roots and full 64-bin polar coverage.
The following errors compare R with the Born target; whole-bin RMS uses
uniform dtheta/pi.

| N=17 case | center maximum error | whole-bin maximum error | whole-bin RMS | second azimuth harmonic |
|---|---:|---:|---:|---:|
| Nearest ring, hz0/hz=0 | 0.040607 | 0.051886 | 0.016706 | 1.000000 |
| Nearest ring, hz0/hz=0.01 | 0.278805 | 0.290920 | 0.156643 | 0.114216 |
| Nearest ring, hz0/hz=0.1 | 0.561205 | 0.573365 | 0.227687 | 0.019220 |
| Second-neighbor ring 353, hz0=0 | 0.016300 | 0.026112 | 0.009549 | 1.000000 |

The best polar case is strongly azimuthally anisotropic. Its phase plot
excludes four near-polar roots (fraction 3.05176e-5). Two meridians lie on
histogram boundaries, so roundoff spreads their counts into adjacent bins;
that does not establish additional physical directions. Finite hz0 reduces
the azimuthal anisotropy in these examples while worsening polar Born
agreement. This is a measured comparison, not a universal monotonicity law.

For fully covered profiles define an exact strong discrepancy as the maximum
of the whole-interval weak supremum error and continuous-azimuth TV. It is
**one in every case**, analytically, even when the histogram looks flat.
An unsupported polar profile instead has undefined global weak error.

```bash
python scripts/analyze_exact_born_feasibility.py --output reports/<fresh-limits-audit>
python -m pytest -q tests/test_exact_born_limits.py
```

- [Finite-theta error bounds and the best reviewed profile](reports/exact_born_finite_model_limits_2026-09-11_final/finite_theta_limits.pdf)
- [Native azimuth distributions and harmonics](reports/exact_born_finite_model_limits_2026-09-11_final/native_phi_diagnostics.pdf)
- [Conditional azimuth of the high-Born second-neighbor ring](reports/exact_born_finite_model_limits_2026-09-11_final/conditional_phi.pdf)
- [Adversarial flat histogram that is not continuous uniformity](reports/exact_born_finite_model_limits_2026-09-11_final/false_uniformity_certificate.pdf)
- [Numerical and analytical error summary](reports/exact_born_finite_model_limits_2026-09-11_final/summary.json)
- [Previous polar residuals and harmonic diagnostics](reports/born_structure_audit_2026-09-10_v2/ring_representatives.pdf)

The earlier approximate-Born findings remain finite-resolution results.
The exact statements established here are the unattainability theorems and
the qualified finite-support iff identity. They neither manufacture an
exact positive family nor infer failure of the ordinary quantum Born rule.
