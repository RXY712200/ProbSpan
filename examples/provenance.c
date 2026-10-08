#include <stdio.h>
#include "probspan/probspan.h"

int main(void) {
    probspan_provenance state = {false, false};
    /* First exposure cannot retroactively compromise the current raw change. */
    if (probspan_provenance_transition(&state, 0, 1, false, true, &state) != PROBSPAN_OK) { return 1; }
    printf("First exposure: exposed=%d compromised=%d\n",
        (int)state.evidence_exposed, (int)state.subjective_independence_compromised);
    if (probspan_provenance_transition(&state, 1, 60, false, false, &state) != PROBSPAN_OK) { return 1; }
    printf("Later change: exposed=%d compromised=%d\n",
        (int)state.evidence_exposed, (int)state.subjective_independence_compromised);
    return 0;
}
