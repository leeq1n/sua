"""Structural and discoverability regressions for artifact finalization."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "ARTIFACT_FINALIZATION.md"
VALIDATION = ROOT / "docs" / "ARTIFACT_GOVERNANCE_VALIDATION.md"
TASKS = ROOT / "benchmarks" / "tasks.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def markdown_targets(path: Path) -> set[str]:
    return set(re.findall(r"\[[^]]+\]\(([^)#]+)", read(path)))


def test_fresh_agent_reaches_finalization_from_ordinary_acceptance_path():
    assert "core-layer/AGENTS_CORE.md" in read(ROOT / "README.md")
    assert "docs/INDEX.md" in read(ROOT / "core-layer" / "AGENTS_CORE.md")
    assert "HOW_TO_READ_GRAPH.md" in markdown_targets(ROOT / "docs" / "INDEX.md")
    assert "ARTIFACT_FINALIZATION.md" in markdown_targets(
        ROOT / "docs" / "HOW_TO_READ_GRAPH.md"
    )
    assert "ARTIFACT_FINALIZATION.md" in markdown_targets(
        ROOT / "docs" / "ACCEPTANCE_PROTOCOL.md"
    )
    assert "ARTIFACT_FINALIZATION.md" in read(ROOT / "docs" / "INDEX.md")


def test_gate_orders_objective_recovery_before_blind_first_promotion_audit():
    text = read(GUIDE)
    ordered_markers = (
        "## 1. Recover the real objective and classify freezes",
        "## 2. Reduce historical implementation residue",
        "## 3. Regress stable killed-defect classes",
        "## 4. Run a blind-first fresh audit",
        "## 5. Reconcile once, then stop",
    )
    positions = [text.index(marker) for marker in ordered_markers]
    assert positions == sorted(positions)


def test_scientific_freeze_is_protected_while_conveniences_remain_challengeable():
    text = read(GUIDE)
    assert "Evidence-backed invariant" in text
    assert "Publication or interface decision" in text
    assert "Implementation convenience" in text
    assert "must not be changed after outcome inspection" in text
    assert "cannot rescue a failed result" in text


def test_independence_is_information_control_not_mandatory_multi_agent_work():
    text = read(GUIDE)
    normalized = " ".join(text.split())
    assert "current artifact" in text
    assert "patch rationales" in text
    assert "previous PASS reports" in text
    assert "A different agent instance is optional" in normalized
    assert "one blind-first audit" in text


def test_proxy_patch_debt_and_killed_defects_have_bounded_controls():
    text = read(GUIDE)
    for phrase in (
        "true objective",
        "remove obsolete controls",
        "stable and recurrent defect classes",
        "existing validation contract",
        "functionally justified exception",
        "major artifact mutation",
    ):
        assert phrase in text


def test_regression_scenarios_are_generic_and_mechanistically_distinct():
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    cases = [
        task for task in tasks
        if task.get("category") == "artifact_finalization_regression"
    ]
    assert {task["case"] for task in cases} == {
        "software-release",
        "benchmark-release",
    }
    assert all(task.get("expected_decision") for task in cases)
    covered = {item["id"] for task in cases for item in task["rubric"]}
    assert {
        "freeze_classification",
        "proxy_rejection",
        "patch_reduction",
        "killed_defect_regression",
        "blind_first",
        "scientific_freeze",
        "bounded_stop",
    } <= covered


def test_validation_record_is_honest_about_evidence_and_terminal_decision():
    text = read(VALIDATION)
    assert "ADAPTER_UPDATE / ARTIFACT-GOVERNANCE ORCHESTRATION ACCEPTED" in text
    assert "STRUCTURALLY_VALIDATED_BEHAVIOR_PENDING" in text
    assert "Behavioral improvement was not measured" in text
    for heading in (
        "Observed failure family",
        "Strongest no-change argument",
        "Existing mechanisms inspected",
        "Exact missing behavior",
        "Candidate solutions before reduction",
        "Selected minimal solution",
        "Rejected heavier alternatives",
        "Red-before-green evidence",
        "Regression results",
        "Remaining uncertainty",
    ):
        assert heading in text
