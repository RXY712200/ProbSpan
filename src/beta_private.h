#ifndef PROBSPAN_BETA_PRIVATE_H
#define PROBSPAN_BETA_PRIVATE_H

#include <stdbool.h>

bool ps_beta_cdf(double x, double alpha, double beta, double *value);
bool ps_beta_quantile(double probability, double alpha, double beta, double *value);

#endif
