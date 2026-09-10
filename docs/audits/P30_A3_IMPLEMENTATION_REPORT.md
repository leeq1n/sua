# P30-A3 Implementation Report

> **Implementation-only handoff.** This report does not issue P30 acceptance,
> does not authenticate an evaluator, and does not authorize freeze,
> submission, or deployment. A fresh independent evaluator must inspect the
> exact clean artifact and produce any terminal decision outside this
> repository.

## Scope and boundary

P30-A3 removes repository self-attestation as a terminal authority. The
implementation permits local tooling to compute artifact identity and clean
state, record local execution/regression evidence, retain candidate bundles,
and prepare a nonterminal handoff. It does not permit caller-supplied role,
identity, audit, materiality, freeze, or evaluator-edit claims to create
`INDEPENDENT ACCEPTANCE PASS`.

The spacecraft-security manuscript was not modified. J28-B was not executed.
No scientific research or fake authentication mechanism was added.

## Implemented trust model

`agent-tools/scripts/p30_acceptance.py` now provides:

- `compute_current_artifact_identity()` — computes the current Git `HEAD`,
  porcelain tracked/untracked change list, and clean/dirty status;
- `prepare_independent_audit_handoff()` — emits a nonterminal handoff and
  returns `ARTIFACT DIRTY / COMMIT OR MATERIALIZE EXACT STATE BEFORE AUDIT`
  for dirty or uncommitted state;
- `verify_external_acceptance_record()` — validates a pre-existing JSON record
  outside the candidate repository, its schema, exact current identity,
  accepted identity, decision, artifact-first status, first-pass freeze,
  evaluator material-edit status, timestamp, and report reference;
- `can_issue_terminal_acceptance()` — always refuses local creation;
- `issue_terminal_acceptance()` — retained only as a compatibility trap and
  always raises `P30AuthorityError`.

The verifier returns
`EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT` only when the external
record matches the exact unchanged clean artifact. It sets
`repository_proved_independence: false` and states
`NOT_MACHINE_PROVEN`; it does not claim that a role string or JSON record
proves who performed the audit.

The compatibility `--terminal-acceptance` CLI mode can only verify an
already-existing external record. Without `--external-record`, it fails
closed. `--artifact-id` is a compatibility label and cannot override the
computed identity. `--non-material-artifact` cannot create acceptance.

## Dirty, stale, and materiality policy

Terminal verification requires a clean, committed artifact. Any tracked or
untracked change makes the current state ineligible and prevents a terminal
record from matching. A prior record whose identity differs from the computed
current identity is rejected as stale/drifted; an artifact mutation after an
external record therefore requires a new external audit. Evaluator material
edit history is not inferred from a caller flag: identity change invalidates
the old record, while hidden authorship remains a governance fact.

Formal artifact work uses a conservative materiality boundary. A trivial,
non-semantic workflow may remain outside the formal state machine, but a
caller-declared non-material flag is not an acceptance authority.

## Legacy finality and promotion paths

All audited legacy surfaces are now classified as execution/candidate state
only at their local boundary:

| Surface | Classification and correction |
|---|---|
| `run_3rounds_manual.py` | Candidate results only; `RUN COMPLETE / CANDIDATE RESULTS SAVED` replaces terminal-looking output. |
| `run_stable.py` | Local candidate convergence only; retention and harness results are explicitly qualified. |
| `run_1round.py` | Local run/candidate result only; no bare `DONE` terminal output. |
| `agent-tools/scripts/weekly_audit.sh` | Reports `ALL SCHEDULED REGRESSION CHECKS PASSED` and separately `ARTIFACT ACCEPTANCE: NOT ISSUED`. |
| `self_upgrade/__main__.py` | Local decisions and candidate bundles only; `--auto-commit` no longer creates canonical commits. |
| `src/v3_auto_commit.py` | Compatibility function validates callers, retains a candidate bundle, and never stages/commits the canonical target. |
| `src/pipeline.py` | Saves candidates for review; `auto_promote` stages candidate metadata only and does not write `core/`. |
| `src/pipeline_lg.py` | Benchmark patching remains an execution/evaluation step; the decision path saves or stages candidates and never promotes to canonical `core/`. |
| `src/switcher.py` | `promote_patch()` and `promote_candidate()` are candidate-only staging aliases; they do not write `core/` or `active/`, create backups, or update the promotion manifest. |

The former material `candidate -> core -> accepted` route is therefore not a
local P30 acceptance route. Any later canonical freeze/deployment requires a
separate external workflow and a matching external decision for the exact
artifact.

## Machine versus governance enforcement

Machine-enforced facts are identity, clean state, tracked/untracked drift,
schema, exact record matching, local nonterminal state, and fail-closed legacy
promotion behavior. Governance/orchestrator-enforced facts are evaluator
freshness, absence of hidden authorship, artifact-first ordering, first-pass
freeze, and independent production of the external record. The repository
does not pretend that the machine layer proves the governance layer.

## Required adversarial coverage

The P30-required focused suite exercises:

1. self-attested complete caller records;
2. fabricated caller identity and fabricated external identity;
3. spoofed evaluator-role claims without machine independence proof;
4. non-material bypass attempts;
5. current identity drift after an external audit record;
6. dirty and untracked artifact rejection;
7. checker/regression-only evidence;
8. missing external record and terminal CLI fail-closed behavior;
9. legacy terminal-output qualification;
10. both legacy promotion aliases remaining candidate-only;
11. valid external-record verification for an exact clean artifact;
12. fresh-agent handoff routing to `READY FOR INDEPENDENT AUDIT`.

## Verification evidence

### P30-required tests

- `pytest -q tests/test_construction_acceptance_separation.py tests/test_switcher.py tests/test_v2_cli.py tests/test_run_stable.py`
  — **94 passed**.
- UTF-8 `py_compile` over the changed Python paths — **pass**.
- `validate_structure.py` with UTF-8 console — **24/24 critical paths present**.
- `validate_links.py` with UTF-8 console — **all cross-references valid**.
- `git diff --check` before the implementation commit — **pass**.

### Adjacent regression evidence

- `tests/test_v181_features.py tests/test_v3_persist.py tests/test_planner_harness_persistence.py`
  — **91 passed, 1 skipped**.
- `tests/test_pipeline.py tests/test_pipeline_harness_integration.py tests/test_harness_integration.py`
  — **15 passed, 2 unrelated existing failures**. Both failures are clean
  planner-harness smoke tests reporting **0/8** passing; they are not caused by
  the P30 trust-boundary or candidate-promotion changes.
- The selected run including the end-to-end tests had the same two E2E
  failures: no qualified scored papers and dry-run `done=False` on the
  filter-empty early-end path. No blanket full-suite pass is claimed.

## Required state fields

```text
SELF_ISSUING_TERMINAL_ACCEPTANCE_REMOVED_OR_DISABLED: YES
CALLER_ROLE_CAN_CREATE_ACCEPTANCE: NO
CALLER_ARTIFACT_ID_CAN_OVERRIDE_CURRENT_IDENTITY: NO
CALLER_NON_MATERIAL_FLAG_CAN_CREATE_ACCEPTANCE: NO
TERMINAL_ARTIFACT_IDENTITY_COMPUTED_FROM_CURRENT_ARTIFACT: YES
DIRTY_TERMINAL_ACCEPTANCE_POLICY: REJECT_DIRTY
PRIOR_ACCEPTANCE_BOUND_TO_ARTIFACT_IDENTITY: YES
ARTIFACT_DRIFT_STALES_ACCEPTANCE: YES
EXTERNAL_AUDIT_RECORD_REQUIRED_FOR_TERMINAL_ACCEPTANCE: YES
EXTERNAL_RECORD_IDENTITY_MATCH_REQUIRED: YES
MACHINE_ENFORCEMENT_LIMIT_DOCUMENTED: YES
EPISTEMIC_INDEPENDENCE_NOT_SELF_ATTESTED: YES
LEGACY_FINALITY_SURFACES_CLASSIFIED: YES
MATERIAL_PROMOTION_P30_GATED_OR_NONTERMINAL: YES
AUTO_PROMOTE_CANNOT_CREATE_ACCEPTANCE: YES
FABRICATED_IDENTITY_TEST_REJECTED: YES
SPOOFED_EVALUATOR_TEST_REJECTED: YES
NON_MATERIAL_BYPASS_TEST_REJECTED: YES
ARTIFACT_DRIFT_TEST_REJECTED: YES
CHECKER_ONLY_ACCEPTANCE_TEST_REJECTED: YES
LEGACY_PROMOTION_BYPASS_TEST_REJECTED: YES
P30_REQUIRED_TESTS_PASS: YES
MANUSCRIPT_MODIFIED: NO
J28B_EXECUTED: NO
IMPLEMENTER_TERMINAL_ACCEPTANCE_CLAIMED: NO
```

## Exact commits

```text
BASE_COMMIT: 8fe3c227cc25fcb00152b48ee27038b1af2fd865
NEW_IMPLEMENTATION_COMMIT: 2c3b541bb7e86d6ec890a9a9cda2b812f2434869
OPTIONAL_HANDOFF_COMMIT: this report's separate local handoff commit
```

The four pre-existing user-owned files under `docs/audits/` remain untracked
and unstaged. Consequently, the current checkout is intentionally reported as
dirty by the P30 handoff until an evaluator materializes the exact committed
artifact state without those unrelated working-tree files.

## Implementation status

P30-A3 implementation is complete at the implementation level and is ready
for a fresh independent audit. This report does not issue terminal acceptance.
