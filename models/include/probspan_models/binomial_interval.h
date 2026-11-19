#ifndef PROBSPAN_MODELS_BINOMIAL_INTERVAL_H
#define PROBSPAN_MODELS_BINOMIAL_INTERVAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PS2_BINOMIAL_WILSON,
    PS2_BINOMIAL_CLOPPER_PEARSON
} ps2_binomial_method;

typedef enum {
    PS2_BINOMIAL_TWO_SIDED,
    PS2_BINOMIAL_LOWER_ONE_SIDED,
    PS2_BINOMIAL_UPPER_ONE_SIDED
} ps2_binomial_sidedness;

typedef enum {
    PS2_BINOMIAL_OK,
    PS2_BINOMIAL_INVALID_ARGUMENT,
    PS2_BINOMIAL_EMPTY,
    PS2_BINOMIAL_UNSUPPORTED,
    PS2_BINOMIAL_NUMERICAL_FAILURE
} ps2_binomial_status;

typedef struct {
    double lower;
    double upper;
    double alpha;
    ps2_binomial_method method;
    ps2_binomial_sidedness sidedness;
} ps2_binomial_result;

/* Fixed-n iid Bernoulli confidence interval. On failure, out is unchanged. */
ps2_binomial_status ps2_binomial_interval(ps2_binomial_method method,
    uint64_t events, uint64_t n, double alpha, ps2_binomial_sidedness sidedness,
    ps2_binomial_result *out);

#ifdef __cplusplus
}
#endif

#endif
