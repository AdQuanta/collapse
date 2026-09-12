---
name: qi-ranard-2021
description: Proof of the universal emergence of classicality via the Quantum Markov Blanket.
metadata:
  type: reference
---

# Qi & Ranard 2021 — Emergent classicality in general multipartite states and channels

**Reference**: X.-L. Qi and D. Ranard, *Quantum* **5**, 555 (2021).

## Core Thesis
The emergence of classical behavior from quantum systems is a universal, structural feature of quantum mechanics, independent of the specific interaction dynamics. This is proven through the existence of a **Quantum Markov Blanket ($Q$)**, a finite region of the environment that "traps" all non-classical information, forcing all other observers in the universe to perceive the system's state as classical.

## Key Contributions
- **The Quantum Markov Blanket ($Q$)**: Proves that for any system-environment interaction, there exists a region $Q$ of constant size $O(1)$ such that any observer outside $Q$ can only access information about the system that is approximately classical.
- **Universal Objectivity**: Because the effective POVM (measurement) used by any observer outside $Q$ is the same, multiple independent observers will necessarily agree on the system's state, explaining the objective nature of classical reality.
- **Dynamic Pointer Basis**: The "pointer basis" is not merely a result of specific Hamiltonian symmetries but is the basis in which the system is effectively measured by the "blanket" $Q$.
- **Entropic Bottleneck**: Uses the strong subadditivity of von Neumann entropy to prove that quantum information cannot be broadcast redundantly; only classical information can survive the "bottleneck" of the Markov blanket.

## Relevance to `unitary-collapse`
Qi and Ranard frame classicality as a **topological/informational property** of the environment. 

The `unitary-collapse` project's "detector" can be viewed as a **physically realized Quantum Markov Blanket**. The "collapsible states" are those that are optimally "measured" by the detector in a way that mimics the behavior of an infinite environment's blanket. 

While Qi and Ranard prove that *some* classical measurement emerges generically, the `unitary-collapse` program focuses on the **specific quality** of that measurement—asking when the resulting statistics follow the **Born Rule**. This bridges the gap between the *existence* of classicality (Qi & Ranard) and the *specific laws* governing that classicality (Born).
