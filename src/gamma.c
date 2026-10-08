#include "gamma_private.h"

#include <math.h>

#define STIRLING_MIN_ARGUMENT 8.0

/* lgamma may write a process-global signgam, even for positive arguments.
   Small positive Gamma values are representable, so log(tgamma) avoids that
   hidden state. For larger inputs use the same remainder already required
   by the large-shape Beta integrator, without overflowing tgamma. */
double ps_log_gamma_positive(double argument) {
    if (argument < STIRLING_MIN_ARGUMENT) { return log(tgamma(argument)); }
    return (argument - 0.5) * log(argument) - argument + PS_LOG_SQRT_TWO_PI +
           ps_stirling_remainder(argument);
}

/* DLMF 5.11.1: at z>=8 the omitted term after z^-17 is below 1e-17.
   Retain the small correction directly rather than subtracting enormous
   log-Gamma values. This is numerical evaluation, not a different Beta law. */
double ps_stirling_remainder(double z) {
    if (z < STIRLING_MIN_ARGUMENT) {
        return log(tgamma(z)) - ((z - 0.5) * log(z) - z + PS_LOG_SQRT_TWO_PI);
    }
    const double inverse = 1.0 / z;
    const double square = inverse * inverse;
    return inverse * (1.0 / 12.0 + square * (-1.0 / 360.0 +
           square * (1.0 / 1260.0 + square * (-1.0 / 1680.0 +
           square * (1.0 / 1188.0 + square * (-691.0 / 360360.0 +
           square * (1.0 / 156.0 + square * (-3617.0 / 122400.0 +
           square * (43867.0 / 244188.0)))))))));
}
