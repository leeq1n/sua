---
description: "Project goal, status, constraints, next step"
status: "summary"
---
# PROJECT_STATE — brief
> L0: Current project state (1-paragraph).  Load when: need snapshot of current goal/version/next step.

## Goal

**SUA is an agent-discipline knowledge library.**  It packages agent
behavior rules (P-n working principles + M-n operating rules),
reasoning primitives, and operating conventions that any agent
runtime can carry into a project.  The repo is self-contained and
does not depend on sibling repositories.

The current top-level project goal is **SUA self-application for constructive
control, with Phase A AI4S as the first adapter evidence source**:
improve scientific-research behavior by routing existing SUA primitives
through the project-layer scientific-state controller in
`AI4S_RESEARCH_MODE.md`. Satellite-security episodes are regression fixtures,
not active research directions. The earlier Phase A did not authorize
core-layer changes; the later general constructive-control repair was a
separate, explicitly authorized governance decision based on repeated
cross-session field evidence.

Within K3, the project-layer Pre-Agent Evidence Gate now requires bounded
cheap reconnaissance, author-claim skepticism, mutation reset, and a precise
residual ambiguity before an expensive Research Agent call. This is
structurally validated; live Agent-allocation behavior remains unmeasured.

At K0-K2, the same adapter now separates constructive problem discovery from
prior-art reduction: project constraints, bounded future-system hypotheses,
broken assumptions, and mechanism-driven donor transfer can trigger a
constructive Add reset without weakening K3/K4. This routing is structurally
validated; its effect on fresh-agent direction quality remains unmeasured.

Generic SUA now distinguishes artifact/evidence Add from constructive
search-space Add, routes well-specified execution directly, batches bounded
constructive expansion before terminal critique in open-ended work, and
requires controller-level replanning when locally valid terminal decisions
produce no global output-space expansion. M-n 29's helper reports structural
coverage only; semantic acceptance still requires evidence. The rejection-aware
retry gate now invalidates local self-PASS after explicit user rejection of the
same core criterion, requires a failure-state record and causal delta before a
retry, and exposes the same loop breaker through the stateless bridge. R3 also
closes the default controller/harness bypass: `max_retries` is only a quantity
ceiling, and missing retry context returns `RETRY_CONTEXT_REQUIRED` before a
second attempt. The canonical `src/retry_gate.py` state carrier now separates
canonical representation family from optional variant metadata, and the
`src/v4_loop.Loop` wiring has executable unit/integration coverage; live LLM
quality remains unmeasured.

At final promotion, the project-layer `ARTIFACT_FINALIZATION.md` adapter now
orchestrates existing SUA primitives around evidence-safe freeze
classification, surrogate-objective recovery, removal-first patch reduction,
stable killed-defect regression, and one blind-first fresh audit. Structural
and discoverability coverage passes; live behavioral improvement remains
unmeasured. P30 now separates implementation and regression evidence from
independent terminal acceptance. P30-A3 removes repository self-attestation:
local tooling computes the exact clean artifact identity and regression state,
but only verifies an already-existing external independent-audit record outside
the candidate repository. The verifier cannot manufacture or prove
independence; the amended state still requires a fresh independent SUA audit.
P30-A4 adds the single explicit post-acceptance liveness edge: after that
external record is verified against the unchanged clean commit, a finalizer
atomically records one external `ACCEPTED_FROZEN` ledger for the exact
identity. It does not modify the audited tree, create the external decision,
or reopen legacy candidate-to-core promotion.

The Phase A addendum separately tests whether SUA can detect recurring domain-
methodology inadequacy before a user requests specialization. The Layer 1
detector is `DOMAIN_SPECIALIZATION_BOOTSTRAP.md`; AI4S remains a Layer 2 adapter
and cannot by itself validate the generic detector.

## What the repo holds

| Area | Location | Purpose |
|---|---|---|
| Operating contract | `core-layer/AGENTS_CORE.md` + `AGENTS.md` | always-loaded rules + per-task 段s (P11 split) |
| Knowledge library | `docs/` | principles, operating rules, design, conventions |
| AI4S research adapter | `docs/AI4S_RESEARCH_MODE.md` | scientific-state routing and evidence gates for new-knowledge tasks |
| Specialization detector | `docs/DOMAIN_SPECIALIZATION_BOOTSTRAP.md` | audit recurring methodological friction before adapter proposals |
| Artifact finalization adapter | `docs/ARTIFACT_FINALIZATION.md` | evidence-safe final-promotion orchestration for externally consumed artifacts |
| Governance | `core-layer/` | 3-layer policy (核心/用户/项目) + modification gates |
| Commit gates | `hooks/` + `agent-tools/scripts/` | commit-msg / pre-commit / pre-push / prepare-commit-msg |
| Legacy runtime | `core/` + `src/` + `self_upgrade/` | v1.x-v3.x self-improving agent (documented legacy, functional) |

## Current version

Latest CHANGELOG entry: **v2.22.x** (see `CHANGELOG.md`).  Release
history is documented there; `README_DETAIL.md` covers the legacy
code (v1.x-v3.x), which is kept because tests and CLI scripts
exercise `src/` (removing it would break CI).

## Tests

`pytest tests/` collects ~875 tests.  Environment-dependent failures:
- LLM / network tests skip when no API key or `SUA_SKIP_NETWORK=1`.
- `core/planner.py` is LLM/user-modified (a known open decision —
  keep or revert, see `test_core_planner_md5_matches_head` which is
  deselected).  Harness tests that depend on planner.py's pre-modification
  shape fail until that decision is made.

## Constraints

See `docs/CONSTRAINTS.md` for the full list (奥卡姆, fail-OPEN,
atomic, user-edits-keys-never-agent, etc.).  Project constraints
change rarely; that file is the source of truth.

## Next step

Phase A decisions are AI4S `AI4S_PROJECT_ADAPTER_VALIDATED` and generic `PROPOSAL_ONLY_NEEDS_MORE_EVIDENCE`.
Next, run the fixed AI4S (including discovery and Pre-Agent), generic
constructive-control, and specialization suites with a valid provider and
blinded scoring. Measure direction diversity, unnecessary Agent calls,
constructive checkbox failures, premature terminal critique, and decision
quality. Do not start Phase B or claim behavioral improvement from structural
tests. The prior `docs/PLANS/PLAN_2026-07-30.md` remains historical context.

## References

- INDEX: [INDEX.md](INDEX.md)
- Working principles: [PRINCIPLES.md](PRINCIPLES.md)
- Operating rules: [OPERATING_RULES.md](OPERATING_RULES.md)
- AI4S Research Mode: [AI4S_RESEARCH_MODE.md](AI4S_RESEARCH_MODE.md)
- AI4S Phase A validation: [AI4S_PHASE_A_VALIDATION.md](AI4S_PHASE_A_VALIDATION.md)
- Domain specialization bootstrap: [DOMAIN_SPECIALIZATION_BOOTSTRAP.md](DOMAIN_SPECIALIZATION_BOOTSTRAP.md)
- Artifact finalization: [ARTIFACT_FINALIZATION.md](ARTIFACT_FINALIZATION.md)
- Artifact-governance validation: [ARTIFACT_GOVERNANCE_VALIDATION.md](ARTIFACT_GOVERNANCE_VALIDATION.md)
- User intent: [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Hard rules: [CONSTRAINTS.md](CONSTRAINTS.md)
- Pending tasks: [../TODO.md](../TODO.md)
- Done tasks: [../DONE.md](../DONE.md)

Last P20-verified: 2026-09-11
