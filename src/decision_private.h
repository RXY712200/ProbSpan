#ifndef PROBSPAN_DECISION_PRIVATE_H
#define PROBSPAN_DECISION_PRIVATE_H

#include "probspan/probspan.h"

typedef struct { double center, lower, upper; } ps_probability_interval;

bool ps_valid_probability_interval(ps_probability_interval interval);
ps_probability_interval ps_complement_interval(ps_probability_interval interval);
probspan_ev_interval ps_ev_interval(ps_probability_interval interval, double odds);
probspan_status ps_validate_odds_pair(double event_odds, double complement_odds);
probspan_odds_geometry ps_odds_geometry(double event_odds, double complement_odds);
probspan_ev_state ps_ev_state(double minimum, double maximum);
probspan_odds_combination ps_odds_combination(double inverse_sum);

#endif
