---
name: zurek-1982
description: Foundational paper on environment-induced superselection (einselection).
metadata:
  type: reference
---

# Zurek 1982 — Environment-induced superselection rules

**Reference**: W. H. Zurek, *Phys. Rev. D* **26**, 1862 (1982).

## Core Thesis
Measurement-like "collapse" is an emergent property of open quantum systems. The interaction between a system and its environment "selects" a privileged set of states—the **pointer basis**—that are stable against decoherence.

## Key Mechanisms
- **Einselection**: Environment-induced superselection. The interaction Hamiltonian $H_{int}$ determines the pointer basis as the set of eigenstates of the observable that commutes with $H_{int}$.
- **Decoherence**: The environment effectively "monitors" the system, causing the off-diagonal elements of the reduced density matrix to decay rapidly.
- **Emergence of Classicality**: The transition from a coherent quantum superposition to an effective statistical mixture of classical alternatives.

## Relevance to `unitary-collapse`
While Zurek studies a subsystem coupled to an environment, this project asks whether a closed qubit–detector unitary has exact product inputs that reach definite qubit outputs and whether their two root measures become Born-like. Pointer-basis selection is relevant to the SPEC preferred-axis gate, but decoherence does not supply the required root statistics or a physical root-selection law.
