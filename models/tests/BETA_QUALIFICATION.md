# D2.3 numerical qualification

Run from the repository root. Windows MinGW appends .exe to the probe path.

```sh
python -m pip install -r models/tests/beta-requirements.txt
cmake -S models -B model-build -DCMAKE_BUILD_TYPE=Release
cmake --build model-build --config Release
ctest --test-dir model-build -C Release --output-on-failure
python models/tests/qualify_beta.py model-build/models_beta_probe
```

The committed deterministic generator crosses all 16 prior pairs, four
history totals with deduplicated endpoints and midpoint splits, and four
future sizes. It samples endpoints, neighboring endpoints, center, and
interior mode neighbors when both updated shapes exceed one. For monotone
or U-shaped distributions a mode is at a sampled endpoint. Eight separate
challenge cases cover encoded shape neighbors, fractional inputs, skew,
subnormal mass, and the zero-rounding midpoint. Three complete supports
are evaluated (two at N=10, one at N=10000).

The reference evaluates the log-beta identity in mpmath at 96 and 192 bits.
It converts prior encodings to exact rational values before testing rounded
update shapes. Prediction reference starts from those encoded updated shapes.
Example decimal spellings such as 3.7 are evaluated as their actual binary64
encodings. A second calculation advances via adjacent mass ratios and
checks total mass. Two small supports are also checked against exact rational
masses and exact normalization. Precision agreement is checked per point
at one tenth of the proposed log and moment tolerances. The expected PMF
classification uses reference exponentiation and binary64 conversion,
separate from the runtime exp and log1p.

## Proposed budgets and bounds

- Absolute log PMF error <= 2^-30. The runtime sums at most 15,000 terms.
  Each argument is formed with a bounded positive addition/division and
  each log1p has magnitude less than 16. The argument condition number of
  log1p is at most one in this domain. Allowing four ulps per libm result,
  plus the basic arithmetic, yields a first-order absolute term-error
  allowance below 1.5e-10 even at maximum length. Compensated summation
  adds approximately 2u times the absolute sum, where u=2^-53, plus
  second-order terms. The proposed budget also leaves headroom for the
  computed zero threshold. It is conditional on the libm allowance and
  supported floating-point environment. It is not an all-libm proof.
- Normal PMF relative error <= 2^-29 follows from exp of the absolute log
  perturbation and rounding headroom. For subnormals use
  2^-29 times the real mass plus one smallest-subnormal step in absolute
  error. Close to zero, log PMF remains informative while relative PMF
  error can be large. A sign guard around log(2^-1075) rejects uncertain
  zero/nonzero classification instead of guessing.
- Relative mean and variance error <= 2^-47 for positive reference values.
  These use positive basic operations with no subtractive cancellation and
  fewer than ten rounding steps. At N=0 both moments are exactly zero.
- Total support mass drift <= 2^-29 on the verified supports. Normalized
  mathematical weights sum to one. The summed absolute error follows from
  the log error propagated through exp, plus negligible bounded subnormal
  rounding over at most 10,001 terms. The implementation does not renormalize
  returned scalar masses.
- States are exact for the empty future batch, returned encoding category,
  and failure paths. ENCODED/SUBNORMAL describe the returned representation
  and permit rounding, including cases that happen to be exactly representable.
  A nonempty in-support event has strictly positive mathematical mass.

[Windows results](beta-qualification-windows.json) used x64 MinGW UCRT64
GCC 16.2.0, CMake 4.4.3, Python 3.13.14 and mpmath 1.3.0 (BSD-3-Clause,
development only). All 2,104 grid calls succeeded. Seven challenge calls
succeeded and one was intentionally rejected within the rounding guard.
The boundary call is also checked for failure atomicity in CTest. These
measurements do not establish full-domain libm qualification. Independent
approval of the assumptions and budgets is required. The results say
nothing about target/foreign population compatibility. B-E002 remains a
counterexample to admitting foreign-group evidence without a cohort contract.
