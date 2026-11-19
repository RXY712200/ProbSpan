#include <probspan_models/binomial_interval.h>

#include <fenv.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "line %d: %s\n", __LINE__, #expr); return 1; \
} } while (0)

int main(void)
{
    ps2_binomial_result out;
    unsigned char before[sizeof out];
    memset(&out, 0xA5, sizeof out);
    memcpy(before, &out, sizeof out);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 0, 0, .05, 0, &out)
        == PS2_BINOMIAL_EMPTY);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, UINT64_MAX, 0, .05, 0, &out)
        == PS2_BINOMIAL_INVALID_ARGUMENT);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, UINT64_MAX, UINT64_MAX, .05, 0, &out)
        == PS2_BINOMIAL_UNSUPPORTED);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 0, 10, NAN, 0, &out)
        == PS2_BINOMIAL_INVALID_ARGUMENT);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 0, 10, INFINITY, 0, &out)
        == PS2_BINOMIAL_INVALID_ARGUMENT);
    CHECK(ps2_binomial_interval((ps2_binomial_method)-1, 0, 10, .05, 0, &out)
        == PS2_BINOMIAL_INVALID_ARGUMENT);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 0, 10, .05,
        (ps2_binomial_sidedness)3, &out) == PS2_BINOMIAL_INVALID_ARGUMENT);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 0, 10, .05, 0, NULL)
        == PS2_BINOMIAL_INVALID_ARGUMENT);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 0, 10, nextafter(1e-10, 0), 0, &out)
        == PS2_BINOMIAL_UNSUPPORTED);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 0, 10, nextafter(.5, 1), 0, &out)
        == PS2_BINOMIAL_UNSUPPORTED);
    CHECK(fesetround(FE_UPWARD) == 0);
    const ps2_binomial_status status = ps2_binomial_interval(
        PS2_BINOMIAL_CLOPPER_PEARSON, 3, 10, .05, 0, &out);
    CHECK(fesetround(FE_TONEAREST) == 0);
    CHECK(status == PS2_BINOMIAL_NUMERICAL_FAILURE);
    CHECK(memcmp(before, &out, sizeof out) == 0);

    for (int method = 0; method <= 1; ++method) {
        for (int sidedness = 0; sidedness <= 2; ++sidedness) {
            for (unsigned n = 1; n <= 10; ++n) {
                for (unsigned k = 0; k <= n; ++k) {
                    ps2_binomial_result mirror;
                    CHECK(ps2_binomial_interval(method, k, n, .05, sidedness, &out) == 0);
                    CHECK(out.method == (ps2_binomial_method)method && out.alpha == .05);
                    CHECK(out.sidedness == (ps2_binomial_sidedness)sidedness);
                    CHECK(out.lower >= 0 && out.lower <= out.upper && out.upper <= 1);
                    CHECK(!signbit(out.lower) && !signbit(out.upper));
                    if (k == 0 || sidedness == PS2_BINOMIAL_UPPER_ONE_SIDED) {
                        CHECK(out.lower == 0);
                    }
                    if (k == n || sidedness == PS2_BINOMIAL_LOWER_ONE_SIDED) {
                        CHECK(out.upper == 1);
                    }
                    const int mirrored_side = sidedness == 0 ? 0 : 3 - sidedness;
                    CHECK(ps2_binomial_interval(method, n-k, n, .05,
                        mirrored_side, &mirror) == 0);
                    CHECK(fabs(out.lower - (1.0-mirror.upper)) <= 0x1p-37);
                }
            }
        }
    }

    CHECK(ps2_binomial_interval(PS2_BINOMIAL_CLOPPER_PEARSON, 0, 10, .05,
        PS2_BINOMIAL_UPPER_ONE_SIDED, &out) == 0);
    CHECK(fabs(out.upper - 0.2588655508930523) < 0x1p-38);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_WILSON, 1, 2, .05, 0, &out) == 0);
    CHECK(fabs(out.lower - 0.0945312057342307) < 0x1p-45);
    CHECK(ps2_binomial_interval(PS2_BINOMIAL_CLOPPER_PEARSON, 500000, 1000000,
        1e-10, 0, &out) == 0);
    CHECK(out.lower < .5 && out.upper > .5);
    return 0;
}
