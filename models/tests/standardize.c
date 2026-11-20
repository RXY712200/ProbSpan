#include <probspan_models/standardize.h>
#include <fenv.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "%d: %s\n", __LINE__, #x); return 1; } } while (0)
#define FAIL(call, status) do { CHECK((call) == (status)); \
    CHECK(memcmp(saved, &out, sizeof out) == 0); } while (0)

int main(void)
{
    ps2_standardized_risk out;
    const double eta = nextafter(0.0, 1.0);
    ps2_fixed_stratum rows[] = {{.8, PS2_RISK_KNOWN, .1}, {.2, PS2_RISK_KNOWN, .4}};
    CHECK(ps2_standardize_fixed(rows, 2, &out) == PS2_STANDARDIZE_OK);
    CHECK(out.kind == PS2_STANDARDIZE_IDENTIFIED && fabs(out.result.point.value - .16) < 1e-15);
    rows[1].support = PS2_RISK_UNKNOWN;
    rows[1].conditional_risk = NAN;
    CHECK(ps2_standardize_fixed(rows, 2, &out) == PS2_STANDARDIZE_OK);
    CHECK(out.kind == PS2_STANDARDIZE_PARTIAL);
    CHECK(fabs(out.result.partial.lower.lower - .08) < 1e-15);
    CHECK(fabs(out.result.partial.upper.upper - .28) < 1e-15);
    rows[0] = (ps2_fixed_stratum){1, PS2_RISK_KNOWN, 0};
    rows[1].target_weight = eta;
    CHECK(ps2_standardize_fixed(rows, 2, &out) == PS2_STANDARDIZE_OK);
    CHECK(out.kind == PS2_STANDARDIZE_PARTIAL && out.result.partial.upper.upper == eta);
    rows[1] = (ps2_fixed_stratum){eta, PS2_RISK_KNOWN, eta};
    CHECK(ps2_standardize_fixed(rows, 2, &out) == PS2_STANDARDIZE_OK);
    CHECK(out.kind == PS2_STANDARDIZE_IDENTIFIED && out.result.point.value == 0);
    CHECK(out.result.point.encoding == PS2_POINT_ROUNDED_ZERO);
    CHECK(out.result.point.enclosure.lower == 0 && !signbit(out.result.point.enclosure.lower));
    CHECK(out.result.point.enclosure.upper == eta);
    rows[1] = (ps2_fixed_stratum){-0.0, PS2_RISK_UNKNOWN, NAN};
    CHECK(ps2_standardize_fixed(rows, 2, &out) == PS2_STANDARDIZE_OK);
    CHECK(out.kind == PS2_STANDARDIZE_IDENTIFIED && out.result.point.encoding == PS2_POINT_EXACT);
    rows[0].support = PS2_RISK_UNKNOWN;
    CHECK(ps2_standardize_fixed(rows, 2, &out) == PS2_STANDARDIZE_OK);
    CHECK(out.kind == PS2_STANDARDIZE_PARTIAL && out.result.partial.lower.lower == 0
        && out.result.partial.upper.upper == 1);

    unsigned char saved[sizeof out];
    memcpy(saved, &out, sizeof out);
    FAIL(ps2_standardize_fixed(NULL, 0, &out), PS2_STANDARDIZE_INVALID_ARGUMENT);
    FAIL(ps2_standardize_fixed(rows, 0, &out), PS2_STANDARDIZE_EMPTY);
    FAIL(ps2_standardize_fixed(rows, UINT64_MAX, &out), PS2_STANDARDIZE_UNSUPPORTED);
    CHECK(ps2_standardize_fixed(rows, 1, NULL) == PS2_STANDARDIZE_INVALID_ARGUMENT);
    rows[0].target_weight = 3;
    rows[1].support = (ps2_risk_support)9;
    FAIL(ps2_standardize_fixed(rows, 2, &out), PS2_STANDARDIZE_INVALID_ARGUMENT);
    rows[1].support = PS2_RISK_KNOWN;
    FAIL(ps2_standardize_fixed(rows, 2, &out), PS2_STANDARDIZE_INVALID_ARGUMENT);
    rows[1].conditional_risk = 1;
    FAIL(ps2_standardize_fixed(rows, 2, &out), PS2_STANDARDIZE_UNSUPPORTED);
    rows[0].target_weight = NAN;
    FAIL(ps2_standardize_fixed(rows, 2, &out), PS2_STANDARDIZE_INVALID_ARGUMENT);
    rows[0].target_weight = INFINITY;
    FAIL(ps2_standardize_fixed(rows, 2, &out), PS2_STANDARDIZE_INVALID_ARGUMENT);
    rows[0].target_weight = -1;
    FAIL(ps2_standardize_fixed(rows, 2, &out), PS2_STANDARDIZE_INVALID_ARGUMENT);
    rows[0].target_weight = 0;
    FAIL(ps2_standardize_fixed(rows, 2, &out), PS2_STANDARDIZE_UNSUPPORTED);
    rows[0].target_weight = 1;
    CHECK(fesetround(FE_UPWARD) == 0);
    const ps2_standardize_status status = ps2_standardize_fixed(rows, 2, &out);
    CHECK(fesetround(FE_TONEAREST) == 0);
    CHECK(status == PS2_STANDARDIZE_NUMERICAL_FAILURE && memcmp(saved, &out, sizeof out) == 0);
    return 0;
}
