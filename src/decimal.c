#include "decimal_private.h"

#include <float.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>

_Static_assert(FLT_RADIX == 2 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024 &&
               DBL_MIN_EXP == -1021, "ProbSpan requires IEEE-754 binary64 double");

#define DECIMAL_BASE UINT32_C(1000000000)
#define DECIMAL_LIMB_DIGITS 9
/* A binary64 midpoint is an odd integer of at most 54 bits times 2^e,
   with -1075<=e<=970. Its exact decimal coefficient has at most 768 digits
   (54-bit integer times 5^1075). These buffers bound midpoints, not input:
   arbitrarily long caller strings are compared as streams without copying. */
#define MIDPOINT_LIMBS 86
#define MIDPOINT_DECIMAL_DIGITS (MIDPOINT_LIMBS * DECIMAL_LIMB_DIGITS)
#define BINARY64_INFINITY UINT64_C(0x7ff0000000000000)
#define BINARY64_FRACTION_MASK UINT64_C(0x000fffffffffffff)
#define BINARY64_HIDDEN_BIT UINT64_C(0x0010000000000000)
#define BINARY64_FRACTION_BITS 52
#define BINARY64_EXPONENT_BIAS 1023
#define BINARY64_SUBNORMAL_EXPONENT (-1074)
#define MAX_DECIMAL_POSITION 309
#define UNDERFLOW_LEADING_FRACTION_ZEROS 324

typedef struct {
    uint32_t limbs[MIDPOINT_LIMBS];
    size_t used;
} decimal_integer;

typedef struct {
    const char *first_digit;
    int position;
} decimal_view;

static decimal_integer integer_from_uint64(uint64_t value) {
    decimal_integer integer = {{0}, 0};
    do {
        integer.limbs[integer.used++] = (uint32_t)(value % DECIMAL_BASE);
        value /= DECIMAL_BASE;
    } while (value != 0);
    return integer;
}

static void multiply_small(decimal_integer *integer, uint32_t factor) {
    uint64_t carry = 0;
    for (size_t i = 0; i < integer->used; ++i) {
        const uint64_t product = (uint64_t)integer->limbs[i] * factor + carry;
        integer->limbs[i] = (uint32_t)(product % DECIMAL_BASE);
        carry = product / DECIMAL_BASE;
    }
    if (carry != 0) {
        integer->limbs[integer->used++] = (uint32_t)carry;
    }
}

static size_t decimal_digits(const decimal_integer *integer, char *digits) {
    size_t written = 0;
    uint32_t divisor = DECIMAL_BASE / 10;
    const uint32_t top = integer->limbs[integer->used - 1];
    while (top < divisor) { divisor /= 10; }
    for (; divisor != 0; divisor /= 10) {
        digits[written++] = (char)('0' + (top / divisor) % 10);
    }
    for (size_t limb = integer->used - 1; limb > 0; --limb) {
        for (divisor = DECIMAL_BASE / 10; divisor != 0; divisor /= 10) {
            digits[written++] = (char)('0' + (integer->limbs[limb - 1] / divisor) % 10);
        }
    }
    return written;
}

/* Normalize the input without copying its digits. The two early magnitude
   decisions are mathematical binary64 bounds, never decimal-length limits:
   310 significant integer digits overflow; a first nonzero fractional digit
   after 324 zeroes is below half the least positive subnormal. */
static decimal_view view_decimal(const char *text) {
    const char *cursor = text;
    while (*cursor == '0') { ++cursor; }
    if (*cursor != '.' && *cursor != '\0') {
        decimal_view view = {cursor, 0};
        while (*cursor != '.' && *cursor != '\0') {
            if (++view.position > MAX_DECIMAL_POSITION) { break; }
            ++cursor;
        }
        return view;
    }
    if (*cursor == '.') {
        ++cursor;
        int zeroes = 0;
        while (*cursor == '0') {
            if (++zeroes >= UNDERFLOW_LEADING_FRACTION_ZEROS) {
                return (decimal_view){NULL, 0};
            }
            ++cursor;
        }
        if (*cursor != '\0') { return (decimal_view){cursor, -zeroes}; }
    }
    return (decimal_view){NULL, 0};
}

static void decode_finite(uint64_t encoding, uint64_t *significand, int *exponent) {
    const unsigned field = (unsigned)(encoding >> BINARY64_FRACTION_BITS);
    *significand = encoding & BINARY64_FRACTION_MASK;
    *exponent = BINARY64_SUBNORMAL_EXPONENT;
    if (field != 0) {
        *significand |= BINARY64_HIDDEN_BIT;
        *exponent = (int)field - BINARY64_EXPONENT_BIAS - BINARY64_FRACTION_BITS;
    }
}

/* Compare the complete decimal with the exact midpoint between encoding
   and its successor. At the maximum finite encoding the successor is the
   overflow result; the same midpoint formula still gives its RN threshold. */
static int compare_midpoint(const decimal_view *input, uint64_t encoding) {
    uint64_t significand;
    int exponent;
    decode_finite(encoding, &significand, &exponent);
    --exponent;
    decimal_integer coefficient = integer_from_uint64(2 * significand + 1);
    const uint32_t factor = exponent < 0 ? 5 : 2;
    const int power = exponent < 0 ? -exponent : exponent;
    for (int i = 0; i < power; ++i) { multiply_small(&coefficient, factor); }
    char digits[MIDPOINT_DECIMAL_DIGITS];
    const size_t count = decimal_digits(&coefficient, digits);
    const int position = (int)count + (exponent < 0 ? exponent : 0);
    if (input->position != position) { return input->position < position ? -1 : 1; }
    const char *cursor = input->first_digit;
    for (size_t i = 0; i < count; ++i) {
        if (*cursor == '.') { ++cursor; }
        const char digit = *cursor == '\0' ? '0' : *cursor;
        if (digit != digits[i]) { return digit < digits[i] ? -1 : 1; }
        if (*cursor != '\0') { ++cursor; }
    }
    /* An arbitrarily remote nonzero tail decides a near-halfway comparison;
       truncating it, even after thousands of zeroes, would break parity. */
    for (; *cursor != '\0'; ++cursor) {
        if (*cursor != '.' && *cursor != '0') { return 1; }
    }
    return 0;
}

static double value_from_encoding(uint64_t encoding) {
    /* Clang's unsigned-integer conversion can reconstruct zero via exact
       cancellation, yielding -0 under downward rounding. A nonnegative
       decimal's zero encoding must remain +0 in every caller rounding mode. */
    if (encoding == 0) { return 0.0; }
    if (encoding == BINARY64_INFINITY) { return INFINITY; }
    uint64_t significand;
    int exponent;
    decode_finite(encoding, &significand, &exponent);
    /* The integer and final power-of-two value are exactly representable.
       Unlike a strtod call or incremental accumulation, this construction
       does not depend on either locale or the caller's rounding direction. */
    return ldexp((double)significand, exponent);
}

double ps_decimal_to_binary64(const char *text) {
    const decimal_view input = view_decimal(text);
    if (input.first_digit == NULL) { return 0.0; }
    if (input.position > MAX_DECIMAL_POSITION) { return INFINITY; }
    uint64_t lower = 0;
    uint64_t upper = BINARY64_INFINITY;
    /* Positive finite IEEE encodings have numerical order. Binary search
       over their exact rounding-cell midpoints gives RN ties-to-even without
       rounding any decimal digit in floating-point arithmetic. */
    while (lower < upper) {
        const uint64_t middle = lower + (upper - lower) / 2;
        const int comparison = compare_midpoint(&input, middle);
        if (comparison == 0) {
            return value_from_encoding(middle + (middle & UINT64_C(1)));
        }
        if (comparison < 0) { upper = middle; }
        else { lower = middle + 1; }
    }
    return value_from_encoding(lower);
}
