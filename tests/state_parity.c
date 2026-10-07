#include "probspan/probspan.h"
#include "analysis_fixtures.h"
#include "state_fixtures.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define COUNT(a) (sizeof(a) / sizeof((a)[0]))
#define CHECK(c) do { if (!(c)) { fprintf(stderr, "State check line %d: %s\n", __LINE__, #c); exit(EXIT_FAILURE); } } while (0)
#define SAME(a, b, f) CHECK((a).f == (b).f)

static void check_ev(probspan_ev_interval a, probspan_ev_interval b) {
    SAME(a, b, center); SAME(a, b, minimum); SAME(a, b, maximum); SAME(a, b, state);
}

static void check_subjective_side(probspan_subjective_side a, probspan_subjective_side b) {
    check_ev(a.ev, b.ev);
    SAME(a, b, has_robust_margin);
    if (a.has_robust_margin) { SAME(a, b, robust_margin); }
}

static void check_historical_side(probspan_historical_side a, probspan_historical_side b) {
    check_ev(a.ev, b.ev); SAME(a, b, positive_ev_probability);
}

static void check_composition(int32_t raw, int64_t events, int64_t complements,
                              double event_odds, double complement_odds) {
    probspan_analysis a;
    memset(&a, 0xa5, sizeof(a));
    unsigned char before[sizeof(a)];
    memcpy(before, &a, sizeof(a));
    probspan_subjective_result s;
    probspan_history_result h;
    double validated;
    probspan_status expected = probspan_subjective_estimate(raw, &s);
    if (expected == PROBSPAN_OK) { expected = probspan_history_estimate(events, complements, &h); }
    if (expected == PROBSPAN_OK) { expected = probspan_odds_validate(event_odds, &validated); }
    if (expected == PROBSPAN_OK) { expected = probspan_odds_validate(complement_odds, &validated); }
    probspan_subjective_analysis sa;
    probspan_historical_analysis ha;
    if (expected == PROBSPAN_OK) { expected = probspan_analyze_subjective(&s, event_odds, complement_odds, &sa); }
    if (expected == PROBSPAN_OK) { expected = probspan_analyze_historical(&h, event_odds, complement_odds, &ha); }
    CHECK(probspan_compose_analysis(raw, events, complements, event_odds, complement_odds, &a) == expected);
    if (expected != PROBSPAN_OK) { CHECK(memcmp(before, &a, sizeof(a)) == 0); return; }
    /* Compare meaningful fields exactly; C padding is not a value or a
       portable persistence format, and unavailable fields have no meaning. */
    SAME(a.subjective, s, raw_percent); SAME(a.subjective, s, used_percent);
    SAME(a.subjective, s, probability); SAME(a.subjective, s, lower);
    SAME(a.subjective, s, upper); SAME(a.subjective, s, logit_half_width);
    SAME(a.subjective, s, model_version);
    CHECK(a.event_odds == event_odds && a.complement_event_odds == complement_odds);
    SAME(a.subjective_analysis, sa, analysis_version);
    SAME(a.subjective_analysis.geometry, sa.geometry, event_break_even);
    SAME(a.subjective_analysis.geometry, sa.geometry, complement_event_break_even);
    SAME(a.subjective_analysis.geometry, sa.geometry, complement_break_even_as_event);
    SAME(a.subjective_analysis.geometry, sa.geometry, combination);
    check_subjective_side(a.subjective_analysis.event, sa.event);
    check_subjective_side(a.subjective_analysis.complement_event, sa.complement_event);
    SAME(a.history, h, event_count); SAME(a.history, h, complement_count);
    SAME(a.history, h, sample_size); SAME(a.history, h, state);
    SAME(a.history, h, statistically_ready); SAME(a.history, h, has_estimate);
    SAME(a.history, h, model_version); SAME(a.history, h, gate_version);
    if (h.has_estimate) {
        SAME(a.history, h, probability); SAME(a.history, h, lower); SAME(a.history, h, upper);
    }
    SAME(a.historical_analysis, ha, available);
    if (ha.available) {
        check_historical_side(a.historical_analysis.event, ha.event);
        check_historical_side(a.historical_analysis.complement_event, ha.complement_event);
    }
    probspan_model_relation relation;
    CHECK(probspan_classify_model_relation(sa.event.ev.state, ha.available,
        ha.available ? ha.event.ev.state : PROBSPAN_CROSSES_THRESHOLD, &relation) == PROBSPAN_OK);
    CHECK(a.event_relation == relation);
    CHECK(probspan_classify_model_relation(sa.complement_event.ev.state, ha.available,
        ha.available ? ha.complement_event.ev.state : PROBSPAN_CROSSES_THRESHOLD, &relation) == PROBSPAN_OK);
    CHECK(a.complement_event_relation == relation);
}

static void check_provenance(void) {
    for (size_t i = 0; i < COUNT(provenance_cases); ++i) {
        const provenance_case *c = &provenance_cases[i];
        probspan_provenance actual;
        CHECK(probspan_provenance_transition(&c->previous, c->previous_raw, c->current_raw,
            c->subject_changed, c->exposed_now, &actual) == PROBSPAN_OK);
        SAME(actual, c->expected, evidence_exposed);
        SAME(actual, c->expected, subjective_independence_compromised);
        /* In-place operation must obey the same old-state causal rule. */
        actual = c->previous;
        CHECK(probspan_provenance_transition(&actual, c->previous_raw, c->current_raw,
            c->subject_changed, c->exposed_now, &actual) == PROBSPAN_OK);
        SAME(actual, c->expected, evidence_exposed);
        SAME(actual, c->expected, subjective_independence_compromised);
    }
    probspan_provenance p = {true, true};
    unsigned char before[sizeof(p)];
    memcpy(before, &p, sizeof(p));
    const int32_t invalid[] = {-1, 101, INT32_MIN, INT32_MAX};
    for (size_t i = 0; i < COUNT(invalid); ++i) {
        CHECK(probspan_provenance_transition(&p, invalid[i], 60, false, false, &p) == PROBSPAN_RAW_PROBABILITY);
        CHECK(memcmp(before, &p, sizeof(p)) == 0);
        CHECK(probspan_provenance_transition(&p, 60, invalid[i], false, false, &p) == PROBSPAN_RAW_PROBABILITY);
        CHECK(memcmp(before, &p, sizeof(p)) == 0);
    }
    CHECK(probspan_provenance_transition(NULL, 60, 60, false, false, &p) == PROBSPAN_INVALID_ARGUMENT);
    CHECK(memcmp(before, &p, sizeof(p)) == 0);
    CHECK(probspan_provenance_transition(&p, 60, 60, false, false, NULL) == PROBSPAN_INVALID_ARGUMENT);
}

int main(void) {
    check_provenance();
    for (size_t i = 0; i < COUNT(subjective_analysis_cases); ++i) {
        const subjective_analysis_case *c = &subjective_analysis_cases[i];
        check_composition(c->raw, 0, 0, c->event_odds, c->complement_odds);
    }
    for (size_t i = 0; i < COUNT(historical_analysis_cases); ++i) {
        const historical_analysis_case *c = &historical_analysis_cases[i];
        check_composition((i % 3 == 0) ? 0 : (i % 3 == 1) ? 60 : 100,
            c->events, c->complements, c->event_odds, c->complement_odds);
    }
    for (size_t i = 0; i < COUNT(threshold_analysis_cases); ++i) {
        const historical_analysis_case *c = &threshold_analysis_cases[i];
        check_composition(60, c->events, c->complements, c->event_odds, c->complement_odds);
    }
    check_composition(-1, 0, 0, 2, 2); check_composition(101, 0, 0, 2, 2);
    check_composition(60, -1, 0, 2, 2); check_composition(60, 0, -1, 2, 2);
    CHECK(probspan_compose_analysis(60, 0, 0, 2, 2, NULL) == PROBSPAN_INVALID_ARGUMENT);
    printf("Provenance: %zu frozen cases; aggregate: %zu composition cases plus safety checks\n",
        COUNT(provenance_cases), COUNT(subjective_analysis_cases) + COUNT(historical_analysis_cases) + COUNT(threshold_analysis_cases));
    return EXIT_SUCCESS;
}
