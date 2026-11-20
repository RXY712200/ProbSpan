#include <string.h>
#include <probspan_models/beta_predict.h>
#include <probspan_models/version.h>
#include <probspan_models/binomial_interval.h>

int main(void)
{
    ps2_binomial_result interval;
    if (ps2_binomial_interval(PS2_BINOMIAL_CLOPPER_PEARSON, 0, 10, .05,
            PS2_BINOMIAL_UPPER_ONE_SIDED, &interval) != PS2_BINOMIAL_OK
        || interval.lower != 0.0 || interval.upper < .25886 || interval.upper > .25887) {
        return 1;
    }
    ps2_beta_posterior posterior;
    ps2_beta_prediction prediction;
    if (ps2_beta_update((ps2_beta_shapes){1, 1}, 1, 2, &posterior) != PS2_BETA_OK
        || ps2_beta_predict(&posterior, 1, 1, &prediction) != PS2_BETA_OK
        || posterior.event_probability != .4 || prediction.pmf < .399999
        || prediction.pmf > .400001) {
        return 2;
    }
    return strcmp(PROBSPAN_MODELS_VERSION_STRING, "2.0.0") != 0
        || ps2_abi_version() != 1u;
}
