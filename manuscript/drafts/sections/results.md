# Manuscript Section: Results

In accordance with Step 6 of the **Scientific Writing Skill**, this section is organized into five figure-driven units. Theory and numerical evidence are interleaved so that each mathematical mechanism directly precedes the quantitative evidence that tests it.

---

## Unit 1: Exact Projective Pencil Construction and Antipodal Outcome Duality (Fig. 1)

To identify initial states that evolve into definite measurement outcomes without non-unitary collapse, we examine the global unitary propagator $U(t) = \exp(-\ii H t)$ acting on the composite Hilbert space $\mathcal{H}_S \otimes \mathcal{H}_D = \mathbb{C}^2 \otimes \mathbb{C}^d$. Let the readout qubit occupy the first factor and partition $U(t)$ into $d \times d$ detector-space operator blocks:
\begin{equation}
U(t) = \begin{pmatrix} A & B \\ C & D \end{pmatrix}, \qquad A, B, C, D \in \mathbb{C}^{d \times d}. \label{eq:block_decomp}
\end{equation}
Consider an arbitrary pure initial qubit state parameterized in homogeneous projective coordinates $q = [\alpha : \beta] \in \mathbb{CP}^1$, initialized alongside a detector microstate $\eta \in \mathcal{H}_D$: $|\Psi(0)\rangle = (\alpha|0\rangle + \beta|1\rangle) \otimes \eta$. Forward unitary evolution maps this product state to:
\begin{equation}
U(t)|\Psi(0)\rangle = |0\rangle \otimes (\alpha A + \beta B)\eta + |1\rangle \otimes (\alpha C + \beta D)\eta.
\end{equation}
Consequently, the system evolves into a definite separable output on pole $0$ ($|0\rangle \otimes \eta'$) if and only if the coefficient of $|1\rangle$ vanishes identically:
\begin{equation}
(\alpha C + \beta D)\eta = 0. \label{eq:pencil_0}
\end{equation}
Similarly, the state evolves into a definite output on pole $1$ ($|1\rangle \otimes \eta''$) if and only if $(\alpha A + \beta B)\eta = 0$. In the standard affine chart $z = \beta/\alpha = e^{\ii\phi}\tan(\theta/2)$, these conditions define the generalized matrix pencils $C + zD$ and $A + zB$. For any regular pencil, the Moler-Stewart generalized eigenvalue theorem [19] guarantees exactly $d$ projective roots in $\mathbb{CP}^1$ counted with algebraic multiplicity.

Unitarity enforces a rigorous geometric constraint between the two outcome sets. Let $q^\perp = [-\bar\beta : \bar\alpha]$ denote the Bloch antipode of $q$. Applying Jacobi's theorem on complementary minors to the unitary block matrix $U$, the pencil determinants satisfy:
\begin{equation}
\det(\alpha C + \beta D) = (-1)^d \det(U) \, \overline{\det(-\bar\beta A + \bar\alpha B)}. \label{eq:jacobi_duality}
\end{equation}
Equation \eqref{eq:jacobi_duality} establishes that the outcome-$1$ pencil roots are the exact Bloch antipodes of the outcome-$0$ pencil roots ($\Omega_j^{(1)} = -\Omega_j^{(0)}$ for $j=1,\ldots,d$). A regular $d$-dimensional detector therefore generates exactly $d$ projective coordinates and their labelled antipodal partners. Defining the outcome densities $\rho_0(\Omega)$ and $\rho_1(\Omega)$, antipodality guarantees that $\rho_1(\Omega) = \rho_0(-\Omega)$ and enforces an odd antipodal asymmetry:
\begin{equation}
a(\Omega) = \frac{\rho_0(\Omega) - \rho_0(-\Omega)}{\rho_0(\Omega) + \rho_0(-\Omega)}, \qquad a(-\Omega) = -a(\Omega).
\end{equation}
An ideal projective measurement corresponds to the pure dipole $a_{\mathrm{B}}(\Omega) = \hat{\bm{n}} \cdot \bm{r}(\Omega)$, and Eq. \eqref{eq:jacobi_duality} strictly forbids all even multipoles ($\ell = 0, 2, 4, \ldots$), restricting deviations from Born symmetry exclusively to odd harmonic modes $\ell \ge 3$.

---

## Unit 2: The Haar Scrambling Null Theorem (Fig. 2c)

Does generic chaotic unitary evolution spontaneously select a preferred measurement axis? To establish a rigorous baseline, we analyze the ensemble of Haar-distributed unitaries $U \sim \mathrm{Haar}(2d)$. For a Haar unitary, the block row $(C^\dagger, D^\dagger)^T$ forms a Haar-distributed Stiefel frame in $V_{d, 2d}$. Using the Ginibre decomposition, the matrix pencil can be expressed as $C + z D = G_0 (G_1 + z G_2)$, where $G_0$ is an invertible random matrix and $G_1, G_2$ are independent standard complex Gaussian matrices [20, 21]. 

Because the common factor $G_0$ cancels from the generalized eigenvalue problem, the projective roots of $C + z D$ are distributed identically to the complex spherical ensemble. The one-point intensity of this ensemble is strictly isotropic across the Riemann sphere:
\begin{equation}
\langle \rho_0(\Omega) \rangle_{\mathrm{Haar}} = \frac{d}{4\pi}.
\end{equation}
Consequently, generic Haar scrambling yields an ensemble-averaged asymmetry $\langle a(\Omega) \rangle = 0$ everywhere, and evaluating the polar Born score on this intensity baseline gives $S_{\mathrm{B}} = 0$. Generic scrambling therefore precloses the spontaneous emergence of a preferred measurement axis. Any observed Born dipole must arise from structured many-body interactions rather than random mixing.

---

## Unit 3: Full-Sphere Born Dipoles in Interacting Spin Rings (Fig. 2)

Having proven that generic scrambling produces a flat isotropic null, we investigate whether structured many-body Hamiltonians can generate a Born-like root geometry. We evaluate a clean ring of $N$ detector spins coupled to a central readout qubit:
\begin{align}
H ={}& -h_{z0}Z_0 - h_z\sum_{i=1}^N Z_i - J\sum_{i=1}^N Z_i Z_{i+1} \nonumber\\
&- \frac{J_x}{\sqrt{N}} X_0 \sum_{i=1}^N X_i - \frac{J_y}{\sqrt{N}} Y_0 \sum_{i=1}^N Y_i, \label{eq:hamiltonian}
\end{align}
with periodic boundary conditions ($Z_{N+1} \equiv Z_1$), matched longitudinal fields $h_{z0} = h_z = 0.1$, ferromagnetic Ising coupling $J = 1$, collective transverse coupling $J_x = 0.01$, and $J_y = 0$ in repository units ($\hbar = 1$). Production campaigns solve the generalized eigenvalue problem $C v = \lambda A v$, which identifies the separable outputs of forward evolution $U(t)$, corresponding to forward pole preimages under $U(-t)$.

Figure 2(a) presents the full-sphere root-count asymmetry $a(\phi, \mu)$ ($\mu = \cos\theta$) for $N=16$ detector spins ($d = 65,536$ roots) at $t = 10^4\,\hbar/J$, partitioned into $36$ azimuthal and $18$ polar equal-area bins without smoothing. All 648 bins are occupied, demonstrating complete spherical support. The resulting distribution exhibits a pronounced, clean dipolar gradient aligned with the $z$-axis:
- The linear correlation between the empirical asymmetry $a(\phi, \mu)$ and $\mu = \cos\theta$ is $0.971$.
- The count-weighted residual from the ideal unit Born dipole $\cos^2(\theta/2)$ is $0.089$.
- Spherical harmonic decomposition reveals that the $\ell=1$ dipole mode accounts for $98.2\%$ of resolved odd multipole power through $\ell=7$.
- An unconstrained free dipole fit recovers the exact physical alignment $\hat{\bm{n}} = \hat{\bm{z}}$ to numerical precision, with dipole amplitude $1.062$ and residual $0.070$.

This full-sphere evidence directly refutes the possibility that high polar agreement is an artifact of azimuthal projection.

---

## Unit 4: Finite-Size Scaling and Robustness Across System Scales (Fig. 3)

To determine whether the observed Born dipole reflects systematic dimensional convergence, we evaluate the multiplicity-weighted polar histogram $P(\theta)$ and define the polar ratio and Born score:
\begin{align}
R(\theta) &= \frac{P(\theta)}{P(\theta) + P(\pi-\theta)}, \nonumber\\
S_{\mathrm{B}} &= 1 - 2\int_0^\pi \left| R(\theta) - \cos^2\frac{\theta}{2} \right| \sin\theta \, d\theta. \label{eq:score_def}
\end{align}
In four repository sweeps totaling 1,208 completed spectra, exactly the 24 matched-field rows pass the declared quality gates: full-sphere coverage $\ge 0.5$ and azimuthal second-harmonic distortion $|c_2| \le 0.25$. These comprise four deterministic stored time slices ($t = 10^3, 10^4, 10^5, 10^6\,\hbar/J$) across system sizes $N=11$ through $16$ ($2,048$ to $65,536$ roots).

Figure 3 demonstrates the robust dimensional scaling of the matched spin ring:
1. **Monotonic Polar Convergence**: The four-time median score $S_{\mathrm{B}}$ increases monotonically with detector dimension: $0.192$ at $N=11$, $0.341$ at $N=12$, $0.495$ at $N=13$, $0.638$ at $N=14$, $0.742$ at $N=15$, and reaches $0.807$ at $N=16$ (Fig. 3a).
2. **Unit Spherical Coverage**: The fraction of occupied equal-area bins is exactly $1.000$ for all 24 evaluated rows, establishing that roots span the entire Bloch sphere without unpopulated patches (Fig. 3b).
3. **Harmonic Suppression**: Azimuthal second-harmonic distortion $|c_2|$ remains safely beneath the analysis gate ($|c_2| \le 0.25$) across all sizes and times (Fig. 3c).

The steady rise of $S_{\mathrm{B}}$ contrasts sharply with the flat invariant Haar intensity baseline ($S_{\mathrm{B}} = 0$), establishing that dimensional scaling actively structures the root geometry toward the Born profile.

---

## Unit 5: Theoretical Certification and Rigorous No-Go Boundaries (Fig. 4)

We conclude by mapping the theoretical boundaries that govern Born-like root geometry:
1. **Analytic Certification of the Commuting-X Family**: We analytically prove that there exists an explicit class of Hamiltonians (the Commuting-X family) whose folded energy spectrum $\sum_i s_i g_i$ directly satisfies the finite-resolution Born gate $C_{\mathrm{B}}$, matching the polar profile $\cos^2(\theta/2)$ (Fig. 4a). This demonstrates that Born root geometry can be rigorously designed from first principles.
2. **Detuning-Interval Obstruction (Theorem H)**: For commuting vector fields of the form $H = K - X_q V - Z_q W$ with $[K, V] = 0$, we prove that exact Born balance cannot hold across any open interval of detuning field $b$ (Fig. 4b). Non-commuting dynamics are therefore mathematically indispensable for generic Born behavior.
3. **Failure of Non-Normal Gaussian Shortcuts**: In non-normal operator pencils, we demonstrate that singular-value convergence is insufficient to predict projective root distributions. In the native exchange channel, the exact root measure concentrates at $\delta_0$, whereas naive Gaussian substitution predicts a broad spurious cloud due to logarithmic singular-value tail divergence (Fig. 4c). 

These results prove that Born root geometry is neither a generic scrambling artifact nor an accidental numerical fluke, but the signature of a strictly bounded mathematical class of non-commuting many-body Hamiltonians.
