#include <probspan_models/beta_predict.h>

#include <fenv.h>
#include <float.h>
#include <math.h>
#include <stddef.h>

#define HISTORY_LIMIT UINT64_C(1000000)
#define FUTURE_LIMIT UINT64_C(10000)
#define LOG_ERROR_BUDGET 0x1p-30

_Static_assert(FLT_RADIX == 2 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024
    && DBL_MIN_EXP == -1021 && FLT_EVAL_METHOD == 0,
    "Beta prediction requires direct binary64 evaluation");

static bool supported_environment(void)
{
    volatile double smallest = DBL_TRUE_MIN;
    return fegetround() == FE_TONEAREST && smallest * 2.0 == 0x1p-1073;
}

ps2_beta_status ps2_beta_update(ps2_beta_shapes prior, uint64_t events,
    uint64_t nonevents, ps2_beta_posterior *out)
{
    if (out == NULL || !isfinite(prior.a) || !isfinite(prior.b)
        || prior.a <= 0.0 || prior.b <= 0.0) {
        return PS2_BETA_INVALID_ARGUMENT;
    }
    if (prior.a < 0.5 || prior.a > 1000000.0 || prior.b < 0.5 || prior.b > 1000000.0
        || events > HISTORY_LIMIT || nonevents > HISTORY_LIMIT - events) {
        return PS2_BETA_UNSUPPORTED;
    }
    if (!supported_environment()) {
        return PS2_BETA_NUMERICAL_FAILURE;
    }
    const ps2_beta_shapes shapes = {prior.a + (double)events, prior.b + (double)nonevents};
    const ps2_beta_posterior result = {
        prior, events, nonevents, shapes, shapes.a / (shapes.a + shapes.b),
        events == 0 && nonevents == 0
    };
    *out = result;
    return PS2_BETA_OK;
}

typedef struct {
    double value;
    double correction;
} log_sum;

static void accumulate(log_sum *sum, double term)
{
    const double adjusted = term - sum->correction;
    const double next = sum->value + adjusted;
    sum->correction = (next - sum->value) - adjusted;
    sum->value = next;
}

static double log_mass(double a, double b, unsigned n, unsigned k)
{
    /* Reduce work on the binomial coefficient and use the same orientation
     * for mirrored inputs. This multiplies one sequence likelihood by its
     * exact combinatorial multiplicity, without subtracting log-Gamma terms. */
    if (k > n - k || (k == n - k && a > b)) {
        const double swap = a;
        a = b;
        b = swap;
        k = n - k;
    }
    log_sum mass = {0};
    for (unsigned i = 0; i < k; ++i) {
        accumulate(&mass, log1p((double)(n - k) / (i + 1u)));
        accumulate(&mass, -log1p(b / (a + i)));
    }
    for (unsigned i = 0; i < n - k; ++i) {
        accumulate(&mass, -log1p((a + k) / (b + i)));
    }
    return mass.value;
}

ps2_beta_status ps2_beta_predict(const ps2_beta_posterior *posterior,
    uint64_t future_n, uint64_t wanted_k, ps2_beta_prediction *out)
{
    if (posterior == NULL || out == NULL || wanted_k > future_n) {
        return PS2_BETA_INVALID_ARGUMENT;
    }
    ps2_beta_posterior expected;
    const ps2_beta_status status = ps2_beta_update(posterior->prior,
        posterior->events, posterior->nonevents, &expected);
    if (status != PS2_BETA_OK) {
        return status;
    }
    if (posterior->shapes.a != expected.shapes.a || posterior->shapes.b != expected.shapes.b
        || posterior->event_probability != expected.event_probability
        || posterior->prior_only != expected.prior_only) {
        return PS2_BETA_INVALID_ARGUMENT;
    }
    if (future_n > FUTURE_LIMIT) {
        return PS2_BETA_UNSUPPORTED;
    }
    ps2_beta_prediction result = {1.0, 0.0, 0.0, 0.0, PS2_BETA_MASS_EXACT_ONE};
    if (future_n != 0) {
        const double n = (double)future_n;
        const double a = expected.shapes.a;
        const double b = expected.shapes.b;
        const double total = a + b;
        result.mean = n * (a / total);
        result.variance = result.mean * (b / total) * ((total + n) / (total + 1.0));
        result.log_pmf = log_mass(a, b, (unsigned)future_n, (unsigned)wanted_k);
        /* The threshold is log(2^-1075), the midpoint between +0 and the
         * smallest subnormal. An ambiguous sign cannot certify zero. */
        const double zero_cutoff = -1075.0 * 0.69314718055994530942;
        if (!isfinite(result.log_pmf) || result.log_pmf >= 0.0
            || fabs(result.log_pmf - zero_cutoff) <= LOG_ERROR_BUDGET) {
            return PS2_BETA_NUMERICAL_FAILURE;
        }
        if (result.log_pmf < zero_cutoff) {
            result.pmf = 0.0;
            result.mass_state = PS2_BETA_MASS_ROUNDED_ZERO;
        } else {
            result.pmf = exp(result.log_pmf);
            if (!(result.pmf > 0.0 && result.pmf <= 1.0)) {
                return PS2_BETA_NUMERICAL_FAILURE;
            }
            result.mass_state = result.pmf < DBL_MIN ? PS2_BETA_MASS_SUBNORMAL
                                                     : PS2_BETA_MASS_ENCODED;
        }
    }
    *out = result;
    return PS2_BETA_OK;
}
