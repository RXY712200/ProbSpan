# Build, install, and consume

Requires C11/binary64, CMake >=3.16, compiler, and build tool. Runtime needs no
Python; Python is optional for checking committed fixture freshness.

## Clean checkout

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Options: `BUILD_TESTING=ON` by default; `PROBSPAN_BUILD_EXAMPLES=OFF` by default.
Set the latter ON to compile/run the two simple public-API examples under CTest.
Set `CMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE` for a C-only validation; every
runtime parity/contract test consumes committed C fixtures without Python.

Multi-configuration generators (Visual Studio) need `cmake --build build
--config Debug`, `ctest --test-dir build -C Debug`, and `cmake --install build
--config Debug`. Single-configuration generators select optimization with
`-DCMAKE_BUILD_TYPE=Debug` or Release at configure time. Unsafe floating flags
are unsupported; preserve the [numerical environment](NUMERICAL_CONTRACT.md).

Windows MinGW example from a terminal containing the compiler/build tool:

```sh
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_C_COMPILER=gcc
cmake --build build
ctest --test-dir build --output-on-failure
```

The library is deliberately static-only. Installed artifacts are the archive,
`include/probspan/probspan.h`, and package/target/version files in
`${CMAKE_INSTALL_LIBDIR}/cmake/ProbSpan`; GNUInstallDirs permits conventional
prefix/layout overrides. No private numerical headers are installed.

## Installed external project

```sh
cmake --install build --prefix /absolute/probspan-prefix
cmake -S tests/consumer -B consumer-build -DCMAKE_PREFIX_PATH=/absolute/probspan-prefix
cmake --build consumer-build
ctest --test-dir consumer-build --output-on-failure
```

Consumer CMake:

```cmake
find_package(ProbSpan 1.0 CONFIG REQUIRED)
add_executable(app main.c)
target_link_libraries(app PRIVATE ProbSpan::probspan)
```

The imported target supplies the installed include directory, C11 feature, archive,
and required math linkage. Version config permits compatible same-major requests.
No source include directory is embedded in exported targets. The committed
consumer test uses only `<probspan/probspan.h>` and the installed package; it
neither adds source-tree include paths nor includes ProbSpan via add_subdirectory.
Consumers using add_subdirectory may also link the build-tree alias
`ProbSpan::probspan`, but that is a different consumption path.

For CI ASan/UBSan, configure C and executable linker flags with
`-fsanitize=address,undefined -fno-omit-frame-pointer` on a supporting toolchain,
and give the installed consumer the corresponding sanitizer linkage. Local
MinGW lacks these runtime libraries; the Linux sanitizer job supplies coverage.
