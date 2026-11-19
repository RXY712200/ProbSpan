# ProbSpanModels 2.0.0 development API

Install the Models package and link `ProbSpanModels::models`. The standalone
static archive uses C11 and platform math functions. It exposes ABI generation
1 through `ps2_abi_version()`. D2.2 adds the following operation.

```c
#include <probspan_models/binomial_interval.h>

int zero_event_bound(double *bound)
{
    ps2_binomial_result result;
    const ps2_binomial_status status = ps2_binomial_interval(
        PS2_BINOMIAL_CLOPPER_PEARSON, 0, 10, 0.05,
        PS2_BINOMIAL_UPPER_ONE_SIDED, &result);
    if (status == PS2_BINOMIAL_OK) {
        *bound = result.upper; /* about 0.258866 */
    }
    return status;
}
```

## Contract

The parameter is the common success probability of iid Bernoulli observations
at fixed n. The caller supplies observations with comparable definitions,
units and horizons. Duplicates, shifting populations and optional stopping
invalidate the assumptions. No sequential coverage guarantee applies.

`ps2_binomial_method` selects Wilson score inversion (approximate coverage)
or Clopper–Pearson (mathematical fixed-n coverage at least nominal).
`ps2_binomial_sidedness` selects two-sided (tail alpha/2), lower-only
(tail alpha), or upper-only (tail alpha). Unconstrained ends are exact 0 or 1.
The zero-success lower end is 0 and the full-success upper end is 1.
The other ends invert the corresponding tail even at those count boundaries.
For example, the upper zero-event endpoint solves (1−p)^n=tail and thus
has real value −expm1(log(tail)/n).

Validation order in `ps2_binomial_status` is:

1. INVALID_ARGUMENT for null output, unknown method/side, events greater
   than n, or alpha nonfinite or outside (0,1).
2. EMPTY for consistent counts with n=0.
3. UNSUPPORTED outside n in [1,1000000] or alpha in [1e-10,0.5].
4. NUMERICAL_FAILURE for a detectable unsupported rounding environment,
   uncertifiable requested resolution, or invalid computed endpoints.
5. OK writes both endpoints and the original alpha, method, and sidedness
   to the caller-owned `ps2_binomial_result`.

All failures leave every byte of the output untouched. Successful values are
finite and ordered in [0,1], with nonnegative zero. The function needs no heap,
I/O or mutable shared state. Separate calls can use separate output objects.
These confidence sets have no prior, readiness gate, or odds/EV interpretation.
F002–F005 are future scope.

## Numerical implementation and bounds

Direct IEEE binary64, round-to-nearest, gradual underflow, and ordinary
correctly rounded basic operations are required. Models disables unsafe
reassociation/contraction for the verified toolchains. Floating-point traps
and nonstandard evaluation modes are outside the supported environment.

Wilson inverts the normal survival function on [0,8] by at most 57 bisections
of 0.5 erfc(z/sqrt(2)). The alpha=.5 one-sided case uses z=0. For p=k/n, the
score root with the positive sign uses the usual shifted center and radius.
The lower root uses the product of the roots to avoid subtracting nearly
equal terms. The high-p upper root uses the symmetric failure-count equation.
A bisection mesh under 2⁻⁵⁴ in ideal arithmetic controls search resolution.
The erfc predicate still inherits platform libm error. Locally observed
endpoint errors are recorded separately from a proposed 2⁻⁴⁵ absolute
screening threshold. The screen leaves rounding headroom over observed
values and requires independent review before being treated as a contract.
It is not a universal libm or relative error bound.

Clopper–Pearson brackets the increasing P(X≥k) root for the lower endpoint
and the decreasing P(X≤k) root for the upper endpoint. At an interior trial
p, one binomial weight near the mode is scaled to exactly 1. The two walks
use rational successive probability ratios and accumulate total and
requested-tail weights separately. Every basic nonnegative interval
operation expands by one adjacent encoding. The subsequent ratios in each
direction decrease. The geometric upper bound is added to both applicable
upper sums when a walk truncates. Otherwise the walk reaches the support
boundary. Dividing tail by total yields an enclosure without subtraction
from 1. Bound movement requires a proved sign from this enclosure, with
quarter probes on ambiguous signs. This gives an outward endpoint conditional
on the floating environment and the enclosure proof, even if the true root
falls between encodings. A returned endpoint can be farther out than the
nearest safe encoding.

Each CP endpoint uses at most 80 rounds, each with up to three tail walks
over at most n off-pivot terms per trial. Storage is O(1); geometric truncation
shortens typical walks. Final bracket width is capped at the proposed
absolute resolution 2⁻³⁸ (roughly 3.64e−12). The bracket itself is an a posteriori
error bound and the cap limits extra width to that scale per endpoint,
independently of confidence level. This proposed cap is a resolution gate,
not a relaxed tail predicate. Independent acceptance of this policy is
pending. There is no uniform tail-relative or ULP guarantee. At n=1e6,
k=n−1 and a very small alpha, the root can be between the last two encodings
below or at 1. Rounding out to 1 makes a 100% relative tail residual possible
while maintaining an outward bound. The qualification distinguishes these
quantities.

See the [qualification procedure and recorded evidence](tests/QUALIFICATION.md).
