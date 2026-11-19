#include <probspan/probspan.h>
#include <probspan_models/version.h>

int main(void)
{
    return probspan_abi_version() != 1u || ps2_abi_version() != 1u;
}
