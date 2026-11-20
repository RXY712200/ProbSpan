# ProbSpanModels 2.0.0

This standalone C11 static package is the D2.1 foundation for the future
ProbSpan v2.0.0 source distribution. Its installed header is
`<probspan_models/version.h>`. It exposes the product string
`PROBSPAN_MODELS_VERSION_STRING` and the compiled ABI query
`ps2_abi_version()`, which returns generation 1. D2.2 provides [fixed-n binomial intervals](API.md). D2.3 adds [explicit Beta update and prediction](API.md#explicit-beta-update-and-batch-prediction). F003–F005 are future work. The legacy package retains its separate version and ABI.

```sh
cmake -S models -B build-models -DCMAKE_BUILD_TYPE=Release
cmake --build build-models --config Release
ctest --test-dir build-models -C Release --output-on-failure
cmake --install build-models --config Release --prefix /path/to/prefix
```

Consumers set CMAKE_PREFIX_PATH to the install prefix and use:

```cmake
find_package(ProbSpanModels 2.0.0 EXACT CONFIG REQUIRED)
target_link_libraries(app PRIVATE ProbSpanModels::models)
```

The archive, public header, and CMake exports can share an install prefix with
ProbSpan 1.1.0. The Models target propagates platform math linkage and has no Python or legacy-package dependency.

Run the repeatable tests from a Git checkout with Python and GCC available:

```powershell
python models/tests/install_matrix.py --cc (Get-Command gcc).Source
```

On Linux use `python3 models/tests/install_matrix.py --generator "Unix Makefiles"`.
The harness prints each command and creates fresh temporary builds and prefixes.
It disables CMake Python discovery and independently compiles the historical
consumer against its original header before linking the current legacy archive
with the same GCC toolchain. This checks compatibility within that architecture
and CRT. Python is used only to orchestrate these tests.
