"""Regression contract for P30: construction and acceptance are separate."""

import json
import os
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
WEEKLY_AUDIT = ROOT / "agent-tools" / "scripts" / "weekly_audit.sh"
LEGACY_RUNNERS = (
    ROOT / "run_1round.py",
    ROOT / "run_3rounds_manual.py",
    ROOT / "run_stable.py",
)

sys.path.insert(0, str(SCRIPTS))

from p30_acceptance import (  # noqa: E402
    ARTIFACT_STATE_ACCEPTED,
    ARTIFACT_STATE_READY_FOR_INDEPENDENT_AUDIT,
    ARTIFACT_STATE_STALE_AFTER_MATERIAL_CHANGE,
    EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT,
    ROLE_IMPLEMENTER,
    ROLE_INDEPENDENT_EVALUATOR,
    ROLE_UNSPECIFIED,
    P30AuthorityError,
    can_issue_terminal_acceptance,
    compute_current_artifact_identity,
    execution_success,
    issue_terminal_acceptance,
    mark_evaluator_material_edit,
    mark_material_change,
    new_acceptance_record,
    prepare_independent_audit_handoff,
    record_independent_audit,
    record_regression,
    verify_external_acceptance_record,
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
    assert "external" in reason.lower()
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
        env={**os.environ, "PYTHONUTF8": "1"},
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
    # A terminal state can only be an externally produced fact in this test;
    # the repository API must not manufacture it.
    prior = prior.__class__(
        **{
            **prior.to_dict(),
            "artifact_state": ARTIFACT_STATE_ACCEPTED,
            "artifact_acceptance": "EXTERNAL_DECISION",
            "terminal_acceptance_status": "EXTERNAL_DECISION",
        }
    )
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


def test_self_attested_complete_record_cannot_create_terminal_acceptance():
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

    allowed, reason = can_issue_terminal_acceptance(record)
    assert allowed is False
    assert "external" in reason.lower()
    with pytest.raises(P30AuthorityError):
        issue_terminal_acceptance(record)


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
    assert "external" in reason.lower()


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


def test_terminal_cli_never_self_issues_from_caller_claims():
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
    assert result.returncode == 2
    assert payload["artifact_acceptance"] != "ACCEPTED"
    assert payload["terminal_acceptance_status"].startswith("ACCEPTANCE BLOCKED")
    assert "INDEPENDENT ACCEPTANCE PASS" not in result.stdout


def test_caller_artifact_id_cannot_override_computed_identity():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--execution-success",
            "--artifact-id",
            "FABRICATED-NOT-HEAD",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["artifact_identity"] != "FABRICATED-NOT-HEAD"


def test_non_material_flag_cannot_create_terminal_acceptance():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--terminal-acceptance",
            "--role",
            ROLE_IMPLEMENTER,
            "--non-material-artifact",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode != 0
    assert "ACCEPTED" not in result.stdout


def _git_repo_with_commit(tmp_path, content="initial"):
    repo = tmp_path / "candidate"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "P30 Test"], cwd=repo, check=True)
    (repo / "artifact.txt").write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=repo, check=True)
    return repo


def _external_record(identity, **overrides):
    record = {
        "schema_version": "P30-A3/v1",
        "record_type": "P30_EXTERNAL_INDEPENDENT_AUDIT",
        "artifact_identity": identity,
        "accepted_artifact_identity": identity,
        "terminal_decision": "INDEPENDENT ACCEPTANCE PASS",
        "evaluator_role_declaration": "INDEPENDENT_EVALUATOR",
        "artifact_first_audit_status": "COMPLETE",
        "first_pass_freeze_status": "FROZEN",
        "evaluator_material_edit_status": "NO",
        "audit_timestamp": "2026-09-10T00:00:00+08:00",
        "audit_report_reference": "external-audit-store/p30-a3-report.md",
    }
    record.update(overrides)
    return record


def test_external_record_identity_mismatch_is_rejected(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    record_path = tmp_path / "external-audit.json"
    record_path.write_text(
        json.dumps(_external_record("FABRICATED-NOT-HEAD")), encoding="utf-8"
    )

    result = verify_external_acceptance_record(
        json.loads(record_path.read_text(encoding="utf-8")),
        repo=repo,
        record_path=record_path,
    )
    assert result.verified is False
    assert "identity" in result.reason.lower()
    assert result.status != EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT


def test_matching_external_record_is_only_verified_not_created(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "external-audit.json"
    record_path.write_text(
        json.dumps(_external_record(identity)), encoding="utf-8"
    )

    result = verify_external_acceptance_record(
        json.loads(record_path.read_text(encoding="utf-8")),
        repo=repo,
        record_path=record_path,
    )
    assert result.verified is True
    assert result.status == EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT
    assert result.repository_proved_independence is False
    assert result.external_terminal_decision == "INDEPENDENT ACCEPTANCE PASS"


def test_cli_verifies_external_record_without_issuing_local_acceptance(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "external-audit.json"
    record_path.write_text(json.dumps(_external_record(identity)), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--verify-external-acceptance",
            "--repo",
            str(repo),
            "--external-record",
            str(record_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT
    assert payload["artifact_acceptance"] == "EXTERNAL_DECISION_VERIFIED"
    assert payload["repository_proved_independence"] is False
    assert payload["terminal_acceptance_status"] != "INDEPENDENT ACCEPTANCE PASS"


def test_legacy_terminal_cli_alias_only_verifies_external_record(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "external-audit-alias.json"
    record_path.write_text(json.dumps(_external_record(identity)), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--terminal-acceptance",
            "--repo",
            str(repo),
            "--external-record",
            str(record_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT
    assert payload["artifact_acceptance"] == "EXTERNAL_DECISION_VERIFIED"
    assert payload["repository_proved_independence"] is False


def test_current_artifact_drift_invalidates_the_same_external_record(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "external-audit.json"
    record_path.write_text(json.dumps(_external_record(identity)), encoding="utf-8")

    (repo / "artifact.txt").write_text("changed", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "material change"], cwd=repo, check=True)

    result = verify_external_acceptance_record(
        json.loads(record_path.read_text(encoding="utf-8")),
        repo=repo,
        record_path=record_path,
    )
    assert result.verified is False
    assert "identity" in result.reason.lower()


def test_dirty_artifact_rejects_external_terminal_verification(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "external-audit.json"
    record_path.write_text(json.dumps(_external_record(identity)), encoding="utf-8")
    (repo / "untracked.txt").write_text("untracked", encoding="utf-8")

    result = verify_external_acceptance_record(
        json.loads(record_path.read_text(encoding="utf-8")),
        repo=repo,
        record_path=record_path,
    )
    assert result.verified is False
    assert "dirty" in result.reason.lower()


def test_external_record_inside_candidate_repository_is_rejected(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = repo / "self-authored-acceptance.json"
    record_path.write_text(json.dumps(_external_record(identity)), encoding="utf-8")

    result = verify_external_acceptance_record(
        json.loads(record_path.read_text(encoding="utf-8")),
        repo=repo,
        record_path=record_path,
    )
    assert result.verified is False
    assert "outside" in result.reason.lower()


def test_external_role_declaration_does_not_prove_independence(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "spoofed-evaluator-claim.json"
    record_path.write_text(json.dumps(_external_record(identity)), encoding="utf-8")

    result = verify_external_acceptance_record(
        json.loads(record_path.read_text(encoding="utf-8")),
        repo=repo,
        record_path=record_path,
    )
    assert result.verified is True
    assert result.external_terminal_decision == "INDEPENDENT ACCEPTANCE PASS"
    assert result.repository_proved_independence is False
    assert "did not prove evaluator independence" in result.reason


def test_handoff_routes_computed_clean_artifact_to_fresh_audit(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    current = compute_current_artifact_identity(repo)
    handoff = prepare_independent_audit_handoff(repo)
    assert handoff["artifact_identity"] == current.identity
    assert handoff["clean"] is True
    assert handoff["artifact_acceptance"] == "NOT_ISSUED"
    assert handoff["terminal_acceptance_status"] == "NOT_ISSUED"
    assert handoff["external_audit_record_required"] == "YES"
    assert handoff["repository_proved_independence"] is False


def test_legacy_finality_surfaces_are_candidate_only():
    for path in LEGACY_RUNNERS:
        text = read(path)
        assert "RUN COMPLETE / CANDIDATE RESULTS" in text
        assert "candidate_decision" in text
        assert 'print("FINAL' not in text
        assert 'print("DONE' not in text

    weekly = read(WEEKLY_AUDIT)
    assert "ALL SCHEDULED REGRESSION CHECKS PASSED" in weekly
    assert "ARTIFACT ACCEPTANCE: NOT ISSUED" in weekly
    assert "ALL AUDITS PASSED" not in weekly


def test_automatic_commit_path_only_retains_candidate_bundle(monkeypatch):
    import src.v3_auto_commit as auto_commit_module

    monkeypatch.setattr(auto_commit_module, "check_callers", lambda target: (True, []))
    monkeypatch.setattr(
        auto_commit_module,
        "write_patch_bundle",
        lambda target: "candidate-bundle.patch",
    )
    result = auto_commit_module.auto_commit("core/planner.py")
    assert result == ""


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
    assert "external" in reason.lower()


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
        env={**os.environ, "PYTHONUTF8": "1"},
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
