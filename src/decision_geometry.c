#include "decision_private.h"

#include <math.h>
#include <stddef.h>

bool ps_valid_probability_interval(ps_probability_interval interval) {
    return isfinite(interval.lower) && isfinite(interval.center) && isfinite(interval.upper) &&
           interval.lower >= 0.0 && interval.upper <= 1.0 &&
           interval.lower <= interval.center && interval.center <= interval.upper;
}

ps_probability_interval ps_complement_interval(ps_probability_interval interval) {
    /* Complementation reverses order: the smallest complement probability
       comes from the largest event probability. Both models use this rule. */
    return (ps_probability_interval){1.0 - interval.center, 1.0 - interval.upper,
                                   1.0 - interval.lower};
}

static double expected_value(double probability, double odds) {
    /* Python rounds multiplication before subtraction. Prevent optional FMA
       contraction from changing an exact epsilon-boundary classification. */
    volatile double gross_return = probability * odds;
    return gross_return - 1.0;
}

probspan_ev_interval ps_ev_interval(ps_probability_interval interval, double odds) {
    const double minimum = expected_value(interval.lower, odds);
    const double maximum = expected_value(interval.upper, odds);
    return (probspan_ev_interval){expected_value(interval.center, odds), minimum, maximum,
                                ps_ev_state(minimum, maximum)};
}

probspan_status ps_validate_odds_pair(double event_odds, double complement_odds) {
    double validated;
    const probspan_status status = probspan_odds_validate(event_odds, &validated);
    return status == PROBSPAN_OK ? probspan_odds_validate(complement_odds, &validated) : status;
}

probspan_odds_geometry ps_odds_geometry(double event_odds, double complement_odds) {
    const double event_threshold = 1.0 / event_odds;
    const double complement_threshold = 1.0 / complement_odds;
    return (probspan_odds_geometry){event_threshold, complement_threshold,
        1.0 - complement_threshold, ps_odds_combination(event_threshold + complement_threshold)};
}

probspan_status probspan_classify_odds_combination(double event_odds, double complement_odds,
                                                  probspan_odds_combination *combination) {
    if (combination == NULL) { return PROBSPAN_INVALID_ARGUMENT; }
    const probspan_status status = ps_validate_odds_pair(event_odds, complement_odds);
    if (status != PROBSPAN_OK) { return status; }
    *combination = ps_odds_geometry(event_odds, complement_odds).combination;
    return PROBSPAN_OK;
}
