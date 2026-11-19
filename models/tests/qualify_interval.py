"""Compare the compiled probe with independent Decimal and rational references."""
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from itertools import product
import json
import math
from pathlib import Path
from statistics import NormalDist
import struct
import subprocess
import sys

from scipy.special import betaincinv, betainccinv

PI = Decimal("3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679")


def tail_and_slope(n, k, x, lower):
    """Normalize independently summed high-precision probability ratios."""
    if x == 0 or x == 1:
        return Decimal(int((n*x >= k) if lower else (n*x <= k))), Decimal(0)
    q = 1 - x
    pivot = int((n + 1) * x)
    normalizer = Decimal(1)
    wanted = (lambda j: j >= k) if lower else (lambda j: j <= k)
    total = Decimal(int(wanted(pivot)))
    boundary = Decimal(int(k == pivot))
    for direction, odds in ((1, x / q), (-1, q / x)):
        term = Decimal(1)
        stop = n if direction == 1 else 0
        for j in range(pivot, stop, direction):
            if direction == 1:
                term *= odds * (n - j) / (j + 1)
            else:
                term *= odds * j / (n - j + 1)
            index = j + direction
            normalizer += term
            if wanted(index):
                total += term
            if index == k:
                boundary = term
            # Beyond both the mode and the queried boundary, the remaining
            # terms decrease. (n+1) times this term bounds the omitted mass.
            if term < Decimal("1e-94") and (index >= k if direction == 1 else index <= k):
                break
    factor = k / x if lower else -(n - k) / q
    return total / normalizer, factor * boundary / normalizer


def rational_tail(n, k, x, lower):
    p = Fraction(x)
    indices = range(k, n+1) if lower else range(k+1)
    return sum(math.comb(n, j)*p**j*(1-p)**(n-j) for j in indices)


@lru_cache(None)
def cp_reference(n, k, tail, lower):
    seed = betaincinv(k, n-k+1, tail) if lower else betainccinv(k+1, n-k, tail)
    target = Decimal(tail)
    brackets = []
    for precision in (50, 90):
        with localcontext() as context:
            context.prec = precision
            x = Decimal(float(seed))
            if (lower and k == n) or (not lower and k == 0):
                power = (target.ln() / n).exp()
                x = power if lower else 1 - power
            elif (lower and k == 1) or (not lower and k == n-1):
                power = ((1-target).ln() / n).exp()
                x = 1 - power if lower else power
            else:
                for _ in range(2):
                    value, slope = tail_and_slope(n, k, x, lower)
                    x -= (value - target) / slope
            rounded = float(x)

            def sign(p):
                if n <= 10:
                    delta = rational_tail(n, k, p, lower) - Fraction(tail)
                else:
                    delta = tail_and_slope(n, k, Decimal(p), lower)[0] - target
                    if abs(delta) < Decimal("1e-36"):
                        raise ArithmeticError("unresolved reference sign")
                return (delta > 0) - (delta < 0)

            side = sign(rounded)
            if not side:
                bracket = rounded, rounded
            elif (side < 0) == lower:
                bracket = rounded, math.nextafter(rounded, 1)
                assert (sign(bracket[1]) >= 0 if lower else sign(bracket[1]) <= 0)
            else:
                bracket = math.nextafter(rounded, 0), rounded
                assert (sign(bracket[0]) <= 0 if lower else sign(bracket[0]) >= 0)
            brackets.append(bracket)
    assert brackets[0] == brackets[1], (n, k, tail, lower, brackets)
    return brackets[0]


@lru_cache(None)
def normal_root(tail, precision):
    with localcontext() as context:
        context.prec = precision
        target = Decimal(tail)
        z = Decimal(-NormalDist().inv_cdf(tail))
        for _ in range(5):
            # Integrate the normal density by its Taylor series on [0,z].
            power = z
            integral = power
            for j in range(1, 280):
                power *= -(z*z) / (2*j)
                integral += power / (2*j+1)
            scale = (2*PI).sqrt()
            residual = Decimal("0.5") - integral/scale - target
            z += residual * scale * (z*z/2).exp()
        return z


def wilson_ref(n, k, tail, lower, precision):
    with localcontext() as context:
        context.prec = precision
        z = normal_root(tail, precision)
        p = Decimal(k)/n
        shift = z*z/(2*n)
        radius = z * ((p*(1-p)+shift/2)/n).sqrt()
        return float((p+shift+(-radius if lower else radius))/(1+2*shift))


def encoding(x):
    return struct.unpack(">Q", struct.pack(">d", x))[0]


def grids():
    for n in (1, 2, 10, 100, 10_000, 1_000_000):
        for k, alpha in product(sorted({0, 1, n//2, n-1, n}),
                                (1e-10, 1e-6, .01, .05, .5)):
            yield "grid", n, k, alpha
    for n, k, alpha in ((3, 1, .11), (31, 17, .033), (4093, 2, .37),
                         (999983, 321987, .004), (999983, 999981, .0003),
                         (10, 0, math.nextafter(1e-10, 1.0)),
                         (100, 99, math.nextafter(.5, 0.0))):
        yield "challenge", n, k, alpha


def main():
    cases = [(group,n,k,alpha,method,side) for group,n,k,alpha in grids()
             for method,side in product(range(2), range(3))]
    lines = "".join(f"{method} {k} {n} {a.hex()} {side}\n"
                    for _,n,k,a,method,side in cases)
    process = subprocess.run([sys.argv[1]], input=lines, capture_output=True,
                             text=True, check=True)
    summary = {}
    for case, line in zip(cases, process.stdout.splitlines(), strict=True):
        group,n,k,alpha,method,side = case
        record = summary.setdefault(f"{group}_{'cp' if method else 'wilson'}",
                                    {"ok":0,"failure":[],"lower":{},"upper":{}})
        status, *values = line.split()
        if status != "0":
            record["failure"].append([n,k,alpha.hex(),side,int(status)])
            continue
        record["ok"] += 1
        tail = alpha/2 if side == 0 else alpha
        for lower, value in zip((True, False), map(float.fromhex, values)):
            if (lower and (side == 2 or k == 0)) or (not lower and (side == 1 or k == n)):
                assert value == (0.0 if lower else 1.0)
                continue
            metrics = record["lower" if lower else "upper"]
            if method:
                lo,hi = cp_reference(n,k,tail,lower)
                safe = lo if lower else hi
                assert value <= safe if lower else value >= safe, (case,value,safe)
                assert abs(value - (hi if lower else lo)) <= 2**-38 + math.ulp(value)
                with localcontext() as context:
                    context.prec = 50
                    mass = (Decimal(rational_tail(n,k,value,lower).numerator) /
                            Decimal(rational_tail(n,k,value,lower).denominator)
                            if n <= 10 else tail_and_slope(n,k,Decimal(value),lower)[0])
                    residual = float(abs(mass - Decimal(tail)))
                metrics["max_tail_abs"] = max(metrics.get("max_tail_abs",0),residual)
                metrics["max_tail_relative"] = max(metrics.get("max_tail_relative",0),residual/tail)
            else:
                safe = wilson_ref(n,k,tail,lower,50)
                assert safe == wilson_ref(n,k,tail,lower,90)
                assert abs(value-safe) <= 2**-45, (case,value,safe)
            metrics["max_endpoint_abs"] = max(metrics.get("max_endpoint_abs",0),abs(value-safe))
            metrics["max_endpoint_grid_steps"] = max(metrics.get("max_endpoint_grid_steps",0),
                                                       abs(encoding(value)-encoding(safe)))
    # Fixed-truth coverage using exact binomial probabilities and actual endpoints.
    asks = "".join(f"{m} {k} 20 {(.05).hex()} 0\n" for m,k in product(range(2),range(21)))
    result = subprocess.run([sys.argv[1]],input=asks,capture_output=True,text=True,check=True)
    for numerator, denominator in ((1, 100), (1, 200)):
        coverage = [Fraction(0), Fraction(0)]
        truth = Fraction(numerator, denominator)
        for (method,k),line in zip(product(range(2),range(21)),result.stdout.splitlines(),strict=True):
            status,lo,hi = line.split()
            assert status == "0"
            if Fraction(float.fromhex(lo)) <= truth <= Fraction(float.fromhex(hi)):
                coverage[method] += math.comb(20,k)*truth**k*(1-truth)**(20-k)
        assert coverage[1] >= Fraction(95,100)
        if denominator == 200:
            assert coverage[0] < Fraction(95,100)
        summary[f"coverage_n20_p_{numerator}_{denominator}"] = dict(zip(("wilson","cp"),map(float,coverage)))
    print(json.dumps(summary,indent=2))
    if any(record.get("failure") for record in summary.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
