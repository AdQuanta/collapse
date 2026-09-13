---
name: griffiths-1984
description: Foundational paper introducing the Consistent Histories interpretation of quantum mechanics.
metadata:
  type: reference
---

# Griffiths 1984 — Consistent Histories and Quantum Interpretation

**Reference**: Robert B. Griffiths, "Consistent histories and the interpretation of quantum mechanics", *Journal of Statistical Physics* **36**(1/2), 219–272 (1984). DOI: [10.1007/BF01015734](https://doi.org/10.1007/BF01015734).

*Companion textbook*: R. B. Griffiths, *Consistent Quantum Theory*, Cambridge University Press, Cambridge (2002). DOI: [10.1017/CBO9780511606052](https://doi.org/10.1017/CBO9780511606052).

## Core Thesis
Quantum mechanics can describe closed, isolated physical systems without external observers, measurement apparatuses, or wave-function collapse. By defining **histories** as time-ordered sequences of projection operators, Griffiths shows that classical probability and Boolean logic can be assigned to a family of histories if and only if quantum interference between alternative histories in the set vanishes (the **consistency condition**).

## Key Mathematical Formalism
- **History Class Operator:** For a sequence of properties $P_{\alpha_k}(t_k)$ at times $t_1 < t_2 < \dots < t_n$:
  $$C_\alpha = P_{\alpha_n}(t_n) P_{\alpha_{n-1}}(t_{n-1}) \cdots P_{\alpha_1}(t_1).$$
- **Consistency Condition (Weak Consistency):** Interference between alternative histories vanishes:
  $$\operatorname{Re}\operatorname{Tr}\left[ C_\alpha \rho_0 C_{\alpha'}^\dagger \right] = 0 \quad (\forall \alpha \neq \alpha').$$
- **Probability Assignment:** When consistency holds, standard Kolmogorov probability additivity is restored:
  $$P(\alpha) = \operatorname{Tr}\left[ C_\alpha \rho_0 C_\alpha^\dagger \right].$$
- **Single-Framework Rule:** Classical reasoning applies strictly within any chosen consistent family, but combining non-commuting frameworks is forbidden.

## Relevance to `unitary-collapse`
Both Griffiths' consistent histories and `unitary-collapse` seek an observer-free, unitary resolution to quantum measurement. While Griffiths allows an infinite multiplicity of incompatible consistent frameworks (leaving open which framework is physically realized), `unitary-collapse` eliminates framework ambiguity by proving that the detector Hamiltonian's matrix pencil $(A_N, C_N)$ uniquely dictates the physical measurement basis and projective roots.
