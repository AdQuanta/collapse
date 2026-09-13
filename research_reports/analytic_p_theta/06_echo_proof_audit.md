# Audit of the interacting central-X ring result

2026-09-13. Result: **PROVED in the stated central-X ring scope** after the
following analytical checks. The complete goal remains OPEN.

| Possible failure | Resolution in report 05 |
|---|---|
| Small normalized commutators do not control nonnormal roots | Exact W is unitary; the Cayley pencil reduction precedes every limit. Trace powers determine its spectral/root law. |
| A first-Magnus approximation may fail for large extensive norm | The error uses a unitary-invariant tracial 2-norm and a two-time commutator bound. No exponential of ||F_N|| is used. |
| Locality estimates in operator norm cost sqrt(N) after summation | Centered shell sums use product-trace orthogonality and a polynomial overlap count before summing exponentially decaying shells. |
| The finite-ring boundary could spoil the infinite-chain CLT | Uniform periodic locality and centered fixed-radius comparison control the boundary; local blocks are taken only after fixing radius. |
| Noncommuting local summands invalidate a classical CLT | Drop block boundary terms in 2-norm; retained different block sums commute and their trace distributions factor. Within-block noncommutativity is retained. |
| The detector spectral measure is an arbitrary spectral sum | A local finite-support Pauli recurrence specifies all moments; factorial growth gives Carleman determinacy. |
| Small finite rings might identify the infinite recurrence incorrectly | Full NNN certificates at N=5 and 6 have different fourth moments. They are kept distinct. Infinite coefficients are computed on unrestricted integer sites, not inferred from either ring. |
| Low frequencies make a phase-average integral divergent | The finite-time kernel is bounded by t², retains nu{0}, and the Cesàro limit is computed using compound-Poisson cutoffs and a probability weak limit. |
| Time and thermodynamic limits are interchanged | Fixed-time locality/CLT is completed first; the later average acts on its exact limiting characteristic functions. |
| Atomic measures are silently smoothed | Exceptional-time atoms are retained. The averaged measure is specified by exact moments; Poisson smoothing is only an inversion device, removed before the RN ratio. |
| The theorem silently covers endpoint or multichannel dynamics | Both are explicitly excluded. The endpoint lacks collective scaling; multiple central axes can have the known nonnormal root pathology. |

The conserved-energy corollary is also exact: Pauli orthogonality gives
tau(F_N D_N/sqrt(N))=hx and energy variance
|h|²+|J1|²+|J2|² for N>=5. Projection onto conserved operators and the
closed-set inequality for the limiting spectral measures preserve a
zero-frequency mass at least hx²/variance. Therefore nonzero hx enforces
the uniform late-time polar law throughout this central-X ring subfamily.

No symbolic check can independently certify the whole locality proof. The
frozen v3 checks test the exact algebra by a distinct dense-matrix method;
the analytical argument and its assumptions are exposed above for review.
