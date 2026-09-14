---
description: "Bounded final-promotion gate for evidence-bearing artifacts"
status: "active"
---

# Artifact Finalization

> L0: Before promoting an externally consumed artifact, recover its real
> objective, reduce historical residue, and obtain one blind-first fresh audit.

This project-layer adapter applies to publications, software releases,
benchmark or dataset releases, technical reports, slide decks, and
reproducibility bundles. It orchestrates existing P5/P7/P17/P18/P22/P26,
P30, Add-Then-Reduce, critical-thinking, negative-knowledge, and acceptance
mechanisms. P30 supplies the role boundary: local verification and regression
evidence do not authorize the implementer to issue terminal acceptance. This
adapter does not require a mandatory multi-agent system.

## Trigger and boundary

Run this gate before final promotion when at least one signal exists:

- repeated local repairs or implementation overrides have accumulated;
- an exact measurable target has become a de facto objective;
- a major artifact mutation occurred after an earlier acceptance;
- a broad edit could reintroduce a stable killed-defect class; or
- the same context created the artifact and supplied all purportedly
  independent validation views.

Ordinary low-risk edits still use ordinary acceptance. Run this gate once per
final-promotion state, and again only after a major artifact mutation or a
finding that materially changes the artifact.

## 1. Recover the real objective and classify freezes

Write the target interface, intended evaluator, and true objective before
reading patch rationales. For every frozen clause that affects promotion,
classify its semantic basis:

| Class | Treatment at finalization |
|---|---|
| **Evidence-backed invariant** | Preserve. Preregistered conditions, measured outcomes, provenance, threat boundaries, causal scope, and claim limits must not be changed after outcome inspection. This gate cannot rescue a failed result or reinterpret evidence post hoc. |
| **Publication or interface decision** | Treat as provisionally stable. Reconsider only when the current artifact or official interface shows that the decision obscures meaning or usability; do not change the evidence it communicates. |
| **Implementation convenience** | Keep challengeable. A workaround, override, counter, wrapper, or local patch does not become an invariant merely because prior checks froze it. |

If a clause mixes classes, preserve the evidence-bearing portion and isolate
the presentation or implementation portion before considering a change. When
classification is uncertain, hold promotion rather than weakening the
scientific or evidentiary boundary.

Replace exact proxy targets with constraints only when an external
specification truly requires them. Otherwise evaluate them against the true
objective: a checker PASS count, exact size/count, or zero local whitespace is
evidence only to the extent that it predicts interface fitness.

## 2. Reduce historical implementation residue

Before adding another compensating patch, compare the current artifact with a
minimal semantic source or default implementation under the official target
interface. Ask which accumulated controls remain causally necessary now.
Prefer to remove obsolete controls, then re-verify the whole artifact. Retain
an unusual control only with a current functional reason, not its historical
rationale or sunk cost.

This is a bounded Add-Then-Reduce pass, not a rewrite. It does not authorize
changes to evidence, claims, public behavior, or compatibility outside the
finalization objective.

## 3. Regress stable killed-defect classes

Carry forward only stable and recurrent defect classes whose reintroduction
would violate evidence, the target interface, or an established quality
boundary. Encode them in the existing validation contract, decision record,
negative-knowledge record, or regression suite nearest the artifact. Do not
create a second ledger or preserve every stylistic preference.

After a broad edit, test the class and its close semantic variants, not only
one literal phrase. A killed defect may reopen only when the governing
objective, external specification, or evidence changes and that change is
recorded.

## 4. Run a blind-first fresh audit

Give the auditor only:

- the current artifact;
- its true objective, target interface, and intended evaluator;
- evidence-backed invariants and claim boundaries; and
- the official external specification or template, when applicable.

Initially withhold patch rationales, previous PASS reports, prior review
personas, and explanations for unusual decisions. Record observations first;
then reconcile them with history and evidence. Under P30, the evaluator must
be a role that did not materially implement the artifact state being accepted.
Only the independent evaluator may issue terminal acceptance. Under P30-A3,
that evaluator must be fresh and independent of material implementation.
A different agent instance is optional as a mechanism, but a fresh evaluator
independent of material implementation is mandatory. A separate agent
instance or human evaluator is preferred when practical; the requirement is
epistemic independence plus blind-first information control, not agent count
alone.

The implementer may report `LOCAL FIX VERIFIED` and `REGRESSION PASS`, then
must hand off with `IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT`.
The handoff must carry the computed current `ARTIFACT_IDENTITY`, clean/dirty
state, prior acceptance/material-change state, regression status, and
evaluator-edit state. The independent evaluator owns the terminal decision by
producing an external record outside the candidate repository. The repository
verifier may confirm that the record matches the exact unchanged clean
artifact, but it cannot create the decision or prove that the evaluator was
genuinely independent.

### P30-A4 post-acceptance liveness

Once the external evaluator has produced the P30-A3 record, the repository's
only post-acceptance entry point is
`finalize_accepted_artifact(external_acceptance_record)` (also exposed as
`--finalize-accepted-artifact`). It consumes the record from outside the
candidate repository, delegates schema/role/decision/identity checks to the
existing verifier, recomputes the clean current identity immediately before
finalization, and rejects any drift or dirty state.

Successful finalization writes one atomic JSON ledger outside the candidate
repository with `ACCEPTED_FROZEN` as its canonical state. The ledger records
the exact accepted commit identity and the reference to the external record;
it does not change the audited tree, create a terminal decision, or claim
`repository_proved_independence = true`. A failed verification or failed
ledger write leaves no new accepted/frozen marker. The old candidate APIs and
automatic loops remain nonterminal and candidate-only.

P30-A3 has two enforcement layers:

- **Machine-enforceable:** computed artifact identity, clean-state requirement,
  drift/staleness, nonterminal local/checker status, external-record schema
  and identity match, and blocked legacy material-finalization paths.
- **Governance/orchestrator-enforced:** fresh evaluator identity, absence of
  hidden authorship, artifact-first ordering, first-pass freezing, and
  independent production of the external report.

The shared `p30_acceptance.py` boundary fails closed when the record is
missing, malformed, stale, dirty, contradictory, or mismatched. It does not
pretend that caller flags prove the governance layer.

Ask: if an informed evaluator encountered only the current artifact, would its
structure and behavior be natural, self-consistent, and appropriate for the
target interface? This is not aesthetic conformity. Preserve every
functionally justified exception and record why it is necessary.

## 5. Reconcile once, then stop

Classify each fresh finding as:

- evidence/invariant conflict: hold promotion and return to the owning
  evidence process;
- interface or implementation residue: make the smallest correction, remove
  superseded patches, and re-run affected checks;
- functionally justified exception: retain it with current evidence; or
- preference only: reject it.

Stop when one blind-first audit has been reconciled, required regressions pass,
and no unresolved finding threatens evidence or interface fitness. Do not
start another polish cycle without a new material finding. The normal outcome
is promote, hold, or return to the existing owning process; these are not new
SUA decision states.

If the evaluator materially edits the artifact during audit, mark
`EVALUATOR_AUTHORITY_VALID = NO`, terminate that evaluator's authority, mark
the resulting artifact state stale, and return to implementation flow.  The
same evaluator cannot issue the terminal decision for that edited state.

## Mechanism-general examples

- **Software release:** a pinned configuration and several compatibility
  shims pass local tests, but the pin is not externally required. Recover the
  supported-platform objective, remove obsolete shims, regress a previously
  fixed insecure default, and inspect a clean installation before release.
- **Benchmark release:** a fixed row count became a proxy while exclusions and
  metadata changed. Preserve measured records and provenance, challenge the
  presentation count, regress a previously removed leakage class, and audit
  the package without curation history.

## Evidence level

Repository tests validate structure, ordering, scenario coverage, and
discoverability. They do not prove that a live agent will reliably perform a
high-quality blind audit. Until blinded treatment trials are run, report
`STRUCTURALLY_VALIDATED_BEHAVIOR_PENDING`.

## References

- [Acceptance protocol](ACCEPTANCE_PROTOCOL.md)
- [Add then Reduce](ADD_THEN_REDUCE.md)
- [Critical-thinking primitives](M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md)
- [Artifact authority separation](ARTIFACT_FINALIZATION_DETAIL.md)
- [Working principles](PRINCIPLES.md)

Last P20-verified: 2026-09-10
