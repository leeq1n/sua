# Candidate status and promotion boundary

> L0: `main` is the canonical implemented baseline; isolated branches are retained candidates, not current SUA capability.

Snapshot: 2026-09-26. The last promoted implementation baseline before this
status-only inventory is `a45de1b73ca4a959da0b7abf78e703f293a74427`
(E2-M2). This inventory is a routing aid, not an independent acceptance record. Before acting on it,
verify the live branch head and its current evidence. Preserve frozen packages
and untracked audit material without adding them to `main` by default.

| Candidate | Exact head at this snapshot | What to retain | Current boundary |
|---|---|---|---|
| E1.3-M1 parent lifecycle | `633de67386db5f585755c824626c50f529307a9a` on `codex/e1-3-m1-implement` | Generic controller change, tests, frozen identity, separate worktree | Implementation candidate; parent behavioral/independent acceptance outstanding. Direct merge from its older base would also remove the canonical E2-M2 regression test. |
| E2-M3 sandbox evidence | `2f8b995f6a491dc8ea0ca4ca3ab08b5ddd0d6b04` on `codex/e2-m3-preserve-sandbox-evidence` | Small diagnostic-preservation patch and regression | Local construction verified; autonomous-repair comparison remains inconclusive. |
| E3-M4 surface authority | `616320aec7137589da0e810b7f4c19b4de105a50` on `codex/e3-m4-isolated` | Domain-neutral authority map and frozen cases | Held-out causal measurement incomplete; the older mixed `codex/e3-m4-authority-separation` branch is historical, not a single-feature promotion unit. |
| E4-A grounded experience | `22d7d8424da7c50dfa8ca3256945513afc31f213` on `codex/e4-a-grounded-experience-anchor` | Frozen benchmark, provenance anchor, tests | Live provider measurement unavailable; candidate overlaps E1.3 in `src/retry_gate.py`. |
| Goal Control and Context Residency | `9aae306` on `codex/goal-control-isolated` | Stable Goal/Task contracts, hot-path reduction, drift/resume regressions | Rebased cleanly onto `main`; 43 focused tests and local structure/link checks passed. Live-agent behavioral effect and independent acceptance unmeasured. |
| Planner contract repair | `c3d101770b0cc4ff60585b7120b01ffbc2b26609` on `codex/planner-contract-repair` | Keep persisted `RoundResult`, align `core.agent.run()` with `.steps`, and update the legacy harness | 49 focused planner/persistence tests passed. The separate end-to-end filter failure occurs on both `main` and candidate; independent review and full-suite delta remain open. |

Keep these candidates and their evidence reachable, but do not count them as
implemented `main` features. A future promotion should take one bounded
candidate at a time from current `main`, preserve frozen evidence, compare
regressions against the same-environment baseline, and obtain the applicable
P30 fresh, artifact-first decision for the exact resulting clean identity.
Behavioral improvement claims require valid held-out behavior evidence; a
quota/credential failure or zero valid runs is measurement failure, not a
negative or positive result. Do not silently combine overlapping candidates
or use a broad merge to promote an unrelated ancestor.

The original mixed worktree also contains untracked `experiments/` packages,
E1.2 apparatus/protocol tests, and historical P30 audit reports. They are
evidence or operator material, not a sixth implementation candidate. Their
identity and intended authority must be checked before any packaging; this
inventory does not add, relocate, or delete them. Use a clean worktree for
canonical development and exact-artifact review.

## Promotion order and stop conditions

1. Review Goal Control first because it directly serves the newly stated
   project objective. Its 43 passing focused tests support a structural
   candidate only. Do not claim reduced live drift until a valid held-out
   behavior comparison and independent artifact-first review are complete.
2. Evaluate E2-M3 and E3-M4 in their own frozen task families. Missing
   credentials, quota-truncated replicates, or missing consumer evidence leave
   the candidate inconclusive; preserve the result rather than substituting
   scripted runs or an altered fixture.
3. Review E1.3-M1 and E4-A together for `src/retry_gate.py` compatibility, then
   measure and promote separately. Neither an old-base merge that removes
   E2-M2 coverage nor a silent combination of the two candidate state models
   is acceptable.
4. Review the planner contract repair as a separate maintenance lane. Preserve
   `RoundResult` persistence and direct agent execution; compare the full
   suite with `main` before promoting. Do not fold the separate filter-stage
   end-to-end failure into this repair.

The canonical full-suite planner mismatch has a separate repair candidate:
legacy `tests/auto/test_planner_harness.py` expects a `list`, while the current
`core.planner.plan_task` returns a persisted `RoundResult`. Until that
candidate is reviewed and promoted, compare each candidate's
regression delta against the same-environment `main` result and report the
full-suite state honestly. The end-to-end filter failure and any later test
failures remain separate baseline investigations.
