# ProbSpan — Phase B: Mathematical Model Evaluation and Comparative Research

**Status:** One authorized, bounded research task; independent review required.
**Repository:** `RXY712200/ProbSpan`.
**Designated working branch:** `docs/phase-b-model-comparison-brief`.
**Accepted Phase A merge / expected main baseline:** `e47c038cd2b1997d87b7fe303f9037c80e6eb955`.
**Accepted Phase A research commit:** `4bc0e28d60bf7c618543aa0d789f34a29d0f4ec6`.
**Published product baseline:** Stable `v1.1.0`; release source commit `46ff21847c5522eb983d3f58e396354461a64f34`.

## 0. Read this first — self-contained, cloud-native task

This document is the complete execution brief for **Phase B**. It must remain usable from a brand-new Codex cloud context with no chat history, previous model memory, local computer, personal files, cached repository contents, or preexisting research state. The user's computer may be off.

Read this actual GitHub file and the repository's current authoritative sources. Establish access to the authorized private governance repository using the account's own connection. Do not ask the user to reconstruct an earlier conversation or keep a local PC running. Work in an available cloud checkout and install only temporary research dependencies you genuinely require.

**Do not mistake this document for a list of winning models.** Your job is to think independently, discover and defend meaningful comparison questions, develop fair mathematical tests, test counterexamples and uncertainty, and distinguish what is known from what cannot yet be known. The examples and candidate families below orient your search; they are not an exclusive method list, mandatory implementation backlog, or predetermined answer.

This is **Phase B only**. The user's larger framework is:
- A: broad scholarly, real-world, software, and community research — **completed and independently accepted**;
- B: rigorous mathematical and methodological comparison — **this task**;
- C: synthesis across findings, overlap/duplication and coupling review, whole-project architecture/scope decisions — **not authorized yet**;
- D: implementation, tests, independent review and controlled publication — **not authorized yet**.

You may flag questions for C without designing C or D in advance.

## 1. Goal and epistemic standards

Convert the accepted Phase A **evidence corpus** into a defensible, reproducible comparison of statistical questions, mathematical models, input assumptions, numerical approaches, validity limits and consequences for probability-based decisions.

Important distinctions:
- A mathematically valid formula may solve the **wrong estimand**.
- A statistically reasonable method may be unusable because its assumptions are uncheckable or contradicted by the evidence.
- An algorithm may be numerically correct but not scientifically applicable.
- A simulation may prove a conditional behavior under its data-generating assumptions without proving field applicability.
- A field score may demonstrate past performance without identifying the causal mechanism or ensuring transportability.
- A method may be correct only within a specific model and have no universally valid extension.
- A carefully supported **no justified estimate**, identifiable bound, conditional verdict, or counterexample is a successful scientific result.

Do not confuse observed empirical coverage with a theorem; do not confuse posterior credible mass with frequentist coverage; do not compare methods that predict different targets as though one had won.

The Phase B deliverable should make it possible for an independent reviewer to locate each important assumption, source, derivation, input case, executable experiment, actual output, and uncertainty, and challenge any comparative claim.

**No model selection, feature priority, API design, new version target, or architecture decision is authorized by this task.** Conditional statements such as "under stated assumptions method X had less bias than Y in this setting" are allowed. Unqualified "ProbSpan should implement X" is not.

## 2. Establish the complete and exact accepted baseline

Before research, verify:
1. Current public repository, branch and clean/unfamiliar working-tree status. The expected accepted `main` is `e47c038cd2b1997d87b7fe303f9037c80e6eb955`. If it changed, inspect the changes and record their effect instead of silently assuming or resetting.
2. Phase A PR #17 was merged, and the accepted eight research artifacts are available on `main`.
3. The current and complete authenticated private `RXY712200/Development-Playbook/WORKFLOW.md` and `RELEASE_POLICY.md` have been read. Do not publish or paraphrase private policy details into the public repository; follow the actual current authorization rules.
4. Current ProbSpan `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `docs/ORIGIN_AND_SCOPE.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/BEHAVIOR_SPEC.md`, `docs/NUMERICAL_CONTRACT.md`, `docs/COMPATIBILITY.md`, `docs/PROVENANCE.md`, and the four `docs/IMPLEMENTATION_*.zh-CN.md` source guides as relevant.
5. The full `docs/TECHNICAL_DEBT.zh-CN.md`: 48 fixed research/capability candidates A01–E48 and four **historically resolved repairs** R01–R04. They are not 52 defects awaiting code fixes.
6. All accepted Phase A artifacts in `docs/research/phase-a/`, **not just its README**:
   - `README.zh-CN.md`;
   - `source-register.tsv` (96 unique records at acceptance; S IDs have actual sources and reading levels);
   - `search-log.md`;
   - `methods-and-assumptions.zh-CN.md`;
   - `real-world-and-software.zh-CN.md`;
   - `ledger-crosswalk.zh-CN.md`;
   - `new-questions-and-gaps.zh-CN.md` (seven provisional NEW-A-001–007 questions);
   - `verification-and-handoff.zh-CN.md`.
7. Earlier accepted `docs/HISTORICAL_EVIDENCE_RESEARCH.zh-CN.md`, `docs/PREVIEW_PROBABILITY_MODELS.zh-CN.md`, `docs/PREVIEW_DEVICE_HISTORY.zh-CN.md`, and `research/preview_history.py` / recorded results.
8. Relevant GitHub Issues, especially #1, #5, #6, #8, #9, #10; current source, public headers, frozen oracles and tests where a claim depends on actual implementation.

**Source hierarchy:** current product contracts and Git-referenced implementation > actual executed tests and reference evidence > accepted research and source metadata > proposals and informal claims. External scientific sources independently support external theories, not claims that ProbSpan already implements them.

At acceptance, Phase A identified missing real-device external validation, incomplete reproduction from raw industry data, and untested additional numeric platforms. These must not be silently "resolved" by new synthetic results.

At the last independent review, the source registry had one small metadata omission (S0029's DOI), which did not undermine the source link. Verify whether that or any other bibliographic issue matters to the new work. Record corrections in a Phase B source errata/addendum; **do not silently rewrite Phase A historical artifacts**.

## 3. Research planning and freedom to reason

You must begin Phase B by designing the **mathematical comparison questions from Phase A**, not from the list of examples in this prompt.

Write a brief internal research plan that:
- identifies high-value unknowns and where different candidate methods truly target the same quantity;
- distinguishes separately scoped problems that should not be ranked against one another;
- decides which comparisons can yield theorem/derivation, which need simulation, which need public empirical data, and which cannot be answered without new field evidence;
- selects **several substantively different deep-study families**, avoiding the trap of doing only Beta-vs-Wilson on one toy binomial problem;
- explains why some candidates get only a structured assessment, while others deserve deeper experimental work;
- reserves room to add or replace candidate methods if research reveals a better alternative;
- records decision criteria before examining simulation outcomes where feasible, to avoid cherry-picking.

There is no forced universal winner, no rigid number of algorithms, and no instruction to "prove Bayes is best". You may reject an entire family of comparisons as invalid if their estimands differ.

You must assess the entire Phase A problem inventory at **coverage level**, and work in **depth** where comparisons are actually meaningful. Do not repeat broad Phase A literature discovery for its own sake; new research is welcome when necessary to resolve disputed or under-evidenced mathematical claims.

**Use your own mathematical judgment.** The lists below are invitations to investigate, not instructions to run every algorithm against every scenario.

## 4. Phase B's six fixed activities

Complete these six activities as one bounded research unit. They are not separate PRs or releases. You may iterate between them when new evidence exposes a flawed assumption, but record genuine changes rather than creating an endless series of new numbered stages.

### B1 — Formalize the scientific questions, targets and observability

For each materially distinct question in the Phase A corpus, clarify as far as possible:

- What is the estimand? E.g., unknown Bernoulli risk in one stable population, a future single-unit predictive probability, target-population standardized risk, count in a future interval, time-to-event CDF, forecast skill, decision utility, evidence independence, or a purely numerical function.
- What is the population, observation unit, prediction information set and time horizon?
- Which observed variables and outcomes exist **at the time of the forecast**, and which are only learned later?
- What kind of uncertainty is at issue: parameter, outcome, group, data collection, missingness, model selection, target selection, numerical representation or unknown causal mechanism?
- Is the estimand identified, partially identified, or not identified under stated data and assumptions?
- What is a mathematically valid baseline? An empty-data/abstain case, no-borrowing model, simple constant/climatology, current ProbSpan v1 behavior, or another appropriate baseline?
- Which comparisons become invalid when different algorithms refer to different quantities or observations?
- Which assumptions are domain-supplied rather than inferable by the library?

Preserve distinguishable input families: outcome history, feature–outcome training data and **forecast–outcome performance history** are not interchangeable.

Build a complete coverage map for A01–E48 and NEW-A-001–007, plus separate reference entries for R01–R04. A coverage entry may state "no comparison justified" or "requires field evidence", with the mathematical reason.

### B2 — Establish candidate models, explicit assumptions and fair baselines

For each selected deep-study problem, **independently decide** which mathematical approaches are plausible from verified sources. Include competing paradigms if genuinely relevant.

Potential research families (NOT a mandatory model list):
- small-sample binomial intervals, Jeffreys and other priors, posterior predictive vs parameter uncertainty, rare and zero-event risks;
- reference-class selection, elicitation, sparse-history borrowing, no/complete/partial pooling, empirical and full hierarchical Bayes, robust/power/commensurate priors and sensitivity;
- cluster/repeated-observation dependence, source overlap, unknown correlation, effective sample size, informative censoring and competing risks;
- source/target admissibility, transportability, population standardization, target weights and their uncertainty, non-overlap or partial-identification bounds;
- feature-based conditional prediction, count/rate, survival, continuous/threshold, sequential and time-varying processes where the estimand truly requires those families;
- scoring rules, calibration, discrimination, properness, sharpness, forecast horizon, subgroup/conditional validation, selective labels, abstention and value of information;
- joint events, model disagreement and correlated prediction sources **as research**, not assumed product features;
- deterministic numerical approximations, tails/quantiles, interval and status robustness, cross-platform and high-precision references, where Phase A identified a real uncertainty.

For each candidate method collect:
- precise mathematical definition and estimand;
- source-backed derivation or proof status;
- likelihood/data-generating assumptions and prior or tuning choice;
- conditions for identifiability/consistency/coverage or the actual conditional guarantee;
- handling of zero data, sparse data, incompatible data and unsupported regions;
- failure semantics / natural abstention or bounds;
- output interpretation (confidence vs credible vs prediction, risk vs hazard, score vs utility);
- fair baseline(s), comparison metrics, sensitivity parameters and resource implications;
- evidence strength, limitations and counterexamples;
- compatibility with *current* ProbSpan only as a factual research boundary, **not an integration design**.

Do not equate mathematical complexity with superior decision performance. Prefer simpler controls in each valid comparison.

### B3 — Derive and challenge the mathematics before trusting code

Develop independent, inspectable derivations and analytical counterexamples that can be checked without trusting a simulation package. Wherever possible:

- verify key identities, posterior updates, predictive moments, identification bounds, estimator expectations and variance expressions;
- distinguish exact mathematical properties from asymptotic approximations or implementation heuristics;
- analyze prior sensitivity, target weighting uncertainty, model misspecification and threshold crossings;
- construct **observationally equivalent data-generating processes** with different target answers to demonstrate non-identifiability;
- test whether "robust" borrowing can detect genuine source–target disagreement with **zero** target outcomes;
- explore when apparent increases in sample size create false precision because of dependence, selection or duplicate evidence;
- distinguish marginal calibration/coverage from conditional and subgroup guarantees;
- distinguish rolling real-time evaluation from leakage through future labels or truth revisions;
- distinguish an inferential uncertainty interval from numerical discretization or floating-point range;
- assess decision correctness under probability uncertainty, threshold rounding and potentially asymmetric costs.

If the literature has a theorem of impossibility or a negative result, summarize its exact assumptions and scope; never present it as "no algorithm can ever solve related problems".

A failed derivation or a counterexample invalidating a favored method must appear in the final report.

### B4 — Execute controlled comparisons and independent numerical checks

For selected **experimentally tractable** questions, write and **run** small, reproducible, research-only scripts, using transparent data-generating processes, deterministic seeds, documented environments and, when needed, independent high-precision references.

Use `research/phase-b/` for research scripts, inputs/manifests and machine-readable outputs, and `docs/research/phase-b/` for the interpretation.

Create experiments that actually discriminate methods; do not simply verify that every algorithm returns a number.

Choose scenarios proactively based on Phase A and B1–B3, for example where relevant:
- honest stationary iid event history vs sparse/rare/no observations;
- target/source agreement vs drift vs hidden conflict and absent target labels;
- common vs heterogeneous strata, changed target composition, missing support and estimated weights;
- independent vs repeated/clustered/overlapping evidence;
- adequate vs biased measurement, truncated follow-up and competing outcomes;
- feature shift, delayed labels, data leakage, temporal drift and new populations;
- prediction reliability by subgroup/horizon vs aggregate score;
- valid versus invalid optional stopping, selective prediction and abstention;
- extreme tail, large count, representation boundary or numerical budget failures.

Not every scenario fits every model. Keep a separate problem-specific protocol, matched target and common valid information set.

Experimental discipline:
1. State the true data-generating mechanism and estimand; distinguish known truth in simulation from unknown truth in field data.
2. Define controls, scenario grid, independent variables, evaluation metrics and relevant limits **before** tuning or seeing results.
3. Use appropriate paired comparisons / common random numbers where beneficial; avoid reusing outcomes or tuning on the evaluation set.
4. Report Monte Carlo uncertainty, finite-replicate uncertainty and relevant convergence diagnostics. Don't assert differences smaller than simulation error.
5. Test sensitivity to priors, sample sizes, group imbalance, dependence, measurement errors, weight estimation and misspecification as relevant.
6. Respect rare-event and extreme-region numerical stability; report true error bounds or disagreement with independent references, not just "passed".
7. Include failure and counterexample cases as well as easy successes.
8. Record enough environment, input, version, seed, command and output to rerun in a fresh cloud environment.
9. If software or runtime limitations prevent a meaningful comparison, record exactly what was not executed; do not fabricate numeric output.
10. Choose tests for actual scientific value, not a quota of scripts, graphs, models or repetitions.

Metrics must match the object: posterior interval coverage only under a specified repeated-sampling setup; Brier/log score for properly paired binary forecasts; CRPS/WIS for compatible distribution/quantile forecasts; hazard and survival metrics only with censoring semantics; error or abstention costs for actual decisions. Note that coverage alone does not establish calibration, and high predictive skill does not prove causal interpretation.

Avoid gratuitous compute or proprietary datasets. Prefer lightweight experiments with independent evidence where possible; larger experiments only when their scientific value justifies them.

### B5 — Confront mathematical comparisons with external evidence

Use Phase A's existing verified bibliography and actual case studies to ask whether conditional simulation claims survive contact with published operational and field results.

Differentiate:
- theorem or algebraic derivation;
- source paper's empirical/simulated findings;
- your own executed experiment;
- official software/reference implementation behavior;
- published field validation;
- anecdotal practitioner issue or forum discussion.

Use published data, reproducible example inputs or public evaluation tables **when legitimately available**. If feasible, reproduce carefully selected real-data analyses or relevant summary metrics with provenance and allowed licenses. Do not claim a source-level paper replication when only a number from its abstract was checked.

Independently revisit surprising or contradictory claims; use additional sources beyond Phase A where gaps demand, discover them yourself, verify exact URLs, DOI/version/code SHA and record access level. No source-count quota. Do not make B a second indiscriminate 96-source discovery exercise.

Explicitly state:
- conditions supported by field evidence;
- conditions only demonstrated in simulation;
- important design differences across domains (weather, clinical risk, hardware, economics, etc.);
- where no public data permits realistic external validation;
- whether a result depends on observation horizon, truth vintage, population, data provenance or action-induced selection;
- which plausible statistical guarantees are unknowable from currently available input.

If a real-data result contradicts an analytical expectation, diagnose whether the estimand or assumptions differ rather than forcing a preferred narrative.

### B6 — Synthesize a conditional evidence map and research handoff

Combine B1–B5 into a scientifically candid evaluation:

- For **each comparable question**, what is supported, refuted, conditional or unresolved?
- Under what assumptions would different methods be defensible?
- Which methods are demonstrably inappropriate on particular input types?
- Which uncertainty/error guarantees are actually established?
- Which counterexamples falsify attractive shortcuts?
- What comparisons are impossible without future observations or additional assumptions?
- What measurements or experiments would most efficiently reduce genuine uncertainty?
- What did Phase B **learn beyond Phase A** rather than merely rephrase its bibliography?
- What overlaps, incompatible assumptions or interface concerns should later Phase C examine? **Only flag them as questions; do not design or merge modules.**
- What independent reviewer evidence is available for every significant claim?

A multi-method/conditional outcome is welcome. Do not award a single global winner to incomparable methods. Do not convert research findings into implementation approvals or update ledger states.

## 5. Required comparisons and substantive coverage

This section is a **coverage checklist**, not a command to use one uniform model or benchmark.

Investigate across these dimensions where they actually affect Phase A's questions:

**Data and meaning:** event identity, population/reference class, unit, horizon, time availability, missingness, censoring, leakage, duplicates, dependency, provenance and outcome revision.

**Inference:** identifiable vs partially identifiable vs unknown; distribution/parameter/predictive uncertainty; Bayesian and frequentist alternatives; sensitivity to prior/likelihood/data model, empirical vs hierarchical estimates.

**Transfer:** matched vs incompatible evidence; observed vs hidden source-target differences; overlap/positivity; standardization with fixed vs estimated target weights; transport claims supported only under assumptions.

**Verification:** posterior correctness vs statistical coverage; calibration by group/time/horizon; proper scores and loss; actual out-of-sample validity; forecast-selection bias; whether abstention changes the evaluation denominator.

**Numerical:** stable algorithms, extreme inputs, adjacent representable values, independent high-precision checks, failure budgets, exact vs tolerance-contracted results; source of any disputed numeric difference.

**Decision:** input probabilities as beliefs vs empirically calibrated forecasts; threshold sensitivity, utility/loss and risk of confident unsupported output.

Treat the seven Phase A provisional discoveries as real research questions, not already approved ledger additions:
- `NEW-A-001`: preliminary vs revised outcome truth;
- `NEW-A-002`: selective or action-dependent labels;
- `NEW-A-003`: sequential monitoring and optional stopping in evaluation;
- `NEW-A-004`: measurement/label error even under nominally identical endpoints;
- `NEW-A-005`: uncertainty from estimated population weights coupled with risk estimation;
- `NEW-A-006`: numeric or input representation near decision boundaries;
- `NEW-A-007`: selective prediction/abstention, score denominator and decision costs.

Investigate newly discovered questions if material. Assign **provisional Phase B IDs** (e.g. `NEW-B-001`) and explain why they are distinct. Do not silently absorb them into permanent A–E numbering.

## 6. Evidence, citation and computation provenance

**All nontrivial claims must trace to real evidence.**

Reuse accepted Phase A source IDs `S0001` etc. from `docs/research/phase-a/source-register.tsv`, but **check the actual content and access level** before relying on a particular quantitative or theorem claim. Some entries were abstract-only or metadata-only; do not upgrade their authority.

New external sources found in Phase B receive stable, non-colliding `B-S0001` identifiers in a **separate addendum**. Record complete title, author, year, DOI or source identity, original URL, full-text location when possible, access date, checked content level, exact relevant claim, limitations, corrections/contradictions, and immutable Git source links if software is inspected. No invented DOI, link, proof or code version.

Every executed experiment needs:
- a unique stable experiment ID (`B-E001` etc.);
- question and estimand;
- source-derived method definition;
- scenario input, true mechanism/constraints and test data;
- parameters/seeds/repetitions and any intended precision budget;
- software versions, commands and environment;
- output file(s) and result interpretation;
- uncertainty/diagnostics and failures;
- source IDs and the ledger/provisional questions addressed;
- exact reproducibility status (executed, partially reproduced, or illustrative only).

Keep scripts understandable, small and testable. Machine-readable outputs (JSON/CSV/TSV) must be valid and their interpretation must be consistent. Prefer text/table summaries to large binary plots; images are optional, not evidence substitutes. Do not commit enormous datasets, binary archives or licensed third-party corpora.

For evidence rankings, distinguish: proof under assumptions, independent analytic derivation, controlled simulation, field/operational assessment, partial software inspection, documentation, and practitioner allegation. Record the strength of *each conclusion*, not a fabricated confidence percentage.

## 7. Canonical deliverables

Create a new `docs/research/phase-b/` directory with the following **eight canonical Markdown documents**, plus the source and experiment artifacts described below. Chinese is preferred for substantive science explanations; retain exact mathematical notation, paper titles, field names, source IDs and shell commands.

1. `README.zh-CN.md` — self-contained navigation, source baseline, precise Phase B question, key **conditional** findings, limitations and evidence hierarchy.
2. `problem-estimand-map.zh-CN.md` — 48 A–E + seven NEW-A questions, separated R01–R04 history; scientific question, estimand, information set, identifiability, possible comparisons or reason none applies; links to accepted A.
3. `candidate-models-and-assumptions.zh-CN.md` — model families chosen by the research itself, exact definitions, assumptions, alternatives, fair baselines, when not comparable, counterarguments, and evidence links.
4. `derivations-and-counterexamples.zh-CN.md` — independent mathematical derivations, limiting cases, impossibility and negative results with precise conditions, worked examples and source attribution.
5. `experiments-and-results.zh-CN.md` — actually executed protocols, experiment IDs, direct output links, scenario-specific results, Monte Carlo uncertainty, numerical-reference checks, interpretation, failures and missing runs.
6. `external-evidence-and-limitations.zh-CN.md` — comparison with published operational evidence; source quality; unresolved field applicability; deviations from original papers and external datasets.
7. `conditional-findings.zh-CN.md` — compact cross-method **conditional** comparison maps. Prefer "when assumptions X and Y hold, these relative properties were observed/proved" over universal ranks. No approved model list.
8. `verification-and-phase-c-handoff.zh-CN.md` — research integrity review, actual file/SHA/tests, bibliography/ID audits, source corrections, independence limits, residual uncertainties and **questions only** to be resolved in Phase C.

Also create:
- `docs/research/phase-b/source-addendum.tsv` for newly verified B sources, with documented schema; it may contain only a header and an explanation if no new sources were needed.
- `research/phase-b/` containing reproducible research scripts, a short README of commands/environment and any lightweight machine-readable outputs. Use scripts only where scientifically valuable; research code is **not** the shipping C library.
- Optional supporting documentation or scenario input manifests if truly needed for clarity.

Do not simply copy the old Phase A catalog into Phase B. Cross-reference its stable source IDs and focus on new mathematical work.

## 8. Quality gates and honest stopping conditions

Complete an evidence-led review before opening a PR. Acceptance is about **validity and inspectability**, not number of pages, algorithms, figures, or paper citations.

Required:
- All eight Phase B documents exist, are substantive and navigable.
- Every A01–E48 and NEW-A-001–007 research question is accounted for; R01–R04 are visibly historical, not re-opened bugs.
- Several distinct, legitimately comparable scientific problem families receive deep analysis, not one toy binomial example cloned throughout.
- Mathematical derivations and important negative results are shown clearly enough to be checked.
- Relevant controlled experiments **actually ran**, with exact source, outputs, uncertainty and independent checks. Intractable/unidentifiable cases are addressed by proof or limits, not counterfeit simulations.
- The research explicitly tests or identifies failure and adversarial conditions, not only favorable performance.
- Results comparing methods state the same estimand/information set or openly explain why comparison is invalid.
- All source and experiment IDs resolve, and source-access distinctions remain honest.
- Novel mathematical claims either have a defensible proof, an executed reproducible test (within its scope), or are plainly marked conjectural.
- All internal Markdown links, anchors, TSV and machine-readable results are checked; `git diff --check` passes.
- Approved Stable release and accepted Phase A source artifacts remain unchanged.
- No private governance text, personal credential, copyrighted full paper or hidden data is committed.
- The report does not choose next version, new API, architecture or release strategy.

Be explicit where assumptions cannot be validated from the available input and where field evidence is still missing. A high-quality conditional negative result is a completed Phase B result, not a failure to find the "right algorithm".

Do not invent external test results, source visits, CI logs, peer-review status, proof, or field validity. If environment limitations prevent an essential research result, report exactly what remains blocked and submit only genuinely supported results for inspection.

Use a bounded, honest stopping criterion: once the planned comparisons are sufficiently rigorous, representative problem families have been evaluated, major discrepancies have been investigated and unanswerable questions have been identified, finish and submit. Do not perform indefinite literature searches or attempt every conceivable model just to appear comprehensive.

## 9. Git permissions and stop point

This file is placed on the dedicated branch `docs/phase-b-model-comparison-brief`, created from the accepted Phase A `main` baseline.

You are authorized to:
- access and read the current repositories and connected, authorized private policies;
- investigate public external literature and software;
- create/update **new Phase B research files** under `docs/research/phase-b/` and **new research-only experiment code/results** under `research/phase-b/`;
- make minimal navigation links if genuinely required, without rewriting earlier conclusions;
- perform local computations and verifications using temporary dependencies;
- make reviewable research-only commits and **push this designated research branch only**;
- open **one PR** against `main` for independent Phase B review, recording exact head SHA.

You are **not** authorized to:
- merge the PR or modify `main` directly;
- edit or rewrite accepted Phase A findings, original permanent technical-debt statuses, public product behavior, source code, public header, oracles, root tests, CI, release history or private policies;
- alter old release tags, create new release tags, publish Preview/RC/Stable, or claim any new product version;
- insert unapproved runtime dependencies into the installed library;
- force-push, reset away unfamiliar changes, overwrite history, or touch unrelated projects;
- silently expand into Phase C architecture synthesis or Phase D software implementation.

If material new evidence challenges the correctness of published ProbSpan code, document the exact affected behavior, evidence and reproducible case, and flag it for independent review. Do not quietly fix production in this research-only PR.

On task start, independently verify that the task branch and main match expectations. If the branch has advanced, inspect the diff; preserve others' work. The user expects cloud-native execution without local host dependencies.

After submitting one reviewable PR, **STOP**. A Codex completion report is not independent PASS, and Phase C cannot begin from this task's permission alone.

## 10. Final English completion report

Provide an English report with:

1. Actual starting `main` and task-branch SHA, exact final branch/PR HEAD and Git tree, local/remote synchronization and workspace cleanliness.
2. Policies/repository/Phase A artifacts actually read (no private policy contents).
3. Six activity outcomes, eight core deliverable links and runnable experiment files.
4. Coverage status of all 48 + seven provisional questions and four repair-history records.
5. Method-family/estimand comparisons actually performed and rationale for choices/exclusions.
6. Actual derivations, analytical counterexamples and important negative/conditional findings, with source and section pointers.
7. Executed commands, inputs, seeds, environments, numeric outputs, convergence and Monte Carlo uncertainty; explicitly list unexecuted analyses.
8. External source addendum, bibliographic checks, field-data access and unreproduced limitations.
9. All material contradictions, invalid comparisons, newly discovered provisional questions and remaining evidence gaps.
10. Documentation/link/TSV/experiment validation evidence; actual diff, CI evidence if any and unchanged production contracts.
11. Technical Debt Impact: **No modification to permanent ledger status/priority/implementation**; note any newly observed risks without changing historical entries.
12. Git commits, one PR URL, open/unmerged status, scope boundaries and what an independent reviewer must verify.

Finish after the PR is open. Do not prescribe or start Phase C.