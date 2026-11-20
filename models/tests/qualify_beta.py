"""Qualify F002 against exact fractions and independently evaluated log-Beta."""
from fractions import Fraction
from itertools import product
import json
import math
import subprocess
import sys

import mpmath as mp

LOG_BUDGET = 2.0**-30
MOMENT_BUDGET = 2.0**-47
ETA = math.ulp(0.0)


def grid():
    priors = (0.5, 1.0, 10.0, 1_000_000.0)
    for a, b, history, n in product(priors, priors, (0, 1, 10, 1_000_000), (0, 1, 10, 10_000)):
        for e in sorted({0, history // 2, history}):
            f = history - e
            aa, bb = a + e, b + f
            keys = {0, min(1, n), n // 2, max(0, n - 1), n}
            if aa > 1 and bb > 1:
                mode = int((n + 1) * (aa - 1) / (aa + bb - 2))
                keys.update(k for k in (mode - 1, mode, mode + 1) if 0 <= k <= n)
            for k in sorted(keys):
                yield (a, b, e, f, n, k)


def reference(a, b, n, k, bits):
    with mp.workprec(bits):
        a, b = mp.mpf(a), mp.mpf(b)
        total = a + b
        mean = n * a / total
        variance = mean * b / total * (total + n) / (total + 1)
        log_pmf = mp.log(mp.binomial(n, k)) + mp.loggamma(a+k) + mp.loggamma(b+n-k)
        log_pmf -= mp.loggamma(total+n) + mp.loggamma(a) + mp.loggamma(b) - mp.loggamma(total)
        return log_pmf, mean, variance


def exact_mass(a, b, n, k):
    result = Fraction(math.comb(n, k))
    for i in range(k):
        result *= Fraction(a+i, a+b+i)
    for i in range(n-k):
        result *= Fraction(b+i, a+b+k+i)
    return result


def input_rows(executable, cases):
    cases = list(cases)
    payload = "".join(f"{a.hex()} {b.hex()} {e} {f} {n} {k}\n" for a,b,e,f,n,k in cases)
    result = subprocess.run([executable], input=payload, capture_output=True, text=True, check=True)
    return zip(cases, result.stdout.splitlines(), strict=True)


def compare(executable, cases):
    summary = dict(calls=0, rounded_zero=0, subnormal=0, ambiguous_rejected=0,
                   max_log_abs=0.0, max_normal_relative=0.0, max_mean_relative=0.0,
                   max_variance_relative=0.0, max_subnormal_grid_steps=0)
    for case, line in input_rows(executable, cases):
        a,b,e,f,n,k = case
        status, pmf, log_pmf, mean, variance, state, sa, sb, probability, prior_only = line.split()
        aa = float(Fraction(a)+e)
        bb = float(Fraction(b)+f)
        checked = reference(aa,bb,n,k,192)
        ordinary = reference(aa,bb,n,k,96)
        with mp.workprec(192):
            assert abs(ordinary[0]-checked[0]) < LOG_BUDGET/10
            for first, second in zip(ordinary[1:],checked[1:]):
                assert abs(first-second) <= MOMENT_BUDGET*abs(second)/10
            cutoff = -1075 * mp.log(2)
            if status == "3":
                assert abs(checked[0]-cutoff) <= 2*LOG_BUDGET, case
                summary["ambiguous_rejected"] += 1
                continue
            assert status == "0", (case,line)
            summary["calls"] += 1
            assert (float.fromhex(sa),float.fromhex(sb)) == (aa,bb)
            assert abs(mp.mpf(float.fromhex(probability))-mp.mpf(aa)/(mp.mpf(aa)+bb)) < MOMENT_BUDGET
            assert int(prior_only) == (e+f == 0)
            actual = tuple(map(float.fromhex,(log_pmf,mean,variance)))
            errors = [abs(mp.mpf(x)-r) for x,r in zip(actual, checked)]
            summary["max_log_abs"] = max(summary["max_log_abs"],float(errors[0]))
            assert errors[0] <= LOG_BUDGET, (case,errors)
            for name,error,truth in zip(("mean","variance"),errors[1:],checked[1:]):
                assert error <= MOMENT_BUDGET*abs(truth), (case,name,error)
                if truth:
                    key=f"max_{name}_relative"
                    summary[key]=max(summary[key],float(error/truth))
            value=float.fromhex(pmf)
            mass=mp.exp(checked[0])
            expected=float(mass)
            assert (value == 0.0) == (expected == 0.0), case
            assert math.copysign(1,value) == 1
            if n == 0:
                assert int(state) == 0 and value == 1 and actual == (0,0,0)
            elif value == 0:
                assert int(state) == 3
                summary["rounded_zero"] += 1
            elif value < sys.float_info.min:
                assert int(state) == 2
                summary["subnormal"] += 1
                steps=abs(round(value/ETA)-round(expected/ETA))
                summary["max_subnormal_grid_steps"]=max(summary["max_subnormal_grid_steps"],steps)
                assert abs(mp.mpf(value)-mass) <= 2*LOG_BUDGET*mass + ETA
            else:
                assert int(state) == 1
                relative=float(abs(mp.mpf(value)-mass)/mass)
                assert relative <= 2*LOG_BUDGET
                summary["max_normal_relative"]=max(summary["max_normal_relative"],relative)
    return summary


def normalization(executable, a, b, n):
    cases = [(float(a),float(b),0,0,n,k) for k in range(n+1)]
    with mp.workprec(192):
        mass=mp.exp(reference(a,b,n,0,192)[0])
        total=[]
        current=[]
        for (_,_,_,_,_,k), line in input_rows(executable,cases):
            status, encoded, log_value, *_ = line.split()
            assert status == "0"
            value=float.fromhex(encoded)
            assert abs(mp.mpf(float.fromhex(log_value))-mp.log(mass)) <= LOG_BUDGET
            total.append(value)
            current.append(mass)
            if k < n:
                mass *= mp.mpf(n-k)*(a+k)/((k+1)*(b+n-k-1))
        assert abs(mp.fsum(current)-1) < mp.mpf("1e-43")
        if n <= 10:
            exact=[exact_mass(a,b,n,k) for k in range(n+1)]
            assert sum(exact) == 1
            assert all(abs(mp.mpf(x.numerator)/x.denominator-m) < mp.mpf("1e-43")
                       for x,m in zip(exact,current))
        drift=abs(math.fsum(total)-1)
        assert drift <= 2*LOG_BUDGET
        return drift


def main():
    executable=sys.argv[1]
    challenge=[
        (math.nextafter(.5,1),math.nextafter(1e6,0),499999,500001,9999,12),
        (1.0,0.5,0,0,3581,0), (0.5,1.0,0,0,3581,3581),
        (3.7,112.1,7,15,2000,1800), (0.75,37.25,3,99,9981,33),
    ]
    # Seek the zero/subnormal midpoint using an independent boundary
    # likelihood, then challenge neighboring encodings on both sides.
    with mp.workprec(192):
        root=mp.findroot(lambda b: reference(1,b,1000,1000,192)[0]+1075*mp.log(2),
                         (100,300))
    for shift in (-1e-8,0,1e-8):
        challenge.append((1.0,float(root)+shift,0,0,1000,1000))
    print(json.dumps({"grid":compare(executable,grid()),
                      "challenge":compare(executable,challenge),
                      "normalization_abs":[normalization(executable,a,b,n)
                                           for a,b,n in ((2,3,10),(1,1,10),(1,5,10000))]},
                     indent=2))


if __name__ == "__main__":
    main()
