#include "probspan/probspan.h"

#include <math.h>
#include <stddef.h>

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

probspan_status probspan_odds_parse(const char *text, double *validated) {
    if (text == NULL || validated == NULL) {
        return PROBSPAN_INVALID_ARGUMENT;
    }
    if (*text == '\0') {
        return PROBSPAN_ODDS_SYNTAX;
    }

    /* Check ASCII grammar independently of range. Computing digits directly
       avoids strtod's process-locale-dependent decimal mark. */
    double value = 0.0;
    double place = 0.1;
    bool fractional = false;
    bool digit_before_dot = false;
    bool digit_after_dot = false;
    for (const unsigned char *cursor = (const unsigned char *)text; *cursor; ++cursor) {
        if (*cursor == '.') {
            if (fractional || !digit_before_dot) {
                return PROBSPAN_ODDS_SYNTAX;
            }
            fractional = true;
            continue;
        }
        if (*cursor < '0' || *cursor > '9') {
            return PROBSPAN_ODDS_SYNTAX;
        }
        const unsigned digit = (unsigned)(*cursor - '0');
        if (fractional) {
            digit_after_dot = true;
            value += digit * place;
            place *= 0.1;
        } else {
            digit_before_dot = true;
            value = value * 10.0 + digit;
        }
    }
    if (fractional && !digit_after_dot) {
        return PROBSPAN_ODDS_SYNTAX;
    }
    return probspan_odds_validate(value, validated);
}
