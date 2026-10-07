# ProbSpan

ProbSpan is a portable C extraction and reimplementation of the probability and decision-analysis core originally developed in [RXY712200/probability-calibration-tool](https://github.com/RXY712200/probability-calibration-tool). The v1.0 baseline is frozen at commit `a581f84ccd217ed45789b3566347255f56ffbeac`.

This repository turns that application-internal core into a reusable standalone C module. Version 1.0 intentionally preserves the original behavior; it does not redesign the algorithms.

The C11 library provides the frozen subjective model, odds validation, and Jeffreys historical estimate, including its credible interval and readiness gate. Step 3 adds independent event/complement EV analyses, subjective robust margins, posterior threshold probabilities, odds geometry, and model-relation classification. The committed oracle is used for parity tests.

Extreme large-parameter cases use a separately authorized high-precision numerical reference where frozen SciPy becomes internally inconsistent. This changes evaluation only, not the v1 model. See the [Step 2 developer note](oracle/LARGE_NUMERICS.md).
