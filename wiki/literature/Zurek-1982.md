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
While Zurek focuses on **open systems** (system + environment), the `unitary-collapse` project explores whether similar "selection" of specific states (collapsible states) can be achieved in a **closed system** (qubit + detector) purely through the structure of the unitary evolution and the projective roots of the relative propagator. Zurek's "pointer basis" is a conceptual ancestor to the "collapsible states" identified in this project.
