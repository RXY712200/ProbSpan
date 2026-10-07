#include "probspan/probspan.h"
#include "subjective_input.h"

#include <stddef.h>

probspan_status probspan_provenance_transition(const probspan_provenance *previous,
    int32_t previous_raw_percent, int32_t current_raw_percent,
    bool subject_changed, bool evidence_exposed_now, probspan_provenance *result) {
    if (previous == NULL || result == NULL) { return PROBSPAN_INVALID_ARGUMENT; }
    if (!ps_valid_raw_percent(previous_raw_percent) || !ps_valid_raw_percent(current_raw_percent)) {
        return PROBSPAN_RAW_PROBABILITY;
    }
    /* Compare raw identity: 0 -> 1 changes provenance even though both
       estimates use 1%. Newly exposed evidence cannot retroactively
       compromise the change preceding it in this same operation. */
    const bool changed = subject_changed || previous_raw_percent != current_raw_percent;
    const probspan_provenance next = {
        previous->evidence_exposed || evidence_exposed_now,
        previous->subjective_independence_compromised || (previous->evidence_exposed && changed)
    };
    /* Both facts are sticky. v1 intentionally provides no reset operation. */
    *result = next;
    return PROBSPAN_OK;
}
