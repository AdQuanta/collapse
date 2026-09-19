# Katz & Kotler 2026 — Probing the Planck Scale with Quantum Computation

> Sources: Katz and Kotler, 2026-04-07
> Raw: [Probing the Planck Scale with Quantum Computation](../../raw/quantum-foundations/2026-04-07-probing-the-planck-scale-with-quantum-computation.md)
> Updated: 2026-09-15

## Overview

Katz and Kotler propose treating a sufficiently large, verified quantum computation as a foundational physics experiment. Their target is not a quantum-gravity interaction measured directly, but classical models underlying quantum mechanics at the Planck scale. The organizing quantity is **Computational Rate Density** (CRD): the number of computational operations realized per unit spacetime volume. The authors argue that quantum computation can compress so many equivalent classical operations into a laboratory run that any classical account reproducing the process would require computational elements below the Planck scale, even after giving that account increasingly generous spatial, temporal, and communication resources.

## Core Construction

The model begins with computing elements separated by a length $l$, each operating once per time step $\tau$. For computer volume $V_3$, runtime $T$, and operation count $N_{\mathrm{ops}}$,

$$
\mathcal{C} \equiv \frac{N_{\mathrm{ops}}}{V_3 T} = \frac{1}{l^3\tau}.
$$

Causality imposes $\tau \ge l/c$, hence $\mathcal{C} \le c/l^4$ and

$$
l \le \left(\frac{V_3 cT}{N_{\mathrm{ops}}}\right)^{1/4}.
$$

The specifically quantum step is the assignment $N_{\mathrm{ops}} \ge 2^n$ equivalent classical operations to a computation using $n$ logical qubits. With that assignment, increasing the verified logical-qubit count pushes the inferred classical element scale downward exponentially. The Planck computational rate density is given as approximately $1.37 \times 2^{490}$ operations $\mathrm{m}^{-3}\mathrm{s}^{-1}$.

## Resource Hierarchy and Thresholds

The paper successively enlarges the resources available to a hypothetical classical explanation. This is the useful structural move: rather than comparing only with a local laboratory simulation, it asks how the bound changes when earlier computations, communication links, and ultimately the causal history of the observable universe are credited to the model.

| Classical account credited with | Logical-qubit threshold quoted for reaching the Planck scale |
|---|---:|
| Large laboratory of $1000\,\mathrm{m}^3$ running for one year | 525 |
| All calculations in the experiment's past light cone since the Big Bang | 806 |
| Fully connected laboratory, counting links between earlier computational events | 1050 |
| Fully connected observable universe, with each event also credited with its causal past | 1609 |

The supplementary discussion gives 882 logical qubits for a relativistic laboratory model with limited temporal memory but broad signal reception. These variants show that connectivity assumptions can move the threshold substantially, while the paper's most permissive construction remains below the logical scale associated with its RSA-2048/Shor scenario.

## What the Proposed Experiment Would Establish

The authors do not claim that factorization alone proves that every quantum amplitude corresponds to a separately executed classical operation. They acknowledge that a classical evolution might use far fewer than $2^n$ operations. Their response is operational: a serious classical contender would need to reproduce not only the final answer but also the tested quantum memories, gates, submodules, and accessible intermediate results of the implemented algorithm. They therefore frame the evidence as cumulative support for quantum mechanics against classical Planck-scale accounts, not as a single-output complexity argument.

Under that framing, a verified large-scale quantum computation would constrain classical substrata that obey the paper's locality, causality, resource-counting, and connectivity assumptions. Conversely, a persistent failure of quantum computation without an identifiable technical cause could motivate a search for a fundamental limit on quantum mechanics. The latter is a proposed diagnostic logic, not a prediction of where or whether such a failure occurs.

## Interpretive Boundaries

- **Indirect probe:** No Planck-scale particle, spacetime fluctuation, or quantum-gravity dynamics is measured. The experiment constrains a class of classical explanations by resource accounting.
- **Key hinge:** The conversion from an $n$-qubit process to at least $2^n$ equivalent classical operations is the central interpretive premise. The CRD thresholds inherit that premise.
- **Model dependence:** The numerical thresholds depend on how computation and communication are counted. The paper makes this dependence visible by presenting a hierarchy from a local lab to a fully connected universe.
- **Verification burden:** The strongest case requires a hard, independently verified computation plus credible validation of the processor's constituent operations; merely possessing a large nominal qubit count is insufficient.
- **NISQ status:** The authors identify noisy random-circuit and boson-sampling experiments as possible earlier routes but leave their NEO accounting unresolved.

## Relevance to `unitary-collapse`

The relation is methodological rather than a shared dynamical mechanism. Both programs ask whether quantum processors can turn a foundational claim into a finite experimental threshold. Katz and Kotler bound the resources available to an underlying classical description; `unitary-collapse` instead predicts detector-, time-, size-, and circuit-dependent departures associated with a restricted set of physically realizable states. The paper does not address single-outcome selection, projective roots, or the derivation of Born probabilities.

The closest bridge is the possibility of a fundamental quantum-computing ceiling. Katz and Kotler cite Planck-scale classical models such as 't Hooft's cellular-automaton interpretation and Palmer's quantum-computing test. Their CRD argument supplies a general resource-accounting template that could help sharpen what a claimed foundational processor threshold actually excludes.

## See Also

- [Falsifiability, Experimental Routes, and Quantum Computing](../concepts/falsifiability-and-experiments.md)
- [Strategic Literature Map](../concepts/literature-map.md)
- [Palmer 2026 — Rational Quantum Mechanics](Palmer-2026.md)
- ['t Hooft 2016 — The Cellular Automaton Interpretation of Quantum Mechanics](tHooft-2016.md)
