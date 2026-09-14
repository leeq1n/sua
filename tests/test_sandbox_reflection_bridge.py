"""Focused ordinary-path tests for preserving sandbox diagnostics."""

from unittest.mock import Mock

import pytest

from src import pipeline_lg


def _state():
    return {
        "patch": {
            "function": "def candidate():\n    return 5\n",
            "test": "def test_candidate():\n    assert candidate() == 4\n",
        },
        "sandbox_passed": False,
        "reflect_attempts": 0,
        "errors": [],
    }


@pytest.mark.parametrize(
    "diagnostic",
    [
        "assertion mismatch: expected 4, got 5",
        "SyntaxError: invalid syntax at line 3",
    ],
)
def test_failure_diagnostic_reaches_existing_reflector(monkeypatch, diagnostic):
    monkeypatch.setattr(
        pipeline_lg,
        "run_in_sandbox",
        lambda *args, **kwargs: {"passed": False, "error": diagnostic},
    )
    reflector = Mock(
        return_value={"fixed": False, "code": "", "attempts": 1, "errors": []}
    )
    monkeypatch.setattr(pipeline_lg, "reflect_and_improve", reflector)

    state = _state()
    pipeline_lg.node_sandbox(state)
    assert state["sandbox_error"] == diagnostic
    assert pipeline_lg._sandbox_result(state) == "reflect"

    pipeline_lg.node_reflect(state)

    assert reflector.call_count == 1
    assert reflector.call_args.args[2] == diagnostic


@pytest.mark.parametrize(
    "sandbox_result",
    [
        {"passed": False},
        {"passed": False, "error": "", "output": ""},
    ],
)
def test_missing_or_empty_diagnostic_uses_generic_fallback(
    monkeypatch, sandbox_result
):
    monkeypatch.setattr(
        pipeline_lg, "run_in_sandbox", lambda *args, **kwargs: sandbox_result
    )
    reflector = Mock(
        return_value={"fixed": False, "code": "", "attempts": 1, "errors": []}
    )
    monkeypatch.setattr(pipeline_lg, "reflect_and_improve", reflector)

    state = _state()
    pipeline_lg.node_sandbox(state)
    pipeline_lg.node_reflect(state)

    assert reflector.call_args.args[2] == "failed"


def test_successful_sandbox_execution_does_not_invoke_reflection(monkeypatch):
    monkeypatch.setattr(
        pipeline_lg,
        "run_in_sandbox",
        lambda *args, **kwargs: {"passed": True, "error": "", "output": ""},
    )
    reflector = Mock()
    monkeypatch.setattr(pipeline_lg, "reflect_and_improve", reflector)

    state = _state()
    pipeline_lg.node_sandbox(state)

    assert state["sandbox_error"] == ""
    assert pipeline_lg._sandbox_result(state) == "evaluate"
    assert reflector.call_count == 0


def test_existing_retry_ceiling_and_routing_remain_unchanged():
    state = {"sandbox_passed": False}
    assert pipeline_lg._sandbox_result(state) == "reflect"
    assert pipeline_lg._sandbox_result({"sandbox_passed": True}) == "evaluate"
    assert pipeline_lg._reflect_result({"reflect_attempts": 0}) == "sandbox"
    assert pipeline_lg._reflect_result({"reflect_attempts": 2}) == "sandbox"
    assert pipeline_lg._reflect_result({"reflect_attempts": 3}) == "evaluate"
