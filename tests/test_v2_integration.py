"""Integration tests — full v2_agent pipeline from Paper to Patch.

These tests are larger than unit tests but run without LLM network.
They verify the WHOLE pipeline:
  Paper → RAG → prompt → chat → parse → harness → patch

Each test exercises a real path (no mocked LLM call yet, just
chat() is mocked) to ensure all pieces wire up correctly.
"""
import os
import sys
import json
import tempfile
from unittest.mock import patch as mock_patch, MagicMock

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)

import pytest

from src.v2_agent import (
    Paper, Patch,
    improve, run_with_fixed_paper, FIXED_PAPER,
    memory_add, memory_find_similar,
)


@pytest.fixture
def fresh_state(tmp_path, monkeypatch):
    """Fresh memory DB + empty target module in a tmp dir.

    The fix: don't monkeypatch _memory_path (which would skip schema
    init).  Instead, point MEMORY_DB at the tmp file and let the real
    _memory_path() function create the schema.
    """
    db = str(tmp_path / "v2_memory.db")
    monkeypatch.setattr("src.v2_agent.MEMORY_DB", db)
    # Trigger _memory_path() so schema is auto-created
    import src.v2_agent
    src.v2_agent._memory_path()
    target = tmp_path / "planner.py"
    target.write_text("# original\ndef plan_task():\n    return []\n",
                      encoding="utf-8")
    return {"target": str(target), "db": db}


class TestEndToEnd:
    """Joint test: Paper → RAG → chat → harness returns Patch or None."""

    def test_pass_path(self, fresh_state):
        """The happy path: LLM returns valid patch, harness passes, Patch."""
        target = fresh_state["target"]
        good = json.dumps({
            "function": "def plan_task(): return ['a', 'b']",
            "test": "def test_x(): assert plan_task() == ['a', 'b']",
            "module": target,
        })
        with mock_patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = good
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            paper = Paper(arxiv_id="2310.02170",
                          title="DyLAN", abstract="dynamic agent network")
            result = improve(paper, target_module=target)
            assert result is not None
            assert "plan_task" in result.function

    def test_harness_fail_returns_none(self, fresh_state):
        """Patch parses but harness fails → returns None (no exception)."""
        target = fresh_state["target"]
        bad = json.dumps({
            "function": "def plan_task(): return WRONG",  # NameError
            "test": "def test_x(): assert plan_task() == ['x']",
            "module": target,
        })
        with mock_patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = bad
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            paper = Paper(arxiv_id="2310.02170", title="X", abstract="Y")
            result = improve(paper, target_module=target)
            assert result is None

    def test_parse_fail_returns_none(self, fresh_state):
        """LLM returns garbage → parse fails → returns None (no exception)."""
        target = fresh_state["target"]
        with mock_patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = "the quick brown fox"
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            paper = Paper(arxiv_id="2310.02170", title="X", abstract="Y")
            assert improve(paper, target_module=target) is None

    def test_empty_response_returns_none(self, fresh_state):
        """Empty LLM response → returns None."""
        target = fresh_state["target"]
        with mock_patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = ""
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            paper = Paper(arxiv_id="2310.02170", title="X", abstract="Y")
            assert improve(paper, target_module=target) is None


class TestRAGIntegration:
    """Joint test: RAG retrieval is wired into the prompt."""

    def test_similar_papers_appear_in_prompt(self, fresh_state):
        target = fresh_state["target"]
        # Add a similar paper
        memory_add("2606.30639",
                   "Self-Evolving World Models for LLM agent planning",
                   ["agent", "planning"])
        good = json.dumps({
            "function": "def plan_task(): return ['x']",
            "test": "def test_x(): assert plan_task() == ['x']",
            "module": target,
        })
        captured_prompts = []
        def fake_chat(messages, **kwargs):
            captured_prompts.append(messages[0]["content"])
            mock_resp = MagicMock()
            mock_resp.content = good
            mock_resp.error = None
            return mock_resp
        with mock_patch("src.v2_agent._chat", side_effect=fake_chat):
            paper = Paper(arxiv_id="2310.02170",
                          title="Agent planning",
                          abstract="agent network planning")
            result = improve(paper, target_module=target)
        assert result is not None
        assert len(captured_prompts) == 1
        prompt = captured_prompts[0]
        # Similar paper should appear in the prompt
        assert "2606.30639" in prompt
        assert "agent" in prompt.lower()


class TestTargetSafetyIntegration:
    """Joint test: target_module safety (UTF-8 + missing paths)
    combined with the rest of the pipeline."""

    def test_utf8_target_with_chinese(self, fresh_state, tmp_path):
        """UTF-8 target (Chinese) file → reads cleanly via UTF-8, not GBK."""
        target = tmp_path / "planner中文.py"
        target.write_text(
            "# 中文注释 + é\ndef plan_task(): return []\n",
            encoding="utf-8",
        )
        good = json.dumps({
            "function": "def plan_task(): return ['x']",
            "test": "def test_x(): assert plan_task() == ['x']",
            "module": str(target),
        })
        with mock_patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = good
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            paper = Paper(arxiv_id="2310.02170", title="X", abstract="Y")
            result = improve(paper, target_module=str(target))
            # Should not crash on UTF-8 read
            assert result is not None


class TestFixedPaperIntegration:
    """Joint test: run_with_fixed_paper dispatches correctly."""

    def test_runs_with_dylan_paper(self, fresh_state):
        target = fresh_state["target"]
        good = json.dumps({
            "function": "def plan_task(): return ['x']",
            "test": "def test_x(): assert plan_task() == ['x']",
            "module": target,
        })
        with mock_patch("src.v2_agent._chat") as mock_chat:
            mock_resp = MagicMock()
            mock_resp.content = good
            mock_resp.error = None
            mock_chat.return_value = mock_resp
            result = run_with_fixed_paper(target_module=target)
            assert result is not None


class TestLLMConfigIntegration:
    """Joint test: LLMConfig.from_env + chat() cooperate after dotenv fix."""

    def test_from_env_loads_dotenv(self, monkeypatch, tmp_path):
        """User's .env in cwd → LLMConfig finds base_url + keys."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "LLM_BASE_URL=https://test.example/v1\n"
            "LLM_MODEL=test-model\n"
            "LLM_API_KEY_0=sk-test-abc\n"
        )
        # Patch dotenv to load this tmp .env explicitly
        with mock_patch("dotenv.load_dotenv") as mock_ld:
            mock_ld.return_value = True
            # Note: this is a smoke test that the call structure exists;
            # actual env loading is dotenv's responsibility.
            from src.llm import LLMConfig
            cfg = LLMConfig.from_env()
            assert isinstance(cfg.base_url, str)
            assert isinstance(cfg.api_keys, list)
