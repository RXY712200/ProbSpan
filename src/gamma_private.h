#ifndef PROBSPAN_GAMMA_PRIVATE_H
#define PROBSPAN_GAMMA_PRIVATE_H

#define PS_LOG_SQRT_TWO_PI 0.91893853320467274178032973640562

/* Positive arguments only, as required by the private Beta machinery. */
double ps_stirling_remainder(double argument);
double ps_log_gamma_positive(double argument);

#endif
