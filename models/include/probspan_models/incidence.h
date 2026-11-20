#ifndef PROBSPAN_MODELS_INCIDENCE_H
#define PROBSPAN_MODELS_INCIDENCE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint64_t tick;
    uint64_t target_events;
    uint64_t other_events;
    uint64_t lost;
} ps2_incidence_row;

typedef struct {
    uint64_t initial_count;
    uint64_t observed_through_tick;
    const ps2_incidence_row *rows;
    uint64_t length;
    uint64_t horizon;
} ps2_incidence_request;

typedef enum {
    PS2_INCIDENCE_OK,
    PS2_INCIDENCE_INVALID_ARGUMENT,
    PS2_INCIDENCE_EMPTY,
    PS2_INCIDENCE_UNSUPPORTED,
    PS2_INCIDENCE_UNSUPPORTED_HORIZON,
    PS2_INCIDENCE_NUMERICAL_FAILURE
} ps2_incidence_status;

typedef enum {
    PS2_INCIDENCE_AT_RISK,
    PS2_INCIDENCE_TERMINAL_COMPLETE,
    PS2_INCIDENCE_SUPPORT_ENDS_AT_HORIZON
} ps2_incidence_support;

typedef enum {
    PS2_INCIDENCE_STRUCTURAL_ZERO,
    PS2_INCIDENCE_POSITIVE_ENCLOSED,
    PS2_INCIDENCE_POSITIVE_NEAR_ZERO
} ps2_incidence_precision;

typedef struct {
    double estimate;
    double lower;
    double upper;
    ps2_incidence_precision precision;
} ps2_incidence_value;

typedef struct {
    ps2_incidence_value survival;
    ps2_incidence_value target;
    uint64_t at_risk_after_horizon;
    ps2_incidence_support support;
} ps2_incidence_result;

/* Request and rows are borrowed for the call. They must not overlap out.
 * The horizon is inclusive. Failure leaves every output byte untouched. */
ps2_incidence_status ps2_cumulative_incidence(const ps2_incidence_request *request,
    ps2_incidence_result *out);

#ifdef __cplusplus
}
#endif

#endif
