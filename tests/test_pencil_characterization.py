"""`SPEC.md` §3 distinct-root contract: finite, infinite, degenerate, singular.

Each case below has an answer known in closed form or by exact construction, so
these are correctness tests rather than regression snapshots.
"""

import numpy as np
import pytest
from scipy.linalg import expm, fractional_matrix_power

from core.hamiltonians.quspin_hamiltonians import SinglePixelHamiltonianQuSpin
from core.pencil_characterization import (
    ROOT_CONDITION_BOUND,
    STATUS_DEFECTIVE,
    STATUS_NOT_SEPARATED,
    STATUS_REGULAR,
    STATUS_SINGULAR,
    characterize_pencil_roots,
)
from core.projective_roots import split_qubit_first_blocks
from core.quantum_utils import generate_random_unitary


def _defective_unitary() -> np.ndarray:
    """Build a unitary whose outcome-0 pencil is ``D (lambda I - M)``.

    With ``M`` a single Jordan block, that pencil has one distinct root at
    ``lambda = 1`` of algebraic multiplicity two and kernel dimension one.  The
    completion is unitary because the rows of ``[C D]`` are orthonormal.
    """

    m = np.array([[1.0, 1.0], [0.0, 1.0]], dtype=np.complex128)
    d = fractional_matrix_power(np.eye(2) + m @ m.conj().T, -0.5)
    c = -d @ m
    lower = np.hstack([c, d])
    # Complete to a unitary by filling the top block with an orthonormal basis
    # of the kernel of the lower block rows.
    _, _, right_h = np.linalg.svd(lower)
    upper = right_h[2:]
    unitary = np.vstack([upper, lower])
    assert np.allclose(unitary.conj().T @ unitary, np.eye(4), atol=1e-14)
    return unitary


def test_generic_finite_roots_are_simple_and_complete() -> None:
    """The generic case of `SPEC.md` §3: every weight is one and they sum to n."""

    blocks = split_qubit_first_blocks(generate_random_unitary(8, seed=20260920))

    result = characterize_pencil_roots(blocks.A, blocks.C)

    assert result.status == STATUS_REGULAR
    assert result.measure_is_defined
    assert result.weights_are_complete
    assert result.distinct_root_count == result.dimension
    assert result.infinite_root_count == 0
    assert all(root.kernel_dimension == 1 for root in result.roots)
    assert all(root.algebraic_multiplicity == 1 for root in result.roots)
    assert result.maximum_kernel_residual < 1.0e-13


def test_infinite_sector_is_carried_by_the_homogeneous_formulation() -> None:
    """A rank-deficient ``U00`` puts weight at ``lambda = infinity``.

    `SPEC.md` §3 requires the infinite sector to be included.  Here it is the
    projective point ``(1, 0)``, whose kernel is exactly ``ker U00``, so its
    weight must equal the nullity of that block.
    """

    rng = np.random.default_rng(20260920)
    dimension, nullity = 6, 2
    u00 = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )
    u00[:, :nullity] = 0.0
    u10 = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
        size=(dimension, dimension)
    )

    result = characterize_pencil_roots(u00, u10)

    assert result.status == STATUS_REGULAR
    assert result.weights_are_complete
    assert result.infinite_root_count == 1
    infinite = next(r for r in result.roots if r.classification == "infinite")
    assert infinite.kernel_dimension == nullity
    assert np.linalg.matrix_rank(u00) == dimension - nullity
    assert infinite.theta == pytest.approx(np.pi, abs=1.0e-12)


def test_semisimple_degenerate_root_is_weighted_by_kernel_dimension() -> None:
    """A sixfold degenerate root must carry weight six, not six entries of one.

    This is the matched ring whose QZ spectrum returns six separate near-zero
    entries.  The contract reduces them to a single distinct root.
    """

    from core.hamiltonians.numpy_hamiltonians import SinglePixelHamiltonianNumpy

    hamiltonian = SinglePixelHamiltonianNumpy(
        N_pixel=4, J=1.0, Jpm=0.0, Jx=0.005, Jy=0.0, Jz=0.0, Jzx=0.0, Jcpm=0.0,
        hx=0.0, hz=0.1, hx0=0.0, hz0=0.1,
        connectivity="ring", central_coupling="all",
    ).generate()
    blocks = split_qubit_first_blocks(expm(-1.0j * hamiltonian * 37.0))

    result = characterize_pencil_roots(blocks.A, blocks.C)

    assert result.status == STATUS_REGULAR
    assert result.weights_are_complete
    assert result.distinct_root_count == 9
    assert result.defective_root_count == 0
    heaviest = max(result.roots, key=lambda root: root.kernel_dimension)
    assert heaviest.kernel_dimension == 6
    assert heaviest.algebraic_multiplicity == 6
    assert heaviest.theta < 1.0e-14
    # The rank boundary is cleanly separated; reported as evidence, not gated.
    assert heaviest.gap_ratio > 1.0e3
    assert result.maximum_kernel_residual < 1.0e-13


def test_defective_root_is_flagged_and_never_weighted_by_multiplicity() -> None:
    """Algebraic multiplicity two, kernel dimension one: the weight is one.

    Counting the two QZ entries would assign the wrong physical weight, which is
    the error `SPEC.md` §3 forbids.
    """

    blocks = split_qubit_first_blocks(_defective_unitary())

    result = characterize_pencil_roots(blocks.D, -blocks.C)

    assert result.distinct_root_count == 1
    root = result.roots[0]
    assert root.algebraic_multiplicity == 2
    assert root.kernel_dimension == 1
    assert root.defective
    assert result.status == STATUS_DEFECTIVE
    # A defective root breaks the completeness identity, and the record must
    # say so rather than padding the weights up to the dimension.
    assert not result.weights_are_complete
    assert result.total_kernel_dimension == 1
    assert result.dimension == 2
    # It must not be presented as a usable measure.
    assert not result.measure_is_defined


def test_singular_pencil_fails_closed_without_inventing_a_measure() -> None:
    """SWAP has a kernel at every projective point, so no finite measure exists."""

    swap = np.eye(4)[[0, 2, 1, 3]]
    blocks = split_qubit_first_blocks(swap)

    result = characterize_pencil_roots(blocks.D, -blocks.C)

    assert result.status == STATUS_SINGULAR
    assert not result.measure_is_defined
    assert result.roots == ()
    assert result.total_kernel_dimension == 0


@pytest.mark.parametrize("size", [2, 3, 4, 5])
def test_nilpotent_exchange_sector_never_reports_usable_roots(size) -> None:
    """The defect the backward residual cannot see must still be caught.

    On this pencil the solver returns angles wrong by up to ``6e-3`` while
    ``maximum_homogeneous_residual`` stays at ``1e-16``, so no residual gate can
    detect the failure.  The kernel-independence identity does: kernels at
    genuinely distinct roots of a regular pencil are linearly independent, and
    here they are not.  This test exercises the production solver, so it fails
    if the solver's behaviour on a defective pencil changes.
    """

    hamiltonian = SinglePixelHamiltonianQuSpin(
        N_pixel=size, J=0.0,
        Jx=0.7 / np.sqrt(size), Jy=0.7 / np.sqrt(size),
        hx=0.0, hz=0.0, hx0=0.0, hz0=0.0,
        central_coupling="all", use_symmetry=False,
    ).generate()
    unitary = expm(-1.0j * 0.61 * hamiltonian)
    dimension = 2**size
    u00 = unitary[:dimension, :dimension]
    u10 = unitary[dimension:, :dimension]

    result = characterize_pencil_roots(u00, u10)

    assert result.status in {STATUS_DEFECTIVE, STATUS_NOT_SEPARATED}
    assert not result.measure_is_defined
    assert not result.weights_are_complete or result.status == STATUS_NOT_SEPARATED
    # Exactly the pencil is nilpotent, so the true spectrum is {0} alone.
    powers = np.linalg.matrix_power(np.linalg.solve(u00, u10), dimension)
    assert np.linalg.norm(powers, 2) == 0.0


def test_kernel_bases_are_orthonormal_and_annihilate_the_pencil() -> None:
    """Every returned kernel basis must be usable as collapsible detector states."""

    blocks = split_qubit_first_blocks(generate_random_unitary(16, seed=20260921))

    result = characterize_pencil_roots(blocks.A, blocks.C)

    assert result.status == STATUS_REGULAR
    for root in result.roots:
        basis = root.kernel_basis
        assert basis.shape == (result.dimension, root.kernel_dimension)
        np.testing.assert_allclose(
            basis.conj().T @ basis, np.eye(root.kernel_dimension), atol=1.0e-13
        )
        pencil = root.beta * blocks.C - root.alpha * blocks.A
        assert np.linalg.norm(pencil @ basis, ord=2) < 1.0e-13


def _jordan_colligation(size: int) -> np.ndarray:
    """Unitary whose outcome-0 pencil is ``D (lambda I - J_size(1))``."""

    m = np.eye(size, dtype=np.complex128) + np.diag(np.ones(size - 1), 1)
    d = fractional_matrix_power(np.eye(size) + m @ m.conj().T, -0.5)
    lower = np.hstack([-d @ m, d])
    _, _, right_h = np.linalg.svd(lower)
    unitary = np.vstack([right_h[size:], lower])
    assert np.allclose(
        unitary.conj().T @ unitary, np.eye(2 * size), atol=1.0e-13
    )
    return unitary


@pytest.mark.parametrize("size", [2, 3, 4, 5, 6, 8])
def test_jordan_block_of_any_size_is_never_reported_regular(size) -> None:
    """A Jordan block has one root; reporting ``size`` simple roots is the worst failure.

    For ``size >= 3`` the QZ images scatter at order ``eps**(1/size)``, which at
    ``size = 8`` is about ``1e-2`` and therefore outside any cluster tolerance.
    Each scattered location then carries its own one-dimensional kernel and those
    kernels are linearly independent, so neither clustering nor the independence
    identity detects the split.  What detects it is that the independence is only
    marginal: the stacked kernel matrix is ill conditioned.
    """

    bare = characterize_pencil_roots(
        np.eye(size, dtype=np.complex128), np.diag(np.ones(size - 1), 1).astype(complex)
    )
    assert bare.status != STATUS_REGULAR
    assert not bare.measure_is_defined

    blocks = split_qubit_first_blocks(_jordan_colligation(size))
    for mapping in ((blocks.D, -blocks.C), (blocks.B, -blocks.A)):
        result = characterize_pencil_roots(*mapping)
        assert result.status != STATUS_REGULAR, f"size={size} mapping reported regular"
        assert not result.measure_is_defined


def test_jordan_mixed_with_generic_simple_roots_is_still_caught() -> None:
    """The defective block must not be laundered by well-behaved neighbours."""

    for size in (3, 4, 5):
        dimension = size + 3
        matrix = np.zeros((dimension, dimension), dtype=np.complex128)
        matrix[:size, :size] = np.diag(np.ones(size - 1), 1)
        for offset, value in enumerate((2.0, 3.5, -1.25)):
            matrix[size + offset, size + offset] = value
        result = characterize_pencil_roots(np.eye(dimension, dtype=np.complex128), matrix)
        assert result.status != STATUS_REGULAR


def test_regular_pencil_with_cardinal_roots_is_not_called_singular() -> None:
    """Roots at every cardinal Bloch point must not be mistaken for a singular pencil.

    Sampling regularity at the fixed points ``lambda in {0, inf, 1, -1, i}`` fails
    exactly here, and this is not a remote coincidence: `SPEC.md` §12
    preferred-basis physics is about roots concentrating on cardinal directions.
    The determinant is ``-alpha beta (beta - alpha)(-beta - alpha)(i beta - alpha)``,
    which is not identically zero, so the pencil is regular with five simple roots.
    """

    u10 = np.diag([0.0, 1.0, 1.0, -1.0, 1.0j]).astype(np.complex128)
    u00 = np.diag([1.0, 0.0, 1.0, 1.0, 1.0]).astype(np.complex128)

    result = characterize_pencil_roots(u00, u10)

    assert result.status == STATUS_REGULAR
    assert result.distinct_root_count == 5
    assert result.total_kernel_dimension == 5
    assert all(root.kernel_dimension == 1 for root in result.roots)
    assert result.infinite_root_count == 1


@pytest.mark.parametrize("dimension", [2, 3, 4, 8])
@pytest.mark.parametrize("angle", [0.3, 1.0, np.pi / 4])
def test_uncoupled_detector_gives_one_root_of_full_weight(dimension, angle) -> None:
    """`SPEC.md` §15.1 matched noninteracting control: ``R_y(theta) tensor I``.

    Its outcome-0 pencil has the single root ``lambda = -tan(theta/2)`` with
    weight equal to the whole detector dimension.  A rank tolerance scaled by the
    evaluated matrix rather than by the pencil shrinks with that matrix and can
    never detect the kernel, which would disable the control entirely.
    """

    cosine, sine = np.cos(angle / 2), np.sin(angle / 2)
    identity = np.eye(dimension, dtype=np.complex128)

    result = characterize_pencil_roots(cosine * identity, -sine * identity)

    assert result.status == STATUS_REGULAR
    assert result.distinct_root_count == 1
    assert result.roots[0].kernel_dimension == dimension
    assert result.weights_are_complete
    assert result.roots[0].alpha / result.roots[0].beta == pytest.approx(
        -np.tan(angle / 2), abs=1.0e-12
    )


def test_uncoupled_spectator_doubles_every_weight() -> None:
    """Contract fixture F6: weights scale with an uncoupled spectator.

    Tensoring the detector with an inert two-level spectator must leave the root
    set alone and double every kernel dimension.  This is the fixture that pins
    basis independence and multiplicity scaling together.
    """

    blocks = split_qubit_first_blocks(generate_random_unitary(8, seed=20260923))
    base = characterize_pencil_roots(blocks.A, blocks.C)
    spectator = np.eye(2, dtype=np.complex128)
    composed = characterize_pencil_roots(
        np.kron(blocks.A, spectator), np.kron(blocks.C, spectator)
    )

    assert base.status == STATUS_REGULAR
    assert composed.status == STATUS_REGULAR
    assert composed.dimension == 2 * base.dimension
    assert composed.distinct_root_count == base.distinct_root_count
    assert composed.total_kernel_dimension == 2 * base.total_kernel_dimension
    base_thetas = sorted(root.theta for root in base.roots)
    composed_thetas = sorted(root.theta for root in composed.roots)
    np.testing.assert_allclose(composed_thetas, base_thetas, atol=1.0e-12)
    assert all(root.kernel_dimension == 2 for root in composed.roots)


def test_cluster_representative_beats_every_member_it_replaces() -> None:
    """Negative control for the phase-aligned mean of `METHOD.md` §4 step 3.

    Replacing the mean by the first cluster member must be detectably worse, or
    the step is unpinned.  A defective root of multiplicity ``m`` scatters as the
    ``m``-th roots of unity about the true location, which sum to zero, so the
    mean is better by orders of magnitude rather than by a constant factor.
    """

    from core.pencil_characterization import _cluster_representative
    from core.relative_evolution_pencil import projective_chordal_distance

    size = 3
    spectrum_alpha, spectrum_beta = [], []
    scatter = np.finfo(float).eps ** (1.0 / size)
    for index in range(size):
        offset = scatter * np.exp(2j * np.pi * index / size)
        spectrum_alpha.append(1.0 + offset)
        spectrum_beta.append(1.0 + 0.0j)
    alpha = np.array(spectrum_alpha)
    beta = np.array(spectrum_beta)

    mean_alpha, mean_beta, spread = _cluster_representative(
        alpha, beta, list(range(size))
    )
    truth = (1.0 + 0.0j, 1.0 + 0.0j)
    mean_error = projective_chordal_distance(mean_alpha, mean_beta, *truth)
    member_errors = [
        projective_chordal_distance(alpha[i], beta[i], *truth) for i in range(size)
    ]

    assert spread > 0.0
    assert mean_error < min(member_errors) / 1.0e3


def test_rank_tolerance_is_load_bearing() -> None:
    """Negative control for the rank tolerance.

    Three distinct simple roots sit at ``lambda = 0``, ``2e-7`` and ``1``, the
    first two separated by more than the cluster tolerance so they are genuinely
    distinct.  Evaluated at the first root the pencil has singular values
    ``{0, 2e-7, 1}``.  A tolerance loose enough to swallow ``2e-7`` assigns that
    root weight two instead of one, so a correct verdict here pins the tolerance
    from the loose side, while the uncoupled-detector control above pins it from
    the tight side.
    """

    dimension = 3
    u00 = np.eye(dimension, dtype=np.complex128)
    u10 = np.diag([0.0, 2.0e-7, 1.0]).astype(np.complex128)

    result = characterize_pencil_roots(u00, u10)

    assert result.status == STATUS_REGULAR
    assert result.distinct_root_count == 3
    assert result.total_kernel_dimension == dimension
    assert all(root.kernel_dimension == 1 for root in result.roots)


INTEGER_WITNESSES = (
    # det = -14 (alpha - beta)^2, kernel dimension one at the double root.
    (
        np.array([[-22.0, 28.0], [-49.0, 63.0]]),
        np.array([[-30.0, 28.0], [-67.0, 63.0]]),
    ),
    # L J_2(1) R under integer L, R.
    (
        np.array([[3.0, 2.0], [9.0, 5.0]]) @ np.array([[9.0, 7.0], [6.0, -3.0]]),
        np.array([[3.0, 2.0], [9.0, 5.0]])
        @ np.array([[1.0, 1.0], [0.0, 1.0]])
        @ np.array([[9.0, 7.0], [6.0, -3.0]]),
    ),
)


@pytest.mark.parametrize("u00, u10", INTEGER_WITNESSES)
def test_defectiveness_survives_a_change_of_basis(u00, u10) -> None:
    """Defectiveness is similarity invariant; a guard on the basis is not.

    These pencils have exactly representable small-integer entries, so there is
    no representation error, and an exact determinant with a repeated factor.
    Both were reported ``regular`` with two spurious simple roots while the
    guard was the conditioning of the stacked kernel basis, which a change of
    basis moves freely.  Certifying on the *root* condition number instead is
    invariant in the way that matters.
    """

    result = characterize_pencil_roots(
        u00.astype(np.complex128), u10.astype(np.complex128)
    )

    assert result.status != STATUS_REGULAR
    assert not result.measure_is_defined
    assert result.maximum_root_condition_number > ROOT_CONDITION_BOUND


def test_certification_margin_is_wide_on_both_populations() -> None:
    """The bound must sit far from both populations, not merely between them.

    A derived constant earns trust from its margin.  Asserting only that some
    huge and some tiny value fall on the right sides would pass for a constant
    fitted to the fixtures, so this pins the separation itself.
    """

    accepted, refused = [], []
    for seed in (20260920, 20260921):
        blocks = split_qubit_first_blocks(generate_random_unitary(8, seed=seed))
        accepted.append(characterize_pencil_roots(blocks.A, blocks.C))
    accepted.append(
        characterize_pencil_roots(
            np.diag([1.0, 0.0, 1.0, 1.0, 1.0]).astype(np.complex128),
            np.diag([0.0, 1.0, 1.0, -1.0, 1.0j]).astype(np.complex128),
        )
    )
    for size in (3, 5, 8):
        refused.append(
            characterize_pencil_roots(
                np.eye(size, dtype=np.complex128),
                np.diag(np.ones(size - 1), 1).astype(np.complex128),
            )
        )
    for u00, u10 in INTEGER_WITNESSES:
        refused.append(
            characterize_pencil_roots(
                u00.astype(np.complex128), u10.astype(np.complex128)
            )
        )

    worst_accepted = max(r.maximum_root_condition_number for r in accepted)
    best_refused = min(r.maximum_root_condition_number for r in refused)
    assert all(r.status == STATUS_REGULAR for r in accepted)
    assert all(r.status != STATUS_REGULAR for r in refused)
    # Five orders of clearance below, and a genuine factor above.  The upper
    # margin is the tighter of the two and is stated rather than rounded up.
    assert worst_accepted < ROOT_CONDITION_BOUND / 1.0e5
    assert best_refused > ROOT_CONDITION_BOUND * 5.0


def test_randomized_defective_pencils_are_never_certified() -> None:
    """A certificate over a population, not a fixture list.

    Jordan structures hidden behind random two-sided equivalences are the case a
    fixture list cannot cover, because the defect is reachable from any listed
    example by a change of basis.
    """

    rng = np.random.default_rng(20260927)

    def graded(size, condition):
        left, _ = np.linalg.qr(
            rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size))
        )
        right, _ = np.linalg.qr(
            rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size))
        )
        return left @ np.diag(np.logspace(0, np.log10(condition), size)) @ right

    certified = 0
    draws = 0
    for _ in range(300):
        size = int(rng.integers(2, 7))
        blocks, remaining = [], size
        while remaining > 0:
            block = int(rng.integers(1, min(remaining, 4) + 1))
            blocks.append(block)
            remaining -= block
        if max(blocks) < 2:
            continue
        matrix = np.zeros((size, size), dtype=np.complex128)
        offset = 0
        for block in blocks:
            value = complex(rng.normal(), rng.normal())
            matrix[offset : offset + block, offset : offset + block] = value * np.eye(
                block
            ) + np.diag(np.ones(block - 1), 1)
            offset += block
        condition = 10 ** rng.uniform(0, 5)
        left, right = graded(size, condition), graded(size, condition)
        draws += 1
        result = characterize_pencil_roots(left @ right, left @ matrix @ right)
        if result.status == STATUS_REGULAR:
            certified += 1

    assert draws > 200
    assert certified == 0


def test_regularity_sampling_survives_a_root_on_a_sample_point() -> None:
    """A regular pencil must not be refused because a root sits on a sample.

    The sample points are deterministic, so a root can be placed exactly on the
    first one.  Deciding a global algebraic property from a fixed finite sample
    needs at least ``n + 1`` points, since the determinant is homogeneous of
    degree ``n``; a count independent of ``n`` has no guarantee at all.
    """

    from core.pencil_characterization import _pencil_is_singular

    rng = np.random.default_rng(20260920)
    alpha = complex(*rng.normal(size=2))
    beta = complex(*rng.normal(size=2))
    first_sample = alpha / beta

    u00 = np.eye(4, dtype=np.complex128)
    u10 = np.diag([first_sample, 2.0, -3.0, 0.5]).astype(np.complex128)

    assert _pencil_is_singular(u00, u10, samples=1)[0]
    assert not _pencil_is_singular(u00, u10)[0]

    result = characterize_pencil_roots(u00, u10)
    assert result.status == STATUS_REGULAR
    assert result.distinct_root_count == 4
    assert result.total_kernel_dimension == 4
