#include "decision_private.h"
#include "model_v1.h"

#include <math.h>
#include <stddef.h>

probspan_ev_state ps_ev_state(double minimum, double maximum) {
    /* Strict inequalities are frozen: exactly +/-epsilon still crosses.
       Inspect interval endpoints, never infer this state from its center. */
    if (minimum > PS_FLOAT_EPSILON) { return PROBSPAN_ROBUST_POSITIVE; }
    if (maximum < -PS_FLOAT_EPSILON) { return PROBSPAN_ROBUST_NEGATIVE; }
    return PROBSPAN_CROSSES_THRESHOLD;
}

probspan_odds_combination ps_odds_combination(double inverse_sum) {
    if (fabs(inverse_sum - 1.0) <= PS_FLOAT_EPSILON) { return PROBSPAN_CRITICAL; }
    if (inverse_sum > 1.0 + PS_FLOAT_EPSILON) { return PROBSPAN_NORMAL_OVERLAP; }
    return PROBSPAN_DOUBLE_POSITIVE_WINDOW;
}

probspan_status probspan_classify_ev(double minimum, double maximum, probspan_ev_state *state) {
    if (state == NULL) { return PROBSPAN_INVALID_ARGUMENT; }
    *state = ps_ev_state(minimum, maximum);
    return PROBSPAN_OK;
}

static bool valid_ev_state(probspan_ev_state state) {
    return state == PROBSPAN_ROBUST_POSITIVE || state == PROBSPAN_ROBUST_NEGATIVE ||
           state == PROBSPAN_CROSSES_THRESHOLD;
}

probspan_status probspan_classify_model_relation(probspan_ev_state subjective,
                                                 bool historical_available,
                                                 probspan_ev_state historical,
                                                 probspan_model_relation *relation) {
    if (relation == NULL || !valid_ev_state(subjective) ||
        (historical_available && !valid_ev_state(historical))) {
        return PROBSPAN_INVALID_ARGUMENT;
    }
    /* Only independent EV states are compared; no probability fusion enters
       this policy or its result. Unavailability takes precedence over crossing. */
    probspan_model_relation result;
    if (!historical_available) { result = PROBSPAN_HISTORY_UNAVAILABLE; }
    else if (subjective == PROBSPAN_CROSSES_THRESHOLD || historical == PROBSPAN_CROSSES_THRESHOLD) {
        result = PROBSPAN_UNCERTAIN;
    } else if (subjective == PROBSPAN_ROBUST_POSITIVE && historical == PROBSPAN_ROBUST_POSITIVE) {
        result = PROBSPAN_AGREEMENT_POSITIVE;
    } else if (subjective == PROBSPAN_ROBUST_NEGATIVE && historical == PROBSPAN_ROBUST_NEGATIVE) {
        result = PROBSPAN_AGREEMENT_NEGATIVE;
    } else { result = PROBSPAN_CONFLICT; }
    *relation = result;
    return PROBSPAN_OK;
}
