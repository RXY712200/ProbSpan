# Release checklist and version discipline

This file is maintainer guidance. Tagging and publishing a GitHub Release are separate deliberate actions, performed only after reviewing the exact source commit and successful CI on that commit.

## v1.0.0 source and contract

- Product version: **1.0.0** (`PROBSPAN_VERSION_*` macros and CMake project version).
- ABI version: **1** (`probspan_abi_version()`).
- Independent subjective/history/gate/odds-analysis versions: **1**; they are not product-version aliases.
- [LICENSE](../LICENSE): MIT; preserve attribution in distributions.
- Frozen origin: `RXY712200/probability-calibration-tool` at `a581f84ccd217ed45789b3566347255f56ffbeac`.

## Historical v1.0.0 pre-tag review

1. Confirm current `main` HEAD and inspect its diff against the accepted release candidate.
2. Confirm all public docs and README describe a **released** library rather than an unapproved candidate; verify every documentation link exists and accurately describes the public header.
3. Verify `LICENSE`, `CHANGELOG.md`, CMake version, product version macros, ABI function, and intended tag all agree.
4. Confirm the source reference and all ordinary/corrected high-precision oracle files remain unchanged. Regenerate/check fixtures using [Testing](TESTING.md).
5. Inspect GitHub Actions on the **exact** HEAD: Windows MSVC, Linux GCC, Linux Clang, macOS AppleClang, Linux GCC ASan/UBSan, and installed consumer.
6. Review pending issues: close only completed implementation issues; leave design records and unresolved limitations open with clear scope.
7. Create an annotated tag `v1.0.0` pointing to the verified commit, then publish a GitHub Release using that exact tag and [Changelog](../CHANGELOG.md). Avoid moving an existing public release tag.
8. Verify tag target, Release page, source archives, and links. Record the final SHA and CI run URL.

## Stabilization recommendation for the next candidate

The current review evaluates the merged source from Preview Phases I–III.
The frozen C model, ABI and 13 public C operations retain their v1 contract.
The optional [device-history reference](PREVIEW_DEVICE_HISTORY.zh-CN.md)
adds separately testable source-level functionality and its own Python
dependencies. Root installation still exports only the static C package.
The [candidate inventory and test evidence](IMPLEMENTATION_VALIDATION.zh-CN.md#preview-device-history-validation)
separate the installed product from source-tree research, examples and
integrations.

Recommendation for the owner's decision: use `v1.1.0-rc.1` for a single
evaluation if the optional reference is explicitly included in the next
minor product release as a Preview integration. This communicates the
additive source distribution capability without changing ABI or model/gate
versions. It does not revive the unapproved database-facing proposal.
If the owner elects to leave the reference solely as repository material,
this stabilization alone does not justify a new C library release.
See [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Before any separately authorized publication, decide the intended
artifact contents, compatibility claim and prerelease labeling. Then
reconcile the numeric CMake project/package version, product-version
header macros and string, changelog, exact-version assertions, C consumer
CMake requirement and its Python product-version check. In this review the
consumer intentionally requires **exactly 1.0.0**, so changing only the
root product version would break that build and protocol. Decide whether
future reference tests pin a separate v1.0.0 installation or use the new
package with an explicitly verified compatibility check. Rerun installation
and both CI workflows on the approved final artifact commit. Keep the
original v1.0.0 tag and release history. The present review still reports
1.0.0 metadata and is a candidate for evaluation ahead of a version decision.

## Later maintenance

A bug fix that changes numerical evaluation while retaining formulas must preserve discrete decisions and documented tolerances. A change in models, priors, gate conditions, or provenance meaning needs a separately versioned compatibility decision. Adding generic statistics or app workflow does not follow automatically from being a numerical C library: refer to [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1).

Never rebuild saved decision snapshots and present them as if produced by the original version; callers own serialization and must retain model/gate/analysis versions with meaningful fields.
