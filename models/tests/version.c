#include <string.h>
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
    return strcmp(PROBSPAN_MODELS_VERSION_STRING, "2.0.0") != 0
        || ps2_abi_version() != 1u;
}
