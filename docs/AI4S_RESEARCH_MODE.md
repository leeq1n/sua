---
description: "Scientific-state controller for discovering, falsifying, and validating new knowledge"
status: "phase-a-diagnosis"
---

# AI4S Research Mode

> L0: Load before proposing implementation when a task aims to discover,
> establish, falsify, or claim new scientific knowledge.
>
> Phase A status: diagnosis recorded; controller and regression evidence are
> not yet complete.

## Phase A diagnosis

SUA already supplies the required reasoning operations: constructive and
adversarial primitives, Add-then-Reduce, verification, self-audit, and
self-application.  `RESEARCH_USAGE.md` maps broad research activities to
tools, but it does not represent the current scientific knowledge state or
define transition-blocking epistemic triggers.  A fresh agent can therefore
perform the operations when explicitly requested without reliably deciding
when a mechanism collision, adapter-dependent effect, weak claim, or failed
branch must schedule them.

The observed AI4S gap is primarily **activation and routing**, not a missing
reasoning primitive.  The Phase A hypothesis is that a project-layer research
adapter can make those decisions explicit enough to change fresh-agent
behavior without adding a principle or modifying the core layer.

## Five diagnosis questions

| Question | Finding | Evidence in the current repo |
|---|---|---|
| Is the capability present but undiscoverable? | Partly. Individual operations are discoverable, but their scientific trigger conditions are not. | `PRINCIPLES.md`, `OPERATING_RULES.md`, and the critical-thinking detail define operations; `RESEARCH_USAGE.md` lists stages and tools. |
| Is it present only informally? | The scientific scheduling logic is informal. | No current document defines a scientific-state transition gate, combination-only novelty block, native/adapter audit, or repeated-collision branch reset. |
| Is the problem routing rather than primitives? | Yes, as the leading diagnosis. | Existing Analyze/Reason/analogy/induction/summary, adversarial reasoning, Reduce, verification, and recursion cover the required operations. |
| Would another P-n duplicate existing principles? | Yes. | P22 already governs replanning; P28/P29 govern recursive application and reduction; P7 rejects an unevidenced new rule. |
| Where should the fix live? | In a project-layer research adapter for Phase A. | It is reusable SUA project knowledge but not yet stable enough for the core; user layer is too local, and a separate skill is out of scope. |

## Falsifiable Phase A hypothesis

Compared with current `RESEARCH_USAGE.md`, the treatment must let a fresh
agent, without user prompts such as "think deeper" or "use SUA":

1. identify the scientific knowledge state;
2. schedule mechanism-level cross-domain search;
3. block combination-only or renamed novelty;
4. trigger Reduce, abstraction lift, or branch reset after collisions;
5. require a cheap falsifier before expensive implementation;
6. request native validation when adapters may manufacture evidence; and
7. persist KILL knowledge so renamed candidates do not immediately revive.

Phase A fails if these outcomes require broad redesign, core edits, or a
second benchmark framework.

## Scope and acceptance boundary

- **Allowed layer**: project docs, research adapter, benchmark fixtures,
  transparent rubrics, validators, tests, and current-state routing.
- **Excluded**: core-layer edits, new P-n, hook enforcement, continuous
  frontier crawlers, a new skill repository, and renewed satellite research.
- **Evidence rule**: deterministic checks validate structure and routing;
  scientific judgment remains rubric-scored and must not be reported as a
  deterministic behavioral gain without a controlled run.

## References

- [Research usage](RESEARCH_USAGE.md) — current baseline research adapter.
- [Operating rules](OPERATING_RULES.md) — existing operations being routed.
- [Add then Reduce](ADD_THEN_REDUCE.md) — canonical reduction operation.
- [Critical-thinking primitives](M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md) —
  canonical adversarial operations.
- [Benchmark tasks](../benchmarks/tasks.json) — existing benchmark convention
  to extend, not replace.

Last P20-verified: 2026-08-29
