"""Regression contract for P30: construction and acceptance are separate."""

import json
import re
import subprocess
import sys
from pathlib import Path


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
