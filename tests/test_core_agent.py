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
    steps = plan_task("test", mock_llm)
    assert len(steps) == 3
    assert "Do A" in steps[0]

def test_planner_no_steps_fallback():
    from core.planner import plan_task
    def mock_llm(prompt):
        return "Just do it"
    steps = plan_task("test", mock_llm)
    assert len(steps) >= 1
    assert "test" in steps[0]

def test_tools_module():
    from core.tools import tool_shell, tool_calculate, tool_read_file, tool_write_file
    result = tool_calculate("15 * 0.34")
    assert "5.1" in result
    result = tool_calculate("2 + 2")
    assert "4" in result
