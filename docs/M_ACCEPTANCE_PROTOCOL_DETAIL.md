# M-acceptance-protocol (full text)
Last P20-verified: 2026-09-11

> L0: L2 detail for `OPERATING_RULES.md` § M-
> acceptance-protocol段 (M-n 29).  Per P11
> 摘要+引用 + R6, this companion is required
> when the summary段 references detailed
> 5-step protocol + 验收 report template +
> cycle loop.

**Origin**: per user message 2026-07-15 explicit
6 parts + 你 implicit research directive
(project acceptance + agent acceptance +
harness references).

## 5-step protocol (detailed)

### Step 1: Design 验收 角度 + 要求

Per M-n 22 3W1H first + NASA SWE-034
("Formulation phase") + Claude
acceptance-criteria-verification skill:

| 角度 | 验收 criteria examples |
|---|---|
| **functional** | 所有 functional requirements met |
| **performance** | latency / throughput / memory OK |
| **兼容性** | framework-agnostic + 跨 project sync |
| **安全** | no PII / no leak / no unsafe patterns |
| **维护性** | docs stay current + R5/R6/R8 PASS |
| **user-facing** | L0 + L1 + L2 + cross-refs visible |
| **framework-agnostic** | Hermes + Codex + Claude Code 全部 |
| **跨项目 sync** | SUA ↔ skill ↔ skill-incubator ↔ KG |
| **R1-R12** | ALL PASS (per c173 VERIFICATION.md) |
| **P-n compliance** | 26 P-n all cited + applied |
| **M-n compliance** | 28 M-n all applied per context |
| **P29 self-application** | agent 主动 reduce context |
| **项目 整洁度 (per user message 2026-07-15 reminder)** | 路径 + 命名 + 文档结构 consistent (per M-n 19 file-naming-convention + c149-c151 .gitignore + c191 整理 + c115 整理 process) |
| **新 agent 可读性 (per user message 2026-07-15 reminder)** | 项目 内容 可读 + 充分 (per M-n 20 agent-discoverability + P26 fresh-agent + VERIFICATION.md per c193 + user message prior 7 docs in sync) |

## Step 2: Execute 验收 (5 constructive + 4 critical primitives)

Per user message Part 3 explicit: "按照规范分析、
推理、联想、归纳、总结的逻辑过一遍完整的
项目".  This is 5 constructive primitives (M-n 16 +
M-n 14 + M-n 25 + M-n 26).

**Per user message 2026-07-16 + M-n 14 two-track**: complete
thinking needs BOTH constructive + adversarial.  Add 4
critical-thinking primitives (per
`docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md`):

### 5 constructive primitives

1. **Analyze** (per M-n 16 observe-think-
   execute stage 1):
   - What: 任务 IS what?
   - Boundaries: 范围 (per R11)
   - Components: 哪些 part / file / commit?
2. **Reason** (per M-n 16 stage 2 + M-n 22
   3W1H):
   - Why: 为什么 这样设计?
   - Trade-offs: what sacrificed?
   - Alternative: what else considered?
3. **联想 (analogize)** (per M-n 14 class比
   + M-n 17 Path 2 inter-domain):
   - 类似 prior pattern in SUA / skill /
     skill-incubator / KG?
   - MCP search (per c94 MCP-first
     verification pattern) for prior art?
4. **归纳 (induct)** (per M-n 14 induction
   + M-n 18 recursive summary):
   - General pattern from specific?
   - What can be applied to other 任务?
5. **总结 (summarize)** (per M-n 26
   compression + M-n 18 destruction):
   - Synthesize into 1-paragraph L0
   - Apply 节点 生命周期 (destroy redundant
     details)

### Constructive quality gate for open-ended work

Primitive names are not evidence of primitive results. When the task includes
open-ended discovery, design, planning, or hypothesis formation, PASS requires
**observable constructive expansion** before terminal critique:

1. Analyze exposes the uncertain object, boundary, and search dimensions.
2. Reason produces alternatives with explicit causal or decision differences.
3. Association records a donor-to-target mapping, transferred invariant or
   constraint, target consequence, and at least one generated delta;
   retrieval alone is insufficient.
4. Induction changes the abstraction, mother problem, or search policy when
   repeated cases share a failure; merely summarizing why all branches fail is
   insufficient.
5. Synthesis yields a comparable set of structurally distinct alternatives
   and a justified transition to critique/selection.

For well-specified execution, direct logical execution is the correct route
and does not require constructive expansion. Apply the quality gate only to
the open-ended portion of a mixed task.

### 4 critical-thinking primitives (per user message 2026-07-16)

Apply phase-aware per M-n 14 two-track. For open-ended work, complete bounded
constructive expansion and synthesis before terminal critique; hard-stop
exceptions remain immediate. Default-on for high-stakes
decisions (architecture, cross-project, new P-n
or M-n lifts); optional for single-file
refactors; skip for trivial fixes.  Full details:
`docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md`.

6. **质疑 (Challenge)** — after Analyze:
   - 3 specific weaknesses in current proposal
   - Highest-damage weakness — proceed
     acknowledging
7. **逆向 (Invert)** — after Reason:
   - OPPOSITE state explicitly
   - 2-3 reasons OPPOSITE could be true
   - What would change if OPPOSITE true
8. **预演失败 (Pre-mortem)** — after 联想:
   - "**this FAILED in 30 days**"
   - 3-5 specific failure modes + causes
   - 1-2 preventable ones — fix before commit
9. **对立论证 (Steelman-the-opposite)** —
   after 归纳:
   - Most charitable opposing case
   - 2-3 strongest opposing arguments
   - Acknowledge valid opposing points

## Step 3: Validate regression evidence and authority condition

Per user message Part 4 "确认没问题":

| Check | Required evidence |
|---|---|
| Implementation checks | Bounded evidence only; implementer reports `REGRESSION PASS`, not terminal acceptance |
| 5 constructive primitives | All applicable primitives have observable outputs; labels alone fail |
| Open-ended constructive quality | Output space expanded with structurally distinct alternatives and a donor transfer; well-specified execution is exempt |
| Phase ordering | Bounded Add and synthesis precede terminal critique, except immediate hard stops |
| 4 critical-thinking primitives | Default-on for high-stakes: 质疑 + 逆向 + 预演失败 + 对立论证 |
| Evidence recorded | test output / commit hash / file size / artifact identity |
| R1-R12 ALL PASS | Per c173 + per latest VERIFICATION.md |
| P-n compliance | All 26 P-n applicable cited |
| M-n compliance | All applicable M-n applied |
| Framework-agnostic | All 4 frameworks (Hermes/Codex/Claude Code/Cursor) |
| P17 老实说 | Don't claim green when yellow |

For a material artifact, the M-n 29 checklist is not sufficient for terminal
acceptance.  The shared P30 state boundary must also show:

- `CURRENT_ROLE = INDEPENDENT_EVALUATOR`;
- a matching `ARTIFACT_IDENTITY` and non-stale prior state;
- `INDEPENDENT_AUDIT_STATUS = INDEPENDENT AUDIT COMPLETE`;
- artifact-first review with first-pass findings frozen before rationale;
- `EVALUATOR_MATERIAL_EDIT = NO`; and
- `EVALUATOR_AUTHORITY_VALID = YES`.

Missing, unknown, contradictory, or stale fields fail closed to
`ACCEPTANCE BLOCKED / INDEPENDENT AUDIT REQUIRED`.  An implementer or checker
may produce regression evidence but cannot issue `INDEPENDENT ACCEPTANCE PASS`.

### Global-progress acceptance

A run of **locally valid terminal decisions** can still fail the task. When
repeated rejection, KILL, stop, or rollback decisions produce no surviving
alternative and no **output-space expansion**, trigger a **controller-level
replan** at the final-objective and abstraction level. Preserve negative
knowledge, diagnose whether the branch, mechanism family, mother space, or
generation policy is saturated, and change the search source or stop with an
explicit global infeasibility conclusion.

There is **no fixed rejection count**. The trigger is evidence of repeated
same-structure terminal decisions plus absence of global progress. A
validation or retrieval tool must not silently become the generation policy.

#### Rejection-aware retry gate

The executable owner is `src/retry_gate.py`; controllers pass a serialized
`RetryState` plus an explicitly classified `RetryProposal` to
`evaluate_retry()`. This section is the protocol contract, not a second gate.

For a user-facing artifact, when the user is the acceptance authority and
explicitly says that the same core acceptance criterion remains unmet, that
rejection invalidates any prior local `PASS` for that criterion. Treat it as an
external failure signal, not as a request for cosmetic polish.

Before another attempt, carry this compact failure-state record:

- `PARENT_OBJECTIVE`
- `FAILED_ACCEPTANCE_CRITERION`
- `FAILURE_CLASS`
- `REPRESENTATION_FAMILY`
- `PRODUCTION_SUBSTRATE`
- `CAUSAL_LAYER`
- `CAUSAL_LAYER_CHANGED`
- `CAUSAL_DELTA`
- `ARTIFACT_ROLE_PLACEMENT`
- `REPRESENTATION_VARIANT` (optional; never a family identity)
- `CRITERION_CLASS`
- `ACCEPTANCE_AUTHORITY`
- `AUTHORITY_BASIS`
- `NEGATIVE_KNOWLEDGE`
- `UNCHANGED_ASSUMPTIONS`
- `PRIOR_LOCAL_PASS`

A retry is admissible only when `CAUSAL_DELTA` changes a layer capable of
explaining the failure. If there is **no causal delta**, stop local polish,
preserve the failed state and negative knowledge, and trigger a
controller-level replan. The abstraction ladder is: local parameter →
implementation → substrate/tool → representation/problem framing → artifact
role/placement → parent objective/acceptance criterion. Move upward when the
same failure survives the current layer; a cosmetically different variant at
the same layer is not a causal change. Record the rejected representation,
substrate, and unchanged assumptions so a renamed retry cannot silently revive
them. `REPRESENTATION_FAMILY` is the canonical representation identity;
`REPRESENTATION_VARIANT` is optional descriptive metadata and changing it alone
does not create a structural delta. Omitted optional fields, including
`ARTIFACT_ROLE_PLACEMENT`, do not count as changed fields.

The controller must not use `max_retries` as retry authorization. It is only a
hard quantity ceiling. After a failed attempt, a canonical retry requires both
the prior `RetryState` and an explicitly classified `RetryProposal`; if either
is missing, the controller stops before a second attempt with
`RETRY_CONTEXT_REQUIRED`.

`RetryState.to_json()` / `RetryState.from_json()` preserve these fields for a
fresh controller invocation. The gate returns `RETRY_ALLOWED`,
`GLOBAL_REPLAN_REQUIRED`, `ACCEPTANCE_AUTHORITY_UNVERIFIED`, or
`RETRY_CONTEXT_REQUIRED`; it does not infer authority or causal layers from
unclassified prose.

### Step 4: If regression evidence fails or the evaluator materially edits → 新 任务 cycle

Per user message Part 5: "如果验收没通过，就需
要当作新任务继续修改（每次你认为做完任务
都需要验收，没通过就修复，修复完再测，循环）":

1. Create new task in PLAN_DETAIL
2. Re-execute fix
3. Re-verify (回到 step 2)
4. Loop until bounded regression evidence is complete, then hand off for a
   fresh independent audit.  Do not loop from implementation directly to
   terminal artifact acceptance.

### Step 5: If regression evidence is sufficient → implementation handoff

Per user message Part 6: "通过了得跟用户明确说明":

- 明确 indicate `IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT`
- List artifact identity and bounded regression evidence
- Mark artifact acceptance `NOT ISSUED`
- Per P30: only the later fresh evaluator may issue terminal acceptance
- Per M-n 24: pace-continuity 中 明确 通知
  you is allowed

## Regression-evidence / acceptance-state template

Per Claude acceptance-criteria-verification
skill + NASA SWE-034:

```
## Verification / Acceptance-State Report

**Run**: 2026-07-15T15:30:00Z
**By**: agent
**Commit**: <hash>
**Branch**: master
**ARTIFACT_IDENTITY**: <commit/hash/version/state id>
**CURRENT_ROLE**: IMPLEMENTER / INDEPENDENT_EVALUATOR / UNSPECIFIED
**MATERIAL_MODIFICATION_SINCE_LAST_ACCEPTANCE**: YES / NO / UNKNOWN
**PRIOR_ACCEPTANCE_STATE**: VALID / STALE / NONE
**LOCAL_FIX_STATUS**: LOCAL FIX VERIFIED / NOT RUN
**REGRESSION_STATUS**: REGRESSION PASS / REGRESSION INCOMPLETE / NOT RUN
**INDEPENDENT_AUDIT_STATUS**: INDEPENDENT AUDIT COMPLETE / INDEPENDENT AUDIT REQUIRED / NOT RUN
**EVALUATOR_MATERIAL_EDIT**: YES / NO / UNKNOWN
**EVALUATOR_AUTHORITY_VALID**: YES / NO / UNKNOWN
**TERMINAL_ACCEPTANCE_STATUS**: NOT ISSUED / ACCEPTANCE BLOCKED / INDEPENDENT ACCEPTANCE PASS

### Results

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | <criterion text> | PASS / FAIL / PARTIAL / SKIP | <evidence> |
| 2 | <criterion text> | PASS / FAIL / PARTIAL / SKIP | <evidence> |
| ... | ... | ... | ... |

### Summary

| Status | Count |
|--------|-------|
| REGRESSION PASS | X |
| FAIL | X |
| PARTIAL | X |
| SKIP | X |
| **Total** | **X** |

### Evidence

- Test output: <path or inline>
- Commit hash: <hash>
- File size: <bytes>
- R1-R12 status: <per VERIFICATION.md>

### 5 primitives applied

- [x] Analyze: <findings>
- [x] Reason: <findings>
- [x] 联想: <findings>
- [x] 归纳: <findings>
- [x] 总结: <findings>

### Next steps

- [ ] <if FAIL: action items>
- [x] <if implementation-only: `IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT`>
- [ ] <if terminal acceptance requested: independent artifact-first decision record>
```

## Worked example (c203 self-application)

Apply M-n 29 to current task (c203 codify
M-n 29 itself):

**Step 1 (Design 角度)**: Functional (5
primitive protocol defined) + Framework-
agnostic (per M-n 20) + R-n (per R1-R12) +
P-n (per 26 P-n) + M-n (per 28 M-n).

**Step 2 (Execute 验收)**:
- Analyze: M-n 29 段 IS 5-step protocol
  (defined in OPERATING_RULES.md 83323 → 78618).
- Reason: 5 primitives match user message Part 3
  explicit + M-n 16 stage 1-2 + M-n 14 class比
  induction + M-n 18 recursive summary + M-n
  26 compression.
- 联想: 类似 Claude acceptance-criteria-
  verification skill + NASA SWE-034.  MCP
  search per c94 confirms pattern.
- 归纳: 5-step pattern = general protocol
  for task acceptance.
- 总结: this L2 companion IS the protocol
  总结.

**Step 3 (Validate)**: Regression evidence is complete; this does not issue
terminal artifact acceptance.

**Step 4 (FAIL check)**: No FAIL.

**Step 5 (implementation handoff)**: This
section.  A separate fresh evaluator is required
for any terminal artifact decision.

## Relationship to M-n 28

M-n 28 (plan-conditional) is BEFORE M-n 29
(acceptance):
- M-n 28 = when to plan vs continue.
- M-n 29 = when implementation is complete, record regression evidence and
  hand off; terminal artifact acceptance remains a separate P30 decision.

Sequence: plan (M-n 28) → execute → accept
(M-n 29) → notify.

## Relationship to VERIFICATION.md (c193)

VERIFICATION.md is THE 1-page project-level
verification summary (per c193).  M-n 29 IS
the protocol that PRODUCES such summaries
(each major commit batch → fresh verification
per M-n 29 → update VERIFICATION.md per
P14 docs stay current).

## Cross-references

- `docs/OPERATING_RULES.md` § M-acceptance-
  protocol (M-n 29 main段)
- `docs/OPERATING_RULES.md` § M-n 14/16/17/
  18/24/26/28
- `docs/PRINCIPLES.md` P17 + P22
- `VERIFICATION.md` (1-page summary per c193)
- NASA SWE-034 (research reference)
- Claude acceptance-criteria-verification
  skill (research reference)
- user message 2026-07-15 — origin
