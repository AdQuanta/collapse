# Antipodality of the Two Outcome Root Sets

> Sources: `SPEC.md` v1.0, 2026-09-15; `exact-formalism-v1` METHOD note, 2026-09-19; Repository execution, 2026-09-21
> Raw: [Research specification snapshot](../../raw/project-governance/research-spec-v1.md); [Exact formalism validation packet](../../raw/campaigns/2026-09-19-exact-formalism-validation.md); [Outcome antipodality verification](../../raw/campaigns/2026-09-21-outcome-antipodality-verification.md)
> Updated: 2026-09-21

The two outcome pencils of [[projective-roots]] are not independent. Unitarity alone forces the outcome-1 collapsible rays to be the Bloch antipodes of the outcome-0 rays, carrying identical kernel dimensions. This page states the theorem, gives two proofs, and records what does and does not follow from it.

## Statement

Write the propagator qubit-first and let a homogeneous ray be $[\alpha:\beta]$, so that the qubit state is $(\beta|0\rangle+\alpha|1\rangle)/\sqrt{|\alpha|^2+|\beta|^2}$. The forbidden branch of outcome $b$ is

$$
\widehat M_0(\alpha,\beta)=\beta U_{10}+\alpha U_{11},
\qquad
\widehat M_1(\alpha,\beta)=\beta U_{00}+\alpha U_{01},
$$

and outcome $b$ is certain exactly when $\widehat M_b|D\rangle=0$.

> **Theorem (antipodal pairing).** For every unitary $U$ on $\mathbb C^2\otimes\mathcal H_D$ and every ray,
> $$\dim\ker\widehat M_0(\alpha,\beta)=\dim\ker\widehat M_1(\bar\beta,-\bar\alpha).$$
> The ray $[\bar\beta:-\bar\alpha]$ carries the orthogonal qubit state, so it is the antipode $\mathbf r\mapsto-\mathbf r$, that is $(\theta,\phi)\mapsto(\pi-\theta,\phi+\pi)$, equivalently $\lambda\mapsto-1/\bar\lambda$.

Nothing is assumed about the dimension, the Hamiltonian family, regularity, degeneracy or defectiveness. This is worth emphasising against the scoped promotion in the [[paper-readiness-ledger]]: the matrix-pencil characterization is certified only for non-singular, non-degenerate, non-exotic Hamiltonians, whereas the theorem here carries no such restriction.

## Proof by subspace intersection

This is the argument recorded in the frozen `verifier/exact_formalism/v1/METHOD.md`. Fix the ray $q\subset\mathbb C^2$ and the outcome $b$, and set

$$
S=U\,(q\otimes\mathcal H_D),
\qquad
T=|b\rangle\otimes\mathcal H_D .
$$

A vector $|D\rangle$ lies in $\ker\widehat M_b$ exactly when $U(q\otimes|D\rangle)$ has no component outside $T$, so the kernel dimension equals $\dim(S\cap T)$. Both subspaces have dimension $d=\dim\mathcal H_D$ inside a space of dimension $2d$, and for any two subspaces

$$
\dim(S^{\perp}\cap T^{\perp})=2d-\dim(S+T)=\dim(S\cap T)+2d-\dim S-\dim T,
$$

which reduces to $\dim(S^{\perp}\cap T^{\perp})=\dim(S\cap T)$ when $\dim S=\dim T=d$. Unitarity identifies the complements as $S^{\perp}=U(q^{\perp}\otimes\mathcal H_D)$ and $T^{\perp}=|1-b\rangle\otimes\mathcal H_D$. Hence the orthogonal ray $q^{\perp}$ carries a kernel of the opposite outcome with the same dimension. $\blacksquare$

## Proof by the branch Gram identity

The second route is longer but yields a ray-local identity used elsewhere. For $c=(\beta,\alpha)$ let $J_c|D\rangle=(\beta|0\rangle+\alpha|1\rangle)\otimes|D\rangle$, so that $J_c^{\dagger}J_{c'}=\langle c,c'\rangle I$ and $\widehat M_b(c)=(\langle b'|\otimes I)\,UJ_c$ with $b'$ the branch that outcome $b$ forbids. Summing over the two qubit projectors,

$$
\widehat M_0(c)^{\dagger}\widehat M_0(c')+\widehat M_1(c)^{\dagger}\widehat M_1(c')
=J_c^{\dagger}U^{\dagger}UJ_{c'}
=\langle c,c'\rangle\,I .
$$

This single identity is the whole content of unitarity for the pair of pencils. Two specialisations do the work:

- $c'=c$ gives $\widehat M_0^{\dagger}\widehat M_0+\widehat M_1^{\dagger}\widehat M_1=\|c\|^2I$. The two positive operators therefore commute and are simultaneously diagonalizable, so the squared singular values of the two branches at one ray are pairwise complementary, $\sigma_i^2(\widehat M_0)+\sigma_{d+1-i}^2(\widehat M_1)=\|c\|^2$. In particular a vector killed by one branch is stretched by the other to full norm, so the two branches cannot both vanish.
- $c'=c^{\perp}$ gives $\widehat M_0(c)^{\dagger}\widehat M_0(c^{\perp})=-\widehat M_1(c)^{\dagger}\widehat M_1(c^{\perp})$.

Let $K=\ker\widehat M_0(c)$ of dimension $k$. By the first item $\widehat M_1(c)$ is injective on $K$, so $\widehat M_1(c)K$ has dimension $k$; by the second item it is orthogonal to the whole range of $\widehat M_1(c^{\perp})$. Hence $\operatorname{rank}\widehat M_1(c^{\perp})\le d-k$ and $\dim\ker\widehat M_1(c^{\perp})\ge k$. Exchanging the roles of the two branches and of $c$ and $c^{\perp}$ gives the reverse inequality, so the two kernel dimensions are equal. $\blacksquare$

## Consequences for the outcome measures

With $\mathcal A$ the antipodal map and $\rho_b$ the separately normalized measures of [[projective-roots]]:

1. **The measures are each other's antipodal pushforward,** $\rho_1=\mathcal A_*\rho_0$, weights included, and the total weights agree, $K_1=K_0$. The equal-prior assumption $P(0)=P(1)=\tfrac12$ is therefore consistent with the root counting rather than an extra stipulation.
2. **The strong criterion is a single-measure statement.** Since $\rho_1(\Omega)=\rho_0(-\Omega)$,
   $$p_0(\Omega)=\frac{\rho_0(\Omega)}{\rho_0(\Omega)+\rho_0(-\Omega)},$$
   and the [[born-like-points]] target $p_0=\cos^2(\theta/2)$ is equivalent to the antipodal balance $\rho_0(-\Omega)=\tan^2(\theta/2)\,\rho_0(\Omega)$ wherever the denominator is nonzero. This is the full-sphere refinement of the polar detailed-balance condition $q_*(1/r)=r^4q_*(r)$ recorded in `RESEARCH_STATE.md` §3.
3. **The reflected polar scoring in the codebase is exact, not a surrogate.** Marginalizing over azimuth turns the antipodal map into $\theta\mapsto\pi-\theta$, so $\rho_1^{(\theta)}(\theta)=\rho_0^{(\theta)}(\pi-\theta)$, which is precisely the condition [[born-like-points]] names before a single reflected histogram may be read as the SPEC weak ratio. The `born_ratio_from_theta(theta, pi - theta)` scoring used throughout the search scripts therefore computes the weak criterion itself.
4. **Singular pencils pair too.** If one outcome pencil is singular, so is the other, at antipodal rays; the theorem does not, however, supply the missing measure on either continuum.

The second and third points together explain why the weak criterion has been scored for years while the strong one has not: the weak score needs only one solved pencil and one reflection, whereas the strong score needs the joint $(\theta,\phi)$ density and its antipodal image.

## What the theorem does not give

- It pairs rays and kernel *dimensions*, not the detector kernel vectors. The collapsible detector states of the two outcomes are unrelated by it.
- It selects no measure for a singular pencil's continuum of rays, which remains the open specification decision.
- It makes neither Born criterion true, and it grants no paper-readiness gate. It removes a conditional from the interpretation of existing scores; it supplies no evidence about their values.

## Numerical certification

`tests/test_outcome_antipodality.py` certifies the theorem in the form used here: 13 passed. The Gram identity holds to 1.790e-15 at detector dimension 2 and 5.024e-15 at dimension 8 on Haar unitaries. On the approved families the worst chordal distance from an outcome-1 Bloch root to the antipode of an outcome-0 root is 1.569e-16 for `ring/all` at $N=3$, $t=3.7$ and 7.841e-16 for `chain/first` at $N=4$, $t=211.0$, against a worst non-antipodal separation of 2.000e+00 — the pairing is not a near coincidence of a clustered spectrum. The degenerate fixture $I_2\otimes I_3$ keeps kernel dimension 3 across the map, and the defective completion with algebraic multiplicity two and kernel dimension one at $\lambda=1$ keeps kernel dimension 1. Replacing the antipodal map by the identity is killed by all three kernel-dimension tests.

Residuals of order 1e-12 appear only at $t=211.0$, where the propagator built by `expm` is itself unitary to 3.428e-13; the residual tracks that error, not the theorem.

## Status

**PROVED**, dimension-independent, no family restriction, and numerically certified. The argument was already present in the frozen `verifier/exact_formalism/v1/METHOD.md` and is the premise of `core/gleason_diagnostics.py`, whose asymmetry field is inversion-odd for this reason; this page is where it now lives as durable knowledge.

See also: [[projective-roots]], [[born-like-points]], [[homogeneous-qz]], [[exact-collapse-formalism]], [[research-specification-v1]].
