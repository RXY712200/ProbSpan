#include <stdio.h>
#include "probspan/probspan.h"

int main(void) {
    probspan_analysis analysis;
    const probspan_status status = probspan_compose_analysis(60, 19, 1, 2.0, 3.0, &analysis);
    if (status != PROBSPAN_OK) { fprintf(stderr, "Analysis failed: %d\n", (int)status); return 1; }
    printf("ProbSpan %s: event EV interval [%.6f, %.6f], center %.6f\n",
        PROBSPAN_VERSION_STRING, analysis.subjective_analysis.event.ev.minimum,
        analysis.subjective_analysis.event.ev.maximum, analysis.subjective_analysis.event.ev.center);
    if (analysis.historical_analysis.available) {
        printf("Historical probability of positive event EV: %.6f\n",
            analysis.historical_analysis.event.positive_ev_probability);
    }
    return 0;
}
