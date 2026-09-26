# M-task-lifecycle (full text)
Last P20-verified: 2026-09-10

> L0: L2 detail for `OPERATING_RULES.md` §
> M-task-lifecycle段 (M-n 31).
> Per P11 摘要+引用 + R6.

**Origin**: per user message 2026-07-15 directive
"中优先级 567 需要处理" (item 6 + item 7).

## 4-phase decision tree

## Goal and task identity extension (2026-09-26)

The Goal Contract is `goal_id`, `objective`, `success_criteria`, `non_goals`,
`constraints`, `status`, `version`. It is the authority for task planning;
the title is descriptive and never encodes retry/revision/feedback history.
A Task has stable `task_id`, title, goal_id, criterion links, status, version,
dependencies, next action, blocker, and residency. Allowed statuses are `ACTIVE`, `WAITING_USER`,
`BLOCKED`, `SUSPENDED`, `SUPERSEDED`, `DONE`, `ABANDONED`.

At each material action, record `Action → Task → Criterion → Goal`.
Goal Guard checks that action, task, criterion, and Goal Contract version
still match a reviewed authorization. The reference contract rejects an exact
`non_goals` action string; the caller must judge natural-language constraints
and semantic alignment. A stored checksum detects direct Goal Contract edits.
Before a material action, ask whether it could succeed while the linked
criterion remains unmet. If yes, name the action's necessary contribution
and return point; if neither is clear, replan instead of promoting a method
or metric into the objective. This is a reasoning check, not a semantic
guarantee from the deterministic reference code.
When a task leaves ACTIVE, capture its capsule, persist it, then evict it
to COLD or ARCHIVED. Resume only when the caller supplies the matching named
trigger and the capsule still matches the current goal. The caller remains
responsible for verifying that the external trigger actually occurred.
A superseded goal never re-enters by default.
Any versioned goal revision suspends its nonterminal task plans for explicit
review before they can resume.
Criterion correction keeps the goal_id and increments the contract version;
objective mutation needs a new goal_id and explicit supersession. New task
creation and supersession both require the expected Goal Checksum. The
feedback router returns a typed next action without silently applying these
contract changes.

`src/goal_control.py` is a deterministic reference contract with regression
tests. Configure `ControlPlane(capsule_dir=...)` or pass a path to a task
transition; without a durable destination, eviction fails closed.
`pause_and_persist` writes a capsule before eviction; `resume_from_file`
checks it against reconstructed current contracts and a named trigger. This is
not automatic natural-language classification or a runtime-wide integration.
Existing P30 acceptance authority remains separate.

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
