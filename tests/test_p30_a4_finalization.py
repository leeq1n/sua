"""Behavioral contract for the P30-A4 post-acceptance lifecycle edge."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "agent-tools" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from p30_acceptance import (  # noqa: E402
    CANONICAL_FINALIZATION_RECORDED,
    CANONICAL_STATE_ACCEPTED_FROZEN,
    EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT,
    FINALIZATION_ACTION_CANONICAL_ACCEPTED_FROZEN,
    compute_current_artifact_identity,
    finalize_accepted_artifact,
)


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
    )
    return result.stdout.strip()


def _git_repo_with_commit(tmp_path: Path, content: str = "initial") -> Path:
    repo = tmp_path / "candidate"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "P30 A4 Test")
    (repo / "artifact.txt").write_text(content, encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "initial")
    return repo


def _external_record(identity: str, **overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
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
        "audit_report_reference": "external-audit-store/p30-a4-report.md",
    }
    record.update(overrides)
    return record


def _write_external_record(path: Path, record: dict[str, object]) -> None:
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def _finalize(repo: Path, record_path: Path, ledger_path: Path):
    return finalize_accepted_artifact(
        json.loads(record_path.read_text(encoding="utf-8")),
        repo=repo,
        record_path=record_path,
        finalization_ledger=ledger_path,
    )


def test_exact_clean_artifact_reaches_durable_canonical_accepted_frozen_state(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    audited_identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "external" / "acceptance.json"
    record_path.parent.mkdir()
    _write_external_record(record_path, _external_record(audited_identity))
    ledger_path = tmp_path / "canonical" / "finalization.json"
    ledger_path.parent.mkdir()

    head_before = _git(repo, "rev-parse", "HEAD")
    artifact_before = (repo / "artifact.txt").read_bytes()
    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is True
    assert result.status == CANONICAL_FINALIZATION_RECORDED
    assert result.accepted_artifact_identity == audited_identity
    assert result.external_decision == "INDEPENDENT ACCEPTANCE PASS"
    assert result.repository_proved_independence is False
    assert ledger_path.is_file()

    finalization = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert finalization["accepted_artifact_identity"] == audited_identity
    assert finalization["external_acceptance_record_reference"] == str(record_path.resolve())
    assert finalization["external_decision"] == "INDEPENDENT ACCEPTANCE PASS"
    assert finalization["finalization_action"] == FINALIZATION_ACTION_CANONICAL_ACCEPTED_FROZEN
    assert finalization["current_canonical_state"] == CANONICAL_STATE_ACCEPTED_FROZEN
    assert finalization["repository_proved_independence"] is False

    assert _git(repo, "rev-parse", "HEAD") == head_before
    assert (repo / "artifact.txt").read_bytes() == artifact_before
    assert _git(repo, "status", "--porcelain=v1", "--untracked-files=all") == ""


def test_finalizer_reuses_a3_verifier_without_issuing_acceptance(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance.json"
    _write_external_record(record_path, _external_record(identity))
    ledger_path = tmp_path / "finalization.json"

    result = _finalize(repo, record_path, ledger_path)

    assert result.external_verification_status == EXTERNAL_ACCEPTANCE_RECORD_MATCHES_CURRENT_ARTIFACT
    assert result.terminal_acceptance_status != "INDEPENDENT ACCEPTANCE PASS"
    assert result.repository_proved_independence is False


@pytest.mark.parametrize(
    ("record_kwargs", "reason_fragment"),
    [
        ({"artifact_identity": "FABRICATED"}, "identity"),
        ({"terminal_decision": "REGRESSION PASS"}, "terminal_decision"),
        ({"evaluator_role_declaration": "IMPLEMENTER"}, "evaluator_role_declaration"),
        ({"evaluator_material_edit_status": "YES"}, "evaluator_material_edit_status"),
        ({"first_pass_freeze_status": "NOT FROZEN"}, "first_pass_freeze_status"),
    ],
)
def test_invalid_external_record_never_creates_canonical_marker(
    tmp_path, record_kwargs, reason_fragment
):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance.json"
    _write_external_record(record_path, _external_record(identity, **record_kwargs))
    ledger_path = tmp_path / "finalization.json"

    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is False
    assert reason_fragment in result.reason
    assert not ledger_path.exists()


def test_missing_record_fails_closed_without_marker(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    ledger_path = tmp_path / "finalization.json"

    result = finalize_accepted_artifact(
        None,
        repo=repo,
        record_path=tmp_path / "missing.json",
        finalization_ledger=ledger_path,
    )

    assert result.finalized is False
    assert "does not exist" in result.reason
    assert not ledger_path.exists()


def test_record_inside_candidate_repository_is_rejected(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = repo / "self-authored.json"
    _write_external_record(record_path, _external_record(identity))
    ledger_path = tmp_path / "finalization.json"

    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is False
    assert "outside" in result.reason
    assert not ledger_path.exists()


def test_dirty_worktree_blocks_finalization(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance.json"
    _write_external_record(record_path, _external_record(identity))
    ledger_path = tmp_path / "finalization.json"
    (repo / "dirty.txt").write_text("not committed", encoding="utf-8")

    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is False
    assert "dirty" in result.reason.lower()
    assert not ledger_path.exists()


def test_record_for_a_is_rejected_after_artifact_changes_to_b(tmp_path):
    repo = _git_repo_with_commit(tmp_path, content="A")
    identity_a = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance-a.json"
    _write_external_record(record_path, _external_record(identity_a))
    ledger_path = tmp_path / "finalization.json"

    (repo / "artifact.txt").write_text("B", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "material change")

    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is False
    assert "identity" in result.reason.lower()
    assert not ledger_path.exists()


def test_checker_only_record_is_not_a_finalization_authority(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "checker.json"
    _write_external_record(record_path, _external_record(identity, terminal_decision="REGRESSION PASS"))
    ledger_path = tmp_path / "finalization.json"

    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is False
    assert not ledger_path.exists()


def test_non_material_caller_flag_cannot_finalize(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance.json"
    _write_external_record(record_path, _external_record(identity))
    ledger_path = tmp_path / "finalization.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--finalize-accepted-artifact",
            "--repo",
            str(repo),
            "--external-record",
            str(record_path),
            "--finalization-ledger",
            str(ledger_path),
            "--non-material-artifact",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 2
    assert "non-materiality" in result.stdout
    assert not ledger_path.exists()


def test_finalization_ledger_inside_candidate_repository_is_rejected(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance.json"
    _write_external_record(record_path, _external_record(identity))
    ledger_path = repo / "canonical-finalization.json"

    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is False
    assert "ledger" in result.reason.lower()
    assert not ledger_path.exists()


def test_existing_conflicting_finalization_cannot_be_overwritten(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance.json"
    _write_external_record(record_path, _external_record(identity))
    ledger_path = tmp_path / "finalization.json"
    ledger_path.write_text(
        json.dumps(
            {
                "accepted_artifact_identity": "OTHER",
                "current_canonical_state": CANONICAL_STATE_ACCEPTED_FROZEN,
            }
        ),
        encoding="utf-8",
    )

    result = _finalize(repo, record_path, ledger_path)

    assert result.finalized is False
    assert "existing" in result.reason.lower()
    assert json.loads(ledger_path.read_text(encoding="utf-8"))["accepted_artifact_identity"] == "OTHER"


def test_cli_finalizer_exposes_the_explicit_liveness_path(tmp_path):
    repo = _git_repo_with_commit(tmp_path)
    identity = compute_current_artifact_identity(repo).identity
    record_path = tmp_path / "acceptance.json"
    _write_external_record(record_path, _external_record(identity))
    ledger_path = tmp_path / "finalization.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "p30_acceptance.py"),
            "--finalize-accepted-artifact",
            "--repo",
            str(repo),
            "--external-record",
            str(record_path),
            "--finalization-ledger",
            str(ledger_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["finalized"] is True
    assert payload["status"] == CANONICAL_FINALIZATION_RECORDED
    assert payload["current_canonical_state"] == CANONICAL_STATE_ACCEPTED_FROZEN
    assert payload["repository_proved_independence"] is False
    assert ledger_path.exists()

