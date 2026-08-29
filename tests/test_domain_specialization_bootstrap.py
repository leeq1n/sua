"""Acceptance tests for domain-general specialization detection."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "DOMAIN_SPECIALIZATION_BOOTSTRAP.md"
DETAIL = ROOT / "docs" / "DOMAIN_SPECIALIZATION_BOOTSTRAP_DETAIL.md"
VALIDATION = ROOT / "docs" / "AI4S_PHASE_A_VALIDATION.md"
TASKS = ROOT / "benchmarks" / "tasks.json"


def test_bootstrap_is_small_detector_not_domain_registry():
    text = DOC.read_text(encoding="utf-8")
    assert len(text.encode("utf-8")) <= 7 * 1024
    for phrase in (
        "Layer 1 — domain specialization detection",
        "Layer 2 — domain adapter",
        "GENERIC_SUFFICIENT",
        "COLLECT_MORE_EVIDENCE",
        "PROPOSE_PROJECT_ADAPTER_EXPERIMENT",
        "not a registry of domains",
        "must not silently mutate core rules",
    ):
        assert phrase in text


def test_bootstrap_defines_signals_lifecycle_and_exit_gates():
    text = DOC.read_text(encoding="utf-8")
    for phrase in (
        "Repeated user steering",
        "Repeated structural failure",
        "Recurring prompt scaffolding",
        "Stable evidence contract",
        "Stable tool sequence",
        "Unrepresented state transitions",
        "Methodological corrections",
        "generic-first counterfactual",
        "Delete the adapter",
        "Broader promotion",
    ):
        assert phrase in text


def test_two_non_ai4s_regressions_cover_positive_and_negative_detection():
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    cases = [
        task for task in tasks
        if task.get("category") == "specialization_regression"
    ]
    assert [task["case"] for task in cases] == ["debugging-negative", "legal-positive"]
    assert cases[0]["expected_decision"] == "GENERIC_SUFFICIENT"
    assert cases[1]["expected_decision"] == "PROPOSE_PROJECT_ADAPTER_EXPERIMENT"
    assert all("research" not in task["task"].lower() for task in cases)

    covered = {
        item["id"]
        for task in cases
        for item in task["rubric"]
    }
    assert {
        "task_family",
        "generic_coverage",
        "methodological_friction",
        "stable_contract",
        "no_over_specialization",
        "proposal_only",
        "deletion_gate",
        "no_core_mutation",
    } <= covered


def test_bootstrap_is_discoverable_without_loading_every_domain_adapter():
    for relative in (
        "docs/HOW_TO_READ_GRAPH.md",
        "docs/HANDOFF.md",
        "docs/PROJECT_STATE.md",
        "docs/INDEX.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "DOMAIN_SPECIALIZATION_BOOTSTRAP.md" in text, relative


def test_phase_a_keeps_adapter_and_generic_decisions_independent():
    report = VALIDATION.read_text(encoding="utf-8")
    detail = DETAIL.read_text(encoding="utf-8")
    assert "AI4S_PROJECT_ADAPTER_VALIDATED" in report
    assert "PROPOSAL_ONLY_NEEDS_MORE_EVIDENCE" in report
    assert "AI4S success does not validate the generic detector" in report
    assert "DOMAIN_SPECIALIZATION_BOOTSTRAP_VALIDATED" in detail
    assert "do not prove domain-general behavior" in detail
