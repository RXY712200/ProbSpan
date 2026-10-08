#include <string.h>
#include <probspan/probspan.h>

int main(void) {
    probspan_analysis result;
    probspan_provenance state = {false, false};
    if (strcmp(PROBSPAN_VERSION_STRING, "1.0.0") != 0 || probspan_abi_version() != 1u) { return 1; }
    if (probspan_compose_analysis(60, 19, 1, 2.0, 2.0, &result) != PROBSPAN_OK) { return 2; }
    if (!result.historical_analysis.available || result.subjective.model_version != 1u ||
        result.history.model_version != 1u || result.history.gate_version != 1u ||
        result.subjective_analysis.analysis_version != 1u) { return 3; }
    if (probspan_provenance_transition(&state, 60, 60, false, true, &state) != PROBSPAN_OK ||
        !state.evidence_exposed || state.subjective_independence_compromised) { return 4; }
    return 0;
}
