"""Constructive finite Born-like families using native X/XX operators.

For H = K - hx0 Xq - hz0 Zq - Xq sum_i g_i Xi, with [K, Xi]=0,
the detector factor cancels from the projected pencil. Each detector X
configuration leaves a two-dimensional qubit block. All roots have equal
algebraic weight; no state preparation measure is introduced.
"""

from __future__ import annotations

from fractions import Fraction
import math

import numpy as np

from core.born import born_ratio_from_theta
from core.born_reciprocity import born_moment_residuals, cosine_moments
from core.exact_born_limits import histogram_born_errors


def signed_sums(values: np.ndarray) -> np.ndarray:
    """Enumerate the spectrum of a sum of commuting Pauli X operators."""
    values = np.asarray(values)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("values must be a finite vector")
    sums = np.zeros(1, dtype=values.dtype)
    for value in values:
        sums = np.concatenate((sums + value, sums - value))
    return sums


def conditional_qubit_angles(
    phase_steps: np.ndarray, *, transverse_phase: float = 0.,
    longitudinal_phase: float = 0.,
) -> np.ndarray:
    """Exact polar roots with phase_steps=2t*g and qubit phases=2t*h.

    Use atan2 of homogeneous block magnitudes, including zero and infinite
    roots. The finite conditional unitary has no indeterminate root.
    """
    if not np.isfinite([transverse_phase, longitudinal_phase]).all():
        raise ValueError("qubit phases must be finite")
    transverse = (signed_sums(phase_steps) + transverse_phase) / 2
    longitudinal = longitudinal_phase / 2
    omega = np.hypot(transverse, longitudinal)
    sin_over_omega = np.sinc(omega / np.pi)
    alpha = np.abs(transverse * sin_over_omega)
    beta = np.hypot(np.cos(omega), longitudinal * sin_over_omega)
    return 2 * np.arctan2(alpha, beta)


def polar_gate_metrics(
    theta: np.ndarray, *, bins: int = 64, moment_order: int = 16,
) -> dict:
    """Evaluate the user-approved gate, keeping missing bins undefined."""
    theta = np.asarray(theta, dtype=float)
    moments = cosine_moments(theta, moment_order)
    edges = np.linspace(0, np.pi, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    blue = np.histogram(theta, edges)[0]
    red = np.histogram(np.pi - theta, edges)[0]
    total = blue + red
    ratio = np.divide(blue, total, out=np.full(bins, np.nan), where=total > 0)
    target = np.cos(centers / 2) ** 2
    residuals = born_moment_residuals(moments)
    rms = float(np.sqrt(np.mean((ratio - target) ** 2)))
    moment_max = float(np.max(np.abs(residuals)))
    return dict(
        counts=blue, reflected_counts=red, edges=edges, centers=centers,
        ratio=ratio, target=target, moments=moments, residuals=residuals,
        coverage=float(np.mean(total > 0)), center_rms=rms,
        moment_max=moment_max,
        accepted=bool(np.all(total > 0) and rms <= .05 and moment_max <= .05),
        S_born_100=born_ratio_from_theta(theta, np.pi-theta, n_theta=100).similarity,
        whole_bin=histogram_born_errors(edges, ratio),
    )


def rational_phase_inventory(
    divisors: list[int], *, numerator: int = 99, factor: int = 200,
    bins: int = 64,
) -> dict:
    """Count rational multiples of pi using integer arithmetic only.

    Every signed sum has phase/pi = integer/denominator. Folding and
    binning are exact, so no floating-point edge decisions enter the proof.
    """
    if not divisors or any(d < 1 or not isinstance(d, int) for d in divisors):
        raise ValueError("divisors must be positive integers")
    common = math.lcm(*divisors)
    denominator = factor * common
    steps = np.array([numerator * common // d for d in divisors], dtype=np.int64)
    phases = signed_sums(steps)
    folded = np.abs((phases + denominator) % (2 * denominator) - denominator)
    indices = np.minimum(folded * bins // denominator, bins - 1)
    counts = np.bincount(indices, minlength=bins)
    remainders = (folded * bins) % denominator
    distance_units = int(np.minimum(remainders, denominator - remainders).min())
    return dict(
        counts=counts, denominator=denominator, folded_integers=folded,
        minimum_edge_distance_over_pi=Fraction(distance_units, bins * denominator),
    )


def _arctan_bounds(reciprocal: int, terms: int = 24) -> tuple[Fraction, Fraction]:
    x = Fraction(1, reciprocal)
    total = sum((-1) ** k * x ** (2*k + 1) / (2*k + 1) for k in range(terms))
    next_term = (-1) ** terms * x ** (2*terms + 1) / (2*terms + 1)
    return min(total, total + next_term), max(total, total + next_term)


def certified_pi_bounds() -> tuple[Fraction, Fraction]:
    """Prove a decimal enclosure using Machin's formula and alternating sums."""
    a, b = _arctan_bounds(5), _arctan_bounds(239)
    lower, upper = 16*a[0] - 4*b[1], 16*a[1] - 4*b[0]
    declared = (Fraction(3141592653589793, 10**15),
                Fraction(3141592653589794, 10**15))
    if not declared[0] < lower < upper < declared[1]:
        raise ArithmeticError("Machin enclosure did not certify pi bounds")
    return declared


def cosine_pi_bounds(
    coefficient: Fraction, pi_bounds: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    """Rational enclosure by Taylor remainder and the Lipschitz bound for cos."""
    coefficient = (coefficient + 1) % 2 - 1
    pi_mid = sum(pi_bounds) / 2
    x = coefficient * pi_mid
    terms = 12
    total = sum((-1)**k * x**(2*k) / math.factorial(2*k)
                for k in range(terms + 1))
    error = (abs(x)**(2*terms + 2) / math.factorial(2*terms + 2)
             + abs(coefficient) * (pi_bounds[1] - pi_bounds[0]) / 2)
    return max(Fraction(-1), total-error), min(Fraction(1), total+error)


def _interval_product(left: tuple, right: tuple) -> tuple:
    values = [a*b for a in left for b in right]
    return min(values), max(values)


def certify_commuting_seed(config: dict) -> dict:
    """Prove the gate and its perturbation radius using exact rational bounds.

    This certificate is a finite analytic/combinatorial computation. Returned
    decimal summaries are display values; all acceptance decisions use exact
    fractions. Twelve Taylor terms suffice by a wide margin here.
    """
    gate = config["criterion"]
    bins, order = gate["theta_bins"], gate["maximum_moment_order"]
    divisors = config["phase_divisors"]
    numerator, factor = config["phase_numerator"], config["phase_denominator_factor"]
    inventory = rational_phase_inventory(divisors, numerator=numerator,
                                         factor=factor, bins=bins)
    pi_bounds = certified_pi_bounds()
    counts = inventory["counts"]
    rms_square_upper = Fraction(0)
    for k, (blue, red) in enumerate(zip(counts, counts[::-1])):
        if blue + red == 0:
            raise ArithmeticError("seed has incomplete polar coverage")
        ratio = Fraction(int(blue), int(blue + red))
        cos_interval = cosine_pi_bounds(Fraction(2*k+1, 2*bins), pi_bounds)
        target = tuple((1+x)/2 for x in cos_interval)
        rms_square_upper += max((ratio-x)**2 for x in target) / bins
    moments = []
    for n in range(order + 1):
        interval = (Fraction(1), Fraction(1))
        for divisor in divisors:
            factor_bounds = cosine_pi_bounds(
                Fraction(n*numerator, factor*divisor), pi_bounds)
            interval = _interval_product(interval, factor_bounds)
        moments.append(interval)
    residual_upper = max(
        max(abs(2*moments[n][0]-moments[n-1][1]-moments[n+1][1]),
            abs(2*moments[n][1]-moments[n-1][0]-moments[n+1][0]))
        for n in range(1, order, 2)
    )
    radius = Fraction(str(config["phase_l1_radius"]))
    edge_lower = inventory["minimum_edge_distance_over_pi"] * pi_bounds[0]
    # |delta a_n| <= n*radius, hence |delta d_m| <= 4n*radius.
    residual_ball_upper = residual_upper + 4*(order-1)*radius
    rms_limit = Fraction(str(gate["maximum_center_rms"]))
    moment_limit = Fraction(str(gate["maximum_moment_residual"]))
    if not (rms_square_upper <= rms_limit**2
            and residual_ball_upper <= moment_limit and radius < edge_lower):
        raise ArithmeticError("the specified seed/ball does not meet the exact gate")
    return dict(
        exact_counts=counts.tolist(), roots=int(counts.sum()),
        denominator=inventory["denominator"],
        minimum_edge_distance_rad_lower=float(edge_lower),
        center_rms_upper=float(math.sqrt(float(rms_square_upper))),
        moment_residual_upper=float(residual_upper),
        entire_ball_moment_residual_upper=float(residual_ball_upper),
        phase_l1_radius=float(radius), coverage=1,
        decisions="Exact Fraction inequalities; floating-point values are display summaries",
        gate_certified=True,
    )
