#include <probspan_models/binomial_interval.h>

#include <fenv.h>
#include <float.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>

_Static_assert(FLT_RADIX == 2 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024
    && DBL_MIN_EXP == -1021 && FLT_EVAL_METHOD == 0,
    "Binomial intervals require direct binary64 evaluation");

typedef struct {
    double lo;
    double hi;
} enclosure;

/* In the supported floating environment, widening a correctly rounded
 * basic operation by one encoding encloses its exact result. */
static double down(double value)
{
    return value == 0.0 ? 0.0 : nextafter(value, 0.0);
}

static double up(double value)
{
    return nextafter(value, INFINITY);
}

static enclosure multiply(enclosure a, enclosure b)
{
    return (enclosure){down(a.lo * b.lo), up(a.hi * b.hi)};
}

static enclosure divide(enclosure a, enclosure b)
{
    return (enclosure){down(a.lo / b.hi), up(a.hi / b.lo)};
}

static enclosure add(enclosure a, enclosure b)
{
    return (enclosure){down(a.lo + b.lo), up(a.hi + b.hi)};
}

static bool in_tail(unsigned j, unsigned k, bool upper_tail)
{
    return upper_tail ? j >= k : j <= k;
}

static void sum_direction(unsigned n, unsigned k, unsigned mode, bool up_index,
    bool upper_tail, enclosure odds, enclosure *total, enclosure *tail)
{
    enclosure term = {1.0, 1.0};
    unsigned j = mode;
    while (up_index ? j < n : j > 0) {
        const double numerator = up_index ? n - j : j;
        const double denominator = up_index ? j + 1u : n - j + 1u;
        const enclosure ratio = multiply(odds, divide(
            (enclosure){numerator, numerator}, (enclosure){denominator, denominator}));
        term = multiply(term, ratio);
        j = up_index ? j + 1u : j - 1u;
        *total = add(*total, term);
        if (in_tail(j, k, upper_tail)) {
            *tail = add(*tail, term);
        }
        /* The exact ratio decreases along each walk. Complete the omitted
         * sum with a geometric upper bound, also valid for any tail subset. */
        if (ratio.hi < 1.0 && term.hi < 0x1p-80) {
            const double denominator_lo = down(1.0 - ratio.hi);
            if (denominator_lo > 0.0) {
                const double remainder = up(up(term.hi * ratio.hi) / denominator_lo);
                if (remainder < 0x1p-70) {
                    total->hi = up(total->hi + remainder);
                    tail->hi = up(tail->hi + remainder);
                    break;
                }
            }
        }
    }
}

static enclosure binomial_tail(unsigned n, unsigned k, double p, bool upper_tail)
{
    /* Any nearby integer works as the normalization pivot, even when the
     * multiplication that selects it rounds across a mode boundary. */
    const unsigned mode = (unsigned)((n + 1u) * p);
    const enclosure prob = {p, p};
    const enclosure complement = {down(1.0 - p), up(1.0 - p)};
    const bool contains_mode = in_tail(mode, k, upper_tail);
    enclosure total = {1.0, 1.0};
    enclosure tail = {contains_mode ? 1.0 : 0.0, contains_mode ? 1.0 : 0.0};
    sum_direction(n, k, mode, true, upper_tail, divide(prob, complement), &total, &tail);
    sum_direction(n, k, mode, false, upper_tail, divide(complement, prob), &total, &tail);
    return divide(tail, total);
}

static bool classify(unsigned n, unsigned k, double p, double target,
    bool upper_tail, double *lo, double *hi)
{
    const enclosure value = binomial_tail(n, k, p, upper_tail);
    if (!isfinite(value.lo) || !isfinite(value.hi)) {
        return false;
    }
    if (value.hi <= target) {
        if (upper_tail) {
            *lo = p;
        } else {
            *hi = p;
        }
        return true;
    }
    if (value.lo >= target) {
        if (upper_tail) {
            *hi = p;
        } else {
            *lo = p;
        }
        return true;
    }
    return false;
}

static bool exact_tail_bound(unsigned n, unsigned k, double target,
    bool lower, double *bound)
{
    double lo = 0.0;
    double hi = 1.0;
    for (unsigned step = 0; step < 80u; ++step) {
        const double mid = lo + (hi - lo) * 0.5;
        if (mid == lo || mid == hi) {
            break;
        }
        if (!classify(n, k, mid, target, lower, &lo, &hi)) {
            /* An uncertain sign cannot move a bracket endpoint. Try points
             * on either side and stop when neither has a certifiable sign. */
            const double left = lo + (mid - lo) * 0.5;
            const double right = mid + (hi - mid) * 0.5;
            const bool a = left > lo && left < mid
                && classify(n, k, left, target, lower, &lo, &hi);
            const bool b = right > lo && right < hi
                && classify(n, k, right, target, lower, &lo, &hi);
            if (!a && !b) {
                break;
            }
        }
    }
    /* A small absolute width caps the loss of resolution. It is not a
     * predicate tolerance: the returned side has a separate sign certificate. */
    if (hi - lo > 0x1p-38) {
        return false;
    }
    *bound = lower ? lo : hi;
    return true;
}

static double normal_quantile(double tail)
{
    if (tail == 0.5) {
        return 0.0;
    }
    double lo = 0.0;
    double hi = 8.0;
    for (unsigned step = 0; step < 57u; ++step) {
        const double mid = lo + (hi - lo) * 0.5;
        if (0.5 * erfc(mid * 0.70710678118654752440) > tail) {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    return lo + (hi - lo) * 0.5;
}

static void wilson(unsigned n, unsigned k, double tail, ps2_binomial_result *result)
{
    const double p = (double)k / n;
    const double q = (double)(n - k) / n;
    const double z = normal_quantile(tail);
    const double shift = z * z / (2.0 * n);
    const double radius = z * sqrt((p * q + shift * 0.5) / n);
    const double plus = p + shift + radius;
    if (result->sidedness != PS2_BINOMIAL_UPPER_ONE_SIDED && k != 0u) {
        /* The product of the roots before division by the leading
         * coefficient gives the lower root without a small subtraction. */
        result->lower = p * p / plus;
    }
    if (result->sidedness != PS2_BINOMIAL_LOWER_ONE_SIDED && k != n) {
        result->upper = p > 0.5 ? 1.0 - q * q / (q + shift + radius)
                                : plus / (1.0 + 2.0 * shift);
    }
}

ps2_binomial_status ps2_binomial_interval(ps2_binomial_method method,
    uint64_t events, uint64_t n, double alpha, ps2_binomial_sidedness sidedness,
    ps2_binomial_result *out)
{
    if (out == NULL
        || (method != PS2_BINOMIAL_WILSON && method != PS2_BINOMIAL_CLOPPER_PEARSON)
        || (sidedness != PS2_BINOMIAL_TWO_SIDED
            && sidedness != PS2_BINOMIAL_LOWER_ONE_SIDED
            && sidedness != PS2_BINOMIAL_UPPER_ONE_SIDED)
        || events > n || !isfinite(alpha) || alpha <= 0.0 || alpha >= 1.0) {
        return PS2_BINOMIAL_INVALID_ARGUMENT;
    }
    if (n == 0u) {
        return PS2_BINOMIAL_EMPTY;
    }
    if (n > UINT64_C(1000000) || alpha < 1e-10 || alpha > 0.5) {
        return PS2_BINOMIAL_UNSUPPORTED;
    }
    volatile double smallest = nextafter(0.0, 1.0);
    if (fegetround() != FE_TONEAREST || smallest * 2.0 != 0x1p-1073) {
        return PS2_BINOMIAL_NUMERICAL_FAILURE;
    }
    const double tail = sidedness == PS2_BINOMIAL_TWO_SIDED ? alpha * 0.5 : alpha;
    ps2_binomial_result result = {0.0, 1.0, alpha, method, sidedness};
    if (method == PS2_BINOMIAL_WILSON) {
        wilson((unsigned)n, (unsigned)events, tail, &result);
    } else if ((sidedness != PS2_BINOMIAL_UPPER_ONE_SIDED && events != 0u
                && !exact_tail_bound((unsigned)n, (unsigned)events, tail, true, &result.lower))
            || (sidedness != PS2_BINOMIAL_LOWER_ONE_SIDED && events != n
                && !exact_tail_bound((unsigned)n, (unsigned)events, tail, false, &result.upper))) {
        return PS2_BINOMIAL_NUMERICAL_FAILURE;
    }
    if (!(result.lower >= 0.0 && result.lower <= result.upper && result.upper <= 1.0)) {
        return PS2_BINOMIAL_NUMERICAL_FAILURE;
    }
    *out = result;
    return PS2_BINOMIAL_OK;
}
