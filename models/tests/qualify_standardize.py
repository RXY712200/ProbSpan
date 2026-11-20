"""Exact Fraction oracle for the installed-independent F003 probe."""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
import math
import random
import struct
import subprocess
import sys

POLICY = Fraction(1, 10**12)
ETA = math.ulp(0.0)
NORMAL = sys.float_info.min


def neighbors(value):
    point = float(value)
    encoded = Fraction(point)
    return ((math.nextafter(point, 0.0) if encoded > value else point),
            (math.nextafter(point, 1.0) if encoded < value else point))


def oracle(rows):
    if not rows:
        return (2, 1)
    weight = known = missing = Fraction()
    for w, support, p in rows:
        if not math.isfinite(w) or w < 0 or support not in (0, 1):
            return (1, 1)
        w = Fraction(w)
        weight += w
        if support:
            if not math.isfinite(p) or not 0 <= p <= 1:
                return (1, 1)
            known += w * Fraction(p)
        else:
            missing += w
    if abs(weight - 1) > POLICY:
        return (3, 1)
    lower = known / weight
    if missing:
        # Explicit assignments to the missing risks attain both endpoints.
        worlds = [sum(Fraction(w) * (Fraction(p) if support else fill)
                      for w, support, p in rows) / weight for fill in (0, 1)]
        assert worlds == [lower, (known + missing) / weight]
        return (0, 1, *neighbors(worlds[0]), *neighbors(worlds[1]))
    bounds = neighbors(lower)
    point = float(lower)
    encoding = 0 if bounds[0] == bounds[1] else (2 if point == 0 else 1)
    return (0, 0, encoding, point, *bounds)


def cases():
    yield "empty", []
    yield "bad-flag", [(1.,2,0.)]
    yield "bad-zero-risk", [(1.,1,0.), (0.,1,2.)]
    yield "all-missing", [(1.,0,0.)]
    yield "zero", [(1.,1,0.)]
    yield "one", [(1.,1,1.)]
    yield "missing-tiny", [(1.,1,0.), (ETA,0,0.)]
    yield "product-tiny", [(1.,1,0.), (ETA,1,ETA)]
    yield "midpoint-tiny", [(.5,1,ETA), (.5,1,0.)]
    yield "midpoint-even", [(.5,1,.5), (.5,1,math.nextafter(.5,1.))]
    yield "midpoint-odd", [(.5,1,math.nextafter(.5,1.)),
                          (.5,1,math.nextafter(math.nextafter(.5,1.),1.))]
    yield "signed-zero", [(1.,1,-0.), (-0.,0,0.)]
    yield "huge-policy", [(sys.float_info.max, 1, 1.)]
    yield "invalid-after-huge", [(sys.float_info.max, 1, 1.), (0., 1, 2.)]
    for sign, anchor in ((1, 1.), (-1, 1. - 2.**-39)):
        remainder = 1 + sign*POLICY - Fraction(anchor)
        for order, residual in enumerate(neighbors(remainder)):
            yield f"policy-{sign}-{order}", [(anchor,1,.5),(residual,0,0.)]
    for w in (math.nextafter(1.,0.),1.,math.nextafter(1.,math.inf)):
        for p in (0.,ETA,math.nextafter(NORMAL,0.),NORMAL,math.nextafter(NORMAL,1.),
                  math.nextafter(.5,0.),.5,math.nextafter(.5,1.),math.nextafter(1.,0.),1.):
            yield "encoding-neighbor", [(w,1,p)]
    yield "phase-b-e003", [(.8,1,.05),(.2,1,.45)]
    yield "simpson-a", [(.5,1,.2),(.5,1,.9)]
    yield "simpson-b", [(.5,1,.1),(.5,1,.8)]
    finite = list(product((0.,.25,.5,.75,1.), (1,), (0.,.5,1.)))
    finite += [(w,0,0.) for w in (0.,.25,.5,.75,1.)]
    for rows in product(finite, repeat=3):
        yield "finite-grid", rows

    rng = random.Random(310003)
    for i in range(160):
        size = 1024 if i < 8 else rng.randint(2,45)
        cuts = sorted([0, 2**20] + [rng.randrange(2**20) for _ in range(size-1)])
        rows = [((b-a)/2**20, int(i % 3 == 0 or rng.random() < .7),
                 math.ldexp(rng.random(), -rng.randrange(1076)))
                for a,b in zip(cuts,cuts[1:])]
        yield f"blind-{size}", rows
        yield f"permuted-{size}", list(reversed(rows))


def encoding(value):
    return struct.pack(">d", value)


def main():
    labeled = list(cases())
    payload = "".join(str(len(rows))+"\n"+"".join(f"{w.hex()} {s} {p.hex()}\n"
                       for w,s,p in rows) for _,rows in labeled)
    result = subprocess.run([sys.argv[1]], input=payload, text=True, capture_output=True, check=True)
    status, groups = Counter(), Counter()
    boundary = {}
    scientific = {}
    for (name,rows),line in zip(labeled,result.stdout.splitlines(),strict=True):
        expected = oracle(rows)
        actual = line.split()
        assert len(actual) == len(expected), (name,line,expected)
        for got,want in zip(actual,expected):
            assert (int(got)==want if isinstance(want,int)
                    else encoding(float.fromhex(got))==encoding(want)), (name,rows,line,expected)
        status[str(expected[0])] += 1
        groups[name if name in ("finite-grid","encoding-neighbor") else
               name.partition("-")[0]] += 1
        if name.startswith("policy-"):
            delta = abs(sum(Fraction(w) for w,_,_ in rows) - 1) - POLICY
            boundary[name] = {"weights":[w.hex() for w,_,_ in rows],
                              "sign": (delta>0)-(delta<0), "status":expected[0]}
        if name in ("phase-b-e003","simpson-a","simpson-b"):
            scientific[name] = expected[3]
    # A beats B within each stratum, but unequal sample mixing reverses the
    # comparison. Holding target weight fixed preserves the stratum ordering.
    assert .9*.2+.1*.9 < .1*.1+.9*.8
    assert scientific["simpson-a"] > scientific["simpson-b"]
    assert abs(scientific["phase-b-e003"]-.13) < 1e-16
    # If both weight and risk equal an estimated Bernoulli mean, omitting
    # covariance predicts .25 instead of E[X^2]=.5 for a single draw.
    shared = [Fraction(0),Fraction(1)]
    assert sum(x*x for x in shared)/2 > (sum(shared)/2)**2
    print(json.dumps({"cases":len(labeled), "input_sha256":hashlib.sha256(payload.encode()).hexdigest(),
                      "status_counts":status, "groups":groups, "policy_boundary":boundary,
                      "scientific_points":scientific}, indent=2))


if __name__ == "__main__":
    main()
