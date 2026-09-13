# General endpoint-chain time averages: exact generator and the missing bound

2026-09-13. **PROVED:** a local operator recurrence gives the first root
moment and its thermodynamic-first Cesàro mean for arbitrary detector fields
and NN/NNN XYZ interactions, with central coupling gx and field h0x.
**PROVED, conditional:** a uniform bound on the total variation of each
replicated frequency measure would give all ordered time averages and R.
**OPEN:** that bound, or another argument establishing all the means.
This does not solve the full goal, and adds no integrability restriction.

## 1. Question, prediction, and conventions

The main endpoint obstruction is the existence and evaluation of the time
means of **all** root moments after the proved fixed-time thermodynamic
limit (report 07). The hypothesis tested here is that Hilbert-space
replication supplies an immediately usable mean-ergodic theorem. The
strongest alternative is that replication is exact only at finite N and
its final trace functional is not uniformly bounded in N.

Prediction before verification: for d=2^N and ell replicas, the required
functional has norm d^(ell-1). If confirmed, the ordinary mean-ergodic
argument settles ell=1 but does not settle the full distribution.

Keep every detector coefficient of the implemented endpoint family:

    H_N = D_N + X_Q(a + g X_1),  a=h0x, g=gx.

D_N includes hx, hy, hz and every NN/NNN XYZ term with the original open
boundaries and positive Pauli signs. Detector dimension is d=2^N and
tau_N=Tr/d. No detector coupling is scaled with N. Central gy, gz, h0y,
h0z are still zero at this step; their nonnormal pencil is a separate gap.

Set H_±=D_N±(gX_1+aI), U_±=exp(-itH_±), and W_N=U_-†U_+.
As already proved, the projective roots are (w-1,w+1), where w runs through
the unitary eigenvalues of W_N with equal algebraic weight. Thus

    m_ell,N(t) = integral cos(ell theta) P_N(dtheta,t)
              = Re tau_N(W_N(t)^ell).

This retains zero and infinite roots as ordinary pole atoms. The pencil in
this scope is regular. Root geometry is not an operational outcome law.

## 2. A self-adjoint local recurrence, with the full detector retained

On the Hilbert space L2(M_d,tau_N), define

    K_N B = H_+ B - B H_-
          = [D_N,B] + g{X_1,B} + 2a B.

Left and right multiplication by Hermitian matrices are self-adjoint and
commute with one another. Consequently K_N is self-adjoint and

    exp(-it K_N) I = U_+ U_-† =: x_N(t).

x_N and W_N are unitarily conjugate. Therefore **every** moment has the
exact representation Re tau_N(x_N(t)^ell). The distinction between this
nonlinear expression and a linear spectral matrix element is essential.

For ell=1, let nu_N be the positive spectral measure of K_N in the unit
vector I. Then

    tau_N(W_N(t)) = <I, exp(-it K_N) I>
                 = integral exp(-it omega) nu_N(domega).

This has a constructive Pauli-word recurrence, not an arbitrary full-matrix
spectral sum. Start B_0=I and apply the displayed local formula for K:

    B_(k+1) = [D,B_k] + g{X_1,B_k} + 2a B_k,
    nu_k = tau(B_k).

Only detector terms overlapping a word contribute to the commutator.
Only the endpoint enters the anticommutator. Each step increases the maximum
site by at most two. Thus each coefficient is exactly computable on a
finite support even for the half-infinite chain. All coefficient-zero
reductions follow from the same polynomial recurrence.

Writing mu2=tau([D,X_1]†[D,X_1]), its first five spectral moments are

    nu_0 = 1,
    nu_1 = 2a,
    nu_2 = 4a² + 4g²,
    nu_3 = 8a³ + 24ag²,
    nu_4 = 16a⁴ + 96a²g² + 16g⁴ + 4g² mu2.

For N>=3, Pauli orthogonality gives

    mu2 = 4(hy²+hz²+J1y²+J1z²+J2y²+J2z²).

Missing endpoint bonds are omitted for N=1,2. The absence of hx, J1x,
J2x from this *low-order coefficient* does not remove them from the
recurrence at higher orders.

## 3. Thermodynamic-first proof for the first moment

Use the tracial GNS Hilbert space of the half-chain algebra. The bounded
finite-range detector interaction generates a strongly continuous,
trace-preserving automorphism group. Its Hilbert-space generator L_D,
with local expression [D,B], is self-adjoint. Endpoint left and right
multiplications are bounded self-adjoint operators of norm one. Hence

    K = L_D + g(L_X1 + R_X1) + 2a I

is self-adjoint on Dom(L_D), by bounded self-adjoint perturbation. The
relative finite-volume dynamics converges on local vectors on every
compact time interval: the proof uses precisely the local perturbation
Duhamel argument of report 07. Thus

    m_1,infinity(t) = Re <I, exp(-itK) I>.

Let nu be the positive unit spectral measure of K in I. The spectral
theorem and dominated convergence give, **after this N limit**,

    b_1 := lim_(T→infinity) (1/T) integral_0^T m_1,infinity(t) dt
         = nu({0}) = ||1_{0}(K) I||² >= 0.

The averaging multiplier (1/T) integral_0^T exp(-it omega)dt is bounded
by one and converges to 1_{omega=0}. No spectral gap, nonresonance,
mixing, quadratic closure, or finite-N time average is assumed.

The local recurrence specifies this spectral measure uniquely. For fixed
coefficients, the sum of absolute Pauli coefficients of K B is bounded by
C(s+1) times that of B when B has support within the first s sites.
After k applications to I, s<=1+2k. Hence ||K^k I||_2<=C1^k k! for a
coefficient-dependent C1. The even spectral moments satisfy Carleman's
divergence condition. In particular the recurrence is determinate, and
the atom can alternatively be extracted from its Stieltjes transform:

    G(z) = <I,(z-K)^(-1)I>,
    nu({0}) = lim_(epsilon downarrow 0) -epsilon Im G(i epsilon).

The second equality is again dominated convergence applied to
epsilon²/(omega²+epsilon²). A continued fraction can be obtained from the
orthogonal-polynomial recurrence of nu. This describes a single moment,
not P or R by itself.

Controls: g=0 gives nu=delta_(2a); [D,X_1]=0 gives
nu=(delta_(2a+2g)+delta_(2a-2g))/2, including coincident atoms. These
recover the earlier commuting first-moment means exactly.

## 4. Why the replica mean-ergodic shortcut fails

Let P_ell cyclically permute ell detector copies. Ordinary matrix traces
give the exact identity

    tau_N(x^ell) = d^(ell-1) tau_N^(tensor ell)(P_ell x^(tensor ell)).

On L2(M_d,tau_N)^(tensor ell), set

    K_N^[ell] = sum_(j=1)^ell K_N acting on copy j.

Then x_N(t)^(tensor ell)=exp(-itK_N^[ell]) I^(tensor ell).
The concluding functional is

    Phi_N,ell(B)=d^(ell-1) tau_rep(P_ell B).

Since P_ell is unitary, its normalized L2 norm is one. Cauchy–Schwarz
gives ||Phi_N,ell||=d^(ell-1), with equality on B=P_ell†.
For ell>=2 this diverges exponentially in N. Rescaling the two vectors
in its matrix-element representation cannot change their norm product.
The same cyclic contraction on finite subalgebras consequently has no
bounded extension to the infinite product tracial L2 space.

**FALSIFIED:** the assertion that this particular replication has a
dimension-independent bounded trace functional. This does not disprove
existence of the desired means, exclude every alternative representation,
or supply a counterexample within the implemented Hamiltonian family.

It also cannot be replaced with a positive single-vector spectral measure.
The allowed one-detector control g=hz=1, all other coefficients zero, has
r(t)=cos²(sqrt(2)t), m_1=r and m_2=2r²-1. Its exact time means are
b_1=1/2 and b_2=-1/4. A normalized positive spectral measure would give
a nonnegative zero-frequency atom, contradicting b_2. Signed or complex
cross-spectral measures are allowed, and are the relevant objects below.

Related ergodic results do not remove the hypothesis gap. Eisner and
Kunszenti-Kovács require an orbit-compactness condition in their entangled
ergodic theorem, and Proposition 1 gives failure without it. We have not
verified their assumptions for this chain. Their abstract counterexample
is **not** a counterexample for our local spin family:
[On the entangled ergodic theorem](https://arxiv.org/abs/1008.2907).

## 5. An explicit sufficient condition that would settle every moment

Let E_N,ell be the spectral projection measure of K_N^[ell] and define
the finite complex measure

    nu_N,ell(B) = d^(ell-1)
                  <P_ell†, E_N,ell(B) I^(tensor ell)>.

Its Fourier transform is c_N,ell(t)=tau_N(W_N(t)^ell), and the generic
Hilbert-space bound is ||nu_N,ell||_TV <= d^(ell-1). Its total mass is
one, but it need not be positive; total mass is not total variation.

**PROVED, conditional theorem.** Suppose, for each fixed ell>=1, that

    sup_N ||nu_N,ell||_TV < infinity.                       (TV)

Then there is a unique finite complex measure nu_infinity,ell with Fourier
transform c_infinity,ell(t), the already proved thermodynamic echo moment.
All its time means exist and

    b_ell = Re nu_infinity,ell({0}).

Proof: bounded total variation gives subsequential weak-* compactness in
the dual of C0(R). For a Schwartz test function, Fourier duality, the
fixed-time limit c_N,ell→c_infinity,ell, and |c_N,ell|<=1 identify the
Fourier transform of any measure limit as c_infinity,ell in distributions.
Both transforms are continuous, so the identity holds pointwise. Fourier
uniqueness makes the limit independent of the subsequence. Dominated
convergence with respect to its finite total variation then gives the
atom formula. No interchange of the N and time limits occurs.

The time-averaged root probabilities live on the compact interval [0,pi].
Any subsequential weak limit therefore exists and has cosine moments
b_ell. Polynomials in cos(theta) are dense in C([0,pi]), so these moments
determine one probability measure and the whole Cesàro family converges.
Normalization, positivity, and atomic mass follow from the actual root
measures, not from positivity of the auxiliary nu_infinity,ell.

Once this measure mu is obtained, the production canonical ratio is exactly

    R = dmu / d(mu + S_*mu),  S(theta)=pi-theta,

defined (mu+S_*mu)-almost everywhere. Densities give the familiar density
ratio only when proved to exist. Nothing assigns values on absent support.

Condition (TV) is a sufficient route, not a necessary condition for Cesàro
convergence. The bound d^(ell-1) neither proves nor disproves (TV) for the
actual dynamical vectors. Also nu_infinity,ell({0}) cannot be replaced by
lim_N nu_N,ell({0}); point masses are not continuous under weak convergence.

## 6. Decision and next discriminating calculation

KEEP the exact local generator, the first-moment theorem, and the explicit
conditional all-moment reduction. REJECT the dimension-independent replica
functional shortcut. Do not promote the full chain time average.

The reduced ell=2 calculation retained hx and all detector interactions,
with exactly the rational parameters of the v5 checker and N=2,3,4,5.
With overlaps O_ij=<i,-|j,+>, the ungrouped coefficient is
O_ij conj(O_kj) O_kl conj(O_il)/d at frequency
E_j,+ + E_l,+ - E_i,- - E_k,-. Summing the exact i/k and j/l
permutations gives the real coefficient

    (2-delta_ik)(2-delta_jl)
    Re[O_ij conj(O_kj) O_kl conj(O_il)]/d, i<=k, j<=l.

Only after those exact resonances are retained are nearby frequencies
coalesced at the predeclared tolerances 1e-12, 1e-10, 1e-8.

**PRELIMINARY_NUMERIC:** the variations at tolerance 1e-10 are

| N | General detector | Commuting control |
|---|---:|---:|
| 2 | 2.1357227330 | 1 within 1.2e-15 |
| 3 | 2.8799658071 | 1 within 1.2e-15 |
| 4 | 3.9463684933 | 1 within 1.2e-15 |
| 5 | 6.2716757519 | 1 within 1.2e-15 |

The 1e-12 and 1e-10 results agree. At N=5, the 1e-8 coalescing result
is 6.2714685658; that sensitivity is retained. This is not an exact
certification of frequency separation or an asymptotic divergence proof.
The maximum eigensolver residual is 2.14e-14. All 24 finite-time moment
comparisons with production homogeneous QZ passed: maximum moment error
9.11e-15 and maximum homogeneous root residual 1.20e-15, versus fixed
gates 1e-8 and 1e-11. No failed root-validity cases were omitted.

The decision on (TV) is **INCONCLUSIVE**. Increasing finite-size values
do not disprove a finite supremum, but give no basis to assert one. Do not
expand this into a large size survey. The next proof target is cancellation
in the near-zero frequency contribution, or a locality-based averaging
argument weaker than global total variation. The Majorana slice stays
parked. Data: `reports/analytic_p_theta/endpoint_replica_weights_v1.json`;
reproduction: `scripts/check_endpoint_replica_weights.py --output <new.json>`.

Candidate: `endpoint_replica_v1.json`. Frozen v5 covers dense exact Pauli
identities at N=1,2,3, derivatives through order four, replica moments
ell=1,2,3, and zero/commuting controls. See the append-only verifier log and
VALIDATION.md for the observed run status: PASS, with both deliberate
wrong-sign/normalization controls rejected. Symbolic checks do not prove
the conditional hypothesis (TV).
