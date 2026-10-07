#include "probspan/probspan.h"
#include "beta_private.h"
#include "decision_private.h"
#include "history_model_private.h"

#include <math.h>
#include <stddef.h>

static bool posterior_probability(double threshold, double alpha, double beta,
                                  bool event_side, double *probability) {
    double cdf;
    if (!ps_beta_cdf(threshold, alpha, beta, &cdf)) { return false; }
    /* This posterior mass is distinct from the credible-interval EV state.
       Preserve v1's subtraction for the event and direct CDF for complement. */
    *probability = fmin(1.0, fmax(0.0, event_side ? 1.0 - cdf : cdf));
    return true;
}

probspan_status probspan_analyze_historical(const probspan_history_result *history,
                                            double event_odds, double complement_odds,
                                            probspan_historical_analysis *analysis) {
    if (history == NULL || analysis == NULL) { return PROBSPAN_INVALID_ARGUMENT; }
    if (history->state != PROBSPAN_VALID) {
        /* Frozen control flow: unavailable history ignores even NaN/invalid
           odds. It is a normal result, not validation or numerical failure. */
        *analysis = (probspan_historical_analysis){0};
        return PROBSPAN_OK;
    }
    const ps_probability_interval interval = {history->probability, history->lower, history->upper};
    if (!history->has_estimate || history->event_count < 0 || history->complement_count < 0 ||
        !ps_valid_probability_interval(interval)) { return PROBSPAN_INVALID_ARGUMENT; }
    const probspan_status status = ps_validate_odds_pair(event_odds, complement_odds);
    if (status != PROBSPAN_OK) { return status; }
    const probspan_odds_geometry geometry = ps_odds_geometry(event_odds, complement_odds);
    double alpha;
    double beta;
    ps_history_shapes(history->event_count, history->complement_count, &alpha, &beta);
    probspan_historical_analysis result = {
        true, {ps_ev_interval(interval, event_odds), 0.0},
        {ps_ev_interval(ps_complement_interval(interval), complement_odds), 0.0}
    };
    if (!posterior_probability(geometry.event_break_even, alpha, beta, true,
                               &result.event.positive_ev_probability) ||
        !posterior_probability(geometry.complement_break_even_as_event, alpha, beta, false,
                               &result.complement_event.positive_ev_probability)) {
        return PROBSPAN_NUMERICAL_FAILURE;
    }
    *analysis = result;
    return PROBSPAN_OK;
}
