> L0: 验收协议 — Verify/Fix/Re-Verify 分离 (M-n 29 实操).  Load when: 验收任务.
# Acceptance Protocol — Verify / Fix / Re-Verify Separation

> **Trigger**: User 2026-07-30 final ask: "验收和修改是不是应该分开？验收只找问题，找完了再集体返修，这样有很多好处".
>
> **Pattern fixed**: Prior turns exhibited "ship → verify → fix → re-verify" within one
> turn, which caused acceptance result drift (M-n 32 Guardrail #1 violation).
> 55% of recent commits were "fix-after-verify" (per audit).
>
> **Decision**: 验收/修改分离 as standard practice. P30 adds the required
> epistemic-role boundary: local verification and regression evidence are not
> independent artifact acceptance. This document codifies the protocol for
> future turns.

## 1. Why separate (per 软件测试 standard practice)

Software testing has well-established phase separation:

| Phase | Purpose | Modifies state? |
|---|---|---|
| **Unit tests** | Test individual components | ❌ no |
| **Integration tests** | Test component interaction | ❌ no |
| **System tests** | Test full system | ❌ no |
| **Acceptance tests** | Verify against requirements | ❌ no |
| **Fix** | Apply patches based on findings | ✅ yes |

**Key principle**: Tests (incl. acceptance) should NOT modify the system under test.
Otherwise test results drift = can't compare across runs.

Per **P30**, the constructor also cannot be the final acceptor. Distinguish:

| State | Issuer | Authority |
|---|---|---|
| **LOCAL FIX VERIFIED** | Implementer | Targeted local issue only |
| **REGRESSION PASS** | Implementer and/or checker | Known frozen invariants and specified checks |
| **INDEPENDENT ACCEPTANCE PASS** | Fresh evaluator with no material authorship of the accepted state | Terminal acceptance, freeze, or submission-readiness |

`CHECKER PASS != INDEPENDENT ACCEPTANCE PASS`.

The IMPLEMENTER may not issue final acceptance of its own modified artifact.
Its handoff is `IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT`.
For final promotion of an externally consumed artifact, see
[Artifact Finalization](ARTIFACT_FINALIZATION.md).
The handoff records `ARTIFACT_IDENTITY`, `CURRENT_ROLE`,
`MATERIAL_MODIFICATION_SINCE_LAST_ACCEPTANCE`, `PRIOR_ACCEPTANCE_STATE`,
`EVALUATOR_MATERIAL_EDIT`, `EVALUATOR_AUTHORITY_VALID`, and
`TERMINAL_ACCEPTANCE_STATUS`; the report template is in the detail file.

P30-A3 clarifies the trust boundary: repository tooling can compute the
current artifact identity and verify an already-existing external record, but
it cannot create independent acceptance from caller-supplied role, identity,
audit, materiality, or evaluator-edit claims. A clean commit hash establishes
identity/integrity; it does not prove evaluator independence.

Per tua-start `AGENTS.md` "Task-done-notify reminder" (M-n 16 stage 1-2):
- 5 primitives must apply BEFORE any commit
- This includes Plan / Search / Lesson / Observe / Cite
- **None of these are "fix and ship"** — they're pre-commit gates

## 2. The role-separated protocol

```
┌─────────────────────────────────────────────────┐
│ Phase 1: IMPLEMENT / LOCAL VERIFICATION         │
│   - Implementer applies the requested change     │
│   - Check the targeted local issue               │
│   - Status: LOCAL FIX VERIFIED                  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Phase 2: REGRESSION CHECK (implementer/checker) │
│   - Run specified frozen-invariant checks        │
│   - Record REGRESSION PASS or findings           │
│   - This is not artifact acceptance              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Phase 3: INDEPENDENT ACCEPTANCE (fresh state)   │
│   - Inspect artifact before implementation report │
│   - Freeze first-pass findings before rationale   │
│   - Only fresh evaluator may return PASS/MODIFY/STOP │
│   - Do not modify during first-pass audit        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Phase 4: MODIFY / RE-AUDIT (only if material)   │
│   - Return to implementation state               │
│   - Material modification makes old acceptance   │
│     stale; obtain another independent audit       │
└─────────────────────────────────────────────────┘
```

## 3. Acceptance location (per user ask: project vs user layer)

| Layer | Purpose | Where |
|---|---|---|
| **核心层** (core) | SUA's permanent contract | agent-tools/scripts/, core-layer/, hooks/ |
| **项目层** (project) | SUA's design + protocol | docs/, AGENTS.md, AGENTS_DETAIL.md |
| **用户层** (user) | Per-user daily work | local file (gitignored) |

**Decision**: Acceptance results live in **用户层** (per-user, ephemeral),
project layer has the **protocol** (this doc).

Rationale:
- Project layer = SUA's design (what SUA is supposed to be)
- User layer = your daily work verification (what state is SUA in *now*)
- Separation per 3-layer policy: project documents don't mix with
  user artifacts.

Practical file naming:
- `docs/ACCEPTANCE_PROTOCOL.md` — this protocol (project layer)
- `~/.config/sua/acceptance/ACCEPTANCE_<DATE>.md` — your state (user layer)

## Detailed protocol and templates

For report structure, external audit records, regression tools, and the
historical implementation plan, read [ACCEPTANCE_PROTOCOL_DETAIL.md](ACCEPTANCE_PROTOCOL_DETAIL.md).

Last P20-verified: 2026-09-28
