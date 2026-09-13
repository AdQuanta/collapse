# Quantum Transport on Complex Networks

## Overview

Quantum transport on networks studies the propagation of quantum states, wave packets, and excitations across discrete graphs. Unlike classical transport (which is governed by Markovian diffusion, random walks, and Master equations), quantum transport is fundamentally wave-like, exhibiting interference, quantum speedups, coherent oscillations, and Anderson localization. 

In the `unitary-collapse` program, quantum transport on the detector graph $G = (V, E)$ dictates how rapidly information deposited by the measured qubit propagates through the detector, whether it undergoes destructive interference or dephasing, and whether it scatters back onto the qubit before a measurement record is permanently registered.

---

## 1. Continuous-Time Quantum Walks (CTQW)

First introduced by Edward Farhi and Sam Gutmann (1998), the **Continuous-Time Quantum Walk (CTQW)** is the natural quantum mechanical generalization of continuous-time Markov chains on a graph:

### Hamiltonian Formulation
Let $G = (V, E)$ be a connected graph with $N$ vertices. The Hilbert space is spanned by the orthonormal localized basis states $\{|j\rangle : j \in V\}$. The walk is governed by the Hamiltonian:
$$\hat{H} = -\gamma A \quad \text{or} \quad \hat{H} = \gamma L = \gamma (D - A),$$
where $\gamma$ is the hopping rate, $A$ is the adjacency matrix, and $L$ is the graph Laplacian.

The probability amplitude to transition from node $i$ to node $j$ in time $t$ is given by the matrix element of the unitary evolution operator:
$$\alpha_{j,i}(t) = \langle j | e^{-i\hat{H}t/\hbar} | i \rangle = \sum_{n=1}^N e^{-i E_n t/\hbar} \langle j | \phi_n \rangle \langle \phi_n | i \rangle,$$
where $E_n$ and $|\phi_n\rangle$ are the eigenvalues and orthonormal eigenvectors of $\hat{H}$.

The transition probability is:
$$\pi_{j,i}(t) = |\alpha_{j,i}(t)|^2.$$

### Classical vs. Quantum Spreading
- **Classical Random Walk:** $\frac{d p_j}{dt} = -\sum_k L_{jk} p_k$. Spreading on a 1D line is diffusive: variance $\sigma^2(t) \sim 2 D t$.
- **Quantum Walk:** $i\hbar \frac{d\psi_j}{dt} = \sum_k H_{jk} \psi_k$. Spreading on a 1D line is **ballistic**: variance $\sigma^2(t) \sim v^2 t^2$, providing a quadratic speedup over classical diffusion.

---

## 2. Algorithmic Quantum Speedups: The Glued-Trees Graph

A landmark breakthrough by Childs, Cleve, Deotto, Farhi, Gutmann, and Spielman (2003) demonstrated an **exponential quantum speedup** for transport on networks:

```
      Entrance                                                      Exit
        (o) ------- (o) === ... === [GLUED TREES] ... === (o) ------- (o)
       Tree 1                                                        Tree 2
```

- **Graph Structure:** Two balanced binary trees of depth $n$ connected at their leaves ("glued" randomly by cycle edges). The total number of vertices is $N \approx 2^{n+1}$.
- **Classical Hitting Time:** A classical random walker starting at the entrance node gets trapped in the exponential proliferation of interior leaves: the probability of reaching the exit node scales as $2^{-n} = 1/\operatorname{poly}(N)$, requiring an exponential time $T_{\text{classical}} \sim \mathcal{O}(2^n)$ to find the exit.
- **Quantum Hitting Time:** Due to destructive interference among paths that branch sideways and constructive interference along the symmetry-reduced column states:
  $$|\mathrm{col}_j\rangle = \frac{1}{\sqrt{N_j}} \sum_{v \in \text{column } j} |v\rangle,$$
  the quantum walk reduces to a 1D tight-binding chain of length $2n$. The quantum walk traverses the graph in polynomial time:
  $$T_{\text{quantum}} \sim \mathcal{O}(n) = \mathcal{O}(\ln N).$$
Childs et al. proved that this exponential speedup is a non-oracular, structural property of quantum graph propagation.

---

## 3. Environment-Assisted Quantum Transport (ENAQT)

In realistic physical networks (such as photosynthetic light-harvesting complexes like the Fenna–Matthews–Olson (FMO) complex, or many-body quantum detectors), quantum transport does not occur in complete isolation: it is coupled to an environment that induces **dephasing**.

Counter-intuitively, pure quantum transport on disordered networks is often inefficient because coherent destructive interference causes **Anderson localization**, trapping the excitation in localized eigenstates.

### The Caruso et al. (2009) & Plenio–Huelga Mechanism
Caruso, Chin, Datta, Huelga, and Plenio (2009) and Mohseni et al. (2008) discovered **Environment-Assisted Quantum Transport (ENAQT)**:
- **Zero Dephasing ($\gamma_{\text{deph}} = 0$):** Strong disorder causes destructive interference. Transport efficiency $\eta_{\text{trans}}$ is low due to localized bound states.
- **Infinite Dephasing ($\gamma_{\text{deph}} \to \infty$):** Continuous measurement by the bath induces the **Quantum Zeno Effect**, freezing the excitation at its initial site ($\eta_{\text{trans}} \to 0$).
- **Intermediate Optimal Dephasing ($\gamma_{\text{deph}} \sim \Delta E$):** Moderate environmental dephasing destroys destructive phase coherences without arresting propagation. It allows the quantum wave to hop between localized energy levels, maximizing transport efficiency to near 100%!

```
Transport
Efficiency ^
  100%     |                    * * *  [ENAQT Peak]
           |                  *       *
           |                *           *
           |              *               *
           |  [Localized]                   *  [Quantum Zeno]
     0%    +---------------------------------------------> Dephasing Rate gamma
```

---

## 4. Topology and Quantum Hitting Times

Mülken and Blumen (2011) systematically analyzed CTQW across different complex network topologies:

| Network Topology | Average Path Length $L$ | Quantum Return Probability $\bar{\pi}_{0,0}$ | Transport Characteristic |
|---|---|---|---|
| **1D Ring / Chain** | $\mathcal{O}(N)$ | $\mathcal{O}(1/N)$ | Ballistic spreading; no localization without disorder |
| **Cayley Tree / Bethe**| $\mathcal{O}(\ln N)$ | Bounded away from zero | Reflection from boundaries; constructive traps |
| **Erdős–Rényi ($G(N,p)$)**| $\mathcal{O}(\ln N / \ln\langle k\rangle)$ | Decays rapidly with $N$ | Rapid de-localization; sensitive to percolation threshold |
| **Watts–Strogatz** | Transitions from $\mathcal{O}(N)$ to $\mathcal{O}(\ln N)$ | Drops sharply at $p_{\text{rewire}} \approx 0.05$ | Small-world shortcuts accelerate transport; preserves clustering |
| **Barabási–Albert** | $\mathcal{O}(\ln N / \ln\ln N)$ | High amplitude on hubs | High-degree hubs act as quantum sinks/traps |
| **Random Regular** | $\mathcal{O}(\ln N)$ | Optimal decay $\sim 1/N$ | Maximal quantum mixing; Ramanujan expander behavior |

---

## 5. Relevance to `unitary-collapse`

Quantum transport on networks provides the exact dynamical foundation for the detector phase in `unitary-collapse`:

1. **Information Extraction without Backflow:** When the qubit interacts with site 1 of the detector, the deposit of excitation must travel outward into the detector modes. If the detector graph has high diameter and directional structure (like a 1D ring or tube geometry, Family III in [[hamiltonian-families]]), the excitation propagates away, preventing coherent back-action on the qubit during the readout time $t_m$.
2. **The Hub Localization Hazard:** On Barabási–Albert scale-free networks, quantum walk amplitudes concentrate strongly on high-degree hubs. If the qubit couples to a hub, the excitation remains trapped near the qubit, causing rapid oscillatory backflow that destroys the stable measurement record.
3. **The ENAQT Analogy in Detector Pixels:** In `unitary-collapse`, the intra-pixel interactions $\sum J_{ij} Z_i Z_j + \sum J_{ij}^{\pm} (X_i X_j + Y_i Y_j)$ act as an internal dephasing mechanism. Just as in ENAQT, moderate internal exchange coupling suppresses localized destructively interfering states and allows the measurement record to spread efficiently across the pixel.

---

## Key References

- [[Farhi-Gutmann-1998]] — Foundational formulation of continuous-time quantum walks.
- [[Childs-et-al-2003]] — Exponential algorithmic speedup by a quantum walk on glued trees.
- [[Caruso-et-al-2009]] — Environment-assisted quantum transport (ENAQT).
- [[Mulken-Blumen-2011]] — Comprehensive review of quantum walks on complex networks.
- [[random-graphs]] — Random graph detectors: ER, WS, BA, and Expander topologies.
- [[hamiltonian-families]] — Spatial locality and detector archetypes in unitary collapse.
