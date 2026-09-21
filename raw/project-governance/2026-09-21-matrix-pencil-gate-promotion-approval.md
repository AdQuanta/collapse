# Matrix-Pencil Gate Promotion Approval and Scope Decision

> Source: User instruction in the active Claude Code conversation
> Collected: 2026-09-21
> Published: 2026-09-21

## What was approved

The user approved promoting the **Complete matrix-pencil characterization** row of
`wiki/governance/paper-readiness-ledger.md`, and in the same instruction set the
scope that the promotion is judged against:

> "If the codebase can compute the projective roots properly for all
> non-singular, non-degenerate, non-'exotic' Hamiltonians, I explicitly APPROVE
> promoting the corresponding ledger gate."

The approval is conditional on that domain, and the ledger entry states the
condition rather than claiming more.

## Why the scope decision was needed

Three independent fresh-context referees had refused three successive
submissions. Each refusal rested on a genuine defect, and each defect was
exhibited on a pathological pencil: a Jordan block of size three or more under
an arbitrary change of basis, an exactly defective integer pencil, a singular
Kronecker structure, a regular pencil whose roots sat on the regularity
sampler's own sample points. All were fixed. None of them was reachable from
`SinglePixelHamiltonianNumpy` or its QuSpin twin at physically sensible
parameters.

The user's judgement was that this had become disproportionate: *"I think you're
spending too much time on non-important things instead of the actual physics."*
The scope decision resolves the standing question the 2026-09-19 contract left
open — whether the gate's word "complete" demands exhaustive coverage of
pathological Kronecker structure — by ruling that it does not.

## The evidence the approval was applied to

A 512-configuration sweep of the approved families (rings and endpoint chains,
`central_coupling` in {all, first}, `N = 3..6`, four field settings spanning zero
and nonzero transverse fields, `t` in {1, 37, 211, 500}, both `SPEC.md` §3
outcome pencils) certifies 498. The 14 exceptions are refusals rather than wrong
answers, and both classes lie outside the approved scope: two have root
condition numbers near `1e28`, and twelve are short-time endpoint-coupled cases
whose roots cluster within `sqrt(eps)`.

Establishing this found two defects in the physically approved domain that all
three referee rounds had missed, precisely because those rounds probed
pathologies instead: an absolute kernel-dimension threshold that refused 145 of
512 approved configurations over a factor of two, and a clustering rule that
merged genuinely distinct near-degenerate roots and placed the representative
where the pencil is not singular. Both are fixed and covered by tests.

## What this approval does not cover

- **It is not verifier activation.** `verifier/matrix_pencil/v1` remains a
  candidate reporting `certification: false`. `SPEC.md` §0.1 reserves activation
  to the user, it was not requested here, and the "Executable verifier" gate
  stays `INCOMPLETE`.
- **It is not a singular-pencil measure rule.** The characterization refuses
  singular pencils; the specification decision the 2026-09-19 contract asks for
  is still owed.
- **It grants no credit to any other gate**, and `paper_ready` remains `false`.
