#ifndef PROBSPAN_MODELS_VERSION_H
#define PROBSPAN_MODELS_VERSION_H

#include <stdint.h>

#define PROBSPAN_MODELS_VERSION_STRING "2.0.0"

#ifdef __cplusplus
extern "C" {
#endif

/* Reports the ABI generation of the linked Models archive. */
uint32_t ps2_abi_version(void);

#ifdef __cplusplus
}
#endif

#endif
