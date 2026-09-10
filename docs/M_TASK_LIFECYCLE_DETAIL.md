# M-task-lifecycle (full text)
Last P20-verified: 2026-09-10

> L0: L2 detail for `OPERATING_RULES.md` §
> M-task-lifecycle段 (M-n 31).
> Per P11 摘要+引用 + R6.

**Origin**: per user message 2026-07-15 directive
"中优先级 567 需要处理" (item 6 + item 7).

## 4-phase decision tree

### Phase 1: task-init

**Trigger**: agent receives user message with
explicit directive.

**Methods**:
- M-n 22 3W1H (What / Why / Who / How)
- M-n 21 ask-or-infer-mark-guess
- M-n 28 4-condition self-audit
- M-n 7 task-summary (if complex)

**Output**: scope + boundaries explicit.

### Phase 2: task-execute

**Trigger**: scope explicit + proceed.

**Methods**:
- M-n 16 observe-think-execute
- M-n 18 sub-task summary + commit
- M-n 24 pace-continuity
- M-n 26 context-decay (per long task)

**Output**: tasks completed + commits.

### Phase 3: implementation-handoff

**Trigger**: all implementation sub-tasks done + local verification and
regression evidence recorded.

**Methods**:
- M-n 29 Step 5 (regression-evidence notification)
- P30 role/state boundary
- user message directive: "明确告知"
- Format: `IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT` plus
  artifact identity and the bounded evidence list

**Output**: the user knows the implementation status.  This phase cannot
issue terminal artifact acceptance.

### Phase 3b: independent-acceptance

**Trigger**: a fresh evaluator receives the current artifact and the
implementation handoff, then completes artifact-first review.

**Authority**: only the evaluator may issue `INDEPENDENT ACCEPTANCE PASS`.
An evaluator that materially edits the artifact loses authority for the
resulting state and returns the work to implementation flow.

### Phase 4: task-retrospective

**Trigger**: notify sent + user message next.

**Methods**:
- M-n 26 (4 sub-steps: re-read + 类比归纳
  + 整理 + checkpoint)
- Memory update (per session)
- 7-check (per user message message-pattern
  directives)

**Output**: lessons captured + memory
current.

## Worked example (c228 self-application)

Apply M-n 31 to user message "中优先级 567 处理":

- **Phase 1 (task-init)**: user message directive
  clear (处理 5+6+7), scope = 3 items.
- **Phase 2 (task-execute)**: 
  - c227 (skill): 3-layer architecture in
    skill (item 5)
  - c228 (SUA): M-n 31 codify + L2
    companion (item 6 + 7 combined)
  - c229 (SUA): PLAN update
- **Phase 3 (implementation-handoff)**: this
  段 records the non-terminal implementation handoff per M-n 29 Step 5 + P30.
- **Phase 4 (task-retrospective)**: per
  M-n 26 → memory update if 必要.

## Task-done indicator (per user message)

Per user message prior directive "如果做完任务，
需要你跟我明确指出":

### Implementation handoff template

```
IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT
- Artifact identity: [commit/hash/version/state id]
- Current role: IMPLEMENTER
- Local fix status: LOCAL FIX VERIFIED / NOT RUN
- Regression status: REGRESSION PASS / REGRESSION INCOMPLETE
- Artifact acceptance: NOT ISSUED
- Next evaluator: fresh artifact-first independent evaluator
- Known limits: [list]
```

### Historical examples (not current terminal templates)

Earlier examples that used generic `Task done` / `PASS` wording are historical
records only.  They must not be reused for a material artifact after P30.
Use the implementation handoff template above and route terminal decisions to
the independent evaluator.

## Project lifecycle (per user message prior)

### Init phase

- AGENTS.md created
- PLAN file (agent-tools/plans/<date>-<topic>.md)
- R1-R12 baseline (12 rules)

### Active phase

- Multiple commits (per M-n 18)
- M-n codify (per M_RULE_AUTHORING)
- Cross-ref maintenance (per P21)
- Retention R5 (per R5)

### Archive phase (after independent acceptance)

- Freeze or tag only after a valid independent terminal decision
- Move to .archive/ if 必要
- Keep context for future reference
- Update README to "completed" status

An implementation commit may be complete without being accepted.  Archive
and freeze are not reachable from the implementation-handoff phase alone.

## Cross-references

- `docs/OPERATING_RULES.md` § M-task-
  lifecycle段 (M-n 31 main段)
- `docs/OPERATING_RULES.md` § M-n 7 + 16
  + 18 + 21 + 22 + 24 + 26 + 28 + 29
- user message 2026-07-15 directive "中优先
  级 567 处理"
