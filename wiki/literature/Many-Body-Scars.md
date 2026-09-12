---
name: many-body-scars
description: Synthesis of research on Quantum Many-Body Scars (QMBS) and weak ergodicity breaking.
metadata:
  type: reference
---

# Quantum Many-Body Scars (QMBS)

**Primary References**: 
- Turner et al., *Nature Physics* **14**, 745–749 (2018).
- Serbyn et al., *Nature Physics* (Review, 2021).
- Moudgalya et al., *Rep. Prog. Phys.* (Review, 2022).

## Core Thesis
Quantum Many-Body Scars represent a "weak" violation of the **Eigenstate Thermalization Hypothesis (ETH)**. While the vast majority of states in a non-integrable system are thermal (obeying ETH), a small, vanishing fraction of "scarred" eigenstates remain non-thermal. These states lead to anomalous dynamics, such as the persistent periodic revivals of an initial product state, even in a nominally chaotic system.

## Key Conceptual Evolution
- **Discovery (Turner 2018)**: Identified in the PXP model of Rydberg atoms. Showed that specific initial states do not thermalize but instead exhibit long-lived oscillations, signaling the presence of a "tower" of scarred eigenstates.
- **Classification (Serbyn 2021)**: Categorized the mechanisms of scar emergence, including spectrum-generating algebras and projector embeddings. Distinguished **Weak Ergodicity Breaking** (QMBS) from **Strong Ergodicity Breaking** (Integrability/MBL).
- **Exactness & Fragmentation (Moudgalya 2022)**: Linked QMBS to **Hilbert Space Fragmentation**, where the Hilbert space splits into disconnected Krylov subspaces. Showed that some scars are exact analytical results rather than just numerical approximations.

## Relevance to `unitary-collapse`
The `unitary-collapse` project's "collapsible states" are functionally equivalent to "many-body scars" in the context of measurement.

1. **Sparsity**: Both QMBS and collapsible states are **sparse** in the Hilbert space but can be **dense** in their respective parameterizations (energy spectrum vs. Bloch sphere).
2. **Anomalous Dynamics**: Just as a scarred state avoids thermalization, a collapsible state avoids the "typical" mixed-state outcome of decoherence, instead evolving into a perfect product state.
3. **Structural Origin**: Both emerge from specific structural properties of the Hamiltonian (e.g., the PXP blockade for scars; the projective root geometry for collapse) that protect these states from the "scrambling" typical of chaotic systems.

In short: **Collapsible states are the "measurement-equivalent" of Many-Body Scars.** They are the non-typical, "special" trajectories that preserve information (disentanglement) in a sea of thermalizing, entangling dynamics.
