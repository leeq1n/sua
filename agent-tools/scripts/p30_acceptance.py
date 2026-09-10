#!/usr/bin/env python3
"""Small, fail-closed P30 authority/state boundary.

This module is the shared plumbing for acceptance-related scripts.  It does
not perform an independent audit and it does not decide whether an artifact
is substantively good.  It records the distinction between execution and
artifact acceptance, refuses material terminal acceptance without explicit
independent-evaluator evidence, and makes material-change/evaluator-edit
resets observable.

P30 rule: ``CHECKER PASS != INDEPENDENT ACCEPTANCE PASS``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path


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


class P30AuthorityError(RuntimeError):
    """Raised when a caller attempts an unauthorized material acceptance."""


@dataclass(frozen=True)
class AcceptanceRecord:
    """Minimal state record used by active acceptance plumbing.

    The fields intentionally remain plain strings so the record can be
    serialized by shell hooks and inspected by other runtimes without a
    shared Python package.  Unknown or contradictory values fail closed in
    :func:`can_issue_terminal_acceptance`.
    """

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
    """Normalize only exact known roles; never infer independence."""

    return value if value in VALID_ROLES else ROLE_UNSPECIFIED


def new_acceptance_record(
    artifact_identity: str,
    role: str = ROLE_UNSPECIFIED,
    material_artifact: bool = True,
) -> AcceptanceRecord:
    """Create an unaccepted record for one explicit artifact state."""

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
    """Record successful execution without issuing artifact acceptance.

    ``prior_record`` is optional.  When supplied, the new identity is treated
    as a material successor to the prior record and its prior acceptance is
    explicitly stale.  A successful execution can therefore reach only the
    independent-audit handoff state for material artifacts.
    """

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
    """Record the implementer's bounded local verification status."""

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
    """Record the independent evaluator's audit evidence.

    The evaluator role is explicit when ``role`` is supplied.  The default
    preserves the caller's role, so this function cannot turn an implementer
    into an evaluator merely because it is called.
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
    """Make the prior acceptance stale for a materially changed identity."""

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
    """Terminate evaluator authority after an evaluator material edit."""

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
    """Return whether this record has sufficient P30 authority evidence."""

    if not record.material_artifact:
        if not record.artifact_identity:
            return False, "artifact identity is missing"
        return True, "non-material artifact is within P30 proportionality exception"

    if not record.artifact_identity:
        return False, "artifact identity is missing"
    if record.current_role != ROLE_INDEPENDENT_EVALUATOR:
        return False, "material terminal acceptance requires an independent evaluator role"
    if record.artifact_state != ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT:
        return False, "artifact is not ready for independent audit"
    if record.material_modification_since_last_acceptance not in {YES, NO}:
        return False, "material-modification state is unknown"
    if record.material_modification_since_last_acceptance == YES:
        if record.prior_acceptance_state != PRIOR_ACCEPTANCE_STALE:
            return False, "material modification did not stale the prior acceptance"
        if not record.prior_artifact_identity:
            return False, "prior artifact identity is missing"
        if record.prior_artifact_identity == record.artifact_identity:
            return False, "material change did not produce a new artifact identity"
    elif record.prior_acceptance_state not in {
        PRIOR_ACCEPTANCE_NONE,
        PRIOR_ACCEPTANCE_VALID,
    }:
        return False, "prior acceptance state is contradictory"
    elif (
        record.prior_acceptance_state == PRIOR_ACCEPTANCE_VALID
        and record.prior_artifact_identity
        and record.prior_artifact_identity != record.artifact_identity
    ):
        return False, "current artifact identity does not match prior valid acceptance"
    if record.regression_status != REGRESSION_PASS:
        return False, "regression evidence is not complete"
    if record.independent_audit_status != INDEPENDENT_AUDIT_COMPLETE:
        return False, "independent artifact-first audit is incomplete"
    if record.artifact_first_reviewed is not True or record.first_pass_frozen is not True:
        return False, "artifact-first first-pass evidence is missing"
    if record.evaluator_material_edit != NO:
        return False, "evaluator material-edit state is not clean"
    if record.evaluator_authority_valid != YES:
        return False, "evaluator authority is not valid"
    if record.terminal_acceptance_status == INDEPENDENT_ACCEPTANCE_PASS:
        return False, "terminal acceptance has already been issued"
    return True, "P30 authority evidence is complete"


def issue_terminal_acceptance(record: AcceptanceRecord) -> AcceptanceRecord:
    """Issue the terminal state only after the fail-closed authority check."""

    allowed, reason = can_issue_terminal_acceptance(record)
    if not allowed:
        raise P30AuthorityError(reason)
    return replace(
        record,
        artifact_state=ARTIFACT_STATE_ACCEPTED,
        artifact_acceptance="ACCEPTED",
        terminal_acceptance_status=(
            INDEPENDENT_ACCEPTANCE_PASS
            if record.material_artifact
            else "NON-MATERIAL ACCEPTANCE"
        ),
    )


def git_artifact_identity(repo: Path | None = None) -> str:
    """Return a commit-bound identity, with a deterministic dirty suffix."""

    root = repo or Path(__file__).resolve().parents[2]
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
        if head.returncode != 0:
            return ""
        identity = head.stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        ).stdout
        if not status.strip():
            return identity
        diff = subprocess.run(
            ["git", "diff", "HEAD", "--binary"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        ).stdout
        digest = hashlib.sha256((status + diff).encode("utf-8")).hexdigest()[:16]
        return f"{identity}-dirty-{digest}"
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="P30 fail-closed state boundary")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execution-success", action="store_true")
    mode.add_argument("--regression-evidence", action="store_true")
    mode.add_argument("--terminal-acceptance", action="store_true")
    parser.add_argument(
        "--role",
        choices=sorted(VALID_ROLES),
        default=ROLE_UNSPECIFIED,
    )
    parser.add_argument("--artifact-id", default="")
    parser.add_argument("--material-artifact", action="store_true", default=True)
    parser.add_argument("--non-material-artifact", action="store_false", dest="material_artifact")
    parser.add_argument(
        "--material-modification",
        choices=(YES, NO, UNKNOWN),
        default=NO,
    )
    parser.add_argument(
        "--prior-acceptance-state",
        choices=(PRIOR_ACCEPTANCE_VALID, PRIOR_ACCEPTANCE_STALE, PRIOR_ACCEPTANCE_NONE),
        default=PRIOR_ACCEPTANCE_NONE,
    )
    parser.add_argument("--prior-artifact-id", default="")
    parser.add_argument("--independent-audit-status", default=NOT_RUN)
    parser.add_argument("--evaluator-material-edit", choices=(YES, NO, UNKNOWN), default=UNKNOWN)
    parser.add_argument("--evaluator-authority-valid", choices=(YES, NO, UNKNOWN), default=UNKNOWN)
    parser.add_argument("--artifact-first-reviewed", action="store_true")
    parser.add_argument("--first-pass-frozen", action="store_true")
    parser.add_argument("--regression-status", default=NOT_RUN)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    identity = args.artifact_id or git_artifact_identity()

    if args.execution_success or args.regression_evidence:
        record = execution_success(
            role=args.role,
            artifact_identity=identity,
            material_artifact=args.material_artifact,
        )
        if args.regression_evidence:
            record = record_regression(record, passed=args.regression_status == REGRESSION_PASS)
        print(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True))
        return 0

    record = new_acceptance_record(
        artifact_identity=identity,
        role=args.role,
        material_artifact=args.material_artifact,
    )
    record = replace(
        record,
        artifact_state=ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT,
        material_modification_since_last_acceptance=args.material_modification,
        prior_acceptance_state=args.prior_acceptance_state,
        prior_artifact_identity=args.prior_artifact_id,
        regression_status=args.regression_status,
        independent_audit_status=args.independent_audit_status,
        evaluator_material_edit=args.evaluator_material_edit,
        evaluator_authority_valid=args.evaluator_authority_valid,
        artifact_first_reviewed=args.artifact_first_reviewed,
        first_pass_frozen=args.first_pass_frozen,
        execution_status="EXECUTION_SUCCESS",
    )
    allowed, reason = can_issue_terminal_acceptance(record)
    if not allowed:
        record = replace(record, terminal_acceptance_status=ACCEPTANCE_BLOCKED)
        print(json.dumps({**record.to_dict(), "reason": reason}, ensure_ascii=False, sort_keys=True))
        return 2
    accepted = issue_terminal_acceptance(record)
    print(json.dumps(accepted.to_dict(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
