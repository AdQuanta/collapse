"""Distinct-root characterization of a homogeneous detector pencil.

`SPEC.md` §3 defines the physical content of an outcome pencil as a set of
*distinct* projective roots, each carrying the weight

    k_j = dim ker M(alpha_j, beta_j),

and it requires degenerate and singular pencils to be handled correctly rather
than discarded.  A QZ spectrum does not supply that object.  QZ returns one
entry per algebraic multiplicity with one arbitrary eigenvector each, which
over-counts a defective root and picks an arbitrary member of a degenerate
kernel.  This module performs the reduction the specification asks for:

1. cluster projectively coincident QZ roots;
2. place each cluster at its phase-aligned mean, which is the accurate
   estimator for a defective cluster because the computed roots of a Jordan
   block of size ``m`` scatter around the true location;
3. take one SVD per *distinct* root and read the kernel dimension and an
   orthonormal kernel basis from it;
4. retain the QZ cluster size only as a diagnostic, never as a weight.

The module fails closed.  A singular pencil has a nonzero kernel at every
projective point, so its collapsible set is a continuum and the finite weighted
sum of `SPEC.md` §3 does not define a measure on it; such a pencil is reported
as ``singular_measure_undefined`` and yields no roots.  A root whose numerical
rank is not separated by a clear singular-value gap is reported as
``rank_gap_unresolved``.  A root whose kernel dimension falls below its
algebraic multiplicity is *defective*: its location carries the ``eps**(1/m)``
sensitivity of a Jordan block and is not determined in double precision, so it
is flagged rather than reported as an ordinary root.  That flag is the only
diagnostic that detects the failure, because a defective root has a small
backward residual and a large forward error at the same time.

Cost is one SVD per distinct root.  This is a certification tool for the
matrix-pencil contract, not the production histogram path.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.relative_evolution_pencil import (
    generalized_relative_evolution_spectrum,
    projective_chordal_distance,
)

# Frozen contract constants.  They are fixed in advance and are not adjusted in
# response to any observed result; a case that violates them is reported as a
# fail-closed status, which is the specified outcome rather than a defect.
CLUSTER_TOLERANCE = 1.0e-7
# The certifiable question is not "is this pencil defective" but "are its roots
# determined at all".  The root condition number ``1/|y* A v|`` answers that and
# is the right invariant: a defective root has an infinite one, and a regular
# pencil whose roots are ill determined is equally uncertifiable.  An earlier
# version gated on the conditioning of the stacked kernel matrix instead, which
# is *not* similarity invariant while defectiveness is, so a change of basis
# defeated it: the exactly defective integer pencil
# ``([[-22,28],[-49,63]], [[-30,28],[-67,63]])`` with determinant
# ``-14(alpha-beta)^2`` and kernel dimension one was reported ``regular`` with
# two spurious simple roots at cond(K) = 2.75e6.
#
# A root whose condition number is ``kappa`` is located to about ``kappa*eps``,
# so requiring it to be determined to better than ``sqrt(eps)`` gives the bound
# ``1/sqrt(eps)``.  This is derived, not fitted.
ROOT_CONDITION_BOUND = 1.0 / np.sqrt(np.finfo(float).eps)
# det(beta C - alpha A) is homogeneous of degree n, so it vanishes identically
# only if it vanishes at n+1 distinct projective points.  A fixed sample count
# independent of n therefore has no exact-arithmetic guarantee; the count is
# derived from n instead, with a floor for very small pencils.
SINGULARITY_SAMPLE_FLOOR = 8

STATUS_REGULAR = "regular"
STATUS_DEFECTIVE = "defective_roots_present"
STATUS_RANK_GAP = "rank_gap_unresolved"
STATUS_NOT_SEPARATED = "roots_not_separated"
STATUS_SINGULAR = "singular_measure_undefined"


@dataclass(frozen=True)
class DistinctProjectiveRoot:
    """One distinct projective root with its kernel-dimension weight.

    ``algebraic_multiplicity`` is the size of the QZ cluster and is a
    diagnostic only.  ``kernel_dimension`` is the `SPEC.md` §3 weight.  They
    differ exactly when the root is defective.
    """

    alpha: complex
    beta: complex
    theta: float
    classification: str
    algebraic_multiplicity: int
    kernel_dimension: int
    kernel_basis: np.ndarray
    smallest_singular_value: float
    boundary_singular_value: float
    # Reported as evidence for the rank decision.  It is deliberately *not* an
    # acceptance gate: no case could be constructed in which such a gate changed
    # a verdict, so it was removed rather than frozen as an unjustified constant.
    gap_ratio: float
    kernel_residual: float
    cluster_spread: float
    defective: bool


@dataclass(frozen=True)
class PencilCharacterization:
    """The `SPEC.md` §3 outcome record for one homogeneous pencil."""

    status: str
    dimension: int
    roots: tuple[DistinctProjectiveRoot, ...]
    total_kernel_dimension: int
    distinct_root_count: int
    defective_root_count: int
    finite_root_count: int
    infinite_root_count: int
    rank_tolerance: float
    cluster_tolerance: float
    maximum_kernel_residual: float
    regularity_status: str
    kernel_independence_rank: int
    kernel_condition_number: float
    maximum_root_condition_number: float

    @property
    def measure_is_defined(self) -> bool:
        """True only when every root carries a trustworthy kernel weight."""

        return self.status == STATUS_REGULAR

    @property
    def weights_are_complete(self) -> bool:
        """True when the kernel weights account for the whole detector space.

        This fails precisely when some root is defective, because a Jordan
        block contributes fewer kernel directions than its algebraic
        multiplicity.
        """

        return self.total_kernel_dimension == self.dimension


def _group_coincident_roots(
    alpha: np.ndarray,
    beta: np.ndarray,
    tolerance: float,
) -> list[list[int]]:
    """Return every chordal-distance group, singletons included."""

    groups: list[list[int]] = []
    for index in range(alpha.size):
        if np.hypot(abs(alpha[index]), abs(beta[index])) == 0.0:
            continue
        for group in groups:
            member = group[0]
            distance = projective_chordal_distance(
                alpha[index], beta[index], alpha[member], beta[member]
            )
            if distance <= tolerance:
                group.append(index)
                break
        else:
            groups.append([index])
    return groups


def _cluster_representative(
    alpha: np.ndarray,
    beta: np.ndarray,
    group: list[int],
) -> tuple[complex, complex, float]:
    """Return the phase-aligned mean of a cluster and its internal spread.

    A defective root of multiplicity ``m`` is returned by QZ as ``m`` values
    scattered around the true location, so the mean is a far better estimator
    than any single member.  For a semisimple cluster the members already agree
    and the mean changes nothing.
    """

    pairs = []
    for index in group:
        scale = float(np.hypot(abs(alpha[index]), abs(beta[index])))
        pairs.append(np.array([alpha[index] / scale, beta[index] / scale]))
    reference = pairs[0]
    aligned = []
    for pair in pairs:
        overlap = np.vdot(reference, pair)
        phase = overlap / abs(overlap) if abs(overlap) > 0.0 else 1.0 + 0.0j
        aligned.append(pair * np.conj(phase))
    mean = np.mean(aligned, axis=0)
    norm = float(np.linalg.norm(mean))
    if norm == 0.0:
        mean, norm = reference, 1.0
    mean = mean / norm
    spread = max(
        (
            projective_chordal_distance(
                alpha[left], beta[left], alpha[right], beta[right]
            )
            for left in group
            for right in group
            if left < right
        ),
        default=0.0,
    )
    return complex(mean[0]), complex(mean[1]), float(spread)


def _pencil_is_singular(
    a: np.ndarray,
    c: np.ndarray,
    samples: int | None = None,
) -> tuple[bool, int]:
    """Decide singularity by sampling *generic* projective points.

    A pencil is singular exactly when ``det(beta C - alpha A)`` vanishes
    identically, so a single full-rank sample certifies regularity.  The
    samples must be generic: `audit_linear_pencil_regularity` samples the
    cardinal points ``lambda in {0, inf, 1, -1, i}``, and a regular pencil whose
    roots sit at those five points is then misread as singular.  That is not a
    remote coincidence in this project, because `SPEC.md` §12 preferred-basis
    physics is precisely about roots concentrating on cardinal Bloch
    directions.  Drawing from a fixed seed keeps the decision deterministic
    while making a collision with the root set a measure-zero accident.
    """

    n = a.shape[0]
    if samples is None:
        samples = max(SINGULARITY_SAMPLE_FLOOR, n + 1)
    eps = np.finfo(float).eps
    scale = max(
        float(np.linalg.norm(a, ord=2)), float(np.linalg.norm(c, ord=2)), 1.0
    )
    tolerance = n * eps * scale
    rng = np.random.default_rng(20260920)
    best = 0
    for _ in range(samples):
        alpha = complex(*rng.normal(size=2))
        beta = complex(*rng.normal(size=2))
        norm = np.hypot(abs(alpha), abs(beta))
        rank = int(
            np.linalg.matrix_rank(
                (beta / norm) * c - (alpha / norm) * a, tol=tolerance
            )
        )
        best = max(best, rank)
        if best == n:
            return False, best
    return True, best


def _kernel_dimension_by_gap(
    singular_values: np.ndarray,
    formation_scale: float,
) -> int:
    """Return the kernel dimension at a *computed* root.

    A machine-epsilon threshold is the wrong criterion here.  The root is
    located only to about ``kappa * eps``, so the kernel singular values sit not
    at zero but at the level that root error induces, and a threshold placed at
    ``n * eps`` decides by a factor of two.  On the approved ring and chain
    families at ``t = 211`` and ``t = 500`` it assigned kernel dimension zero to
    genuine twofold roots whose smallest singular values were ``4.6e-15``
    against a tolerance of ``2.3e-15``, while the gap separating them from the
    rest of the spectrum was thirteen orders wide: 145 of 512 physically
    approved configurations refused over a factor of two.

    The scale that matters is ``sqrt(eps) * formation_scale``.  A root ceases to
    be determined once its condition number reaches ``1/sqrt(eps)``, which is
    exactly where the root-condition bound refuses it, so a singular value below
    that scale cannot be distinguished from zero by anything this method knows.
    Everything below it is kernel; everything above it is not.  In practice the
    two populations are separated by ten orders or more, so the boundary is not
    a close call: the widest measured kernel singular value on the approved
    families is ``6e-15`` and the narrowest retained one is ``1e-1``.
    """

    values = np.asarray(singular_values, dtype=float)
    ceiling = np.sqrt(np.finfo(float).eps) * max(formation_scale, float(values[0]))
    return int(np.count_nonzero(values <= ceiling))


def characterize_pencil_roots(
    u00: np.ndarray,
    u10: np.ndarray,
    *,
    cluster_tolerance: float = CLUSTER_TOLERANCE,
) -> PencilCharacterization:
    """Return the `SPEC.md` §3 distinct-root record for ``beta U10 - alpha U00``.

    The finite sector, the ``lambda = infinity`` sector, degenerate roots and
    singular pencils are all handled by the same homogeneous formulation: the
    infinite root is the point ``(alpha, beta) = (1, 0)``, whose kernel is
    ``ker U00``, and it needs no special case.
    """

    spectrum = generalized_relative_evolution_spectrum(
        u00, u10, assess_regularity=True
    )
    a = np.asarray(u00, dtype=np.complex128)
    c = np.asarray(u10, dtype=np.complex128)
    n = a.shape[0]
    eps = np.finfo(float).eps
    regularity = spectrum.regularity_audit
    assert regularity is not None  # assess_regularity=True was requested

    singular_pencil, sampled_rank = _pencil_is_singular(a, c)
    if singular_pencil:
        return PencilCharacterization(
            status=STATUS_SINGULAR,
            dimension=n,
            roots=(),
            total_kernel_dimension=0,
            distinct_root_count=0,
            defective_root_count=0,
            finite_root_count=0,
            infinite_root_count=0,
            rank_tolerance=float(spectrum.rank_tolerance),
            cluster_tolerance=float(cluster_tolerance),
            maximum_kernel_residual=np.nan,
            regularity_status=f"singular_at_{sampled_rank}_of_{n}_generic_samples",
            kernel_independence_rank=0,
            kernel_condition_number=np.nan,
            maximum_root_condition_number=np.nan,
        )

    # Roundoff in the *formed* matrix ``beta C - alpha A`` is governed by the
    # terms that were combined, not by the norm of the result, which can lose
    # every leading digit to cancellation.  Scaling the rank tolerance by
    # ``sigma_max`` of the difference therefore refuses legitimate roots at
    # large ``|lambda|``; the formation scale is the correct backward-error
    # reference.
    norm_a = float(np.linalg.norm(a, ord=2))
    norm_c = float(np.linalg.norm(c, ord=2))

    groups = _group_coincident_roots(spectrum.alpha, spectrum.beta, cluster_tolerance)
    # A merge that does not produce a root was not a merge.  Near-degenerate but
    # genuinely distinct roots occur physically -- weak, localized coupling at
    # short evolution time puts ring/first roots within 1e-8 of one another --
    # and grouping them places the representative between two roots rather than
    # on one, where the pencil is not singular at all.  Splitting such a group
    # back into singletons is the local repair; it recovered 32 of the 34
    # approved configurations that remained refused after the kernel-scale fix.
    repaired: list[list[int]] = []
    for group in groups:
        if len(group) > 1:
            trial_alpha, trial_beta, _ = _cluster_representative(
                spectrum.alpha, spectrum.beta, group
            )
            trial = trial_beta * c - trial_alpha * a
            trial_values = np.linalg.svd(trial, compute_uv=False)
            trial_scale = abs(trial_beta) * norm_c + abs(trial_alpha) * norm_a
            if _kernel_dimension_by_gap(trial_values, trial_scale) == 0:
                repaired.extend([member] for member in group)
                continue
        repaired.append(group)
    groups = repaired
    roots: list[DistinctProjectiveRoot] = []
    rank_gap_unresolved = False
    worst_kernel_residual = 0.0
    rank_tolerance = 0.0

    for group in groups:
        alpha, beta, spread = _cluster_representative(
            spectrum.alpha, spectrum.beta, group
        )
        matrix = beta * c - alpha * a
        left, singular_values, right_h = np.linalg.svd(matrix)
        formation_scale = abs(beta) * norm_c + abs(alpha) * norm_a
        tolerance = n * eps * formation_scale
        rank_tolerance = max(rank_tolerance, tolerance)
        kernel_dimension = _kernel_dimension_by_gap(singular_values, formation_scale)
        rank = n - kernel_dimension
        if kernel_dimension == 0:
            # The cluster mean is not a root of the pencil at all.  That is a
            # rank statement, not a weight, so it fails closed with the others.
            rank_gap_unresolved = True
            kernel_dimension = 0
            boundary = float(singular_values[-1])
            gap_ratio = np.inf
        else:
            boundary = float(singular_values[rank - 1]) if rank else np.inf
            largest_discarded = float(singular_values[n - kernel_dimension])
            gap_ratio = (
                boundary / largest_discarded if largest_discarded > 0.0 else np.inf
            )

        basis = right_h[rank:].conj().T if kernel_dimension else np.zeros((n, 0), complex)
        residual = (
            float(np.linalg.norm(matrix @ basis, ord=2)) if kernel_dimension else 0.0
        )
        worst_kernel_residual = max(worst_kernel_residual, residual)
        pair_scale = max(abs(alpha), abs(beta))
        infinite = abs(beta) <= spectrum.projective_tolerance * pair_scale
        roots.append(
            DistinctProjectiveRoot(
                alpha=alpha,
                beta=beta,
                theta=float(2.0 * np.arctan2(abs(alpha), abs(beta))),
                classification="infinite" if infinite else "finite",
                algebraic_multiplicity=len(group),
                kernel_dimension=kernel_dimension,
                kernel_basis=basis,
                smallest_singular_value=float(singular_values[-1]),
                boundary_singular_value=boundary,
                gap_ratio=float(gap_ratio),
                kernel_residual=residual,
                cluster_spread=spread,
                # A cluster whose mean is not a root at all has weight zero and
                # is a refusal, not a defective root; only a genuine deficiency
                # between a nonzero kernel and the cluster size is defectiveness.
                defective=0 < kernel_dimension < len(group),
            )
        )

    # Kernels at genuinely distinct roots of a regular pencil are linearly
    # independent, so their union must have rank equal to the sum of the
    # kernel dimensions.  A deficiency proves the reported roots are not
    # distinct: they are one root that the solver scattered beyond the cluster
    # tolerance, which is what a defective root does.  This is a theorem, not a
    # tuned gate, and it is the test that catches a scattered Jordan block
    # whose individual backward residuals all look clean.
    stacked = (
        np.hstack([root.kernel_basis for root in roots if root.kernel_dimension])
        if any(root.kernel_dimension for root in roots)
        else np.zeros((n, 0), dtype=np.complex128)
    )
    total_kernel = sum(root.kernel_dimension for root in roots)
    if stacked.shape[1]:
        stacked_values = np.linalg.svd(stacked, compute_uv=False)
        independence_rank = int(
            np.count_nonzero(
                stacked_values > max(stacked.shape) * eps * float(stacked_values[0])
            )
        )
        smallest = float(stacked_values[-1])
        kernel_condition = (
            float(stacked_values[0]) / smallest if smallest > 0.0 else np.inf
        )
    else:
        independence_rank = 0
        kernel_condition = np.nan

    defective_count = sum(1 for root in roots if root.defective)
    # One test, not three.  A rank deficiency in the stacked kernel matrix and
    # a column count above ``n`` both drive its smallest singular value to zero
    # and therefore its condition number to infinity, so the conditioning bound
    # strictly subsumes both; ``kernel_independence_rank`` is kept as reported
    # evidence rather than as a second, redundant gate.
    # The certification criterion: every root must be determined to better than
    # sqrt(eps).  Defective roots fail automatically, because their condition
    # number diverges; so do regular pencils whose roots are genuinely not
    # resolvable, which must also not be certified.
    local = spectrum.local_coordinate_condition_numbers
    finite_local = local[np.isfinite(local)]
    root_condition = float(np.max(finite_local)) if finite_local.size else np.inf
    # Both are refusals; prefer the more specific label.  When the structure was
    # positively identified -- a cluster whose kernel dimension falls below its
    # size -- say `defective`.  Reserve `roots_not_separated` for the case where
    # the roots are not determined well enough to identify any structure.
    # Kernels at distinct roots of a regular pencil are independent, so the
    # weights can never exceed the dimension.  An excess proves the reported
    # roots are not distinct -- two near-degenerate roots each claiming the
    # other's kernel direction -- and is a theorem violation, not a judgement
    # call, so it refuses ahead of everything else.
    if total_kernel > n:
        status = STATUS_NOT_SEPARATED
    elif defective_count:
        status = STATUS_DEFECTIVE
    elif not (root_condition <= ROOT_CONDITION_BOUND):
        status = STATUS_NOT_SEPARATED
    elif rank_gap_unresolved:
        status = STATUS_RANK_GAP
    else:
        status = STATUS_REGULAR

    return PencilCharacterization(
        status=status,
        dimension=n,
        roots=tuple(roots),
        total_kernel_dimension=total_kernel,
        distinct_root_count=len(roots),
        defective_root_count=defective_count,
        finite_root_count=sum(1 for r in roots if r.classification == "finite"),
        infinite_root_count=sum(1 for r in roots if r.classification == "infinite"),
        rank_tolerance=float(rank_tolerance),
        cluster_tolerance=float(cluster_tolerance),
        maximum_kernel_residual=worst_kernel_residual,
        regularity_status=f"regular_full_rank_{sampled_rank}_of_{n}",
        kernel_independence_rank=independence_rank,
        kernel_condition_number=float(kernel_condition),
        maximum_root_condition_number=root_condition,
    )
