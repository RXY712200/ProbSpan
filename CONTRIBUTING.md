# Contributing to ProbSpan

ProbSpan is deliberately small: a deterministic C11 core for probability uncertainty, EV/decision classification, and information-provenance semantics. The authoritative product boundary is [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1). Please open an issue explaining the concrete decision-analysis use case before proposing broad features or alternate models.

## Before changing code

1. Identify whether your change is a bug fix, a numerical evaluation correction, a public contract change, or a new mathematical model. These are **not interchangeable**.
2. Keep the original v1 model, Jeffreys prior, odds grammar, policy thresholds, causal ordering and independent version meanings unchanged in a compatible patch.
3. Do not change frozen oracle values to make a test pass. The only authorized exceptional reference method is documented in [Numerical contract](docs/NUMERICAL_CONTRACT.md). Changes to that reference policy need a separate explicit decision and evidence.
4. Prefer small modules with one responsibility, clear comments for non-obvious numerical decisions, and no runtime heavy dependencies, global mutable state or workflow/storage/UI code.

## Local development

```sh
cmake -S . -B build -DPROBSPAN_BUILD_EXAMPLES=ON
cmake --build build
ctest --test-dir build --output-on-failure
cmake --install build --prefix /tmp/probspan-install
cmake -S tests/consumer -B consumer-build -DCMAKE_PREFIX_PATH=/tmp/probspan-install
cmake --build consumer-build
ctest --test-dir consumer-build --output-on-failure
```

Adapt multi-config commands on MSVC. For a pure C build set `-DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE`; Python, SciPy and mpmath are development-only oracle tools. Reference/check commands, tool versions, and precision rules are in [Testing](docs/TESTING.md). Avoid unsafe floating flags such as `-ffast-math`.

## Review expectations

- Explain affected API/ABI/model versions and compatibility implications.
- Include focused edge cases and unchanged-output-on-error tests where applicable.
- State whether exact discrete results, elementary numeric parity, Beta parity, or bit-exact decimal semantics apply.
- Keep changes to [API](docs/API.md), [Behavior specification](docs/BEHAVIOR_SPEC.md), [Numerical contract](docs/NUMERICAL_CONTRACT.md) and examples synchronized.
- Ensure the multi-platform CI passes, including installed consumer and sanitizer job.

New probability distributions, calibration scores, probability fusion, persistence, and workflow machinery are **not** automatically in scope. Please use an issue to discuss any future-version design rather than introducing it through a compatibility patch.

## License

By contributing code or documentation you agree that the contribution is provided under the project's [MIT License](LICENSE), unless a different arrangement is explicitly agreed with the maintainer. Do not paste unlicensed third-party code or large copyrighted reference passages.
