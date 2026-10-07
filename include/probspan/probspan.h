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

typedef enum {
    PROBSPAN_ROBUST_POSITIVE = 0,
    PROBSPAN_ROBUST_NEGATIVE,
    PROBSPAN_CROSSES_THRESHOLD
} probspan_ev_state;

typedef enum {
    PROBSPAN_NORMAL_OVERLAP = 0,
    PROBSPAN_CRITICAL,
    PROBSPAN_DOUBLE_POSITIVE_WINDOW
} probspan_odds_combination;

typedef enum {
    PROBSPAN_AGREEMENT_POSITIVE = 0,
    PROBSPAN_AGREEMENT_NEGATIVE,
    PROBSPAN_CONFLICT,
    PROBSPAN_UNCERTAIN,
    PROBSPAN_HISTORY_UNAVAILABLE
} probspan_model_relation;

typedef struct {
    double center;
    double minimum;
    double maximum;
    probspan_ev_state state;
} probspan_ev_interval;

typedef struct {
    double event_break_even;
    double complement_event_break_even;
    double complement_break_even_as_event;
    probspan_odds_combination combination;
} probspan_odds_geometry;

typedef struct {
    probspan_ev_interval ev;
    /* False only for odds exactly 1; robust_margin then has no meaning. */
    bool has_robust_margin;
    double robust_margin;
} probspan_subjective_side;

typedef struct {
    uint32_t analysis_version;
    probspan_odds_geometry geometry;
    probspan_subjective_side event;
    probspan_subjective_side complement_event;
} probspan_subjective_analysis;

typedef struct {
    probspan_ev_interval ev;
    double positive_ev_probability;
} probspan_historical_side;

typedef struct {
    /* False for history not VALID; both side fields must then be ignored. */
    bool available;
    probspan_historical_side event;
    probspan_historical_side complement_event;
} probspan_historical_analysis;

typedef struct {
    bool evidence_exposed;
    bool subjective_independence_compromised;
} probspan_provenance;

/* A complete historical analysis fact, not a cache. Callers own storage and
   must retain these independent versioned results rather than silently
   recomputing them with a later model. */
typedef struct {
    probspan_subjective_result subjective;
    double event_odds;
    double complement_event_odds;
    probspan_subjective_analysis subjective_analysis;
    probspan_history_result history;
    probspan_historical_analysis historical_analysis;
    probspan_model_relation event_relation;
    probspan_model_relation complement_event_relation;
} probspan_analysis;

unsigned probspan_abi_version(void);
/* Non-OK returns leave output unchanged for both operations below.
   Start with {false, false} and equal previous/current raw inputs for an
   initial analysis. Exposure is an observed caller fact, not a display
   request. Clocks and revision lifecycle remain caller responsibilities. */
probspan_status probspan_provenance_transition(const probspan_provenance *previous,
    int32_t previous_raw_percent, int32_t current_raw_percent,
    bool subject_changed, bool evidence_exposed_now, probspan_provenance *result);
probspan_status probspan_compose_analysis(int32_t raw_percent,
    int64_t event_count, int64_t complement_count,
    double event_odds, double complement_event_odds, probspan_analysis *result);

/* A non-OK return leaves the caller's output object unchanged. */
probspan_status probspan_subjective_half_width(double probability, double *half_width);
probspan_status probspan_subjective_estimate(int32_t raw_percent,
                                             probspan_subjective_result *result);
probspan_status probspan_odds_validate(double odds, double *validated);
/* Full-string ASCII decimal grammar: digits, then optional dot and digits. */
probspan_status probspan_odds_parse(const char *text, double *validated);
probspan_status probspan_history_estimate(int64_t event_count, int64_t complement_count,
                                          probspan_history_result *result);

probspan_status probspan_classify_ev(double ev_minimum, double ev_maximum,
                                    probspan_ev_state *state);
probspan_status probspan_classify_odds_combination(double event_odds, double complement_odds,
                                                  probspan_odds_combination *combination);
/* historical_state is ignored when historical_available is false. */
probspan_status probspan_classify_model_relation(probspan_ev_state subjective_state,
                                                 bool historical_available,
                                                 probspan_ev_state historical_state,
                                                 probspan_model_relation *relation);
/* Inputs are estimates produced by the corresponding estimate API. Invalid
   objects/odds leave output unchanged. A non-VALID history returns OK with
   available=false before examining odds or the unavailable estimate fields. */
probspan_status probspan_analyze_subjective(const probspan_subjective_result *subjective,
                                            double event_odds, double complement_odds,
                                            probspan_subjective_analysis *analysis);
probspan_status probspan_analyze_historical(const probspan_history_result *history,
                                            double event_odds, double complement_odds,
                                            probspan_historical_analysis *analysis);

#ifdef __cplusplus
}
#endif

#endif
