#include <probspan_models/incidence.h>
#include <fenv.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "%d: %s\n", __LINE__, #x); return 1; } } while (0)
#define FAIL(code) do { CHECK(ps2_cumulative_incidence(&request, &out) == (code)); \
    CHECK(memcmp(saved, &out, sizeof out) == 0); } while (0)

int main(void)
{
    ps2_incidence_row rows[] = {{1, 2, 3, 0}, {2, 1, 0, 0}};
    ps2_incidence_request request = {10, 3, rows, 2, 0};
    ps2_incidence_result out;
    CHECK(ps2_cumulative_incidence(&request, &out) == PS2_INCIDENCE_OK);
    CHECK(out.survival.lower == 1 && out.target.precision == PS2_INCIDENCE_STRUCTURAL_ZERO);
    request.horizon = 1;
    CHECK(ps2_cumulative_incidence(&request, &out) == PS2_INCIDENCE_OK);
    CHECK(fabs(out.target.estimate - .2) < 1e-15 && fabs(out.survival.estimate - .5) < 1e-15);
    CHECK(out.at_risk_after_horizon == 5);
    request.horizon = 2;
    CHECK(ps2_cumulative_incidence(&request, &out) == PS2_INCIDENCE_OK);
    CHECK(fabs(out.target.estimate - .3) < 1e-15 && fabs(out.survival.estimate - .4) < 1e-15);
    CHECK(out.target.upper < .36);
    rows[0].lost = 2;
    CHECK(ps2_cumulative_incidence(&request, &out) == PS2_INCIDENCE_OK);
    CHECK(fabs(out.target.estimate - (0.2 + 0.5/3)) < 1e-15);
    rows[1].lost = 2;
    CHECK(ps2_cumulative_incidence(&request, &out) == PS2_INCIDENCE_OK);
    CHECK(out.support == PS2_INCIDENCE_SUPPORT_ENDS_AT_HORIZON);
    unsigned char saved[sizeof out];
    memcpy(saved, &out, sizeof out);
    request.horizon = 3;
    FAIL(PS2_INCIDENCE_UNSUPPORTED_HORIZON);
    request.horizon = 4;
    rows[1].tick = 1;
    FAIL(PS2_INCIDENCE_INVALID_ARGUMENT);
    rows[1].tick = 0;
    FAIL(PS2_INCIDENCE_INVALID_ARGUMENT);
    rows[1].tick = 4;
    FAIL(PS2_INCIDENCE_INVALID_ARGUMENT);
    rows[1].tick = 2;
    rows[1].target_events = UINT64_MAX;
    FAIL(PS2_INCIDENCE_INVALID_ARGUMENT);
    request.initial_count = 0;
    FAIL(PS2_INCIDENCE_EMPTY);
    request.initial_count = UINT64_MAX;
    FAIL(PS2_INCIDENCE_UNSUPPORTED);
    request.initial_count = 10;
    request.length = UINT64_MAX;
    FAIL(PS2_INCIDENCE_UNSUPPORTED);
    request.length = 2;
    request.rows = NULL;
    FAIL(PS2_INCIDENCE_INVALID_ARGUMENT);
    CHECK(ps2_cumulative_incidence(NULL, &out) == PS2_INCIDENCE_INVALID_ARGUMENT);
    CHECK(ps2_cumulative_incidence(&request, NULL) == PS2_INCIDENCE_INVALID_ARGUMENT);
    request.horizon = 3;
    request.length = 0;
    CHECK(fesetround(FE_UPWARD) == 0);
    const ps2_incidence_status status = ps2_cumulative_incidence(&request, &out);
    CHECK(fesetround(FE_TONEAREST) == 0);
    CHECK(status == PS2_INCIDENCE_NUMERICAL_FAILURE && memcmp(saved, &out, sizeof out) == 0);
    CHECK(ps2_cumulative_incidence(&request, &out) == PS2_INCIDENCE_OK);
    CHECK(out.target.upper == 0 && out.survival.lower == 1 && out.at_risk_after_horizon == 10);

    rows[0] = (ps2_incidence_row){0, 0, 10, 0};
    rows[1] = (ps2_incidence_row){1, 0, 0, 0};
    request.rows = rows;
    request.length = 2;
    CHECK(ps2_cumulative_incidence(&request, &out) == PS2_INCIDENCE_OK);
    CHECK(out.support == PS2_INCIDENCE_TERMINAL_COMPLETE && out.at_risk_after_horizon == 0);
    CHECK(out.survival.precision == PS2_INCIDENCE_STRUCTURAL_ZERO && out.target.lower == 0);
    memcpy(saved, &out, sizeof out);
    rows[1].lost = 1;
    FAIL(PS2_INCIDENCE_INVALID_ARGUMENT);
    return 0;
}
