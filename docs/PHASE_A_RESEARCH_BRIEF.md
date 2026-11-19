# ProbSpan — Phase A Comprehensive Research Brief

**Status:** Authorized research assignment / self-contained handoff for a fresh Codex context.
**Project:** \`RXY712200/ProbSpan\` (public repository).
**Task branch:** \`docs/phase-a-research-brief\`.
**Reference main SHA at task creation:** \`2cf68294a6a420d77c7fd1016157fdeb9a65d8a5\`.
**Published Stable release:** \`v1.1.0\`; approved source commit \`46ff21847c5522eb983d3f58e396354461a64f34\`.
**Stable source tree:** \`0cf4a495a547e4c6f4a434e334a9a3809027e386\`.

## 0. CRITICAL: independent, cloud-capable execution

This file is the complete source of task instructions. A brand-new Codex cloud session must be able to complete the assignment without any previous conversation, personal memory, local desktop file, Windows path, cached source, temporary notebook, or unpublished draft.

Start by opening this file from the authenticated GitHub repository. Read the repository and authoritative policy files yourself. Do not assume any earlier context, existing local checkout, installed dependency, or previously gathered bibliography. Use the cloud workspace's available checkout, web/browsing, GitHub access, and ordinary research capabilities. Cloud-only execution is fully acceptable; the user's PC may be powered off.

If an available environment lacks repository access, private-policy access, or external research access, identify the exact limitation and use other permitted access paths. Do not invent sources, findings, test runs, or Git commits. If essential access genuinely cannot be obtained, finish with a precise blocker report instead of pretending the research is complete.

The user wants breadth and depth, including methods, applications, implementation experience, criticism and failure cases. **Discover external sources yourself.** This brief deliberately does **not** prescribe a list of external papers, project repositories or URLs. The researcher, not the task author, must identify, verify, compare, and cite the actual primary sources, expanding beyond obvious starting points.

Only the project repository and internal mandatory governance entry points are identified here for navigation. Do not confuse these with a predetermined research bibliography.

## 1. Purpose, scope, and non-goals

### Purpose

Produce a substantial, independently inspectable **Phase A research evidence foundation** to inform the future Phase B (mathematical/model evaluation), Phase C (cross-method synthesis, overlap and architecture review), and Phase D (integrated implementation, testing, independent acceptance and releases).

Phase A must first discover **what questions should be asked**, not only answer the current list. ProbSpan's outstanding "technical debt" includes scientific uncertainty, statistical applicability, predictive validation, mathematical impossibility, prospective capabilities and only some ordinary engineering issues. Treat these distinctions explicitly.

Investigate many possible approaches without prematurely deciding the preferred model. The outcome is source-backed research material, unresolved questions, reproducible evidence, and a usable map for later decision-making.

### In scope

- Current ProbSpan mathematical/numerical/API behavior and research history.
- All 48 permanent candidates A01–E48 and four resolved repair records R01–R04.
- Scholarly research, technical reports, official scientific guidance, standards, numerical references, statistical software implementations, operational case studies and practitioner discussions.
- Foundational and modern methods, alternative paradigms, invalid assumptions, counterexamples and irreducible limits.
- Evidence-quality appraisal, provenance, bibliographic verification, comparison **of claims and assumptions**, gap discovery, source-indexing, and fact checking.
- Bounded computational reproduction of key externally published examples **only if practical**, isolated from production software; never invent validation.
- Chinese-readable substantive research reports, with exact original-language technical names and full source metadata.

### Strictly out of scope

- No changes to C production code, CMake, installed API/ABI, test fixtures, numeric oracle, existing model contracts, CI or workflow policies.
- Do not implement new probability models, alter prior/gate/EV semantics, add dependencies to the library, or change stable/release tags.
- Do not write Phase B's final model verdict, Phase C's architecture, or Phase D's implementation plan by pretending conclusions have already been approved.
- Do not create permanent new technical-debt IDs, rewrite prior research as if historical statements never existed, or change existing item states/priorities.
- Do not automatically treat another project's algorithm or implementation as suitable for ProbSpan.
- Do not copy code or large copyrighted passages from publications or repositories.
- Do not make medical, financial, safety-critical or gambling recommendations; these domains are methodological case studies only.

## 2. Governance, baseline, and source-of-truth audit

1. Verify the current remote main, this task branch HEAD, exact Git state, visibility, and v1.1.0 release. If main has changed, inspect the difference; never reset or overwrite another person's work.
2. Through authenticated access, read the **complete current** private \`RXY712200/Development-Playbook/WORKFLOW.md\` and \`RELEASE_POLICY.md\`. Follow their authority and Git-action boundaries. Never copy private policy contents into the public ProbSpan repository.
3. Read ProbSpan's full \`AGENTS.md\`, \`CONTRIBUTING.md\`, \`README.md\`, \`docs/ORIGIN_AND_SCOPE.md\`, \`docs/ARCHITECTURE.md\`, \`docs/API.md\`, \`docs/BEHAVIOR_SPEC.md\`, \`docs/NUMERICAL_CONTRACT.md\`, \`docs/COMPATIBILITY.md\`, \`docs/PROVENANCE.md\`, \`docs/TESTING.md\` and relevant \`src/\`, \`include/\`, \`tests/\`, \`oracle/\` files.
4. Read the four Chinese source guides \`docs/IMPLEMENTATION_WALKTHROUGH.zh-CN.md\`, \`IMPLEMENTATION_API_REFERENCE.zh-CN.md\`, \`IMPLEMENTATION_INTERNALS.zh-CN.md\`, and \`IMPLEMENTATION_VALIDATION.zh-CN.md\`.
5. Read the complete permanent ledger \`docs/TECHNICAL_DEBT.zh-CN.md\`, plus \`docs/HISTORICAL_EVIDENCE_RESEARCH.zh-CN.md\`, \`docs/PREVIEW_PROBABILITY_MODELS.zh-CN.md\`, \`docs/PREVIEW_DEVICE_HISTORY.zh-CN.md\`, and \`research/\` artifacts.
6. Inspect the relevant GitHub issue histories, especially issues #1, #5, #6, #8, #9 and #10. Issue #1 currently records a **narrow deterministic probability -> uncertainty -> decision core**, with no generic statistics catalog, UI/database application framework, or automatic fusion as part of current v1 promises.
7. Establish a table: exact implemented behavior; source/commit evidence; tests; public guarantees; caller-side assumptions; external-only research; unresolved mathematical questions; known fundamental limitations.

The user's request to research widely does **not** by itself amend the current product identity. Nevertheless, research beyond that identity is encouraged: classify it as possible caller-side, separate-product, future-scope or unsuitable evidence, without prejudging decisions.

## 3. One Phase A unit with eight fixed activities

Carry out all eight activities as a **single coherent research assignment**, not eight release cycles. This list defines required work, not predetermined scientific conclusions.

### A1 — Audit existing knowledge and extract the exact research problem inventory

For **each** ledger candidate A01–E48, record:
- exact existing statement and stable ID;
- classification: confirmed engineering bug, implemented-with-limits, research question, proposal, deferred capability or fundamental limit;
- what ProbSpan presently computes and explicitly does not compute;
- mathematical estimand and assumptions, if known;
- whether the problem is one of computation, identifiability, evidence admission, transport, measurement, validation or decision semantics;
- evidence and uncertainty already present in this repository;
- what would be new knowledge worth searching for.

Separately account for R01–R04 as *historical resolved repairs*, not pending features. Preserve the 52-ID ledger unchanged.

Identify relationships among the topics as **research questions** rather than final architectural dependencies.

### A2 — Broad academic discovery: theory, alternatives, criticism and mathematics

Investigate at minimum:

**Foundations**
- Frequentist and Bayesian probability semantics; objective frequencies and subjective judgment; conditional versus unconditional targets; reference classes; prior, likelihood, posterior and posterior predictive; aleatoric vs epistemic uncertainty; identifiability, partial identification and non-identification; confidence, credible and prediction intervals; decision uncertainty.
- Elicitation of expert beliefs, coherence, calibration and scoring of human forecasts; weak/absent evidence, sensitivity to assumptions and abstention.

**Binary and rare events**
- Bernoulli/binomial likelihood, Beta-Binomial conjugacy, Jeffreys and alternative priors, Wilson/exact and other intervals, coverage/small-sample behavior, sparse and zero events, posterior predictive probabilities, statistical readiness versus source validity.
- Accuracy of approximations, tail evaluation and extremely large parameters.

**Historical borrowing and generalization**
- No/complete/partial pooling, empirical and hierarchical Bayes, robust meta-analytic predictive priors, power/commensurate/discounted priors, dynamic borrowing, model/prior conflict, prior sensitivity, negative transfer and reference-population choice.
- Source/target exchangeability, transportability, covariate/label/concept shift, conditioning, selection bias, confounding, positivity, standardization, importance weighting, Simpson reversals and evaluation under drift.

**Evidence validity and dependence**
- Different event definitions, observation units, windows/horizons, target populations and measurement regimes; duplicate records, overlapping queries, clustering, longitudinal/repeated observations, shared latent causes, unobserved dependence, effective sample size, missingness/censoring, survivorship, reporting delay, right-censoring, selection on outcome, measurement error, dataset leakage and provenance.
- Why "more observations" does not automatically repair systematic bias.

**Broader predictive model classes**
- Feature-conditioned predictions, GLMs/logistic regression, hierarchical and nonparametric models, count/overdispersion models, survival/hazard/time-to-event and competing risks, nonstationary and seasonal time series, continuous and threshold predictions, rare-event processes, correlation and joint/conditional events, sequential updating and online forecasting.
- Ensemble/model averaging, correlated experts and double-counted evidence as research, without presuming ProbSpan should perform probability fusion.

**Forecast assessment and decisions**
- Strictly proper scoring rules, Brier and logarithmic scores, decomposition, calibration/reliability, resolution/discrimination, sharpness, CRPS/weighted interval scores, prediction interval coverage, conformal prediction, uncertainty quantification, cross-validation, rolling-origin/time-based validation, out-of-population testing, forecast skill baselines, confidence in evaluation itself, verification bias, decision utility, robust threshold decisions and value of information.
- Explicit distinction: scoring performance is not proof of causal truth, subgroup calibration or field applicability.

**Computational foundations**
- Beta/Gamma special functions, incomplete beta, CDF and quantiles, inverse methods, extreme tails, floating-point environments, rounding/precision, overflow/underflow, cancellation, reproducibility, numeric status/failure handling, independent high-precision references, discrepancies between mathematical formulas and software implementations, exact-decimal parsing and deterministic contracts.

**Epistemic and fundamental limits**
- Cases where the target cannot be estimated from available observations, no distribution-free solution exists without assumptions, historical data cannot legitimately be borrowed, or a rigorous "no justified estimate" result is preferable to confident output.

Seek foundational scholarship, modern studies, critical reviews, negative findings, counterexamples and significant disagreements. Broaden beyond this taxonomy when discovered evidence warrants it.

### A3 — Cross-disciplinary practical applications

Study how **real systems** define probability targets, collect data, estimate, validate and communicate uncertainty in at least ten materially distinct application families:

- operational weather forecasting and ensemble verification;
- climate, hydrology and environmental extremes;
- industrial quality control and manufacturing yield;
- hardware/device reliability, survival to a fixed horizon, component/process revisions;
- software/service reliability, outages, correlated incident observations;
- epidemic surveillance, public-health forecasting and reporting delays;
- medical prognosis, external validation, risk of bias and applicability;
- energy/load/demand and operational probabilistic forecasting;
- actuarial/insurance risk, frequency/severity and tail probabilities;
- finance/economic risk forecasting, with clear separation of prices, beliefs and outcomes;
- forecasting tournaments, crowd judgment and prediction histories;
- sports/event markets as examples of odds, margins, model selection and leakage;
- logistics, cybersecurity and scientific experimental design where material.

For each substantive case, record: actor, target estimand/event, population, unit, time horizon, data regime, mathematical method, validation metrics, baselines, real failure modes, known limits and original source.

Investigate **published empirical validation**, not just "industry X uses method Y". Compare operational claims against independent audits when available.

### A4 — Real software and numerical implementations

Find relevant open-source numerical/statistical packages and scientific/operational forecasting systems **independently**, not from a fixed list supplied by the task.

For each selected software example, inspect when available:
- exact project identity, version and immutable source commit;
- model semantics and scientific references;
- relevant code, interfaces and boundaries;
- numerical methods, errors and validity checks;
- unit/regression/reference tests and actual supported guarantees;
- issue trackers, known bugs, maintainers' caveats and release history;
- dependencies, licensing and reproducibility;
- risk in transplanting ideas into a deterministic C library.

Do not equate an existing implementation with proof that its statistical assumptions hold. Favor real source inspection over a marketing README. Do not import code into ProbSpan.

### A5 — Practitioner experience, adversarial examples and failure investigations

Search substantial field reports, technical incident write-ups, reproducible GitHub issues/discussions, researcher notes and meaningful forums (including statistical Q&A, Reddit where appropriate, and Chinese communities when useful).

Find examples of:
- correct formula applied to non-comparable data;
- incorrect denominators, observation horizons or target definitions;
- duplicated or dependent events creating false precision;
- Simpson's paradox and target-mixture change;
- distribution shift, leakage and selection bias;
- false confidence from tiny samples or rare events;
- well-calibrated average forecasts failing a key subgroup;
- retrospective testing incorrectly treated as prospective validation;
- scientific software's extreme-input or platform-specific numerical failure;
- statistical assumptions rejected by external validation;
- complex methods losing to simpler baselines;
- forecast aggregation double-counting common information;
- scientifically defensible refusal to estimate.

Record original URL, date, author's claim, other participants' counterarguments, independent corroboration and reproduction limits. Forum reports are leads and context, **not equivalent to peer-reviewed mathematical evidence**.

### A6 — Active source discovery, citation chasing and gap-driven search

Discover sources yourself. Do not stop at suggested names or popular blog posts.

Perform four documented research passes:

1. **Broad scan:** databases and search services for major theory, operational cases and software families; varied Chinese/English terminology.
2. **Citation chaining:** follow foundational works backward and follow-up research forward; find corrections, replications, controversies and independent implementations.
3. **Gap-driven scan:** focus where ledger topics have weak evidence, incorrect assumptions, missing real-world checks, divergent theory or unaddressed questions.
4. **Adversarial verification:** deliberately search for counterexamples and failures of the most promising methods; cross-check influential claims against a second independent source where possible.

Useful *discovery channels*, not a compulsory bibliography, include scholarly metadata databases, journal/publisher archives, institutional repositories, scientific societies, operational forecasting centers, standards agencies, open-source hosting, specialist Q&A forums and relevant academic conference proceedings.

When external web browsing is available, use it actively. If a specific website blocks access, record its inaccessible status, bibliographic metadata from alternative legitimate services and which claims could not be verified. Do not guess at a paywalled result.

For every meaningful search branch log actual query concepts, source/channel, date, discovered candidates, screened items, exclusions and reason for follow-up. Do not fabricate counts or claim exhaustive literature coverage.

### A7 — Build an evidence-linked ledger crosswalk and novel question registry

Map **all 48** A–E candidates, plus the distinct four repair-history IDs, to the verified bibliography and practical evidence.

The crosswalk should reveal:
- which claims/assumptions have strong evidence;
- which have only single-source or indirect support;
- which are inconsistent or disputed;
- which are mathematical impossibilities or identifiable only under explicit assumptions;
- which apply to software implementation vs caller evidence vs external domain validation;
- which ledger items overlap, depend on other *questions*, or concern different estimands;
- which apparently attractive methods might be invalid on the stated data.

Proactively search for **questions not listed** in the 48 candidates. Use provisional IDs such as \`NEW-A-001\`, never permanent ledger IDs. Explain why each is genuinely new rather than a renamed existing topic.

Do not close or promote ledger items; do not decide final method or feature scope.

### A8 — Verify the body of research and prepare the Phase A handoff

Carry out independent-style verification against the saved sources. Audit source titles/DOIs/years/versions and that cited passages actually support the attached claims. Revisit contested conclusions and negative evidence. Distinguish observed tests from hypothetical examples.

Check that:
- no invented source, inaccessible paper read-claim, or fake quoted result exists;
- primary literature and official documentation are preferred where an assertion depends on them;
- source links are complete and usable, and critical sources have DOI, archive or immutable versions where possible;
- critical methods state assumptions, target population, estimand, horizon and known failure cases;
- no real-world validation is inferred from synthetic tests;
- no mathematical correctness is inferred just from a green CI;
- no general result is inferred from a case study without justification;
- current ProbSpan behavior is not overwritten by proposed behavior;
- all existing 52 IDs are accounted for and the four historical repairs remain historical;
- new questions, contradictory evidence and missing results are clearly visible;
- findings and limits can be checked by a stranger opening the repository.

Do not select a final mathematical model or produce a Phase B/C/D approval document.

## 4. Research expectations and stopping criterion

A comprehensive survey must be **broad and substantive**. As an audit target, try to gather meaningful material spanning:
- about 30 or more distinct primary/foundational scholarly works;
- about 12 or more official scientific, standards or statistical guidance sources;
- about 10 or more genuinely relevant software/algorithm implementations;
- at least 10 substantive real-world operational or empirical cases;
- about 8 or more informative practitioner/community reports.

These are **coverage targets, not quotas or proxies for truth**. Do not pad the bibliography with duplicates, irrelevant sources or shallow snippets to hit a count. Report shortfalls and their causes.

Stop this Phase A unit when the eight activities and required research artifacts are genuinely complete, the 48-item matrix is covered, important assertions are sourced, and the residual gaps are clearly visible. A mathematically unresolved question is an acceptable research finding.

Use source-coverage and diminishing marginal discovery as part of the stopping justification, not an arbitrary time or search count. Do not leave the project in an infinite exploratory loop.

## 5. Exact source provenance requirements

**Every external source included as evidence must have a discoverable, checked URL found by you.**

Make a stable source index; assign identifiers \`S0001\`, \`S0002\`, etc. The same source gets the same ID everywhere. Avoid duplicate entries for alternate links to the same work; keep alternate URLs in the source record.

For each record preserve, as available:

- stable source ID;
- source type: peer-reviewed article / preprint / scholarly book / technical report / official guidance / open-source implementation / case study / practitioner discussion / other;
- title, complete authors or organization, publication year/date, version and last accessed date;
- original exact URL;
- DOI and official landing-page URL, when applicable;
- open full-text URL if legally available;
- immutable code-commit permalink when a repository implementation is described;
- peer-review/retraction/correction status where pertinent;
- whether the full text, abstract only, documentation only or code was actually inspected;
- concrete research questions and ledger IDs supported;
- what statement is supported, which claim is **not** supported, and critical limitations;
- independent verification or contradictory source IDs;
- notes on licensing if source/code reuse is discussed.

Use markdown source links in prose plus stable source IDs. Preserve direct URLs in the index so links can be exported, reviewed or recovered. For an empirical statement, cite the *actual evidence*, not a general homepage. For formula claims, cite the paper or appropriate original documentation. Never give a fake DOI, fabricated exact quotation, unvisited "verified" link, or invented GitHub commit SHA.

Make explicit confidence and evidence-level distinctions: theorem / derivation / empirical field study / simulation / implementation test / software docs / anecdote / unverified claim.

If two sources genuinely disagree, record both along with the differing data, assumptions, estimands, or validity arguments; do not silently pick a side.

## 6. Research deliverables — commit these as new public Markdown/TSV artifacts

Create the following under \`docs/research/phase-a/\` (new directory). Organize larger materials into sections or additional files only when necessary for clarity; retain these canonical entry points.

1. **\`README.zh-CN.md\` — Research overview and navigation.**
   Scope, precise source baseline, start/end access window, methodology, evidence status, research taxonomy, major *observations*, limits and navigation. No final model choice.
2. **\`source-register.tsv\` — Full bibliography and provenance register.**
   UTF-8 TSV with a documented schema. Stable IDs, bibliographic fields, exact URLs, verified availability, evidence types, ledger mappings, contradictions and reproducibility markers. Quote/escape tabs/newlines correctly and validate parsing.
3. **\`search-log.md\` — Search and screening trail.**
   Query families and languages, discovery services, citation chasing, exclusions, source checking, rejected/duplicate or inaccessible leads, diminishing-returns argument and known coverage gaps. Record actual operations, not imagined work.
4. **\`methods-and-assumptions.zh-CN.md\` — Technical research encyclopedia.**
   Topic-grouped mathematical questions, candidate approaches, formal assumptions, estimands, what may fail, theoretical limits, source IDs, formulas where needed, and open issues. Explain conflicting definitions and avoid false equivalence.
5. **\`real-world-and-software.zh-CN.md\` — Applied cases and implementation research.**
   Substantive industry cases, real data/validation practice, exact project source references, test and error-handling evidence, known incidents/limitations, license notes and source IDs. Separate field results, lab simulations and forum reports.
6. **\`ledger-crosswalk.zh-CN.md\` — Complete 52-ID crosswalk.**
   One unambiguous entry for every A01–E48 and R01–R04, linking source IDs, current implemented/partial/research status without altering it, newly found evidence, assumptions, disputes and missing evidence.
7. **\`new-questions-and-gaps.zh-CN.md\` — Provisional discoveries and research uncertainty.**
   New provisional IDs, deduplication against the existing ledger, strongest counterexamples, rejected hypotheses, unresolved research, unavailable sources, potential high-risk misinterpretations and questions for later B/C phases **without designing those phases**.
8. **\`verification-and-handoff.zh-CN.md\` — Research integrity review.**
   Exact repository baseline, document inventory, source-counts by quality, claim/source spot checks, crosswalk completeness, broken-link audit results, code/contract non-modification check, detected contradictions, reproducibility and limitations.

These are *research artifacts*, not a stable public API or a new release. Distinguish a preliminary research finding from an accepted tested implementation. Avoid publishing private governance text.

Documents should be primarily Chinese for future owner review. Mathematical terms, paper titles, technical identifiers, commands and original citation metadata should remain precise.

## 7. Git operations, permissions and execution constraints

This task's file was committed on the dedicated branch \`docs/phase-a-research-brief\`. Use that existing branch as the research work branch if it remains accessible and based on the expected source baseline. Verify the branch and clean checkout first.

This assignment authorizes:
- reading the public repository and authorized private governance;
- external scholarly/web/software research;
- writing **new research artifacts only** in \`docs/research/phase-a/\`, with minimal necessary index linkage if appropriate;
- ordinary local verification of created documentation, TSV data and citations;
- making clean research-only commits, pushing **the research branch only**, and opening **one reviewable PR** to \`main\` for independent assessment.

No authorization for:
- merging the PR;
- updating main directly;
- modifying released code, numerical oracles, behavior, tests or current ledger statuses;
- changing any private governance repository;
- publishing tags/releases or altering historical ones;
- force-push or history rewriting;
- adding unapproved runtime dependencies or new public interfaces;
- uploading user secrets or private account data.

Preserve unfamiliar local changes; do not use destructive cleanup. If the branch unexpectedly differs, inspect and explain the variance before writing.

A fresh cloud Codex session may find no local repository copy. Clone/check out the authorized remote and branch from scratch; obtain its own access to research sites. Do not ask the user to power on their personal computer or provide local paths.

## 8. Validation, acceptance criteria and stopping point

Before opening the PR, validate:

- All eight activities completed in substance.
- All eight canonical deliverables exist and link to one another.
- All A01–E48 candidates + R01–R04 have entries and correct stable IDs.
- All cited \`Snnnn\` identifiers exist in \`source-register.tsv\`.
- Every source has a URL/metadata status and the important links were actually checked.
- No dangling internal Markdown anchors or missing local research files.
- No fabricated research or unsupported generalization.
- At least ten actual applied domains were investigated (or deficiencies transparently documented).
- No duplicate bibliography entries falsely counted as unique sources.
- Paper/software versions and technical limitations are distinguishable.
- Explicit record of evidence gaps and unresolved scientific debates.
- The source, ledger, stable release, API, model and numerical contracts remain unchanged.
- \`git diff --check\` passes.
- Research files contain no private policy text or credentials.
- Local verification commands and results are recorded.
- Final PR scope is exclusively authorized research documents and minimal navigation.

Do not assume green C CI proves research correctness. Academic claims require source and method review. Do not invent a test run if the cloud environment does not support one.

After pushing and opening the PR, **stop**. The independent reviewer will check the actual GitHub source corpus, links, evidence traceability and product-boundary handling. Do not mark your own work as independently PASS.

## 9. Final Codex report (English)

Provide one concise but complete report:

1. Repository, branch, starting/final HEAD SHA, remote tracking and working-tree state.
2. What was read from the actual repository and governance, without exposing private text.
3. Eight-activity completion status and artifact paths.
4. Source counts by scholarly/official/software/field/community category; deduplication and quality breakdown.
5. Exact domain coverage, ledger coverage, provisional new-question count.
6. Most important evidence-backed findings and the most important conflicting/negative evidence, citing source IDs and repository paths.
7. Reference verification methodology and any inaccessible/non-verifiable sources.
8. Exact document integrity checks and commands actually run.
9. Remaining research uncertainties and reasons for any coverage target shortfall.
10. Proof that production source/contracts and the existing ledger were not modified.
11. Technical Debt Impact: **No change to ledger statuses or implementation**, unless reporting an observed discrepancy rather than modifying it.
12. Commit SHA, PR URL, explicit unmerged status, and what independent review should inspect.

This concludes **Phase A only**. No Phase B method selection, Phase C architecture decisions, or Phase D implementation/release is authorized.
