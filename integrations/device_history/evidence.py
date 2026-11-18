"""Caller-side evidence review for one fixed-horizon device endpoint."""

from dataclasses import dataclass
from enum import StrEnum
from math import fsum, isfinite


ENDPOINT = "eligible-device-failure-100h/v1"
HOURS = 100
SCHEMA = "device-history-evidence/v1"
STRATA = ("low", "high")
MAX_COUNT = (1 << 63) - 1


class Applicability(StrEnum):
    SUPPORTED = "supported"
    CONDITIONAL = "conditional"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


class Path(StrEnum):
    STRICT = "strict_target"
    POOL = "shared_parameter_pool"
    STANDARD = "two_stratum_standard"


class Assumption(StrEnum):
    TARGET_SHARED = "target_independent_common_parameter"
    SOURCE_TARGET_SHARED = "source_target_independent_common_parameter"
    TARGET_STRATIFIED = "target_independent_within_and_across_strata"
    SOURCE_TARGET_STRATIFIED = "source_target_independent_common_within_each_stratum"


@dataclass(frozen=True)
class Declaration:
    applicability: Applicability
    assumption: Assumption
    reference: str
    kind: str = "caller_declaration"  # Or caller_supplied_audit. Neither is verified here.


@dataclass(frozen=True)
class Scope:
    population: str
    snapshot: str
    revision: str
    process_version: str
    conditions: str


@dataclass(frozen=True)
class Observation:
    device: str
    cycle: str
    cluster: str
    query: str
    stratum: str
    start_hour: int
    available_hour: int
    followup_hours: int
    failed: bool | None
    process_version: str
    conditions: str
    definition: str = ENDPOINT
    unit: str = "device-cycle"
    horizon_hours: int = HOURS


@dataclass(frozen=True)
class Batch:
    scope: Scope
    rows: tuple[Observation, ...]


@dataclass(frozen=True)
class Counts:
    events: int
    complements: int

    @property
    def size(self):
        return self.events + self.complements


@dataclass(frozen=True)
class Audit:
    presented: int
    after_cutoff: int
    duplicate_aliases: int
    zero_weight: int
    included: int
    withheld: int


@dataclass(frozen=True)
class Review:
    path: Path
    applicability: Applicability
    reason: str
    declaration: Declaration
    target_scope: Scope
    source_scope: Scope | None
    cutoff_hour: int
    weights: tuple[float, float] | None
    target_audit: Audit
    source_audit: Audit
    counts: tuple[Counts, ...] | None
    schema: str = SCHEMA
    estimand: str = ENDPOINT
    strata: tuple[str, str] = STRATA


class _Reject(Exception):
    def __init__(self, applicability, reason):
        self.applicability = applicability
        self.reason = reason


def _known(value):
    return isinstance(value, str) and bool(value.strip())


def _hour(value):
    return type(value) is int and value >= 0


def _weight_pair(weights):
    if weights is None:
        raise _Reject(Applicability.UNKNOWN, "weights_unknown")
    if (not isinstance(weights, (tuple, list)) or len(weights) != 2
            or any(type(w) not in (float, int) or not 0 <= w <= 1 or not isfinite(w)
                   for w in weights)
            or abs(fsum(weights) - 1) > 1e-12):
        raise _Reject(Applicability.INCOMPATIBLE, "invalid_weights")
    scale = fsum(weights)
    return weights[0] / scale, weights[1] / scale


def _check_declaration(path, declaration, target, source):
    if not all(_known(field) for scope in (target, source) if scope is not None
               for field in vars(scope).values()):
        raise _Reject(Applicability.UNKNOWN, "scope_unknown")
    if (not isinstance(declaration.applicability, Applicability)
            or not _known(declaration.reference)
            or declaration.kind not in ("caller_declaration", "caller_supplied_audit")):
        raise _Reject(Applicability.UNKNOWN, "declaration_evidence_unknown")
    if declaration.applicability != Applicability.SUPPORTED:
        raise _Reject(declaration.applicability, "declaration_" + declaration.applicability.value)
    expected = {
        Path.STRICT: Assumption.TARGET_SHARED,
        Path.POOL: Assumption.SOURCE_TARGET_SHARED,
        Path.STANDARD: (Assumption.TARGET_STRATIFIED if source is None
                        else Assumption.SOURCE_TARGET_STRATIFIED),
    }[path]
    if declaration.assumption != expected:
        raise _Reject(Applicability.INCOMPATIBLE, "assumption_mismatch")
    if path == Path.POOL and source is None:
        raise _Reject(Applicability.UNKNOWN, "source_required")
    if path == Path.STRICT and source is not None:
        raise _Reject(Applicability.INCOMPATIBLE, "strict_disallows_source")
    if source and (source.process_version, source.conditions) != (
            target.process_version, target.conditions):
        raise _Reject(Applicability.INCOMPATIBLE, "scope_regime_mismatch")


def _visible(batch, cutoff, counts):
    """A known later row is excluded before reading outcomes or identity."""
    if batch is None:
        return
    for row in batch.rows:
        if not _hour(row.available_hour):
            raise _Reject(Applicability.UNKNOWN, "availability_time_unknown")
        if row.available_hour > cutoff:
            counts["after_cutoff"] += 1
        else:
            yield row


def _validate(row, scope):
    if not all(_known(x) for x in (row.device, row.cycle, row.cluster, row.query)):
        raise _Reject(Applicability.UNKNOWN, "observation_identity_unknown")
    if row.stratum not in STRATA:
        raise _Reject(Applicability.INCOMPATIBLE, "unknown_stratum")
    if not all(_known(x) for x in (row.definition, row.unit, row.process_version, row.conditions)):
        raise _Reject(Applicability.UNKNOWN, "observation_context_unknown")
    if (type(row.horizon_hours) is not int
            or (row.definition, row.unit, row.horizon_hours) != (ENDPOINT, "device-cycle", HOURS)):
        raise _Reject(Applicability.INCOMPATIBLE, "endpoint_mismatch")
    if (row.process_version, row.conditions) != (scope.process_version, scope.conditions):
        raise _Reject(Applicability.INCOMPATIBLE, "observation_regime_mismatch")
    if row.failed is None or type(row.followup_hours) is not int or row.followup_hours != HOURS:
        raise _Reject(Applicability.CONDITIONAL, "incomplete_outcome")
    if type(row.failed) is not bool:
        raise _Reject(Applicability.INCOMPATIBLE, "invalid_outcome")
    if not _hour(row.start_hour) or row.start_hour + HOURS > row.available_hour:
        raise _Reject(Applicability.INCOMPATIBLE, "invalid_observation_time")


def _select(target, source, cutoff_hour, weights, audits):
    accepted = {}
    devices, clusters = set(), set()
    by_stratum = [[0, 0] for _ in STRATA]
    for role, batch in enumerate((target, source)):
        for row in _visible(batch, cutoff_hour, audits[role]):
            _validate(row, batch.scope)
            key = (row.device, row.cycle)
            if key in accepted:
                old_role, old = accepted[key]
                if old_role != role:
                    raise _Reject(Applicability.INCOMPATIBLE, "source_target_overlap")
                # Query identity is extraction metadata. The underlying outcome,
                # context and availability must agree before aliases can collapse.
                if any(value != getattr(old, name) for name, value in vars(row).items()
                       if name != "query"):
                    raise _Reject(Applicability.INCOMPATIBLE, "observation_conflict")
                audits[role]["duplicate_aliases"] += 1
                continue
            if row.device in devices or row.cluster in clusters:
                raise _Reject(Applicability.CONDITIONAL, "unmodelled_dependence")
            devices.add(row.device)
            clusters.add(row.cluster)
            accepted[key] = role, row
            h = STRATA.index(row.stratum)
            if weights is not None and weights[h] == 0:
                audits[role]["zero_weight"] += 1
                continue
            by_stratum[h][0 if row.failed else 1] += 1
            audits[role]["included"] += 1
    if weights is not None:
        if any(w > 0 and sum(by_stratum[h]) == 0 for h, w in enumerate(weights)):
            raise _Reject(Applicability.CONDITIONAL, "missing_stratum_support")
        return tuple(Counts(*pair) for pair in by_stratum)
    total = Counts(*(sum(pair[i] for pair in by_stratum) for i in range(2)))
    if max(total.events, total.complements) > MAX_COUNT:
        raise _Reject(Applicability.INCOMPATIBLE, "count_range")
    return (total,)


def review(path: Path, target: Batch, declaration: Declaration, *, cutoff_hour: int,
           source: Batch | None = None, weights=None) -> Review:
    """Fail closed for the entire requested analysis. No partial counts escape."""
    source_scope = source.scope if source is not None else None
    audits = [dict(presented=len(batch.rows) if batch else 0, after_cutoff=0,
                   duplicate_aliases=0, zero_weight=0, included=0)
              for batch in (target, source)]
    normalized = None
    try:
        if not _hour(cutoff_hour):
            raise _Reject(Applicability.UNKNOWN, "cutoff_unknown")
        _check_declaration(path, declaration, target.scope, source_scope)
        if path == Path.STANDARD:
            normalized = _weight_pair(weights)
        elif weights is not None:
            raise _Reject(Applicability.INCOMPATIBLE, "weights_require_standardization")
        counts = _select(target, source, cutoff_hour, normalized, audits)
        applicability, reason = Applicability.SUPPORTED, "eligible_under_supplied_assumptions"
    except _Reject as error:
        applicability, reason, counts = error.applicability, error.reason, None
        for audit in audits:
            audit["included"] = 0
    for audit in audits:
        audit["withheld"] = audit["presented"] - sum(audit[key] for key in (
            "after_cutoff", "duplicate_aliases", "zero_weight", "included"))
    return Review(path, applicability, reason, declaration, target.scope, source_scope,
                  cutoff_hour, normalized, Audit(**audits[0]), Audit(**audits[1]), counts)
