"""Synthetic 100-hour device histories. Run from the ProbSpan checkout."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path as FilePath

from .evidence import (Applicability, Assumption, Batch, Declaration,
                       Observation, Path, Scope, review)
from .standardization import standardize
from .v1 import estimate_v1


def device_batch(population, events_and_totals):
    scope = Scope(population, "synthetic-snapshot", "1", "process-A", "fixed-load-A")
    rows = []
    for stratum, (events, total) in zip(("low", "high"), events_and_totals):
        for i in range(total):
            device = f"{population}-{stratum}-{i}"
            rows.append(Observation(device, "cycle-1", device, "query-A", stratum,
                                    0, 100, 100, i < events,
                                    scope.process_version, scope.conditions))
    return Batch(scope, tuple(rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consumer", type=FilePath)
    args = parser.parse_args()
    target = device_batch("target", [(19, 20), (0, 0)])
    source = device_batch("source", [(10, 10), (0, 0)])
    strict = review(Path.STRICT, target, Declaration(
        Applicability.SUPPORTED, Assumption.TARGET_SHARED, "synthetic-shared-p"), cutoff_hour=100)
    pooled = review(Path.POOL, target, Declaration(
        Applicability.SUPPORTED, Assumption.SOURCE_TARGET_SHARED, "synthetic-shared-p"),
        cutoff_hour=100, source=source)
    weighted = review(Path.STANDARD, device_batch("target", [(2, 20), (9, 20)]), Declaration(
        Applicability.SUPPORTED, Assumption.TARGET_STRATIFIED, "synthetic-fixed-strata"),
        cutoff_hour=100, weights=(.8, .2))
    results = (estimate_v1(strict, args.consumer), estimate_v1(pooled, args.consumer),
               standardize(weighted))
    print(json.dumps([asdict(x) for x in results], indent=2, allow_nan=False))
    return any(x.status != "ok" for x in results)


if __name__ == "__main__":
    raise SystemExit(main())
