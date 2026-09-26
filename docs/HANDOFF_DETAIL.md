---
description: "L2 detail companion for HANDOFF.md — operational defaults, anti-patterns, health-check, see-also."
status: "active, detail"
last_updated: "2026-07-14"
---

# HANDOFF — Detail (L2)

> L0: L2 detail for `HANDOFF.md`.  Per P11 摘要+引用, the
> summary file is the short current entry route; this file holds
> conditional operating detail and a clearly marked historical snapshot.

---

## Operational defaults for any new agent

1. **Always apply P25 step 7 (post-modify re-apply new rules
   check)**.  After modifying any principle, check that the
   modified principle still applies to your change.

2. **Always 7-check BEFORE commit** (7 checks):
   top-down / 5-family / ordering / cross-ref / cap (R5: ≤7KB,
   R8: ≤300 lines) / L0 + R10 / inductive.

3. **Commit message MUST cite a P##** — the `hooks/commit-msg`
   hook enforces this.  Empty citations = commit rejected.

4. **Sub-tasks need M-task-summary**; parent verification is
   an empty commit citing consumed children (see
   `docs/SUMMARY_LIFECYCLE.md`).

5. **Default decision = EXECUTE when user says trust/go/next**.
   Exception: 真歧义 (real ambiguity) → state ambiguity, list
   options, pick one, apply, cite principle (per AGENTS.md
   "When in doubt").

## Sibling project awareness (per user meta-rule 2026-07-15)

Per user meta-rule "skill 项目是基于 SUA 的": SUA is upstream,
agent-reflection-skill is downstream.  This means:

### When SUA changes, skill needs attention

Every SUA commit that establishes a **new reusable pattern**
(e.g., P-n merge, M-n addition, R-n fix, 7-check discovery)
should trigger the question: "Should this pattern be lifted
to `../agent-reflection-skill/`?"

### Decision tree (when a SUA commit is "skill-extractable")

A SUA commit is skill-extractable if:

1. The commit demonstrates a **meta-cognitive pattern**
   (about how to reason, not what to do in this project).
2. The pattern has **3+ observed occurrences** (per
   M_RULE_AUTHORING 3-condition gate; not just 1 case).
3. The pattern is **framework-agnostic** (would work in
   Hermes / Claude Code / Codex, not just SUA).

### Sync protocol (lightweight, not auto)

SUA does **not** automatically update skill.  Instead:

- SUA commits cite the pattern in their commit message
  (per `"this commit demonstrates X"` parenthetical).
- The skill project maintains a "patterns pending extraction"
  list in its HANDOFF.md.
- When SUA becomes stable (parent verify batch), the agent
  reviews the "patterns pending" list and extracts those
  that meet the 3-condition gate.

This is **lightweight**: no auto-sync, no CI cron.  Just a
discipline: when SUA's project self-org (per P27) detects
a stable pattern, the next agent opens the skill project.

### Reverse direction

Skill project changes do **not** require SUA changes (skill
is downstream).  But: if skill codifies a pattern that SUA
**doesn't already have**, that's a signal to add it to SUA
too (per "skill 等 SUA").

### When NOT to sync

- When SUA change is **specific to SUA** (e.g., OKR update,
  P-n specific to SUA's tests) — NOT skill-extractable.
- When skill change is **specific to a framework** (e.g.,
  Hermes-specific invocation syntax) — irrelevant to SUA.



## Sub-project-for-experimentation pattern (per user 2026-07-15)

Per user meta-rule 2026-07-15: "如果当前经验不足以
支撑项目，可以考虑新建一个子项目用来做实验积累失败
经验".

**When to consider**: when current project lacks
experience to handle a task, or when a sub-task
becomes too complex to handle in the main project.

**Anti-pattern**: 可能陷进子任务，需要设定好目标.

**Lifecycle**: 子项目 → 经验积累完成，知道怎么处理后
→ 切回主项目.

**Codification status (2026-07-15)**: 1st occurrence
in SUA; not yet lifted to P-n (M_RULE_AUTHORING
3-condition gate; bootstrap exception applies per
user-explicit ask).  Plan: codify as M-experiment-in-
subproject段 in OPERATING_RULES.md (commit c89), then
L2 detail companion (commit c90), then parent verify
(commit c91).  See queue in this turn's planning
response.

**Related principles**: P21 (sub-project is sibling
per cross-project independence), P22 (stuck→plan
could route to sub-project), P27 (project self-org
allows sub-project for self-development).

## What NOT to do (per AGENTS.md + refactor audit findings)

- Don't create parallel doc structures (M33 in M-self-application)
- Don't commit to sibling projects from this repo (P21)
- Don't fix mechanically at 1st occurrence (P7 — wait for 3+)
- Don't write a script for what a doc could state (P23)
- Don't claim green when yellow (P17)


## Quick health check before starting work

Run this 4-item check before declaring "ready":

- [ ] Have you read this HANDOFF.md? (yes/no)
- [ ] Have you read `docs/HOW_TO_READ_GRAPH.md`?  (yes/no)
- [ ] Have you read `docs/PROJECT_STATE.md` Goal段? (yes/no)
- [ ] Have you read the L0 of `docs/PRINCIPLES.md`? (yes/no)

If yes to all 4, you can start.  If no, go back.


## See also

- `AGENTS.md` — root operating rules (load first)
- `docs/PROJECT_STATE.md` — current state snapshot
- `docs/HOW_TO_READ_GRAPH.md` — 3-step reading pattern
- `docs/SELF_ORG.md` — P27 candidate (project self-org)
- `../agent-reflection-skill/README.md` — sibling project (downstream)

## Historical onboarding snapshot (superseded 2026-09-26)

> ---
> description: "Onboarding doc for any new agent entering this project. Read this FIRST (after AGENTS.md), then follow the next-steps tree."
> status: "active"
> last_updated: "2026-08-29"
> ---
>
> # HANDOFF — Onboard a new agent into SUA
>
> > L0: Orientation for any new agent taking over this project.
> > Read this file first (after `AGENTS.md`), then follow the
> > next-steps tree at the bottom.
>
> ## What this project IS (per c73 vision sync + c52 SELF_ORG + c57 read pattern)
>
> `self-upgrade-agent` (SUA) is a **project that constrains
> agent behavior by its own documentation**, so an agent that
> follows the project's rules can operate correctly **without
> depending on the Hermes runtime**.
>
> **Three deliverable layers** (per user meta-rule 2026-07-14 + c89 M-n 11):
>
> 1. **Operational rules**: 26 P-n (P1-P30
>    minus P6 + P15 + P16 + P24) + 24 M-n
>    (M-task-summary through M-pace-continuity,
>    per c95-c134)
> 2. **Self-organization**: the project itself follows its own
>    rules (per P27 + 7-check pattern; documented in
>    `docs/HOW_TO_READ_GRAPH.md`)
> 3. **Reusable reasoning patterns**: SUA is the *origin*
>    (孵化器, hatching machine) for the `agent-reflection-skill`
>    at `../agent-reflection-skill/`.  Patterns first appear in
>    SUA, then get extracted into the skill when reusable.
>
> **Why this matters for you (the new agent)**: this is a
> **meta-rules project**.  The rules document themselves are
> the contract.  Reading and applying them IS the work.
>
> ## Quick orientation — what to read first
>
> | Order | Doc | What it gives you |
> |---|---|---|
> | 1 | `AGENTS.md` | Operating rules for agents (project entry) |
> | 2 | `docs/HOW_TO_READ_GRAPH.md` | 3-step read pattern (L0→L1→L2) |
> | 3 | `docs/PROJECT_STATE.md` | Current goal + last commits + next step |
> | 4 | `docs/PRINCIPLES.md` (top) | The 4 root axioms + 5-family framework |
> | 5 | `docs/OPERATING_RULES.md` | 9 M-* rules (workflow patterns) |
> | 6 | Below in this HANDOFF.md | Where to start working |
>
> **Don't read**: the `_DETAIL.md` companion files unless you
> need L2 depth on a specific doc.  They're reference, not
> orientation.
>
> **Conditional AI4S route**: when the task aims to discover, establish,
> falsify, or claim new scientific knowledge, load
> `docs/AI4S_RESEARCH_MODE.md` before proposing implementation. Follow its L2
> pointer only after identifying the current scientific knowledge state.
>
> **Conditional specialization route**: when a recurring task family repeatedly
> needs the same methodological steering, load
> `docs/DOMAIN_SPECIALIZATION_BOOTSTRAP.md` before proposing any new mode,
> adapter, skill, or core trigger.
>
> ## Current state (per HEAD = commit 1f1d205, c78 = 47b)
>
> - **Active goal**: Phase A validates the project-layer AI4S scientific-state
>   controller, including the bounded K3 Pre-Agent Evidence Gate, and evaluates
>   a separate domain-general specialization bootstrap. Satellite-security
>   history is regression evidence only; core promotion and Phase B are out of
>   scope.
>
> - **Commits**: 319 in mainline
> - **Last commit**: c78 = P3+P24 merge (47b, c47 plan)
> - **P-n count**: P1-P30 with P6/P15/P16/P24 excluded from the working count = 26 working principles (P30 separates construction from terminal acceptance)
> - **R-n compliance**: R5 compliant (0 violations);
>   R4/R6 conflict resolved (c75); R12 still has 1 violation
>   (knowledge-graph-seed PHILOSOPHY.md stale, sibling project)
> - **M-n status**: 21 operator rules (M-n 1-21; M-n 1-9 = M-task-summary, M-must-read, etc. from c18 + c37; M-n 10-21 = c83 M-skill-synchronize, c89 M-experiment-in-subproject, c92 M-terminology-clarity, c95 修订 L4 boundary, c97 M-layer-extension, c98 M-two-track-reasoning, c99 M-principle-reordering, c100 M-observe-think-execute, c106 M-context-freshness-check, c111 M-recursive-summary-protocol, c115 M-file-naming-convention, c116 M-agent-discoverability-check, c118 M-ask-or-infer-mark-guess) (M-task-summary, M-must-read,
>   M-context-snapshot, M-subtask-summary, M-intent-parsing,
>   M-learn, M-add-then-reduce, M-self-audit, M-self-application)
> - **MCP tools**: 5 tools available (chrome_devtools, llm_wiki,
>   zotero, sciverse, mineru) — see `docs/MCP_TOOLS.md`
> - **Skill relationship**: SUA is upstream; skill is downstream
>   — see "Sibling projects" below
>
>
> ## Sibling projects
>
> | Project | Path | Role | Status |
> |---|---|---|---|
> | `self-upgrade-agent` | this project | origin (rules + patterns + 7-check) | active, 319 commits |
> | `agent-reflection-skill` | `../agent-reflection-skill/` | downstream (skill for any agent) | early scaffold (2 commits), see plan above |
> | `knowledge-graph-seed` | `../knowledge-graph-seed/` | sibling (kg graph backend) | R12 stale, out of SUA scope |
>
> For the skill project: read `../agent-reflection-skill/README.md`
> for its scope, then `SKILL.md` for invocation contract.
>
> ## Key files at a glance
>
> | Layer | Doc |
> |---|---|
> | **L0** (entry) | `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/HOW_TO_READ_GRAPH.md` |
> | **L1** (operational) | `docs/PRINCIPLES.md`, `docs/OPERATING_RULES.md` |
> | **L2** (detail) | `docs/PRINCIPLES_FULL.md`, `docs/PRINCIPLES_DETAIL_DETAIL.md`, `docs/PRINCIPLES_DETAIL.md` (root axioms), `docs/OPERATING_RULES_DETAIL.md` |
> | **Contracts** | `docs/SUMMARY_LIFECYCLE.md` (recursive destroy contract, c62), `docs/MCP_TOOLS.md`, `docs/EXTENSIONS.md` (+ `_DETAIL.md`) |
> | **Self-ref** | `docs/SELF_ORG.md` (P27 candidate, c52), `docs/HOW_TO_READ_GRAPH.md` (3-step pattern, c57) |
>
> ## Framework-agnostic (per M-n 20)
>
> This project is designed for:
> - **Hermes** (current)
> - **Codex** (per user message)
> - **Claude Code** (per user message)
> - **Others** (auto-detected via AGENTS.md)
>
> File names avoid Hermes-specific terms (per M-n
> 19).  Future agents should be able to read this
> project without Hermes-specific knowledge.
>
> ## Detail (L2)
>
> For operational defaults, anti-patterns, health-check, and see-also cross-references, see [`HANDOFF_DETAIL.md`](HANDOFF_DETAIL.md).  Per R6, this companion is required when the summary exceeds 7 KB.
>
> Last P20-verified: 2026-09-10
