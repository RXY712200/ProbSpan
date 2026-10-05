#include "probspan/probspan.h"

int main(void) {
    return probspan_abi_version() == 1u ? 0 : 1;
}
