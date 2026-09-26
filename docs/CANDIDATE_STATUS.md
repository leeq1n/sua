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
| Planner contract repair | `c3d101770b0cc4ff60585b7120b01ffbc2b26609` on `codex/planner-contract-repair` | Keep persisted `RoundResult`, align `core.agent.run()` with `.steps`, and update the legacy harness | 49 focused planner/persistence tests passed; independent review remains open. |
| Pipeline filter retention | `d2e9da9` on `codex/pipeline-filter-retention` | Keep qualified papers available after the memory write; clear stale scores on a failed filter; isolate the offline end-to-end fixture | Five memory/filter tests and the no-qualified-papers route passed. Its full-flow end-to-end test still reaches the separate planner contract failure on this branch. |
| Planner + pipeline integration | `0a7112e0eb204facec2b0b971dc4e992167d521c` on `codex/pipeline-planner-integration` | Combined review surface for the two separate repairs above | 57 focused/offline tests passed, including all three end-to-end cases. A broader run stopped at five failures after 441 passed and nine skipped; see below. This is an integration candidate, not independently accepted capability. |

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
4. Review planner and filter repairs first as separate diagnoses, then use the
   integration branch for their end-to-end interaction. Preserve `RoundResult`
   persistence and qualified-paper routing. Compare the broad suite against
   current `main` and obtain a P30 independent decision on the exact clean
   integration artifact before any promotion.

The canonical planner mismatch has a separate repair candidate: legacy
`tests/auto/test_planner_harness.py` expects a `list`, while the current
`core.planner.plan_task` returns a persisted `RoundResult`. The filter defect
was independently reproduced: `node_filter` cleared `scored_papers` after
the memory write, ending a qualified run before patch generation. The
integration candidate demonstrates both paths together without changing
their separate provenance.

The broader integration run (`SUA_SKIP_NETWORK=1 uv run pytest tests/ -q
--maxfail=5 --tb=short`) reported 5 failed, 441 passed, 9 skipped. Two
failures also reproduce alone on `main`: a Windows subprocess UTF-8 decode
error in `test_constructive_control.py`, and a banned phrase in historical
`CHANGELOG.md` detected by `test_prompt_hygiene.py`. Three were not reproduced
in the targeted `main` run and need an order-dependent baseline comparison:
`test_pipeline_lg_safety_net_works` (planner byte restoration) and two
`test_planner_harness_persistence.py` cases. No claim of a green full suite or
behavioral improvement follows from the 57 focused passes.
