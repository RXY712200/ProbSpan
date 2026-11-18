#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#include <probspan/probspan.h>

static bool read_count(const char *input, int64_t *count) {
    if (*input == '\0') {
        return false;
    }
    for (const char *p = input; *p != '\0'; ++p) {
        if (*p < '0' || *p > '9') {
            return false;
        }
    }
    errno = 0;
    const intmax_t value = strtoimax(input, NULL, 10);
    if (errno == ERANGE || value > INT64_MAX) {
        return false;
    }
    *count = (int64_t)value;
    return true;
}

static const char *state_name(probspan_history_state state) {
    switch (state) {
        case PROBSPAN_NO_HISTORY: return "NO_HISTORY";
        case PROBSPAN_INSUFFICIENT: return "INSUFFICIENT";
        case PROBSPAN_VALID: return "VALID";
    }
    return NULL;
}

int main(int argc, char **argv) {
    int64_t events, complements;
    if (argc != 3 || !read_count(argv[1], &events) || !read_count(argv[2], &complements)) {
        fputs("usage: device-history-v1 nonnegative-events nonnegative-complements\n", stderr);
        return EXIT_FAILURE;
    }
    probspan_history_result result;
    const probspan_status status = probspan_history_estimate(events, complements, &result);
    if (status != PROBSPAN_OK) {
        printf("{\"c_status\":%d}\n", (int)status);
        return EXIT_SUCCESS;
    }
    const char *state = state_name(result.state);
    if (state == NULL) {
        return EXIT_FAILURE;
    }
    printf("{\"c_status\":0,\"state\":\"%s\",\"size\":%" PRIu64
           ",\"statistically_ready\":%s,\"model_version\":%" PRIu32
           ",\"gate_version\":%" PRIu32 ",\"abi_version\":%" PRIu32
           ",\"product_version\":\"%s\",\"estimate\":",
           state, result.sample_size, result.statistically_ready ? "true" : "false",
           result.model_version, result.gate_version, probspan_abi_version(),
           PROBSPAN_VERSION_STRING);
    if (result.has_estimate) {
        printf("{\"mean\":%.17g,\"lower\":%.17g,\"upper\":%.17g}}\n",
               result.probability, result.lower, result.upper);
    } else {
        puts("null}");
    }
    return EXIT_SUCCESS;
}
