# A constructive finite Hamiltonian family with Born-like polar response

11 September 2026. This study uses the user's explicitly selected acceptance
gate, now recorded in [RESEARCH_STATE.md](RESEARCH_STATE.md). It preserves the
implemented finite equal-root counting measure. No continuum distribution,
continuous averaging, fitted response, or alternative POVM is substituted.

**Result.** The effective iff condition is a finite set of projected-root
count and moment inequalities. A nonempty native Hamiltonian family satisfies
them analytically: unequal central X couplings, arbitrary commuting detector
X/XX dynamics on the supported graphs, arbitrary detector size N>=13, and
an explicit open neighborhood of coupling and central-field perturbations.
Its seed has full coverage, R RMSE 0.0177314, maximal moment residual
0.0417128, and canonical S_born=0.9456796. The guarantee is a rational
combinatorial certificate, not a fit or inference from random successes.

The family is a sufficient subset of the full microscopic preimage. It
proves that neither detector chaos nor a particular detector graph is
necessary for this **polar** gate. It does not show that generic Hamiltonians
pass, or that this geometry defines physical measurement probabilities.

## 1. Exact meaning of the acceptance test

RESEARCH_STATE originally specified the target but no binary tolerances.
The user selected the previously declared audit gate; its conventions are:

* B=64 uniform bins on [0,pi], no pseudocount, complete blue-plus-red coverage.
* Target b_k=(1+cos theta_k)/2 at theta_k=(k+1/2)pi/B.
* sqrt(mean_k (R_k-b_k)^2)<=1/20.
* max_{m=0,...,7}|d_m|<=1/20, with
  a_n=d^(-1) sum_j cos(n theta_j) and d_m=2a_(2m+1)-a_(2m)-a_(2m+2).

The target has offset 1/2, cosine amplitude 1/2, phase zero, and no higher
harmonics. The gate allows deviations bounded by these two metrics; it does
not separately require exact harmonic zeros. Normalization uses all d=2^N
roots with algebraic multiplicity. Missing bins fail rather than receive a
fictitious interpolated probability. Exact zero/infinite projective roots
belong to theta=0/pi; indeterminate roots are invalid.

The displayed S_born is the existing `core/born.py` diagnostic at **100 bins**:

\[
S_{\rm born}=1-2\Delta\theta\sum_k
 |R_k-\cos^2(\theta_k/2)|\sin\theta_k.
\]

Its native empty-bin value is 1/2. Consequently it is reported with coverage
and cannot replace the gate. The score is not clipped or recalibrated here.
All P/R diagnostic plots show 64 bins and explicitly label the 100-bin score.

Dense-angle validation additionally uses exact whole-bin supremum and RMS
errors, including bin endpoints. These are stronger than checking a dense
finite grid, but are distinct from the accepted bin-center RMS. For the seed
they are 0.0379321 and 0.0183972. The
[finite-model no-go study](EXACT_BORN_FINITE_MODEL_LIMITS.md) remains valid:
this accepted approximate profile is not globally exact Born behavior.

## 2. Reduction and effective iff theorem

Use the central qubit first, Pauli eigenvalues +/-1, hbar=1, and the
production qubit-Z block convention:

\[
U(t)=e^{-itH}=\begin{pmatrix}A&B'\\C&D\end{pmatrix},
\qquad Cv=\lambda Av,\qquad \theta=2\arctan|\lambda|.
\]

For homogeneous generalized eigenvalues (alpha,beta), use
theta=2 atan2(|alpha|,|beta|). The companion branch has angle pi-theta.
The qubit kets are derived from the roots; a continuously scanned input
state or detector density matrix is not an input to this root statistic.
Sources are `core/relative_evolution_pencil.py`, `core/projective_roots.py`,
`core/analysis.py`, and `core/born.py`. The production pencil is the fixed
input-pole convention identified in `manuscript/audits/THEORY_AUDIT.md`.

Let n_k and nbar_k be the exact blue and antipodal-red counts in the actual
half-open bins. Put s_k=n_k+nbar_k. The broadest effective condition for this
declared gate is

\[
\boxed{C_B:\quad s_k>0\ (\forall k),\quad
 \sum_k\left(\frac{n_k-b_ks_k}{s_k}\right)^2\le\frac B{400},
 \quad |2a_{2m+1}-a_{2m}-a_{2m+2}|\le\frac1{20}\ (0\le m\le7).}
\]

**Iff proof.** The implemented readout gives R_k=n_k/s_k, so the second
inequality is exactly the squared RMS criterion multiplied by B. The first
is exactly full coverage. The last inequalities are exactly the raw-root
moment criterion. Substitution proves sufficiency; applying those same
identities to any accepted output proves necessity. No additional symmetry,
spectral-spacing, graph, eigenvector, or preparation hypothesis enters.

The regular projected pencil determines all inputs to C_B. A smaller
sufficient object is the vector of count ratios and support indicators,
together with the eight moment residuals. The finite histogram alone does
not determine the raw-angle moments. The generic effective quantum channel
for an arbitrarily chosen detector state is not the relevant object here.

Before binning, the stronger measure identity is
P=(1+cos theta)E with reflection-even E=(P+reflection(P))/2. It is iff Born
equality on supported reflection pairs, and its complete infinite cosine
moment hierarchy is exact. Eight tested moments are not that hierarchy.
Half-open-bin atoms can also make nbar differ from the reversed n array;
the theorem uses actual antipodal counts rather than assuming reversal.

## 3. Native commuting class and a microscopic formula

Consider the existing central-X, central-field and detector-X/XX channels:

\[
H=K-h_{x0}X_q-h_{z0}Z_q-X_q\sum_{i=1}^N g_iX_i,
\quad
K=-\sum_i f_iX_i-\sum_{(ij)\in G}\kappa_{ij}X_iX_j.
\]

All signs here match the native negative Pauli coefficients. The g_i are
the **effective** coefficients; a campaign's quoted collective Jx carries
its separate 1/sqrt(N) scaling. The backend already allows site-dependent
Jx and fields as disorder realizations. The current Jxx interface has a
common edge coefficient on each generated graph. Every supported graph and
every such common coefficient is included. The operator proof also permits
independent XX edge weights, but that larger weighting interface is not
claimed to be exposed by the current generator.

More broadly, the proof needs only [K,V]=0 for V=sum_i g_i Xi, with K a
detector-only Hamiltonian built from allowed channels. The X/XX expression
is an explicit freely variable subset of that commutant. Thus the family
may include other native commuting terms, particularly arbitrary dynamics
on zero-coupled tensor-factor spectators; it is not restricted to K being
diagonal in every individual Xi.

Every term of K commutes with every X_i and with the remaining H. Thus
U=e^{-itK}U_rest, and the same invertible detector factor multiplies A and C
on the left and cancels from their pencil. In the joint detector X basis,
each sign vector s_i=+/-1 has v_s=sum_i g_i s_i and a two-dimensional block

\[
H_s=-(h_{x0}+v_s)X-h_{z0}Z,\qquad
\Omega_s=\sqrt{(h_{x0}+v_s)^2+h_{z0}^2},
\]
\[
\alpha_s=i(h_{x0}+v_s)\frac{\sin(t\Omega_s)}{\Omega_s},\quad
\beta_s=\cos(t\Omega_s)+ih_{z0}\frac{\sin(t\Omega_s)}{\Omega_s}.
\]

The zero-frequency limit uses sin(t Omega)/Omega=t. Since
|alpha|²+|beta|²=1, no block is indeterminate. This gives an exact microscopic
test of C_B for **all** parameters in this commuting class, without a dense
many-body eigensolve. It is necessary and sufficient within this class.

At h_x0=h_z0=0 define phi_i=2t g_i. Then

\[
\theta_s=|\operatorname{wrap}(\sum_i s_i\phi_i)|,
\quad a_n=\prod_i\cos(n\phi_i).
\]

With a transverse qubit field only, multiply a_n by cos(2nt h_x0). These
identities give explicit finite count and trigonometric inequalities in the
couplings for the entire commuting-class preimage. They require neither
resonant detector transitions nor detector level repulsion.

## 4. An explicit parameterized family with a proof for every member

Take the thirteen divisors

\[
q=(2,4,8,16,3,5,7,11,13,6,10,14,12),\qquad
\phi_i^*=\frac{99\pi}{200q_i}.
\]

The construction starts from pi/(2q_i): these cosine factors annihilate
the unwanted integer modes 2 through 16 by divisibility. At that uncontracted
point the first moment is too small: d_0=-0.0542222, just outside the gate.
The declared factor 99/100 moves that design into the allowed moment region.
This is an explicit finite spectral design, not a claim of genericity or a
fit of R to an adjustable sinusoid. Its continuous neighborhood is certified
below; no search is performed by the reproduction script.

For any N>=13, select any thirteen active sites, permute these values, choose
independent signs eta_i, and append zeros for other sites. One may also add
2pi times any integers to these reference phases. For any t>0 require

\[
\Delta=\sum_{i=1}^N|2tg_i-\phi_i^{\rm ref}|
       +2t|h_{x0}|+2t|h_{z0}|\le 4\times10^{-5}.
\]

Let K be any supported detector Hamiltonian commuting with the actual V,
including every X/XX Hamiltonian above with unrestricted allowed coefficients.
These conditions define H_Born. They allow arbitrary
detector size, several graph classes, graph coefficient signs/magnitudes,
detector spectral changes, active-site choices, coupling permutations and
signs, continuous unequal-coupling variations, nonzero qubit detuning,
transverse fields, and time changes compensated by energy scaling.

**Certificate at the reference point.** Write phase/pi as integer/D with
D=48,048,000. Expand the finite product
prod_i(z^(99 L/q_i)+z^(-99 L/q_i)), L=240,240. Its 8192 signed sums,
reduced modulo 2D and folded, determine the 64 bin counts by integer division.
No floating-point decisions select bins. The minimum distance of any root
from any bin edge is greater than **0.0001014113013 rad**. All reflection
pairs are occupied; their smallest total count is 248.

`certify_commuting_seed` encloses pi using Machin's arctangent identity and
alternating rational sums, then encloses each required cosine with a Taylor
remainder and a Lipschitz bound. Products and gate comparisons use exact
`Fraction` arithmetic. It proves

\[
\operatorname{RMSE}_{64}<0.017731405,\qquad
\max_m|d_m|<0.041712764.
\]

**Proof for the full family.** Signs and permutations do not change the
signed-sum measure. Zero-coupled extra spins duplicate each root equally.
The 2pi phase aliases give only a common sign to each conditional qubit
propagator and preserve its projective root. The detector factor K cancels.
For each sign configuration, the change in the conditional qubit generator
has t times operator norm at most Delta/2. The unitary evolution bounds the
Fubini–Study displacement by Delta/2, hence the polar-angle displacement by
Delta. This argument includes central detuning and holds at poles by
continuity; it does not use a divergent eigenvalue perturbation denominator.

Since Delta is smaller than every reference bin margin, **all 64 counts and
R values remain exactly the same** throughout the family. Moreover,
|delta a_n|<=n Delta because cos(n theta) is n-Lipschitz. Thus
|delta d_m|<=4(2m+1)Delta<=60 Delta. Uniformly over H_Born,

\[
\max_m|d_m|<0.041712764+60(0.00004)
             =0.044112764<0.05.
\]

This proves every member passes C_B. The guarantee is finite, exact for the
specified gate, and not restricted to the tested random realizations. The
small certified coupling/field radius is conservative; it must not be
described as broad robustness against arbitrary noncommuting perturbations.
The unrestricted commuting detector directions supply much of the breadth.

## 5. Microscopic preimage and equivalences

The **full** allowed microscopic preimage is precisely the inverse image of
C_B under (H,t)->(C,A)->root angles->counts and moments. In the commuting
class, the explicit formulas above eliminate the many-body propagator from
this test. Our displayed ball is a constructive subset even of that class:
rescaling its phases by 199/198 lies outside the certified radius and still
passes. Native interacting N=17 ring 353 also passes the same gate, but its
XXZ/longitudinal detector lies outside this commuting-X construction.

There is no established simpler closed-form classification of all local
couplings in that larger preimage. In particular, specifying the spectrum
of Hd alone omits eigenvectors and the projected coupling dynamics. This
study does not claim that enumerating one constructive class solves that
remaining inverse problem.

Take the union over the exact geometry-preserving transformations below
whenever the result remains in the implemented operator class. This orbit
closure is also a constructive sufficient family; it includes detector
dimensions and spectator dynamics outside the simple diagonal-X display.
An isospectral replacement of spectator Omega Z by Omega X, for example,
changes its computational-basis eigenvector participation by a factor two
per spin without changing the active root law. This is a precise basis-
dependent localization counterexample, not a claim of MBL in the active
detector. Generic isospectral replacements on an active detector do not
have this invariance unless they also preserve the projected dynamics.

The following transformations preserve the relevant geometry exactly:

| Transformation | Precise scope and reason |
|---|---|
| Detector unitary conjugation | Common similarity of A,C preserves their generalized roots. It stays within the native local model only if the transformed operators are supported. |
| Site permutations / graph isomorphisms | Permute both graph and attachments; this is a detector basis conjugation. |
| Global energy shifts | Multiply both blocks by the same phase. |
| H->aH, t->t/a | Preserve U exactly for positive a; negative times require a separately permitted convention. |
| Add detector K commuting with the rest of H | Common invertible left factor cancels, even for infinite roots. |
| Tensor spectators | Duplicate all roots equally; arbitrary added direct-sum sectors generally change their normalized counts. |
| Different X/XX detector graphs and coefficients | All cancel in the constructive class; their graph and Hamiltonian spectra need not coincide. |
| Independent g_i signs / active-site permutations | Relabel the uniformly counted detector X configurations; valid in this class. |
| Integer 2pi coupling-phase aliases | Preserve the reference conditional propagator projectively; the same perturbation guarantee applies around each alias. |
| Qubit Z-axis rephasing of the block basis | Changes only root azimuths, so preserves this polar gate. Closure in the native interaction channels must be checked. |
| General readout rotation | Does not generally preserve polar angles; its effect is explicitly scanned. |

An inaccessible subspace in a prepared-state experiment is not automatically
irrelevant here: equal root counting includes the entire declared detector
space. A term changing only the unused columns of a unitary can preserve the
pencil, but changing a Hamiltonian block does not in general change only
those columns after exponentiation. These are propagator statements, not
unrestricted permissions to alter microscopic sectors.

## 6. Necessity, counterexamples and physical mechanism

| Property | Classification for the approved gate |
|---|---|
| C_B count/moment inequalities | Necessary and sufficient. |
| Explicit H_Born conditions | Sufficient, not necessary; accepted points outside the ball and the interacting ring are counterexamples to necessity. |
| Commuting X/XX detector | A sufficient realization mechanism when paired with the certified coupling design; alone not sufficient. |
| Detector chaos / WD spacings | Not necessary: the certified commuting detector works. Not sufficient when the coupling/readout changes. |
| Particular graph, regularity, graph spectrum | Not necessary; chain, ring, random graph and complete graph members give identical R. |
| Equal attachment strengths | Not necessary: all thirteen design strengths are unequal. |
| Coupling signs | Independent signs are irrelevant within this class; not claimed irrelevant for general Hqd. |
| Zero qubit detuning / exact central-X symmetry | Not necessary for the polar gate: the certified ball includes hz0!=0. |
| Degenerate spectra | Not necessary; generic detector X fields remove degeneracies without changing roots. |
| Nondegenerate spectra | Not necessary; K=0 gives degenerate commuting examples with the same accepted profile. |
| Detector eigenvector localization | Relevant only together with the coupling and basis; basis-dependent labels alone do not specify the pencil. |
| Preparation state | Not an input to the equal-root statistic. Its physical selection role remains unresolved. |
| Fixed time | Relevant through dimensionless tH. Rescaling preserves behavior; arbitrary uncompensated timing does not. |
| Bidirectional charge transfer | Necessary only in the previously proved magnetization-conserving, longitudinal-qubit subclass, unless that grading is broken. |

A fully explicit nondegenerate example is available without a random-matrix
argument. In integer units pi/(2D), let w_i=99L/q_i and choose detector fields
f_i=M 2^i with integer M>2 sum_i|w_i|, K=-sum_i f_i Xi. Distinct detector
sign configurations occupy disjoint energy intervals, and their two central
energies differ since no signed sum of w_i is zero. The 16384 full energies
are therefore distinct; K still cancels. The reproduction tests verify these
integer conditions. Conversely K=0 has repeated energies. Thus degeneracy
is not the mechanism enforcing the gate.

The mechanism is **commuting-factor cancellation plus a controlled folded
coupling spectrum**. A two-dimensional conditional qubit block makes the
proof tractable; it does not force Born behavior on its own. Setting g=0
fails coverage, taking large qubit detuning fails the gate, and the uncontracted
phase design fails the moment criterion despite a high-looking polar curve.
This rules out symmetry or good-looking R alone as a sufficient explanation.

## 7. Departures, diagnostics and numerical evidence

At the measure level write P=(1+cos theta)E+epsilon, with E reflection-even
and epsilon reflection-odd. Then R-R_B=(1/2)d epsilon/dE, or epsilon/(2E)
for densities. Weakly populated reflected pairs amplify imbalance. In a
fixed bin, first-order count variations give
delta R=(nbar delta n-n delta nbar)/(n+nbar)^2; actual integer histograms
are constant until a root crosses an edge and then jump. A smooth universal
microscopic derivative of binned R would therefore be incorrect.

In the zero-field commuting class,
partial a_n/partial phi_i=-n sin(n phi_i) prod_{j!=i}cos(n phi_j),
which gives the corresponding first-order moment residual directly. At
factor zeros use this product formula, not a logarithmic derivative. Exact
reflection pairing fixes offset and even-cosine parity when bins respect
the pairing; it does not fix the fundamental amplitude or higher odd modes.
Sine coefficients require an extension convention; the natural even
2pi extension of a polar function has no sine terms by definition.

The numerical study contains 256 inside-family and 256 outside-ball draws,
with actual coupling/field increments, detector coefficients and random seed
saved. Every inside draw must retain the exact certified counts and pass.
All 256 inside draws pass; 184 of 256 outside draws also pass. The combined
focused test suite passes 72 tests, including 15 new family checks.
Outside the ball is not the complement of C_B: accepted outside examples
are retained. These are deterministic finite spectra, not independent
statistical samples of roots; no root-count error bars are invented.

Six independent reduced N=5 native QuSpin exponentials, spanning chain,
ring and complete graphs with and without central detuning, agree with the
conditional formula to 2e-12 in polar angle. These validate the operator
conventions. Sixteen additional random native noncommuting N=5 Hamiltonians
verify the effective iff evaluator against independent Bloch-z histogramming
and Chebyshev-polynomial moment recurrence. The N=13 acceptance proof
separately uses all 8192 exact signed
sums; a large dense local simulation is neither needed nor performed.

Plots include P and R vs Born with S_born, residuals, cosine harmonics,
raw moment residuals, microscopically different detector graphs with the
same R, inside/outside error distributions, and coupling, timing, central
field/symmetry and output-axis perturbations. Detector graph, spectrum and
X-field variations cancel analytically; state perturbations are not plotted
as though a preparation density matrix were an input to this statistic.

* [P(theta), R(theta) vs Born and S_born](reports/born_commuting_family_2026-09-11_verified/diagnostics.pdf)
* [Residuals and harmonics](reports/born_commuting_family_2026-09-11_verified/residuals_and_harmonics.pdf)
* [Different detector graphs with the same response](reports/born_commuting_family_2026-09-11_verified/distinct_detector_families.pdf)
* [Random ensemble errors](reports/born_commuting_family_2026-09-11_verified/ensemble_errors.pdf)
* [Perturbations and S_born](reports/born_commuting_family_2026-09-11_verified/perturbations.pdf)
* [Certificate and numerical summary](reports/born_commuting_family_2026-09-11_verified/summary.json)

The same directory contains PGFPlots-readable DAT files for P, R, Born,
residuals, harmonics and graph nodes/edges, plus source hashes and all sampled
parameters. Reports are generated, ignored outputs; the derivation, config,
reproduction code and tests are versioned.

```bash
python scripts/analyze_born_commuting_family.py --output reports/<fresh-family-audit>
python -m pytest -q tests/test_born_commuting_family.py
```

The established result is an exact effective iff theorem for the approved
finite gate and a broad, explicitly certified microscopic sufficient family.
The full noncommuting local-Hamiltonian inverse classification remains
implicit through C_B. The family is broad in commuting detector dynamics
and equivalences, with a conservatively small guaranteed radius in the
root-changing parameters. It is neither a generic-chaos theorem nor an
exact continuous Born law.

## 8. Deliverable audit

| Requested result | Authoritative evidence |
|---|---|
| Definition, offset/amplitude/phase, tolerances | RESEARCH_STATE section 3 and this report section 1; user-selected finite gate. |
| Effective reduction, iff and both directions | Section 2, the native block pencil, exact count inequalities, and the tested gate evaluator. |
| Smallest sufficient diagnostic object | Count ratios/support plus eight raw-angle moment residuals; no preparation-channel substitution. |
| Microscopic preimage and limits | Section 3 gives the full commuting-class formula; section 5 separates the general implicit preimage from the constructive subset. |
| Wide constructive family, every-member guarantee | Section 4: integer counts, rational cosine enclosures, bin margin and Lipschitz proof, with arbitrary allowed commuting detector dynamics. |
| Equivalences and distinct realizations | Section 5, four detector graph/spectrum plots, sign/spectator/alias tests. |
| False necessity claims and failures | Section 6, explicit integer nondegenerate and degenerate spectra, accepted outside points, failing uncontracted design and detuning. |
| Random/adversarial verification | 512 saved Hamiltonian draws; 256/256 certified draws pass; rational certificate and independent native matrix tests. |
| Necessity/sufficiency classification | Section 6 table, with restricted-subclass and basis qualifications. |
| Mechanism and departures | Commuting-factor cancellation and folded coupling spectrum; exact block formula, moment derivatives, count jumps and perturbation plots. |
| P/R/Born/S_born diagnostics | Five figure sets and named-column DAT files in the linked verified artifact directory. |

The numerical and microscopic claims are restricted to the approved polar
criterion. Full-sphere geometry and an operational preparation/selection
measure are separate questions, not silently certified by this result.
