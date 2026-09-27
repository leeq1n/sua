> L0: Cross-runtime entry pointer for loading SUA from a runtime with skill support.
# Cross-Runtime Skill Bridge

> L1: Use a small `SKILL.md` to route an agent to SUA's canonical files when
> the runtime does not load this repository's entry documents directly.

## Use and boundary

The bridge is a pointer, not a copy of SUA's rules. Give the runtime read access
to this repository, then load `core-layer/AGENTS_CORE.md`, `AGENTS.md`, and the
relevant documents through `docs/INDEX.md`. Follow `docs/HANDOFF.md` and
`docs/PROJECT_STATE.md` for current authority. If the runtime cannot read
these files, report that the full SUA contract was not loaded.

## Thin skill example

Replace `<path-to-sua>` with the repository location when installing this
example. The exact installation mechanism is runtime-specific.

```markdown
---
name: sua-bridge
description: Load SUA repository discipline when the user explicitly requests it.
---
# SUA bridge

Read `<path-to-sua>/core-layer/AGENTS_CORE.md` first, then
`<path-to-sua>/AGENTS.md`. Follow their reading route and consult only the
project documents relevant to the active task. If either entry file is
unavailable, say that SUA could not be fully loaded.

## LOOP-BREAKER GATE (repeated user rejection)

When the user is the acceptance authority for a user-facing criterion and
explicitly says the same core criterion remains unmet, that rejection
invalidates any prior local `PASS`. Treat that message as an external failure
signal. Before another retry, record `PARENT_OBJECTIVE`,
`FAILED_ACCEPTANCE_CRITERION`, `FAILURE_CLASS`,
`REPRESENTATION_FAMILY`, `PRODUCTION_SUBSTRATE`, `CAUSAL_LAYER_CHANGED`, and
`CAUSAL_DELTA`. A retry with no causal delta is not allowed: stop local polish,
preserve negative knowledge, and trigger a controller-level replan. Escalate
from local parameter → implementation → substrate/tool → representation/problem
framing → artifact role/placement → parent objective/acceptance criterion.
`REPRESENTATION_FAMILY` is the canonical representation identity;
`REPRESENTATION_VARIANT` is optional metadata and a variant rename alone does
not create a structural delta. Omitted optional fields do not count as changed.
`max_retries` is only a quantity ceiling: after a failed attempt, missing
`RetryState` or `RetryProposal` stops the controller before a second attempt
with `RETRY_CONTEXT_REQUIRED`.
See `docs/M_ACCEPTANCE_PROTOCOL_DETAIL.md` for the canonical detail.
The executable state carrier and decision gate are `src/retry_gate.py`, and
the existing `src/v4_loop.Loop` controller is the retry execution owner.

For a material artifact, local execution or regression evidence is not
terminal acceptance. Follow P30 in `docs/PRINCIPLES_FULL.md`: the implementer
prepares evidence, while an independent fresh-state evaluator makes the
terminal decision for the exact artifact.
```

## When to use which entry point

| Situation | Entry |
|---|---|
| Agent can read this repository directly | `core-layer/AGENTS_CORE.md` then `AGENTS.md` |
| Runtime loads `SKILL.md` on request | Thin bridge above, pointing to this repository |
| Stateless session without repository access | Supply the needed source files; do not claim the full contract was loaded |
| CI or pipeline | Repository hooks and explicit verification commands |

## See also

- [README.md](../README.md) — repository onboarding
- [INDEX.md](INDEX.md) — current document map
- [PRINCIPLES_FULL.md](PRINCIPLES_FULL.md) — P30 authority boundary
- [M_ACCEPTANCE_PROTOCOL_DETAIL.md](M_ACCEPTANCE_PROTOCOL_DETAIL.md) — retry gate detail

Last P20-verified: 2026-09-28
