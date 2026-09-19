# Results

## 1. Homogeneous pencils classify pole-compatible product inputs (Fig. 2)

Let the readout qubit be the first factor of $\mathbb C^2\otimes\mathbb C^d$, and partition the unitary propagator into detector-space blocks,

\[
U(t)=\begin{pmatrix}A&B\\C&D\end{pmatrix},
\qquad A,B,C,D\in\mathbb C^{d\times d}.
\]

For a qubit ray $q=[\alpha:\beta]\in\mathbb{CP}^1$ and detector vector $\eta\neq0$,

\[
U[(\alpha|0\rangle+\beta|1\rangle)\otimes\eta]
=|0\rangle\otimes(\alpha A+\beta B)\eta
+|1\rangle\otimes(\alpha C+\beta D)\eta.
\]

The output lies on qubit pole $0$ exactly when

\[
(\alpha C+\beta D)\eta=0,
\]

and on pole $1$ exactly when $(\alpha A+\beta B)\eta=0$. In the affine chart $z=\beta/\alpha=e^{\mathrm i\phi}\tan(\theta/2)$, these conditions become the pencils $C+zD$ and $A+zB$. The homogeneous formulation retains $z=\infty$. A regular $d\times d$ pencil has exactly $d$ roots in $\mathbb{CP}^1$, counted with algebraic multiplicity \cite{MolerStewart1973}. This count does not imply distinct roots or equal physical weights; singular pencils require Kronecker rather than ordinary eigenvalue analysis.

Unitarity relates the two outcome labels exactly. If $q^\perp=[-\bar\beta:\bar\alpha]$ denotes the Bloch antipode, Jacobi complementary-minor duality gives

\[
\det(\alpha C+\beta D)
=(-1)^d\det(U)\,
\overline{\det(-\bar\beta A+\bar\alpha B)}.
\]

Hence the outcome-$1$ roots are the exact antipodal multiset of the outcome-$0$ roots, including algebraic multiplicity. For identically processed root measures,

\[
\rho_1(\Omega)=\rho_0(-\Omega),\qquad
a(\Omega)=\frac{\rho_0(\Omega)-\rho_0(-\Omega)}
{\rho_0(\Omega)+\rho_0(-\Omega)},
\]

so $a(-\Omega)=-a(\Omega)$. An ideal projective Born profile is the unit dipole $a_{\mathrm B}(\Omega)=\hat{\bm n}\cdot\bm r(\Omega)$. Exact antipodality removes even multipoles from the paired asymmetry, but it does not remove higher odd contributions or require a uniform total root density.

## 2. Haar propagators provide an exact isotropic ensemble null

For $U\sim\mathrm{Haar}(2d)$, the adjoint block row formed from $C$ and $D$ is a Haar Stiefel frame. Its Ginibre representation contributes a common invertible factor that cancels from the generalized-root problem. The roots of $C+zD$ therefore have exactly the complex spherical-ensemble law \cite{Krishnapur2009,AlishahiZamani2015}, with one-point intensity

\[
\langle\rho_0(\Omega)\rangle_{\mathrm{Haar}}=\frac{d}{4\pi}.
\]

The Haar ensemble consequently has no fixed preferred axis at the one-point level, and its normalized ensemble intensity gives $S_{\mathrm B}=0$. This is an exact finite-$d$ ensemble statement, not a claim that a single finite Haar realization is uniform or a concentration bound for its fluctuations.

## 3. The production pencil is an inverse-time forward construction

The post-cutoff campaigns fix the input pole and solve

\[
Cv=\lambda Av,
\qquad
U(|0\rangle\otimes v)=(|0\rangle+\lambda|1\rangle)\otimes Av,
\]

for finite roots. These roots enumerate separable output qubits of $U(t)$. Equivalently, they are exact forward pole-$0$ preimages for $U^\dagger(t)=U(-t)$, and the companion outcome coordinates follow by antipodal duality. For the highlighted real Hamiltonian, changing $t\to-t$ conjugates the roots, reflecting $\phi$ while preserving $\theta$ and every quoted fixed-$z$ polar diagnostic. The stored production roots therefore support the polar comparisons below, but they are not silently identified with the same-time forward pencil.

## 4. A matched spin ring develops a strongly dipolar full-sphere asymmetry (Fig. 3)

We analyze the clean ring Hamiltonian

\[
\begin{aligned}
H={}&-h_{z0}Z_0-h_z\sum_i Z_i-J\sum_i Z_iZ_{i+1}
-J_{\pm}\sum_i(\sigma_i^+\sigma_{i+1}^-+\mathrm{H.c.})\\
&-\frac{J_x}{\sqrt N}X_0\sum_iX_i
-\frac{J_y}{\sqrt N}Y_0\sum_iY_i,
\end{aligned}
\]

with periodic detector bonds, $h_{z0}=h_z=0.1$, $J=1$, $J_{\pm}=J_y=0$, and collective $J_x=0.01$ in units with $\hbar=1$.

Figure 3 shows the audited $N=16,t=10^4$ map. The 65,536 finite production roots and their exact antipodal partners populate all 648 cells of a $36\times18$ equal-area $(\phi,\mu)$ grid, with $\mu=\cos\theta$, without smoothing. The resulting asymmetry is strongly aligned with the $z$-axis: its correlation with $\mu$ is $0.971$, and its count-weighted residual from the unit Born dipole is $0.089$. A spherical-harmonic projection through $\ell=7$ assigns $0.982$ of the resolved odd power to $\ell=1$. A free weighted dipole fit returns $\hat{\bm n}=\hat{\bm z}$ to the displayed precision, amplitude $1.062$, and residual $0.070$.

The full-sphere map matters because a favorable polar marginal can coexist with severe azimuthal pinching. Here every displayed equal-area cell is occupied, and the two-dimensional field is dipole dominated. The result remains finite resolution: the residual rises on finer grids once cells become sparsely populated, so we make no continuum claim.

## 5. The matched sequence shows a monotonic finite-size trend (Fig. 4)

Let $P(\theta)$ denote the multiplicity-weighted production-root histogram and define

\[
R(\theta)=\frac{P(\theta)}{P(\theta)+P(\pi-\theta)},
\]

\[
S_{\mathrm B}=1-2\int_0^\pi
\left|R(\theta)-\cos^2\frac{\theta}{2}\right|
\sin\theta\,\mathrm d\theta.
\]

The ideal profile gives $S_{\mathrm B}=1$, while the isotropic Haar one-point intensity gives $S_{\mathrm B}=0$. In the four audited sweep tables, exactly 24 of 1,208 completed spectra pass the declared polar-coverage and second-harmonic gates; all 24 are matched-field rows comprising four deterministic saved times at each $N=11,\ldots,16$.

The four-time median score rises monotonically with $N$:

| $N$ | 11 | 12 | 13 | 14 | 15 | 16 |
|---:|---:|---:|---:|---:|---:|---:|
| median $S_{\mathrm B}$ | 0.192 | 0.411 | 0.571 | 0.715 | 0.788 | 0.807 |

All 24 matched rows have unit polar coverage and satisfy $|c_2|\le0.25$. These quantities establish a descriptive finite-size trend. The four times are deterministic observations rather than stochastic replicates; $|c_2|$ probes only the second azimuthal harmonic; and the six sizes do not justify a thermodynamic extrapolation or identify the mechanism behind the matched-field condition.

## 6. Existence, geometry, and measurement remain distinct

The exact results answer an existence question: which product boundary states reach definite qubit poles, and how are their labels related? The Haar theorem and matched-ring calculations address geometry: whether the corresponding root counts are isotropic or dipolar. They do not answer selection. Algebraic multiplicity is not a preparation probability, different roots generally require different detector microstates, and instantaneous factorization does not demonstrate stable, distinguishable, or redundant records. The evidence therefore supports a structural classification program, not a completed unitary theory of measurement.
