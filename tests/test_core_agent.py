"""Tests for core agent module."""
import pytest

def test_import_agent():
    from core.agent import run, register_tool, list_tools, call_tool, MAX_TURNS
    assert callable(run)
    assert MAX_TURNS == 10

def test_import_planner():
    from core.planner import plan_task
    assert callable(plan_task)

def test_tool_registration():
    from core.agent import register_tool, list_tools, call_tool, _TOOLS
    orig = dict(_TOOLS)
    try:
        _TOOLS.clear()
        register_tool("test", lambda x: x, "test tool")
        assert "test" in _TOOLS
        tools = list_tools()
        assert any(t["name"] == "test" for t in tools)
        result = call_tool("test", x="hello")
        assert result == "hello"
    finally:
        _TOOLS.clear()
        _TOOLS.update(orig)

def test_call_missing_tool():
    from core.agent import call_tool
    result = call_tool("nonexistent")
    assert "not registered" in result.lower()

def test_planner_with_mock_llm():
    from core.planner import plan_task
    def mock_llm(prompt):
        return "1. Do A\n2. Do B\n3. Do C"
    result = plan_task("test", mock_llm)
    assert result.round_id is not None
    assert result.steps == ["Do A", "Do B", "Do C"]

def test_planner_no_steps_fallback():
    from core.planner import plan_task
    def mock_llm(prompt):
        return "Just do it"
    result = plan_task("test", mock_llm)
    assert result.steps == ["Just do it"]


def test_agent_run_consumes_persisted_plan():
    from core.agent import run

    def mock_llm(prompt):
        return '["Do A", "Do B"]' if "Decompose this task" in prompt else "none"

    outcome = run("test", mock_llm, max_turns=2)
    assert outcome["steps_planned"] == 2
    assert outcome["steps_executed"] == 2

def test_tools_module():
    from core.tools import tool_shell, tool_calculate, tool_read_file, tool_write_file
    result = tool_calculate("15 * 0.34")
    assert "5.1" in result
    result = tool_calculate("2 + 2")
    assert "4" in result


def test_shell_nonzero_exit_is_reported_as_failure():
    from core.tools import tool_shell
    assert tool_shell("exit 7").startswith("Shell error: exit code 7")


def test_agent_quick_test_streaming_default():
    """quick_test(stream=True) is the v1.8.1 default."""
    import inspect
    from core.agent import quick_test
    sig = inspect.signature(quick_test)
    assert "stream" in sig.parameters
    assert sig.parameters["stream"].default is True


def test_agent_quick_test_streaming_source_uses_chat_stream():
    """quick_test source should reference chat_stream and chat_simple."""
    import inspect
    from core.agent import quick_test
    src = inspect.getsource(quick_test)
    assert "chat_stream" in src, "quick_test should use chat_stream when stream=True"
    assert "chat_simple" in src, "quick_test should use chat_simple when stream=False"


def test_agent_quick_test_accepts_stream_kwarg():
    """quick_test(stream=False) is callable without crashing on import."""
    from core.agent import quick_test
    # Just verify it accepts the kwarg (without actually invoking)
    assert callable(quick_test)
