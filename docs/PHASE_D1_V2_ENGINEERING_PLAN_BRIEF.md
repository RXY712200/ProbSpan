# ProbSpan v2.0.0 — Phase D1: Feature Scope, Engineering Blueprint, Fixed Work Breakdown

**Authorization status:** D1 product/engineering **PLANNING ONLY**. New features, source edits, Preview/RC/Stable releases, and Phase D2 are **not yet authorized** by this task.
**Repository:** `RXY712200/ProbSpan` (public).
**Dedicated GitHub branch:** `docs/v2.0.0-d1-engineering-plan`.
**Verified accepted starting `main`:** `a838344bd93b81ca26713d48ae8b6b1bf6969a62` (Phase D local-handoff PR #20 merged).
**Known Stable:** `v1.1.0` annotated release, implementation commit `46ff21847c5522eb983d3f58e396354461a64f34`.
**Execution environment:** The owner wishes to resume development with **local Codex on Windows**. This task works from a fresh checkout and a fresh conversation; GitHub is the durable record.

## 0. Explicit product decision: v2.0.0 MUST plan real new capabilities

The project owner has made a new, explicit product decision: **ProbSpan 2.0.0 must substantively add useful statistical/probability models and analytical capabilities informed by Phases A, B and C.**

Do **not** respond by merely cleaning up v1.1.0, re-running tests, drafting a device-history wrapper, or indefinitely deferring every investigated mathematical family. That would not fulfill the owner's objective.

Equally, do **not** automatically convert 48 permanent research problems, 8 provisional research questions or 26 overlap findings into 48/8/26 shipping functions. Some findings concern mathematical impossibility, provenance, validity, negative results, or design risk rather than runtime features. Phase B did not establish field validity or a universal winner across models.

Your D1 job is to **translate accepted research into a concrete, technically defensible, ambitious but bounded v2 feature and engineering plan**. Recommend an actual coherent feature set that would make a substantial upgrade; specify exact input/output semantics, module boundaries, dependencies and independent acceptance tests; and candidly identify invalid conflations, research gaps and alternatives. A user-approved future D2 task will implement one bounded unit at a time.

### How the new owner decision relates to Phase C

Phase C's "keep the current C core by default; consider an external adapter with real evidence" was a **conditional recommendation given then-unknown product demand**, not a permanent veto over a newly authorized v2 planning objective.

Now the owner has expressed explicit demand for expanded functionality. Re-evaluate all Phase C options and nine decisions **under that new objective**. Distinguish:

- v1's historically frozen semantics and installed-consumer compatibility — hard constraints unless the owner later expressly approves a well-supported break/migration;
- v1's former non-goals — accurate descriptions of v1, **not necessarily permanent prohibitions for an independently designed v2 module**;
- Phase C's conditional architecture recommendations and deferred tasks — evidence and concerns to address, not unconditional orders;
- missing real-device or industry samples — barriers to **field-validity claims**, not automatic barriers to developing rigorously specified pure mathematical functions with synthetic/independent reference validation;
- scientific nonidentifiability — actual limits that no coding effort can eliminate.

The preferred design may preserve the narrow v1 core **and** build genuinely new, independently typed v2 capabilities. If a user-relevant capability cannot be defensibly included in this release, document the precise blocker and a valid alternate path instead of vague "future research" or an arbitrary universal interface.

## 1. Start by independently verifying authority and the complete technical baseline

1. Identify the actual local checkout and Git remote. Inspect branch, `HEAD`, staged/unstaged/untracked work, worktrees and `origin/main`; fetch safely, preserving unfamiliar changes. Verify the accepted `main` baseline and merge commits of PRs #17, #18, #19 and #20. The given SHAs are **historical pins**, not a claim that main can never move. If actual HEAD or work is unexpected, investigate without resetting/overwriting.
2. Through authenticated authorized access, read **the entire current private** `RXY712200/Development-Playbook/WORKFLOW.md` and `RELEASE_POLICY.md`; do not reveal/copy private policy content into the public repository. Follow actual Git, scope, documentation, review and release permissions.
3. Read complete project `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `docs/PHASE_D_LOCAL_HANDOFF.zh-CN.md`, `docs/ORIGIN_AND_SCOPE.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/BEHAVIOR_SPEC.md`, `docs/NUMERICAL_CONTRACT.md`, `docs/COMPATIBILITY.md`, `docs/PROVENANCE.md`, `docs/TESTING.md`, `docs/TECHNICAL_DEBT.zh-CN.md`, and the four `docs/IMPLEMENTATION_*.zh-CN.md` guides.
4. Read **all actual Phase A, B, C canonical research documents and TSV registers**, not just summaries. Inspect all seven B experiment implementations/protocol/results and sources needed to substantiate proposed implementations. Read the C overlap and decision registers with exact IDs and conclusions, plus relevant issues, including #1, #5, #6, #8, #9 and #10.
5. Inspect the actual `include/` public header, `src/`, private numerical helpers, `tests/`, `oracle/`, `CMakeLists.txt` and packaging, `tests/consumer/`, `integrations/device_history/`, and relevant historical `research/` material. Cite specific functions/source boundaries rather than imagined components.
6. Verify current Stable tag, current project versions/ABI/model/gate/versioning, source-tree vs Stable differences, toolchains and current portability guarantees. Do not assume Windows tests succeeded merely because CI or Linux tests succeeded.

If an expected source is genuinely inaccessible, record the exact gap and its effect. Do not use old chat memory, user PC absolute paths, cloud-only logs, or unverified historical statements to paper it over.

## 2. Fixed D1 activities (six). D1 is one planning unit, not six separate releases

### D1.1 — Build a product/evidence-to-feature decision map

Make a complete **many-to-many** crosswalk of:

- all 48 permanent A01–E48 candidates with their current ledger states;
- NEW-A-001–007 and NEW-B-001 as **provisional**, not approved ledger additions;
- R01–R04 as resolved historical repairs, never reopened merely to inflate feature counts;
- relevant A sources, B derivations/experiments `B-E001`–`B-E007`, C overlap `C-O001`–`C-O026`, and decisions `C-D001`–`C-D009`;
- actual current v1/v1.1.0 capabilities, optional device reference and development/reference-only code.

For every **feature candidate**, distinguish:
- exact user operation and estimand (who/what, unit, target, horizon, conditioning);
- available inputs and responsibility for evidence admission;
- new mathematical computation versus new validation, diagnostics, provenance, formatting, or evaluation;
- technical feasibility with actual source code and C11 constraints;
- strength and independence of proof, synthetic experiment, observational holdout, field evidence and existing tests;
- prerequisites, negative/zero-data behavior, alternatives including *not shipping it in v2*;
- recommendation: `V2_CORE`, `V2_OPTIONAL`, `V2_SUPPORT`, `EXTERNAL_CALLER`, `REQUIRES_EVIDENCE`, `DEFERRED`, or `REJECTED`, with a written rationale. These are **new D1 planning labels only**; never mutate permanent ledger statuses.

All researched topics must be accounted for; no fabricated feature quotas. Make clear which concrete new operations make v2.0.0 substantially more capable than v1.1.0.

### D1.2 — Evaluate the feature families; select an ambitious, feasible scope

**Actively evaluate all following families.** They are a starting checklist, **not a mandated universal API**, and you may find a better decomposition.

**A. Advanced binary/rare-event inference.** Exact input definitions and guarantees for Wilson/score and Clopper–Pearson intervals, possible alternate Beta priors/sensitivity, one-sided/zero-event bounds, frequentist-versus-credible distinctions, fixed n, interval and uncertainty target, extreme numeric behavior. Preserve old Jeffreys result; select which additions merit public v2 functions.

**B. Multi-source/history borrowing and hierarchical risk.** Validated target-only vs complete pooling, fixed historical discount/power priors, robust mixtures, empirical Bayes and hierarchical models (including known-group versus genuinely new-group prediction). For each, specify exposure/selection assumptions, whether sources can share a parameter, how hyperparameter and borrowing uncertainty propagates, and the behavior for zero target, conflict and no compatible source. Review B-E002/B-E007 carefully. Do not relabel pooling or a simple weighted average as a fully validated hierarchical Bayesian model.

**C. Stratified/target-population inference.** Weighted standardization and partial pooling must remain distinct. Review current two-stratum Preview, fixed known weights vs estimated weights, weight–risk covariance, clustered observations, missing stratum/positivity, Simpson reversals, stable target population definition; see B-E003. Decide where standalone analysis belongs and which result is parameter versus prediction.

**D. Event time, count/rate and competing risks.** Fixed-horizon binary risks, Poisson/event rates, future counts, survival functions and cause-specific CIF require genuinely different observation structures. B-E004 is a counterexample to naive `1-KM`. Compare a **small, mathematically valid independent v2 module**, an optional adapter, and non-inclusion where the necessary time/risk-set inputs are absent. Do not create a generic "turn counts into survival" conversion.

**E. Forecast evaluation and calibration.** Proper scores (Brier/log loss), paired/stratified comparisons, reliability/calibration checks, time and truth vintage, missing/selectively labeled outcomes, rolling look-ahead, sequential peeking, abstention rates/cost and evaluation denominator. B-E005/B-E007 show nontrivial failures. Compare **pure evaluators of caller-supplied frozen prediction/truth records** with any storage solution; the small C kernel need not own a DB or clock merely because v2 offers evaluation.

**F. Conditional/feature-based, continuous, joint and multi-event problems.** Examine feature-conditioned forecasts, continuous threshold/tails, count or time-varying processes, single versus joint event probabilities, probability fusion/common-signal dependence, expert elicitation, cross-domain migration. Identify concrete plausible v2 scope **if** inputs and independently verifiable estimands exist, otherwise state exact nonidentifiability or unsupported field work. A dedicated module or separate artifact is preferable to falsely typing all cases as Bernoulli histories.

**G. Crosscutting numeric, evidence and decision support.** Confirm binary64, exact decimal semantics, Beta tail resolution and accepted tolerances; avoid strengthening B-E006 from tolerance-checked 15/15 to strict 15/15 (independent review: **10/15 strict; 15/15 with 1e-10 probability tolerance**). Separate numerical computability, estimate availability, sample readiness, source applicability, identification and decision utility. Consider useful explicit refusal/partial bounds and diagnostics; do not magically certify source truth or turn v1 provenance flags into an independent evidence oracle.

For each family, perform **a real prioritization**: expected user-facing capability, mathematically valid minimum deliverable, implementation/verification effort, dependencies, portability, opportunity cost, validation demands, and risk of misleading results. A research result being interesting alone is not a product case. A source or synthetic dataset not being "field validated" alone is not enough to discard a deterministic mathematical function. Decide, explain and show a minimal valid example and a destructive counterexample for major candidates.

The resulting recommended v2 must have **multiple substantive new analytical capabilities**, not just new wrappers. The recommendation may be challenged and revised by the independent reviewer/owner; D1 cannot approve itself.

### D1.3 — Design consistent but scientifically honest architecture and contracts

Investigate at least: incremental independent additions atop frozen v1, optional separate v2 model modules within the same repository, mixed C core + optional consumer-side tools, and a broader integrated v2 (as comparator). You may propose another superior architecture.

Build a **real dependency map and migration/compatibility analysis**:
- v1 public 13 functions, ABI, structs/layout, status/error precedence, solver/gate/subjective policy, exact odds parsing, EV and provenance history;
- possible new v2 public APIs and where public types must be *distinct* rather than fake generic doubles;
- package boundary, installed consumer compatibility, CMake target naming, C11 portability, optional third-party math dependencies and licensing;
- private shared Beta/math/EV primitives where contracts truly match, independent reference implementations and test harnesses, deliberate duplication where it avoids false coupling;
- stateful vs pure functions; external data clocks/stores vs values, exposure and evidence declarations;
- numerical and scientific failure vs legitimate `UNKNOWN`/unidentified/abstention; partial results, zero samples, incompatible horizons;
- version and migration policy: **do not rewrite v1 contracts**. Identify any proposed breaking change and alternatives; a `2.0.0` marketing/version goal is *not* automatic authorization for ABI breakage;
- no invented universal fit/predict model, automatic evidence-admission certificate, mandatory Python runtime for existing C clients, or implicit forecast-history DB unless separately justified.

Use **non-binding** C-like sketches or structured tables where they clarify meaning; do not add public headers/source code. For each major API suggestion give exact inputs/outputs/units/status, ownership, preconditions and a minimal valid and invalid caller scenario. Aim for extensibility with narrowly shared infrastructure, not complexity for its own sake.

### D1.4 — Fix the full D1–D5 execution roadmap and detailed work units

Treat these as the **five top-level Phase D stages**; D1 must produce a fully specified, bounded plan, with the **fixed number** of internal work units for every subsequent stage. Choose unit counts after evaluating real complexity; do not arbitrarily force all families into a fixed number or fragment them into dozens of artificial micro-tasks.

- **D1 — scope/architecture/engineering-plan review (this task):** six activities D1.1–D1.6, ending in independent review of the D1 planning PR.
- **D2 — implement validated foundational new-model capabilities:** actual feature-family commits for selected v2 base, old-v1 compatibility preserved; potential Preview milestones only after meaningful, tested increments.
- **D3 — implement and integrate remaining approved v2 analytical families:** avoid artificially tying separate statistical estimands; make optional components genuinely optional; end with coherent feature freeze readiness.
- **D4 — RC validation/stabilization:** no routine feature expansion. Reconcile source, actual API/docs, current-vs-preview documentation changes, independent math references, regression coverage, new consumer integration, relevant toolchains, distribution/licensing.
- **D5 — Stable candidate acceptance and controlled publication:** final evidence, precise SHA, version/ABI/migration/docs/install/release assets, no automatic tags/releases.

For each stage and **each numbered internal work unit** provide:
- actual deliverable and files/modules involved (proposed if not yet authorized);
- input/output and mathematical contract;
- dependencies and work that can proceed independently;
- minimum tests, counterexamples and independent numerical/field evidence where applicable;
- compatibility and documentation/ledger impacts;
- which Git actions and user decisions will require explicit later authorization;
- observable PASS, FAIL, and stop conditions;
- meaningful Preview or RC checkpoint if applicable.

All numerical counts of stages/units, scoped dependencies and planned stopping conditions must be explicit **in the D1 artifact**. Do not rely on "we will decide every step later" to avoid doing engineering design. Ordinary bug fixes and validation retries remain inside their original work unit. Material change to the plan needs a documented replanning proposal and owner approval, not an endlessly appended `D3.999`.

**The scope of v2.0.0 and D2–D5 roadmap is a proposal pending independent acceptance and owner authorization.** Do not claim the newly proposed schedule/work units are already authorized for implementation.

### D1.5 — Plan actual scientific, numerical, consumer, portability and release verification

For each intended implementation family, define test matrices that catch:
- false reference-class transfer, incompatible endpoints, hidden overlap/cluster dependence, targetless conflicts and missing strata;
- proper distinction between Beta posterior parameters, future-event predictions, future batch counts, credible/confidence intervals, weighted target estimates, cause-specific risk, calibration scores, EV/utility;
- numerical tail/quantile errors, binary64 representability/rounding, error budgets and failure atomicity;
- proper-score edge cases, truth-revision leakage, optional stopping, selective labels and incompatible evaluation denominators;
- ABI & source compatibility, installed old consumer against new package, compiler and libm variation on real CI platforms;
- packaging with optional dependencies absent, no implicit global state, resource usage and clean redistributable build.

Differentiate mathematical proof, synthetic Monte Carlo with uncertainty, published observational holdout, independent high-precision reference, internal CTest, exact-SHA CI and **real-world applicability**. Name exact fixture provenance/required new tests and what is still unvalidated. Reuse existing B scripts only as valid evidence for their original scope; do not treat them as automatic production test suites.

Create a milestone documentation strategy: initial D1 trusted design baseline, partial Preview snapshots accurately linked to their actual code, full source/document reconstruction at RC, and final Stable review. No mechanical full rewrite at every preview; no release from green checks alone. The detailed Chinese implementation guides and public API docs must remain synchronized with actual changes as they occur.

**Preview planning:** indicate candidate feature bundles and objective success gates, but **do not mandate a fixed count of actual Preview releases**. A name such as `v2.0.0-preview.1` is an illustrative candidate, not authorization to create a tag or prerelease. Follow the private release policy: meaningful tested work, independent technical acceptance and separately authorized published releases. RC count also follows substantive risk, not commit counts.

### D1.6 — Adversarial self-review, owner decision package, quality verification

Challenge your own scope:
- Which research output is not implementable from available inputs? Where must v2 refuse?
- Which proposed public functions accidentally use an incompatible notion of probability or interval?
- Is any method advertised with field validity or guaranteed accuracy unsupported by B's simulations?
- Are any two new modules incorrectly sharing results, priors, error codes, data schemas or calibration statements?
- Has an optional Python or machine-learning dependency leaked into the base C11 runtime?
- Does proposed time-series, survival, count, or joint model require a completely different data schema or module?
- Could adding a new model force maintenance of unrelated existing models or silently change v1 behavior?
- Is the plan trying to implement every open research problem for appearance's sake, while neglecting a coherent useful minimal subset?
- Conversely, has it used "not proven useful" to exclude all functionality that the owner expressly requested?
- What is the **concrete v2 feature delta** relative to Stable v1.1.0? What would make v2.0.0 worthy of its scope?
- Which owner choices are actually necessary before D2, and which technical design decisions should the engineer/independent reviewer make without serial unnecessary questioning?

Provide a concise, **decidable owner decision register**. Include your expert recommended default for each choice and meaningful alternatives; clearly mark `OWNER_REQUIRED`, `PROPOSED`, `DEFERRED`; none `OWNER_APPROVED` absent explicit recorded authorization. Owner's explicit preference for new v2 features **is already approved as product direction**, but **individual API breaks, exact model list, novel dependencies, distribution and releases are not**.

Be willing to recommend an ambitious but conditional plan with clear assumptions and risk paths instead of demanding real-world datasets for every pure algorithm before doing *any* planning.

## 3. All substantial work MUST be written into GitHub, not left in chat or local files

Create all canonical D1 artifacts in the **public GitHub repository**, under:

`docs/plans/v2.0.0/`

Required, substantive and navigable deliverables (Simplified Chinese preferred):

1. `README.zh-CN.md` — authoritative D1 plan entry, exact accepted baselines, v2 goal and actual scope/approval status.
2. `feature-scope-and-evidence.zh-CN.md` — recommended **new** features, alternatives/omissions and real v1→v2 capability delta; map all 48 permanent + 8 provisional + R repairs distinctly.
3. `estimands-models-and-contracts.zh-CN.md` — per-model explicit estimands, data requirements, output types, assumptions, errors, anti-conflation counterexamples and representative possible v2 signatures.
4. `architecture-and-compatibility.zh-CN.md` — meaningful architecture options, chosen proposal with reasons, module/dependency graph, shared-vs-separated math, old ABI and consumers, packaging/licensing and migration.
5. `stages-and-fixed-work-units.zh-CN.md` — five macro stages D1–D5; **explicit fixed internal work-unit counts and numbered work units**, dependencies, actions, deliverables and measurable independent acceptance.
6. `verification-and-test-matrix.zh-CN.md` — proof/experiment/independent oracle/CTest/consumer/CI/field validation separated, failure/abstention, numerics and platform acceptance tests by work unit.
7. `preview-rc-stable-strategy.zh-CN.md` — objective Preview/RC/Stable gates, documentation trust/rebuild and exact-SHA validation, **no compulsory release count, dates, tag or publishing action**.
8. `owner-decisions-risks-and-handoff.zh-CN.md` — reconciled C-D001–009 statuses under the new v2 product goal, owner choices and recommended defaults, risk classification, adversarial review and exact next authorization boundary.

Additionally include:
- `feature-register.tsv`: each proposed v2 feature ID (`V2-Fnnn`), related A/B/C identifiers, family, v1 gap, estimand, inputs, recommended placement, target stage/unit, status, dependencies, evidence and acceptance gate; include feature candidates not selected with justified status.
- `work-unit-register.tsv`: all D1–D5 units (D1.1–D1.6 plus bounded proposed D2–D5), dependency IDs, scope, deliverable, verification, owner/permission gate, and Preview/RC milestone eligibility.

You may add **other source-backed diagrams/tables/design files** under this directory if they substantially improve future development. Do not create a separate competing governance policy or huge duplicates of Phase A/B/C.

**GitHub persistence is mandatory.** Draft locally if necessary, but push the complete documentation to this branch and create one PR against main. All durable decisions, phase details, evidence links, risk and test matrices must exist in version-controlled GitHub files; **no essential plan may exist only in the Codex chat response, ephemeral terminal output, unpushed local notes, external drive or PDF**. Chat completion report is merely a concise pointer to committed facts.

## 4. Explicit action permissions and stop point

Authorized D1 actions:
- read local and remote ProbSpan, authenticated private policy, public source/literature if needed;
- inspect but do not change actual current implementation/tests/oracles;
- create/update the new **D1 planning files** under `docs/plans/v2.0.0/`;
- use the already-created branch `docs/v2.0.0-d1-engineering-plan`, which includes this pinned task brief, or safely create a separate worktree attached to that branch; preserve unknown existing local changes;
- run read-only build/test commands or isolated baseline builds if relevant, accurately noting environment and outcomes; no source modification;
- commit and push D1 documents to **this branch only**, then open **one** reviewable GitHub PR into `main`; stop for independent ChatGPT verification.

Not authorized:
- implement **any D2/D3 feature**, public header/source code, test/oracle/build changes, preview runtime, adapters or data-store;
- alter existing stable model, ABI, v1 consumer, release notes/tag/version macros, baseline numerical or behavioral contracts;
- alter/delete Phase A/B/C accepted evidence, permanent technical debt states, existing GitHub issues, policy repo or historical commits;
- directly push to main, merge PR, rewrite history, force-push, change other branches, or silently grant model/release approvals;
- publish `v2.0.0` Preview/RC/Stable, create tags/releases, or download/use unauthorized personal/industry data;
- replace this product plan with an unrelated re-research cycle or a superficial "maintain v1 only" document.

Because your D1 plan itself proposes major new product architecture and public surface, **its PR acceptance is a gate before implementation**. Keep all decisions and plans honestly marked `PROPOSED` where approval is pending. No automatic Phase D2 after opening PR.

If the local repository is behind/dirty, do not discard changes. Fetch, identify the existing remote D1 branch, use a separate worktree where suitable, and preserve the task-brief commit as an ancestor. If `origin/main` has advanced, evaluate the difference and report precise new baseline. No nested cloud tasks or dependency on any earlier conversation.

## 5. Acceptance checklist

A reviewer must be able to verify from the actual remote branch/PR:

- D1 contains a **substantive proposed v2 feature set**, with explicit new functionality and staged implementation, not just unchanged v1 and generic "research later".
- All families A–G were fairly assessed, with meaningful inclusions and technically explained exclusions/deferments, and a clear v1.1.0→v2.0.0 delta.
- All 48 permanent problems, eight provisional research questions, and four historical resolved repairs are traceable without promoting questions to permanent approved backlog.
- All nine C decision IDs are reconciled; the new owner-level v2 direction is reflected, but no unsupported feature/API approval is fabricated.
- Exact mathematical estimands, input observability, assumptions, missing/unknown behavior, confidence-vs-credible-vs-predictive differences and incompatible results are clear.
- Numeric B-E006 tolerance statement is accurate; Phase B observational/synthetic limits remain visible.
- V1 public API/ABI and installed consumer have a real compatibility strategy. Major-version naming does not silently permit breaking users.
- Selected architecture has real source-dependency support, no magic universal modeling API or false common probability/result object.
- D1–D5 are bounded and D2–D5 have fixed numbered work units. Dependencies and test gates are feasible and specific rather than generic checkboxes.
- Preview candidates correspond to meaningful implementation work, without compulsory Preview/RC count or unauthorized release.
- All eight documents and both TSV registers are consistent, machine-parseable where applicable, internally navigable and link to primary accepted evidence.
- Actual Markdown links, local anchors, TSV row/column/ID integrity, traceable feature/work-unit references and `git diff --check` pass.
- Only new D1 documentation changed; source, tests, oracles, policy, permanent ledger, accepted research and Stable artifacts remain untouched.
- Documentation is recoverable by a brand-new local Codex session solely from GitHub plus the authorized private policies.

**A polished but empty roadmap is FAIL.** So is indiscriminate feature sprawl that erases distinct statistical meanings or expects unobserved data to exist. Do not claim an engineering test, field pilot or CI run without actual evidence for the exact revision and environment.

## 6. Final report (English, factual)

After pushing to the review branch and opening the PR, report:

1. Actual baseline main, branch initial/final local/remote/PR HEAD and tree; local worktree state.
2. Private policy read success without disclosure, project files/sources/research actually read and old Stable verification.
3. D1 six activity outputs, all required artifacts and exact GitHub links.
4. Recommended v2 feature groups and planned new public/internal functionality; real exclusions, alternatives and major risks.
5. Fixed D1–D5 unit counts, dependency map, Preview/RC checkpoints and substantive acceptance gates.
6. Mapping counts for 48+8 and R01–R04, 26 C overlap rows, 9 C decisions, 7 B experiments.
7. Contract, numerical and old-consumer compatibility assumptions; unresolved decisions and owner gates.
8. Actual link/anchor/TSV/coverage/diff checks, any baseline builds and CI on exact SHA if actually available; environmental limitations.
9. Technical Debt Impact, explicit whether permanent ledger/state changed.
10. Committed file list, commit SHA, **open/unmerged PR link**, explicit statement that no D2 implementation or release started.

Stop at the open PR for independent ChatGPT review. This task does **not** grant automatic approval of the architecture or publication of v2.0.0.
