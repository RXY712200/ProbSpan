#include <fenv.h>
#include <inttypes.h>
#include <locale.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "probspan/probspan.h"
#include "decimal_private.h"
#include "decimal_fixtures.h"

#define COUNT(array) (sizeof(array) / sizeof((array)[0]))
#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Decimal check failed at line %d: %s\n", __LINE__, #condition); \
    exit(EXIT_FAILURE); } } while (0)

static uint64_t representation(double value) {
    _Static_assert(sizeof(value) == sizeof(uint64_t), "Binary64 representation required");
    uint64_t bits;
    memcpy(&bits, &value, sizeof(bits));
    return bits;
}

static void check_vectors(void) {
    for (size_t i = 0; i < COUNT(decimal_cases); ++i) {
        const decimal_case *item = &decimal_cases[i];
        CHECK(representation(ps_decimal_to_binary64(item->text)) == item->bits);
        double actual = 7.0;
        CHECK(probspan_odds_parse(item->text, &actual) == item->status);
        if (item->status == PROBSPAN_OK) { CHECK(representation(actual) == item->bits); }
        else { CHECK(actual == 7.0); }
    }
}

/* This executable also serves the development differential test. Lines grow
   dynamically, so the harness imposes no decimal length cap. Each response
   reports both conversion bits and public validation, including unchanged
   output on range rejection. Runtime library code allocates nothing. */
static void stream_vectors(void) {
    size_t capacity = 128;
    char *line = malloc(capacity);
    CHECK(line != NULL);
    size_t used = 0;
    int byte;
    while ((byte = getchar()) != EOF) {
        if (byte == '\n') {
            line[used] = '\0';
            double output = 7.0;
            const probspan_status status = probspan_odds_parse(line, &output);
            const uint64_t bits = representation(ps_decimal_to_binary64(line));
            const char *name = status == PROBSPAN_OK ? "ok" :
                               status == PROBSPAN_ODDS_RANGE ? "odds_range" : "unexpected";
            printf("%s %016" PRIx64 " %016" PRIx64 "\n", name, bits,
                   representation(output));
            used = 0;
            continue;
        }
        if (used + 1 == capacity) {
            CHECK(capacity <= SIZE_MAX / 2);
            capacity *= 2;
            char *grown = realloc(line, capacity);
            if (grown == NULL) { free(line); exit(EXIT_FAILURE); }
            line = grown;
        }
        line[used++] = (char)byte;
    }
    CHECK(used == 0 && !ferror(stdin));
    free(line);
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--stdin") == 0) {
        stream_vectors();
        return EXIT_SUCCESS;
    }
    check_vectors();
    size_t rounding_modes = 0;
    const int original_rounding = fegetround();
    static const int modes[] = {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO};
    for (size_t i = 0; i < COUNT(modes); ++i) {
        if (fesetround(modes[i]) == 0) { check_vectors(); ++rounding_modes; }
    }
    CHECK(fesetround(original_rounding) == 0);
    static const char *const locales[] = {
        "de_DE.UTF-8", "de_DE", "German_Germany.1252", "fr_FR.UTF-8"
    };
    bool comma_locale = false;
    for (size_t i = 0; i < COUNT(locales); ++i) {
        if (setlocale(LC_NUMERIC, locales[i]) != NULL &&
            strcmp(localeconv()->decimal_point, ",") == 0) {
            check_vectors();
            comma_locale = true;
            break;
        }
    }
    CHECK(setlocale(LC_NUMERIC, "C") != NULL);
    printf("Exact decimal parity: %zu vectors; %zu rounding modes; comma locale %s.\n",
           COUNT(decimal_cases), rounding_modes, comma_locale ? "passed" : "unavailable");
    return EXIT_SUCCESS;
}
