#ifndef PROBSPAN_SUBJECTIVE_INPUT_H
#define PROBSPAN_SUBJECTIVE_INPUT_H

#include <stdbool.h>
#include <stdint.h>

/* Raw identity belongs to both estimation and provenance. Keep its accepted
   domain in one place without making provenance calculate an estimate. */
static inline bool ps_valid_raw_percent(int32_t raw_percent) {
    return raw_percent >= 0 && raw_percent <= 100;
}

#endif
