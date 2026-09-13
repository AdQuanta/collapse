# PROVED: central-X interacting rings via a local recurrence and tracial echo

2026-09-13. This report resolves the interacting detector step **for rings
with central X conservation**. It also covers the subsequent detector NN XYZ
and NNN XYZ blocks under that same central-coupling restriction. Additional
central coupling axes and non-X central fields are not covered. The full
ring-and-chain goal remains OPEN.

The result is an exact characterization by a local Pauli recurrence, a
determinate scalar moment problem and explicit measure transforms. It is
not a closed elementary formula for the generic interacting detector's
spectral density. It supplies the finite root law and both ordered limits
without diagonalizing an arbitrary many-body Hamiltonian.

## 1. Scope and exact finite-N root representation

Let D_N be the detector Hamiltonian with any fixed real uniform field and
NN/NNN XYZ coefficients in the production ring family. N>=5. Set

    H_N = I_Q tensor D_N + X_Q tensor (a I + g F_N),
    F_N = N^(-1/2) sum_i X_i, a=h0x, g=gx;
    gy=gz=h0y=h0z=0.

The Pauli conventions, positive signs and ring bond multiplicities are those
in report 01. The normalized detector trace tau_N=2^(-N)Tr is dictated by
algebraic root multiplicity, not a preparation ensemble.

X_Q and ring translations are conserved. There need not be an integrable
detector symmetry. The central-X sectors give

    U_±=exp[-it(D_N ± gF_N ± a I)],
    W_N=U_-^dagger U_+,
    A=U_-(I+W_N)/2, C=U_-(W_N-I)/2.

W_N is unitary. For each eigenvalue w_j, the production homogeneous root
has representative (alpha_j,beta_j)=(w_j-1,w_j+1). Its polar angle is
theta_j=arccos(Re w_j). W_N=1 gives a zero root and W_N=-1 an infinite root.
Both coordinates never vanish together; all these pencils are regular.

Thus P_N is the equal-weight atomic pushforward of the W_N spectrum and

    integral cos(ell theta) P_N(dtheta,t) = Re tau_N(W_N(t)^ell), ell>=0. (1)

The zeroth moment is one. Support is precisely the resulting atoms with
algebraic multiplicity; no density is asserted at finite N. Polar reflection
multiplies (1) by (-1)^ell, so symmetry is equivalent to vanishing odd
moments, and is not generally present at finite time.

### An explicit finite recurrence, rather than a formal spectral sum

Expand each conditional Hamiltonian in Pauli words P, with coefficients
h_±(P). Include ±a in the identity word. Write P Q=eta(P,Q)(P*Q), where
eta is a fourth root of unity. Define

    b_{±,0}(P)=1_{P=I},
    b_{±,r+1}(R)=sum_{P*Q=R} h_±(P) b_{±,r}(Q) eta(P,Q).

The coefficients of U_± are sum_r (-it)^r b_{±,r}(P)/r!. For finite N this
series converges absolutely for every finite t, with operator-norm tail
bounded by the exponential-series tail using ||D_N±gF_N±a||. Multiplying
these Pauli series gives W_N and its powers. Their identity coefficients
give tau_N(W_N^ell), including the complex traces, not only their real parts.

With p_ell=2^N tau_N(W_N^ell), Newton's recurrence

    c_0=1, c_k=-(1/k)sum_{ell=1}^k c_{k-ell}p_ell, 1<=k<=2^N,

constructs det(zI-W_N)=sum_{k=0}^{2^N}c_k z^(2^N-k). Its roots and (1)
therefore determine P_N exactly. The recurrence remains exponentially costly
at general finite N, but exposes local coefficients and the limits below;
no assertion of efficient generic many-body solution is made.

## 2. Precise locality input

For bounded finite-range spin interactions the infinite-volume dynamics
exists in norm on local observables. On each fixed |s|<=T, a time-evolved
single-site observable has centered local shell pieces A_{i,r}(s), supported
within radius r of site i, such that

    X_i(s)=sum_{r>=0} A_{i,r}(s),
    tau(A_{i,r})=0, ||A_{i,r}(s)|| <= c_T exp(-b r).             (2)

The same bounds hold uniformly on finite rings, with shells ending at the
ring diameter. Use trace-preserving conditional expectations onto balls
and their successive differences. This input follows from the
Lieb--Robinson bound, the norm thermodynamic limit, and local approximation
in Theorem 3.1, Theorem 3.5 and Section 4 of
[Nachtergaele--Sims--Young, Quasi-Locality Bounds I](https://arxiv.org/abs/1810.02428).
All remaining echo, Gaussian and root deductions are given below.

Constants depend on fixed microscopic coefficients and T; they need not
remain bounded as T increases. We never interchange N→infinity and T→infinity.

## 3. A tracial commutator bound

Use ||B||_2=sqrt(tau_N(B^dagger B)). For a translated centered local operator
B_i with support radius R, product-trace factorization makes
tau_N(B_i^dagger B_j)=0 at disjoint supports. Consequently

    ||sum_i B_i||_2 <= sqrt[N c(R+1)] ||B_0||.                 (3)

If supports wind around a small ring, the number of overlaps is at most
min(N,c(R+1)), still bounded by c(R+1).

Set F_N(s)=N^(-1/2)sum_i X_i(s), with evolution by D_N alone. For shell
orders r,q, only O(r+q+1) relative displacements contribute to the
commutator. Group its terms by the first site:

    [F_N(s),F_N(u)] = (1/N)sum_{i,r,q} B_i^{r,q}(s,u).

Each B_i^{r,q} is a sum of O(r+q+1) local commutators, has trace zero,
support radius O(r+q+1), and norm at most
c(r+q+1)||A_{0,r}(s)|| ||A_{0,q}(u)||. Applying (3) and summing shells gives

    sup_{|s|,|u|<=T} ||[F_N(s),F_N(u)]||_2 <= C_T/sqrt(N).   (4)

The summability is explicit: a double sum of
(r+q+1)^(3/2) exp[-b(r+q)] is finite. Tracial centering is essential.
An operator-norm commutator estimate alone would not give (4).

## 4. Time ordering disappears for this scalar detector echo

Define G_N(t)=integral_0^t F_N(s)ds and interaction-picture propagators
V_±(t)=T exp[∓ig integral_0^t F_N(s)ds]. For any self-adjoint time-dependent
generator K'(s), differentiating exp[-iK(s)] and using unitary invariance
of the 2-norm gives

    ||T exp[-i integral_0^t K'(s)ds]-exp[-iK(t)]||_2
       <= (1/2) integral_0^t ||[K(s),K'(s)]||_2 ds,
    K(s)=integral_0^s K'(u)du.                                (5)

To see the factor 1/2, the logarithmic derivative of exp[-iK] averages
unitary conjugates of K' over 0<=v<=1; their distance from K' is bounded by
v||[K,K']||_2. Integrate v, then apply Duhamel between two unitary evolutions.

Equations (4)–(5) imply, for each fixed t,

    ||W_N(t)-exp(-2iat)exp[-2igG_N(t)]||_2 <= C_{t,g}/sqrt(N). (6)

Products and powers of unitaries telescope in this norm. Therefore, for each
fixed ell, the difference of their normalized trace powers tends to zero.
This is the missing justification for using the first integrated field in
this scope; it is not an uncontrolled long-time Magnus approximation.

## 5. Scalar central limit theorem for G_N(t)

Fix t and truncate (2) at radius R before integrating. The result is a
translated centered self-adjoint local observable Y_i^R(t), of fixed radius R.
Equation (3) and the shell bound imply uniformly in N

    ||G_N(t)-N^(-1/2)sum_i Y_i^R(t)||_2
       <= |t| c_T sum_{r>R} sqrt[c(r+1)] exp(-br) -> 0.        (7)

For fixed R, divide a large ring into blocks of length L and retain only
Y_i^R supported wholly in one block. The omitted boundary terms have
2-norm after 1/sqrt(N) normalization at most C_R sqrt(R/L), plus a final
incomplete-block error vanishing at fixed L as N grows. Distinct retained
block sums commute and their tracial distributions factor exactly. They are
identically distributed bounded self-adjoint random variables in this
product trace. The elementary iid characteristic-function expansion proves
their scalar CLT as N grows with L fixed.

Let L→infinity next. The block variance divided by L approaches the finite
covariance sum of Y_i^R. Finally let R→infinity using (7). The estimate

    |tau(exp(isB))-tau(exp(isC))| <= |s| ||B-C||_2

follows by Duhamel and justifies each approximation for characteristic
functions even when B and C do not commute. Thus G_N(t) has a scalar Gaussian
tracial limit with variance

    sigma(t)^2=lim_N tau_N(G_N(t)^2).                         (8)

Finite-ring local expectations converge to those in the infinite chain by
(2); centered fixed-radius differences are again bounded by (3). This
justifies using infinite-chain blocks in the argument without a global
operator-norm replacement of the ring Hamiltonian.

## 6. A constructive spectral measure from local Pauli moments

Let

    C(s)=lim_N tau_N(F_N(s)F_N(0))
        =sum_j tau(X_0(s)X_j).

The sum converges absolutely locally uniformly in s by (2). Finite-N C_N
are real, even, positive-definite functions with C_N(0)=1. Their limit
therefore has a unique symmetric probability spectral measure nu:

    C(s)=integral cos(omega s) nu(domega),
    sigma(t)^2=integral |integral_0^t exp(iomega s)ds|^2 nu(domega)
       =nu{0}t^2+2 integral_{omega!=0}(1-cos(omega t))/omega^2 nu(domega). (9)

Tonelli or bounded finite-time kernels justify these integrations, and
0<=sigma(t)^2<=t^2. A zero frequency is not discarded or divided by zero.

The measure nu is specified by an exact **local** recurrence, independent
of any finite-N many-body spectrum. Set L(O)=[D,O] on finite Pauli words.
With the multiplication rule in Section 1,

    L(P)=sum_{Q overlapping P} h(Q)(eta(Q,P)-eta(P,Q))(Q*P),
    mu_2k=sum_j [X_j] L^(2k)(X_0), mu_2k+1=0.               (10)

Here [X_j] means that Pauli coefficient. Only finitely many words/sites
occur at any given order. This recurrence is implemented independently of
the verifier in `core/analytic_liouvillian.py`.

These are the moments of nu. To justify both differentiating C and their
determinacy, note that each commutator can enlarge the support only by the
fixed interaction range. Counting overlapping Hamiltonian terms bounds

    ||L^k X_0|| <= c^k k!,
    mu_2k <= c'(k+1) (c^k k!)^2.                            (11)

The polynomial factor in the second bound counts overlapping translates in
(3). This also bounds finite-N moments uniformly, so higher moments give
uniform integrability and pass to the weak spectral limit. Carleman's sum
sum_k mu_2k^(-1/(2k)) diverges by (11) (zero moments give the degenerate case).
Hence (10) determines nu uniquely. Positive moment matrices give its usual
orthogonal-polynomial/Jacobi continued-fraction reconstruction, with finite
termination when the support is finite. All diagonal Jacobi coefficients
vanish by symmetry. Thus nu is a determinate recurrence-defined object,
not an unspecified or fitted detector spectral density.

## 7. PROVED thermodynamic root law

Combining (1), (6) and the scalar CLT gives

    m_ell(t)=cos(2ell a t) exp[-2ell^2 g^2 sigma(t)^2].        (12)

Polynomials in cos(theta) are dense on [0,pi]. Tightness is automatic, so
these cosine moments prove weak convergence of the actual production root
measure to

    P_infinity(t)=Law(F(a t+g sigma(t)G)), G standard Gaussian. (13)

For g sigma(t)!=0 this is the smooth positive folded wrapped-Gaussian
density from report 01. Otherwise it is the atom delta_{F(at)}. This
retains all exceptional times. Normalization and full/atomic support follow
from this explicit pushforward; reflection is determined by odd moments.

The normality of W_N is crucial. Vanishing commutators or trace convergence
alone do not control a generic nonnormal pencil, as the repository's
multichannel XY counterexample already proves. This theorem does not apply
to that counterexample because its central X is not conserved.

## 8. PROVED Cesàro average after the thermodynamic limit

For ell>=1, construct a symmetric probability measure kappa_ell whose
characteristic function is

    kappa_hat_ell(t)=exp[-2ell^2 g^2 sigma(t)^2].              (14)

This construction is explicit. The mass nu{0} gives a Gaussian component
of variance 4ell^2 g^2 nu{0}. Away from zero use the symmetric measure

    Lambda_ell(domega)=4ell^2 g^2 1_{omega!=0} nu(domega)/omega^2.

It obeys integral min(1,omega^2) Lambda_ell(domega)<infinity. Restrict it to
|omega|>epsilon: the resulting finite measure defines the compound-Poisson
law exp(-lambda)sum_{r>=0} Lambda_ell^(*r)/r!. Convolve with the Gaussian
component, then take epsilon↓0. Its characteristic functions converge to
(14), continuously at t=0 by sigma(t)^2<=t^2; the continuity theorem gives
a unique probability limit. This also covers an infinite total Lambda mass.

Average (12) only now. Fubini applies to bounded characteristic functions,
and the Cesàro average of exp[it(omega+2ell a)] tends to the indicator of
omega=-2ell a. Dominated convergence gives the exact coefficients

    b_0=1, b_ell=lim_T T^(-1)integral_0^T m_ell(t)dt
                =kappa_ell{2ell a}, ell>=1.                 (15)

Symmetry of kappa removes the sign. Compactness and uniqueness of cosine
moments prove that the Cesàro-averaged **measures** converge. No density or
interchange of thermodynamic and time limits is assumed. Formula (15) is
valid even if low-frequency detector weight makes the total Lambda mass
infinite. It reduces the average to explicit atom weights of a probability
law constructed from the recurrence-defined nu.

## 9. Canonical R, including measures without an established density

Equations (10), (14), and (15) determine the averaged measure completely.
For a directly evaluable regularization define, 0<r<1,

    f_r(theta)=(1/pi)[1+2sum_{ell>=1}r^ell b_ell cos(ell theta)]. (16)

This is the positive Poisson smoothing of the even folded measure. Its
series converges absolutely. For an interval I=(u,v) whose endpoints carry
no averaged mass, its exact mass is

    M(I)=lim_{r↑1} [(v-u)/pi
       +(2/pi)sum_{ell>=1}r^ell b_ell(sin(ell v)-sin(ell u))/ell]. (17)

Use intersected polar neighborhoods at endpoints. Recover atoms by shrinking
neighborhoods. The canonical ratio, defined almost everywhere relative to
the measure plus its reflection, is the differentiation limit

    R(theta)=lim_{epsilon↓0}
       M(I_epsilon(theta)) /
       [M(I_epsilon(theta))+M(S I_epsilon(theta))].          (18)

Choose continuity boundaries in (17). Differentiation of finite Borel
measures on the interval proves (18) is exactly dP_bar/d(P_bar+S_*P_bar).
At an atom this is the atom/reflected-atom mass ratio. Empty reflected
support stays undefined; the production plotting convention remains 1/2.
Thus no implicit smoothing, atom deletion or replacement observable enters R.

Useful evaluated cases follow without reconstructing every coefficient:

- **Explicit full-detector consequence:** if hx!=0 and g!=0, the result is
  uniform for arbitrary remaining detector fields and NN/NNN XYZ coefficients.
  Indeed the conserved fluctuation E_N=D_N/sqrt(N) has
  tau(F_N E_N)=hx and
  tau(E_N^2)=v_E=|h|^2+|J1|^2+|J2|^2, by Pauli orthogonality. Orthogonal
  projection of F_N onto the zero-frequency Liouvillian subspace gives
  nu_N{0}>=hx^2/v_E. The closed-set inequality for weak measure convergence
  preserves this lower bound in nu. Hence sigma(t)^2>=hx^2 t^2/v_E,
  (12) tends to zero at every nonzero cosine order, and both the ordinary
  late-time limiting root measure and its Cesàro average are dtheta/pi.
  This evaluates R=1/2 on the entire interacting ladder retaining a nonzero
  detector hx. It uses a conserved-energy overlap, not a chaos assumption.
- If g!=0 and nu{0}>0, each kappa_ell has a nondegenerate Gaussian component
  and no atoms. Then b_ell=0, P_bar=dtheta/pi, and R=1/2 for every a.
- If g=0, P_bar=delta_0 for a=0 and dtheta/pi for a!=0, as in report 01.
- If nu is atomless, nu{0}=0, and I=integral nu(domega)/omega^2<infinity,
  compound-Poisson terms of order >=1 are atomless. Thus at a=0,
  b_ell=exp(-4ell^2 g^2 I): P_bar is a folded Gaussian with variance 2g^2 I
  before F, and R is its explicit reflected-density ratio. At a!=0 all
  b_ell vanish and R=1/2. The I convention here uses the full symmetric nu.
- A finite symmetric pure-point nu gives compound-Poisson convolution
  sums, retaining all resonance relations between its frequencies. These
  atom weights, not an unjustified uniform phase approximation, enter (15).

## 10. Exact reductions, independent checks, and remaining scope

If [D,M]=0, nu=delta_0 and sigma(t)^2=t^2; this recovers all the commuting
detector field/XX/NNN XX results, including the central X field a.
For independent spins in field (p,0,q), nu has mass p^2/(p^2+q^2) at zero
and equal remaining masses at ±2sqrt(p^2+q^2), giving report 03 exactly.
For p=0,a=0 its compound-Poisson atom is
exp(-ell^2 g^2/q^2)I0(ell^2 g^2/q^2), the previously derived average.

The v3 independent verifier passed all eight supplied exact matrix cases,
including symbolic Ising detector moments, the 1/N commutator coefficient,
full detector NN/NNN XYZ moment certificates and the echo Taylor coefficients
through fourth order. The noninteracting control includes the sixth
Liouvillian moment. These checks support the algebra; the proof of the
limits is Sections 2–8, not an extrapolation of the checked sizes.

Endpoint-chain detector coupling does not carry 1/sqrt(N), so (4) does not
eliminate its time ordering. Additional central coupling axes destroy the
scalar conditional-unitary reduction and can have the established nonnormal
root pathology. These are the next outstanding steps; this report does not
meet the full-family completion criteria in `goal-analytic.md`.
