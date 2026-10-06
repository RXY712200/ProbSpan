"""Generate the authorized large-parameter reference with mpmath 1.3.0.

Run with: uv run --with mpmath==1.3.0 python oracle/generate_large.py
The ordinary frozen oracle is never read or rewritten by this generator.
"""

from __future__ import annotations

import argparse
import json
from itertools import pairwise
from pathlib import Path

import mpmath as mp

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "large_reference.json"
DIGITS = 80
CHECK_DIGITS = 60
TAIL_LIMIT = 256
RESIDUAL = mp.mpf("1e-45")
MAX_ITERATIONS = 180
MAX_COUNT = 2**63 - 1


def count_cases() -> list[tuple[int, int]]:
    cases = [(n, n) for n in (10**6, 5 * 10**8, 10**12, 10**16, 10**17, 10**18)]
    cases += [(n, n) for n in (2**53 - 1, 2**53, 2**53 + 1, MAX_COUNT)]
    for n in (10**12, MAX_COUNT):
        cases += [(0, n), (n, 0), (1, n), (n, 1), (100, n), (n, 100)]
    cases += [(n // 3, n) for n in (10**15, 10**17, 10**18, MAX_COUNT)]
    cases += [(MAX_COUNT // 1000, MAX_COUNT), (MAX_COUNT, MAX_COUNT // 1000)]
    return cases


class BetaIntegral:
    """Direct arbitrary-precision Beta integral after a log-odds substitution.

    mpmath's adaptive tanh-sinh quadrature is independent of the C solver's
    fixed-order Gauss-Legendre rule. Exact log-gamma normalization is safe at
    60/80 digits for the int64 domain; no Stirling series is used here.
    """

    def __init__(self, alpha: mp.mpf, beta: mp.mpf):
        self.alpha, self.beta = alpha, beta
        self.total = alpha + beta
        self.center = alpha / self.total
        self.scale = mp.sqrt(1 / alpha + 1 / beta)
        self.normalizer = (
            mp.loggamma(self.total)
            - mp.loggamma(alpha)
            - mp.loggamma(beta)
            + alpha * mp.log(self.center)
            + beta * mp.log(1 - self.center)
            + mp.log(self.scale)
        )

    def density(self, t: mp.mpf) -> mp.mpf:
        shift = self.scale * t
        return mp.exp(
            self.normalizer
            + self.alpha * shift
            - self.total * mp.log1p(self.center * mp.expm1(shift))
        )

    def integral(self, lower: mp.mpf, upper: mp.mpf) -> mp.mpf:
        # Split around the central mass so adaptive quadrature cannot miss it.
        knots = (
            [lower]
            + [mp.mpf(k) for k in (-64, -16, -8, -4, 0, 4, 8, 16, 64) if lower < k < upper]
            + [upper]
        )
        return mp.quad(self.density, knots, method="tanh-sinh")

    def cdf_t(self, t: mp.mpf) -> mp.mpf:
        if t < 0:
            return self.integral(mp.mpf(-TAIL_LIMIT), t)
        return 1 - self.integral(t, mp.mpf(TAIL_LIMIT))

    def cdf(self, x: mp.mpf) -> mp.mpf:
        if x <= 0 or x >= 1:
            return mp.mpf(0 if x <= 0 else 1)
        t = (mp.log(x / (1 - x)) - mp.log(self.alpha / self.beta)) / self.scale
        if abs(t) >= TAIL_LIMIT:
            return mp.mpf(0 if t < 0 else 1)
        return self.cdf_t(t)

    def quantile(self, p: mp.mpf) -> mp.mpf:
        lower, upper, t = mp.mpf(-TAIL_LIMIT), mp.mpf(TAIL_LIMIT), mp.mpf(0)
        for _ in range(MAX_ITERATIONS):
            residual = self.cdf_t(t) - p
            if abs(residual) < RESIDUAL:
                x = self.center * mp.exp(self.scale * t)
                x /= 1 + self.center * mp.expm1(self.scale * t)
                assert abs(self.cdf(x) - p) < mp.mpf("1e-40")
                return x
            if residual < 0:
                lower = t
            else:
                upper = t
            candidate = t - residual / self.density(t)
            t = candidate if lower < candidate < upper else (lower + upper) / 2
        raise ArithmeticError("High-precision quantile did not converge")


def calculate(events: int, complements: int) -> dict:
    alpha, beta = mp.mpf(events) + mp.mpf("0.5"), mp.mpf(complements) + mp.mpf("0.5")
    integral = BetaIntegral(alpha, beta)
    lower, upper = (
        integral.quantile(mp.mpf("0.025")),
        integral.quantile(mp.mpf("0.975")),
    )
    mean = alpha / (alpha + beta)
    assert 0 <= lower < mean < upper <= 1
    assert abs(integral.integral(mp.mpf(-TAIL_LIMIT), mp.mpf(TAIL_LIMIT)) - 1) < mp.mpf("1e-40")
    if events == complements:
        assert abs(integral.cdf(mp.mpf("0.5")) - mp.mpf("0.5")) < mp.mpf("1e-40")
        assert abs(lower + upper - 1) < mp.mpf("1e-40")

    # The private C primitive accepts binary64 shapes, unlike the exact count
    # formula above. Test its mathematical value at those represented inputs.
    a, b = mp.mpf(float(events) + 0.5), mp.mpf(float(complements) + 0.5)
    primitive = BetaIntegral(a, b)
    center = a / (a + b)
    sigma = mp.sqrt(center * (1 - center) / (a + b + 1))
    probes = []
    for k in (-2, -1, 0, 1, 2):
        x = max(0.0, min(1.0, float(center + k * sigma)))
        probability = primitive.cdf(mp.mpf(x))
        reflected = BetaIntegral(b, a).cdf(1 - mp.mpf(x))
        assert 0 <= probability <= 1
        assert abs(probability + reflected - 1) < mp.mpf("1e-40")
        probes.append({"x": x, "cdf": mp.nstr(probability, 50)})
    assert all(mp.mpf(p["cdf"]) <= mp.mpf(q["cdf"]) for p, q in pairwise(probes))
    ready = events + complements >= 20 and upper - lower <= mp.mpf("0.25")
    return {
        "events": events,
        "complements": complements,
        "mean": mp.nstr(mean, 50),
        "lower": mp.nstr(lower, 50),
        "upper": mp.nstr(upper, 50),
        "ready": bool(ready),
        "cdf_probes": probes,
    }


def generate(digits: int) -> dict:
    with mp.workdps(digits):
        cases = []
        for events, complements in count_cases():
            print(f"{digits} digits: {events}/{complements}", flush=True)
            cases.append(calculate(events, complements))
    return {
        "metadata": {
            "scope": "Large-parameter SciPy breakdown region and boundary controls only; ordinary frozen oracle unchanged",
            "authorization": "Step 2 corrected large-count numerical reference policy",
            "model": "alpha=events+0.5; beta=complements+0.5; mean=alpha/(alpha+beta); central Beta quantiles 0.025/0.975",
            "gate": "sample_size>=20 and upper-lower<=0.25; model_version=1; gate_version=1",
            "tool": "mpmath",
            "tool_version": mp.__version__,
            "decimal_precision": digits,
            "method": "Exact log-gamma normalized Beta integral; adaptive tanh-sinh quadrature in scaled logit coordinate; safeguarded Newton quantiles",
            "tail_limit": TAIL_LIMIT,
            "tail_note": "Shapes>=0.5 give omitted standardized logit tail mass below 1e-78 at +/-256",
            "stored_significant_digits": 50,
            "private_cdf_inputs": "Exact represented binary64 shapes and x; public interval uses exact integer counts plus 0.5",
            "absolute_tolerance": 1e-10,
            "relative_tolerance": 1e-10,
        },
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-precision", action="store_true")
    args = parser.parse_args()
    if mp.__version__ != "1.3.0":
        raise SystemExit("Reference generation requires mpmath 1.3.0")
    data = generate(CHECK_DIGITS if args.verify_precision else DIGITS)
    if args.verify_precision:
        saved = json.loads(OUTPUT.read_text(encoding="utf-8"))
        # Comparing rounded binary64 expectations validates the precision budget
        # independently of decimal formatting beyond the C output resolution.
        for actual, expected in zip(data["cases"], saved["cases"], strict=True):
            for key in ("mean", "lower", "upper"):
                assert float(actual[key]) == float(expected[key])
            for actual_probe, expected_probe in zip(
                actual["cdf_probes"], expected["cdf_probes"], strict=True
            ):
                assert actual_probe["x"] == expected_probe["x"]
                assert float(actual_probe["cdf"]) == float(expected_probe["cdf"])
        print("60/80-digit reference expectations agree at binary64 precision")
        return
    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("ascii")
    if args.check:
        if OUTPUT.read_bytes() != payload:
            raise SystemExit("Large-count reference is stale")
        print("Large-count reference is current")
    else:
        OUTPUT.write_bytes(payload)
        print(f"Wrote {len(data['cases'])} corrected reference cases")


if __name__ == "__main__":
    main()
