/* Research probe for B-E006. Build against the frozen sources without modifying them. */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "beta_private.h"
#include "probspan/probspan.h"

int main(int argc, char **argv) {
    double answer = 0.0;
    if (argc == 5 && (strcmp(argv[1], "cdf") == 0 || strcmp(argv[1], "ppf") == 0)) {
        const double a = strtod(argv[2], NULL);
        const double b = strtod(argv[3], NULL);
        const double x = strtod(argv[4], NULL);
        const bool success = strcmp(argv[1], "cdf") == 0
            ? ps_beta_cdf(x, a, b, &answer)
            : ps_beta_quantile(x, a, b, &answer);
        if (!success || !isfinite(answer)) {
            fputs("Beta probe failed\n", stderr);
            return 1;
        }
        printf("%a\n", answer);
        return 0;
    }
    if (argc == 3 && strcmp(argv[1], "odds") == 0) {
        double odds;
        if (probspan_odds_parse(argv[2], &odds) != PROBSPAN_OK) {
            return 1;
        }
        const double threshold = 1.0 / odds;
        printf("%a %a\n", odds, threshold);
        return 0;
    }
    return 2;
}
