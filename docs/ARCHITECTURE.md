# Architecture

The public contract is `include/probspan/probspan.h`. Only that header is
installed; private headers and numerical primitives are not public APIs.

## Dependency direction

```text
analysis_composition -> estimation / odds / side analysis / relation APIs
subjective_analysis -> decision_geometry / decision_policy / probability_math
historical_analysis -> decision_geometry / decision_policy / history shapes / Beta
historical          -> history shapes / Beta / frozen model parameters
subjective          -> raw validation / probability_math / model parameters
odds                -> private exact decimal converter
provenance          -> raw validation
Beta                -> continued fraction / transformed logit integration
```

No mathematical module depends on provenance or the composer. Provenance
neither changes estimates nor needs odds. Composition delegates and assembles
outputs, without formulas. Development references depend on frozen Python or
mpmath; runtime C never depends on this tooling.

## Responsibilities

| Module | Responsibility |
|---|---|
| `probspan.c` | ABI version query |
| `model_v1.h` | Authoritative frozen behavioral parameters and independent versions |
| `subjective.c` | Raw clamp, piecewise logit width, subjective interval |
| `subjective_input.h` | Shared raw-domain validation without calculating an estimate |
| `probability_math.h` | Frozen quotient-then-log logit |
| `historical.c`, `history_model_private.h` | Jeffreys shapes, posterior estimate, readiness gate |
| `odds.c` | ASCII grammar and gross-odds validation |
| `decimal.c` | Exact decimal midpoint comparison and ties-even encoding |
| `beta.c` | Ordinary CDF/quantile evaluation and numerical strategy selection |
| `gamma.c`, `gamma_private.h` | Positive log-Gamma and shared Stirling remainder without hidden signgam state |
| `beta_logit.c` | Stable transformed integration/quantiles for large shapes |
| `decision_geometry.c` | EV arithmetic, reversed complement bounds, thresholds, shared odds validation |
| `decision_policy.c` | Epsilon branches and independent-model relations |
| `subjective_analysis.c` | Two-sided subjective EV and S availability |
| `historical_analysis.c` | History short-circuit and posterior threshold mass |
| `provenance.c` | Sticky exposure/compromise, old-state causality, state invariant |
| `analysis_composition.c` | Complete versioned value via existing operations |
| `oracle/` | Independent authoritative development references and metadata |
| `tests/` | C-only fixtures, parity, invariants, safety, differential and installed-consumer tests |

Small private seams localize formula, policy, input identity, and numerical
concerns. Iteration/tolerance constants belong to numerical algorithms;
behavioral parameters belong to `model_v1.h`. A solver change does not authorize
changing a model threshold or reference tolerance.

## Boundary and ownership

[Issue #1](https://github.com/RXY712200/ProbSpan/issues/1) limits the library to
the decision pipeline and information-independence meaning. Beta and decimal
machinery exist because this model needs trustworthy posterior evaluation and
input conversion. They are foundations, not public general math catalogs.

Callers own storage, clocks, subject identity, lifecycle, and presentation.
ProbSpan accepts mathematical inputs/explicit facts and returns values without
I/O or allocation. Independent versions let callers preserve historical facts.
There is no singleton, hidden state, lock, automatic migration, or reset policy.

## Execution flow and invariants

`probspan_compose_analysis` is a value composer. It obtains the independent subjective and historical estimates, validates both odds, delegates to the two side analyzers, and classifies each relation. It does not mutate provenance or call a persistence adapter. The caller may separately invoke `probspan_provenance_transition` with observed information-exposure facts.

The **numerical evaluation boundary** is private: Beta functions, gamma normalization, logit integration and decimal midpoint logic cannot be called through the installed public header. This prevents consumers from depending on internal numerical strategies that may legitimately change while the v1 decision contract stays fixed.

**Review checklist for any change:** identify whether it affects (a) formula/branch semantics, (b) a private numerical implementation, (c) API/ABI/source compatibility, or (d) development tooling only. An implementation correction must leave frozen datasets intact unless a separate, explicitly documented high-precision reference exception has been authorized. Avoid broadening the library with unrelated general statistics or application workflow machinery.

Development Python utilities read the frozen source checkout or independent high-precision references. They do not run during installed-library use; generated C fixtures allow the runtime tests to compile without a Python interpreter.
