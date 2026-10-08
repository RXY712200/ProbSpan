# Changelog

This file tracks published source/API contracts and significant compatibility corrections. Experimental fixture and reference changes do not implicitly create new model versions.

## 1.0.0 — 2026-10-08

First stable public source/API contract. See [the API reference](docs/API.md), [numerical contract](docs/NUMERICAL_CONTRACT.md) and [release procedure](docs/RELEASING.md).

- Extracted/reimplemented the author's frozen Probability Calibration Tool
  behavior at `a581f84ccd217ed45789b3566347255f56ffbeac` in portable C11.
- Subjective model, Jeffreys posterior, central credible interval, readiness gate.
- ASCII odds grammar and exact locale/rounding-mode-independent binary64
  decimal conversion, round-to-nearest ties-to-even.
- Independent event/complement EV intervals, robust margins, thresholds,
  odds-combination classifications, posterior threshold probabilities, relations.
- Authorized large-parameter numerical evaluation/reference corrections for
  demonstrably inconsistent frozen SciPy output; model formulas unchanged.
- Pure sticky provenance with old-exposure causality, raw identity, and rejection
  of unreachable compromised-without-exposure states.
- Complete versioned analysis value composition and explicit availability.
- Product version macros for 1.0.0 and ABI version 1.
- Reentrancy audit fix: private positive log-Gamma evaluation avoids libm's
  potentially shared signgam state; unchanged reference/tolerance parity required.
- Portability audit fix: positive-zero decimal reconstruction is explicit under
  downward rounding; Linux Clang exposed a signed-zero conversion artifact.
- Static-library install/export package `ProbSpan::probspan`, public examples,
  installed external consumer, and focused compiler/platform/sanitizer CI.
- Frozen-reference, corrected high-precision, bit-exact decimal, safety,
  composition, fixture freshness, stress, warning/static-analysis tests and docs.

No earlier ProbSpan releases are implied. The source is distributed under the MIT License; no runtime workflow, persistence, clock, or probability fusion is included.
