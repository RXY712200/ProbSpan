# ProbSpan

ProbSpan is a portable C extraction and reimplementation of the probability and decision-analysis core originally developed in [RXY712200/probability-calibration-tool](https://github.com/RXY712200/probability-calibration-tool). The v1.0 baseline is frozen at commit `a581f84ccd217ed45789b3566347255f56ffbeac`.

This repository turns that application-internal core into a reusable standalone C module. Version 1.0 intentionally preserves the original behavior; it does not redesign the algorithms.

The C11 library now provides the frozen subjective model, odds validation, and Jeffreys historical estimate, including its credible interval and readiness gate. The committed oracle is used for parity tests.
