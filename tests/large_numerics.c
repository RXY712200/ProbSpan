#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "probspan/probspan.h"
#include "beta_private.h"
#include "large_fixtures.h"

#define COUNT(array) (sizeof(array) / sizeof((array)[0]))
#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Large numerical check failed at line %d: %s\n", __LINE__, #condition); \
    exit(EXIT_FAILURE); } } while (0)
#define INVARIANT_PROBABILITY_TOLERANCE 1e-10

static double max_interval_error;
static double max_cdf_error;

static bool close_value(double actual, double expected) {
    return isfinite(actual) && fabs(actual - expected) <= LARGE_ABS_TOL +
           LARGE_REL_TOL * fabs(expected);
}

static double cdf(double x, double alpha, double beta) {
    double probability;
    CHECK(ps_beta_cdf(x, alpha, beta, &probability));
    CHECK(isfinite(probability) && probability >= 0.0 && probability <= 1.0);
    return probability;
}

/* At int64 magnitudes, one ulp of x can represent substantial probability
   mass. A correctly rounded quantile need not have CDF(q)==p. Require that p
   lies between the CDFs of neighboring representable x values instead. This
   also covers intervals that correctly round to the endpoint one. */
static void check_quantile_bracket(double x, double p, double alpha, double beta) {
    const double below = cdf(fmax(0.0, nextafter(x, 0.0)), alpha, beta);
    const double above = cdf(fmin(1.0, nextafter(x, 1.0)), alpha, beta);
    if (below > p + INVARIANT_PROBABILITY_TOLERANCE ||
        above < p - INVARIANT_PROBABILITY_TOLERANCE) {
        fprintf(stderr, "Quantile bracket: a=%.17g b=%.17g p=%.17g x=%.17g below=%.17g above=%.17g\n",
                alpha, beta, p, x, below, above);
    }
    CHECK(below <= p + INVARIANT_PROBABILITY_TOLERANCE);
    CHECK(above >= p - INVARIANT_PROBABILITY_TOLERANCE);
}

static void check_complement(double x, double probability, double alpha, double beta) {
    const double complement = 1.0 - x;
    /* Subtracting tiny x from one may discard x completely. Bounding the
       rounded complement by adjacent doubles avoids asserting a false exact
       identity at a different mathematical argument. */
    const double below = cdf(fmax(0.0, nextafter(complement, 0.0)), beta, alpha);
    const double above = cdf(fmin(1.0, nextafter(complement, 1.0)), beta, alpha);
    CHECK(probability + below <= 1.0 + INVARIANT_PROBABILITY_TOLERANCE);
    CHECK(probability + above >= 1.0 - INVARIANT_PROBABILITY_TOLERANCE);
    if (1.0 - complement == x) {
        CHECK(fabs(probability + cdf(complement, beta, alpha) - 1.0) <=
              INVARIANT_PROBABILITY_TOLERANCE);
    }
}

static void check_reference(void) {
    for (size_t i = 0; i < COUNT(large_cases); ++i) {
        const large_case *expected = &large_cases[i];
        probspan_history_result actual;
        CHECK(probspan_history_estimate(expected->events, expected->complements, &actual) ==
              PROBSPAN_OK);
        CHECK(actual.event_count == expected->events &&
              actual.complement_count == expected->complements);
        CHECK(actual.sample_size == (uint64_t)expected->events +
                                    (uint64_t)expected->complements);
        CHECK(actual.has_estimate && actual.model_version == 1 && actual.gate_version == 1);
        CHECK(actual.statistically_ready == expected->ready);
        CHECK(actual.state == (expected->ready ? PROBSPAN_VALID : PROBSPAN_INSUFFICIENT));
        CHECK(close_value(actual.probability, expected->mean));
        CHECK(close_value(actual.lower, expected->lower));
        CHECK(close_value(actual.upper, expected->upper));
        max_interval_error = fmax(max_interval_error, fmax(fabs(actual.lower - expected->lower),
                                                         fabs(actual.upper - expected->upper)));
        const double alpha = (double)expected->events + 0.5;
        const double beta = (double)expected->complements + 0.5;
        for (size_t j = 0; j < COUNT(expected->probes); ++j) {
            const large_cdf_probe *probe = &expected->probes[j];
            const double probability = cdf(probe->x, alpha, beta);
            CHECK(close_value(probability, probe->cdf));
            max_cdf_error = fmax(max_cdf_error, fabs(probability - probe->cdf));
        }
    }
}

static void stress_pair(int64_t events, int64_t complements) {
    const double alpha = (double)events + 0.5;
    const double beta = (double)complements + 0.5;
    const double mean = alpha / (alpha + beta);
    const double sigma = sqrt(mean * (1.0 - mean) / (alpha + beta + 1.0));
    double previous = -1.0;
    for (int k = -2; k <= 2; ++k) {
        const double x = fmax(0.0, fmin(1.0, mean + k * sigma));
        const double probability = cdf(x, alpha, beta);
        CHECK(probability >= previous - INVARIANT_PROBABILITY_TOLERANCE);
        check_complement(x, probability, alpha, beta);
        previous = probability;
    }
    static const double probabilities[] = {0.025, 0.5, 0.975};
    double quantiles[3];
    for (size_t i = 0; i < COUNT(probabilities); ++i) {
        CHECK(ps_beta_quantile(probabilities[i], alpha, beta, &quantiles[i]));
        CHECK(isfinite(quantiles[i]) && quantiles[i] >= 0.0 && quantiles[i] <= 1.0);
        check_quantile_bracket(quantiles[i], probabilities[i], alpha, beta);
        if (i > 0) { CHECK(quantiles[i] >= quantiles[i - 1]); }
    }
    if (events == complements) {
        CHECK(fabs(cdf(0.5, alpha, beta) - 0.5) <= INVARIANT_PROBABILITY_TOLERANCE);
        CHECK(fabs(quantiles[1] - 0.5) <= LARGE_ABS_TOL);
        CHECK(fabs(quantiles[0] + quantiles[2] - 1.0) <= LARGE_ABS_TOL);
    }
    probspan_history_result estimate;
    CHECK(probspan_history_estimate(events, complements, &estimate) == PROBSPAN_OK);
    CHECK(estimate.has_estimate && estimate.state == PROBSPAN_VALID &&
          estimate.statistically_ready);
    CHECK(close_value(estimate.probability, mean));
    CHECK(isfinite(estimate.lower) && isfinite(estimate.upper));
    CHECK(estimate.lower <= estimate.upper);
}

static void check_stress(void) {
    int64_t magnitudes[19];
    int64_t n = INT64_C(10000);
    for (size_t i = 0; i < 15; ++i) {
        magnitudes[i] = n;
        if (i < 14) { n *= 10; }
    }
    magnitudes[15] = INT64_C(9007199254740991);
    magnitudes[16] = INT64_C(9007199254740992);
    magnitudes[17] = INT64_C(9007199254740993);
    magnitudes[18] = INT64_MAX;
    for (size_t i = 0; i < COUNT(magnitudes); ++i) {
        n = magnitudes[i];
        const int64_t pairs[10][2] = {
            {n, n}, {0, n}, {n, 0}, {1, n}, {n, 1},
            {100, n}, {n, 100}, {n / 1000, n}, {n, n / 1000}, {n / 3, n}
        };
        for (size_t j = 0; j < COUNT(pairs); ++j) {
            stress_pair(pairs[j][0], pairs[j][1]);
        }
    }
}

int main(void) {
    check_reference();
    printf("Corrected high-precision parity: %zu histories and %zu CDF probes; "
           "max interval error %.17g, max CDF error %.17g.\n",
           COUNT(large_cases), COUNT(large_cases) * 5, max_interval_error, max_cdf_error);
    check_stress();
    puts("Invariant/domain stress: 190 public histories, 570 quantiles, 950 primary CDF "
         "evaluations through INT64_MAX; zero numerical failures.");
    return EXIT_SUCCESS;
}
