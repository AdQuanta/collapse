# The Big Picture: Unitary Collapse

## The Fundamental Question
Can definite measurement-like collapse and Born-like outcome statistics arise from **pure unitary dynamics** of a qubit coupled to a complex many-body detector, without modifying Schrödinger evolution or invoking multiple unobserved Everettian branches?

---

## The Conceptual Trajectory: One More Arrow of Time

A major theme of twentieth-century physics is that an apparent "arrow of time" and effective irreversibility can emerge from time-reversible microscopic unitary laws once inaccessible degrees of freedom are accounted for:

```
Spontaneous emission       Thermalization             Measurement
reduced irreversibility    local relaxation           definite outcome
global unitarity       --> global unitarity       --> unitary route?
[Lindblad/Open Systems]    [ETH/Dephasing/Scrambling] [Restricted State Loophole]
```

1. **Spontaneous Emission:** An excited atom decaying into a vacuum appears irreversible, yet the global system (atom + quantized electromagnetic field) follows exact linear unitary evolution (Lindblad 1976; Breuer & Petruccione 2002).
2. **Thermalization:** Closed many-body systems relax locally toward thermal equilibria even though the global pure wavefunction undergoes reversible Schrödinger evolution (Deutsch 1991; Srednicki 1994).
3. **Measurement:** Can the collapse of the wavefunction be placed on the exact same conceptual trajectory?

---

## The Linearity Obstruction

The standard measurement model correlates a measured qubit with an apparatus and environment:
$$
(\alpha|0\rangle + \beta|1\rangle)|A_{\text{ready}}\rangle|E_{\text{ready}}\rangle \longrightarrow \alpha|0\rangle|A_0\rangle|E_0\rangle + \beta|1\rangle|A_1\rangle|E_1\rangle.
$$
Decoherence and einselection (Zurek 1982, 2003) explain why local interference between branches becomes inaccessible: the reduced density matrix approaches:
$$
\rho_{QA} \simeq |\alpha|^2 |0\rangle\langle 0| \otimes \rho_{A_0} + |\beta|^2 |1\rangle\langle 1| \otimes \rho_{A_1}.
$$
However, decoherence does not alter the global pure state; it remains a macroscopic superposition.

**Established Statement (The Linearity Obstruction):**
If a physical theory assumes:
1. **Universal linear/unitary evolution**, and
2. **Universal physical superposition** (every linear combination of physically possible states is itself physically possible),
then any measurement interaction that correlates basis states with distinct detector records *unavoidably correlates their superpositions with superpositions of macroscopic records* (Bassi & Ghirardi 2000).

---

## The Restricted-State Loophole

The loophole explored in the `unitary-collapse` program is to **retain exact unitarity while relaxing universal physical superposition**.

In the laboratory, an experimentalist never performs an abstract operation: *"take two arbitrary global initial state vectors and add them."* State preparation is itself a physical dynamical process, implemented through a sequence of interactions governed by the Hamiltonian.

It is therefore logically possible that the set of physically realized global states $\mathcal{R} \subset \mathcal{H}$ is only a very small, structured subset of the mathematical Hilbert space, and that this subset is **not closed under vector addition** (not a vector space). In that case, the linear combination used in the standard no-go theorem is mathematically well-defined but physically unrealized.

### The Historical Bohr Analogy (Draft §15.1)
In early quantum theory, Bohr resolved the radiative instability of classical atoms by restricting electrons to a discrete subset of allowed orbits satisfying quantum boundary conditions. Similarly, the mathematical Hilbert space provides a continuous background, but the physically realized states may be restricted by finite-time boundary conditions under the unitary propagator. Unlike Bohr orbits, these special states are Hamiltonian-dependent and become increasingly dense as detector size $N$ grows.

---

## The Tripartite Research Challenge (Draft §15)

The foundational draft (`main.pdf`) clarifies that "unitary collapse" is not one question, but three:
1. **Existence:** Are there product inputs that evolve unitarily to product outcome states?
   - *Status:* **PROVED.** The block-pencil construction reduces this to generalized eigenvalue problems, producing $d = 2^n$ exact special states per outcome.
2. **Statistics:** How are these special states distributed on the Bloch sphere, and why should they obey the Born rule rather than an isotropic/uniform law?
   - *Status:* **ACTIVE RESEARCH.** Structured detectors approach Born-like weights, while Haar-random unitaries are strictly isotropic ([[haar-baseline]]).
3. **Ontology / Selection:** Why should nature occupy this restricted set?
   - *Status:* **OPEN.** Requires an operational preparation/selection measure over microstates, or a dynamical relaxation mechanism driving states toward the collapsible set.

See also: [[projective-roots]], [[born-like-points]], [[haar-baseline]], [[theorem-targets]], [[foundational-draft-aug2026]].
