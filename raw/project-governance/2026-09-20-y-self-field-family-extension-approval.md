# Y Self-Field Family Extension Approval

> Source: User instruction in the active Claude Code conversation
> Collected: 2026-09-20
> Published: 2026-09-20

## What was approved

The user directed that the open-1D-chain Born search vary the complete set of
twelve model parameters:

- qubit self-field \(h_{0x}, h_{0y}, h_{0z}\);
- detector self-field \(h_x, h_y, h_z\);
- intra-detector interaction \(J_{xx}, J_{yy}, J_{zz}\);
- qubit–detector coupling \(g_x, g_y, g_z\).

Ten of these already existed in `core/hamiltonians`. The two \(Y\) self-fields,
\(h_y\) and \(h_{0y}\), did not exist anywhere in the repository. Supplying them
requires adding new terms to the approved single-pixel Hamiltonian family, which
`SPEC.md` §23 hard-FAIL condition 9 forbids the research agent from doing without
explicit user approval. The user was told this and approved the change,
explicitly choosing that it be recorded here as a governed family change rather
than treated as routine.

## The terms added

Both twins, `SinglePixelHamiltonianNumpy` and `SinglePixelHamiltonianQuSpin`,
gained `hy` and `hy0` (the latter falling back to `hy` when unset, matching the
existing `hx0`/`hz0` convention). Keeping the builder's overall minus sign, the
Hamiltonian gains

\[
-\,h_{0y} Y_0 \;-\; h_y \sum_{i=1}^{N} Y_i .
\]

As with every other coefficient in this builder, the code parameters are the
negatives of the `SPEC.md` §9 coefficients.

## Why this is inside the approved hierarchy

`SPEC.md` §10.2 orders the one-body-field hierarchy as longitudinal fields, then
one transverse direction, then "fully general \(x,y,z\) fields only if needed."
The \(Y\) self-fields are therefore the top rung of a hierarchy the spec already
contemplates, not a new kind of term. They are unlocked here by user instruction
rather than by the systematic-failure route of §10.4, and the campaign's rung
structure keeps them at zero until the lower rungs have been scanned.

The \(Y\) fields are not redundant within this family. A qubit rotation that
removes \(h_{0y}\) turns the diagonal coupling \(\sum_\alpha g_\alpha
\sigma_0^\alpha \sigma_1^\alpha\) into a general \(3\times3\) form that the
builder cannot express, so the rotation leaves the approved family. The same
argument applies to \(h_y\) on the detector side. Physically, the \(Y\) fields
remove the last antiunitary (time-reversal) symmetry of the model, which is
itself a mechanism hypothesis the campaign intends to test.

## Structural consequences, and what was verified

A single-site \(Y\) term is purely imaginary in the computational basis. This
makes it unlike every other term in the builder and has three consequences, each
of which is covered by `tests/test_single_pixel_y_fields.py`:

1. The dense accumulator must be complex. Both twins switch to `complex128` only
   when a \(Y\) self-field is active, so every pre-existing caller keeps its
   previous real dtype and bit-identical output.
2. Total \(S_z\) is no longer conserved, and \(Z\)-parity is broken. The QuSpin
   `diagonalize` and `diagonalize_sectors` symmetry predicates were updated to
   decline the magnetization and parity sectors whenever a \(Y\) field is
   present. A stale predicate would have returned a wrong spectrum silently
   rather than raising.
3. The two twins must continue to agree exactly. They do: the maximum entrywise
   difference over randomized chain and ring configurations with all twelve
   parameters active is \(0\).

Verified in addition: the added terms equal \(-h_{0y}Y_0 - h_y\sum_i Y_i\)
exactly against explicitly constructed Pauli operators; the resulting matrix is
Hermitian to machine zero; `hy0` inherits `hy` when unset; and with a \(Y\) field
active the `use_symmetry=True` path reproduces the dense spectrum to
\(6.7\times10^{-15}\).
