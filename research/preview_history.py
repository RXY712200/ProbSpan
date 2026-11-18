"""Standalone Preview experiment. No ProbSpan runtime or oracle imports."""

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import time
import zipfile
from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from itertools import combinations
from pathlib import Path

import numpy as np
import scipy
from scipy.special import betaincinv, betaln, logsumexp


@dataclass(frozen=True)
class Scenario:
    name: str
    source: tuple[float, float] = (.2, .2)
    target: tuple[float, float] = (.2, .2)
    target_n: tuple[int, int] = (4, 4)
    source_n: tuple[int, int] = (20, 20)  # per group
    weights: tuple[float, float] = (.5, .5)
    relation: str = "common"
    defect: str = ""


SCENARIOS = (
    Scenario("shared"),
    Scenario("shared_zero", target_n=(0, 0)),
    Scenario("heterogeneous", (.15, .45), (.15, .45), relation="exchangeable"),
    Scenario("mix_shift", (.05, .45), (.05, .45), (18, 2), (5, 35), (.9, .1), "stratified"),
    Scenario("missing_support", (.05, .45), (.05, .45), (18, 0), (30, 0), (.9, .1),
             "stratified"),
    Scenario("hidden_conflict", (.1, .1), (.55, .55)),
    Scenario("hidden_conflict_zero", (.1, .1), (.55, .55), (0, 0)),
    Scenario("declared_conflict", (.1, .1), (.55, .55), defect="regime"),
    Scenario("temporal_drift", (.1, .1), (.45, .45), defect="drift"),
    Scenario("overlap", defect="overlap"),
    Scenario("duplicate", defect="copy"),
    Scenario("cluster", defect="cluster"),
    Scenario("outcome_selection", defect="selection"),
    Scenario("incompatible", defect="definition"),
    Scenario("censoring", defect="censoring"),
)
MODELS = ("strict", "pool", "standard", "eb", "hier", "robust", "target_standard")
UNIT = "unit-cycle"
DEFINITION = "failure-within-100h-v1"
HORIZON = 100
GROUPS = 8
THRESHOLDS = (.15, .30, .45)


@dataclass(frozen=True)
class Record:
    record_id: str
    unit_id: str
    role: str
    subject: str
    stratum: int
    cluster: str
    query: str
    revision: str
    definition: str
    unit: str
    horizon: int
    observed_at: int
    regime: str
    sampling: str
    outcome: int | None
    followup: int
    true_probability: float


def generate(case, rng):
    """Three disjoint windows. Evaluation records always use target truth."""
    records = []
    truth = np.array(case.target)
    if case.relation == "exchangeable":
        truth = rng.beta(truth * 12, (1 - truth) * 12)
    for role, day in (("source", 0), ("target", 1), ("evaluation", 2)):
        for h in range(2):
            n = (case.source_n if role == "source" else case.target_n)[h]
            if role == "evaluation":
                n = 160
            for g in range(GROUPS if role == "source" else 1):
                subject = f"{'S' if role == 'source' else 'T'}-{h}-{g}"
                if role == "source" and case.defect == "drift" and g == 0:
                    subject = f"T-{h}-0"
                p = case.source[h] if role == "source" else truth[h]
                if role == "source" and case.relation == "exchangeable":
                    p = rng.beta(p * 12, (1 - p) * 12)
                cluster_case = role == "source" and case.defect == "cluster"
                for i in range(n):
                    # Perfect intracluster dependence is deliberately adversarial.
                    if not cluster_case or i % 5 == 0:
                        y = int(rng.random() < p)
                    key = f"{role}:{subject}:{i}"
                    defect = case.defect if role == "source" else ""
                    if defect == "selection" and y == 0 and rng.random() < .75:
                        continue
                    # Coarsen the binary observation: a shorter inspection
                    # leaves the 100-hour outcome unknown, including some failures.
                    incomplete = defect == "censoring" and i % 2 == 0
                    record = Record(
                        key, key, role, subject, h,
                        f"{subject}:{i // 5}" if cluster_case else key,
                        "A", "snapshot-1", "failure-v0" if defect == "definition" else DEFINITION,
                        UNIT, HORIZON, day * 1000 + i,
                        "old" if defect in {"regime", "drift"} else "current",
                        "outcome-selected" if defect == "selection" else "unselected",
                        None if incomplete else y, 50 if incomplete else HORIZON,
                        float(p),
                    )
                    records.append(record)
                    if defect == "copy" or (defect == "overlap" and i < n // 2):
                        records.append(replace(record, record_id=key + ":B", query="B"))
    return records, truth


def select_source(records):
    """Checks observed metadata. Shared mechanisms need a separate declaration."""
    seen = {}
    for row in records:
        key = row.unit_id
        if key in seen:
            old = seen[key]
            observed = replace(row, record_id=old.record_id, query=old.query,
                               true_probability=old.true_probability)
            if observed != old:
                return None, "identity_conflict"
        seen[key] = row
    rows = list(seen.values())
    if any((r.definition, r.unit, r.horizon) != (DEFINITION, UNIT, HORIZON) for r in rows):
        return None, "definition"
    if any(r.regime != "current" for r in rows):
        return None, "regime"
    if any(r.sampling != "unselected" for r in rows):
        return None, "selection"
    if any(r.outcome is None or r.followup < r.horizon for r in rows):
        return None, "censoring"
    if len({r.cluster for r in rows}) != len(rows):
        return None, "dependence"
    return rows, "eligible"


def counts(rows):
    return sum(r.outcome for r in rows), len(rows)


def beta_result(e, n):
    a, b = e + .5, n - e + .5
    lo, hi = betaincinv(a, b, [.025, .975])
    return np.array([a / (a + b), lo, hi])


def count_binomial(rows, prediction_weights):
    # A stratified design with unequal p generally has a Poisson-binomial sum
    # conditional on allocated counts. Its aggregate Jeffreys fit is a benchmark.
    if not rows or any(w and not any(r.stratum == h for r in rows)
                       for h, w in enumerate(prediction_weights)):
        return None
    return beta_result(*counts(rows))


def hyper_grid(resolution, max_k):
    mu = np.linspace(.01, .99, resolution)
    k = np.geomspace(2, max_k, resolution)
    m, c = np.meshgrid(mu, k)
    return (m * c).ravel(), ((1 - m) * c).ravel()


def stratified_result(source, target, weights, method, rng, draws, grid,
                      robust_weight, cap):
    marginal = np.zeros(draws)
    mean = 0.
    aa, bb = grid
    for h, weight in enumerate(weights):
        if weight == 0:
            continue
        hist = [r for r in source if r.stratum == h]
        cur = [r for r in target if r.stratum == h]
        event, n = counts(cur)
        successes, size = counts(hist)
        if method == "standard":
            if not size + n:
                return None
            a, b = successes + event + .5, size + n - successes - event + .5
            estimate = a / (a + b)
            sample = rng.beta(a, b, draws)
        elif method == "robust":
            if not size:
                return None
            m = (successes + .5) / (size + 1)
            # Plug-in source prior paired with a weak component. This is a
            # capped mixture sensitivity experiment, not a fitted MAP prior.
            effective = min(cap, size)
            a = np.array([m * effective, .5])
            b = np.array([(1 - m) * effective, .5])
            log_mass = np.log([1 - robust_weight, robust_weight])
            log_mass += betaln(a + event, b + n - event) - betaln(a, b)
            a, b = a + event, b + n - event
            mass = np.exp(log_mass - logsumexp(log_mass))
            estimate = mass @ (a / (a + b))
            choice = rng.choice(2, size=draws, p=mass)
            sample = rng.beta(a[choice], b[choice])
        else:
            groups = defaultdict(list)
            for row in hist:
                groups[row.subject].append(row)
            if len(groups) < 2:
                return None
            log_mass = np.zeros(len(aa))
            log_beta = betaln(aa, bb)
            for rows in groups.values():
                e, k = counts(rows)
                log_mass += betaln(aa + e, bb + k - e) - log_beta
            a, b = aa + event, bb + n - event
            if method == "eb":
                best = log_mass.argmax()
                estimate = a[best] / (a[best] + b[best])
                sample = rng.beta(a[best], b[best], draws)
            else:
                # A uniform discrete prior in (mu, log k). Target evidence
                # updates the hyperparameters as well as its own group risk.
                log_mass += betaln(a, b) - log_beta
                mass = np.exp(log_mass - logsumexp(log_mass))
                estimate = mass @ (a / (a + b))
                choice = rng.choice(len(aa), size=draws, p=mass)
                sample = rng.beta(a[choice], b[choice])
        mean += weight * estimate
        marginal += weight * sample
    return np.array([mean, *np.quantile(marginal, [.025, .975])])


def analyze(case, source, target, model, forced, rng, config, grid):
    if model == "strict":
        # Require the observed target allocation to match the estimand's mix.
        # Known heterogeneous strata need a defined conditional likelihood.
        if (case.relation != "common" and not forced) or not target:
            return None
        return count_binomial(target, case.weights)
    if model == "target_standard":
        return stratified_result([], target, case.weights, "standard", rng, config.draws,
                                 grid, config.weak_weight, config.cap)
    if source is None:
        return None
    if not forced and model == "pool" and case.relation != "common":
        return None
    if not forced and model == "standard" and case.relation == "exchangeable":
        return None
    if not forced and model in {"eb", "hier", "robust"} and case.relation == "stratified":
        return None
    if model == "pool":
        return count_binomial(source + target, case.weights)
    return stratified_result(source, target, case.weights, model, rng, config.draws, grid,
                             config.weak_weight, config.cap)


def loss_record(result, truth, eval_rate):
    mean, lower, upper = result
    assert 0 < mean < 1 and 0 <= lower <= upper <= 1
    metrics = dict(bias=mean-truth, abs_error=abs(mean-truth),
                   brier=eval_rate*(1-mean)**2+(1-eval_rate)*mean**2,
                   log_loss=-eval_rate*math.log(mean)-(1-eval_rate)*math.log1p(-mean),
                   cover=float(lower <= truth <= upper), width=upper-lower)
    for t in THRESHOLDS:
        label = f"{t:.2f}"
        metrics["wrong_" + label] = float((mean > t) != (truth > t))
        metrics["regret_" + label] = abs(truth-t) * metrics["wrong_" + label]
        metrics["false_certainty_" + label] = float(
            (lower > t and truth <= t) or (upper < t and truth > t))
    return metrics


def run(case, config, grid):
    totals = defaultdict(list)
    reasons = defaultdict(int)
    first = None
    for i in range(config.reps):
        # Case order, posterior simulation and sensitivities cannot affect data.
        seed = [config.seed, SCENARIOS.index(case), i]
        rows, truth_by_stratum = generate(case, np.random.default_rng(seed))
        first = rows if first is None else first
        raw = [r for r in rows if r.role == "source"]
        target = [r for r in rows if r.role == "target"]
        test = [r for r in rows if r.role == "evaluation"]
        assert not ({r.unit_id for r in test} & {r.unit_id for r in raw + target})
        assert max((r.observed_at for r in raw + target), default=-1) < min(
            r.observed_at for r in test)
        clean, reason = select_source(raw)
        reasons[reason] += 1
        truth = float(np.dot(case.weights, truth_by_stratum))
        eval_rate = sum(w * np.mean([r.outcome for r in test if r.stratum == h])
                        for h, w in enumerate(case.weights))
        for mode, source in (("admitted", clean), ("bypass", [
                replace(r, outcome=0) if r.outcome is None else r for r in raw])):
            for j, model in enumerate(MODELS):
                rng = np.random.default_rng([*seed, j, 971])
                result = analyze(case, source, target, model, mode == "bypass", rng, config, grid)
                totals[mode, model].append(None if result is None else loss_record(
                    result, truth, eval_rate))
    for (mode, model), results in totals.items():
        actual = [m for m in results if m is not None]
        summary = {k: float(np.mean([m[k] for m in actual])) for k in actual[0]} if actual else {}
        # Derive an illustrative combined cost without assuming a production cost.
        # An abstention cost C adds C*(1-available/reps) to this unconditional loss.
        summary["unconditional_regret_0.30"] = sum(m["regret_0.30"] for m in actual)/config.reps
        yield dict(case=case.name, mode=mode, model=model, available=len(actual),
                   reps=config.reps, source_reasons=dict(reasons), **summary), first


def verify_math():
    # Independent integer-factorial CDFs for Beta(2, 3) and Beta(1, 1).
    def cdf(x):
        return sum(math.comb(4, j)*x**j*(1-x)**(4-j) for j in range(2, 5))
    for p in (.025, .975):
        assert abs(cdf(betaincinv(2, 3, p))-p) < 1e-14
    assert abs(beta_result(0, 1)[0] - .25) < 1e-15
    assert np.allclose(betaincinv(1, 1, [.025, .975]), [.025, .975])
    for n, expected in ((0, 1/5), (1, 5/9), (5, 1001/1013)):
        mass = np.array([.8, .2]) * np.exp(
            betaln([9, 1], np.array([1, 1])+n)-betaln([9, 1], [1, 1]))
        assert abs(mass[1]/sum(mass)-expected) < 1e-14
    for case in SCENARIOS:
        rows, _ = generate(case, np.random.default_rng(3))
        source = [r for r in rows if r.role == "source"]
        clean, reason = select_source(source)
        if case.defect in {"overlap", "copy"}:
            assert reason == "eligible" and len(clean) < len(source)
            corrupted = replace(source[0], outcome=1-source[0].outcome)
            assert select_source([*source, corrupted])[1] == "identity_conflict"
        if case.defect in {"selection", "cluster", "definition", "censoring", "regime", "drift"}:
            assert clean is None, case.name


def inspect_wine(path):
    """Descriptive audit only. Equal text rows prove neither shared nor distinct units."""
    with zipfile.ZipFile(path) as archive:
        files = {}
        for kind in ("red", "white"):
            payload = archive.read(f"winequality-{kind}.csv")
            reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter=";")
            rows = list(reader)
            files[kind] = dict(records=len(rows), label_ge_7=sum(int(r["quality"]) >= 7 for r in rows),
                               equal_row_excess=len(rows)-len({tuple(r.values()) for r in rows}),
                               sha256=hashlib.sha256(payload).hexdigest())
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=902618)
    parser.add_argument("--reps", type=int, default=320)
    parser.add_argument("--draws", type=int, default=4096)
    parser.add_argument("--grid", type=int, default=25)
    parser.add_argument("--max-k", type=float, default=128)
    parser.add_argument("--weak-weight", type=float, default=.2)
    parser.add_argument("--cap", type=float, default=20)
    parser.add_argument("--case", choices=[c.name for c in SCENARIOS], action="append")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, help="Write first replicate of each case as JSONL")
    parser.add_argument("--wine-zip", type=Path)
    config = parser.parse_args()
    if (not 0 < config.weak_weight < 1 or min(config.reps, config.draws) < 1
            or config.grid < 3 or config.max_k <= 2 or config.cap <= 0 or config.seed < 0):
        parser.error("Invalid simulation configuration")
    verify_math()
    tick = time.perf_counter()
    grid = hyper_grid(config.grid, config.max_k)
    results = []
    fixtures = {}
    for case in SCENARIOS:
        if not config.case or case.name in config.case:
            for result, first in run(case, config, grid):
                results.append(result)
                fixtures[case.name] = first
    if config.fixture:
        with config.fixture.open("x", encoding="utf-8") as stream:
            for case, first in fixtures.items():
                for row in first:
                    stream.write(json.dumps({"case": case, **asdict(row)}) + "\n")
    parameters = {k: v for k, v in vars(config).items() if not isinstance(v, Path)}
    payload = dict(config=parameters, python=platform.python_version(), numpy=np.__version__,
                   scipy=scipy.__version__, results=results)
    if config.wine_zip:
        payload["descriptive_wine_audit"] = inspect_wine(config.wine_zip)
    with config.output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(f"Wrote {len(results)} result cells in {time.perf_counter()-tick:.2f}s")


if __name__ == "__main__":
    main()
