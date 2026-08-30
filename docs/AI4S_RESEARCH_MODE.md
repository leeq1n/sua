---
description: "Scientific-state controller for discovering, falsifying, and validating new knowledge"
status: "active-project-layer"
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
| **K0 Mother problem** | Scientific object, project constraints, and success claim are explicit | Frame the mother problem and what is not being optimized. |
| **K1 Frontier change** | A supported current change or bounded future-system hypothesis exposes an old assumption | Generate problem hypotheses from assumption failure; do not treat forecasts as evidence. |
| **K2 Mechanism candidate** | Problem, constraint, generic mechanism, and cheap falsifier are stated | Use donor analogy to generate deltas, then abstract away application nouns. |
| **K3 Prior-art coverage** | Mechanism-level bridges cover the nearest mature theories | Schedule cross-domain analogy and strongest generic-mechanism search. |
| **K4 Novelty decision** | Role-separated tribunal leaves an exact mechanism delta | KILL, Reduce, reset/lift, or provisionally retain; record the decision. |
| **K5 Cheap falsification** | Cheapest decisive falsifier has been run | Reject or bound the mechanism before costly work. |
| **K6 Native validation** | Claim-matched native/external evidence survives adapter audit | Validate in the target system and distinguish security from natural failure. |
| **K7 Knowledge product** | Surviving claim, limits, and reopening conditions are explicit | Develop method/theory, then communicate; preserve negative knowledge too. |

### Pre-Agent evidence gate inside K3

`PRE_AGENT_EVIDENCE_GATE` controls whether K3 may spend an expensive Research
Agent call; it is not a new scientific state. First run bounded cheap
reconnaissance over the exact task, generic mechanism, nearest mature field,
and operational/standards reality. Check author claims against actual methods
and comparators, and reset reconnaissance after a major candidate mutation.

Escalation is allowed only when the evidence note states a precise residual
mechanism uncertainty, why another cheap search is unlikely to settle it, the
Agent's expected information gain, and the decision its result will trigger.
Otherwise KILL, Reduce, modify, or continue targeted cheap search. Adequate
bounded coverage plus a precise residual ambiguity stops reconnaissance; the
gate must not demand exhaustive search.

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

- Before narrow novelty search, run bounded constructive Add across target
  constraints, future-system deltas, broken assumptions, and mechanism-driven
  donor domains. A method remains unauthorized until a problem and generic
  mechanism survive K2/K3.
- Mechanism-equivalent collisions schedule Reduce, abstraction lift, or
  mother-space reset; they do not schedule a renamed nearby candidate.
- Candidate-family or mother-space saturation can trigger a constructive Add
  reset at a higher abstraction level. Literature saturation is not evidence
  that scientific opportunity is saturated.
- Combination-only or terminology-only novelty cannot pass K4 without a
  distinct interaction mechanism.
- Adapter-dependent effects schedule native/adapter audit before external
  claims.
- Missing cheap falsifiers, claim/evidence mismatch, and rescue inflation
  move backward or KILL; they never justify a larger MVP.
- Search operates on the generic mechanism outside application vocabulary and
  stops on coverage, not a ritual number of fields.
- A paper's "first" or "novel" language is retrieval evidence, not verified
  novelty; compare its actual method, experiment, and strongest comparator.
- A material change to the scientific object, property, threat model, output,
  mechanism, evidence, attacker, evaluation target, or contribution lane
  resets the candidate to cheap K3 reconnaissance. Parameter refinement does
  not.

## Diagnosis and layer decision

The repo already contains the reasoning operations, but current
`RESEARCH_USAGE.md` schedules them only by broad activity (literature,
experiment, writing), not by scientific knowledge state. The gap is therefore
activation/routing rather than missing primitives. Another P-n would duplicate
P22/P28/P29. Phase A keeps the controller in the project-layer research
adapter; user-layer placement is too local, core promotion lacks evidence, and
a separate skill would be premature.

AI4S adapter decision: **`AI4S_PROJECT_ADAPTER_VALIDATED`**. See the
[validation report](AI4S_PHASE_A_VALIDATION.md) for the structural evidence,
failed live A/B attempt, and remaining uncertainty.

AI4S is a Layer 2 domain adapter. The separate Layer 1 question—whether generic
SUA should propose any specialization—is governed by
[Domain Specialization Bootstrap](DOMAIN_SPECIALIZATION_BOOTSTRAP.md).
Its separate decision is **`PROPOSAL_ONLY_NEEDS_MORE_EVIDENCE`**.

## Detail and use

Beyond K1, or when repeated Reduce may require constructive Add reset, load
[AI4S_RESEARCH_MODE_DETAIL.md](AI4S_RESEARCH_MODE_DETAIL.md). It defines the
discovery loop, triggers, candidate gate, analogy stop, tribunal, evidence
gates and ledger, resource policy, and benchmark contract.

## References

- [Research usage](RESEARCH_USAGE.md) — baseline research adapter.
- [Add then Reduce](ADD_THEN_REDUCE.md) — canonical reduction operation.
- [Critical-thinking primitives](M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md) —
  canonical adversarial operations.
- [Benchmark tasks](../benchmarks/tasks.json) — shared fixture source.

Last P20-verified: 2026-08-30
