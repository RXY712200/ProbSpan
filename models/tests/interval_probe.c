#include <probspan_models/binomial_interval.h>

#include <inttypes.h>
#include <stdio.h>

int main(void)
{
    uint64_t n, k;
    int method, side;
    double alpha;
    while (scanf("%d %" SCNu64 " %" SCNu64 " %la %d", &method, &k, &n, &alpha, &side) == 5) {
        ps2_binomial_result out = {0};
        const int status = ps2_binomial_interval(method, k, n, alpha, side, &out);
        printf("%d %a %a\n", status, out.lower, out.upper);
    }
    return feof(stdin) ? 0 : 1;
}
