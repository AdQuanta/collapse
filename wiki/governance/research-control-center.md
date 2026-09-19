# Research Control Center

> Sources: Repository research specification, Unknown; User instruction, 2026-09-15
> Raw: [Research specification v1.0](../../raw/project-governance/research-spec-v1.md); [Paper readiness reset](../../raw/project-governance/2026-09-15-paper-readiness-reset.md)
> Updated: 2026-09-19

## Purpose

This is the starting point for fresh-context work. It separates controlling authority, current state, durable knowledge, evidence, and historical material so an agent can load only the layer needed for the next decision.

## Authority and current state

1. Read the [research specification](research-specification-v1.md) first. The live source is [`SPEC.md`](../../SPEC.md).
2. Then read [`RESEARCH_STATE.md`](../../RESEARCH_STATE.md) for the current frontier.
3. Reconcile every state item against the specification. Where an older goal, acceptance gate, family scope, limit prescription, or manuscript claim conflicts, the specification wins.

4. Consult the [paper readiness ledger](paper-readiness-ledger.md). Every gate is currently `INCOMPLETE`; existing results must be verified again before receiving v1.0 credit.

`RESEARCH_STATE.md` is a handoff, not a historical diary or an independent success definition. It should identify the best current hypothesis, established and falsified results, verifier status, and immediate next experiment or derivation.

## Durable scientific knowledge

Use these pages by question rather than loading the entire wiki:

| Question | Start here |
|---|---|
| What exactly is a collapsible state? | [Projective roots](../concepts/projective-roots.md) |
| What is the current Born target? | [Research specification](research-specification-v1.md), then [Born-like points](../concepts/born-like-points.md) |
| What current analytic obstruction is verified? | [Commuting/QND detector sector](../campaigns/commuting-qnd-sector.md) |
| Where is earlier campaign evidence? | [`research_reports/`](../../research_reports/) and the append-only [research log](../log.md); neither grants v1.0 credit without revalidation |
| Which models are approved now? | [Research specification](research-specification-v1.md), then [Hamiltonian families](../concepts/hamiltonian-families.md) for historical context |
| What numerical conventions apply? | [Homogeneous QZ](../methods/homogeneous-qz.md), [relative evolution](../methods/relative-evolution.md), and [production pipeline](../methods/production-pipeline.md) |

## Progress ledger

The [paper-readiness ledger](paper-readiness-ledger.md) is the only live wiki ledger. The former 87-case ring/chain hierarchy was deleted as obsolete; do not recreate it or route work through its family files. Historical rows remain available in Git history and older reports, but they receive no v1.0 credit unless independently reverified and entered against a current specification gate.

## Evidence and result packets

The specification requires one append-only run ledger and standardized candidate packets. Existing manuscript-era registries remain useful evidence inventories, but they are not themselves a v1.0 certification:

- [`manuscript/EVIDENCE_REGISTRY.md`](../../manuscript/EVIDENCE_REGISTRY.md) — claim-to-artifact inventory from the earlier manuscript scope;
- [`manuscript/NUMERICAL_PROVENANCE.md`](../../manuscript/NUMERICAL_PROVENANCE.md) — provenance for selected manuscript-era numerical claims;
- [`manuscript/RESULTS_NEEDED.md`](../../manuscript/RESULTS_NEEDED.md) — earlier gap analysis;
- [`research_reports/`](../../research_reports/) — detailed derivations, campaign reports, negative results, and audits;
- [`configs/`](../../configs/) — versioned numerical configurations;
- [`hpc/`](../../hpc/) — production campaign runbooks.

Before promoting a candidate, its packet must be remapped to the specification's complete requirements: exact roots and multiplicities, both outcome measures, all four Born metrics, estimator robustness, finite-size and late-time behavior, preferred-basis stability, region robustness, detector-state diagnostics, mechanism and controls, and reproducibility metadata. Prior evidence must be rerun or independently revalidated rather than grandfathered.

## Verifier status

The existing [`verifier/analytic_p_theta/`](../../verifier/analytic_p_theta/) records are frozen, scoped checks for the analytical-distribution program. They do not constitute the complete hybrid verifier required by `SPEC.md` v1.0.

Until an approved full verifier certifies every mandatory gate and a fresh-context referee passes the scientific layer, `paper_ready = false`. Manuscript drafts, narrative registries, and figure plans must not be treated as the active research contract.

## Working loop

For each iteration:

1. select one unresolved specification gate;
2. form a falsifiable mechanism or mathematical hypothesis;
3. run the smallest decisive derivation or experiment in an approved family;
4. append the result to the evidence ledger, including negative evidence;
5. run the frozen applicable verifier;
6. update `RESEARCH_STATE.md` compactly;
7. update the relevant wiki article and paper-readiness gate.

## See Also

- [Audit framework](../audits/framework.md)
- [Scientific rules](../concepts/scientific-rules.md)
- [Symmetry sectors](../concepts/symmetry-sectors.md)
