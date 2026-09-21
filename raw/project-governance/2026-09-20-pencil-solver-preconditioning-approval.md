# Homogeneous-Pencil Solver Preconditioning and Exchange-Assertion Approval

> Source: User instruction in the active Claude Code conversation
> Collected: 2026-09-20
> Published: 2026-09-20

## Why this record exists

An independent fresh-context referee reviewing the 2026-09-20 pencil-solver work
noted that an existing test's acceptance assertion had been replaced after the
new code was seen to fail it, with no approval recorded in the repository. That
is the pattern `CLAUDE.md` §Forbidden and `SPEC.md` §23 hard-FAIL condition 9
target. The referee's inference was that no approval had been obtained.

That inference is half right and the correction matters. The user was shown the
substitution, its justification, and its costs, and explicitly chose it in the
conversation before it was made. What was missing was the written record, not the
authorization. This file supplies the record.

## What was approved

Two decisions, each put to the user as an explicit choice among stated
alternatives, each answered before the corresponding change was made.

**1. Default-on preconditioning of the homogeneous pencil solver.** The user was
told that `generalized_relative_evolution_spectrum` is the single root solver for
all of `core/`, `scripts/` and `verifier/`, that changing it shifts every
projective root the project computes, and that `SPEC.md` §0.1 freezes the
verifier while `exact-formalism-v1` is hash-bound to its sources. Presented with
default-on, opt-in, and a forced-left-eigenvector variant, the user chose
**default-on**, on the stated understanding that the exact-formalism packet would
be freshly recertified and the result reported. It was, and it passed.

**2. Restating the exchange-sector assertion.** The user was told that
preconditioning fixes the semisimple ring and chain families but exposes genuine
ill-conditioning in the defective collective-exchange sector, whose existing test
pinned a LAPACK deflation accident. Presented with four options — restate the
assertion, auto-disable preconditioning when a pencil is defective, make
preconditioning opt-in, or stop and defer — the user chose **restate the exchange
test**, specifically to assert exact nilpotency of \(U_{00}^{-1}U_{10}\) by matrix
powers, a basis-independent property, in place of a QZ angle gate.

## What was not approved, and remains outstanding

- **No verifier was activated.** `verifier/matrix_pencil/v1` is proposed as a
  candidate and reports `certification: false`. `SPEC.md` §0.1 reserves
  activation to the user, and it has not been requested or granted.
- **No numerical tolerance was changed** anywhere in this work. The two literals
  removed from the exchange test, \(10^{-12}\) and \(10^{-14}\), were replaced by
  exact equality to zero, which is strictly stronger.
- **No singular-pencil measure rule was adopted.** The characterization refuses
  singular pencils rather than defining a measure on them, because `SPEC.md`
  supplies no rule. That specification decision is still owed by the user.

## Honest account of the cost of decision 2

The restated assertion is strictly stronger as mathematics — exact, tolerance-free
and basis-independent — and strictly weaker as a test of the production solver,
because it no longer exercises the QZ path for root correctness and passes
identically with preconditioning on or off. The earlier `RESEARCH_STATE.md`
characterization that it "strengthens the §5 no-go" stated only the first half.

That coverage loss has since been repaired from a different direction rather than
by reverting: `tests/test_pencil_characterization.py` exercises the production
solver on the same nilpotent sectors through
`core.pencil_characterization.characterize_pencil_roots`, and requires it to
refuse to report usable roots. That test is sensitive to solver behaviour, which
the restated assertion is not.
