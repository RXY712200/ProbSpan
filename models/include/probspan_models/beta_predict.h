#ifndef PROBSPAN_MODELS_BETA_PREDICT_H
#define PROBSPAN_MODELS_BETA_PREDICT_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PS2_BETA_OK,
    PS2_BETA_INVALID_ARGUMENT,
    PS2_BETA_UNSUPPORTED,
    PS2_BETA_NUMERICAL_FAILURE
} ps2_beta_status;

typedef struct {
    double a;
    double b;
} ps2_beta_shapes;

typedef struct {
    ps2_beta_shapes prior;
    uint64_t events;
    uint64_t nonevents;
    ps2_beta_shapes shapes;
    double event_probability;
    bool prior_only;
} ps2_beta_posterior;

typedef enum {
    PS2_BETA_MASS_EXACT_ONE,
    PS2_BETA_MASS_ENCODED,
    PS2_BETA_MASS_SUBNORMAL,
    PS2_BETA_MASS_ROUNDED_ZERO
} ps2_beta_mass_state;

typedef struct {
    double pmf;
    double log_pmf;
    double mean;
    double variance;
    ps2_beta_mass_state mass_state;
} ps2_beta_prediction;

/* Caller supplies one admissible homogeneous cohort. Failures preserve out. */
ps2_beta_status ps2_beta_update(ps2_beta_shapes prior, uint64_t events,
    uint64_t nonevents, ps2_beta_posterior *out);

/* Pass a posterior produced by ps2_beta_update. Input/output must not overlap. */
ps2_beta_status ps2_beta_predict(const ps2_beta_posterior *posterior,
    uint64_t future_n, uint64_t wanted_k, ps2_beta_prediction *out);

#ifdef __cplusplus
}
#endif

#endif
