# D3.2 numerical qualification

Run from the repository root. MinGW adds .exe to the probe path.

```sh
cmake -S models -B model-build -DCMAKE_BUILD_TYPE=Release
cmake --build model-build --config Release
ctest --test-dir model-build -C Release --output-on-failure
python models/tests/qualify_incidence.py model-build/models_incidence_probe
```

## Enclosure proof

With Y the exact risk count and d and o the two terminal counts, each
included event row updates F with S*d/Y and S with S*(Y-d-o)/Y, in that
order. Loss only changes the next integer Y. The validator subtracts
each exit count only after a comparison proves it fits. All converted
integers are at most 2^53 and exact. The validation pass also covers rows
after the requested horizon, which the computation pass never reads.

For each nontrivial division, product or addition, round the lower
calculation toward the predecessor and the upper calculation toward the
successor by applying nextafter to the nearest-even result. A single
adjacent step suffices for each correctly rounded basic operation under
the supported binary64 environment. Zero is a valid nonnegative lower
bound, and intersecting the upper enclosure with one is justified by
the exact estimator identities. Nonnegative multiplication and addition
are monotone in both operands. Induction over event rows therefore
encloses each real output. The returned approximate point lies inside
its enclosure. Its absolute error is bounded by the larger of the exact
distances to the two reported endpoints. This is a computable per-input
bound, independent of any measured oracle agreement. No post-hoc
clamping is applied to a separate point estimate.

Structural zero is derived from integers. Before any positive risk set
Y, S >= Y/n0. Initially it holds with equality. At a terminal step the
factor changes the bound to (Y-d-o)/n0, then censoring only reduces the
next Y. A positive post-event S therefore remains >= 1/n0, even across
complete loss. Likewise a positive target increment is >= d/n0. This
proves that neither positive output can underflow anywhere in the
authorized domain. The near-zero diagnostic conservatively means the
enclosure includes zero for a structurally positive quantity. It is
not evidence of mathematical zero or a claim of correctly rounded underflow.

For an additional review screen, write u=2^-53 and gamma(j)=ju/(1-ju).
Positive ratios and exact intermediate increments are at least 1/n0.
On their nearby normal encodings, a nearest step plus one directed
neighbor contributes at most 4u relative perturbation per operation.
Each path to a summand of F traverses at most 2m operations for survival
and ratio/product, plus m additions for accumulation, with m event rows.
The analogous S path uses at most 2m. Expanding nonnegative sums and
bounding products by the usual gamma inequality gives the conservative
width screen 2*gamma(12m+8) for both probabilities. The induction is
self-consistent over m<=1e6 because the bound cannot drive a positive
intermediate below half its exact value. This screen is separate from
the rigorous returned enclosure. The D1 candidate gamma(6m+8) was not
adopted for this different sequence of directed operations. No uniform
tail-relative accuracy is inferred.

There are at most two linear passes over one million rows and fixed
scratch. The library uses no allocation or I/O. Non-nearest rounding
and a failed gradual-underflow probe yield NUMERICAL_FAILURE without
writeback. Compile-time checks exclude non-binary64 or extended
evaluation. The runtime proof assumes no unsafe compiler transformations
or traps.

## Independent evidence

The qualifier uses exact rational products/sums on small risk sets and
30/60 decimal digits (about 100/199 bits) for longer cohorts. The long
reference reconstructs event-time denominators independently and checks
tier agreement against 1e-21. Both tiers use the same mathematical
recursion, so agreement cannot expose a shared scientific or risk-set
mistake. Exact Fraction examples and the directed source proof address
different parts of that risk. The million-row case uses Decimal rather
than Fraction. The probe serializes binary64 values in hexadecimal, and
the qualifier checks exact metadata, containment, absolute and relative
observations, and width. A fixed seed 320004 generates the 160 held-out
cohorts. The summary records the complete text-input hash. Use --memory
to separately trace the development Python heap.

The 10-person example gives F=.2 at tick 1 and F=.3 at tick 2. Treating
competing exits as censoring gives .36. The B-E004 two-period mechanism
gives .24 for CIF versus .28 with competing events treated as censoring.
The Phase B informative-loss control shows that identical observed
risk-set data can coexist with different unobserved outcomes. For example, after one of two units is lost at tick 1 and the other remains event-free at tick 2, the lost unit could have a target event by tick 2 or remain event-free. The rows agree while the completed cohort risk differs by 1/2. Thus
these numerical checks do not certify censoring assumptions.

[Windows evidence](incidence-qualification-windows.json) used UCRT64
GCC 16.2.0, CMake 4.4.3, Python 3.13.14 and Release warning flags
-Wall -Wextra -Wpedantic -Werror. The reference uses only the Python
standard library. Existing qualifiers retain their existing reference
dependencies. No new installed runtime dependency was added.

The Windows qualifier took 4.71 s without tracing and 14.02 s with tracing.
Peak traced Python heap was 187989074 bytes. The large development probe
uses a row allocation and is separate from the no-allocation library.
GCC -O2 -fstack-usage reported a 192-byte static library entry-point frame.
