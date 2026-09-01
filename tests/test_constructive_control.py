"""Regression tests for phase-aware constructive control in SUA."""

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
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "5 repos + 4 zip + 1 tag" not in result.stdout
    assert "STRUCTURAL BASELINE ONLY" in result.stdout
    assert "open-ended" in result.stdout
    assert "semantic acceptance still requires evidence" in result.stdout
    assert result.stdout.index("[Step 2] Execute") < result.stdout.index(
        "[Step 2a] Apply"
    )
