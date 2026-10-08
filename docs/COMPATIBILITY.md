# Requirements and compatibility

- C11 implementation and headers; C++ linkage guards for callers.
- IEEE-754 binary64 `double`, standard integer types, normal floating environment
  described in [numerical contract](NUMERICAL_CONTRACT.md).
- CMake >=3.16 for supported builds/packages. v1 ships **static-only**;
  `BUILD_SHARED_LIBS` does not create a shared library. No DLL export surface.
- Standard C and libm only. CMake propagates `m` on non-MSVC platforms.
- No runtime Python, SciPy, mpmath, database, UI, filesystem, network,
  environment-variable access, or library heap allocation.
- Odds parsing is ASCII and locale-independent. Runtime does not mutate locale;
  no global/static mutable state. Independent calls are naturally reentrant and
  thread-safe given separate outputs and stable supported floating environments.
  Shared caller buffers still require caller synchronization. No locks added.

Local candidate checks use Windows x64 MinGW GCC 16.2.0. The CI workflow defines
Windows MSVC, Linux GCC, Linux Clang, and macOS AppleClang jobs, plus Linux
GCC ASan/UBSan. A workflow definition is not verification evidence: use the
successful run on the exact candidate commit to establish which jobs passed.
No untested compiler/OS is claimed verified just because source is portable.
MSVC/GCC/Clang warning configuration is retained; fast-math is unsupported.

No operating-system API is used by runtime C. Portability still depends on the
compiler/libm and binary64 requirements; numerical tolerance rather than universal
libm bit identity is the contract. Extreme narrow posterior quantiles have
representable-x limitations; numerical failures are explicit status values.

## Compatibility commitments

Product version macros identify 1.0.0; ABI query identifies generation 1.
Result model/gate/analysis versions are independent and remain 1. Final v1
source/API names and meanings are frozen after release audit. Future changes
must distinguish implementation corrections from model changes and avoid
silently reinterpreting saved versioned results. Incompatible public changes
require an explicit ABI/API compatibility decision, not a struct layout guess.

ABI number 1 is not a promise of one binary layout across compilers, architectures,
or build settings. Rebuild static consumers with compatible headers/toolchains;
never serialize raw struct bytes. See [API persistence guidance](API.md#persistence-and-replay).

No license decision has been supplied; licensing remains unchanged and requires
owner choice. Technical candidate readiness is separate from redistribution
permission and final tag authorization.
