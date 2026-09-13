---
name: childs-et-al-2003
description: Landmark paper proving an exponential algorithmic speedup for quantum walk propagation on glued-trees graphs.
metadata:
  type: reference
---

# Childs et al. 2003 — Exponential Algorithmic Speedup by a Quantum Walk

**Reference**: Andrew M. Childs, Richard Cleve, Enrico Deotto, Edward Farhi, Sam Gutmann, and Daniel A. Spielman, "Exponential algorithmic speedup by a quantum walk", in *Proceedings of the Thirty-Fifth Annual ACM Symposium on Theory of Computing (STOC '03)*, ACM, New York, pp. 59–68 (2003). DOI: [10.1145/780542.780552](https://doi.org/10.1145/780542.780552). arXiv: [quant-ph/0209131](https://arxiv.org/abs/quant-ph/0209131).

## Core Thesis
Established the first rigorous, non-oracular demonstration that a continuous-time quantum walk can solve a graph traversal problem **exponentially faster than any classical algorithm**. On the "glued-trees" graph, a classical Markov chain requires time scaling as $2^{n/2} \sim \sqrt{N}$ to traverse from entrance to exit, whereas a quantum walk traverses the entire network in polynomial time $\mathcal{O}(n) = \mathcal{O}(\ln N)$.

## Key Mathematical Formalism
- **The Glued-Trees Graph $G_n$:**
  Two identical balanced binary trees of depth $n$ (each having $2^n$ leaves) are joined at their leaves by a random cycle of alternating edges. The total number of vertices is $N = 2^{n+2} - 2$.
- **Classical Trapping:** A classical random walker starting at the root of Tree 1 moves forward with probability $2/3$ and backward with probability $1/3$ while inside the tree, but once it reaches the glued center, it gets lost in the exponential number of interior vertices. The probability of hitting the exit root before returning to the entrance is exponentially suppressed: $P_{\text{exit}} \le 2^{-n}$.
- **Quantum Column State Reduction:**
  Define the orthonormal column states:
  $$|\mathrm{col}_j\rangle = \frac{1}{\sqrt{N_j}} \sum_{v \in \text{column } j} |v\rangle \quad (j = 0, 1, \dots, 2n + 1).$$
  Because the Hamiltonian respects the column symmetry, the quantum walk starting in $|\mathrm{col}_0\rangle$ remains strictly confined to the $(2n+2)$-dimensional subspace spanned by $\{|\mathrm{col}_j\rangle\}$.
- **Effective 1D Tight-Binding Chain:**
  In the column basis, the walk reduces to an unbranched 1D tight-binding chain of length $2n+2$ with hopping matrix elements $\langle \mathrm{col}_j | H | \mathrm{col}_{j+1} \rangle = -\sqrt{2}\gamma$. The wave packet propagates ballistically across the chain, reaching the exit in time $T \sim \mathcal{O}(n)$.

## Relevance to `unitary-collapse`
Childs et al. prove that symmetry in complex network connectivity can collapse an exponentially large graph into an effectively low-dimensional, ballistically propagating quantum channel. This provides a direct mathematical mechanism for how high-dimensional detector spin networks in `unitary-collapse` can transport measurement signals coherently without becoming trapped in multi-spin ergodic states.
