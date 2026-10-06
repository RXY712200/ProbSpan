#include "probspan/probspan.h"

#include <math.h>
#include <stddef.h>

#include "decimal_private.h"

probspan_status probspan_odds_validate(double odds, double *validated) {
    if (validated == NULL) {
        return PROBSPAN_INVALID_ARGUMENT;
    }
    if (!isfinite(odds) || odds < 1.0) {
        return PROBSPAN_ODDS_RANGE;
    }
    *validated = odds;
    return PROBSPAN_OK;
}

static bool valid_decimal_syntax(const char *text) {
    if (*text == '\0') {
        return false;
    }

    /* ASCII checks freeze the grammar independently of locale and conversion. */
    bool fractional = false;
    bool digit_before_dot = false;
    bool digit_after_dot = false;
    for (const unsigned char *cursor = (const unsigned char *)text; *cursor; ++cursor) {
        if (*cursor == '.') {
            if (fractional || !digit_before_dot) {
                return false;
            }
            fractional = true;
            continue;
        }
        if (*cursor < '0' || *cursor > '9') {
            return false;
        }
        if (fractional) {
            digit_after_dot = true;
        } else {
            digit_before_dot = true;
        }
    }
    if (fractional && !digit_after_dot) {
        return false;
    }
    return true;
}

probspan_status probspan_odds_parse(const char *text, double *validated) {
    if (text == NULL || validated == NULL) {
        return PROBSPAN_INVALID_ARGUMENT;
    }
    if (!valid_decimal_syntax(text)) { return PROBSPAN_ODDS_SYNTAX; }
    /* Repeated binary64 digit arithmetic can round to a neighboring value.
       The frozen Python float conversion instead rounds the complete decimal
       once, to nearest with ties to even; keep that concern private. */
    return probspan_odds_validate(ps_decimal_to_binary64(text), validated);
}
