# Phase B experiment commands

From the repository root, use Python 3.12 and a C11 compiler on a standard IEEE-754 binary64 host. The recorded run used Linux x86-64, GCC 14.2.0, Python 3.12.14, NumPy 2.2.6, SciPy 1.15.3, and mpmath 1.3.0. NumPy's `default_rng` used PCG64. The simulation seeds are 57031 and 57032. The other runs are deterministic enumerations, quadrature or fixed-data analyses.

```sh
python -m venv /tmp/probspan-b-env
/tmp/probspan-b-env/bin/python -m pip install numpy==2.2.6 scipy==1.15.3 mpmath==1.3.0
mkdir -p /tmp/probspan-b-results
/tmp/probspan-b-env/bin/python research/phase-b/comparisons.py /tmp/probspan-b-results/comparisons.json
gcc -std=c11 -O2 -Wall -Wextra -Werror -Iinclude -Isrc research/phase-b/beta_probe.c src/*.c -lm -o /tmp/probspan-b-beta
/tmp/probspan-b-env/bin/python research/phase-b/numerical.py /tmp/probspan-b-beta /tmp/probspan-b-results/numerical.json
curl -fsSL https://raw.githubusercontent.com/stan-dev/example-models/e5b7d9e2e9ecc375805c7e49e4a4d4c1882b5e3b/knitr/pool-binary-trials/efron-morris-75-data.tsv -o /tmp/probspan-b-results/batting.tsv
/tmp/probspan-b-env/bin/python research/phase-b/batting.py /tmp/probspan-b-results/batting.tsv /tmp/probspan-b-results/batting.json
```

The baseball script verifies the downloaded TSV SHA-256 and consistent early, remaining and seasonal counts. The data stays in the temporary directory. The C probe links the source tree only for research. JSON output forbids NaN and Infinity. For byte-level comparison on the recorded host, run `cmp` on each generated JSON and the matching file in this directory. On other floating-point stacks, inspect numeric differences before interpreting byte differences.

[Prior protocol](protocol.md) · [Results and uncertainty](../../docs/research/phase-b/experiments-and-results.zh-CN.md) · [Source addendum](../../docs/research/phase-b/source-addendum.tsv)
