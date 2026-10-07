#include "probspan/probspan.h"
#include "decision_private.h"
#include "model_v1.h"
#include "probability_math.h"

#include <math.h>
#include <stddef.h>

static probspan_subjective_side analyze_side(ps_probability_interval interval,
                                            double half_width, double odds, double threshold) {
    probspan_subjective_side result = {ps_ev_interval(interval, odds), odds != 1.0, 0.0};
    /* At odds exactly one, logit(threshold) is undefined. v1 makes only S
       unavailable; the EV interval and its classification remain available. */
    if (result.has_robust_margin) {
        result.robust_margin = (ps_logit(interval.center) - ps_logit(threshold)) / half_width;
    }
    return result;
}

probspan_status probspan_analyze_subjective(const probspan_subjective_result *subjective,
                                            double event_odds, double complement_odds,
                                            probspan_subjective_analysis *analysis) {
    if (subjective == NULL || analysis == NULL) { return PROBSPAN_INVALID_ARGUMENT; }
    const ps_probability_interval interval = {
        subjective->probability, subjective->lower, subjective->upper
    };
    if (!ps_valid_probability_interval(interval) || interval.center <= 0.0 ||
        interval.center >= 1.0 || !isfinite(subjective->logit_half_width) ||
        subjective->logit_half_width <= 0.0) { return PROBSPAN_INVALID_ARGUMENT; }
    const probspan_status status = ps_validate_odds_pair(event_odds, complement_odds);
    if (status != PROBSPAN_OK) { return status; }
    const probspan_odds_geometry geometry = ps_odds_geometry(event_odds, complement_odds);
    const probspan_subjective_analysis result = {
        PS_ODDS_ANALYSIS_VERSION, geometry,
        analyze_side(interval, subjective->logit_half_width, event_odds, geometry.event_break_even),
        analyze_side(ps_complement_interval(interval), subjective->logit_half_width,
                     complement_odds, geometry.complement_event_break_even)
    };
    *analysis = result;
    return PROBSPAN_OK;
}
