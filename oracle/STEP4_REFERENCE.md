# Step 4 portable state and composition

`state_reference.json` projects 23 observed transitions from the frozen
application at `a581f84ccd217ed45789b3566347255f56ffbeac`. Generation executes
the same isolated service fixtures as the original oracle, plus initial hidden
analysis and unchanged first exposure. Expected booleans come from committed
application results. The development adapter reports actual visible evidence,
not merely an exposure request; application timestamps verify initial exposure
but are omitted from the portable data and C API.

Coverage includes same-operation first exposure with raw/subject changes,
previous exposure with later changes, raw 0 -> 1, odds-only changes, hiding and
showing evidence, unavailable/insufficient history, and restored compromised
inputs. C tests also check in-place transitions and unchanged output on errors.

The composer delegates to accepted estimate, odds, analysis, and relation APIs.
Tests reuse all 742 subjective, 166 ordinary historical, and 18 corrected
large-count threshold inputs, comparing every meaningful composed field exactly
with the individual APIs. Existing independent reference parity tests continue
to validate those delegated implementations. Unavailable fields and C padding
are not interpreted as stored values.

Reproduction in the frozen reference environment:

```text
python oracle/generate_state.py --reference-root <frozen-checkout> --check
python tests/generate_state_fixtures.py --check
```

The public API was reviewed against [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1).
It adds only two provenance facts and complete mathematical analysis values.
There are no application identities, timestamps, revision counters, UI requests,
workflow states, persistence operations, or fused probabilities. Provenance is
separate from composition: neither alters mathematical estimates. Callers retain
the returned independent model/gate/analysis versions and derived results as
historical facts; future models must not silently reinterpret stored results.
Raw-domain validation is shared with estimation without changing accepted rules.
Full API and state documentation is now in [API](../docs/API.md) and
[Provenance](../docs/PROVENANCE.md). Final API hardening rejects unreachable
compromised-without-exposure inputs; all 23 reachable expected transitions are unchanged.

## Release status

The portable provenance projection and composer parity are frozen in v1.0.0. The source application's lifecycle, timestamps and persistence records remain outside the C API; new provenance changes require both reference-derived evidence and a review against [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1). See [Provenance](../docs/PROVENANCE.md) and [API](../docs/API.md).
