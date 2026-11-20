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


## Explicit Beta update and batch prediction

Include `<probspan_models/beta_predict.h>`. With the same ABI generation 1,
`ps2_beta_update(ps2_beta_shapes prior, uint64_t events, uint64_t nonevents,
ps2_beta_posterior *out)` stores the explicit prior, counts, updated shapes,
single-event predictive mean and prior-only flag. Finite positive prior
shapes must be in [0.5, 1000000], with at most 1000000 observations total.
Beta(1,1) with 1 success and 2 failures gives Beta(2,3) and mean .4.
Zero counts succeed with the prior and prior-only flag.

`ps2_beta_predict(const ps2_beta_posterior *posterior, uint64_t future_n,
uint64_t wanted_k, ps2_beta_prediction *out)` consumes an initialized
posterior value produced by the update call, up to N=10000 and 0≤k≤N.
It replays the update and requires exact field equality, including the
evidence flag and predictive mean. A caller can reproduce the record by
calling the updater with the original prior and counts. Matching fields
check model consistency and cannot authenticate observations. Input and
output objects belong to the caller and must not overlap.

Validation order for update is pointers, finite positive prior,
supported shape/count range, then floating environment. Predict checks
pointers and k≤N first, propagates update validation, checks the
posterior fields, then checks N and runs the solver. The scoped
`ps2_beta_status` values are OK, INVALID_ARGUMENT, UNSUPPORTED and
NUMERICAL_FAILURE. All errors preserve output bytes. As with fixed-n
intervals, binary64 nearest-even and gradual underflow are required.

Given encoded a,b, the batch PMF is choose(N,k) B(a+k,b+N−k)/B(a,b).
For m=a/(a+b), the count mean is Nm and variance is
Nm(1−m)(a+b+N)/(a+b+1). For N>1 the multiplier exceeds one because trials
share the uncertain p. The inputs represent homogeneous, disjoint units
under the same horizon and conditional independence. Evidence admission
belongs to the caller. F002 has no source-borrowing or readiness rule.

The implementation evaluates the rising-factor likelihood for one binary
sequence and its binomial multiplicity via compensated log1p sums.
It uses O(N) time, at most 1.5N terms, O(1) workspace and no heap or I/O.
It evaluates normalized mathematical masses without adjusting returned
probabilities. N=0,k=0 gives exact 1, log 0 and both moments zero.
For nonempty batches the mass is mathematically positive. ENCODED and
SUBNORMAL describe finite positive binary64 mass. ROUNDED_ZERO returns
positive zero with finite log PMF. For example, Beta(.5,1000000) with N=k=10000
reaches ROUNDED_ZERO. An unresolved sign near the half-smallest-subnormal
midpoint produces NUMERICAL_FAILURE with no writeback. See the
[reference methods and proposed budgets](tests/BETA_QUALIFICATION.md).



## Fixed-weight target standardization

Include `<probspan_models/standardize.h>` and link `ProbSpanModels::models`.

```c
const ps2_fixed_stratum strata[] = {
    {.75, PS2_RISK_KNOWN, .5}, {.25, PS2_RISK_UNKNOWN, 0}
};
ps2_standardized_risk result;
if (ps2_standardize_fixed(strata, 2, &result) == PS2_STANDARDIZE_OK
    && result.kind == PS2_STANDARDIZE_PARTIAL) {
    /* Outward interval: [.375, .625]. */
    double lower = result.result.partial.lower.lower;
    double upper = result.result.partial.upper.upper;
    (void)lower;
    (void)upper;
}
```

Inputs and outputs are caller-owned and must not overlap. Inputs are
borrowed for the call. Both signs of zero weight are accepted as zero.
A known risk must be finite in [0,1] even at zero weight. Unknown risk
storage is ignored and may be left unspecified.

Validation precedence is null pointers, count zero (EMPTY), count above
1024 (UNSUPPORTED), then invalid rows (INVALID_ARGUMENT) before an
oversized weight (UNSUPPORTED). Unsupported rounding or lack of gradual
underflow returns NUMERICAL_FAILURE before exact normalization. A weight
above 2 can never fit the policy range. All other normalization decisions
are exact, including zero total (UNSUPPORTED). Every unsuccessful call
leaves the output bytes untouched.

Let W be the exact sum of encoded weights, A the exact weighted sum of
known risks and U the exact sum of unknown weights. Acceptance uses the
closed interval |W−1| ≤ 1/10^12 as a decimal rational. At U=0 the exact
target risk is A/W, returned as a nearest-even point and adjacent
enclosure. EXACT means equal enclosure endpoints, ROUNDED means a
nonexact nonzero point, and ROUNDED_ZERO denotes loss of a strictly
positive exact point. At U>0 read only the partial result. The lower
enclosure surrounds A/W and the upper enclosure surrounds (A+U)/W.
Use the lower enclosure's lower value and upper enclosure's upper
value for the outward sharp identification interval. Setting every
unknown risk to 0 or every unknown risk to 1 attains the respective
real endpoint. Zero-weight unknown rows do not affect identification.
Tiny positive unknown weights preserve the partial state.

These are fixed target weights over disjoint exhaustive strata with
comparable endpoints and horizons. They are not sample pooling weights
or inferred weights. The set is not a confidence or credible interval.
The function makes no inference about transportability or covariance
between estimated risks and weights. See
[exact arithmetic and qualification](tests/STANDARDIZE_QUALIFICATION.md).

F004 and F005 are future work, F006 is excluded, and the future ProbSpan
v2.0.0 source release is unpublished.
