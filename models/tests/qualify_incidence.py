"""Independent rational and Decimal checks of the compiled incidence probe."""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import random
import subprocess
import sys
import time
import tracemalloc

MAX_COUNT = 2**53


def cases():
    yield "empty", 0, 0, 0, []
    yield "oversized", MAX_COUNT+1, 0, 0, []
    yield "cutoff", 2, 0, 1, []
    yield "after-cutoff", 2, 1, 0, [(2,0,0,0)]
    yield "future-invalid", 2, 2, 0, [(1,0,0,2), (2,0,1,0)]
    yield "duplicate", 2, 2, 0, [(1,0,0,0), (1,0,0,0)]
    yield "overflow", 2, 2, 0, [(1,1,2**64-1,2**64-1)]
    for n in (1,2,10,100,MAX_COUNT):
        for shape, row in (("target",(n,0,0)), ("other",(0,n,0)),
                           ("lost",(0,0,n)), ("tied",(n//3,n//3,n-2*(n//3)))):
            for horizon in (0,1,2):
                yield shape,n,2,horizon,[(1,*row),(2,0,0,0)]
        yield "no-exits",n,0,0,[]
    yield "tick-zero",2,0,0,[(0,1,0,0)]
    yield "ten-person",10,2,2,[(1,2,3,0),(2,1,0,0)]
    yield "phase-b-e004",100,2,2,[(1,10,20,0),(2,14,0,0)]
    yield "least-survival",MAX_COUNT,2,2,[(1,0,MAX_COUNT-1,0)]
    yield "least-incidence",MAX_COUNT,2,2,[(1,0,MAX_COUNT-1,0),(2,1,0,0)]
    yield "support-loss-while-positive",MAX_COUNT,3,3,[(1,0,MAX_COUNT-1,0),(2,0,0,1)]

    rng = random.Random(320004)
    for index in range(160):
        count = rng.randint(1,500)
        remaining = count
        rows = []
        for tick in range(rng.choice((2,10,100))):
            d = rng.randrange(remaining+1)
            other = rng.randrange(remaining-d+1)
            lost = rng.randrange(remaining-d-other+1)
            rows.append((tick,d,other,lost))
            remaining -= d+other+lost
        yield "held-out",count,len(rows),rng.randrange(len(rows)+1),rows

    for size in (100, 10000, 1000000):
        rows = [(i, int(i % 3 == 0), int(i % 3 == 1), int(i % 3 == 2))
                for i in range(size)]
        yield "long", MAX_COUNT, size, size, rows
        if size < 1000000:
            yield "long-censor", size+1, size, size, [
                (i, int(i == size-1), 0, int(i < size-1)) for i in range(size)]


def validate(n, cutoff, horizon, rows):
    remaining = n
    after = n
    depleted = None
    terminal = False
    previous = -1
    for tick,d,o,c in rows:
        exits = d+o+c
        if tick <= previous or tick > cutoff or exits > remaining:
            return 1, 0, 0
        if tick <= horizon:
            after = remaining - exits
            if remaining and not after:
                depleted = tick
                terminal = remaining == d+o
        remaining -= exits
        previous = tick
    if horizon > cutoff or (depleted is not None and not terminal and horizon > depleted):
        return 4, 0, 0
    return 0, (0 if after else 1 if terminal else 2), after


def formula(n, horizon, rows, number):
    # Evaluate by event-time factors; censor-only terms are absent from the
    # product. Grouped risk counts are reconstructed in a separate pass.
    def terms():
        exits_before = 0
        for tick,d,o,c in rows:
            if tick > horizon:
                break
            if d+o:
                yield n - exits_before,d,o
            exits_before += d+o+c

    survival, target = number(1), number(0)
    for y,d,o in terms():
        if d:
            target += survival * number(d) / y
        survival *= number(y-d-o) / y
    return survival,target


def decimal_reference(n, horizon, rows, precision):
    with localcontext() as ctx:
        ctx.prec = precision
        return formula(n,horizon,rows,Decimal)


def main():
    # Tracing peak Python heap is an optional separate run. It slows the
    # million-row Decimal passes considerably and is disabled by default.
    if "--memory" in sys.argv:
        tracemalloc.start()
    start = time.perf_counter()
    digest = hashlib.sha256()
    counts, groups = Counter(), Counter()
    max_abs = [0.,0.]
    max_rel = [0.,0.]
    max_width = [0.,0.]
    max_tier_difference = 0.
    for name,n,cutoff,horizon,rows in cases():
        payload = f"{n} {cutoff} {horizon} {len(rows)}\n" + "".join(
            f"{tick} {d} {o} {c}\n" for tick,d,o,c in rows)
        digest.update(payload.encode("ascii"))
        run = subprocess.run([sys.argv[1]], input=payload, text=True, capture_output=True, check=True)
        fields = run.stdout.split()
        status = int(fields[0])
        if n == 0 or n > MAX_COUNT:
            expected, support, after = (2 if n == 0 else 3), 0, 0
        else:
            expected, support, after = validate(n,cutoff,horizon,rows)
        assert status == expected, (name,status,expected)
        counts[str(status)] += 1
        groups[name] += 1
        if status:
            assert fields == [str(status),"1"], (name,fields)
            continue
        assert list(map(int,fields[1:3])) == [support,after]
        if len(rows) <= 100:
            truth = formula(n,horizon,rows,Fraction)
        else:
            coarse = decimal_reference(n,horizon,rows,30)
            fine = decimal_reference(n,horizon,rows,60)
            with localcontext() as ctx:
                ctx.prec = 60
                delta = max(abs(a-b) for a,b in zip(coarse,fine))
                assert delta < Decimal("1e-21"), (name,delta)
            max_tier_difference = max(max_tier_difference,float(delta))
            truth = tuple(map(Fraction,fine))
        m = sum(t <= horizon and d+o > 0 for t,d,o,c in rows)
        gu = Fraction(12*m+8,2**53)
        width_cap = 2*gu/(1-gu)
        for slot,exact in enumerate(truth):
            diagnostic = int(fields[3+4*slot])
            lo,estimate,hi = (Fraction(float.fromhex(x)) for x in fields[4+4*slot:7+4*slot])
            assert 0 <= lo <= estimate <= hi <= 1 and lo <= exact <= hi, (name,slot,fields)
            assert diagnostic == (0 if exact == 0 else 2 if lo == 0 else 1)
            assert hi-lo <= width_cap, (name,slot,float(hi-lo))
            error=abs(estimate-exact)
            max_abs[slot]=max(max_abs[slot],float(error))
            max_width[slot]=max(max_width[slot],float(hi-lo))
            if exact:
                assert exact >= Fraction(1,MAX_COUNT)
                max_rel[slot]=max(max_rel[slot],float(error/exact))
        if name == "ten-person":
            assert truth == (Fraction(2,5),Fraction(3,10))
            assert 1-Fraction(8,10)*Fraction(4,5) == Fraction(36,100)
        if name == "phase-b-e004":
            assert truth[1] == Fraction(24,100)
            assert 1-Fraction(9,10)*Fraction(56,70) == Fraction(28,100)
    evidence = {"input_sha256":digest.hexdigest(),"status_counts":counts,"groups":groups,
                "max_absolute_error_S_F":max_abs,"max_relative_error_S_F":max_rel,
                "max_enclosure_width_S_F":max_width,"max_decimal_tier_difference":max_tier_difference}
    print(json.dumps(evidence,indent=2))
    print(f"elapsed {time.perf_counter()-start:.2f}s", file=sys.stderr)
    if tracemalloc.is_tracing():
        print(f"Python peak traced bytes {tracemalloc.get_traced_memory()[1]}",file=sys.stderr)


if __name__ == "__main__":
    main()
