# Haar-Random Unitary Baseline & The Spherical Ensemble

## Overview
A critical conceptual baseline in the `unitary-collapse` program is the behavior of **Haar-random global unitaries** $U \sim \text{Haar}(U(2d))$. When the measured qubit interacts with a detector via a maximally generic, unstructured random unitary, does a Born-like dipole emerge?

**Result (PROVED):** No. Haar-random unitaries generate an **isotropically uniform** distribution of special states on the Bloch sphere, yielding a flat 50–50 outcome fraction ($a(\Omega) = 0$).

This establishes a central doctrine of the project:
> **"More random is not more Born."**  
> Maximal genericity erases the distinguished measurement axis. A successful detector must possess structured asymmetry that breaks global isotropy while maintaining sufficient many-body complexity to prevent coherent information backflow.

---

## Proposition 3: Rotational Invariance Proof

**Theorem (Draft §5, Prop. 3):** For Haar-random $U \in U(2d)$, the probability law of the outcome-labelled generalized-eigenvalue point process on the Riemann sphere is invariant under the $SU(2)$ action rotating the qubit Bloch sphere. Consequently, its one-point intensity is uniform on the sphere.

### Proof Sketch
1. Let $R = \begin{pmatrix} r_{00} & r_{01} \\ r_{10} & r_{11} \end{pmatrix} \in SU(2)$ be an arbitrary qubit rotation.
2. By right-invariance of the Haar measure on $U(2d)$, $U$ and $U(R \otimes I_D)$ are identically distributed.
3. The block propagator transforms as:
   $$
   \begin{bmatrix} C' & D' \end{bmatrix} = \begin{bmatrix} C & D \end{bmatrix} \begin{pmatrix} r_{00} I_D & r_{01} I_D \\ r_{10} I_D & r_{11} I_D \end{pmatrix}
   $$
4. Factoring the pencil gives:
   $$
   C' + z D' = (r_{00} + z r_{01}) [C + z' D], \quad \text{where } z' = \frac{r_{10} + z r_{11}}{r_{00} + z r_{01}}
   $$
5. The fractional-linear map $z \mapsto z'$ is the exact **Möbius representation** of the spatial Bloch-sphere rotation induced by $R \in SU(2)$.
6. Because the distribution of the pencil is invariant under this rotation, the generalized-eigenvalue point process is rotationally invariant. A rotation-invariant one-point measure on $S^2$ is strictly uniform.
7. Furthermore, outcome interchange ($|0\rangle \leftrightarrow |1\rangle$) is also a symmetry of Haar measure. Thus, the ensemble-averaged outcome fraction is:
   $$
   f_0(\Omega) = \frac{1}{2}, \quad a(\Omega) = \frac{\rho_0(\Omega)-\rho_1(\Omega)}{\rho_0(\Omega)+\rho_1(\Omega)} = 0.
   $$

---

## Connection to Non-Hermitian RMT: The Spherical Ensemble

The Haar block pencil $(C, D)$ is deeply connected to the **complex spherical ensemble** of random matrix theory (Krishnapur 2009; Alishahi & Zamani 2015).

For two independent complex Ginibre matrices $G_1, G_2 \in \mathbb{C}^{d \times d}$, the generalized eigenvalues of $G_1 - z G_2$ form a determinantal point process on the plane with joint density:
$$
P(z_1, \dots, z_d) \propto \prod_{j<k} |z_j - z_k|^2 \prod_{j=1}^d \frac{1}{(1+|z_j|^2)^{d+1}}.
$$
Under stereographic projection to the sphere, this joint density becomes strictly rotation-invariant, exhibiting quadratic eigenvalue repulsion $|z_j - z_k|^2$ and uniform one-point density.

While the blocks $C$ and $D$ of a Haar unitary are not independent (they are constrained by unitarity $C C^\dagger + D D^\dagger = I$), they share the underlying $SU(2)$ covariance that enforces spherical isotropy.

---

## Numerical Diagnostic Profile
In repository benchmarking (`core/hamiltonian_classification.py` and `work/wd_discriminator_2026-08-27`):
- **Coverage:** $1.000$ (full-sphere support).
- **Polar Score $S_{\text{born}}$:** $\approx -0.045$ (reflecting a flat $50\text{--}50$ line with zero dipole).
- **Harmonic Leakage:** $\approx 0.939$ (94% of angular power lies outside the $\ell = 1$ dipole).
- **Dipole Sharpness:** $\approx 0.029$ (negligible dipolar alignment).

This profile serves as the quantitative negative control for all detector campaigns.

See also: [[big-picture]], [[spectral-statistics]], [[foundational-draft-aug2026]].
