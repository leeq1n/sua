> L0: 跨运行时 skill 桥接 (Agent Skills SKILL.md) — 给非标准 agent runtime 的入口.
# Cross-Runtime Skill Bridge

> L1: Supplementary guide for using SUA in **agent runtimes other
> than the canonical "Read 6 files" onboarding**. This document
> augments `README.md` (which assumes an agent that can directly
> read the SUA repository); it does NOT replace the canonical
> workflow.

## Why this document exists

`README.md` §"Quick start (new agent)" assumes an agent that can
read SUA files in-place and follow a 6-step onboarding. This works
for code-repo-integrated agents but is awkward in:

- **Cursor / Claude Code / Codex / Antigravity** — users want a
  portable skill format, not a directory read
- **Hermes / other runtimes** — may have a `SKILL.md` convention
  (per Agent Skills open standard, 2025-12-18)
- **Browser-based or stateless sessions** — cannot persist "Read
  AGENTS.md" between turns

This bridge gives those users a one-line entry point that loads
SUA discipline without changing the canonical 6-step workflow.

## Quick bridge (for non-canonical runtimes)

If your agent supports the Agent Skills open standard
(`SKILL.md` with YAML frontmatter), you can create a thin
bridge skill that cross-references SUA:

```yaml
---
name: sua-bridge
description: |
  Bridge to Self-Upgrade Agent (SUA) discipline — 4-step
  preflight + 5-step acceptance + Hard rules.
  Auto-load: when user says "用 sua 规范" / "按 SUA 约束" /
  "load sua" / "self-upgrade agent discipline" / "agent
  constraints".
  Universal format: works in Hermes / Codex / Claude Code /
  Cursor / Antigravity / GitHub Copilot.
  Source: <path-to-this-repo>  # point at SUA's own files
version: 1.0.0
---

# SUA Bridge (loaded on user request)

You are now governed by SUA discipline. Apply these rules to
yourself (per P-28 self-application).

## 4-STEP PREFLIGHT (non-trivial tasks)

1. **M-n 28 plan** — 5W1H + MECE Issue Tree
2. **P-130 search** — ≥3 external queries + ≥1 community cite
3. **1-line lesson** — one-sentence expected learning
4. **M-n 16 observe** — Pre-mortem Q1-Q7

## 5-STEP REGRESSION EVIDENCE (before implementation handoff)

```
[Build]    file paths + content
[Content]  1-line description
[Execution] EXECUTION_SUCCESS | EXECUTION_FAILED
[Regression] REGRESSION PASS | REGRESSION INCOMPLETE | NOT RUN
[Artifact] artifact identity: commit/hash/version/state id
[Role]     IMPLEMENTER | INDEPENDENT_EVALUATOR | UNSPECIFIED
[Acceptance] NOT ISSUED | ACCEPTANCE BLOCKED / INDEPENDENT AUDIT REQUIRED
[Handoff]  IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT
[Caveats]  scope limits / gaps / ad-hoc verification
[Cite]     P## / M-n from PRINCIPLES.md / OPERATING_RULES.md
```

`EXECUTION_SUCCESS` and `REGRESSION PASS` are evidence states only.  They
must not be renamed or wrapped as artifact acceptance.  A bridge runtime must
not infer evaluator independence from a model name, new session, runtime, or
role label alone. For a material artifact, the fresh evaluator must produce a
machine-readable P30 record outside the candidate repository. Repository
tooling may verify the record's schema, exact clean artifact identity, and
absence of drift, returning `EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT`;
it must not create `INDEPENDENT ACCEPTANCE PASS` or claim to prove evaluator
independence from self-attested fields.

P30-A3 trust boundary:

- machine checks cover identity, clean state, drift/staleness, schema, and
  nonterminal local evidence;
- the human/orchestrator owns the governance facts of fresh identity, hidden
  authorship, artifact-first ordering, first-pass freeze, and independent
  production of the record.

P30 proportionality may keep trivial non-semantic work outside a formal
terminal workflow; a caller-declared non-material flag cannot create acceptance.

## HARD RULES (binding)

- P5  test before commit
- P11 摘要+引用 (no replicate)
- P14 docs current
- P17 老实说 (no fake green)
- P20 README ≤ 7KB
- P22 stuck → plan
- P30 constructor cannot be the final acceptor; checker output is regression evidence only, and external records are verified rather than created
- P-130 external search first

## Coverage caveat (per AGENTS.md line 80)

60-70% coverage is realistic. LLM attention decay = some turns
will forget. Re-read this skill on confusion.

## Always cross-ref SUA source (per P-11 mirror-not-replicate)

For full SUA discipline, defer to the canonical source:

- **Core rules** (~6KB cache-stable): `core-layer/AGENTS_CORE.md`
- **Operating rules**: `docs/OPERATING_RULES.md`
- **Principles**: `docs/PRINCIPLES.md`
- **Self-application protocol**: `core-layer/protocols/M_SELF_APPLICATION.md`
  (if present)

Do NOT replicate SUA full content into the bridge — always
cross-reference back to the source of truth.
```

## When to use which entry point

| Runtime | Use | Why |
|---|---|---|
| Code repo agent (claude code, etc.) | `README.md` 6-step onboarding | Direct file read works |
| Hermes / Cursor / Codex / Antigravity | This bridge as `SKILL.md` | Skill auto-load mechanism |
| Stateless / browser session | This bridge as system-prompt injection | No persistence between turns |
| CI / pipeline automation | `commit-msg` + `pre-commit` hooks | Mechanical enforcement |

## Why this is a supplement, not a replacement

The 6-step onboarding in `README.md` is the **canonical** SUA
workflow — it is the workflow that SUA itself uses and validates.
The bridge is a **convenience layer** for runtimes that cannot
follow the canonical 6-step pattern. Both paths converge on the
same discipline; the bridge just provides a shorter entry point.

## Self-Contained Mandate (per P-14)

This bridge file references SUA but does not include SUA's full
content. SUA is the source of truth; the bridge is a thin
pointer. Per P-11 mirror-not-replicate, do not duplicate SUA
content into this file.

## See also

- `README.md` — canonical 6-step onboarding
- `AGENTS.md` — operating rules
- `core-layer/AGENTS_CORE.md` — cache-stable core
- Agent Skills open standard: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>

Last P20-verified: 2026-09-10
