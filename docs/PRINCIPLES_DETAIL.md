---
description: "L2 routing index for extended principle semantics"
status: "routing-index"
---

# PRINCIPLES_DETAIL — Principles Detail Routing

> L0: L2 routing index.  Follow each extended principle to its canonical
> detail section; P30 lives in `PRINCIPLES_FULL.md`.

This file is the generic detail route for fresh agents.  It prevents the
historical P19 compatibility stub from being mistaken for the complete
per-principle detail source.  The canonical principle summary remains
`PRINCIPLES.md`; extended operational semantics remain in the linked detail
surfaces below.

## Canonical extended-detail routes

| Principle | Canonical detail | Why it is routed here |
|---|---|---|
| P19 — Data Flow Observability | [`PRINCIPLES_DETAIL_DETAIL.md`](PRINCIPLES_DETAIL_DETAIL.md) | Deep detail and historical compatibility route |
| P20 — Progressive Disclosure | [`PRINCIPLES_FULL.md`](PRINCIPLES_FULL.md) | Full principle text and protection context |
| P25 — Principle Modification Discipline | [`PRINCIPLES_FULL.md`](PRINCIPLES_FULL.md) | Full principle-modification safeguards |
| P26 — Fresh-Agent Discoverability | [`PRINCIPLES_FULL.md`](PRINCIPLES_FULL.md) | Full fresh-agent acceptance contract |
| P27 — Project Self-Organization | [`PRINCIPLES_FULL.md`](PRINCIPLES_FULL.md) | Full self-organization and recursion context |
| P28 — Recursion to Self | [`PRINCIPLES_FULL.md`](PRINCIPLES_FULL.md) | Full recursion and self-application context |
| P30 — Separation of Construction and Acceptance | [`PRINCIPLES_FULL.md#p30-separation-of-construction-and-acceptance`](PRINCIPLES_FULL.md#p30-separation-of-construction-and-acceptance) | Full role, state-machine, stale-state, checker, and evaluator-authority contract |

## P19 compatibility pointer

The former P19-only stub was retained as a compatibility target for older
links.  It is no longer the meaning of this generic detail route.  For P19's
deep text, use [`PRINCIPLES_DETAIL_DETAIL.md`](PRINCIPLES_DETAIL_DETAIL.md);
for P30 and other extended principles, use the canonical routes above.

### P19 — Data Flow Observability {#p19}

Older links may still resolve to this anchor.  The full P19 detail is in
[`PRINCIPLES_DETAIL_DETAIL.md`](PRINCIPLES_DETAIL_DETAIL.md).

## Fresh-agent rule

When an L1 document says “see `PRINCIPLES_DETAIL.md`”, read this routing index
and follow the row for the principle in scope.  For P30, the route must end at
the P30 section in `PRINCIPLES_FULL.md`, including:

- the implementer versus independent-evaluator authority boundary;
- `EXECUTION_SUCCESS` versus `ARTIFACT_ACCEPTANCE`;
- material-change staleness and evaluator-edit authority termination; and
- the required `LOCAL FIX VERIFIED` → `REGRESSION PASS` → independent-audit
  handoff sequence.

See [`PRINCIPLES.md`](PRINCIPLES.md) for the L0/L1 principle summary and
[`INDEX.md`](INDEX.md) for the project reading order.

Last P20-verified: 2026-09-10
