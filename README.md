# ProbSpan

**A small deterministic C core for probability uncertainty and decision analysis.**

[![Portable C11 CI](https://github.com/RXY712200/ProbSpan/actions/workflows/ci.yml/badge.svg)](https://github.com/RXY712200/ProbSpan/actions/workflows/ci.yml)

ProbSpan combines an independent **subjective probability**, **historical event counts**, and **gross-return odds** into clearly separated uncertainty estimates, expected-value intervals, threshold probabilities, and model-relationship classifications. It does **not** combine the two probability models into a supposed best estimate, place bets, or make decisions on the caller's behalf.

```text
subjective probability -> subjective uncertainty ----\
                                                  -> EV intervals -> classifications
historical event counts -> Jeffreys posterior ----/        |               |
                                      odds / payoff -------+               |
                                                                  model relationships
```

Version **1.0.0** is the first public contract: C11, static linking, 13 functions, one installed public header, no heavy runtime dependencies. The detailed numerical and behavioral contracts are versioned separately from the library's ABI.

## Capabilities and limits

- **Subjective estimation:** preserves a raw 0–100% input, applies the frozen 1–99% mathematical clamp, and evaluates a defined logit-width uncertainty interval. **This is not a statistical confidence interval.**
- **Historical estimation:** Jeffreys Beta(½,½) posterior, a central 95% credible interval, and an explicit historical-readiness gate. History may be absent, insufficient, or valid.
- **Odds and decisions:** ASCII decimal odds parsing with exact binary64 ties-to-even rounding; event/complement EV intervals; break-even geometry; robust-margin S; odds-combination, interval, and model-relation classifications.
- **Historical decision probabilities:** posterior probability that each side's EV is positive, available only for valid history.
- **Information provenance:** pure, sticky exposure/compromise rules preserving the distinction between independent subjective judgment and evidence-informed revision.
- **Reproducible analysis values:** composition preserves raw inputs, numerical results, availability and independent model/gate/analysis versions. Callers own any storage or replay system.

**Important:** the historical model is not a forecast guarantee, the subjective interval is not a confidence interval, and none of these classifications constitutes a betting, financial, medical, or safety recommendation. The extremely large Beta parameter reference uses separately authorized high-precision calculations because frozen SciPy becomes mathematically inconsistent there; no v1 model formula was changed.

## Build, test, and install

```sh
cmake -S . -B build -DPROBSPAN_BUILD_EXAMPLES=ON
cmake --build build
ctest --test-dir build --output-on-failure
cmake --install build --prefix /path/to/prefix
```

For Visual Studio and other multi-configuration generators, provide `--config Debug` to build/install and `-C Debug` to CTest as applicable. To verify a C-only installation without optional Python fixture checks, configure with `-DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE`.

An installed CMake project consumes the static target as follows:

```cmake
find_package(ProbSpan 1.0 CONFIG REQUIRED)
target_link_libraries(your_app PRIVATE ProbSpan::probspan)
```

Set `CMAKE_PREFIX_PATH` to your chosen install prefix when needed. See [Build and install](docs/BUILD_AND_INSTALL.md) and the [external consumer test](tests/consumer).

## Minimal C example

```c
#include <stdio.h>
#include <probspan/probspan.h>

int main(void) {
    probspan_analysis result;
    probspan_status status = probspan_compose_analysis(60, 19, 1, 2.0, 3.0, &result);
    if (status != PROBSPAN_OK) { return 1; }
    printf("Event EV interval: [%.6f, %.6f]\n",
           result.subjective_analysis.event.ev.minimum,
           result.subjective_analysis.event.ev.maximum);
    if (result.historical_analysis.available) {
        printf("Historical P(EV > 0): %.6f\n",
               result.historical_analysis.event.positive_ev_probability);
    }
    return 0;
}
```

More: [decision example](examples/decision.c) · [provenance example](examples/provenance.c) · [API reference](docs/API.md). Check availability flags before interpreting optional fields; use `probspan_odds_parse` for decimal text instead of writing a second parser.

## Documentation

| Audience | Read |
|---|---|
| Application integrators | [API contract](docs/API.md), [Behavior specification](docs/BEHAVIOR_SPEC.md), [Provenance](docs/PROVENANCE.md) |
| Numerics reviewers | [Numerical contract](docs/NUMERICAL_CONTRACT.md), [Frozen reference methodology](oracle/README.md), [Testing](docs/TESTING.md) |
| C/CMake developers | [Architecture](docs/ARCHITECTURE.md), [Build and install](docs/BUILD_AND_INSTALL.md), [Compatibility](docs/COMPATIBILITY.md), [Contributing](CONTRIBUTING.md) |
| Maintainers | [Origin and scope](docs/ORIGIN_AND_SCOPE.md), [Release procedure](docs/RELEASING.md), [Changelog](CHANGELOG.md), [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1) |

## Compatibility and project boundary

ProbSpan requires C11 and IEEE-754 binary64 `double`, with normal supported floating-point behavior; it uses standard C and libm, not Python, SciPy or mpmath at runtime. The library performs no heap allocation, I/O, network access, locale mutation, or global mutable state management. Exact binary64 odds conversion does **not** imply universal bit-identical libm results. See the [numerical contract](docs/NUMERICAL_CONTRACT.md); fast-math and non-default rounding are outside the full numerical contract.

The library deliberately excludes UI, Round/Session workflow, database, revision counters, timestamps, probability fusion, generic distribution catalogs and calibration scoring. [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1) records this product boundary and future review criterion.

ProbSpan is extracted/reimplemented from the same author's [Probability Calibration Tool](https://github.com/RXY712200/probability-calibration-tool), at frozen source commit `a581f84ccd217ed45789b3566347255f56ffbeac`. This is an implementation of the original model, not a claim of universal probability calibration.

## License

**MIT License** — see [LICENSE](LICENSE). Copyright (c) 2026 RXY712200.
