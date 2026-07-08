"""Tests for src/langchain_bridge.py — HermesChatModel.

Verifies:
  - _generate produces correct ChatResult for plain text
  - _generate parses patchgen-style JSON into tool_calls
  - _generate parses ReAct-style JSON into tool_calls
  - _generate handles LLM error gracefully
  - _generate translates SystemMessage/HumanMessage/AIMessage correctly
  - bind_tools works (inherited from BaseChatModel)
"""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent")

import pytest

from src.langchain_bridge import HermesChatModel


def _make_response(content="", error=None):
    """Mock LLMResponse."""
    r = MagicMock()
    r.content = content
    r.error = error
    return r


class TestHermesChatModel:
    def test_llm_type(self):
        m = HermesChatModel()
        assert m._llm_type == "hermes"

    def test_generate_plain_text(self):
        """LLM returns plain text → AIMessage with content."""
        with patch("src.llm.chat", return_value=_make_response("Hello!")):
            m = HermesChatModel()
            from langchain_core.messages import HumanMessage
            result = m.invoke([HumanMessage(content="hi")])
            assert result.content == "Hello!"
            assert not result.tool_calls

    def test_generate_patchgen_json(self):
        """LLM returns patchgen JSON → tool_call with submit_patch."""
        patch_json = (
            '{"function": "def plan_task():\\n    return [\\"step\\"]",'
            ' "test": "def test(): assert True",'
            ' "module": "core/planner.py"}'
        )
        with patch("src.llm.chat", return_value=_make_response(patch_json)):
            m = HermesChatModel()
            from langchain_core.messages import HumanMessage
            result = m.invoke([HumanMessage(content="write a patch")])
            assert result.content == ""  # content suppressed when tool_calls
            assert len(result.tool_calls) == 1
            tc = result.tool_calls[0]
            assert tc["name"] == "submit_patch"
            assert "def plan_task" in tc["args"]["function"]
            assert "core/planner.py" == tc["args"]["module"]

    def test_generate_react_json(self):
        """LLM returns ReAct-style JSON → tool_call with name + args."""
        react_json = (
            '{"name": "memory_search", '
            '"arguments": {"query": "agent reasoning", "top_k": 3}}'
        )
        with patch("src.llm.chat", return_value=_make_response(react_json)):
            m = HermesChatModel()
            from langchain_core.messages import HumanMessage
            result = m.invoke([HumanMessage(content="search memory")])
            assert len(result.tool_calls) == 1
            tc = result.tool_calls[0]
            assert tc["name"] == "memory_search"
            assert tc["args"]["query"] == "agent reasoning"
            assert tc["args"]["top_k"] == 3

    def test_generate_json_in_markdown_fence(self):
        """JSON wrapped in ```json ... ``` is still parsed."""
        wrapped = (
            "```json\n"
            '{"name": "memory_add_paper", '
            '"arguments": {"arxiv_id": "2310.02170", "summary": "test", '
            '"topics": ["agent"]}}\n'
            "```"
        )
        with patch("src.llm.chat", return_value=_make_response(wrapped)):
            m = HermesChatModel()
            from langchain_core.messages import HumanMessage
            result = m.invoke([HumanMessage(content="add paper")])
            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["name"] == "memory_add_paper"

    def test_generate_invalid_json_returns_plain_text(self):
        """Garbage input → no tool_calls, content preserved."""
        with patch("src.llm.chat",
                   return_value=_make_response("not json at all")):
            m = HermesChatModel()
            from langchain_core.messages import HumanMessage
            result = m.invoke([HumanMessage(content="x")])
            assert result.content == "not json at all"
            assert not result.tool_calls

    def test_generate_llm_error(self):
        """LLM returns error → AIMessage with error marker."""
        with patch("src.llm.chat",
                   return_value=_make_response("", error="connection refused")):
            m = HermesChatModel()
            from langchain_core.messages import HumanMessage
            result = m.invoke([HumanMessage(content="x")])
            assert "LLM error" in result.content
            assert "connection refused" in result.content

    def test_generate_system_message_translated(self):
        """SystemMessage → role: system in messages."""
        captured = {}

        def fake_chat(messages, **kwargs):
            captured["messages"] = messages
            return _make_response("ok")

        with patch("src.llm.chat", side_effect=fake_chat):
            m = HermesChatModel()
            from langchain_core.messages import (
                SystemMessage, HumanMessage,
            )
            m.invoke([
                SystemMessage(content="You are helpful."),
                HumanMessage(content="hi"),
            ])
            roles = [msg["role"] for msg in captured["messages"]]
            assert roles == ["system", "user"]
            assert captured["messages"][0]["content"] == "You are helpful."
            assert captured["messages"][1]["content"] == "hi"

    def test_generate_aimessage_with_tool_calls_preserved(self):
        """Previous AI tool_calls are round-tripped to OpenAI format."""
        captured = {}

        def fake_chat(messages, **kwargs):
            captured["messages"] = messages
            return _make_response("ok")

        with patch("src.llm.chat", side_effect=fake_chat):
            m = HermesChatModel()
            from langchain_core.messages import (
                AIMessage, HumanMessage, ToolMessage,
            )
            prior_ai = AIMessage(
                content="",
                tool_calls=[{
                    "id": "tc_1",
                    "name": "memory_search",
                    "args": {"query": "x"},
                }],
            )
            tool_result = ToolMessage(
                tool_call_id="tc_1",
                content="result-1",
            )
            m.invoke([
                prior_ai,
                tool_result,
                HumanMessage(content="next"),
            ])
            # The assistant message should have tool_calls formatted
            assert captured["messages"][0]["role"] == "assistant"
            assert captured["messages"][0]["tool_calls"][0]["function"]["name"] == "memory_search"
            assert captured["messages"][1]["role"] == "tool"
            assert captured["messages"][1]["tool_call_id"] == "tc_1"

    def test_generate_passes_thinking_config(self):
        """Per-call thinking control reaches chat()."""
        captured = {}

        def fake_chat(messages, **kwargs):
            captured.update(kwargs)
            return _make_response("ok")

        with patch("src.llm.chat", side_effect=fake_chat):
            m = HermesChatModel(enable_thinking=True, thinking_budget=1024)
            from langchain_core.messages import HumanMessage
            m.invoke([HumanMessage(content="x")])
            assert captured.get("enable_thinking") is True
            assert captured.get("thinking_budget") == 1024

    def test_bind_tools_returns_bound_model(self):
        """bind_tools is inherited; returns a runnable that injects tools."""
        m = HermesChatModel()
        # bind_tools is on BaseChatModel; returns a RunnableBinding
        bound = m.bind_tools([{"name": "test_tool", "description": "x"}])
        # Just verify it doesn't error
        assert bound is not None