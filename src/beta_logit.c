#include "beta_logit.h"

#include <float.h>
#include <math.h>

#define LOG_SQRT_TWO_PI 0.91893853320467274178
#define SERIES_SMALL_ARGUMENT 0.125
#define SERIES_MAX_TERMS 40
#define STIRLING_MIN_ARGUMENT 8.0
#define CDF_CENTERED_FRACTION_LIMIT 0.1
#define LOGIT_TAIL_LIMIT 64.0
#define QUADRATURE_PANEL_WIDTH 2.0
#define QUADRATURE_ABSOLUTE_TOLERANCE 2e-14
#define QUADRATURE_MAX_DEPTH 12
#define QUANTILE_PROBABILITY_TOLERANCE 2e-14
#define QUANTILE_MAX_ITERATIONS 100
#define QUANTILE_BRACKET_RELATIVE_TOLERANCE (8.0 * DBL_EPSILON)

typedef struct {
    double alpha;
    double sum;
    double center;
    double center_roundoff;
    double scale;
    double log_density_at_zero;
} logit_density;

static double sum_roundoff(double a, double b, double sum) {
    const double b_part = sum - a;
    return (a - (sum - b_part)) + (b - b_part);
}

/* log1p(x)-x loses its quadratic term by subtraction near zero. Keeping
   that term is essential when its multiplier is a shape as large as 2^63. */
static double log1p_minus_x(double x) {
    if (fabs(x) >= SERIES_SMALL_ARGUMENT) {
        return log1p(x) - x;
    }
    double term = -x * x / 2.0;
    double sum = term;
    for (int n = 3; n <= SERIES_MAX_TERMS; ++n) {
        term *= -x * (n - 1.0) / n;
        sum += term;
        if (fabs(term) <= DBL_EPSILON * fabs(sum)) {
            break;
        }
    }
    return sum;
}

static double expm1_minus_x(double x) {
    if (fabs(x) >= SERIES_SMALL_ARGUMENT) {
        return expm1(x) - x;
    }
    double term = x * x / 2.0;
    double sum = term;
    for (int n = 3; n <= SERIES_MAX_TERMS; ++n) {
        term *= x / n;
        sum += term;
        if (fabs(term) <= DBL_EPSILON * fabs(sum)) {
            break;
        }
    }
    return sum;
}

/* Stirling's remainder, DLMF 5.11.1. This evaluates only the small correction,
   never a difference of enormous log-gamma values. At z>=8 the omitted term
   after z^-17 is below 1e-17, well below the integration tolerance; small z
   uses the C math runtime. */
static double stirling_remainder(double z) {
    if (z < STIRLING_MIN_ARGUMENT) {
        return lgamma(z) - ((z - 0.5) * log(z) - z + LOG_SQRT_TWO_PI);
    }
    const double inverse = 1.0 / z;
    const double square = inverse * inverse;
    return inverse * (1.0 / 12.0 + square * (-1.0 / 360.0 +
           square * (1.0 / 1260.0 + square * (-1.0 / 1680.0 +
           square * (1.0 / 1188.0 + square * (-691.0 / 360360.0 +
           square * (1.0 / 156.0 + square * (-3617.0 / 122400.0 +
           square * (43867.0 / 244188.0)))))))));
}

static logit_density make_density(double alpha, double beta) {
    const double sum = alpha + beta;
    const double center = alpha / sum;
    /* Retain the division and shape-sum roundoff separately. Losing this
       correction would shift a narrow quantile by multiple representable x
       values even though the transformed root itself has converged. */
    const double center_roundoff = (fma(-center, sum, alpha) -
                                   center * sum_roundoff(alpha, beta, sum)) / sum;
    logit_density density = {
        alpha, sum, center, center_roundoff, sqrt(1.0 / alpha + 1.0 / beta),
        -LOG_SQRT_TWO_PI - stirling_remainder(alpha) -
        stirling_remainder(beta) + stirling_remainder(sum)
    };
    return density;
}

/* Change variables in the exact beta integral (DLMF 8.17.1):
   logit(x)=log(alpha/beta)+scale*t. After including the Jacobian, the
   density at t=0 depends only on Stirling remainders. Its width stays O(1)
   even when the original posterior is narrower than 1e-9. This is numerical
   integration of the beta law, not a normal approximation to that law. */
static double density_at(const logit_density *density, double t) {
    const double displacement = density->scale * t;
    const double exponential = expm1(displacement);
    const double weighted = density->center * exponential;
    double difference;
    if (fabs(displacement) < SERIES_SMALL_ARGUMENT ||
        fabs(weighted) < SERIES_SMALL_ARGUMENT) {
        /* Cancel the linear terms algebraically before multiplying by shapes. */
        difference = -density->alpha * expm1_minus_x(displacement) -
                     density->sum * log1p_minus_x(weighted);
    } else {
        difference = density->alpha * displacement - density->sum * log1p(weighted);
    }
    return exp(density->log_density_at_zero + difference);
}

/* Positive abscissas and weights of the 16-point Gauss-Legendre rule.
   Panels are split and compared to their two half-panels to check accuracy. */
static double gauss_panel(const logit_density *density, double lower, double upper) {
    static const double nodes[8] = {
        0.09501250983763744019, 0.28160355077925891323,
        0.45801677765722738634, 0.61787624440264374845,
        0.75540440835500303390, 0.86563120238783174388,
        0.94457502307323257608, 0.98940093499164993260
    };
    static const double weights[8] = {
        0.18945061045506849629, 0.18260341504492358887,
        0.16915651939500253819, 0.14959598881657673208,
        0.12462897125553387205, 0.09515851168249278481,
        0.06225352393864789286, 0.02715245941175409485
    };
    const double middle = (lower + upper) / 2.0;
    const double half_width = (upper - lower) / 2.0;
    double integral = 0.0;
    for (int index = 0; index < 8; ++index) {
        const double offset = half_width * nodes[index];
        integral += weights[index] * (density_at(density, middle - offset) +
                                     density_at(density, middle + offset));
    }
    return half_width * integral;
}

static bool adaptive_panel(const logit_density *density, double lower, double upper,
                           double tolerance, int depth, double *value) {
    const double middle = (lower + upper) / 2.0;
    const double whole = gauss_panel(density, lower, upper);
    const double halves = gauss_panel(density, lower, middle) +
                          gauss_panel(density, middle, upper);
    if (!isfinite(halves)) {
        return false;
    }
    if (fabs(halves - whole) <= tolerance) {
        *value = halves;
        return true;
    }
    if (depth == QUADRATURE_MAX_DEPTH) {
        return false;
    }
    double left;
    double right;
    if (!adaptive_panel(density, lower, middle, tolerance / 2.0, depth + 1, &left) ||
        !adaptive_panel(density, middle, upper, tolerance / 2.0, depth + 1, &right)) {
        return false;
    }
    *value = left + right;
    return true;
}

static bool integrate(const logit_density *density, double lower, double upper, double *value) {
    double integral = 0.0;
    const double length = upper - lower;
    while (lower < upper) {
        const double end = fmin(upper, lower + QUADRATURE_PANEL_WIDTH);
        const double tolerance = QUADRATURE_ABSOLUTE_TOLERANCE * (end - lower) / length;
        double panel;
        if (!adaptive_panel(density, lower, end, tolerance, 0, &panel)) {
            return false;
        }
        integral += panel;
        lower = end;
    }
    *value = integral;
    return true;
}

static bool transformed_cdf(const logit_density *density, double t, double *value) {
    /* For shapes >=0.5, the slowest standardized logit tail decays with rate
       at least sqrt(0.5). The omitted mass outside +/-64 is below 1e-19.
       Integrating the closer tail also avoids loss near probability one. */
    if (t <= -LOGIT_TAIL_LIMIT) {
        *value = 0.0;
        return true;
    }
    if (t >= LOGIT_TAIL_LIMIT) {
        *value = 1.0;
        return true;
    }
    double integral;
    if (t <= 0.0) {
        if (!integrate(density, -LOGIT_TAIL_LIMIT, t, &integral)) {
            return false;
        }
        *value = integral;
    } else {
        if (!integrate(density, t, LOGIT_TAIL_LIMIT, &integral)) {
            return false;
        }
        *value = 1.0 - integral;
    }
    return true;
}

/* Compute x - alpha/(alpha+beta) with compensated products and sums. A naive
   subtraction of rounded means can lose several CDF digits for 2^63 shapes.
   fma is standard C11 and supplies the product roundoff even on platforms
   whose long double has no extra precision. */
static double centered_difference(double x, double alpha, double beta) {
    const double ax = alpha * x;
    const double bx = beta * x;
    const double sum = ax + bx;
    const double error = fma(alpha, x, -ax) + fma(beta, x, -bx) +
                         sum_roundoff(ax, bx, sum);
    const double difference = sum - alpha;
    const double remainder = sum_roundoff(sum, -alpha, difference) + error;
    return (difference + remainder) / (alpha + beta);
}

bool ps_beta_logit_cdf(double x, double alpha, double beta, double *value) {
    if (alpha > beta) {
        double reflected;
        if (!ps_beta_logit_cdf(1.0 - x, beta, alpha, &reflected)) {
            return false;
        }
        *value = 1.0 - reflected;
        return true;
    }
    const logit_density density = make_density(alpha, beta);
    const double delta = centered_difference(x, alpha, beta);
    double displacement;
    if (fabs(delta) < CDF_CENTERED_FRACTION_LIMIT * density.center * (1.0 - density.center)) {
        displacement = log1p(delta / density.center) -
                       log1p(-delta / (1.0 - density.center));
    } else {
        displacement = log(x / density.center) -
                       (log1p(-x) - log1p(-density.center));
    }
    return transformed_cdf(&density, displacement / density.scale, value);
}

static double probability_at(const logit_density *density, double t) {
    const double displacement = density->scale * t;
    const double exponential = expm1(displacement);
    const double denominator = 1.0 + density->center * exponential;
    /* Near the center, add the small offset and retained center roundoff
       before the final rounding to a binary64 quantile. Far into a skewed
       tail the multiplicative form avoids cancellation between center and
       a nearly opposite offset. */
    if (fabs(exponential) < SERIES_SMALL_ARGUMENT) {
        const double offset = density->center * (1.0 - density->center) *
                              exponential / denominator;
        return density->center + (offset + density->center_roundoff);
    }
    return density->center * exp(displacement) / denominator;
}

bool ps_beta_logit_quantile(double probability, double alpha, double beta, double *value) {
    if (alpha > beta) {
        double reflected;
        if (!ps_beta_logit_quantile(1.0 - probability, beta, alpha, &reflected)) {
            return false;
        }
        *value = 1.0 - reflected;
        return true;
    }
    const logit_density density = make_density(alpha, beta);
    double lower = -LOGIT_TAIL_LIMIT;
    double upper = LOGIT_TAIL_LIMIT;
    double t = 0.0;
    for (int iteration = 0; iteration < QUANTILE_MAX_ITERATIONS; ++iteration) {
        double cdf;
        if (!transformed_cdf(&density, t, &cdf)) {
            return false;
        }
        const double residual = cdf - probability;
        if (fabs(residual) <= QUANTILE_PROBABILITY_TOLERANCE ||
            upper - lower <= QUANTILE_BRACKET_RELATIVE_TOLERANCE * fmax(1.0, fabs(t))) {
            *value = probability_at(&density, t);
            return true;
        }
        if (residual < 0.0) {
            lower = t;
        } else {
            upper = t;
        }
        /* Newton works in a coordinate whose density has ordinary scale;
           bisection guards every step when a tail makes Newton unsafe. */
        const double candidate = t - residual / density_at(&density, t);
        t = isfinite(candidate) && candidate > lower && candidate < upper ?
            candidate : lower + (upper - lower) / 2.0;
    }
    return false;
}
