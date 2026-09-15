# Add-then-reduce cycle (M-add-then-reduce M-rule)
Last P20-verified: 2026-09-15

> L0: Add expands task-relevant state; Reduce tests, consolidates, and removes what no longer earns complexity.
> Load when: planning a multi-leaf task,
> noticing doc/context bloat, or evaluating whether to
> apply M-learn's 3 sub-actions.

## The 2-phase cycle

Tasks have a 2-phase lifecycle; the cycle repeats:

- **Add (执行期)**: expand the kind of state the task needs. Permitted to be
  redundant during this phase — exploration needs slack. No premature
  compression.
- **Reduce (整理期)**: compress, abstract, dedupe, destroy
  intermediate state.  Only triggered by signal (see
  below).  This is where M-learn's 3 sub-actions run.

Add has two forms. Choose from the task objective; do not silently substitute
one for the other:

- **artifact/evidence Add** gathers information, writes code or documents,
  pushes commits, and stores snapshots. It is sufficient for well-specified
  execution and for later verification.
- **constructive search-space Add** is for open-ended discovery, design,
  planning, or hypothesis formation. It generates structurally distinct
  alternatives, mechanisms, problem representations, constraints, or donor
  transfers. More papers, more notes, renamed variants, or more objections do
  not by themselves expand the search space.

For open-ended work, use a **bounded constructive Add window**: expand first,
then synthesize before terminal critique. Risks may be recorded during Add,
but terminal rejection belongs to Reduce unless a hard-stop exception applies.
End the window when new additions repeat the same structure, the task's
explicit diversity requirement is met, or a decision-relevant resource bound
is reached. No universal candidate count is required.

## Trigger for reduce (3 signal types)

| Signal type | What triggers it | Who runs M-learn |
|---|---|---|
| Structural | parent-task INTEGRATE point (all sub-tasks done) | always |
| Context | user says "乱" / "compress" / "整理"; or agent notices context overflow risk | when signaled |
| Doc drift | > 2 files with Last P20-verified > 30 days, or M-self-audit flags multiple drifts | when signaled |

## Why signal-triggered, not always-on

Premature compression kills nuance; "I'll reduce later"
never happens.  Signal trigger balances both failure modes.

## Add phase MUST end before reduce phase begins

Don't mix.  Mixing = partial reductions leaving
inconsistencies (violates P11 摘要+引用).

For constructive search-space Add, "end" means the alternatives have been
synthesized into comparable representations. Retrieval may expose known hard
constraints during Add, but retrieval alone must not become the generation
policy (`idea -> search -> reject -> repeat`).

## Task-scoped grounded-experience state

If the open-ended task materially depends on an established external
ecosystem or consumer convention, the Add phase may create one compact,
task-scoped experience anchor on an existing task/plan/acceptance/artifact
surface. Its fields are:

`PARENT_OBJECTIVE`, `CONSUMER`, `EVIDENCE_SOURCES`,
`EVIDENCE_BACKED_INVARIANTS`, `TENTATIVE_HYPOTHESES`, `NON_BINDING_VARIANTS`,
`NEGATIVE_KNOWLEDGE / ANTI_PATTERNS`,
`CURRENT_CONSTRAINT_TO_ARTIFACT_OR_ACTION_MAPPING`, and
`LAST_REANCHOR_REASON`.

The anchor records relational/function transfer, not visual or lexical
similarity. Re-consume it only at a meaningful boundary: major revision,
representation change, production-substrate change, repeated local patches,
target/reference drift, context restoration, local PASS with degraded
consumer alignment, or proposed contradiction. A re-consumption preserves
the evidence-backed mapping; re-ground and re-plan on contradiction. Do not
change a classification without new evidence, and do not create the anchor
for a fully specified/direct task.

## Reduce phase actions (per M-learn)

1. Pull all relevant intermediate state (child summaries,
   Temp snapshots, draft commits) into context
2. Run M-learn's 3 sub-actions (总结归纳 + 类比外推 + 更新知识库)
3. **Destroy intermediate state** — child summaries that
   have been consumed go to git history / Temp cleanup /
   `git rm` of intermediate files.  Destroy is a
   *postcondition* of reduce, not an afterthought.

## Anti-patterns

- **Don't** trigger reduce during add phase (premature).
- **Don't** count evidence volume as constructive expansion.
- **Don't** protect unsafe, impossible, or constraint-violating branches until
  Reduce; hard-stop exceptions interrupt Add immediately.
- **Don't** skip reduce entirely (additive without reduce
  = doc bloat, per P13 + P14).
- **Don't** silent-destroy — every destroy must be a
  `git rm` / `os.unlink()` in a commit, with the destroy
  action recorded in commit message body (auditable,
  per P17).

## Relationship to other M-* rules

- **M-task-summary**: leaf reflection (always-on, no signal)
- **M-learn**: the *mechanism* of reduce; dual-track trigger
  (structural always + signal when noticed); 3 sub-actions
- **M-context-snapshot**: storage for add-phase
- **M-add-then-reduce**: the *cycle* of which M-learn is
  the reduce arm and M-task-summary is the per-leaf pause

## See also

- `docs/OPERATING_RULES.md` — M-add-then-reduce rule
  (parent doc, brief pointer).
- `docs/SUMMARY_LIFECYCLE.md` — M-task-summary child-
  summary destroy contract (related: a specific
  destroy pattern that fits the "destroy intermediate
  state" step).
- PRINCIPLES.md P11 (摘要+引用) — the principle that
  Add-phase-then-Reduce-phase is sequential (don't mix).
- PRINCIPLES.md P13 (concise) + P14 (docs stay current) —
  the principles that justify the Reduce phase.
- PRINCIPLES.md P17 (honest reporting) — the principle
  that makes "destroy action in commit body" auditable.
