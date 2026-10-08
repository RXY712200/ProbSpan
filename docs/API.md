# Public API contract

Include `<probspan/probspan.h>`. C++ callers receive C linkage. Private Beta and
decimal entry points are not supported interfaces. All functions are reentrant
and use no shared mutable state. Callers must supply live, correctly typed
objects and prevent concurrent writes to the same output. Every status-returning
operation leaves output unchanged on non-OK return. Normal unavailability is OK
with explicit flags. Arbitrary overlapping objects are not supported;
provenance specifically supports `result == previous`.

## Versions

| Identifier | Value and meaning |
|---|---|
| `PROBSPAN_VERSION_MAJOR` | 1, product major release |
| `PROBSPAN_VERSION_MINOR` | 0, product minor release |
| `PROBSPAN_VERSION_PATCH` | 0, product patch release |
| `PROBSPAN_VERSION_STRING` | `"1.0.0"`, product version |
| `probspan_abi_version()` | unsigned 1, ABI contract generation; no arguments/errors |

Product/ABI versions do not replace independent result versions: subjective
model, historical model, historical gate, and subjective odds analysis each
carry version 1. There is no universal model/cache version.

## Enums

| Type | Every value and meaning |
|---|---|
| `probspan_status` | `PROBSPAN_OK`: success; `PROBSPAN_INVALID_ARGUMENT`: null pointer, malformed estimate, invalid applicable relation enum, or unreachable provenance; `PROBSPAN_RAW_PROBABILITY`: raw outside 0..100; `PROBSPAN_SUBJECTIVE_DOMAIN`: width probability outside [0.01,0.99], including NaN; `PROBSPAN_HISTORY_COUNTS`: negative count; `PROBSPAN_ODDS_SYNTAX`: invalid grammar; `PROBSPAN_ODDS_RANGE`: nonfinite/rounded odds <1; `PROBSPAN_NUMERICAL_FAILURE`: untrustworthy Beta solver result |
| `probspan_history_state` | `PROBSPAN_NO_HISTORY`: zero counts; `PROBSPAN_INSUFFICIENT`: estimate exists but gate fails; `PROBSPAN_VALID`: gate passes |
| `probspan_ev_state` | `PROBSPAN_ROBUST_POSITIVE`, `PROBSPAN_ROBUST_NEGATIVE`, `PROBSPAN_CROSSES_THRESHOLD`: whole-interval EV classification |
| `probspan_odds_combination` | `PROBSPAN_NORMAL_OVERLAP`, `PROBSPAN_CRITICAL`, `PROBSPAN_DOUBLE_POSITIVE_WINDOW`: inverse-odds geometry |
| `probspan_model_relation` | `PROBSPAN_AGREEMENT_POSITIVE`, `PROBSPAN_AGREEMENT_NEGATIVE`, `PROBSPAN_CONFLICT`, `PROBSPAN_UNCERTAIN`, `PROBSPAN_HISTORY_UNAVAILABLE`: independent-state relationship |

Do not assume enum byte size; persist semantic names or an explicit caller schema.

## Structs and every field

| Struct | Fields |
|---|---|
| `probspan_subjective_result` | `raw_percent`: original int32 input; `used_percent`: clamped integer; `probability`: used/100; `lower`, `upper`: subjective bounds; `logit_half_width`: d(p); `model_version`: subjective model |
| `probspan_history_result` | `event_count`, `complement_count`: int64 counts; `sample_size`: exact uint64 sum; `state`: history state; `statistically_ready`: gate; `has_estimate`: numeric availability; `probability`: posterior mean; `lower`, `upper`: credible bounds; `model_version`: history model; `gate_version`: history gate |
| `probspan_ev_interval` | `center`, `minimum`, `maximum`: EV; `state`: interval state |
| `probspan_odds_geometry` | `event_break_even`: 1/Oe; `complement_event_break_even`: 1/Oc on complement axis; `complement_break_even_as_event`: 1-1/Oc on event axis; `combination`: inverse-sum classification |
| `probspan_subjective_side` | `ev`: EV interval; `has_robust_margin`: S availability; `robust_margin`: S if available |
| `probspan_subjective_analysis` | `analysis_version`: odds analysis version; `geometry`: thresholds/combination; `event`, `complement_event`: subjective sides |
| `probspan_historical_side` | `ev`: EV interval; `positive_ev_probability`: posterior probability of positive side EV |
| `probspan_historical_analysis` | `available`: only VALID history; `event`, `complement_event`: historical sides |
| `probspan_provenance` | `evidence_exposed`: ever exposed; `subjective_independence_compromised`: later raw/subject change after exposure; invariant compromised implies exposed |
| `probspan_analysis` | `subjective`: estimate; `event_odds`, `complement_event_odds`: validated odds; `subjective_analysis`: two-sided analysis; `history`: estimate; `historical_analysis`: availability/sides; `event_relation`, `complement_event_relation`: model relationships |

**Unavailable fields:** when `has_estimate=false`, do not interpret history
probability/lower/upper. When historical `available=false`, do not interpret
either historical side. When `has_robust_margin=false`, do not interpret S.
Current zero placeholders are not a promised numeric value for these fields.

## Functions

Formulas: [behavior specification](BEHAVIOR_SPEC.md). Tolerances/environment:
[numerical contract](NUMERICAL_CONTRACT.md). All functions follow unchanged
output on error and the reentrancy rule above. Signatures in the header are
authoritative; argument names below follow header order.

### Estimates and odds

| Function | Domains, outputs, and statuses in precedence order |
|---|---|
| `probspan_subjective_half_width(probability, half_width)` | double p in [0.01,0.99]; writes elementary d(p). NULL -> INVALID_ARGUMENT; invalid p -> SUBJECTIVE_DOMAIN |
| `probspan_subjective_estimate(raw_percent, result)` | int32 raw 0..100; preserves raw and returns model interval/version. NULL -> INVALID_ARGUMENT; raw -> RAW_PROBABILITY |
| `probspan_history_estimate(event_count, complement_count, result)` | Each int64 0..INT64_MAX, exact uint64 sum. NULL -> INVALID_ARGUMENT; negative -> HISTORY_COUNTS; solver -> NUMERICAL_FAILURE. Zero sum -> NO_HISTORY/has_estimate=false; insufficient nonzero still has estimate |
| `probspan_odds_validate(odds, validated)` | double finite >=1; writes identical odds. NULL -> INVALID_ARGUMENT; odds -> ODDS_RANGE |
| `probspan_odds_parse(text, validated)` | Non-NULL NUL-terminated ASCII `[0-9]+(\.[0-9]+)?`; exact conversion then range validation. Either NULL -> INVALID_ARGUMENT; syntax -> ODDS_SYNTAX; rounded range -> ODDS_RANGE. Locale/rounding-mode independent |

### Classification and analysis

| Function | Domains, outputs, availability, and statuses |
|---|---|
| `probspan_classify_ev(ev_minimum, ev_maximum, state)` | double endpoints, normally ordered/finite. Applies frozen comparisons directly; only NULL -> INVALID_ARGUMENT. No added numeric validation: NaN comparisons follow C semantics; first matching branch wins for unordered inputs. Finite valid model intervals are the useful contract |
| `probspan_classify_odds_combination(event_odds, complement_odds, combination)` | Validates both odds, event first, writes inverse-sum class. NULL -> INVALID_ARGUMENT; either odds -> ODDS_RANGE |
| `probspan_classify_model_relation(subjective_state, historical_available, historical_state, relation)` | Subjective enum valid; historical enum valid only if available, otherwise ignored. NULL/invalid applicable enum -> INVALID_ARGUMENT; unavailable -> HISTORY_UNAVAILABLE. No probability arithmetic |
| `probspan_analyze_subjective(subjective, event_odds, complement_odds, analysis)` | Estimate from subjective_estimate; const input. NULL -> INVALID_ARGUMENT; finite ordered [0,1] bounds, interior center, finite positive width required (INVALID_ARGUMENT); then event/complement odds (ODDS_RANGE). Writes both EVs, geometry, S availability, version 1. Exact odds=1 disables S only |
| `probspan_analyze_historical(history, event_odds, complement_odds, analysis)` | Estimate from history_estimate; const input. NULL -> INVALID_ARGUMENT. Any state other than VALID returns OK/unavailable before inspecting estimate numbers or odds. VALID requires has_estimate, nonnegative counts, finite ordered [0,1] bounds (INVALID_ARGUMENT); then odds (ODDS_RANGE); CDF failure -> NUMERICAL_FAILURE. No gate recomputation |

Estimate structs are not authenticated objects. Guards protect structural misuse,
not a forged claim that an interval/version came from the library. Use estimate
APIs or composition; analysis APIs do not rederive intervals or verify versions.

### Provenance and complete composition

`probspan_provenance_transition(previous, previous_raw_percent,
current_raw_percent, subject_changed, evidence_exposed_now, result)` accepts two
raw int32 percentages in [0,100] and explicit caller boolean facts. Pointer
checks come first (INVALID_ARGUMENT), then compromised=>exposed invariant
(INVALID_ARGUMENT), then raw domain (RAW_PROBABILITY). Outputs use old exposure
for compromise. In-place operation is supported. Initialize {false,false} and
equal raw inputs for initial analysis. No reset operation exists.

`probspan_compose_analysis(raw_percent, event_count, complement_count,
event_odds, complement_event_odds, result)` returns complete nested values.
Validation/delegation order is: output pointer, subjective input, history
counts/solver, event odds, complement odds, subjective analysis, historical
analysis, relations. Returns the first delegated error. Invalid raw precedes
negative history; history errors precede odds errors. Unlike historical analysis
alone, valid odds are required even without history because subjective analysis
uses them. Availability remains normal state. No partial output on failure.

## Persistence and replay

Raw C struct bytes are **not a portable serialization format** because of
padding, compiler ABI, enum representation, alignment, and platform layout.
Serialize meaningful fields explicitly, respecting flags. Keep raw input,
counts, odds, availability, derived outputs/relations, subjective model version,
history model version, history gate version, and odds analysis version.
Product/ABI version may additionally identify the implementation.

A saved result is what that model returned then. A future model must not
silently recompute/relabel it as the original analysis. The library has no
storage/migration API. Store provenance separately if needed; it describes
independence and does not alter mathematical outputs.
