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

## 4. Acceptance state/report structure

Each terminal material-artifact workflow produces a P30 state record before
any terminal decision.  Ordinary checkers may produce regression evidence
without creating an acceptance record.  The shared fail-closed state boundary
is implemented in `agent-tools/scripts/p30_acceptance.py`.

```markdown
# Artifact Acceptance State Record — <DATE>

## Artifact and authority state
- HEAD: <git SHA>
- ARTIFACT_IDENTITY: <commit/hash/version/state id>
- Tag: <vX.Y.Z if tagged>
- Working tree: clean / dirty
- Python version: <ver>
- Platform: <Windows/Mac/Linux>
- MATERIAL_ARTIFACT: YES / NO
- CURRENT_ROLE: IMPLEMENTER / INDEPENDENT_EVALUATOR / UNSPECIFIED
- ARTIFACT_STATE: UNACCEPTED / ACCEPTED / STALE_AFTER_MATERIAL_CHANGE / READY_FOR_INDEPENDENT_AUDIT
- MATERIAL_MODIFICATION_SINCE_LAST_ACCEPTANCE: YES / NO / UNKNOWN
- PRIOR_ACCEPTANCE_STATE: VALID / STALE / NONE
- PRIOR_ARTIFACT_IDENTITY: <identity or NONE>
- EVALUATOR_MATERIAL_EDIT: YES / NO / UNKNOWN
- EVALUATOR_AUTHORITY_VALID: YES / NO / UNKNOWN

## Run command
- bash sua-verify-<name>.py
- python -m pytest tests/

## Evidence states
| Check | Result | Detail |
|---|---|---|
| local fix | LOCAL FIX VERIFIED / NOT RUN | targeted issue evidence |
| regression | REGRESSION PASS / REGRESSION INCOMPLETE / NOT RUN | specified checks only |
| execution | EXECUTION_SUCCESS / EXECUTION_FAILED | runtime/task completion only |
| independent audit | INDEPENDENT AUDIT COMPLETE / INDEPENDENT AUDIT REQUIRED / NOT RUN | fresh artifact-first evaluator |
| evaluator edit | YES / NO / UNKNOWN | material edit terminates evaluator authority |
| ... | ... | ... |

## Findings
1. <finding 1>
2. <finding 2>
...

## Severity
- BLOCKER: must fix before ship
- MAJOR: should fix this turn
- MINOR: can defer to next session
- INFO: documentation only

## Terminal decision
- LOCAL_FIX_STATUS: <status>
- REGRESSION_STATUS: <status>
- INDEPENDENT_AUDIT_STATUS: <status>
- TERMINAL_ACCEPTANCE_STATUS: NOT ISSUED / ACCEPTANCE BLOCKED / INDEPENDENT ACCEPTANCE PASS
- ISSUER_ROLE: <explicit role>

For a material artifact, an unknown, missing, contradictory, or stale
authority field yields `ACCEPTANCE BLOCKED / INDEPENDENT AUDIT REQUIRED`.
Only a fresh `INDEPENDENT_EVALUATOR` with matching artifact identity,
artifact-first first-pass evidence, no material edit, and valid authority may
issue `INDEPENDENT ACCEPTANCE PASS`.  `EXECUTION_SUCCESS`, checker output,
`REGRESSION PASS`, and an implementation handoff never issue it.

## Next action
If independent audit finds a material issue → Phase 4, then a new Phase 3.
If the result is implementation-only → report READY FOR INDEPENDENT AUDIT.
If a material evaluator edit occurs → terminate that evaluator authority,
mark the resulting state stale, and return to implementation flow.
```

## 5. Regression-evidence tools (sua-verify- prefix scripts)

Currently 3 scripts in `agent-tools/scripts/`:
- `self_health_check.py` — string pattern checks
- `cross_repo_audit.py` — sibling pollution check
- `hook_principles_loader.py` — Q2 closure registry
- `p30_acceptance.py` — shared role/state/identity boundary; terminal mode is
  fail-closed unless all P30 evidence fields are explicit

Recommended new tools (per gap analysis):
- `validate_links.py` — markdown cross-reference integrity (22 broken refs found)
- `validate_structure.py` — file structure matches expected layout
- `token_budget.py` — large file detection (> 100KB)

These should be invoked from a single entrypoint:

```bash
bash agent-tools/scripts/run_acceptance.sh
```

This produces regression evidence only.  It does not produce or imply
`INDEPENDENT ACCEPTANCE PASS`.

## 6. Regression evidence as gate (notifier + rejector)

Two modes:

### 6a. Advisory mode (default)

- Run regression checks → produce evidence
- Decision is human's
- No automatic reject

### 6b. Gate mode (STRICT_EVAL=1)

- Run regression checks → if incomplete, reject the technical transition
- Pre-commit hook: `bash agent-tools/scripts/run_acceptance.sh --gate`
- Set in `.git/hooks/pre-commit`

`--gate` is a technical regression gate only.  It never authorizes artifact
acceptance.  A request for terminal acceptance must use the P30 state record;
missing role, identity, non-stale state, artifact-first evidence, or clean
evaluator-authority fields is refused.

## 7. Implementation plan

The original protocol was a **project-layer** change (new doc + protocol),
not a core-layer change. The P30 amendment is different: because it adds a
canonical principle, its necessary registry and validation surfaces are
updated under the principle-modification procedure.

### Files to create
- `docs/ACCEPTANCE_PROTOCOL.md` (this file) — already done
- `agent-tools/scripts/run_acceptance.sh` — single entrypoint
- `agent-tools/scripts/validate_links.py` — link integrity check
- `agent-tools/scripts/p30_acceptance.py` — shared P30 authority/state boundary

### Files to modify
- `hooks/pre-commit` — add acceptance run (gated by STRICT_EVAL)
- `docs/PROJECT_STATE.md` — add acceptance protocol reference
- `AGENTS.md` — add acceptance phase to task-done-notify

### P30-A2 active-path correction

The current active-path correction keeps M-n 29/M-n 31 execution and
implementation completion useful, but routes their output to regression
evidence and an independent-audit handoff.  `run_acceptance.sh`,
`verify_after.py`, `eval_before.py`, `release_audit.py`, and the pre-commit and
pre-push hooks call or enforce the shared P30 boundary.  A terminal request
without a complete role/identity/audit state is refused.

### Files NOT to modify (留新 session)
- `core-layer/AGENTS_CORE.md` — core layer change requires M-n 15
- `docs/OPERATING_RULES.md` — 109KB file, split first (separate task)

## 8. Net assessment

Per 预判 (good vs bad):

| Aspect | Good | Bad |
|---|---|---|
| Acceptance / Fix separation | ✅ Stable results | ⚠️ More turns |
| User-layer acceptance | ✅ Project layer clean | ⚠️ Need new dir |
| New validate_links.py | ✅ Prevent link drift | ⚠️ Maintenance burden |
| Role-separated protocol | ✅ Software test standard + independent authority | ⚠️ Adoption cost |

**Net verdict**: Adoption is worth it. Reduces verify-then-fix churn,
makes acceptance results comparable across versions.

## 8a. Final promotion of externally consumed artifacts

When acceptance targets a publication, release, dataset, benchmark, report,
deck, or reproducibility bundle—and repeated local repairs, frozen proxies, a
major mutation, killed-defect risk, or validator correlation is present—run
the bounded [Artifact Finalization](ARTIFACT_FINALIZATION.md) gate before the
final acceptance decision. It preserves evidence-backed freezes while
challenging historical presentation and implementation residue. P30 supplies
the authority boundary: the implementer may prepare the handoff and report
regressions, but only an independent fresh-state evaluator may issue terminal
acceptance.

## 9. References

- tua-start `AGENTS.md` "Task-done-notify reminder" (5 primitives)
- tua-start `AGENTS.md` "Iterative thinking" (Apply / Observe / Re-think)
- tua-start `AGENTS.md` "Recursive test-verify" (TDD pattern)
- M-n 32 Guardrail #1 (real verify before claim)
- M-n 36 pre-release audit (no github commit confusion)
- R137 wordy-trap defense (avoid "全部好了" claim)
- P-7 Occam (smallest effective change)
- P-14 self-contained mandate (no internal refs in user-facing docs)
- P-17 no fabricate (honest value assessment)
- Industry: 软件测试 V-model (Verification & Validation phases)
- Industry: Test-driven development (test first, code until pass)

Last P20-verified: 2026-09-10
