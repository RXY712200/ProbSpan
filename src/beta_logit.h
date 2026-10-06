#ifndef PROBSPAN_BETA_LOGIT_H
#define PROBSPAN_BETA_LOGIT_H

#include <stdbool.h>

bool ps_beta_logit_cdf(double x, double alpha, double beta, double *value);
bool ps_beta_logit_quantile(double probability, double alpha, double beta, double *value);

#endif
