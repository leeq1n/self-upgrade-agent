"""Tests for src/react.py — ReAct loop driver."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src import react
from src.react import (
    ReActConfig, ReactStep, parse_llm_step,
    _format_tools_for_prompt, _format_observation,
)


# --------------------------------------------------------------------- #
# Parser tests
# --------------------------------------------------------------------- #

class TestParseLlmStep:
    def test_parses_thought_action_input(self):
        text = """\
Thought: I need to search for agent papers.
Action: memory_search
Action Input: query="agent reasoning"
"""
        step = parse_llm_step(text)
        assert step.thought == "I need to search for agent papers."
        assert step.action == "memory_search"
        assert step.action_input == {"query": "agent reasoning"}

    def test_parses_bracketed_action(self):
        text = """\
Thought: x
Action: [memory_search]
Action Input: {"query": "y"}
"""
        step = parse_llm_step(text)
        assert step.action == "memory_search"

    def test_parses_final_answer(self):
        text = """\
Thought: I have enough info.
Final Answer: 42
"""
        step = parse_llm_step(text)
        assert step.is_final is True
        assert step.final_answer == "42"

    def test_parses_action_input_json(self):
        text = """\
Thought: t
Action: memory_add_paper
Action Input: {"arxiv_id": "2310.02170", "summary": "DyLAN", "topics": ["agent"]}
"""
        step = parse_llm_step(text)
        assert step.action == "memory_add_paper"
        assert step.action_input["arxiv_id"] == "2310.02170"
        assert step.action_input["topics"] == ["agent"]

    def test_parses_action_input_keyvalue(self):
        text = """\
Thought: t
Action: memory_search
Action Input:
query="agent"
top_k=3
"""
        step = parse_llm_step(text)
        assert step.action_input == {"query": "agent", "top_k": "3"}


# --------------------------------------------------------------------- #
# Format helpers
# --------------------------------------------------------------------- #

class TestFormatHelpers:
    def test_format_tools_empty_registry(self, monkeypatch):
        from src.mcp_client import clear_registry
        clear_registry()
        result = _format_tools_for_prompt()
        assert "(no tools registered)" in result

    def test_format_tools_with_registered(self):
        from src.mcp_client import clear_registry, register_tool, list_tools

        @register_tool(name="format_test", description="format test", schema={})
        def f():
            return None
        result = _format_tools_for_prompt()
        assert "format_test" in result
        clear_registry()

    def test_format_observation_dict(self):
        result = _format_observation({"k": "v"})
        assert '"k"' in result and '"v"' in result

    def test_format_observation_string(self):
        assert _format_observation("hello") == "hello"


# --------------------------------------------------------------------- #
# ReActConfig defaults
# --------------------------------------------------------------------- #

class TestConfig:
    def test_defaults(self):
        cfg = ReActConfig()
        assert cfg.max_iterations == 8
        assert cfg.tools_desc_chars == 4000
        assert cfg.scratchpad_max_chars == 8000
        assert cfg.on_step is None


# --------------------------------------------------------------------- #
# Integration with mock LLM
# --------------------------------------------------------------------- #

class TestRunReactMocked:
    """Mock chat() to simulate LLM responses, verify the loop."""

    def test_final_answer_immediate(self, monkeypatch):
        from src.react import run_react
        from src.mcp_client import clear_registry, register_tool
        clear_registry()

        @register_tool(name="noop", description="x", schema={})
        def noop():
            return "ok"

        # Mock chat() to return Final Answer immediately
        def fake_chat(*args, **kwargs):
            from src.llm import LLMResponse
            return LLMResponse(
                content="Thought: I am done.\nFinal Answer: 42",
                error=None,
            )

        monkeypatch.setattr(react, "chat", fake_chat)
        result = run_react("what is the answer?")
        assert result["final_answer"] == "42"
        assert result["iterations"] == 1
        assert result["error"] is None

    def test_action_then_final_answer(self, monkeypatch):
        from src.react import run_react
        from src.llm import LLMResponse
        from src.mcp_client import clear_registry, register_tool
        clear_registry()

        @register_tool(name="get_answer", description="x", schema={})
        def get_answer():
            return "the answer is 42"

        # Mock chat() to make one tool call then give Final Answer
        call_count = [0]

        def fake_chat(*args, **kwargs):
            call_count[0] += 1
            from src.llm import LLMResponse
            if call_count[0] == 1:
                return LLMResponse(
                    content=(
                        'Thought: I should use the tool.\n'
                        'Action: get_answer\n'
                        'Action Input: \n'
                    ),
                    error=None,
                )
            else:
                return LLMResponse(
                    content="Thought: Got it.\nFinal Answer: 42",
                    error=None,
                )

        monkeypatch.setattr(react, "chat", fake_chat)
        result = run_react("get the answer")
        assert result["final_answer"] == "42"
        assert result["iterations"] == 2
        # Verify the transcript has both steps
        assert len(result["transcript"]) == 2
        assert result["transcript"][0].action == "get_answer"
        assert "42" in result["transcript"][0].observation
        assert result["transcript"][1].is_final is True

    def test_max_iterations_exceeded(self, monkeypatch):
        from src.react import run_react
        from src.llm import LLMResponse
        from src.mcp_client import clear_registry, register_tool
        clear_registry()

        @register_tool(name="loop_tool", description="x", schema={})
        def loop_tool():
            return "loop"

        # Always return a tool call (never Final Answer)
        def fake_chat(*args, **kwargs):
            from src.llm import LLMResponse
            return LLMResponse(
                content="Thought: looping\nAction: loop_tool\nAction Input: ",
                error=None,
            )

        monkeypatch.setattr(react, "chat", fake_chat)
        cfg = ReActConfig(max_iterations=3)
        result = run_react("loop", config=cfg)
        assert result["final_answer"] is None
        assert result["iterations"] == 3
        assert "max_iterations" in result["error"]

    def test_llm_error_returns_error(self, monkeypatch):
        from src.react import run_react
        from src.llm import LLMResponse

        def fake_chat(*args, **kwargs):
            return LLMResponse(content="", error="connection refused")

        monkeypatch.setattr(react, "chat", fake_chat)
        result = run_react("task")
        assert result["final_answer"] is None
        assert "connection refused" in result["error"]

    def test_unknown_tool_returns_error_in_observation(self, monkeypatch):
        from src.react import run_react
        from src.llm import LLMResponse
        from src.mcp_client import clear_registry
        clear_registry()

        call_count = [0]

        def fake_chat(*args, **kwargs):
            call_count[0] += 1
            from src.llm import LLMResponse
            if call_count[0] == 1:
                return LLMResponse(
                    content=(
                        "Thought: trying a tool\n"
                        "Action: nonexistent_tool\n"
                        "Action Input: "
                    ),
                    error=None,
                )
            return LLMResponse(
                content="Thought: Got error.\nFinal Answer: handled",
                error=None,
            )

        monkeypatch.setattr(react, "chat", fake_chat)
        result = run_react("test")
        assert result["final_answer"] == "handled"
        # Observation should mention the error
        assert "not found" in result["transcript"][0].observation

    def test_on_step_callback_fires(self, monkeypatch):
        from src.react import run_react
        from src.llm import LLMResponse
        from src.mcp_client import clear_registry, register_tool
        clear_registry()

        @register_tool(name="x", description="x", schema={})
        def x():
            return "x"

        steps_seen = []

        def on_step(iteration, thought, action, observation):
            steps_seen.append((iteration, action))

        call_count = [0]

        def fake_chat(*args, **kwargs):
            call_count[0] += 1
            from src.llm import LLMResponse
            if call_count[0] == 1:
                return LLMResponse(
                    content="Thought: t\nAction: x\nAction Input: ",
                    error=None,
                )
            return LLMResponse(content="Final Answer: done", error=None)

        monkeypatch.setattr(react, "chat", fake_chat)
        cfg = ReActConfig(on_step=on_step)
        run_react("task", config=cfg)
        # Should have 2 step callbacks (1 tool call + 1 final)
        assert len(steps_seen) == 2
        assert steps_seen[0] == (1, "x")
        assert steps_seen[1] == (2, None)