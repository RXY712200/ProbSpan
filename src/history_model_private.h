#ifndef PROBSPAN_HISTORY_MODEL_PRIVATE_H
#define PROBSPAN_HISTORY_MODEL_PRIVATE_H

#include <stdint.h>
#include "model_v1.h"

/* Shared shape construction keeps credible intervals and posterior threshold
   probabilities on the same frozen Jeffreys model and binary64 conversion. */
static inline void ps_history_shapes(int64_t events, int64_t complements,
                                     double *alpha, double *beta) {
    *alpha = (double)events + PS_JEFFREYS_ALPHA;
    *beta = (double)complements + PS_JEFFREYS_BETA;
}

#endif
