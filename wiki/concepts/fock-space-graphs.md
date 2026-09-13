# Fock-Space Graphs, Many-Body Localization & Krylov Complexity

## Overview

In many-body quantum mechanics, the state of an $N$-particle system lives in an exponentially large Hilbert space of dimension $\mathcal{N} = 2^N$ (for spins) or $\binom{N}{k}$ (for conserved particle number). While physical interactions occur in real physical space (on a 1D chain, 2D lattice, or detector network), the **dynamics of the quantum state can be mapped exactly to single-particle hopping on a high-dimensional complex graph** known as the **Fock-space graph** (or Hilbert-space graph).

This graph-theoretic representation connects many-body physics directly to spectral graph theory, Anderson localization, quantum chaos, and the operator-growth complexity underlying the `unitary-collapse` program.

---

## 1. The Fock-Space Graph Construction

### Graph Definition
Let $\mathcal{H}$ be the $2^N$-dimensional Hilbert space of $N$ spin-$1/2$ particles. Choose the computational basis (product states in the $Z$-basis):
$$\mathcal{B} = \{|\boldsymbol{\sigma}\rangle = |\sigma_1, \sigma_2, \dots, \sigma_N\rangle : \sigma_i \in \{\uparrow, \downarrow\}\}.$$

The Hamiltonian $\hat{H} = \hat{H}_{\text{diag}} + \hat{H}_{\text{off}}$ defines a graph $G_{\text{Fock}} = (V, E)$:
1. **Vertices $V$:** The $2^N$ computational basis states $|\boldsymbol{\sigma}\rangle$.
2. **Edges $E$:** An undirected edge connects $|\boldsymbol{\sigma}\rangle$ and $|\boldsymbol{\sigma}'\rangle$ if the off-diagonal Hamiltonian matrix element is non-zero:
   $$t_{\boldsymbol{\sigma}, \boldsymbol{\sigma}'} = \langle \boldsymbol{\sigma} | \hat{H}_{\text{off}} | \boldsymbol{\sigma}' \rangle \neq 0.$$
3. **On-Site Potentials:** Each node $|\boldsymbol{\sigma}\rangle$ is assigned an on-site energy given by the diagonal expectation value:
   $$\mathcal{E}_{\boldsymbol{\sigma}} = \langle \boldsymbol{\sigma} | \hat{H}_{\text{diag}} | \boldsymbol{\sigma}' \rangle = \sum_{\langle i,j \rangle} J_{ij} \sigma_i \sigma_j + \sum_i h_i^z \sigma_i.$$

```
                |000>
               /  |  \
         |100>  |010>  |001>       (3-cube / Hypercube Graph)
          | \    / \    / |
         |110>  |101>  |011>
               \  |  /
                |111>
```

### Graph Topologies of Many-Body Hamiltonians
- **Non-Interacting Tight-Binding Model:** Nearest-neighbor hopping on an $N$-dimensional hypercube $\{0, 1\}^N$ (degree $d = N$).
- **Heisenberg / Spin Exchange ($\sum J_{ij} (X_i X_j + Y_i Y_j)$):** In a fixed-magnetization sector with $k$ up-spins, vertices form a **Johnson graph** $J(N, k)$ of dimension $\binom{N}{k}$, where edges connect states differing by a single spin swap.
- **Correlated Disorder:** Crucially, while a standard Anderson localization model on a random graph has independent on-site random energies, the on-site energies $\mathcal{E}_{\boldsymbol{\sigma}}$ on the Fock-space graph are **strongly correlated**: $2^N$ site energies are determined by only $\mathcal{O}(N)$ or $\mathcal{O}(N^2)$ microscopic Hamiltonian couplings.

---

## 2. Many-Body Localization (MBL) as Anderson Localization on Graphs

A breakthrough pioneered by Altshuler, Gefen, Kamenev, and Levitov (AGKL 1997) and formalized by Basko, Aleiner, and Altshuler (BAA 2006) proved that **Many-Body Localization (MBL) in disordered interacting systems is mathematically isomorphic to Anderson localization on a high-dimensional disordered graph**:

### The AGKL / BAA Mapping
- AGKL considered quasiparticle decay in a quantum dot (interacting Fermi liquid). An initial single-particle excitation decays into 2-particle-1-hole (2p-1h) states, which further decay into 3p-2h states, generating a branching tree of accessible configurations in Fock space.
- The Fock-space graph locally resembles a **Bethe lattice (Cayley tree)** with effective coordination number (branching ratio):
  $$K \sim \text{number of accessible decay channels} \propto \epsilon^2 / \Delta,$$
  where $\epsilon$ is the excitation energy and $\Delta$ is the single-particle level spacing.
- **The BAA Transition:** BAA proved that when disorder exceeds a critical threshold $W_c$, destructive quantum interference on the Fock-space graph completely arrests quantum transport. Wave packets remain exponentially localized around a single computational basis state in Fock space:
  $$\psi(\boldsymbol{\sigma}) \sim \exp\left( -\frac{\operatorname{dist}(\boldsymbol{\sigma}, \boldsymbol{\sigma}_0)}{\xi_{\text{Fock}}} \right),$$
  halting thermalization and preserving quantum memory indefinitely.

---

## 3. Non-Ergodic Extended States & Multifractality (De Luca et al. 2014, Tikhonov & Mirlin 2016)

Recent analytical and numerical studies on Bethe lattices and Random Regular Graphs (RRG) revealed that the transition between thermalization and MBL is richer than a simple metal-insulator transition:

### The Three Phases on Fock-Space Expander Graphs
1. **Ergodic Extended Phase ($W < W_E$):**
   Wave functions delocalize uniformly over the entire Hilbert space. The Inverse Participation Ratio (IPR) scales as $I_2 \equiv \sum_{\boldsymbol{\sigma}} |\psi(\boldsymbol{\sigma})|^4 \sim 1/\mathcal{N}$. The system satisfies the Eigenstate Thermalization Hypothesis (ETH) and exhibits Wigner–Dyson level statistics ($\langle r \rangle \approx 0.536$).
2. **Non-Ergodic Extended (NEE) Phase ($W_E < W < W_c$):**
   States are extended throughout the graph (transmission is non-zero), but occupy a vanishing, **fractal subset** of Hilbert space. The generalized IPR scales as:
   $$I_q = \sum_{\boldsymbol{\sigma}} |\psi(\boldsymbol{\sigma})|^{2q} \sim \mathcal{N}^{-\tau(q)}, \quad \tau(q) = D_q(q - 1),$$
   with non-trivial fractal dimension $0 < D_q < 1$ (multifractality). The system violates full thermalization while avoiding complete insulator localization.
3. **Anderson Localized Phase ($W > W_c$):**
   States are strictly localized ($D_q = 0$ for $q > 0$). Spectral statistics are Poissonian ($\langle r \rangle \approx 0.386$).

---

## 4. Krylov Complexity & Operator Growth as 1D Graph Hopping

The mapping of quantum dynamics to graphs extends naturally from state space to **operator space** via the **Krylov subspace method** (Parker, Cao, Avdoshkin, Scaffidi & Altman 2019):

### The Liouvillian Super-Graph
Let $\hat{O}_0$ be a simple local operator (e.g., Pauli $Z_1$). Under Heisenberg evolution, the operator evolves via the Liouvillian superoperator $\hat{\mathcal{L}} = [\hat{H}, \cdot]$:
$$\hat{O}(t) = e^{i\hat{H}t} \hat{O}_0 e^{-i\hat{H}t} = \sum_{n=0}^\infty \frac{(it)^n}{n!} \mathcal{L}^n \hat{O}_0.$$
The operator Hilbert space is equipped with the Frobenius (or Wightman) inner product:
$$(A \mid B) \equiv \frac{1}{\mathcal{N}} \operatorname{Tr}(A^\dagger B).$$

### The Lanczos Algorithm as a 1D Chain Mapping
Applying the Gram–Schmidt / Lanczos algorithm to the Krylov sequence $\{\hat{O}_0, \mathcal{L}\hat{O}_0, \mathcal{L}^2\hat{O}_0, \dots\}$ constructs an orthonormal operator basis $\{|\mathcal{O}_n)\}$ in which the Liouvillian is **strictly tridiagonal**:
$$\mathcal{L} |\mathcal{O}_n) = b_n |\mathcal{O}_{n-1}) + a_n |\mathcal{O}_n) + b_{n+1} |\mathcal{O}_{n+1}).$$

```
    Operator Growth mapped to a 1D Semi-Infinite Tight-Binding Chain:
       b_1           b_2           b_3           b_4
   ( O_0 ) <=====> ( O_1 ) <=====> ( O_2 ) <=====> ( O_3 ) <=====> ...
     a_0           a_1           a_2           a_3
```

- **Krylov Complexity Operator:**
  $$\hat{K} = \sum_{n=0}^\infty n |\mathcal{O}_n)(\mathcal{O}_n| \implies K(t) = (\mathcal{O}(t) | \hat{K} | \mathcal{O}(t)).$$
- **The Universal Operator Growth Hypothesis (Parker et al. 2019):**
  In generic chaotic many-body quantum systems in spatial dimension $d \ge 1$, the Lanczos hopping coefficients grow asymptotically linearly:
  $$b_n \sim \alpha n + \beta \quad (\text{as } n \to \infty),$$
  where $\alpha = \lambda_L / 2$ is directly proportional to the quantum Lyapunov exponent $\lambda_L$ governing out-of-time-order correlators (OTOCs). In integrable systems, $b_n \sim \sqrt{n}$ grows sublinearly.

---

## 5. Quantum Scars & Hilbert-Space Fragmentation

In certain non-integrable many-body systems, quantum thermalization is avoided not by disorder (MBL), but by algebraic structure:
1. **Many-Body Quantum Scars (Turner et al. 2018; Serbyn et al. 2021):** A small, measure-zero set of non-thermal eigenstates embedded in an otherwise chaotic, Wigner–Dyson spectrum. In the Fock-space graph, scars correspond to regular, highly symmetric periodic paths that fail to explore the full graph volume.
2. **Hilbert-Space Fragmentation (Moudgalya et al. 2022):** Strict local dynamical constraints (e.g., dipole conservation, center-of-mass conservation, or fracton constraints) shatter the Fock-space graph into an exponential number of disconnected subgraphs (Krylov sectors), preventing ergodicity even within a single symmetry sector.

---

## 6. Relevance to `unitary-collapse`

The Fock-space graph framework provides crucial analytical machinery for the `unitary-collapse` program:

1. **The Relative Evolution Pencil on Fock Space:**
   In `unitary-collapse`, the block pencil $C_N v = \lambda A_N v$ acts on the $2^N$-dimensional detector Hilbert space. Constructing the matrices $A_N$ and $C_N$ is equivalent to solving an operator-pencil problem on the Fock-space graph of the detector.
2. **Projective Roots as Non-Ergodic Trajectories:**
   Generic eigenstates in chaotic detectors thermalize and spread uniformly across the $2^N$ nodes of the Fock-space graph ($D_q = 1$). In contrast, the **projective roots** $v \in \mathbb{C}^{2^N}$ that satisfy the product-to-product measurement boundary condition must remain coherent and structured: they behave like **many-body scars or non-ergodic extended states** on the Fock-space graph, avoiding thermal scrambling to deliver a definite pointer reading.
3. **Krylov Complexity Bounds on Detector Readout:**
   The readout timescale $t_m$ corresponds to the time required for the qubit operator to propagate to depth $K(t_m)$ along the detector's Krylov chain. If the detector Hamiltonian has bounded operator growth ($b_n \sim \sqrt{n}$ as in 1D rings), the operator spreads without rapid chaotic dispersion, protecting the Born dipole balance condition $C_B$.

---

## Key References

- [[Altshuler-et-al-1997]] — Quasiparticle lifetime and localization on Fock-space graphs.
- [[Basko-Aleiner-Altshuler-2006]] — Foundational paper on Many-Body Localization.
- [[Tikhonov-Mirlin-2016]] — Multifractality and eigenstate statistics on random regular graphs.
- [[Many-Body-Scars]] — Quantum scars and non-thermalizing submanifolds in chaotic systems.
- [[spectral-statistics]] — Level spacing statistics and Wigner–Dyson chaos.
- [[projective-roots]] — Matrix pencil construction of the collapsible state variety.
