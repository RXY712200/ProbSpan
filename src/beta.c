#include "beta_private.h"
#include "beta_logit.h"

#include <float.h>
#include <math.h>
#include <stddef.h>

/* The continued fraction is evaluated with Lentz's method. Its tiny floor
   prevents division by zero without changing ordinary beta-tail results. */
#define PS_BETA_CF_MAX_ITERATIONS 20000
#define PS_BETA_CF_RELATIVE_TOLERANCE (8.0 * DBL_EPSILON)
#define PS_BETA_CF_TINY (DBL_MIN / DBL_EPSILON)
#define PS_BETA_QUANTILE_MAX_ITERATIONS 200
#define PS_BETA_LOGIT_SWITCH_SUM 10000.0
#define PS_BETA_LOGIT_MIN_SHAPE 0.5

static bool use_logit_integration(double alpha, double beta) {
    /* The alternate integrator's documented tail bound requires both shapes
       >=0.5. This is a numerical precondition, independent of model policy. */
    return alpha >= PS_BETA_LOGIT_MIN_SHAPE && beta >= PS_BETA_LOGIT_MIN_SHAPE &&
           alpha + beta > PS_BETA_LOGIT_SWITCH_SUM;
}

static double nonzero(double value) {
    if (fabs(value) < PS_BETA_CF_TINY) {
        return value < 0.0 ? -PS_BETA_CF_TINY : PS_BETA_CF_TINY;
    }
    return value;
}

static bool beta_fraction(double a, double b, double x, double *result) {
    const double sum = a + b;
    const double a_plus_one = a + 1.0;
    const double a_minus_one = a - 1.0;
    double c = 1.0;
    double d = 1.0 / nonzero(1.0 - sum * x / a_plus_one);
    double fraction = d;

    for (int iteration = 1; iteration <= PS_BETA_CF_MAX_ITERATIONS; ++iteration) {
        const double m = (double)iteration;
        const double m2 = 2.0 * m;
        double term = m * (b - m) * x / ((a_minus_one + m2) * (a + m2));
        d = 1.0 / nonzero(1.0 + term * d);
        c = nonzero(1.0 + term / c);
        fraction *= d * c;

        term = -(a + m) * (sum + m) * x / ((a + m2) * (a_plus_one + m2));
        d = 1.0 / nonzero(1.0 + term * d);
        c = nonzero(1.0 + term / c);
        const double delta = d * c;
        fraction *= delta;
        if (!isfinite(fraction)) {
            return false;
        }
        if (fabs(delta - 1.0) <= PS_BETA_CF_RELATIVE_TOLERANCE) {
            *result = fraction;
            return true;
        }
    }
    return false;
}

bool ps_beta_cdf(double x, double alpha, double beta, double *value) {
    if (value == NULL || !isfinite(x) || !isfinite(alpha) || !isfinite(beta) ||
        alpha <= 0.0 || beta <= 0.0 || x < 0.0 || x > 1.0) {
        return false;
    }
    if (x == 0.0 || x == 1.0) {
        *value = x;
        return true;
    }
    /* Large shapes make the ordinary gamma normalization cancel and the
       continued fraction slow. The transformed integral has stable scale
       throughout the history domain and preserves the same beta law. */
    if (use_logit_integration(alpha, beta)) {
        return ps_beta_logit_cdf(x, alpha, beta, value);
    }

    /* log-gamma keeps the beta normalization representable before exponentiation.
       Reflecting the upper tail avoids subtracting nearly equal numbers there. */
    const double log_front = lgamma(alpha + beta) - lgamma(alpha) - lgamma(beta) +
                             alpha * log(x) + beta * log1p(-x);
    const double front = exp(log_front);
    double fraction;
    double probability;
    if (x < (alpha + 1.0) / (alpha + beta + 2.0)) {
        if (!beta_fraction(alpha, beta, x, &fraction)) {
            return false;
        }
        probability = front * fraction / alpha;
    } else {
        if (!beta_fraction(beta, alpha, 1.0 - x, &fraction)) {
            return false;
        }
        probability = 1.0 - front * fraction / beta;
    }
    if (!isfinite(probability)) {
        return false;
    }
    *value = fmax(0.0, fmin(1.0, probability));
    return true;
}

bool ps_beta_quantile(double probability, double alpha, double beta, double *value) {
    if (value == NULL || !isfinite(probability) || probability < 0.0 ||
        probability > 1.0 || !isfinite(alpha) || !isfinite(beta) ||
        alpha <= 0.0 || beta <= 0.0) {
        return false;
    }
    if (probability == 0.0 || probability == 1.0) {
        *value = probability;
        return true;
    }
    if (use_logit_integration(alpha, beta)) {
        return ps_beta_logit_quantile(probability, alpha, beta, value);
    }

    /* Bisection is slower than unconstrained Newton iteration but never steps
       outside [0,1] and stays reliable for the Jeffreys 0.5 shape tails. */
    double lower = 0.0;
    double upper = 1.0;
    for (int iteration = 0; iteration < PS_BETA_QUANTILE_MAX_ITERATIONS; ++iteration) {
        const double middle = lower + (upper - lower) / 2.0;
        if (middle == lower || middle == upper) {
            *value = middle;
            return true;
        }
        double cdf;
        if (!ps_beta_cdf(middle, alpha, beta, &cdf)) {
            return false;
        }
        if (cdf < probability) {
            lower = middle;
        } else {
            upper = middle;
        }
    }
    return false;
}
