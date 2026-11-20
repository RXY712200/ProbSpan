#include <probspan_models/beta_predict.h>

#include <fenv.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { if (!(expr)) { fprintf(stderr, "%d: %s\n", __LINE__, #expr); return 1; } } while (0)

int main(void)
{
    ps2_beta_posterior p, other;
    ps2_beta_prediction prediction, mirror;
    CHECK(ps2_beta_update((ps2_beta_shapes){1, 1}, 0, 0, &p) == PS2_BETA_OK);
    CHECK(p.prior_only && p.shapes.a == 1 && p.shapes.b == 1);
    CHECK(ps2_beta_update((ps2_beta_shapes){1, 1}, 1, 2, &p) == PS2_BETA_OK);
    CHECK(!p.prior_only && p.shapes.a == 2 && p.shapes.b == 3 && p.event_probability == .4);
    CHECK(ps2_beta_predict(&p, 0, 0, &prediction) == PS2_BETA_OK);
    CHECK(prediction.pmf == 1 && prediction.log_pmf == 0 && prediction.mean == 0
        && prediction.variance == 0 && prediction.mass_state == PS2_BETA_MASS_EXACT_ONE);
    CHECK(ps2_beta_predict(&p, 1, 1, &prediction) == PS2_BETA_OK);
    CHECK(fabs(prediction.pmf - .4) < 0x1p-50 && fabs(prediction.variance - .24) < 0x1p-50);
    CHECK(ps2_beta_predict(&p, 10, 3, &prediction) == PS2_BETA_OK);
    CHECK(prediction.mean == 4 && fabs(prediction.variance - 6.0) < 0x1p-48);
    CHECK(ps2_beta_update((ps2_beta_shapes){1, 1}, 2, 1, &other) == PS2_BETA_OK);
    CHECK(ps2_beta_predict(&other, 10, 7, &mirror) == PS2_BETA_OK);
    CHECK(prediction.log_pmf == mirror.log_pmf);
    CHECK(ps2_beta_update((ps2_beta_shapes){.5, 1000000}, 0, 0, &p) == PS2_BETA_OK);
    CHECK(ps2_beta_predict(&p, 10000, 10000, &prediction) == PS2_BETA_OK);
    CHECK(prediction.pmf == 0 && !signbit(prediction.pmf) && isfinite(prediction.log_pmf)
        && prediction.mass_state == PS2_BETA_MASS_ROUNDED_ZERO);

    unsigned char before[sizeof prediction];
    memcpy(before, &prediction, sizeof prediction);
    CHECK(ps2_beta_predict(&p, 0, 1, &prediction) == PS2_BETA_INVALID_ARGUMENT);
    CHECK(ps2_beta_predict(&p, UINT64_MAX, 0, &prediction) == PS2_BETA_UNSUPPORTED);
    other = p;
    other.event_probability = NAN;
    CHECK(ps2_beta_predict(&other, 1, 0, &prediction) == PS2_BETA_INVALID_ARGUMENT);
    other = p;
    other.prior_only = false;
    CHECK(ps2_beta_predict(&other, 1, 0, &prediction) == PS2_BETA_INVALID_ARGUMENT);
    other = p;
    other.shapes.a = INFINITY;
    CHECK(ps2_beta_predict(&other, 1, 0, &prediction) == PS2_BETA_INVALID_ARGUMENT);
    CHECK(ps2_beta_predict(NULL, 1, 0, &prediction) == PS2_BETA_INVALID_ARGUMENT);
    CHECK(fesetround(FE_UPWARD) == 0);
    const ps2_beta_status status = ps2_beta_predict(&p, 1, 0, &prediction);
    CHECK(fesetround(FE_TONEAREST) == 0);
    CHECK(status == PS2_BETA_NUMERICAL_FAILURE);
    CHECK(memcmp(before, &prediction, sizeof prediction) == 0);

    CHECK(ps2_beta_update((ps2_beta_shapes){1, 0x1.4ca2b6548a0c9p+8},
        0, 0, &other) == PS2_BETA_OK);
    CHECK(ps2_beta_predict(&other, 1000, 1000, &prediction) == PS2_BETA_NUMERICAL_FAILURE);
    CHECK(memcmp(before, &prediction, sizeof prediction) == 0);

    unsigned char prior_bytes[sizeof p];
    memcpy(prior_bytes, &p, sizeof p);
    CHECK(ps2_beta_update((ps2_beta_shapes){NAN, 1}, 0, 0, &p) == PS2_BETA_INVALID_ARGUMENT);
    CHECK(ps2_beta_update((ps2_beta_shapes){-1, INFINITY}, 0, 0, &p) == PS2_BETA_INVALID_ARGUMENT);
    CHECK(ps2_beta_update((ps2_beta_shapes){nextafter(.5, 0), 1}, 0, 0, &p) == PS2_BETA_UNSUPPORTED);
    CHECK(ps2_beta_update((ps2_beta_shapes){1, nextafter(1000000, INFINITY)}, 0, 0, &p) == PS2_BETA_UNSUPPORTED);
    CHECK(ps2_beta_update((ps2_beta_shapes){1, 1}, 1, UINT64_MAX, &p) == PS2_BETA_UNSUPPORTED);
    CHECK(ps2_beta_update((ps2_beta_shapes){1, 1}, UINT64_MAX, 1, &p) == PS2_BETA_UNSUPPORTED);
    CHECK(memcmp(prior_bytes, &p, sizeof p) == 0);
    return 0;
}
