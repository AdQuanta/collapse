# Projective Roots & Collapsible States

## Physical Setup & The Linearity Loophole
The system is composed of a measured qubit $Q$ coupled to a many-body detector $D$ with Hilbert-space dimension $d = 2^n$:
$$
\mathcal{H} = \mathcal{H}_Q \otimes \mathcal{H}_D, \quad H = H_Q + H_D + H_{QD}, \quad U(t) = e^{-iHt}.
$$
In the standard linearity obstruction, a unitary measurement that correlates basis states $|0\rangle \to |0\rangle|\Phi_0\rangle$ and $|1\rangle \to |1\rangle|\Phi_1\rangle$ inevitably maps an arbitrary superposition $\alpha|0\rangle + \beta|1\rangle$ into an entangled cat state $\alpha|0\rangle|\Phi_0\rangle + \beta|1\rangle|\Phi_1\rangle$.

The **restricted-state loophole** asks: *What initial product states evolve at time $t$ into separable product states aligned with the readout basis?*

---

## Exact Collapsible States (Draft Def. 1)

**Definition:** An initial product state $|\psi\rangle_Q \otimes |\eta\rangle_D$ is an **exact outcome-$k$ collapsible state** at time $t$ if:
$$
U(t)|\psi\rangle_Q \otimes |\eta\rangle_D = |k\rangle_Q \otimes |\Phi_k\rangle_D \quad (k \in \{0, 1\}),
$$
for some normalized detector state $|\Phi_k\rangle_D$. Both the initial and final states are strictly separable, and the final qubit is aligned with a chosen readout pole.

---

## The Block Propagator & Dual Matrix Pencils (Draft §3)

Partition $U(t)$ into $d \times d$ blocks in the qubit readout basis $\{|0\rangle, |1\rangle\}$:
$$
U(t) = \begin{pmatrix} A(t) & B(t) \\ C(t) & D(t) \end{pmatrix}.
$$
Representing the initial qubit state in stereographic coordinates:
$$
|\psi(z)\rangle = \frac{|0\rangle + z|1\rangle}{\sqrt{1+|z|^2}}, \quad z = e^{i\phi}\tan(\theta/2) \in \mathbb{C} \cup \{\infty\},
$$
the evolved state is:
$$
U(t)|\psi(z)\rangle|\eta\rangle = \frac{1}{\sqrt{1+|z|^2}}\Big[ |0\rangle \otimes (A + zB)|\eta\rangle + |1\rangle \otimes (C + zD)|\eta\rangle \Big].
$$

### 1. Dual Outcome Pencils
- **Outcome 0:** Eliminating the $|1\rangle$ component requires $(C + zD)|\eta\rangle = 0$. This is the generalized eigenvalue problem:
  $$
  C|\eta\rangle = \lambda D|\eta\rangle, \quad z = -\lambda.
  $$
- **Outcome 1:** Eliminating the $|0\rangle$ component requires $(A + zB)|\eta\rangle = 0$:
  $$
  A|\eta\rangle = \lambda B|\eta\rangle, \quad z = -\lambda.
  $$

### 2. The Production Complementary-Minor Pencil
In the production pipeline (see `core/relative_evolution_pencil.py` and `core/analysis.py`), the relative evolution pencil is conventionally formulated as:
$$
Cv = \lambda Av.
$$
By unitary complementary-minor duality, this fixed-input-pole pencil is algebraically paired with the forward branches, relating the two outcome multisets by exact Bloch antipodes (see `manuscript/audits/THEORY_AUDIT.md`).

---

## Fundamental Mathematical Propositions

### Proposition 1: Finite Special-State Count (Draft Prop. 1)
For a regular $d \times d$ matrix pencil, $\det(C + zD)$ defines a degree-$d$ generalized characteristic polynomial on the Riemann sphere $\mathbb{C} \cup \{\infty\}$.
- **Exact Count:** Counting algebraic multiplicities, there are generically exactly $d = 2^n$ roots per pencil.
- **Measure Zero:** For any finite $n$, the set of collapsible qubit states is finite, and thus has Lebesgue measure zero on the continuous Bloch sphere $S^2$.

### Proposition 2: Generic Non-Closure Under Superposition (Draft Prop. 2)
Except in nongeneric cases where generalized eigenspaces share a common eigenvalue $z$ and degenerate nullspace:
- Two collapsible states with distinct generalized eigenvalues $z_1 \neq z_2$ possess distinct detector eigenvectors $|\eta_1\rangle \neq |\eta_2\rangle$.
- Their vector sum $(\alpha |\psi(z_1)\rangle|\eta_1\rangle + \beta |\psi(z_2)\rangle|\eta_2\rangle)$ is **entangled** and does not satisfy either pencil null condition with a single common $z$.
- **Consequence:** The physical set of collapsible states is **not a vector space**. Non-closure under superposition is not an ad hoc axiom; it is an exact algebraic consequence of the generalized eigenvalue problem.

---

## Homogeneous Coordinates & Bloch Sphere Mapping (Draft App. B)

To treat finite, infinite ($z = \infty$), and near-singular roots on an equal footing without numerical matrix inversion, roots are solved in homogeneous coordinates $(\alpha, \beta)$ using the **homogeneous QZ algorithm**:
$$
(\alpha C + \beta D)|\eta\rangle = 0.
$$
The corresponding Bloch vector $\vec{r} = (r_x, r_y, r_z)^T \in S^2$ is evaluated projectively:
$$
\vec{r} = \frac{1}{|\alpha|^2 + |\beta|^2} \begin{pmatrix} 2\text{Re}(\alpha^* \beta) \\ 2\text{Im}(\alpha^* \beta) \\ |\alpha|^2 - |\beta|^2 \end{pmatrix}, \quad \theta = 2\operatorname{atan2}(|\alpha|, |\beta|).
$$

---

## Approximate Solutions & Extended Disentangling States (Draft §2.3, §3.3)

### Approximate $\varepsilon$-Collapsible States
In real physical systems and numerical simulations, exact zero nullity is relaxed to a smallest-singular-value problem:
$$
\min_{\|\eta\|=1} \|(C + zD)\eta\| = \sigma_{\min}(C + zD) \le \varepsilon.
$$
This formulation allows the study of finite-width stability basins around exact roots.

### Extended Disentangling States $\mathcal{C}_{\text{sep}}(t)$
The requirement of landing on $|0\rangle$ or $|1\rangle$ is stronger than mere disentanglement. The extended set of disentangling states is:
$$
\mathcal{C}_{\text{sep}}(t) = \{ |\psi\rangle|\eta\rangle : U(t)|\psi\rangle|\eta\rangle = |\phi\rangle|\Phi\rangle \text{ for some } |\phi\rangle, |\Phi\rangle \}.
$$
This corresponds to vanishing bipartite entanglement $S(\rho_Q(t)) = 0 \iff \text{Tr}(\rho_Q^2) = 1$, connecting the theory to the geometry of universal entanglers and product varieties.

See also: [[born-like-points]], [[homogeneous-qz]], [[relative-propagator]], [[foundational-draft-aug2026]].
