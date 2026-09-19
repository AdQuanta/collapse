# Random Graph Detectors & Complex Networks

## Overview

In the `unitary-collapse` program, the measurement apparatus is modeled microscopically as a quantum many-body spin system (a "detector pixel") coupled to the measured qubit. The spatial connectivity among the detector spins is governed by an **interaction graph** $G = (V, E)$, where vertices $V = \{1, \dots, N\}$ represent physical detector spins and edges $(i, j) \in E$ specify pairwise coupling terms ($Z_i Z_j$ exchange and $X_i X_j + Y_i Y_j$ flip-flop interactions).

The choice of interaction topology $G$ plays a profound role in the physics of unitary collapse:
- **Spatial Locality vs. Scrambling:** 1D chains and rings feature high diameter ($D \sim N$) and slow, ballistic/diffusive operator spreading ($v_B t$), delaying thermalization and preserving coherent phase structures. In contrast, expander graphs and all-to-all networks feature logarithmic diameter ($D \sim \ln N$) and fast information scrambling, driving the system rapidly toward quantum chaos.
- **Symmetry and Degeneracies:** Regular lattices possess spatial translation and reflection symmetries ($D_N$ or $\mathbb{Z}_N$), leading to degenerate multiplets and mixed symmetry sectors. Generic random graphs have trivial automorphism groups ($\operatorname{Aut}(G) = \{e\}$), eliminating accidental degeneracies and isolating single irreducible representations.
- **Testing the Universality of the Born Dipole:** By systematically varying graph topology from 1D rings to Erdős–Rényi, Watts–Strogatz, Barabási–Albert, and Random Regular expanders, the program investigates whether the Born-like root distribution ($R_*(\theta) = \cos^2(\theta/2)$) requires strict spatial locality or persists across complex networks.

---

## Supported Topologies in the Codebase (`core/detector_graphs.py`)

The repository provides deterministic, seed-controlled implementations of five primary graph families:

```
    1D Ring Lattice          Watts-Strogatz          Erdos-Renyi             Barabasi-Albert
     (High Diameter,         (Small-World,           (Homogeneous            (Scale-Free,
      High Clustering)        Short Path Length)      Poisson Degree)         Power-Law Hubs)
         O---O---O               O---O---O               O-------O               ( HUB )
        /         \             / \ /   / \             / \     / \             / / | \ \
       O           O           O---O---O---O           O---O---O---O           O O  O  O O
        \         /             \ / \   \ /             \ /     \ /
         O---O---O               O---O---O               O-------O
     p_rewire = 0            0 < p_rewire < 1        p_edge = c / N          k_i ~ i^(-1/2)
```

### 1. Erdős–Rényi Random Graphs ($G(N, p)$)
- **Construction:** Each of the $\binom{N}{2}$ possible edges is included independently with probability $p \in [0, 1]$.
- **Degree Distribution:** Binomial, converging for large $N$ with mean degree $\langle k \rangle = c = p(N-1)$ to a Poisson distribution:
  $$P(k) = \frac{c^k e^{-c}}{k!}.$$
- **Percolation Threshold:** A giant connected component emerges at $c = 1$. The graph is connected almost surely if $p > \frac{\ln N}{N}$.
- **Physical Role:** Serves as the benchmark for homogeneous, uncorrelated randomness without geometric structure.

### 2. Watts–Strogatz Small-World Networks ($WS(N, k, p)$)
- **Construction:** Begins as a 1D regular ring lattice where each node connects to its $k$ nearest neighbors. Each edge is then independently rewired with probability $p \in [0, 1]$ to a uniformly chosen target node (avoiding self-loops and duplicate edges).
- **Small-World Crossover:**
  - At $p = 0$: Regular lattice with high clustering coefficient $C(0) \approx 3/4$ and long average path length $L(0) \sim N / 2k$.
  - For $0 < p \ll 1$: A handful of long-range shortcuts causes the average path length to drop precipitously to logarithmic scaling $L(p) \sim \ln N$, while the clustering coefficient remains virtually unchanged ($C(p) \approx C(0)$).
  - At $p \to 1$: Converges to a random graph ($L \sim \ln N$, $C \sim k/N$).
- **Physical Role:** Interpolates continuously between strictly local 1D detectors ($p=0$, where audited positive Born leads exist) and non-local random networks ($p > 0$).

### 3. Barabási–Albert Scale-Free Networks ($BA(N, m)$)
- **Construction:** A dynamic growth model with **preferential attachment**. Starting from a small seed graph, new nodes are added sequentially, each establishing $m$ edges to existing nodes $i$ with probability proportional to their current degree:
  $$\Pi(i) = \frac{k_i}{\sum_j k_j}.$$
- **Scale-Free Degree Distribution:** In the large-$N$ limit, the degree distribution follows a stationary power law:
  $$P(k) \propto k^{-\gamma}, \quad \gamma = 3,$$
  independent of $m$.
- **Structural Heterogeneity:** Produces high-degree "hubs" that act as structural focal points, with ultra-short average path length $L \sim \frac{\ln N}{\ln \ln N}$.
- **Physical Role:** Tests whether high-degree hubs pin or localize qubit quantum walks, preventing uniform many-body dephasing.

### 4. Random Regular Graphs & Expander Graphs ($RRG(N, d)$)
- **Construction:** Sampled uniformly from the space of all graphs where every vertex has exactly degree $d$ ($N \cdot d$ must be even). Generated via the Bollobás pairing (configuration) model.
- **Expander Properties:** Random regular graphs with $d \ge 3$ are excellent **expander graphs**: they combine sparse connectivity with high algebraic connectivity, leaving no bottlenecks or localized bottlenecks.
- **Physical Role:** Serves as the ideal testbed for quantum chaos and fast scrambling without the confounding influence of degree fluctuations or boundary effects.

---

## Spectral Graph Theory & Algebraic Connectivity

The dynamics of quantum spins on a graph is deeply connected to the spectral properties of the underlying graph matrices:

### Adjacency and Laplacian Matrices
1. **Adjacency Matrix $A$:** $A_{ij} = 1$ if $(i,j) \in E$, and $0$ otherwise.
2. **Combinatorial Laplacian $L$:**
   $$L = D - A, \quad L_{ij} = \begin{cases} k_i & \text{if } i = j, \\ -1 & \text{if } (i, j) \in E, \\ 0 & \text{otherwise,} \end{cases}$$
   where $D = \operatorname{diag}(k_1, \dots, k_N)$ is the degree matrix.
3. **Normalized Laplacian $\mathcal{L}$:**
   $$\mathcal{L} = D^{-1/2} L D^{-1/2} = \mathbb{I} - D^{-1/2} A D^{-1/2}.$$

### The Spectral Gap and Cheeger's Inequality
The eigenvalues of the combinatorial Laplacian satisfy:
$$0 = \lambda_1 \le \lambda_2 \le \dots \le \lambda_N.$$
The second smallest eigenvalue $\lambda_2(L)$ is the **algebraic connectivity** (Fiedler value):
- $\lambda_2 > 0$ if and only if the graph $G$ is connected.
- For a 1D ring, $\lambda_2 \sim \frac{4\pi^2}{N^2} \to 0$ as $N \to \infty$ (diffusive/ballistic bottleneck).
- For a random regular expander graph, $\lambda_2 \ge c > 0$ remains strictly bounded away from zero as $N \to \infty$.

**Cheeger's Isoperimetric Constant $h(G)$:**
$$h(G) = \min_{S \subset V, 0 < |S| \le |V|/2} \frac{|\partial S|}{|S|},$$
where $|\partial S|$ is the number of edges connecting $S$ to $V \setminus S$. Cheeger's inequality bounds the spectral gap:
$$2 h(G) \ge \lambda_2 \ge \frac{h(G)^2}{2 d_{\max}}.$$
A large spectral gap $\lambda_2$ implies that the graph has no structural bottlenecks: quantum information and excitations cannot be trapped in local subgraphs.

### Ramanujan Bound for Optimal Expanders
Alon and Boppana proved that for any $d$-regular graph, the second largest eigenvalue of the adjacency matrix satisfies:
$$\lambda_2(A) \ge 2\sqrt{d - 1} - o(1) \quad (\text{as } N \to \infty).$$
A $d$-regular graph achieving $\lambda_2(A) \le 2\sqrt{d-1}$ is called a **Ramanujan graph** (Lubotzky, Phillips & Sarnak 1988). Random regular graphs are asymptotically almost Ramanujan (Friedman's theorem, 2004).

---

## Quantum Dynamics: Continuous-Time Quantum Walks on Graphs

A single excitation hopping on graph $G$ is modeled as a **Continuous-Time Quantum Walk (CTQW)** (Farhi & Gutmann 1998; Mülken & Blumen 2011):

### Hamiltonian Formulation
The single-particle Hamiltonian on $\mathcal{H}_1 = \operatorname{span}\{|1\rangle, \dots, |N\rangle\}$ is:
$$\hat{H} = -\gamma A \quad \text{or} \quad \hat{H} = \gamma L = \gamma (D - A),$$
where $\gamma$ is the tunneling rate. The quantum state evolves via:
$$|\psi(t)\rangle = e^{-i\hat{H}t/\hbar} |\psi(0)\rangle = \sum_{j=1}^N \langle j | e^{-i\hat{H}t/\hbar} |i\rangle |j\rangle.$$

### Transition Amplitudes and Return Probability
The transition amplitude from node $i$ to node $j$ is:
$$\alpha_{j,i}(t) = \langle j | e^{-i\hat{H}t/\hbar} | i \rangle = \sum_{n=1}^N e^{-i E_n t/\hbar} \langle j | \phi_n \rangle \langle \phi_n | i \rangle,$$
where $\{|\phi_n\rangle\}$ are the eigenvectors of $A$ or $L$. The **quantum return probability** is:
$$P_{i \to i}(t) = |\alpha_{i,i}(t)|^2 = \left| \sum_{n=1}^N e^{-i E_n t/\hbar} |\langle i | \phi_n \rangle|^2 \right|^2.$$

### Classical vs. Quantum Spreading
| Metric | Classical Random Walk ($\dot{p} = -L p$) | Quantum Walk ($i\dot{\psi} = L \psi$) |
|---|---|---|
| **Propagator** | Stochastic matrix $T(t) = e^{-L t}$ | Unitary operator $U(t) = e^{-iLt}$ |
| **Limiting State** | Thermal/stationary distribution $p_i^* = d_i / 2|E|$ | No stationary state; persists in coherent oscillations |
| **Spreading on 1D Ring** | Diffusive: $\sigma(t) \sim \sqrt{t}$ | Ballistic: $\sigma(t) \sim t$ |
| **Hitting Time on Trees** | Exponential: $T_{\text{hit}} \sim 2^h$ (Childs et al. 2003) | Polynomial / Exponential speedup via destructive interference |
| **Limiting Uniformity** | Approached monotonically via entropy increase | Time-averaged probability $\bar{P}_{ij} = \sum_n |\langle i | \phi_n \rangle|^2 |\langle j | \phi_n \rangle|^2$ |

---

## Quantum Chaos & Level Statistics on Graphs (Kottos & Smilansky)

When the detector contains multiple interacting spins, the many-body spectrum undergoes a transition between integrability (Poissonian statistics) and quantum chaos (Wigner–Dyson statistics):

### Kottos–Smilansky Quantum Graphs (1997, 1999)
Kottos and Smilansky demonstrated that quantum wave propagation on non-trivial graphs provides the cleanest mathematical paradigm for quantum chaos:
- In the semiclassical limit, closed classical orbits on the graph correspond to periodic paths.
- An exact **trace formula** expresses the quantum density of states in terms of periodic orbits:
  $$d(E) = \bar{d}(E) + \frac{1}{\pi} \operatorname{Im} \sum_{p} \sum_{r=1}^\infty \frac{L_p}{r} \mathcal{A}_{p,r} e^{i r k L_p}.$$
- On chaotic graphs (e.g., incommensurate bond lengths or random connectivity), the spectral level spacings $s = (E_{i+1} - E_i)/\Delta$ follow the Wigner surmise of Random Matrix Theory (RMT):
  $$P(s) = \frac{\pi}{2} s \, e^{-\frac{\pi}{4} s^2} \quad (\text{GOE, linear level repulsion}).$$

### The $r$-Statistic Metric
In `core/graph_spectral_sectors.py`, level repulsion is quantified using the consecutive spacing ratio $r_n$ (Atas et al. 2013):
$$r_n = \frac{\min(s_n, s_{n-1})}{\max(s_n, s_{n-1})}, \quad \langle r \rangle_{\text{Poisson}} \approx 0.386, \quad \langle r \rangle_{\text{GOE}} \approx 0.536, \quad \langle r \rangle_{\text{GUE}} \approx 0.600.$$

---

## Localization & Many-Body Localization (MBL) on Networks

The phenomenon of localization on complex graphs provides a critical bridge to many-body physics:

### Anderson Localization on the Bethe Lattice (Abou-Chacra, Thouless & Anderson 1973)
The Bethe lattice (infinite regular Cayley tree with coordination number $K+1$) is an exactly solvable model for localization:
- Due to the absence of closed loops, self-energies satisfy independent recursive relations.
- In 1973, Abou-Chacra, Thouless, and Anderson proved that a critical disorder threshold $W_c$ separates an extended phase from an exponentially localized phase.
- In 2014, De Luca, Altshuler, Kravtsov, and Scardicchio discovered that the extended phase on Bethe lattices and random regular graphs contains a broad **non-ergodic extended (NEE)** regime: states are extended throughout the graph but occupy a fractal subset of vertices with fractal dimension $0 < D_q < 1$ (multifractality).

### The Fock Space as a Complex Network (Altshuler et al. 1997, BAA 2006)
Basko, Aleiner, and Altshuler (2006) recognized that **Many-Body Localization (MBL)** in interacting quantum spin systems can be mapped mathematically to single-particle Anderson localization on a disordered graph:
- **Vertices:** The $2^N$ computational basis states $|\sigma_1 \dots \sigma_N\rangle$ form the nodes of an $N$-dimensional hypercube graph.
- **Edges:** Local flip-flop interactions $(X_i X_j + Y_i Y_j)$ connect basis states differing by two spins.
- **On-Site Potentials:** Diagonal interactions $\sum J_{ij} Z_i Z_j + \sum h_i Z_i$ act as correlated on-site random energies.
The MBL transition is literally a localization transition on this high-dimensional Fock-space graph.

---

## Symmetry Resolution on Interaction Graphs (`core/graph_spectral_sectors.py`)

A critical requirement of the `unitary-collapse` pipeline is that level-spacing statistics must never be computed across mixed symmetry sectors:

### The Problem of Spurious Poisson Statistics
If a detector Hamiltonian commutes with a non-trivial spatial symmetry group $\mathcal{G} = \operatorname{Aut}(G)$, eigenvalues from different irreducible representations (irreps) are statistically independent. Superimposing multiple independent GOE spectra results in an artificial Poissonian distribution ($\langle r \rangle \to 0.386$), falsely mimicking an integrable system.

### The Resolution Pipeline in `core/graph_spectral_sectors.py`:
1. **Computational Hamming Weight Conservation ($U(1)$):**
   The detector Hamiltonian conserves the total number of up-spins:
   $$\hat{N}_{\uparrow} = \sum_{i=1}^N \frac{\mathbb{I} + Z_i}{2}, \quad [H_D, \hat{N}_{\uparrow}] = 0.$$
   The $2^N$-dimensional Hilbert space factorizes into disjoint blocks of dimension $\binom{N}{w}$ for $w = 0, 1, \dots, N$.
2. **Graph Automorphisms ($\operatorname{Aut}(G)$):**
   Using `core.graph_symmetry.graph_automorphisms`, the pipeline constructs the full symmetry permutation group $\mathcal{G} \le S_N$ satisfying:
   $$\pi(A) = A \quad (\forall \pi \in \mathcal{G}).$$
3. **Spin-Reversal Symmetry at Half-Filling ($\mathbb{Z}_2$):**
   At $w = N/2$ (for even $N$), the Hamiltonian commutes with global spin-flip $\mathcal{C} = \bigotimes_{i=1}^N X_i$.
4. **Group-Algebra Projector:**
   The code evaluates a deterministic, generic Hermitian element of the group algebra $\mathbb{C}[\mathcal{G}]$:
   $$\hat{\Omega} = \sum_{\pi \in \mathcal{G}} c_\pi \hat{P}_\pi,$$
   which splits each Hamming sector into distinct, non-degenerate irreducible representation rows. Level statistics $\langle r \rangle$ are evaluated strictly within individual non-trivial invariant sectors.

---

## Role in `unitary-collapse`: Locality vs. Scrambling

The interaction graph determines whether the detector acts as an ideal measurement apparatus:

```
+-----------------------------------------------------------------------------------------+
|                                    THE TOPOLOGY SPECTRUM                                |
|                                                                                         |
|  1D Chain / Ring               Watts-Strogatz (p ~ 0.1)          Expander / All-to-All  |
|  Strict Locality               Small-World Network               Maximal Scrambling     |
|                                                                                         |
|  * High diameter (D ~ N)       * Low diameter (D ~ ln N)         * Minimal diameter     |
|  * Zero spectral gap           * High clustering preserved       * Maximal spectral gap |
|  * Slow operator spreading     * Efficient dephasing             * Instant thermalization|
|  * Positive Born leads!        * Transitional Born scores        * Haar isotropic decay |
+-----------------------------------------------------------------------------------------+
```

1. **Historical Ring Leads:** Legacy calculations in `RESEARCH_STATE.md` and earlier reports observed that structured detectors with 1D periodic ring topology achieved favorable scalar scores ($S_{\text{born}} > 0.93$, ratio RMSE $< 0.02$). Under SPEC v1.0, these scalar thresholds are historical diagnostics only; genuine paper readiness requires certifying the full 4-metric suite ($E_2, E_\infty, E_{\text{harm}}, E_{\text{marg}}$) under the frozen verifier across an open weak-coupling region with matched controls.
2. **Expander / Scrambling Hypothesis:** Large graph gaps can promote rapid mixing and may drive roots toward an isotropic Haar-like baseline, but this mechanism has not been established for the SPEC pencils. For a uniform outcome ratio $p_0=1/2$, the SPEC error against Born is $E_2=1/(2\sqrt3)$, not zero.
3. **The Small-World Frontier:** Watts–Strogatz networks allow continuous tuning of the rewiring probability $p_{\text{rewire}}$, providing a potential future probe in the generality program (SPEC §18) to study how shortcuts degrade candidate mechanisms.

---

## Key References

- [[Erdos-Renyi-1959]] — Foundational paper on random graphs and component evolution.
- [[Watts-Strogatz-1998]] — Collective dynamics of small-world networks.
- [[Barabasi-Albert-1999]] — Scale-free networks and preferential attachment.
- [[Chung-1997]] — Spectral Graph Theory: Laplacians, Cheeger inequalities, and expanders.
- [[Farhi-Gutmann-1998]] — Continuous-time quantum walks on graphs.
- [[Kottos-Smilansky-1997]] — Quantum chaos on graphs and Wigner-Dyson spectral statistics.
- [[Mulken-Blumen-2011]] — Comprehensive review of quantum walks on complex networks.
- [[Abou-Chacra-Thouless-Anderson-1973]] — Anderson localization on the Bethe lattice.
- [[Basko-Aleiner-Altshuler-2006]] — Many-body localization as localization on Fock-space graphs.
- [[hamiltonian-families]] — Detector Hamiltonian archetypes and interaction architectures.
- [[spectral-statistics]] — Level spacing ratios and symmetry-resolved spectra.
