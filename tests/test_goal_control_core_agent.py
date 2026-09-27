"""Execution boundary for the daily agent's explicit Goal Contract path."""

import json
from types import SimpleNamespace

import pytest

from core import agent
from src.goal_control import ControlPlane, DriftError, Goal, Task


def controlled_plane():
    control = ControlPlane()
    control.add_goal(Goal("G1", "Deliver the report", ("report delivered",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))
    return control


def test_controlled_agent_uses_resident_context_and_traces_tool_attempt(monkeypatch):
    control = controlled_plane()
    seen = {}

    def plan(prompt, llm_call):
        seen["prompt"] = prompt
        return SimpleNamespace(steps=["Calculate total"])

    monkeypatch.setattr(agent, "plan_task", plan)
    monkeypatch.setattr(agent, "call_tool", lambda name, *args, **kwargs: "4")
    result = agent.run("unbound historical instruction", lambda prompt: "calc: 2+2",
                       control=control,
                       review_action=lambda action, context: "report delivered")
    assert result["execution_succeeded"] is True
    assert result["goal_complete"] is None
    assert result["success"] is False
    assert "unbound historical instruction" not in seen["prompt"]
    assert "Deliver the report" in seen["prompt"]
    assert control.traces[0][1:] == ("T1", "report delivered", "G1")


def test_controlled_agent_denies_tool_before_side_effect(monkeypatch):
    control = controlled_plane()
    calls = []
    monkeypatch.setattr(agent, "plan_task",
                        lambda prompt, llm_call: SimpleNamespace(steps=["Unrelated work"]))
    monkeypatch.setattr(agent, "call_tool",
                        lambda name, *args, **kwargs: calls.append(name))
    result = agent.run("ignored", lambda prompt: "shell: erase files",
                       control=control, review_action=lambda action, context: None)
    assert calls == []
    assert result["success"] is False
    assert "goal guard rejected" in result["logs"][0]["error"]
    assert control.traces == []


def test_later_guard_denial_cannot_report_an_earlier_tool_as_task_success(monkeypatch):
    control = controlled_plane()
    calls = []
    monkeypatch.setattr(agent, "plan_task", lambda prompt, llm_call: SimpleNamespace(
        steps=["Read source", "Build unrelated dashboard"]))
    monkeypatch.setattr(agent, "call_tool",
                        lambda name, *args, **kwargs: calls.append(name) or "ok")
    decisions = iter(["report delivered", None])
    result = agent.run("ignored", lambda prompt: "read: source.txt",
                       control=control,
                       review_action=lambda action, context: next(decisions))
    assert calls == ["read"]
    assert result["success"] is False
    assert "goal guard rejected" in result["logs"][-1]["error"]


def test_controlled_agent_rejects_goal_mutation_between_plan_and_tool(monkeypatch):
    control = controlled_plane()
    calls = []
    monkeypatch.setattr(agent, "plan_task",
                        lambda prompt, llm_call: SimpleNamespace(steps=["Write report"]))
    monkeypatch.setattr(agent, "call_tool",
                        lambda name, *args, **kwargs: calls.append(name))

    def review(action, context):
        control.goals["G1"].objective = "Different objective"
        return "report delivered"

    result = agent.run("ignored", lambda prompt: "read: source.txt",
                       control=control, review_action=review)
    assert result["success"] is False
    assert calls == []
    assert control.traces == []


def test_controlled_agent_requires_explicit_reviewer(monkeypatch):
    monkeypatch.setattr(agent, "plan_task", lambda prompt, llm_call: pytest.fail("planned"))
    with pytest.raises(DriftError):
        agent.run("ignored", lambda prompt: "none", control=controlled_plane())


def test_daily_entrypoint_requires_explicit_goal_contract(monkeypatch):
    monkeypatch.delenv("SUA_GOAL_CONTRACT", raising=False)
    result = agent.quick_test("Write report", stream=False)
    assert result["success"] is False
    assert result["steps_executed"] == 0
    assert "Goal Contract required" in result["error"]


def test_daily_entrypoint_loads_matching_goal_and_task(tmp_path):
    path = tmp_path / "goal.json"
    path.write_text(json.dumps({
        "goal": {"goal_id": "G1", "objective": "Deliver the report",
                 "success_criteria": ["report delivered"],
                 "non_goals": ["build dashboard"]},
        "task": {"task_id": "T1", "title": "Write report", "goal_id": "G1",
                 "criteria": ["report delivered"]},
    }), encoding="utf-8")
    control = agent._load_control_contract(path, "Write report")
    assert control.active_task_id == "T1"
    assert control.working_context()["goal"].objective == "Deliver the report"
    with pytest.raises(DriftError):
        agent._load_control_contract(path, "Build dashboard")


def test_daily_entrypoint_rejects_malformed_criteria(tmp_path):
    path = tmp_path / "goal.json"
    path.write_text(json.dumps({
        "goal": {"goal_id": "G1", "objective": "Deliver the report",
                 "success_criteria": "report delivered"},
        "task": {"task_id": "T1", "title": "Write report", "goal_id": "G1",
                 "criteria": ["report delivered"]},
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="list of strings"):
        agent._load_control_contract(path, "Write report")


def test_daily_entrypoint_guarded_run_with_model_review(tmp_path, monkeypatch):
    pytest.importorskip("httpx")
    from src import llm

    path = tmp_path / "goal.json"
    path.write_text(json.dumps({
        "goal": {"goal_id": "G1", "objective": "Deliver the report",
                 "success_criteria": ["report delivered"]},
        "task": {"task_id": "T1", "title": "Write report", "goal_id": "G1",
                 "criteria": ["report delivered"]},
    }), encoding="utf-8")
    monkeypatch.setattr(llm.LLMConfig, "from_env",
                        lambda: SimpleNamespace(ready=True, timeout=1))
    monkeypatch.setattr(llm, "chat_simple",
                        lambda prompt, **kwargs: (
                            '{"allow": true, "criterion": "report delivered"}'
                            if prompt.startswith("Review this proposed tool action")
                            else "calc: 2+2"))
    monkeypatch.setattr(agent, "plan_task",
                        lambda prompt, llm_call: SimpleNamespace(steps=["Calculate total"]))
    calls = []
    monkeypatch.setattr(agent, "call_tool",
                        lambda name, *args, **kwargs: calls.append((name, args, kwargs)) or "4")
    result = agent.quick_test("Write report", stream=False,
                              goal_contract_path=path)
    assert result["execution_succeeded"] is True
    assert result["goal_complete"] is None
    assert result["success"] is False
    assert calls == [("calc", ("2+2",), {})]


def test_controlled_agent_calls_builtin_tools_with_their_real_signatures(monkeypatch, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("source text", encoding="utf-8")
    monkeypatch.setattr(agent, "plan_task",
                        lambda prompt, llm_call: SimpleNamespace(steps=["Use tool"]))
    for tool, argument in (("calc", "1+1"), ("read", str(source)),
                           ("shell", "echo SUA_TOOL_OK")):
        result = agent.run("ignored", lambda prompt: f"{tool}: {argument}",
                           control=controlled_plane(),
                           review_action=lambda action, context: "report delivered")
        assert result["tools_used"] == 1, tool
        assert result["execution_succeeded"] is True, tool
        assert result["goal_complete"] is None
        assert result["success"] is False


def test_unknown_tool_cannot_count_as_execution_or_goal_success(monkeypatch):
    control = controlled_plane()
    monkeypatch.setattr(agent, "plan_task", lambda prompt, llm_call: SimpleNamespace(
        steps=["First", "Second"]))
    choices = iter(["missing: x", "none"])
    result = agent.run("ignored", lambda prompt: next(choices), control=control,
                       review_action=lambda action, context: "report delivered",
                       verify_completion=lambda context, logs: True)
    assert result["tools_used"] == 0
    assert result["execution_succeeded"] is False
    assert result["goal_complete"] is None
    assert result["success"] is False
    assert control.traces == []


def test_controlled_goal_completion_requires_explicit_evidence_verifier(monkeypatch):
    control = controlled_plane()
    monkeypatch.setattr(agent, "plan_task", lambda prompt, llm_call: SimpleNamespace(
        steps=["Calculate", "No more tools needed"]))
    choices = iter(["calc: 1+1", "none"])
    result = agent.run("ignored", lambda prompt: next(choices), control=control,
                       review_action=lambda action, context: "report delivered")
    assert result["execution_succeeded"] is True
    assert result["goal_complete"] is None
    assert result["success"] is False

    accepted = agent.run(
        "ignored", lambda prompt: "calc: 1+1", control=controlled_plane(),
        review_action=lambda action, context: "report delivered",
        verify_completion=lambda context, logs: True,
    )
    assert accepted["execution_succeeded"] is True
    assert accepted["goal_complete"] is True
    assert accepted["success"] is True
