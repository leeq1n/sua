# P30-A4 Implementation Report

Status: `P30-A4 IMPLEMENTATION COMPLETE / READY FOR FRESH INDEPENDENT AUDIT`

This is an implementation-only handoff. It is not an independent acceptance
decision and does not claim that the repository proved evaluator independence.

## Scope and commits

- `BASE_COMMIT`: `2c3b541bb7e86d6ec890a9a9cda2b812f2434869`
- `NEW_IMPLEMENTATION_COMMIT`: `1ba8c650a9eb9146e4d437a31019771557829cc7`
- `OPTIONAL_HANDOFF_COMMIT`: this report's commit; exact hash is supplied in
  the final task handoff because a commit cannot contain its own hash.
- No push was performed.
- The four pre-existing untracked audit files were not modified or staged.

## Chosen canonical finalization semantics

P30-A3 had already disabled the legacy candidate-to-`core/` promotion paths,
so the A4 change does not reopen `promote_candidate`, `promote_patch`, or
automatic promotion. The single canonical post-acceptance representation is
one external JSON finalization ledger with:

- `accepted_artifact_identity`
- `external_acceptance_record_reference`
- `external_decision`
- `finalization_timestamp`
- `finalization_action`
- `current_canonical_state`

The canonical state is `ACCEPTED_FROZEN`. The ledger is outside the candidate
repository, so recording it does not change the audited tree or HEAD. A
conflicting existing ledger cannot be overwritten; an identical existing
finalization is idempotently recognized.

## Executable post-acceptance path

The dedicated function is:

```text
finalize_accepted_artifact(
    external_acceptance_record,
    repo=<candidate-repository>,
    record_path=<external-record>,
    finalization_ledger=<external-ledger>,
)
```

The equivalent command is:

```text
python agent-tools/scripts/p30_acceptance.py \
  --finalize-accepted-artifact \
  --repo <candidate-repository> \
  --external-record <external-audit-record.json> \
  --finalization-ledger <external-finalization-ledger.json>
```

The finalizer consumes an already-existing external P30-A3 record. It reuses
`verify_external_acceptance_record`, recomputes the current identity before
verification and again immediately before finalization, requires a clean
committed artifact, and requires exact identity equality. It records the
external decision as consumed; it does not create `INDEPENDENT ACCEPTANCE
PASS` and always reports `repository_proved_independence: false`.

## Identity preservation and atomicity

The audited clean commit remains the accepted artifact identity. No file in
the candidate tree is edited and no new candidate commit is created. After
all verifier and current-identity gates pass, the ledger is written to a
temporary file in its existing external directory, flushed, fsynced, and
atomically replaced into place. Verification failures, conflicting existing
state, invalid ledger paths, or write failures return a rejected result and do
not create a new accepted/frozen marker.

## Required positive liveness evidence

The new A4 behavioral suite proves:

1. exact clean artifact A plus a matching valid external record reaches a
   durable `ACCEPTED_FROZEN` ledger;
2. the ledger identity equals the exact audited identity A; and
3. HEAD, the artifact bytes, and the candidate working tree remain unchanged.

The explicit CLI path is also exercised successfully.

## Required negative controls

The A4 suite verifies no finalization for missing records, fabricated or
mismatched identities, dirty state, artifact drift after audit,
checker/regression-only decisions, implementer/self-attested evaluator fields,
non-material caller flags, evaluator material-edit status, records inside the
candidate repository, missing external ledger directories, and conflicting
existing finalization state. Failed paths leave no new canonical marker.

## Validation evidence

- P30-A4 behavioral suite: **16 passed**.
- P30/A3 trust-boundary, artifact-finalization, switcher, CLI, and stable-run
  focused suite: **117 passed**.
- Adjacent persistence/features/planner persistence suite: **91 passed, 1
  skipped**.
- Structure validation: **24/24 critical paths present**.
- Link validation: **all cross-references valid**.
- Changed Python sources and tests: **compile passed**.
- Separate existing planner/harness smoke suite: **15 passed, 2 failed**.
  Both failures are the known clean-planner harness condition reporting
  `0.0`/`8` harness tests; this P30-A4 change does not modify planner or
  harness code.

## Required implementation flags

```text
POST_ACCEPTANCE_WORKFLOW_IMPLEMENTED: YES
EXTERNAL_RECORD_CONSUMED_BY_FINALIZER: YES
EXACT_CURRENT_IDENTITY_RECOMPUTED: YES
EXTERNAL_RECORD_IDENTITY_MATCH_REQUIRED: YES

DIRTY_FINALIZATION_BLOCKED: YES
DRIFTED_RECORD_FINALIZATION_BLOCKED: YES
MISSING_RECORD_FINALIZATION_BLOCKED: YES

FINALIZATION_PRESERVES_AUDITED_IDENTITY: YES
CANONICAL_ACCEPTED_STATE_DURABLE: YES
PARTIAL_FINALIZATION_FAILS_CLOSED: YES

POST_ACCEPTANCE_CANONICAL_PROMOTION_REACHABLE: YES
POST_ACCEPTANCE_PROMOTION_P30_GOVERNED: YES
P30_DEADLOCK_RESOLVED: YES

SELF_ISSUING_TERMINAL_ACCEPTANCE_REINTRODUCED: NO
CALLER_ROLE_ACCEPTANCE_REINTRODUCED: NO
CALLER_IDENTITY_ACCEPTANCE_REINTRODUCED: NO
NON_MATERIAL_BYPASS_REINTRODUCED: NO
CHECKER_ONLY_ACCEPTANCE_REINTRODUCED: NO
LEGACY_AUTO_PROMOTION_REINTRODUCED: NO

CANDIDATE_WORKFLOW_REMAINS_USABLE: YES
PROPORTIONALITY_PRESERVED: YES

P30_REQUIRED_TESTS_PASS: YES
UNRELATED_EXISTING_FAILURES: 2 planner/harness smoke failures; clean planner harness remains 0/8, unrelated to P30-A4

MANUSCRIPT_MODIFIED: NO
J28B_EXECUTED: NO
IMPLEMENTER_TERMINAL_ACCEPTANCE_CLAIMED: NO
```

Fresh independent artifact-first evaluation remains the next step.
