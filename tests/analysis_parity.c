#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "probspan/probspan.h"
#include "analysis_fixtures.h"

#define COUNT(array) (sizeof(array) / sizeof((array)[0]))
#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Analysis check failed at line %d: %s\n", __LINE__, #condition); \
    exit(EXIT_FAILURE); } } while (0)

static double maximum_ordinary_posterior_error;
static double maximum_corrected_posterior_error;

static void check_elementary(double actual, double expected) {
    if (!isfinite(actual) || fabs(actual - expected) > ANALYSIS_ELEMENTARY_ABS_TOL +
        ANALYSIS_ELEMENTARY_REL_TOL * fabs(expected)) {
        fprintf(stderr, "Elementary mismatch: actual %.17g expected %.17g\n", actual, expected);
        exit(EXIT_FAILURE);
    }
}

static void check_ev(probspan_ev_interval actual, probspan_ev_interval expected) {
    check_elementary(actual.center, expected.center);
    check_elementary(actual.minimum, expected.minimum);
    check_elementary(actual.maximum, expected.maximum);
    CHECK(actual.state == expected.state);
    CHECK(actual.minimum <= actual.center && actual.center <= actual.maximum);
}

static void check_subjective_side(probspan_subjective_side actual, probspan_subjective_side expected,
                                  double odds) {
    check_ev(actual.ev, expected.ev);
    CHECK(actual.has_robust_margin == expected.has_robust_margin);
    CHECK(actual.has_robust_margin == (odds != 1.0));
    if (actual.has_robust_margin) { check_elementary(actual.robust_margin, expected.robust_margin); }
}

static void check_subjective(void) {
    for (size_t i = 0; i < COUNT(subjective_analysis_cases); ++i) {
        const subjective_analysis_case *item = &subjective_analysis_cases[i];
        probspan_subjective_result estimate;
        CHECK(probspan_subjective_estimate(item->raw, &estimate) == PROBSPAN_OK);
        probspan_subjective_analysis actual;
        memset(&actual, 0xa5, sizeof(actual));
        unsigned char before[sizeof(actual)];
        memcpy(before, &actual, sizeof(actual));
        CHECK(probspan_analyze_subjective(&estimate, item->event_odds, item->complement_odds,
                                          &actual) == item->status);
        if (item->status != PROBSPAN_OK) {
            CHECK(memcmp(before, &actual, sizeof(actual)) == 0);
            continue;
        }
        CHECK(actual.analysis_version == item->expected.analysis_version);
        CHECK(actual.geometry.combination == item->expected.geometry.combination);
        check_elementary(actual.geometry.event_break_even, item->expected.geometry.event_break_even);
        check_elementary(actual.geometry.complement_event_break_even,
                         item->expected.geometry.complement_event_break_even);
        check_elementary(actual.geometry.complement_break_even_as_event,
                         item->expected.geometry.complement_break_even_as_event);
        check_subjective_side(actual.event, item->expected.event, item->event_odds);
        check_subjective_side(actual.complement_event, item->expected.complement_event,
                              item->complement_odds);
    }
}

static void check_historical_side(probspan_historical_side actual, probspan_historical_side expected,
                                  double *maximum_error) {
    check_ev(actual.ev, expected.ev);
    CHECK(isfinite(actual.positive_ev_probability));
    CHECK(actual.positive_ev_probability >= 0.0 && actual.positive_ev_probability <= 1.0);
    const double error = fabs(actual.positive_ev_probability - expected.positive_ev_probability);
    CHECK(error <= ANALYSIS_BETA_ABS_TOL +
                   ANALYSIS_BETA_REL_TOL * fabs(expected.positive_ev_probability));
    *maximum_error = fmax(*maximum_error, error);
}

static void check_histories(const historical_analysis_case *cases, size_t count, double *maximum_error) {
    for (size_t i = 0; i < count; ++i) {
        const historical_analysis_case *item = &cases[i];
        probspan_history_result estimate;
        CHECK(probspan_history_estimate(item->events, item->complements, &estimate) == PROBSPAN_OK);
        probspan_historical_analysis actual;
        memset(&actual, 0xa5, sizeof(actual));
        unsigned char before[sizeof(actual)];
        memcpy(before, &actual, sizeof(actual));
        CHECK(probspan_analyze_historical(&estimate, item->event_odds, item->complement_odds,
                                          &actual) == item->status);
        if (item->status != PROBSPAN_OK) {
            CHECK(memcmp(before, &actual, sizeof(actual)) == 0);
            continue;
        }
        CHECK(actual.available == item->expected.available);
        if (actual.available) {
            check_historical_side(actual.event, item->expected.event, maximum_error);
            check_historical_side(actual.complement_event, item->expected.complement_event, maximum_error);
        }
    }
}

static void check_classifiers(void) {
    for (size_t i = 0; i < COUNT(ev_state_cases); ++i) {
        probspan_ev_state state;
        CHECK(probspan_classify_ev(ev_state_cases[i].minimum, ev_state_cases[i].maximum, &state) ==
              PROBSPAN_OK);
        CHECK(state == ev_state_cases[i].state);
    }
    for (size_t i = 0; i < COUNT(combination_cases); ++i) {
        const combination_case *item = &combination_cases[i];
        probspan_odds_combination combination = PROBSPAN_CRITICAL;
        CHECK(probspan_classify_odds_combination(item->event_odds, item->complement_odds,
                                                &combination) == item->status);
        CHECK(combination == (item->status == PROBSPAN_OK ? item->state : PROBSPAN_CRITICAL));
    }
    for (size_t i = 0; i < COUNT(relation_cases); ++i) {
        const relation_case *item = &relation_cases[i];
        probspan_model_relation relation;
        CHECK(probspan_classify_model_relation(item->subjective, item->historical_available,
                                               item->historical, &relation) == PROBSPAN_OK);
        CHECK(relation == item->relation);
    }
}

static void check_geometry(void) {
    static const int32_t raw_values[] = {1, 25, 50, 60, 85, 99};
    for (size_t i = 0; i < COUNT(raw_values); ++i) {
        probspan_subjective_result estimate;
        CHECK(probspan_subjective_estimate(raw_values[i], &estimate) == PROBSPAN_OK);
        const double pairs[4][2] = {
            {1.0 / estimate.lower, 2.0}, {1.0 / estimate.upper, 2.0},
            {2.0, 1.0 / (1.0 - estimate.upper)}, {2.0, 1.0 / (1.0 - estimate.lower)}
        };
        for (size_t side = 0; side < 4; ++side) {
            probspan_subjective_analysis result;
            CHECK(probspan_analyze_subjective(&estimate, pairs[side][0], pairs[side][1], &result) ==
                  PROBSPAN_OK);
            check_elementary(side < 2 ? result.event.robust_margin : result.complement_event.robust_margin,
                             side % 2 == 0 ? 1.0 : -1.0);
        }
    }
    probspan_history_result history;
    probspan_historical_analysis result;
    CHECK(probspan_history_estimate(50, 50, &history) == PROBSPAN_OK);
    CHECK(probspan_analyze_historical(&history, 2.0, 2.0, &result) == PROBSPAN_OK && result.available);
    CHECK(fabs(result.event.positive_ev_probability - 0.5) <= ANALYSIS_BETA_ABS_TOL);
    CHECK(fabs(result.complement_event.positive_ev_probability - 0.5) <= ANALYSIS_BETA_ABS_TOL);
}

static void check_arguments(void) {
    probspan_subjective_result subject;
    probspan_history_result history;
    CHECK(probspan_subjective_estimate(50, &subject) == PROBSPAN_OK);
    CHECK(probspan_history_estimate(50, 50, &history) == PROBSPAN_OK);
    probspan_subjective_analysis subjective_output = {.analysis_version = 42};
    probspan_historical_analysis historical_output = {.available = true};
    CHECK(probspan_analyze_subjective(NULL, 2.0, 2.0, &subjective_output) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(subjective_output.analysis_version == 42);
    CHECK(probspan_analyze_subjective(&subject, 2.0, 2.0, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_analyze_historical(NULL, 2.0, 2.0, &historical_output) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(historical_output.available);
    CHECK(probspan_analyze_historical(&history, 2.0, 2.0, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_classify_ev(0.0, 0.0, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_classify_odds_combination(2.0, 2.0, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_classify_model_relation(PROBSPAN_ROBUST_POSITIVE, false,
                                          PROBSPAN_ROBUST_POSITIVE, NULL) == PROBSPAN_INVALID_ARGUMENT);
    probspan_model_relation relation = PROBSPAN_CONFLICT;
    CHECK(probspan_classify_model_relation((probspan_ev_state)99, false,
                                          PROBSPAN_ROBUST_POSITIVE, &relation) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(relation == PROBSPAN_CONFLICT);
    CHECK(probspan_classify_model_relation(PROBSPAN_ROBUST_POSITIVE, true,
                                          (probspan_ev_state)99, &relation) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(relation == PROBSPAN_CONFLICT);
    CHECK(probspan_classify_model_relation(PROBSPAN_CROSSES_THRESHOLD, false,
                                          (probspan_ev_state)99, &relation) == PROBSPAN_OK);
    CHECK(relation == PROBSPAN_HISTORY_UNAVAILABLE);
    subject.logit_half_width = 0.0;
    CHECK(probspan_analyze_subjective(&subject, 2.0, 2.0, &subjective_output) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(subjective_output.analysis_version == 42);
    history.has_estimate = false;
    CHECK(probspan_analyze_historical(&history, 2.0, 2.0, &historical_output) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(historical_output.available);
    history.state = PROBSPAN_NO_HISTORY;
    history.lower = history.probability = history.upper = NAN;
    CHECK(probspan_analyze_historical(&history, NAN, -1.0, &historical_output) == PROBSPAN_OK);
    CHECK(!historical_output.available);
}

int main(void) {
    check_subjective();
    check_histories(historical_analysis_cases, COUNT(historical_analysis_cases),
                    &maximum_ordinary_posterior_error);
    check_histories(threshold_analysis_cases, COUNT(threshold_analysis_cases),
                    &maximum_corrected_posterior_error);
    check_classifiers();
    check_geometry();
    check_arguments();
    printf("Step 3 subjective parity: %zu cases; historical parity: %zu cases "
           "(max posterior error %.17g).\n", COUNT(subjective_analysis_cases),
           COUNT(historical_analysis_cases), maximum_ordinary_posterior_error);
    printf("Corrected large thresholds: %zu cases (max posterior error %.17g); "
           "exact states: %zu EV, %zu combinations, %zu relations.\n",
           COUNT(threshold_analysis_cases), maximum_corrected_posterior_error,
           COUNT(ev_state_cases), COUNT(combination_cases), COUNT(relation_cases));
    return EXIT_SUCCESS;
}
