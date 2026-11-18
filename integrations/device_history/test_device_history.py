"""Isolated regression and independent numerical checks for the Preview reference."""

from dataclasses import replace
from fractions import Fraction as F
from math import asin, cos, exp, lgamma, pi, sin, sqrt
import os
from pathlib import Path as FilePath
import unittest

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

from research.preview_history import SCENARIOS, generate, hyper_grid, stratified_result

from .evidence import (Applicability, Assumption, Batch, Counts, Declaration,
                       Observation, Path, review)
from .example import device_batch
from .standardization import ENDPOINT_WIDTH, standardize
from .v1 import estimate_v1


def declaration(assumption, applicability=Applicability.SUPPORTED):
    return Declaration(applicability, assumption, "synthetic-fixture-design")


def half_integer_cdf(e, c, x):
    """Independent recurrence from the arcsine CDF, for bounded test cases."""
    if x <= 0:
        return 0.
    if x >= 1:
        return 1.
    a = b = .5
    value = (2 / pi) * asin(sqrt(x))
    kernel = lambda: x**a * (1-x)**b * exp(lgamma(a+b)-lgamma(a)-lgamma(b))
    for _ in range(e):
        value -= kernel() / a
        a += 1
    for _ in range(c):
        value += kernel() / b
        b += 1
    return value


def independent_limits(counts, weights):
    # Integrate against the first Beta density directly with x=sin²(theta).
    # This removes the endpoint singularity without using inverse Beta grids.
    a, b = counts[0].events + .5, counts[0].complements + .5
    norm = 2 * exp(lgamma(a+b)-lgamma(a)-lgamma(b))
    w, v = weights
    e, c = counts[1].events, counts[1].complements

    def cdf(q):
        def integrand(t):
            y = (q - w*sin(t)**2) / v
            return norm * sin(t)**(2*a-1) * cos(t)**(2*b-1) * half_integer_cdf(e, c, y)

        edges = [asin(sqrt(x)) for x in ((q-v)/w, q/w) if 0 < x < 1]
        value, error = quad(integrand, 0, pi/2, points=edges, epsabs=2e-11, epsrel=2e-11)
        if error > 2e-10:
            raise AssertionError("independent quadrature did not converge")
        return value

    return tuple(brentq(lambda q: cdf(q)-p, 0, 1, xtol=1e-12) for p in (.025, .975))


def rational_moments(counts, weights):
    mean, variance = F(0), F(0)
    for (events, complements), w in zip(counts, weights):
        a, b = F(2*events+1, 2), F(2*complements+1, 2)
        mean += w*a/(a+b)
        variance += w*w*a*b/((a+b)**2*(a+b+1))
    return float(mean), float(variance)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.target = device_batch("target", [(1, 3), (2, 3)])
        self.source = device_batch("source", [(3, 4), (0, 0)])
        self.row = self.target.rows[0]

    def strict(self, *rows, applicability=Applicability.SUPPORTED):
        batch = replace(self.target, rows=rows)
        return review(Path.STRICT, batch, declaration(Assumption.TARGET_SHARED, applicability),
                      cutoff_hour=100)

    def reject(self, audit, reason, applicability):
        self.assertEqual((audit.reason, audit.applicability), (reason, applicability))
        self.assertIsNone(audit.counts)
        self.assertEqual(audit.target_audit.included + audit.source_audit.included, 0)
        self.assertEqual(estimate_v1(audit, None).status, "unavailable_review")
        self.assertIsNone(standardize(audit).estimate)

    def test_strict_and_pool_counts(self):
        self.assertEqual(self.strict(*self.target.rows).counts, (Counts(3, 3),))
        pool = review(Path.POOL, self.target, declaration(Assumption.SOURCE_TARGET_SHARED),
                      cutoff_hour=100, source=self.source)
        self.assertEqual(pool.counts, (Counts(6, 4),))
        self.assertEqual(pool.source_audit.included, 4)
        self.assertEqual(pool.target_scope, self.target.scope)
        self.assertEqual(pool.source_scope, self.source.scope)

    def test_duplicates_and_conflicts(self):
        other = replace(self.row, query="query-B")
        result = self.strict(self.row, other, self.target.rows[1])
        self.assertEqual(result.counts, (Counts(1, 1),))
        self.assertEqual(result.target_audit.duplicate_aliases, 1)
        self.reject(self.strict(self.row, replace(other, failed=False)), "observation_conflict",
                    Applicability.INCOMPATIBLE)
        pool = review(Path.POOL, self.target, declaration(Assumption.SOURCE_TARGET_SHARED),
                      cutoff_hour=100, source=replace(self.source, rows=(other,)))
        self.reject(pool, "source_target_overlap", Applicability.INCOMPATIBLE)

    def test_unmodelled_dependence_preserves_records(self):
        for row in (replace(self.target.rows[1], cluster=self.row.cluster),
                    replace(self.target.rows[1], device=self.row.device, cycle="cycle-2")):
            with self.subTest(row=row):
                result = self.strict(self.row, row)
                self.reject(result, "unmodelled_dependence", Applicability.CONDITIONAL)
                self.assertEqual(result.target_audit.withheld, 2)
                self.assertEqual(result.target_audit.duplicate_aliases, 0)

    def test_definitions_regime_censoring_and_identity(self):
        for row, reason, status in (
            (replace(self.row, definition="other"), "endpoint_mismatch", Applicability.INCOMPATIBLE),
            (replace(self.row, horizon_hours=50), "endpoint_mismatch", Applicability.INCOMPATIBLE),
            (replace(self.row, process_version="old"), "observation_regime_mismatch",
             Applicability.INCOMPATIBLE),
            (replace(self.row, followup_hours=50, failed=None), "incomplete_outcome",
             Applicability.CONDITIONAL),
            (replace(self.row, followup_hours=50, failed=False), "incomplete_outcome",
             Applicability.CONDITIONAL),
            (replace(self.row, start_hour=1), "invalid_observation_time", Applicability.INCOMPATIBLE),
            (replace(self.row, cycle=""), "observation_identity_unknown", Applicability.UNKNOWN),
        ):
            with self.subTest(reason=reason):
                self.reject(self.strict(row), reason, status)

    def test_declaration_and_zero_target(self):
        for status in (Applicability.UNKNOWN, Applicability.CONDITIONAL, Applicability.INCOMPATIBLE):
            self.reject(self.strict(applicability=status), f"declaration_{status}", status)
        empty = replace(self.target, rows=())
        unreferenced = replace(declaration(Assumption.TARGET_SHARED), reference="")
        self.reject(review(Path.STRICT, empty, unreferenced, cutoff_hour=100),
                    "declaration_evidence_unknown", Applicability.UNKNOWN)
        unsupported = review(Path.POOL, empty, declaration(Assumption.TARGET_SHARED),
                             cutoff_hour=100, source=self.source)
        self.reject(unsupported, "assumption_mismatch", Applicability.INCOMPATIBLE)
        unknown_source = review(Path.POOL, empty, declaration(Assumption.SOURCE_TARGET_SHARED),
                                cutoff_hour=100)
        self.reject(unknown_source, "source_required", Applicability.UNKNOWN)
        old = replace(self.source, scope=replace(self.source.scope, process_version="old"))
        self.reject(review(Path.POOL, empty, declaration(Assumption.SOURCE_TARGET_SHARED),
                           cutoff_hour=100, source=old), "scope_regime_mismatch",
                    Applicability.INCOMPATIBLE)
        allowed = review(Path.POOL, empty, declaration(Assumption.SOURCE_TARGET_SHARED),
                         cutoff_hour=100, source=self.source)
        self.assertEqual(allowed.counts, (Counts(3, 1),))
        self.assertEqual(allowed.declaration.kind, "caller_declaration")

    def test_cutoff_excludes_later_outcome_even_on_same_identity(self):
        later = replace(self.row, available_hour=200, failed=False)
        result = self.strict(self.row, later)
        self.assertEqual(result.counts, (Counts(1, 0),))
        self.assertEqual(result.target_audit.after_cutoff, 1)
        self.reject(self.strict(replace(later, available_hour=None)), "availability_time_unknown",
                    Applicability.UNKNOWN)

    def test_target_weights_and_support(self):
        dec = declaration(Assumption.TARGET_STRATIFIED)
        for weights in (None, (.5, .4), (-.1, 1.1), (float("nan"), .5), (0,), (True, 0)):
            result = review(Path.STANDARD, self.target, dec, cutoff_hour=100, weights=weights)
            self.reject(result, "weights_unknown" if weights is None else "invalid_weights",
                        Applicability.UNKNOWN if weights is None else Applicability.INCOMPATIBLE)
        batch = replace(self.target, rows=(self.row,))
        self.reject(review(Path.STANDARD, batch, dec, cutoff_hour=100, weights=(.8, .2)),
                    "missing_stratum_support", Applicability.CONDITIONAL)
        result = review(Path.STANDARD, self.target, dec, cutoff_hour=100, weights=(1, 0))
        self.assertEqual(result.counts, (Counts(1, 2), Counts(0, 0)))
        self.assertEqual(result.target_audit.zero_weight, 3)


class NumericalTests(unittest.TestCase):
    def check_limits(self, counts, weights, expected):
        self.assertEqual(expected.status, "ok")
        value = expected.estimate
        for bracket, p in zip((value.lower_bracket, value.upper_bracket),
                              independent_limits(counts, weights)):
            self.assertLessEqual(bracket[0], p)
            self.assertGreaterEqual(bracket[1], p)
            self.assertLessEqual(bracket[1]-bracket[0], ENDPOINT_WIDTH)
        return value

    def test_known_heterogeneous_and_population_change(self):
        batch = device_batch("target", [(2, 20), (9, 20)])
        estimates = []
        for weights in ((F(4, 5), F(1, 5)), (F(1, 5), F(4, 5))):
            r = review(Path.STANDARD, batch, declaration(Assumption.TARGET_STRATIFIED),
                       cutoff_hour=100, weights=tuple(map(float, weights)))
            estimate = self.check_limits(r.counts, r.weights, standardize(r))
            mean, variance = rational_moments([(2, 18), (9, 11)], weights)
            self.assertAlmostEqual(estimate.mean, mean, places=15)
            self.assertAlmostEqual(estimate.variance, variance, places=15)
            estimates.append(estimate.mean)
        self.assertGreater(estimates[1], estimates[0])

    def test_boundary_and_budget_failure(self):
        batch = device_batch("target", [(0, 1), (1, 1)])
        dec = declaration(Assumption.TARGET_STRATIFIED)
        r = review(Path.STANDARD, batch, dec, cutoff_hour=100, weights=(.5, .5))
        outcome = self.check_limits(r.counts, r.weights, standardize(r))
        self.assertAlmostEqual(outcome.lower + outcome.upper, 1.)
        self.assertAlmostEqual(outcome.mean, .5)
        self.assertAlmostEqual(outcome.variance, .03125)
        failure = standardize(r, max_bins=256)
        self.assertEqual(failure.status, "numerical_budget_exhausted")
        self.assertIsNone(failure.estimate)
        one = review(Path.STANDARD, batch, dec, cutoff_hour=100, weights=(1, 0))
        estimate = standardize(one).estimate
        self.assertEqual(estimate.bins, 0)
        self.assertAlmostEqual(estimate.mean, .25)
        self.assertAlmostEqual(estimate.variance, .0625)
        for p, bracket in zip((.025, .975), (estimate.lower_bracket, estimate.upper_bracket)):
            limit = brentq(lambda x: half_integer_cdf(0, 1, x) - p, 0, 1, xtol=1e-14)
            self.assertLessEqual(bracket[0], limit)
            self.assertGreaterEqual(bracket[1], limit)

    def test_numerical_range_failure_preserves_review(self):
        batch = device_batch("target", [(3, 10001), (0, 0)])
        r = review(Path.STANDARD, batch, declaration(Assumption.TARGET_STRATIFIED),
                   cutoff_hour=100, weights=(1, 0))
        result = standardize(r)
        self.assertEqual(result.status, "numerical_range")
        self.assertEqual(r.counts, (Counts(3, 9998), Counts(0, 0)))
        self.assertIs(result.review, r)
        self.assertIsNone(result.estimate)

    def test_phase_two_mix_shift(self):
        case = next(c for c in SCENARIOS if c.name == "mix_shift")
        rows, truth = generate(case, np.random.default_rng([902618, SCENARIOS.index(case), 0]))

        def convert(role):
            original = device_batch(role, [(0, 0), (0, 0)])
            return replace(original, rows=tuple(
                Observation(row.unit_id, "cycle", row.cluster, row.query,
                            ("low", "high")[row.stratum], row.observed_at, row.observed_at + 100,
                            100, bool(row.outcome), "process-A", "fixed-load-A")
                for row in rows if row.role == role))

        r = review(Path.STANDARD, convert("target"), declaration(Assumption.SOURCE_TARGET_STRATIFIED),
                   cutoff_hour=1500, source=convert("source"), weights=case.weights)
        actual = standardize(r)
        prior = stratified_result([row for row in rows if row.role == "source"],
                                  [row for row in rows if row.role == "target"], case.weights,
                                  "standard", np.random.default_rng(42), 131072,
                                  hyper_grid(25, 128), .2, 20)
        self.assertEqual(actual.status, "ok")
        self.assertEqual(r.target_audit.included, 20)
        self.assertEqual(r.source_audit.included, 320)
        self.assertAlmostEqual(case.weights @ truth, .09)
        self.assertAlmostEqual(actual.estimate.mean, prior[0], places=14)
        self.assertLess(abs(actual.estimate.lower - prior[1]), .002)
        self.assertLess(abs(actual.estimate.upper - prior[2]), .002)


class InstalledV1Tests(unittest.TestCase):
    def test_installed_v1_values_and_states(self):
        executable = FilePath(os.environ["PROBSPAN_DEVICE_CONSUMER"])
        for events, total, expected_state in ((0, 0, "NO_HISTORY"), (18, 20, "INSUFFICIENT"),
                                              (19, 20, "VALID")):
            r = review(Path.STRICT, device_batch("target", [(events, total), (0, 0)]),
                       declaration(Assumption.TARGET_SHARED), cutoff_hour=100)
            result = estimate_v1(r, executable)
            self.assertEqual(result.status, "ok")
            self.assertEqual(result.history["state"], expected_state)
            self.assertEqual(result.history["statistically_ready"], expected_state == "VALID")
            if total:
                self.assertAlmostEqual(result.history["estimate"]["mean"], (events+.5)/(total+1))
            else:
                self.assertIsNone(result.history["estimate"])
        r = review(Path.POOL, device_batch("target", [(19, 20), (0, 0)]),
                   declaration(Assumption.SOURCE_TARGET_SHARED), cutoff_hour=100,
                   source=device_batch("source", [(10, 10), (0, 0)]))
        result = estimate_v1(r, executable)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.history["size"], 30)
        self.assertAlmostEqual(result.history["estimate"]["mean"], 29.5/31)
        self.assertEqual(result.history["state"], "VALID")
