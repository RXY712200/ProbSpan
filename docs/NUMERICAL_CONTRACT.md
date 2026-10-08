# Numerical contract

## Environment and exact guarantees

The implementation requires IEEE-754 binary64 `double`: radix 2, 53 significand
bits, exponent range -1021..1024 as described by C float macros. The decimal
converter checks these at compile time. The converter constructs encoded values
arithmetically rather than reading object layout. Normal supported builds use
round-to-nearest ties-even, gradual
underflow, and ordinary C/libm behavior. The **full library is not contracted
under non-default rounding modes**, floating-point traps, flush-to-zero, or
unsafe optimization. Do not use `-ffast-math`, `/fp:fast`, reassociation, or
similar flags that discard NaNs/infinities or change arithmetic ordering.

Exact contract items are input identity, integer counts/sum, versions, flags,
enums, availability, validation precedence, and policy branches. Exact decimal
conversion is a special guarantee: integer midpoint comparisons choose the
nearest binary64 encoding, ties to even, independent of locale and caller
rounding mode. The converter streams arbitrarily long valid input against
bounded exact midpoint coefficients; it does not accumulate digits in floating
arithmetic, call locale-sensitive conversion, or allocate memory. Syntax is
ASCII only. Public odds acceptance follows conversion and rejects nonfinite or
rounded values below 1. Four rounding modes and a comma locale are tested.

That parser guarantee does **not** make `log`, `exp`, division, Beta integration,
or all other arithmetic rounding-mode independent.

## Tolerance and branch contract

`oracle/numerical_policy.json` is the authoritative accepted parity policy:

| Result | Acceptance |
|---|---|
| Integers, states, flags, versions, structure/availability | Exact |
| Decimal parser binary64 result | Exact bit pattern |
| Elementary binary64 outputs | absolute error <= 1e-12 + 1e-12*abs(reference) |
| Beta CDF/quantile outputs, including corrected large references | absolute error <= 1e-10 + 1e-10*abs(reference) |

Tolerances do not replace branching. EV epsilon is separately frozen at 1e-12;
states and history gates must match reference exactly even when floats are
compared by tolerance. No blanket bit-identical promise exists for every libm
result across every compiler/architecture. Auditable deterministic behavior
means defined formulas, evaluation intent, numerical policy, and tested discrete
semantics. Do not enlarge tolerances to conceal a compiler defect.

EV computes a rounded product followed by subtraction. A volatile intermediate
prevents optional FMA contraction from changing an epsilon-boundary state.
Logit uses `log(p/(1-p))`, not algebraic replacements. Compiler optimizations
that disregard these decisions are unsupported.

## Ordinary Beta evaluation

`beta.c` evaluates the incomplete Beta using log-gamma normalization, tail
reflection, and a Lentz continued fraction. The fraction has a tiny denominator
floor, 20,000 iteration cap, and 8*DBL_EPSILON relative convergence test.
Ordinary quantiles use bracketed bisection (up to 200 iterations). Private
solver failures propagate as NUMERICAL_FAILURE rather than partial outputs.
These controls are numerical implementation details, not new model boundaries.

The final reentrancy audit found that C/POSIX `lgamma` may write shared
`signgam` state ([GNU libc manual](https://sourceware.org/glibc/manual/2.41/html_node/Special-Functions.html)).
The private positive log-Gamma helper therefore uses `log(tgamma(x))` below 8
and the existing Stirling remainder above it. The remainder polynomial and
cutoff are shared with large-shape normalization. This fixes hidden libm state
without changing Beta formulas, ordinary references, tolerances, or discrete
rules. It may change last bits of numeric evaluation; all accepted parity is
still required. There is no new public Gamma API.

## Authorized large-parameter exception

Frozen SciPy 1.18.1 is demonstrably inconsistent at extreme shapes. At balanced
10^18 counts, complementary CDFs sum to about 1.47725, and its own 2.5% quantile
evaluates to about 7.95e-51. At balanced 10^12 counts, complementary CDFs already
disagree by about 3e-6. Another extreme skewed case produces NaN quantiles and
therefore a spurious insufficient gate result. These are evaluator artifacts,
not mathematical v1 behavior.

The explicitly authorized policy uses separate high-precision mathematical
references in this region. Ordinary rows remain untouched. Jeffreys prior,
central 95% interval, thresholds, gate, and model versions are unchanged.
See the original evidence in [large-numerics note](../oracle/LARGE_NUMERICS.md)
and [threshold note](../oracle/STEP3_REFERENCE.md).

`generate_large.py` uses mpmath **1.3.0**, **80 decimal digits**, exact
log-gamma-normalized Beta density, adaptive tanh-sinh integration in standardized
logit coordinates, and safeguarded Newton quantiles. Normalization, symmetry,
monotonicity, complementarity, and inverse residuals below 1e-40 are checked.
Tail limits +/-256 omit less than 1e-78 probability for covered shapes.
An independent 60-digit run agrees after rounding every stored expected value
to binary64. Step 3 threshold data uses the same 80-digit independent integral;
none of these expected values is produced by the C implementation.

Public reference intervals use exact integer counts plus 0.5. Private CDF probes
and odds-derived threshold references evaluate **the exact real values encoded
by their binary64 shapes and x**, since rounding an input at extreme concentration
can change mass substantially. Runtime shapes preserve accepted `(double)count
+ 0.5`; public mean preserves `(double)e+0.5` divided by `(double)n+0.5+0.5`.
These representations are distinct from exact real count formulas; tolerated
numeric comparison does not authorize a model change.

## Runtime large-shape strategy and resolution

For shapes >=0.5 with sum>10,000, `beta_logit.c` integrates the same Beta law in
a scaled logit coordinate. Adaptive 16-point Gauss-Legendre panels avoid slow
fractions and large log-gamma cancellation. Stirling remainders and compensated
centering/conversion retain information without relying on wider `long double`.
Safeguarded quantile iteration maintains a bracket in transformed coordinates.
The strategy threshold selects evaluation, not a new prior or valid count domain.

At INT64_MAX scale, one representable x step can span substantial probability
mass. An extremely skewed endpoint can round to 1. Consequently CDF(q) need not
equal its nominal target within small probability tolerance even for the best
binary64 quantile. Tests require neighboring-double CDFs to bracket the target
with accepted probability tolerance; complement identities also use brackets
where subtraction rounds x. High-precision generation checks identities on
exact real arguments. Such representable-x limits are documented, not hidden
by claiming arbitrary precision at runtime.
