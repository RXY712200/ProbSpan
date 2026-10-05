#ifndef PROBSPAN_PROBSPAN_H
#define PROBSPAN_PROBSPAN_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PROBSPAN_OK = 0,
    PROBSPAN_INVALID_ARGUMENT,
    PROBSPAN_RAW_PROBABILITY,
    PROBSPAN_SUBJECTIVE_DOMAIN,
    PROBSPAN_HISTORY_COUNTS,
    PROBSPAN_ODDS_SYNTAX,
    PROBSPAN_ODDS_RANGE,
    /* The private Beta solver could not produce a trustworthy interval. */
    PROBSPAN_NUMERICAL_FAILURE
} probspan_status;

typedef enum {
    PROBSPAN_NO_HISTORY = 0,
    PROBSPAN_INSUFFICIENT,
    PROBSPAN_VALID
} probspan_history_state;

typedef struct {
    int32_t raw_percent;
    int32_t used_percent;
    double probability;
    double lower;
    double upper;
    double logit_half_width;
    uint32_t model_version;
} probspan_subjective_result;

typedef struct {
    int64_t event_count;
    int64_t complement_count;
    uint64_t sample_size;
    probspan_history_state state;
    bool statistically_ready;
    /* False for NO_HISTORY: probability/lower/upper must not be read. */
    bool has_estimate;
    double probability;
    double lower;
    double upper;
    uint32_t model_version;
    uint32_t gate_version;
} probspan_history_result;

unsigned probspan_abi_version(void);
/* A non-OK return leaves the caller's output object unchanged. */
probspan_status probspan_subjective_half_width(double probability, double *half_width);
probspan_status probspan_subjective_estimate(int32_t raw_percent,
                                             probspan_subjective_result *result);
probspan_status probspan_odds_validate(double odds, double *validated);
/* Full-string ASCII decimal grammar: digits, then optional dot and digits. */
probspan_status probspan_odds_parse(const char *text, double *validated);
probspan_status probspan_history_estimate(int64_t event_count, int64_t complement_count,
                                          probspan_history_result *result);

#ifdef __cplusplus
}
#endif

#endif
