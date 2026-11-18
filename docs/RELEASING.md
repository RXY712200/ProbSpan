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

## v1.1.0 Stable preparation

The v1.1.0 source distribution includes the optional [device-history reference](PREVIEW_DEVICE_HISTORY.zh-CN.md) in the source distribution. Its product string is `1.1.0` and the eventual Stable tag name is `v1.1.0`. The [published prerelease](https://github.com/RXY712200/ProbSpan/releases/tag/v1.1.0-rc.1) remains historical evidence. The Stable release uses GitHub-generated source ZIP and tar.gz archives with zero uploaded binaries. Publication requires separate approval of the exact final commit. CMake sees numeric package version `1.1.0`. The optional consumer checks both the numeric package version at configure time and the full product string and v1 protocol versions at run time. ABI, model, gate, and analysis versions remain 1. The root install contains the static C package.

Before publication, verify the clean install, both consumers, frozen fixtures, and both CI workflows on the approved full SHA. Relevant `main` pushes trigger optional CI. To replay an existing run, use `gh run rerun <run-id>` after checking its head SHA. An authorized maintainer can bypass path filters after setting `approved_sha` to the full approved commit SHA.

```sh
gh workflow run device-history-preview.yml --ref main -f candidate_sha="$approved_sha"
```

For a manual run, inspect the `Verify tested revision` step. The event SHA identifies the workflow ref and can differ from the checked-out candidate SHA. Record both the run URL and the tested source SHA. Preserve the original v1.0.0 tag and release history.

## Later maintenance

A bug fix that changes numerical evaluation while retaining formulas must preserve discrete decisions and documented tolerances. A change in models, priors, gate conditions, or provenance meaning needs a separately versioned compatibility decision. Adding generic statistics or app workflow does not follow automatically from being a numerical C library: refer to [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1).

Never rebuild saved decision snapshots and present them as if produced by the original version; callers own serialization and must retain model/gate/analysis versions with meaningful fields.
