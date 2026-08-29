"""Structural acceptance tests for the project-layer AI4S controller."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "AI4S_RESEARCH_MODE.md"
DETAIL = ROOT / "docs" / "AI4S_RESEARCH_MODE_DETAIL.md"
VALIDATION = ROOT / "docs" / "AI4S_PHASE_A_VALIDATION.md"
TASKS = ROOT / "benchmarks" / "tasks.json"


def test_summary_is_small_discoverable_controller():
    text = SUMMARY.read_text(encoding="utf-8")
    assert len(text.encode("utf-8")) <= 7 * 1024
    assert "discover, establish, falsify, or claim" in text
    assert "AI4S_RESEARCH_MODE_DETAIL.md" in text
    assert "scientific knowledge state" in text
    assert "Implementation is blocked" in text


def test_detail_contains_state_transitions_and_all_required_triggers():
    text = DETAIL.read_text(encoding="utf-8")
    for state in ("K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7"):
        assert state in text
    for trigger in (
        "Repeated mechanism collision",
        "Combination-only novelty",
        "Renaming without mechanism change",
        "Adapter dependence",
        "No cheap falsifier",
        "Claim/evidence mismatch",
        "Candidate rescue inflation",
        "Mother-space saturation",
    ):
        assert trigger in text


def test_detail_reuses_canonical_operations_and_defines_scientific_gates():
    text = DETAIL.read_text(encoding="utf-8")
    for phrase in (
        "Capability -> Broken Assumption -> Mechanism",
        "search by mechanism, not by nouns",
        "Prosecutor",
        "Reviewer #2",
        "Author",
        "MECHANISM_EQUIVALENT",
        "do_not_revive_unless",
        "expected kill value / cost",
        "AI4S_PROJECT_ADAPTER_VALIDATED",
    ):
        assert phrase in text


def test_pre_agent_gate_is_bounded_and_requires_residual_ambiguity_note():
    summary = SUMMARY.read_text(encoding="utf-8")
    detail = DETAIL.read_text(encoding="utf-8")
    assert "PRE_AGENT_EVIDENCE_GATE" in summary
    for phrase in (
        "specific residual uncertainty",
        "expected information gain",
        "exact-task",
        "operational / standards / product",
        "Why cheap search is no longer sufficient",
        "Stop/KILL condition",
    ):
        assert phrase in detail
    assert "no fixed search count" in detail.lower()


def test_author_claims_and_major_mutations_do_not_inherit_novelty():
    detail = DETAIL.read_text(encoding="utf-8")
    for phrase in (
        "AUTHOR_CLAIMED_NOVELTY",
        "ACTUAL_METHOD",
        "ACTUAL_EXPERIMENT",
        "STRONGEST_COMPARATOR",
        "VERIFIED_DELTA",
        "UNVERIFIED_MARKETING",
        "MAJOR_CANDIDATE_MUTATION_RESETS_NOVELTY",
        "parameter refinement",
        "scientific-object mutation",
    ):
        assert phrase in detail


def test_six_ai4s_regressions_cover_behavioral_acceptance_surface():
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    cases = [task for task in tasks if task.get("category") == "ai4s_regression"]
    assert [task["case"] for task in cases] == list("ABCDEF")
    assert all(task.get("expected_decision") for task in cases)
    assert all(task.get("rubric") for task in cases)

    covered = {
        item["id"]
        for task in cases
        for item in task["rubric"]
    }
    assert {
        "state",
        "cross_domain",
        "mechanism_equivalent",
        "reduce",
        "combination_block",
        "native_audit",
        "kill_ledger",
        "block_mvp",
        "lift_or_reset",
    } <= covered


def test_six_pre_agent_regressions_cover_collisions_mutation_and_escape():
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    cases = [
        task for task in tasks
        if task.get("category") == "ai4s_pre_agent_regression"
    ]
    assert [task["case"] for task in cases] == list("ABCDEF")
    assert all(task.get("expected_decision") for task in cases)
    covered = {item["id"] for task in cases for item in task["rubric"]}
    assert {
        "direct_collision",
        "operational_collision",
        "author_claim_skepticism",
        "mutation_reset",
        "residual_ambiguity",
        "allow_agent",
        "bounded_search",
    } <= covered
    mutation = next(task for task in cases if task["case"] == "D")
    assert "episode 1" in mutation["task"].lower()
    assert "episode 4" in mutation["task"].lower()


def test_phase_a_does_not_route_through_core_layer():
    summary = SUMMARY.read_text(encoding="utf-8")
    detail = DETAIL.read_text(encoding="utf-8")
    assert "core-layer trigger" not in summary.lower()
    assert "Do not modify `core-layer/`" in detail


def test_fresh_agent_discovers_ai4s_from_project_entry_points():
    for relative in (
        "README.md",
        "docs/HOW_TO_READ_GRAPH.md",
        "docs/HANDOFF.md",
        "docs/PROJECT_STATE.md",
        "docs/INDEX.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "AI4S_RESEARCH_MODE.md" in text, relative


def test_phase_a_validation_is_honest_and_records_terminal_decision():
    text = VALIDATION.read_text(encoding="utf-8")
    for phrase in (
        "AI4S_PROJECT_ADAPTER_VALIDATED",
        "PROPOSAL_ONLY_NEEDS_MORE_EVIDENCE",
        "839 passed",
        "858 passed",
        "401",
        "directional behavior score was not produced",
        "Failure pre-mortem",
        "Self-audit",
    ):
        assert phrase in text
    state = (ROOT / "docs" / "PROJECT_STATE.md").read_text(encoding="utf-8")
    assert "AI4S `AI4S_PROJECT_ADAPTER_VALIDATED`" in state
    assert "generic `PROPOSAL_ONLY_NEEDS_MORE_EVIDENCE`" in state
