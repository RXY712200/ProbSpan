"""Run isolated Release builds and installed-package checks with one GCC toolchain."""

import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
STABLE = "46ff21847c5522eb983d3f58e396354461a64f34"


def run(*args, expected_error=None):
    command = [str(arg) for arg in args]
    print(subprocess.list2cmdline(command), flush=True)
    if expected_error is None:
        subprocess.run(command, check=True)
        return
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, errors="replace", check=False)
    if result.returncode == 0 or any(term not in result.stdout for term in expected_error):
        raise RuntimeError(result.stdout)
    print(result.stdout, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator", default="MinGW Makefiles")
    parser.add_argument("--cc", default="gcc")
    args = parser.parse_args()
    run(args.cc, "--version")
    run("cmake", "--version")
    with tempfile.TemporaryDirectory(prefix="ps21-") as directory:
        space = Path(directory)

        def configure(source, build, *options, expected_error=None):
            run("cmake", "-S", source, "-B", build, "-G", args.generator,
                f"-DCMAKE_C_COMPILER={args.cc}", "-DCMAKE_BUILD_TYPE=Release",
                "-DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE", *options,
                expected_error=expected_error)

        def build_test(build):
            run("cmake", "--build", build, "--config", "Release", "--parallel", "4")
            run("ctest", "--test-dir", build, "-C", "Release", "--output-on-failure")

        legacy = space / "legacy"
        models = space / "models"
        configure(ROOT, legacy, "-DPROBSPAN_BUILD_EXAMPLES=ON", "-DCMAKE_INSTALL_LIBDIR=lib")
        build_test(legacy)
        configure(ROOT / "models", models, "-DCMAKE_INSTALL_LIBDIR=lib")
        build_test(models)

        def install(build, prefix):
            run("cmake", "--install", build, "--config", "Release", "--prefix", prefix)
            lines = (build / "install_manifest.txt").read_text(encoding="utf-8").splitlines()
            paths = {Path(line).resolve().relative_to(prefix.resolve()).as_posix() for line in lines}
            if len(paths) != len(lines):
                raise RuntimeError("Duplicate install manifest entry")
            return paths

        def consumer(name, prefix, *options, error=None):
            build = space / name
            configure(ROOT / "models/tests/consumer", build, f"-DD21_PREFIX={prefix.as_posix()}",
                      *options, expected_error=error)
            if error is None:
                build_test(build)

        legacy_only = space / "legacy-prefix"
        models_only = space / "models-prefix"
        legacy_files = install(legacy, legacy_only)
        models_files = install(models, models_only)
        expected = {
            "include/probspan_models/version.h", "include/probspan_models/binomial_interval.h",
            "include/probspan_models/beta_predict.h", "lib/libprobspan_models.a",
            *(f"lib/cmake/ProbSpanModels/ProbSpanModels{name}.cmake"
              for name in ("Config", "ConfigVersion", "Targets", "Targets-release")),
        }
        if models_files != expected or models_files & legacy_files:
            raise RuntimeError(f"Unexpected install manifest: {models_files}")

        legacy_exact = ("-DUSE_LEGACY=ON", "-DLEGACY_REQUEST=1.1.0", "-DLEGACY_EXACT=ON")
        models_exact = ("-DUSE_MODELS=ON", "-DMODELS_REQUEST=2.0.0")
        build = space / "existing-consumer"
        configure(ROOT / "tests/consumer", build,
                  f"-DProbSpan_DIR={legacy_only.as_posix()}/lib/cmake/ProbSpan",
                  "-DCMAKE_FIND_USE_PACKAGE_REGISTRY=FALSE",
                  "-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=FALSE")
        build_test(build)
        consumer("legacy-exact", legacy_only, *legacy_exact)
        consumer("models-exact", models_only, *models_exact)
        consumer("missing-models", legacy_only, *models_exact,
                 error=("Could not find a package configuration file provided by", "ProbSpanModels"))
        consumer("missing-legacy", models_only, *legacy_exact,
                 error=("Could not find a package configuration file provided by", "ProbSpan"))
        consumer("legacy-major", legacy_only, "-DUSE_LEGACY=ON", "-DLEGACY_REQUEST=2.0",
                 error=("not compatible", "version: 1.1.0"))
        consumer("models-major", models_only, "-DUSE_MODELS=ON", "-DMODELS_REQUEST=3.0",
                 error=("not compatible", "version: 2.0.0"))

        for name, order in (("legacy-first", (legacy, models)), ("models-first", (models, legacy))):
            prefix = space / name
            first_paths = install(order[0], prefix)
            original = {path: (prefix / path).read_bytes() for path in first_paths}
            second_paths = install(order[1], prefix)
            actual = {p.relative_to(prefix).as_posix() for p in prefix.rglob("*") if p.is_file()}
            if (first_paths & second_paths or actual != legacy_files | models_files
                    or any((prefix / path).read_bytes() != data for path, data in original.items())):
                raise RuntimeError(f"Package collision in {name}")
            for reverse in ("ON", "OFF"):
                consumer(f"{name}-{reverse}", prefix, *legacy_exact, *models_exact,
                         f"-DMODELS_FIRST={reverse}")

        historical = space / "historical"
        header = historical / "probspan/probspan.h"
        header.parent.mkdir(parents=True)
        for output, source in ((header, "include/probspan/probspan.h"),
                               (historical / "old.c", "tests/consumer/main.c")):
            output.write_bytes(subprocess.check_output(["git", "show", f"{STABLE}:{source}"], cwd=ROOT))
        obj = historical / "old.o"
        exe = historical / "old.exe"
        # Compile with only the historical header, then link without compiling again.
        run(args.cc, "-std=c11", "-I", historical, "-c", historical / "old.c", "-o", obj)
        run(args.cc, obj, legacy_only / "lib/libprobspan.a", "-lm", "-o", exe)
        run(exe)
        print("All installation and historical-object checks passed.", flush=True)


if __name__ == "__main__":
    main()
