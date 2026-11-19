# ProbSpan — Phase C: Cross-Method Synthesis, Integration Review, and Architecture Design

**Task status:** Authorized Phase C research/design assignment. **No implementation or release authorized.**
**Repository:** `RXY712200/ProbSpan` (public).
**Dedicated task branch:** `docs/phase-c-integration-architecture-brief`.
**Verified starting `main` / Phase B merge:** `45075a1da4adedf871299d148ef7dfa502335d72`.
**Accepted Phase B research HEAD:** `b6cff295748b53e565ff5e661ddde7beba5b9a95`, tree `8e357032779dae168c3fb43aaf2938d6996a1bc7`.
**Accepted Phase A merge:** `e47c038cd2b1997d87b7fe303f9037c80e6eb955`.
**Published Stable baseline:** v1.1.0, source commit `46ff21847c5522eb983d3f58e396354461a64f34`.

## 0. Mission: think independently; do not presume that integration means merging everything

Phase C is the deliberate **whole-project synthesis stage**, performed **after** broad Phase A discovery and mathematical Phase B comparison and **before** any substantial production implementation.

The owner's concern is not simply "which model won?" or "which formulas could share a function?"

The project now has many possible mathematical routes. Some may overlap in truly reusable infrastructure; some may merely appear similar; some may be incompatible; others may be best left independent or outside ProbSpan entirely.

**Your central responsibility is to determine, with evidence, where integration creates real value, where separation is safer, and what a maintainable, coherent product architecture *could* look like.**

Do **not** optimize for the shortest code, fewest files, maximal abstraction, largest feature list, or largest public API. Opposite problems matter equally:

- **Under-integration**: duplicating verified numerical or evidence-validation logic, multiplying inconsistent error handling, maintaining separate copies of the same correct primitive, needless parallel abstractions.
- **Over-integration**: forcing distinct estimands/data types/statistical assumptions into one fake universal model; conflating posterior probabilities with scores, fields with outcomes, or evidence provenance with scientific validity; creating a central framework so coupled that every additional model changes unrelated paths.
- **False consolidation**: sharing a UI-friendly result name or helper while silently changing meaning, temporal availability, numerical contract, provenance or downstream decision logic.
- **Speculative design**: building a framework for potential future capabilities that are not supported by evidence or actually wanted by users.

You may conclude that some features should be independent, optional, deferred, delegated to the caller, implemented in a separate package, researched further, or **not implemented**. A reasoned "retain the current narrow core" is a legitimate option and must be compared fairly.

Your deliverable is **a rigorous, conditional architecture synthesis and owner-decision package**, not a running implementation, new API commitment, or authorized feature selection. Provide a coherent recommended *proposal* when warranted, with explicit unresolved owner choices and honest alternatives; do not use "needs owner approval" as an excuse to avoid doing the technical comparison.

### Fresh-cloud execution rule

This pinned file must be executable by a completely new Codex Cloud context using only GitHub-connected repositories, public sources, and the available cloud workspace. Do not rely on old conversations, private agent memory, local Windows paths, the user's PC being powered on, unpublished analysis, or a nested Codex Cloud task.

Read this complete file, then independently read the actual repository and policies. Do not use a list of prescribed papers as a substitute for thinking; sources already in the repository are your starting evidence, not a closed set.

If the environment cannot read the approved source or policy or write to the branch, identify the **specific** missing capability and stop the affected actions honestly. Do **not** try to spawn another Cloud task via an unauthorized CLI/session token. In a cloud working checkout with shell and Git permissions, execute directly.

## 1. Authority, product identity, and preserved baselines

Before deciding anything, verify:

1. Actual repository, branch, remote refs, current `main`, PR #18 merged status, task branch starting point and clean/unfamiliar working tree. If unexpected changes exist, inspect them; never reset or overwrite them.
2. Read **the complete current authoritative private policy files** from authenticated `RXY712200/Development-Playbook`: `WORKFLOW.md` and `RELEASE_POLICY.md`. Do not paste private policy bodies into public ProbSpan files. Follow the actual Git-operation and owner-decision boundaries.
3. Read current `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `docs/ORIGIN_AND_SCOPE.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/BEHAVIOR_SPEC.md`, `docs/NUMERICAL_CONTRACT.md`, `docs/COMPATIBILITY.md`, `docs/PROVENANCE.md`, `docs/TESTING.md`, the four `docs/IMPLEMENTATION_*.zh-CN.md` technical guides, the whole `docs/TECHNICAL_DEBT.zh-CN.md`, and relevant GitHub issues, especially #1, #5, #6, #8, #9 and #10.
4. Inspect the actual current public header, relevant `src/` implementation, build config, testing/oracle sources, optional `integrations/device_history/`, and predecessor experimental `research/` code. Record **actual function/file/ownership boundaries**, not an imagined module diagram.
5. Read **all eight Phase A research artifacts** in `docs/research/phase-a/`, including 96-source registry, 52-entry crosswalk, seven provisional discoveries, empirical application cases and access caveats. Do not rely solely on A's executive summary.
6. Read **all eight Phase B canonical research documents**, its source addendum, the comparison protocol, scripts, JSON results, and the Phase B verification/handoff in `docs/research/phase-b/` and `research/phase-b/`. Check key claim-to-experiment/source traceability, not just the completion report.
7. Verify Stable v1.1.0 remains immutable and that newly merged A/B materials are research, **not expanded Stable API promises**.

### Current product boundary, subject to owner decision

The accepted v1 product is a **small, deterministic C probability -> uncertainty -> decision analysis core** with scoped provenance semantics. The caller handles data collection, event/entity identity, clocks, data storage, workflow, subjective assessment inputs, domain inference and evidence eligibility.

`docs/ORIGIN_AND_SCOPE.md` and Issue #1 are current scope authorities. They explicitly exclude a generic ML/statistics framework, all-purpose probability fusion, Brier/log-loss/ECE runtime, UI/DB/serialization, etc. as **v1 promises**.

Researching such topics is appropriate. Recommending a future extension may be appropriate **if and only if** the case is technically substantiated and clearly requires a subsequent owner product-scope decision. Do not silently turn research topics, open issues, or successful simulations into planned public features.

The already released 13-function public C ABI/API, exact parsing semantics, Jeffreys historical posterior/gate, subjective rules, odds/EV/decision meanings, numerical policy and provenance/order semantics are historical compatibility constraints. A proposed architecture cannot overwrite them by wishful thinking. If an alternative would require a contract break, identify a separate compatibility/migration option and its cost; do not edit the contract.

**Never merge different estimands simply because they produce the same type `double`.**

## 2. Phase A/B scientific conclusions that must be represented accurately

Read and substantiate each item yourself from accepted research files and underlying evidence, including:

- Three **different data families**: (i) mature binary outcome histories; (ii) feature + outcome samples; (iii) probability forecast + subsequently realized outcome histories. Different estimands, time availability and evaluation mechanisms.
- Readiness/sample count is not evidence admission or transportability; pool only under a defensible relation between source and target.
- No-target-data robust borrowing cannot identify hidden source/target conflict. Full pooling can improve RMSE dramatically under genuine agreement and be catastrophic under conflict; the Phase B results are **conditional experiments**, not validation of a particular real device or use case.
- Complete pooling, empirical Bayes, partial pooling, robust mixtures and no borrowing can all be meaningful under **different** assumptions. They are not interchangeable variants of a universal "Bayesian model" API.
- Conditional binary probability, parameter uncertainty, posterior probability of favorable EV, future batch count, count rate, time-to-event cumulative incidence, joint probability, distributional tail and calibrated forecast score may be different outputs with different units or event horizons.
- In B-E003 shared data made population-weight/risk covariance consequential. Ignoring overlap, estimating weights independently or failing positivity can change coverage or destroy identifiability.
- In B-E004 ordinary 1−KM treating competitor events as censored estimated a different quantity than the true competing-event CIF; adding a wrapper function does not fix missing risk-set observations.
- In B-E005 repeated use of a fixed-time test increased crossing frequency. Overall calibration can hide subgroup failures. Truth vintage, forecast time and selective outcome visibility affect valid evaluation.
- In B-E007 the ranking of pool vs hierarchical forecasting changed under player-weighted vs at-bat-weighted evaluation; review the target evaluation denominator before declaring winners.
- Numeric precision, output representation and probability semantics are separate. B-E006's 15/15 adjacent checks were under the **accepted 1e-10 probability tolerance**, **not** universal strict mathematical bracketing; a prior independent review counted only 10/15 strict checks. Do not silently strengthen the claim or present a failed strict bracket as a confirmed violation of the current numeric contract.
- Phase A's `NEW-A-001` through `NEW-A-007` and Phase B's `NEW-B-001` remain **provisional questions**, not newly approved permanent ledger IDs.
- R01–R04 are **completed historical repairs**; don't reopen them merely to justify work.
- Additional real-device external validation, raw-data industry replication and untested numerical toolchains remain missing. A/B simulations do not create those facts.

Use these observations as **claims to re-evaluate against the actual source**, not as a preselected architectural answer.

## 3. Core working philosophy: overlaps need a multidimensional decision

For every plausible pair/family of related methods, ask at least:

1. **Estimand overlap:** Are they estimating the same mathematical quantity, or only superficially named alike?
2. **Evidence overlap:** Do they accept the same source data, observation unit, time horizon, eligibility/independence assumptions, and missingness semantics?
3. **Mathematical overlap:** Do they legitimately share a likelihood, distribution, special function, inference operation or reference identity?
4. **Algorithmic overlap:** Could a common numerical primitive be verified once and reused without binding unrelated algorithms to one optimizer or tolerance?
5. **Contract overlap:** Are input validation, output statuses, units, interval interpretation and failure semantics actually compatible?
6. **Temporal/provenance overlap:** Can the same provenance metadata apply without implying scientifically validated admission or silently reconstructing an unobserved past?
7. **Operational overlap:** Who owns storage, calibration history, labels, dependence/duplicate decisions, serialization, data privacy, heavy numeric dependencies or runtime state?
8. **Maintenance overlap:** Would shared code reduce duplication and test costs more than it increases coupling, branching, compatibility risk and change propagation?
9. **Validation overlap:** Can the same tests/fixtures verify this sharing? Which tests must stay distinct due to different truth or guarantee?
10. **User value/scope overlap:** Would users actually need these paths together in a small auditable C package, or should one be a separate optional adapter/tool/application?

A pair might legitimately share **only one layer**. E.g., two families may share an incomplete-Beta routine but not a prior, result type, input eligibility or decision policy.

**Do not assume that shared mathematics means shared public API. Do not assume that independent APIs require duplicated numeric algorithms.**

Track both advantages and counterexamples for each proposed reuse. Explicitly justify deliberate duplication where isolation, clear ownership, licensing or distinct semantics makes it better than abstraction.

## 4. Seven fixed Phase C activities — one bounded review/design task

These activities form **one coherent authorized unit**. Do not split into micro-stages or separate releases. Iterate internally as needed, but finish at one reviewable PR.

### C1 — Consolidate A/B evidence and inspect the actual current call graph

Establish a complete fact base from the pinned accepted commits:

- Inventory actual public functions, C struct/types/enums, private numerical helpers, parsing, historical estimation, subjective scoring rules, odds/EV, decision policies, provenance transition logic, default/zero-state/failure semantics.
- Map existing source dependencies and calls, external installed consumer, frozen oracle and test responsibilities. Distinguish what is genuinely in core versus optional caller-side/device-history integration, research scripts and historical examples.
- Trace actual data and state through probability -> uncertainty -> decision. Identify where caller assertions about historical exposure, input admissibility or independence enter, and whether they are enforced, assumed or merely represented.
- Build a revision-backed list of current invariants, public promises and hard non-goals. Record exact path and call-site evidence.
- Map every A01–E48 candidate, NEW-A-001–007 and NEW-B-001 to one or more **architectural questions**, not invented features. Account for R01–R04 separately as immutable precedent/history.
- Classify evidence: formally proved, executed under stated synthetic DGP, public observational holdout, official documentation, software inspection, operational field validation, unverified/unknown.
- Flag any source/claim inconsistency but do not automatically modify accepted A/B artifacts or stable code.

The first deliverable is **an accurate current-vs-researched capability map**. Do not design interfaces until you can describe the real current ones.

### C2 — Discover true reuse, false similarities, deliberate separation and conflicts

Build a detailed **cross-method overlap/reuse matrix** with at least four categories:

- **Actually shareable mathematical/numerical primitives**, if proved equivalent and contract-compatible.
- **Potentially shareable internal engineering infrastructure**, subject to cost and contract conditions.
- **Shared conceptual/evidence vocabulary but intentionally separate implementations or outputs**, because semantics differ.
- **Unrelated, out-of-scope, unsupported or invalid merges**, with explicit rationale.

Explore (not limit to) these crosscuts:

**Statistical primitives and model semantics**
- Beta distribution CDF/inversion and other special functions vs fixed Jeffreys policy and model-specific likelihoods.
- Same Bernoulli likelihood under no pooling, full pooling, hierarchical/EB models, robust mixtures and historical discounting; determine what can be reused without collapsing distinct inference into one configurable parameter soup.
- Group-level posterior, new-group predictive, individual prediction, parameter interval, future-batch predictive distribution and decision-quality probability.
- Standardization, target weights and population mixture vs aggregation/complete pooling; different exposure units and estimands.
- Survival/CIF, rate/count, binary fixed-horizon risk and continuous threshold probability; ask whether relation is mathematical conversion under explicit assumptions or a genuinely shared engine.

**Data, domain and uncertainty boundaries**
- Independent mature event counts vs case-level observations vs repeated/clustered records vs censored histories vs forecast–outcome archives.
- Event eligibility, matching endpoints and horizons, source–target comparisons, posterior conflicts, selection bias, missing truth, duplicate detection, measure error and informative censoring.
- Partial-identification bounds/abstention vs model-produced estimates; a common status vocabulary may be possible without pretending identical inference.
- Expert elicitation and human subjective ranges vs empirical model intervals; avoid relabeling frozen subjective width as frequentist/bayesian coverage.
- Provenance/version/time/observation availability: common metadata vocabulary vs ownership of actual storage, audit logs, clocks and source evidence.
- Calibration/scoring vs making a new event prediction; probabilities of different events vs several forecasts of the same event; marginal and joint probabilities with unobserved dependence.

**Engineering/numerical/testing foundations**
- Exact decimal/binary64 semantics, relative/absolute error budgets, domain checking, status propagation, deterministic ordering and unchanged-output-on-error.
- Shared reference fixtures vs model-specific statistical validation; protection from false confidence from reused library backends.
- Public C ABI stability vs private helper reuse vs separate optional application/tool layers; resource/dependency footprints and portability.
- Test/scenario harnesses and evidence checklists for independently meaningful results; reuse that reduces error without coupling all applications to one schema.

For each important overlap/candidate, record:
- source methods and exact source/ledger IDs;
- each model's estimand, assumptions and I/O semantics;
- proposed reuse *level* (none, concept, validation, math kernel, private helper, distinct higher-level module, external adapter, separate project);
- alternative independent implementation;
- expected benefit, engineering complexity, proof/testing burden and failure/coupling risk;
- whether a common function can preserve existing contracts or would require a new boundary;
- a concrete **counterexample** where reuse would silently change meaning;
- evidence needed before accepting the shared abstraction;
- provisional recommendation with confidence and uncertainty, not feature authorization.

No empty labels such as "high overlap" without the actual shared invariant.

### C3 — Compare whole-project architecture alternatives, including no change

Do a **real alternatives analysis**. At minimum consider:

- **Baseline/no-change:** existing narrow ProbSpan core remains; research and caller-side validation continue elsewhere.
- **Minimal conservative extension:** preserve core, reuse only demonstrably general private primitives and add selected orthogonal pieces after approval.
- **Separately scoped vertical modules/adapters:** keep core minimal while keeping data-heavy model families or forecast validation in optional components or separate projects when appropriate.
- **Broader integrated library:** evaluate the credible benefits and serious costs of exposing multiple distinct statistical model families under one project. This is a comparator, not a preferred destination.
- Any **better architecture independently discovered** after studying actual source topology and evidence.

Do not make the above artificially exhaustive or force precisely four choices if a more appropriate decomposition emerges.

For each alternative analyze:

1. Which concrete user problems it solves or intentionally does not solve.
2. Data ownership, observation lifecycle, context/horizon semantics, and scientific claims.
3. Feature inclusion/exclusion criteria, separate products vs optional libraries vs caller-owned processing.
4. Reuse opportunities, duplication, module boundaries, coupling, dependency direction and likely cycle risks.
5. Public API/ABI and migration consequences (old installed consumer; error/decision semantics).
6. Portability and installed C11 footprint; optional NumPy/SciPy vs standard C; reproducibility.
7. Required real-world evidence and numerical/scientific validation to justify features.
8. Testing, maintenance, complexity, extensibility and cost of future methods.
9. Scientific misuse risk and users' likely interpretation of outputs.
10. What evidence would make you choose a different architecture.

A complex "universal plugin framework" is not automatically superior. A tiny core is not automatically sufficient for every future objective. Compare substantively and fairly.

### C4 — Produce a coherent **proposed** modular responsibility and contract design

After the comparisons, develop one or more defensible **conditional architecture blueprints**. Provide enough technical specificity that an independent reviewer can inspect boundaries and an owner can make meaningful choices, while **not** adding shipping APIs.

Include, where applicable:

- Layered responsibility and dependency-direction diagrams; ASCII/Mermaid is acceptable and should be text-source auditable.
- Existing-vs-proposed modules; reuses vs independent paths; current public vs proposed private vs optional/consumer-side boundaries.
- Clear data flow from external observations/evidence admission to model evaluation, uncertainty representation, downstream decision, forecast verification and audit trail **where such paths belong to the selected option**.
- Typed/semantic contracts in a **non-binding design notation**, distinguishing reference population, identity, unit, time horizon, data maturity, exact parameter meaning, uncertainty family, validation claims and decision inputs. Do not turn the result into one arbitrary "ProbabilityResult" hiding incompatible types.
- Where to enforce checks and where to require explicit caller-provided assertions/evidence because the library cannot infer them.
- Provenance metadata vs evidence validity: what can be recorded mechanically, what needs domain attestations, and what remains unknowable.
- Compatibility layering preserving legacy v1.1.0 semantics (do not silently reparameterize `Jeffreys`, gate, subjective intervals or odds).
- Handling of insufficient data, missing target support, contradictory evidence, numerical failure, incomparable horizons, incomplete labels and impossible identification. Distinguish errors from scientifically legitimate abstention.
- Model-specific tests, shared primitives' independent references, cross-path integration tests and tests that detect false sharing.
- Caller workflows and potential optional dependency models without making the core depend on a large runtime.
- Scope exclusions/deferments and why they remain separate.

Demonstrate the blueprint with a **small set of worked scenarios that actually stress the architecture**:
- valid versus invalid historical borrowing under source/target conflict;
- repeated/clustered/censored observations vs iid binary counts;
- a conditional forecast versus a historical probability estimate versus an evaluation score;
- posterior parameter threshold probability versus next-event probability;
- numerical precision or representability near a decision boundary;
- a prospective truth-version/selection problem (if scoring is considered);
- adding a new method without causing unnecessary changes to unrelated model families.

Treat these as adversarial probes, not a list of compulsory features. If an alternative does not support a scenario, show exactly which owner or external layer handles it, and whether that is an acceptable gap.

Design output should remain a **proposal pending owner decisions**.

### C5 — Cross-component integration, migration, complexity, and validation audit

Run an **integration-level review** on your leading candidate(s), not just disconnected notes about models.

Consider:
- Does a model/helper change propagate into other model contracts? Could that be prevented?
- Are two concepts deliberately duplicated? Why is duplicate code preferable here, if so?
- Does a shared validation gate conflate mathematical computability, enough sample, eligibility, applicability and future predictive quality?
- Can an invalid inference path accidentally produce a seemingly valid downstream EV/decision? Which uncertainty/status distinctions prevent that?
- Would a shared parameter/output record induce invalid conversions across probability estimands?
- Could new lifecycle/state features undermine deterministic/reentrant design or require hidden clocks/storage?
- Does the suggested design introduce unforeseen external dependencies, licensing obligations, data privacy/ownership complications or portability loss?
- Do current tests/oracles/consumer code demonstrate compatibility at relevant boundaries?
- Which changes would be backward-compatible additions, internal replacements, new optional artifacts, or genuine breaking changes?
- Is the design maintainable by a small open-source C project rather than a large statistics platform team?
- Could a substantially **simpler** architecture satisfy the actual justified use cases with less risk?

For each material risk, record severity in ordinary descriptive language with concrete failure paths and evidence. Distinguish confirmed defect, plausible risk, research gap and fundamental limitation. Avoid speculative fearmongering.

Where practical and useful, create **small design-only proof sketches or traceable static checks** (e.g., dependency inventory, source symbol map, sample contracts or algorithm equivalence derivation). Do not edit C implementation, build a new framework or declare an unexecuted prototype tested.

### C6 — Form a cohesive, conditional **Phase D entry plan**, not a release mandate

Phase D is one higher-level development/verification/distribution stage similar to the rigorous v1.1.0 engineering cycle. Do **not** initiate it. Phase C should help the owner understand what a bounded, feasible Phase D *could* implement after scope authorization.

Develop a **dependency-aware and risk-aware implementation candidate plan**:
- First separate **must preserve**, **justified candidate**, **research still needed**, **caller-owned**, **optional/separate**, **defer/reject**, and **owner decision needed**.
- For justified candidates, explain scientific prerequisite, contract assumptions, independent test evidence, numerical budget, data provenance, compatibility and acceptance criteria.
- Identify true shared infrastructure that would be implemented once *if* approved, and independent modules that can proceed without forced coupling.
- Highlight ordering constraints only where real (e.g., evidence applicability before statistical borrowing; semantic types before pretending incompatible results are interchangeable; numerical correctness and field validation as distinct gates).
- Offer a minimal coherent implementation slice and a reasoned expanded alternative **if** both are defensible; avoid planning dozens of token micro-releases.
- Identify provisional assumptions and unknown real-user requirements that need owner choice before substantial implementation.
- Include testable entry/exit gates for potential coding/RC/Stable processes but **no automatic version name, milestone dates or prescribed count of previews/RCs/releases**.
- Explicitly state what real data, independent scientific validation and platform test evidence are missing. Do not claim integration or CTest would validate those hypotheses.
- Preserve the freedom to **not implement** a capability if evidence/utility is inadequate.

The plan is an *owner decision aid*, not authorization to implement any candidate.

### C7 — Independent-style synthesis, contradictions, owner decision register and handoff

Challenge your own recommended design using an alternative-minded review, explicitly seeking:
- source/estimate conflations;
- overly convenient shared types or helpers;
- hidden exposure/observation assumptions;
- possible double counting of the same historical evidence;
- scoring/forecasting conflation;
- incompatible statistical validation and uncertainty interpretation;
- invalid status and decision propagation;
- strong public contracts unsupported by current real data;
- unnecessary public surface, packaging burdens, dependency cycles or costly maintenance;
- conflicts between accepted A/B evidence and architecture descriptions;
- places where "no change" remains the technically sound conclusion.

Produce a defensible synthesis:
- what genuinely overlaps and **why**;
- what must remain separate and **why**;
- what could be shared only after proof/validation;
- which paths are optional, deferred or outside ProbSpan;
- which decisions can be made technically and which require **explicit owner choice**;
- preferred *conditional* architecture alternative(s) with transparent disadvantages;
- major rejected alternatives with falsifiable reasons;
- identified implementation prerequisites and independent-review checks;
- what Phase C added beyond repeating A/B;
- what future observation would change each major conclusion.

Any nontrivial contradiction or evidence shortfall remains visible. Do not convert "recommend" to "approved".

## 5. Decision quality requirements (more important than volume)

Make reasoned trade-offs, not a fake matrix where everything is "medium complexity" and nothing is decided.

A useful Phase C should answer concrete questions such as:

- If both a fixed Beta-binomial model and a separate hierarchical model need Beta CDF/quantiles, can a stable internal numeric kernel serve both while leaving distinct model parameterization, prior validation and result semantics?
- If forecast scoring needs stored predictions and truth revisions, is the core library the right owner of the history store? Or is it merely a potential consumer of already validated snapshots? What would sharing provenance mean in each design?
- If multiple methods use `n` and "confidence," are they actually measuring the same sample unit, interval type, target and truth? What harm would a universal `confidence` property do?
- Can data eligibility be expressed with verifiable conditions, or does a C caller supply non-enforceable assertions? How to avoid silently treating an assertion as certified independent evidence?
- If relative rankings reverse under different scoring weights or source-target conflict, which architectural choices remain justifiable and what must stay configurable **outside** the model rather than inside frozen core policy?
- Is a shared error/status mechanism helpful, or would an all-purpose `VALID` flag hide three different concepts: computable result, sufficient sample and applicable evidence?
- Would adding survival/count/feature prediction into the same binary-oriented API create misleading conversions, or can they remain independent modules/consumer-side methods with only carefully shared primitives?
- Would an extra abstraction make future model integration materially cheaper, or would a small duplicate helper be easier to audit and maintain?
- Does a "clean" module graph change the probability/uncertainty/decision meaning, risk of scientific misuse or portability?

These are **thought exercises** to drive independent reasoning, not canned answers.

## 6. Traceability and research integrity

For every significant architectural claim, preserve a clear evidence chain:
- current product implementation/contract: file path, symbol, exact Git baseline SHA;
- Phase A: A source `Snnnn`, ledger ID, case study or original assumption;
- Phase B: experiment `B-E00n`, derivation, real-data case, provisional question or `B-Snnnn` source;
- inference or design judgment: clearly labeled as **your proposal**, with assumptions, risks and rejected alternatives.

Distinguish:
1. confirmed current behavior;
2. proved mathematical result;
3. synthetic experimental observation;
4. public observational or operational field evidence;
5. architectural inference and engineering estimate;
6. unsupported, unverified or owner-dependent possibility.

Avoid treating one synthetic RMSE number as a general complexity or benefit estimate; avoid invented engineering benchmarks and numerical precision claims. If important literature is needed beyond A/B, research it independently, verify URL/source version and record it as a **C source addendum** only, without manipulating A/B source history. New findings are welcome; this should not become a second Phase A mass literature survey.

Do not make external links the only evidence: cite stable source IDs and internal file references where applicable, and keep exact primary URLs in any source addendum.

Do not invent actor/use-case priorities, performance measurements, user demand or budget. Where empirical inputs are absent, give sensitivity, conditional choices and a concise owner-decision question.

## 7. Deliverables: one coherent Phase C design package

Create a **new** `docs/research/phase-c/` directory. Produce these canonical documents, Chinese for the substantive review:

1. `README.zh-CN.md` — navigable overview, actual accepted source revisions, the Phase C question, main *conditional* conclusions and clear non-authorization status.
2. `current-state-and-evidence-map.zh-CN.md` — verified current source/API/call/dependency map, A/B evidence map, all 48 permanent candidates, seven NEW-A and one NEW-B, plus four resolved repair precedents.
3. `overlap-and-separation.zh-CN.md` — thorough cross-method overlap, true reuse, deliberate separation, semantic incompatibility, coupling/duplication trade-offs, counterexamples and evidence anchors.
4. `architecture-alternatives.zh-CN.md` — credible whole-system alternatives including no-change; balanced comparison of utility, complexity, portability, API effects, scientific requirements and maintenance cost; conditional recommendations.
5. `proposed-boundaries-and-contracts.zh-CN.md` — one or more textual/diagrammed *non-binding* architecture blueprints, module responsibilities and dependency direction, semantic contracts, errors/status, data ownership, provenance and usage walkthroughs.
6. `integration-risks-and-validation.zh-CN.md` — adversarial review, impact analysis, actual constraints and missing evidence, realistic regression/field/numeric test design, dependency/ownership/ABI/license and migration risks.
7. `conditional-phase-d-plan.zh-CN.md` — a coherent implementation candidate sequence and entry/exit criteria **only under later user authorization**; no version, code or release implied.
8. `decision-register-and-handoff.zh-CN.md` — specific owner decisions needed, option benefits/costs, expert recommendation rationale, unresolved alternatives, no-action paths, source/ID audit and independent review checklist.

Also produce:
- `overlap-register.tsv` — stable row IDs (e.g., `C-O001`), related methods/questions, actual overlap dimensions, proposed sharing level, coupling/duplication risk, evidence IDs, alternatives and confidence/limitations. Include meaningful non-overlap and false-similarity cases, not just items marked reusable.
- `decision-register.tsv` — stable IDs (`C-D001`), precise decision, options including baseline/no change where appropriate, evidence, reversibility, compatibility/scope impact, recommendation and explicit status (`PROPOSED`, `OWNER_REQUIRED`, `DEFERRED`, etc.). **Do not set any row to OWNER_APPROVED unless actual owner authorization already exists in repository evidence.**
- Optional diagram source or small non-executable analysis tools **only** if materially improve verification. Do not create boilerplate code solely to make the artifact count bigger.

Keep document navigation simple and legible. Prefer structured side-by-side matrices and worked counterexamples, not hundreds of pages restating mathematical definitions already covered in A/B.

Do not edit the accepted Phase A or B records, `docs/TECHNICAL_DEBT.zh-CN.md`, product contracts, source tree or historical releases to "make them agree" with the new proposal. Point to a proposed future correction instead if evidence establishes a discrepancy.

## 8. Stage-wide acceptance checks

Verify that:

- All seven Phase C activities have substantive evidence.
- All eight canonical documents and two registers exist, are internally consistent, and navigate correctly.
- The product source/public API/ABI, existing tests, released version and Phase A/B evidence **remain byte-for-byte untouched**.
- The A/B accepted HEADs and actual current source are pinned and source claims checked.
- All 48 A–E, seven NEW-A and one NEW-B questions are accounted for, and R01–R04 remain historical repairs; a question can justifiably map to "no integration opportunity" or "not enough evidence".
- The overlap matrix contains genuine reuse, false similarities, meaningful deliberate separation and cases of insufficient evidence.
- The architecture options are substantively different and evaluate current no-change as a serious control.
- The recommended proposal includes negative/competing analysis and concrete reasoned boundaries, not a universal model that erases estimands.
- At least a few critical cross-path walkthroughs test proposed responsibilities and failure/status propagation.
- No claim that shared code implies statistical validity, or that a CI pass implies field model validity.
- Contracts, data ownership, provenance, evidence eligibility, decision status and numerical constraints are kept distinct where needed.
- All material tradeoffs have evidence and honest unknowns; decisions needing owner approval remain unapproved.
- The Phase D plan is conditional and bounded. It cannot itself approve the implementation, version or publication.
- Local paths/links/anchors, TSV parsing/column consistency, stable references, Markdown syntax and `git diff --check` have been validated. Record checks actually executed.
- There is no leakage of private governance text, credentials, or third-party copyrighted material.
- No production code, scripts, tests or numeric reference files were changed, and no runnable implementation of proposed models was added.

There is no numeric score target for design quality or source count quota. Stop when the review is coherent, the central overlaps and counterexamples have been considered from multiple directions, and decision options plus evidence gaps are sufficiently concrete for independent review. Avoid an unbounded analysis cycle.

## 9. Git permissions and execution stop point

The dedicated Phase C branch `docs/phase-c-integration-architecture-brief` starts from accepted main `45075a1da4adedf871299d148ef7dfa502335d72`. This task brief is committed as a new file on that branch.

This task **authorizes Codex** to:
- read the authenticated authorized private policy repository and public ProbSpan/current research;
- investigate literature or source code necessary for architecture reasoning;
- create **Phase C research/design files only** in `docs/research/phase-c/` and minimal new supporting source-only design assets there;
- check its documents and perform isolated, non-invasive static/research validation;
- commit and push its research work **to the designated Phase C branch only**;
- open **one PR** against `main` for **independent review**, with exact SHA evidence.

This task **does not authorize Codex** to:
- merge its own PR; change `main` directly; push other branches; force-push or rewrite history;
- edit v1 C implementation, public headers/API/ABI, root tests/oracle, CMake, CI, dependency manifests, installed consumer, interfaces or version metadata;
- modify Phase A/B reports, the permanent ledger or private Development-Playbook;
- create PRs in other repositories, product releases, RCs, tags, or edit existing tags/releases;
- implement the architecture, start Phase D, silently enlarge product scope, or accept its own findings as independently PASS;
- use a nested Cloud task to circumvent unavailable shell/Git/network access.

Preserve unknown checkout changes. If the branch has advanced, inspect and adapt rather than resetting.

**Stop after pushing one reviewable PR and writing the completion report**. A later user decision is required before implementing the suggested architecture or proceeding to Phase D.

## 10. English final report

Provide a precise, evidence-backed report (in English):

1. Repository and actual `main`/task branch starting HEADs, final local + remote + PR HEADs and tree, working-tree state.
2. Governance read/access facts without private content disclosure, source/public contract and Phase A/B files actually read.
3. Seven activity outcomes; canonical documents, TSV registers and any supporting diagrams.
4. Mapping counts for 48 + 7 + 1 provisional and R01–R04, with evidence of completeness.
5. Most consequential real reuse opportunities, meaningful false similarities and intentional separations; source/experiment anchors.
6. Contrasting architectural alternatives; why any conditional recommendation beat the no-change baseline and under what evidence it would not.
7. Design tradeoffs, dependency boundaries, semantic/output/status/provenance analysis, ABI/consumer/portability risks, and adversarial scenario results.
8. Owner decisions still required; unresolved scientific/data/field verification constraints; non-approved status.
9. Actual internal-link, TSV, traceability, scope and diff checks; CI only if actually available for the exact HEAD; limitations.
10. Technical Debt Impact: no change to the permanent ledger or product, note evidence-only implications and IDs separately.
11. Commits, PR link, open/unmerged status, precise stop point. No claim to independent PASS or Phase D approval.

This ends Phase C design research only.
