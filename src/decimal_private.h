#ifndef PROBSPAN_DECIMAL_PRIVATE_H
#define PROBSPAN_DECIMAL_PRIVATE_H

/* Precondition: text matches [0-9]+(\.[0-9]+)?. No locale or allocation. */
double ps_decimal_to_binary64(const char *text);

#endif
