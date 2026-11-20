#include <probspan_models/incidence.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    ps2_incidence_request request;
    while (scanf("%" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64,
                 &request.initial_count, &request.observed_through_tick,
                 &request.horizon, &request.length) == 4) {
        if (request.length > 1000000) {
            return 1;
        }
        ps2_incidence_row *rows = calloc((size_t)request.length, sizeof *rows);
        if (request.length != 0 && rows == NULL) {
            return 1;
        }
        for (uint64_t i = 0; i < request.length; ++i) {
            if (scanf("%" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64,
                      &rows[i].tick, &rows[i].target_events, &rows[i].other_events,
                      &rows[i].lost) != 4) {
                free(rows);
                return 1;
            }
        }
        request.rows = rows;
        ps2_incidence_result out;
        unsigned char saved[sizeof out];
        memset(&out, 0xa5, sizeof out);
        memcpy(saved, &out, sizeof out);
        const ps2_incidence_status status = ps2_cumulative_incidence(&request, &out);
        free(rows);
        if (status != PS2_INCIDENCE_OK) {
            printf("%d %d\n", status, memcmp(saved, &out, sizeof out) == 0);
        } else {
            printf("0 %d %" PRIu64 " %d %a %a %a %d %a %a %a\n",
                   out.support, out.at_risk_after_horizon,
                   out.survival.precision, out.survival.lower, out.survival.estimate,
                   out.survival.upper, out.target.precision, out.target.lower,
                   out.target.estimate, out.target.upper);
        }
    }
    return feof(stdin) ? 0 : 1;
}
