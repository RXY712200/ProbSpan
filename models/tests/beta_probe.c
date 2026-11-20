#include <probspan_models/beta_predict.h>
#include <inttypes.h>
#include <stdio.h>

int main(void)
{
    ps2_beta_shapes prior;
    uint64_t e, f, n, k;
    while (scanf("%la %la %" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64,
                 &prior.a, &prior.b, &e, &f, &n, &k) == 6) {
        ps2_beta_posterior posterior = {0};
        ps2_beta_prediction prediction = {0};
        ps2_beta_status status = ps2_beta_update(prior, e, f, &posterior);
        if (status == PS2_BETA_OK) {
            status = ps2_beta_predict(&posterior, n, k, &prediction);
        }
        printf("%d %a %a %a %a %d %a %a %a %d\n", status,
               prediction.pmf, prediction.log_pmf, prediction.mean, prediction.variance,
               prediction.mass_state, posterior.shapes.a, posterior.shapes.b,
               posterior.event_probability, posterior.prior_only);
    }
    return feof(stdin) ? 0 : 1;
}
