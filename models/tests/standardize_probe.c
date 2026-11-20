#include <probspan_models/standardize.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    unsigned n;
    while (scanf("%u", &n) == 1) {
        ps2_fixed_stratum rows[1024];
        if (n > 1024) {
            return 1;
        }
        for (unsigned i = 0; i < n; ++i) {
            int support;
            if (scanf("%la %d %la", &rows[i].target_weight, &support, &rows[i].conditional_risk) != 3) {
                return 1;
            }
            rows[i].support = (ps2_risk_support)support;
        }
        ps2_standardized_risk out;
        unsigned char saved[sizeof out];
        memset(&out, 0xa5, sizeof out);
        memcpy(saved, &out, sizeof out);
        const ps2_standardize_status status = ps2_standardize_fixed(rows, n, &out);
        if (status != PS2_STANDARDIZE_OK) {
            printf("%d %d\n", status, memcmp(saved, &out, sizeof out) == 0);
        } else if (out.kind == PS2_STANDARDIZE_IDENTIFIED) {
            const ps2_standardized_point point = out.result.point;
            printf("0 0 %d %a %a %a\n", point.encoding, point.value, point.enclosure.lower,
                   point.enclosure.upper);
        } else {
            printf("0 %d %a %a %a %a\n", out.kind,
                out.result.partial.lower.lower, out.result.partial.lower.upper,
                out.result.partial.upper.lower, out.result.partial.upper.upper);
        }
    }
    return feof(stdin) ? 0 : 1;
}
