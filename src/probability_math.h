#ifndef PROBSPAN_PROBABILITY_MATH_H
#define PROBSPAN_PROBABILITY_MATH_H

#include <math.h>

/* Keep the frozen quotient-then-log arithmetic shared by subjective bounds
   and S geometry. log(p)-log1p(-p) is not its literal v1 evaluation order. */
static inline double ps_logit(double probability) {
    return log(probability / (1.0 - probability));
}

#endif
