#include <string.h>
#include <probspan_models/version.h>

int main(void)
{
    return strcmp(PROBSPAN_MODELS_VERSION_STRING, "2.0.0") != 0
        || ps2_abi_version() != 1u;
}
