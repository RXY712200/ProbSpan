"""Deterministic two-stratum Jeffreys reference, independent of the C core."""

from dataclasses import dataclass
from math import fsum, isfinite
from platform import python_version

import numpy as np
import scipy
from scipy.special import betainc, betaincinv

from .evidence import Applicability, Path, Review


ALGORITHM = "weighted-independent-jeffreys/equal-mass-envelope-v1"
TAILS = (.025, .975)
MIN_BINS = 256
MAX_BINS = 262144
MAX_STRATUM = 10000
PROBABILITY_GUARD = 2e-9
ENDPOINT_WIDTH = 2e-5


@dataclass(frozen=True)
class StandardizedRisk:
    mean: float
    variance: float
    lower: float
    upper: float
    lower_bracket: tuple[float, float]
    upper_bracket: tuple[float, float]
    bins: int


@dataclass(frozen=True)
class Standardization:
    review: Review
    status: str
    estimate: StandardizedRisk | None = None
    algorithm: str = ALGORITHM
    result_type: str = "target_parameter_posterior"
    python: str = python_version()
    numpy: str = np.__version__
    scipy: str = scipy.__version__
    bin_budget: int = MAX_BINS


class _NumericFailure(Exception):
    pass


def _shapes(counts):
    return counts.events + .5, counts.complements + .5


def _moments(shapes, weights):
    means = [a / (a + b) for a, b in shapes]
    variances = [m * (1 - m) / (a + b + 1) for (a, b), m in zip(shapes, means)]
    return (fsum(w * m for w, m in zip(weights, means)),
            fsum(w * w * v for w, v in zip(weights, variances)))


def _inverse_grid(shapes, bins):
    levels = np.arange(bins + 1) / bins
    edges = betaincinv(*shapes, levels)
    recovered = betainc(*shapes, edges)
    if (not np.all(np.isfinite(recovered)) or not np.all(np.diff(edges) > 0)
            or edges[0] != 0 or edges[-1] != 1
            or np.max(np.abs(recovered - levels)) > PROBABILITY_GUARD / 2):
        raise _NumericFailure("beta_grid_failure")
    return edges


def _invert(cdf, target):
    lo, hi = 0., 1.
    for _ in range(42):
        mid = (lo + hi) / 2
        mass = cdf(mid)
        if not 0 <= mass <= 1:
            raise _NumericFailure("cdf_failure")
        if mass < target:
            lo = mid
        else:
            hi = mid
    return lo, hi


def _quantile_brackets(shapes, weights, max_bins):
    # Integrate the smaller weight to reduce the interval extension caused by
    # each bin. The other weight is at least one half, keeping division stable.
    i = 0 if weights[0] <= weights[1] else 1
    j = 1 - i
    if weights[i] == 0:
        out = []
        for p in TAILS:
            lo, hi = betaincinv(*shapes[j], [p - PROBABILITY_GUARD, p + PROBABILITY_GUARD])
            if (not 0 <= lo <= hi <= 1 or hi - lo > ENDPOINT_WIDTH
                    or abs(betainc(*shapes[j], lo) - (p - PROBABILITY_GUARD)) > 1e-9
                    or abs(betainc(*shapes[j], hi) - (p + PROBABILITY_GUARD)) > 1e-9):
                raise _NumericFailure("beta_quantile_failure")
            out.append((float(lo), float(hi)))
        return out, 0
    bins = MIN_BINS
    while bins <= max_bins:
        grid = _inverse_grid(shapes[i], bins) * weights[i]

        def conditional_mass(q, edge):
            x = np.clip((q - edge) / weights[j], 0., 1.)
            return float(np.mean(betainc(*shapes[j], x)))

        # The integrand is decreasing in the integrated coordinate. Left bin
        # edges bound the CDF above and right edges bound it below. Inverting
        # the upper CDF gives the lower bound on the quantile, and vice versa.
        out = []
        for p in TAILS:
            lo, _ = _invert(lambda q: conditional_mass(q, grid[:-1]), p - PROBABILITY_GUARD)
            _, hi = _invert(lambda q: conditional_mass(q, grid[1:]), p + PROBABILITY_GUARD)
            if lo > hi:
                raise _NumericFailure("cdf_bracket_failure")
            out.append((lo, hi))
        if all(hi - lo <= ENDPOINT_WIDTH for lo, hi in out):
            return out, bins
        bins *= 2
    raise _NumericFailure("numerical_budget_exhausted")


def standardize(review: Review, *, max_bins: int = MAX_BINS) -> Standardization:
    """Estimate q, with a quantified discretization bracket at each endpoint."""
    if (review.path != Path.STANDARD or review.applicability != Applicability.SUPPORTED
            or review.counts is None or review.weights is None):
        return Standardization(review, "unavailable_review", bin_budget=max_bins)
    if (type(max_bins) is not int or not MIN_BINS <= max_bins <= MAX_BINS):
        return Standardization(review, "invalid_numerical_budget", bin_budget=max_bins)
    if any(c.size > MAX_STRATUM for c in review.counts):
        return Standardization(review, "numerical_range", bin_budget=max_bins)
    shapes = tuple(map(_shapes, review.counts))
    mean, variance = _moments(shapes, review.weights)
    try:
        brackets, bins = _quantile_brackets(shapes, review.weights, max_bins)
        lower, upper = (fsum(pair) / 2 for pair in brackets)
        if not all(map(isfinite, (mean, variance, lower, upper))) or not lower < upper:
            raise _NumericFailure("invalid_numeric_result")
    except _NumericFailure as error:
        return Standardization(review, str(error), bin_budget=max_bins)
    estimate = StandardizedRisk(mean, variance, lower, upper, *brackets, bins)
    return Standardization(review, "ok", estimate, bin_budget=max_bins)
