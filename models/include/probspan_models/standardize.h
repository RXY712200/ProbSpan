#ifndef PROBSPAN_MODELS_STANDARDIZE_H
#define PROBSPAN_MODELS_STANDARDIZE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PS2_RISK_UNKNOWN,
    PS2_RISK_KNOWN
} ps2_risk_support;

typedef struct {
    double target_weight;
    ps2_risk_support support;
    double conditional_risk;
} ps2_fixed_stratum;

typedef enum {
    PS2_STANDARDIZE_OK,
    PS2_STANDARDIZE_INVALID_ARGUMENT,
    PS2_STANDARDIZE_EMPTY,
    PS2_STANDARDIZE_UNSUPPORTED,
    PS2_STANDARDIZE_NUMERICAL_FAILURE
} ps2_standardize_status;

typedef enum {
    PS2_STANDARDIZE_IDENTIFIED,
    PS2_STANDARDIZE_PARTIAL
} ps2_standardize_kind;

typedef enum {
    PS2_POINT_EXACT,
    PS2_POINT_ROUNDED,
    PS2_POINT_ROUNDED_ZERO
} ps2_point_encoding;

typedef struct {
    double lower;
    double upper;
} ps2_risk_enclosure;

typedef struct {
    double value;
    ps2_point_encoding encoding;
    ps2_risk_enclosure enclosure;
} ps2_standardized_point;

typedef struct {
    ps2_standardize_kind kind;
    union {
        ps2_standardized_point point;
        struct {
            ps2_risk_enclosure lower;
            ps2_risk_enclosure upper;
        } partial;
    } result;
} ps2_standardized_risk;

/* Input and output must not overlap. Read only the active result member.
 * Unknown-stratum risks are ignored. On failure, out is unchanged. */
ps2_standardize_status ps2_standardize_fixed(const ps2_fixed_stratum *strata,
    uint64_t count, ps2_standardized_risk *out);

#ifdef __cplusplus
}
#endif

#endif
