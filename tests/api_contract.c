#include "probspan/probspan.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "API contract line %d: %s\n", __LINE__, #c); exit(EXIT_FAILURE); } } while (0)
/* Snapshot bytes only to detect writes on errors, never as a value format. */
#define UNCHANGED(call, status, object) do { \
    unsigned char saved[sizeof(object)]; memcpy(saved, &(object), sizeof(object)); \
    CHECK((call) == (status)); CHECK(memcmp(saved, &(object), sizeof(object)) == 0); \
} while (0)

static void check_provenance_invariant(void) {
    probspan_provenance malformed = {false, true};
    probspan_provenance output = {true, false};
    for (int changed = 0; changed <= 1; ++changed) {
        for (int exposed = 0; exposed <= 1; ++exposed) {
            UNCHANGED(probspan_provenance_transition(&malformed, 60, 70,
                changed != 0, exposed != 0, &output), PROBSPAN_INVALID_ARGUMENT, output);
            UNCHANGED(probspan_provenance_transition(&malformed, 60, 70,
                changed != 0, exposed != 0, &malformed), PROBSPAN_INVALID_ARGUMENT, malformed);
        }
    }
    /* State validity precedes raw-domain validation, including aliasing. */
    UNCHANGED(probspan_provenance_transition(&malformed, -1, 101, false, true, &malformed),
        PROBSPAN_INVALID_ARGUMENT, malformed);
    probspan_provenance valid = {false, false};
    CHECK(probspan_provenance_transition(&valid, 0, 1, true, true, &valid) == PROBSPAN_OK);
    CHECK(valid.evidence_exposed && !valid.subjective_independence_compromised);
    CHECK(probspan_provenance_transition(&valid, 1, 0, false, false, &valid) == PROBSPAN_OK);
    CHECK(valid.evidence_exposed && valid.subjective_independence_compromised);
}

static void check_precedence_and_safety(void) {
    probspan_analysis output;
    memset(&output, 0xa5, sizeof(output));
    CHECK(probspan_compose_analysis(-1, -1, -1, NAN, NAN, NULL) == PROBSPAN_INVALID_ARGUMENT);
    UNCHANGED(probspan_compose_analysis(-1, -1, -1, NAN, NAN, &output), PROBSPAN_RAW_PROBABILITY, output);
    UNCHANGED(probspan_compose_analysis(60, -1, -1, NAN, NAN, &output), PROBSPAN_HISTORY_COUNTS, output);
    UNCHANGED(probspan_compose_analysis(60, 0, 0, NAN, NAN, &output), PROBSPAN_ODDS_RANGE, output);
    UNCHANGED(probspan_compose_analysis(60, 0, 0, 2, NAN, &output), PROBSPAN_ODDS_RANGE, output);
    double number = 42;
    UNCHANGED(probspan_odds_parse(NULL, &number), PROBSPAN_INVALID_ARGUMENT, number);
    UNCHANGED(probspan_odds_parse("0x1", &number), PROBSPAN_ODDS_SYNTAX, number);
    UNCHANGED(probspan_odds_parse("0.5", &number), PROBSPAN_ODDS_RANGE, number);
    CHECK(probspan_odds_parse("invalid", NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_odds_validate(NAN, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_subjective_half_width(NAN, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_subjective_estimate(-1, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_history_estimate(-1, -1, NULL) == PROBSPAN_INVALID_ARGUMENT);
    probspan_subjective_result subjective;
    memset(&subjective, 0xa5, sizeof(subjective));
    UNCHANGED(probspan_subjective_estimate(101, &subjective), PROBSPAN_RAW_PROBABILITY, subjective);
    UNCHANGED(probspan_subjective_half_width(NAN, &number), PROBSPAN_SUBJECTIVE_DOMAIN, number);
    probspan_history_result history;
    memset(&history, 0xa5, sizeof(history));
    UNCHANGED(probspan_history_estimate(-1, 0, &history), PROBSPAN_HISTORY_COUNTS, history);
    probspan_model_relation relation = PROBSPAN_CONFLICT;
    UNCHANGED(probspan_classify_model_relation((probspan_ev_state)-1, false,
        PROBSPAN_ROBUST_POSITIVE, &relation), PROBSPAN_INVALID_ARGUMENT, relation);
    UNCHANGED(probspan_classify_model_relation(PROBSPAN_ROBUST_POSITIVE, true,
        (probspan_ev_state)999, &relation), PROBSPAN_INVALID_ARGUMENT, relation);
    CHECK(probspan_classify_model_relation(PROBSPAN_ROBUST_POSITIVE, false,
        (probspan_ev_state)999, &relation) == PROBSPAN_OK);
    CHECK(relation == PROBSPAN_HISTORY_UNAVAILABLE);
    CHECK(probspan_classify_model_relation(PROBSPAN_ROBUST_POSITIVE, true,
        PROBSPAN_ROBUST_POSITIVE, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_classify_ev(0, 0, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_classify_odds_combination(NAN, NAN, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_analyze_subjective(NULL, 2, 2, NULL) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(probspan_analyze_historical(NULL, 2, 2, NULL) == PROBSPAN_INVALID_ARGUMENT);
    /* Unavailability means these fields have no numerical interpretation. */
    CHECK(probspan_compose_analysis(0, 0, 0, 1, 1, &output) == PROBSPAN_OK);
    CHECK(!output.history.has_estimate && !output.historical_analysis.available);
    CHECK(!output.subjective_analysis.event.has_robust_margin);
    CHECK(!output.subjective_analysis.complement_event.has_robust_margin);
    CHECK(output.event_relation == PROBSPAN_HISTORY_UNAVAILABLE);
    CHECK(output.complement_event_relation == PROBSPAN_HISTORY_UNAVAILABLE);
}

int main(void) {
    CHECK(PROBSPAN_VERSION_MAJOR == 1 && PROBSPAN_VERSION_MINOR == 0 && PROBSPAN_VERSION_PATCH == 0);
    CHECK(strcmp(PROBSPAN_VERSION_STRING, "1.0.0") == 0 && probspan_abi_version() == 1u);
    probspan_analysis analysis;
    CHECK(probspan_compose_analysis(60, 19, 1, 2, 2, &analysis) == PROBSPAN_OK);
    CHECK(analysis.subjective.model_version == 1u && analysis.history.model_version == 1u &&
        analysis.history.gate_version == 1u && analysis.subjective_analysis.analysis_version == 1u);
    check_provenance_invariant();
    check_precedence_and_safety();
    puts("Public API contract: versions, malformed provenance, aliasing, safety and status precedence passed");
    return EXIT_SUCCESS;
}
