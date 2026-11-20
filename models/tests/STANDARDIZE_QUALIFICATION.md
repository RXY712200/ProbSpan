# D3.1 exact standardization qualification

Run from the repository root. MinGW adds .exe to the probe path.

```sh
cmake -S models -B model-build -DCMAKE_BUILD_TYPE=Release
cmake --build model-build --config Release
ctest --test-dir model-build -C Release --output-on-failure
python models/tests/qualify_standardize.py model-build/models_standardize_probe
```

## Finite arithmetic proof

The runtime uses 70 unsigned 32-bit little-significance-order limbs per
integer, with scale 2^-2148. frexp/scalbn extracts a binary64 significand
without reading representation bytes. Removing trailing zeros makes the
least encoded exponent at least -1074. Thus even eta times eta is one
exact unit. Each known product adds at most 53 shifted significands.
Word shifts use 0–31 and uint64_t intermediates. Carry advances at most
70 words. Subtraction follows a nonnegative comparison and tracks borrow.
There is no signed cancellation in W, A or U.

A valid normalization cannot contain a weight above 2. The row validator
diagnoses invalid data before the oversized-weight check. For all remaining
inputs W <= 2048, A+U <= W, and |W−1| times 10^12 is less than 2^51.
In integer units this is less than 2^2199, inside the 2240-bit capacity.
The policy multiplies the nonnegative integer distance by a 40-bit exact
constant and compares it with the integer encoding of one. This is
equivalent to the exact closed decimal-rational inequality. No floating
policy approximation or uncertainty band is used.

For 0 <= numerator < W, long division doubles the integer remainder,
extracts one bit and subtracts W when applicable. The invariant is that
the remainder is nonnegative and below W after each bit. The scan stops
at a zero remainder, 53 significant digits, or bit 1074. The retained
significand and scale form the exact lower encoding. A nonzero remainder
establishes that its immediate successor is the upper encoding. Comparing
twice the remainder with W and testing significand parity resolves the
nearest-even midpoint, including exactly half eta. Equality numerator=W
returns exact one. For partial identification the returned outward bounds
use the lower encoding of A/W and upper encoding of (A+U)/W.

The algorithm has at most 1024 rows, up to 53 shifted additions per product,
40 policy multiplier bits, and at most 1074 quotient iterations per endpoint
with 70-word passes. The doubled remainder is below 2W and fits. Scratch is
fixed-size and there is no allocation or recursion. Windows GCC 16.2.0
-O2 -fstack-usage reported a 2144-byte static frame for the entry point,
128 bytes for the ratio helper, and 64 for decode, excluding library frames
and ABI-passed values. The runtime numerical-failure path is reachable on
unsupported rounding or a failed gradual-underflow probe. Exact arithmetic
has no ambiguous-policy or unqualified subdomain in the supported environment.

## Independent qualification

The Python standard-library Fraction oracle converts each supplied float
to its exact rational value, evaluates the original equations, constructs
adjacent encodings, and compares returned float bits, not a tolerance.
It explicitly assigns 0 or 1 to each unknown risk and verifies the two
attainable worlds. The seed is 310003. Cases are reproducible from the
script and hashed in the summary, including exact hex input patterns and
signs at both normalization boundaries. The test includes eight independent
1024-row vectors and their reversals, plus smaller held-out permutations.
It checks positive zero, subnormals, midpoint ties, invalid states, and
output atomicity on probe failures. CTest additionally exercises null,
overflow-size and non-nearest rounding failures.

The Windows UCRT64 GCC 16.2.0 Release run used -Wall -Wextra -Wpedantic
-Werror. The oracle and probe took about 0.56 seconds together for 8371
cases. It observed 1324 successful results, 7043 expected unsupported
cases, three invalid cases and one empty case. There were zero mismatches
or unexpected failures. The qualifier uses only the Python standard
library. The [Windows summary](standardize-qualification-windows.json)
records the input hash and exact boundary evidence.

B-E003's fixed-weight inputs give approximately .13. A Simpson example
gives standardized .55 versus .45 with equal target weights, while raw
sample mixing with opposite .9/.1 proportions reverses the ordering.
The same estimator used for a random weight and risk has
E[X^2]=E[X]^2+Var(X), illustrating why a fixed-weight computation cannot
stand in for covariance-aware estimated-weight inference. These are
estimand checks. Broader validation needs domain-specific evidence.
