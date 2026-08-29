"""Tests for the AI4S adapter over SUA's existing benchmark fixtures."""

import pytest

from benchmarks.ai4s_eval import (
    build_guide,
    compare_scored_runs,
    load_ai4s_tasks,
    run_arm,
    score_run,
)


def test_load_ai4s_tasks_filters_existing_task_source():
    tasks = load_ai4s_tasks()
    assert [task["id"] for task in tasks] == [f"ai4s-{c}" for c in "abcdef"]


def test_treatment_adds_controller_to_same_baseline_guide():
    baseline, baseline_files = build_guide("baseline")
    treatment, treatment_files = build_guide("treatment")
    assert "Research Usage Guide" in baseline
    assert "AI4S Research Mode" not in baseline
    assert baseline in treatment
    assert "AI4S Research Mode" in treatment
    assert len(baseline_files) == 1
    assert len(treatment_files) == 3


def test_run_arm_keeps_rubric_unscored_and_uses_same_task_prompt():
    seen = []

    def fake_llm(prompt, *, system, config):
        seen.append((prompt, system))
        return "candidate response"

    result = run_arm("baseline", llm_call=fake_llm, tasks=load_ai4s_tasks()[:1])
    assert result["arm"] == "baseline"
    assert result["results"][0]["response"] == "candidate response"
    assert all(item["rating"] is None for item in result["results"][0]["rubric"])
    assert seen[0][0] == load_ai4s_tasks()[0]["task"]


def test_score_run_requires_explicit_complete_binary_ratings():
    raw = run_arm(
        "baseline",
        llm_call=lambda prompt, *, system, config: "response",
        tasks=load_ai4s_tasks()[:1],
    )
    task = raw["results"][0]
    ratings = {task["id"]: {item["id"]: 1 for item in task["rubric"]}}
    scored = score_run(raw, ratings)
    assert scored["score"]["earned"] == scored["score"]["possible"]

    ratings[task["id"]].pop(next(iter(ratings[task["id"]])))
    with pytest.raises(ValueError, match="ratings must exactly match"):
        score_run(raw, ratings)


def test_compare_reports_direction_without_claiming_significance():
    baseline = {"arm": "baseline", "score": {"earned": 2, "possible": 5}}
    treatment = {"arm": "treatment", "score": {"earned": 4, "possible": 5}}
    comparison = compare_scored_runs(baseline, treatment)
    assert comparison["score_delta"] == 2
    assert comparison["rate_delta"] == pytest.approx(0.4)
    assert comparison["interpretation"] == "directional_only_not_significance"
