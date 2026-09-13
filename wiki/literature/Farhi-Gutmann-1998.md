---
name: farhi-gutmann-1998
description: Foundational paper introducing continuous-time quantum walks on decision trees and general graphs.
metadata:
  type: reference
---

# Farhi & Gutmann 1998 — Quantum Computation and Decision Trees

**Reference**: Edward Farhi and Sam Gutmann, "Quantum computation and decision trees", *Physical Review A* **58**(2), 915–920 (1998). DOI: [10.1103/PhysRevA.58.915](https://doi.org/10.1103/PhysRevA.58.915). arXiv: [quant-ph/9706062](https://arxiv.org/abs/quant-ph/9706062).

## Core Thesis
Introduced the **Continuous-Time Quantum Walk (CTQW)** as a general framework for quantum algorithms and quantum transport. Farhi and Gutmann mapped the adjacency structure of a graph directly into a physical Hamiltonian, showing that a quantum particle can traverse certain decision trees exponentially faster than a classical random walker due to constructive quantum interference along designated paths.

## Key Mathematical Formalism
- **Continuous-Time Quantum Walk Hamiltonian:**
  Let $G = (V, E)$ be an undirected graph with adjacency matrix $A$. The Hilbert space is $\mathcal{H} = \operatorname{span}\{|v\rangle : v \in V\}$. The Hamiltonian is defined directly by the adjacency matrix:
  $$\langle u | \hat{H} | v \rangle = \begin{cases} -\gamma & \text{if } (u, v) \in E, \\ 0 & \text{otherwise,} \end{cases} \implies \hat{H} = -\gamma A,$$
  where $\gamma$ is the transition rate per unit time.
- **Unitary State Evolution:**
  $$|\psi(t)\rangle = e^{-i\hat{H}t/\hbar} |\psi(0)\rangle, \quad i\hbar \frac{d\psi_v(t)}{dt} = -\gamma \sum_{u \in \mathcal{N}(v)} \psi_u(t).$$
- **Traversal of Decision Trees:**
  Farhi and Gutmann analyzed trees where branching causes a classical random walker to get hopelessly lost (exponential hitting time $T \sim 2^n$). They proved that tuning the quantum walk Hamiltonian enables ballistic propagation across the tree in linear time $T \sim \mathcal{O}(n)$, establishing quantum interference as an algorithmic resource for graph traversal.

## Relevance to `unitary-collapse`
Farhi and Gutmann's CTQW is the exact mathematical model describing single-excitation transport in the detector interaction graphs of `core/detector_graphs.py`. When a qubit flips the first detector spin, the excitation propagates through the detector via a CTQW. Understanding the ballistic vs. localized spreading of this quantum walk is essential for establishing whether the detector can achieve macro-record registration on the measurement timescale $t_m$.
