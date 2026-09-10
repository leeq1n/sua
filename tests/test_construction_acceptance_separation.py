"""Regression contract for P30: construction and acceptance are separate."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PRINCIPLES = ROOT / "docs" / "PRINCIPLES.md"
PRINCIPLES_FULL = ROOT / "docs" / "PRINCIPLES_FULL.md"
ACCEPTANCE = ROOT / "docs" / "ACCEPTANCE_PROTOCOL.md"
FINALIZATION = ROOT / "docs" / "ARTIFACT_FINALIZATION.md"
VALIDATION = ROOT / "docs" / "ARTIFACT_GOVERNANCE_VALIDATION.md"
REGISTRY = ROOT / "agent-tools" / "hook_principles.json"
EVAL_BEFORE = ROOT / "agent-tools" / "scripts" / "eval_before.py"
CORE = ROOT / "core-layer" / "AGENTS_CORE.md"
LOADER = ROOT / "agent-tools" / "scripts" / "hook_principles_loader.py"
SCRIPTS = ROOT / "agent-tools" / "scripts"
M29_SCRIPT = SCRIPTS / "m_n29_5step.py"
DETAIL_ROUTE = ROOT / "docs" / "PRINCIPLES_DETAIL.md"
GRAPH = ROOT / "docs" / "HOW_TO_READ_GRAPH.md"
RUN_ACCEPTANCE = SCRIPTS / "run_acceptance.sh"
VERIFY_AFTER = SCRIPTS / "verify_after.py"
EVAL_BEFORE_SCRIPT = SCRIPTS / "eval_before.py"
RELEASE_AUDIT = SCRIPTS / "release_audit.py"
SELF_HEALTH = SCRIPTS / "self_health_check.py"
PRE_PUSH = ROOT / "hooks" / "pre-push"

sys.path.insert(0, str(SCRIPTS))

from p30_acceptance import (  # noqa: E402
    ARTIFACT_STATE_ACCEPTED,
    ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT,
    ARTIFACT_STATE_STALE_AFTER_MATERIAL_CHANGE,
    ROLE_IMPLEMENTER,
    ROLE_INDEPENDENT_EVALUATOR,
    ROLE_UNSPECIFIED,
    P30AuthorityError,
    can_issue_terminal_acceptance,
    execution_success,
    issue_terminal_acceptance,
    mark_evaluator_material_edit,
    mark_material_change,
    new_acceptance_record,
    record_independent_audit,
    record_regression,
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_p30_is_reachable_from_the_canonical_principles_surface():
    summary = read(PRINCIPLES)
    detail = read(PRINCIPLES_FULL)
    assert "P30" in summary
    assert "Separation of Construction and Acceptance" in detail
    assert "Meta-rules" in summary
    assert "P30" in re.search(
        r"\*\*Meta-rules\*\*.*?(?=\n\n|\Z)", summary, re.S
    ).group(0)


def test_p30_is_visible_on_the_always_loaded_entry_surface():
    text = read(CORE)
    assert "P30" in text
    assert "constructor cannot be the final acceptor" in text


def test_p30_contains_the_required_role_and_state_contract():
    detail = read(PRINCIPLES_FULL)
    required = (
        "CONSTRUCTOR CANNOT BE THE FINAL ACCEPTOR",
        "LOCAL FIX VERIFIED",
        "REGRESSION PASS",
        "INDEPENDENT ACCEPTANCE PASS",
        "CORRELATED VALIDATION FAILURE",
        "CHECKER PASS != INDEPENDENT ACCEPTANCE PASS",
        "OLD_ACCEPTANCE_STATE = STALE",
        "ARTIFACT FIRST",
        "OPEN-WORLD ACCEPTANCE",
        "IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT",
    )
    assert all(phrase in detail for phrase in required)
    assert "No direct path from:" in detail
    assert "IMPLEMENTED" in detail
    assert "ACCEPTED" in detail


def test_acceptance_protocol_does_not_conflate_implementation_with_acceptance():
    text = read(ACCEPTANCE)
    for phrase in (
        "LOCAL FIX VERIFIED",
        "REGRESSION PASS",
        "INDEPENDENT ACCEPTANCE PASS",
        "IMPLEMENTER may not issue final acceptance",
        "CHECKER PASS != INDEPENDENT ACCEPTANCE PASS",
        "READY FOR INDEPENDENT AUDIT",
    ):
        assert phrase in text
    assert "P30" in text
    assert "IMPLEMENTED → ACCEPTED" not in text
    for field in (
        "ARTIFACT_IDENTITY",
        "CURRENT_ROLE",
        "MATERIAL_MODIFICATION_SINCE_LAST_ACCEPTANCE",
        "PRIOR_ACCEPTANCE_STATE",
        "EVALUATOR_MATERIAL_EDIT",
        "EVALUATOR_AUTHORITY_VALID",
        "TERMINAL_ACCEPTANCE_STATUS",
    ):
        assert field in text


def test_finalization_adapter_delegates_terminal_authority_to_p30():
    text = read(FINALIZATION)
    assert "P30" in text
    assert "did not materially implement" in text
    assert "Only the independent evaluator may issue terminal acceptance." in text
    assert "adds no P-n" not in text


def test_material_change_invalidates_prior_adapter_acceptance_record():
    text = " ".join(read(VALIDATION).split())
    assert "STALE AFTER P30 AMENDMENT" in text
    assert "independent acceptance has not been performed" in text


def test_registry_and_precommit_validation_accept_p30():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert "P30" in registry["principles"]["active"]
    assert "P30" in read(EVAL_BEFORE)
    result = subprocess.run(
        [sys.executable, str(LOADER), "--active-list"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "P30" in result.stdout.split()


def test_existing_evidence_and_constructive_safeguards_remain_intact():
    combined = "\n".join(
        read(path)
        for path in (
            PRINCIPLES_FULL,
            FINALIZATION,
            ROOT / "docs" / "ADD_THEN_REDUCE.md",
            ROOT / "docs" / "M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md",
            ROOT / "docs" / "OPERATING_RULES.md",
        )
    )
    for phrase in (
        "must not be changed after outcome inspection",
        "cannot rescue a failed result",
        "no fixed rejection count",
        "must not interleave terminal critique",
        "safety",
        "known impossibility",
        "explicit hard constraint",
    ):
        assert phrase in combined


def test_implementer_checker_success_cannot_issue_terminal_acceptance():
    record = execution_success(
        role=ROLE_IMPLEMENTER,
        artifact_identity="commit-implementer",
        material_artifact=True,
    )
    record = record_regression(record, passed=True)

    assert record.artifact_state == ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT
    allowed, reason = can_issue_terminal_acceptance(record)
    assert allowed is False
    assert "independent evaluator" in reason.lower()
    with pytest.raises(P30AuthorityError):
        issue_terminal_acceptance(record)


def test_legacy_m29_completion_is_non_terminal_regression_evidence():
    result = subprocess.run(
        [
            sys.executable,
            str(M29_SCRIPT),
            "--self",
            "--task-profile",
            "well-specified",
            "--claim",
            "legacy completion path",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "REGRESSION EVIDENCE ONLY" in result.stdout
    assert "READY FOR INDEPENDENT AUDIT" in result.stdout
    assert "INDEPENDENT ACCEPTANCE PASS" not in result.stdout


def test_execution_success_is_not_artifact_acceptance():
    record = execution_success(
        role=ROLE_IMPLEMENTER,
        artifact_identity="commit-execution-success",
        material_artifact=True,
    )
    assert record.execution_status == "EXECUTION_SUCCESS"
    assert record.artifact_acceptance == "NOT_ISSUED"
    assert record.artifact_state == ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT
    assert record.terminal_acceptance_status != "INDEPENDENT ACCEPTANCE PASS"


def test_material_modification_stales_prior_acceptance():
    prior = new_acceptance_record(
        artifact_identity="commit-before-change",
        role=ROLE_INDEPENDENT_EVALUATOR,
        material_artifact=True,
    )
    prior = record_regression(prior, passed=True)
    prior = record_independent_audit(
        prior,
        artifact_first=True,
        first_pass_frozen=True,
        evaluator_material_edit=False,
    )
    prior = issue_terminal_acceptance(prior)
    assert prior.artifact_state == ARTIFACT_STATE_ACCEPTED

    changed = mark_material_change(
        prior,
        artifact_identity="commit-after-change",
        role=ROLE_IMPLEMENTER,
    )
    assert changed.artifact_state == ARTIFACT_STATE_STALE_AFTER_MATERIAL_CHANGE
    assert changed.prior_acceptance_state == "STALE"
    assert changed.material_modification_since_last_acceptance == "YES"
    assert changed.prior_artifact_identity == "commit-before-change"
    assert can_issue_terminal_acceptance(changed)[0] is False


def test_matching_independent_evaluator_can_issue_terminal_acceptance():
    record = execution_success(
        role=ROLE_INDEPENDENT_EVALUATOR,
        artifact_identity="commit-independent",
        material_artifact=True,
    )
    record = record_regression(record, passed=True)
    record = record_independent_audit(
        record,
        artifact_first=True,
        first_pass_frozen=True,
        evaluator_material_edit=False,
    )

    accepted = issue_terminal_acceptance(record)
    assert accepted.artifact_state == ARTIFACT_STATE_ACCEPTED
    assert accepted.terminal_acceptance_status == "INDEPENDENT ACCEPTANCE PASS"
    assert accepted.artifact_acceptance == "ACCEPTED"


def test_evaluator_material_edit_terminates_that_evaluator_authority():
    record = execution_success(
        role=ROLE_INDEPENDENT_EVALUATOR,
        artifact_identity="commit-audited",
        material_artifact=True,
    )
    record = record_regression(record, passed=True)
    record = record_independent_audit(
        record,
        artifact_first=True,
        first_pass_frozen=True,
        evaluator_material_edit=False,
    )
    edited = mark_evaluator_material_edit(record, "commit-evaluator-edit")

    assert edited.evaluator_material_edit == "YES"
    assert edited.evaluator_authority_valid == "NO"
    assert edited.artifact_state == ARTIFACT_STATE_STALE_AFTER_MATERIAL_CHANGE
    assert edited.current_role == ROLE_UNSPECIFIED
    with pytest.raises(P30AuthorityError):
        issue_terminal_acceptance(edited)


def test_unspecified_role_fails_closed_for_material_terminal_acceptance():
    record = execution_success(
        role=ROLE_UNSPECIFIED,
        artifact_identity="commit-unknown-role",
        material_artifact=True,
    )
    record = record_regression(record, passed=True)
    allowed, reason = can_issue_terminal_acceptance(record)
    assert allowed is False
    assert "role" in reason.lower()


def test_checker_pass_alone_cannot_produce_acceptance():
    record = new_acceptance_record(
        artifact_identity="commit-checker-only",
        role=ROLE_INDEPENDENT_EVALUATOR,
        material_artifact=True,
    )
    record = record_regression(record, passed=True)
    assert record.regression_status == "REGRESSION PASS"
    assert record.artifact_acceptance == "NOT_ISSUED"
    assert can_issue_terminal_acceptance(record)[0] is False


def test_terminal_cli_refuses_missing_authority_fields():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--terminal-acceptance",
            "--role",
            ROLE_IMPLEMENTER,
            "--artifact-id",
            "commit-cli-blocked",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["terminal_acceptance_status"].startswith("ACCEPTANCE BLOCKED")
    assert payload["artifact_acceptance"] != "ACCEPTED"


def test_terminal_cli_accepts_only_a_complete_independent_record():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--terminal-acceptance",
            "--role",
            ROLE_INDEPENDENT_EVALUATOR,
            "--artifact-id",
            "commit-cli-independent",
            "--material-modification",
            "NO",
            "--prior-acceptance-state",
            "NONE",
            "--regression-status",
            "REGRESSION PASS",
            "--independent-audit-status",
            "INDEPENDENT AUDIT COMPLETE",
            "--evaluator-material-edit",
            "NO",
            "--evaluator-authority-valid",
            "YES",
            "--artifact-first-reviewed",
            "--first-pass-frozen",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["artifact_state"] == ARTIFACT_STATE_ACCEPTED
    assert payload["terminal_acceptance_status"] == "INDEPENDENT ACCEPTANCE PASS"


def test_acceptance_identity_must_match_the_material_change_record():
    record = new_acceptance_record(
        artifact_identity="commit-current",
        role=ROLE_INDEPENDENT_EVALUATOR,
        material_artifact=True,
    )
    record = record_regression(record, passed=True)
    record = record_independent_audit(
        record,
        artifact_first=True,
        first_pass_frozen=True,
        evaluator_material_edit=False,
    )
    record = record.__class__(
        **{
            **record.to_dict(),
            "material_modification_since_last_acceptance": "YES",
            "prior_acceptance_state": "STALE",
            "prior_artifact_identity": "",
        }
    )
    allowed, reason = can_issue_terminal_acceptance(record)
    assert allowed is False
    assert "identity" in reason.lower()


def test_fresh_agent_detail_route_exposes_p30_canonical_section():
    route = read(DETAIL_ROUTE)
    graph = read(GRAPH)
    assert "P30" in route
    assert "PRINCIPLES_FULL.md" in route
    assert "P30" in graph
    assert "PRINCIPLES_DETAIL.md" in graph
    assert "P30" in graph or "PRINCIPLES_FULL.md" in graph


def test_normal_implementation_completion_remains_non_terminal():
    result = subprocess.run(
        [
            sys.executable,
            str(M29_SCRIPT),
            "--self",
            "--task-profile",
            "well-specified",
            "--claim",
            "ordinary implementation task",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "EXECUTION COMPLETE" in result.stdout
    assert "IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT" in result.stdout
    assert "INDEPENDENT ACCEPTANCE PASS" not in result.stdout


def test_active_acceptance_paths_are_explicitly_non_terminal():
    for path in (RUN_ACCEPTANCE, VERIFY_AFTER, EVAL_BEFORE_SCRIPT, RELEASE_AUDIT, PRE_PUSH):
        text = path.read_text(encoding="utf-8")
        assert "REGRESSION EVIDENCE" in text or "p30_acceptance" in text
    health = read(SELF_HEALTH)
    assert "REGRESSION_EVIDENCE" in health
    assert "artifact_acceptance" in health


def test_active_python_gates_refuse_terminal_acceptance_mode():
    for script in (VERIFY_AFTER, EVAL_BEFORE_SCRIPT):
        result = subprocess.run(
            [sys.executable, str(script), "--terminal-acceptance"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert result.returncode == 2
        assert "ACCEPTANCE BLOCKED" in result.stdout


def test_run_acceptance_shell_gate_refuses_terminal_acceptance_mode():
    bash = shutil.which("bash")
    if not bash:
        pytest.skip("bash is not available on this host")
    result = subprocess.run(
        [bash, "agent-tools/scripts/run_acceptance.sh", "--terminal-acceptance"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 2
    assert "ACCEPTANCE BLOCKED" in result.stdout
