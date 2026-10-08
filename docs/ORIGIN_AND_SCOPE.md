# Origin and scope

ProbSpan is a C extraction/reimplementation from the author's own
[RXY712200/probability-calibration-tool](https://github.com/RXY712200/probability-calibration-tool).
The behavioral baseline is exactly
`a581f84ccd217ed45789b3566347255f56ffbeac`.

Extracted concerns are the subjective uncertainty model, Jeffreys historical
model/gate, odds/EV decision analysis, independent-model relations, and relevant
deterministic information-provenance semantics. v1 is behavioral extraction,
not algorithm redesign. The explicitly authorized extreme SciPy correction
uses separately identified mathematical references; original ordinary output
and tolerances remain frozen. See [numerical contract](NUMERICAL_CONTRACT.md).

The original Qt/UI, SQLite, Round/Session lifecycle, character identities,
history regimes, persistence, backup/recovery, localization, correction/completion
workflow, revision_count, and history_exposed_at stayed outside runtime/public
ProbSpan. Original application names appear only where origin/reference tooling
needs to execute and describe frozen observations. Generic mathematical history
and explicit actual exposure remain legitimate library concepts.

[Issue #1](https://github.com/RXY712200/ProbSpan/issues/1) defines the long-term
boundary: a small deterministic probability -> uncertainty -> decision core,
with provenance only for decision trust. Callers own clocks, arbitrary subject
identities, evidence presentation, workflow, and storage. The library returns
values rather than maintaining application entities.

Non-goals include Brier/Log Loss/ECE, calibration curves, reliability diagrams,
generic distribution catalogs, alternative priors, configurable v1 replacements,
machine learning, probability fusion, databases, serialization engines, clocks,
and revision ledgers. Internal Beta/decimal algorithms support this narrow model.

This origin statement makes no global-originality or trademark-clearance claim.
No license is inferred from authorship or copied from another repository. The
owner has not chosen a license; this remains release metadata requiring a
separate owner decision, without blocking technical candidate validation.
