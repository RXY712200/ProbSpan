# Release checklist and version discipline

This file is maintainer guidance. Tagging and publishing a GitHub Release are separate deliberate actions, performed only after reviewing the exact source commit and successful CI on that commit.

## v1.0.0 source and contract

- Product version: **1.0.0** (`PROBSPAN_VERSION_*` macros and CMake project version).
- ABI version: **1** (`probspan_abi_version()`).
- Independent subjective/history/gate/odds-analysis versions: **1**; they are not product-version aliases.
- [LICENSE](../LICENSE): MIT; preserve attribution in distributions.
- Frozen origin: `RXY712200/probability-calibration-tool` at `a581f84ccd217ed45789b3566347255f56ffbeac`.

## Pre-tag review

1. Confirm current `main` HEAD and inspect its diff against the accepted release candidate.
2. Confirm all public docs and README describe a **released** library rather than an unapproved candidate; verify every documentation link exists and accurately describes the public header.
3. Verify `LICENSE`, `CHANGELOG.md`, CMake version, product version macros, ABI function, and intended tag all agree.
4. Confirm the source reference and all ordinary/corrected high-precision oracle files remain unchanged. Regenerate/check fixtures using [Testing](TESTING.md).
5. Inspect GitHub Actions on the **exact** HEAD: Windows MSVC, Linux GCC, Linux Clang, macOS AppleClang, Linux GCC ASan/UBSan, and installed consumer.
6. Review pending issues: close only completed implementation issues; leave design records and unresolved limitations open with clear scope.
7. Create an annotated tag `v1.0.0` pointing to the verified commit, then publish a GitHub Release using that exact tag and [Changelog](../CHANGELOG.md). Avoid moving an existing public release tag.
8. Verify tag target, Release page, source archives, and links. Record the final SHA and CI run URL.

## Later maintenance

A bug fix that changes numerical evaluation while retaining formulas must preserve discrete decisions and documented tolerances. A change in models, priors, gate conditions, or provenance meaning needs a separately versioned compatibility decision. Adding generic statistics or app workflow does not follow automatically from being a numerical C library: refer to [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1).

Never rebuild saved decision snapshots and present them as if produced by the original version; callers own serialization and must retain model/gate/analysis versions with meaningful fields.
