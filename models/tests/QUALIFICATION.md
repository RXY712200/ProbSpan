# D2.2 numerical qualification

The deterministic grid in [qualify_interval.py](qualify_interval.py) contains
the pinned n, k and alpha grid and seven separately selected challenge
tuples. It runs both methods and all sides against the compiled probe,
with alpha input represented in hexadecimal binary64 notation.
The JSON reports per-side maxima, raw encoding distances, probability-tail
residuals and failed cases. Input cases are reproducible from the committed
script. There is no randomized fixture.

Run from the repository root, substituting the executable path for your build:

```sh
python -m pip install -r models/tests/qualification-requirements.txt
cmake -S models -B model-build -DCMAKE_BUILD_TYPE=Release
cmake --build model-build --config Release
ctest --test-dir model-build -C Release --output-on-failure
python models/tests/qualify_interval.py model-build/models_interval_probe
```

Windows MinGW uses the .exe suffix. NumPy and SciPy (BSD-licensed projects)
are development-only. SciPy supplies a starting value for interior CP roots.
The independent reference uses 50- and 90-decimal-digit Decimal recurrence
with a tighter omitted-mass bound and Newton refinement, analytic powers at
edge counts, and tests both adjacent binary64 points. For n≤10 the sign
test uses exact rational binomial mass. The higher-n Decimal sign comparison
rejects poorly separated signs. The two precisions must agree on the
adjacent bracket. Finite-precision agreement alone does not establish
strict coverage. The runtime outward argument instead rests on explicit
interval arithmetic and the geometric remainder in the production tail
solver. The high-precision reference shares the binomial recurrence
identity and does not call the C implementation to calculate expected values.

Wilson uses a high-precision Taylor integral of the normal density and
Newton iteration, then evaluates the score roots in Decimal. The floating
NormalDist value is only a starting point. B-E001 is reproduced at n=20,
p=.01, using actual interval endpoints with exact rational sampling
probabilities. A separate fixed truth p=.005 exhibits Wilson undercoverage.
These are fixed-n coverage calculations, separate from the error budgets and
not evidence of field applicability.

[Windows results](qualification-windows.json) used UCRT64 GCC 16.2.0,
CMake 4.4.3, Python 3.13.14, NumPy 2.4.4 and SciPy 1.17.1. All 750 grid and
42 challenge calls succeeded. The maximum Wilson endpoint difference was
2.22e−16 (five encoding steps at most). CP differed from the nearest safe
endpoint by at most 1.95e−15. Near-zero endpoints can differ by many encoding
steps even with small absolute error. The largest CP relative tail discrepancy
was 1 at a resolution-limited upper endpoint. Proposed budgets describe a
checked resolution cap for CP and a qualification screen for Wilson, with
no full-domain certification of Wilson libm error or an exhaustive test of
all CP input encodings. Independent review of the proof, thresholds,
productive domain and wider portability is required.
