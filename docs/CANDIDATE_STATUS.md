# Candidate status and promotion boundary

> L0: `main` is the canonical implemented baseline; isolated branches are retained candidates, not current SUA capability.

Snapshot: 2026-09-26. The last promoted implementation baseline before this
status-only inventory is `a45de1b73ca4a959da0b7abf78e703f293a74427`
(E2-M2). This inventory is a routing aid, not an independent acceptance record. Before acting on it,
verify the live branch head and its current evidence. Preserve frozen packages
and untracked audit material without adding them to `main` by default.

| Candidate | Exact head at this snapshot | What to retain | Current boundary |
|---|---|---|---|
| E1.3-M1 parent lifecycle | `633de67386db5f585755c824626c50f529307a9a` | Generic controller change, tests, frozen identity, separate worktree | Implementation candidate; parent behavioral/independent acceptance outstanding. Direct merge from its older base would also remove the canonical E2-M2 regression test. |
| E2-M3 sandbox evidence | `2f8b995f6a491dc8ea0ca4ca3ab08b5ddd0d6b04` | Small diagnostic-preservation patch and regression | Local construction verified; autonomous-repair comparison remains inconclusive. |
| E3-M4 surface authority | `616320aec7137589da0e810b7f4c19b4de105a50` | Domain-neutral authority map and frozen cases | Held-out causal measurement incomplete; the mixed `codex/e3-m4-authority-separation` branch is not a single-feature promotion unit. |
| E4-A grounded experience | `22d7d8424da7c50dfa8ca3256945513afc31f213` | Frozen benchmark, provenance anchor, tests | Live provider measurement unavailable; candidate overlaps E1.3 in `src/retry_gate.py`. |
| Goal Control and Context Residency | `9aae306` on `codex/goal-control-isolated` | Stable Goal/Task contracts, hot-path reduction, drift/resume regressions | Rebased cleanly onto `main`; 43 focused tests and local structure/link checks passed. Live-agent behavioral effect and independent acceptance unmeasured. |

Keep these candidates and their evidence reachable, but do not count them as
implemented `main` features. A future promotion should take one bounded
candidate at a time from current `main`, preserve frozen evidence, compare
regressions against the same-environment baseline, and obtain the applicable
P30 fresh, artifact-first decision for the exact resulting clean identity.
Behavioral improvement claims require valid held-out behavior evidence; a
quota/credential failure or zero valid runs is measurement failure, not a
negative or positive result. Do not silently combine overlapping candidates
or use a broad merge to promote an unrelated ancestor.
