# Frozen v1 behavior

Baseline: `a581f84ccd217ed45789b3566347255f56ffbeac`. The authorized extreme
SciPy exception changes numerical evaluation, not the model, and is not
represented as original SciPy output.

## Subjective

Raw integer r in [0,100] is preserved. Used u=1 for r=0, u=99 for r=100,
otherwise u=r; p=u/100.0. `logit(x)=ln(x/(1-x))`, quotient before log;
`logistic(z)=1/(1+exp(-z))`. Let L=ln(1.5), M=ln(2), H=ln(1.4), X=ln(1.2).

| Branch tested in order | d(p) |
|---|---|
| p <= 0.45 | L |
| p < 0.55 | L + ((p-0.45)/(0.55-0.45))*(M-L) |
| p <= 0.85 | M |
| p < 0.95 | M - ((p-0.85)/(0.95-0.85))*(M-H) |
| otherwise p <= 0.99 | H - ((p-0.95)/(0.99-0.95))*(H-X) |

Direct width API accepts [0.01,0.99]. Inclusivity matters, including plateau
starting exactly at 0.55. Bounds are logistic(logit(p)-d(p)) and
logistic(logit(p)+d(p)). This model-defined subjective uncertainty interval is
**not a statistical confidence interval**. Subjective model version=1.

## Historical

Nonnegative int64 e,c; n is exact unsigned sum. n=0 -> NO_HISTORY, unavailable
mean/interval, gate false, versions retained. n>0 -> Jeffreys alpha=e+0.5,
beta=c+0.5, mean alpha/(alpha+beta), central 95% Beta interval. Quantile tails
are `(1-0.95)/2` and `1-tail`, evaluated in binary64.
Ready iff `n>=20 AND upper-lower<=0.25`. Ready -> VALID, else INSUFFICIENT;
nonzero insufficient history still has estimate. History model/gate versions
are independently 1. Large-count conversion/evaluation is specified in the
[numerical contract](NUMERICAL_CONTRACT.md).

## Odds

O is a gross return multiplier including stake, finite and >=1. Text grammar
is exactly ASCII `[0-9]+(\.[0-9]+)?`: leading zeros allowed; no sign, exponent,
spaces, comma, missing digits, or trailing characters. Complete decimal rounds
once to binary64 nearest ties-even before range check; acceptance uses rounded
odds. Parser is locale/rounding-mode independent. Odds=1 is valid; S unavailable.

## Decision analysis

For event Oe and complement Oc, thresholds are `be=1/Oe`, `bc=1/Oc`, and
`1-bc` (complement threshold on primary-event axis). For either model with p
and [lo,hi]:

| Side | Center | Minimum | Maximum |
|---|---|---|---|
| Event | p*Oe-1 | lo*Oe-1 | hi*Oe-1 |
| Complement | (1-p)*Oc-1 | (1-hi)*Oc-1 | (1-lo)*Oc-1 |

Bounds reverse under complementation. Multiply rounds before subtraction.
E=1e-12 is a policy boundary. If minimum>E -> ROBUST_POSITIVE; else if
maximum<-E -> ROBUST_NEGATIVE; else CROSSES_THRESHOLD. Strict inequalities;
exact +/-E does not satisfy its robust branch. Whole interval, not midpoint.

S_event=(logit(p)-logit(be))/d(p);
S_complement=(logit(1-p)-logit(bc))/d(p).
Only exact O=1 disables S, not EV. Threshold at side lower bound -> S≈+1;
at upper bound -> S≈-1. Positive S means center exceeds threshold in logit
distance scaled by width. Subjective odds analysis version=1.

For T=1/Oe+1/Oc: `abs(T-1)<=E` -> CRITICAL; else `T>1+E` -> NORMAL_OVERLAP;
else DOUBLE_POSITIVE_WINDOW. Preserve order and binary64 evaluation.

Historical analysis exists only for VALID history; otherwise returns unavailable
before validating odds. Event positive-EV mass is `1-BetaCDF(1/Oe;alpha,beta)`;
complement mass is `BetaCDF(1-1/Oc;alpha,beta)`. Clamp final results to [0,1].
Event subtraction remains frozen. Posterior mass is distinct from interval state.

| Subjective \ historical | Unavailable | Positive | Negative | Crossing |
|---|---|---|---|---|
| Positive | HISTORY_UNAVAILABLE | AGREEMENT_POSITIVE | CONFLICT | UNCERTAIN |
| Negative | HISTORY_UNAVAILABLE | CONFLICT | AGREEMENT_NEGATIVE | UNCERTAIN |
| Crossing | HISTORY_UNAVAILABLE | UNCERTAIN | UNCERTAIN | UNCERTAIN |

Unavailable precedes crossing. Models remain independent; no fused/weighted/best
probability. Historical analysis has no invented extra version; aggregate
retains its historical model/gate versions separately.

## Provenance and historical fact

```text
changed = subject_changed OR previous_raw_percent != current_raw_percent
new_exposed = old_exposed OR evidence_exposed_now
new_compromised = old_compromised OR (old_exposed AND changed)
```

Raw inputs each 0..100; old exposure controls compromise. First exposure in the
same operation as change is not retroactive. Raw 0->1 is an identity change
despite equal mathematical estimates. Caller supplies subject_changed and
actual exposure; odds are irrelevant. Flags are sticky; no reset. Malformed
compromised=true/exposed=false is INVALID_ARGUMENT, output untouched.

Initialize {false,false}; initial actual exposure sets exposed without compromise.
Clocks, lifecycle, storage belong to callers. Complete aggregate nests estimates,
odds, analyses, relations, availability, and independent versions as historical
facts. See [API replay guidance](API.md#persistence-and-replay) and
[provenance](PROVENANCE.md).
