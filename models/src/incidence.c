#include <probspan_models/incidence.h>

#include <fenv.h>
#include <float.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>

_Static_assert(FLT_RADIX == 2 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024
    && DBL_MIN_EXP == -1021 && FLT_EVAL_METHOD == 0,
    "Cumulative incidence requires direct binary64 evaluation");

typedef struct {
    double lower;
    double upper;
} enclosure;

/* Widen each basic operation before feeding it into a later operation.
 * Intersect with the analytically known probability domain [0,1]. */
static enclosure outward(double lower, double upper)
{
    return (enclosure){lower == 0.0 ? 0.0 : nextafter(lower, 0.0),
        upper >= 1.0 ? 1.0 : nextafter(upper, 1.0)};
}

static enclosure ratio(uint64_t numerator, uint64_t denominator)
{
    if (numerator == 0 || numerator == denominator) {
        const double value = numerator == 0 ? 0.0 : 1.0;
        return (enclosure){value, value};
    }
    const double value = (double)numerator / (double)denominator;
    return outward(value, value);
}

static enclosure multiply(enclosure a, enclosure b)
{
    return outward(a.lower * b.lower, a.upper * b.upper);
}

static enclosure add(enclosure a, enclosure b)
{
    return outward(a.lower + b.lower, a.upper + b.upper);
}

static ps2_incidence_value summarize(enclosure range, bool structural_zero)
{
    const ps2_incidence_precision precision = structural_zero
        ? PS2_INCIDENCE_STRUCTURAL_ZERO
        : range.lower == 0.0 ? PS2_INCIDENCE_POSITIVE_NEAR_ZERO
                             : PS2_INCIDENCE_POSITIVE_ENCLOSED;
    return (ps2_incidence_value){range.lower + (range.upper - range.lower) * 0.5,
        range.lower, range.upper, precision};
}

static ps2_incidence_status validate_rows(const ps2_incidence_request *request,
    ps2_incidence_result *result, uint64_t *included)
{
    uint64_t at_risk = request->initial_count;
    uint64_t previous = 0;
    bool beyond_support = false;
    result->at_risk_after_horizon = at_risk;
    result->support = PS2_INCIDENCE_AT_RISK;
    for (uint64_t i = 0; i < request->length; ++i) {
        const ps2_incidence_row *row = &request->rows[i];
        if ((i != 0 && row->tick <= previous) || row->tick > request->observed_through_tick
            || row->target_events > at_risk
            || row->other_events > at_risk - row->target_events
            || row->lost > at_risk - row->target_events - row->other_events) {
            return PS2_INCIDENCE_INVALID_ARGUMENT;
        }
        const uint64_t survivors = at_risk - row->target_events - row->other_events;
        if (row->tick <= request->horizon) {
            *included = i + 1;
            result->at_risk_after_horizon = survivors - row->lost;
            if (at_risk != 0 && result->at_risk_after_horizon == 0) {
                if (survivors == 0) {
                    result->support = PS2_INCIDENCE_TERMINAL_COMPLETE;
                } else {
                    result->support = PS2_INCIDENCE_SUPPORT_ENDS_AT_HORIZON;
                    beyond_support = row->tick < request->horizon;
                }
            }
        }
        at_risk = survivors - row->lost;
        previous = row->tick;
    }
    if (beyond_support || request->horizon > request->observed_through_tick) {
        return PS2_INCIDENCE_UNSUPPORTED_HORIZON;
    }
    return PS2_INCIDENCE_OK;
}

ps2_incidence_status ps2_cumulative_incidence(const ps2_incidence_request *request,
    ps2_incidence_result *out)
{
    if (request == NULL || out == NULL || (request->length != 0 && request->rows == NULL)) {
        return PS2_INCIDENCE_INVALID_ARGUMENT;
    }
    if (request->initial_count == 0) {
        return PS2_INCIDENCE_EMPTY;
    }
    if (request->initial_count > (UINT64_C(1) << 53) || request->length > UINT64_C(1000000)) {
        return PS2_INCIDENCE_UNSUPPORTED;
    }
    uint64_t included = 0;
    ps2_incidence_result result = {0};
    const ps2_incidence_status status = validate_rows(request, &result, &included);
    if (status != PS2_INCIDENCE_OK) {
        return status;
    }
    volatile double smallest = DBL_TRUE_MIN;
    if (fegetround() != FE_TONEAREST || smallest * 2.0 != 0x1p-1073) {
        return PS2_INCIDENCE_NUMERICAL_FAILURE;
    }

    enclosure survival = {1.0, 1.0};
    enclosure target = {0.0, 0.0};
    bool target_zero = true;
    uint64_t at_risk = request->initial_count;
    for (uint64_t i = 0; i < included; ++i) {
        const ps2_incidence_row *row = &request->rows[i];
        const uint64_t survivors = at_risk - row->target_events - row->other_events;
        if (row->target_events != 0) {
            const enclosure increment = multiply(survival, ratio(row->target_events, at_risk));
            target = target_zero ? increment : add(target, increment);
            target_zero = false;
        }
        if (survivors != at_risk) {
            survival = survivors == 0 ? (enclosure){0.0, 0.0}
                : multiply(survival, ratio(survivors, at_risk));
        }
        at_risk = survivors - row->lost;
    }
    result.survival = summarize(survival, result.support == PS2_INCIDENCE_TERMINAL_COMPLETE);
    result.target = summarize(target, target_zero);
    *out = result;
    return PS2_INCIDENCE_OK;
}
