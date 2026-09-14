---
description: "Surface-scoped authority map for generic externally consumed artifacts"
status: "active"
---

# Artifact Authority Separation

> L0: Surface-scoped artifact authority; references constrain only their authorized surface, never the whole artifact.

This detail surface extends the generic [Artifact Finalization](ARTIFACT_FINALIZATION.md)
adapter. It applies when an externally consumed artifact has more than one
plausible source of authority or when a reference/source artifact might be
mistaken for the objective itself.

This is a conversation-level clarification, not a new terminal state, ledger,
or orchestrator. It does not change P30, the existing acceptance boundary, or
the direct-execution path for well-specified tasks.

## Surface-scoped authority

An artifact may have different authorities for different surfaces. A source
that is authoritative for one surface is not silently authoritative for every
other surface.

| Surface | What it controls | Evidence or source that may constrain it | What it may not override |
|---|---|---|---|
| **Semantic/content authority** | Meaning, claims, data, causal interpretation, and provenance | An independently established content source, validated result, or explicit claim boundary | Style, composition, or consumer preference cannot rewrite established semantic truth |
| **Information/composition authority** | Hierarchy, ordering, grouping, discoverability, and information flow | The actual target interface, information requirements, or fresh-reader observations | Composition similarity cannot establish semantic correctness or end-use success |
| **Style authority** | Appearance, convention, and presentation preference | An applicable style source, reference, convention, or declared preference | Style/reference similarity cannot establish semantic correctness or end-use success |
| **End-use/consumer authority** | Actual downstream compatibility, use, interpretation, operation, or acceptance | Concrete consumer-use evidence, target-interface behavior, or an authorized consumer decision | Local structure, export, or reference similarity cannot overrule concrete consumer failure; consumer feedback cannot silently rewrite established factual content |

The authority map is surface-scoped. It does not rank one source as the
universal owner of the artifact. Parent objective and actual target interface
remain primary whenever sources are compared or reconciled.

The required surface-scoped invariants are:

- style/reference similarity cannot establish semantic correctness;
- composition similarity cannot establish end-use success;
- end-use failure cannot silently rewrite established semantic truth; and
- a reference artifact is not the universal optimization target.

## Conversation activation

Before optimizing against a reference or source artifact, ask only the
questions needed to resolve a real ambiguity:

1. Which authority surface is relevant: semantic/content,
   information/composition, style, or end-use/consumer?
2. Which evidence or source holds authority for that surface?
3. What may that authority constrain in the current artifact?
4. What may it **not** override?
5. What parent objective and actual target interface remain in force?

If the source, target interface, and authority surface are unambiguous, use
the direct path. Do not require an authority map, tribunal, or extra review
cycle merely because the artifact has a source. No unnecessary authority
ceremony is required for a direct/simple artifact.

When the ambiguity is real, keep the answer local to the affected surface.
The conversation may state the map in a short handoff or review note:

```text
SURFACE: <one authority surface>
AUTHORITY SOURCE: <source or evidence>
MAY CONSTRAIN: <claims, ordering, appearance, or end-use property>
MAY NOT OVERRIDE: <the protected neighboring surface>
PARENT OBJECTIVE: <objective>
TARGET INTERFACE: <actual consumer-facing interface>
```

This note is a transient reasoning aid. It is not a new authority ledger or a
replacement for the existing acceptance and artifact-finalization records.

## Conflict boundaries

Apply the following bounded routing rules:

- A style match to a reference is style evidence only. It cannot establish
  semantic correctness.
- A composition match to a reference is composition evidence only. It cannot
  establish end-use success.
- A concrete end-use failure is evidence against the affected consumer
  acceptance dimension. It does not silently rewrite independently established
  semantic truth.
- If semantic/content evidence and style, composition, or consumer feedback
  conflict, preserve the established semantic/content result and review the
  affected non-semantic dimension through its owning authority.
- If information/composition evidence and consumer evidence conflict, hold or
  reopen the affected end-use/consumer dimension rather than treating a
  readable arrangement as proof of successful use.
- An unresolved conflict holds only the affected acceptance dimension unless
  the parent objective or actual target interface is itself shown to change.
- A reference artifact is not the universal optimization target. Similarity is
  useful only for the authority surface it is authorized to constrain.

These rules preserve the existing distinction between local verification,
regression evidence, and independent terminal acceptance. They do not turn a
surface-scoped finding into a global artifact `PASS`.

## Relationship to existing SUA behavior

The main artifact-finalization surface still owns objective recovery, freeze
classification, Add-then-Reduce, killed-defect regression, blind-first audit,
bounded reconciliation, and stopping. This detail surface only makes the
authority mapping explicit at the point where a conversation handles a
reference/source conflict.

The existing runtime may carry an optional artifact role-placement description
and route an evidenced role-placement failure through its causal retry path.
This document does not add a new runtime state or require machine validation
of authority independence. P30 remains the authority boundary for terminal
acceptance, and a local or regression result remains scoped to the evidence it
actually checks.

## Candidate evidence boundary

The accompanying domain-neutral regression family covers:

- a reference-style trap;
- a composition trap;
- semantic preservation under conflicting consumer or style feedback;
- a multi-authority artifact with four legitimate sources; and
- a direct/simple artifact with no authority ambiguity.

The expected behavioral outcomes are correct authority-source mapping,
prevention of cross-surface authority leakage, preservation of the parent
objective and end-use boundary, and no unnecessary ceremony on direct
controls. Mechanical fixture checks establish structure only. Matched fresh
agent sessions with the canonical baseline and this candidate are required to
measure live authority-separation behavior; aesthetic quality is not scored.

## References

- [Artifact Finalization](ARTIFACT_FINALIZATION.md)
- [Acceptance Protocol](ACCEPTANCE_PROTOCOL.md)
- [P30 separation of construction and acceptance](PRINCIPLES_FULL.md#p30-separation-of-construction-and-acceptance)
- [Add-then-Reduce](ADD_THEN_REDUCE.md)

Last P20-verified: 2026-09-14
