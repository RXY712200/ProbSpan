#include "probspan/probspan.h"

#include <stddef.h>

probspan_status probspan_compose_analysis(int32_t raw_percent,
    int64_t event_count, int64_t complement_count,
    double event_odds, double complement_event_odds, probspan_analysis *result) {
    if (result == NULL) { return PROBSPAN_INVALID_ARGUMENT; }
    probspan_analysis analysis = {0};
    probspan_status status = probspan_subjective_estimate(raw_percent, &analysis.subjective);
    if (status != PROBSPAN_OK) { return status; }
    status = probspan_history_estimate(event_count, complement_count, &analysis.history);
    if (status != PROBSPAN_OK) { return status; }
    status = probspan_odds_validate(event_odds, &analysis.event_odds);
    if (status != PROBSPAN_OK) { return status; }
    status = probspan_odds_validate(complement_event_odds, &analysis.complement_event_odds);
    if (status != PROBSPAN_OK) { return status; }
    status = probspan_analyze_subjective(&analysis.subjective, analysis.event_odds,
        analysis.complement_event_odds, &analysis.subjective_analysis);
    if (status != PROBSPAN_OK) { return status; }
    status = probspan_analyze_historical(&analysis.history, analysis.event_odds,
        analysis.complement_event_odds, &analysis.historical_analysis);
    if (status != PROBSPAN_OK) { return status; }
    /* Relations compare independent states; neither model modifies the other.
       Unavailable historical side fields are deliberately never read. */
    const bool available = analysis.historical_analysis.available;
    status = probspan_classify_model_relation(analysis.subjective_analysis.event.ev.state,
        available, available ? analysis.historical_analysis.event.ev.state : PROBSPAN_CROSSES_THRESHOLD,
        &analysis.event_relation);
    if (status != PROBSPAN_OK) { return status; }
    status = probspan_classify_model_relation(analysis.subjective_analysis.complement_event.ev.state,
        available, available ? analysis.historical_analysis.complement_event.ev.state : PROBSPAN_CROSSES_THRESHOLD,
        &analysis.complement_event_relation);
    if (status != PROBSPAN_OK) { return status; }
    *result = analysis;
    return PROBSPAN_OK;
}
