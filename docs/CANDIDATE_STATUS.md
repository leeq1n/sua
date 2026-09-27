# Candidate status and promotion boundary

> L0: `main` is the canonical implemented baseline; isolated branches are retained candidates, not current SUA capability.

Snapshot: 2026-09-27. The last promoted implementation baseline before this
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
| Goal Control daily integration | `6e53851ce1149610d80d029f498530e8ba350a4e` on `codex/goal-control-daily-flow` | Goal/Task contracts, guarded daily entrypoint, durable trace and feedback, signed task capsule with host-owned latest-state anchor and serialized writes; includes planner/filter repair | Clean offline suite: 1075 passed, 16 skipped. Independent P30 decision: ACCEPT for this exact structural candidate; Windows alias test skipped. Live drift/resume effect remains unmeasured, so this is not promoted capability. Earlier `codex/goal-control-operational` is retained as candidate history. |
| Mechanism-space evaluation baseline | `639367dfa6a2b9f2ceabcff6da3a204470139114` on `codex/mechanism-space-baseline` | Eight draft large-search-space scenarios and evaluation plan | Structural tests and validators passed; no model behavior, independent acceptance, or claim of innovation-search convergence. Separate from the Authority/Science paper experiment. |
| Planner contract repair | `c3d101770b0cc4ff60585b7120b01ffbc2b26609` on `codex/planner-contract-repair` | Keep persisted `RoundResult`, align `core.agent.run()` with `.steps`, and update the legacy harness | 49 focused planner/persistence tests passed; independent review remains open. |
| Pipeline filter retention | `d2e9da9` on `codex/pipeline-filter-retention` | Keep qualified papers available after the memory write; clear stale scores on a failed filter; isolate the offline end-to-end fixture | Five memory/filter tests and the no-qualified-papers route passed. Its full-flow end-to-end test still reaches the separate planner contract failure on this branch. |
| Planner + pipeline integration | `7f3fe1e7fd647f5159fe6323fc12dac70097d616` on `codex/pipeline-planner-integration` | Combined review surface for the two separate repairs above, with suite hygiene cherry-picked for order-independent offline verification | 57 focused tests and the repository's offline fast suite passed: 987 passed, 15 skipped, zero failures. Independent P30 decision for this exact head: MODIFY. Keep the runtime repairs as candidate material; do not promote this branch. |
| Suite hygiene | `3df9ffadbec1e12be294594ae684f8b9b0eba6df` on `codex/windows-suite-hygiene` | Windows subprocess decoding, planner test isolation, bounded memory-ceiling fixture, and context tests isolated from developer memory | Targeted failures and the v1.8.1 feature file pass. Full-suite evidence is on the integration branch, which also contains this branch's changes; independent review remains open. |

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

1. Goal Control daily integration has independent P30 structural acceptance
   for `6e53851`, including signed-state replay and concurrent-write review.
   Its 1075 offline passes support regression only. A valid held-out behavior
   comparison, and review of the exact proposed `main` promotion identity,
   remain required before promotion. Keep its structural acceptance separate
   from a claim that live agents drift less.
2. Keep the mechanism-space evaluation baseline separate from the paper's
   Authority/Science experiment. Freeze its discriminator and duplicate-search
   metrics before any held-out model run; its draft scenarios are not evidence
   that large-space innovation search converges.
3. Evaluate E2-M3 and E3-M4 in their own frozen task families. Missing
   credentials, quota-truncated replicates, or missing consumer evidence leave
   the candidate inconclusive; preserve the result rather than substituting
   scripted runs or an altered fixture.
4. Review E1.3-M1 and E4-A together for `src/retry_gate.py` compatibility, then
   measure and promote separately. Neither an old-base merge that removes
   E2-M2 coverage nor a silent combination of the two candidate state models
   is acceptable.
5. The independent P30 audit of integration head `7f3fe1e` found the planner
   and filter runtime repairs structurally valid, but returned MODIFY: some
   end-to-end tests mutate tracked files, and the offline fixture changes
   process environment without scoped restoration. Preserve `RoundResult`
   persistence and qualified-paper routing as candidate material. Hold the
   integration branch; any later revised promotion artifact needs a fresh
   exact-identity review.

The canonical planner mismatch has a separate repair candidate: legacy
`tests/auto/test_planner_harness.py` expects a `list`, while the current
`core.planner.plan_task` returns a persisted `RoundResult`. The filter defect
was independently reproduced: `node_filter` cleared `scored_papers` after
the memory write, ending a qualified run before patch generation. The
integration candidate demonstrates both paths together without changing
their separate provenance.

The final integration run used `SUA_SKIP_NETWORK=1`, `SUA_FAST=1`, and
`PYTHONIOENCODING=utf-8` with `uv run pytest tests/ -q --maxfail=5
--tb=short`: 987 passed, 15 skipped, zero failed in 99.17 seconds. Earlier
non-fast runs exposed five test-environment/order failures and a slow test
that inserts over 10,000 rows; the separate hygiene branch retains their
fixes. The non-fast suite was not completed. The fast-suite result is code
regression evidence, not live-agent drift reduction or P30 acceptance.
