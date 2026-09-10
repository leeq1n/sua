#!/usr/bin/env python3
"""P30 construction/acceptance boundary.

This module can compute repository state, record local regression evidence,
prepare an audit handoff, and verify an already-existing external audit
record.  It cannot create independent acceptance from local caller input.

The external record is a governance artifact produced outside the candidate
repository.  Verification checks schema, identity, clean state, and drift;
it does not prove that the evaluator was genuinely independent.  That fact
belongs to the human/orchestrator workflow.

P30 rule: ``CHECKER PASS != INDEPENDENT ACCEPTANCE PASS``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Mapping


ROLE_IMPLEMENTER = "IMPLEMENTER"
ROLE_INDEPENDENT_EVALUATOR = "INDEPENDENT_EVALUATOR"
ROLE_UNSPECIFIED = "UNSPECIFIED"
VALID_ROLES = frozenset(
    {ROLE_IMPLEMENTER, ROLE_INDEPENDENT_EVALUATOR, ROLE_UNSPECIFIED}
)

ARTIFACT_STATE_UNACCEPTED = "UNACCEPTED"
ARTIFACT_STATE_ACCEPTED = "ACCEPTED"
ARTIFACT_STATE_STALE_AFTER_MATERIAL_CHANGE = "STALE_AFTER_MATERIAL_CHANGE"
ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT = "READY_FOR_INDEPENDENT_AUDIT"

YES = "YES"
NO = "NO"
UNKNOWN = "UNKNOWN"

PRIOR_ACCEPTANCE_VALID = "VALID"
PRIOR_ACCEPTANCE_STALE = "STALE"
PRIOR_ACCEPTANCE_NONE = "NONE"

NOT_RUN = "NOT_RUN"
NOT_ISSUED = "NOT_ISSUED"
REGRESSION_PASS = "REGRESSION PASS"
REGRESSION_INCOMPLETE = "REGRESSION INCOMPLETE"
INDEPENDENT_AUDIT_COMPLETE = "INDEPENDENT AUDIT COMPLETE"
INDEPENDENT_AUDIT_REQUIRED = "INDEPENDENT AUDIT REQUIRED"
INDEPENDENT_ACCEPTANCE_PASS = "INDEPENDENT ACCEPTANCE PASS"
ACCEPTANCE_BLOCKED = "ACCEPTANCE BLOCKED / INDEPENDENT AUDIT REQUIRED"

P30_SCHEMA_VERSION = "P30-A3/v1"
EXTERNAL_RECORD_TYPE = "P30_EXTERNAL_INDEPENDENT_AUDIT"
EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT = (
    "EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT"
)
EXTERNAL_ACCEPTANCE_RECORD_REJECTED = "EXTERNAL_ACCEPTANCE_RECORD_REJECTED"
DIRTY_ARTIFACT = "ARTIFACT DIRTY / COMMIT OR MATERIALIZE EXACT STATE BEFORE AUDIT"
MACHINE_INDEPENDENCE_PROOF = "NOT_MACHINE_PROVEN"

EXTERNAL_RECORD_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "record_type",
        "artifact_identity",
        "accepted_artifact_identity",
        "terminal_decision",
        "evaluator_role_declaration",
        "artifact_first_audit_status",
        "first_pass_freeze_status",
        "evaluator_material_edit_status",
        "audit_timestamp",
        "audit_report_reference",
    }
)


class P30AuthorityError(RuntimeError):
    """Raised when local tooling is asked to create terminal acceptance."""


@dataclass(frozen=True)
class CurrentArtifactIdentity:
    """Identity and clean-state facts computed from one repository."""

    identity: str
    commit: str
    clean: bool
    changed_paths: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "identity": self.identity,
            "commit": self.commit,
            "clean": self.clean,
            "changed_paths": list(self.changed_paths),
        }


@dataclass(frozen=True)
class ExternalAcceptanceVerification:
    """Result of verifying an external record without creating acceptance."""

    verified: bool
    status: str
    reason: str
    artifact_identity: str
    external_record_identity: str = ""
    external_terminal_decision: str = ""
    artifact_clean: bool = False
    external_record_path: str = ""
    repository_proved_independence: bool = False
    machine_independence_statement: str = MACHINE_INDEPENDENCE_PROOF
    artifact_acceptance: str = NOT_ISSUED
    terminal_acceptance_status: str = NOT_ISSUED

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AcceptanceRecord:
    """Local evidence record; it is never a terminal acceptance authority."""

    artifact_identity: str
    current_role: str = ROLE_UNSPECIFIED
    material_artifact: bool = True
    artifact_state: str = ARTIFACT_STATE_UNACCEPTED
    material_modification_since_last_acceptance: str = NO
    prior_acceptance_state: str = PRIOR_ACCEPTANCE_NONE
    prior_artifact_identity: str = ""
    local_fix_status: str = NOT_RUN
    regression_status: str = NOT_RUN
    independent_audit_status: str = NOT_RUN
    evaluator_material_edit: str = UNKNOWN
    evaluator_authority_valid: str = UNKNOWN
    artifact_first_reviewed: bool = False
    first_pass_frozen: bool = False
    execution_status: str = NOT_RUN
    artifact_acceptance: str = NOT_ISSUED
    terminal_acceptance_status: str = NOT_ISSUED

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _role(value: str | None) -> str:
    """Normalize a label for reporting; never infer identity or independence."""

    return value if value in VALID_ROLES else ROLE_UNSPECIFIED


def new_acceptance_record(
    artifact_identity: str,
    role: str = ROLE_UNSPECIFIED,
    material_artifact: bool = True,
) -> AcceptanceRecord:
    """Create a local, unaccepted record for explicit evidence plumbing."""

    return AcceptanceRecord(
        artifact_identity=artifact_identity or "",
        current_role=_role(role),
        material_artifact=material_artifact,
        artifact_state=ARTIFACT_STATE_UNACCEPTED,
        evaluator_authority_valid=(
            YES if _role(role) == ROLE_INDEPENDENT_EVALUATOR else NO
        ),
    )


def execution_success(
    *,
    role: str,
    artifact_identity: str,
    material_artifact: bool = True,
    prior_record: AcceptanceRecord | None = None,
) -> AcceptanceRecord:
    """Record successful local execution without issuing artifact acceptance."""

    if prior_record is not None:
        record = mark_material_change(
            prior_record, artifact_identity=artifact_identity, role=role
        )
    else:
        record = new_acceptance_record(
            artifact_identity=artifact_identity,
            role=role,
            material_artifact=material_artifact,
        )

    return replace(
        record,
        current_role=_role(role),
        material_artifact=material_artifact,
        artifact_state=(
            ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT
            if material_artifact
            else ARTIFACT_STATE_UNACCEPTED
        ),
        execution_status="EXECUTION_SUCCESS",
        artifact_acceptance=NOT_ISSUED,
        terminal_acceptance_status=NOT_ISSUED,
    )


def record_local_fix(record: AcceptanceRecord) -> AcceptanceRecord:
    """Record bounded local verification status."""

    return replace(record, local_fix_status="LOCAL FIX VERIFIED")


def record_regression(
    record: AcceptanceRecord, *, passed: bool
) -> AcceptanceRecord:
    """Record regression evidence; this never changes the record to accepted."""

    return replace(
        record,
        regression_status=REGRESSION_PASS if passed else REGRESSION_INCOMPLETE,
        artifact_state=(
            ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT
            if passed and record.material_artifact
            else record.artifact_state
        ),
        artifact_acceptance=NOT_ISSUED,
        terminal_acceptance_status=NOT_ISSUED,
    )


def record_independent_audit(
    record: AcceptanceRecord,
    *,
    artifact_first: bool,
    first_pass_frozen: bool,
    evaluator_material_edit: bool,
    role: str | None = None,
) -> AcceptanceRecord:
    """Record locally supplied audit claims as non-authoritative annotations.

    This function intentionally does not confer authority.  The same-process
    caller may populate the fields, but only an external record can be
    verified as a prior governance event, and the repository still cannot
    prove the evaluator's epistemic independence.
    """

    current_role = record.current_role if role is None else _role(role)
    material_edit = YES if evaluator_material_edit else NO
    authority = (
        YES
        if current_role == ROLE_INDEPENDENT_EVALUATOR and not evaluator_material_edit
        else NO
    )
    complete = artifact_first and first_pass_frozen and not evaluator_material_edit
    return replace(
        record,
        current_role=current_role,
        artifact_first_reviewed=artifact_first,
        first_pass_frozen=first_pass_frozen,
        evaluator_material_edit=material_edit,
        evaluator_authority_valid=authority,
        independent_audit_status=(
            INDEPENDENT_AUDIT_COMPLETE if complete else INDEPENDENT_AUDIT_REQUIRED
        ),
        terminal_acceptance_status=NOT_ISSUED,
    )


def mark_material_change(
    prior_record: AcceptanceRecord,
    *,
    artifact_identity: str,
    role: str = ROLE_IMPLEMENTER,
) -> AcceptanceRecord:
    """Mark a local successor record stale; formal drift uses computed identity."""

    prior_state = (
        PRIOR_ACCEPTANCE_VALID
        if prior_record.artifact_state == ARTIFACT_STATE_ACCEPTED
        else prior_record.prior_acceptance_state
    )
    if prior_state != PRIOR_ACCEPTANCE_VALID:
        prior_state = (
            PRIOR_ACCEPTANCE_STALE
            if prior_record.artifact_identity
            else PRIOR_ACCEPTANCE_NONE
        )
    return replace(
        prior_record,
        artifact_identity=artifact_identity or "",
        current_role=_role(role),
        artifact_state=ARTIFACT_STATE_STALE_AFTER_MATERIAL_CHANGE,
        material_modification_since_last_acceptance=YES,
        prior_acceptance_state=(
            PRIOR_ACCEPTANCE_STALE
            if prior_state == PRIOR_ACCEPTANCE_VALID
            else prior_state
        ),
        prior_artifact_identity=prior_record.artifact_identity,
        local_fix_status=NOT_RUN,
        regression_status=NOT_RUN,
        independent_audit_status=NOT_RUN,
        evaluator_material_edit=NO,
        evaluator_authority_valid=NO,
        artifact_first_reviewed=False,
        first_pass_frozen=False,
        execution_status=NOT_RUN,
        artifact_acceptance=(
            "STALE" if prior_record.artifact_state == ARTIFACT_STATE_ACCEPTED else NOT_ISSUED
        ),
        terminal_acceptance_status=ACCEPTANCE_BLOCKED,
    )


def mark_evaluator_material_edit(
    record: AcceptanceRecord, artifact_identity: str
) -> AcceptanceRecord:
    """Terminate the evaluator's authority after a material artifact edit."""

    prior_state = (
        PRIOR_ACCEPTANCE_STALE
        if record.artifact_identity
        else PRIOR_ACCEPTANCE_NONE
    )
    return replace(
        record,
        artifact_identity=artifact_identity or "",
        current_role=ROLE_UNSPECIFIED,
        artifact_state=ARTIFACT_STATE_STALE_AFTER_MATERIAL_CHANGE,
        material_modification_since_last_acceptance=YES,
        prior_acceptance_state=prior_state,
        prior_artifact_identity=record.artifact_identity,
        evaluator_material_edit=YES,
        evaluator_authority_valid=NO,
        independent_audit_status=INDEPENDENT_AUDIT_REQUIRED,
        artifact_acceptance=(
            "STALE" if record.artifact_state == ARTIFACT_STATE_ACCEPTED else NOT_ISSUED
        ),
        terminal_acceptance_status=ACCEPTANCE_BLOCKED,
    )


def can_issue_terminal_acceptance(
    record: AcceptanceRecord,
) -> tuple[bool, str]:
    """Always deny local creation; terminal authority is external-only."""

    return False, (
        "terminal acceptance creation is external-only; repository tooling "
        "may verify a matching external independent-audit record but cannot "
        "prove or manufacture evaluator independence"
    )


def issue_terminal_acceptance(record: AcceptanceRecord) -> AcceptanceRecord:
    """Compatibility trap: local records can never create terminal acceptance."""

    raise P30AuthorityError(
        "repository tooling cannot create terminal acceptance; "
        "verify an already-existing external independent-audit record"
    )


def _git_output(args: list[str], root: Path) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)
    return result.returncode, result.stdout or "", result.stderr or ""


def compute_current_artifact_identity(
    repo: Path | str | None = None,
) -> CurrentArtifactIdentity:
    """Compute the current commit identity and clean/dirty state.

    A clean committed repository returns its exact commit identity.  A dirty
    state is represented as ``DIRTY:<HEAD>`` and is never eligible for
    terminal verification; no filename-only or incomplete dirty digest is
    used as an acceptance identity.
    """

    root = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
    rc, head, _ = _git_output(["rev-parse", "HEAD"], root)
    commit = head.strip() if rc == 0 else ""
    rc, status, _ = _git_output(
        ["status", "--porcelain=v1", "--untracked-files=all"], root
    )
    changed = tuple(line for line in status.splitlines() if line.strip())
    clean = rc == 0 and not changed and bool(commit)
    if clean:
        identity = commit
    elif commit:
        identity = f"DIRTY:{commit}"
    else:
        identity = ""
    return CurrentArtifactIdentity(
        identity=identity,
        commit=commit,
        clean=clean,
        changed_paths=changed,
    )


def git_artifact_identity(repo: Path | str | None = None) -> str:
    """Compatibility wrapper returning the computed current-state identity."""

    return compute_current_artifact_identity(repo).identity


def prepare_independent_audit_handoff(
    repo: Path | str | None = None,
) -> dict[str, object]:
    """Prepare a nonterminal handoff from computed repository state."""

    current = compute_current_artifact_identity(repo)
    ready = current.clean
    return {
        "artifact_identity": current.identity,
        "commit": current.commit,
        "clean": current.clean,
        "changed_paths": list(current.changed_paths),
        "artifact_state": (
            ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT
            if ready
            else DIRTY_ARTIFACT
        ),
        "status": "READY FOR INDEPENDENT AUDIT" if ready else DIRTY_ARTIFACT,
        "artifact_acceptance": NOT_ISSUED,
        "terminal_acceptance_status": NOT_ISSUED,
        "external_audit_record_required": YES,
        "repository_proved_independence": False,
        "machine_independence_statement": MACHINE_INDEPENDENCE_PROOF,
    }


def _rejected_verification(
    *,
    current: CurrentArtifactIdentity,
    reason: str,
    record_path: Path | None = None,
    external_identity: str = "",
    external_decision: str = "",
) -> ExternalAcceptanceVerification:
    return ExternalAcceptanceVerification(
        verified=False,
        status=EXTERNAL_ACCEPTANCE_RECORD_REJECTED,
        reason=reason,
        artifact_identity=current.identity,
        external_record_identity=external_identity,
        external_terminal_decision=external_decision,
        artifact_clean=current.clean,
        external_record_path=str(record_path) if record_path else "",
        artifact_acceptance=NOT_ISSUED,
        terminal_acceptance_status=ACCEPTANCE_BLOCKED,
    )


def _record_path_is_external(record_path: Path, repo: Path) -> bool:
    record_resolved = record_path.resolve()
    repo_resolved = repo.resolve()
    try:
        record_resolved.relative_to(repo_resolved)
    except ValueError:
        return True
    return False


def verify_external_acceptance_record(
    external_record: Mapping[str, object],
    *,
    repo: Path | str | None = None,
    record_path: Path | str | None = None,
) -> ExternalAcceptanceVerification:
    """Verify an external record against the computed current artifact.

    The record must already exist outside the candidate repository.  This
    function checks the machine-verifiable parts of the contract only.  It
    deliberately reports a matching external decision rather than creating
    ``INDEPENDENT ACCEPTANCE PASS`` or asserting that independence was proved.
    """

    root = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
    current = compute_current_artifact_identity(root)
    path = Path(record_path).resolve() if record_path is not None else None

    if path is None:
        return _rejected_verification(
            current=current,
            reason="external audit record path is required",
        )
    if not path.is_file():
        return _rejected_verification(
            current=current,
            reason="external audit record does not exist as a file",
            record_path=path,
        )
    if not _record_path_is_external(path, root):
        return _rejected_verification(
            current=current,
            reason="external audit record must be outside the candidate repository",
            record_path=path,
        )
    if not current.clean:
        return _rejected_verification(
            current=current,
            reason=DIRTY_ARTIFACT,
            record_path=path,
        )
    if not isinstance(external_record, Mapping):
        return _rejected_verification(
            current=current,
            reason="external audit record must be a JSON object",
            record_path=path,
        )

    missing = sorted(EXTERNAL_RECORD_REQUIRED_FIELDS - set(external_record))
    if missing:
        return _rejected_verification(
            current=current,
            reason=f"external audit record schema incomplete: missing {missing}",
            record_path=path,
        )

    values = {
        key: external_record.get(key) for key in EXTERNAL_RECORD_REQUIRED_FIELDS
    }
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        return _rejected_verification(
            current=current,
            reason="external audit record contains missing or non-string required values",
            record_path=path,
        )

    external_identity = str(external_record["artifact_identity"])
    accepted_identity = str(external_record["accepted_artifact_identity"])
    decision = str(external_record["terminal_decision"])

    if external_record["schema_version"] != P30_SCHEMA_VERSION:
        return _rejected_verification(
            current=current,
            reason="unsupported external audit record schema version",
            record_path=path,
            external_identity=external_identity,
            external_decision=decision,
        )
    if external_record["record_type"] != EXTERNAL_RECORD_TYPE:
        return _rejected_verification(
            current=current,
            reason="external audit record type is not a P30 external record",
            record_path=path,
            external_identity=external_identity,
            external_decision=decision,
        )
    if external_identity != current.identity:
        return _rejected_verification(
            current=current,
            reason=(
                "external audit record artifact identity does not match "
                "the computed current artifact identity"
            ),
            record_path=path,
            external_identity=external_identity,
            external_decision=decision,
        )
    if accepted_identity != current.identity:
        return _rejected_verification(
            current=current,
            reason="accepted artifact identity does not match current artifact identity",
            record_path=path,
            external_identity=external_identity,
            external_decision=decision,
        )

    expected = {
        "terminal_decision": INDEPENDENT_ACCEPTANCE_PASS,
        "evaluator_role_declaration": ROLE_INDEPENDENT_EVALUATOR,
        "artifact_first_audit_status": "COMPLETE",
        "first_pass_freeze_status": "FROZEN",
        "evaluator_material_edit_status": NO,
    }
    for field, expected_value in expected.items():
        if external_record[field] != expected_value:
            return _rejected_verification(
                current=current,
                reason=f"external audit record field {field!r} is not {expected_value!r}",
                record_path=path,
                external_identity=external_identity,
                external_decision=decision,
            )

    # A stale prior record cannot be silently revived by a new caller field.
    prior_state = external_record.get("prior_acceptance_state")
    prior_identity = external_record.get("prior_artifact_identity")
    if prior_state == PRIOR_ACCEPTANCE_STALE and prior_identity == current.identity:
        return _rejected_verification(
            current=current,
            reason="external record marks the current artifact as stale",
            record_path=path,
            external_identity=external_identity,
            external_decision=decision,
        )

    return ExternalAcceptanceVerification(
        verified=True,
        status=EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT,
        reason=(
            "external acceptance record matches the current clean artifact; "
            "repository tooling did not prove evaluator independence"
        ),
        artifact_identity=current.identity,
        external_record_identity=external_identity,
        external_terminal_decision=decision,
        artifact_clean=current.clean,
        external_record_path=str(path),
        repository_proved_independence=False,
        machine_independence_statement=MACHINE_INDEPENDENCE_PROOF,
        artifact_acceptance="EXTERNAL_DECISION_VERIFIED",
        terminal_acceptance_status=EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="P30 nonterminal boundary and external-record verifier")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execution-success", action="store_true")
    mode.add_argument("--regression-evidence", action="store_true")
    mode.add_argument("--prepare-independent-audit", action="store_true")
    mode.add_argument("--verify-external-acceptance", action="store_true")
    # Compatibility alias: it may only verify an existing external record.
    mode.add_argument("--terminal-acceptance", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--repo", default="", help="candidate repository root (default: this repository)")
    parser.add_argument("--external-record", default="", help="external JSON record outside the candidate repository")
    # These legacy fields remain parseable for compatibility, but are never
    # trusted for acceptance and never override computed repository identity.
    parser.add_argument("--role", choices=sorted(VALID_ROLES), default=ROLE_UNSPECIFIED)
    parser.add_argument("--artifact-id", default="")
    parser.add_argument("--material-artifact", action="store_true", default=True)
    parser.add_argument("--non-material-artifact", action="store_false", dest="material_artifact")
    parser.add_argument("--material-modification", choices=(YES, NO, UNKNOWN), default=NO)
    parser.add_argument("--prior-acceptance-state", choices=(PRIOR_ACCEPTANCE_VALID, PRIOR_ACCEPTANCE_STALE, PRIOR_ACCEPTANCE_NONE), default=PRIOR_ACCEPTANCE_NONE)
    parser.add_argument("--prior-artifact-id", default="")
    parser.add_argument("--independent-audit-status", default=NOT_RUN)
    parser.add_argument("--evaluator-material-edit", choices=(YES, NO, UNKNOWN), default=UNKNOWN)
    parser.add_argument("--evaluator-authority-valid", choices=(YES, NO, UNKNOWN), default=UNKNOWN)
    parser.add_argument("--artifact-first-reviewed", action="store_true")
    parser.add_argument("--first-pass-frozen", action="store_true")
    parser.add_argument("--regression-status", default=NOT_RUN)
    return parser


def _blocked_payload(
    current: CurrentArtifactIdentity,
    reason: str,
    *,
    caller_artifact_id: str = "",
) -> dict[str, object]:
    payload = {
        "artifact_identity": current.identity,
        "computed_artifact_identity": current.identity,
        "commit": current.commit,
        "clean": current.clean,
        "changed_paths": list(current.changed_paths),
        "artifact_state": DIRTY_ARTIFACT if not current.clean else ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT,
        "artifact_acceptance": NOT_ISSUED,
        "terminal_acceptance_status": ACCEPTANCE_BLOCKED,
        "external_audit_record_required": YES,
        "repository_proved_independence": False,
        "reason": reason,
    }
    if caller_artifact_id:
        payload["caller_artifact_id_ignored"] = caller_artifact_id
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parents[2]
    current = compute_current_artifact_identity(repo)

    if args.terminal_acceptance or args.verify_external_acceptance:
        if not args.external_record:
            print(json.dumps(_blocked_payload(
                current,
                "terminal acceptance requires an already-existing external independent-audit record",
                caller_artifact_id=args.artifact_id,
            ), ensure_ascii=False, sort_keys=True))
            return 2
        if not args.material_artifact:
            print(json.dumps(_blocked_payload(
                current,
                "caller-declared non-materiality is not an acceptance authority",
                caller_artifact_id=args.artifact_id,
            ), ensure_ascii=False, sort_keys=True))
            return 2
        try:
            record = json.loads(Path(args.external_record).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(json.dumps(_blocked_payload(
                current,
                f"external independent-audit record could not be read: {exc}",
                caller_artifact_id=args.artifact_id,
            ), ensure_ascii=False, sort_keys=True))
            return 2
        result = verify_external_acceptance_record(
            record,
            repo=repo,
            record_path=args.external_record,
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True))
        return 0 if result.verified else 2

    if args.prepare_independent_audit:
        print(json.dumps(prepare_independent_audit_handoff(repo), ensure_ascii=False, sort_keys=True))
        return 0

    # Execution/regression modes may report the caller role, but always use
    # the computed identity and keep artifact acceptance unissued.
    record = execution_success(
        role=args.role,
        artifact_identity=current.identity,
        material_artifact=True,
    )
    if args.regression_evidence:
        record = record_regression(record, passed=args.regression_status == REGRESSION_PASS)
    payload = record.to_dict()
    payload.update({
        "computed_artifact_identity": current.identity,
        "artifact_clean": current.clean,
        "changed_paths": list(current.changed_paths),
        "external_audit_record_required": YES,
        "repository_proved_independence": False,
    })
    if args.artifact_id:
        payload["caller_artifact_id_ignored"] = args.artifact_id
    if not args.material_artifact:
        payload["caller_non_materiality_ignored"] = True
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
