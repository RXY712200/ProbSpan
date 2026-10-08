# Changelog

## 1.0.0 — release candidate — 2026-10-08

Intended first-version date: 2026-10-08. Final release sealing remains pending
independent audit; this entry does not assert that a tag/release was published.

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
- Static-library install/export package `ProbSpan::probspan`, public examples,
  installed external consumer, and focused compiler/platform/sanitizer CI.
- Frozen-reference, corrected high-precision, bit-exact decimal, safety,
  composition, fixture freshness, stress, warning/static-analysis tests and docs.

No earlier ProbSpan releases are implied. Licensing is unchanged; owner choice
is required. No runtime workflow, persistence, clock, or probability fusion.
