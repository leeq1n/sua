"""Regression tests for phase-aware constructive control in SUA."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADD_REDUCE = ROOT / "docs" / "ADD_THEN_REDUCE.md"
TWO_TRACK = ROOT / "docs" / "M_TWO_TRACK_REASONING_DETAIL.md"
CRITICAL = ROOT / "docs" / "M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md"
ACCEPTANCE = ROOT / "docs" / "M_ACCEPTANCE_PROTOCOL_DETAIL.md"
OPERATING = ROOT / "docs" / "OPERATING_RULES.md"
AI4S_DETAIL = ROOT / "docs" / "AI4S_RESEARCH_MODE_DETAIL.md"
SCRIPT = ROOT / "agent-tools" / "scripts" / "m_n29_5step.py"
VERIFICATION = ROOT / "VERIFICATION.md"
AGENTS_DETAIL = ROOT / "AGENTS_DETAIL.md"
PREPARE_COMMIT_MSG = ROOT / "hooks" / "prepare-commit-msg"
BRIDGE = ROOT / "docs" / "CROSS_RUNTIME_SKILL_BRIDGE.md"
TASKS = ROOT / "benchmarks" / "tasks.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_open_ended_work_requires_observable_constructive_expansion():
    acceptance = read(ACCEPTANCE)
    two_track = read(TWO_TRACK)
    for phrase in (
        "observable constructive expansion",
        "structurally distinct",
        "donor-to-target mapping",
        "target consequence",
        "retrieval alone",
    ):
        assert phrase in acceptance or phrase in two_track


def test_constructive_add_is_distinct_from_artifact_and_evidence_add():
    text = read(ADD_REDUCE)
    assert "artifact/evidence Add" in text
    assert "constructive search-space Add" in text
    assert "bounded constructive Add window" in text
    assert "synthesize before terminal critique" in text


def test_critique_order_is_phase_aware_without_weakening_hard_stops():
    critical = read(CRITICAL)
    two_track = read(TWO_TRACK)
    combined = critical + two_track
    assert "phase-aware" in combined
    assert "must not interleave terminal critique" in combined
    for hard_stop in (
        "safety",
        "known impossibility",
        "explicit hard constraint",
        "decisive existing evidence",
    ):
        assert hard_stop in combined


def test_local_rejection_without_global_progress_triggers_replanning():
    operating = read(OPERATING)
    acceptance = read(ACCEPTANCE)
    combined = operating + acceptance
    assert "locally valid terminal decisions" in combined
    assert "no fixed rejection count" in combined
    assert "controller-level replan" in combined
    assert "output-space expansion" in combined


def test_rejection_aware_retry_gate_carries_causal_state_and_authority():
    acceptance = read(ACCEPTANCE)
    operating = read(OPERATING)
    combined = acceptance + operating
    for phrase in (
        "user is the acceptance authority",
        "invalidates any prior local `PASS`",
        "PARENT_OBJECTIVE",
        "FAILED_ACCEPTANCE_CRITERION",
        "FAILURE_CLASS",
        "REPRESENTATION_FAMILY",
        "PRODUCTION_SUBSTRATE",
        "CAUSAL_DELTA",
        "abstraction ladder",
        "no causal delta",
        "src/retry_gate.py",
    ):
        assert phrase in combined


def test_stateless_bridge_exposes_loop_breaker_activation():
    bridge = read(BRIDGE)
    assert "LOOP-BREAKER GATE" in bridge
    assert "user is the acceptance authority" in bridge
    assert "invalidates any prior local `PASS`" in bridge
    assert "CAUSAL_DELTA" in bridge
    assert "controller-level replan" in bridge
    assert "src/retry_gate.py" in bridge


def test_repeated_user_rejection_fixture_is_domain_general_and_complete():
    tasks = json.loads(read(TASKS))
    cases = [
        task for task in tasks
        if task.get("category") == "global_progress_regression"
    ]
    assert {task["case"] for task in cases} == {
        "same-structure-local-retry"
    }
    case = cases[0]
    assert "spacecraft" not in case["task"].lower()
    assert case["expected_decision"] == "GLOBAL_REPLAN_REQUIRED"
    assert case["baseline_expected_failure"]
    assert {
        "repeated_failure",
        "user_authority",
        "failure_record",
        "causal_delta",
        "abstraction_escalation",
        "negative_knowledge",
        "stop_local_retry",
        "global_replan",
    } == {item["id"] for item in case["rubric"]}


def test_well_specified_work_skips_creativity_ceremony():
    two_track = read(TWO_TRACK)
    acceptance = read(ACCEPTANCE)
    combined = two_track + acceptance
    assert "well-specified execution" in combined
    assert "direct logical execution" in combined
    assert "does not require constructive expansion" in combined


def test_ai4s_adapter_still_separates_generation_from_falsification():
    text = read(AI4S_DETAIL)
    normalized = " ".join(text.split())
    assert "separates problem generation from candidate falsification" in text
    assert "CONSTRUCTIVE_ADD_RESET" in text
    assert "Add never weakens the K3/K4 tribunal" in normalized


def test_mn29_script_is_task_generic_and_honest_about_semantic_coverage():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--self",
            "--claim",
            "preserve constructive expansion",
            "--task-profile",
            "open-ended",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "5 repos + 4 zip + 1 tag" not in result.stdout
    assert "STRUCTURAL BASELINE ONLY" in result.stdout
    assert "open-ended" in result.stdout
    assert "semantic acceptance still requires evidence" in result.stdout
    assert "Loop not enforced in script" not in result.stdout
    assert "src.retry_gate.evaluate_retry" in result.stdout
    assert result.stdout.index("[Step 2] Execute") < result.stdout.index(
        "[Step 2a] Apply"
    )


def test_verification_surfaces_match_phase_aware_constructive_control():
    verification = read(VERIFICATION)
    agents_detail = read(AGENTS_DETAIL)
    hook = read(PREPARE_COMMIT_MSG)
    combined = verification + agents_detail + hook

    assert "Last constructive-control verification: 2026-09-12" in verification
    assert "open-ended discovery / design / hypothesis formation" in verification
    assert "deterministic / well-specified execution" in verification
    assert "live behavioral improvement remains unmeasured" in verification
    assert "11 constructive-control regressions" in verification
    assert "critical-thinking BEFORE constructive" not in combined
    assert "4 critical-thinking primitives** FIRST" not in combined
    assert "15 design criteria" not in verification
    assert "--task-profile open-ended" in hook
