---
description: "Scientific-state controller for discovering, falsifying, and validating new knowledge"
status: "active-phase-a"
---

# AI4S Research Mode

> L0: Load before proposing implementation when a task aims to discover,
> establish, falsify, or claim new scientific knowledge.

## Activation contract

Activate this mode from the research project's entry instructions whenever
the objective is to discover, establish, falsify, or claim new scientific
knowledge. Activation depends on the objective, not words such as "deep",
"organize", "analogy", or "use SUA".

This is a **scientific knowledge-state controller**. It routes SUA's existing
Analyze/Reason/association/induction/summary, four critical-thinking
primitives, Add-then-Reduce, verification, and self-application operations.
It does not add a P-n or replace those canonical operations.

## Control loop

First declare the current state and evidence. Then execute only the operation
required to satisfy the next gate. A failed gate loops backward; it never
silently advances to implementation.

| State | Knowledge condition | Required operation before advancing |
|---|---|---|
| **K0 Mother problem** | Scientific object and success claim are explicit | Frame the mother problem and what is not being optimized. |
| **K1 Frontier change** | A new capability and invalidated old assumption are evidenced | Scan capabilities; expand possible mechanisms without defending a candidate. |
| **K2 Mechanism candidate** | Capability, constraint, mechanism, and cheap falsifier are stated | Abstract away application nouns and expose necessary causal structure. |
| **K3 Prior-art coverage** | Mechanism-level bridges cover the nearest mature theories | Schedule cross-domain analogy and strongest generic-mechanism search. |
| **K4 Novelty decision** | Role-separated tribunal leaves an exact mechanism delta | KILL, Reduce, reset/lift, or provisionally retain; record the decision. |
| **K5 Cheap falsification** | Cheapest decisive falsifier has been run | Reject or bound the mechanism before costly work. |
| **K6 Native validation** | Claim-matched native/external evidence survives adapter audit | Validate in the target system and distinguish security from natural failure. |
| **K7 Knowledge product** | Surviving claim, limits, and reopening conditions are explicit | Develop method/theory, then communicate; preserve negative knowledge too. |

## Non-negotiable transition gates

Implementation is blocked before K4 unless novelty is explicitly not the
objective. Large implementation is blocked before K5. Native-system,
external-validity, causal, and security claims are blocked before their K6
evidence gates. A template filled with plausible prose is not a passed gate.

At every candidate transition, emit:

```text
STATE: K#
CLAIM TYPE: ...
EVIDENCE: ...
TRIGGER: ...
NEXT OPERATION: ...
DECISION: ADVANCE / HOLD / REDUCE / KILL / LIFT / RESET
LEDGER UPDATE: ...
```

## Automatic routing defaults

- Mechanism-equivalent collisions schedule Reduce, abstraction lift, or
  mother-space reset; they do not schedule a renamed nearby candidate.
- Combination-only or terminology-only novelty cannot pass K4 without a
  distinct interaction mechanism.
- Adapter-dependent effects schedule native/adapter audit before external
  claims.
- Missing cheap falsifiers, claim/evidence mismatch, and rescue inflation
  move backward or KILL; they never justify a larger MVP.
- Search operates on the generic mechanism outside application vocabulary and
  stops on coverage, not a ritual number of fields.

## Diagnosis and layer decision

The repo already contains the reasoning operations, but current
`RESEARCH_USAGE.md` schedules them only by broad activity (literature,
experiment, writing), not by scientific knowledge state. The gap is therefore
activation/routing rather than missing primitives. Another P-n would duplicate
P22/P28/P29. Phase A keeps the controller in the project-layer research
adapter; user-layer placement is too local, core promotion lacks evidence, and
a separate skill would be premature.

## Detail and use

Before moving a candidate beyond K1, load
[AI4S_RESEARCH_MODE_DETAIL.md](AI4S_RESEARCH_MODE_DETAIL.md). It defines the
triggers, candidate representation, analogy coverage stop, tribunal, claim
evidence gates, KILL ledger, frontier scan, resource policy, and benchmark
contract. The summary is the router; the detail is the operating protocol.

## References

- [Research usage](RESEARCH_USAGE.md) — baseline research adapter.
- [Add then Reduce](ADD_THEN_REDUCE.md) — canonical reduction operation.
- [Critical-thinking primitives](M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md) —
  canonical adversarial operations.
- [Benchmark tasks](../benchmarks/tasks.json) — shared fixture source.

Last P20-verified: 2026-08-29
