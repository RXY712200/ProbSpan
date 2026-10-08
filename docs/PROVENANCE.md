# Evidence exposure and subjective independence

Provenance describes whether an independent subjective estimate can still claim
information independence after relevant evidence has been exposed. It does not
change its mathematical probability, uncertainty, EV, or classification.

The state has only `evidence_exposed` and
`subjective_independence_compromised`. Reachable states are {false,false},
{true,false}, and {true,true}. **Compromised implies exposed.** Caller-created
{false,true} is rejected with INVALID_ARGUMENT, leaving output unchanged,
including in-place output. No additional states or reset API exist in v1.

The caller reports actual exposure and whether the decision subject changed.
ProbSpan cannot identify arbitrary caller subjects or infer whether information
was seen from a request to display it. Both previous/current raw percentages
are checked internally in 0..100 and compared before mathematical clamping.

## Causal ordering

```text
changed = subject_changed OR previous_raw != current_raw
new_exposed = old_exposed OR exposed_now
new_compromised = old_compromised OR (old_exposed AND changed)
```

Only previously exposed evidence can compromise a current change. Exposure in
the same logical operation occurs after the entered change and cannot
retroactively contaminate it. Exposure alone is not compromise: the already
entered estimate can remain independent. Callers must group/report operations
honestly; this API records facts, not a proof of what a person knew.

| Previous state | Operation | Result |
|---|---|---|
| false,false | Initial input, no actual exposure | false,false |
| false,false | Initial input, actual exposure | true,false |
| false,false | Raw 0->1 and first exposure together | true,false |
| false,false | Subject changes and first exposure together | true,false |
| true,false | Raw 0->1 | true,true |
| true,false | Subject changes | true,true |
| true,false | Only odds change | true,false |
| true,false | Evidence later hidden/unavailable | true,false |
| true,true | Previous raw/subject restored | true,true |

Raw 0 and 1 both produce 1% mathematical input, but they are different entered
values. Comparing used probability instead would lose the frozen provenance
meaning. Subject identity is a caller boolean fact because the library owns no
identity framework. Odds are irrelevant and are absent from the transition API.

Exposure remains sticky after hiding evidence or losing available history.
Compromise remains sticky after restoring raw/subject values or changing odds.
Use {false,false} plus equal raw inputs for initialization. For a genuinely new
independent decision the caller owns construction/lifecycle; v1 does not provide
a transition that resets an existing state.

First exposure is observable as old.exposed=false/new.exposed=true; callers may
attach their own clock data or count operations outside ProbSpan. The library
assigns no timestamps, lifecycle numbers, or storage records. See
[example](../examples/provenance.c) and [API](API.md).

## Integration contract

The library cannot observe an application screen, a data feed, a user's attention, or the provenance of a file. The caller must determine whether a *valid relevant evidential result was actually exposed*, and pass that factual boolean. Merely requesting or scheduling an exposure does not set it. This separation is required for both mathematical correctness and the product boundary in [Issue #1](https://github.com/RXY712200/ProbSpan/issues/1).

Once `subjective_independence_compromised` becomes true, subsequent transitions of the **same logical decision** retain the compromised state. A caller starting a genuinely new independent decision initializes a new state object; it must not silently erase exposure history on an existing decision. Revision counters, event timestamps and audit record persistence remain caller responsibilities.

The C API intentionally carries no confidence score for provenance: these booleans encode causal state from caller-supplied facts, **not proof that a human decision was independent**. Validate facts at the application boundary.
