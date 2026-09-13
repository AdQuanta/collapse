# The ring longitudinal direction and the missing logarithmic-tail estimate

13 September 2026. **PROVED, conditional root-stability result. The full
exact-Born phase objective remains OPEN.** No production observable, solver,
acceptance threshold or campaign parameter is changed here.

The native ring scales the longitudinal central-detector coupling as 1/N,
whereas its two transverse couplings scale as 1/sqrt(N). This difference
gives a deterministic propagator estimate for arbitrary values of the other
14 parameters. A stated logarithmic-tail condition converts that estimate
into equality of the thermodynamic polar root laws. That condition has not
been established for either multichannel candidate.

## Research question and discriminating alternatives

**Hypothesis:** at fixed time, the thermodynamic ring root law is independent
of a bounded change of the unscaled parameter gz.

**Strongest alternative:** an asymptotically small perturbation of the
propagator changes its nonnormal pencil roots through singular values too
small for bounded trace statistics to detect.

**Prediction before analysis:** the 1/N normalization should force all
fixed-cutoff logarithmic potentials to agree as N grows. Agreement of the
uncut root potentials requires a separate estimate uniform near zero
singular value. The argument below establishes this exact separation.
It neither assumes nor proves Born balance.

## 1. An unconditional bound for the implemented Hamiltonian

Fix all ring parameters other than gz, denoting that parameter by a. Let

\[
H_N(a)=H_N(0)+a Z_0\otimes\frac1N\sum_{i=1}^N Z_i,
\qquad U_N(a,t)=e^{-itH_N(a)}.
\]

The central qubit is first, Pauli eigenvalues are +/-1, hbar=1, and the
detector dimension is d=2^N. Write
\(\|M\|_{2,2d}^2=\operatorname{Tr}(M^\dagger M)/(2d)\) for full matrices.
Orthogonality of distinct Pauli strings gives exactly

\[
\|H_N(a)-H_N(b)\|_{2,2d}^2=(a-b)^2/N.
\tag{1}
\]

Duhamel's identity, unitary invariance and the norm triangle inequality give

\[
\|U_N(a,t)-U_N(b,t)\|_{2,2d}
\le |t|\,|a-b|/\sqrt N.
\tag{2}
\]

This is exact for every N and real t. No commutation, detector mixing,
perturbative expansion, randomness or spectral gap is required. In contrast,
the operator norm of the Hamiltonian difference is |a-b| and does not vanish.

Partition U into central-Z blocks and retain A=U00, C=U10. For the production
pencil \(M_a(z)=C_a-zA_a\), use the rectangular matrix consisting of its
first d input columns. Its Frobenius norm cannot exceed that of the full
propagator difference. Normalizing by d introduces at most sqrt(2). Left
multiplication by \([-zI,I]\) has norm sqrt(1+|z|^2). Consequently

\[
\|M_a(z)-M_b(z)\|_{2,d}
\le B_r(N,t,a,b):=
\sqrt{2(1+r^2)}\,|t|\,|a-b|/\sqrt N,
\quad r=|z|.
\tag{3}
\]

All three estimates apply to the full interacting 15-parameter ring, with
only the comparison direction restricted to gz. They do not imply stability
in the other 14 independent directions.

## 2. Fixed-cutoff logarithmic potentials

For 0<epsilon<1, define

\[
L_{a,N}^{\epsilon}(x)=\frac1{2\pi d}\int_0^{2\pi}
\sum_{j=1}^d \log\max(s_j(M_a(e^{x+i\phi})),\epsilon)\,d\phi.
\]

This is an auxiliary analytical quantity, not a replacement for QZ or the
frozen verifier. Let \(J_{a,N}^{\epsilon}(x)=L_{a,N}^{\epsilon}(x)
-L_{a,N}^{\epsilon}(0)\).

The sorted singular-value inequality
\(\sum_j(s_j(M)-s_j(M'))^2\le\|M-M'\|_F^2\), followed by Cauchy-Schwarz,
and the 1/epsilon Lipschitz constant of log max(s,epsilon), yields

\[
|L_{a,N}^{\epsilon}(x)-L_{b,N}^{\epsilon}(x)|
\le B_{e^x}/\epsilon,
\qquad
|J_{a,N}^{\epsilon}(x)-J_{b,N}^{\epsilon}(x)|
\le (B_{e^x}+B_1)/\epsilon.
\tag{4}
\]

For completeness, the singular-value inequality follows by applying the
Hermitian ordered-eigenvalue squared-distance bound to the dilations
\(\left(\begin{smallmatrix}0&M\\M^\dagger&0\end{smallmatrix}\right)\).
Their eigenvalues are the positive and negative singular values, and both
squared Frobenius distances acquire the same factor two.

Equation (4) tends to zero at every fixed t, x and epsilon. It remains uniform
over a,b in a bounded interval. This conclusion alone says nothing about the
uncut determinant difference.

## 3. Explicit condition sufficient for root stability

Assume the pencils are regular at the time under consideration. Define the
nonnegative truncation error

\[
T_{a,N,x}(\epsilon)=\frac1{2\pi d}\int_0^{2\pi}\sum_j
\left[\log\frac{\epsilon}{s_j(M_a(e^{x+i\phi}))}\right]_+d\phi.
\tag{5}
\]

Isolated determinant zeros on a circle are interpreted through their
integrable logarithmic singularities. At each finite N, regularity and the
bounded upper singular values make these integrals finite.

The exact root potential from Theorem F of
[BORN_NONNORMAL_LIMIT.md](BORN_NONNORMAL_LIMIT.md) obeys

\[
|J_{a,N}(x)-J_{b,N}(x)|\le
\frac{B_{e^x}+B_1}{\epsilon}
+T_{a,N,x}+T_{b,N,x}+T_{a,N,0}+T_{b,N,0}.
\tag{6}
\]

**Conditional theorem.** Fix t and two values a,b. Suppose, for each rational
x including zero and c in {a,b},

\[
\lim_{\epsilon\downarrow0}\limsup_{N\to\infty}
T_{c,N,x}(\epsilon)=0.
\tag{7}
\]

Then the exact potentials have vanishing difference locally uniformly in x.
In particular, if the thermodynamic polar root measure exists for one of
these values of gz, it exists and is identical for the other.

**Proof.** In (6), first take N to infinity with epsilon fixed. Equation (3)
removes the first term. Then take epsilon to zero and apply (7). This proves
pointwise agreement at every rational x. Exact root potentials are uniformly
1-Lipschitz, so their difference is 2-Lipschitz; a finite rational grid gives
local uniform agreement. Theorem F identifies this topology with weak
convergence of the complete polar root measure, including its zero and
infinite-root masses. No invertibility of A is needed.

If (7) holds uniformly over a bounded interval of gz, the conclusion is
uniform over that interval. If it holds at every sufficiently late fixed t,
all those thermodynamic instantaneous measures agree between a and b.
An ordinary subsequent t-to-infinity limit, if it exists for one, is therefore
the same for the other. This is the required order of limits; equation (2)
does not give a uniform-in-time estimate and cannot justify swapping them.

A concrete stronger sufficient condition is a uniform singular-value count
bound. Let F_(c,N,x)(u) be the circle-averaged fraction of singular values
below u. If, for some gamma>0 and C independent of N and the tested c,

\[
F_{c,N,x}(u)\le C u^\gamma\quad(0<u<u_0),
\]

then Tonelli's theorem gives
\(T(\epsilon)=\int_0^\epsilon F(u)\,du/u\le C\epsilon^\gamma/\gamma\).
Taking epsilon of order \(N^{-1/[2(\gamma+1)]}\) in (6) gives a potential
difference of order \(N^{-\gamma/[2(\gamma+1)]}\) at fixed t and x.
This is a sufficient bound to prove, not a fitted rate or a claim about the
candidate data. Its constants need not be uniform in time.

## 4. Limits and research consequence

**PROVED:** all fixed-cutoff potentials lose the ring gz dependence under
the stated scaling. **PROVED, conditional:** the actual thermodynamic root
law also loses it if (7) holds for the compared pencils.

**OPEN:** condition (7), a polynomial tail bound, and even the existence of
the relevant thermodynamic root laws for seeds 079 and 047. Small QZ backward
residuals cannot supply (7). The native exchange counterexample in Theorem G
already rules out an unconditional inference from trace or singular-value
weak convergence to root convergence. This report does not supply a
counterexample specifically to gz independence.

For endpoint chains the Hamiltonian difference is (a-b)Z0Z1, with normalized
Hilbert-Schmidt norm |a-b|. No N-decay follows from this argument. Ring
central fields also have order-one norm, as do changes in gx or gy under
their 1/sqrt(N) scaling. Thus even a proof of (7) would settle only one
direction of the full open-region requirement.

**Decision: KEEP as an analytical reduction, not candidate promotion.**
It identifies a precise extra estimate needed before interpreting ring gz
robustness as thermodynamic phase evidence. The existing baseline campaign
retains all its parameters, saved quantities and frozen gates. Its root and
residual archives do not contain the full circle-dependent singular-value
data needed to test (7); no such test is claimed here. A future targeted
singular-value study would be a separately specified experiment, and finite
samples alone would not prove (7).

Provenance: derived from `core/ring_chain_family.py` at source commit
31727fae54aa4f518d4e050047e7540ed34575d7 and Theorem F, with the corrected
interpretation J' = CDF and J'' = interior log-radius measure. No numerical
experiment, random seed or production submission belongs to this result.
