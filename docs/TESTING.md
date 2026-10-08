# Testing and authoritative references

## C-only tests

Configure/build/CTest from a fresh directory as in [build guide](BUILD_AND_INSTALL.md).
Committed fixtures contain expected values; no Python is needed to run C tests.
When Python is discovered, five fixture freshness tests are additionally registered.
With examples ON, two example executables are additionally tested.

| Test | Coverage |
|---|---|
| smoke | ABI and basic library use |
| api_contract | Product/ABI/model versions, NULL/status precedence, invalid enum/raw/count/odds, unchanged errors, availability, malformed provenance including in-place output |
| oracle_parity | 163 ordinary estimate/width/history/odds/domain vectors and 25 constants |
| large_numerics | 28 corrected histories, 140 CDF probes; 190 history stress cases, 570 quantiles, 950 primary CDF evaluations through INT64_MAX, bracket/complement/inverse invariants |
| decimal_parity | 41 exact-bit vectors, four rounding modes, comma locale; stdin mode for differential corpus |
| analysis_parity | 742 subjective, 166 ordinary history, 18 corrected threshold cases; 22 EV, 33 combination, 12 relation cases, safety and S-boundary checks |
| state_parity | 23 frozen provenance observations, in-place transitions, 926 composed results compared field by field with individual APIs, failure safety |
| installed consumer | Public-only find_package/imported-target consumption from installed prefix |

Fixtures and references from accepted Steps 1–4 are preserved. Discrete values
must match exactly; numeric tolerances remain in `oracle/numerical_policy.json`.
Do not regenerate oracle values from C or change expectations to fit a failure.

## Exact development tools

Local candidate environment: Windows x64, GCC 16.2.0 (MSYS2 UCRT64), CMake 4.4.4,
Python 3.13.14, SciPy 1.18.1 in frozen reference environment, mpmath 1.3.0,
Ruff 0.16.10, uv 0.11.29. Installed consumers require only CMake/compiler,
not these development Python tools. CI runner compiler versions are reported
in each workflow configure log; use actual successful run logs for evidence.

## Frozen reference regeneration

Create a detached source checkout at exactly
`a581f84ccd217ed45789b3566347255f56ffbeac` with its development dependencies.
Generators check SHA and tracked cleanliness before importing that project's
`src`. Run the following in its environment, with absolute ProbSpan script paths
if the working directory is the frozen checkout:

```text
python oracle/generate.py --reference-root <frozen-checkout> --check
python oracle/generate_decimal.py --reference-root <frozen-checkout> --check
python oracle/generate_analysis.py --reference-root <frozen-checkout> --check
python oracle/generate_state.py --reference-root <frozen-checkout> --check
```

These verify original `v1_vectors.jsonl` (244 rows), exact decimal data (41),
Step 3 additions (920), and portable state observations (23). The state generator
executes isolated frozen application transitions only during development and
projects portable facts; no application runtime code enters the C library.

Relevant frozen regression suite:

```text
pytest tests/unit/core tests/integration/application/test_calculate.py tests/integration/application/test_recalculate.py tests/integration/application/test_revision_lock.py -q
```

## Corrected independent high-precision references

```text
uv run --with mpmath==1.3.0 python oracle/generate_large.py --check
uv run --with mpmath==1.3.0 python oracle/generate_large.py --verify-precision
uv run --with mpmath==1.3.0 python oracle/generate_threshold.py --reference-root <frozen-checkout> --check
```

80-digit generation checks all committed large historical and threshold
references. Separate 60-digit generation compares historical means, interval
bounds, and CDF expectations after binary64 rounding. Method, argument
representation, evidence of SciPy breakdown, and the unchanged numerical policy
are detailed in [numerical contract](NUMERICAL_CONTRACT.md). Threshold generation
executes frozen EV/gate code with only inconsistent numerical evaluators replaced
by independent high-precision values.

## Fixtures and exact decimal differential

From ProbSpan root:

```text
python tests/generate_fixtures.py --check
python tests/generate_large_fixtures.py --check
python tests/generate_decimal_fixtures.py --check
python tests/generate_analysis_fixtures.py --check
python tests/generate_state_fixtures.py --check
```

In the frozen reference environment:

```text
python tests/decimal_differential.py --reference-root <frozen-checkout> --executable <absolute-built-decimal-parity-executable>
```

The fixed-seed corpus has 6,099 cases, including remote midpoint perturbations
and 100,000-digit patterns; expectations execute the frozen parser and Python
conversion, not the C parser. Runtime parser allocation is still bounded by
midpoint representation rather than input length.

## Quality, portability, and sanitizer evidence

Local strong checks compile runtime/new tests/examples with C11, `-Wall -Wextra
-Wpedantic -Wconversion -Wshadow -Wstrict-prototypes -Werror -fanalyzer`.
Unchanged legacy oracle/smoke tests omit only Wconversion due existing count
conversions; they retain other warnings and static analysis. Python checks:

```text
ruff check --isolated --line-length 100 --target-version py313 oracle tests
ruff format --isolated --line-length 100 --target-version py313 --check oracle tests
```

The focused CI matrix configures, builds, tests, installs, and runs an external
consumer on Windows MSVC, Linux GCC/Clang, macOS AppleClang, plus Linux GCC with
ASan/UBSan. Local MinGW cannot link ASan/UBSan because runtime libraries are
absent; successful Linux sanitizer CI is required candidate evidence.
Never mark portability/sanitizers passed from workflow YAML alone, and never
suppress a finding or remove a failing platform to conceal a defect.

Final audit also inspects runtime allocation, globals, locale/I/O/environment
access, public application leakage, exported package paths, and unchanged
accepted reference/test data. Release approval requires review of the exact tagged commit and successful CI on that same commit. A green workflow does not substitute for verifying the model/fixture contracts, external consumer, or release metadata. See [the release checklist](RELEASING.md).

## Release evidence and review workflow

Release work should keep a reproducible trail: the final source SHA, a successful CI run on that exact SHA, the unchanged authoritative reference blobs, and the final docs/license/version status. The portable CI workflow is [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). It exercises five jobs: Windows MSVC, Linux GCC, Linux Clang, macOS AppleClang and Linux GCC with ASan/UBSan. The installed consumer test verifies that only public installed headers and the exported CMake package are needed.

**Triage when a job fails:** (1) reproduce its configure/build command; (2) identify whether behavior or a compiler/ABI/locale assumption differs; (3) check discrete states separately from elementary and Beta tolerances; (4) preserve all frozen datasets; (5) repair source or platform integration rather than removing the failing target. If frozen SciPy is internally inconsistent in an extreme numeric region, follow the separately documented high-precision reference exception—not a silent oracle overwrite.

For contributions, follow [CONTRIBUTING.md](../CONTRIBUTING.md). For tagging and a GitHub Release, follow [RELEASING.md](RELEASING.md).
