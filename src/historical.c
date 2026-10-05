#include "probspan/probspan.h"

#include <math.h>
#include <stddef.h>

#include "beta_private.h"
#include "model_v1.h"

probspan_status probspan_history_estimate(int64_t event_count, int64_t complement_count,
                                          probspan_history_result *result) {
    if (result == NULL) {
        return PROBSPAN_INVALID_ARGUMENT;
    }
    if (event_count < 0 || complement_count < 0) {
        return PROBSPAN_HISTORY_COUNTS;
    }
    const uint64_t sample_size = (uint64_t)event_count + (uint64_t)complement_count;
    probspan_history_result estimate = {
        event_count, complement_count, sample_size,
        PROBSPAN_NO_HISTORY, false, false,
        0.0, 0.0, 0.0, PS_HISTORY_VERSION, PS_HISTORY_GATE_VERSION
    };
    if (sample_size == 0) {
        /* Availability is explicit; zero-valued numeric fields have no meaning
           when there is no history and must not be interpreted as estimates. */
        *result = estimate;
        return PROBSPAN_OK;
    }

    const double alpha = (double)event_count + PS_JEFFREYS_ALPHA;
    const double beta = (double)complement_count + PS_JEFFREYS_BETA;
    const double tail = (1.0 - PS_HISTORY_CREDIBLE_LEVEL) / 2.0;
    double lower;
    double upper;
    if (!ps_beta_quantile(tail, alpha, beta, &lower) ||
        !ps_beta_quantile(1.0 - tail, alpha, beta, &upper)) {
        return PROBSPAN_NUMERICAL_FAILURE;
    }

    estimate.has_estimate = true;
    estimate.probability = ((double)event_count + PS_JEFFREYS_ALPHA) /
                           ((double)sample_size + PS_JEFFREYS_ALPHA + PS_JEFFREYS_BETA);
    estimate.lower = lower;
    estimate.upper = upper;
    /* Both conditions are required. An extreme interval from fewer than 20
       samples remains insufficient, and 20 samples can still be too wide. */
    estimate.statistically_ready = sample_size >= PS_HISTORY_MIN_SAMPLE_SIZE &&
                                    upper - lower <= PS_HISTORY_MAX_INTERVAL_WIDTH;
    estimate.state = estimate.statistically_ready ? PROBSPAN_VALID : PROBSPAN_INSUFFICIENT;
    *result = estimate;
    return PROBSPAN_OK;
}
