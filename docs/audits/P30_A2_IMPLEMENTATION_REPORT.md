---
description: "P30-A2 non-acceptance implementation handoff"
status: "implementation-only"
artifact_type: "implementation handoff"
---

# P30-A2 Implementation Report — Non-Acceptance Handoff

## Authority, scope, and boundary

This report records the bounded implementation requested by the independent
P30-A2 audit. It is an implementation handoff, not an acceptance report and
not a terminal decision.

- Audit baseline: `e6594f83e132b29274bff279e627370592500350`
- Implementation commit: `8392a32b78ee7fce8b61e388ba76cf8eadc6f47a`
- Branch: `main`
- Push: not performed
- Implementer role: `IMPLEMENTER`
- Material artifact: `YES`
- Current artifact state: `READY_FOR_INDEPENDENT_AUDIT`
- Manuscript scope: none
- J28-B scope: none

The current manuscript status remains:
`TARGETED SCIENTIFIC CORRECTIONS COMPLETE / READY FOR INDEPENDENT J28-B`.
No manuscript, research claim, experiment, threshold, seed, HIL/NOS3/cFS
runtime claim, or broader P30 policy was changed in this correction.

## B1 — Legacy completion paths are nonterminal

The old M-n29/M-n31 and cross-runtime completion language was changed so that
implementation completion, checker output, and execution success are
explicitly nonterminal evidence. The active handoff language now uses
`REGRESSION PASS`, `EXECUTION_SUCCESS`, and
`READY_FOR_INDEPENDENT_AUDIT`; it does not convert those states into artifact
acceptance.

The following surfaces now preserve the construction/acceptance boundary:

- `AGENTS.md` and `AGENTS_DETAIL.md` describe implementation handoff and
  independent audit as separate stages.
- `docs/M_TASK_LIFECYCLE_DETAIL.md`,
  `docs/M_ACCEPTANCE_PROTOCOL_DETAIL.md`, and
  `docs/OPERATING_RULES_DETAIL.md` separate the implementation handoff from
  independent acceptance.
- `docs/CROSS_RUNTIME_SKILL_BRIDGE.md` distinguishes execution evidence,
  regression evidence, and acceptance evidence; no role or status is inferred
  from a generic checker result.
- Historical examples that used completion-like acceptance wording are marked
  as historical and cannot serve as the current terminal path.

## M1 — Role, artifact, and material-change identity are active

`agent-tools/scripts/p30_acceptance.py` is the shared fail-closed boundary for
the active acceptance state machine. It tracks, explicitly rather than by
convention:

- current role;
- material-artifact status;
- artifact identity;
- current artifact state;
- prior acceptance state and prior artifact identity;
- local-fix and regression evidence states;
- independent-audit state;
- artifact-first and first-pass-frozen markers;
- evaluator material edits and evaluator authority validity; and
- execution status, artifact acceptance, and terminal-acceptance status as
  separate fields.

The active scripts and hooks call this boundary for nonterminal checks. The
technical entry points now include `eval_before.py`, `verify_after.py`,
`release_audit.py`, `self_health_check.py`, `m_n29_5step.py`,
`run_acceptance.sh`, `pre-commit`, and `pre-push`. A request for
`--terminal-acceptance` is rejected for the implementer path and by the shell
regression entry point. A checker `PASS` is therefore not sufficient to issue
artifact acceptance.

## M2 — Stale acceptance and evaluator-authority reset

The state transitions are explicit and fail closed:

1. A local fix may be recorded as regression evidence and may move the
   artifact to `READY_FOR_INDEPENDENT_AUDIT`.
2. A material modification requires the prior acceptance state and prior
   artifact identity to be recorded; it moves the prior state to
   `STALE_AFTER_MATERIAL_CHANGE` and requires a new independent audit.
3. An evaluator material edit terminates evaluator authority, clears the
   effective role to `UNSPECIFIED`, marks the artifact stale, and requires a
   new independent audit.
4. Terminal artifact acceptance is issuable only when the record explicitly
   identifies a complete independent evaluator, a matching current identity,
   a completed regression record, artifact-first/first-pass-frozen evidence,
   no evaluator material edit, and valid evaluator authority.
5. Missing, unspecified, contradictory, stale, or mismatched state blocks
   terminal acceptance rather than being repaired by inference or relabeling.

The generic acceptance report schema in `docs/ACCEPTANCE_PROTOCOL.md` and the
handoff requirements in `docs/ARTIFACT_FINALIZATION.md` expose these fields so
that a later evaluator can reconstruct the authority boundary from the
artifact itself.

## M3 — P30 discoverability and first-read routing

`docs/PRINCIPLES_DETAIL.md` is now an L2 routing index rather than a P19-only
stub. It routes the P30 construction/acceptance principle to the anchored
section in `docs/PRINCIPLES_FULL.md`, while preserving the existing P19 anchor
needed by legacy `docs/SKILLS.md` navigation.

The P30 route is also surfaced through `core-layer/AGENTS_CORE.md`,
`docs/HOW_TO_READ_GRAPH.md`, and `docs/INDEX.md`. The structural validator
includes `p30_acceptance.py` as a critical active path. This closes the
fresh-agent discoverability gap without changing the principle beyond the
requested routing and active-boundary correction.

## Same-class bypass recheck

During the active-path recheck, generic completion/acceptance-like output was
also found in the release-audit, self-health, and hook/report surfaces. These
were brought under the same boundary: they now emit technical regression
evidence and an implementation handoff, not terminal artifact acceptance.
The cross-runtime shell entry point likewise rejects a direct terminal
acceptance request. No unrelated governance or research-policy surface was
expanded.

## Bounded regression evidence

The following checks were run against the implementation commit:

- Focused construction/acceptance, artifact-finalization,
  constructive-control, cross-repository-audit, and canonicalization suites:
  `56 passed`.
- Cross-reference validation: all documented cross-references valid.
- Structural validation: all `24` critical paths present.
- Python compilation of the changed active scripts: completed successfully.
- Shell syntax validation for `run_acceptance.sh`, `pre-commit`, and
  `pre-push`: completed successfully.
- `eval_before.py`: completed with the repository's three existing sibling
  `VERIFICATION.md` warnings; no new acceptance was issued.
- `m_n29_5step.py`: completed as structural/regression evidence with an
  implementation handoff.
- Shared-boundary CLI: implementer terminal-acceptance request rejected with
  exit code `2`; a valid independent-evaluator record remains the only
  terminal-acceptance route.
- `run_acceptance.sh --terminal-acceptance`: rejected with exit code `2`.
- `verify_after.py`: exited `0` and reported nonterminal regression evidence;
  its only incomplete condition was the dirty working tree caused by the
  preserved user-owned audit files.

These are bounded structural and behavioral-contract checks. They are not a
fresh independent audit and do not constitute live agent-behavior evidence.

## Artifact identity and residual risks

The implementation artifact is identified by commit
`8392a32b78ee7fce8b61e388ba76cf8eadc6f47a` on `main`. The four pre-existing
user-owned audit reports under `docs/audits/` were preserved and were not
modified or staged by the implementation commit. This report is the
non-acceptance handoff artifact to be committed separately.

Residual conditions intentionally left for the fresh independent audit:

- No independent evaluator has reviewed this implementation in the current
  cycle.
- The implementer has not and cannot claim terminal acceptance for this
  material artifact.
- The focused checks exercise the explicit state boundary but do not replace
  an artifact-first/open-world audit of all active completion paths.
- The full repository test suite was not run in this bounded correction.
- The three existing sibling `VERIFICATION.md` warnings remain and are not
  part of this P30 correction.
- The working tree may remain dirty because the user-owned independent audit
  reports must remain untouched.

## Required implementation flags

```text
BASE_COMMIT: e6594f83e132b29274bff279e627370592500350
NEW_COMMIT: 8392a32b78ee7fce8b61e388ba76cf8eadc6f47a

B1_LEGACY_TERMINAL_BYPASS_CLOSED: YES
M1_ROLE_AND_ARTIFACT_IDENTITY_TRACKING: YES
M2_STALE_ACCEPTANCE_AND_AUTHORITY_RESET: YES
M3_P30_ROUTE_AND_FIRST_READ_DISCOVERABILITY: YES
SAME_CLASS_BYPASS_RECHECKED: YES
CANONICAL_SUA_TERMINAL_ACCEPTANCE_CLAIMED: NO
MANUSCRIPT_MODIFIED: NO
J28B_EXECUTED: NO
PUSHED: NO
```

This report is implementation-only. The required next authority step is a
fresh independent audit from the implementation identity above.

P30 CORRECTIONS IMPLEMENTED / READY FOR FRESH INDEPENDENT AUDIT
