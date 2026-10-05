#include "probspan/probspan.h"

#include <math.h>
#include <stddef.h>

#include "model_v1.h"

static double logit(double probability) {
    return log(probability / (1.0 - probability));
}

static double logistic(double value) {
    return 1.0 / (1.0 + exp(-value));
}

probspan_status probspan_subjective_half_width(double probability, double *half_width) {
    if (half_width == NULL) {
        return PROBSPAN_INVALID_ARGUMENT;
    }
    if (!(probability >= PS_SUBJECTIVE_MIN && probability <= PS_SUBJECTIVE_MAX)) {
        return PROBSPAN_SUBJECTIVE_DOMAIN;
    }

    const double low = log(PS_FACTOR_LOW);
    const double mid = log(PS_FACTOR_MID);
    const double high = log(PS_FACTOR_HIGH);
    const double maximum = log(PS_FACTOR_MAX);

    /* Preserve the reference's branch inclusivity. The long [0.55, 0.85]
       plateau is not a symmetric uncertainty rule. */
    if (probability <= PS_SUBJECTIVE_LOW) {
        *half_width = low;
    } else if (probability < PS_SUBJECTIVE_MID_HIGH) {
        const double fraction = (probability - PS_SUBJECTIVE_LOW) /
                                (PS_SUBJECTIVE_MID_HIGH - PS_SUBJECTIVE_LOW);
        *half_width = low + fraction * (mid - low);
    } else if (probability <= PS_SUBJECTIVE_HIGH) {
        *half_width = mid;
    } else if (probability < PS_SUBJECTIVE_VERY_HIGH) {
        const double fraction = (probability - PS_SUBJECTIVE_HIGH) /
                                (PS_SUBJECTIVE_VERY_HIGH - PS_SUBJECTIVE_HIGH);
        *half_width = mid - fraction * (mid - high);
    } else {
        const double fraction = (probability - PS_SUBJECTIVE_VERY_HIGH) /
                                (PS_SUBJECTIVE_MAX - PS_SUBJECTIVE_VERY_HIGH);
        *half_width = high - fraction * (high - maximum);
    }
    return PROBSPAN_OK;
}

probspan_status probspan_subjective_estimate(int32_t raw_percent,
                                             probspan_subjective_result *result) {
    if (result == NULL) {
        return PROBSPAN_INVALID_ARGUMENT;
    }
    if (raw_percent < 0 || raw_percent > 100) {
        return PROBSPAN_RAW_PROBABILITY;
    }

    /* Raw 0/100 remain distinct for provenance; only the mathematical input
       is clamped to 1/99, exactly as in the frozen reference. */
    const int32_t used_percent = raw_percent == 0 ? 1 : (raw_percent == 100 ? 99 : raw_percent);
    const double probability = used_percent / 100.0;
    double half_width;
    const probspan_status status = probspan_subjective_half_width(probability, &half_width);
    if (status != PROBSPAN_OK) {
        return status;
    }
    const double center_logit = logit(probability);
    *result = (probspan_subjective_result){
        raw_percent, used_percent, probability,
        logistic(center_logit - half_width), logistic(center_logit + half_width),
        half_width, PS_SUBJECTIVE_VERSION
    };
    return PROBSPAN_OK;
}
