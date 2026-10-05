#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "model_v1.h"
#include "beta_private.h"
#include "oracle_fixtures.h"

#define COUNT(array) (sizeof(array) / sizeof((array)[0]))
#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "Oracle parity failure at %s:%d: %s\n", __FILE__, __LINE__, #condition); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

static bool close_enough(double actual, double expected, double absolute, double relative) {
    return isfinite(actual) && isfinite(expected) &&
           fabs(actual - expected) <= absolute + relative * fabs(expected);
}

#define CHECK_ELEMENTARY(actual, expected) \
    CHECK(close_enough((actual), (expected), ORACLE_ELEMENTARY_ABS_TOL, ORACLE_ELEMENTARY_REL_TOL))
#define CHECK_BETA(actual, expected) \
    CHECK(close_enough((actual), (expected), ORACLE_BETA_ABS_TOL, ORACLE_BETA_REL_TOL))

static void check_constants(void) {
    CHECK(PS_SUBJECTIVE_VERSION == ORACLE_SUBJECTIVE_MODEL_VERSION);
    CHECK(PS_HISTORY_VERSION == ORACLE_HISTORY_MODEL_VERSION);
    CHECK(PS_HISTORY_GATE_VERSION == ORACLE_HISTORY_GATE_VERSION);
    CHECK(PS_ODDS_ANALYSIS_VERSION == ORACLE_ODDS_ANALYSIS_VERSION);
    CHECK(PS_STATS_VERSION == ORACLE_STATS_VERSION);
    CHECK(PS_FLOAT_EPSILON == ORACLE_FLOAT_EPSILON);
    CHECK(PS_SUBJECTIVE_MIN == ORACLE_SUBJECTIVE_MIN_PROBABILITY);
    CHECK(PS_SUBJECTIVE_LOW == ORACLE_SUBJECTIVE_LOW_BREAKPOINT);
    CHECK(PS_SUBJECTIVE_MID_HIGH == ORACLE_SUBJECTIVE_MID_HIGH_BREAKPOINT);
    CHECK(PS_SUBJECTIVE_HIGH == ORACLE_SUBJECTIVE_HIGH_BREAKPOINT);
    CHECK(PS_SUBJECTIVE_VERY_HIGH == ORACLE_SUBJECTIVE_VERY_HIGH_BREAKPOINT);
    CHECK(PS_SUBJECTIVE_MAX == ORACLE_SUBJECTIVE_MAX_PROBABILITY);
    CHECK(PS_FACTOR_LOW == ORACLE_SUBJECTIVE_FACTOR_LOW);
    CHECK(PS_FACTOR_MID == ORACLE_SUBJECTIVE_FACTOR_MID);
    CHECK(PS_FACTOR_HIGH == ORACLE_SUBJECTIVE_FACTOR_HIGH);
    CHECK(PS_FACTOR_MAX == ORACLE_SUBJECTIVE_FACTOR_MAX);
    CHECK(PS_JEFFREYS_ALPHA == ORACLE_JEFFREYS_ALPHA);
    CHECK(PS_JEFFREYS_BETA == ORACLE_JEFFREYS_BETA);
    CHECK(PS_HISTORY_CREDIBLE_LEVEL == ORACLE_HISTORY_CREDIBLE_LEVEL);
    CHECK(PS_HISTORY_MIN_SAMPLE_SIZE == ORACLE_HISTORY_MIN_SAMPLE_SIZE);
    CHECK(PS_HISTORY_MAX_INTERVAL_WIDTH == ORACLE_HISTORY_MAX_INTERVAL_WIDTH);
    CHECK_ELEMENTARY(log(PS_FACTOR_LOW), ORACLE_LOG_FACTOR_LOW);
    CHECK_ELEMENTARY(log(PS_FACTOR_MID), ORACLE_LOG_FACTOR_MID);
    CHECK_ELEMENTARY(log(PS_FACTOR_HIGH), ORACLE_LOG_FACTOR_HIGH);
    CHECK_ELEMENTARY(log(PS_FACTOR_MAX), ORACLE_LOG_FACTOR_MAX);
}

static void check_subjective(void) {
    for (size_t index = 0; index < COUNT(subjective_cases); ++index) {
        const subjective_case *expected = &subjective_cases[index];
        probspan_subjective_result actual;
        CHECK(probspan_subjective_estimate(expected->raw, &actual) == PROBSPAN_OK);
        CHECK(actual.raw_percent == expected->raw);
        CHECK(actual.used_percent == expected->used);
        CHECK(actual.model_version == (uint32_t)expected->version);
        CHECK_ELEMENTARY(actual.probability, expected->probability);
        CHECK_ELEMENTARY(actual.lower, expected->lower);
        CHECK_ELEMENTARY(actual.upper, expected->upper);
        CHECK_ELEMENTARY(actual.logit_half_width, expected->width);
        if (expected->raw >= 1 && expected->raw <= 99) {
            CHECK(actual.lower < actual.probability && actual.probability < actual.upper);
        }
    }
    CHECK(subjective_cases[0].raw != subjective_cases[1].raw);
    CHECK(subjective_cases[0].used == subjective_cases[1].used);
    CHECK(subjective_cases[99].raw != subjective_cases[100].raw);
    CHECK(subjective_cases[99].used == subjective_cases[100].used);

    for (size_t index = 0; index < COUNT(width_cases); ++index) {
        double actual;
        CHECK(probspan_subjective_half_width(width_cases[index].probability, &actual) == PROBSPAN_OK);
        CHECK_ELEMENTARY(actual, width_cases[index].width);
    }
    for (size_t index = 0; index < COUNT(raw_validation_cases); ++index) {
        probspan_subjective_result actual;
        CHECK(probspan_subjective_estimate(raw_validation_cases[index].raw, &actual) ==
              raw_validation_cases[index].status);
    }
    for (size_t index = 0; index < COUNT(width_validation_cases); ++index) {
        double actual;
        CHECK(probspan_subjective_half_width(width_validation_cases[index].probability, &actual) ==
              width_validation_cases[index].status);
    }
}

static void check_history(void) {
    for (size_t index = 0; index < COUNT(history_cases); ++index) {
        const history_case *expected = &history_cases[index];
        probspan_history_result actual;
        CHECK(probspan_history_estimate(expected->events, expected->complements, &actual) == PROBSPAN_OK);
        CHECK(actual.event_count == expected->events);
        CHECK(actual.complement_count == expected->complements);
        CHECK(actual.sample_size == expected->size);
        CHECK(actual.state == expected->state);
        CHECK(actual.statistically_ready == expected->ready);
        CHECK(actual.has_estimate == expected->available);
        CHECK(actual.model_version == (uint32_t)expected->model_version);
        CHECK(actual.gate_version == (uint32_t)expected->gate_version);
        if (expected->available) {
            CHECK_ELEMENTARY(actual.probability, expected->probability);
            CHECK_BETA(actual.lower, expected->lower);
            CHECK_BETA(actual.upper, expected->upper);
        }
    }
    for (size_t index = 0; index < COUNT(history_validation_cases); ++index) {
        probspan_history_result actual;
        CHECK(probspan_history_estimate(history_validation_cases[index].events,
                                        history_validation_cases[index].complements, &actual) ==
              history_validation_cases[index].status);
    }

    /* These are gate and availability invariants, not a second set of
       manually transcribed floating-point oracle values. */
    probspan_history_result empty, below_minimum, wide, ready, symmetric;
    CHECK(probspan_history_estimate(0, 0, &empty) == PROBSPAN_OK);
    CHECK(empty.state == PROBSPAN_NO_HISTORY && !empty.has_estimate);
    CHECK(probspan_history_estimate(19, 0, &below_minimum) == PROBSPAN_OK);
    CHECK(below_minimum.sample_size < PS_HISTORY_MIN_SAMPLE_SIZE && !below_minimum.statistically_ready);
    CHECK(probspan_history_estimate(18, 2, &wide) == PROBSPAN_OK);
    CHECK(wide.sample_size == PS_HISTORY_MIN_SAMPLE_SIZE &&
          wide.upper - wide.lower > PS_HISTORY_MAX_INTERVAL_WIDTH && !wide.statistically_ready);
    CHECK(probspan_history_estimate(19, 1, &ready) == PROBSPAN_OK);
    CHECK(ready.state == PROBSPAN_VALID && ready.statistically_ready);
    CHECK(probspan_history_estimate(50, 50, &symmetric) == PROBSPAN_OK);
    CHECK_BETA(symmetric.lower + symmetric.upper, 1.0);
}

static void check_beta_cdf(void) {
    const double tail = (1.0 - ORACLE_HISTORY_CREDIBLE_LEVEL) / 2.0;
    for (size_t index = 0; index < COUNT(history_cases); ++index) {
        const history_case *item = &history_cases[index];
        if (!item->available) {
            continue;
        }
        const double alpha = item->events + ORACLE_JEFFREYS_ALPHA;
        const double beta = item->complements + ORACLE_JEFFREYS_BETA;
        double cdf;
        CHECK(ps_beta_cdf(item->lower, alpha, beta, &cdf));
        CHECK_BETA(cdf, tail);
        CHECK(ps_beta_cdf(item->upper, alpha, beta, &cdf));
        CHECK_BETA(cdf, 1.0 - tail);
    }
    double endpoint;
    CHECK(ps_beta_cdf(0.0, 0.5, 0.5, &endpoint) && endpoint == 0.0);
    CHECK(ps_beta_cdf(1.0, 0.5, 0.5, &endpoint) && endpoint == 1.0);
}

static void check_odds(void) {
    for (size_t index = 0; index < COUNT(odds_text_cases); ++index) {
        double actual;
        const odds_text_case *expected = &odds_text_cases[index];
        CHECK(probspan_odds_parse(expected->text, &actual) == expected->status);
        if (expected->status == PROBSPAN_OK) {
            CHECK_ELEMENTARY(actual, expected->value);
        }
    }
    for (size_t index = 0; index < COUNT(odds_numeric_cases); ++index) {
        double actual;
        const odds_numeric_case *expected = &odds_numeric_cases[index];
        CHECK(probspan_odds_validate(expected->input, &actual) == expected->status);
        if (expected->status == PROBSPAN_OK) {
            CHECK_ELEMENTARY(actual, expected->value);
        }
    }
}

static void check_api_arguments(void) {
    double odds = 7.0;
    CHECK(probspan_subjective_estimate(50, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_subjective_half_width(0.5, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_history_estimate(1, 0, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_odds_validate(2.0, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_odds_parse(NULL, &odds) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_odds_parse("2", NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_odds_parse("+2", &odds) == PROBSPAN_ODDS_SYNTAX && odds == 7.0);
    probspan_subjective_result subjective = {.raw_percent = 42};
    CHECK(probspan_subjective_estimate(-1, &subjective) == PROBSPAN_RAW_PROBABILITY);
    CHECK(subjective.raw_percent == 42);
}

int main(void) {
    check_constants();
    check_subjective();
    check_history();
    check_beta_cdf();
    check_odds();
    check_api_arguments();
    printf("Step 2 oracle parity passed: %zu subjective, %zu widths, %zu history, "
           "%zu odds text, %zu numeric odds, and %zu domain rejection vectors.\n",
           COUNT(subjective_cases), COUNT(width_cases), COUNT(history_cases),
           COUNT(odds_text_cases), COUNT(odds_numeric_cases),
           COUNT(raw_validation_cases) + COUNT(width_validation_cases) +
           COUNT(history_validation_cases));
    return EXIT_SUCCESS;
}
