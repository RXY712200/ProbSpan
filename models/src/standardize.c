#include <probspan_models/standardize.h>

#include <fenv.h>
#include <float.h>
#include <math.h>
#include <stddef.h>

_Static_assert(FLT_RADIX == 2 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024
    && DBL_MIN_EXP == -1021 && FLT_EVAL_METHOD == 0,
    "Fixed standardization requires direct binary64 evaluation");

/* Integer units of 2^-2148. At most 1024 weights <= 2 enter the
 * accumulator. Even multiplication by the policy denominator fits. */
enum { LIMBS = 70, SCALE = 2148, SUBNORMAL_SHIFT = 1074 };
typedef struct {
    uint32_t limb[LIMBS];
} integer;

typedef struct {
    uint64_t significand;
    int exponent;
} dyadic;

static dyadic decode(double value)
{
    dyadic result = {0, 0};
    if (value != 0.0) {
        const double fraction = frexp(value, &result.exponent);
        result.significand = (uint64_t)scalbn(fraction, 53);
        result.exponent -= 53;
        while (!(result.significand & 1u)) {
            result.significand >>= 1;
            ++result.exponent;
        }
    }
    return result;
}

static void add_word(integer *out, unsigned offset, uint32_t value)
{
    unsigned i = offset / 32u;
    uint64_t carry = (uint64_t)value << (offset % 32u);
    while (carry != 0 && i < LIMBS) {
        carry += out->limb[i];
        out->limb[i++] = (uint32_t)carry;
        carry >>= 32;
    }
}

static void add_significand(integer *out, unsigned offset, uint64_t value)
{
    add_word(out, offset, (uint32_t)value);
    add_word(out, offset + 32u, (uint32_t)(value >> 32));
}

static void add_product(integer *out, dyadic a, dyadic b)
{
    unsigned offset = (unsigned)(SCALE + a.exponent + b.exponent);
    while (b.significand != 0) {
        if (b.significand & 1u) {
            add_significand(out, offset, a.significand);
        }
        b.significand >>= 1;
        ++offset;
    }
}

static int compare(const integer *a, const integer *b)
{
    for (unsigned i = LIMBS; i-- > 0;) {
        if (a->limb[i] != b->limb[i]) {
            return a->limb[i] < b->limb[i] ? -1 : 1;
        }
    }
    return 0;
}

/* The caller establishes a >= b. Unsigned wrap extracts the result word. */
static void subtract(integer *a, const integer *b)
{
    uint64_t borrow = 0;
    for (unsigned i = 0; i < LIMBS; ++i) {
        const uint64_t subtrahend = (uint64_t)b->limb[i] + borrow;
        const uint64_t word = a->limb[i];
        a->limb[i] = (uint32_t)(word - subtrahend);
        borrow = word < subtrahend;
    }
}

static void double_integer(integer *a)
{
    uint32_t carry = 0;
    for (unsigned i = 0; i < LIMBS; ++i) {
        const uint32_t word = a->limb[i];
        a->limb[i] = (word << 1) | carry;
        carry = word >> 31;
    }
}

static int within_policy(const integer *weight)
{
    integer one = {0}, delta, scaled = {0};
    add_word(&one, SCALE, 1);
    if (compare(weight, &one) >= 0) {
        delta = *weight;
        subtract(&delta, &one);
    } else {
        delta = one;
        subtract(&delta, weight);
    }

    /* Compare |W-1| * 10^12 with 1 in the same integer units. */
    uint64_t factor = UINT64_C(1000000000000);
    for (unsigned bit = 0; factor != 0; ++bit, factor >>= 1) {
        if (factor & 1u) {
            for (unsigned i = 0; i < LIMBS; ++i) {
                add_word(&scaled, 32u*i + bit, delta.limb[i]);
            }
        }
    }
    return compare(&scaled, &one) <= 0;
}

static ps2_standardized_point encode_ratio(integer remainder, const integer *denominator)
{
    const integer zero = {0};
    if (compare(&remainder, denominator) == 0) {
        return (ps2_standardized_point){1.0, PS2_POINT_EXACT, {1.0, 1.0}};
    }

    uint64_t significand = 0;
    unsigned digits = 0;
    unsigned position = 0;
    /* Generate exact fractional bits until the encoding grid is reached:
     * 53 significant bits for normals, bit 1074 for subnormals. */
    while (position < SUBNORMAL_SHIFT && digits < 53 && compare(&remainder, &zero) != 0) {
        double_integer(&remainder);
        ++position;
        const int bit = compare(&remainder, denominator) >= 0;
        if (bit) {
            subtract(&remainder, denominator);
        }
        significand = (significand << 1) | (unsigned)bit;
        if (significand != 0) {
            ++digits;
        }
    }

    const double lower = scalbn((double)significand, -(int)position);
    if (compare(&remainder, &zero) == 0) {
        return (ps2_standardized_point){lower, PS2_POINT_EXACT, {lower, lower}};
    }
    const double upper = nextafter(lower, 1.0);
    double_integer(&remainder);
    const int midpoint = compare(&remainder, denominator);
    const double nearest = midpoint > 0 || (midpoint == 0 && (significand & 1u))
        ? upper : lower;
    return (ps2_standardized_point){nearest,
        nearest == 0.0 ? PS2_POINT_ROUNDED_ZERO : PS2_POINT_ROUNDED, {lower, upper}};
}

ps2_standardize_status ps2_standardize_fixed(const ps2_fixed_stratum *strata,
    uint64_t count, ps2_standardized_risk *out)
{
    if (strata == NULL || out == NULL) {
        return PS2_STANDARDIZE_INVALID_ARGUMENT;
    }
    if (count == 0) {
        return PS2_STANDARDIZE_EMPTY;
    }
    if (count > 1024) {
        return PS2_STANDARDIZE_UNSUPPORTED;
    }
    int oversized = 0;
    for (uint64_t i = 0; i < count; ++i) {
        const ps2_fixed_stratum *row = &strata[i];
        if (!isfinite(row->target_weight) || row->target_weight < 0
            || (row->support != PS2_RISK_KNOWN && row->support != PS2_RISK_UNKNOWN)
            || (row->support == PS2_RISK_KNOWN && (!isfinite(row->conditional_risk)
                || row->conditional_risk < 0 || row->conditional_risk > 1))) {
            return PS2_STANDARDIZE_INVALID_ARGUMENT;
        }
        oversized |= row->target_weight > 2.0;
    }
    if (oversized) {
        return PS2_STANDARDIZE_UNSUPPORTED;
    }
    volatile double smallest = DBL_TRUE_MIN;
    if (fegetround() != FE_TONEAREST || smallest * 2.0 != 0x1p-1073) {
        return PS2_STANDARDIZE_NUMERICAL_FAILURE;
    }

    integer weight = {0}, known = {0}, missing = {0};
    for (uint64_t i = 0; i < count; ++i) {
        const ps2_fixed_stratum *row = &strata[i];
        const dyadic w = decode(row->target_weight);
        const unsigned offset = (unsigned)(SCALE + w.exponent);
        add_significand(&weight, offset, w.significand);
        if (row->support == PS2_RISK_UNKNOWN) {
            add_significand(&missing, offset, w.significand);
        } else {
            add_product(&known, w, decode(row->conditional_risk));
        }
    }
    if (!within_policy(&weight)) {
        return PS2_STANDARDIZE_UNSUPPORTED;
    }

    const integer zero = {0};
    ps2_standardized_risk result = {0};
    const ps2_standardized_point lower = encode_ratio(known, &weight);
    if (compare(&missing, &zero) == 0) {
        result.kind = PS2_STANDARDIZE_IDENTIFIED;
        result.result.point = lower;
    } else {
        result.kind = PS2_STANDARDIZE_PARTIAL;
        result.result.partial.lower = lower.enclosure;
        for (unsigned i = 0; i < LIMBS; ++i) {
            add_word(&known, 32u*i, missing.limb[i]);
        }
        result.result.partial.upper = encode_ratio(known, &weight).enclosure;
    }
    *out = result;
    return PS2_STANDARDIZE_OK;
}
