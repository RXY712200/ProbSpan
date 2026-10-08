# ProbSpan

**A small deterministic C core for probability uncertainty and decision analysis.**

ProbSpan turns an independent subjective probability, historical event counts, and gross-return odds into uncertainty intervals, expected-value intervals, classifications, and relationships between the two models. It never produces a fused or recommended probability.

```text
Probability -> Uncertainty -> Historical evidence -> Odds / payoff
            -> EV interval -> Classification -> Model relationship
```

Version 1.0.0 is a release candidate pending independent final audit. No release tag or GitHub Release is created by this candidate.

## Capabilities

- Frozen subjective uncertainty and Jeffreys posterior with a central 95% interval and readiness gate.
- Locale-independent ASCII odds parsing with exact decimal-to-binary64 rounding.
- Event/complement EV bounds, robust margins, break-even geometry, posterior threshold probabilities, and discrete classifications.
- Pure evidence-exposure/independence provenance and complete versioned analysis values for caller-owned storage.
- Committed frozen-reference fixtures and separately authorized high-precision references for inconsistent extreme SciPy results.

Portable C11, static library, IEEE-754 binary64 `double`, standard C/libm only. No runtime Python, database, UI, filesystem, network, heap allocation, or mutable global state. Determinism means a defined numerical contract and exact policy branches, not identical libm bits on every platform.

## Build

```sh
cmake -S . -B build -DPROBSPAN_BUILD_EXAMPLES=ON
cmake --build build
ctest --test-dir build --output-on-failure
cmake --install build --prefix /your/prefix
```

Multi-configuration generators need `--config Debug` for build/install and `-C Debug` for CTest. Installed users link `ProbSpan::probspan` after `find_package(ProbSpan CONFIG REQUIRED)`.

## Use

```c
#include <probspan/probspan.h>

probspan_analysis result;
if (probspan_compose_analysis(60, 19, 1, 2.0, 3.0, &result) == PROBSPAN_OK) {
    double minimum = result.subjective_analysis.event.ev.minimum;
    /* Read historical sides only if historical_analysis.available. */
    (void)minimum;
}
```

Complete examples: [decision](examples/decision.c), [provenance](examples/provenance.c).

## Documentation

| Subject | Document |
|---|---|
| Public types, fields, functions, errors | [API](docs/API.md) |
| Frozen formulas and boundaries | [Behavior specification](docs/BEHAVIOR_SPEC.md) |
| Exact guarantees, tolerances, large-count exception | [Numerical contract](docs/NUMERICAL_CONTRACT.md) |
| Exposure and independence | [Provenance](docs/PROVENANCE.md) |
| Responsibilities and dependencies | [Architecture](docs/ARCHITECTURE.md) |
| Build, install, external consumption | [Build and install](docs/BUILD_AND_INSTALL.md) |
| Tests and reference regeneration | [Testing](docs/TESTING.md) |
| Requirements and compatibility | [Compatibility](docs/COMPATIBILITY.md) |
| Extraction and product boundary | [Origin and scope](docs/ORIGIN_AND_SCOPE.md) |
| First-version candidate changes | [Changelog](CHANGELOG.md) |

## Origin and scope

Extracted/reimplemented from the author's own [Probability Calibration Tool](https://github.com/RXY712200/probability-calibration-tool), frozen at `a581f84ccd217ed45789b3566347255f56ffbeac`. v1 preserves behavioral semantics rather than redesigning algorithms. The extreme-parameter numerical exception is documented explicitly.

[Issue #1](https://github.com/RXY712200/ProbSpan/issues/1) defines the long-term boundary. Workflow, storage, clocks, and presentation belong to callers. v1 excludes statistical score/calibration APIs, distribution catalogs, machine learning, alternative priors, and probability fusion.

No license has been selected or added. The owner must choose licensing before licensed redistribution can be assumed.
