"""B-E006: independent high-precision quadrature at binary64 arguments."""

import argparse
import json
import math
from pathlib import Path
import subprocess

import mpmath as mp


def probe(executable, kind, a, b, x):
    out = subprocess.check_output(
        [executable, kind, float(a).hex(), float(b).hex(), float(x).hex()], text=True
    )
    return float.fromhex(out.strip())


def reference(a, b, x, digits, limit):
    with mp.workdps(digits):
        x, a, b = mp.mpf(x), mp.mpf(a), mp.mpf(b)
        if x == 0 or x == 1:
            return x
        if x > a / (a + b):
            return 1 - reference(b, a, 1 - x, digits, limit)
        if a == b and x == mp.mpf(".5"):
            return mp.mpf(".5")
        scale = mp.sqrt(1 / a + 1 / b)
        center = mp.log(a / b)
        t = (mp.log(x / (1 - x)) - center) / scale
        log_constant = mp.loggamma(a + b) - mp.loggamma(a) - mp.loggamma(b) + mp.log(scale)

        def density(z):
            logit = center + scale * z
            return mp.exp(log_constant - a * mp.log1p(mp.exp(-logit)) - b * mp.log1p(mp.exp(logit)))

        knots = [-limit, -64, -32, -16, -8, -4, -2]
        if t <= knots[0]:
            raise ValueError(f"x outside quadrature budget: t={t}")
        return mp.quad(density, [z for z in knots if z < t] + [t])


def checked_reference(a, b, x):
    lo = reference(a, b, x, 65, 128)
    hi = reference(a, b, x, 95, 192)
    with mp.workdps(95):
        return float(hi), float(abs(lo - hi))


def analyze(executable):
    # A direct arcsine CDF gives an independent normalization check on quadrature.
    with mp.workdps(95):
        a = b = mp.mpf(".5")
        x = mp.mpf(".0001")
        arcsine_error = float(abs(reference(a, b, x, 95, 192) - 2 * mp.asin(mp.sqrt(x)) / mp.pi))
    assert arcsine_error < 1e-45

    cases = [
        ("arcsine", .5, .5, [.0001, .15, .5, .9999]),
        ("at_switch", 4999.5, 5000.5, [.49, .5, .51]),
        ("after_switch", 5000.5, 5000.5, [.49, .5, .51]),
        ("strong_skew", float(2**62), .5, [math.nextafter(1, 0), 1.]),
        ("extreme_balanced", float(2**62), float(2**62), [math.nextafter(.5, 0), .5, math.nextafter(.5, 1)]),
    ]
    outputs = []
    for name, a, b, xs in cases:
        cdfs = []
        for x in xs:
            ref, drift = checked_reference(a, b, x)
            cdf = probe(executable, "cdf", a, b, x)
            cdfs.append({
                "x_hex": x.hex(), "runtime_cdf": cdf, "reference_cdf": ref,
                "absolute_error": abs(cdf - ref), "reference_budget_difference": drift,
            })
        quantiles = []
        for p in (.025, .5, .975):
            value = probe(executable, "ppf", a, b, p)
            left, right = max(0., math.nextafter(value, 0.)), min(1., math.nextafter(value, 1.))
            grid = [checked_reference(a, b, x) for x in (left, value, right)]
            quantiles.append({
                "p": p, "ppf_hex": value.hex(), "reference_cdf_prev_at_next": [c for c, _ in grid],
                "reference_budget_difference": max(d for _, d in grid),
                "bracketed_with_1e_minus_10": grid[0][0] - 1e-10 <= p <= grid[2][0] + 1e-10,
            })
        outputs.append({"case": name, "shape_a": a, "shape_b": b, "cdf": cdfs, "quantiles": quantiles})

    thresholds = []
    symmetric_shape = float(2**62)
    for string in ("1.9999999999999999", "2.0000000000000001", "2.0000000000000004"):
        out = subprocess.check_output([executable, "odds", string], text=True).split()
        odds, x = map(float.fromhex, out)
        ref, drift = checked_reference(symmetric_shape, symmetric_shape, x)
        with mp.workdps(95):
            x_exact = 1 / mp.mpf(string)
            exact_tail = float(1 - reference(symmetric_shape, symmetric_shape, x_exact, 95, 192))
        c_tail = 1 - probe(executable, "cdf", symmetric_shape, symmetric_shape, x)
        thresholds.append({
            "decimal_input": string, "odds_hex": odds.hex(), "threshold_hex": x.hex(),
            "c_tail": c_tail, "represented_reference_tail": 1 - ref,
            "exact_decimal_threshold_reference_tail": exact_tail,
            "reference_budget_difference": drift,
        })
    return {"arcsine_absolute_error": arcsine_error, "cases": outputs, "thresholds": thresholds}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("probe", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = {"B-E006": analyze(str(args.probe.resolve()))}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
